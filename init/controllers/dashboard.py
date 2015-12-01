def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget(response)
    return service()

@service.json
def json_dash_history():
    t = table_dashboard('dashboard', 'ajax_dashboard')

    q = db.dashboard_events.id > 0
    for f in set(t.cols):
        if f == 'dash_created':
            continue
        if t.colprops[f].filter_redirect is not None:
            _f = t.colprops[f].filter_redirect
            _t = "dashboard_ref"
        elif f == "dash_type":
            _f = f
            _t = "dashboard_ref"
        else:
            _f = f
            _t = "dashboard_events"
        q = _where(q, _t, t.filter_parse(f),  _f)
    q &= _where(None, 'dashboard_events', domain_perms(), 'dash_svcname')|_where(None, 'dashboard_events', domain_perms(), 'dash_nodename')
    q = apply_filters(q, db.dashboard_events.dash_nodename, db.dashboard_events.dash_svcname)

    sql = """select
               v.begin,
               count(v.begin)
             from (
               select
                 t.begin,
                 t.end,
                 dashboard_events.dash_md5,
                 dashboard_events.dash_nodename,
                 dashboard_events.dash_svcname
               from
                 dashboard_events
                 join (
                   select
                     date(date_sub(now(), interval inc-1 day)) as begin,
                     date(date_sub(now(), interval inc-2 day)) as end
                   from
                     u_inc
                   where
                     inc<=10
                   order by inc desc
                 ) t on
                   dashboard_events.dash_begin <= t.end and
                   (dashboard_events.dash_end >= t.begin or dashboard_events.dash_end is null)
                 join dashboard_ref on
                   dashboard_events.dash_md5 = dashboard_ref.dash_md5
               where %(where)s
               group by
                 t.begin,
                 t.end,
                 dashboard_events.dash_md5,
                 dashboard_events.dash_nodename,
                 dashboard_events.dash_svcname
             ) v
             group by v.begin, v.end
    """%dict(where=str(q))
    rows = db.executesql(sql)
    data = []
    for row in rows:
        data.append((row[0], row[1]))
    return data



#############################################################################


class col_dash_entry(HtmlTableColumn):
    def get(self, o):
        dash_dict = self.t.colprops['dash_dict'].get(o)
        dash_fmt = self.t.colprops['dash_fmt'].get(o)
        if dash_dict is None or len(dash_dict) == 0:
            return ""
        try:
            d = json.loads(dash_dict)
            for k in d:
                if isinstance(d[k], str) or isinstance(d[k], unicode):
                    d[k] = d[k].encode('utf8')
            s = T.translate(dash_fmt, d)
        except KeyError:
            s = 'error parsing: %s'%dash_dict
        except json.decoder.JSONDecodeError:
            s = 'error loading JSON: %s'%dash_dict
        except UnicodeEncodeError:
            s = 'error transcoding: %s'%dash_dict
        except TypeError:
            s = 'type error: %s'%dash_dict
        return s

