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
        self.colprops.update({
            'sw_name': HtmlTableColumn(
                     field='sw_name',
                    ),
            'sw_port': HtmlTableColumn(
                     field='sw_port',
                    ),
            'sw_slot': HtmlTableColumn(
                     field='sw_slot',
                    ),
            'sw_portspeed': HtmlTableColumn(
                     field='sw_portspeed',
                    ),
            'sw_portnego': HtmlTableColumn(
                     field='sw_portnego',
                    ),
            'sw_porttype': HtmlTableColumn(
                     field='sw_porttype',
                    ),
            'sw_portstate': HtmlTableColumn(
                     field='sw_portstate',
                    ),
            'sw_portname': HtmlTableColumn(
                     field='sw_portname',
                    ),
            'sw_rportname': HtmlTableColumn(
                     field='sw_rportname',
                    ),
            'sw_rname': HtmlTableColumn(
                     field='sw_rname',
                    ),
            'sw_updated': HtmlTableColumn(
                     field='sw_updated',
                    ),
            'sw_fabric': HtmlTableColumn(
                     field='sw_fabric',
                    ),
            'sw_index': HtmlTableColumn(
                     field='sw_index',
                    ),
        })
        for c in self.cols:
            self.colprops[c].table = 'v_switches'
        self.ajax_col_values = 'ajax_sanswitches_col_values'

@auth.requires_login()
def ajax_sanswitches_col_values():
    table_id = request.vars.table_id
    t = table_sanswitches(table_id, 'ajax_sanswitches')
    col = request.args[0]
    o = db.v_switches[col]
    q = db.v_switches.id > 0
    for f in t.cols:
        q = _where(q, 'v_switches', t.filter_parse(f), f)
    q = apply_filters_id(q, node_field=db.v_switches.sw_rname)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_sanswitches():
    table_id = request.vars.table_id
    t = table_sanswitches(table_id, 'ajax_sanswitches')

    o = t.get_orderby(default=db.v_switches.sw_name|db.v_switches.sw_index|db.v_switches.sw_portstate)
    q = db.v_switches.id > 0
    for f in t.cols:
        q = _where(q, 'v_switches', t.filter_parse(f), f)
    q = apply_filters_id(q, node_field=db.v_switches.sw_rname)

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
          """table_sanswitches("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def sanswitches_load():
    return sanswitches()["table"]

