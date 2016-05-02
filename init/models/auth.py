import re
from gluon.tools import Auth

def get_node(node_id):
    q = db.nodes.node_id == node_id
    return db(q).select().first()

def get_nodename(node_id):
    node = get_node(node_id)
    if node is None:
        s = str(node_id)
    else:
        s = node.nodename + " in app " + node.app
    return s

def get_node_id(s):
    node = get_node(s)
    if node:
        return node.node_id
    q = db.nodes.nodename == s
    q = q_filter(q, app_field=db.nodes.app)
    nodes = db(q).select(db.nodes.node_id)
    if len(nodes) > 1:
        raise Exception("Multiple nodes match the '%s' nodename. Use a node id." % s)
    node = nodes.first()
    if node is None:
        raise KeyError("Node '%s' not found" % s)
    return node.node_id

def get_svc(svc_id):
    q = db.services.svc_id == svc_id
    return db(q).select().first()

def get_svcname(svc_id):
    svc = get_svc(svc_id)
    if svc is None:
        s = str(svc_id)
    elif svc.svc_app:
        s = svc.svcname + " in app " + svc.svc_app
    else:
        s = svc.svcname + " in no app"
    return s

def get_svc_id(s):
    svc = get_svc(s)
    if svc:
        return svc.svc_id
    q = db.services.svcname == s
    if auth_is_node():
        q &= db.services.svc_app.belongs(node_responsibles_apps(auth.user.node_id))
    else:
        q = q_filter(q, app_field=db.services.svc_app)
    svcs = db(q).select(db.services.svc_id)
    if len(svcs) > 1:
        raise Exception("Multiple services match the '%s' svcname. Use a service id." % s)
    svc = svcs.first()
    if svc is None:
        raise KeyError("Service '%s' not found" % s)
    return svc.svc_id

def check_privilege(privs):
    ug = user_groups()
    if 'Manager' in ug:
        return
    if type(privs) == list:
        privs = set(privs)
    else:
        privs = set([privs])
    if len(privs & set(ug)) == 0:
        raise Exception("Not authorized: user has no %s privilege" % ", ".join(privs))

def node_responsible(node_id=None):
    if node_id is None:
        raise Exception("node_responsible() must have a not None node_id parameter")
    q = db.nodes.node_id == node_id
    n = db(q).count()
    if n == 0:
        raise Exception("Node %s does not exist" % node_id)
    if "Manager" in user_groups():
        return
    q &= db.nodes.app.belongs(user_apps())
    n = db(q).count()
    if n == 0:
        raise Exception("Not authorized: user is not responsible for node %s" % node_id)

def svc_responsible(svc_id=None):
    if svc_id is None:
        raise Exception("svc_responsible() must have a not None svc_id parameter")
    q = db.services.svc_id == svc_id
    n = db(q).count()
    if n == 0:
        raise Exception("Service %s does not exist" % svc_id)
    if "Manager" in user_groups():
        return
    q &= db.services.svc_app.belongs(user_apps())
    n = db(q).count()
    if n == 0:
        raise Exception("Not authorized: user is not responsible for service %s" % svc_id)

def user_default_app(id=None):
    if id is None:
        id = auth.user_id
    q = db.apps_responsibles.group_id.belongs(user_group_ids())
    q &= db.apps_responsibles.app_id == db.apps.id
    q &= db.apps.app != ""
    q &= db.apps.app != None
    row = db(q).select(db.apps.app, orderby=db.apps.app).first()
    if row is None:
        return
    return row.app

def user_fullname(id):
    rows = db(db.auth_user.id==id).select()
    if len(rows) != 1:
        return None
    return ' '.join((rows[0].first_name, rows[0].last_name))

def group_role(id):
    rows = db(db.auth_group.id==id).select()
    if len(rows) != 1:
        return None
    return rows[0].role

def lib_get_group(id):
    try:
        id = int(id)
        return db.auth_group[id]
    except:
        q = db.auth_group.role == id
        return db(q).select().first()

def lib_group_id(role):
    rows = db(db.auth_group.role==role).select()
    if len(rows) != 1:
        return None
    return rows[0].id

def user_private_group_id():
    q = db.auth_membership.user_id == auth.user_id
    q &= db.auth_membership.group_id == db.auth_group.id
    q &= db.auth_group.role.like("user_%")
    row = db(q).select(db.auth_group.id).first()
    if row is None:
        return
    return row.id

