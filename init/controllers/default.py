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


    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select(orderby=db.v_apps.app)
    else:
        rows = db(query).select(limitby=(start,end), orderby=db.v_apps.app)

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

def alerts_apps_without_responsible():
    import datetime
    now = datetime.datetime.now()
    in_24h = now + datetime.timedelta(hours=24)

    def managers():
        rows = db(db.v_users.role=="Manager").select()
        m = []
        for row in rows:
            m.append(row.email)
        return ','.join(m)

    rows = db((db.v_apps.id>0)&(db.v_apps.mailto==None)).select()
    for row in rows:
        subject = T("[%(app)s] application has no responsible", dict(app=row.app))
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
        db.alerts.insert(subject=subject,
                         body=body,
                         send_at=now,
                         created_at=now,
                         sent_to=row.mailto)

    return dict(alerts=rows)

def alerts_services_not_updated():
    """ Alert if service is not updated for 48h
    """
    import datetime
    now = datetime.datetime.now()
    two_day_ago = now - datetime.timedelta(days=2)
    three_day_ago = now - datetime.timedelta(days=3)

    def format_subject(row):
        return T("[%(app)s][%(svcname)s] service configuration not updated for more than 48h", dict(app=row.svc_app, svcname=row.svc_name))

    rows = db(db.v_services.updated<two_days_ago).select()
    for row in rows:
        subject = format_subject(row)
        body = T("Service will be purged from database after 3 days without update")
        dups = db(db.alerts.subject==subject).select()
        if len(dups) > 0:
            """ don't raise a duplicate alert
            """
            continue
        db.alerts.insert(subject=subject,
                         body=body,
                         send_at=now,
                         created_at=now,
                         sent_to=row.mailto)

    """ Remove the service after 3 days
    """
    rows = db(db.v_services.mon_updated<three_day_ago).select()
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
        body = T("Service will be purged from database after 24 hours without update")
        dups = db(db.alerts.subject==subject).select()
        if len(dups) > 0:
            """ don't raise a duplicate alert
            """
            continue
        db.alerts.insert(subject=subject,
                         body=body,
                         send_at=now,
                         created_at=now,
                         sent_to=row.mailto)

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
    import datetime

    now = datetime.datetime.now()
    in_24h = now + datetime.timedelta(hours=24)
    rows = db((db.v_svcactions.status=='err')&((db.v_svcactions.ack!=1)|(db.v_svcactions.ack==None))).select(orderby=db.v_svcactions.end)
    for row in rows:
        d = dict(app=row.app,
                 svcname=row.svcname,
                 action=row.action,
                 node=row.hostname)
        subject = T("[%(app)s] failed action '%(svcname)s %(action)s' on node '%(node)s' not acknowledged", d)

        body = T("node: %(node)s\n"+\
                 "service: %(service)s\n"+\
                 "app: %(app)s\n"+\
                 "responsibles: %(responsibles)s\n"+\
                 "action: %(action)s\n"+\
                 "begin: %(begin)s\n"+\
                 "end: %(end)s\n"+\
                 "error message:\n%(log)s\n", dict(
                  node=row.hostname,
                  service=row.svcname,
                  app=row.app,
                  responsibles=row.responsibles,
                  action=row.action,
                  begin=row.begin,
                  end=row.end,
                  log=row.status_log,
                ))

        """ Check if the alert is already queued
        """
        dups = db(db.alerts.action_id==row.id).select()
        if len(dups) > 0:
            continue

        """ Queue alert
        """
        db.alerts.insert(subject=subject,
                         body=body,
                         send_at=in_24h,
                         created_at=now,
                         action_id=row.id,
                         sent_to=row.mailto)

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
        msg = "To: %s\r\nFrom: %s\r\nSubject: %s\r\nContent-type: text/html;charset=utf-8\r\n%s"%(row.sent_to, botaddr, row.subject, row.body)
        try:
            server.sendmail(botaddr, row.sent_to, msg)
        except:
            """ Don't mark as sent if the mail sending fails
            """
            raise
            continue

        db(db.alerts.id==row.id).update(sent_at=now)
        row.sent_at=now

        """ If the alert concerns an unaknowledged action,
            auto-ack it
        """
        ack_comment = T("Automatically acknowledged upon ticket generation. Alert sent to %(to)s", dict(to=row.sent_to))
        if row.action_id is not None:
            db(db.SVCactions.id==row.action_id).update(ack=1, acked_comment=ack_comment, acked_date=now, acked_by=botaddr)

    server.quit()
    return dict(alerts_sent=rows)

