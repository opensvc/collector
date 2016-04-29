def node_svc_id(node_id, svcname):
    if svcname is None:
        return ""
    svcname = svcname.strip("'")
    if svcname == "" or svcname is None:
        return ""
    q = db.services.svcname == svcname
    q &= db.services.svc_app == db.apps.app
    q &= db.apps.id == db.apps_responsibles.app_id
    q &= db.apps_responsibles.group_id.belongs(node_responsibles(node_id))
    rows = db(q).select(db.services.svc_id)
    if len(rows) > 1:
        raise Exception("multiple services found matching the name in the node's responsability zone")
    if len(rows) == 0:
        return create_svc(node_id, svcname)
    return rows.first().svc_id

def create_svc(node_id, svcname):
    node = get_node(node_id)
    data = {
      "svcname": svcname,
      "svc_app": node.app,
      "svc_id": get_new_svc_id(),
      "updated": datetime.datetime.now()
    }
    db.services.insert(**data)
    return data["svc_id"]

def node_responsibles(node_id):
    q = db.nodes.node_id == node_id
    q &= db.apps.app == db.nodes.app
    q &= db.apps_responsibles.app_id == db.apps.id
    q &= db.auth_group.id == db.apps_responsibles.group_id
    rows = db(q).select(db.auth_group.id)
    return [r.id for r in rows]

def node_responsibles_apps(node_id):
    groups = node_responsibles(node_id)
    q = db.apps_responsibles.group_id.belongs(groups)
    q &= db.apps_responsibles.app_id == db.apps.id
    rows = db(q).select(db.apps.app)
    return [r.app for r in rows]

def auth_to_node_id(auth):
    q = db.auth_node.uuid == auth[0]
    q &= db.auth_node.nodename == auth[1].strip("'")
    row = db(q).select(db.auth_node.node_id).first()
    if row is None:
        return None
    return row.node_id

def common_responsible(node_id=None, svc_id=None, app=None, user_id=None):
    try:
        if "Manager" in user_groups():
            return True
    except:
        pass
    if node_id is None and svc_id is None and app is None and user_id is None:
        return False
    q = db.auth_group.id > 0
    if node_id:
        q &= db.nodes.node_id == node_id
        q &= db.nodes.app == db.apps.app
    if svc_id:
        q &= db.services.svc_id == svc_id
        q &= db.apps.app == db.services.svc_app
    if app:
        q &= db.apps.app == app
    if user_id and not "Manager" in user_groups():
        q &= db.auth_membership.user_id == user_id
        q &= db.apps_responsibles.group_id == db.auth_membership.group_id

    q &= db.apps.id == db.apps_responsibles.app_id
    q &= db.apps_responsibles.group_id == db.auth_group.id
    if db(q).count() > 0:
        return True
    return False

def check_auth(node, uuid):
    q = db.auth_node.nodename == node
    q &= db.auth_node.uuid == uuid
    n = db(q).count()
    if n != 1:
        q = db.auth_node.nodename == node
        n = db(q).count()
        if n == 0:
            raise Exception("agent %s not registered"%node)
        else:
            raise Exception("agent authentication error")

def auth_uuid(fn):
    def new(*args, **kwargs):
        try:
            if 'auth' in kwargs:
                uuid, node = kwargs['auth']
            else:
                uuid, node = args[-1]
        except:
            raise Exception("no authentication data found in the request")

        try:
            check_auth(node, uuid)
        except Exception as e:
            _log('node.auth',
                 'node authentication error: %(e)s',
                 dict(e=str(e)),
                 node_id=auth_to_node_id(kwargs['auth']),
                 user="feed",
                 level="warning")
            raise
        return fn(*args, **kwargs)

    return new

def node_auth():
    """
    auth.settings.login_methods.append(node_auth())
    """

    def node_login_aux(node, uuid):
        try:
            check_auth(node, uuid)
            from gluon.storage import Storage
            user = Storage()
            user.id = -1
            user.nodename = node
            user.node_id = auth_to_node_id([uuid, node])

            session.auth = Storage()
            session.auth.user = user
            session.auth.last_visit = request.now
            #self.auth = auth

            return True
        except Exception as e:
            if not auth_is_user(node):
                _log('node.auth',
                     'node authentication error: %(e)s',
                     dict(e=str(e)),
                     node_id=auth_to_node_id([uuid, node]),
                     user="feed",
                     level="warning")
            return False
    return node_login_aux

def auth_is_user(email):
    if db(db.auth_user.email==email).select().first() is None:
        return False
    return True

def auth_is_node():
    if hasattr(auth.user, "nodename"):
        return True
    return False

def auth_node_group():
    q = db.nodes.node_id == auth.user.node_id
    try:
        return db(q).select(db.nodes.team_responsible).first().team_responsible
    except:
        return

def auth_node_group_id():
    q = db.nodes.node_id == auth.user.node_id
    q &= db.nodes.team_responsible == db.auth_group.role
    try:
        return db(q).select(db.auth_group.id).first().id
    except:
        return
