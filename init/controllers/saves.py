def beautify_size_b(d):
       try:
          d = int(d)
       except:
          return '-'
       if d < 0:
           neg = True
           d = -d
       else:
           neg = False
       if d < 1024:
           v = 1.0 * d
           unit = 'B'
       elif d < 1048576:
           v = 1.0 * d / 1024
           unit = 'KB'
       elif d < 1073741824:
           v = 1.0 * d / 1048576
           unit = 'MB'
       elif d < 1099511627776:
           v = 1.0 * d / 1073741824
           unit = 'GB'
       else:
           v = 1.0 * d / 1099511627776
           unit = 'TB'
       if v >= 100:
           fmt = "%d"
       elif v >= 10:
           fmt = "%.1f"
       else:
           fmt = "%.2f"
       fmt = fmt + " %s"
       if neg:
           v = -v
       return fmt%(v, unit)

class table_saves(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols =  ['id',
                      'save_server',
                      'save_id',
                      'save_app',
                      'node_id',
                      'nodename',
                      'svc_id',
                      'svcname',
                      'save_name',
                      'save_group',
                      'save_level',
                      'save_size',
                      'save_volume',
                      'save_date',
                      'save_retention']
        self.child_tables = ["charts"]

        self.cols += nodes_cols
        self.colprops = nodes_colprops
        self.colprops.update({
            'id': HtmlTableColumn(
                     table='saves',
                     field='id',
                    ),
            'save_server': HtmlTableColumn(
                     table='saves',
                     field='save_server',
                    ),
            'save_id': HtmlTableColumn(
                     table='saves',
                     field='save_id',
                    ),
            'node_id': HtmlTableColumn(
                     table='saves',
                     field='node_id',
                    ),
            'svc_id': HtmlTableColumn(
                     table='saves',
                     field='svc_id',
                    ),
            'nodename': HtmlTableColumn(
                     table='nodes',
                     field='nodename',
                    ),
            'svcname': HtmlTableColumn(
                     table='services',
                     field='svcname',
                    ),
            'save_app': HtmlTableColumn(
                     table='saves',
                     field='save_app',
                    ),
            'save_name': HtmlTableColumn(
                     table='saves',
                     field='save_name',
                    ),
            'save_group': HtmlTableColumn(
                     table='saves',
                     field='save_group',
                    ),
            'save_volume': HtmlTableColumn(
                     table='saves',
                     field='save_volume',
                    ),
            'save_level': HtmlTableColumn(
                     table='saves',
                     field='save_level',
                    ),
            'save_size': HtmlTableColumn(
                     table='saves',
                     field='save_size',
                    ),
            'save_date': HtmlTableColumn(
                     table='saves',
                     field='save_date',
                    ),
            'save_retention': HtmlTableColumn(
                     table='saves',
                     field='save_retention',
                    ),
        })
        self.ajax_col_values = 'ajax_saves_col_values'

@auth.requires_login()
def ajax_saves_col_values():
    table_id = request.vars.table_id
    t = table_saves(table_id, 'ajax_saves')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = q_filter(app_field=db.saves.save_app)
    l1 = db.nodes.on(db.saves.node_id==db.nodes.node_id)
    l2 = db.services.on(db.saves.svc_id==db.services.svc_id)
    q = apply_filters_id(q, db.saves.node_id, db.saves.svc_id)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, left=(l1,l2), cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_saves():
    table_id = request.vars.table_id
    t = table_saves(table_id, 'ajax_saves')

    o = ~db.saves.save_date
    o |= db.nodes.nodename

    q = q_filter(app_field=db.saves.save_app)
    l1 = db.nodes.on(db.saves.node_id==db.nodes.node_id)
    l2 = db.services.on(db.saves.svc_id==db.services.svc_id)
    q = apply_filters_id(q, db.saves.node_id, db.saves.svc_id)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.saves.id.count(), left=(l1,l2)).first()(db.saves.id.count())
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=True, left=(l1,l2))
        return t.table_lines_data(n, html=False)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        t.csv_left = (l1,l2)
        return t.csv()

    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        t.csv_left = (l1,l2)
        return t.do_commonality()

