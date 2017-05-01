class table_patches(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['nodename']
        self.cols += ['id',
                      'node_id',
                      'patch_num',
                      'patch_rev',
                      'patch_install_date',
                      'patch_updated']
        self.cols += nodes_cols
        self.colprops = nodes_colprops
        self.colprops.update({
            'nodename': HtmlTableColumn(
                     table='nodes',
                     field='nodename',
                    ),
            'node_id': HtmlTableColumn(
                     table='patches',
                     field='node_id',
                    ),
            'patch_num': HtmlTableColumn(
                     table='patches',
                     field='patch_num',
                    ),
            'patch_rev': HtmlTableColumn(
                     table='patches',
                     field='patch_rev',
                    ),
            'patch_updated': HtmlTableColumn(
                     table='patches',
                     field='patch_updated',
                    ),
            'patch_install_date': HtmlTableColumn(
                     table='patches',
                     field='patch_install_date',
                    ),
            'id': HtmlTableColumn(
                     table='patches',
                     field='id',
                    ),
        })
        self.colprops['nodename'].display = True
        self.ajax_col_values = 'ajax_patches_col_values'

@auth.requires_login()
def ajax_patches_col_values():
    table_id = request.vars.table_id
    t = table_patches(table_id, 'ajax_patches')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.patches.node_id==db.nodes.node_id
    q = q_filter(q, app_field=db.nodes.app)
    q = apply_filters_id(q, node_field=db.patches.node_id)

    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_patches():
    table_id = request.vars.table_id
    t = table_patches(table_id, 'ajax_patches')
    o = t.get_orderby(default=db.nodes.nodename|db.patches.patch_num|db.patches.patch_rev|db.nodes.app)

    q = db.patches.id>0
    q &= db.patches.node_id==db.nodes.node_id
    q = q_filter(q, app_field=db.nodes.app)
    q = apply_filters_id(q, node_field=db.patches.node_id)

    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.patches.id.count()).first()(db.patches.id.count())
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def patches():
    t = SCRIPT(
          """table_patches("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def patches_load():
    return patches()["table"]

