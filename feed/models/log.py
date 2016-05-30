import gluon.contrib.simplejson as json

def get_node(node_id):
    q = db.nodes.node_id == node_id
    return db(q).select().first()

def get_nodename(node_id):
    node = get_node(node_id)
    if node is None:
        s = str(node_id)
    else:
        s = node.nodename + " in app " + node.app
    return s

def beautify_data(d):
    l = []
    for key in sorted(d.keys()):
        if type(d[key]) in (int, float):
            val = str(d[key])
        else:
            val = d[key]
        l.append("%s: %s" % (key, val))
    return ", ".join(l)

def log_events(i):
    l = {
      'event': 'log_change',
      'data': {'id': i},
    }
    _websocket_send(event_msg(l))

def _log(action, fmt, d, user=None, svc_id=None, node_id=None, level="info"):
    if user is None:
        user = 'agent'
    db.log.insert(
      log_action=action,
      log_fmt=fmt,
      log_dict=json.dumps(d),
      log_user=user,
      svc_id=svc_id,
      node_id=node_id,
      log_level=level
    )
    i = db.executesql("SELECT LAST_INSERT_ID()")[0][0]
    db.commit()
    table_modified("log")
    log_events(i)