@auth.requires_login()
def alerts():
    columns = dict(
        id = dict(
            pos = 1,
            title = T('Alert Id'),
            size = 5
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
            size = 10
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
def svcmon():
    if not getattr(session, 'svcmon_filters'):
        session.svcmon_filters = {
            1: dict(name='preferred node',
                    id=1,
                    active=False,
                    q=(db.v_svcmon.mon_nodname==db.v_svcmon.svc_autostart)
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

    query = apply_session_filters(session.svcmon_filters, query, 'v_svcmon')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select(orderby=db.v_svcmon.mon_svcname|~db.v_svcmon.mon_nodtype)
    else:
        rows = db(query).select(limitby=(start,end), orderby=db.v_svcmon.mon_svcname|~db.v_svcmon.mon_nodtype)

    return dict(services=rows, filters=session.filters, nav=nav)

class viz(object):
    vizdir = 'applications'+str(URL(r=request,c='static',f='/'))
    vizprefix = 'tempviz'
    services = set([])
    resources = {}
    prdnodes = set([])
    drpnodes = set([])
    prddisks = {}
    drpdisks = {}
    array = {}
    arrayinfo = {}
    drpsvc2disk = set([])
    prddisk2svc = set([])
    prdnode2disk = set([])
    drpnode2disk = set([])
    drpdisk2node = set([])
    syncs = {}
    data = ""
    img_node = 'applications'+str(URL(r=request,c='static',f='node.png'))
    img_disk = 'applications'+str(URL(r=request,c='static',f='hd.png'))
    img_svc = 'applications'+str(URL(r=request,c='static',f='svc.png'))
    img_sync = 'applications'+str(URL(r=request,c='static',f='sync.png'))

    def __str__(self):
        buff = """
        digraph G {
                rankdir=LR;
                ranksep=0.75;
                nodesep=0.1;
                splines=true;
                penwidth=1;
                center=true;
                fontsize=8;

                node [shape=plaintext, fontsize=8];
                edge [fontsize=8];

                bgcolor=white;
        """
        self.add_arrays()
        buff += self.data
        buff += self.rank(self.prdnodes)
        buff += self.rank(self.prddisks.values())
        buff += self.rank(self.services)
        buff += self.rank(self.syncs.values())
        buff += self.rank(self.drpdisks.values())
        buff += self.rank(self.drpnodes)
        buff += "}"
        return buff

    def write(self, type):
        import tempfile
        f = tempfile.NamedTemporaryFile(delete=False, dir=self.vizdir, prefix=self.vizprefix)
        f.close()
        dot = f.name + '.dot'
        with open(dot, 'w') as f:
            f.write(str(self))
            f.close()
        if type == 'dot':
            return dot
        from subprocess import *
        dst = f.name + '.' + type
        cmd = [ 'dot', '-T'+type, '-o', dst, dot ]
        process = Popen(cmd, stdout=None, stderr=None)
        process.communicate()
        return dst

    def viz_cron_cleanup(self):
        """ unlink static/.viz*.png
        """
        import os
        for name in glob.glob(self.vizdir + '/.viz*.png'):
            os.unlink(name)

    def __init__(self):
        pass

    def add_service(self, svc):
        vid = 'svc_'+svc
        if vid in self.services: return
        self.services |= set([vid])
        if svc not in self.resources:
            self.resources[svc] = set([])
        self.data += r"""
        %(v)s [label="%(s)s", fontsize=12];
        subgraph cluster_%(v)s {%(v)s; %(res)s};
        """%(dict(v=vid, s=svc, img=self.img_svc, res=';'.join(self.resources[svc])))

    def add_node(self, vid, node, model="", mem=""):
        self.data += r"""
        %(v)s [label="%(n)s\n%(model)s\n%(mem)s MB", image="%(img)s"];
        """%(dict(v=vid, n=node, model=model, mem=mem, img=self.img_node))

    def add_prdnode(self, node, model="", mem=""):
        vid = 'node_'+node
        if vid in self.prdnodes: return
        self.prdnodes |= set([vid])
        self.add_node(vid, node, model, mem)

    def add_drpnode(self, node, model=None, mem=None):
        vid = 'node_'+node
        if vid in self.drpnodes: return
        self.drpnodes |= set([vid])
        self.add_node(vid, node, model, mem)

    def add_disk(self, vid, disk, size="", vendor="", model="", arrayid="", devid=""):
        self.add_array(vid, arrayid, vendor, model)
        self.data += r"""
        %(id)s [label="%(name)s\n%(devid)s\n%(size)s GB", image="%(img)s"];
        """%(dict(id=vid, name=disk, size=size, img=self.img_disk, devid=devid))

    def add_array(self, vid, arrayid="", vendor="", model=""):
        if arrayid == "":
            return
        if arrayid not in self.array:
            self.array[arrayid] = set([vid])
        else:
            self.array[arrayid] |= set([vid])
        if arrayid not in self.arrayinfo:
            self.arrayinfo[arrayid] = "%s - %s"%(vendor.strip(), model.strip())

    def add_arrays(self):
        for a in self.array:
            self.data += r"""
        subgraph cluster_%(a)s {label="%(l)s"; fontsize=12; %(disks)s};
        """%(dict(a=a, l=r"""%s\n%s"""%(a, self.arrayinfo[a]), disks='; '.join(self.array[a])))

    def add_prddisk(self, id, disk, size="", vendor="", model="", arrayid="", devid=""):
        vid = 'disk_'+str(id)
        if disk in self.prddisks: return
        self.prddisks[disk]= vid
        self.add_disk(vid, disk, size, vendor, model, arrayid, devid)

    def add_drpdisk(self, id, disk, size="", vendor="", model="", arrayid="", devid=""):
        vid = 'disk_'+str(id)
        if disk in self.drpdisks: return
        self.drpdisks[disk] = vid
        self.add_disk(vid, disk, size, vendor, model, arrayid, devid)

    def rank(self, list):
        return """{ rank=same; %s };
               """%'; '.join(list)

    def add_prdnode2disk(self, node, disk):
        vid1 = 'node_'+node
        vid2 = self.prddisks[disk]
        key = vid1+vid2
        if key in self.prdnode2disk: return
        self.prdnode2disk |= set([key])
        self.data += """
        edge [label="", arrowsize=0, color=black]; %(n)s -> %(d)s;
        """%(dict(n=vid1, d=vid2))

    def add_prddisk2svc(self, disk, svc):
        vid1 = self.prddisks[disk]
        vid2 = 'svc_'+svc
        key = vid1+vid2
        if key in self.prddisk2svc: return
        self.prddisk2svc |= set([key])
        self.data += """
        edge [label="", arrowsize=0, color=grey]; %(d)s -> %(s)s;
        """%(dict(d=vid1, s=vid2))

    def add_drpsvc2disk(self, svc, disk):
        vid1 = 'svc_'+svc
        vid2 = self.drpdisks[disk]
        key = vid1+vid2
        if key in self.drpsvc2disk: return
        self.drpsvc2disk |= set([key])
        self.data += """
        edge [label="", arrowsize=0, color=grey]; %(s)s -> %(d)s;
        """%(dict(s=vid1, d=vid2))

    def add_drpdisk2node(self, disk, node):
        vid1 = self.drpdisks[disk]
        vid2 = 'node_'+node
        key = vid1+vid2
        if key in self.drpdisk2node: return
        self.drpdisk2node |= set([key])
        self.data += """
        edge [label="", arrowsize=0, color=black]; %(d)s -> %(n)s;
        """%(dict(d=vid1, n=vid2))

    def add_sync(self, svc, sync):
        key = svc,sync.sync_src,sync.sync_dst
        vid = "sync_%d"%len(self.syncs)
        if key in self.syncs:
            return
        self.syncs[key] = vid
        if svc not in self.resources:
            self.resources[svc] = set([])
        self.resources[svc] |= set([vid])
        label = r"%s\n(%s)"%(sync.sync_src, ",".join(sync.sync_prdtarget.split(' ')+sync.sync_drptarget.split(' ')))
        self.data += r"""
        %(v)s [label="%(s)s", image="%(img)s"];
        """%(dict(v=vid, s=label, img=self.img_sync))

    def add_dg(self, svc, dg):
        vid = "dg_" + svc + "_" + dg
        if svc not in self.resources:
            self.resources[svc] = set([])
        self.resources[svc] |= set([vid])
        self.data += r"""
        %(v)s [label="%(s)s", image="%(img)s"];
        """%(dict(v=vid, s=dg, img=self.img_disk))


def svcmon_viz():
    request.vars['perpage'] = 0
    s = svcmon()
    v = viz()
    disks = db(db.svcdisks.id>0).select()
    for svc in s['services']:
        for sync in db(db.svc_res_sync.sync_svcname==svc.svc_name).select():
            v.add_sync(svc.svc_name, sync)
        dl = [ disk for disk in disks if disk.disk_nodename == svc.mon_nodname and disk.disk_svcname == svc.svc_name ]
        if svc.mon_nodtype == 'PRD':
            v.add_prdnode(svc.mon_nodname, svc.model, svc.mem_bytes)
            if len(dl) == 0:
                disk_id = svc.mon_nodname + "_unknown"
                v.add_prddisk(svc.mon_nodname, disk_id, size="?")
                v.add_prdnode2disk(svc.mon_nodname, disk_id)
                v.add_prddisk2svc(disk_id, svc.svc_name)
            else:
                for d in dl:
                    v.add_dg(svc.svc_name, d.disk_dg)
                    v.add_prddisk(d.id, d.disk_id, d.disk_size, d.disk_vendor, d.disk_model, d.disk_arrayid, d.disk_devid)
                    v.add_prdnode2disk(svc.mon_nodname, d.disk_id)
                    v.add_prddisk2svc(d.disk_id, svc.svc_name)
        else:
            v.add_drpnode(svc.mon_nodname, svc.model, svc.mem_bytes)
            if len(dl) == 0:
                disk_id = svc.mon_nodname + "_unknown"
                v.add_drpdisk(svc.mon_nodname, disk_id, size="?")
                v.add_drpsvc2disk(svc.svc_name, disk_id)
                v.add_drpdisk2node(disk_id, svc.mon_nodname)
            else:
                for d in dl:
                    v.add_drpdisk(d.id, d.disk_id, d.disk_size, d.disk_vendor, d.disk_model, d.disk_arrayid, d.disk_devid)
                    v.add_drpsvc2disk(svc.svc_name, d.disk_id)
                    v.add_drpdisk2node(d.disk_id, svc.mon_nodname)
        v.add_service(svc.svc_name)
    fname = v.write('png')
    import os
    img = str(URL(r=request,c='static',f=os.path.basename(fname)))
    return dict(s=s['services'], v=str(v), disks=disks, img=img)

def viz_cron_cleanup():
    viz().viz_cron_cleanup()

def svcmon_csv():
    import gluon.contenttype
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    request.vars['perpage'] = 0
    return svcmon()['services']

def _svcaction_ack(request):
    action_ids = ([])
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        action_ids += ([key[6:]])
    for action_id in action_ids:
        query = (db.v_svcactions.id == action_id)&(db.v_svcactions.status != "ok")
        db(query).update(ack=1,
                         acked_comment=request.vars.ackcomment,
                         acked_by=' '.join([session.auth.user.first_name, session.auth.user.last_name]),
                         acked_date=datetime.datetime.now())
        """ Cancel pending alert
        """
        db((db.alerts.action_id==action_id)&(db.alerts.sent_at==None)).delete()
    del request.vars.ackcomment

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
def node():
    node = db(db.nodes.nodename==request.vars.nodename).select()
    if len(node) != 1:
        response.flash(T('error'))
        return
    return dict(node=node)

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

@service.xmlrpc
def delete_services(hostid=None):
    if hostid is None:
        return 0
    db(db.services.svc_hostid==hostid).delete()
    db.commit()
    return 0

@service.xmlrpc
def update_service(vars, vals):
    if 'svc_hostid' not in vars:
        return 0
    sql="""insert delayed into services (%s) values (%s)""" % (','.join(vars), ','.join(vals))
    db.executesql(sql)
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

@service.xmlrpc
def svcmon_update(vars, vals):
    upd = []
    for a, b in zip(vars, vals):
        upd.append("%s=%s" % (a, b))
    sql="""insert delayed into svcmon (%s) values (%s) on duplicate key update %s""" % (','.join(vars), ','.join(vals), ','.join(upd))
    db.executesql(sql)
    db.commit()
    return 0

@service.xmlrpc
def register_disk(vars, vals):
    upd = []
    for a, b in zip(vars, vals):
        upd.append("%s=%s" % (a, b))
    sql="""insert delayed into svcdisks (%s) values (%s) on duplicate key update %s""" % (','.join(vars), ','.join(vals), ','.join(upd))
    db.executesql(sql)
    db.commit()
    return 0

@service.xmlrpc
def register_sync(vars, vals):
    upd = []
    for a, b in zip(vars, vals):
        upd.append("%s=%s" % (a, b))
    sql="""insert delayed into svc_res_sync (%s) values (%s) on duplicate key update %s""" % (','.join(vars), ','.join(vals), ','.join(upd))
    db.executesql(sql)
    db.commit()
    return 0

@service.xmlrpc
def delete_syncs(svcname):
    if svcname is None or svcname == '':
        return 0
    db(db.svc_res_sync.sync_svcname==svcname).delete()
    db.commit()
    return 0

