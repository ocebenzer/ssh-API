from flask import Flask, request

from utils import get_keys, ssh_connect, ssh_disconnect, ssh_run, json_response

app = Flask(__name__)

@app.route("/")
def route():
    routes = {
        "/run": {
            "description": "run a command in a machine through ssh",
            "headers": {
                "command": "command to be run",
                "token": "token of the machine",
            },
            "response": {
                "stdin": "standart input during the execution of ssh",
                "stdout": "standart output during the execution of ssh",
                "stderr": "standart error during the execution of ssh",
            },
        },
        "/connect": {
            "description": "register a machine to get a token",
            "headers": {
                "ip": "machine ip",
                "username": "username to be used in ssh",
                "password": "password to be used in ssh",
            },
            "response": {
                "duration": "timeout duration for the token",
                "token": "token of the machine",
            },
        },
        "/disconnect": {
            "description": "disconnect your machine's ssh connection",
            "headers": {
                "token": "token of the machine",
            },
            "response": {
            },
        },
    }

    return json_response(routes)

@app.route("/run")
def run():
    [ command, token ] = get_keys(request.headers, "command", "token")

    ssh_response = ssh_run(command, token)

    if not ssh_response:
        return json_response({ "error": "invalid key" }, 400)

    return json_response(ssh_response)

@app.route("/connect")
def connect():
    [ ip, username, password ] = get_keys(request.headers, "ip", "username", "password")

    if not (ip and username and password):
        return json_response({ "error": "bad request" }, 400)

    connection_data = ssh_connect(ip, username, password)

    if not connection_data:
        return json_response({ "error": "server is full right now, try again later" }, 503)

    return json_response(connection_data, 201)

@app.route("/disconnect")
def disconnect():
    [ token ] = get_keys(request.headers, "token")
    ssh_disconnect(token)
    return json_response(status_code = 201)
