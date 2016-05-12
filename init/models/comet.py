from gluon.contrib.websocket_messaging import websocket_send
import json
import hashlib

dbopensvc = config_get("dbopensvc", "dbopensvc")
websocket_url = config_get("websocket_url", "http://%s:8889" % dbopensvc)
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

def _websocket_send(msg, group="generic", schedule=False):
    try:
        if schedule:
            __websocket_send(msg, group)
        else:
            ___websocket_send(msg, group)
    except Exception as e:
        print e

def __websocket_send(msg, group="generic"):
    q_fn = "___websocket_send"
    q_args = [msg, group]
    task = scheduler.task_status(
      (db.scheduler_task.function_name == q_fn) & \
      (db.scheduler_task.args == json.dumps(q_args)) & \
      (db.scheduler_task.status == "QUEUED")
    )
    if task is not None:
        # already queued
        return
    start = datetime.datetime.now() + datetime.timedelta(seconds=1)
    scheduler.queue_task(q_fn, q_args,
                         group_name="fast",
                         start_time=start)
    # tasks submitted from tasks need a manual commit
    db.commit()


def ___websocket_send(msg, group="generic"):
    websocket_send(websocket_url, msg, websocket_key, group)

def ws_send(event, data={"a": "b"}):
    l = {
      'event': event,
      'data': data,
    }
    _websocket_send(event_msg(l))

