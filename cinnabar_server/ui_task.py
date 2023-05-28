import re
from flask import Blueprint, g, redirect, render_template, request, url_for, flash, abort

from .database import get_db, tabClient, tabTask, make_dict
from .api_task import api_task_list, api_task_view
from .api_client import api_client_list, api_client_view

bp_task = Blueprint('task', __name__, url_prefix='/task')

@bp_task.route("/", endpoint="index", methods=['GET', 'POST'])
def ui_task_list():
    if request.method == "GET":
        tasks = api_task_list()["data"]
        return render_template("task/task.list.html", tasks=tasks)

@bp_task.route("/create", endpoint="create", methods=['GET', 'POST'])
def ui_task_create():
    if request.method == "POST":
        pass

    elif request.method == "GET":
        clients = api_client_list()['data']
        return render_template("task/task.create.html", clients=clients)
    
@bp_task.route("/<id>", endpoint="view", methods=['GET', 'POST'])
def ui_task_view(id):
    task = api_task_view(id)
    log_path = task['log']
    log = ''
    if log_path:
        with open(log_path, 'r') as f:
            log = f.read()
    task['logfile'] = log
    return render_template("task/task.view.html", task=task)