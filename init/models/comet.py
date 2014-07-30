from gluon.contrib.websocket_messaging import websocket_send
import json
import uuid

websocket_url = "http://127.0.0.1:8889"
websocket_key = "magix123"

def event_msg(data):
    _data = {
      'uuid': uuid.uuid1().hex,
    }
    if type(data) == dict:
        _data['data'] = [data]
    elif type(data) == list:
        _data["data"] = data
    return json.dumps(_data)

def _websocket_send(msg, group="generic"):
    try:
        websocket_send(websocket_url, msg, websocket_key, group)
    except:
        pass
