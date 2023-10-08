#!/usr/bin/env python3

from flask import Flask, request, Response
from http import HTTPStatus
from typing import Optional
from model import LicensedUser, DemoUser, init_db
import traceback


app = Flask(__name__)


def query_licensed(serial: str, mac: str, ip: str) -> Response:
    try:
        user: Optional[LicensedUser] = LicensedUser.get_or_none(
            LicensedUser.serial == serial
        )

        # The serial key was not found in the db
        if not user:
            return Response("not found", HTTPStatus.NOT_FOUND)  # code 404

        # Activation
        if user.mac is None and user.ip is None:
            user.mac = mac.strip()  # type: ignore[assignment]
            user.ip = ip.strip()  # type: ignore[assignment]
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
            user.remainings = remainings  # type: ignore[assignment]
            user.save()

        # Return the current remainings of the user (this branch can also can imply reactivation)
        return Response(str(user.remainings), HTTPStatus.OK)  # code 200

    except Exception:
        traceback.print_exc()
        # Other error
        return Response("other error", HTTPStatus.INTERNAL_SERVER_ERROR)  # code 500


@app.route("/v4/license", methods=["GET", "POST"])
def licensed_user() -> Response:
    req_serial: Optional[str] = request.args.get("serial", None)
    req_mac: Optional[str] = request.args.get("mac", None)
    req_ip: Optional[str] = request.args.get("ip", None)

    if (not req_serial) or (not req_mac) or (not req_ip):
        return Response("bad request", HTTPStatus.BAD_REQUEST)  # code 400

    return query_licensed(req_serial, req_mac, req_ip)


@app.route("/v4/demo", methods=["GET", "POST"])
def demo_user() -> Response:
    req_remainings: Optional[int] = request.args.get("remainings", None, int)
    req_mac: Optional[str] = request.args.get("mac", None)

    if (req_remainings is None) or (not req_mac):
        return Response("bad request", HTTPStatus.BAD_REQUEST)  # code 400

    return query_demo(req_mac, req_remainings)


if __name__ == "__main__":
    init_db()
    app.run()
