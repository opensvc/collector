def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget(response)
    return service()

@auth.requires_login()
@service.json
def json_appinfo_log():
    q = db.appinfo_log.app_nodename == request.vars.nodename
    q &= db.appinfo_log.app_svcname == request.vars.svcname
    q &= db.appinfo_log.app_launcher == request.vars.launcher
    q &= db.appinfo_log.app_key == request.vars.key

    # permission validation
    if 'Manager' not in user_groups():
        q1 = db.appinfo_log.app_svcname == db.services.svc_name
        q1 &= db.services.svc_app == db.apps.app
        q1 &= db.apps.id == db.apps_responsibles.app_id
        q1 &= db.apps_responsibles.group_id.belongs(user_group_ids())
        n = db(q&q1).count()
        if n == 0:
            return "Permission denied"

    rows = db(q).select(db.appinfo_log.app_updated,
                        db.appinfo_log.app_value)
    data = []
    for row in rows:
        data.append([row.app_updated, row.app_value])
    return [data]

@auth.requires_login()
def ajax_appinfo_log():
    session.forget(response)
    row_id = request.vars.rowid
    id = 'chart_'+row_id

    return TABLE(
      H3(T("History of key '%(key)s' from launcher '%(launcher)s'", dict(launcher=request.vars.launcher, key=request.vars.key))),
      DIV(
        _id=id,
      ),
      SCRIPT(
       "stats_appinfo('%(url)s', '%(id)s');"%dict(
              id=id,
              url=URL(r=request,
                      f='call/json/json_appinfo_log',
                      vars={'svcname': request.vars.svcname,
                            'nodename': request.vars.nodename,
                            'launcher': request.vars.launcher,
                            'key': request.vars.key},
                  )
            ),
        _name='%s_to_eval'%row_id,
      ),
    )

class table_appinfo(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'app_svcname',
                     'app_nodename',
                     'app_launcher',
                     'app_key',
                     'app_value',
                     'app_updated']
        self.colprops = {
            'id': HtmlTableColumn(
                     table='appinfo',
                     field='id',
                    ),
            'app_svcname': HtmlTableColumn(
                     table='appinfo',
                     field='app_svcname',
                    ),
            'app_nodename': HtmlTableColumn(
                     table='appinfo',
                     field='app_nodename',
                    ),
            'app_launcher': HtmlTableColumn(
                     table='appinfo',
                     field='app_launcher',
                    ),
            'app_key': HtmlTableColumn(
                     table='appinfo',
                     field='app_key',
                    ),
            'app_value': HtmlTableColumn(
                     table='appinfo',
                     field='app_value',
                    ),
            'app_updated': HtmlTableColumn(
                     table='appinfo',
                     field='app_updated',
                    ),
        }
        self.ajax_col_values = 'ajax_appinfo_col_values'
        self.span = ['app_svcname', 'app_nodename', 'app_launcher']

@auth.requires_login()
def ajax_appinfo_col_values():
    table_id = request.vars.table_id
    t = table_appinfo(table_id, 'ajax_appinfo')
    col = request.args[0]
    o = db.appinfo[col]
    q = q_filter(svc_field=db.appinfo.app_svcname)
    q = apply_filters(q, None, db.appinfo.app_svcname)

    for f in t.cols:
        q = _where(q, 'appinfo', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_appinfo():
    table_id = request.vars.table_id
    t = table_appinfo(table_id, 'ajax_appinfo')

    o = db.appinfo.app_svcname | db.appinfo.app_nodename | db.appinfo.app_launcher | db.appinfo.app_key
    q = q_filter(svc_field=db.appinfo.app_svcname)
    q = apply_filters(q, None, db.appinfo.app_svcname)

    for f in set(t.cols):
        q = _where(q, 'appinfo', t.filter_parse(f), f)

    t.csv_q = q
    t.csv_orderby = o

    if len(request.args) == 1 and request.args[0] == 'csv':
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def appinfo():
    t = SCRIPT(
          """table_appinfo("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def appinfo_load():
    return appinfo()["table"]

