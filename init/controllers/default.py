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
                   user=user_name())
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

    query = db.v_svcmon.mon_frozen==1
    query &= _where(None, 'v_svcmon', domain_perms(), 'mon_nodname')
    query = apply_db_filters(query, 'v_svcmon')
    frozen = db(query).select(db.v_svcmon.mon_svcname, db.v_svcmon.mon_nodname,
                              orderby=db.v_svcmon.mon_svcname)

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

    query = db.v_nodes.warranty_end < now + datetime.timedelta(days=30)
    query &= db.v_nodes.warranty_end != "0000-00-00 00:00:00"
    query &= db.v_nodes.warranty_end is not None
    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
    query = apply_db_filters(query, 'v_nodes')
    warrantyend = db(query).select(db.v_nodes.nodename,
                                    db.v_nodes.warranty_end,
                                    orderby=db.v_nodes.warranty_end
                                   )

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
        query &= (~db.v_nodes.model.like("%virtual%"))
        query &= (~db.v_nodes.model.like("%virtuel%"))
        query &= (~db.v_nodes.model.like("%cluster%"))
        query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
        query = apply_db_filters(query, 'v_nodes')
        rows = db(query).select(db.obsolescence.obs_name, groupby=db.obsolescence.obs_name)
        obswarnmiss = len(rows)

        query = (db.obsolescence.obs_alert_date==None)|(db.obsolescence.obs_alert_date=="0000-00-00")
        query &= (db.v_nodes.os_concat==db.obsolescence.obs_name)|(db.v_nodes.model==db.obsolescence.obs_name)
        query &= (~db.v_nodes.model.like("%virtual%"))
        query &= (~db.v_nodes.model.like("%virtuel%"))
        query &= (~db.v_nodes.model.like("%cluster%"))
        query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
        query = apply_db_filters(query, 'v_nodes')
        rows = db(query).select(db.obsolescence.obs_name, groupby=db.obsolescence.obs_name)
        obsalertmiss = len(rows)
    else:
        obswarnmiss = 0
        obsalertmiss = 0

    pkgdiff = {}
    clusters = {}
    query = _where(None, 'v_svc_group_status', domain_perms(), 'svcname')
    query &= db.v_svc_group_status.svcname==db.v_svcmon.mon_svcname
    query = apply_db_filters(query, 'v_svcmon')
    rows = db(query).select(db.v_svc_group_status.nodes, distinct=True)
    for row in rows:
        nodes = row.nodes.split(',')
        s = set(nodes)
        if s in clusters.values():
            continue
        clusters[row.nodes] = set(nodes)
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

    q = db.v_stats_netdev_err_avg_last_day.avgrxerrps > 0
    q |= db.v_stats_netdev_err_avg_last_day.avgtxerrps > 0
    q |= db.v_stats_netdev_err_avg_last_day.avgcollps > 0
    q |= db.v_stats_netdev_err_avg_last_day.avgrxdropps > 0
    q |= db.v_stats_netdev_err_avg_last_day.avgtxdropps > 0
    query = _where(None, 'v_stats_netdev_err_avg_last_day', domain_perms(), 'nodename')
    query &= db.v_stats_netdev_err_avg_last_day.nodename==db.v_nodes.nodename
    query = apply_db_filters(query, 'v_nodes')
    query &= q
    netdeverrs = db(query).select()

    q = db.v_checks.chk_value < db.v_checks.chk_low
    q |= db.v_checks.chk_value > db.v_checks.chk_high
    query = _where(None, 'v_checks', domain_perms(), 'chk_nodename')
    query &= q
    query &= db.v_checks.chk_nodename==db.v_nodes.nodename
    query = apply_db_filters(query, 'v_nodes')
    checks = db(query).select()

    return dict(svcnotupdated=svcnotupdated,
                frozen=frozen,
                nodeswithoutasset=nodeswithoutasset,
                lastchanges=lastchanges,
                svcwitherrors=svcwitherrors,
                svcnotonprimary=svcnotonprimary,
                appwithoutresp=appwithoutresp,
                warrantyend=warrantyend,
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
                netdeverrs=netdeverrs,
                checks=checks,
               )

def alert_format_body(msg="", app=None, svcname=None, node=None, action=None,
                      begin=None, end=None, svctype=None, pid=None):
    def header_field(title=None, value=None, fmt=None):
        if value is None:
            return None
        if fmt is None:
            fmt = value
        return (B(title),fmt)

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

    header = []
    header.append(header_field("application", app))
    header.append(header_field("service name", svcname, A(svcname, _href=URL_WITH_HOST(r=request, f='svcmon', vars={'svcname':svcname}))))
    header.append(header_field("service type", svctype))
    header.append(header_field("node name", node, A(node, _href=URL_WITH_HOST(r=request, f='svcmon', vars={'nodename':node}))))
    header.append(header_field("action", action))
    header.append(header_field("begin", begin, str(begin)))
    header.append(header_field("end", end, str(end)))
    header.append(header_field("pid", pid, A(pid, _href=URL_WITH_HOST(r=request, f='svcactions', vars={'pid':pid, 'hostname':node, 'perpage':0}))))
    header = [TR(TD(h[0], _width="40%"), TD(h[1])) for h in header if h is not None]

    out = DIV(
      TABLE(
        SPAN(header),
        TR(TD(msg, _colspan=2)),
      ),
      _style="width:400"
    )
    return out

