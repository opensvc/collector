def detach_group_from_app(group_id, app_id):
    if type(app_id) != list:
        app_id = [app_id]

    rows = db(db.apps.id.belongs(app_id)).select(db.apps.app)
    u = ', '.join([r.app for r in rows])
    g = db(db.auth_group.id==group_id).select(db.auth_group.role)[0].role

    q = db.apps_responsibles.app_id.belongs(app_id)
    q &= db.apps_responsibles.group_id == group_id
    db(q).delete()
    table_modified("apps_responsibles")
    _log('apps.group.detach',
         'detached group %(g)s from app %(u)s',
         dict(g=g, u=u))

def attach_group_to_app(group_id, app_id):
    if type(app_id) != list:
        app_id = [app_id]

    done = []
    for id in app_id:
        q = db.apps_responsibles.app_id == id
        q &= db.apps_responsibles.group_id==group_id
        if db(q).count() != 0:
            continue
        done.append(id)
        db.apps_responsibles.insert(app_id=id, group_id=group_id)
    table_modified("apps_responsibles")


    rows = db(db.apps.id.belongs(done)).select()
    u = ', '.join([r.app for r in rows])
    g = db(db.auth_group.id==group_id).select(db.auth_group.role)[0].role
    _log('apps.group.attach',
         'attached group %(g)s to apps %(u)s',
         dict(g=g, u=u))

    # remove dashboard alerts
    for r in rows:
        q = db.dashboard.dash_type == "application code without responsible"
        q &= db.dashboard.dash_dict.like('%%:"%s"%%'%r.app)
        db(q).delete()
    table_modified("dashboard")

def lib_app_id(id):
    try:
        id = int(id)
        return id
    except:
        pass
    q = db.apps.app == id
    row = db(q).select(db.apps.id).first()
    if row is not None:
        return row.id

