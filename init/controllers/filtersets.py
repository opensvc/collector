#
# Filtersets
#
filters_colprops = {
    'f_table': HtmlTableColumn(
             title='Table',
             table='gen_filters',
             field='f_table',
             display=True,
             img='filter16',
             _class='db_table_name',
            ),
    'f_field': HtmlTableColumn(
             title='Field',
             table='gen_filters',
             field='f_field',
             display=True,
             img='filter16',
             _class='db_column_name',
            ),
    'f_value': HtmlTableColumn(
             title='Value',
             table='gen_filters',
             field='f_value',
             display=True,
             img='filter16',
            ),
    'f_updated': HtmlTableColumn(
             title='Updated',
             table='gen_filters',
             field='f_updated',
             display=True,
             img='time16',
             _class="datetime_no_age",
            ),
    'f_author': HtmlTableColumn(
             title='Author',
             table='gen_filters',
             field='f_author',
             display=True,
             img='guy16',
            ),
    'f_op': HtmlTableColumn(
             title='Operator',
             table='gen_filters',
             field='f_op',
             display=True,
             img='filter16',
            ),
    'id': HtmlTableColumn(
             title='Id',
             table='gen_filters',
             field='id',
             display=False,
             img='key',
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
                     title='Filterset',
                     field='fset_name',
                     display=True,
                     img='filter16',
                     _class='fset_name',
                    ),
            'fset_stats': HtmlTableColumn(
                     title='Compute stats',
                     field='fset_stats',
                     display=True,
                     img='spark16',
                     _class='boolean',
                    ),
            'fset_updated': HtmlTableColumn(
                     title='Fset updated',
                     field='fset_updated',
                     display=False,
                     img='time16',
                     _class="datetime_no_age",
                    ),
            'fset_author': HtmlTableColumn(
                     title='Fset author',
                     field='fset_author',
                     display=False,
                     img='guy16',
                    ),
            'f_log_op': HtmlTableColumn(
                     title='Operator',
                     field='f_log_op',
                     display=True,
                     img='filter16',
                    ),
            'id': HtmlTableColumn(
                     title='Id',
                     field='id',
                     display=False,
                     img='key',
                    ),
            'fset_id': HtmlTableColumn(
                     title='Filterset id',
                     field='fset_id',
                     display=False,
                     img='key',
                    ),
            'f_id': HtmlTableColumn(
                     title='Filter id',
                     field='f_id',
                     display=False,
                     img='key',
                    ),
            'f_order': HtmlTableColumn(
                     title='Ordering',
                     field='f_order',
                     display=False,
                     img='filter16',
                    ),
            'encap_fset_name': HtmlTableColumn(
                     title='Encap filterset',
                     field='encap_fset_name',
                     display=True,
                     img='filter16',
                     _class='fset_name',
                    ),
            'encap_fset_id': HtmlTableColumn(
                     title='Encap filterset id',
                     field='encap_fset_id',
                     display=False,
                     img='key',
                    ),
        }
        self.colprops.update(filters_colprops)
        for c in self.colprops:
            self.colprops[c].table = 'v_gen_filtersets'
        self.events = ["gen_filtersets_change",
                       "gen_filtersets_filters_change",
                       "gen_filters_change"]
        self.force_cols = ["fset_id", "f_id", "encap_fset_id"]
        self.span = ['fset_name', 'fset_stats']
        self.keys = ['fset_id', 'f_id', 'encap_fset_id']
        self.ajax_col_values = ajax_filtersets_col_values
        self.dbfilterable = False
        self.dataable = True
        self.wsable = True
        self.checkboxes = True

@auth.requires_login()
def ajax_filtersets_col_values():
    table_id = request.vars.table_id
    t = table_filtersets(table_id, 'ajax_filtersets')
    col = request.args[0]
    o = db.v_gen_filtersets[col]
    q = db.v_gen_filtersets.fset_id > 0
    for f in t.cols:
        q = _where(q, 'v_gen_filtersets', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_filtersets():
    table_id = request.vars.table_id
    t = table_filtersets(table_id, 'ajax_filtersets')
    o = db.v_gen_filtersets.fset_name|db.v_gen_filtersets.f_order|db.v_gen_filtersets.join_id
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
          """$.when(osvc.app_started).then(function(){ table_filtersets("layout", %s) })""" % request_vars_to_table_options(),
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
        self.keys = ["id"]
        self.force_cols = ["id"]
        self.span = ["f_table", "f_field"]
        self.cols = ["id"] + filters_cols
        self.colprops = filters_colprops
        self.ajax_col_values = 'ajax_filters_col_values'
        self.dbfilterable = False
        self.dataable = True
        self.wsable = True
        self.checkboxes = True
        self.checkbox_id = "id"
        self.events = ["gen_filters_change"]

@auth.requires_login()
def ajax_filters_col_values():
    table_id = request.vars.table_id
    t = table_filters(table_id, 'ajax_filters')
    col = request.args[0]
    o = db.gen_filters[col]
    q = db.gen_filters.id > 0
    for f in t.cols:
        q = _where(q, 'gen_filters', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_filters():
    table_id = request.vars.table_id
    t = table_filters(table_id, 'ajax_filters')

    o = db.gen_filters.f_table|db.gen_filters.f_field|db.gen_filters.f_op|db.gen_filters.f_field
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
          """$.when(osvc.app_started).then(function(){ table_filters("layout", %s) })""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def filters_load():
    return filters()["table"]


