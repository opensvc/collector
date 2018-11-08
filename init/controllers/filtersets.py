#
# Filtersets
#
filters_colprops = {
    'f_table': HtmlTableColumn(
             table='gen_filters',
             field='f_table',
            ),
    'f_field': HtmlTableColumn(
             table='gen_filters',
             field='f_field',
            ),
    'f_value': HtmlTableColumn(
             table='gen_filters',
             field='f_value',
            ),
    'f_updated': HtmlTableColumn(
             table='gen_filters',
             field='f_updated',
            ),
    'f_author': HtmlTableColumn(
             table='gen_filters',
             field='f_author',
            ),
    'f_op': HtmlTableColumn(
             table='gen_filters',
             field='f_op',
            ),
    'id': HtmlTableColumn(
             table='gen_filters',
             field='id',
            ),
}

filters_cols = ['f_table',
                'f_field',
                'f_op',
                'f_value',
                'f_updated',
                'f_author']

class table_filtersets(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['fset_id',
                     'fset_name',
                     'fset_stats',
                     'fset_updated',
                     'fset_author',
                     'f_id',
                     'f_order',
                     'f_log_op',
                     'encap_fset_id',
                     'encap_fset_name']
        self.cols += filters_cols

        self.colprops = {
            'fset_name': HtmlTableColumn(
                     field='fset_name',
                    ),
            'fset_stats': HtmlTableColumn(
                     field='fset_stats',
                    ),
            'fset_updated': HtmlTableColumn(
                     field='fset_updated',
                    ),
            'fset_author': HtmlTableColumn(
                     field='fset_author',
                    ),
            'f_log_op': HtmlTableColumn(
                     field='f_log_op',
                    ),
            'id': HtmlTableColumn(
                     field='id',
                    ),
            'fset_id': HtmlTableColumn(
                     field='fset_id',
                    ),
            'f_id': HtmlTableColumn(
                     field='f_id',
                    ),
            'f_order': HtmlTableColumn(
                     field='f_order',
                    ),
            'encap_fset_name': HtmlTableColumn(
                     field='encap_fset_name',
                    ),
            'encap_fset_id': HtmlTableColumn(
                     field='encap_fset_id',
                    ),
        }
        self.colprops.update(filters_colprops)
        for c in self.colprops:
            self.colprops[c].table = 'v_gen_filtersets'
        self.ajax_col_values = ajax_filtersets_col_values

@auth.requires_login()
def ajax_filtersets_col_values():
    table_id = request.vars.table_id
    t = table_filtersets(table_id, 'ajax_filtersets')
    col = request.args[0]
    o = db.v_gen_filtersets[col]
    q = db.v_gen_filtersets.fset_id > 0
    for f in t.cols:
        q = _where(q, 'v_gen_filtersets', t.filter_parse(f), f)
    t.object_list = db(q).select(
        o,
        db.v_gen_filtersets.id.count(),
        orderby=~db.v_gen_filtersets.id.count(),
        groupby=o,
        cacheable=True,
    )
    return t.col_values_cloud_grouped(col)

@auth.requires_login()
def ajax_filtersets():
    table_id = request.vars.table_id
    t = table_filtersets(table_id, 'ajax_filtersets')
    o = t.get_orderby(default=db.v_gen_filtersets.fset_name|db.v_gen_filtersets.f_order|db.v_gen_filtersets.join_id)
    q = db.v_gen_filtersets.fset_id > 0
    for f in t.cols:
        q = _where(q, 'v_gen_filtersets', t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def filtersets():
    t = SCRIPT(
          """table_filtersets("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def filtersets_load():
    return filtersets()["table"]


#
# filters
#
class table_filters(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ["id"] + filters_cols
        self.colprops = filters_colprops
        self.ajax_col_values = 'ajax_filters_col_values'

@auth.requires_login()
def ajax_filters_col_values():
    table_id = request.vars.table_id
    t = table_filters(table_id, 'ajax_filters')
    col = request.args[0]
    o = db.gen_filters[col]
    q = db.gen_filters.id > 0
    for f in t.cols:
        q = _where(q, 'gen_filters', t.filter_parse(f), f)
    t.object_list = db(q).select(
        o,
        db.gen_filters.id.count(),
        orderby=~db.gen_filters.id.count(),
        groupby=o,
        cacheable=True,
    )
    return t.col_values_cloud_grouped(col)

@auth.requires_login()
def ajax_filters():
    table_id = request.vars.table_id
    t = table_filters(table_id, 'ajax_filters')

    o = t.get_orderby(default=db.gen_filters.f_table|db.gen_filters.f_field|db.gen_filters.f_op|db.gen_filters.f_field)
    q = db.gen_filters.id > 0
    for f in t.cols:
        q = _where(q, 'gen_filters', t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def filters():
    t = SCRIPT(
          """table_filters("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def filters_load():
    return filters()["table"]


