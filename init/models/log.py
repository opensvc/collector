import simplejson

def _log(action, fmt, d, user=None):
    if user is None:
        user = user_name()
    vars = ['log_action',
            'log_fmt',
            'log_dict',
            'log_user']
    vals = [action,
            fmt,
            simplejson.dumps(d),
            user]
    generic_insert('log', vars, vals)
