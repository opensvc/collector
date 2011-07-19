import gluon.contrib.simplejson as json

def _log(action, fmt, d, user=None, svcname=None, nodename=None):
    if user is None:
        user = 'feed'
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

def im_log(to, msg):
    import applications.init.modules.im as im
    try:
        im.gtalk().send(to, msg)
    except:
        pass

def im_log_node(node, msg):
    """ given a node name, lookup all responsibles flagged with
        im_notifications and a valid im config
    """
    q = db.nodes.nodename == node
    q &= db.nodes.team_responsible == db.auth_group.role
    q &= db.auth_group.id == db.auth_membership.group_id
    q &= db.auth_user.id == db.auth_membership.user_id
    q &= db.auth_user.im_notifications == True
    q &= db.auth_user.im_username != None
    users = db(q).select(db.auth_user.im_username)
    if len(users) == 0:
        return
    import applications.init.modules.im as im
    try:
        g = im.gtalk()
        for u in users:
            g.send(u.im_username, msg)
    except:
        pass

def im_log_svc(svc, msg):
    """ given a service name, lookup all responsibles flagged with
        im_notifications and a valid im config
    """
    q = db.services.svc_name == svc
    q &= db.services.svc_app == db.apps.app
    q &= db.apps.id == db.apps_responsibles.app_id
    q &= db.apps_responsibles.group_id == db.auth_membership.group_id
    q &= db.auth_user.id == db.auth_membership.user_id
    q &= db.auth_user.im_notifications == True
    q &= db.auth_user.im_username != None
    users = db(q).select(db.auth_user.im_username)
    if len(users) == 0:
        return
    import applications.init.modules.im as im
    try:
        g = im.gtalk()
        for u in users:
            g.send(u.im_username, msg)
    except:
        pass
