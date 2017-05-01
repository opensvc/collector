class table_apps(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'app',
                     'app_domain',
                     'app_team_ops',
                     'publications',
                     'responsibles',
                    ]
        self.colprops = {
            'id': HtmlTableColumn(
                     table='v_apps',
                     field='id',
                    ),
            'app': HtmlTableColumn(
                     table='v_apps',
                     field='app',
                    ),
            'app_domain': HtmlTableColumn(
                     table='v_apps',
                     field='app_domain',
                    ),
            'app_team_ops': HtmlTableColumn(
                     table='v_apps',
                     field='app_team_ops',
                    ),
            'publications': HtmlTableColumn(
                     table='v_apps',
                     field='publications',
                    ),
            'responsibles': HtmlTableColumn(
                     table='v_apps',
                     field='responsibles',
                    ),
        }
        self.ajax_col_values = 'ajax_apps_col_values'

@auth.requires_login()
def ajax_apps_col_values():
    table_id = request.vars.table_id
    t = table_apps(table_id, 'ajax_apps')
    col = request.args[0]
    o = db.v_apps[col]
    q = db.v_apps.id > 0
    t.object_list = db(q).select(orderby=o, groupby=o)
    for f in t.cols:
        q = _where(q, 'v_apps', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_apps():
    table_id = request.vars.table_id
    t = table_apps(table_id, 'ajax_apps')
    o = t.get_orderby(default=~db.v_apps.app)
    q = db.v_apps.id > 0
    if not "Manager" in user_groups():
        q &= db.v_apps.id.belongs(user_app_ids())
    for f in t.cols:
        q = _where(q, 'v_apps', t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, groupby=o, limitby=limitby, cacheable=True)
        return t.table_lines_data(n, html=False)


@auth.requires_login()
def apps():
    t = SCRIPT(
          """table_apps("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def apps_load():
    return apps()["table"]

