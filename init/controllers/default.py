# coding: utf8

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    return dict(message=T('Select a report type'))

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

def _pagination(request, query):
    start = 0
    end = 0
    nav = ''
    perpage = int(request.vars.perpage) if 'perpage' in request.vars.keys() else 20

    if perpage <= 0:
        return (start, end, nav)

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

def toggle_session_filters(filters):
    if request.vars.addfilter is not None and request.vars.addfilter != '':
        filters[int(request.vars.addfilter)]['active'] = True
        if request.vars.filtervalue is not None and request.vars.filtervalue != '':
            filters[int(request.vars.addfilter)]['value'] = request.vars.filtervalue
    elif request.vars.delfilter is not None and request.vars.delfilter != '':
        filters[int(request.vars.delfilter)]['active'] = False

def apply_session_filters(filters, query, table=None):
    for filter in filters.values():
        if filter['active']:
            if filter.has_key('q'):
                query &= filter['q']
            elif filter.has_key('field') and table is not None:
                query &= _where(None, table, filter['value'], filter['field'])
    return query

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
        query = (db.apps_responsibles.app_id == id)&(db.apps_responsibles.user_id == request.vars.users)
        rows = db(query).select()
        if len(rows) == 0:
            db.apps_responsibles.insert(app_id=id,user_id=request.vars.users)

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
        query = (db.apps_responsibles.app_id == id)&(db.apps_responsibles.user_id == request.vars.users)
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
        responsibles = dict(
            pos = 2,
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
    query &= _where(None, 'v_svcmon', domain_perms(), 'mon_nodname')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select(db.v_apps.id,
                                db.v_apps.app,
                                db.v_apps.responsibles,
                                orderby=db.v_apps.app,
                                left=db.v_svcmon.on(db.v_svcmon.svc_app==db.v_apps.app),
                                groupby=db.v_apps.app)
    else:
        rows = db(query).select(db.v_apps.id,
                                db.v_apps.app,
                                db.v_apps.responsibles,
                                limitby=(start,end),
                                orderby=db.v_apps.app,
                                left=db.v_svcmon.on(db.v_svcmon.svc_app==db.v_apps.app),
                                groupby=db.v_apps.app)

    query = (db.auth_user.id>0)
    users = db(query).select()
    return dict(columns=columns, colkeys=colkeys,
                apps=rows, users=users, nav=nav)

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
    rows = db(db.v_users.role=="Manager").select()
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
        return T("[%(app)s][%(svcname)s] service configuration not updated for more than 48h", dict(app=row.svc_app, svcname=row.svc_name))

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

def get_racks():
    racks = []
    for row in db(db.nodes.id>0).select(db.nodes.loc_rack, groupby=db.nodes.loc_rack, orderby=db.nodes.loc_rack):
        racks.append(row.loc_rack)
    return dict(racks=racks)

def asset_filters(table):
   return {
    101: dict(name='country',
            id=101,
            active=False,
            value=None,
            field='loc_country',
            table=table,
    ),
    102: dict(name='zip',
            id=102,
            active=False,
            value=None,
            field='loc_zip',
            table=table,
    ),
    103: dict(name='city',
            id=103,
            active=False,
            value=None,
            field='loc_city',
            table=table,
    ),
    104: dict(name='addr',
            id=104,
            active=False,
            value=None,
            field='loc_addr',
            table=table,
    ),
    105: dict(name='building',
            id=105,
            active=False,
            value=None,
            field='loc_building',
            table=table,
    ),
    106: dict(name='floor',
            id=106,
            active=False,
            value=None,
            field='loc_floor',
            table=table,
    ),
    107: dict(name='room',
            id=107,
            active=False,
            value=None,
            field='loc_room',
            table=table,
    ),
    108: dict(name='rack',
            id=108,
            active=False,
            value=None,
            field='loc_rack',
            table=table,
    ),
    109: dict(name='nb power supply',
            id=109,
            active=False,
            value=None,
            field='power_supply_nb',
            table=table,
    ),
    110: dict(name='power cabinet #1',
            id=110,
            active=False,
            value=None,
            field='power_cabinet1',
            table=table,
    ),
    111: dict(name='power cabinet #2',
            id=111,
            active=False,
            value=None,
            field='power_cabinet2',
            table=table,
    ),
    112: dict(name='power protector',
            id=112,
            active=False,
            value=None,
            field='power_protect',
            table=table,
    ),
    113: dict(name='power protector breaker',
            id=113,
            active=False,
            value=None,
            field='power_protect_breaker',
            table=table,
    ),
    114: dict(name='power breaker #1',
            id=114,
            active=False,
            value=None,
            field='power_breaker1',
            table=table,
    ),
    115: dict(name='power breaker #2',
            id=115,
            active=False,
            value=None,
            field='power_breaker2',
            table=table,
    ),
}

@auth.requires_login()
def envfile():
    query = _where(None, 'services', request.vars.svcname, 'svc_name')
    query &= _where(None, 'v_svcmon', domain_perms(), 'svc_name')
    rows = db(query).select()
    if len(rows) == 0:
        return "None"
    #return dict(svc=rows[0])
    envfile = rows[0]['services']['svc_envfile']
    if envfile is None:
        return "None"
    return PRE(envfile.replace('\\n','\n'), _style="text-align:left")

@auth.requires_membership('Manager')
def user_event_log():
    rows = db(db.auth_event.user_id==request.vars.uid).select(orderby=~db.auth_event.id, limitby=(0, 20))
    x = TR(TH(T('Date')), TH(T('From')), TH(T('Event')))
    def to_row(row):
       return TR(TD(row.time_stamp), TD(row.client_ip), TD(row.description))
    xx = map(to_row, rows)
    return TABLE(x, xx)

@auth.requires_membership('Manager')
def _user_grant_manager(request):
    ids = ([])
    manager_group_id = auth.id_group('Manager')
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        ids += ([int(key[6:])])
    for id in ids:
        if not auth.has_membership(manager_group_id, id):
            auth.add_membership(manager_group_id, id)
    redirect(URL(r=request, f='users'))

@auth.requires_membership('Manager')
def _user_revoke_manager(request):
    ids = ([])
    manager_group_id = auth.id_group('Manager')
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        ids += ([int(key[6:])])
    for id in ids:
        if auth.has_membership(manager_group_id, id):
            auth.del_membership(manager_group_id, id)
    redirect(URL(r=request, f='users'))

@auth.requires_membership('Manager')
def _user_domain_edit(request):
    ids = ([])
    manager_group_id = auth.id_group('Manager')
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        id = int(key[6:])
        domains = request.vars["domains_"+str(id)]
        group = auth.user_group(id)
        if domains is None or len(domains) == 0:
            sql = "delete from domain_permissions where group_id=%s"%group
        else:
            sql = "insert into domain_permissions set group_id=%(group)s, domains='%(domains)s' on duplicate key update domains='%(domains)s'"%dict(domains=domains, group=group)
        #raise Exception(sql)
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

@auth.requires_login()
def users():
    if request.vars.action is not None and request.vars.action == "grant":
        _user_grant_manager(request)
    elif request.vars.action is not None and request.vars.action == "revoke":
        _user_revoke_manager(request)
    elif request.vars.action is not None and request.vars.action == "del":
        _user_del(request)
    elif request.vars.action is not None and request.vars.action == "set_domains":
        _user_domain_edit(request)

    o = db.v_users.fullname

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

    return dict(users=rows, nav=nav)

@auth.requires_login()
def svcmon():
    o = db.v_svcmon.mon_svcname|~db.v_svcmon.mon_nodtype

    if not getattr(session, 'svcmon_filters'):
        session.svcmon_filters = {
            1: dict(name='preferred node',
                    id=1,
                    active=False,
                    q=(db.v_svcmon.mon_nodname==db.v_svcmon.svc_autostart)
            ),
            2: dict(name='container name',
                    id=2,
                    active=False,
                    value=None,
                    field='svc_vmname',
            ),
            3: dict(name='opensvc version',
                    id=3,
                    active=False,
                    value=None,
                    field='svc_version',
            ),
            4: dict(name='service name',
                    id=4,
                    active=False,
                    value=None,
                    field='mon_svcname',
            ),
            5: dict(name='nodename',
                    id=5,
                    active=False,
                    value=None,
                    field='mon_nodname',
            ),
            6: dict(name='responsibles',
                    id=6,
                    active=False,
                    value=None,
                    field='responsibles',
            ),
        }
    session.svcmon_filters.update(asset_filters('v_svcmon'))
    toggle_session_filters(session.svcmon_filters)

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
    query &= _where(None, 'v_svcmon', domain_perms(), 'mon_nodname')

    query = apply_session_filters(session.svcmon_filters, query, 'v_svcmon')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select(orderby=o)
    else:
        rows = db(query).select(limitby=(start,end), orderby=o)

    msgs = db(db.svcmessages.id>0).select()
    svcmsg = [msg.msg_svcname for msg in msgs if len(msg.msg_body)>0]

    return dict(services=rows, filters=session.filters, nav=nav, svcmsg=svcmsg)

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
    img_svc = 'applications'+str(URL(r=request,c='static',f='svc.png'))

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

def svcmon_viz():
    request.vars['perpage'] = 0
    s = svcmon()
    v = viz()
    for svc in s['services']:
        v.add_node(svc)
        v.add_disks(svc)
        v.add_service(svc)
        v.add_node2svc(svc)
    fname = v.write('png')
    import os
    img = str(URL(r=request,c='static',f=os.path.basename(fname)))
    return dict(s=s['services'], v=str(v), img=img)

def viz_cron_cleanup():
    viz().viz_cron_cleanup()

def svcmon_csv():
    import gluon.contenttype
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    request.vars['perpage'] = 0
    return svcmon()['services']

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
    if not getattr(session, 'svcactions_filters'):
        session.svcactions_filters = {
            1: dict(name='not acknowledged',
                    id=1,
                    active=False,
                    q=((db.v_svcactions.status=='err')&(db.v_svcactions.ack==None))
               ),
        }

    session.svcactions_filters.update(asset_filters('v_svc_actions'))
    toggle_session_filters(session.svcactions_filters)

    if request.vars.ackcomment is not None:
        _svcaction_ack(request)
    query = _where(None, 'v_svcactions', request.vars.svcname, 'svcname')
    query &= _where(None, 'v_svcactions', request.vars.id, 'id')
    query &= _where(None, 'v_svcactions', request.vars.app, 'app')
    query &= _where(None, 'v_svcactions', request.vars.responsibles, 'responsibles')
    query &= _where(None, 'v_svcactions', request.vars.action, 'action')
    query &= _where(None, 'v_svcactions', request.vars.status, 'status')
    query &= _where(None, 'v_svcactions', request.vars.time, 'time')
    query &= _where(None, 'v_svcactions', request.vars.begin, 'begin')
    query &= _where(None, 'v_svcactions', request.vars.end, 'end')
    query &= _where(None, 'v_svcactions', request.vars.hostname, 'hostname')
    query &= _where(None, 'v_svcactions', request.vars.status_log, 'status_log')
    query &= _where(None, 'v_svcactions', request.vars.pid, 'pid')
    query &= _where(None, 'v_svcactions', request.vars.ack, 'ack')
    query &= _where(None, 'v_svcactions', domain_perms(), 'hostname')

    query = apply_session_filters(session.svcactions_filters, query, 'v_svcactions')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select(orderby=~db.v_svcactions.begin|~db.v_svcactions.id)
    else:
        rows = db(query).select(limitby=(start,end), orderby=~db.v_svcactions.begin|~db.v_svcactions.id)

    return dict(actions=rows, nav=nav)

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
    return svcactions()['actions']

@auth.requires_login()
def services():
    rows = db().select(db.services.ALL)
    return dict(services=rows)

def nodes_csv():
    import gluon.contenttype
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    request.vars['perpage'] = 0
    return nodes()['nodes']

@auth.requires_login()
def nodes():
    columns = dict(
        nodename = dict(
            pos = 1,
            title = T('Node name'),
            size = 10
        ),
        loc_country = dict(
            pos = 2,
            title = T('Country'),
            size = 10
        ),
        loc_zip = dict(
            pos = 3,
            title = T('ZIP'),
            size = 10
        ),
        loc_city = dict(
            pos = 4,
            title = T('City'),
            size = 10
        ),
        loc_addr = dict(
            pos = 5,
            title = T('Address'),
            size = 10
        ),
        loc_building = dict(
            pos = 6,
            title = T('Building'),
            size = 10
        ),
        loc_room = dict(
            pos = 7,
            title = T('Room'),
            size = 10
        ),
        loc_rack = dict(
            pos = 8,
            title = T('Rack'),
            size = 10
        ),
        cpu_freq = dict(
            pos = 9,
            title = T('CPU freq'),
            size = 10
        ),
        mem_bytes = dict(
            pos = 10,
            title = T('Memory'),
            size = 10
        ),
        os_name = dict(
            pos = 11,
            title = T('OS name'),
            size = 10
        ),
        os_kernel = dict(
            pos = 12,
            title = T('OS kernel'),
            size = 10
        ),
        cpu_dies = dict(
            pos = 13,
            title = T('CPU dies'),
            size = 10
        ),
        cpu_model = dict(
            pos = 14,
            title = T('CPU model'),
            size = 10
        ),
        serial = dict(
            pos = 15,
            title = T('Serial'),
            size = 10
        ),
        model = dict(
            pos = 16,
            title = T('Model'),
            size = 10
        ),
        team_responsible = dict(
            pos = 17,
            title = T('Team responsible'),
            size = 10
        ),
        role = dict(
            pos = 18,
            title = T('Role'),
            size = 10
        ),
        environnement = dict(
            pos = 19,
            title = T('Env'),
            size = 10
        ),
        warranty_end = dict(
            pos = 20,
            title = T('Warranty end'),
            size = 10
        ),
        status = dict(
            pos = 21,
            title = T('Status'),
            size = 10
        ),
        type = dict(
            pos = 22,
            title = T('Type'),
            size = 10
        ),
        power_supply_nb = dict(
            pos = 23,
            title = T('Power supply number'),
            size = 10
        ),
        power_cabinet1 = dict(
            pos = 24,
            title = T('Power cabinet #1'),
            size = 10
        ),
        power_cabinet2 = dict(
            pos = 25,
            title = T('Power cabinet #2'),
            size = 10
        ),
        power_protect = dict(
            pos = 26,
            title = T('Power protector'),
            size = 10
        ),
        power_protect_breaker = dict(
            pos = 27,
            title = T('Power protector breaker'),
            size = 10
        ),
        power_breaker1 = dict(
            pos = 28,
            title = T('Power breaker #1'),
            size = 10
        ),
        power_breaker2 = dict(
            pos = 29,
            title = T('Power breaker #2'),
            size = 10
        ),
    )
    def _sort_cols(x, y):
        return cmp(columns[x]['pos'], columns[y]['pos'])
    colkeys = columns.keys()
    colkeys.sort(_sort_cols)

    if not getattr(session, 'nodes_filters'):
        session.nodes_filters = {
            1: dict(name='nodes with services',
                    id=1,
                    active=True,
                    q=(db.nodes.nodename.belongs(db()._select(db.svcmon.mon_nodname))),
            ),
        }

    toggle_session_filters(session.nodes_filters)

    # filtering
    query = (db.nodes.id>0)
    for key in columns.keys():
        if key not in request.vars.keys():
            continue
        query &= _where(None, 'nodes', request.vars[key], key)

    query &= _where(None, 'nodes', domain_perms(), 'nodename')

    query = apply_session_filters(session.nodes_filters, query, 'nodes')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select()
    else:
        rows = db(query).select(limitby=(start,end))

    return dict(columns=columns, colkeys=colkeys,
                nodes=rows,
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
    query = (db.nodes.id>0)
    query &= _where(None, 'nodes', request.vars.node, 'nodename')
    query &= _where(None, 'nodes', domain_perms(), 'nodename')
    rows = db(query).select()
    if len(rows) != 1:
        response.flash = "vars: %s"%str(request.vars)
        return dict(form=None)
    record = rows[0]
    id = record.id
    record = db(db.nodes.id==id).select()[0]
    form=SQLFORM(db.nodes, record)
    if form.accepts(request.vars):
        response.flash = T("edition recorded")
        redirect(URL(r=request, f='node', vars={'nodename':request.vars.node}))
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
    r = lambda x: "'%(x)s'"%dict(x=x)
    sql = "insert into svcmessages (%s) values (%s) on duplicate key update %s"%(
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
                P(T("new message")),
                TEXTAREA(_id='msgbody_'+request.vars.svcname)
               )
    return DIV(
            H3("%(s)s messages"%dict(s=rows[0].msg_svcname)),
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
    rows = db((db.resmon.svcname==request.vars.svcname)&(db.resmon.nodename==request.vars.node)).select(orderby=db.resmon.rid)
    def print_row(row):
        cssclass = 'status_'+row.res_status.replace(" ", "_")
        return TR(
                 TD(row.rid),
                 TD(row.res_desc),
                 TD(row.res_status, _class='%s'%cssclass),
               )
    t = TABLE(
          TR(TH('id'), TH('description'), TH('status')),
          map(print_row, rows)
    )
    return t

@auth.requires_login()
def ajax_node():
    nodes = db(db.nodes.nodename==request.vars.node).select()
    if len(nodes) != 1:
        return T("No asset information for %(node)s",dict(node=request.vars.nodename))
    node = nodes[0]
    loc = TABLE(
      TR(TD(T('location'), _class="boxed", _colspan=2)),
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
      TR(TD(T('power'), _class="boxed", _colspan=2)),
      TR(TD(T('nb power supply'), _style='font-style:italic'), TD(node['power_supply_nb'])),
      TR(TD(T('power cabinet #1'), _style='font-style:italic'), TD(node['power_cabinet1'])),
      TR(TD(T('power cabinet #2'), _style='font-style:italic'), TD(node['power_cabinet2'])),
      TR(TD(T('power protector'), _style='font-style:italic'), TD(node['power_protect'])),
      TR(TD(T('power protector breaker'), _style='font-style:italic'), TD(node['power_protect_breaker'])),
      TR(TD(T('power breaker #1'), _style='font-style:italic'), TD(node['power_breaker1'])),
      TR(TD(T('power breaker #2'), _style='font-style:italic'), TD(node['power_breaker1'])),
    )
    server = TABLE(
      TR(TD(T('server'), _class="boxed", _colspan=2)),
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
      TR(TD(T('cpu'), _class="boxed", _colspan=2)),
      TR(TD(T('cpu frequency'), _style='font-style:italic'), TD(node['cpu_freq'])),
      TR(TD(T('cpu cores'), _style='font-style:italic'), TD(node['cpu_cores'])),
      TR(TD(T('cpu dies'), _style='font-style:italic'), TD(node['cpu_dies'])),
      TR(TD(T('cpu vendor'), _style='font-style:italic'), TD(node['cpu_vendor'])),
      TR(TD(T('cpu model'), _style='font-style:italic'), TD(node['cpu_model'])),
    )
    mem = TABLE(
      TR(TD(T('memory'), _class="boxed", _colspan=2)),
      TR(TD(T('memory banks'), _style='font-style:italic'), TD(node['mem_banks'])),
      TR(TD(T('memory slots'), _style='font-style:italic'), TD(node['mem_slots'])),
      TR(TD(T('memory total'), _style='font-style:italic'), TD(node['mem_bytes'])),
    )
    os = TABLE(
      TR(TD(T('operating system'), _class="boxed", _colspan=2)),
      TR(TD(T('os name'), _style='font-style:italic'), TD(node['os_name'])),
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

    query = (db.v_services.svc_drpnode!=None)&(db.v_services.svc_drpnode!='')
    query &= _where(None, 'v_services', request.vars.svc_name, 'svc_name')
    query &= _where(None, 'v_services', request.vars.svc_app, 'svc_app')
    query &= _where(None, 'v_services', request.vars.responsibles, 'responsibles')
    query &= _where(None, 'v_services', request.vars.svc_type, 'svc_type')
    query &= _where(None, 'v_services', request.vars.svc_drptype, 'svc_drptype')
    query &= _where(None, 'v_services', request.vars.svc_autostart, 'svc_autostart')
    query &= _where(None, 'v_services', request.vars.svc_nodes, 'svc_nodes')
    query &= _where(None, 'v_services', request.vars.svc_drpnode, 'svc_drpnode')
    query &= _where(None, 'v_services', request.vars.svc_drpnodes, 'svc_drpnodes')
    query &= _where(None, 'drpservices', request.vars.svc_wave, 'drp_wave', tableid=db.v_services.id)
    query &= _where(None, 'v_services', domain_perms(), 'svc_nodes')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        svc_rows = db(query).select(db.v_services.ALL, db.drpservices.drp_wave, db.drpservices.drp_project_id, left=db.drpservices.on((db.v_services.svc_name==db.drpservices.drp_svcname)&(db.drpservices.drp_project_id==request.vars.prjlist)),groupby=db.v_services.svc_name)
    else:
        svc_rows = db(query).select(db.v_services.ALL, db.drpservices.drp_wave, db.drpservices.drp_project_id, left=db.drpservices.on((db.v_services.svc_name==db.drpservices.drp_svcname)&(db.drpservices.drp_project_id==request.vars.prjlist)),groupby=db.v_services.svc_name, limitby=(start,end))

    prj_rows = db().select(db.drpprojects.drp_project_id, db.drpprojects.drp_project)
    return dict(services=svc_rows, projects=prj_rows, nav=nav)

def drplan_csv():
    import gluon.contenttype
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    request.vars['perpage'] = 0
    return drplan()['apps']

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

from pychart import *
@auth.requires_login()
def stats():
    def format_x(ordinal):
        d = datetime.date.fromordinal(int(ordinal))
        return "/a50/6{}" + d.strftime("%y-%m-%d")

    def format_y(x):
        return "/6{}" + str(x)

    def tics(min, max):
        s = (10**len(str(max)))/10
        if s < 1: s = 1
        t = []
        for i in range(1, 10):
            t.append(s*i)
            if s*(i+2) > max: break
        return t

    def grid(min, max):
        s = (10**len(str(max)))/10
        if s < 1: s = 1
        t = []
        for i in range(1, 10):
            t.append(s*i)
            if s*(i+1) > max: break
        return t


    rows = db(db.stat_day.id>0).select(orderby=db.stat_day.day)

    """ actions
    """
    action = str(URL(r=request,c='static',f='stat_action.png'))
    path = 'applications'+action
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    data = [(row.day.toordinal(), row.nb_action_ok, row.nb_action_warn, row.nb_action_err) for row in rows]

    chart_object.set_defaults(area.T, y_range = (0, None),
                              x_coord = category_coord.T(data, 0))
    chart_object.set_defaults(bar_plot.T, data = data)
    ar = area.T(x_coord = category_coord.T(data, 0),
                y_grid_interval=grid,
                x_axis = axis.X(label="", format=format_x, tic_interval=3),
                y_axis = axis.Y(label="", format=format_y, tic_interval=tics))
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="ok", fill_style=fill_style.black)
    plot2 = bar_plot.T(label="warn", hcol=2, stack_on = plot1, fill_style=fill_style.yellow)
    plot3 = bar_plot.T(label="err", hcol=3, stack_on = plot2, fill_style=fill_style.red)
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

    chart_object.set_defaults(area.T, y_range = (0, None),
                              x_coord = category_coord.T(data, 0))
    chart_object.set_defaults(bar_plot.T, data = data)
    ar = area.T(x_coord = category_coord.T(data, 0),
                y_grid_interval=grid,
                x_axis = axis.X(label = "", format=format_x, tic_interval=3),
                y_axis = axis.Y(label = "", format=format_y, tic_interval=tics))
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="err", fill_style=fill_style.red)
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()

    """ services (drp ready)
    """
    action = str(URL(r=request,c='static',f='stat_service_type.png'))
    path = 'applications'+action
    can = canvas.init(path)

    data = [(row.day.toordinal(), row.nb_svc_prd, row.nb_svc-row.nb_svc_prd) for row in rows]
    chart_object.set_defaults(area.T, y_range = (0, None),
                              x_coord = category_coord.T(data, 0))
    chart_object.set_defaults(bar_plot.T, data = data)
    ar = area.T(x_coord = category_coord.T(data, 0),
                y_grid_interval=grid,
                x_axis = axis.X(label = "", format=format_x, tic_interval=3),
                y_axis = axis.Y(label = "", format=format_y, tic_interval=tics))
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="prd svc")
    plot2 = bar_plot.T(label="other svc", hcol=2, stack_on = plot1)
    ar.add_plot(plot1, plot2)
    ar.draw(can)
    can.close()

    """ services (drp ready)
    """
    action = str(URL(r=request,c='static',f='stat_service.png'))
    path = 'applications'+action
    can = canvas.init(path)

    data = [(row.day.toordinal(), row.nb_svc_with_drp, row.nb_svc_prd-row.nb_svc_with_drp) for row in rows]
    chart_object.set_defaults(area.T, y_range = (0, None),
                              x_coord = category_coord.T(data, 0))
    chart_object.set_defaults(bar_plot.T, data = data)
    ar = area.T(x_coord = category_coord.T(data, 0),
                y_grid_interval=grid,
                x_axis = axis.X(label = "", format=format_x, tic_interval=3),
                y_axis = axis.Y(label = "", format=format_y, tic_interval=tics))
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="prd svc with drp")
    plot2 = bar_plot.T(label="prd svc without drp", hcol=2, stack_on = plot1)
    ar.add_plot(plot1, plot2)
    ar.draw(can)
    can.close()

    """ services (clustered)
    """
    action = str(URL(r=request,c='static',f='stat_service_clustered.png'))
    path = 'applications'+action
    can = canvas.init(path)

    data = [(row.day.toordinal(), row.nb_svc_cluster, row.nb_svc-row.nb_svc_cluster) for row in rows]
    chart_object.set_defaults(area.T, y_range = (0, None),
                              x_coord = category_coord.T(data, 0))
    chart_object.set_defaults(bar_plot.T, data = data)
    ar = area.T(x_coord = category_coord.T(data, 0),
                y_grid_interval = grid,
                x_axis = axis.X(label = "", format=format_x, tic_interval=3),
                y_axis = axis.Y(label = "", format=format_y, tic_interval = tics))
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="clustered svc")
    plot2 = bar_plot.T(label="not clustered svc", hcol=2, stack_on = plot1)
    ar.add_plot(plot1, plot2)
    ar.draw(can)
    can.close()

    """ nodes
    """
    action = str(URL(r=request,c='static',f='stat_node.png'))
    path = 'applications'+action
    can = canvas.init(path)

    data = [(row.day.toordinal(), row.nb_nodes_prd, row.nb_nodes-row.nb_nodes_prd) for row in rows]
    chart_object.set_defaults(area.T, y_range = (0, None),
                              x_coord = category_coord.T(data, 0))
    chart_object.set_defaults(bar_plot.T, data = data)
    ar = area.T(x_coord = category_coord.T(data, 0),
                y_grid_interval = grid,
                x_axis = axis.X(label = "", format=format_x, tic_interval=3),
                y_axis = axis.Y(label = "", format=format_y, tic_interval=tics))
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="prd nodes")
    plot2 = bar_plot.T(label="other nodes", hcol=2, stack_on = plot1)
    ar.add_plot(plot1, plot2)
    ar.draw(can)
    can.close()

    """ apps
    """
    action = str(URL(r=request,c='static',f='stat_app.png'))
    path = 'applications'+action
    can = canvas.init(path)

    data = [(row.day.toordinal(), row.nb_apps) for row in rows]
    chart_object.set_defaults(area.T, y_range = (0, None),
                              x_coord = category_coord.T(data, 0))
    chart_object.set_defaults(bar_plot.T, data = data)
    ar = area.T(x_coord = category_coord.T(data, 0),
                y_grid_interval = grid,
                x_axis = axis.X(label = "", format=format_x, tic_interval=3),
                y_axis = axis.Y(label = "", format=format_y, tic_interval=tics))
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="apps")
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()

    """ accounts
    """
    action = str(URL(r=request,c='static',f='stat_accounts.png'))
    path = 'applications'+action
    can = canvas.init(path)

    data = [(row.day.toordinal(), row.nb_accounts) for row in rows]
    chart_object.set_defaults(area.T, y_range = (0, None),
                              x_coord = category_coord.T(data, 0))
    chart_object.set_defaults(bar_plot.T, data = data)
    ar = area.T(x_coord = category_coord.T(data, 0),
                y_grid_interval = grid,
                x_axis = axis.X(label="", format=format_x, tic_interval=3),
                y_axis = axis.Y(label="", format=format_y, tic_interval=tics))
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="accounts")
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()

    """ disks
    """
    action = str(URL(r=request,c='static',f='stat_disk.png'))
    path = 'applications'+action
    can = canvas.init(path)

    data = [(row.day.toordinal(), row.disk_size) for row in rows]
    chart_object.set_defaults(area.T, y_range = (0, None),
                              x_coord = category_coord.T(data, 0))
    chart_object.set_defaults(bar_plot.T, data = data)
    ar = area.T(x_coord = category_coord.T(data, 0),
                y_grid_interval = grid,
                x_axis = axis.X(label = "", format=format_x, tic_interval=3),
                y_axis = axis.Y(label = "", format=format_y, tic_interval=tics))
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="disk size (GB)")
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()

    """ disks per svc
    """
    sql = "select svcname, group_concat(disk_size order by day separator ',') from stat_day_svc group by svcname"
    rows = db.executesql(sql)

    action = str(URL(r=request,c='static',f='stat_disk_svc.png'))
    path = 'applications'+action
    can = canvas.init(path)

    data1 = [(row[0], int(row[1].split(',')[-1]) or 0) for row in rows]
    data = sorted(data1, key = lambda x: x[1])[-10:]
    chart_object.set_defaults(area.T, y_range = (0, None),
                              x_coord = category_coord.T(data, 0))
    chart_object.set_defaults(bar_plot.T, data = data)
    ar = area.T(x_coord = category_coord.T(data, 0),
                y_grid_interval = grid,
                x_axis = axis.X(label = "", format="/a60%s"),
                y_axis = axis.Y(label = "", format=format_y, tic_interval=tics))
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="disk size (GB)")
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()

    return dict()

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
    elif isinstance(x, str) and x[0] == "'" and x[-1] == "'":
        return x
    else:
        return "'%s'"%str(x)

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
    generic_insert('services', vars, vals)

