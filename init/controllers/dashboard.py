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
    f1 = q_filter(node_field=db.dashboard.node_id)
    f2 = q_filter(svc_field=db.dashboard.svc_id)
    q &= (f1|f2)
    q = apply_filters_id(q, db.dashboard.node_id, db.dashboard.svc_id)

    sql = """select
               v.begin,
               count(v.begin)
             from (
               select
                 t.begin,
                 t.end,
                 dashboard_events.dash_md5,
                 dashboard_events.node_id,
                 dashboard_events.svc_id
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
                 dashboard_events.node_id,
                 dashboard_events.svc_id
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
                     'svc_id',
                     'svcname',
                     'node_id',
                     'nodename',
                     'node_app',
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
            'svcname': HtmlTableColumn(
                     table='services',
                     field='svcname',
                    ),
            'svc_id': HtmlTableColumn(
                     table='dashboard',
                     field='svc_id',
                    ),
            'nodename': HtmlTableColumn(
                     table='nodes',
                     field='nodename',
                    ),
            'node_id': HtmlTableColumn(
                     table='dashboard',
                     field='node_id',
                    ),
            'node_app': HtmlTableColumn(
                     table='nodes',
                     field='app',
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
        self.keys = ["node_id", "dash_type", "svc_id", "dash_md5"]
        self.order = ["~dash_severity", "dash_type", "nodename", "svcname"]

@auth.requires_login()
def ajax_dashboard_col_values():
    table_id = request.vars.table_id
    t = table_dashboard(table_id, 'ajax_dashboard')
    col = request.args[0]
    if col is None or t.colprops[col].table is None:
        return
    if t.colprops[col].filter_redirect is None:
        o = db[t.colprops[col].table][t.colprops[col].field]
        s = [o]
    else:
        o = db.dashboard[t.colprops[col].filter_redirect]
        s = [db.dashboard.dash_fmt, db.dashboard.dash_dict]
    q = db.dashboard.id > 0
    l1 = db.nodes.on(db.dashboard.node_id==db.nodes.node_id)
    l2 = db.services.on(db.dashboard.svc_id==db.services.svc_id)
    for f in set(t.cols):
        q = _where(q, t.colprops[f].table, t.filter_parse(f),  f if t.colprops[f].filter_redirect is None else t.colprops[f].filter_redirect)
    f1 = q_filter(node_field=db.dashboard.node_id)
    f2 = q_filter(svc_field=db.dashboard.svc_id)
    q &= (f1|f2)
    q = apply_filters_id(q, db.dashboard.node_id, db.dashboard.svc_id)
    t.object_list = db(q).select(*s, orderby=o, left=(l1,l2))
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_dashboard():
    table_id = request.vars.table_id
    t = table_dashboard(table_id, 'ajax_dashboard')
    o = ~db.dashboard.dash_severity|db.dashboard.dash_type|db.nodes.nodename|db.services.svcname
    o = t.get_orderby(default=o)
    q = db.dashboard.id > 0
    l1 = db.nodes.on(db.dashboard.node_id==db.nodes.node_id)
    l2 = db.services.on(db.dashboard.svc_id==db.services.svc_id)
    for f in set(t.cols):
        q = _where(q, t.colprops[f].table, t.filter_parse(f), t.colprops[f].field if t.colprops[f].filter_redirect is None else t.colprops[f].filter_redirect)
    f1 = q_filter(node_field=db.dashboard.node_id)
    f2 = q_filter(svc_field=db.dashboard.svc_id)
    q &= (f1|f2)
    q = apply_filters_id(q, db.dashboard.node_id, db.dashboard.svc_id)

    t.csv_q = q
    t.csv_orderby = o
    t.csv_left = (l1,l2)

    if len(request.args) == 1 and request.args[0] == 'csv':
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.dashboard.id.count()).first()(db.dashboard.id.count())
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, cacheable=True, limitby=limitby, left=(l1,l2))
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def index():
    t = SCRIPT(
          """table_dashboard("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def index_load():
    return index()["table"]

def test_dashboard_events():
    dashboard_events()


