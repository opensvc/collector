def allowed_user_ids():
    """
    Return ids of the users member of the same groups than the requester.
    """
    q = db.auth_membership.group_id.belongs(user_org_group_ids())
    q &= db.auth_membership.group_id == db.auth_group.id
    q &= db.auth_group.role != "Everybody"
    rows = db(q).select(db.auth_membership.user_id)
    return [r.user_id for r in rows] + [auth.user_id]

def allowed_user_ids_q(table="auth_user"):
    """
    Return a DAL expression limiting the query to the users member of the
    same groups than the requester.
    """
    try:
        check_privilege("Manager")
        q = db[table].id > 0
    except:
        user_ids = allowed_user_ids()
        q = db[table].id.belongs(user_ids)
    return q

def user_id_q(id):
    """
    Return a DAL expression limiting the query to the user identified
    by id, being either email or a user_id.
    """
    if type(id) in (unicode, str) and "@" in id:
        q = db.auth_user.email == id
    elif id == "self":
        q = db.auth_user.id == auth.user_id
    else:
        q = db.auth_user.id == id
    return q