@auth.requires_login()
def alerts():
    columns = dict(
        id = dict(
            pos = 1,
            title = T('Alert Id'),
            img = '',
            size = 3
        ),
        sent_at = dict(
            pos = 4,
            title = T('Sent at'),
            img = '',
            size = 10
        ),
        sent_to = dict(
            pos = 5,
            title = T('Assigned to'),
            img = '',
            size = 7
        ),
        subject = dict(
            pos = 6,
            title = T('Subject'),
            img = '',
            size = 30
        ),
        body = dict(
            pos = 7,
            title = T('Description'),
            img = '',
            size = 30
        ),
    )
    def _sort_cols(x, y):
        return cmp(columns[x]['pos'], columns[y]['pos'])
    colkeys = columns.keys()
    colkeys.sort(_sort_cols)

    query = _where(None, 'alerts', request.vars.id, 'id')
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
def ajax_pkgdiff():
    nodes = set(request.vars.node.split(','))
    nodes -= set([""])
    n = len(nodes)

    if n == 0:
         return DIV(T("No nodes selected"))

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

@auth.requires_login()
def svcmon():
    service_action()

    d1 = v_svcmon_columns()
    d2 = v_nodes_columns()
    for k in d2:
        d2[k]['pos'] += 50
        d2[k]['display'] = False

    del(d2['nodename'])
    columns = d1.copy()
    columns.update(d2)

    def _sort_cols(x, y):
        return cmp(columns[x]['pos'], columns[y]['pos'])
    colkeys = columns.keys()
    colkeys.sort(_sort_cols)
    __update_columns(columns, 'svcmon')

    o = db.v_svcmon.mon_svcname
    o |= ~db.v_svcmon.mon_overallstatus
    o |= ~db.v_svcmon.mon_nodtype
    o |= db.v_svcmon.mon_nodname

    toggle_db_filters()

    query = _where(None, 'v_svcmon', domain_perms(), 'mon_nodname')
    for key in columns.keys():
        if key not in request.vars.keys():
            continue
        query &= _where(None, 'v_svcmon', request.vars[key], key)

    query &= _where(None, 'v_svcmon', request.vars.svc_app, 'svc_app')
    query &= _where(None, 'v_svcmon', request.vars.responsibles, 'responsibles')
    query &= _where(None, 'v_svcmon', request.vars.svc_autostart, 'svc_autostart')
    query &= _where(None, 'v_svcmon', request.vars.svc_containertype, 'svc_containertype')
    query &= _where(None, 'v_svcmon', request.vars.svc_vcpus, 'svc_vcpus')
    query &= _where(None, 'v_svcmon', request.vars.svc_vmem, 'svc_vmem')

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

@auth.requires_login()
def packages():
    d1 = dict(
        pkg_nodename = dict(
            pos = 1,
            title = T('Nodename'),
            display = True,
            nestedin = 'packages',
            img = 'node16',
            size = 10
        ),
        pkg_name = dict(
            pos = 2,
            title = T('Package'),
            display = True,
            nestedin = 'packages',
            img = 'pkg16',
            size = 10
        ),
        pkg_version = dict(
            pos = 3,
            title = T('Version'),
            display = True,
            nestedin = 'packages',
            img = 'pkg16',
            size = 4
        ),
        pkg_arch = dict(
            pos = 4,
            title = T('Arch'),
            display = True,
            nestedin = 'packages',
            img = 'pkg16',
            size = 10
        ),
        pkg_updated = dict(
            pos = 5,
            title = T('Updated'),
            display = True,
            nestedin = 'packages',
            img = 'pkg16',
            size = 6
        ),
    )

    d2 = v_nodes_columns()
    for k in d2:
        d2[k]['pos'] += 10
        d2[k]['display'] = False
        d2[k]['nestedin'] = 'v_nodes'

    del(d2['nodename'])
    columns = d1.copy()
    columns.update(d2)

    def _sort_cols(x, y):
        return cmp(columns[x]['pos'], columns[y]['pos'])

    colkeys = columns.keys()
    colkeys.sort(_sort_cols)
    __update_columns(columns, 'packages')

    o = db.packages.pkg_nodename
    o |= db.packages.pkg_name
    o |= db.packages.pkg_arch

    toggle_db_filters()

    # filtering
    query = db.packages.id>0
    query &= db.packages.pkg_nodename==db.v_nodes.nodename
    for key in d1.keys():
        if key not in request.vars.keys():
            continue
        query &= _where(None, 'packages', request.vars[key], key)
    for key in d2.keys():
        if key not in request.vars.keys():
            continue
        query &= _where(None, 'v_nodes', request.vars[key], key)

    query &= _where(None, 'packages', domain_perms(), 'pkg_nodename')

    query = apply_db_filters(query, 'v_nodes')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select(orderby=o)
    else:
        rows = db(query).select(limitby=(start,end), orderby=o)

    return dict(columns=columns, colkeys=colkeys,
                packages=rows,
                nav=nav,
                active_filters=active_db_filters('v_nodes'),
                available_filters=avail_db_filters('v_nodes'),
               )

