import gluon.contrib.simplejson as json

def log_events(i):
    l = {
      'event': 'log_change',
      'data': {'id': i},
    }
    _websocket_send(event_msg(l), schedule=False)

def _log(action, fmt, d, user=None, svcname=None, nodename=None, level="info"):
    if user is None:
        user = user_name()
    db.log.insert(
      log_action=action,
      log_fmt=fmt,
      log_dict=json.dumps(d),
      log_user=user,
      log_svcname=svcname,
      log_nodename=nodename,
      log_level=level
    )
    i = db.executesql("SELECT LAST_INSERT_ID()")[0][0]
    db.commit()
    log_events(i)
