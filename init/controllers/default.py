# coding: utf8

from pychart import *

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

def _pagination(request, query, groupby=None):
    start = 0
    end = 0
    nav = ''
    perpage = int(request.vars.perpage) if 'perpage' in request.vars.keys() else 20

    if perpage <= 0:
        return (start, end, nav)
    if groupby is not None:
        totalrecs = len(db(query).select(groupby=groupby))
    else:
        totalrecs = db(query).count()
    totalpages = totalrecs / perpage
    if totalrecs % perpage > 0: totalpages = totalpages + 1
    try:
        page = int(request.args[0]) if len(request.args) else 1
    except:
        """ casting error
        """
        page = 1

    # out of range conditions
    if page <= 0: page = 1
    if page > totalpages: page = 1
    start = (page-1)*perpage
    end = start+perpage
    if end > totalrecs:
        end = totalrecs

    num_pages = 10
    def page_range():
        s = page - num_pages/2
        e = page + num_pages/2
        if s <= 0:
            e = e - s
            s = 1
        if e > totalpages:
            s = s - (e - totalpages)
            e = totalpages
        if s <= 0:
            s = 1
        return range(s, e+1)

    pr = page_range()
    pager = []
    if page != 1:
        pager.append(A(T('<< '),_href=URL(r=request,args=[page-1],vars=request.vars)))
    for p in pr:
        if p == page:
            pager.append(A(str(p)+' ', _class="current_page"))
        else:
            pager.append(A(str(p)+' ', _href=URL(r=request,args=[p],vars=request.vars)))
    if page != totalpages:
        pager.append(A(T('>> '),_href=URL(r=request,args=[page+1],vars=request.vars)))
    v = request.vars
    v.perpage = 0
    pager.append(A(T('all'),_href=URL(r=request,vars=v)))

    # paging toolbar
    if totalrecs == 0:
        pager.append(P("No records found matching filters", _style='text-align:center'))
    else:
        info=T("Showing %(first)d to %(last)d out of %(total)d records", dict(first=start+1, last=end, total=totalrecs))
        nav = P(pager, _style='text-align:center', _title=info)

    return (start, end, nav)

def domain_perms():
    domain_perms = "abracadabra@0123456789"
    rows = db(db.domain_permissions.id>0).select()
    if len(rows) == 0:
        # wildcard for collectors with no domain_permissions information
        domain_perms = None
    query = (db.auth_membership.user_id==session.auth.user.id)&(db.domain_permissions.group_id==db.auth_membership.group_id)
    rows = db(query).select(db.domain_permissions.domains)
    if len(rows) == 0:
        return domain_perms
    if rows[0]['domains'] is None:
        return domain_perms
    return rows[0]['domains']

def _domain_perms():
    dom = domain_perms()
    if dom is None:
        return '%'
    return dom

def toggle_db_filters():
    if request.vars.addfilter is not None and request.vars.addfilter != '':
        filters = db(db.filters.id==request.vars.addfilter).select(db.filters.fil_name)
        if len(filters) == 0:
            return
        name = filters[0].fil_name
        ids = db(db.filters.fil_name==name).select(db.filters.id)
        for id in [r.id for r in ids]:
            try:
                db.auth_filters.insert(fil_uid=session.auth.user.id,
                                  fil_id=id,
                                  fil_value=request.vars.filtervalue)
            except:
                pass

    elif request.vars.delfilter is not None and request.vars.delfilter != '':
        filters = db(db.auth_filters.id==request.vars.delfilter).select(db.filters.fil_name, left=db.filters.on(db.auth_filters.fil_id==db.filters.id))
        if len(filters) == 0:
            return
        name = filters[0].fil_name
        ids = db(db.filters.fil_name==name)._select(db.filters.id)
        q = db.auth_filters.fil_id.belongs(ids)
        db(q).delete()

    elif request.vars.togfilter is not None and request.vars.togfilter != '':
        filters = db(db.auth_filters.id==request.vars.togfilter).select(
                        db.filters.fil_name,
                        db.auth_filters.fil_active,
                        left=db.filters.on(db.auth_filters.fil_id==db.filters.id)
                  )
        if len(filters) == 0:
            return
        name = filters[0].filters.fil_name
        ids = db(db.filters.fil_name==name)._select(db.filters.id)
        cur = filters[0].auth_filters.fil_active
        if cur: tgt = '0'
        else: tgt = '1'
        q = db.auth_filters.fil_id.belongs(ids)
        db(q).update(fil_active=tgt)
        del request.vars.togfilter

def apply_db_filters(query, table=None):
    q = db.auth_filters.fil_uid==session.auth.user.id
    q &= db.auth_filters.fil_active==1
    q &= db.filters.fil_table==table
    filters = db(q).select(db.auth_filters.fil_value,
                           db.filters.fil_name,
                           db.filters.fil_table,
                           db.filters.fil_column,
                           left=db.filters.on(db.filters.id==db.auth_filters.fil_id))
    for f in filters:
        if 'ref' not in f.filters.fil_column:
            if table not in db or f.filters.fil_column not in db[table]:
                continue
            query &= _where(None, table, f.auth_filters.fil_value, f.filters.fil_column)
        elif f.filters.fil_column == 'ref1':
            """ only primary nodes
            """
            query &= db.v_svcmon.mon_nodname==db.v_svcmon.svc_autostart
        elif f.filters.fil_column == 'ref2':
            """ only nodes with services
            """
            query &= db.v_nodes.nodename.belongs(db()._select(db.svcmon.mon_nodname))
        elif f.filters.fil_column == 'ref3':
            """ only not acknowledged actions
            """
            query &= (db.v_svcactions.status=='err')&(db.v_svcactions.ack==None)
    return query

def avail_db_filters(table=None):
    o = db.filters.fil_pos|db.filters.fil_img|db.filters.fil_name
    active_fid = db(db.auth_filters.fil_uid==session.auth.user.id)._select(db.auth_filters.fil_id)
    q = ~db.filters.id.belongs(active_fid)
    filters = db(q).select(db.filters.id,
                           db.filters.fil_name,
                           db.filters.fil_img,
                           db.filters.fil_table,
                           db.filters.fil_column,
                           db.filters.fil_need_value,
                           db.filters.fil_pos,
                           orderby=o,
                           groupby=db.filters.fil_name,
                          )
    return filters

def active_db_filters(table=None):
    o = db.filters.fil_pos|db.filters.fil_img|db.filters.fil_name
    q = db.auth_filters.fil_uid==session.auth.user.id
    filters = db(q).select(db.auth_filters.fil_value,
                           db.auth_filters.id,
                           db.auth_filters.fil_active,
                           db.filters.fil_name,
                           db.filters.fil_img,
                           db.filters.fil_table,
                           db.filters.fil_column,
                           left=db.filters.on(db.filters.id==db.auth_filters.fil_id),
                           groupby=db.filters.fil_name,
                           orderby=o
                          )
    return filters

@auth.requires_login()
def service_action():
    action = request.vars.select_action
    request.vars.select_action = 'choose'

    if action is None or action == '' or action == 'choose':
        return

    ids = ([])
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        ids += ([key[6:]])

    if len(ids) == 0:
        response.flash = "no target to execute %s on"%action
        return

    sql = """select m.mon_nodname, m.mon_svcname
             from v_svcmon m
             join v_apps_flat a on m.svc_app=a.app
             where m.id in (%(ids)s)
             and responsible='%(user)s'
             group by m.mon_nodname, m.mon_svcname
          """%dict(ids=','.join(ids),
                   user=' '.join([session.auth.user.first_name,
                                  session.auth.user.last_name]))
    rows = db.executesql(sql)

    from subprocess import Popen
    def do_select_action(node, svc, action):
        cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                      '-o', 'ForwardX11=no',
                      '-o', 'PasswordAuthentication=no',
               'opensvc@'+node,
               '--',
               'sudo', '/opt/opensvc/bin/svcmgr', '--service', svc, action]
        process = Popen(cmd, stdin=None, stdout=None, close_fds=True)
        #process.communicate()

    for row in rows:
        do_select_action(row[0], row[1], action)

    response.flash = T("launched %(action)s on %(n)d services", dict(
                       n=len(rows), action=action))