@auth.requires_login()
def saves():
    t = SCRIPT(
          """view_saves("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def saves_load():
    return saves()["table"]

@auth.requires_login()
def ajax_saves_charts():
    t = table_saves('saves', 'ajax_saves')
    nt = table_saves_charts('charts', 'ajax_saves_charts')

    o = db.saves.id
    q = q_filter(app_field=db.saves.save_app)
    q = apply_filters_id(q, node_field=db.saves.node_id)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    nt.setup_pager(-1)
    nt.additional_inputs = t.ajax_inputs()

    h_data_svc = ""
    h_data_app = ""
    h_data_server = ""
    h_data_group = ""

    sql = """select
               count(distinct(saves.save_app))
             from
               saves
               left join nodes on
               saves.node_id = nodes.node_id
             where
               %(q)s
          """%dict(q=q)
    n_app = db.executesql(sql)[0][0]

    def pie_data_svc(q):
        sql = """select
                   t.obj,
                   sum(t.size)
                 from (
                   select
                     if(saves.svc_id != "", saves.svc_id, saves.node_id) as obj,
                     saves.save_size as size
                   from
                     saves
                     left join nodes on
                     saves.node_id = nodes.node_id
                   where
                     %(q)s
                 ) t
                 group by t.obj
                 """%dict(q=q)
        rows = db.executesql(sql)
        return rows

    def data_total(data):
        total = 0
        for l in data:
            total += l[1]
        return total

    if n_app == 1:
        data_svc = []
        rows = pie_data_svc(q)
        for row in rows:
            if row[0] is None or row[0] == "":
                label = 'unknown'
            else:
		try:
                    label = str(row[0])
		except:
                    label = row[0]
            try:
                size = int(row[1])
            except:
                continue
            data_svc += [[label +' (%s)'%beautify_size_b(size), size]]

        data_svc.sort(lambda x, y: cmp(y[1], x[1]))
        if len(data_svc) == 0:
            data_svc = [["", 0]]

        total = data_total(rows)
        h_data_svc = {
          'total': int(total//1024//1024),
          'data': [data_svc],
        }

    def pie_data_app(q):
        sql = """select
                   saves.save_app,
                   sum(saves.save_size)
                 from
                   saves
                   left join nodes on
                   saves.node_id = nodes.node_id
                 where
                   %(q)s
                 group by saves.save_app
                 """%dict(q=q)
        rows = db.executesql(sql)
        return rows

    if n_app > 1:
        data_app = []
        rows = pie_data_app(q)
        for row in rows:
            if row[0] is None or row[0] == "":
                label = 'unknown'
            else:
		try:
                    label = str(row[0])
		except:
                    label = row[0]
            try:
                size = int(row[1])
            except:
                continue
            data_app += [[label +' (%s)'%beautify_size_b(size), size]]

        data_app.sort(lambda x, y: cmp(y[1], x[1]))
        if len(data_app) == 0:
            data_app = [["", 0]]

        total = data_total(rows)
        h_data_app = {
          'total': int(total//1024//1024),
          'data': [data_app],
        }


    sql = """select distinct(saves.save_server) from
               saves left join nodes on
               saves.node_id = nodes.node_id
             where
               %(q)s"""%dict(q=q)
    n_servers = len(db.executesql(sql))

    if n_servers == 1:
        sql = """select
                   saves.save_group,
                   sum(saves.save_size)
                 from
                   saves
                   left join nodes on
                   saves.node_id = nodes.node_id
                 where
                   %(q)s
                 group by saves.save_group
                 """%dict(q=q)
        rows = db.executesql(sql)

        data_group = []
        for row in rows:
            if row[0] is None or row[0] == "":
                label = 'unknown'
            else:
                label = row[0]
            try:
                size = int(row[1])
            except:
                continue
            data_group += [[str(label) +' (%s)'%beautify_size_b(size), size]]

        data_group.sort(lambda x, y: cmp(y[1], x[1]))
        if len(data_group) == 0:
            data_group = [["", 0]]

        total = data_total(rows)
        h_data_group = {
          'total': int(total//1024//1024),
          'data': [data_group],
        }

    if n_servers > 1:
        sql = """select
                   saves.save_server,
                   sum(saves.save_size)
                 from
                   saves
                   left join nodes on
                   saves.node_id = nodes.node_id
                 where
                   %(q)s
                 group by saves.save_server
                 """%dict(q=q)
        rows = db.executesql(sql)

        data_server = []
        for row in rows:
            if row[0] is None or row[0] == "":
                label = 'unknown'
            else:
                label = row[0]
            try:
                size = int(row[1])
            except:
                continue
            data_server += [[str(label) +' (%s)'%beautify_size_b(size), size]]

        data_server.sort(lambda x, y: cmp(y[1], x[1]))
        if len(data_server) == 0:
            data_server = [["", 0]]

        total = data_total(rows)
        h_data_server = {
          'total': int(total//1024//1024),
          'data': [data_server],
        }

    nt.object_list = [{
      'chart': json.dumps({
        'chart_svc': h_data_svc,
        'chart_ap': h_data_app,
        'chart_group': h_data_group,
        'chart_server': h_data_server
      })
    }]


    if len(request.args) == 1 and request.args[0] == 'data':
        return nt.table_lines_data(-1)

class table_saves_charts(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['chart']
        self.colprops.update({
            'chart': HtmlTableColumn(
                     field='chart',
                    ),
        })

