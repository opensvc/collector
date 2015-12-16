class table_sanswitches(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = [
                      'sw_fabric',
                      'sw_name',
                      'sw_index',
                      'sw_slot',
                      'sw_port',
                      'sw_portspeed',
                      'sw_portnego',
                      'sw_porttype',
                      'sw_portstate',
                      'sw_portname',
                      'sw_rportname',
                      'sw_rname',
                      'sw_updated',
                     ]
        #self.colprops = v_nodes_colprops
        self.keys = ['sw_fabric', 'sw_name', 'sw_index', 'sw_rportname']
        self.span = ['sw_fabric', 'sw_name', 'sw_index']
        self.colprops.update({
            'sw_name': HtmlTableColumn(
                     title='Switch Name',
                     field='sw_name',
                     img='net16',
                     display=True,
                    ),
            'sw_port': HtmlTableColumn(
                     title='Port',
                     field='sw_port',
                     img='net16',
                     display=True,
                    ),
            'sw_slot': HtmlTableColumn(
                     title='Slot',
                     field='sw_slot',
                     img='net16',
                     display=True,
                    ),
            'sw_portspeed': HtmlTableColumn(
                     title='Port Speed',
                     field='sw_portspeed',
                     img='net16',
                     display=True,
                    ),
            'sw_portnego': HtmlTableColumn(
                     title='Port Nego',
                     field='sw_portnego',
                     img='net16',
                     display=True,
                     _class='boolean',
                    ),
            'sw_porttype': HtmlTableColumn(
                     title='Port Type',
                     field='sw_porttype',
                     img='net16',
                     display=True,
                    ),
            'sw_portstate': HtmlTableColumn(
                     title='Port State',
                     field='sw_portstate',
                     img='net16',
                     display=True,
                    ),
            'sw_portname': HtmlTableColumn(
                     title='Port Name',
                     field='sw_portname',
                     img='net16',
                     display=True,
                    ),
            'sw_rportname': HtmlTableColumn(
                     title='Remote Port Name',
                     field='sw_rportname',
                     img='net16',
                     display=True,
                    ),
            'sw_rname': HtmlTableColumn(
                     title='Remote Name',
                     field='sw_rname',
                     img='net16',
                     display=True,
                    ),
            'sw_updated': HtmlTableColumn(
                     title='Updated',
                     field='sw_updated',
                     img='time16',
                     display=True,
                     _class="datetime_no_age",
                    ),
            'sw_fabric': HtmlTableColumn(
                     title='Switch Fabric',
                     field='sw_fabric',
                     img='net16',
                     display=False,
                    ),
            'sw_index': HtmlTableColumn(
                     title='Port Index',
                     field='sw_index',
                     img='net16',
                     display=True,
                    ),
        })
        for c in self.cols:
            self.colprops[c].table = 'v_switches'
            self.colprops[c].t = self
        self.extraline = True
        self.ajax_col_values = 'ajax_sanswitches_col_values'
        self.dataable = True
        self.span = ["sw_name", "sw_index"]
        self.keys = ["sw_name", "sw_index"]

@auth.requires_login()
def ajax_sanswitches_col_values():
    table_id = request.vars.table_id
    t = table_sanswitches(table_id, 'ajax_sanswitches')
    col = request.args[0]
    o = db.v_switches[col]
    q = db.v_switches.id > 0
    for f in t.cols:
        q = _where(q, 'v_switches', t.filter_parse(f), f)
    q = apply_filters(q, db.v_switches.sw_rname, None)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_sanswitches():
    table_id = request.vars.table_id
    t = table_sanswitches(table_id, 'ajax_sanswitches')

    o = db.v_switches.sw_name|db.v_switches.sw_index|db.v_switches.sw_portstate
    q = db.v_switches.id > 0
    for f in t.cols:
        q = _where(q, 'v_switches', t.filter_parse(f), f)
    q = apply_filters(q, db.v_switches.sw_rname, None)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.v_switches.id.count(), cacheable=True).first()._extra[db.v_switches.id.count()]
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def sanswitches():
    t = SCRIPT(
          """$.when(osvc.app_started).then(function(){ table_sanswitches("layout", %s) })""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def sanswitches_load():
    return sanswitches()["table"]