class table_dashboard(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'dash_severity',
                     'dash_links',
                     'dash_type',
                     'dash_svcname',
                     'dash_nodename',
                     'dash_env',
                     'dash_entry',
                     'dash_created',
                     'dash_updated',
                     'dash_md5']
        self.colprops = {
            'dash_links': HtmlTableColumn(
                     title='Links',
                     field='dummy',
                     img='link16',
                     display=True,
                     _class="dash_links",
                    ),
            'dash_created': HtmlTableColumn(
                     title='Begin date',
                     table='dashboard',
                     field='dash_created',
                     img='time16',
                     _class='datetime_no_age',
                     display=True,
                    ),
            'dash_updated': HtmlTableColumn(
                     title='Last update',
                     table='dashboard',
                     field='dash_updated',
                     img='time16',
                     _class='datetime_no_age',
                     display=True,
                    ),
            'dash_severity': HtmlTableColumn(
                     title='Severity',
                     table='dashboard',
                     field='dash_severity',
                     img='alert16',
                     display=True,
                     _class='dash_severity',
                    ),
            'dash_svcname': HtmlTableColumn(
                     title='Service',
                     table='dashboard',
                     field='dash_svcname',
                     img='svc',
                     display=True,
                     _class='svcname',
                    ),
            'dash_nodename': HtmlTableColumn(
                     title='Node',
                     table='dashboard',
                     field='dash_nodename',
                     img='node16',
                     display=True,
                     _class='nodename',
                    ),
            'dash_entry': col_dash_entry(
                     title='Alert',
                     table='dashboard',
                     field='dummy',
                     filter_redirect='dash_dict',
                     img='alert16',
                     display=True,
                     _class='dash_entry',
                    ),
            'dash_env': HtmlTableColumn(
                     title='Env',
                     table='dashboard',
                     field='dash_env',
                     img='svc',
                     display=True,
                     _class='env',
                    ),
            'dash_fmt': HtmlTableColumn(
                     title='Format',
                     table='dashboard',
                     field='dash_fmt',
                     img='alert16',
                     display=False,
                    ),
            'dash_dict': HtmlTableColumn(
                     title='Dictionary',
                     table='dashboard',
                     field='dash_dict',
                     img='alert16',
                     display=False,
                    ),
            'dash_type': HtmlTableColumn(
                     title='Type',
                     table='dashboard',
                     field='dash_type',
                     img='alert16',
                     display=True,
                     _class='alert_type',
                    ),
            'dash_md5': HtmlTableColumn(
                     title='Signature',
                     table='dashboard',
                     field='dash_md5',
                     img='alert16',
                     display=False,
                    ),
            'id': HtmlTableColumn(
                     title='Alert id',
                     table='dashboard',
                     field='id',
                     img='key',
                     display=False,
                    ),
        }
        self.keys = ["dash_nodename", "dash_type", "dash_svcname", "dash_md5"]
        #self.span = ["dash_nodename", "dash_type", "dash_svcname", "dash_md5"]
        self.span = ["id"]
        self.order = ["~dash_severity", "dash_type", "dash_nodename", "dash_svcname"]
        self.colprops['dash_svcname'].t = self
        self.colprops['dash_nodename'].t = self
        self.colprops['dash_links'].t = self
        self.colprops['dash_entry'].t = self
        self.extraline = True
        self.checkboxes = True
        self.checkbox_id_table = 'dashboard'
        self.checkbox_id_col = 'id'
        self.special_filtered_cols = ['dash_entry']
        self.wsable = True
        self.dataable = True
        self.events = ["dashboard_change"]

@auth.requires_login()
def ajax_dashboard_col_values():
    t = table_dashboard('dashboard', 'ajax_dashboard')
    col = request.args[0]
    if t.colprops[col].filter_redirect is None:
        o = db.dashboard[col]
        s = [o]
    else:
        o = db.dashboard[t.colprops[col].filter_redirect]
        s = [db.dashboard.dash_fmt, db.dashboard.dash_dict]
    q = db.dashboard.id > 0
    for f in set(t.cols):
        q = _where(q, 'dashboard', t.filter_parse(f),  f if t.colprops[f].filter_redirect is None else t.colprops[f].filter_redirect)
    q &= _where(None, 'dashboard', domain_perms(), 'dash_svcname')|_where(None, 'dashboard', domain_perms(), 'dash_nodename')
    q = apply_filters(q, db.dashboard.dash_nodename, db.dashboard.dash_svcname)
    t.object_list = db(q).select(*s, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_dashboard():
    t = table_dashboard('dashboard', 'ajax_dashboard')
    o = ~db.dashboard.dash_severity|db.dashboard.dash_type|db.dashboard.dash_nodename|db.dashboard.dash_svcname
    q = db.dashboard.id > 0
    for f in set(t.cols):
        q = _where(q, 'dashboard', t.filter_parse(f), f if t.colprops[f].filter_redirect is None else t.colprops[f].filter_redirect)
    q &= _where(None, 'dashboard', domain_perms(), 'dash_svcname')|_where(None, 'dashboard', domain_perms(), 'dash_nodename')
    q = apply_filters(q, db.dashboard.dash_nodename, db.dashboard.dash_svcname)

    t.csv_q = q
    t.csv_orderby = o

    if len(request.args) == 1 and request.args[0] == 'csv':
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.dashboard.id.count()).first()(db.dashboard.id.count())
        limitby = (t.pager_start,t.pager_end)
        t.object_list = db(q).select(orderby=o, cacheable=True, limitby=limitby)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def index():
    t = table_dashboard('dashboard', 'ajax_dashboard')
    t = DIV(
          t.html(),
          _id='dashboard',
        )
    return dict(table=t)

def index_load():
    return index()["table"]

