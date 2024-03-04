def node_app_id(node_id=None):
    if node_id is None:
        node_id = auth.user.node_id
    if node_id is None:
        return
    q = db.nodes.node_id == node_id
    q &= db.nodes.app == db.apps.app
    row = db(q).select(db.apps.id).first()
    if row is None:
        return []
    return row.id

def node_cluster_id(node_id):
    try:
        return get_node(node_id).cluster_id
    except Exception as exc:
        return ""


def search_node_svc(node_id, svcname, responsibles, cluster_id):
    q = db.services.svcname == svcname
    q &= db.services.cluster_id == cluster_id
    q &= db.services.svc_app == db.apps.app
    q &= db.apps.id == db.apps_responsibles.app_id
    q &= db.apps_responsibles.group_id.belongs(responsibles)
    rows = db(q).select(
        db.services.svcname,
        db.services.svc_id,
        db.services.svc_app,
        db.services.svc_env,
        db.services.svc_availstatus,
        db.services.svc_status,
        groupby=db.services.svc_id
    )
    if len(rows) > 1:
        raise Exception("multiple services found matching the service name '%(svcname)s' in the node '%(node_id)s' cluster %(cluster_id)s responsibility zone: %(svc_ids)s" % dict(
            svcname=svcname,
            cluster_id=cluster_id,
            node_id=node_id,
            svc_ids=', '.join([r.svc_id for r in rows]),
        ))

    if len(rows) == 1:
        return rows.first()

    # encap service
    q = db.nodes.node_id == node_id
    q &= db.svcmon.mon_vmname == db.nodes.nodename
    q &= db.svcmon.svc_id == db.services.svc_id
    q &= db.services.svcname == svcname
    q &= db.services.svc_app == db.apps.app
    q &= db.apps.id == db.apps_responsibles.app_id
    q &= db.apps_responsibles.group_id.belongs(responsibles)

    rows = db(q).select(
        db.services.svcname,
        db.services.svc_id,
        db.services.svc_app,
        db.services.svc_env,
        db.services.svc_availstatus,
        db.services.svc_status,
        groupby=db.services.svc_id,
    )
    if len(rows) > 1:
        raise Exception("multiple services found matching the service name '%(svcname)s' in the encap node '%(node_id)s' responsibility zone: %(svc_ids)s" % dict(
            svcname=svcname,
            node_id=node_id,
            svc_ids=', '.join([r.svc_id for r in rows]),
        ))

    if len(rows) == 1:
        return rows.first()


    #
    # no service was found in the node's responsability zone.
    # if we already have a service instance on the cluster, fetch the svc_id from there,
    # as a svcname can be found twice on the same node
    #
    if cluster_id:
        q = db.svcmon.node_id == db.nodes.node_id
        q &= db.nodes.cluster_id == cluster_id
    else:
        q = db.svcmon.node_id == node_id
    q &= db.svcmon.svc_id == db.services.svc_id
    q &= db.services.svcname == svcname
    rows = db(q).select(
        db.services.svcname,
        db.services.svc_id,
        db.services.svc_app,
        db.services.svc_env,
        db.services.svc_availstatus,
        db.services.svc_status,
    )

    if len(rows) >= 1:
        return rows.first()

    #
    # last chance: maybe an orphan service was created (without cluster_id)
    # in the app namespace
    #
    q = db.services.svcname == svcname
    q &= db.services.cluster_id == ""
    q &= db.services.svc_app == db.apps.app
    q &= db.apps.id == db.apps_responsibles.app_id
    q &= db.apps_responsibles.group_id.belongs(responsibles)
    rows = db(q).select(
        db.services.svcname,
        db.services.svc_id,
        db.services.svc_app,
        db.services.svc_env,
        db.services.svc_availstatus,
        db.services.svc_status,
        groupby=db.services.svc_id
    )
    if len(rows) > 1:
        raise Exception("multiple orphan services found matching the service name '%(svcname)s' in the node '%(node_id)s' cluster 'empty' responsibility zone: %(svc_ids)s" % dict(
            svcname=svcname,
            node_id=node_id,
            svc_ids=', '.join([r.svc_id for r in rows]),
        ))
    elif len(rows) == 1:
        return rows.first()


def node_svc(node_id, svcname, app=None):
    if node_id is None or svcname is None:
        return
    svcname = svcname.strip("'")
    if svcname == "":
        return
    cluster_id = node_cluster_id(node_id)
    responsibles = node_responsibles(node_id)

    found = search_node_svc(node_id, svcname, responsibles, cluster_id)

    if found:
        return found
    else:
        return create_svc(node_id, cluster_id, svcname, app=app, responsibles=responsibles)


def node_svc_id(node_id, svcname):
    svc = node_svc(node_id, svcname)
    if svc is None:
        return ""
    return svc["svc_id"]

def create_svc(node_id, cluster_id, svcname, app=None, responsibles=None):
    name = "create_svc_%s" % svcname
    lock_id = acquire_lock(name, timeout=20)
    if lock_id:
        result = _create_svc(node_id, cluster_id, svcname, app=app, responsibles=responsibles)
        release_lock(name, lock_id)
        return result
    raise Exception("unable to acquire lock %s" % name)