def user_primary_group():
    sql = """select auth_group.role from
               auth_group,
               auth_membership
             where
               auth_membership.user_id = %(user_id)s and
               auth_membership.primary_group = 'T' and
               auth_membership.group_id = auth_group.id
             limit 1"""%dict(user_id=auth.user_id)
    rows = db.executesql(sql)
    if len(rows) != 1:
        return None
    return rows[0][0]

def user_primary_group_id():
    sql = """select auth_group.id from
               auth_group,
               auth_membership
             where
               auth_membership.user_id = %(user_id)s and
               auth_membership.primary_group = 'T' and
               auth_membership.group_id = auth_group.id
             limit 1"""%dict(user_id=auth.user_id)
    rows = db.executesql(sql)
    if len(rows) != 1:
        return None
    return rows[0][0]

def user_default_group():
    gid = user_default_group_id()
    return db.auth_group[gid].role

def user_default_group_id():
    gid = user_primary_group_id()
    if gid:
        return gid
    gid = user_private_group_id()
    if gid:
        return gid
    q = db.auth_membership.user_id == auth.user_id
    q &= db.auth_membership.group_id == db.auth_group.id
    q &= db.auth_group.privilege == "F"
    g = db(q).select(db.auth_group.id).first()
    if g:
        return g.id

def user_phone_work():
    q = db.auth_user.id == auth.user_id
    row = db(q).select(db.auth_user.phone_work).first()
    return row.phone_work

def user_email():
    q = db.auth_user.id == auth.user_id
    row = db(q).select(db.auth_user.email).first()
    if row is None:
        return None
    return row.email

def clear_cache_user_groups():
    cache.redis.clear(regex="user_groups:.*")

def user_groups(id=None):
    if id is None:
        id = auth.user_id
    return cache.redis("user_groups:%d"%auth.user_id, lambda: _user_groups(id), time_expire=14400)

def _user_groups(id):
    q = db.auth_membership.user_id==id
    q &= db.auth_membership.group_id==db.auth_group.id
    rows = db(q).select(db.auth_group.role)
    return map(lambda x: x.role, rows)

def clear_cache_user_published_apps():
    cache.redis.clear(regex="user_published_apps:.*")

def user_published_apps(id=None):
    if id is None:
        id = auth.user_id
    return cache.redis("user_published_apps:%d"%id, lambda: _user_published_apps(id), time_expire=14400)

def _user_published_apps(id=None):
    q = db.auth_membership.user_id==id
    q &= db.auth_membership.group_id==db.auth_group.id
    q &= db.apps_publications.group_id == db.auth_membership.group_id
    q &= db.apps_publications.app_id == db.apps.id
    rows = db(q).select(db.apps.app)
    return map(lambda x: x.app, rows)

def clear_cache_user_apps():
    cache.redis.clear(regex="user_apps:.*")

def user_apps(id=None):
    if id is None:
        id = auth.user_id
    return cache.redis("user_apps:%d"%id, lambda: _user_apps(id), time_expire=14400)

def _user_apps(id):
    q = db.auth_membership.user_id==id
    q &= db.auth_membership.group_id==db.auth_group.id
    q &= db.apps_responsibles.group_id == db.auth_membership.group_id
    q &= db.apps_responsibles.app_id == db.apps.id
    rows = db(q).select(db.apps.app)
    return map(lambda x: x.app, rows)

def clear_cache_user_app_ids():
    cache.redis.clear(regex="user_app_ids:.*")

def user_app_ids(id=None):
    if id is None:
        id = auth.user_id
    return cache.redis("user_app_ids:%d"%id, lambda: _user_app_ids(id), time_expire=14400)

def _user_app_ids(id):
    q = db.auth_membership.user_id==id
    q &= db.auth_membership.group_id==db.auth_group.id
    q &= db.apps_responsibles.group_id == db.auth_membership.group_id
    rows = db(q).select(db.apps_responsibles.app_id)
    return map(lambda x: x.app_id, rows)

def clear_cache_user_group_ids():
    cache.redis.clear(regex="user_group_ids:.*")

def user_group_ids(id=None):
    if id is None:
        id = auth.user_id
    return cache.redis("user_group_ids:%d"%id, lambda: _user_group_ids(id), time_expire=14400)

def _user_group_ids(id):
    q = db.auth_membership.user_id==id
    q &= db.auth_membership.group_id==db.auth_group.id
    rows = db(q).select(db.auth_group.id)
    return map(lambda x: x.id, rows)

def user_org_group_ids(id=None):
    if id is None:
        id = auth.user_id
    if id is None:
        return []
    sql = """select g.id from auth_group g, auth_membership am
             where
              am.group_id=g.id and
              am.user_id=%s and
              g.privilege='F' and
              g.role != 'UnaffectedProjects' and
              not g.role like 'user_%%'
           """%str(id)
    rows = db.executesql(sql)
    return map(lambda r: r[0], rows)