@auth.requires_login()
def packages_csv():
    import gluon.contenttype
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    request.vars['perpage'] = 0
    return str(packages()['packages'])

@auth.requires_login()
def patches():
    d1 = dict(
        patch_nodename = dict(
            pos = 1,
            title = T('Nodename'),
            display = True,
            nestedin = 'patches',
            img = 'node16',
            size = 10
        ),
        patch_num = dict(
            pos = 2,
            title = T('Patchnum'),
            display = True,
            nestedin = 'patches',
            img = 'pkg16',
            size = 10
        ),
        patch_rev = dict(
            pos = 3,
            title = T('Patchrev'),
            display = True,
            nestedin = 'patches',
            img = 'pkg16',
            size = 4
        ),
        patch_updated = dict(
            pos = 4,
            title = T('Updated'),
            display = True,
            nestedin = 'patches',
            img = 'pkg16',
            size = 6
        ),
    )

    d2 = v_nodes_columns()
    for k in d2:
        d2[k]['pos'] += 10
        d2[k]['display'] = False
        d2[k]['nestedin'] = 'v_nodes'

    del(d2['nodename'])
    columns = d1.copy()
    columns.update(d2)

    def _sort_cols(x, y):
        return cmp(columns[x]['pos'], columns[y]['pos'])

    colkeys = columns.keys()
    colkeys.sort(_sort_cols)
    __update_columns(columns, 'patches')

    o = db.patches.patch_nodename
    o |= db.patches.patch_num
    o |= db.patches.patch_rev

    toggle_db_filters()

    # filtering
    query = db.patches.id>0
    query &= db.patches.patch_nodename==db.v_nodes.nodename
    for key in d1.keys():
        if key not in request.vars.keys():
            continue
        query &= _where(None, 'patches', request.vars[key], key)
    for key in d2.keys():
        if key not in request.vars.keys():
            continue
        query &= _where(None, 'v_nodes', request.vars[key], key)

    query &= _where(None, 'patches', domain_perms(), 'patch_nodename')

    query = apply_db_filters(query, 'v_nodes')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select(orderby=o)
    else:
        rows = db(query).select(limitby=(start,end), orderby=o)

    return dict(columns=columns, colkeys=colkeys,
                patches=rows,
                nav=nav,
                active_filters=active_db_filters('v_nodes'),
                available_filters=avail_db_filters('v_nodes'),
               )

@auth.requires_login()
def patches_csv():
    import gluon.contenttype
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    request.vars['perpage'] = 0
    return str(checks()['patches'])

@auth.requires_login()
def _checks_set_low_threshold(request):
    val = int(request.vars.val)
    ids = ([])
    now = datetime.datetime.now()
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        ids += ([key[6:]])
    for i in ids:
        rows = db(db.checks_live.id==i).select()
        if len(rows) != 1:
            continue
        chk = rows[0]
        q = db.checks_settings.chk_nodename==chk.chk_nodename
        q &= db.checks_settings.chk_type==chk.chk_type
        q &= db.checks_settings.chk_instance==chk.chk_instance
        settings = db(q).select()
        if len(settings) == 0:
            # insert
            defq = db.checks_defaults.chk_type==chk.chk_type
            defq &= db.checks_defaults.chk_type==chk.chk_type
            defaults = db(defq).select()
            if len(defaults) != 1:
                continue
            default = defaults[0]
            db.checks_settings.insert(chk_nodename=chk.chk_nodename,
                                      chk_type=chk.chk_type,
                                      chk_instance=chk.chk_instance,
                                      chk_low=val,
                                      chk_high=default.chk_high,
                                      chk_changed_by=user_name(),
                                      chk_changed=now)
        elif len(settings) == 1:
            # update
            db(q).update(chk_low=val,
                         chk_changed_by=user_name(),
                         chk_changed=now)

def _checks_set_high_threshold(request):
    val = int(request.vars.val)
    ids = ([])
    now = datetime.datetime.now()
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        ids += ([key[6:]])
    for i in ids:
        rows = db(db.checks_live.id==i).select()
        if len(rows) != 1:
            continue
        chk = rows[0]
        q = db.checks_settings.chk_nodename==chk.chk_nodename
        q &= db.checks_settings.chk_type==chk.chk_type
        q &= db.checks_settings.chk_instance==chk.chk_instance
        settings = db(q).select()
        if len(settings) == 0:
            # insert
            defq = db.checks_defaults.chk_type==chk.chk_type
            defq &= db.checks_defaults.chk_type==chk.chk_type
            chk_defaults = db(defq).select()
            if len(chk_defaults) != 1:
                continue
            chk_default = chk_defaults[0]
            db.checks_settings.insert(chk_nodename=chk.chk_nodename,
                                      chk_type=chk.chk_type,
                                      chk_instance=chk.chk_instance,
                                      chk_high=val,
                                      chk_low=chk_default.chk_low,
                                      chk_changed_by=user_name(),
                                      chk_changed=now)
        elif len(settings) == 1:
            # update
            db(q).update(chk_high=val,
                         chk_changed_by=user_name(),
                         chk_changed=now)

