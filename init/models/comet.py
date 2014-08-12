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
        __websocket_send(msg, group)
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
                         immediate=True,
                         start_time=start)


def ___websocket_send(msg, group="generic"):
    websocket_send(websocket_url, msg, websocket_key, group)
