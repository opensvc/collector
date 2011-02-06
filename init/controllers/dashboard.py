def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

one_days_ago = now - datetime.timedelta(days=1)
tmo = now - datetime.timedelta(minutes=15)

def PANEL(a, content=None):
    a = a.replace('.', '_')
    if content is None:
        content = DIV("Loading ...", _id="panelbody_"+a)
        pass

    d = DIV(
      DIV(
        A(
          "X",
          _id="panelclose_"+a,
          _onclick="getElementById('panel_%s').className='panel';"%a,
          _class="panel_close",
        ),
        _id="panelmove_"+a,
        _class="panel_move",
        _ondblclick="getElementById('panel_%s').className='panel';"%a,
      ),
      content,
      _id="panel_"+a,
      _class="panel",
      _onmouseover="""$("#panel_%(a)s").draggable({handle: "#panelmove_%(a)s"});"""%dict(a=a)
    )
    return d

def svc_status(svc, cellclass="cell2", nestedin=None):
    cl = {}
    for k in ['mon_overallstatus',
              'mon_containerstatus',
              'mon_ipstatus',
              'mon_fsstatus',
              'mon_diskstatus',
              'mon_syncstatus',
              'mon_appstatus',
              'mon_hbstatus']:
        if nestedin is None:
            if svc[k] is None:
                cl[k] = 'status_undef'
            elif 'mon_updated' in svc and svc['mon_updated'] < tmo:
                cl[k] = 'status_expired'
            else:
                cl[k] = 'status_'+svc[k].replace(" ", "_")
        else:
            if svc[nestedin][k] is None:
                cl[k] = 'status_undef'
            elif 'mon_updated' in svc[nestedin] and \
                 svc[nestedin]['mon_updated'] < tmo:
                cl[k] = 'status_expired'
            else:
                cl[k] = 'status_'+svc[nestedin][k].replace(" ", "_")

    if nestedin is None:
        overallstatus = svc.mon_overallstatus
    else:
        overallstatus = svc[nestedin].mon_overallstatus


    t = DIV(
          TABLE(
            TR(
              TD(overallstatus,
                 _colspan=7,
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
              TD("hb", _class=cellclass+' '+cl['mon_hbstatus']),
            ),
          ),
          _class="svcstatus",
        )
    return t

def _header(header):
    l = []
    for h in header:
        l.append(TH(T(h)))
    tr = TR(*l)
    return tr

def _table(data, id, title, header, lfmt):
    if len(data) == 0:
        return DIV()

    cellclass = 'cell1'
    cellclasses = {}
    cellclasses['cell1'] = 'cell2'
    cellclasses['cell2'] = 'cell1'
    lines = []

    for line in data:
        cellclass = cellclasses[cellclass]
        lines += [lfmt(line, cellclass)]

    t = DIV(
         TABLE(
           TR(
             TD(
               H2(T(title)),
               _colspan=99,
             ),
           ),
           _header(header),
           lines,
         ),
         _class="dashboard",
         _id=id,
       )
    return t

""" Service status not updated
"""
def svcmon_not_updated_line(line, cellclass):
    tr = TR(
      TD(
        A(
          line.mon_svcname,
          _href=URL(r=request, c='default', f='svcmon',
                    vars={'svcmon_f_svc_name':line.mon_svcname,
                          'clear_filters': 'true'})
        ),
       _class=cellclass,
      ),
      TD(
        A(
          line.mon_nodname,
          _href=URL(r=request, c='default', f='svcmon',
                    vars={'svcmon_f_mon_nodname':line.mon_nodname,
                          'clear_filters': 'true'})
        ),
        _class=cellclass
      ),
      TD(
        line.mon_updated,
        _class=cellclass
      ),
      TD(
        svc_status(line, cellclass),
        _class=cellclass,
        _style="text-align:center",
      ),
    )
    return tr

def svcmon_not_updated(svcnotupdated, title):
    return _table(data=svcnotupdated,
                  id='svcmon_not_updated',
                  title=title,
                  header=["Service",
                          "Node",
                          "Last updated date",
                          "Last known status"],
                  lfmt=svcmon_not_updated_line)

@service.json
def svcnotupdated():
    title = 'Service status not updated'
    if request.args[2] == 'false':
        return ['', '', '', '', str(T(title))]
    q = db.v_svcmon.mon_updated<tmo
    q &= _where(None, 'v_svcmon', domain_perms(), 'mon_svcname')
    q = apply_db_filters(q, 'v_svcmon')
    svcnotupdated = db(q).select(orderby=~db.v_svcmon.mon_updated, limitby=(0,50))
    return [0, 1, len(svcnotupdated), str(svcmon_not_updated(svcnotupdated, title)), str(T(title))]


""" node checks
"""
def node_checks_line(line, cellclass):
    vars = {
        'chk_nodename':line.v_checks.chk_nodename,
        'chk_svcname':line.v_checks.chk_svcname,
        'chk_type':line.v_checks.chk_type,
        'chk_instance':line.v_checks.chk_instance,
    }
    tr = TR(
           TD(
             A(
               line.v_checks.chk_nodename,
               _href=URL(r=request, c='checks', f='checks',
                         vars={'checks_f_chk_nodename':line.v_checks.chk_nodename,
                               'clear_filters': 'true'}),
             ),
             _class=cellclass,
           ),
           TD(
             A(
               line.v_checks.chk_svcname,
               _href=URL(r=request, c='checks',
                         f='checks_settings_insert', vars=vars),
             ),
             _class=cellclass,
           ),
           TD(
             A(
               line.v_checks.chk_type,
               _href=URL(r=request, c='checks',
                         f='checks_defaults_insert', vars=vars),
             ),
             _class=cellclass,
           ),
           TD(
             A(
               line.v_checks.chk_instance,
               _href=URL(r=request, c='checks',
                         f='checks_settings_insert', vars=vars),
             ),
             _class=cellclass,
           ),
           TD(
              line.v_checks.chk_value,
              _class=cellclass,
           ),
           TD(
             A(
               line.v_checks.chk_low,
               _href=URL(r=request, c='checks',
                         f='checks_settings_insert', vars=vars),
             ),
             _class=cellclass,
           ),
           TD(
             A(
               line.v_checks.chk_high,
               _href=URL(r=request, c='checks',
                         f='checks_settings_insert', vars=vars),
             ),
             _class=cellclass,
           ),
         )
    return tr

def node_checks(checks, title):
    return _table(data=checks,
                  id='node_checks',
                  title=title,
                  header=["Node",
                          "Service",
                          "Check",
                          "Instance",
                          "Value",
                          "Low threshold",
                          "High threshold"],
                  lfmt=node_checks_line)

@service.json
def checks():
    title = 'Node check alerts'
    if request.args[2] == 'false':
        return ['', '', '', '', str(T(title))]
    q = db.v_checks.chk_value < db.v_checks.chk_low
    q |= db.v_checks.chk_value > db.v_checks.chk_high
    query = _where(None, 'v_checks', domain_perms(), 'chk_nodename')
    query &= q
    query &= db.v_checks.chk_nodename==db.v_nodes.nodename
    query = apply_db_filters(query, 'v_nodes')
    checks = db(query).select()
    return [0, 1, len(checks), str(node_checks(checks, title)), str(T(title))]


""" Last status changes
"""
def last_changes_line(line, cellclass):
    d = prettydate(line.svcmon_log.mon_begin, T)
    tr = TR(
      TD(
        A(
          d,
          _href=URL(r=request, c='svcmon_log', f='svcmon_log',
                    vars={'svcmon_log_f_mon_svcname':line.svcmon_log.mon_svcname,
                          'clear_filters': 'true'}),
        ),
        _class=cellclass,
      ),
      TD(
        A(
          line.svcmon_log.mon_svcname,
          _href=URL(r=request, c='default', f='svcmon',
                    vars={'svcmon_f_svc_name':line.svcmon_log.mon_svcname,
                          'clear_filters': 'true'}),
        ),
        _class=cellclass,
      ),
      TD(
        A(
          line.svcmon_log.mon_nodname,
          _href=URL(r=request, c='default', f='svcmon',
                    vars={'svcmon_f_mon_nodname':line.svcmon_log.mon_nodname,
                          'clear_filters': 'true'}),
        ),
        _class=cellclass,
      ),
      TD(
         svc_status(line, cellclass, nestedin='svcmon_log'),
         _class=cellclass,
         _style="text-align:center",
      ),
    )
    return tr

def last_changes(data, title):
    return _table(data=data,
                  id='node_checks',
                  title=title,
                  header=["Since",
                          "Service",
                          "Node",
                          "Status"],
                  lfmt=last_changes_line)

@service.json
def lastchanges():
    title = "Last service status changes"
    if request.args[2] == 'false':
        return ['', '', '', '', str(T(title))]
    onehourago = now - datetime.timedelta(minutes=60)
    query = db.svcmon_log.mon_begin>onehourago
    query &= db.svcmon_log.mon_svcname==db.v_svcmon.mon_svcname
    query &= db.svcmon_log.mon_nodname==db.v_svcmon.mon_nodname
    query &= _where(None, 'svcmon_log', domain_perms(), 'mon_svcname')
    query = apply_db_filters(query, 'v_svcmon')
    n = db(query).count()
    lastchanges = db(query).select(orderby=~db.svcmon_log.mon_begin, limitby=(0,20))
    return [0, 20, n, str(last_changes(lastchanges, title)), title, '/h']


""" Services with unacknowleged errors
"""
def svc_with_errors_line(line, cellclass):
    tr = TR(
      TD(
        A(
          line.svc_name,
          _href=URL(r=request, c='default', f='svcmon',
                    vars={'svcmon_f_svc_name':line.svc_name,
                          'clear_filters': 'true'}),
        ),
        _class=cellclass,
      ),
      TD(
        line.svc_type,
        _class=cellclass,
      ),
      TD(
        A(
          line.err,
          _href=URL(r=request,c='svcactions',f='svcactions',
                    vars={'actions_f_svcname': line.svc_name,
                          'actions_f_status': 'err',
                          'actions_f_ack': '!1|empty',
                          'clear_filters': 'true'}),
        ),
        _class=cellclass,
      ),
      TD(
        svc_status(line, cellclass),
        _class=cellclass,
        _style="text-align:center",
      ),
    )
    return tr

def svc_with_errors(data, title):
    return _table(data=data,
                  id='svc_with_errors',
                  title=title,
                  header=["Service",
                          "Env",
                          "Error count",
                          "Status"],
                  lfmt=svc_with_errors_line)

@service.json
def svcwitherrors():
    title = "Services with errors"
    if request.args[2] == 'false':
        return ['', '', '', '', str(T(title))]
    query = (db.v_svcmon.err>0)
    query &= _where(None, 'v_svcmon', domain_perms(), 'mon_svcname')
    query = apply_db_filters(query, 'v_svcmon')
    data = db(query).select(orderby=~db.v_svcmon.err,
                            groupby=db.v_svcmon.mon_svcname)
    return [0, 1, len(data),
            str(svc_with_errors(data, title)), str(T(title))]

""" pkg differences amongst cluster nodes
"""
def pkg_diff_line(data, line, cellclass):
    tr = TR(
      TD(
        line.replace(',', ', '),
        _class=cellclass,
        _style="cursor:help",
        _onclick="""
               getElementById("node").value="%(nodes)s";
               ajax("%(url)s",['node'],"panelbody_%(a)s");
               getElementById("panel_%(a)s").className="panel_shown";
               getElementById("panel_%(a)s").style.top=event.pageY+'px';
            """%dict(url=URL(r=request,c='pkgdiff',f='ajax_pkgdiff'),
                     nodes=line, a='pkgdiff'),
      ),
      TD(
        data[line],
        _class=cellclass,
        _style="cursor:help",
        _onclick="""
               getElementById("node").value="%(nodes)s";
               ajax("%(url)s",['node'],"panelbody_%(a)s");
               getElementById("panel_%(a)s").className="panel_shown";
               getElementById("panel_%(a)s").style.top=event.pageY+'px';
            """%dict(url=URL(r=request,c='pkgdiff',f='ajax_pkgdiff'),
                     nodes=line, a='pkgdiff'),
      ),
    )
    return tr

def pkg_diff_header():
    tr = TR(
      TH(T("Cluster")),
      TH(T("Number of package differences")),
    )
    return tr

def pkg_diff_table(data, title):
    cellclass = 'cell1'
    cellclasses = {}
    cellclasses['cell1'] = 'cell2'
    cellclasses['cell2'] = 'cell1'
    lines = []

    for line in sorted(data, key=data.__getitem__):
        cellclass = cellclasses[cellclass]
        lines += [pkg_diff_line(data, line, cellclass)]

    t = TABLE(
        TR(
          TD(
            H2(T(title)),
            _colspan=99,
          ),
        ),
        pkg_diff_header(),
        lines,
    )
    return t

def pkg_diff(data, title):
    if len(data) == 0:
        return DIV()
    d = DIV(
      PANEL('pkgdiff'),
      INPUT(_id='node', _type='hidden'),
      pkg_diff_table(data, title),
      _class='dashboard',
    )
    return d


@service.json
def pkgdiff():
    title = "Package differences amongst cluster nodes"
    if request.args[2] == 'false':
        return ['', '', '', '', str(T(title))]
    data = {}
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
        if key in data:
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
        data[key] = x[0][0]

    return [0, 1, len(data),
            str(pkg_diff(data, title)), str(T(title))]


""" Services not up on all nodes
"""
def svc_not_up_line(line, cellclass):
    tr = TR(
      TD(
        A(
          line.v_svc_group_status.svcname,
           _href=URL(r=request, c='default', f='svcmon',
                     vars={'svcmon_f_svc_name':line.v_svc_group_status.svcname,
                           'clear_filters': 'true'}),
        ),
        _class=cellclass,
      ),
      TD(
        line.v_svc_group_status.svctype,
        _class=cellclass,
      ),
      TD(
        line.v_svc_group_status.nodes.replace(',', ', '),
        _class=cellclass,
      ),
      TD(
        line.v_svc_group_status.groupstatus.replace(',', ', '),
        _class=cellclass,
      ),
    )
    return tr

def svc_not_up(data, title):
    return _table(data=data,
                  id='svc_not_up',
                  title=title,
                  header=["Service",
                          "Env",
                          "Cluster",
                          "Cluster status"],
                  lfmt=svc_not_up_line)

@service.json
def svcnotup():
    title = "Services not up"
    if request.args[2] == 'false':
        return ['', '', '', '', str(T(title))]
    query = (~db.v_svc_group_status.groupstatus.like("up,%"))
    query &= (~db.v_svc_group_status.groupstatus.like("%,up,%"))
    query &= (~db.v_svc_group_status.groupstatus.like("%,up"))
    query &= (db.v_svc_group_status.groupstatus!="up")
    query &= _where(None, 'v_svc_group_status', domain_perms(), 'svcname')
    query &= db.v_svc_group_status.svcname==db.v_svcmon.mon_svcname
    query = apply_db_filters(query, 'v_svcmon')
    data = db(query).select(groupby=db.v_svc_group_status.svcname, orderby=db.v_svc_group_status.svcname)

    return [0, 1, len(data),
            str(svc_not_up(data, title)), str(T(title))]


""" Services not up on their primary node
"""
def svc_not_on_primary_line(line, cellclass):
    tr = TR(
      TD(
        A(
          line.v_svcmon.svc_name,
          _href=URL(r=request, c='default', f='svcmon',
                    vars={'svcmon_f_svc_name':line.v_svcmon.svc_name,
                          'clear_filters': 'true'}),
        ),
        _class=cellclass,
      ),
      TD(
        A(
          line.v_svcmon.svc_autostart,
          _href=URL(r=request, c='default', f='svcmon',
                    vars={'svcmon_f_mon_nodname':line.v_svcmon.svc_autostart,
                          'clear_filters': 'true'}),
        ),
        _class=cellclass,
      ),
      TD(
        line.v_svcmon.svc_type,
        _class=cellclass,
      ),
      TD(
        svc_status(line.v_svcmon, cellclass),
        _class=cellclass,
        _style="text-align:center",
      ),
    )
    return tr

def svc_not_on_primary(data, title):
    return _table(data=data,
                  id='svc_not_on_primary',
                  title=title,
                  header=["Service",
                          "Primary node",
                          "Env",
                          "Status on primary"],
                  lfmt=svc_not_on_primary_line)

@service.json
def svcnotonprimary():
    title = "Services not up on primary"
    if request.args[2] == 'false':
        return ['', '', '', '', str(T(title))]
    query = _where(None, 'v_svcmon', domain_perms(), 'mon_svcname')
    query &= (db.v_svcmon.svc_autostart==db.v_svcmon.mon_nodname)
    query &= ((db.v_svcmon.mon_overallstatus!="up")|(db.v_svcmon.mon_updated<tmo))
    q = db.v_svc_group_status.groupstatus.like("up,%")
    q |= db.v_svc_group_status.groupstatus.like("%,up,%")
    q |= db.v_svc_group_status.groupstatus.like("%,up")
    q |= db.v_svc_group_status.groupstatus=="up"
    query &= db.v_svc_group_status.svcname==db.v_svcmon.mon_svcname
    query &= q
    query = apply_db_filters(query, 'v_svcmon')
    data = db(query).select()
    return [0, 1, len(data),
            str(svc_not_on_primary(data, title)), str(T(title))]


""" Applications without responsibles
"""
def app_wo_resp_line(line, cellclass):
    tr = TR(
      TD(line.app, _class=cellclass),
    )
    return tr
    pass

def app_wo_resp(data, title):
    return _table(data=data,
                  id='app_wo_resp',
                  title=title,
                  header=["App"],
                  lfmt=app_wo_resp_line)

@service.json
def appwithoutresp():
    title = "Application without responsibles"
    if request.args[2] == 'false':
        return ['', '', '', '', str(T(title))]
    query = (db.v_apps.responsibles==None)
    query |= (db.v_apps.responsibles=="")
    data = db(query).select(db.v_apps.app)
    return [0, 1, len(data),
            str(app_wo_resp(data, title)), str(T(title))]


""" Systems close to warranty end
"""
def warranty_end_line(line, cellclass):
    tr = TR(
      TD(
        A(
          line.nodename,
          _href=URL(r=request, c='default', f='svcmon',
                    vars={'svcmon_f_mon_nodname':line.nodename,
                          'clear_filters': 'true'}),
        ),
        _class=cellclass,
      ),
      TD(
        line.warranty_end,
        _class=cellclass,
      ),
    )
    return tr

def warranty_end(data, title):
    return _table(data=data,
                  id='warranty_end',
                  title=title,
                  header=["Nodename", "Warranty end"],
                  lfmt=warranty_end_line)

@service.json
def warrantyend():
    title = "Nodes close to warranty end"
    if request.args[2] == 'false':
        return ['', '', '', '', str(T(title))]
    query = db.v_nodes.warranty_end < now + datetime.timedelta(days=30)
    query &= db.v_nodes.warranty_end != "0000-00-00 00:00:00"
    query &= db.v_nodes.warranty_end is not None
    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
    query = apply_db_filters(query, 'v_nodes')
    data = db(query).select(db.v_nodes.nodename,
                            db.v_nodes.warranty_end,
                            orderby=db.v_nodes.warranty_end)
    return [0, 1, len(data),
            str(warranty_end(data, title)), str(T(title))]


""" Systems obsolescent (alert)
"""
def obs_os_alert_line(line, cellclass):
    tr = TR(
      TD(
        A(
          line.v_nodes.nodename,
          _href=URL(r=request, c='default', f='svcmon',
                    vars={'svcmon_f_mon_nodname':line.v_nodes.nodename,
                          'clear_filters': 'true'}),
        ),
        _class=cellclass,
      ),
      TD(
        line.obsolescence.obs_name,
        _class=cellclass,
      ),
      TD(
        line.obsolescence.obs_alert_date,
        _class=cellclass,
      ),
    )
    return tr

def obs_os_alert(data, title):
    return _table(data=data,
                  id='obs_os_alert',
                  title=title,
                  header=["Nodename", "Operating system", "Alert since"],
                  lfmt=obs_os_alert_line)

@service.json
def obsosalert():
    title = "Nodes with obsolescent operating system (alert)"
    if request.args[2] == 'false':
        return ['', '', '', '', str(T(title))]
    query = (db.obsolescence.obs_alert_date!=None)&(db.obsolescence.obs_alert_date!="0000-00-00")&(db.obsolescence.obs_alert_date<now)
    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
    query = apply_db_filters(query, 'v_nodes')
    join = db.obsolescence.obs_type=="os"
    join &= db.obsolescence.obs_name==db.v_nodes.os_concat
    data = db(query).select(db.v_nodes.nodename,
                            db.obsolescence.obs_name,
                            db.obsolescence.obs_alert_date,
                            left=db.v_nodes.on(join),
                            orderby=db.obsolescence.obs_alert_date|db.v_nodes.nodename
                           )
    return [0, 1, len(data),
            str(obs_os_alert(data, title)), str(T(title))]


""" Systems obsolescent (alert)
"""
def obs_os_warn_line(line, cellclass):
    tr = TR(
      TD(
        A(
          line.v_nodes.nodename,
          _href=URL(r=request, c='default', f='svcmon',
                    vars={'svcmon_f_mon_nodname':line.v_nodes.nodename,
                          'clear_filters': 'true'}),
        ),
        _class=cellclass,
      ),
      TD(
        line.obsolescence.obs_name,
        _class=cellclass,
      ),
      TD(
        line.obsolescence.obs_warn_date,
        _class=cellclass,
      ),
    )
    return tr

def obs_os_warn(data, title):
    return _table(data=data,
                  id='obs_os_warn',
                  title=title,
                  header=["Nodename", "Operating system", "Warning since"],
                  lfmt=obs_os_warn_line)

@service.json
def obsoswarn():
    title = "Nodes with obsolescent operating system (warn)"
    if request.args[2] == 'false':
        return ['', '', '', '', str(T(title))]
    warn = (db.obsolescence.obs_warn_date!=None)&(db.obsolescence.obs_warn_date!="0000-00-00")&(db.obsolescence.obs_warn_date<now)
    alert = (db.obsolescence.obs_alert_date==None)|(db.obsolescence.obs_alert_date=="0000-00-00")|(db.obsolescence.obs_alert_date>=now)
    query = warn & alert
    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
    query = apply_db_filters(query, 'v_nodes')
    join = db.obsolescence.obs_type=="os"
    join &= db.obsolescence.obs_name==db.v_nodes.os_concat
    data = db(query).select(db.v_nodes.nodename,
                            db.obsolescence.obs_name,
                            db.obsolescence.obs_warn_date,
                            left=db.v_nodes.on(join),
                            orderby=db.obsolescence.obs_warn_date|db.v_nodes.nodename
                           )
    return [0, 1, len(data),
            str(obs_os_warn(data, title)), str(T(title))]


""" Model obsolescent (alert)
"""
def obs_hw_alert_line(line, cellclass):
    tr = TR(
      TD(
        A(
          line.v_nodes.nodename,
          _href=URL(r=request, c='default', f='svcmon',
                    vars={'svcmon_f_mon_nodname':line.v_nodes.nodename,
                          'clear_filters': 'true'}),
        ),
        _class=cellclass,
      ),
      TD(
        line.obsolescence.obs_name,
        _class=cellclass,
      ),
      TD(
        line.obsolescence.obs_alert_date,
        _class=cellclass,
      ),
    )
    return tr

def obs_hw_alert(data, title):
    return _table(data=data,
                  id='obs_hw_alert',
                  title=title,
                  header=["Nodename", "Model", "Alert since"],
                  lfmt=obs_hw_alert_line)

@service.json
def obshwalert():
    title = "Nodes with obsolescent hardware (alert)"
    if request.args[2] == 'false':
        return ['', '', '', '', str(T(title))]
    query = (db.obsolescence.obs_alert_date!=None)&(db.obsolescence.obs_alert_date!="0000-00-00")&(db.obsolescence.obs_alert_date<now)
    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
    query = apply_db_filters(query, 'v_nodes')
    join = db.obsolescence.obs_type=="hw"
    join &= db.obsolescence.obs_name==db.v_nodes.model
    data = db(query).select(db.v_nodes.nodename,
                            db.obsolescence.obs_name,
                            db.obsolescence.obs_alert_date,
                            left=db.v_nodes.on(join),
                            orderby=db.obsolescence.obs_alert_date|db.v_nodes.nodename
                           )
    return [0, 1, len(data),
            str(obs_hw_alert(data, title)), str(T(title))]


""" Model obsolescent (warning)
"""
def obs_hw_warn_line(line, cellclass):
    tr = TR(
      TD(
        A(
          line.v_nodes.nodename,
          _href=URL(r=request, c='default', f='svcmon',
                    vars={'svcmon_f_mon_nodname':line.v_nodes.nodename,
                          'clear_filters': 'true'}),
        ),
        _class=cellclass,
      ),
      TD(
        line.obsolescence.obs_name,
        _class=cellclass,
      ),
      TD(
        line.obsolescence.obs_warn_date,
        _class=cellclass,
      ),
    )
    return tr

def obs_hw_warn(data, title):
    return _table(data=data,
                  id='obs_hw_warn',
                  title=title,
                  header=["Nodename", "Model", "Warning since"],
                  lfmt=obs_hw_warn_line)

@service.json
def obshwwarn():
    title = "Nodes with obsolescent hardware (warn)"
    if request.args[2] == 'false':
        return ['', '', '', '', str(T(title))]
    warn = (db.obsolescence.obs_warn_date!=None)&(db.obsolescence.obs_warn_date!="0000-00-00")&(db.obsolescence.obs_warn_date<now)
    alert = (db.obsolescence.obs_alert_date==None)|(db.obsolescence.obs_alert_date=="0000-00-00")|(db.obsolescence.obs_alert_date>=now)
    query = warn & alert
    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
    query = apply_db_filters(query, 'v_nodes')
    join = db.obsolescence.obs_type=="hw"
    join &= db.obsolescence.obs_name==db.v_nodes.model
    data = db(query).select(db.v_nodes.nodename,
                            db.obsolescence.obs_name,
                            db.obsolescence.obs_warn_date,
                            left=db.v_nodes.on(join),
                            orderby=db.obsolescence.obs_warn_date|db.v_nodes.nodename
                           )
    return [0, 1, len(data),
            str(obs_hw_warn(data, title)), str(T(title))]


""" Obsolescence information missing
"""
def obs_miss(obswarnmiss, obsalertmiss, title):
    if obswarnmiss + obsalertmiss == 0:
        return DIV()
    return DIV(
      TABLE(
        TR(
          TD(
            H2(T(title)),
            _colspan=99,
          ),
        ),
        TR(
          TH(T("Date not set")),
          TH(T("Item count")),
        ),
        TR(
          TD(T("Warn")),
          TD(
            A(obswarnmiss,
              _href=URL(r=request, c='obsolescence', f='obsolescence_config',
                        vars={'obs_f_obs_warn_date': 'empty|0000-00-00 00:00:00',
                              'clear_filters': 'true'})
            ),
          ),
        ),
        TR(
          TD(T("Alert"), _class="cell1"),
          TD(
            A(
              obsalertmiss,
              _href=URL(r=request, c='obsolescence', f='obsolescence_config',
                        vars={'obs_f_obs_alert_date': 'empty|0000-00-00 00:00:00',
                              'clear_filters': 'true'}),
            ),
            _class="cell1",
          ),
        ),
      ),
      _class="dashboard",
      _id="obs_miss",
    )

@service.json
def obsmiss():
    title = "Items with missing obsolescence information"
    if request.args[2] == 'false':
        return ['', '', '', '', str(T(title))]
    rows = db(db.v_users.id==session.auth.user.id).select(db.v_users.manager)
    if len(rows) == 1 and rows[0].manager == 1:
        query = (db.obsolescence.obs_warn_date==None)|(db.obsolescence.obs_warn_date=="0000-00-00")
        query &= (db.v_nodes.os_concat==db.obsolescence.obs_name)|(db.v_nodes.model==db.obsolescence.obs_name)
        query &= (~db.v_nodes.model.like("%virtual%"))
        query &= (~db.v_nodes.model.like("%virtuel%"))
        query &= (~db.v_nodes.model.like("%cluster%"))
        query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
        query = apply_db_filters(query, 'v_nodes')
        rows = db(query).select(db.obsolescence.obs_name,
                                groupby=db.obsolescence.obs_name)
        obswarnmiss = len(rows)

        query = (db.obsolescence.obs_alert_date==None)|(db.obsolescence.obs_alert_date=="0000-00-00")
        query &= (db.v_nodes.os_concat==db.obsolescence.obs_name)|(db.v_nodes.model==db.obsolescence.obs_name)
        query &= (~db.v_nodes.model.like("%virtual%"))
        query &= (~db.v_nodes.model.like("%virtuel%"))
        query &= (~db.v_nodes.model.like("%cluster%"))
        query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
        query = apply_db_filters(query, 'v_nodes')
        rows = db(query).select(db.obsolescence.obs_name,
groupby=db.obsolescence.obs_name)
        obsalertmiss = len(rows)
    else:
        obswarnmiss = 0
        obsalertmiss = 0
    return [0, 1, obswarnmiss+obsalertmiss,
            str(obs_miss(obswarnmiss, obsalertmiss, title)), str(T(title))]


""" Nodes without asset
"""
def nodes_without_asset_line(line, cellclass):
    tr = TR(
      TD(
        A(
          line.mon_nodname,
          _href=URL(r=request, c='default', f='svcmon',
                    vars={'svcmon_f_mon_nodname':line.mon_nodname,
                          'clear_filters': 'true'}),
        ),
        _class=cellclass,
      ),
    )
    return tr

def nodes_without_asset(data, title):
    return _table(data=data,
                  id='nodes_without_asset',
                  title=title,
                  header=["Nodename"],
                  lfmt=nodes_without_asset_line)

@service.json
def nodeswithoutasset():
    title = "Nodes without asset information"
    if request.args[2] == 'false':
        return ['', '', '', '', str(T(title))]
    q = ~db.svcmon.mon_nodname.belongs(db()._select(db.nodes.nodename))
    q &= _where(None, 'svcmon', domain_perms(), 'mon_nodname')
    data = db(q).select(db.svcmon.mon_nodname,
                        groupby=db.svcmon.mon_nodname)
    return [0, 1, len(data),
            str(nodes_without_asset(data, title)), str(T(title))]


""" Frozen services
"""
def frozen_line(line, cellclass):
    tr = TR(
      TD(
        A(
          line.mon_svcname,
          _href=URL(r=request, c='default', f='svcmon',
                    vars={'svcmon_f_svc_name':line.mon_svcname,
                          'clear_filters': 'true'}),
        ),
        _class=cellclass,
      ),
      TD(
        A(
          line.mon_nodname,
          _href=URL(r=request, c='default', f='svcmon',
                    vars={'svcmon_f_mon_nodname':line.mon_nodname,
                          'clear_filters': 'true'}),
        ),
        _class=cellclass,
      ),
    )
    return tr

def frozen_t(data, title):
    return _table(data=data,
                  id='frozen',
                  title=title,
                  header=["Service", "Nodename"],
                  lfmt=frozen_line)

@service.json
def frozen():
    title = "Frozen services"
    if request.args[2] == 'false':
        return ['', '', '', '', str(T(title))]
    query = db.v_svcmon.mon_frozen==1
    query &= _where(None, 'v_svcmon', domain_perms(), 'mon_nodname')
    query = apply_db_filters(query, 'v_svcmon')
    data = db(query).select(db.v_svcmon.mon_svcname,
                            db.v_svcmon.mon_nodname,
                            orderby=db.v_svcmon.mon_svcname)
    return [0, 1, len(data),
            str(frozen_t(data, title)), str(T(title))]


""" Netdev errors
"""
def netdev_err_line(line, cellclass):
    tr = TR(
      TD(
        A(
          line.v_stats_netdev_err_avg_last_day.nodename,
          _href=URL(r=request, c='default', f='svcmon',
                    vars={'svcmon_f_mon_nodname':line.v_stats_netdev_err_avg_last_day.nodename})
        ),
        _class=cellclass
      ),
      TD(line.v_stats_netdev_err_avg_last_day.dev, _class=cellclass),
      TD("%.02f"%line.v_stats_netdev_err_avg_last_day.avgrxerrps,
         _class=cellclass),
      TD("%.02f"%line.v_stats_netdev_err_avg_last_day.avgtxerrps,
         _class=cellclass),
      TD("%.02f"%line.v_stats_netdev_err_avg_last_day.avgcollps,
         _class=cellclass),
      TD("%.02f"%line.v_stats_netdev_err_avg_last_day.avgrxdropps,
         _class=cellclass),
      TD("%.02f"%line.v_stats_netdev_err_avg_last_day.avgtxdropps,
         _class=cellclass),
    )
    return tr

def netdev_err(data, title):
    return _table(data=data,
                  id='netdev_err',
                  title=title,
                  header=["Nodename",
                          "Device",
                          "Avg rx err/s",
                          "Avg tx err/s",
                          "Avg coll/s",
                          "Avg rx drop/s",
                          "Avg tx drop/s"],
                  lfmt=netdev_err_line)

@service.json
def netdeverrs():
    title = "Nodes with network device errors in the last day"
    if request.args[2] == 'false':
        return ['', '', '', '', str(T(title))]
    q = db.v_stats_netdev_err_avg_last_day.avgrxerrps > 0
    q |= db.v_stats_netdev_err_avg_last_day.avgtxerrps > 0
    q |= db.v_stats_netdev_err_avg_last_day.avgcollps > 0
    q |= db.v_stats_netdev_err_avg_last_day.avgrxdropps > 0
    q |= db.v_stats_netdev_err_avg_last_day.avgtxdropps > 0
    query = _where(None, 'v_stats_netdev_err_avg_last_day', domain_perms(), 'nodename')
    query &= db.v_stats_netdev_err_avg_last_day.nodename==db.v_nodes.nodename
    query = apply_db_filters(query, 'v_nodes')
    query &= q
    data = db(query).select()
    return [0, 1, len(data),
            str(netdev_err(data, title)), str(T(title))]

@service.json
def toggle():
    dashboard = request.args[2]
    u = auth.user_id
    q = db.upc_dashboard.upc_user_id==u
    q &= db.upc_dashboard.upc_dashboard==dashboard
    rows = db(q).select()
    if len(rows) > 0:
        db(q).delete()
    else:
        db.upc_dashboard.insert(upc_user_id=u, upc_dashboard=dashboard)


