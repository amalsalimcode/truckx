import os

import db
import json
import _thread
from flask import send_file
from flask_cors import CORS
from common import encode_auth_token
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, render_template
from common import is_event_type_unknown, check_auth, decode_auth_token


server = Flask(__name__)
socketio = SocketIO(server)
CORS(server)


@server.route("/", methods=['POST'])
def main():

    post_data = json.loads(request.data.decode('ascii'))
    r_type = post_data.get("type", "").lower()

    if r_type == "login":
        return handle_login(post_data)

    resp, status = check_auth(request)
    if status != 200:
        return resp, status

    imei = resp
    if r_type == "alarm":
        return handle_alarm(post_data, imei)


@server.route("/videoupload", methods=['POST'])
def video_upload():
    resp, status = check_auth(request)
    if status != 200:
        return resp, status

    post_data = json.loads(request.data.decode('ascii'))
    handle_video(post_data)

    return 'Done', 200


@server.route("/fetchvideo", methods=['GET'])
def fetch_video():

    imei = request.args.get('imei')
    file_name = request.args.get('filename')
    file_path = os.path.join('media/' + str(imei) + "/", secure_filename(file_name))

    return send_file(file_path, attachment_filename=file_name)


@server.route("/alarm", methods=['GET'])
def alarm():
    st_dt = request.args.get("start_date")
    end_dt = request.args.get("end_date")
    alarm_type = request.args.get("alarm_type")

    if st_dt and end_dt and alarm_type:
        alarms = db.get_alarm_from_args(st_dt, end_dt, alarm_type.upper())
    else:
        alarms = db.get_alarms()

    return jsonify({"alarms": alarms}, 200)


@server.route("/dashcam", methods=['POST'])
def send_dashcam_request():
    post_data = json.loads(request.data.decode('ascii'))
    send_dashcam_req_soc(post_data.get("imei"), post_data.get("command"))
    return "Done", 200


def handle_video(p):
    # create folder if this is first time media being received
    os.makedirs(os.path.join('media/' + str(p.get('imei'))), exist_ok=True)

    file_path = os.path.join('media/' + str(p.get('imei')) + "/", secure_filename(p.get('filename')))

    f = open(file_path, 'w')
    f.write(p.get('data'))
    f.close()


def handle_login(post_data):
    imei = post_data.get("imei")
    token = encode_auth_token(imei)
    return render_template("index.html", **{'token': token})


def handle_alarm(p, imei):
    if is_event_type_unknown(p.get('alarm_type')):
        return jsonify({"error": "unknown alarm type"}), 400

    al_id = db.create_alarm(imei, p.get('alarm_type'), p.get("alarm_time", ""),
                            p.get("latitude", ""), p.get("longitude"))

    for file_name in p.get("file_list"):
        db.create_file(al_id, file_name)

    return 'Done', 200


socket_connections_sid = {}
socket_connections_imei = {}

@socketio.on('connect')
def test_connect():
    token = request.args.get('token')
    imei, status = decode_auth_token(token)
    if status != 200:
        raise ConnectionRefusedError('unauthorized')

    socket_connections_imei[imei] = request.sid
    socket_connections_sid[request.sid] = imei


@socketio.on('location update')
def location_update(msg):
    imei = socket_connections_imei[request.sid]
    db.create_location(imei, msg['location_time'], msg['latitude'], msg['longitude'])


def send_dashcam_req_soc(imei, command):
    sid = socket_connections_sid[imei]
    msg = {"type": "COMMAND", "imei": imei, "command": command}
    emit("command request", msg, room=sid)


@socketio.on('command response')
def dashcam_command_response(msg):
    print("here is the dash cam response to sent command", msg)


if __name__ == "__main__":
    server.config['SECRET_KEY'] = 'ELSA#@#SECRETKEY$%@999'
    db.init_table()
    _thread.start_new_thread(lambda: socketio.run(server), ())
    server.run(port=5005)
