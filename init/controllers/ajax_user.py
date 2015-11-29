def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

@service.json
def set_user_group():
    user_id = request.vars.user_id
    group_id = request.vars.group_id
    membership = request.vars.membership

    if 'Manager' not in user_groups():
        return {"err": "Not allowed"}
    if user_id is None:
        return {"err": "user id not specified"}
    if group_id is None:
        return {"err": "group id not specified"}

    q = db.auth_group.id == group_id
    g = db(q).select().first()
    if g is None:
        return {"err": "group id does not exist"}
    g = g.role

    q = db.v_users.id == user_id
    u = db(q).select(db.v_users.fullname).first()
    if u is None:
        return {"err": "user id does not exist"}
    u = u.fullname

    if membership == "true":
        db.auth_membership.insert(
          user_id=user_id,
          group_id=group_id
        )
        _log('users.group.attach',
             'attached group %(g)s to user %(u)s',
             dict(g=g, u=u))
    elif membership == "false":
        q = db.auth_membership.user_id == user_id
        q &= db.auth_membership.group_id == group_id
        db(q).delete()
        _log('users.group.detach',
             'detached group %(g)s from user %(u)s',
             dict(g=g, u=u))
    else:
        return {"err": "Unsupported membership target value"}

    return {}
