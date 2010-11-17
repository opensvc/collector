import gluon.contrib.simplejson as json

def _log(action, fmt, d, user=None):
    if user is None:
        user = user_name()
    vars = ['log_action',
            'log_fmt',
            'log_dict',
            'log_user']
    vals = [action,
            fmt,
            json.dumps(d),
            user]
    generic_insert('log', vars, vals)
