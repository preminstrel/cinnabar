import json
import os
from flask import (Blueprint, Markup, Response, current_app, g, redirect, request, url_for)
from paramiko.config import SSHConfig
from fabric import Connection
from termcolor import cprint, colored
import datetime
from sqlalchemy.dialects.postgresql import insert

from .database import get_db, tabClient, tabTask, make_dict

CLIENT_TIMEOUT = 3600

bp_api_task = Blueprint('api_task', __name__, url_prefix='/api/task')

@bp_api_task.route("/", endpoint="list", methods=['GET', 'POST'])
def api_task_list() -> dict:
    '''
    return a list of tasks
    '''
    if request.method == "GET":
        tasks = []
        db = get_db()

        if request.args.get("client"):
            for r in db.execute(tabTask.select().where(tabTask.c.client == request.args.get("client")).order_by(tabTask.c.id.asc())).all():
                client = make_dict(r._mapping)
                tasks.append(client)
        else:
            for r in db.execute(tabTask.select().order_by(tabTask.c.id.asc())).all():
                client = make_dict(r._mapping)
                tasks.append(client)
        db.close()
        return {
            "code": 0,
            "message": "return a list of tasks",
            "data": tasks
        }

    elif request.method == "POST":
            db = get_db()
            ids = []
            if len(request.data) > 1:

                ids = request.json.get("id", [])
                if isinstance(ids, int):
                    ids = [ids]
                action = request.json.get("action")

            elif len(request.form) > 0:
                ids = request.form.getlist("id")
                action = request.form.get("action")

            if len(ids) == 0:
                return {"code": -1, "message": "no task id provided"}
            if action == "delete":
                for id in ids:
                    db.execute(
                        tabTask.delete().where(tabTask.c.id == id)
                    )
                    db.commit()
                return {"code": 0, "message": f"task id={ids} deleted"}

            if action == "duplicate":
                newids = []
                for id in ids:
                    # Fetch old task info
                    row = db.query(tabTask.c.client, tabTask.c.command, tabTask.c.title, tabTask.c.env).where(tabTask.c.id == id).first()
                    if row == None:
                        return {"code": -1, "action": action, "message": f"repeat task {id=} fail.", "data": {}}
                    max_id = db.execute(tabTask.select().order_by(tabTask.c.id.desc()).limit(1)).first()

                    # Create a task, id is auto increament
                    result = db.execute(
                        tabTask.insert().values(
                            id=str(int(max_id[0])+1),
                            client=row[0],
                            command=row[1],
                            status="QUEUE",
                            title=row[2],
                            env=row[3],
                            created_time=datetime.datetime.now(), 
                        )
                    )
                    newid = result.inserted_primary_key[0]
                    db.commit()

                    newids.append(newid)

                return {"code": 0, "message": f"duplicate task id={ids} to newids={newids}"}

            return {"code": -2, "message": f"action={action} not supported"}

@bp_api_task.route("/pure", methods=['GET', 'POST'])
def api_task_list_pure() -> dict:
    '''
    return a list of tasks
    '''
    tasks = []
    db = get_db()

    for r in db.execute(tabTask.select().order_by(tabTask.c.id.asc())).all():
        client = make_dict(r._mapping)
        tasks.append(client)
    db.close()
    return {
        "code": 0,
        "message": "return a list of tasks",
        "data": tasks
    }

@bp_api_task.route("/<id>", endpoint="view", methods=['GET', 'POST'])
def api_task_view(id):
    db = get_db()
    row = db.query(tabTask.c).where(tabTask.c.id == id).first()

    if row == None:
        return {"code": -1, "message": f"task {id} not found"}
    else:
        retdict = make_dict(row._mapping)
    return retdict

@bp_api_task.route("/create", endpoint="create", methods=["POST"])
def api_task_create():
    '''
    Create task
    '''
    db = get_db()
    kw = {}
    if request.method == "POST":
        if len(request.data):
            for k, v in request.json.items():
                kw[k] = v
        if len(request.form):
            for k, v in request.form.items():
                kw[k] = v
        max_id = db.execute(tabTask.select().order_by(tabTask.c.id.desc()).limit(1)).first()
        if max_id:
            id = int(max_id[0]) + 1
        else:
            id = 10000
        if "env" not in kw:
            kw["env"] = ""
        result = db.execute(
            tabTask.insert().values(
                id=str(id),
                client=kw["client"],
                status="QUEUE",
                title=kw["title"],
                command=kw["command"],
                created_time=datetime.datetime.now(),
                env=kw["env"],
            )
        )
        db.commit()
        db.close()

        return redirect(url_for("task.index"))