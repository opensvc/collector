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
                      'save_nodename',
                      'save_svcname',
                      'save_name',
                      'save_group',
                      'save_level',
                      'save_size',
                      'save_volume',
                      'save_date',
                      'save_retention']
        self.force_cols = ["id", "os_name"]
        self.keys =  ['id']
        self.span = nodes_cols + [
                      'save_server',
                      'save_app',
                      'save_nodename',
                      'save_svcname']
        self.child_tables = ["charts"]

        self.cols += nodes_cols
        self.colprops = nodes_colprops
        self.colprops.update({
            'id': HtmlTableColumn(
                     title='Id',
                     table='saves',
                     field='id',
                     img='key',
                     display=False,
                    ),
            'save_server': HtmlTableColumn(
                     title='Server',
                     table='saves',
                     field='save_server',
                     img='save16',
                     display=True,
                     _class='nodename_no_os',
                    ),
            'save_id': HtmlTableColumn(
                     title='Id',
                     table='saves',
                     field='save_id',
                     img='save16',
                     display=False,
                    ),
            'save_nodename': HtmlTableColumn(
                     title='Nodename',
                     table='saves',
                     field='save_nodename',
                     img='node16',
                     display=True,
                     _class='nodename',
                    ),
            'save_svcname': HtmlTableColumn(
                     title='Service',
                     table='saves',
                     field='save_svcname',
                     img='save16',
                     display=True,
                     _class='svcname',
                    ),
            'save_app': HtmlTableColumn(
                     title='App',
                     table='saves',
                     field='save_app',
                     img='save16',
                     display=True,
                    ),
            'save_name': HtmlTableColumn(
                     title='Name',
                     table='saves',
                     field='save_name',
                     img='save16',
                     display=True,
                    ),
            'save_group': HtmlTableColumn(
                     title='Group',
                     table='saves',
                     field='save_group',
                     img='save16',
                     display=True,
                    ),
            'save_volume': HtmlTableColumn(
                     title='Volume',
                     table='saves',
                     field='save_volume',
                     img='save16',
                     display=True,
                    ),
            'save_level': HtmlTableColumn(
                     title='Level',
                     table='saves',
                     field='save_level',
                     img='save16',
                     display=True,
                    ),
            'save_size': HtmlTableColumn(
                     title='Size',
                     table='saves',
                     field='save_size',
                     img='save16',
                     display=True,
                     _class='size_b',
                    ),
            'save_date': HtmlTableColumn(
                     title='Date',
                     table='saves',
                     field='save_date',
                     img='time16',
                     display=True,
                     default_filter=">-1d",
                     _class="datetime_no_age",
                    ),
            'save_retention': HtmlTableColumn(
                     title='Retention',
                     table='saves',
                     field='save_retention',
                     img='time16',
                     display=True,
                     _class="datetime_no_age",
                    ),
        })
        self.colprops['save_nodename'].display = True
        self.colprops['save_server'].t = self
        self.colprops['save_nodename'].t = self
        self.colprops['save_svcname'].t = self
        self.extraline = True
        self.checkbox_id_col = 'id'
        self.checkbox_id_table = 'saves'
        self.dataable = True
        self.wsable = True
        self.dbfilterable = True
        self.ajax_col_values = 'ajax_saves_col_values'
        self.events = ["saves_change"]

@auth.requires_login()
def ajax_saves_col_values():
    table_id = request.vars.table_id
    t = table_saves(table_id, 'ajax_saves')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.saves.id > 0
    l = db.nodes.on(db.saves.save_nodename==db.nodes.nodename)
    q = _where(q, 'saves', domain_perms(), 'save_nodename') | _where(q, 'saves', domain_perms(), 'save_svcname')
    q = apply_filters(q, db.saves.save_nodename, db.saves.save_svcname)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, left=l, cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_saves():
    table_id = request.vars.table_id
    t = table_saves(table_id, 'ajax_saves')

    o = ~db.saves.save_date
    o |= db.saves.save_nodename

    q = db.saves.id>0
    l = db.nodes.on(db.saves.save_nodename==db.nodes.nodename)
    q = _where(q, 'saves', domain_perms(), 'save_nodename') | _where(q, 'saves', domain_perms(), 'save_svcname')
    q = apply_filters(q, db.saves.save_nodename, db.saves.save_svcname)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.saves.id.count(), left=l).first()(db.saves.id.count())
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=True, left=l)
        return t.table_lines_data(n, html=False)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        t.csv_left = l
        return t.csv()

    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        t.csv_left = l
        return t.do_commonality()

