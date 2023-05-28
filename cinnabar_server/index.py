from flask import Blueprint, render_template

bp_index = Blueprint('index', __name__, url_prefix='/')

@bp_index.route("/", endpoint="index", methods=['GET', 'POST'])
def ui_index():
    return render_template("index.html")