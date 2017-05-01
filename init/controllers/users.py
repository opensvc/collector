
class table_users(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['manager',
                     'id',
                     'fullname',
                     'email',
                     'phone_work',
                     'primary_group',
                     'groups',
                     'lock_filter',
                     'fset_name',
                     'quota_app',
                     'quota_org_group',
                     'last']
        self.colprops = {
            'id': HtmlTableColumn(
                     table='v_users',
                     field='id',
                    ),
            'fullname': HtmlTableColumn(
                     table='v_users',
                     field='fullname',
                    ),
            'email': HtmlTableColumn(
                     table='v_users',
                     field='email',
                    ),
            'phone_work': HtmlTableColumn(
                     table='v_users',
                     field='phone_work',
                    ),
            'primary_group': HtmlTableColumn(
                     table='v_users',
                     field='primary_group',
                    ),
            'groups': HtmlTableColumn(
                     table='v_users',
                     field='groups',
                    ),
            'manager': HtmlTableColumn(
                     table='v_users',
                     field='manager',
                    ),
            'lock_filter': HtmlTableColumn(
                     table='v_users',
                     field='lock_filter',
                    ),
            'quota_app': HtmlTableColumn(
                     table='v_users',
                     field='quota_app',
                    ),
            'quota_org_group': HtmlTableColumn(
                     table='v_users',
                     field='quota_org_group',
                    ),
            'fset_name': HtmlTableColumn(
                     table='v_users',
                     field='fset_name',
                    ),
            'last': HtmlTableColumn(
                     table='v_users',
                     field='last',
                    ),
        }
        self.ajax_col_values = 'ajax_users_col_values'

@auth.requires_login()
def ajax_users_col_values():
    table_id = request.vars.table_id
    t = table_users(table_id, 'ajax_users')
    col = request.args[0]
    o = db.v_users[col]
    q = db.v_users.id > 0
    t.object_list = db(q).select(orderby=o, groupby=o)
    for f in t.cols:
        q = _where(q, 'v_users', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_membership('Manager')
@auth.requires_login()
def ajax_users():
    table_id = request.vars.table_id
    t = table_users(table_id, 'ajax_users')
    o = t.get_orderby(default=~db.v_users.last)
    q = db.v_users.id > 0
    for f in t.cols:
        q = _where(q, 'v_users', t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def users():
    t = SCRIPT(
          """table_users("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def users_load():
    return users()["table"]

