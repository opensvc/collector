def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget(response)
    return service()

def refresh_b_disk_app():
    task_refresh_b_disk_app()

#
# quotas
#
class table_quota(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'array_name',
                     'array_model',
                     'dg_name',
                     'dg_size',
                     'dg_reserved',
                     'dg_reservable',
                     'dg_used',
                     'dg_free',
                     'app',
                     'quota',
                     'quota_used']
        self.keys = ['array_name',
                     'dg_name',
                     'app']
        self.span = ['array_name',
                     'dg_name',
                     'app']
        self.colprops.update({
            'id': HtmlTableColumn(
                     title='Id',
                     table='v_disk_quota',
                     field='id',
                     img='key',
                    ),
            'array_name': HtmlTableColumn(
                     title='Array',
                     #table='stor_array',
                     table='v_disk_quota',
                     field='array_name',
                     img='hd16',
                     display=True,
                     _class="disk_array",
                    ),
            'array_model': HtmlTableColumn(
                     title='Array Model',
                     #table='stor_array',
                     table='v_disk_quota',
                     field='array_model',
                     img='hd16',
                     display=True,
                     _dataclass="bluer",
                    ),
            'array_id': HtmlTableColumn(
                     title='Array Id',
                     #table='stor_array',
                     table='v_disk_quota',
                     field='array_id',
                     img='hd16',
                     display=True,
                    ),
            'dg_name': HtmlTableColumn(
                     title='Array Disk Group',
                     #table='stor_array_dg',
                     table='v_disk_quota',
                     field='dg_name',
                     img='hd16',
                     display=True,
                     _class="disk_array_dg",
                    ),
            'dg_free': HtmlTableColumn(
                     title='Free',
                     #table='stor_array_dg',
                     table='v_disk_quota',
                     field='dg_free',
                     img='hd16',
                     display=True,
                     _class="numeric size_mb",
                    ),
            'dg_used': HtmlTableColumn(
                     title='Used',
                     #table='stor_array_dg',
                     table='v_disk_quota',
                     field='dg_used',
                     img='hd16',
                     display=True,
                     _class="numeric size_mb",
                    ),
            'dg_reservable': HtmlTableColumn(
                     title='Reservable',
                     #table='stor_array_dg',
                     table='v_disk_quota',
                     field='dg_reservable',
                     img='hd16',
                     display=True,
                     _class="numeric size_mb",
                    ),
            'dg_reserved': HtmlTableColumn(
                     title='Reserved',
                     #table='stor_array_dg',
                     table='v_disk_quota',
                     field='dg_reserved',
                     img='hd16',
                     display=True,
                     _class="numeric size_mb",
                    ),
            'dg_size': HtmlTableColumn(
                     title='Size',
                     #table='stor_array_dg',
                     table='v_disk_quota',
                     field='dg_size',
                     img='hd16',
                     display=True,
                     _class="numeric size_mb",
                    ),
            'dg_id': HtmlTableColumn(
                     title='Array Disk Group Id',
                     #table='stor_array_dg',
                     table='v_disk_quota',
                     field='dg_id',
                     img='hd16',
                     display=True,
                    ),
            'app': HtmlTableColumn(
                     title='App',
                     #table='apps',
                     table='v_disk_quota',
                     field='app',
                     img='svc',
                     display=True,
                     _class="app",
                    ),
            'app_id': HtmlTableColumn(
                     title='App Id',
                     #table='apps',
                     table='v_disk_quota',
                     field='app_id',
                     img='svc',
                     display=True,
                    ),
            'quota': HtmlTableColumn(
                     title='Quota',
                     #table='stor_array_dg_quota',
                     table='v_disk_quota',
                     field='quota',
                     img='hd16',
                     display=True,
                     _class="quota numeric size_mb",
                    ),
            'quota_used': HtmlTableColumn(
                     title='Quota Used',
                     #table='stor_array_dg_quota',
                     table='v_disk_quota',
                     field='quota_used',
                     img='hd16',
                     display=True,
                     _class="numeric size_mb",
                    ),
        })
        for i in self.cols:
            self.colprops[i].t = self
        self.extraline = True
        self.checkboxes = True
        self.dbfilterable = False
        self.ajax_col_values = 'ajax_quota_col_values'
        self.dataable = True
        self.force_cols = ["id"]
        self.keys = ["id"]
        self.events = ["stor_array_dg_quota_change"]

