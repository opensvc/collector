def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget(response)
    return service()

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
        self.colprops.update({
            'id': HtmlTableColumn(
                     table='v_disk_quota',
                     field='id',
                    ),
            'array_name': HtmlTableColumn(
                     table='v_disk_quota',
                     field='array_name',
                    ),
            'array_model': HtmlTableColumn(
                     table='v_disk_quota',
                     field='array_model',
                    ),
            'array_id': HtmlTableColumn(
                     table='v_disk_quota',
                     field='array_id',
                    ),
            'dg_name': HtmlTableColumn(
                     table='v_disk_quota',
                     field='dg_name',
                    ),
            'dg_free': HtmlTableColumn(
                     table='v_disk_quota',
                     field='dg_free',
                    ),
            'dg_used': HtmlTableColumn(
                     table='v_disk_quota',
                     field='dg_used',
                    ),
            'dg_reservable': HtmlTableColumn(
                     table='v_disk_quota',
                     field='dg_reservable',
                    ),
            'dg_reserved': HtmlTableColumn(
                     table='v_disk_quota',
                     field='dg_reserved',
                    ),
            'dg_size': HtmlTableColumn(
                     table='v_disk_quota',
                     field='dg_size',
                    ),
            'dg_id': HtmlTableColumn(
                     table='v_disk_quota',
                     field='dg_id',
                    ),
            'app': HtmlTableColumn(
                     table='v_disk_quota',
                     field='app',
                    ),
            'app_id': HtmlTableColumn(
                     table='v_disk_quota',
                     field='app_id',
                    ),
            'quota': HtmlTableColumn(
                     table='v_disk_quota',
                     field='quota',
                    ),
            'quota_used': HtmlTableColumn(
                     table='v_disk_quota',
                     field='quota_used',
                    ),
        })
        self.ajax_col_values = 'ajax_quota_col_values'

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
    q = q_filter(app_field=db.v_disk_quota.app)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_quota():
    table_id = request.vars.table_id
    t = table_quota(table_id, 'ajax_quota')

    update_dg_reserved()

    o = t.get_orderby(default=db.v_disk_quota.array_name|db.v_disk_quota.dg_name)
    q = q_filter(app_field=db.v_disk_quota.app)
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
        self.cols = ['disk_id',
                     'disk_region',
                     'disk_vendor',
                     'disk_model',
                     'app_id',
                     'app',
                     'node_id',
                     'nodename',
                     'svc_id',
                     'svcname',
                     'disk_dg',
                     'svcdisk_updated',
                     'size',
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
        self.colprops.update(disk_app_colprops)
        import copy
        _nodes_colprops = copy.copy(nodes_colprops)
        for i in _nodes_colprops:
            _nodes_colprops[i].table = 'nodes'
        self.colprops.update(_nodes_colprops)
        self.ajax_col_values = 'ajax_disks_col_values'

@auth.requires_login()
def ajax_disks_col_values():
    table_id = request.vars.table_id
    t = table_disks(table_id, 'ajax_disks')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.svcdisks.id>0
    q |= db.stor_array.id>0
    l0 = db.svcdisks.on(db.svcdisks.disk_id == db.diskinfo.disk_id)
    l1 = db.stor_array.on(db.diskinfo.disk_arrayid == db.stor_array.array_name)
    l2 = db.nodes.on(db.svcdisks.node_id==db.nodes.node_id)
    l3 = db.services.on(db.svcdisks.svc_id==db.services.svc_id)
    l4 = db.apps.on(db.svcdisks.app_id==db.apps.id)
    q = q_filter(q, app_field=db.apps.app)
    q = apply_filters_id(q, db.svcdisks.node_id)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), t.colprops[f].field)
    t.object_list = db(q).select(o, cacheable=True, orderby=o, left=(l0,l1,l2,l3,l4))
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_disks():
    table_id = request.vars.table_id
    t = table_disks(table_id, 'ajax_disks')

    o = t.get_orderby(default=db.diskinfo.disk_id|db.services.svcname|db.nodes.nodename)
    q = db.diskinfo.id>0
    q |= db.stor_array.id>0
    l0 = db.svcdisks.on(db.svcdisks.disk_id == db.diskinfo.disk_id)
    l1 = db.stor_array.on(db.diskinfo.disk_arrayid == db.stor_array.array_name)
    l2 = db.nodes.on(db.svcdisks.node_id==db.nodes.node_id)
    l3 = db.services.on(db.svcdisks.svc_id==db.services.svc_id)
    l4 = db.apps.on(db.svcdisks.app_id==db.apps.id)
    q = q_filter(q, app_field=db.apps.app)
    q = apply_filters_id(q, db.svcdisks.node_id)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), t.colprops[f].field)

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.diskinfo.id.count(), cacheable=True,
                         left=(l0,l1,l2,l3,l4)).first()._extra[db.diskinfo.id.count()]
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby,
                                     cacheable=False, left=(l0,l1,l2,l3,l4))
        return t.table_lines_data(n, html=False)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        t.csv_left = (l0,l1,l2,l3)
        t.csv_limit = 60000
        return t.csv()

    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        t.csv_orderby = o
        t.csv_left = (l0,l1,l2,l3)
        return t.do_commonality()

