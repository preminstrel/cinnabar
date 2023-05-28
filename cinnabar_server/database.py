import json
import os
import re
from datetime import datetime
import click
from flask import __version__, current_app, Flask
from sqlalchemy import (CHAR, INTEGER, DOUBLE, TEXT, Column, MetaData, Table, create_engine, text, Engine)
from sqlalchemy.orm import scoped_session, sessionmaker, Session

metaCinnabar = MetaData()

tabClient = Table(
    "client", metaCinnabar,
    Column('name', TEXT(), primary_key=True),
    Column('hostname', TEXT()),
    Column('status', TEXT()),
    Column('ip', TEXT()),
    Column('user', TEXT()),
    Column('timestamp', TEXT()),
    Column('gpu', TEXT()),
    Column('cpu', TEXT()),
    Column('memory', TEXT()),
    Column('os', TEXT()),
    Column('condaEnvs', TEXT()),
)

tabTask = Table(
    "task", metaCinnabar,
    Column('id', TEXT(), primary_key=True),
    Column('client', TEXT()),
    Column('status', TEXT()),
    Column('title', TEXT()),
    Column('command', TEXT()),
    Column('true_command', TEXT()),
    Column('pid', TEXT()),
    Column('created_time', TEXT()),
    Column('start_time', TEXT()),
    Column('end_time', TEXT()),
    Column('result', TEXT()),
    Column('log', TEXT()),
    Column('env', TEXT()),
    Column('error', TEXT()),
)

def make_dict(row, json_cols=['gpu', 'memory']):
    '''
    return a decoded dict from `sqlalchemy.engine.row.Row`
    '''
    if not getattr(row, "items", None):
        row = row._mapping

    ret = {}
    for k, v in dict(row).items():
        if k in json_cols:
            try:
                ret[k] = json.loads(v)
            except:
                ret[k] = v
        else:
            ret[k] = v if v not in [float("inf") or float("-inf")] else None
    return ret


def get_db() -> Session:
    return current_app.db


def get_engine() -> Engine:
    return current_app.engine


@click.command('init_db')
def init_db():
    '''
    Init database
    '''
    engine = get_engine()
    tabClient.create(engine, checkfirst=True)
    tabTask.create(engine, checkfirst=True)


@ click.command('clean_db')
def clean_db():
    '''
    Clean database (Danger)
    '''
    engine = get_engine()
    confirm = input(
        "you are about to clean the database, input 'delete' to comfirm: ")
    if confirm == "delete":
        metaCinnabar.drop_all(engine, [tabClient, tabTask])

def init_app_db(app: Flask):
    '''
    init database object for app
    '''

    db_url = app.config["DATABASE"]


    if re.match(r"sqlite://", db_url):
        app.engine = create_engine(db_url)
    else:
        app.engine = create_engine("sqlite:///" + db_url)

    # Create Database Session (this is thread safe)
    app.db = scoped_session(
        sessionmaker(autoflush=True, bind=app.engine)
    )

    # Auto init database
    tabClient.create(app.engine, checkfirst=True)
    tabTask.create(app.engine, checkfirst=True)

    # Register commands
    app.cli.add_command(init_db)
    app.cli.add_command(clean_db)

    return app.db