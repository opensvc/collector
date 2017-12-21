import gluon.contrib.simplejson as json
import logging

DATE_FMT = "%Y-%m-%d %H:%M:%S"

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
    if isinstance(d1, pydal.objects.Row):
        d1 = dict(d1)
    if isinstance(d2, pydal.objects.Row):
        d2 = dict(d2)
    for key in sorted(d2.keys()):
        if key not in d1:
            continue
        if d1[key] != d2[key]:
            if type(d1[key]) in (int, float):
                val1 = str(d1[key])
	    elif type(d1[key]) in (datetime.datetime,):
                val1 = d1[key].strftime(DATE_FMT)
            elif type(d1[key]) == str:
                val1 = unicode(d1[key], errors="ignore")
            else:
                val1 = d1[key]
            if type(d2[key]) in (int, float):
                val2 = str(d2[key])
	    elif type(d2[key]) in (datetime.datetime,):
                val2 = d2[key].strftime(DATE_FMT)
            else:
                val2 = d2[key]
            l.append("%s: %s => %s" % (key, val1, val2))
    return ", ".join(l)

def log_events(i):
    ws_send('log_change', {'id': i})

def _log(action, fmt, d, user=None, svc_id="", level="info", node_id=""):
    if user is None:
        user = user_name()
    if user in ("Unknown", "agent"):
        if node_id != "":
            user = "agent"
        elif svc_id != "":
            user = "agent"
    if hasattr(auth.user, "node_id") and node_id is "":
        node_id = auth.user.node_id
    if hasattr(auth.user, "svc_id") and svc_id is "":
        svc_id = auth.user.svc_id

    logger = logging.getLogger("web2py.app.init.log")
    logger.setLevel(logging.DEBUG)
    if level == "info":
        _logger = logger.info
    elif level == "warning":
        _logger = logger.warning
    elif level == "error":
        _logger = logger.error
    else:
        _logger = None
    if _logger:
         s = ""
         if user:
             s += "user[%s] " % user
         if node_id != "":
             s += "node[%s] " % node_id
         if svc_id != "":
             s += "svc[%s] " % svc_id
         s += "action[%s] " % str(action)
         try:
             s += fmt % d
             _logger(s)
         except Exception:
             pass

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