@auth.requires_login()
def index():
    toggle_db_filters()

    now = datetime.datetime.now()
    one_days_ago = now - datetime.timedelta(days=1)
    tmo = now - datetime.timedelta(minutes=15)

    query = db.svcmon.mon_frozen==1
    query &= _where(None, 'svcmon', domain_perms(), 'mon_nodname')
    frozen = db(query).select(db.svcmon.mon_svcname, db.svcmon.mon_nodname,
                              orderby=db.svcmon.mon_svcname)

    query = ~db.svcmon.mon_nodname.belongs(db()._select(db.nodes.nodename))
    query &= _where(None, 'svcmon', domain_perms(), 'mon_nodname')
    nodeswithoutasset = db(query).select(db.svcmon.mon_nodname, groupby=db.svcmon.mon_nodname,)

    query = db.v_svcmon.mon_updated<tmo
    query &= _where(None, 'v_svcmon', domain_perms(), 'mon_svcname')
    query = apply_db_filters(query, 'v_svcmon')
    svcnotupdated = db(query).select(orderby=~db.v_svcmon.mon_updated, limitby=(0,50))

    query = db.svcmon_log.mon_end>one_days_ago
    query &= db.svcmon_log.mon_svcname==db.v_svcmon.mon_svcname
    query &= db.svcmon_log.mon_nodname==db.v_svcmon.mon_nodname
    query &= _where(None, 'svcmon_log', domain_perms(), 'mon_svcname')
    query = apply_db_filters(query, 'v_svcmon')
    lastchanges = db(query).select(orderby=~db.svcmon_log.mon_begin, limitby=(0,20))

    query = (db.v_svcmon.err>0)
    query &= _where(None, 'v_svcmon', domain_perms(), 'mon_svcname')
    query = apply_db_filters(query, 'v_svcmon')
    svcwitherrors = db(query).select(orderby=~db.v_svcmon.err, groupby=db.v_svcmon.mon_svcname)

    query = (~db.v_svc_group_status.groupstatus.like("up,%"))
    query &= (~db.v_svc_group_status.groupstatus.like("%,up,%"))
    query &= (~db.v_svc_group_status.groupstatus.like("%,up"))
    query &= (db.v_svc_group_status.groupstatus!="up")
    query &= _where(None, 'v_svc_group_status', domain_perms(), 'svcname')
    query &= db.v_svc_group_status.svcname==db.v_svcmon.mon_svcname
    query = apply_db_filters(query, 'v_svcmon')
    svcnotup = db(query).select(groupby=db.v_svc_group_status.svcname, orderby=db.v_svc_group_status.svcname)

    query = (db.v_svcmon.svc_autostart==db.v_svcmon.mon_nodname)
    query &= ((db.v_svcmon.mon_overallstatus!="up")|(db.v_svcmon.mon_updated<tmo))
    query &= _where(None, 'v_svcmon', domain_perms(), 'mon_svcname')
    query = apply_db_filters(query, 'v_svcmon')
    svcnotonprimary = db(query).select()

    query = (db.v_apps.responsibles==None)
    query |= (db.v_apps.responsibles=="")
    appwithoutresp = db(query).select(db.v_apps.app)

    warn = (db.obsolescence.obs_warn_date!=None)&(db.obsolescence.obs_warn_date!="0000-00-00")&(db.obsolescence.obs_warn_date<now)
    alert = (db.obsolescence.obs_alert_date==None)|(db.obsolescence.obs_alert_date=="0000-00-00")|(db.obsolescence.obs_alert_date>=now)
    query = warn & alert
    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
    query = apply_db_filters(query, 'v_nodes')
    join = db.obsolescence.obs_type=="os"
    join &= db.obsolescence.obs_name==db.v_nodes.os_concat
    obsoswarn = db(query).select(db.v_nodes.nodename,
                                 db.obsolescence.obs_name,
                                 db.obsolescence.obs_warn_date,
                                 left=db.v_nodes.on(join),
                                 orderby=db.obsolescence.obs_warn_date|db.v_nodes.nodename
                                )

    query = (db.obsolescence.obs_alert_date!=None)&(db.obsolescence.obs_alert_date!="0000-00-00")&(db.obsolescence.obs_alert_date<now)
    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
    query = apply_db_filters(query, 'v_nodes')
    join = db.obsolescence.obs_type=="os"
    join &= db.obsolescence.obs_name==db.v_nodes.os_concat
    obsosalert = db(query).select(db.v_nodes.nodename,
                                 db.obsolescence.obs_name,
                                 db.obsolescence.obs_alert_date,
                                 left=db.v_nodes.on(join),
                                 orderby=db.obsolescence.obs_alert_date|db.v_nodes.nodename
                                )

    warn = (db.obsolescence.obs_warn_date!=None)&(db.obsolescence.obs_warn_date!="0000-00-00")&(db.obsolescence.obs_warn_date<now)
    alert = (db.obsolescence.obs_alert_date==None)|(db.obsolescence.obs_alert_date=="0000-00-00")|(db.obsolescence.obs_alert_date>=now)
    query = warn & alert
    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
    query = apply_db_filters(query, 'v_nodes')
    join = db.obsolescence.obs_type=="hw"
    join &= db.obsolescence.obs_name==db.v_nodes.model
    obshwwarn = db(query).select(db.v_nodes.nodename,
                                 db.obsolescence.obs_name,
                                 db.obsolescence.obs_warn_date,
                                 left=db.v_nodes.on(join),
                                 orderby=db.obsolescence.obs_warn_date|db.v_nodes.nodename
                                )

    query = (db.obsolescence.obs_alert_date!=None)&(db.obsolescence.obs_alert_date!="0000-00-00")&(db.obsolescence.obs_alert_date<now)
    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
    query = apply_db_filters(query, 'v_nodes')
    join = db.obsolescence.obs_type=="hw"
    join &= db.obsolescence.obs_name==db.v_nodes.model
    obshwalert = db(query).select(db.v_nodes.nodename,
                                 db.obsolescence.obs_name,
                                 db.obsolescence.obs_alert_date,
                                 left=db.v_nodes.on(join),
                                 orderby=db.obsolescence.obs_alert_date|db.v_nodes.nodename
                                )

    rows = db(db.v_users.id==session.auth.user.id).select(db.v_users.manager)
    if len(rows) == 1 and rows[0].manager == 1:
        query = (db.obsolescence.obs_warn_date==None)|(db.obsolescence.obs_warn_date=="0000-00-00")
        query &= (db.v_nodes.os_concat==db.obsolescence.obs_name)|(db.v_nodes.model==db.obsolescence.obs_name)
        query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
        query &= apply_db_filters(query, 'v_nodes')
        rows = db(query).select(db.obsolescence.obs_name, groupby=db.obsolescence.obs_name)
        obswarnmiss = len(rows)

        query = (db.obsolescence.obs_alert_date==None)|(db.obsolescence.obs_alert_date=="0000-00-00")
        query &= (db.v_nodes.os_concat==db.obsolescence.obs_name)|(db.v_nodes.model==db.obsolescence.obs_name)
        query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
        query &= apply_db_filters(query, 'v_nodes')
        rows = db(query).select(db.obsolescence.obs_name, groupby=db.obsolescence.obs_name)
        obsalertmiss = len(rows)
    else:
        obswarnmiss = 0
        obsalertmiss = 0

    pkgdiff = {}
    rows = db(db.v_svc_group_status.id>0).select(db.v_svc_group_status.nodes, distinct=True)
    for row in rows:
        nodes = row.nodes.split(',')
        n = len(nodes)
        if n == 1:
            continue
        nodes.sort()
        key = ','.join(nodes)
        if key in pkgdiff:
            continue
        sql = """select count(id) from (
                   select *,count(pkg_nodename) as c
                   from packages
                   where pkg_nodename in (%(nodes)s)
                   group by pkg_name,pkg_version,pkg_arch
                   order by pkg_name,pkg_version,pkg_arch
                 ) as t
                 where t.c!=%(n)s;
              """%dict(n=n, nodes=','.join(map(repr, nodes)))
        x = db.executesql(sql)
        if len(x) != 1 or len(x[0]) != 1 or x[0][0] == 0:
            continue
        pkgdiff[key] = x[0][0]

    return dict(svcnotupdated=svcnotupdated,
                frozen=frozen,
                nodeswithoutasset=nodeswithoutasset,
                lastchanges=lastchanges,
                svcwitherrors=svcwitherrors,
                svcnotonprimary=svcnotonprimary,
                appwithoutresp=appwithoutresp,
                obsoswarn=obsoswarn,
                obsosalert=obsosalert,
                obshwwarn=obshwwarn,
                obshwalert=obshwalert,
                obswarnmiss=obswarnmiss,
                obsalertmiss=obsalertmiss,
                svcnotup=svcnotup,
                active_filters=active_db_filters('v_svcmon'),
                available_filters=avail_db_filters('v_svcmon'),
                pkgdiff=pkgdiff,
               )

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

        """ Purge pending alerts
        """
        db((db.alerts.app_id==id)&(db.alerts.sent_at==None)).delete()

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
            size = 4
        ),
        roles = dict(
            pos = 2,
            title = T('Roles'),
            size = 12
        ),
        responsibles = dict(
            pos = 3,
            title = T('Responsibles'),
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

def _where(query, table, var, field, tableid=None):
    if query is None:
        if tableid is not None:
            query = (tableid > 0)
        else:
            query = (db[table].id > 0)
    if var is None: return query
    if len(var) == 0: return query

    if '&' in var and '|' in var:
        """don't even try to guess order
        """
        return query

    done = False

    if var[0] == '|':
        _or=True
        var = var[1:]
    elif var[0] == '&':
        _or=False
        var = var[1:]
    else:
        _or=False

    if '&' in var:
        i = var.index('&')
        chunk = var[:i]
        var = var[i:]
    elif '|' in var:
        i = var.index('|')
        chunk = var[:i]
        var = var[i:]
    else:
        done = True
        chunk = var

    if len(chunk) == 0:
        return query

    if chunk[0] == '!':
        _not = True
        chunk = chunk[1:]
    else:
        _not = False

    if len(chunk) == 0:
        return query

    if chunk == 'empty':
        q = (db[table][field]==None)|(db[table][field]=='')
    elif chunk[0] not in '<>=':
        q = db[table][field].like(chunk)
    else:
        _op = chunk[0]

        if len(chunk) == 0:
            return query

        chunk = chunk[1:]
        if _op == '>':
            q = db[table][field]>chunk
        elif _op == '<':
            q = db[table][field]<chunk
        elif _op == '=':
            q = db[table][field]==chunk

    if _not:
        q = ~q

    if _or:
        query |= q
    else:
        query &= q

    if not done:
        query = _where(query, table, var, field)

    return query

def managers():
    rows = db(db.v_users.manager==1).select()
    m = []
    for row in rows:
        m.append(row.email)
    return ','.join(m)

def domainname(fqdn):
    if fqdn is None or fqdn == "":
        return
    l = fqdn.split('.')
    if len(l) < 2:
        return
    l[0] = ""
    return '.'.join(l)

def alert_format_subject(msg="", app=None, svcname=None):
    s = ""
    if app is not None:
        s += "[%s]"%app
    if svcname is not None:
        s += "[%s]"%svcname
    if len(s) > 0:
        out = ' '.join([s, msg])
    else:
        out = msg
    return T(out)

def alert_format_body(msg="", app=None, svcname=None, node=None, action=None,
                      begin=None, end=None, svctype=None, pid=None):
    def header_field(title=None, value=None):
        if value is None:
            return TR(_style='font-size:0')
        return TR(TD(B(T(title))),TD(value))

    def URL_WITH_HOST(a=None, c=None, f=None, r=None, args=[], vars={}, host=None, scheme="https"):
        path = URL(a=a,c=c,f=f,r=r,args=args,vars=vars)
        try:
            import applications.init.modules.config as cf
            if host is None or not isinstance(host,str): host = cf.http_host
        except:
            pass
        if not isinstance(scheme,str): scheme = r.env.wsgi_url_scheme
        return '%s://%s%s' % (scheme,host,path)
        return path

    out = DIV(
      TABLE(
        header_field("application", app),
        header_field("service name", A(svcname, _href=URL_WITH_HOST(r=request, f='svcmon', vars={'svcname':svcname}))),
        header_field("service type", svctype),
        header_field("node name", A(node, _href=URL_WITH_HOST(r=request, f='node', vars={'nodename':node}))),
        header_field("action", action),
        header_field("begin", str(begin)),
        header_field("end", str(end)),
        header_field("pid", A(pid, _href=URL_WITH_HOST(r=request, f='svcactions', vars={'pid':pid, 'hostname':node, 'perpage':0}))),
        TR(TD(msg, _colspan=2)),
      ),
      _style="width:400"
    )
    return out

def alerts_apps_without_responsible():
    import datetime
    now = datetime.datetime.now()
    in_24h = now + datetime.timedelta(hours=24)

    rows = db((db.v_apps.id>0)&(db.v_apps.mailto==None)).select()
    for row in rows:
        subject = alert_format_subject("application has no responsible", app=row.app)
        body = ""
        dups = db(db.alerts.subject==subject).select()
        if len(dups) > 0:
            """ don't raise a duplicate alert
            """
            continue
        db.alerts.insert(subject=subject,
                         body=body,
                         send_at=in_24h,
                         created_at=now,
                         app_id=row.id,
                         sent_to=managers())

    return dict(alerts=rows)

def alerts_svc_not_on_primary():
    import datetime
    now = datetime.datetime.now()

    rows = db((db.v_svcmon.mon_overallstatus!='up')&(db.v_svcmon.svc_autostart==db.v_svcmon.mon_nodname)).select()
    for row in rows:
        subject = T("[%(app)s][%(svcname)s] service not 'up' on its primary node", dict(app=row.svc_app, svcname=row.mon_svcname))
        body = ""
        dups = db(db.alerts.subject==subject).select()
        if len(dups) > 0:
            """ don't raise a duplicate alert
            """
            continue
        if row.mailto is None or row.mailto == "":
            to = managers()
        else:
            to = row.mailto
        db.alerts.insert(subject=subject,
                         body=body,
                         send_at=now,
                         created_at=now,
                         sent_to=to)

    return dict(alerts=rows)

def alerts_services_not_updated():
    """ Alert if service is not updated for 48h
    """
    import datetime
    now = datetime.datetime.now()
    two_days_ago = now - datetime.timedelta(days=2)
    three_days_ago = now - datetime.timedelta(days=3)

    def format_subject(row):
        return T("[%(app)s][%(svcname)s] service configuration not updated since %(last)s", dict(
                 last=row.updated,
                 app=row.svc_app,
                 svcname=row.svc_name
                )
               )

    rows = db(db.v_services.updated<two_days_ago).select()
    for row in rows:
        subject = format_subject(row)
        body = alert_format_body(DIV(
          P(T("Last status update occured on %s."%str(row.updated))),
          P(T("Service will be purged on %s"%str(row.updated + datetime.timedelta(days=3)))),
        ), svcname=row.svc_name, app=row.svc_app, svctype=row.svc_type)
        dups = db(db.alerts.subject==subject).select()
        if len(dups) > 0:
            """ don't raise a duplicate alert
            """
            continue
        if row.mailto is None or row.mailto == "":
            to = managers()
        else:
            to = row.mailto
        db.alerts.insert(subject=subject,
                         body=body,
                         send_at=now,
                         created_at=now,
                         domain=domainname(row.svc_name),
                         sent_to=to)

    """ Remove the service after 3 days
    """
    rows = db(db.v_services.updated<three_days_ago).select()
    for row in rows:
        db(db.svcmon.mon_svcname==row.svc_name).delete()
        db(db.services.svc_name==row.svc_name).delete()

    return dict(deleted=rows)

def alerts_svcmon_not_updated():
    """ Alert if svcmon is not updated for 2h
    """
    import datetime
    now = datetime.datetime.now()
    two_hours_ago = now - datetime.timedelta(hours=2)
    one_day_ago = now - datetime.timedelta(days=1)

    def format_subject(row):
        return T("[%(app)s][%(svcname)s] service status not updated for more than 2h", dict(app=row.svc_app, svcname=row.mon_svcname))

    rows = db(db.v_svcmon.mon_updated<two_hours_ago).select()
    for row in rows:
        subject = format_subject(row)
        body = alert_format_body(
          T("Service will be purged from database on %s"%str(row.mon_updated+datetime.timedelta(days=1))),
          svcname=row.mon_svcname,
          app=row.svc_app,
          node=row.mon_nodname,
          svctype=row.svc_type
        )
        dups = db(db.alerts.subject==subject).select()
        if len(dups) > 0:
            """ don't raise a duplicate alert
            """
            continue
        if row.mailto is None or row.mailto == "":
            to = managers()
        else:
            to = row.mailto
        db.alerts.insert(subject=subject,
                         body=body,
                         send_at=now,
                         created_at=now,
                         domain=domainname(row.mon_svcname),
                         sent_to=to)

    """ Remove the service after 24h
    """
    rows = db(db.v_svcmon.mon_updated<one_day_ago).select()
    for row in rows:
        db(db.svcmon.mon_svcname==row.mon_svcname).delete()
        db(db.services.svc_name==row.mon_svcname).delete()

    return dict(deleted=rows)

def alerts_failed_actions_not_acked():
    """ Actions not ackowleged : Alert responsibles & Acknowledge
        This function is meant to be scheduled daily, at night,
        and alerts generated should be sent as soon as possible.
    """
    def insert_alert(r, log, rids):
        d = dict(app=r.app,
                 svcname=r.svcname,
                 action=r.action,
                 node=r.hostname)
        subject = T("[%(app)s] failed action '%(svcname)s %(action)s' on node '%(node)s' not acknowledged", d)

        body = alert_format_body(
          map(P, log),
          node=r.hostname,
          svcname=r.svcname,
          app=r.app,
          pid=r.pid,
          action=r.action,
          begin=r.begin,
          end=r.end)

        """ Check if the alert is already queued
        """
        dups = db(db.alerts.action_id==r.id).select()
        if len(dups) > 0:
            return

        """ Queue alert
        """
        if r.mailto is None or r.mailto == "":
            to = managers()
        else:
            to = r.mailto
        db.alerts.insert(subject=subject,
                         body=body,
                         send_at=in_24h,
                         created_at=now,
                         action_id=r.id,
                         action_ids=','.join(rids),
                         domain=domainname(r.svcname),
                         sent_to=to)

    import datetime

    now = datetime.datetime.now()
    in_24h = now + datetime.timedelta(hours=24)
    rows = db((db.v_svcactions.status=='err')&((db.v_svcactions.ack!=1)|(db.v_svcactions.ack==None))).select(orderby=db.v_svcactions.end)
    pid = None
    rids = []
    for row in rows:
        if pid is None:
            pid = row.pid
            if row.status_log != None: log = str(row.status_log).split('\\n')
            else: log = []
            rids.append(str(row.id))
            prev = row
        elif pid != row.pid:
            insert_alert(prev, log, rids)
            pid = row.pid
            if row.status_log != None: log = str(row.status_log).split('\\n')
            else: log = []
            rids = [str(row.id)]
            prev = row
        else:
            if row.status_log != None: log += str(row.status_log).split('\\n')
            rids.append(str(row.id))
    if len(rows) > 0:
        insert_alert(prev, log, rids)

    return dict(alerts_queued=rows)


def send_alerts():
    """ Send mail alert
    """
    import smtplib
    import datetime

    now = datetime.datetime.now()
    server = smtplib.SMTP('localhost')

    rows = db((db.alerts.sent_at==None)&(db.alerts.send_at<now)).select()
    for row in rows:
        """
        body = TABLE(
                 TR(TD(T('node'),TD(row.hostname))),
                 TR(TD(T('service'),TD(row.svcname))),
                 TR(TD(T('app'),TD(row.app))),
                 TR(TD(T('responsibles'),TD(row.responsibles))),
                 TR(TD(T('action'),TD(row.action))),
                 TR(TD(T('begin'),TD(row.begin))),
                 TR(TD(T('end'),TD(row.end))),
                 TR(TD(T('error message'),TD(row.status_log))),
               )
        """
        botaddr = 'admins@opensvc.com'
        msg = "To: %s\r\nFrom: %s\r\nSubject: %s\r\nContent-type: text/html;charset=utf-8\r\n\r\n%s"%(row.sent_to, botaddr, row.subject, row.body)
        try:
            server.sendmail(botaddr, row.sent_to.split(", "), msg)
        except:
            """ Don't mark as sent if the mail sending fails
            """
            continue

        db(db.alerts.id==row.id).update(sent_at=now)
        row.sent_at=now

        """ If the alert concerns an unaknowledged action,
            auto-ack it
        """
        ack_comment = T("Automatically acknowledged upon ticket generation. Alert sent to %(to)s", dict(to=row.sent_to))
        if row.action_ids is not None:
            sql = "update table SVCactions set ack=1, acked_comment=%(ack_comment)s, acked_date=%(acked_date)s, acked_by=%(acked_by)s where action_id in (%(ids)s)"%dict(ack_comment=ack_comment, acked_date=now, acked_by=botaddr, ids=row.action_ids)
            db.executesql(sql)
            #db(db.SVCactions.id==row.action_id).update(ack=1, acked_comment=ack_comment, acked_date=now, acked_by=botaddr)

    server.quit()
    return dict(alerts_sent=rows)

@auth.requires_login()
def alerts():
    columns = dict(
        id = dict(
            pos = 1,
            title = T('Alert Id'),
            size = 3
        ),
        created_at = dict(
            pos = 2,
            title = T('Created at'),
            size = 10
        ),
        send_at = dict(
            pos = 3,
            title = T('Scheduled at'),
            size = 10
        ),
        sent_at = dict(
            pos = 4,
            title = T('Sent at'),
            size = 10
        ),
        sent_to = dict(
            pos = 5,
            title = T('Assigned to'),
            size = 7
        ),
        subject = dict(
            pos = 6,
            title = T('Subject'),
            size = 30
        ),
        body = dict(
            pos = 7,
            title = T('Description'),
            size = 30
        ),
    )
    def _sort_cols(x, y):
        return cmp(columns[x]['pos'], columns[y]['pos'])
    colkeys = columns.keys()
    colkeys.sort(_sort_cols)

    query = _where(None, 'alerts', request.vars.id, 'id')
    query &= _where(None, 'alerts', request.vars.created_at, 'created_at')
    query &= _where(None, 'alerts', request.vars.send_at, 'send_at')
    query &= _where(None, 'alerts', request.vars.sent_at, 'sent_at')
    query &= _where(None, 'alerts', request.vars.responsibles, 'responsibles')
    query &= _where(None, 'alerts', request.vars.subject, 'subject')
    query &= _where(None, 'alerts', request.vars.body, 'body')
    query &= _where(None, 'alerts', domain_perms(), 'domain')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select(orderby=~db.alerts.id)
    else:
        rows = db(query).select(limitby=(start,end), orderby=~db.alerts.id)

    return dict(alerts=rows,
                nav=nav,
                columns=columns, colkeys=colkeys)

@auth.requires_login()
def service_availability(rows, begin=None, end=None):
    h = {}
    def status_merge_down(s):
        if s == 'up': return 'warn'
        elif s == 'down': return 'down'
        elif s == 'stdby up': return 'stdby up with down'
        elif s == 'stdby up with up': return 'warn'
        elif s == 'stdby up with down': return 'stdby up with down'
        elif s == 'undef': return 'down'
        else: return 'undef'

    def status_merge_up(s):
        if s == 'up': return 'up'
        elif s == 'down': return 'warn'
        elif s == 'stdby up': return 'stdby up with up'
        elif s == 'stdby up with up': return 'stdby up with up'
        elif s == 'stdby up with down': return 'warn'
        elif s == 'undef': return 'up'
        else: return 'undef'

    def status_merge_stdby_up(s):
        if s == 'up': return 'stdby up with up'
        elif s == 'down': return 'stdby up with down'
        elif s == 'stdby up': return 'stdby up'
        elif s == 'stdby up with up': return 'stdby up with up'
        elif s == 'stdby up with down': return 'warn'
        elif s == 'undef': return 'stdby up'
        else: return 'undef'

    def status(row):
        s = 'undef'
        for sn in ['mon_containerstatus',
                  'mon_ipstatus',
                  'mon_fsstatus',
                  'mon_appstatus',
                  'mon_diskstatus']:
            if row.svcmon_log[sn] in ['warn', 'stdby down', 'todo']: return 'warn'
            elif row.svcmon_log[sn] == 'undef': return 'undef'
            elif row.svcmon_log[sn] == 'n/a': continue
            elif row.svcmon_log[sn] == 'up': s = status_merge_up(s)
            elif row.svcmon_log[sn] == 'down': s = status_merge_down(s)
            elif row.svcmon_log[sn] == 'stdby up': s = status_merge_stdby_up(s)
            else: return 'undef'
        return s

    if end is None or begin is None:
        return {}
    period = end - begin

    """ First pass at range construction:
          for each row in resultset, create a new range
    """
    for row in rows:
        if row.svcmon_log.mon_svcname not in h:
            h[row.svcmon_log.mon_svcname] = {'ranges': [],
                                  'range_count': 0,
                                  'holes': [],
                                  'begin': begin,
                                  'end': end,
                                  'period': period,
                                  'downtime': 0,
                                  'discarded': [],
                                 }
        s = status(row)
        if s not in ['up', 'stdby up with up']:
            h[row.svcmon_log.mon_svcname]['discarded'] += [(row.svcmon_log.id, s)]
            continue

        """ First range does not need overlap detection
        """
        (b, e) = (row.svcmon_log.mon_begin, row.svcmon_log.mon_end)
        if len(h[row.svcmon_log.mon_svcname]['ranges']) == 0:
            h[row.svcmon_log.mon_svcname]['ranges'] = [(b, e)]
            h[row.svcmon_log.mon_svcname]['range_count'] += 1
            continue

        """ Overlap detection
        """
        add = False
        for i, (b, e) in enumerate(h[row.svcmon_log.mon_svcname]['ranges']):
            if row.svcmon_log.mon_end < b or row.svcmon_log.mon_begin > e:
                """        XXXXXXXXXXX
                    XXX        or         XXX
                """
                add = True
            elif row.svcmon_log.mon_begin >= b and row.svcmon_log.mon_end <= e:
                """        XXXXXXXXXXX
                              XXX
                """
                add = False
                break
            elif row.svcmon_log.mon_begin <= b and row.svcmon_log.mon_end >= e:
                """        XXXXXXXXXXX
                         XXXXXXXXXXXXXXXXX
                """
                add = False
                b = row.svcmon_log.mon_begin
                e = row.svcmon_log.mon_end
                h[row.svcmon_log.mon_svcname]['ranges'][i] = (b, e)
                break
            elif row.svcmon_log.mon_begin < b and row.svcmon_log.mon_end >= b:
                """        XXXXXXXXXXX
                         XXXXX
                """
                add = False
                b = row.svcmon_log.mon_begin
                h[row.svcmon_log.mon_svcname]['ranges'][i] = (b, e)
                break
            elif row.svcmon_log.mon_begin <= e and row.svcmon_log.mon_end > e:
                """        XXXXXXXXXXX
                                   XXXXX
                """
                add = False
                e = row.svcmon_log.mon_end
                h[row.svcmon_log.mon_svcname]['ranges'][i] = (b, e)
                break


        if add:
            h[row.svcmon_log.mon_svcname]['range_count'] += 1
            h[row.svcmon_log.mon_svcname]['ranges'] += [(row.svcmon_log.mon_begin,row.svcmon_log.mon_end)]

    def delta_to_min(d):
        return (d.days*1440)+(d.seconds//60)

    o = db.svcmon_log_ack.mon_begin
    query = (db.svcmon_log_ack.id>0)
    query &= _where(None, 'svcmon_log_ack', request.vars.mon_svcname, 'mon_svcname')
    query &= _where(None, 'svcmon_log_ack', request.vars.mon_begin, 'mon_end')
    query &= _where(None, 'svcmon_log_ack', request.vars.mon_end, 'mon_begin')
    query &= _where(None, 'svcmon_log_ack', domain_perms(), 'mon_svcname')
    acked = db(query).select(orderby=o)

    def get_holes(svc, _e, b):
        ack_overlap = 0
        holes = []

        def _hole(b, e, acked, a):
            if a is None:
                a = dict(mon_acked_by='',
                         mon_acked_on='',
                         mon_comment='',
                         mon_account=1,
                         id='',
                        )
            h = dict(begin=b,
                     end=e,
                     acked=acked,
                     acked_by=a['mon_acked_by'],
                     acked_on=a['mon_acked_on'],
                     acked_comment=a['mon_comment'],
                     acked_account=a['mon_account'],
                     id=a['id'],
                    )
            return h

        for a in [ack for ack in acked if ack.mon_svcname == svc]:
            (ab, ae) = (a.mon_begin, a.mon_end)

            if _e >= ab and b <= ae:
                """ hole is completely acknowledged
                      XXXXX
                          _e
                                   XXXXXXXXXX
                                   b
                         ============= acked segment
                        ab           ae
                """
                holes += [_hole(_e, b, 1, a)]
                ack_overlap += 1
                break

            elif _e <= ab and ab < b and ae >= b:
                """ hole is partly acknowledged
                      XXXXX
                          _e
                                   XXXXXXXXXX
                                   b
                               =========== acked segment
                              ab         ae
                """
                holes += [_hole(_e, ab, 0, None)]
                holes += [_hole(ab, b, 1, a)]
                ack_overlap += 1

            elif ab <= _e and ae < b and ae > _e:
                """ hole is partly acknowledged
                      XXXXX
                          _e
                                   XXXXXXXXXX
                                   b
                     ========= acked segment
                    ab       ae
                """
                holes += [_hole(_e, ae, 1, a)]
                holes += [_hole(ae, b, 0, None)]
                ack_overlap += 1

            elif ab > _e and ab < b and ae > _e and ae < b:
                """ hole is partly acknowledged
                      XXXXX
                          _e
                                        XXXXXXXXXX
                                        b
                               ====== acked segment
                              ab    ae
                """
                holes += [_hole(_e, ab, 0, None)]
                holes += [_hole(ab, ae, 1, a)]
                holes += [_hole(ae, b, 0, None)]
                ack_overlap += 1

        if ack_overlap == 0:
            holes += [_hole(_e, b, 0, None)]

        return holes


    for svc in h:
        _e = None

        for i, (b, e) in enumerate(h[svc]['ranges']):
            """ Merge overlapping ranges
                      begin                            end
                init:   |                              _e
                        |                               |
                prev:   |   XXXXXXXXXXXXXXXXX           |
                        |                   _e          |
                curr:   |                 XXXXXXXXXXXX  |
                        |                 b          e  |
            """
            if _e is not None and b < _e:
                b = _e

            """ Discard segment heading part outside scope
                      begin                            end
                        |                               |
                    XXXXXXXXXXXXXXXXX                   |
                    b   |           e                   |
            """
            if b < begin:
                b = begin

            """ Discard segment trailing part outside scope
                      begin                            end
                        |                               |
                        |                    XXXXXXXXXXXXXXXX
                        |                    b          |   e
            """
            if e > end:
                e = end

            """ Store changed range
            """
            h[svc]['ranges'][i] = (b, e)

            """ Store holes
            """
            if _e is not None and _e < b:
                h[svc]['holes'] += get_holes(svc, _e, b)

            """ Store the current segment endpoint for use in the
                next loop iteration
            """
            _e = e

        if len(h[svc]['ranges']) == 0:
            h[svc]['holes'] += get_holes(svc, begin, end)
        else:
            """ Add heading hole
            """
            (b, e) = h[svc]['ranges'][0]
            if b > begin:
                h[svc]['holes'] = get_holes(svc, begin, b) + h[svc]['holes']

            """ Add trailing hole
            """
            (b, e) = h[svc]['ranges'][-1]
            if e < end:
                h[svc]['holes'] = h[svc]['holes'] + get_holes(svc, e, end)

        """ Account acknowledged time
        """
        for _h in h[svc]['holes']:
            if _h['acked'] == 1 and _h['acked_account'] == 0:
                continue
            h[svc]['downtime'] += delta_to_min(_h['end'] - _h['begin'])

        """ Compute availability
        """
        h[svc]['period_min'] = delta_to_min(h[svc]['period'])

        if h[svc]['period_min'] == 0:
            h[svc]['availability'] = 0
        else:
            h[svc]['availability'] = (h[svc]['period_min'] - h[svc]['downtime']) * 100.0 / h[svc]['period_min']

    return h

def service_availability_chart(h):
    def format_x(ts):
        d = datetime.date.fromtimestamp(ts)
        return "/a50/5{}" + d.strftime("%y-%m-%d")

    def sort_by_avail(x, y):
        return cmp(h[x]['availability'], h[y]['availability'])

    k = h.keys()
    k.sort(sort_by_avail, reverse=True)

    data = []
    from time import mktime
    x_min = 0
    x_max = 0

    def get_range(holes):
        last = 0
        ticks = []
        for _h in holes:
            tsb = mktime(_h['begin'].timetuple())
            tse = mktime(_h['end'].timetuple())
            d1 = tsb - last
            if d1 < 0:
                continue
            d2 = tse - tsb
            if d2 == 0:
                continue
            last = tse
            ticks += [d1, d2]
        if len(ticks) == 0:
            ticks = [0, 0]
        return ticks

    for svc in k:
        if x_min == 0:
            x_min = mktime(h[svc]['begin'].timetuple())
        else:
            x_min = min(mktime(h[svc]['begin'].timetuple()), x_min)

        if x_max == 0:
            x_max = mktime(h[svc]['end'].timetuple())
        else:
            x_max = min(mktime(h[svc]['end'].timetuple()), x_max)

        ticks = get_range([_h for _h in h[svc]['holes'] if _h['acked']==0 or (_h['acked']==1 and _h['acked_account']==1)])
        ticks_acked = get_range([_h for _h in h[svc]['holes'] if _h['acked']==1 and _h['acked_account']==0])

        data += [(svc, tuple(ticks), tuple(ticks_acked))]

    if len(data) == 0:
        return

    duration = x_max - x_min
    if duration < 691200:
        ti = 86400
    elif duration < 2764800:
        ti = 604800
    else:
        ti = 2592000

    action = str(URL(r=request,c='static',f='avail.png'))
    path = 'applications'+action
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 3
    theme.reinitialize()

    ar = area.T(y_coord = category_coord.T(data, 0),
                size = (150,len(data)*8),
                x_range = (x_min, x_max),
                x_axis = axis.X(label="", format=format_x, tic_interval=ti),
                y_axis = axis.Y(label="",  format="/4{}%s"))
    bar_plot.fill_styles.reset()

    chart_object.set_defaults(interval_bar_plot.T,
                              direction="horizontal",
                              width=3,
                              cluster_sep = 0,
                              data=data)
    plot1 = interval_bar_plot.T(
                fill_styles=[fill_style.Plain(bgcolor=color.salmon), None],
                line_styles=[None, None],
                cluster=(0,2),
                label="/5accounted"
    )
    plot2 = interval_bar_plot.T(
                fill_styles=[fill_style.Plain(bgcolor=color.thistle3), None],
                line_styles=[None, None],
                hcol=2, cluster=(1,2),
                label="/5ignored"
    )
    ar.add_plot(plot1, plot2)
    ar.draw(can)
    can.close()
    return action

def str_to_date(s, fmt="%Y-%m-%d %H:%M:%S"):
    if s is None or s == "" or len(fmt) == 0:
        return None
    s = s.strip()
    if s[0] in ["<", ">"]:
        s = s[1:]
    try:
        return datetime.datetime.strptime(s, fmt)
    except:
        return str_to_date(s, fmt[0:-1])

@auth.requires_login()
def _svcmon_log_ack(request):
    request.vars.ackflag = "0"
    svcs = set([])

    b = str_to_date(request.vars.ack_begin)
    e = str_to_date(request.vars.ack_end)
    if request.vars.ac == 'true':
        account = 1
    else:
        account = 0

    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        svcs |= set(['_'.join(key.split('_')[1:-1])])
    for svc in svcs:
        svcmon_log_ack_write(svc, b, e, 
                             request.vars.ackcomment,
                             account)

@auth.requires_login()
def svcmon_log():
    if request.vars.ackflag == "1":
        _svcmon_log_ack(request)

    now = datetime.datetime.now()
    if request.vars.mon_begin is None or request.vars.mon_begin == "":
        begin = now - datetime.timedelta(days=7, microseconds=now.microsecond)
        request.vars.mon_begin = ">"+str(begin)
    else:
        begin = str_to_date(request.vars.mon_begin)

    if request.vars.mon_end is None or request.vars.mon_end == "":
        end = now - datetime.timedelta(seconds=1200, microseconds=now.microsecond)
        request.vars.mon_end = "<"+str(end)
    else:
        end = str_to_date(request.vars.mon_end)

    toggle_db_filters()

    o = db.svcmon_log.mon_begin|db.svcmon_log.mon_end
    query = db.v_svcmon.mon_svcname==db.svcmon_log.mon_svcname
    query &= db.v_svcmon.mon_nodname==db.svcmon_log.mon_nodname
    query &= _where(None, 'svcmon_log', request.vars.mon_svcname, 'mon_svcname')
    query &= _where(None, 'svcmon_log', request.vars.mon_begin, 'mon_end')
    query &= _where(None, 'svcmon_log', request.vars.mon_end, 'mon_begin')
    query &= _where(None, 'svcmon_log', domain_perms(), 'mon_svcname')

    query = apply_db_filters(query, 'v_svcmon')

    rows = db(query).select(orderby=o)
    nav = DIV()

    h = service_availability(rows, begin, end)

    img = service_availability_chart(h)

    return dict(rows=rows,
                h=h,
                nav=nav,
                img=img,
                active_filters=active_db_filters('v_svcmon'),
                available_filters=avail_db_filters('v_svcmon'),
               )

@auth.requires_login()
def ajax_pkgdiff():
    nodes = request.vars.pkgnodes.split(',')
    n = len(nodes)
    sql = """select * from (
               select group_concat(pkg_nodename order by pkg_nodename),
                      pkg_name,
                      pkg_version,
                      pkg_arch,
                      count(pkg_nodename) as c
               from packages
               where pkg_nodename in (%(nodes)s)
               group by pkg_name,pkg_version,pkg_arch
               order by pkg_name,pkg_version,pkg_arch
             ) as t
             where t.c!=%(n)s;
          """%dict(n=n, nodes=','.join(map(repr, nodes)))
    rows = db.executesql(sql)

    def fmt_header():
        return TR(
                 TH(T("Node")),
                 TH(T("Package")),
                 TH(T("Version")),
                 TH(T("Arch")),
               )

    def fmt_line(row):
        return TR(
                 TD(row[0]),
                 TD(row[1]),
                 TD(row[2]),
                 TD(row[3]),
               )

    def fmt_table(rows):
        return TABLE(
                 fmt_header(),
                 map(fmt_line, rows),
               )

    return DIV(fmt_table(rows))

@auth.requires_login()
def ajax_envfile():
    return DIV(
             H3(T("Service configuration file for %(svc)s",dict(
                     svc=request.vars.svcname
                   )
                ),
                _style='text-align:center',
             ),
             envfile(request.vars.svcname)
           )

@auth.requires_login()
def envfile(svcname):
    query = _where(None, 'services', svcname, 'svc_name')
    query &= _where(None, 'v_svcmon', domain_perms(), 'svc_name')
    rows = db(query).select()
    if len(rows) == 0:
        return "None"
    #return dict(svc=rows[0])
    envfile = rows[0]['services']['svc_envfile']
    if envfile is None:
        return "None"
    return DIV(
             P(T("updated: %(upd)s",dict(
                     upd=rows[0]['services']['updated']
                   ),
                ),
                _style='text-align:center',
             ),
             PRE(envfile.replace('\\n','\n'), _style="text-align:left"),
           )

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
    db(db.auth_membership.group_id==id).delete()
    db(db.apps_permissions.group_id==id).delete()
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

@auth.requires_membership('Manager')
def _obs_warn_date_edit(request):
    _obs_date_edit(request, "warn")

@auth.requires_membership('Manager')
def _obs_alert_date_edit(request):
    _obs_date_edit(request, "alert")

@auth.requires_membership('Manager')
def _obs_date_edit(request, what):
    ids = ([])
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        id = int(key[6:])
        date = request.vars[what+"_date_"+str(id)]
        if date is None or len(date) == 0:
            sql = """update obsolescence
                     set obs_%(what)s_date='',
                         obs_%(what)s_date_updated='%(now)s',
                         obs_%(what)s_date_updated_by='%(user)s'
                     where id=%(id)s;
                  """%dict(id=id,
                           now=datetime.datetime.now(),
                           what=what,
                           user=' '.join([session.auth.user.first_name, session.auth.user.last_name])
                          )
        else:
            sql = """update obsolescence
                     set obs_%(what)s_date='%(date)s',
                         obs_%(what)s_date_updated='%(now)s',
                         obs_%(what)s_date_updated_by='%(user)s'
                     where id=%(id)s;
                  """%dict(id=id,
                           now=datetime.datetime.now(),
                           what=what,
                           date=date,
                           user=' '.join([session.auth.user.first_name, session.auth.user.last_name])
                          )
        #raise Exception(sql)
        db.executesql(sql)

@auth.requires_membership('Manager')
def _obs_item_del(request):
    ids = ([])
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        ids += ([int(key[6:])])
    sql = "delete from obsolescence where id in (%s)"%','.join(map(str, ids))
    db.executesql(sql)

def _refresh_obsolescence(request):
    cron_obsolescence_os()
    cron_obsolescence_hw()

@auth.requires_membership('Manager')
def obsolescence_config():
    if request.vars.action == "del":
        _obs_item_del(request)
    elif request.vars.action == "set_warn_date":
        _obs_warn_date_edit(request)
    elif request.vars.action == "set_alert_date":
        _obs_alert_date_edit(request)
    elif request.vars.action == "refresh":
        _refresh_obsolescence(request)

    toggle_db_filters()

    o = db.obsolescence.obs_type
    o |= db.obsolescence.obs_name
    o |= db.obsolescence.obs_warn_date
    o |= db.obsolescence.obs_alert_date

    g = db.obsolescence.obs_type|db.obsolescence.obs_name

    query = (db.obsolescence.obs_type=="os")&(db.obsolescence.obs_name==db.v_nodes.os_concat)
    query |= (db.obsolescence.obs_type=="hw")&(db.obsolescence.obs_name==db.v_nodes.model)
    query &= _where(None, 'obsolescence', request.vars.obs_type, 'obs_type')
    query &= _where(None, 'obsolescence', request.vars.obs_name, 'obs_name')
    query &= _where(None, 'obsolescence', request.vars.obs_warn_date, 'obs_warn_date')
    query &= _where(None, 'obsolescence', request.vars.obs_alert_date, 'obs_alert_date')

    query = apply_db_filters(query, 'v_nodes')

    (start, end, nav) = _pagination(request, query, groupby=g)
    if start == 0 and end == 0:
        rows = db(query).select(db.obsolescence.ALL, db.v_nodes.id.count(), orderby=o, groupby=g)
    else:
        rows = db(query).select(db.obsolescence.ALL, db.v_nodes.id.count(), limitby=(start,end), orderby=o, groupby=g)

    return dict(obsitems=rows,
                active_filters=active_db_filters('v_nodes'),
                available_filters=avail_db_filters('v_nodes'),
                nav=nav)

def ajax_filter_cloud():
    val = request.vars.filtervalue
    fil = request.vars.addfilter
    filters = db(db.filters.id==fil).select()
    if len(filters) == 0:
        return DIV()
    if filters[0].fil_need_value != 1:
        return DIV()
    if filters[0].fil_search_table is None:
        return DIV()
    n = {}
    f = filters[0]
    col = db[f.fil_search_table][f.fil_column]
    q = col.like('%'+val+'%')
    rows = db(q).select(col)
    for i in [r[f.fil_column] for r in rows]:
        if i in n:
            n[i] += 1
        else:
            n[i] = 1
    if len(n) == 0:
        return DIV()
    c_max = max(n.values())
    def format_item(i, c, c_max):
        s = float(c) / c_max * 100 + 70
        return SPAN(i+' ',
                    _onClick="""getElementById("filtervalue").value="%s";
                                getElementById("filtervalue").focus();
                             """%str(i),
                    _style="""font-size:'+str(s)+'%;
                              padding:0.4em;
                              cursor:pointer;
                           """
                   )
    d = []
    for i in sorted(n):
        if i == '':
            continue
        d += [format_item(i, n[i], c_max)]
    return SPAN(d)

def ajax_obsolete_os_nodes():
    if request.vars.obs_type == "os":
        query = (db.obsolescence.obs_type=="os")&(db.v_nodes.os_concat==request.vars.obs_name)
    elif request.vars.obs_type == "hw":
        query = (db.obsolescence.obs_type=="hw")&(db.v_nodes.model==request.vars.obs_name)
    else:
        return DIV()

    query = apply_db_filters(query, 'v_nodes')
    rows = db(query).select(db.v_nodes.nodename, orderby=db.v_nodes.nodename, groupby=db.v_nodes.nodename)
    nodes = [row.nodename for row in rows]
    return DIV(
             H3(T("""Nodes in %(os)s""",dict(os=request.vars.obs_name))),
             PRE('\n'.join(nodes)),
           )

@auth.requires_login()
def svcmon():
    service_action()

    columns = dict(
        svcname = dict(
            pos = 1,
            title = T('Service'),
            display = True,
            size = 10
        ),
        containertype = dict(
            pos = 2,
            title = T('Container type'),
            display = True,
            size = 3
        ),
        svcapp = dict(
            pos = 3,
            title = T('App'),
            display = True,
            size = 3
        ),
        svctype = dict(
            pos = 4,
            title = T('Service type'),
            display = True,
            size = 3
        ),
        responsibles = dict(
            pos = 4,
            title = T('Responsibles'),
            display = False,
            size = 5
        ),
        nodetype = dict(
            pos = 5,
            title = T('Node type'),
            display = True,
            size = 3
        ),
        nodename = dict(
            pos = 6,
            title = T('Node name'),
            display = True,
            size = 6
        ),
        overallstatus = dict(
            pos = 7,
            title = T('Status'),
            display = True,
            size = 4
        ),
        mon_updated = dict(
            pos = 8,
            title = T('Last status update'),
            display = False,
            size = 6
        ),
        mon_frozen = dict(
            pos = 9,
            title = T('Frozen'),
            display = False,
            size = 3
        ),
        svc_vcpus = dict(
            pos = 10,
            title = T('Vcpus'),
            display = False,
            size = 3
        ),
        svc_vmem = dict(
            pos = 11,
            title = T('Vmem'),
            display = False,
            size = 3
        ),
    )

    def _sort_cols(x, y):
        return cmp(columns[x]['pos'], columns[y]['pos'])
    colkeys = columns.keys()
    colkeys.sort(_sort_cols)

    o = db.v_svcmon.mon_svcname
    o |= ~db.v_svcmon.mon_overallstatus
    o |= ~db.v_svcmon.mon_nodtype
    o |= db.v_svcmon.mon_nodname

    toggle_db_filters()

    query = _where(None, 'v_svcmon', request.vars.svcname, 'mon_svcname')
    query &= _where(None, 'v_svcmon', request.vars.svctype, 'mon_svctype')
    query &= _where(None, 'v_svcmon', request.vars.containerstatus, 'mon_containerstatus')
    query &= _where(None, 'v_svcmon', request.vars.overallstatus, 'mon_overallstatus')
    query &= _where(None, 'v_svcmon', request.vars.svcapp, 'svc_app')
    query &= _where(None, 'v_svcmon', request.vars.responsibles, 'responsibles')
    query &= _where(None, 'v_svcmon', request.vars.svcautostart, 'svc_autostart')
    query &= _where(None, 'v_svcmon', request.vars.containertype, 'svc_containertype')
    query &= _where(None, 'v_svcmon', request.vars.nodename, 'mon_nodname')
    query &= _where(None, 'v_svcmon', request.vars.nodetype, 'mon_nodtype')
    query &= _where(None, 'v_svcmon', request.vars.mon_updated, 'mon_updated')
    query &= _where(None, 'v_svcmon', request.vars.mon_frozen, 'mon_frozen')
    query &= _where(None, 'v_svcmon', request.vars.svc_vcpus, 'svc_vcpus')
    query &= _where(None, 'v_svcmon', request.vars.svc_vmem, 'svc_vmem')
    query &= _where(None, 'v_svcmon', domain_perms(), 'mon_nodname')

    query = apply_db_filters(query, 'v_svcmon')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select(orderby=o)
    else:
        rows = db(query).select(limitby=(start,end), orderby=o)

    msgs = db(db.svcmessages.id>0).select()
    svcmsg = [msg.msg_svcname for msg in msgs if len(msg.msg_body)>0]

    return dict(columns=columns, colkeys=colkeys, actions=rows,
                services=rows,
                nav=nav,
                svcmsg=svcmsg,
                active_filters=active_db_filters('v_svcmon'),
                available_filters=avail_db_filters('v_svcmon'),
               )

class viz(object):
    vizdir = 'applications'+str(URL(r=request,c='static',f='/'))
    vizprefix = 'tempviz'
    loc = {
        'country': {},
        'city': {},
        'building': {},
        'floor': {},
        'room': {},
        'rack': {},
    }
    svcclu = {}
    services = set([])
    resources = {}
    nodes = set([])
    disks = {}
    cdg = {}
    cdgdg = {}
    vidcdg = {}
    array = {}
    arrayinfo = {}
    disk2svc = set([])
    node2disk = set([])
    node2svc = set([])
    data = ""
    img_node = 'applications'+str(URL(r=request,c='static',f='node.png'))
    img_disk = 'applications'+str(URL(r=request,c='static',f='hd.png'))

    def __str__(self):
        buff = """
        graph G {
                //size=12;
                rankdir=LR;
                ranksep=2.5;
                //nodesep = 0.1;
                //sep=0.1;
                splines=false;
                penwidth=1;
                //center=true;
                fontsize=8;
                compound=true;
                node [shape=plaintext, fontsize=8];
                edge [fontsize=8];
                bgcolor=white;

        """
        self.add_services()
        self.add_arrays()
        self.add_citys()
        #self.rank(['cluster_'+s for s in self.array])
        #self.rank(self.services)
        buff += self.data
        buff += "}"
        return buff

    def write(self, type):
        import tempfile
        f = tempfile.NamedTemporaryFile(dir=self.vizdir, prefix=self.vizprefix)
        f.close()
        dot = f.name + '.dot'
        f = open(dot, 'w')
        f.write(str(self))
        f.close()
        if type == 'dot':
            return dot
        from subprocess import Popen
        dst = f.name + '.' + type
        cmd = [ 'dot', '-T'+type, '-o', dst, dot ]
        process = Popen(cmd, stdout=None, stderr=None)
        process.communicate()
        return dst

    def viz_cron_cleanup(self):
        """ unlink static/tempviz*.png
        """
        import os
        import glob
        for name in glob.glob(os.path.join(self.vizdir, self.vizprefix+'*.png')):
            os.unlink(name)
        for name in glob.glob(os.path.join(self.vizdir, self.vizprefix+'*.dot')):
            os.unlink(name)

        for name in glob.glob(os.path.join(self.vizdir, 'stats_*.png')):
            os.unlink(name)

    def __init__(self):
        pass

    def vid_svc(self, svc, nodename):
        return "svc_"+nodename.replace(".", "_").replace("-", "_")+"_"+svc.replace(".", "_").replace("-", "_")

    def vid_svc_dg(self, svc, dg):
        return "dg_"+svc.replace(".", "_").replace("-", "_")+"_"+dg

    def vid_node(self, node):
        return 'node_'+node.replace(".", "_").replace("-", "_")

    def vid_disk(self, id):
        return 'disk_'+str(id).replace(".", "_").replace("-", "_")

    def vid_loc(self, id):
        return str(id).replace(".", "_").replace("-", "_").replace(" ", "_")

    def add_service(self, svc):
        vid = self.vid_svc(svc.svc_name, svc.mon_nodname)
        if vid in self.services: return
        self.services = set([vid])
        if svc.mon_overallstatus == "warn":
            color = "orange"
        elif svc.mon_overallstatus == "up":
            color = "green"
        else:
            color = "grey"
        servicesdata = r"""
        %(v)s [label="%(s)s", style="rounded,filled", fillcolor="%(color)s", fontsize="12"];
        """%(dict(v=vid, s=svc.svc_name, color=color))
        if svc.mon_nodname not in self.svcclu:
            self.svcclu[svc.mon_nodname] = {}
        if svc.mon_overallstatus not in self.svcclu[svc.mon_nodname]:
            self.svcclu[svc.mon_nodname][svc.mon_overallstatus] = set([])
        self.svcclu[svc.mon_nodname][svc.mon_overallstatus] |= set([servicesdata])

    def add_node(self, svc):
        vid = self.vid_node(svc.mon_nodname)
        if vid in self.nodes: return
        self.nodes |= set([vid])
        if svc.loc_city not in self.loc['city']:
            self.loc['city'][svc.loc_city] = ""
        self.loc['city'][svc.loc_city] += r"""
        %(v)s [label="", image="%(img)s"];
        subgraph cluster_%(v)s {fontsize=8; penwidth=0; label="%(n)s\n%(model)s\n%(mem)s MB"; labelloc=b; %(v)s};
        """%(dict(v=vid, n=svc.mon_nodname, model=svc.model, mem=svc.mem_bytes, img=self.img_node))

    def add_disk(self, id, disk, size="", vendor="", model="", arrayid="", devid=""):
        vid = self.vid_disk(id)
        if disk in self.disks: return
        self.disks[disk]= vid
        self.add_array(vid, arrayid, vendor, model)
        self.data += r"""
        %(id)s [label="%(name)s\n%(devid)s\n%(size)s GB", image="%(img)s"];
        """%(dict(id=vid, name=disk, size=size, img=self.img_disk, devid=devid))

    def add_array(self, vid, arrayid="", vendor="", model=""):
        if arrayid == "" or arrayid is None:
            return
        if arrayid not in self.array:
            self.array[arrayid] = set([vid])
        else:
            self.array[arrayid] |= set([vid])
        if arrayid not in self.arrayinfo:
            title = arrayid
            self.arrayinfo[arrayid] = r"%s\n%s - %s"%(title, vendor.strip(), model.strip())

    def add_services(self):
        for n in self.svcclu:
            for s in self.svcclu[n]:
                self.data += r"""subgraph cluster_%(n)s_%(s)s {penwidth=0;
                %(svcs)s
        };"""%dict(n=n.replace('.','_').replace('-','_'), s=s.replace(' ','_'), svcs=''.join(self.svcclu[n][s]))

    def add_citys(self):
        for a in self.loc['city']:
            self.data += r"""
        subgraph cluster_%(a)s {label="%(l)s"; color=grey; style=rounded; fontsize=12; %(n)s};
        """%(dict(a=self.vid_loc(a), l=a, n=self.loc['city'][a]))

    def add_arrays(self):
        for a in self.array:
            if a is None:
                continue
            nodes = [self.cdg_cluster(v) for v in self.array[a] if "cdg_" in v]
            nodes += [v for v in self.array[a] if "cdg_" not in v]
            self.data += r"""
        subgraph cluster_%(a)s {label="%(l)s"; fillcolor=lightgrey; style="rounded,filled"; fontsize=12; %(disks)s};
        """%(dict(a=a.replace("-","_"), l=self.arrayinfo[a], disks=';'.join(nodes)))

    def rank(self, list):
        return """{ rank=same; %s };
               """%'; '.join(list)

    def add_node2svc(self, svc):
        vid1 = self.vid_node(svc.mon_nodname)
        vid2 = self.vid_svc(svc.svc_name, svc.mon_nodname)
        key = vid1+vid2
        if key in self.node2svc: return
        if svc.mon_overallstatus == "up":
            color = "darkgreen"
        else:
            color = "grey"
        self.node2svc |= set([key])
        self.data += """
        edge [color=%(c)s, label="", arrowsize=0, penwidth=1]; %(n)s -- %(d)s;
        """%(dict(c=color, n=vid1, d=vid2))

    def add_disk2svc(self, disk, svc, dg=""):
        vid1 = self.disks[disk]
        if dg == "":
            vid2 = self.vid_svc(svc.svc_name, svc.mon_nodname)
        else:
            vid2 = self.vid_svc_dg(svc.svc_name, dg)
        key = vid1+vid2
        if key in self.disk2svc: return
        self.disk2svc |= set([key])
        if svc.mon_overallstatus == "up":
            color = "darkgreen"
        else:
            color = "grey"
        self.data += """
        edge [color=%(c)s, label="", arrowsize=0, penwidth=1]; %(s)s -- %(d)s;
        """%(dict(c=color, d=vid1, s=vid2))

    def cdg_cluster(self, cdg):
        if cdg not in self.cdg or len(self.cdg[cdg]) == 0:
            return ""
        if cdg in self.cdgdg:
            dg = self.cdgdg[cdg]
        else:
            dg = cdg

        return r"""
            %(cdg)s [shape="plaintext"; label=<<table color="white"
            cellspacing="0" cellpadding="2" cellborder="1">
            <tr><td colspan="3">%(dg)s</td></tr>
            <tr><td>wwid</td><td>devid</td><td>size</td></tr>
            %(n)s
            </table>>]"""%dict(dg=dg, cdg=cdg, n=''.join(self.cdg[cdg]))

    def vid_cdg(self, d):
        key = d.disk_arrayid,d.disk_svcname,d.disk_dg
        cdg = 'cdg_'+str(len(self.vidcdg))
        if key not in self.vidcdg:
            self.vidcdg[key] = cdg
            self.cdgdg[cdg] = d.disk_dg
        return self.vidcdg[key]

    def add_dgdisk(self, d):
        cdg = self.vid_cdg(d)
        vid = self.vid_disk(d.id)
        self.disks[d.disk_id] = vid
        self.add_array(cdg, d.disk_arrayid, d.disk_vendor, d.disk_model)
        if cdg not in self.cdg:
            self.cdg[cdg] = []
        label="<tr><td>%(name)s</td><td>%(devid)s</td><td>%(size)s GB</td></tr>"%(dict(id=vid, name=d.disk_id, size=d.disk_size, img=self.img_disk, devid=d.disk_devid))
        if label not in self.cdg[cdg]:
            self.cdg[cdg].append(label)

    def add_dg2svc(self, cdg, svc, dg=""):
        vid1 = cdg
        if dg == "":
            vid2 = self.vid_svc(svc.svc_name, svc.mon_nodname)
        else:
            vid2 = self.vid_svc_dg(svc.svc_name, dg)
        key = cdg+vid2
        if key in self.disk2svc: return
        self.disk2svc |= set([key])
        if svc.mon_overallstatus == "up":
            color = "darkgreen"
        else:
            color = "grey"
        self.data += """
        edge [color=%(c)s, label="", arrowsize=0, penwidth=1]; %(s)s -- %(cdg)s;
        """%(dict(c=color, d=vid1, s=vid2, cdg=cdg))

    def add_disks(self, svc):
        svccdg = set([])
        q = (db.v_svcdisks.disk_svcname==svc.svc_name)
        q &= (db.v_svcdisks.disk_nodename==svc.mon_nodname)
        q &= (db.v_svcdisks.disk_id!="")
        dl = db(q).select()
        if len(dl) == 0:
            disk_id = svc.mon_nodname + "_unknown"
            self.add_disk(svc.mon_nodname, disk_id, size="?")
            self.add_disk2svc(disk_id, svc)
        else:
            for d in dl:
                if d.disk_dg is None or d.disk_dg == "":
                    disk_id = svc.mon_nodname + "_unknown"
                    self.add_disk(svc.mon_nodname, disk_id, size="?")
                    self.add_disk2svc(disk_id, svc)
                else:
                    svccdg |= set([self.vid_cdg(d)])
                    self.add_dgdisk(d)
        for cdg in svccdg:
            self.add_dg2svc(cdg, svc)

def svcmon_viz_img(services):
    v = viz()
    for svc in services:
        v.add_node(svc)
        v.add_disks(svc)
        v.add_service(svc)
        v.add_node2svc(svc)
    fname = v.write('png')
    import os
    img = str(URL(r=request,c='static',f=os.path.basename(fname)))
    return img

def ajax_svcmon_viz():
    s = svcmon()
    img = svcmon_viz_img(s['services'])
    return IMG(_src=img, _border=0)

def svcmon_viz():
    request.vars['perpage'] = 0
    s = svcmon()
    img = svcmon_viz_img(s['services'])
    return dict(s=s['services'], img=img)

def viz_cron_cleanup():
    viz().viz_cron_cleanup()

def svcmon_csv():
    import gluon.contenttype
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    request.vars['perpage'] = 0
    return str(svcmon()['services'])

def cron_obsolescence_hw():
    sql = """insert ignore into obsolescence (obs_type, obs_name)
             select "hw", model
             from nodes
             where model!=''
             group by model;
          """
    db.executesql(sql)
    return dict(message=T("done"))

def cron_obsolescence_os():
    sql = """insert ignore into obsolescence (obs_type, obs_name)
             select "os", concat_ws(" ", os_name, os_vendor, os_release, os_update)
             from nodes
             where os_name!='' or os_vendor!='' or os_release!='' or os_update!=''
             group by os_name, os_vendor, os_release, os_update;
          """
    db.executesql(sql)
    return dict(message=T("done"))

def cron_stat_day():
    #when = datetime.datetime.now()-datetime.timedelta(days=14)
    when = None
    if when is None:
        when = datetime.datetime.now()
    begin = datetime.datetime(year=when.year, month=when.month, day=when.day, hour=0, minute=0, second=0)
    end = begin + datetime.timedelta(days=1, seconds=-1)

    pairs = ["nb_svc=(select count(distinct svc_name) from services)"]
    pairs += ["nb_action=(select count(distinct id) from SVCactions where begin>'%s' and begin<'%s')"%(begin, end)]
    pairs += ["nb_action_err=(select count(distinct id) from SVCactions where begin>'%s' and begin<'%s' and status='err')"%(begin, end)]
    pairs += ["nb_action_warn=(select count(distinct id) from SVCactions where begin>'%s' and begin<'%s' and status='warn')"%(begin, end)]
    pairs += ["nb_action_ok=(select count(distinct id) from SVCactions where begin>'%s' and begin<'%s' and status='ok')"%(begin, end)]
    pairs += ["nb_apps=(select count(distinct svc_app) from services)"]
    pairs += ["nb_accounts=(select count(distinct id) from auth_user)"]
    pairs += ["nb_svc_with_drp=(select count(distinct svc_name) from services where svc_drpnode is not NULL and svc_drpnode!='')"]
    pairs += ["nb_svc_prd=(select count(distinct svc_name) from services where svc_type='PRD')"]
    pairs += ["nb_svc_cluster=(select sum(length(svc_nodes)-length(replace(svc_nodes,' ',''))+1>1) from services)"]
    pairs += ["nb_nodes=(select count(distinct mon_nodname) from svcmon)"]
    pairs += ["nb_nodes_prd=(select count(distinct mon_nodname) from v_svcmon where mon_nodtype='PRD')"]
    pairs += ["disk_size=(select sum(t.disk_size) from (select distinct s.disk_id, s.disk_size from svcdisks s) t)"]
    sql = "insert into stat_day set day='%(end)s', %(pairs)s on duplicate key update %(pairs)s"%dict(end=end, pairs=','.join(pairs))
    #raise Exception(sql)
    db.executesql(sql)
    return dict(sql=sql)

def cron_stat_day_svc():
    when = None
    if when is None:
        when = datetime.datetime.now()
    begin = datetime.datetime(year=when.year, month=when.month, day=when.day, hour=0, minute=0, second=0)
    end = begin + datetime.timedelta(days=1, seconds=-1)

    rows = db(db.services.id>0).select(db.services.svc_name, groupby=db.services.svc_name)

    for row in rows:
        svc = row.svc_name
        pairs = ["nb_action=(select count(distinct id) from SVCactions where begin>'%s' and begin<'%s' and hostname='%s')"%(begin, end, svc)]
        pairs += ["nb_action_err=(select count(distinct id) from SVCactions where begin>'%s' and begin<'%s' and status='err' and hostname='%s')"%(begin, end, svc)]
        pairs += ["nb_action_warn=(select count(distinct id) from SVCactions where begin>'%s' and begin<'%s' and status='warn' and hostname='%s')"%(begin, end, svc)]
        pairs += ["nb_action_ok=(select count(distinct id) from SVCactions where begin>'%s' and begin<'%s' and status='ok' and hostname='%s')"%(begin, end, svc)]
        pairs += ["disk_size=(select sum(t.disk_size) from (select distinct s.disk_id, s.disk_size from svcdisks s where s.disk_svcname='%s') t)"%svc]
        sql = "insert into stat_day_svc set day='%(end)s', svcname='%(svc)s', %(pairs)s on duplicate key update %(pairs)s"%dict(end=end, svc=svc, pairs=','.join(pairs))
        #raise Exception(sql)
        db.executesql(sql)
    return dict(sql=sql)

def cron_purge_alerts():
    sql = "delete from alerts using alerts, SVCactions where alerts.sent_at is NULL and alerts.action_id=SVCactions.id and SVCactions.ack=1"
    db.executesql(sql)

def cron_unfinished_actions():
    now = datetime.datetime.now()
    tmo = now - datetime.timedelta(minutes=120)
    q = (db.SVCactions.begin < tmo)
    q &= (db.SVCactions.end==None)
    rows = db(q).update(status="err")
    return "%d actions marked timed out"%rows

def _svcaction_ack(request):
    action_ids = ([])
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        action_ids += ([key[6:]])
    for action_id in action_ids:
        query = (db.v_svcactions.id == action_id)&(db.v_svcactions.status != "ok")
        rows = db(query).select()
        if len(rows) != 1:
            continue
        a = rows[0]
        _svcaction_ack_one(request, action_id)

        """ Cancel pending alert
        """
        db((db.alerts.action_id==action_id)&(db.alerts.sent_at==None)).delete()
    del request.vars.ackcomment


def _svcaction_ack_one(request, action_id):
        query = (db.v_svcactions.id == action_id)&(db.v_svcactions.status != "ok")
        db(query).update(ack=1,
                         acked_comment=request.vars.ackcomment,
                         acked_by=' '.join([session.auth.user.first_name, session.auth.user.last_name]),
                         acked_date=datetime.datetime.now())

@auth.requires_login()
def svcactions():
    columns = dict(
        svcname = dict(
            pos = 1,
            title = T('Service'),
            display = True,
            size = 10
        ),
        hostname = dict(
            pos = 2,
            title = T('Node name'),
            display = True,
            size = 6
        ),
        pid = dict(
            pos = 3,
            title = T('Pid'),
            display = True,
            size = 4
        ),
        action = dict(
            pos = 4,
            title = T('Action'),
            display = True,
            size = 6
        ),
        status = dict(
            pos = 5,
            title = T('Status'),
            display = True,
            size = 3
        ),
        begin = dict(
            pos = 6,
            title = T('Begin'),
            display = True,
            size = 6
        ),
        end = dict(
            pos = 7,
            title = T('End'),
            display = True,
            size = 6
        ),
        status_log = dict(
            pos = 8,
            title = T('Log'),
            display = True,
            size = 10
        ),
        time = dict(
            pos = 9,
            title = T('Duration'),
            display = False,
            size = 10
        ),
        id = dict(
            pos = 10,
            title = T('Id'),
            display = False,
            size = 3
        ),
        ack = dict(
            pos = 11,
            title = T('Ack'),
            display = False,
            size = 3
        ),
        app = dict(
            pos = 12,
            title = T('App'),
            display = False,
            size = 3
        ),
        responsibles = dict(
            pos = 13,
            title = T('Responsibles'),
            display = False,
            size = 6
        ),
    )

    def _sort_cols(x, y):
        return cmp(columns[x]['pos'], columns[y]['pos'])
    colkeys = columns.keys()
    colkeys.sort(_sort_cols)

    o = ~db.v_svcactions.begin|~db.v_svcactions.end|~db.v_svcactions.id

    toggle_db_filters()

    if request.vars.ackflag == "1":
        _svcaction_ack(request)

    # filtering
    query = (db.v_svcactions.id>0)
    for key in columns.keys():
        if key not in request.vars.keys():
            continue
        query &= _where(None, 'v_svcactions', request.vars[key], key)

    query &= _where(None, 'v_svcactions', domain_perms(), 'hostname')

    query = apply_db_filters(query, 'v_svcactions')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select(orderby=o)
    else:
        rows = db(query).select(orderby=o, limitby=(start,end))

    return dict(columns=columns, colkeys=colkeys, actions=rows,
                active_filters=active_db_filters('v_svcactions'),
                available_filters=avail_db_filters('v_svcactions'),
                nav=nav)

def svcactions_rss():
    #return BEAUTIFY(request)
    import gluon.contrib.rss2 as rss2
    import datetime
    d = svcactions()
    url = request.url[:-4]
    items = []
    desc = 'filtering options for this feed: '
    for key in request.vars.keys():
        if request.vars[key] != '': desc += key+'['+request.vars[key]+'] '
    for action in d['actions']:
        items += [rss2.RSSItem(title="""[osvc] %s %s returned %s"""%(action.action,action.svcname,action.status),
                      link = """http://%s%s?id==%s"""%(request.env.http_host,url,action.id),
                      description="""<b>id:</b> %s<br><b>begin:</b> %s<br>%s"""%(action.begin,action.id,action.status_log))]
    rss = rss2.RSS2(title="OpenSVC actions",
                link = """http://%s%s?%s"""%(request.env.http_host,url,request.env.query_string),
                description = desc,
                lastBuildDate = datetime.datetime.now(),
                items = items
    )
    response.headers['Content-Type']='application/rss+xml'
    return rss2.dumps(rss)

def svcactions_csv():
    import gluon.contenttype
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    request.vars['perpage'] = 0
    return str(svcactions()['actions'])

@auth.requires_login()
def services():
    rows = db().select(db.services.ALL)
    return dict(services=rows)

def nodes_csv():
    import gluon.contenttype
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    request.vars['perpage'] = 0
    return str(nodes()['nodes'])

@auth.requires_login()
def nodes():
    o = db.v_nodes.nodename

    columns = dict(
        nodename = dict(
            pos = 1,
            title = T('Node name'),
            display = True,
            size = 10
        ),
        loc_country = dict(
            pos = 2,
            title = T('Country'),
            display = False,
            size = 10
        ),
        loc_zip = dict(
            pos = 3,
            title = T('ZIP'),
            display = False,
            size = 10
        ),
        loc_city = dict(
            pos = 4,
            title = T('City'),
            display = False,
            size = 10
        ),
        loc_addr = dict(
            pos = 5,
            title = T('Address'),
            display = False,
            size = 10
        ),
        loc_building = dict(
            pos = 6,
            title = T('Building'),
            display = True,
            size = 10
        ),
        loc_room = dict(
            pos = 7,
            title = T('Room'),
            display = False,
            size = 10
        ),
        loc_rack = dict(
            pos = 8,
            title = T('Rack'),
            display = True,
            size = 10
        ),
        cpu_freq = dict(
            pos = 9,
            title = T('CPU freq'),
            display = False,
            size = 10
        ),
        mem_bytes = dict(
            pos = 10,
            title = T('Memory'),
            display = True,
            size = 10
        ),
        os_name = dict(
            pos = 11,
            title = T('OS name'),
            display = False,
            size = 10
        ),
        os_kernel = dict(
            pos = 12,
            title = T('OS kernel'),
            display = False,
            size = 10
        ),
        cpu_dies = dict(
            pos = 13,
            title = T('CPU dies'),
            display = True,
            size = 10
        ),
        cpu_model = dict(
            pos = 14,
            title = T('CPU model'),
            display = True,
            size = 10
        ),
        serial = dict(
            pos = 15,
            title = T('Serial'),
            display = True,
            size = 10
        ),
        model = dict(
            pos = 16,
            title = T('Model'),
            display = False,
            size = 10
        ),
        team_responsible = dict(
            pos = 17,
            title = T('Team responsible'),
            display = True,
            size = 10
        ),
        role = dict(
            pos = 18,
            title = T('Role'),
            display = False,
            size = 10
        ),
        environnement = dict(
            pos = 19,
            title = T('Env'),
            display = True,
            size = 10
        ),
        warranty_end = dict(
            pos = 20,
            title = T('Warranty end'),
            display = False,
            size = 10
        ),
        status = dict(
            pos = 21,
            title = T('Status'),
            display = True,
            size = 10
        ),
        type = dict(
            pos = 22,
            title = T('Type'),
            display = False,
            size = 10
        ),
        power_supply_nb = dict(
            pos = 23,
            title = T('Power supply number'),
            display = False,
            size = 10
        ),
        power_cabinet1 = dict(
            pos = 24,
            title = T('Power cabinet #1'),
            display = False,
            size = 10
        ),
        power_cabinet2 = dict(
            pos = 25,
            title = T('Power cabinet #2'),
            display = False,
            size = 10
        ),
        power_protect = dict(
            pos = 26,
            title = T('Power protector'),
            display = False,
            size = 10
        ),
        power_protect_breaker = dict(
            pos = 27,
            title = T('Power protector breaker'),
            display = False,
            size = 10
        ),
        power_breaker1 = dict(
            pos = 28,
            title = T('Power breaker #1'),
            display = False,
            size = 10
        ),
        power_breaker2 = dict(
            pos = 29,
            title = T('Power breaker #2'),
            display = False,
            size = 10
        ),
    )
    def _sort_cols(x, y):
        return cmp(columns[x]['pos'], columns[y]['pos'])
    colkeys = columns.keys()
    colkeys.sort(_sort_cols)

    toggle_db_filters()

    # filtering
    query = (db.v_nodes.id>0)
    for key in columns.keys():
        if key not in request.vars.keys():
            continue
        query &= _where(None, 'v_nodes', request.vars[key], key)

    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')

    query = apply_db_filters(query, 'v_nodes')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select(orderby=o)
    else:
        rows = db(query).select(orderby=o, limitby=(start,end))

    return dict(columns=columns, colkeys=colkeys,
                nodes=rows,
                active_filters=active_db_filters('v_nodes'),
                available_filters=avail_db_filters('v_nodes'),
                nav=nav)

@auth.requires_login()
def node_insert():
    form=SQLFORM(db.nodes)
    if form.accepts(request.vars):
        response.flash = T("edition recorded")
        redirect(URL(r=request, f='nodes'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)

@auth.requires_login()
def node_edit():
    query = (db.v_nodes.id>0)
    query &= _where(None, 'v_nodes', request.vars.node, 'nodename')
    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
    rows = db(query).select()
    if len(rows) != 1:
        response.flash = "vars: %s"%str(request.vars)
        return dict(form=None)
    record = rows[0]
    id = record.id
    record = db(db.v_nodes.id==id).select()[0]
    form=SQLFORM(db.v_nodes, record)
    if form.accepts(request.vars):
        response.flash = T("edition recorded")
        redirect(URL(r=request, f='nodes'))
    elif form.errors:
        response.flash = T("errors in form")

    return dict(form=form)

@auth.requires_login()
def ajax_svc_message_save():
    vars = {
            'msg_svcname': request.vars.svcname,
            'msg_last_editor': ' '.join([session.auth.user.first_name,
                                         session.auth.user.last_name]),
            'msg_last_edit_date':str(datetime.datetime.now()),
            'msg_body':request.vars['msgbody_'+request.vars.svcname],
           }
    v = lambda x: "%(x)s=values(%(x)s)"%dict(x=x)
    r = lambda x: "'%(x)s'"%dict(x=x.replace("'",'"'))
    sql = """insert into svcmessages (%s) values (%s)
             on duplicate key update %s
          """%(
               ','.join(vars.keys()),
               ','.join(map(r, vars.values())),
               ','.join(map(v, vars.keys())),
              )
    db.executesql(sql)

@auth.requires_login()
def ajax_svc_message_load():
    rows = db(db.svcmessages.msg_svcname==request.vars.svcname).select()
    if len(rows) != 1:
        return DIV(
                P(H3("%(svc)s"%dict(svc=request.vars.svcname), _style="text-align:center")),
                P(T("new message"), _style="text-align:center"),
                TEXTAREA(_id='msgbody_'+request.vars.svcname)
               )
    return DIV(
            H3(T("%(s)s messages",dict(s=rows[0].msg_svcname)), _style="text-align:center"),
            P(
              T("last edited on "),
              rows[0].msg_last_edit_date,
              BR(),
              T(" by "),
              rows[0].msg_last_editor,
            ),
            TEXTAREA(
              rows[0].msg_body,
              _id='msgbody_'+rows[0].msg_svcname,
            ),
           )

def svc_status(svc, cellclass="cell2"):
    cl = {}
    for k in ['mon_overallstatus',
              'mon_containerstatus',
              'mon_ipstatus',
              'mon_fsstatus',
              'mon_diskstatus',
              'mon_syncstatus',
              'mon_appstatus']:
        if svc[k] is None:
            cl[k] = 'status_undef'
        else:
            cl[k] = 'status_'+svc[k].replace(" ", "_")

    t = TABLE(
      TR(
        TD(svc.mon_overallstatus,
           _colspan=6,
           _class=cellclass+' status '+cl['mon_overallstatus'],
        ),
      ),
      TR(
        TD("vm", _class=cellclass+' '+cl['mon_containerstatus']),
        TD("ip", _class=cellclass+' '+cl['mon_ipstatus']),
        TD("fs", _class=cellclass+' '+cl['mon_fsstatus']),
        TD("dg", _class=cellclass+' '+cl['mon_diskstatus']),
        TD("sync", _class=cellclass+' '+cl['mon_syncstatus']),
        TD("app", _class=cellclass+' '+cl['mon_appstatus']),
      ),
    )
    return t

@auth.requires_login()
def ajax_svcmon_log_transition():
    svc = request.vars.svcname
    b = str_to_date(request.vars.begin)
    e = str_to_date(request.vars.end)

    """ real transition dates
    """
    tb = b
    te = e

    def get_states_at(d, svc):
        q = (db.svcmon_log.mon_svcname==svc)
        q &= (db.svcmon_log.mon_begin!=db.svcmon_log.mon_end)

        rows = db(q&(db.svcmon_log.mon_end<=d)).select(orderby=~db.svcmon_log.mon_end, limitby=(0,1))
        n = len(rows)
        if n == 0:
            before = DIV(T("No known state before %(date)s", dict(date=d)))
        else:
            before = svc_status(rows[0])
            tb = rows[0].mon_end

        rows = db(q&(db.svcmon_log.mon_begin>=d)).select(orderby=db.svcmon_log.mon_begin, limitby=(0,1))
        n = len(rows)
        if n == 0:
            after = DIV(T("No known state after %(date)s", dict(date=d)))
        else:
            after = svc_status(rows[0])
            te = rows[0].mon_begin

        return (before, after)

    (bb, ab) = get_states_at(b, svc)
    (be, ae) = get_states_at(e, svc)

    header = DIV(
               H3(T("State transitions for %(svc)s", dict(svc=svc))),
             )
    t = TABLE(
          TR(
            TH(b, _colspan=2, _style="text-align:center"),
            TH(e, _colspan=2, _style="text-align:center"),
          ),
          TR(
            TD(bb),
            TD(ab),
            TD(be),
            TD(ae),
          ),
        )
    return DIV(header, t)

@auth.requires_login()
def ajax_svcmon_log_ack_write():
    svc = request.vars.xi
    b = str_to_date(request.vars.bi)
    e = str_to_date(request.vars.ei)
    comment = request.vars.ci

    if request.vars.ac == 'true':
        account = 1
    else:
        account = 0

    svcmon_log_ack_write(svc, b, e, comment, account)

    input_close = INPUT(_value=T('close & refresh table'), _id='close', _type='submit', _onclick="""
                    getElementById("panel_ack").className="panel";
                  """%dict(url=URL(r=request,f='ajax_svcmon_log_ack_write'),
                           svcname=svc)
                  )
    return DIV(T("saved"), P(input_close))

@auth.requires_login()
def svcmon_log_ack_write(svc, b, e, comment="", account=False):
    def db_insert_ack_segment(svc, begin, end, comment, account):
        r = db.svcmon_log_ack.insert(
            mon_svcname = svc,
            mon_begin = begin,
            mon_end = end,
            mon_comment = comment,
            mon_account = account,
            mon_acked_on = datetime.datetime.now(),
            mon_acked_by = ' '.join([session.auth.user.first_name,
                                     session.auth.user.last_name])
        )

    rows = db_select_ack_overlap(svc, b, e)
    l = len(rows)

    if l == 1:
        b = min(rows[0].mon_begin, b)
        e = max(rows[0].mon_end, e)
    elif l > 1:
        b = min(rows[0].mon_begin, b)
        e = max(rows[-1].mon_end, e)

    db_delete_ack_overlap(svc, b, e)
    db_insert_ack_segment(svc, b, e, comment, account)

def db_select_ack_overlap(svc, begin, end):
    b = str(begin)
    e = str(end)
    o = db.svcmon_log_ack.mon_begin
    query = (db.svcmon_log_ack.mon_svcname==svc)
    query &= _where(None, 'svcmon_log_ack', domain_perms(), 'mon_svcname')
    query &= ((db.svcmon_log_ack.mon_end>b)&(db.svcmon_log_ack.mon_end<e))|((db.svcmon_log_ack.mon_begin>b)&(db.svcmon_log_ack.mon_begin<e))
    rows = db(query).select(orderby=o)
    return rows

def db_delete_ack_overlap(svc, begin, end):
    b = str(begin)
    e = str(end)
    query = (db.svcmon_log_ack.mon_svcname==svc)
    query &= _where(None, 'svcmon_log_ack', domain_perms(), 'mon_svcname')
    query &= ((db.svcmon_log_ack.mon_end>b)&(db.svcmon_log_ack.mon_end<=e))|((db.svcmon_log_ack.mon_begin>=b)&(db.svcmon_log_ack.mon_begin<e))
    return db(query).delete()

@auth.requires_login()
def ajax_svcmon_log_ack_load():
    svc = request.vars.svcname
    begin = request.vars.begin
    end = request.vars.end

    """ Load relevant acknowledged segments
    """
    rows = db_select_ack_overlap(svc, begin, end)

    ack_overlap_lines = []
    for row in rows:
        ack_overlap_lines += [TR(
                    TD(row.mon_begin, _id="begin_"+str(row.id)),
                    TD(row.mon_end, _id="end_"+str(row.id)),
                    TD(row.mon_comment, _id="comment_"+str(row.id)),
                    TD(row.mon_acked_by, _id="acked_by_"+str(row.id)),
                    TD(row.mon_acked_on, _id="acked_on_"+str(row.id)),
                  )
                 ]
    ack_overlap_table = TABLE(
                          TR(
                            TH(T("begin")),
                            TH(T("end")),
                            TH(T("comment")),
                            TH(T("acked by")),
                            TH(T("acked on")),
                          ),
                          ack_overlap_lines,
                        )
    xi = INPUT(_value=svc, _id='xi', _type='hidden')
    bi = INPUT(_value=begin, _id='bi')
    ei = INPUT(_value=end, _id='ei')
    ac = INPUT(_id='ac',
               _type='checkbox',
               _onChange='this.value=this.checked',
              )
    ci = TEXTAREA(_value='', _id='ci')
    input_save = INPUT(_value='save', _id='save', _type='button', _onclick="""
               ajax("%(url)s",['xi', 'bi', 'ei', 'ci', 'ac'],"panelbody_ack");
              """%dict(url=URL(r=request,f='ajax_svcmon_log_ack_write'),
                       svcname=svc)
         )
    title = H3(T("Ack unavailability period for %(svc)s", dict(svc=svc)))
    ti = TABLE(
           TR(
             TH(T("begin")),
             TH(T("end")),
           ),
           TR(
             TD(bi),
             TD(ei),
           ),
           TR(
             TH(T("account in availability ratio")),
             TD(ac, _colspan=2),
           ),
           TR(
             TH(T("comment"), _colspan=2),
           ),
           TR(
             TD(ci, _colspan=2),
           ),
           TR(
             TD(input_save, _colspan=2),
           ),
         )
    return DIV(
             title,
             xi,
             ti
           )

@auth.requires_login()
def ajax_res_status():
    svcname = request.vars.svcname
    node = request.vars.node
    return res_status(svcname, node)

def res_status(svcname, node):
    rows = db((db.resmon.svcname==svcname)&(db.resmon.nodename==node)).select(orderby=db.resmon.rid)
    def print_row(row):
        cssclass = 'status_'+row.res_status.replace(" ", "_")
        return (TR(
                 TD(row.rid),
                 TD(row.res_status, _class='%s'%cssclass),
                 TD(row.res_desc),
               ),
               TR(
                 TD(),
                 TD(),
                 TD(PRE(row.res_log)),
               ))
    t = TABLE(
          TR(
            TH('id'),
            TH('status'),
            TH('description'),
          ),
          map(print_row, rows)
    )
    return DIV(
             P(
               H3("%(svc)s@%(node)s"%dict(svc=svcname, node=node),
               _style="text-align:center")
             ),
             t,
           )

@auth.requires_login()
def ajax_action_status():
    id = None
    for k in request.vars:
        if 'spin_' in k:
            id = request.vars[k]
            break

    if id is None:
        return SPAN()

    rows = db(db.SVCactions.id==id).select()

    if len(rows) != 1:
        return SPAN()

    status = rows[0].status
    if status is not None:
        return SPAN(
                 status,
                 _class="status_"+status,
               )
    else:
        return IMG(
                _src=URL(r=request,c='static',f='spinner_16.png'),
                _border=0,
                _title=T("unfinished"),
                _onload="""
                  var spintimer_%(id)s;
                  clearTimeout(spintimer_%(id)s);
                  spintimer=setTimeout(function validate(){ajax('%(url)s',
['spin_%(id)s'], 'spin_span_%(id)s')}, 3000);
                """%dict(
                      url=URL(r=request,f='ajax_action_status'),
                      id=id,
                    )
              )

@auth.requires_login()
def ajax_service():
    rowid = request.vars.rowid
    rows = db(db.v_svcmon.mon_svcname==request.vars.node).select()
    viz = svcmon_viz_img(rows)
    if len(rows) == 0:
        return DIV(
                 T("No service information for %(node)s",
                   dict(node=request.vars.node)),
               )

    s = rows[0]
    t_misc = TABLE(
      TR(
        TD(T('opensvc version'), _style='font-style:italic'),
        TD(s['svc_version'])
      ),
      TR(
        TD(T('unacknowledged errors'), _style='font-style:italic'),
        TD(s['err'])
      ),
      TR(
        TD(T('type'), _style='font-style:italic'),
        TD(s['svc_type'])
      ),
      TR(
        TD(T('application'), _style='font-style:italic'),
        TD(s['svc_app'])
      ),
      TR(
        TD(T('comment'), _style='font-style:italic'),
        TD(s['svc_comment'])
      ),
      TR(
        TD(T('last update'), _style='font-style:italic'),
        TD(s['svc_updated'])
      ),
      TR(
        TD(T('container type'), _style='font-style:italic'),
        TD(s['svc_containertype'])
      ),
      TR(
        TD(T('container name'), _style='font-style:italic'),
        TD(s['svc_vmname'])
      ),
      TR(
        TD(T('responsibles'), _style='font-style:italic'),
        TD(s['responsibles'])
      ),
      TR(
        TD(T('responsibles mail'), _style='font-style:italic'),
        TD(s['mailto'])
      ),
      TR(
        TD(T('primary node'), _style='font-style:italic'),
        TD(s['svc_autostart'])
      ),
      TR(
        TD(T('nodes'), _style='font-style:italic'),
        TD(s['svc_nodes'])
      ),
      TR(
        TD(T('drp node'), _style='font-style:italic'),
        TD(s['svc_drpnode'])
      ),
      TR(
        TD(T('drp nodes'), _style='font-style:italic'),
        TD(s['svc_drpnodes'])
      ),
      TR(
        TD(T('vcpus'), _style='font-style:italic'),
        TD(s['svc_vcpus'])
      ),
      TR(
        TD(T('vmem'), _style='font-style:italic'),
        TD(s['svc_vmem'])
      ),
    )

    def print_status_row(row):
        r = TR(
              TD(row.mon_nodname, _style='font-style:italic'),
              TD(svc_status(row))
            )
        return r
    status = map(print_status_row, rows)
    t_status = TABLE(
                 status,
               )

    def print_rstatus_row(row):
        r = TR(
              TD(
                res_status(row.mon_svcname, row.mon_nodname)
              )
            )
        return r
    rstatus = map(print_rstatus_row, rows)
    t_rstatus = TABLE(
                 rstatus,
               )

    def js(tab, rowid):
        buff = ""
        for i in range(1, 6):
            buff += """getElementById('%(tab)s_%(id)s').style['display']='none';
                       getElementById('li%(tab)s_%(id)s').style['backgroundColor']='#EEE';
                    """%dict(tab='tab'+str(i), id=rowid)
        buff += """getElementById('%(tab)s_%(id)s').style['display']='block';
                   getElementById('li%(tab)s_%(id)s').style['backgroundColor']='orange';
                """%dict(tab=tab, id=rowid)
        return buff


    t = TABLE(
      TR(
        TD(
          UL(
            LI(
              P(
                T("close %(n)s", dict(n=request.vars.node)),
                _class="tab closetab",
                _onclick="""
                    getElementById("tr_id_%(id)s").style['display']='none'
                """%dict(id=rowid),
              ),
            ),
            LI(
              P(
                T("properties"),
                _class="tab",
                _onclick=js('tab1', rowid)
               ),
              _id="litab1_"+str(rowid),
              _style="background-color:orange",
            ),
            LI(P(T("status"), _class="tab", _onclick=js('tab2', rowid)), _id="litab2_"+str(rowid)),
            LI(P(T("resources"), _class="tab", _onclick=js('tab3', rowid)), _id="litab3_"+str(rowid)),
            LI(P(T("env"), _class="tab", _onclick=js('tab4', rowid)), _id="litab4_"+str(rowid)),
            LI(P(T("topology"), _class="tab", _onclick=js('tab5', rowid)), _id="litab5_"+str(rowid)),
            _class="web2py-menu web2py-menu-horizontal",
          ),
          _style="border-bottom:solid 1px orange;padding:1px",
        ),
      ),
      TR(
        TD(
          DIV(
            t_misc,
            _id='tab1_'+str(rowid),
            _class='cloud_shown',
          ),
          DIV(
            t_status,
            _id='tab2_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            t_rstatus,
            _id='tab3_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            envfile(request.vars.node),
            _id='tab4_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=viz),
            _id='tab5_'+str(rowid),
            _class='cloud',
          ),
        ),
      ),
    )
    return t

@auth.requires_login()
def perf_stats_blockdev(node, s, e):
    rows = db.executesql("""
      select dev,
             avg(tps) as avg_tps,
             min(tps) as min_tps,
             max(tps) as max_tps,
             avg(rsecps) as rsecps,
             avg(wsecps) as wsecps,
             avg(avgrq_sz) as avg_avgrq_sz,
             min(avgrq_sz) as min_avgrq_sz,
             max(avgrq_sz) as max_avgrq_sz,
             avg(await) as avg_await,
             min(await) as min_await,
             max(await) as max_await,
             avg(svctm) as avg_svctm,
             min(svctm) as min_svctm,
             max(svctm) as max_svctm,
             avg(pct_util) as avg_pct_util,
             min(pct_util) as min_pct_util,
             max(pct_util) as max_pct_util
      from stats_blockdev
      where date >= "%(s)s" and
            date <= "%(e)s" and
            nodename = "%(node)s"
      group by dev;
    """%dict(node=node, s=s, e=e))

    if len(rows) == 0:
        return SPAN()

    from time import mktime

    def format_x(x):
        return "/6{}" + str(x)

    def format_y(x):
        return "/6{}" + str(x)

    import random
    rand = int(random.random()*1000000)

    """ %util
    """
    data1 = [(row[0],
              row[15],
              row[16],
              row[17],
             ) for row in rows]
    data = sorted(data1, key = lambda x: x[1])

    action1 = URL(r=request,c='static',f='stats_blockdev1_'+str(rand)+'.png')
    path = 'applications'+str(action1)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = category_coord.T(data, 0),
           x_axis = axis.X(label = 'blockdev %util', format=format_x, tic_interval=10),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (0, 100),
           size = (150,len(data)*8),
         )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="avg",
                       line_style=None,
                       width=2,
                       hcol=1,
                       cluster=(1,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot2 = bar_plot.T(label="min",
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       line_style=None,
                       width=2,
                       hcol=2,
                       cluster=(0,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot3 = bar_plot.T(label="max",
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       width=2,
                       hcol=3,
                       cluster=(2,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    ar.add_plot(plot1, plot2, plot3)
    ar.draw(can)
    can.close()

    """ service time
    """
    data1 = [(row[0],
              row[12],
              row[13],
              row[14],
             ) for row in rows]
    data = sorted(data1, key = lambda x: x[1])

    action2 = URL(r=request,c='static',f='stats_blockdev2_'+str(rand)+'.png')
    path = 'applications'+str(action2)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = category_coord.T(data, 0),
           x_axis = axis.X(label = 'blockdev service time (ms)', format=format_x),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (0, None),
           size = (150,len(data)*8),
         )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="avg",
                       line_style=None,
                       width=2,
                       hcol=1,
                       cluster=(1,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot2 = bar_plot.T(label="min",
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       line_style=None,
                       width=2,
                       hcol=2,
                       cluster=(0,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot3 = bar_plot.T(label="max",
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       width=2,
                       hcol=3,
                       cluster=(2,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    ar.add_plot(plot1, plot2, plot3)
    ar.draw(can)
    can.close()

    """ await
    """
    data1 = [(row[0],
              row[9],
              row[10],
              row[11],
             ) for row in rows]
    data = sorted(data1, key = lambda x: x[1])

    action3 = URL(r=request,c='static',f='stats_blockdev3_'+str(rand)+'.png')
    path = 'applications'+str(action3)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = category_coord.T(data, 0),
           x_axis = axis.X(label = 'blockdev wait time (ms)', format=format_x),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (0, None),
           size = (150,len(data)*8),
         )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="avg",
                       line_style=None,
                       width=2,
                       hcol=1,
                       cluster=(1,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot2 = bar_plot.T(label="min",
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       line_style=None,
                       width=2,
                       hcol=2,
                       cluster=(0,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot3 = bar_plot.T(label="max",
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       width=2,
                       hcol=3,
                       cluster=(2,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    ar.add_plot(plot1, plot2, plot3)
    ar.draw(can)
    can.close()

    """ request size
    """
    data1 = [(row[0],
              row[6],
              row[7],
              row[8],
             ) for row in rows]
    data = sorted(data1, key = lambda x: x[1])

    action4 = URL(r=request,c='static',f='stats_blockdev4_'+str(rand)+'.png')
    path = 'applications'+str(action4)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = category_coord.T(data, 0),
           x_axis = axis.X(label = 'blockdev request size (sector)',
                           format=format_x),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (0, None),
           size = (150,len(data)*8),
         )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="avg",
                       line_style=None,
                       width=2,
                       hcol=1,
                       cluster=(1,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot2 = bar_plot.T(label="min",
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       line_style=None,
                       width=2,
                       hcol=2,
                       cluster=(0,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot3 = bar_plot.T(label="max",
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       width=2,
                       hcol=3,
                       cluster=(2,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    ar.add_plot(plot1, plot2, plot3)
    ar.draw(can)
    can.close()

    """ tps
    """
    data1 = [(row[0],
              row[1],
              row[2],
              row[3],
             ) for row in rows]
    data = sorted(data1, key = lambda x: x[1])

    action5 = URL(r=request,c='static',f='stats_blockdev5_'+str(rand)+'.png')
    path = 'applications'+str(action5)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = category_coord.T(data, 0),
           x_axis = axis.X(label = 'blockdev io//s',
                           format=format_x),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (0, None),
           size = (150,len(data)*8),
         )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="avg",
                       line_style=None,
                       width=2,
                       hcol=1,
                       cluster=(1,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot2 = bar_plot.T(label="min",
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       line_style=None,
                       width=2,
                       hcol=2,
                       cluster=(0,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot3 = bar_plot.T(label="max",
                       width=2,
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       hcol=3,
                       cluster=(2,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    ar.add_plot(plot1, plot2, plot3)
    ar.draw(can)
    can.close()

    return DIV(
             IMG(_src=action1),
             IMG(_src=action4),
             IMG(_src=action2),
             IMG(_src=action3),
             IMG(_src=action5),
           )

def tic_interval_from_ts(_min, _max):
    p = _max - _min
    r = []
    intervals = [2419200, 1209600, 604800, 86400, 21600, 7200, 3600]
    for i in intervals:
        if p / i >= 6:
            break
    return range(_min, _max, i)

def tic_interval_from_ord(rows):
    _min = rows[0].day.toordinal()
    _max = rows[-1].day.toordinal()
    p = _max - _min
    r = []
    i = p // 10
    if i == 0:
        i = 1
    return i

def tic_start_ts(rows):
    from time import mktime
    start_date = mktime(rows[0].date.timetuple())
    end_date = mktime(rows[-1].date.timetuple())
    p = end_date - start_date
    if p < 86400:
        """ align start to closest preceding hour
        """
        start_date = ((start_date // 3600) + 1) * 3600
    else:
        """ align start to closest preceding day
        """
        start_date = ((start_date // 86400) + 1) * 86400
    return start_date

@auth.requires_login()
def perf_stats_proc(node, s, e):
    q = db.stats_proc.nodename == node
    q &= db.stats_proc.date > s
    q &= db.stats_proc.date < e
    rows = db(q).select(orderby=db.stats_proc.date)
    if len(rows) == 0:
        return SPAN()

    from time import mktime

    start_date = tic_start_ts(rows)

    def format_x(ts):
        d = datetime.datetime.fromtimestamp(ts+start_date)
        return "/a50/5{}" + d.strftime("%y-%m-%d %H:%M")

    def format_y(x):
        return "/6{}" + str(x)

    import random
    rand = int(random.random()*1000000)


    """ Usage KB
    """
    action1 = URL(r=request,c='static',f='stats_load_'+str(rand)+'.png')
    path = 'applications'+str(action1)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    data = [(mktime(row.date.timetuple())-start_date,
             row.runq_sz,
             row.plist_sz,
             row.ldavg_1,
             row.ldavg_5,
             row.ldavg_15,
            ) for row in rows]

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'load average',
                      format=format_x,
                      tic_interval=tic_interval_from_ts,
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (None, mktime(rows[-1].date.timetuple())-start_date),
         )
    bar_plot.fill_styles.reset()
    plot1 = line_plot.T(label="ldavg_1",
                       ycol=3,
                       line_style=line_style.T(width=2, color=color.gray30),
                       data = data,
                       data_label_format="",
                       )
    plot2 = line_plot.T(label="ldavg_5",
                       ycol=4,
                       line_style=line_style.T(width=2, color=color.gray50),
                       data = data,
                       data_label_format="",
                       )
    plot3 = line_plot.T(label="ldavg_15",
                       ycol=5,
                       line_style=line_style.T(width=2, color=color.gray70),
                       data = data,
                       data_label_format="",
                       )
    plot4 = line_plot.T(label="runq_sz",
                       ycol=1,
                       line_style=line_style.T(width=1, color=color.salmon),
                       data = data,
                       data_label_format="",
                       )
    ar.add_plot(plot1, plot2, plot3, plot4)
    ar.draw(can)
    can.close()


    """ Usage Percent
    """
    rand = int(random.random()*1000000)
    action2 = URL(r=request,c='static',f='stats_proc_'+str(rand)+'.png')
    path = 'applications'+str(action2)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'process list',
                      format=format_x,
                      tic_interval=tic_interval_from_ts,
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (None, mktime(rows[-1].date.timetuple())-start_date),
         )
    bar_plot.fill_styles.reset()
    plot1 = line_plot.T(label="plist_sz",
                       ycol=2,
                       line_style=line_style.T(width=2, color=color.salmon),
                       data = data,
                       data_label_format="",
                       )
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()
    return DIV(
             IMG(_src=action1),
             IMG(_src=action2),
           )

@auth.requires_login()
def perf_stats_swap(node, s, e):
    q = db.stats_swap.nodename == node
    q &= db.stats_swap.date > s
    q &= db.stats_swap.date < e
    rows = db(q).select(orderby=db.stats_swap.date)
    if len(rows) == 0:
        return SPAN()

    from time import mktime

    start_date = tic_start_ts(rows)

    def format_x(ts):
        d = datetime.datetime.fromtimestamp(ts+start_date)
        return "/a50/5{}" + d.strftime("%y-%m-%d %H:%M")

    def format_y(x):
        return "/6{}" + str(x)

    import random
    rand = int(random.random()*1000000)


    """ Usage KB
    """
    action1 = URL(r=request,c='static',f='stats_swap_'+str(rand)+'.png')
    path = 'applications'+str(action1)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    data = [(mktime(row.date.timetuple())-start_date,
             row.kbswpused-row.kbswpcad,
             row.kbswpcad,
             row.kbswpfree,
             row.pct_swpused,
             row.pct_swpcad,
            ) for row in rows]

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'swap usage (KB)',
                      format=format_x,
                      tic_interval=tic_interval_from_ts,
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (None, mktime(rows[-1].date.timetuple())-start_date),
         )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="used",
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       hcol=1,
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=1,
                       direction='vertical')
    plot2 = bar_plot.T(label="used, cached",
                       hcol=2,
                       stack_on=plot1,
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=1,
                       direction='vertical')
    plot3 = bar_plot.T(label="free",
                       hcol=3,
                       stack_on=plot2,
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=1,
                       direction='vertical')
    ar.add_plot(plot1, plot2, plot3)
    ar.draw(can)
    can.close()


    return DIV(
             IMG(_src=action1),
           )

@auth.requires_login()
def perf_stats_block(node, s, e):
    q = db.stats_block.nodename == node
    q &= db.stats_block.date > s
    q &= db.stats_block.date < e
    rows = db(q).select(orderby=db.stats_block.date)
    if len(rows) == 0:
        return SPAN()

    from time import mktime

    start_date = tic_start_ts(rows)

    def format_x(ts):
        d = datetime.datetime.fromtimestamp(ts+start_date)
        return "/a50/5{}" + d.strftime("%y-%m-%d %H:%M")

    def format_y(x):
        return "/6{}" + str(x)

    import random
    rand = int(random.random()*1000000)


    """ TPS
    """
    action1 = URL(r=request,c='static',f='stats_block1_'+str(rand)+'.png')
    path = 'applications'+str(action1)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    data = [(mktime(row.date.timetuple())-start_date,
             row.tps,
             row.rtps,
             row.wtps,
             row.rbps/2,
             row.wbps/2,
            ) for row in rows]

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'io//s',
                      tic_interval=tic_interval_from_ts,
                      format=format_x
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (None, mktime(rows[-1].date.timetuple())-start_date),
         )
    bar_plot.fill_styles.reset()
    plot1 = line_plot.T(label="read",
                       ycol=2,
                       line_style=line_style.T(color=color.thistle3,
                                               width=2),
                       data = data,
                       data_label_format="",
                       )
    plot2 = line_plot.T(label="write",
                       ycol=3,
                       line_style=line_style.T(color=color.salmon,
                                               width=2),
                       data = data,
                       data_label_format="",
                       )
    ar.add_plot(plot1, plot2)
    ar.draw(can)
    can.close()


    """ BPS
    """
    rand = int(random.random()*1000000)
    action2 = URL(r=request,c='static',f='stats_block2_'+str(rand)+'.png')
    path = 'applications'+str(action2)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'KB//s',
                      tic_interval = tic_interval_from_ts,
                      format=format_x
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (None, mktime(rows[-1].date.timetuple())-start_date),
         )
    bar_plot.fill_styles.reset()
    plot1 = line_plot.T(label="read",
                       ycol=4,
                       line_style=line_style.T(color=color.thistle3,
                                               width=2),
                       data = data,
                       data_label_format="",
                       )
    plot2 = line_plot.T(label="write",
                       ycol=5,
                       line_style=line_style.T(color=color.salmon,
                                               width=2),
                       data = data,
                       data_label_format="",
                       )
    ar.add_plot(plot1, plot2)
    ar.draw(can)
    can.close()

    return DIV(
             IMG(_src=action1),
             IMG(_src=action2),
           )

@auth.requires_login()
def perf_stats_mem_u(node, s, e):
    q = db.stats_mem_u.nodename == node
    q &= db.stats_mem_u.date > s
    q &= db.stats_mem_u.date < e
    rows = db(q).select(orderby=db.stats_mem_u.date)
    if len(rows) == 0:
        return SPAN()

    from time import mktime

    start_date = tic_start_ts(rows)

    def format_x(ts):
        d = datetime.datetime.fromtimestamp(ts+start_date)
        return "/a50/5{}" + d.strftime("%y-%m-%d %H:%M")

    def format_y(x):
        return "/6{}" + str(x)

    import random
    rand = int(random.random()*1000000)


    """ Usage KB
    """
    action1 = URL(r=request,c='static',f='stats_mem_u_'+str(rand)+'.png')
    path = 'applications'+str(action1)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    data = [(mktime(row.date.timetuple())-start_date,
             row.kbmemfree,
             row.kbmemused-row.kbbuffers-row.kbcached-row.kbmemsys,
             row.pct_memused,
             row.kbbuffers,
             row.kbcached,
             row.kbcommit,
             row.pct_commit,
             row.kbmemsys,
            ) for row in rows]

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'memory usage (KB)',
                      format=format_x,
                      tic_interval=tic_interval_from_ts,
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (None, mktime(rows[-1].date.timetuple())-start_date)
         )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="free",
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       hcol=1,
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=1,
                       direction='vertical')
    plot2 = bar_plot.T(label="used",
                       hcol=2,
                       stack_on=plot1,
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=1,
                       direction='vertical')
    plot3 = bar_plot.T(label="used, buffer",
                       hcol=4,
                       stack_on=plot2,
                       fill_style=fill_style.black,
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=1,
                       direction='vertical')
    plot4 = bar_plot.T(label="used, cache",
                       hcol=5,
                       stack_on=plot3,
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=1,
                       direction='vertical')
    plot5 = bar_plot.T(label="used, sys",
                       hcol=8,
                       stack_on=plot4,
                       fill_style=fill_style.Plain(bgcolor=color.coral),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=1,
                       direction='vertical')
    plot6 = line_plot.T(label="commit",
                       ycol=6,
                       line_style=line_style.T(color=color.darkkhaki,
                                               width=2),
                       data = data,
                       data_label_format="",
                       )
    ar.add_plot(plot1, plot2, plot3, plot4, plot5, plot6)
    ar.draw(can)
    can.close()


    """ Usage Percent
    """
    rand = int(random.random()*1000000)
    action2 = URL(r=request,c='static',f='stats_mem_u_'+str(rand)+'.png')
    path = 'applications'+str(action2)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'memory usage (%)',
                      tic_interval = tic_interval_from_ts,
                      format=format_x
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (None, mktime(rows[-1].date.timetuple())-start_date)
         )
    bar_plot.fill_styles.reset()
    plot1 = line_plot.T(label="used",
                       ycol=3,
                       line_style=line_style.T(color=color.salmon,
                                               width=2),
                       data = data,
                       data_label_format="",
                       )
    plot2 = line_plot.T(label="commit",
                       ycol=7,
                       line_style=line_style.T(color=color.darkkhaki,
                                               width=2),
                       data = data,
                       data_label_format="",
                       )
    ar.add_plot(plot1, plot2)
    ar.draw(can)
    can.close()
    return DIV(
             IMG(_src=action1),
             IMG(_src=action2),
           )


@auth.requires_login()
def perf_stats_netdev(node, s, e):
    q = db.stats_netdev.nodename == node
    q &= db.stats_netdev.date > s
    q &= db.stats_netdev.date < e
    rows = db(q).select(db.stats_netdev.dev,
                        groupby=db.stats_netdev.dev,
                        orderby=db.stats_netdev.dev,
                       )
    devs = [r.dev for r in rows]

    t = []
    for dev in devs:
        t += perf_stats_netdev_one(node, s, e, dev)
    def format(x):
        return SPAN(x)
    return SPAN(map(format, t))

@auth.requires_login()
def perf_stats_netdev_one(node, s, e, dev):
    q = db.stats_netdev.nodename == node
    q &= db.stats_netdev.date > s
    q &= db.stats_netdev.date < e
    q &= db.stats_netdev.dev == dev
    rows = db(q).select(orderby=db.stats_netdev.date)
    if len(rows) == 0:
        return SPAN()

    from time import mktime

    start_date = tic_start_ts(rows)

    def format_x(ts):
        d = datetime.datetime.fromtimestamp(ts+start_date)
        return "/a50/5{}" + d.strftime("%y-%m-%d %H:%M")

    def format_y(x):
        return "/6{}" + str(x)

    def format2_y(x):
        return "/a50/6{}" + str(x)

    import random
    rand = int(random.random()*1000000)
    action = URL(r=request,c='static',f='stats_netdev_'+str(rand)+'.png')
    path = 'applications'+str(action)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    data = [(mktime(row.date.timetuple())-start_date,
             row.rxpckps,
             row.txpckps,
             row.rxkBps,
             row.txkBps) for row in rows]

    ar = area.T(
           #x_coord = category_coord.T(data, 0),
           x_coord = linear_coord.T(),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'dev '+dev,
                      format=format_x,
                      tic_interval=tic_interval_from_ts,
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (None, mktime(rows[-1].date.timetuple())-start_date)
         )
    bar_plot.fill_styles.reset();
    plot1 = line_plot.T(label="rx kB//s",
                       ycol=3,
                       line_style=line_style.T(color=color.thistle3, width=2),
                       data = data,
                       data_label_format="",
                       )
    plot2 = line_plot.T(label="tx kB//s",
                       ycol=4,
                       line_style=line_style.T(width=2, color=color.salmon),
                       data = data,
                       data_label_format="",
                       )
    ar.add_plot(plot1, plot2)
    ar.draw(can)
    can.close()

    return DIV(IMG(_src=action))

@auth.requires_login()
def perf_stats_netdev_err(node, s, e):
    rows = db.executesql("""
      select dev,
             max(rxerrps) as max_rxerrps,
             max(txerrps) as max_txerrps,
             max(collps) as max_collps,
             max(rxdropps) as max_rxdropps,
             max(txdropps) as max_txdropps
      from stats_netdev_err
      where date >= "%(s)s" and
            date <= "%(e)s" and
            nodename = "%(node)s"
      group by dev;
    """%dict(node=node, s=s, e=e))

    if len(rows) == 0:
        return SPAN()

    from time import mktime

    def format_x(x):
        return "/6{}" + str(x)

    def format_y(x):
        return "/6{}" + str(x)

    import random
    rand = int(random.random()*1000000)

    """ %util
    """
    data1 = [(row[0],
              row[1],
              row[2],
              row[3],
              row[4],
              row[5],
             ) for row in rows]
    data = sorted(data1, key = lambda x: x[1])

    action1 = URL(r=request,c='static',f='stats_netdev_err_'+str(rand)+'.png')
    path = 'applications'+str(action1)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = category_coord.T(data, 0),
           x_axis = axis.X(label = 'net dev errors', format=format_x, tic_interval=10),
           y_axis = axis.Y(label = "", format=format_y),
           size = (150,len(data)*8),
         )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="max rxerr//s",
                       line_style=None,
                       width=2,
                       hcol=1,
                       cluster=(0,5),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot2 = bar_plot.T(label="max txerr//s",
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       line_style=None,
                       width=2,
                       hcol=2,
                       cluster=(1,5),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot3 = bar_plot.T(label="max coll//s",
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       width=2,
                       hcol=3,
                       cluster=(2,5),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot4 = bar_plot.T(label="max rxdrop//s",
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       width=2,
                       hcol=4,
                       cluster=(3,5),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot5 = bar_plot.T(label="max txdrop//s",
                       fill_style=fill_style.Plain(bgcolor=color.darkkhaki),
                       line_style=None,
                       width=2,
                       hcol=5,
                       cluster=(4,5),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    ar.add_plot(plot1, plot2, plot3, plot4, plot5)
    ar.draw(can)
    can.close()

    return DIV(IMG(_src=action1))

@auth.requires_login()
def perf_stats_cpu(node, s, e):
    q = db.stats_cpu.nodename == node
    q &= db.stats_cpu.date > s
    q &= db.stats_cpu.date < e
    rows = db(q).select(db.stats_cpu.cpu,
                        groupby=db.stats_cpu.cpu,
                        orderby=db.stats_cpu.cpu,
                       )
    cpus = [r.cpu for r in rows]

    t = []
    for cpu in cpus:
        t += perf_stats_cpu_one(node, s, e, cpu)
    def format(x):
        return SPAN(x)
    return SPAN(map(format, t))

@auth.requires_login()
def perf_stats_cpu_one(node, s, e, cpu):
    q = db.stats_cpu.nodename == node
    q &= db.stats_cpu.date > s
    q &= db.stats_cpu.date < e
    q &= db.stats_cpu.cpu == cpu
    rows = db(q).select(orderby=db.stats_cpu.date)
    if len(rows) == 0:
        return SPAN()

    from time import mktime

    start_date = tic_start_ts(rows)

    def format_x(ts):
        d = datetime.datetime.fromtimestamp(ts+start_date)
        return "/a50/5{}" + d.strftime("%y-%m-%d %H:%M")

    def format_y(x):
        return "/6{}" + str(x)

    def format2_y(x):
        return "/a50/6{}" + str(x)

    import random
    rand = int(random.random()*1000000)
    action = URL(r=request,c='static',f='stats_cpu_'+str(rand)+'.png')
    path = 'applications'+str(action)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    data = [(mktime(row.date.timetuple())-start_date,
             row.usr,
             row.nice,
             row.sys,
             row.iowait,
             row.steal,
             row.irq,
             row.soft,
             row.guest,
             row.idle) for row in rows]

    ar = area.T(
           #x_coord = category_coord.T(data, 0),
           x_coord = linear_coord.T(),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'cpu '+cpu,
                      format=format_x,
                      tic_interval=tic_interval_from_ts,
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (None, mktime(rows[-1].date.timetuple())-start_date)
         )
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="usr",
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       hcol=1,
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=1,
                       direction='vertical')
    plot2 = bar_plot.T(label="nice",
                       hcol=2,
                       stack_on=plot1,
                       fill_style=fill_style.Plain(bgcolor=color.darkkhaki),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=1,
                       direction='vertical')
    plot3 = bar_plot.T(label="sys",
                       hcol=3,
                       stack_on=plot2,
                       fill_style=fill_style.black,
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=1,
                       direction='vertical')
    plot4 = bar_plot.T(label="iowait",
                       hcol=4,
                       stack_on=plot3,
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=1,
                       direction='vertical')
    plot5 = bar_plot.T(label="steal",
                       hcol=5,
                       stack_on=plot4,
                       fill_style=fill_style.Plain(bgcolor=color.coral),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=1,
                       direction='vertical')
    plot6 = bar_plot.T(label="irq",
                       hcol=6,
                       stack_on=plot5,
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=1,
                       direction='vertical')
    plot7 = bar_plot.T(label="soft",
                       hcol=7,
                       stack_on=plot6,
                       fill_style=fill_style.Plain(bgcolor=color.navajowhite2),
                       line_style=None,
                       data = data,
                       width=1,
                       data_label_format="",
                       direction='vertical')
    plot8 = bar_plot.T(label="guest",
                       hcol=8,
                       stack_on=plot7,
                       fill_style=fill_style.Plain(bgcolor=color.plum3),
                       line_style=None,
                       data = data,
                       width=1,
                       data_label_format="",
                       direction='vertical')
    ar.add_plot(plot1, plot2, plot3, plot4, plot5, plot6, plot7, plot8)
    ar.draw(can)
    can.close()

    return DIV(IMG(_src=action))

@auth.requires_login()
def perf_stats_mem_u_trend_data(node, s, e, p):
    sql = """select cast(avg(kbmemfree+kbcached) as unsigned),
                    cast(std(kbmemfree+kbcached) as unsigned)
             from stats_mem_u
             where nodename="%(node)s"
               and date>date_sub("%(s)s", interval %(p)s)
               and date<date_sub("%(e)s", interval %(p)s)
          """%dict(s=s,e=e,node=node,p=p)
    rows = db.executesql(sql)
    if len(rows) != 1:
        return [(p, 0, 0)]
    r = rows[0]
    if r[0] is None or r[1] is None:
        return [(p, 0, 0)]
    return [(p, r[0], r[1])]

def period_to_range(period):
    if period <= datetime.timedelta(days=1):
        return ["6 day", "5 day", "4 day", "3 day",
                "2 day", "1 day", "0 day"]
    elif period <= datetime.timedelta(days=7):
        return ["3 week", "2 week", "1 week", "0 week"]
    elif period <= datetime.timedelta(days=30):
        return ["2 month", "1 month", "0 month"]
    else:
        return []

@auth.requires_login()
def perf_stats_mem_u_trend(node, s, e):
    data = []
    start = str_to_date(s)
    end = str_to_date(e)
    period = end - start
    for p in period_to_range(period):
        data += perf_stats_mem_u_trend_data(node, s, e, p)

    if len(data) == 0:
        return SPAN()

    def format_x(x):
        return "/a50/5{}" + str(x)

    def format_y(x):
        return "/6{}" + str(x)

    import random
    rand = int(random.random()*1000000)
    action = URL(r=request,c='static',f='stats_mem_u_trend_'+str(rand)+'.png')
    path = 'applications'+str(action)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = category_coord.T(data, 0),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'period over period available memory (KB)',
                      format=format_x,
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           #y_range = (0, None),
         )
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="avg avail mem (KB)",
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       hcol=1,
                       line_style=None,
                       data = data,
                       data_label_format="",
                       #width=1,
                       direction='vertical')
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()

    return IMG(_src=action)

@auth.requires_login()
def perf_stats_cpu_trend_data(node, s, e, p):
    sql = """select 100-avg(idle),std(idle)
             from stats_cpu
             where cpu="all"
               and nodename="%(node)s"
               and date>date_sub("%(s)s", interval %(p)s)
               and date<date_sub("%(e)s", interval %(p)s)
          """%dict(s=s,e=e,node=node,p=p)
    rows = db.executesql(sql)
    if len(rows) != 1:
        return [(p, 0, 0)]
    r = rows[0]
    if r[0] is None or r[1] is None:
        return [(p, 0, 0)]
    return [(p, r[0], r[1])]

@auth.requires_login()
def perf_stats_cpu_trend(node, s, e):
    data = []
    start = str_to_date(s)
    end = str_to_date(e)
    period = end - start

    for p in period_to_range(period):
        data += perf_stats_cpu_trend_data(node, s, e, p)

    if len(data) == 0:
        return SPAN()

    def format_x(x):
        return "/a50/5{}" + str(x)

    def format_y(x):
        return "/6{}" + str(x)

    import random
    rand = int(random.random()*1000000)
    action = URL(r=request,c='static',f='stats_cpu_trend_'+str(rand)+'.png')
    path = 'applications'+str(action)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = category_coord.T(data, 0),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'period over period cpu usage (%)',
                      format=format_x,
                    ),
           y_axis = axis.Y(label = "", format=format_y, tic_interval=10),
           y_range = (0, 100),
           y_grid_interval = 10,
         )
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="avg cpu usage (%)",
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       hcol=1,
                       line_style=None,
                       data = data,
                       data_label_format="",
                       #width=1,
                       error_bar = error_bar.bar2, error_minus_col=2,
                       direction='vertical')
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()

    return IMG(_src=action)

@auth.requires_login()
def ajax_perf_stats():
     node = None
     begin = None
     end = None
     for k in request.vars:
         if 'node_' in k:
             node = request.vars[k]
         elif 'begin_' in k:
             begin = request.vars[k]
         elif 'end_' in k:
             end = request.vars[k]
     if node is None or begin is None or end is None:
         return SPAN()
     return DIV(
              perf_stats_trends(node, begin, end),
              perf_stats_cpu(node, begin, end),
              perf_stats_mem_u(node, begin, end),
              perf_stats_swap(node, begin, end),
              perf_stats_proc(node, begin, end),
              perf_stats_netdev(node, begin, end),
              perf_stats_netdev_err(node, begin, end),
              perf_stats_block(node, begin, end),
              perf_stats_blockdev(node, begin, end),
              _style="""background-color:white;
                        padding:10px;
                        -moz-border-radius:8px;
                        -webkit-border-radius:8px;
                     """
            )

@auth.requires_login()
def perf_stats_trends(node, begin, end):
    return DIV(
              perf_stats_cpu_trend(node, begin, end),
              perf_stats_mem_u_trend(node, begin, end),
           )

@auth.requires_login()
def perf_stats(node, rowid):
    now = datetime.datetime.now()
    s = now - datetime.timedelta(days=0,
                                 hours=now.hour,
                                 minutes=now.minute,
                                 microseconds=now.microsecond)
    e = s + datetime.timedelta(days=1)

    t = DIV(
          SPAN(
            INPUT(
              _type='hidden',
              _value=node,
              _id='node_'+rowid,
            ),
            INPUT(
              _value=s.strftime("%Y-%m-%d %H:%M"),
              _id='begin_'+rowid,
            ),
            INPUT(
              _value=e.strftime("%Y-%m-%d %H:%M"),
              _id='end_'+rowid,
            ),
            INPUT(
              _value='gen',
              _type='button',
              _onClick="""getElementById('perf_%(id)s').innerHTML='%(spinner)s';
                          ajax("%(url)s",
                              ['node_%(id)s',
                               'begin_%(id)s',
                               'end_%(id)s'
                              ],"perf_%(id)s");
                      """%dict(url=URL(r=request,f='ajax_perf_stats'),
                               id=rowid,
                               spinner=IMG(_src=URL(r=request,c='static',f='spinner_16.png')),
                              )
            )
          ),
          DIV(
            _id='perf_'+rowid
          ),
        )
    return t

@auth.requires_login()
def ajax_node():
    rowid = request.vars.rowid
    nodes = db(db.v_nodes.nodename==request.vars.node).select()
    if len(nodes) == 0:
        return DIV(
                 T("No asset information for %(node)s",
                   dict(node=request.vars.node)
                 ),
                 P(
                   A(
                     T("insert"),
                     _href=URL(r=request, f='node_insert'),
                   ),
                   _style='text-align:center',
                 ),
               )

    node = nodes[0]
    loc = TABLE(
      TR(TD(T('country'), _style='font-style:italic'), TD(node['loc_country'])),
      TR(TD(T('city'), _style='font-style:italic'), TD(node['loc_city'])),
      TR(TD(T('zip'), _style='font-style:italic'), TD(node['loc_zip'])),
      TR(TD(T('address'), _style='font-style:italic'), TD(node['loc_addr'])),
      TR(TD(T('building'), _style='font-style:italic'), TD(node['loc_building'])),
      TR(TD(T('floor'), _style='font-style:italic'), TD(node['loc_floor'])),
      TR(TD(T('room'), _style='font-style:italic'), TD(node['loc_room'])),
      TR(TD(T('rack'), _style='font-style:italic'), TD(node['loc_rack'])),
    )
    power = TABLE(
      TR(TD(T('nb power supply'), _style='font-style:italic'), TD(node['power_supply_nb'])),
      TR(TD(T('power cabinet #1'), _style='font-style:italic'), TD(node['power_cabinet1'])),
      TR(TD(T('power cabinet #2'), _style='font-style:italic'), TD(node['power_cabinet2'])),
      TR(TD(T('power protector'), _style='font-style:italic'), TD(node['power_protect'])),
      TR(TD(T('power protector breaker'), _style='font-style:italic'), TD(node['power_protect_breaker'])),
      TR(TD(T('power breaker #1'), _style='font-style:italic'), TD(node['power_breaker1'])),
      TR(TD(T('power breaker #2'), _style='font-style:italic'), TD(node['power_breaker1'])),
    )
    server = TABLE(
      TR(TD(T('model'), _style='font-style:italic'), TD(node['model'])),
      TR(TD(T('type'), _style='font-style:italic'), TD(node['type'])),
      TR(TD(T('serial'), _style='font-style:italic'), TD(node['serial'])),
      TR(TD(T('warranty end'), _style='font-style:italic'), TD(node['warranty_end'])),
      TR(TD(T('team responsible'), _style='font-style:italic'), TD(node['team_responsible'])),
      TR(TD(T('status'), _style='font-style:italic'), TD(node['status'])),
      TR(TD(T('role'), _style='font-style:italic'), TD(node['role'])),
      TR(TD(T('env'), _style='font-style:italic'), TD(node['environnement'])),
    )
    cpu = TABLE(
      TR(TD(T('cpu frequency'), _style='font-style:italic'), TD(node['cpu_freq'])),
      TR(TD(T('cpu cores'), _style='font-style:italic'), TD(node['cpu_cores'])),
      TR(TD(T('cpu dies'), _style='font-style:italic'), TD(node['cpu_dies'])),
      TR(TD(T('cpu vendor'), _style='font-style:italic'), TD(node['cpu_vendor'])),
      TR(TD(T('cpu model'), _style='font-style:italic'), TD(node['cpu_model'])),
    )
    mem = TABLE(
      TR(TD(T('memory banks'), _style='font-style:italic'), TD(node['mem_banks'])),
      TR(TD(T('memory slots'), _style='font-style:italic'), TD(node['mem_slots'])),
      TR(TD(T('memory total'), _style='font-style:italic'), TD(node['mem_bytes'])),
    )
    os = TABLE(
      TR(TD(T('os name'), _style='font-style:italic'), TD(node['os_name'])),
      TR(TD(T('os vendor'), _style='font-style:italic'), TD(node['os_vendor'])),
      TR(TD(T('os release'), _style='font-style:italic'), TD(node['os_release'])),
      TR(TD(T('os update'), _style='font-style:italic'), TD(node['os_update'])),
      TR(TD(T('os segment'), _style='font-style:italic'), TD(node['os_segment'])),
      TR(TD(T('os kernel'), _style='font-style:italic'), TD(node['os_kernel'])),
      TR(TD(T('os arch'), _style='font-style:italic'), TD(node['os_arch'])),
    )
    t = TABLE(
      TR(TD(H2(request.vars.node), _colspan=2, _style='text-align:center')),
      TR(TD(loc), TD(power)),
      TR(TD(server), TD(os)),
      TR(TD(cpu), TD(mem)),
      TR(TD(A(T("edit"), _href=URL(r=request, f='node_edit', vars={'node': request.vars.node})), _colspan=2, _style='text-align:center')),
    )

    def js(tab, rowid):
        buff = ""
        for i in range(1, 8):
            buff += """getElementById('%(tab)s_%(id)s').style['display']='none';
                       getElementById('li%(tab)s_%(id)s').style['backgroundColor']='#EEE';
                    """%dict(tab='tab'+str(i), id=rowid)
        buff += """getElementById('%(tab)s_%(id)s').style['display']='block';
                   getElementById('li%(tab)s_%(id)s').style['backgroundColor']='orange';
                """%dict(tab=tab, id=rowid)
        return buff

    t = TABLE(
      TR(
        TD(
          UL(
            LI(
              P(
                T("close %(n)s", dict(n=request.vars.node)),
                _class="tab closetab",
                _onclick="""
                    getElementById("tr_id_%(id)s").style['display']='none'
                """%dict(id=rowid),
              ),
            ),
            LI(
              P(
                T("server"),
                _class="tab",
                _onclick=js('tab1', rowid),
              ),
              _id="litab1_"+str(rowid),
              _style="background-color:orange",
            ),
            LI(P(T("os"), _class="tab", _onclick=js('tab2', rowid)), _id="litab2_"+str(rowid)),
            LI(P(T("mem"), _class="tab", _onclick=js('tab3', rowid)), _id="litab3_"+str(rowid)),
            LI(P(T("cpu"), _class="tab", _onclick=js('tab4', rowid)), _id="litab4_"+str(rowid)),
            LI(P(T("location"), _class="tab", _onclick=js('tab5', rowid)), _id="litab5_"+str(rowid)),
            LI(P(T("power"), _class="tab", _onclick=js('tab6', rowid)), _id="litab6_"+str(rowid)),
            LI(P(T("stats"), _class="tab", _onclick=js('tab7', rowid)), _id="litab7_"+str(rowid)),
            _class="web2py-menu web2py-menu-horizontal",
          ),
          _style="border-bottom:solid 1px orange;padding:1px",
        ),
      ),
      TR(
        TD(
          DIV(
            server,
            _id='tab1_'+str(rowid),
            _class='cloud_shown',
          ),
          DIV(
            os,
            _id='tab2_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            mem,
            _id='tab3_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            cpu,
            _id='tab4_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            loc,
            _id='tab5_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            power,
            _id='tab6_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            perf_stats(request.vars.node, rowid),
            _id='tab7_'+str(rowid),
            _class='cloud',
          ),
        ),
      ),
    )
    return t

class ex(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

@auth.requires_membership('Manager')
def _drplan_clone_project(request):
    prj_rows = db(db.drpprojects.drp_project==request.vars.cloneproject).select(db.drpprojects.drp_project_id)
    if len(prj_rows) != 0:
        response.flash = T("project '%(prj)s' already exists", dict(prj=request.vars.cloneproject))
        return
    db.drpprojects.insert(drp_project=request.vars.cloneproject)
    q = db.drpprojects.drp_project==request.vars.cloneproject
    dst_prj = db(q).select(db.drpprojects.drp_project_id)[0]
    q = db.drpservices.drp_project_id==request.vars.prjlist
    src_prj_rows = db(q).select(db.drpservices.drp_project_id,
                                db.drpservices.drp_svcname,
                                db.drpservices.drp_wave,)
    for row in src_prj_rows:
        db.drpservices.insert(drp_svcname=row.drp_svcname,
                              drp_wave=row.drp_wave,
                              drp_project_id=dst_prj.drp_project_id)
    q = db.drpprojects.drp_project_id==request.vars.prjlist
    src_prj = db(q).select(db.drpprojects.drp_project)[0]
    response.flash = T("project '%(dst)s' cloned from '%(src)s'. %(num)s services DR configurations ported to the new project", dict(dst=request.vars.cloneproject, src=src_prj.drp_project, num=str(len(src_prj_rows))))
    request.vars.prjlist = str(dst_prj.drp_project_id)
    del request.vars.cloneproject

@auth.requires_membership('Manager')
def _drplan_add_project(request):
    prj_rows = db(db.drpprojects.drp_project==request.vars.addproject).select(db.drpprojects.drp_project_id)
    if len(prj_rows) != 0:
        response.flash = T("project '%(prj)s' already exists", dict(prj=request.vars.addproject))
        return
    db.drpprojects.insert(drp_project=request.vars.addproject)
    response.flash = T("project '%(prj)s' created", dict(prj=request.vars.addproject))
    q = db.drpprojects.drp_project==request.vars.addproject
    dst_prj = db(q).select(db.drpprojects.drp_project_id)[0]
    request.vars.prjlist = str(dst_prj.drp_project_id)
    del request.vars.addproject

@auth.requires_membership('Manager')
def _drplan_del_project(request):
    db(db.drpprojects.drp_project_id == request.vars.prjlist).delete()
    num_deleted = db(db.drpservices.drp_project_id == request.vars.prjlist).delete()
    response.flash = T("project deleted. %(num)d services DR configurations dropped.", dict(num=num_deleted))

@auth.requires_membership('Manager')
def _drplan_set_wave(request):
    svcs = ([])
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        svcs += ([key[6:]])
    for svc in svcs:
        if request.vars.setwave == "del":
                query = (db.drpservices.drp_svcname == svc)&(db.drpservices.drp_project_id == request.vars.prjlist)
                db(query).delete()
        else:
            try:
                db.drpservices.insert(drp_svcname=svc, drp_wave=request.vars.setwave, drp_project_id=request.vars.prjlist)
            except:
                query = (db.drpservices.drp_svcname == svc)&(db.drpservices.drp_project_id == request.vars.prjlist)
                db(query).update(drp_wave=request.vars.setwave)

@auth.requires_login()
def drplan():
    if request.vars.cloneproject is not None and request.vars.cloneproject != '':
        _drplan_clone_project(request)
    elif request.vars.addproject is not None and request.vars.addproject != '':
        _drplan_add_project(request)
    elif request.vars.delproject is not None and request.vars.delproject != '':
        _drplan_del_project(request)
    elif request.vars.setwave is not None and request.vars.setwave != '':
        _drplan_set_wave(request)

    toggle_db_filters()

    query = (db.v_svcmon.svc_drpnode!=None)&(db.v_svcmon.svc_drpnode!='')
    query &= _where(None, 'v_svcmon', request.vars.svc_name, 'svc_name')
    query &= _where(None, 'v_svcmon', request.vars.svc_app, 'svc_app')
    query &= _where(None, 'v_svcmon', request.vars.responsibles, 'responsibles')
    query &= _where(None, 'v_svcmon', request.vars.svc_type, 'svc_type')
    query &= _where(None, 'v_svcmon', request.vars.svc_drptype, 'svc_drptype')
    query &= _where(None, 'v_svcmon', request.vars.svc_autostart, 'svc_autostart')
    query &= _where(None, 'v_svcmon', request.vars.svc_nodes, 'svc_nodes')
    query &= _where(None, 'v_svcmon', request.vars.svc_drpnode, 'svc_drpnode')
    query &= _where(None, 'v_svcmon', request.vars.svc_drpnodes, 'svc_drpnodes')
    query &= _where(None, 'drpservices', request.vars.svc_wave, 'drp_wave', tableid=db.v_svcmon.id)
    query &= _where(None, 'v_svcmon', domain_perms(), 'svc_nodes')

    query = apply_db_filters(query, 'v_svcmon')

    g = db.v_svcmon.svc_name
    j = (db.v_svcmon.svc_name==db.drpservices.drp_svcname)&(db.drpservices.drp_project_id==request.vars.prjlist)

    (start, end, nav) = _pagination(request, query, groupby=g)
    if start == 0 and end == 0:
        svc_rows = db(query).select(db.v_svcmon.ALL,
                                    db.drpservices.drp_wave,
                                    db.drpservices.drp_project_id,
                                    left=db.drpservices.on(j),
                                    groupby=g)
    else:
        svc_rows = db(query).select(db.v_svcmon.ALL,
                                    db.drpservices.drp_wave,
                                    db.drpservices.drp_project_id,
                                    left=db.drpservices.on(j),
                                    groupby=g,
                                    limitby=(start,end))

    prj_rows = db().select(db.drpprojects.drp_project_id, db.drpprojects.drp_project)
    return dict(services=svc_rows,
                projects=prj_rows,
                active_filters=active_db_filters('v_svcmon'),
                available_filters=avail_db_filters('v_svcmon'),
                nav=nav)

def drplan_csv():
    import gluon.contenttype
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    request.vars['perpage'] = 0
    return str(drplan()['apps'])

def _drplan_scripts_header(phase):
    l = ["""#!/bin/sh"""]
    l += ["""if [ "`id -u`" != "0" ] ; then echo excute this script as root ; exit 1 ; fi"""]
    l += ["""echo Confirm excution of the '%s' disaster recovery phase"""%phase]
    l += ["""echo Type 'GO' to confirm"""]
    l += ["""read confirm"""]
    l += ["""if [ "$confirm" != "GO" ] ; then echo "aborted" ; exit 0 ; fi"""]
    l += ["""rm -f ~root/authorized_keys"""]
    l += ["""cat - <<EOF >/tmp/ssh_config_drp || exit 1"""]
    l += ['StrictHostKeyChecking=no']
    l += ['ForwardX11=no']
    l += ['PasswordAuthentication=no']
    l += ['ConnectTimeout=10']
    l += ['EOF']
    l += ['']
    return l

def _scripts(rows, title, action, nodecol=None, service=False):
    ssh = '/usr/bin/ssh -F /tmp/ssh_config_drp'
    cmd = '/service/bin/svcmgr'
    lines = _drplan_scripts_header(title)
    for row in rows:
        _cmd = ' '.join([ssh, row.services[nodecol], '--'])
        if service:
            _cmd += """ %s --service %s %s"""%(cmd, row.services.svc_name, action)
        else:
            _cmd += """ %s %s"""%(cmd, action)
        lines += ["""echo %s"""%_cmd]
        lines += [_cmd+' >/dev/null 2>&1 &']
    lines += ['']
    sh = '\n'.join(lines)
    nodes_nb = len(rows)
    return (sh, nodes_nb)

@auth.requires_login()
def drplan_scripts():
    q_drpnode_is_set = (db.services.svc_drpnode!=None)
    q_drpnode_is_set &= (db.services.svc_drpnode!='')
    q_autostart_is_set = (db.services.svc_autostart!=None)
    q_autostart_is_set &= (db.services.svc_autostart!='')
    q_wave_is_set = (db.drpservices.drp_wave!=None)&(db.drpservices.drp_wave!='')
    q_cur_project = (db.drpservices.drp_project_id==request.vars.prjlist)
    p = {}

    """stop/start DEV
    """
    query = q_drpnode_is_set & q_wave_is_set & q_cur_project
    dev_rows = db(query).select(db.services.ALL, db.drpservices.drp_wave, db.drpservices.drp_project_id, left=db.drpservices.on(db.services.svc_name==db.drpservices.drp_svcname),groupby=db.services.svc_drpnode)
    (sh, node_nb) = _scripts(dev_rows, 'STOP DEV', 'stop', 'svc_drpnode')
    p['stopdev'] =  dict(action='stop', phase='DEV', sh=sh, node_nb=node_nb, shname='00_stop_dev.sh')
    (sh, node_nb) = _scripts(dev_rows, 'START DEV', 'startdev', 'svc_drpnode')
    p['startdev'] =  dict(action='start', phase='DEV', sh=sh, node_nb=node_nb, shname='15_start_dev.sh')

    """stop/start PRD
    """
    query = q_autostart_is_set & q_drpnode_is_set & q_wave_is_set & q_cur_project
    prd_rows = db(query).select(db.services.ALL, db.drpservices.drp_wave, db.drpservices.drp_project_id, left=db.drpservices.on(db.services.svc_name==db.drpservices.drp_svcname),groupby=db.services.svc_autostart)
    (sh, node_nb) = _scripts(prd_rows, 'STOP PRD', 'stop', 'svc_autostart')
    p['stopprd'] =  dict(action='stop', phase='PRD', sh=sh, node_nb=node_nb, shname='01_stop_prd.sh')

    wquery = query & (db.drpservices.drp_wave==0)
    prd_rows = db(wquery).select(db.services.ALL, db.drpservices.drp_wave, db.drpservices.drp_project_id, left=db.drpservices.on((db.services.svc_name==db.drpservices.drp_svcname)&(db.drpservices.drp_project_id==request.vars.prjlist)),groupby=db.services.svc_name,orderby=(db.services.svc_autostart))
    (sh, node_nb) = _scripts(prd_rows, 'START PRD WAVE 0', 'start', 'svc_autostart')
    p['startprd0'] =  dict(action='start', phase='PRD WAVE 0', sh=sh, node_nb=node_nb, shname='11_start_prd0.sh')

    wquery = query & (db.drpservices.drp_wave==1)
    prd_rows = db(wquery).select(db.services.ALL, db.drpservices.drp_wave, db.drpservices.drp_project_id, left=db.drpservices.on((db.services.svc_name==db.drpservices.drp_svcname)&(db.drpservices.drp_project_id==request.vars.prjlist)),groupby=db.services.svc_name,orderby=(db.services.svc_autostart))
    (sh, node_nb) = _scripts(prd_rows, 'START PRD WAVE 1', 'start', 'svc_autostart')
    p['startprd1'] =  dict(action='start', phase='PRD WAVE 1', sh=sh, node_nb=node_nb, shname='12_start_prd1.sh')

    wquery = query & (db.drpservices.drp_wave==2)
    prd_rows = db(wquery).select(db.services.ALL, db.drpservices.drp_wave, db.drpservices.drp_project_id, left=db.drpservices.on((db.services.svc_name==db.drpservices.drp_svcname)&(db.drpservices.drp_project_id==request.vars.prjlist)),groupby=db.services.svc_name,orderby=(db.services.svc_autostart))
    (sh, node_nb) = _scripts(prd_rows, 'START PRD WAVE 2', 'start', 'svc_autostart')
    p['startprd2'] =  dict(action='start', phase='PRD WAVE 2', sh=sh, node_nb=node_nb, shname='13_start_prd2.sh')

    wquery = query & (db.drpservices.drp_wave==3)
    prd_rows = db(wquery).select(db.services.ALL, db.drpservices.drp_wave, db.drpservices.drp_project_id, left=db.drpservices.on((db.services.svc_name==db.drpservices.drp_svcname)&(db.drpservices.drp_project_id==request.vars.prjlist)),groupby=db.services.svc_name,orderby=(db.services.svc_autostart))
    (sh, node_nb) = _scripts(prd_rows, 'START PRD WAVE 3', 'start', 'svc_autostart')
    p['startprd3'] =  dict(action='start', phase='PRD WAVE 3', sh=sh, node_nb=node_nb, shname='14_start_prd3.sh')

    """stop/start DR
    """
    query = q_drpnode_is_set & q_wave_is_set & q_cur_project & q_drpnode_is_set
    dr_rows = db(query).select(db.services.ALL, db.drpservices.drp_wave, db.drpservices.drp_project_id, left=db.drpservices.on(db.services.svc_name==db.drpservices.drp_svcname),groupby=db.services.svc_drpnode)
    (sh, node_nb) = _scripts(dr_rows, 'STOP DR', 'stop', 'svc_drpnode')
    p['stopdr'] =  dict(action='stop', phase='DR', sh=sh, node_nb=node_nb, shname='10_stop_dr.sh')

    wquery = query & (db.drpservices.drp_wave==0)
    dr_rows = db(wquery).select(db.services.ALL, db.drpservices.drp_wave, db.drpservices.drp_project_id, left=db.drpservices.on((db.services.svc_name==db.drpservices.drp_svcname)&(db.drpservices.drp_project_id==request.vars.prjlist)),groupby=db.services.svc_name,orderby=(db.services.svc_drpnode))
    (sh, node_nb) = _scripts(dr_rows, 'START DR WAVE 0', 'svc_drpnode', 'start', service=True)
    p['startdr0'] =  dict(action='start', phase='DR WAVE 0', sh=sh, node_nb=node_nb, shname='02_start_dr0.sh')

    wquery = query & (db.drpservices.drp_wave==1)
    dr_rows = db(wquery).select(db.services.ALL, db.drpservices.drp_wave, db.drpservices.drp_project_id, left=db.drpservices.on((db.services.svc_name==db.drpservices.drp_svcname)&(db.drpservices.drp_project_id==request.vars.prjlist)),groupby=db.services.svc_name,orderby=(db.services.svc_drpnode))
    (sh, node_nb) = _scripts(dr_rows, 'START DR WAVE 1', 'start', 'svc_drpnode', service=True)
    p['startdr1'] =  dict(action='start', phase='DR WAVE 1', sh=sh, node_nb=node_nb, shname='03_start_dr1.sh')

    wquery = query & (db.drpservices.drp_wave==2)
    dr_rows = db(wquery).select(db.services.ALL, db.drpservices.drp_wave, db.drpservices.drp_project_id, left=db.drpservices.on((db.services.svc_name==db.drpservices.drp_svcname)&(db.drpservices.drp_project_id==request.vars.prjlist)),groupby=db.services.svc_name,orderby=(db.services.svc_drpnode))
    (sh, node_nb) = _scripts(dr_rows, 'START DR WAVE 2', 'start', 'svc_drpnode', service=True)
    p['startdr2'] =  dict(action='start', phase='DR WAVE 2', sh=sh, node_nb=node_nb, shname='04_start_dr2.sh')

    wquery = query & (db.drpservices.drp_wave==3)
    dr_rows = db(wquery).select(db.services.ALL, db.drpservices.drp_wave, db.drpservices.drp_project_id, left=db.drpservices.on((db.services.svc_name==db.drpservices.drp_svcname)&(db.drpservices.drp_project_id==request.vars.prjlist)),groupby=db.services.svc_name,orderby=(db.services.svc_drpnode))
    (sh, node_nb) = _scripts(dr_rows, 'START DR WAVE 3', 'start', 'svc_drpnode', service=True)
    p['startdr3'] =  dict(action='start', phase='DR WAVE 3', sh=sh, node_nb=node_nb, shname='05_start_dr3.sh')

    return dict(p=p)

def _drplan_script_write(fpath, buff):
    import os
    f = open(fpath, 'w')
    f.write(buff)
    f.close()
    os.chmod(fpath, 0755)
    return fpath

def drplan_scripts_archive():
    import os
    import tarfile
    import tempfile
    import gluon.contenttype
    r = drplan_scripts()
    p = r['p']
    dir = tempfile.mkdtemp()
    olddir = os.getcwd()
    os.chdir(dir)
    tarpath = "dr_scripts.tar"
    tar = tarfile.open(tarpath, "w")
    for key in p.keys():
        _drplan_script_write(p[key]['shname'], p[key]['sh'])
        tar.add(p[key]['shname'])
    tar.close()
    response.headers['Content-Type']=gluon.contenttype.contenttype('.tar')
    f = open(tarpath, 'r')
    buff = f.read()
    f.close()
    for key in p.keys():
        os.unlink(p[key]['shname'])
    os.unlink(tarpath)
    os.chdir(olddir)
    os.rmdir(dir)
    return buff

@auth.requires_login()
def stats():
    d = {}
    d.update(stats_global())
    d.update(stats_disks_per_svc())
    d.update(stats_last_day_avg_cpu())
    d.update(stats_last_day_avg_mem())
    return d

def format_x(ordinal):
    d = datetime.date.fromordinal(int(ordinal))
    return "/a50/6{}" + d.strftime("%y-%m-%d")

def format_y(x):
    return "/6{}" + str(x)

def format2_y(x):
    return "/a50/6{}" + str(x)

@auth.requires_login()
def stats_global():
    from time import mktime
    rows = db(db.stat_day.id>0).select(orderby=db.stat_day.day)
    if len(rows) == 0:
        return dict()

    """ actions
    """
    action = str(URL(r=request,c='static',f='stat_action.png'))
    path = 'applications'+action
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    data = [(row.day.toordinal(), row.nb_action_ok, row.nb_action_warn, row.nb_action_err) for row in rows]
    ti = tic_interval_from_ord(rows)

    ar = area.T(x_coord = category_coord.T(data, 0),
                y_coord = linear_coord.T(),
                x_axis = axis.X(label="", format=format_x,
                                tic_interval=ti),
                y_axis = axis.Y(label="", format=format_y))
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="ok",
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       line_style=None,
                       width = 2,
                       data = data,
                       data_label_format="",
                       direction='vertical')
    plot2 = bar_plot.T(label="warn",
                       hcol=2,
                       stack_on=plot1,
                       fill_style=fill_style.Plain(bgcolor=color.darkkhaki),
                       line_style=None,
                       width = 2,
                       data = data,
                       data_label_format="",
                       direction='vertical')
    plot3 = bar_plot.T(label="err",
                       hcol=3,
                       stack_on=plot2,
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       width = 2,
                       data = data,
                       data_label_format="",
                       direction='vertical')
    ar.add_plot(plot1, plot2, plot3)
    ar.draw(can)
    can.close()

    """ actions (errs only)
    """
    action = str(URL(r=request,c='static',f='stat_action_err.png'))
    path = 'applications'+action
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    data = [(row.day.toordinal(), row.nb_action_err) for row in rows]
    ar = area.T(x_coord = category_coord.T(data, 0),
                y_coord = linear_coord.T(),
                x_axis = axis.X(label = "", format=format_x,
                                tic_interval=ti),
                y_axis = axis.Y(label = "", format=format_y))
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="err",
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       width = 2,
                       data = data,
                       data_label_format="",
                       direction='vertical')
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()

    """ services (drp ready)
    """
    action = str(URL(r=request,c='static',f='stat_service_type.png'))
    path = 'applications'+action
    can = canvas.init(path)

    data = [(row.day.toordinal(), row.nb_svc_prd, row.nb_svc-row.nb_svc_prd) for row in rows]
    ar = area.T(x_coord = category_coord.T(data, 0),
                y_coord = linear_coord.T(),
                x_axis = axis.X(label = "", format=format_x,
                                tic_interval=ti),
                y_axis = axis.Y(label = "", format=format_y))
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="prd svc",
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       width = 2,
                       data = data,
                       data_label_format="",
                       direction='vertical')
    plot2 = bar_plot.T(label="other svc", hcol=2, stack_on = plot1,
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       width = 2,
                       data = data,
                       data_label_format="",
                       direction='vertical')
    ar.add_plot(plot1, plot2)
    ar.draw(can)
    can.close()

    """ services (drp ready)
    """
    action = str(URL(r=request,c='static',f='stat_service.png'))
    path = 'applications'+action
    can = canvas.init(path)

    data = [(row.day.toordinal(), row.nb_svc_with_drp, row.nb_svc_prd-row.nb_svc_with_drp) for row in rows]
    ar = area.T(x_coord = category_coord.T(data, 0),
                y_coord = linear_coord.T(),
                x_axis = axis.X(label = "", format=format_x,
                                tic_interval=ti),
                y_axis = axis.Y(label = "", format=format_y))
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="prd svc with drp",
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       data = data,
                       width = 2,
                       data_label_format="",
                       direction='vertical')
    plot2 = bar_plot.T(label="prd svc without drp", hcol=2, stack_on = plot1,
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       width = 2,
                       data = data,
                       data_label_format="",
                       direction='vertical')
    ar.add_plot(plot1, plot2)
    ar.draw(can)
    can.close()

    """ services (clustered)
    """
    action = str(URL(r=request,c='static',f='stat_service_clustered.png'))
    path = 'applications'+action
    can = canvas.init(path)

    data = [(row.day.toordinal(), row.nb_svc_cluster, row.nb_svc-row.nb_svc_cluster) for row in rows]
    ar = area.T(x_coord = category_coord.T(data, 0),
                y_coord = linear_coord.T(),
                x_axis = axis.X(label = "", format=format_x,
                                tic_interval=ti),
                y_axis = axis.Y(label = "", format=format_y))
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="clustered svc",
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       width = 2,
                       data = data,
                       data_label_format="",
                       direction='vertical')
    plot2 = bar_plot.T(label="not clustered svc", hcol=2, stack_on = plot1,
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       width = 2,
                       data = data,
                       data_label_format="",
                       direction='vertical')
    ar.add_plot(plot1, plot2)
    ar.draw(can)
    can.close()

    """ nodes
    """
    action = str(URL(r=request,c='static',f='stat_node.png'))
    path = 'applications'+action
    can = canvas.init(path)

    data = [(row.day.toordinal(), row.nb_nodes_prd, row.nb_nodes-row.nb_nodes_prd) for row in rows]
    ar = area.T(x_coord = category_coord.T(data, 0),
                y_coord = linear_coord.T(),
                x_axis = axis.X(label = "", format=format_x,
                                tic_interval=ti),
                y_axis = axis.Y(label = "", format=format_y))
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="prd nodes",
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       width = 2,
                       data = data,
                       data_label_format="",
                       direction='vertical')
    plot2 = bar_plot.T(label="other nodes", hcol=2, stack_on = plot1,
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       width = 2,
                       data = data,
                       data_label_format="",
                       direction='vertical')
    ar.add_plot(plot1, plot2)
    ar.draw(can)
    can.close()

    """ apps
    """
    action = str(URL(r=request,c='static',f='stat_app.png'))
    path = 'applications'+action
    can = canvas.init(path)

    data = [(row.day.toordinal(), row.nb_apps) for row in rows]
    ar = area.T(x_coord = category_coord.T(data, 0),
                y_coord = linear_coord.T(),
                x_axis = axis.X(label = "", format=format_x,
                                tic_interval=ti),
                y_axis = axis.Y(label = "", format=format_y))
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="apps",
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       width = 2,
                       data = data,
                       data_label_format="",
                       direction='vertical')
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()

    """ accounts
    """
    action = str(URL(r=request,c='static',f='stat_accounts.png'))
    path = 'applications'+action
    can = canvas.init(path)

    data = [(row.day.toordinal(), row.nb_accounts) for row in rows]
    ar = area.T(x_coord = category_coord.T(data, 0),
                y_coord = linear_coord.T(),
                x_axis = axis.X(label="", format=format_x,
                                tic_interval=ti),
                y_axis = axis.Y(label="", format=format_y))
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="accounts",
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       width = 2,
                       data = data,
                       data_label_format="",
                       direction='vertical')
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()

    """ disks
    """
    action = str(URL(r=request,c='static',f='stat_disk.png'))
    path = 'applications'+action
    can = canvas.init(path)

    data = [(row.day.toordinal(), row.disk_size) for row in rows]
    ar = area.T(x_coord = category_coord.T(data, 0),
                y_coord = linear_coord.T(),
                x_axis = axis.X(label = "", format=format_x,
                                tic_interval=ti),
                y_axis = axis.Y(label = "", format=format_y))
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="disk size (GB)",
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       width = 2,
                       data = data,
                       data_label_format="",
                       direction='vertical')
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()
    return dict()

@auth.requires_login()
def stats_disks_per_svc():
    """ disks per svc
    """
    dom = _domain_perms()
    if dom is None:
        dom = '%'
    sql = """select svcname, group_concat(disk_size order by day separator ',')
             from stat_day_svc
             where svcname like '%(dom)s'
             group by svcname
          """%dict(dom=dom)
    rows = db.executesql(sql)

    if len(rows) == 0:
        return dict(stat_disk_svc=None)

    import random
    rand = int(random.random()*1000000)
    img = 'stat_disk_svc_'+str(rand)+'.png'
    action = str(URL(r=request,c='static',f=img))
    path = 'applications'+action
    can = canvas.init(path)

    def compute_size(s):
        if s is None or len(s) == 0:
            return 0
        return int(s.split(',')[-1])

    data1 = [(row[0], compute_size(row[1])) for row in rows]
    data = sorted(data1, key = lambda x: x[1])[-15:]

    ar = area.T(x_coord = linear_coord.T(),
                y_coord = category_coord.T(data, 0),
                y_axis = axis.Y(label = "", format="/6{}%s"),
                x_axis = axis.X(label = "", format=format2_y)
               )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="disk size (GB)",
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       width = 2,
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()
    return dict(stat_disk_svc=img)

@auth.requires_login()
def stats_last_day_avg_cpu():
    """ last day avg cpu usage per node
    """
    dom = _domain_perms()
    now = datetime.datetime.now()
    end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
    begin = end - datetime.timedelta(days=1)
    sql = """select nodename,100-avg(idle) as avg,std(idle) as std
             from stats_cpu
             where cpu='all'
               and date>'%(begin)s'
               and date<'%(end)s'
               and nodename like '%(dom)s'
             group by nodename
             order by avg"""%dict(begin=str(begin),end=str(end),dom=dom)
    rows = db.executesql(sql)

    if len(rows) == 0:
        return dict(stat_cpu_avg_day=None)

    import random
    rand = int(random.random()*1000000)
    img = 'stat_cpu_avg_day_'+str(rand)+'.png'
    action = str(URL(r=request,c='static',f=img))
    path = 'applications'+action
    can = canvas.init(path)

    data1 = [(row[0], row[1]) for row in rows]
    if len(data1) > 31:
        data = data1[0:15] + [("...", 0)] + data1[-15:]
    else:
        data = data1
    ar = area.T(x_coord = linear_coord.T(),
                size = (150,len(data)*6),
                y_coord = category_coord.T(data, 0),
                y_axis = axis.Y(label = "", format="/6{}%s"),
                x_axis = axis.X(label = "", format=format2_y)
               )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="cpu usage (%)",
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       width = 2,
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()
    return dict(stat_cpu_avg_day=img)

@auth.requires_login()
def stats_last_day_avg_mem():
    """ available mem
    """
    dom = _domain_perms()
    sql = """select * from (
               select nodename,(kbmemfree+kbcached) as avail
               from stats_mem_u
               where nodename like '%(dom)s'
               group by nodename
               order by nodename, date
             ) tmp
             order by avail desc;
          """%dict(dom=dom)
    rows = db.executesql(sql)

    if len(rows) == 0:
        return dict(stat_mem_avail=None)

    import random
    rand = int(random.random()*1000000)
    img = 'stat_mem_avail_'+str(rand)+'.png'
    action = str(URL(r=request,c='static',f=img))
    path = 'applications'+action
    can = canvas.init(path)

    data1 = [(row[0], row[1]) for row in rows]
    if len(data1) > 31:
        data = data1[0:15] + [("...", 0)] + data1[-15:]
    else:
        data = data1
    ar = area.T(x_coord = linear_coord.T(),
                size = (150,len(data)*6),
                y_coord = category_coord.T(data, 0),
                y_axis = axis.Y(label = "", format="/6{}%s"),
                x_axis = axis.X(label = "", format=format2_y)
               )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="available memory (KB)",
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       width = 2,
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()
    return dict(stat_mem_avail=img)


@service.xmlrpc
def delete_services(hostid=None):
    if hostid is None:
        return 0
    db(db.services.svc_hostid==hostid).delete()
    db.commit()
    return 0

@service.xmlrpc
def delete_service_list(hostid=None, svcnames=[]):
    if hostid is None or len(svcnames) == 0:
        return 0
    for svcname in svcnames:
        q = (db.services.svc_name==svcname)
        q &= (db.services.svc_hostid==hostid)
        db(q).delete()
        db.commit()
    return 0

@service.xmlrpc
def begin_action(vars, vals):
    sql="""insert delayed into SVCactions (%s) values (%s)""" % (','.join(vars), ','.join(vals))
    db.executesql(sql)
    db.commit()
    return 0

@service.xmlrpc
def res_action(vars, vals):
    upd = []
    for a, b in zip(vars, vals):
        upd.append("%s=%s" % (a, b))
    sql="""insert delayed into SVCactions (%s) values (%s)""" % (','.join(vars), ','.join(vals))
    db.executesql(sql)
    db.commit()
    return 0

@service.xmlrpc
def end_action(vars, vals):
    upd = []
    h = {}
    for a, b in zip(vars, vals):
        h[a] = b
        if a not in ['hostname', 'svcname', 'begin', 'action', 'hostid']:
            upd.append("%s=%s" % (a, b))
    sql="""update SVCactions set %s where hostname=%s and svcname=%s and begin=%s and action=%s""" %\
        (','.join(upd), h['hostname'], h['svcname'], h['begin'], h['action'])
    #raise Exception(sql)
    db.executesql(sql)
    db.commit()
    return 0

def value_wrap(a):
    return "%(a)s=values(%(a)s)"%dict(a=a)

def quote_wrap(x):
    if isinstance(x, (int, long, float, complex)):
        return x
    elif isinstance(x, str) and len(x) == 0:
        return "''"
    elif isinstance(x, str) and x[0] == "'" and x[-1] == "'":
        return x
    elif isinstance(x, str) and x[0] == '"' and x[-1] == '"':
        return x
    else:
        return "'%s'"%str(x).replace("'", '"')

def insert_multiline(table, vars, valsl):
    value_wrap = lambda a: "%(a)s=values(%(a)s)"%dict(a=a)
    line_wrap = lambda x: "(%(x)s)"%dict(x=','.join(map(quote_wrap, x)))
    upd = map(value_wrap, vars)
    lines = map(line_wrap, valsl)
    sql="""insert delayed into %s (%s) values %s on duplicate key update %s""" % (table, ','.join(vars), ','.join(lines), ','.join(upd))
    db.executesql(sql)
    db.commit()

def generic_insert(table, vars, vals):
    if len(vals) == 0:
        return
    elif isinstance(vals[0], list):
        insert_multiline(table, vars, vals)
    else:
        insert_multiline(table, vars, [vals])

@service.xmlrpc
def update_service(vars, vals):
    if 'svc_hostid' not in vars:
        return
    if 'updated' not in vars:
        vars += ['updated']
        vals += [datetime.datetime.now()]
    generic_insert('services', vars, vals)

@service.xmlrpc
def res_action_batch(vars, vals):
    generic_insert('SVCactions', vars, vals)

@service.xmlrpc
def resmon_update(vars, vals):
    generic_insert('resmon', vars, vals)

@service.xmlrpc
def register_disk(vars, vals):
    generic_insert('svcdisks', vars, vals)

@service.xmlrpc
def register_sync(vars, vals):
    pass

@service.xmlrpc
def register_ip(vars, vals):
    pass

@service.xmlrpc
def register_fs(vars, vals):
    pass

@service.xmlrpc
def insert_stats_cpu(vars, vals):
    generic_insert('stats_cpu', vars, vals)

@service.xmlrpc
def insert_stats_mem_u(vars, vals):
    generic_insert('stats_mem_u', vars, vals)

@service.xmlrpc
def insert_stats_proc(vars, vals):
    generic_insert('stats_proc', vars, vals)

@service.xmlrpc
def insert_stats_swap(vars, vals):
    generic_insert('stats_swap', vars, vals)

@service.xmlrpc
def insert_stats_block(vars, vals):
    generic_insert('stats_block', vars, vals)

@service.xmlrpc
def insert_stats_blockdev(vars, vals):
    generic_insert('stats_blockdev', vars, vals)

@service.xmlrpc
def insert_stats_netdev(vars, vals):
    generic_insert('stats_netdev', vars, vals)

@service.xmlrpc
def insert_stats_netdev_err(vars, vals):
    generic_insert('stats_netdev_err', vars, vals)

@service.xmlrpc
def insert_pkg(vars, vals):
    generic_insert('packages', vars, vals)

@service.xmlrpc
def delete_pkg(node):
    if node is None or node == '':
        return 0
    db(db.packages.pkg_nodename==node).delete()
    db.commit()

@service.xmlrpc
def delete_syncs(svcname):
    pass

@service.xmlrpc
def delete_ips(svcname, node):
    pass

@service.xmlrpc
def delete_fss(svcname):
    pass

@service.xmlrpc
def delete_disks(svcname, node):
    if svcname is None or svcname == '':
        return 0
    db((db.svcdisks.disk_svcname==svcname)&(db.svcdisks.disk_nodename==node)).delete()
    db.commit()

@service.xmlrpc
def svcmon_update(vars, vals):
    generic_insert('svcmon', vars, vals)
    h = {}
    for a,b in zip(vars, vals):
        h[a] = b
    tmo = datetime.datetime.strptime(h['mon_updated'].split('.')[0], "%Y-%m-%d %H:%M:%S") - datetime.timedelta(minutes=18)
    query = db.svcmon_log.mon_svcname==h['mon_svcname']
    query &= db.svcmon_log.mon_nodname==h['mon_nodname']
    last = db(query).select(orderby=~db.svcmon_log.id, limitby=(0,1))
    if len(last) == 0:
        _vars = ['mon_begin',
                 'mon_end',
                 'mon_svcname',
                 'mon_nodname',
                 'mon_overallstatus',
                 'mon_ipstatus',
                 'mon_fsstatus',
                 'mon_diskstatus',
                 'mon_containerstatus',
                 'mon_appstatus',
                 'mon_syncstatus']
        _vals = [h['mon_updated'],
                 h['mon_updated'],
                 h['mon_svcname'],
                 h['mon_nodname'],
                 h['mon_overallstatus'],
                 h['mon_ipstatus'],
                 h['mon_fsstatus'],
                 h['mon_diskstatus'],
                 h['mon_containerstatus'],
                 h['mon_appstatus'],
                 h['mon_syncstatus']]
        generic_insert('svcmon_log', _vars, _vals)
    elif last[0].mon_end < tmo:
        _vars = ['mon_begin',
                 'mon_end',
                 'mon_svcname',
                 'mon_nodname',
                 'mon_overallstatus',
                 'mon_ipstatus',
                 'mon_fsstatus',
                 'mon_diskstatus',
                 'mon_containerstatus',
                 'mon_appstatus',
                 'mon_syncstatus']
        _vals = [last[0].mon_end,
                 h['mon_updated'],
                 h['mon_svcname'],
                 h['mon_nodname'],
                 "undef",
                 "undef",
                 "undef",
                 "undef",
                 "undef",
                 "undef",
                 "undef"]
        generic_insert('svcmon_log', _vars, _vals)
        _vars = ['mon_begin',
                 'mon_end',
                 'mon_svcname',
                 'mon_nodname',
                 'mon_overallstatus',
                 'mon_ipstatus',
                 'mon_fsstatus',
                 'mon_diskstatus',
                 'mon_containerstatus',
                 'mon_appstatus',
                 'mon_syncstatus']
        _vals = [h['mon_updated'],
                 h['mon_updated'],
                 h['mon_svcname'],
                 h['mon_nodname'],
                 h['mon_overallstatus'],
                 h['mon_ipstatus'],
                 h['mon_fsstatus'],
                 h['mon_diskstatus'],
                 h['mon_containerstatus'],
                 h['mon_appstatus'],
                 h['mon_syncstatus']]
        generic_insert('svcmon_log', _vars, _vals)
    elif h['mon_overallstatus'] != last[0].mon_overallstatus or \
         h['mon_ipstatus'] != last[0].mon_ipstatus or \
         h['mon_fsstatus'] != last[0].mon_fsstatus or \
         h['mon_diskstatus'] != last[0].mon_diskstatus or \
         h['mon_containerstatus'] != last[0].mon_containerstatus or \
         h['mon_appstatus'] != last[0].mon_appstatus or \
         h['mon_syncstatus'] != last[0].mon_syncstatus:
        _vars = ['mon_begin',
                 'mon_end',
                 'mon_svcname',
                 'mon_nodname',
                 'mon_overallstatus',
                 'mon_ipstatus',
                 'mon_fsstatus',
                 'mon_diskstatus',
                 'mon_containerstatus',
                 'mon_appstatus',
                 'mon_syncstatus']
        _vals = [h['mon_updated'],
                 h['mon_updated'],
                 h['mon_svcname'],
                 h['mon_nodname'],
                 h['mon_overallstatus'],
                 h['mon_ipstatus'],
                 h['mon_fsstatus'],
                 h['mon_diskstatus'],
                 h['mon_containerstatus'],
                 h['mon_appstatus'],
                 h['mon_syncstatus']]
        generic_insert('svcmon_log', _vars, _vals)
        db(db.svcmon_log.id==last[0].id).update(mon_end=h['mon_updated'])
    else:
        db(db.svcmon_log.id==last[0].id).update(mon_end=h['mon_updated'])

