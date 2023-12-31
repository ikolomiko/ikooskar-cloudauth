#!/usr/bin/env python3
# type: ignore[assignment]

from flask import Flask, request, Response
from http import HTTPStatus
from typing import Optional
from model import LicensedUser, DemoUser, init_db
from datetime import datetime
import traceback

init_db()
app = Flask(__name__)


def query_licensed(serial: str, mac: str) -> Response:
    try:
        user: Optional[LicensedUser] = LicensedUser.get_or_none(
            LicensedUser.serial == serial
        )

        # The serial key was not found in the db
        if not user:
            return Response("not found", HTTPStatus.NOT_FOUND)  # code 404

        ip = get_ip_address()

        # Activation
        if user.mac is None and user.ip is None:
            user.mac = mac.strip()
            user.ip = ip
            user.activation_date = datetime.now()
            user.save()
            return Response("activated", HTTPStatus.CREATED)  # code 201

        # At least one of the request params match the ones in the db
        if user.mac == mac or user.ip == ip:
            return Response("success", HTTPStatus.OK)  # code 200

        # The given serial key exists in the db but with a different set of mac and ip addresses
        return Response("unauthorized", HTTPStatus.UNAUTHORIZED)  # code 401

    except Exception:
        traceback.print_exc()
        # Other error
        return Response("other error", HTTPStatus.INTERNAL_SERVER_ERROR)  # code 500


def query_demo(mac: str, remainings: int) -> Response:
    try:
        if remainings < 0:
            remainings = 0

        user: Optional[DemoUser] = DemoUser.get_or_none(DemoUser.mac == mac)

        # New demo user
        if not user:
            DemoUser.create(mac=mac, remainings=3)
            return Response("3", HTTPStatus.CREATED)  # activated, code 201

        # No remainings were left, end of demo
        if user.remainings <= 0:
            return Response("0", HTTPStatus.FORBIDDEN)  # code 403

        # Decrement the remainings in the db
        if remainings < user.remainings:
            user.remainings = remainings
            user.save()

        # Return the current remainings of the user (this branch can also can imply reactivation)
        return Response(str(user.remainings), HTTPStatus.OK)  # code 200

    except Exception:
        traceback.print_exc()
        # Other error
        return Response("other error", HTTPStatus.INTERNAL_SERVER_ERROR)  # code 500


def get_ip_address() -> str:
    if request.environ.get("HTTP_X_FORWARDED_FOR") is None:
        return str(request.environ["REMOTE_ADDR"])
    else:
        return str(request.environ["HTTP_X_FORWARDED_FOR"])


@app.route("/api/v4/license", methods=["GET", "POST"])
def licensed_user() -> Response:
    req_serial: Optional[str] = request.args.get("serial", None)
    req_mac: Optional[str] = request.args.get("mac", None)

    if (req_serial is None) or (req_mac is None):
        return Response("bad request", HTTPStatus.BAD_REQUEST)  # code 400

    return query_licensed(req_serial, req_mac)


@app.route("/api/v4/demo", methods=["GET", "POST"])
def demo_user() -> Response:
    req_remainings: Optional[int] = request.args.get("remainings", None, int)
    req_mac: Optional[str] = request.args.get("mac", None)

    if (req_remainings is None) or (req_mac is None):
        return Response("bad request", HTTPStatus.BAD_REQUEST)  # code 400

    return query_demo(req_mac, req_remainings)


@app.route("/api/v4/ip", methods=["GET"])
def ip_address() -> Response:
    return Response(get_ip_address(), HTTPStatus.OK)  # code 200


if __name__ == "__main__":
    app.run()
