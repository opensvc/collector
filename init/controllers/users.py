
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
                     'domains',
                     'last']
        self.force_cols = ['id']
        self.keys = ['id']
        self.span = ['id']
        self.colprops = {
            'id': HtmlTableColumn(
                     title='User Id',
                     table='v_users',
                     field='id',
                     img='guy16',
                     display=True,
                    ),
            'fullname': HtmlTableColumn(
                     title='Full name',
                     table='v_users',
                     field='fullname',
                     img='guy16',
                     display=True,
                     _class="username",
                    ),
            'email': HtmlTableColumn(
                     title='Email',
                     table='v_users',
                     field='email',
                     img='guy16',
                     display=True,
                    ),
            'phone_work': HtmlTableColumn(
                     title='Work desk phone',
                     table='v_users',
                     field='phone_work',
                     img='guy16',
                     display=True,
                    ),
            'primary_group': HtmlTableColumn(
                     title='Primary group',
                     table='v_users',
                     field='primary_group',
                     img='guys16',
                     display=True,
                    ),
            'groups': HtmlTableColumn(
                     title='Groups',
                     table='v_users',
                     field='groups',
                     img='guys16',
                     display=True,
                     _class="groups",
                    ),
            'domains': HtmlTableColumn(
                     title='Domains',
                     table='v_users',
                     field='domains',
                     img='filter16',
                     display=True,
                     _class='users_domain',
                    ),
            'manager': HtmlTableColumn(
                     title='Role',
                     table='v_users',
                     field='manager',
                     img='guy16',
                     display=True,
                     _class='users_role',
                    ),
            'lock_filter': HtmlTableColumn(
                     title='Lock filterset',
                     table='v_users',
                     field='lock_filter',
                     img='attach16',
                     display=True,
                     _class='boolean',
                    ),
            'fset_name': HtmlTableColumn(
                     title='Filterset',
                     table='v_users',
                     field='fset_name',
                     img='filter16',
                     display=True,
                    ),
            'last': HtmlTableColumn(
                     title='Last events',
                     table='v_users',
                     field='last',
                     img='time16',
                     display=True,
                     _class="datetime_no_age",
                    ),
        }
        self.colprops['domains'].t = self
        self.ajax_col_values = 'ajax_users_col_values'
        self.dbfilterable = False
        self.dataable = True
        self.wsable = True
        self.checkboxes = True
        self.events = ["auth_user_change"]

@auth.requires_login()
def ajax_users_col_values():
    t = table_users('users', 'ajax_users')
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
    t = table_users('users', 'ajax_users')
    o = ~db.v_users.last
    q = db.v_users.id > 0
    for f in t.cols:
        q = _where(q, 'v_users', t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def users():
    t = table_users('users', 'ajax_users')
    d = DIV(
          t.html(),
          _id='users',
        )
    return dict(table=d)

def users_load():
    return users()["table"]

