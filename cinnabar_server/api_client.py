import json
import os
from flask import (Blueprint, Markup, Response, current_app, g, redirect, request, stream_with_context)
from .database import get_db, tabClient, make_dict

CLIENT_TIMEOUT = 3600

bp_api_client = Blueprint('api_client', __name__, url_prefix='/api/client')

@bp_api_client.route("/", endpoint="list", methods=['GET', 'POST'])
def api_client_list() -> dict:
    '''
    return a list of clients
    '''
    #api_client_update()
    clients = []
    db = get_db()

    for r in db.execute(tabClient.select().order_by(tabClient.c.name.asc())).all():
        client = make_dict(r._mapping)
        clients.append(client)
    db.close()
    for client in clients:
        if client['gpu']:
            gpu_status = ""
            for gpu in client['gpu']:
                gpu_info = client['gpu'][gpu]
                memory_used = gpu_info['memory_used']
                memory_total = gpu_info['memory_total']
                util = gpu_info['utilization']
                gpu_status += f"<i class=\"bi bi-nvidia text-success\"></i> {memory_used}GB/{memory_total}GB | Util {util}%\n"
            client['gpu'] = gpu_status
        if client['memory']:
            client['memory'] = f"{client['memory']['used_memory']}GB/{client['memory']['total_memory']}GB"
    return {
        "code": 0,
        "message": "return a list of clients",
        "data": clients
    }

@bp_api_client.route("/<name>", endpoint="view", methods=['GET', 'POST'])
def api_client_view(name):
    '''
    GET:    return infomation of the client
    POST:   control the client
    '''

    db = get_db()
    row = db.query(tabClient.c).where(tabClient.c.name == name).first()

    if row == None:
        return {"code": -1, "message": f"client {name} not found"}
    else:
        retdict = make_dict(row._mapping)

    if request.method == "POST":
        pass

    else:
        return {
            "code": 0,
            "message": "api_client get suceess",
            "url": request.url,
            "data": retdict,
        }