def user_published_nodes(id=None):
    q = db.nodes.app.belongs(user_published_apps(id))
    rows = db(q).select(db.nodes.node_id, cacheable=True)
    return map(lambda x: x.node_id, rows)

def user_nodes(id=None):
    q = db.nodes.team_responsible.belongs(user_groups(id))
    rows = db(q).select(db.nodes.node_id, cacheable=True)
    return map(lambda x: x.node_id, rows)

def user_published_services(id=None):
    q = db.services.svc_app.belongs(user_published_apps(id))
    rows = db(q).select(db.services.svc_id, cacheable=True)
    return map(lambda x: x.svc_id, rows)

def user_services(id=None):
    q = db.services.svc_app.belongs(user_apps(id))
    rows = db(q).select(db.services.svc_id, cacheable=True)
    return map(lambda x: x.svc_id, rows)

def member_of(g):
    groups = user_groups()
    if isinstance(g, str) and g in groups:
        return True
    elif isinstance(g, list) or isinstance(g, tuple):
        for _g in g:
            if _g in groups:
                return True
    else:
        raise Exception("member_of_group param must be a role or a list of roles")
    return False

def email_of(u):
    sql = """select email from auth_user where concat(first_name, " ", last_name) = "%s" """ % u
    rows = db.executesql(sql)
    if len(rows) != 1:
        return
    return rows[0][0]

def auth_register_callback(form):
    table_modified("auth_group")
    table_modified("auth_membership")

    q = db.auth_user.email == form.vars.email
    user = db(q).select().first()

    do_create_app_on_register(user)
    do_membership_on_register(user)

def do_membership_on_register(user):
    groups = config_get("membership_on_register", [])
    for group in groups:
        g = db(db.auth_group.role==group).select(db.auth_group.id, db.auth_group.role).first()
        if g is None:
            continue
        db.auth_membership.insert(user_id=user.id, group_id=g.id)
        _log("user.group.attach",
             "user %(u)s attached to group %(g)s",
             d=dict(u=user.email, g=g.role),
             user=" ".join((user.first_name, user.last_name)))

def do_create_app_on_register(user):
    if not config_get("create_app_on_register", False):
        return
    q = db.auth_group.role == "user_%d" % user.id
    group_id = db(q).select().first().id
    app = "user_%d_app" % user.id

    app_id = db.apps.insert(app=app)
    table_modified("apps")
    db.apps_responsibles.insert(app_id=app_id, group_id=group_id)
    table_modified("apps_responsibles")
    db.apps_publications.insert(app_id=app_id, group_id=group_id)
    table_modified("apps_publications")
    _log("app.add",
         "app %(app)s created on user register",
         d=dict(app=app),
         user=" ".join((user.first_name, user.last_name)))

class MyAuth(Auth):
    def __init__(self, environment, db = None):
        Auth.__init__(self,environment,db)
        self.log_messages = [self.messages[k] for k in self.messages \
                             if self.messages[k] is not None and '_log' in k]
        self.log_patterns = [T(m).replace('%(id)s','(?P<id>[0-9]+)').replace('%(id)s','(?P<group_id>[0-9]+)') for m in self.log_messages]


    def log_event(self, description, vars=None, origin='auth'):
        Auth.log_event(self, description, vars, origin)
        # user_id is now set

        if description is None:
            return

        for i, p in enumerate(self.log_patterns):
            v = re.search(p, description)
            if v is None:
                continue
            d = v.groupdict()
            if 'id' in d:
                d['id'] = user_fullname(int(d['id']))
            if 'group_id' in d:
                d['group_id'] = group_role(int(d['group_id']))
            m = self.log_messages[i]
            action = [origin]
            if 'Registered' in m:
                 action.append('add')
            elif 'reset' in m or 'changed' in m or 'updated' in m:
                 action.append('change')
            _log('.'.join(action), m, d)
            return

    def update_groups(self):
        return

    def login_bare(self, username, password):
        r = Auth.login_bare(self, username, password)
        if r is False:
            return False
        if self.user is None or (type(self.user) == str and self.user == username):
            from gluon.storage import Storage
            self.user = Storage()
            self.user.id = -1
            self.user.email = "root@"+username
            self.user.nodename = username
            self.user.node_id = auth_to_node_id([password, username])
            self.user.first_name = username
            self.user.last_name = username
        return r