def _checks_reset_settings(request):
    ids = ([])
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        ids += ([key[6:]])
    for i in ids:
        rows = db(db.checks_live.id==i).select()
        if len(rows) != 1:
            continue
        chk = rows[0]
        q = db.checks_settings.chk_nodename==chk.chk_nodename
        q &= db.checks_settings.chk_type==chk.chk_type
        q &= db.checks_settings.chk_instance==chk.chk_instance
        settings = db(q).delete()

@auth.requires_login()
def checks():
    if request.vars.action == "set_low_thres":
        _checks_set_low_threshold(request)
    elif request.vars.action == "set_high_thres":
        _checks_set_high_threshold(request)
    elif request.vars.action == "reset":
        _checks_reset_settings(request)

    d1 = dict(
        chk_nodename = dict(
            pos = 1,
            title = T('Nodename'),
            display = True,
            nestedin = 'v_checks',
            img = 'node16',
            size = 10
        ),
        chk_svcname = dict(
            pos = 2,
            title = T('Service'),
            display = True,
            nestedin = 'v_checks',
            img = 'check16',
            size = 10
        ),
        chk_type = dict(
            pos = 3,
            title = T('Type'),
            display = True,
            nestedin = 'v_checks',
            img = 'check16',
            size = 3
        ),
        chk_instance = dict(
            pos = 4,
            title = T('Instance'),
            display = True,
            nestedin = 'v_checks',
            img = 'check16',
            size = 10
        ),
        chk_value = dict(
            pos = 5,
            title = T('Value'),
            display = True,
            nestedin = 'v_checks',
            img = 'check16',
            size = 3
        ),
        chk_low = dict(
            pos = 6,
            title = T('Low threshold'),
            display = True,
            nestedin = 'v_checks',
            img = 'check16',
            size = 3
        ),
        chk_high = dict(
            pos = 7,
            title = T('High threshold'),
            display = True,
            nestedin = 'v_checks',
            img = 'check16',
            size = 10
        ),
        chk_created = dict(
            pos = 8,
            title = T('Created'),
            display = False,
            nestedin = 'v_checks',
            img = 'check16',
            size = 6
        ),
        chk_updated = dict(
            pos = 9,
            title = T('Updated'),
            display = True,
            nestedin = 'v_checks',
            img = 'check16',
            size = 6
        ),
    )
    d2 = v_nodes_columns()
    for k in d2:
        d2[k]['pos'] += 10
        d2[k]['display'] = False
        d2[k]['nestedin'] = 'v_nodes'
    del(d2['nodename'])

    columns = d1.copy()
    columns.update(d2)

    def _sort_cols(x, y):
        return cmp(columns[x]['pos'], columns[y]['pos'])

    colkeys = columns.keys()
    colkeys.sort(_sort_cols)
    __update_columns(columns, 'checks')

    o = db.v_checks.chk_nodename
    o |= db.v_checks.chk_type
    o |= db.v_checks.chk_instance

    toggle_db_filters()

    # filtering
    query = db.v_checks.id>0
    query &= db.v_checks.chk_nodename==db.v_nodes.nodename
    for key in d1.keys():
        if key not in request.vars.keys():
            continue
        query &= _where(None, 'v_checks', request.vars[key], key)
    for key in d2.keys():
        if key not in request.vars.keys():
            continue
        query &= _where(None, 'v_nodes', request.vars[key], key)

    query &= _where(None, 'v_checks', domain_perms(), 'chk_nodename')

    query = apply_db_filters(query, 'v_nodes')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select(orderby=o)
    else:
        rows = db(query).select(limitby=(start,end), orderby=o)

    return dict(columns=columns, colkeys=colkeys,
                checks=rows,
                nav=nav,
                active_filters=active_db_filters('v_nodes'),
                available_filters=avail_db_filters('v_nodes'),
               )

def checks_csv():
    import gluon.contenttype
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    request.vars['perpage'] = 0
    return str(checks()['checks'])

class viz(object):
    import os
    vizdir = os.path.join(os.getcwd(), 'applications', 'init', 'static')
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
        files = []
        for name in glob.glob(os.path.join(self.vizdir, self.vizprefix+'*.png')):
            files.append(name)
            os.unlink(name)
        for name in glob.glob(os.path.join(self.vizdir, self.vizprefix+'*.dot')):
            files.append(name)
            os.unlink(name)
        for name in glob.glob(os.path.join(self.vizdir, 'stats_*_[0-9]*.png')):
            files.append(name)
            os.unlink(name)
        for name in glob.glob(os.path.join(self.vizdir, 'stat_*_[0-9]*.png')):
            files.append(name)
            os.unlink(name)
        for name in glob.glob(os.path.join(self.vizdir, 'stats_*_[0-9]*.svg')):
            files.append(name)
            os.unlink(name)
        return files

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
    return viz().viz_cron_cleanup()

