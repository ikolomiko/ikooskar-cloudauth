#!/usr/bin/env python3

from datetime import datetime
from peewee import SqliteDatabase, TextField, Model, IntegerField, DateTimeField
from pathlib import Path

Path("./data").mkdir(parents=True, exist_ok=True)
db = SqliteDatabase("data/database.db")


class LicensedUser(Model):
    serial = TextField(primary_key=True, unique=True, null=False)
    mac = TextField(null=True, default=None)
    ip = TextField(null=True, default=None)
    created_date = DateTimeField(default=datetime.now)

    class Meta:
        database = db


class DemoUser(Model):
    mac = TextField(primary_key=True, unique=True, null=False)
    remainings = IntegerField(null=False, default=3)
    created_date = DateTimeField(default=datetime.now)

    class Meta:
        database = db


def init_db():
    LicensedUser.create_table()
    DemoUser.create_table()
