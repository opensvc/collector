import gluon.contrib.simplejson as json

def beautify_data(d):
    l = []
    for key in sorted(d.keys()):
        if type(d[key]) in (int, float):
            val = str(d[key])
        else:
            val = d[key]
        l.append("%s: %s" % (key, val))
    return ", ".join(l)

def beautify_change(d1, d2):
    l = []
    for key in sorted(d2.keys()):
        if key not in d1:
            continue
        if d1[key] != d2[key]:
            if type(d1[key]) in (int, float):
                val1 = str(d1[key])
            elif type(d1[key]) == str:
                val1 = unicode(d1[key], errors="ignore")
            else:
                val1 = d1[key]
            if type(d2[key]) in (int, float):
                val2 = str(d2[key])
            else:
                val2 = d2[key]
            l.append("%s: %s => %s" % (key, val1, val2))
    return ", ".join(l)

def log_events(i):
    l = {
      'event': 'log_change',
      'data': {'id': i},
    }
    _websocket_send(event_msg(l), schedule=False)

def _log(action, fmt, d, user=None, svcname=None, nodename=None, level="info"):
    if user is None:
        user = user_name()
    if user in ("Unknown", "agent"):
        if nodename is not None:
            user = nodename
        elif svcname is not None:
            user = svcname
    if user == "agent" and nodename is None:
        nodename = auth.user.nodename
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
    table_modified("log")
    log_events(i)
