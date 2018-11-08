class table_nodesan(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = [
                      'id',
                      'nodename',
                      'assetname',
                      'fqdn',
                      'loc_country',
                      'loc_zip',
                      'loc_city',
                      'loc_addr',
                      'loc_building',
                      'loc_floor',
                      'loc_room',
                      'loc_rack',
                      'os_name',
                      'os_release',
                      'os_vendor',
                      'os_arch',
                      'os_kernel',
                      'cpu_dies',
                      'cpu_cores',
                      'cpu_threads',
                      'cpu_model',
                      'cpu_freq',
                      'cpu_vendor',
                      'mem_banks',
                      'mem_slots',
                      'mem_bytes',
                      'listener_port',
                      'version',
                      'team_responsible',
                      'team_integ',
                      'team_support',
                      'app',
                      'serial',
                      'model',
                      'bios_version',
                      'sp_version',
                      'enclosure',
                      'enclosureslot',
                      'hvvdc',
                      'hvpool',
                      'hv',
                      'role',
                      'node_env',
                      'asset_env',
                      'status',
                      'type',
                      'warranty_end',
                      'maintenance_end',
                      'hw_obs_warn_date',
                      'hw_obs_alert_date',
                      'os_obs_warn_date',
                      'os_obs_alert_date',
                      'power_supply_nb',
                      'power_cabinet1',
                      'power_cabinet2',
                      'power_protect',
                      'power_protect_breaker',
                      'power_breaker1',
                      'power_breaker2',
                      'node_updated',
                      'hba_id',
                      'tgt_id',
                      'array_name',
                      'array_model',
                      'array_cache',
                      'array_firmware',
                      'array_updated',
                      'array_level',
                     ]
        self.colprops = nodes_colprops
        self.colprops.update({
            'node_updated': HtmlTableColumn(
                     field='node_updated',
                    ),
            'node_id': HtmlTableColumn(
                     field='node_id',
                    ),
            'id': HtmlTableColumn(
                     field='id',
                    ),
            'hba_id': HtmlTableColumn(
                     field='hba_id',
                    ),
            'tgt_id': HtmlTableColumn(
                     field='tgt_id',
                    ),
            'array_name': HtmlTableColumn(
                     field='array_name',
                    ),
            'array_model': HtmlTableColumn(
                     field='array_model',
                    ),
            'array_cache': HtmlTableColumn(
                     field='array_cache',
                    ),
            'array_firmware': HtmlTableColumn(
                     field='array_firmware',
                    ),
            'array_updated': HtmlTableColumn(
                     field='array_updated',
                    ),
            'array_level': HtmlTableColumn(
                     field='array_level',
                    ),
        })
        for c in self.cols:
            self.colprops[c].table = 'v_nodesan'
        self.ajax_col_values = 'ajax_nodesan_col_values'

@auth.requires_login()
def ajax_nodesan_col_values():
    table_id = request.vars.table_id
    t = table_nodesan(table_id, 'ajax_nodesan')
    col = request.args[0]
    o = db.v_nodesan[col]
    q = q_filter(app_field=db.v_nodesan.app)
    for f in t.cols:
        q = _where(q, 'v_nodesan', t.filter_parse(f), f)
    q = apply_filters_id(q, node_field=db.v_nodesan.node_id)
    t.object_list = db(q).select(
        o,
        db.v_nodesan.id.count(),
        orderby=~db.v_nodesan.id.count(),
        groupby=o,
    )
    return t.col_values_cloud_grouped(col)

@auth.requires_login()
def ajax_nodesan():
    table_id = request.vars.table_id
    t = table_nodesan(table_id, 'ajax_nodesan')

    o = t.get_orderby(default=db.v_nodesan.nodename|db.v_nodesan.hba_id|db.v_nodesan.tgt_id)
    q = q_filter(app_field=db.v_nodesan.app)
    for f in t.cols:
        q = _where(q, 'v_nodesan', t.filter_parse(f), f)
    q = apply_filters_id(q, node_field=db.v_nodesan.node_id)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.v_nodesan.id.count(), cacheable=True).first()._extra[db.v_nodesan.id.count()]
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def nodesan():
    t = SCRIPT(
          """table_nodesan("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def nodesan_load():
    return nodesan()["table"]

