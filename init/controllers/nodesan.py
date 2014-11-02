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
        self.colprops = v_nodes_colprops
        self.span = ["nodename"]
        self.keys = ['hba_id', 'tgt_id']
        for col in self.colprops:
            self.colprops[col].display = False
        self.colprops['node_updated'] = self.colprops['updated']
        self.colprops['nodename'].display = True
        self.colprops.update({
            'id': HtmlTableColumn(
                     title='Id',
                     field='id',
                     img='net16',
                     display=False,
                    ),
            'hba_id': HtmlTableColumn(
                     title='Hba Id',
                     field='hba_id',
                     img='net16',
                     display=True,
                    ),
            'tgt_id': HtmlTableColumn(
                     title='Target Id',
                     field='tgt_id',
                     img='net16',
                     display=True,
                    ),
            'array_name': HtmlTableColumn(
                     title='Array Name',
                     field='array_name',
                     img='disk16',
                     display=True,
                    ),
            'array_model': HtmlTableColumn(
                     title='Array Model',
                     field='array_model',
                     img='disk16',
                     display=True,
                    ),
            'array_cache': HtmlTableColumn(
                     title='Array Cache',
                     field='array_cache',
                     img='disk16',
                     display=False,
                    ),
            'array_firmware': HtmlTableColumn(
                     title='Array Firmware',
                     field='array_firmware',
                     img='disk16',
                     display=False,
                    ),
            'array_updated': HtmlTableColumn(
                     title='Array Updated',
                     field='array_updated',
                     img='time16',
                     display=False,
                    ),
            'array_level': HtmlTableColumn(
                     title='Array Level',
                     field='array_level',
                     img='disk16',
                     display=False,
                    ),
        })
        for c in self.cols:
            self.colprops[c].table = 'v_nodesan'
            self.colprops[c].t = self
            if self.colprops[c].field.startswith('array_') or self.colprops[c].field in ['tgt_id', 'hba_id']:
                self.colprops[c]._dataclass = "bluer"
        self.extraline = True
        self.dataable = True
        self.force_cols = ['id', 'os_name']
        self.checkboxes = True
        self.ajax_col_values = 'ajax_nodesan_col_values'

@auth.requires_login()
def ajax_nodesan_col_values():
    t = table_nodesan('nodesan', 'ajax_nodesan')
    col = request.args[0]
    o = db.v_nodesan[col]
    q = db.v_nodesan.id > 0
    for f in t.cols:
        q = _where(q, 'v_nodesan', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_nodesan():
    t = table_nodesan('nodesan', 'ajax_nodesan')

    o = db.v_nodesan.nodename|db.v_nodesan.hba_id|db.v_nodesan.tgt_id
    q = db.v_nodesan.id > 0
    for f in t.cols:
        q = _where(q, 'v_nodesan', t.filter_parse(f), f)
    q = apply_filters(q, db.v_nodesan.nodename, None)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        t.csv()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.v_nodesan.id.count(), cacheable=True).first()._extra[db.v_nodesan.id.count()]
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def nodesan():
    t = table_nodesan('nodesan', 'ajax_nodesan')
    t = DIV(
          t.html(),
          _id='nodesan',
        )
    return dict(table=t)