@auth.requires_login()
def disks():
    t = SCRIPT(
          """view_disks("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

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
        self.colprops.update({
            'chart': HtmlTableColumn(
                     field='chart',
                    ),
        })

@auth.requires_login()
def ajax_disk_charts():
    table_id = request.vars.table_id
    nt = table_disk_charts(table_id, 'ajax_disk_charts')
    t = table_disks('disks', 'ajax_disks')
    volatile_filters = request.vars.volatile_filters
    request.vars.volatile_filters = None

    q = db.diskinfo.id > 0
    q = q_filter(q, app_field=db.apps.app)
    q = apply_filters_id(q, db.svcdisks.node_id)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), t.colprops[f].field)

    nt.setup_pager(-1)

    h_data_svc = ""
    h_data_app = ""
    h_data_dg = ""
    h_data_array = ""

    sql = """  select
                 count(distinct(svcdisks.app_id)),
                 max(diskinfo.disk_level)
               from
                 diskinfo
               left join svcdisks on diskinfo.disk_id=svcdisks.disk_id
               left join stor_array on diskinfo.disk_arrayid=stor_array.array_name
               left join nodes on svcdisks.node_id=nodes.node_id
               left join services on svcdisks.svc_id=services.svc_id
               left join apps on svcdisks.app_id=apps.id
               where
                 %(q)s
           """%dict(q=q)
    n_app = db.executesql(sql)[0][0]
    max_level = db.executesql(sql)[0][1]

    if max_level is None:
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
        return

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
                       diskinfo.disk_id,
                       svcdisks.disk_region,
                       svcdisks.svc_id as obj,
                       svcdisks.disk_used as disk_used,
                       diskinfo.disk_size,
                       diskinfo.disk_alloc
                     from
                       diskinfo
                     left join svcdisks on diskinfo.disk_id=svcdisks.disk_id
                     left join stor_array on diskinfo.disk_arrayid=stor_array.array_name
                     left join nodes on svcdisks.node_id=nodes.node_id
                     left join services on svcdisks.svc_id=services.svc_id
                     left join apps on svcdisks.app_id=apps.id
                     where %(q)s
                     and diskinfo.disk_level=%(level)d
                     and svcdisks.svc_id != ""
                     union all
                     select
                       diskinfo.disk_id,
                       svcdisks.disk_region,
                       nodes.nodename as obj,
                       svcdisks.disk_used as disk_used,
                       diskinfo.disk_size,
                       diskinfo.disk_alloc
                     from
                       diskinfo
                     left join svcdisks on diskinfo.disk_id=svcdisks.disk_id
                     left join stor_array on diskinfo.disk_arrayid=stor_array.array_name
                     left join nodes on svcdisks.node_id=nodes.node_id
                     left join services on svcdisks.svc_id=services.svc_id
                     left join apps on svcdisks.app_id=apps.id
                     where %(q)s
                     and diskinfo.disk_level=%(level)d
                     and (svcdisks.svc_id = "" or svcdisks.svc_id is NULL)
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
                       diskinfo.disk_id,
                       svcdisks.disk_region,
                       apps.app as app,
                       svcdisks.disk_used as disk_used,
                       diskinfo.disk_size,
                       diskinfo.disk_alloc
                     from
                       diskinfo
                     left join svcdisks on diskinfo.disk_id=svcdisks.disk_id
                     left join stor_array on diskinfo.disk_arrayid=stor_array.array_name
                     left join nodes on svcdisks.node_id=nodes.node_id
                     left join services on svcdisks.svc_id=services.svc_id
                     left join apps on svcdisks.app_id=apps.id
                     where %(q)s
                     and diskinfo.disk_level=%(level)d
                     and svcdisks.svc_id != ""
                     union all
                     select
                       diskinfo.disk_id,
                       svcdisks.disk_region,
                       apps.app as app,
                       svcdisks.disk_used as disk_used,
                       diskinfo.disk_size,
                       diskinfo.disk_alloc
                     from
                       diskinfo
                     left join svcdisks on diskinfo.disk_id=svcdisks.disk_id
                     left join stor_array on diskinfo.disk_arrayid=stor_array.array_name
                     left join nodes on svcdisks.node_id=nodes.node_id
                     left join services on svcdisks.svc_id=services.svc_id
                     left join apps on svcdisks.app_id=apps.id
                     where %(q)s
                     and diskinfo.disk_level=%(level)d
                     and (svcdisks.svc_id = "" or svcdisks.svc_id is NULL)
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


    sql = """select count(distinct diskinfo.disk_arrayid)
             from
                 diskinfo
               left join svcdisks on diskinfo.disk_id=svcdisks.disk_id
               left join stor_array on diskinfo.disk_arrayid=stor_array.array_name
               left join nodes on svcdisks.node_id=nodes.node_id
               left join services on svcdisks.svc_id=services.svc_id
               left join apps on svcdisks.app_id=apps.id
               where
                 %(q)s
          """%dict(q=q)
    n_arrays = db.executesql(sql)[0][0]

    sql = """select count(distinct diskinfo.disk_group)
             from
                 diskinfo
               left join svcdisks on diskinfo.disk_id=svcdisks.disk_id
               left join stor_array on diskinfo.disk_arrayid=stor_array.array_name
               left join nodes on svcdisks.node_id=nodes.node_id
               left join services on svcdisks.svc_id=services.svc_id
               left join apps on svcdisks.app_id=apps.id
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
                       diskinfo.disk_id,
                       max(svcdisks.disk_used) as disk_used,
                       diskinfo.disk_size,
                       diskinfo.disk_alloc,
                       diskinfo.disk_arrayid,
                       diskinfo.disk_group
                     from
                       diskinfo
                     left join svcdisks on diskinfo.disk_id=svcdisks.disk_id
                     left join stor_array on diskinfo.disk_arrayid=stor_array.array_name
                     left join nodes on svcdisks.node_id=nodes.node_id
                     left join services on svcdisks.svc_id=services.svc_id
                     left join apps on svcdisks.app_id=apps.id
                     where %(q)s
                     group by diskinfo.disk_id, svcdisks.disk_region
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
                       diskinfo.disk_id,
                       max(svcdisks.disk_used) as disk_used,
                       diskinfo.disk_size,
                       diskinfo.disk_alloc,
                       diskinfo.disk_arrayid
                     from
                       diskinfo
                     left join svcdisks on diskinfo.disk_id=svcdisks.disk_id
                     left join stor_array on diskinfo.disk_arrayid=stor_array.array_name
                     left join nodes on svcdisks.node_id=nodes.node_id
                     left join services on svcdisks.svc_id=services.svc_id
                     left join apps on svcdisks.app_id=apps.id
                     where %(q)s
                     and diskinfo.disk_level=%(level)d
                     group by diskinfo.disk_id, svcdisks.disk_region
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
    if len(rows) < 1:
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
    if len(rows) < 1:
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
    if len(rows) < 1:
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
    if len(rows) < 1:
        return [disk_used, disk_quota]
    for r in rows:
        disk_used.append([r.stat_day_disk_app_dg.day, r.stat_day_disk_app_dg.disk_used])
        if r.stat_day_disk_app_dg.quota is None:
            quota = 0
        else:
            quota = r.stat_day_disk_app_dg.quota
        disk_quota.append([r.stat_day_disk_app_dg.day, quota])
    return [disk_used, disk_quota]