@auth.requires_login()
def ajax_alert_events():
    session.forget(response)
    limit = datetime.datetime.now() - datetime.timedelta(days=30)
    q = db.dashboard_events.dash_md5 == request.vars.dash_md5
    q &= db.dashboard_events.dash_nodename == request.vars.dash_nodename
    q &= db.dashboard_events.dash_svcname == request.vars.dash_svcname
    q &= db.dashboard_events.dash_begin > limit
    q &= _where(None, 'dashboard_events', domain_perms(), 'dash_svcname')|_where(None, 'dashboard_events', domain_perms(), 'dash_nodename')
    rows = db(q).select(db.dashboard_events.dash_begin,
                        db.dashboard_events.dash_end)

    if len(rows) == 0:
        data_on = [[str(request.vars.dash_created), 1],
                   [str(now), 1],
                   [str(now), 'null']]
    else:
        data_on = []
        last = len(rows)

    for i, row in enumerate(rows):
        data_on += [[str(row.dash_begin), 1]]
        if row.dash_end is None:
            data_on += [[str(now), 1]]
            data_on += [[str(now), 'null']]
        else:
            data_on += [[str(row.dash_end), 1]]
            data_on += [[str(row.dash_end), 'null']]

    data = str([str(data_on).replace("'null'","null"), [[str(now), 1]]]).replace('"','')
    #s = """data_%(rowid)s=%(data)s;$('#%(id)s').empty();avail_plot('%(id)s', data_%(rowid)s);"""%dict(
    #       data=data,
    #       id='plot_%s'%request.vars.rowid,
    #       rowid=request.vars.rowid,
    #     )

    wikipage_name = "alert"
    if request.vars.dash_nodename is not None:
        wikipage_name += "_"+request.vars.dash_nodename
    if request.vars.dash_svcname is not None:
        wikipage_name += "_"+request.vars.dash_svcname
    if request.vars.dash_md5 is not None:
        wikipage_name += "_"+request.vars.dash_md5

    s = """alert_event("%(id)s", 
        {
        "md5name" : "%(md5name)s",
        "nodes": "%(node)s",
        "begin_date":"%(bdate)s",
        "svcname" : "%(svcname)s",
        });"""%dict(
               id='plot_%s'%request.vars.rowid,
               rowid=request.vars.rowid,
               node=request.vars.dash_nodename,
               bdate=request.vars.dash_created,
               md5name=request.vars.dash_md5,
               svcname=request.vars.dash_svcname)

    s += """wiki("%(id)s", {"nodes": "%(node)s"});"""%dict(
               id='wiki_%s'%request.vars.rowid,
               rid=str(request.vars.rowid),
               node=wikipage_name)

    return TABLE(DIV(
             H2(T("Alert timeline")),
             DIV(
               #data,
               _id='plot_%s'%request.vars.rowid,
               #_style='width:300px;',#height:50px',
             ),
             BR(),
             DIV(
               _id='wiki_%s'%request.vars.rowid,
             ),
             SCRIPT(s, _name='%s_to_eval'%request.vars.rowid),
             _style="padding:1em",
           ))

def test_dashboard_events():
    dashboard_events()

#
# alerts tabs
#
class table_dashboard_node(table_dashboard):
    def __init__(self, id=None, func=None, innerhtml=None):
        table_dashboard.__init__(self, id, func, innerhtml)
        self.hide_tools = True
        self.pageable = False
        self.bookmarkable = False
        self.commonalityable = False
        self.linkable = False
        self.checkboxes = True
        self.filterable = False
        self.exportable = False
        self.dbfilterable = False
        self.columnable = False
        self.refreshable = False
        self.wsable = False
        self.dataable = True
        self.child_tables = []

def ajax_dashboard_node():
    tid = request.vars.table_id
    t = table_dashboard_node(tid, 'ajax_dashboard_node')
    q = _where(None, 'dashboard', domain_perms(), 'dash_nodename')
    for f in ['dash_nodename']:
        q = _where(q, 'dashboard', t.filter_parse(f), f)
    if request.args[0] == "data":
        t.object_list = db(q).select(cacheable=True)
        return t.table_lines_data(-1, html=False)

def ajax_dashboard_svc():
    tid = request.vars.table_id
    t = table_dashboard_node(tid, 'ajax_dashboard_svc')
    q = _where(None, 'dashboard', domain_perms(), 'dash_svcname')
    for f in ['dash_svcname']:
        q = _where(q, 'dashboard', t.filter_parse(f), f)
    if request.args[0] == "data":
        t.object_list = db(q).select(cacheable=True)
        return t.table_lines_data(-1, html=False)

@auth.requires_login()
def dashboard_node():
    node = request.args[0]
    tid = 'dashboard_'+node.replace('-', '_').replace('.', '_')
    t = table_dashboard_node(tid, 'ajax_dashboard_node')
    t.colprops['dash_nodename'].force_filter = node

    return DIV(
             t.html(),
             _id=tid,
           )

@auth.requires_login()
def dashboard_svc():
    svcname = request.args[0]
    tid = 'dashboard_'+svcname.replace('-','_').replace('.','_')
    t = table_dashboard_node(tid, 'ajax_dashboard_svc')
    t.colprops['dash_svcname'].force_filter = svcname

    return DIV(
             t.html(),
             _id=tid,
           )