def svcmon_csv():
    import gluon.contenttype
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    request.vars['perpage'] = 0
    return str(svcmon()['services'])

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

    if 'ackcomment' in request.vars:
        del request.vars.ackcomment


def _svcaction_ack_one(request, action_id):
        query = (db.v_svcactions.id == action_id)&(db.v_svcactions.status != "ok")
        db(query).update(ack=1,
                         acked_comment=request.vars.ackcomment,
                         acked_by=user_name(),
                         acked_date=datetime.datetime.now())

@auth.requires_login()
def svcactions():
    columns = dict(
        svcname = dict(
            pos = 1,
            title = T('Service'),
            display = True,
            img = 'svc',
            size = 10
        ),
        hostname = dict(
            pos = 2,
            title = T('Node name'),
            display = True,
            img = 'node16',
            size = 6
        ),
        pid = dict(
            pos = 3,
            title = T('Pid'),
            display = True,
            img = 'action16',
            size = 4
        ),
        action = dict(
            pos = 4,
            title = T('Action'),
            display = True,
            img = 'action16',
            size = 6
        ),
        status = dict(
            pos = 5,
            title = T('Status'),
            display = True,
            img = 'action16',
            size = 3
        ),
        begin = dict(
            pos = 6,
            title = T('Begin'),
            display = True,
            img = 'action16',
            size = 6
        ),
        end = dict(
            pos = 7,
            title = T('End'),
            display = True,
            img = 'action16',
            size = 6
        ),
        status_log = dict(
            pos = 8,
            title = T('Log'),
            display = True,
            img = 'action16',
            size = 10
        ),
        time = dict(
            pos = 9,
            title = T('Duration'),
            display = False,
            img = 'action16',
            size = 10
        ),
        id = dict(
            pos = 10,
            title = T('Id'),
            display = False,
            img = 'action16',
            size = 3
        ),
        ack = dict(
            pos = 11,
            title = T('Ack'),
            display = False,
            img = 'action16',
            size = 3
        ),
        app = dict(
            pos = 12,
            title = T('App'),
            display = False,
            img = 'svc',
            size = 3
        ),
        responsibles = dict(
            pos = 13,
            title = T('Responsibles'),
            display = False,
            img = 'guy16',
            size = 6
        ),
    )

    def _sort_cols(x, y):
        return cmp(columns[x]['pos'], columns[y]['pos'])
    colkeys = columns.keys()
    colkeys.sort(_sort_cols)
    __update_columns(columns, 'svcactions')

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

@auth.requires_membership('Manager')
def _nodes_del(request):
    node_ids = ([])
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        node_ids += ([key[6:]])

    if len(node_ids) == 0:
        response.flash = T('invalid node selection')
        return
    for id in node_ids:
        db(db.nodes.id==id).delete()
    response.flash = T('nodes removed')
    del(request.vars['action'])
    redirect(URL(r=request, f='nodes'))

@auth.requires_login()
def ajax_set_user_prefs_column():
    field = request.vars.set_col_field
    table = request.vars.set_col_table
    visible = request.vars.set_col_value
    sql = """replace into user_prefs_columns
             (upc_user_id, upc_table, upc_field, upc_visible)
             values
             (%(uid)s, '%(table)s', '%(field)s', %(visible)s)
          """%dict(uid=session.auth.user.id,
                   table=table, field=field, visible=visible)
    try:
        db.executesql(sql)
    except:
        raise Exception(sql)

