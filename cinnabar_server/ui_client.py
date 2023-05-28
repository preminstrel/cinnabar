import re
from flask import Blueprint, g, redirect, render_template, request, url_for, flash, abort
from .api_client import api_client_list, api_client_view

bp_client = Blueprint('client', __name__, url_prefix='/client')

@bp_client.route("/", endpoint="index", methods=['GET', 'POST'])
def ui_client_list():
    clients = api_client_list()["data"]
    return render_template("client/client.list.html", clients=clients)


@bp_client.route("/<name>", endpoint="view", methods=['GET', 'POST'])
def ui_client_view(name):
    ret = api_client_view(name)
    if ret["code"] == 0:
        client = ret["data"]
    else:
        abort(404)

    red = request.args.get("redirect")
    if red != None:
        if red == "ssh":
            return redirect(f"ssh://{client['user']}@{client['ip']}")

        return redirect(request.path)

    return render_template(
        "client/client.view.html",
        client=client,
    )
