import jwt
import datetime


def encode_auth_token(imei):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=10, seconds=5),
            'iat': datetime.datetime.utcnow(), 'sub': imei
        }
        return jwt.encode(payload, 'SECRETKEY@123', algorithm='HS256').decode('ascii')
    except Exception as e:
        return e


def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, 'SECRETKEY@123')
        return payload['sub'], 200
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.', 401
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.', 401


def check_auth(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return ("fail", "Please provide a valid auth token"), 401

    try:
        auth_token = auth_header.split(" ")[1]
    except IndexError:
        return ("fail", "Bearer token malformed"), 400

    return decode_auth_token(auth_token)


def is_event_type_unknown(ev_type):
    if ev_type not in ['VIBRATION', 'OVERSPEED', 'CRASH',
                       'HARD_ACCELERATION', 'HARD_BRAKE', 'SHARP_TURN']:
        return True

    return False