@service.xmlrpc
def res_action_batch(vars, vals):
    generic_insert('SVCactions', vars, vals)

@service.xmlrpc
def resmon_update(vars, vals):
    generic_insert('resmon', vars, vals)

@service.xmlrpc
def svcmon_update(vars, vals):
    generic_insert('svcmon', vars, vals)

@service.xmlrpc
def register_disk(vars, vals):
    generic_insert('svcdisks', vars, vals)

@service.xmlrpc
def register_sync(vars, vals):
    generic_insert('svc_res_sync', vars, vals)

@service.xmlrpc
def register_ip(vars, vals):
    generic_insert('svc_res_ip', vars, vals)

@service.xmlrpc
def register_fs(vars, vals):
    generic_insert('svc_res_fs', vars, vals)

@service.xmlrpc
def delete_syncs(svcname):
    if svcname is None or svcname == '':
        return 0
    db(db.svc_res_sync.sync_svcname==svcname).delete()
    db.commit()

@service.xmlrpc
def delete_ips(svcname, node):
    if svcname is None or svcname == '':
        return 0
    if node is None or node == '':
        return 0
    db((db.svc_res_ip.ip_svcname==svcname)&(db.svc_res_ip.ip_node==node)).delete()
    db.commit()

@service.xmlrpc
def delete_fss(svcname):
    if svcname is None or svcname == '':
        return 0
    db(db.svc_res_fs.fs_svcname==svcname).delete()
    db.commit()

@service.xmlrpc
def delete_disks(svcname, node):
    if svcname is None or svcname == '':
        return 0
    db((db.svcdisks.disk_svcname==svcname)&(db.svcdisks.disk_nodename==node)).delete()
    db.commit()

