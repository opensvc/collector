import gluon.contrib.simplejson as json

def _log(action, fmt, d, user=None, svcname=None, nodename=None):
    if user is None:
        user = user_name()
    vars = ['log_action',
            'log_fmt',
            'log_dict',
            'log_user',
            'log_svcname',
            'log_nodename']
    vals = [action,
            fmt,
            json.dumps(d),
            user,
            svcname,
            nodename]
    generic_insert('log', vars, vals)

