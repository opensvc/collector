from gluon.contrib.websocket_messaging import websocket_send

websocket_url = "https://dbopensvc:8889"
websocket_key = "magix123"

def _websocket_send(msg, group="generic"):
    try:
        websocket_send(websocket_url, msg, websocket_key, group)
    except:
        pass
