def refresh_b_apps():
    try:
        sql = "drop table if exists b_apps_new"
        db.executesql(sql)
        sql = "create table b_apps_new like b_apps"
        db.executesql(sql)
        sql = "insert into b_apps_new select * from v_apps"
        db.executesql(sql)
        sql = "drop table if exists b_apps_old"
        db.executesql(sql)
        sql = "rename table b_apps to b_apps_old, b_apps_new to b_apps"
        db.executesql(sql)
    except:
        sql = "drop table if exists b_apps"
        db.executesql(sql)
        sql = """CREATE TABLE `b_apps` (
  `id` int(11) NOT NULL DEFAULT '0',
  `app` varchar(64) CHARACTER SET latin1 NOT NULL,
  `roles` varchar(342) DEFAULT NULL,
  `responsibles` varchar(342) DEFAULT NULL,
  `mailto` varchar(342) DEFAULT NULL,
  KEY `i_app` (`app`)
)
"""
        db.executesql(sql)
        sql = "insert into b_apps select * from v_apps"
        db.executesql(sql)
    db.commit()


class table_apps(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'app',
                     'app_domain',
                     'app_team_ops',
                     'roles',
                     'responsibles',
                     'mailto']
        self.keys = ['id']
        self.span = ['id']
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
            'roles': HtmlTableColumn(
                     table='v_apps',
                     field='roles',
                    ),
            'responsibles': HtmlTableColumn(
                     table='v_apps',
                     field='responsibles',
                    ),
            'mailto': HtmlTableColumn(
                     table='v_apps',
                     field='mailto',
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
    o = ~db.v_apps.app
    q = db.v_apps.id > 0
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

