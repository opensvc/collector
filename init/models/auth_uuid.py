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
                 nodename=node,
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

            session.auth = Storage()
            session.auth.user = user
            session.auth.last_visit = request.now
            #self.auth = auth

            #db(db.nodes.nodename==node).select(db.nodes.nodename, db.nodes.team_responsible).first()
            #session.auth.user_id = session.auth.user.nodename
            return True
        except Exception as e:
            if not auth_is_user(node):
                _log('node.auth',
                     'node authentication error: %(e)s',
                     dict(e=str(e)),
                     nodename=node,
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
    q = db.nodes.nodename == auth.user.nodename
    try:
        return db(q).select(db.nodes.team_responsible).first().team_responsible
    except:
        return

def auth_node_group_id():
    q = db.nodes.nodename == auth.user.nodename
    q &= db.nodes.team_responsible == db.auth_group.role
    try:
        return db(q).select(db.auth_group.id).first().id
    except:
        return
