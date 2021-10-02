from flask import jsonify, make_response
from paramiko.client import AutoAddPolicy, SSHClient

import time
import _thread
from uuid import uuid4

sessions = {}

def json_response(dict={}, status_code=200):
    return make_response(jsonify(dict), status_code)

def get_keys(d, *keys):
    return [ d[k] if k in d else None for k in keys ]

def ssh_connect(ip, username, password, duration=60):
    if len(sessions) > 3:
        return None

    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(ip, 22, username, password)

    token = str(uuid4())
    sessions[token] = client
    print("sessions", sessions)

    connection_data = {
        "token": token,
        "duration": duration,
    }

    _thread.start_new_thread(ssh_timeout, connection_data.values())
    connection_data["dir"]= ssh_directory(client)
    return connection_data

def ssh_timeout(token, duration):
    time.sleep(duration)
    ssh_disconnect(token)

def ssh_disconnect(token):
    client = sessions.pop(token, None)
    client.close()
    print("sessions", sessions)

def ssh_run(command, token):
    try:
        client = sessions[token]
    except KeyError:
        return None

    stdin, stdout, stderr = client.exec_command(command)

    response = {
        "stdin": read_file(stdin),
        "stdout": read_file(stdout),
        "stderr": read_file(stderr),
        "dir": ssh_directory(client)
    }
    return response

def read_file(file):
    try:
        return file.read().decode("utf-8")
    except IOError:
        return ""

def ssh_directory(client):
    directory = client.exec_command('pwd')[1]
    return read_file(directory)