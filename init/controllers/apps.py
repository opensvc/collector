@auth.requires_membership('Manager')
def _del_app(request):
    ids = ([])
    count = 0
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        ids += ([key[6:]])
    for id in ids:
        count += db(db.apps.id == id).delete()
    if count > 1:
        s = 's'
    else:
        s = ''
    response.flash = T("%(count)s application%(s)s deleted", dict(count=count, s=s))
    del request.vars.appctl

@auth.requires_membership('Manager')
def _add_app(request):
    apps = db(db.apps.app==request.vars.addapp).select(db.apps.id)
    if len(apps) != 0:
        response.flash = T("application '%(app)s' already exists", dict(app=request.vars.addapp))
        return
    db.apps.insert(app=request.vars.addapp)
    response.flash = T("application '%(app)s' created", dict(app=request.vars.addapp))
    q = db.apps.app==request.vars.addapp
    app = db(q).select(db.apps.id)[0]
    request.vars.appid = str(app.id)
    del request.vars.appctl
    del request.vars.addapp

@auth.requires_membership('Manager')
def _set_resp(request):
    ids = ([])
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        ids += ([key[6:]])
    for id in ids:
        query = db.apps_responsibles.app_id == id
        query &= db.apps_responsibles.group_id == request.vars.select_roles
        rows = db(query).select()
        if len(rows) == 0:
            db.apps_responsibles.insert(app_id=id,
                                        group_id=request.vars.select_roles)

    num = len(ids)
    if num > 1:
        s = 's'
    else:
        s = ''
    response.flash = T("%(num)s assignment%(s)s added", dict(num=num, s=s))
    del request.vars.resp

@auth.requires_membership('Manager')
def _unset_resp(request):
    ids = ([])
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        ids += ([key[6:]])
    for id in ids:
        query = (db.apps_responsibles.app_id == id)&(db.apps_responsibles.group_id == request.vars.select_roles)
        num = db(query).delete()
    if num > 1:
        s = 's'
    else:
        s = ''
    response.flash = T("%(num)s assignment%(s)s removed", dict(num=num, s=s))
    del request.vars.resp

@auth.requires_membership('Manager')
def apps():
    columns = dict(
        app = dict(
            pos = 1,
            title = T('App'),
            img = 'svc',
            size = 4
        ),
        roles = dict(
            pos = 2,
            title = T('Roles'),
            img = 'guy16',
            size = 12
        ),
        responsibles = dict(
            pos = 3,
            title = T('Responsibles'),
            img = 'guy16',
            size = 12
        ),
    )
    def _sort_cols(x, y):
        return cmp(columns[x]['pos'], columns[y]['pos'])
    colkeys = columns.keys()
    colkeys.sort(_sort_cols)

    if request.vars.appctl == 'del':
        _del_app(request)
    elif request.vars.appctl == 'add' and request.vars.addapp is not None and request.vars.addapp != '':
        _add_app(request)
    elif request.vars.resp == 'del':
        _unset_resp(request)
    elif request.vars.resp == 'add':
        _set_resp(request)

    # filtering
    query = (db.v_apps.id>0)
    for key in columns.keys():
        if key not in request.vars.keys():
            continue
        query &= _where(None, 'v_apps', request.vars[key], key)

    g = db.v_apps.app

    (start, end, nav) = _pagination(request, query, groupby=g)
    if start == 0 and end == 0:
        rows = db(query).select(db.v_apps.id,
                                db.v_apps.app,
                                db.v_apps.roles,
                                db.v_apps.responsibles,
                                orderby=db.v_apps.app,
                                left=db.v_svcmon.on(db.v_svcmon.svc_app==db.v_apps.app),
                                groupby=g)
    else:
        rows = db(query).select(db.v_apps.id,
                                db.v_apps.app,
                                db.v_apps.roles,
                                db.v_apps.responsibles,
                                limitby=(start,end),
                                orderby=db.v_apps.app,
                                left=db.v_svcmon.on(db.v_svcmon.svc_app==db.v_apps.app),
                                groupby=g)

    query = ~db.auth_group.role.like('user_%')
    roles = db(query).select()
    return dict(columns=columns, colkeys=colkeys,
                apps=rows, roles=roles, nav=nav)