@auth.requires_login()
def saves():
    t = SCRIPT(
          """$.when(osvc.app_started).then(function(){ view_saves("layout", %s) })""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def saves_load():
    return saves()["table"]

class col_chart(HtmlTableColumn):
    def html(self, o):
       l = []
       if len(o['chart_svc']) > 2:
           l += [DIV(
                      H3(T("Services")),
                      DIV(
                        o['chart_svc'],
                        _id='chart_svc',
                      ),
                      _style="float:left;width:500px",
                    )]
       if len(o['chart_ap']) > 2:
           l += [DIV(
                      H3(T("Applications")),
                      DIV(
                        o['chart_ap'],
                        _id='chart_ap',
                      ),
                      _style="float:left;width:500px",
                    )]
       if len(o['chart_group']) > 2:
           l += [DIV(
                  H3(T("Groups")),
                  DIV(
                    o['chart_group'],
                    _id='chart_group',
                  ),
                  _style="float:left;width:500px",
                )]
       if len(o['chart_server']) > 2:
           l += [DIV(
                  H3(T("Servers")),
                  DIV(
                    o['chart_server'],
                    _id='chart_server',
                  ),
                  _style="float:left;width:500px",
                )]

       l += [DIV(
               _class='spacer',
             )]
       l += [DIV(
               _id='chart_info',
             )]
       return DIV(l)

@auth.requires_login()
def ajax_saves_charts():
    t = table_saves('saves', 'ajax_saves')
    nt = table_saves_charts('charts', 'ajax_saves_charts')

    o = db.saves.id
    q = db.saves.id>0
    q = _where(q, 'saves', domain_perms(), 'save_nodename')
    q = apply_filters(q, db.saves.save_nodename, None)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    nt.setup_pager(-1)
    nt.dbfilterable = False
    nt.filterable = True
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
               saves.save_nodename = nodes.nodename
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
                     if(saves.save_svcname != "", saves.save_svcname, saves.save_nodename) as obj,
                     saves.save_size as size
                   from
                     saves
                     left join nodes on
                     saves.save_nodename = nodes.nodename
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
                   saves.save_nodename = nodes.nodename
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
               save_nodename = nodes.nodename
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
                   saves.save_nodename = nodes.nodename
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
                   saves.save_nodename = nodes.nodename
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

    nt.object_list = [{'chart_svc': json.dumps(h_data_svc),
                       'chart_ap': json.dumps(h_data_app),
                       'chart_group': json.dumps(h_data_group),
                       'chart_server': json.dumps(h_data_server)}]

    if len(request.args) == 1 and request.args[0] == 'line':
        return nt.table_lines_data(-1)

class table_saves_charts(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['chart']
        self.keys = ['chart']
        self.span = ['chart']
        self.colprops.update({
            'chart': col_chart(
                     title='Chart',
                     field='chart',
                     img='spark16',
                     display=True,
                    ),
        })
        for i in self.cols:
            self.colprops[i].t = self
        self.dbfilterable = False
        self.filterable = False
        self.pageable = False
        self.exportable = False
        self.linkable = False
        self.bookmarkable = False
        self.commonalityable = False
        self.refreshable = False
        self.columnable = False
        self.headers = False
        self.highlight = False
        self.on_change = "plot_savedonuts"
        self.parent_tables = ["saves"]