@auth.requires_login()
def nodes():
    if request.vars.action is not None and request.vars.action == "delnodes":
        _nodes_del(request)

    o = db.v_nodes.nodename

    columns = v_nodes_columns()
    __update_columns(columns, 'nodes')

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
def checks_defaults_insert():
    q = (db.checks_defaults.chk_type==request.vars.chk_type)
    rows = db(q).select()
    if len(rows) == 1:
        record = rows[0]
    else:
        record = None

    form = SQLFORM(db.checks_defaults,
                 record=record,
                 fields=['chk_type',
                         'chk_low',
                         'chk_high'],
                 labels={'chk_type': T('Check type'),
                         'chk_low': T('Low threshold'),
                         'chk_high': T('High threshold')},
                )
    if form.accepts(request.vars):
        response.flash = T("edition recorded")
        redirect(URL(r=request, f='index'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)

@auth.requires_login()
def checks_settings_insert():
    q = (db.checks_settings.chk_nodename==request.vars.chk_nodename)
    q &= (db.checks_settings.chk_svcname==request.vars.chk_svcname)
    q &= (db.checks_settings.chk_type==request.vars.chk_type)
    q &= (db.checks_settings.chk_instance==request.vars.chk_instance)
    rows = db(q).select()
    if len(rows) == 0:
        defaults = db(db.checks_defaults.chk_type==request.vars.chk_type).select().first()
        db.checks_settings.insert(chk_nodename=request.vars.chk_nodename,
                                  chk_svcname=request.vars.chk_svcname,
                                  chk_type=request.vars.chk_type,
                                  chk_instance=request.vars.chk_instance,
                                  chk_low=defaults.chk_low,
                                  chk_high=defaults.chk_high,
                                 )
        rows = db(q).select()
    record = rows[0]

    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)
    form = SQLFORM(db.checks_settings,
                 record=record,
                 deletable=True,
                 hidden_fields=['chk_changed',
                                'chk_changed_by'],
                 fields=['chk_nodename',
                         'chk_svcname',
                         'chk_type',
                         'chk_instance',
                         'chk_changed',
                         'chk_changed_by',
                         'chk_low',
                         'chk_high'],
                 labels={'chk_nodename': T('Node'),
                         'chk_svcname': T('Service'),
                         'chk_type': T('Check type'),
                         'chk_instance': T('Check instance'),
                         'chk_changed': T('Change date'),
                         'chk_changed_by': T('Change author'),
                         'chk_low': T('Low threshold'),
                         'chk_high': T('High threshold')},
                )
    request.vars['chk_changed_by'] = user_name()
    request.vars['chk_changed'] = str(now)
    if form.accepts(request.vars):
        response.flash = T("edition recorded")
        db(q).update(chk_changed=now,
                     chk_changed_by=user_name())
        redirect(URL(r=request, f='index'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form, record=record)

def _label(key):
    d = v_nodes_columns()
    return DIV(
             IMG(
               _src=URL(r=request,c='static',f=d[key]['img']+'.png'),
               _border=0,
               _style='vertical-align:top;margin-right:10px',
             ),
             d[key]['title'],
           )

def _node_form(record=None):
    if record is not None:
        deletable = True
    else:
        deletable = False
    return SQLFORM(db.nodes,
                 record=record,
                 deletable=deletable,
                 hidden_fields=['mem_bytes',
                                'mem_banks',
                                'mem_slots',
                                'os_name',
                                'os_kernel',
                                'os_vendor',
                                'os_release',
                                'os_arch',
                                'cpu_freq',
                                'cpu_dies',
                                'cpu_cores',
                                'cpu_model',
                                'cpu_vendor',
                                'environnement',
                                'serial',
                                'model'],
                 fields=['nodename',
                         'warranty_end',
                         'status',
                         'role',
                         'type',
                         'loc_country',
                         'loc_zip',
                         'loc_city',
                         'loc_addr',
                         'loc_building',
                         'loc_floor',
                         'loc_room',
                         'loc_rack',
                         'power_supply_nb',
                         'power_cabinet1',
                         'power_cabinet2',
                         'power_protect',
                         'power_protect_breaker',
                         'power_breaker1',
                         'power_breaker2',
                        ],
                 labels={
                         'nodename': _label('nodename'),
                         'warranty_end': _label('warranty_end'),
                         'status': _label('status'),
                         'role': _label('role'),
                         'type': _label('type'),
                         'loc_country': _label('loc_country'),
                         'loc_zip': _label('loc_zip'),
                         'loc_city': _label('loc_city'),
                         'loc_addr': _label('loc_addr'),
                         'loc_building': _label('loc_building'),
                         'loc_floor': _label('loc_floor'),
                         'loc_room': _label('loc_room'),
                         'loc_rack': _label('loc_rack'),
                         'power_supply_nb': _label('power_supply_nb'),
                         'power_cabinet1': _label('power_cabinet1'),
                         'power_cabinet2': _label('power_cabinet2'),
                         'power_protect': _label('power_protect'),
                         'power_protect_breaker': _label('power_protect_breaker'),
                         'power_breaker1': _label('power_breaker1'),
                         'power_breaker2': _label('power_breaker2'),
                        },
                )

@auth.requires_login()
def node_insert():
    form = _node_form()
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
    form = _node_form(record)
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
            'msg_last_editor': user_name(),
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

@auth.requires_login()
def ajax_res_status():
    svcname = request.vars.mon_svcname
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
               H2("%(svc)s@%(node)s"%dict(svc=svcname, node=node),
               _style="text-align:center")
             ),
             t,
             _class="dashboard",
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
        def pid_to_filter(pid):
            if pid is None:
                return ''
            return pid.replace(',', '|')

        if rows[0].end is None:
            end = rows[0].begin
        else:
            end = rows[0].end
            pass

        pid = A(
             rows[0].pid,
             _href=URL(
                     r=request,
                     f='svcactions',
                     vars={
                       'pid':pid_to_filter(rows[0].pid),
                       'hostname':rows[0].hostname,
                       'svcname':rows[0].svcname,
                       'begin':'>'+str(rows[0].begin-datetime.timedelta(days=1)),
                       'end':'<'+str(end+datetime.timedelta(days=1)),
                       'perpage':0,
                     }
          ),
        )
        return SPAN(
                 IMG(
                   _src=URL(r=request,c='static',f='action16.png'),
                   _border=0,
                   _onload="""
                     document.getElementById('spin_span_pid_%(id)s').innerHTML='%(pid)s';
                     document.getElementById('spin_span_end_%(id)s').innerHTML='%(end)s';
                   """%dict(
                         id=id,
                         pid=pid,
                         end=rows[0].end,
                       ),
                   _style='display:none',
                 ),
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
        r = DIV(
              H2(row.mon_nodname, _style='text-align:center'),
              svc_status(row),
              _style='float:left; padding:0 1em',
            )
        return r
    status = map(print_status_row, rows)
    t_status = SPAN(
                 status,
               )

    def print_rstatus_row(row):
        r = DIV(
              res_status(row.mon_svcname, row.mon_nodname),
              _style='float:left',
            )
        return r
    rstatus = map(print_rstatus_row, rows)
    t_rstatus = SPAN(
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

    w = __stats_bar_width(rows)

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
                       width=w,
                       direction='vertical')
    plot2 = bar_plot.T(label="used, cached",
                       hcol=2,
                       stack_on=plot1,
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot3 = bar_plot.T(label="free",
                       hcol=3,
                       stack_on=plot2,
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
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

    w = __stats_bar_width(rows)

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
                       width=w,
                       direction='vertical')
    plot2 = bar_plot.T(label="used",
                       hcol=2,
                       stack_on=plot1,
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot3 = bar_plot.T(label="used, buffer",
                       hcol=4,
                       stack_on=plot2,
                       fill_style=fill_style.black,
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot4 = bar_plot.T(label="used, cache",
                       hcol=5,
                       stack_on=plot3,
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot5 = bar_plot.T(label="used, sys",
                       hcol=8,
                       stack_on=plot4,
                       fill_style=fill_style.Plain(bgcolor=color.coral),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
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

def __stats_bar_width(rows):
    width = 120//len(rows)
    if width == 0:
        return 1
    return width

@auth.requires_login()
def perf_stats_cpu_one(node, s, e, cpu):
    q = db.stats_cpu.nodename == node
    q &= db.stats_cpu.date > s
    q &= db.stats_cpu.date < e
    q &= db.stats_cpu.cpu == cpu
    rows = db(q).select(orderby=db.stats_cpu.date)
    if len(rows) == 0:
        return SPAN()

    w = __stats_bar_width(rows)

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
                       width=w,
                       direction='vertical')
    plot2 = bar_plot.T(label="nice",
                       hcol=2,
                       stack_on=plot1,
                       fill_style=fill_style.Plain(bgcolor=color.darkkhaki),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot3 = bar_plot.T(label="sys",
                       hcol=3,
                       stack_on=plot2,
                       fill_style=fill_style.black,
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot4 = bar_plot.T(label="iowait",
                       hcol=4,
                       stack_on=plot3,
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot5 = bar_plot.T(label="steal",
                       hcol=5,
                       stack_on=plot4,
                       fill_style=fill_style.Plain(bgcolor=color.coral),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot6 = bar_plot.T(label="irq",
                       hcol=6,
                       stack_on=plot5,
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot7 = bar_plot.T(label="soft",
                       hcol=7,
                       stack_on=plot6,
                       fill_style=fill_style.Plain(bgcolor=color.navajowhite2),
                       line_style=None,
                       data = data,
                       width=w,
                       data_label_format="",
                       direction='vertical')
    plot8 = bar_plot.T(label="guest",
                       hcol=8,
                       stack_on=plot7,
                       fill_style=fill_style.Plain(bgcolor=color.plum3),
                       line_style=None,
                       data = data,
                       width=w,
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
def _ajax_perf_stats(f):
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
     return f(node, begin, end)

def ajax_perf_stats_trends():
    return _ajax_perf_stats(perf_stats_trends)

def ajax_perf_stats_cpu():
    return _ajax_perf_stats(perf_stats_cpu)

def ajax_perf_stats_mem_u():
    return _ajax_perf_stats(perf_stats_mem_u)

def ajax_perf_stats_swap():
    return _ajax_perf_stats(perf_stats_swap)

def ajax_perf_stats_proc():
    return _ajax_perf_stats(perf_stats_proc)

def ajax_perf_stats_netdev():
    return _ajax_perf_stats(perf_stats_netdev)

def ajax_perf_stats_netdev_err():
    return _ajax_perf_stats(perf_stats_netdev_err)

def ajax_perf_stats_block():
    return _ajax_perf_stats(perf_stats_block)

def ajax_perf_stats_blockdev():
    return _ajax_perf_stats(perf_stats_blockdev)

@auth.requires_login()
def perf_stats_trends(node, begin, end):
    return DIV(
              perf_stats_cpu_trend(node, begin, end),
              perf_stats_mem_u_trend(node, begin, end),
           )

@auth.requires_login()
def perf_stats(node, rowid):
    def format_ajax(id, f, e):
        return """getElementById('%(e)s').innerHTML='%(spinner)s';
                  ajax("%(url)s",
                       ['node_%(id)s',
                        'begin_%(id)s',
                        'end_%(id)s'
                       ],"%(e)s");
               """%dict(url=URL(r=request,f=f),
                               id=rowid,
                               e=e,
                               spinner=IMG(_src=URL(r=request,c='static',f='spinner_16.png')),
                       )

    now = datetime.datetime.now()
    s = now - datetime.timedelta(days=0,
                                 hours=now.hour,
                                 minutes=now.minute,
                                 microseconds=now.microsecond)
    e = s + datetime.timedelta(days=1)

    timepicker = """Calendar.setup({inputField:this.id, ifFormat:"%Y-%m-%d %H:%M:%S", showsTime: true,timeFormat: "24" });"""
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
              _class='datetime',
              _onfocus=timepicker,
            ),
            INPUT(
              _value=e.strftime("%Y-%m-%d %H:%M"),
              _id='end_'+rowid,
              _class='datetime',
              _onfocus=timepicker,
            ),
            INPUT(
              _value='gen',
              _type='button',
              _onClick=format_ajax(rowid, 'ajax_perf_stats_cpu', 'perf_cpu_'+rowid)+\
                       format_ajax(rowid, 'ajax_perf_stats_mem_u', 'perf_mem_u_'+rowid)+\
                       format_ajax(rowid, 'ajax_perf_stats_trends', 'perf_trends_'+rowid)+\
                       format_ajax(rowid, 'ajax_perf_stats_swap', 'perf_swap_'+rowid)+\
                       format_ajax(rowid, 'ajax_perf_stats_proc', 'perf_proc_'+rowid)+\
                       format_ajax(rowid, 'ajax_perf_stats_netdev', 'perf_netdev_'+rowid)+\
                       format_ajax(rowid, 'ajax_perf_stats_netdev_err', 'perf_netdev_err_'+rowid)+\
                       format_ajax(rowid, 'ajax_perf_stats_block', 'perf_block_'+rowid)+\
                       format_ajax(rowid, 'ajax_perf_stats_blockdev', 'perf_blockdev_'+rowid)
            )
          ),
          DIV(
            _id='perf_trends_'+rowid
          ),
          DIV(
            _id='perf_cpu_'+rowid
          ),
          DIV(
            _id='perf_mem_u_'+rowid
          ),
          DIV(
            _id='perf_swap_'+rowid
          ),
          DIV(
            _id='perf_proc_'+rowid
          ),
          DIV(
            _id='perf_netdev_'+rowid
          ),
          DIV(
            _id='perf_netdev_err_'+rowid
          ),
          DIV(
            _id='perf_block_'+rowid
          ),
          DIV(
            _id='perf_blockdev_'+rowid
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
      TR(TD(T('os kernel'), _style='font-style:italic'), TD(node['os_kernel'])),
      TR(TD(T('os arch'), _style='font-style:italic'), TD(node['os_arch'])),
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

@auth.requires_membership('Manager')
def billing():
    query = (db.v_billing_per_os.nb!=0)
    billing_per_os = db(query).select()
    query = (db.v_billing_per_app.nb!=0)
    billing_per_app = db(query).select()
    return dict(billing_per_os=billing_per_os, billing_per_app=billing_per_app)

#
# XMLRPC
#
#########
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
def push_checks(vars, vals):
    generic_insert('checks_live', vars, vals)

@service.xmlrpc
def update_asset(vars, vals):
    generic_insert('nodes', vars, vals)

@service.xmlrpc
def res_action_batch(vars, vals):
    generic_insert('SVCactions', vars, vals)

def _resmon_clean(node, svcname):
    if node is None or node == '':
        return 0
    if svcname is None or svcname == '':
        return 0
    q = db.resmon.nodename==node.strip("'")
    q &= db.resmon.svcname==svcname.strip("'")
    db(q).delete()
    db.commit()

@service.xmlrpc
def resmon_update(vars, vals):
    h = {}
    for a,b in zip(vars, vals[0]):
        h[a] = b
    if 'nodename' in h and 'svcname' in h:
        _resmon_clean(h['nodename'], h['svcname'])
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
def update_sym_xml(symid, vars, vals):
    import os

    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
    if not os.path.exists(dir):
        os.makedirs(dir)

    dir = os.path.join(dir, symid)
    if not os.path.exists(dir):
        os.makedirs(dir)

    for a,b in zip(vars, vals):
        a = os.path.join(dir, a)
        try:
            f = open(a, 'w')
            f.write(b)
            f.close()
        except:
            pass

    symmetrix = local_import('symmetrix', reload=True)
    s = symmetrix.Vmax(p)

    #
    # better to create hashes from the batch rather than
    # during an interactive session
    #
    s.get_sym_all()

    #
    # populate the diskinfo table
    #
    vars = ['disk_id', 'disk_devid', 'disk_arrayid']
    vals = []
    for devname, dev in s.dev.items():
        vals.append([dev.wwn, devname, symid])
    generic_insert('diskinfo', vars, vals)

@service.xmlrpc
def delete_pkg(node):
    if node is None or node == '':
        return 0
    db(db.packages.pkg_nodename==node).delete()
    db.commit()

@service.xmlrpc
def insert_patch(vars, vals):
    generic_insert('patches', vars, vals)

@service.xmlrpc
def delete_patch(node):
    if node is None or node == '':
        return 0
    db(db.patches.patch_nodename==node).delete()
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

