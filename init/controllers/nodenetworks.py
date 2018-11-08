class table_nodenetworks(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = [
                      'id',
                      'node_id',
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
                      'updated',
                      'mac',
                      'intf',
                      'addr_type',
                      'addr',
                      'mask',
                      'flag_deprecated',
                      'addr_updated',
                      'net_name',
                      'net_network',
                      'net_broadcast',
                      'net_comment',
                      'net_gateway',
                      'net_begin',
                      'net_end',
                      'prio',
                      'net_pvid',
                      'net_netmask',
                      'net_team_responsible']
        self.colprops = nodes_colprops
        self.colprops.update({
            'id': HtmlTableColumn(
                     field='id',
                    ),
            'nodename': HtmlTableColumn(
                     field='nodename',
                     table='nodes',
                    ),
            'node_id': HtmlTableColumn(
                     field='node_id',
                    ),
            'net_id': HtmlTableColumn(
                     field='net_id',
                    ),
            'net_pvid': HtmlTableColumn(
                     field='net_pvid',
                    ),
            'net_begin': HtmlTableColumn(
                     field='net_begin',
                    ),
            'net_end': HtmlTableColumn(
                     field='net_end',
                    ),
            'prio': HtmlTableColumn(
                     field='prio',
                    ),
            'net_gateway': HtmlTableColumn(
                     field='net_gateway',
                    ),
            'net_comment': HtmlTableColumn(
                     field='net_comment',
                    ),
            'net_name': HtmlTableColumn(
                     field='net_name',
                    ),
            'net_network': HtmlTableColumn(
                     field='net_network',
                    ),
            'net_broadcast': HtmlTableColumn(
                     field='net_broadcast',
                    ),
            'net_netmask': HtmlTableColumn(
                     field='net_netmask',
                    ),
            'net_team_responsible': HtmlTableColumn(
                     field='net_team_responsible',
                    ),
            'mac': HtmlTableColumn(
                     field='mac',
                    ),
            'intf': HtmlTableColumn(
                     field='intf',
                    ),
            'addr_type': HtmlTableColumn(
                     field='addr_type',
                    ),
            'addr': HtmlTableColumn(
                     field='addr',
                    ),
            'mask': HtmlTableColumn(
                     field='mask',
                    ),
            'flag_deprecated': HtmlTableColumn(
                     field='flag_deprecated',
                    ),
            'addr_updated': HtmlTableColumn(
                     field='addr_updated',
                    ),
        })
        for c in self.cols:
            self.colprops[c].table = 'v_nodenetworks'
        self.ajax_col_values = 'ajax_nodenetworks_col_values'
        self.csv_limit = 30000

@auth.requires_login()
def ajax_nodenetworks_col_values():
    table_id = request.vars.table_id
    t = table_nodenetworks(table_id, 'ajax_nodenetworks')
    col = request.args[0]
    o = db.v_nodenetworks[col]
    q = q_filter(app_field=db.v_nodenetworks.app)
    for f in t.cols:
        q = _where(q, 'v_nodenetworks', t.filter_parse(f), f)
    q = apply_filters_id(q, node_field=db.v_nodenetworks.node_id)
    t.object_list = db(q).select(
        o,
        db.v_nodenetworks.id.count(),
        orderby=~db.v_nodenetworks.id.count(),
        groupby=o,
    )
    return t.col_values_cloud_grouped(col)

@auth.requires_login()
def ajax_nodenetworks():
    table_id = request.vars.table_id
    t = table_nodenetworks(table_id, 'ajax_nodenetworks')

    o = t.get_orderby(default=db.v_nodenetworks.nodename|db.v_nodenetworks.intf)
    q = q_filter(app_field=db.v_nodenetworks.app)
    for f in t.cols:
        q = _where(q, 'v_nodenetworks', t.filter_parse(f), f)
    q = apply_filters_id(q, node_field=db.v_nodenetworks.node_id)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.v_nodenetworks.id.count(), cacheable=True).first()._extra[db.v_nodenetworks.id.count()]
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=True)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def nodenetworks():
    t = SCRIPT(
          """table_nodenetworks("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def nodenetworks_load():
    return nodenetworks()["table"]

