from gluon.contrib.websocket_messaging import websocket_send
from applications.init.modules.aconfig import config_get
import json
import hashlib

dbopensvc_host = config_get('dbopensvc_host', '127.0.0.1')
websocket_host = config_get("websocket_host", dbopensvc_host)
websocket_url = config_get("websocket_url", "http://%s:8889" % websocket_host)
websocket_key = config_get("websocket_key", "magix123")

def event_msg(data):
    uuid = hashlib.md5()
    uuid.update(json.dumps(data))
    _data = {
      'uuid': uuid.hexdigest(),
    }
    if type(data) == dict:
        _data['data'] = [data]
    elif type(data) == list:
        _data["data"] = data
    return json.dumps(_data)

def _websocket_send(msg, group="generic"):
    websocket_send(websocket_url, msg, websocket_key, group)

def ws_send(event, data={"a": "b"}):
    l = {
      'event': event,
      'data': data,
    }
    _websocket_send(event_msg(l))

