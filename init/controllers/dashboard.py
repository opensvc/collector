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
    f1 = q_filter(node_field=db.dashboard.dash_nodename)
    f2 = q_filter(svc_field=db.dashboard.dash_svcname)
    q &= (f1|f2)
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
                     'dash_md5',
                     'dash_created',
                     'dash_updated']
        self.colprops = {
            'dash_links': HtmlTableColumn(
                     field='dummy',
                    ),
            'dash_created': HtmlTableColumn(
                     table='dashboard',
                     field='dash_created',
                    ),
            'dash_updated': HtmlTableColumn(
                     table='dashboard',
                     field='dash_updated',
                    ),
            'dash_severity': HtmlTableColumn(
                     table='dashboard',
                     field='dash_severity',
                    ),
            'dash_svcname': HtmlTableColumn(
                     table='dashboard',
                     field='dash_svcname',
                    ),
            'dash_nodename': HtmlTableColumn(
                     table='dashboard',
                     field='dash_nodename',
                    ),
            'dash_entry': HtmlTableColumn(
                     table='dashboard',
                     field='dummy',
                     filter_redirect='dash_dict',
                    ),
            'dash_env': HtmlTableColumn(
                     table='dashboard',
                     field='dash_env',
                    ),
            'dash_fmt': HtmlTableColumn(
                     table='dashboard',
                     field='dash_fmt',
                    ),
            'dash_dict': HtmlTableColumn(
                     table='dashboard',
                     field='dash_dict',
                    ),
            'dash_type': HtmlTableColumn(
                     table='dashboard',
                     field='dash_type',
                    ),
            'dash_md5': HtmlTableColumn(
                     table='dashboard',
                     field='dash_md5',
                    ),
            'id': HtmlTableColumn(
                     table='dashboard',
                     field='id',
                    ),
        }
        self.span = ["id"]
        self.keys = ["dash_nodename", "dash_type", "dash_svcname", "dash_md5"]
        self.order = ["~dash_severity", "dash_type", "dash_nodename", "dash_svcname"]

@auth.requires_login()
def ajax_dashboard_col_values():
    table_id = request.vars.table_id
    t = table_dashboard(table_id, 'ajax_dashboard')
    col = request.args[0]
    if t.colprops[col].filter_redirect is None and col in db.dashboard:
        o = db.dashboard[col]
        s = [o]
    else:
        o = db.dashboard[t.colprops[col].filter_redirect]
        s = [db.dashboard.dash_fmt, db.dashboard.dash_dict]
    q = db.dashboard.id > 0
    for f in set(t.cols):
        q = _where(q, 'dashboard', t.filter_parse(f),  f if t.colprops[f].filter_redirect is None else t.colprops[f].filter_redirect)
    f1 = q_filter(node_field=db.dashboard.dash_nodename)
    f2 = q_filter(svc_field=db.dashboard.dash_svcname)
    q &= (f1|f2)
    q = apply_filters(q, db.dashboard.dash_nodename, db.dashboard.dash_svcname)
    t.object_list = db(q).select(*s, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_dashboard():
    table_id = request.vars.table_id
    t = table_dashboard(table_id, 'ajax_dashboard')
    o = ~db.dashboard.dash_severity|db.dashboard.dash_type|db.dashboard.dash_nodename|db.dashboard.dash_svcname
    q = db.dashboard.id > 0
    for f in set(t.cols):
        q = _where(q, 'dashboard', t.filter_parse(f), f if t.colprops[f].filter_redirect is None else t.colprops[f].filter_redirect)
    f1 = q_filter(node_field=db.dashboard.dash_nodename)
    f2 = q_filter(svc_field=db.dashboard.dash_svcname)
    q &= (f1|f2)
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
    t = SCRIPT(
          """table_dashboard("layout", %s)""" % request_vars_to_table_options(),
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
    f1 = q_filter(node_field=db.dashboard.dash_nodename)
    f2 = q_filter(svc_field=db.dashboard.dash_svcname)
    q &= (f1|f2)
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


