import logging
import os
import platform
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from termcolor import cprint
from fabric import Connection
import json
import datetime
import time
from sqlalchemy.dialects.postgresql import insert

from cinnabar.error import cuda_out_of_memory
from cinnabar.watcher import get_hostnames_and_ips_from_ssh_config, get_gpu_status, get_cpu_status, get_memory_status, get_os, get_hostname, get_free_gpu, get_conda_envs

from .database import get_db, tabClient, tabTask
from .api_task import api_task_list_pure
from .api_client import api_client_list

class Config(object):
    SCHEDULER_API_ENABLED = True

def create_app(test_config=None):
    __version__ = "0.1.1"
    logging.basicConfig(level="INFO")
    ##################################
    # Create Flask App
    ##################################
    app = Flask(
        __name__,
        instance_path=os.path.expanduser("~/Library/Logs/cinnabar/"),
        instance_relative_config=True
    )
    # make sure instance_path exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Default Config
    app.config.from_mapping({
        "NAME": platform.node().replace(".local", ""),
        "SECRET_KEY": "cinnabar",
        "DATABASE": os.path.expanduser("~/Library/Logs/cinnabar/cinnabar.sqlite3"),
        "STORAGE": os.path.expanduser("~/Library/Logs/cinnabar/"),
        "VERSION": __version__,
    })

    app.config.from_prefixed_env("CINNABAR")

    app.logger.info(f'''
---------------------------------------------------------------------------------------------------------------------------------------
\033[31m░█████╗░██╗███╗░░██╗███╗░░██╗░█████╗░██████╗░░█████╗░██████╗░ \033[1m CINNABAR SERVER {__version__}\033[0m
\033[31m██╔══██╗██║████╗░██║████╗░██║██╔══██╗██╔══██╗██╔══██╗██╔══██╗ \033[0m author : Hanshi Sun
\033[31m██║░░╚═╝██║██╔██╗██║██╔██╗██║███████║██████╦╝███████║██████╔╝ \033[0m platform : {platform.platform()}
\033[31m██║░░██╗██║██║╚████║██║╚████║██╔══██║██╔══██╗██╔══██║██╔══██╗ \033[0m node     : {platform.node()}
\033[31m╚█████╔╝██║██║░╚███║██║░╚███║██║░░██║██████╦╝██║░░██║██║░░██║ \033[0m database : {app.config["DATABASE"]}
\033[31m░╚════╝░╚═╝╚═╝░░╚══╝╚═╝░░╚══╝╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝ \033[0m storage  : {app.config["STORAGE"]}
---------------------------------------------------------------------------------------------------------------------------------------
    ''')

    # init database
    from .database import init_app_db
    db = init_app_db(app)

    # register blueprints
    from .api_client import bp_api_client
    from .api_task import bp_api_task
    from .index import bp_index
    from .ui_client import bp_client
    from .ui_task import bp_task

    # api routes:
    app.register_blueprint(bp_api_client)
    app.register_blueprint(bp_api_task)

    # ui routes:
    app.register_blueprint(bp_index)
    app.register_blueprint(bp_client)
    app.register_blueprint(bp_task)


    # register scheduler and tasks
    app.config.from_object(Config())
    def api_client_update():
        '''
        update clients info
        '''
        with app.app_context():
            hostnames_and_ips = get_hostnames_and_ips_from_ssh_config()
            db = get_db()

            for server in hostnames_and_ips:
                ip = hostnames_and_ips[server]
                cprint(f"================= \ueba3 {server} ================", "cyan")
                connection = Connection(host=server)
                try:
                    result = connection.run("whoami", hide=True, warn=True, timeout=5)
                    user = result.stdout.strip()
                    cprint(f"\ueb77 SSH Success with server {server} as user: \033[3m{user}\033[0m", "green")
                except Exception as e:
                    cprint(f"\uea87 SSH Error with server {server}: {e}\n", "red")
                    status = "offline"
                    db.execute(
                        insert(tabClient)
                        .values(
                            name=server,
                            status=status,
                            ip=ip,
                        )
                        .on_conflict_do_update(
                            index_elements=['name'],
                            set_={
                                'status': status,
                                'ip': ip,
                            }
                        )
                    )
                    db.commit()
                else:
                    gpu = get_gpu_status(connection)
                    cpu = get_cpu_status(connection)
                    memory = get_memory_status(connection)
                    os = get_os(connection)
                    status = "online"
                    hostname = get_hostname(connection)
                    condaEnvs = get_conda_envs(connection)
                    connection.close()

                    db.execute(
                        insert(tabClient)
                        .values(
                            name=server,
                            hostname=hostname,
                            status=status,
                            ip=ip,
                            user=user,
                            timestamp=datetime.datetime.now(),
                            gpu=json.dumps(gpu),
                            cpu=cpu,
                            memory=json.dumps(memory),
                            os=os,
                            condaEnvs=str(condaEnvs),
                        )
                        .on_conflict_do_update(
                            index_elements=['name'],
                            set_={
                                'hostname': hostname,
                                'status': status,
                                'ip': ip,
                                'user': user,
                                'timestamp': datetime.datetime.now(),
                                'gpu': json.dumps(gpu),
                                'cpu': cpu,
                                'memory': json.dumps(memory),
                                'os': os,
                                'condaEnvs': str(condaEnvs),
                            }
                        )
                    )
                    db.commit()
            db.close()

            return {
                "code": 0,
                "message": "successfully update clients info",
            }

    def api_client_excute():
        '''
        execute command on clients
        '''
        with app.app_context():
            db = get_db()
            clients = api_client_list()["data"]
            tasks = api_task_list_pure()["data"]
            for task in tasks:
                if task["status"] == "QUEUE":
                    target_client = task["client"]
                    client = [client for client in clients if client["name"] == target_client][0]
                    if client["status"] == "online":
                        connection = Connection(host=client["name"])
                        free_gpu = get_free_gpu(connection)
                        if len(free_gpu) > 0:
                            gpu = free_gpu[0]
                            connection.run('mkdir -p ~/Logs/', hide=True)
                            command = f"CUDA_VISIBLE_DEVICES={gpu} nohup "+ task["command"] + f" > ~/Logs/{task['id']}.log 2>&1 & echo $!"
                            # activate conda env if needed (Python envs), Fabric does not support command like `python`, `conda`, and so on.
                            if task["env"]:
                                    # MENTION: using with connection.prefix() will cause different PID
                                    command = command.replace("python", f'/home/{client["user"]}/anaconda3/envs/{task["env"]}/bin/python')
                                    result = connection.run(command, hide=True)
                                    cprint(command, "green")
                            else:
                                result = connection.run(command, hide=True)
                                cprint(command, "green")
                            if result.return_code != 0:
                                cprint(f"SSH Error with server {client['name']}: {result.stderr}\n", "red")
                                db.execute(tabTask.update().where(tabTask.c.id == task["id"]).values(
                                    status="FAIL",
                                    true_command=command,
                                    start_time=datetime.datetime.now(),
                                ))
                                db.commit()
                            else:
                                pid = result.stdout.splitlines()[0]
                                db.execute(tabTask.update().where(tabTask.c.id == task["id"]).values(
                                    status="ONGOING",
                                    true_command=command,
                                    start_time=datetime.datetime.now(),
                                    pid=pid,
                                ))
                                db.commit()
                                time.sleep(1) # wait for GPU to be occupied
            db.close()

    def api_client_syncback():
        '''
        syncback task log using connection.get to local cinnabar storage app.config["STORAGE"]/task/{task_id}.log
        '''
        with app.app_context():
            db = get_db()
            clients = api_client_list()["data"]
            tasks = api_task_list_pure()["data"]
            for task in tasks:
                if task["status"] == "ONGOING":
                    target_client = task["client"]
                    client = [client for client in clients if client["name"] == target_client][0]
                    if client["status"] == "online":
                        connection = Connection(host=client["name"])
                        try:
                            connection.run(f"ls ~/Logs/{task['id']}.log", hide=True)
                        except Exception as e:
                            cprint(f"SSH Error with server {client['name']}: {e}\n", "green")
                            db.execute(tabTask.update().where(tabTask.c.id == task["id"]).values(
                                status="FAILED",
                                end_time=datetime.datetime.now(),
                                result="FAIL",
                            ))
                        else:
                            # check if the process is still running
                            result = connection.run(command=f'ps -p {task["pid"]}', hide=True, warn=True)
                            if result.return_code == 0:
                                cprint(f"Task {task['id']} is still running, skip syncback", "green")
                            else:
                                os.system(f"mkdir -p {app.config['STORAGE']}/task/")
                                storage = os.path.join(app.config["STORAGE"], "task", f"{task['id']}.log")
                                os.system(f"touch {storage}")
                                cprint(f"Syncback /home/{client['user']}/Logs/{task['id']}.log to {storage} from client {client['name']}", "green")
                                connection.get(f"/home/{client['user']}/Logs/{task['id']}.log", storage)
                                if cuda_out_of_memory(storage):
                                    cprint("CUDA out of memory", "red")
                                    db.execute(tabTask.update().where(tabTask.c.id == task["id"]).values(
                                    status="FINISH",
                                    end_time=datetime.datetime.now(),
                                    log=storage,
                                    result="FAIL",
                                    error="CUDA out of memory",
                                ))
                                else:
                                    cprint("Task finished successfully", "green")
                                    db.execute(tabTask.update().where(tabTask.c.id == task["id"]).values(
                                        status="FINISH",
                                        end_time=datetime.datetime.now(),
                                        log=storage,
                                        result="PASS",
                                    ))
                                
                                db.commit()
            db.close()

    scheduler = BackgroundScheduler()
    scheduler.add_job(id='update_clients', func=api_client_update, trigger="interval", minutes=3)
    scheduler.add_job(id='excute_tasks', func=api_client_excute, trigger="interval", minutes=1)
    scheduler.add_job(id='syncback_tasks', func=api_client_syncback, trigger="interval", minutes=0.5, max_instances=10)
    with app.app_context():
        scheduler.start()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(
        host="127.0.0.1", port=8500, debug=True, threaded=True,
    )