@auth.requires_membership('Manager')
def user_event_log():
    rows = db(db.auth_event.user_id==request.vars.uid).select(orderby=~db.auth_event.id, limitby=(0, 20))
    x = TR(TH(T('Date')), TH(T('From')), TH(T('Event')))
    def to_row(row):
       return TR(TD(row.time_stamp), TD(row.client_ip), TD(row.description))
    xx = map(to_row, rows)
    return TABLE(x, xx)

@auth.requires_membership('Manager')
def _user_grant(request):
    ids = ([])
    group_id = request.vars.select_role
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        ids += ([int(key[6:])])
    if len(ids) == 0:
        response.flash = T('no user selected')
        return
    for id in ids:
        if not auth.has_membership(group_id, id):
            auth.add_membership(group_id, id)
    redirect(URL(r=request, f='users'))

@auth.requires_membership('Manager')
def _user_revoke(request):
    ids = ([])
    group_id = request.vars.select_role
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        ids += ([int(key[6:])])
    if len(ids) == 0:
        response.flash = T('no user selected')
        return
    for id in ids:
        if auth.has_membership(group_id, id):
            auth.del_membership(group_id, id)
    redirect(URL(r=request, f='users'))

@auth.requires_membership('Manager')
def _role_add(request):
    role = request.vars.newrole
    if role is None or len(role) == 0:
        response.flash = T('invalid role name')
        return
    db.auth_group.insert(role=role)
    response.flash = T('new role added')
    redirect(URL(r=request, f='users'))

@auth.requires_membership('Manager')
def _role_del(request):
    id = request.vars.select_delrole
    if id is None or len(id) == 0:
        response.flash = T('invalid role: %(id)s', dict(id=id))
        return
    if int(id) == auth.id_group("Manager"):
        response.flash = T("you are not allowed to delete the Manager group", dict(id=id))
        return
    db(db.auth_membership.group_id==id).delete()
    db(db.apps_responsibles.group_id==id).delete()
    db(db.auth_group.id==id).delete()
    response.flash = T('role removed')
    redirect(URL(r=request, f='users'))

@auth.requires_membership('Manager')
def _user_domain_edit(request):
    ids = ([])
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        id = int(key[6:])
        domains = request.vars["domains_"+str(id)]
        group = auth.user_group(id)
        if domains is None or len(domains) == 0:
            sql = "delete from domain_permissions where group_id=%s"%group
        else:
            sql = "insert into domain_permissions set group_id=%(group)s, domains='%(domains)s' on duplicate key update domains='%(domains)s'"%dict(domains=domains, group=group)
        db.executesql(sql)
    redirect(URL(r=request, f='users'))

@auth.requires_membership('Manager')
def _user_del(request):
    ids = ([])
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        ids += ([int(key[6:])])
    sql = "delete u, m from auth_user u join auth_membership m on u.id=m.user_id where u.id in (%s)"%','.join(map(str, ids))
    db.executesql(sql)
    redirect(URL(r=request, f='users'))

@auth.requires_membership('Manager')
def users():
    if request.vars.action is not None and request.vars.action == "grant":
        _user_grant(request)
    elif request.vars.action is not None and request.vars.action == "revoke":
        _user_revoke(request)
    elif request.vars.action is not None and request.vars.action == "del":
        _user_del(request)
    elif request.vars.action is not None and request.vars.action == "addrole":
        _role_add(request)
    elif request.vars.action is not None and request.vars.action == "delrole":
        _role_del(request)
    elif request.vars.action is not None and request.vars.action == "set_domains":
        _user_domain_edit(request)

    o = ~db.v_users.last

    query = _where(None, 'v_users', request.vars.fullname, 'fullname')
    query &= _where(None, 'v_users', request.vars.email, 'email')
    query &= _where(None, 'v_users', request.vars.domains, 'domains')
    query &= _where(None, 'v_users', request.vars.domains, 'manager')
    query &= _where(None, 'v_users', request.vars.last, 'last')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select(orderby=o)
    else:
        rows = db(query).select(limitby=(start,end), orderby=o)

    roles = db(~db.auth_group.role.like("user_%")).select(orderby=db.auth_group.role)

    return dict(users=rows, nav=nav, roles=roles)


