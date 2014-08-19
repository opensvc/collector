class table_nodenetworks(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = [
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
                      'project',
                      'serial',
                      'model',
                      'enclosure',
                      'enclosureslot',
                      'hvvdc',
                      'hvpool',
                      'hv',
                      'role',
                      'host_mode',
                      'environnement',
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
                      'addr_updated',
                      'net_name',
                      'net_network',
                      'net_broadcast',
                      'net_comment',
                      'net_gateway',
                      'net_begin',
                      'net_end',
                      'net_pvid',
                      'net_netmask',
                      'net_team_responsible']
        self.colprops = v_nodes_colprops
        for col in self.colprops:
            self.colprops[col].display = False
        self.colprops['nodename'].display = True
        self.colprops.update({
            'net_id': HtmlTableColumn(
                     title='Net Id',
                     field='net_id',
                     img='net16',
                     display=True,
                    ),
            'net_pvid': HtmlTableColumn(
                     title='Net VLAN id',
                     field='net_pvid',
                     img='net16',
                     display=True,
                    ),
            'net_begin': HtmlTableColumn(
                     title='Net Ip range begin',
                     field='net_begin',
                     img='net16',
                     display=True,
                    ),
            'net_end': HtmlTableColumn(
                     title='Net Ip range end',
                     field='net_end',
                     img='net16',
                     display=True,
                    ),
            'net_gateway': HtmlTableColumn(
                     title='Net Gateway',
                     field='net_gateway',
                     img='net16',
                     display=True,
                    ),
            'net_comment': HtmlTableColumn(
                     title='Net Comment',
                     field='net_comment',
                     img='net16',
                     display=True,
                    ),
            'net_name': HtmlTableColumn(
                     title='Net Name',
                     field='net_name',
                     img='net16',
                     display=True,
                    ),
            'net_network': HtmlTableColumn(
                     title='Net Network',
                     field='net_network',
                     img='net16',
                     display=True,
                    ),
            'net_broadcast': HtmlTableColumn(
                     title='Net Broadcast',
                     field='net_broadcast',
                     img='net16',
                     display=True,
                    ),
            'net_netmask': HtmlTableColumn(
                     title='Net Netmask',
                     field='net_netmask',
                     img='net16',
                     display=True,
                    ),
            'net_team_responsible': HtmlTableColumn(
                     title='Net Team Responsible',
                     field='net_team_responsible',
                     img='guys16',
                     display=True,
                    ),
            'mac': HtmlTableColumn(
                     title='Mac Address',
                     field='mac',
                     img='net16',
                     display=True,
                    ),
            'intf': HtmlTableColumn(
                     title='Interface',
                     field='intf',
                     img='net16',
                     display=True,
                    ),
            'addr_type': HtmlTableColumn(
                     title='Ip Address Type',
                     field='addr_type',
                     img='net16',
                     display=True,
                    ),
            'addr': HtmlTableColumn(
                     title='Ip Address',
                     field='addr',
                     img='net16',
                     display=True,
                    ),
            'mask': HtmlTableColumn(
                     title='Netmask',
                     field='mask',
                     img='net16',
                     display=True,
                    ),
            'addr_updated': HtmlTableColumn(
                     title='Address Update',
                     field='addr_updated',
                     img='net16',
                     display=True,
                    ),
        })
        for c in self.cols:
            self.colprops[c].table = 'v_nodenetworks'
            self.colprops[c].t = self
            if self.colprops[c].field.startswith('net_'):
                self.colprops[c]._dataclass = "bluer"
        self.extraline = True
        #self.checkboxes = True
        self.ajax_col_values = 'ajax_nodenetworks_col_values'
        self.keys = ["nodename", "addr"]
        self.span = ["nodename"]

@auth.requires_login()
def ajax_nodenetworks_col_values():
    t = table_nodenetworks('nodenetworks', 'ajax_nodenetworks')
    col = request.args[0]
    o = db.v_nodenetworks[col]
    q = db.v_nodenetworks.id > 0
    for f in t.cols:
        q = _where(q, 'v_nodenetworks', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_nodenetworks():
    t = table_nodenetworks('nodenetworks', 'ajax_nodenetworks')

    o = db.v_nodenetworks.nodename|db.v_nodenetworks.intf
    q = db.v_nodenetworks.id > 0
    for f in t.cols:
        q = _where(q, 'v_nodenetworks', t.filter_parse(f), f)
    q = apply_filters(q, db.v_nodenetworks.nodename, None)

    if len(request.args) == 1 and request.args[0] == 'line':
        if request.vars.volatile_filters is None:
            t.setup_pager(-1)
            limitby = (t.pager_start,t.pager_end)
        else:
            limitby = (0, 500)
        t.object_list = db(q).select(orderby=o, limitby=limitby, cacheable=False)
        t.set_column_visibility()
        return TABLE(t.table_lines()[0])

    n = db(q).select(db.v_nodenetworks.id.count(), cacheable=True).first()._extra[db.v_nodenetworks.id.count()]
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)

    return t.html()

@auth.requires_login()
def nodenetworks():
    t = DIV(
          ajax_nodenetworks(),
          _id='nodenetworks',
        )
    return dict(table=t)


