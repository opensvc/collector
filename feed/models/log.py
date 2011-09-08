import gluon.contrib.simplejson as json

def _log(action, fmt, d, user=None, svcname=None, nodename=None, level="info"):
    if user is None:
        user = 'feed'
    vars = ['log_action',
            'log_fmt',
            'log_dict',
            'log_user',
            'log_svcname',
            'log_nodename',
            'log_level']
    vals = [action,
            fmt,
            json.dumps(d),
            user,
            svcname,
            nodename,
            level]
    generic_insert('log', vars, vals)