def _create_svc(node_id, cluster_id, svcname, app=None, responsibles=None):
    if svcname == "cluster":
        return
    from gluon.storage import Storage
    node = get_node(node_id)
    if node is None:
        return

    if not app:
        app = node.app
    elif not common_responsible(app=app, node_id=node_id):
        app = node.app

    # verify the app is valid
    q = db.apps.app == app
    row = db(q).select().first()
    if row is None:
        return

    # Last retry search, in lock mode, perhaps changes during last search
    db.commit()  # ensure start from fresh db
    found = search_node_svc(node_id, svcname, responsibles, cluster_id)
    if found:
        _log('create_svc',
             'existing service:%s cluster_id:%s app:%s responsibles:%s' % (svcname, cluster_id, app, responsibles),
             dict(),
             node_id=node_id,
             svc_id=found.svc_id,
             user="feed",
             level="info")
        return found

    svc_id = get_new_svc_id()
    data = {
      "svcname": svcname,
      "svc_app": app,
      "svc_env": node.node_env,
      "svc_availstatus": "undef",
      "svc_status": "undef",
      "svc_id": svc_id,
      "cluster_id": cluster_id,
      "updated": datetime.datetime.now()
    }
    _log('create_svc',
         'new service:%s cluster_id:%s app:%s responsibles:%s' % (svcname, cluster_id, app, responsibles),
         dict(),
         node_id=node_id,
         svc_id=svc_id,
         user="feed",
         level="info")
    db.services.insert(**data)
    db.commit()
    return Storage(data)

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

def auth_to_node(auth):
    q = db.auth_node.uuid == auth[0]
    q &= db.auth_node.nodename == auth[1].strip("'")
    row = db(q).select(db.auth_node.node_id).first()
    if row is None:
        return None
    q = db.nodes.node_id == row.node_id
    return db(q).select().first()

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
    l = []
    if node_id:
        # TODO: verify possible dups apps_responsibles entries because no uniq key app_id, group_id
        #       => multiple rows returned => break final request count(t.group_id) ...
        l.append(""" select ar.group_id from nodes n, apps a, apps_responsibles ar where n.app=a.app and n.node_id="%(node_id)s" and ar.app_id=a.id """ % dict(node_id=node_id))
    if svc_id:
        l.append(""" select ar.group_id from services s, apps a, apps_responsibles ar where s.svc_app=a.app and s.svc_id="%(svc_id)s" and ar.app_id=a.id """ % dict(svc_id=svc_id))
    if app:
        l.append(""" select ar.group_id from apps a, apps_responsibles ar where a.app="%(app)s" and ar.app_id=a.id  """ % dict(app=app))
    if user_id:
        l.append(""" select am.group_id from auth_membership am where am.user_id=%(user_id)d  """ % dict(user_id=user_id))
    sub = " union all ".join(l)
    sql = """ select * from (select count(t.group_id) as c from (%(sub)s) as t group by t.group_id) u where u.c=%(n)d """ % dict(sub=sub, n=len(l))
    rows = db.executesql(sql)

    if len(rows) > 0:
        return True
    return False

def check_auth(node, uuid):
    q = db.auth_node.nodename == node
    q &= db.auth_node.uuid == uuid
    rows = db(q).select(db.auth_node.node_id)
    n = len(rows)
    if n != 1:
        q = db.auth_node.nodename == node
        n = db(q).count()
        if n == 0:
            raise Exception("agent %s not registered"%node)
        else:
            raise Exception("agent authentication error")
    db(db.nodes.node_id==rows.first().node_id).update(last_comm=request.now)

def auth_uuid(fn):
    def new(*args, **kwargs):
        try:
            if 'auth' in kwargs:
                uuid, agent = kwargs['auth']
            else:
                uuid, agent = args[-1]
        except:
            raise Exception("no authentication data found in the request")

        if "@" in agent:
            svcname, nodename = agent.split("@")
            node_id = auth_to_node_id((uuid, nodename))
            svc_id = node_svc_id(node_id, svcname)
        else:
            nodename = agent
            svcname = None
            node_id = auth_to_node_id((uuid, nodename))
            svc_id = None

        try:
            check_auth(nodename, uuid)
        except Exception as e:
            _log('node.auth',
                 'node authentication error: %(e)s from %(nodename)s',
                 dict(e=str(e), nodename=nodename),
                 node_id=node_id,
                 svc_id=svc_id,
                 nodename=nodename,
                 svcname=svcname,
                 user="feed",
                 level="warning")
            raise
        return fn(*args, **kwargs)

    return new

def node_auth():
    """
    auth.settings.login_methods.append(node_auth())
    """

    def node_login_aux(agent, uuid):
        if "@" in agent:
            svcname, nodename = agent.split("@")
            node_id = auth_to_node_id((uuid, nodename))
            svc_id = node_svc_id(node_id, svcname)
        else:
            nodename = agent
            svcname = None
            node_id = auth_to_node_id((uuid, nodename))
            svc_id = None

        try:
            check_auth(nodename, uuid)
            from gluon.storage import Storage
            user = Storage()
            user.id = -1
            user.nodename = nodename
            user.svcname = svcname
            user.node_id = node_id
            user.svc_id = svc_id

            session.auth = Storage()
            session.auth.user = user
            session.auth.last_visit = request.now
            return True
        except Exception as e:
            if not auth_is_user(agent):
                _log(
                  'node.auth',
                  'node authentication error: %(e)s from %(nodename)s',
                  dict(e=str(e), nodename=nodename),
                  node_id=node_id,
                  svc_id=svc_id,
                  user="feed",
                  level="warning"
                )
            return False
    return node_login_aux

def auth_is_user(email):
    if db(db.auth_user.email==email).select(db.auth_user.id).first() is None:
        return False
    return True

def auth_is_node():
    if hasattr(auth.user, "node_id") and auth.user.node_id is not None:
        return True
    return False

def auth_is_svc():
    if hasattr(auth.user, "svc_id") and auth.user.svc_id is not None:
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