def update_dg_reserved():
    sql = """select dg_id, sum(v_disk_quota.quota)
             from v_disk_quota
             group by dg_id
          """
    rows = db.executesql(sql)
    for row in rows:
        if row[0] is None or row[1] is None:
           continue
        sql = """update stor_array_dg set dg_reserved=%(reserved)s
                 where id=%(dg_id)s
              """%dict(reserved=row[1], dg_id=row[0])
        db.executesql(sql)
    db.commit()

@auth.requires_login()
def ajax_quota_col_values():
    table_id = request.vars.table_id
    t = table_quota(table_id, 'ajax_quota')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.v_disk_quota.id>0
    q = _where(q, 'v_disk_quota', domain_perms(), 'array_name')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_quota():
    table_id = request.vars.table_id
    t = table_quota(table_id, 'ajax_quota')

    update_dg_reserved()

    o = db.v_disk_quota.array_name | db.v_disk_quota.dg_name
    q = db.v_disk_quota.array_id > 0
    q = _where(q, 'v_disk_quota', domain_perms(), 'array_name')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        t.setup_pager(n)
        limitby = (t.pager_start, t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def quota():
    t = SCRIPT(
          """table_quota("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def quota_load():
    return quota()["table"]


#
# disks
#
class table_disks(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.events = ["disks_change"]
        self.cols = ['disk_id',
                     'disk_region',
                     'disk_vendor',
                     'disk_model',
                     'app',
                     'disk_nodename',
                     'disk_svcname',
                     'disk_dg',
                     'svcdisk_updated',
                     'disk_used',
                     'disk_size',
                     'disk_alloc',
                     'disk_name',
                     'disk_devid',
                     'disk_raid',
                     'disk_group',
                     'disk_arrayid',
                     'disk_level',
                     'array_model',
                     'disk_created',
                     'disk_updated',
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
                     'power_breaker2']
        self.force_cols = ["os_name"]
        self.colprops.update(disk_app_colprops)
        import copy
        _nodes_colprops = copy.copy(nodes_colprops)
        for i in _nodes_colprops:
            _nodes_colprops[i].table = 'nodes'
        self.colprops.update(_nodes_colprops)
        for i in self.cols:
            self.colprops[i].t = self
        self.extraline = True
        self.checkboxes = True
        self.checkbox_id_col = 'svcdisk_id'
        self.checkbox_id_table = 'b_disk_app'
        self.dbfilterable = True
        self.wsable = True
        self.dataable = True
        self.ajax_col_values = 'ajax_disks_col_values'
        self.keys = ['disk_id', 'disk_region', 'disk_nodename']
        self.span = ['disk_id', 'disk_size', 'disk_alloc', 'disk_arrayid',
                     'disk_devid', 'disk_name', 'disk_raid', 'disk_group', 'array_model']
        self.child_tables = ["charts"]

@auth.requires_login()
def ajax_disks_col_values():
    t = table_disks('disks', 'ajax_disks')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.b_disk_app.id>0
    q |= db.stor_array.id<0
    l1 = db.stor_array.on(db.b_disk_app.disk_arrayid == db.stor_array.array_name)
    l2 = db.nodes.on(db.b_disk_app.disk_arrayid==db.nodes.nodename)
    q = _where(q, 'b_disk_app', domain_perms(), 'disk_nodename')
    q = apply_filters(q, db.b_disk_app.disk_nodename, None)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, cacheable=True, orderby=o, left=(l1,l2))
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_disks():
    t = table_disks('disks', 'ajax_disks')

    o = db.b_disk_app.disk_id | db.b_disk_app.disk_svcname | db.b_disk_app.disk_nodename
    q = db.b_disk_app.id>0
    q |= db.stor_array.id<0
    l1 = db.stor_array.on(db.b_disk_app.disk_arrayid == db.stor_array.array_name)
    l2 = db.nodes.on(db.b_disk_app.disk_arrayid==db.nodes.nodename)
    q = _where(q, 'b_disk_app', domain_perms(), 'disk_nodename')
    q = apply_filters(q, db.b_disk_app.disk_nodename, None)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), t.colprops[f].field)

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.b_disk_app.id.count(), cacheable=True, left=(l1,l2)).first()._extra[db.b_disk_app.id.count()]
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=False, left=(l1,l2))
        return t.table_lines_data(n, html=False)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        t.csv_left = (l1,l2)
        t.csv_limit = 60000
        return t.csv()

    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        t.csv_orderby = o
        t.csv_left = (l1,l2)
        return t.do_commonality()

@auth.requires_login()
def disks():
    t = table_disks('disks', 'ajax_disks')
    u = table_disk_charts('charts', 'ajax_disk_charts')
    d = DIV(
          DIV(
            T("Statistics"),
             _style="text-align:left;font-size:120%;background-color:#e0e1cd",
             _class="icon down16 clickable",
             _onclick="""
               if (!$("#charts").is(":visible")) {
                 $(this).addClass("down16");
                 $(this).removeClass("right16");
                 $("#charts").show();
               } else {
                 $(this).addClass("right16");
                 $(this).removeClass("down16");
                 $("#charts").hide();
               }"""
          ),
          DIV(
            u.html(),
            _id="charts",
          ),
          DIV(
            t.html(),
            _id='disks',
          ),
        )
    return dict(table=d)

def disks_load():
    return disks()["table"]


#
# charts table
#
class table_disk_charts(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['chart']
        self.keys = ['chart']
        self.span = ['chart']
        self.colprops.update({
            'chart': HtmlTableColumn(
                     title='Chart',
                     field='chart',
                     img='spark16',
                     display=True,
                     _class="disks_charts",
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
        self.dataable = True
        self.parent_tables = ["disks"]

@auth.requires_login()
def ajax_disk_charts():
    nt = table_disk_charts('charts', 'ajax_disk_charts')
    t = table_disks('disks', 'ajax_disks')
    volatile_filters = request.vars.volatile_filters
    request.vars.volatile_filters = None

    o = db.b_disk_app.disk_id
    q = db.b_disk_app.id>0
    q = _where(q, 'b_disk_app', domain_perms(), 'disk_nodename')
    q = apply_filters(q, db.b_disk_app.disk_nodename, None)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    request.vars.volatile_filters = volatile_filters

    nt.setup_pager(-1)
    nt.dbfilterable = False
    nt.filterable = True
    nt.additional_inputs = t.ajax_inputs()

    h_data_svc = ""
    h_data_app = ""
    h_data_dg = ""
    h_data_array = ""

    sql = """  select
                 count(distinct(b_disk_app.app)),
                 max(b_disk_app.disk_level)
               from
                 b_disk_app
               left join stor_array on b_disk_app.disk_arrayid=stor_array.array_name
               left join nodes on b_disk_app.disk_arrayid=nodes.nodename
               where
                 %(q)s
           """%dict(q=q)
    n_app = db.executesql(sql)[0][0]
    max_level = db.executesql(sql)[0][1]

    if max_level is None:
        if len(request.args) == 1 and request.args[0] == 'line':
            nt.object_list = [{'chart_svc': json.dumps([]),
                               'chart_ap': json.dumps([]),
                               'chart_dg': json.dumps([]),
                               'chart_ar': json.dumps([])}]
            return nt.table_lines_data(-1)
        return

        return ''

    levels = range(0, max_level+1)

    def pie_data_svc(q, level=0):
        sql = """
               select
                 t.obj,
                 sum(t.size) size,
                 sum(t.alloc) alloc
               from
                 (
                 select
                   v.obj obj,
                   sum(if(v.disk_used is not NULL and v.disk_used>0, v.disk_used, v.disk_size)) size,
                   max(if(v.disk_alloc is not NULL, v.disk_alloc, v.disk_size)) alloc
                 from
                   (
                   select
                     u.disk_id,
                     u.obj,
                     max(u.disk_used) as disk_used,
                     u.disk_size,
                     u.disk_alloc
                   from
                   (
                     select
                       b_disk_app.disk_id,
                       b_disk_app.disk_region,
                       b_disk_app.disk_svcname as obj,
                       b_disk_app.disk_used as disk_used,
                       b_disk_app.disk_size,
                       b_disk_app.disk_alloc
                     from
                       b_disk_app
                     left join stor_array on b_disk_app.disk_arrayid=stor_array.array_name
                     left join nodes on b_disk_app.disk_arrayid=nodes.nodename
                     where %(q)s
                     and b_disk_app.disk_level=%(level)d
                     and b_disk_app.disk_svcname != ""
                     union all
                     select
                       b_disk_app.disk_id,
                       b_disk_app.disk_region,
                       b_disk_app.disk_nodename as obj,
                       b_disk_app.disk_used as disk_used,
                       b_disk_app.disk_size,
                       b_disk_app.disk_alloc
                     from
                       b_disk_app
                     left join stor_array on b_disk_app.disk_arrayid=stor_array.array_name
                     left join nodes on b_disk_app.disk_arrayid=nodes.nodename
                     where %(q)s
                     and b_disk_app.disk_level=%(level)d
                     and (b_disk_app.disk_svcname = "" or b_disk_app.disk_svcname is NULL)
                   ) u
                   group by u.disk_id, u.disk_region
                 ) v
                 group by v.disk_id
               ) t
               group by t.obj
               order by t.obj, size desc
                 """%dict(q=q, level=level)
        rows = db.executesql(sql)
        return rows

    def data_total(data):
        total = 0
        backend_total = 0
        for l in data:
            total += l[1]
            backend_total += l[2]
        return int(total), int(backend_total)

    if n_app == 1:
        data_svc = []
        for level in levels:
            _data_svc = []
            rows = pie_data_svc(q, level)
            for row in rows:
                if row[0] is None:
                    label = 'unknown'
                else:
                    label = row[0]
                try:
                    size = int(row[1])
                except:
                    continue
                _data_svc += [[label +' (%s)'%beautify_size_mb(size), size]]

            _data_svc.sort(lambda x, y: cmp(y[1], x[1]))
            if len(_data_svc) == 0:
                _data_svc = [["", 0]]
            if level == 0:
                total, backend_total = data_total(rows)
            else:
                diff = total - data_total(rows)[0]
                if diff > 0:
                    _data_svc += [["n/a " +' (%s)'%beautify_size_mb(diff), diff]]
            data_svc.append(_data_svc)
        h_data_svc = {
          'total': total,
          'backend_total': backend_total,
          'data': data_svc,
        }

    def pie_data_app(q, level=0):
        sql = """
               select
                 t.app,
                 sum(t.size) size,
                 sum(t.alloc) alloc
               from
                 (
                 select
                   v.app app,
                   sum(if(v.disk_used is not NULL and v.disk_used>0, v.disk_used, v.disk_size)) size,
                   max(if(v.disk_alloc is not NULL, v.disk_alloc, v.disk_size)) alloc
                 from
                   (
                   select
                     u.disk_id,
                     u.app,
                     max(u.disk_used) as disk_used,
                     u.disk_size,
                     u.disk_alloc
                   from
                   (
                     select
                       b_disk_app.disk_id,
                       b_disk_app.disk_region,
                       b_disk_app.app as app,
                       b_disk_app.disk_used as disk_used,
                       b_disk_app.disk_size,
                       b_disk_app.disk_alloc
                     from
                       b_disk_app
                     left join stor_array on b_disk_app.disk_arrayid=stor_array.array_name
                     left join nodes on b_disk_app.disk_arrayid=nodes.nodename
                     where %(q)s
                     and b_disk_app.disk_level=%(level)d
                     and b_disk_app.disk_svcname != ""
                     union all
                     select
                       b_disk_app.disk_id,
                       b_disk_app.disk_region,
                       b_disk_app.app as app,
                       b_disk_app.disk_used as disk_used,
                       b_disk_app.disk_size,
                       b_disk_app.disk_alloc
                     from
                       b_disk_app
                     left join stor_array on b_disk_app.disk_arrayid=stor_array.array_name
                     left join nodes on b_disk_app.disk_arrayid=nodes.nodename
                     where %(q)s
                     and b_disk_app.disk_level=%(level)d
                     and (b_disk_app.disk_svcname = "" or b_disk_app.disk_svcname is NULL)
                   ) u
                   group by u.disk_id, u.disk_region
                 ) v
                 group by v.disk_id
               ) t
               group by t.app
               order by t.app, size desc
                 """%dict(q=q, level=level)
        rows = db.executesql(sql)
        return rows

    if n_app > 1:
        data_app = []
        for level in levels:
            rows = pie_data_app(q, level)
            _data_app = []
            for row in rows:
                if row[0] is None:
                    label = 'unknown'
                else:
                    label = row[0]
                try:
                    size = int(row[1])
                except:
                    continue
                _data_app += [[label +' (%s)'%beautify_size_mb(size), size]]

            _data_app.sort(lambda x, y: cmp(y[1], x[1]))
            if len(_data_app) == 0:
                _data_app = [["", 0]]
            if level == 0:
                total, backend_total = data_total(rows)
            else:
                diff = total - data_total(rows)[0]
                if diff > 0:
                    _data_app += [["n/a " +' (%s)'%beautify_size_mb(diff), diff]]
            data_app.append(_data_app)
        h_data_app = {
          'total': total,
          'backend_total': backend_total,
          'data': data_app,
        }


    sql = """select count(distinct b_disk_app.disk_arrayid)
             from
                 b_disk_app
               left join stor_array on b_disk_app.disk_arrayid=stor_array.array_name
               left join nodes on b_disk_app.disk_arrayid=nodes.nodename
               where
                 %(q)s
          """%dict(q=q)
    n_arrays = db.executesql(sql)[0][0]

    sql = """select count(distinct b_disk_app.disk_group)
             from
                 b_disk_app
               left join stor_array on b_disk_app.disk_arrayid=stor_array.array_name
               left join nodes on b_disk_app.disk_arrayid=nodes.nodename
               where
                 %(q)s
          """%dict(q=q)
    n_dg = db.executesql(sql)[0][0]

    if n_arrays == 1 and n_dg > 1:
        sql = """select
                   t.disk_arrayid,
                   sum(if(t.disk_used is not NULL and t.disk_used>0, t.disk_used, t.disk_size)) size,
                   sum(if(t.disk_alloc is not NULL, t.disk_alloc, t.disk_size)) alloc,
                   t.disk_group
                 from (
                   select
                     sum(u.disk_used) as disk_used,
                     u.disk_size,
                     u.disk_alloc,
                     u.disk_arrayid,
                     u.disk_group
                   from
                   (
                     select
                       b_disk_app.disk_id,
                       max(b_disk_app.disk_used) as disk_used,
                       b_disk_app.disk_size,
                       b_disk_app.disk_alloc,
                       b_disk_app.disk_arrayid,
                       b_disk_app.disk_group
                     from
                       b_disk_app
                     left join stor_array on b_disk_app.disk_arrayid=stor_array.array_name
                     left join nodes on b_disk_app.disk_arrayid=nodes.nodename
                     where %(q)s
                     group by b_disk_app.disk_id, b_disk_app.disk_region
                   ) u
                   group by u.disk_id
                 ) t
                 group by t.disk_arrayid, t.disk_group
                 order by size desc, t.disk_arrayid, t.disk_group"""%dict(q=q)
        rows = db.executesql(sql)

        data_dg = []
        for row in rows:
            if row[3] is None:
                dg = ''
            else:
                dg = ' '.join((row[0],row[3]))

            label = dg
            try:
                size = int(row[1])
            except:
                continue
            data_dg += [[label +' (%s)'%beautify_size_mb(size), size]]
        total, backend_total = data_total(rows)
        data_dg.sort(lambda x, y: cmp(y[1], x[1]))
        data_dg = [data_dg]
        h_data_dg = {
          'total': total,
          'backend_total': backend_total,
          'data': data_dg,
        }


    def pie_data_array(q, level=0):
        sql = """select
                   t.disk_arrayid,
                   sum(if(t.disk_used is not NULL and t.disk_used>0, t.disk_used, t.disk_size)) size,
                   sum(if(t.disk_alloc is not NULL, t.disk_alloc, t.disk_size)) alloc
                 from (
                   select
                     sum(u.disk_used) as disk_used,
                     u.disk_size,
                     u.disk_alloc,
                     u.disk_arrayid
                   from
                   (
                     select
                       b_disk_app.disk_id,
                       max(b_disk_app.disk_used) as disk_used,
                       b_disk_app.disk_size,
                       b_disk_app.disk_alloc,
                       b_disk_app.disk_arrayid
                     from
                       b_disk_app
                     left join stor_array on b_disk_app.disk_arrayid=stor_array.array_name
                     left join nodes on b_disk_app.disk_arrayid=nodes.nodename
                     where %(q)s
                     and b_disk_app.disk_level=%(level)d
                     group by b_disk_app.disk_id, b_disk_app.disk_region
                   ) u
                   group by u.disk_id
                 ) t
                 group by t.disk_arrayid
                 order by size desc, t.disk_arrayid"""%dict(q=q, level=level)
        rows = db.executesql(sql)
        return rows

    if n_arrays > 1:
        data_array = []
        for level in levels:
            rows = pie_data_array(q, level)
            _data_array = []
            for row in rows:
                if row[0] is None:
                    array = ''
                else:
                    array = row[0]
                label = array
                try:
                    size = int(row[1])
                except:
                    continue
                _data_array += [[label +' (%s)'%beautify_size_mb(size), size]]
            _data_array.sort(lambda x, y: cmp(y[1], x[1]))
            if len(_data_array) == 0:
                _data_array = [["", 0]]
            if level == 0:
                total, backend_total = data_total(rows)
            else:
                diff = total - data_total(rows)[0]
                if diff > 0:
                    _data_array += [["n/a " +' (%s)'%beautify_size_mb(diff), diff]]
            data_array.append(_data_array)
        h_data_array = {
          'total': total,
          'backend_total': backend_total,
          'data': data_array,
        }


    nt.object_list = [{
      'chart': json.dumps({
        'chart_svc': h_data_svc,
        'chart_ap': h_data_app,
        'chart_dg': h_data_dg,
        'chart_ar': h_data_array
      })
    }]

    if len(request.args) == 1 and request.args[0] == 'data':
        return nt.table_lines_data(-1)


#
# charts in tabs
#
@auth.requires_login()
def ajax_array_dg():
    session.forget(response)
    array_name = request.vars.array
    dg_name = request.vars.dg
    row_id = request.vars.rowid
    id = 'chart_'+array_name.replace(" ", "").replace("-", "")+'_'+dg_name.replace(" ", "")
    d = DIV(
          H3(T("Array disk group usage history")),
          DIV(
            _id=id,
          ),
          SCRIPT(
           "stats_disk_array('%(url)s', '%(id)s');"%dict(
                  id=id,
                  url=URL(r=request,
                          f='call/json/json_disk_array_dg',
                          vars={'array_name': array_name,
                                'dg_name': dg_name},
                      )
                ),
            _name='%s_to_eval'%row_id,
          ),
          _style="float:left;width:500px",
        )
    return d

@auth.requires_login()
def ajax_array():
    session.forget(response)
    array_name = request.vars.array
    row_id = request.vars.rowid
    id = 'chart_'+array_name.replace(" ", "").replace("-", "")
    d = DIV(
          H3(T("Array usage history")),
          DIV(
            _id=id,
          ),
          SCRIPT(
           "stats_disk_array('%(url)s', '%(id)s');"%dict(
                  id=id,
                  url=URL(r=request,
                          f='call/json/json_disk_array',
                          vars={'array_name': array_name},
                      )
                ),
            _name='%s_to_eval'%row_id,
          ),
          _style="float:left;width:500px",
        )
    return d

@auth.requires_login()
def ajax_app():
    session.forget(response)
    app_id = request.vars.app_id
    dg_id = request.vars.dg_id
    row_id = request.vars.rowid
    id = row_id + '_chart'
    d = DIV(
        DIV(
          H3(T("Application usage history")),
          DIV(
            _id=id+'_dg',
          ),
          _style="float:left;width:500px",
        ),
        DIV(
          H3(T("Application usage history (all disk groups)")),
          DIV(
            _id=id,
          ),
          _style="float:left;width:500px",
        ),
        SCRIPT(
           "stats_disk_app('%(url)s', '%(id)s');"%dict(
                  id=id+'_dg',
                  url=URL(r=request,
                          f='call/json/json_disk_app_dg',
                          args=[app_id, dg_id]
                      )
                ),
           "stats_disk_app('%(url)s', '%(id)s');"%dict(
                  id=id,
                  url=URL(r=request,
                          f='call/json/json_disk_app',
                          args=[app_id]
                      )
                ),
            _name='%s_to_eval'%row_id,
        ),
        )
    return d

@service.json
def json_disk_array_dg():
    array_name = request.vars.array_name
    dg_name = request.vars.dg_name
    q = db.stat_day_disk_array_dg.array_name == array_name
    q &= db.stat_day_disk_array_dg.array_dg == dg_name
    q &= db.stat_day_disk_array_dg.disk_size != None
    q &= db.stat_day_disk_array_dg.disk_size != 0
    rows = db(q).select(cacheable=True)
    disk_used = []
    disk_free = []
    disk_reserved = []
    disk_reservable = []
    if len(rows) < 2:
        return [disk_used, disk_free, disk_reserved, disk_reservable]
    for r in rows:
        disk_used.append([r.day, r.disk_used])
        disk_free.append([r.day, r.disk_size-r.disk_used])
        disk_reserved.append([r.day, r.reserved])
        disk_reservable.append([r.day, r.reservable])
    return [disk_used, disk_free, disk_reserved, disk_reservable]

@service.json
def json_disk_array():
    array_name = request.vars.array_name
    q = db.stat_day_disk_array.array_name == array_name
    q &= db.stat_day_disk_array.disk_size != None
    q &= db.stat_day_disk_array.disk_size != 0
    rows = db(q).select(cacheable=True)
    disk_used = []
    disk_free = []
    disk_reserved = []
    disk_reservable = []
    if len(rows) < 2:
        return [disk_used, disk_free, disk_reserved, disk_reservable]
    for r in rows:
        disk_used.append([r.day, r.disk_used])
        disk_free.append([r.day, r.disk_size-r.disk_used])
        disk_reserved.append([r.day, r.reserved])
        disk_reservable.append([r.day, r.reservable])
    return [disk_used, disk_free, disk_reserved, disk_reservable]

@service.json
def json_disk_app(app_id):
    q = db.apps.id == int(app_id)
    q &= db.stat_day_disk_app.app == db.apps.app
    rows = db(q).select(cacheable=True)
    disk_used = []
    disk_quota = []
    if len(rows) < 2:
        return [disk_used, disk_quota]
    for r in rows:
        disk_used.append([r.stat_day_disk_app.day, r.stat_day_disk_app.disk_used])
        disk_quota.append([r.stat_day_disk_app.day, r.stat_day_disk_app.quota])
    return [disk_used, disk_quota]

@service.json
def json_disk_app_dg(app_id, dg_id):
    q = db.apps.id == int(app_id)
    q &= db.stat_day_disk_app_dg.app == db.apps.app
    q &= db.stat_day_disk_app_dg.dg_id == int(dg_id)
    rows = db(q).select(cacheable=True)
    disk_used = []
    disk_quota = []
    if len(rows) < 2:
        return [disk_used, disk_quota]
    for r in rows:
        disk_used.append([r.stat_day_disk_app_dg.day, r.stat_day_disk_app_dg.disk_used])
        if r.stat_day_disk_app_dg.quota is None:
            quota = 0
        else:
            quota = r.stat_day_disk_app_dg.quota
        disk_quota.append([r.stat_day_disk_app_dg.day, quota])
    return [disk_used, disk_quota]

