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
def json_resinfo_log():
    q = db.resinfo_log.node_id == request.vars.node_id
    q &= db.resinfo_log.svc_id == request.vars.svc_id
    q &= db.resinfo_log.rid == request.vars.rid
    q &= db.resinfo_log.res_key == request.vars.key

    # permission validation
    if 'Manager' not in user_groups():
        q1 = db.resinfo_log.svc_id == db.services.svc_id
        q1 &= db.services.svc_app == db.apps.app
        q1 &= db.apps.id == db.apps_responsibles.app_id
        q1 &= db.apps_responsibles.group_id.belongs(user_group_ids())
        n = db(q&q1).count()
        if n == 0:
            return "Permission denied"

    rows = db(q).select(db.resinfo_log.updated,
                        db.resinfo_log.res_value)
    data = []
    for row in rows:
        data.append([row.updated, row.res_value])
    return [data]

@auth.requires_login()
def ajax_resinfo_log():
    session.forget(response)
    row_id = request.vars.rowid
    id = 'chart_'+row_id

    return DIV(
      H3(T("History of key '%(key)s' from rid '%(rid)s'", dict(rid=request.vars.rid, key=request.vars.key))),
      DIV(
        _id=id,
      ),
      SCRIPT(
       "stats_resinfo('%(url)s', '%(id)s');"%dict(
              id=id,
              url=URL(r=request,
                      f='call/json/json_resinfo_log',
                      vars={'svc_id': request.vars.svc_id,
                            'node_id': request.vars.node_id,
                            'rid': request.vars.rid,
                            'key': request.vars.key},
                  )
            ),
        _name='%s_to_eval'%row_id,
      ),
      _class="p-3",
    )

class table_resinfo(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'svc_id',
                     'svcname',
                     'node_id',
                     'nodename',
                     'rid',
                     'res_key',
                     'res_value',
                     'updated']
        self.colprops = {
            'id': HtmlTableColumn(
                     table='resinfo',
                     field='id',
                    ),
            'svc_id': HtmlTableColumn(
                     table='resinfo',
                     field='svc_id',
                    ),
            'svcname': HtmlTableColumn(
                     table='services',
                     field='svcname',
                    ),
            'node_id': HtmlTableColumn(
                     table='resinfo',
                     field='node_id',
                    ),
            'nodename': HtmlTableColumn(
                     table='nodes',
                     field='nodename',
                    ),
            'rid': HtmlTableColumn(
                     table='resinfo',
                     field='rid',
                    ),
            'res_key': HtmlTableColumn(
                     table='resinfo',
                     field='res_key',
                    ),
            'res_value': HtmlTableColumn(
                     table='resinfo',
                     field='res_value',
                    ),
            'updated': HtmlTableColumn(
                     table='resinfo',
                     field='updated',
                    ),
        }
        self.ajax_col_values = 'ajax_resinfo_col_values'

@auth.requires_login()
def ajax_resinfo_col_values():
    table_id = request.vars.table_id
    t = table_resinfo(table_id, 'ajax_resinfo')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.resinfo.node_id == db.nodes.node_id
    q &= db.resinfo.svc_id == db.services.svc_id
    q = q_filter(q, svc_field=db.resinfo.svc_id)
    q = apply_filters_id(q, svc_field=db.resinfo.svc_id)

    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_resinfo():
    table_id = request.vars.table_id
    t = table_resinfo(table_id, 'ajax_resinfo')

    o = t.get_orderby(default=db.services.svcname|db.nodes.nodename|db.resinfo.rid|db.resinfo.res_key)
    q = db.resinfo.node_id == db.nodes.node_id
    q &= db.resinfo.svc_id == db.services.svc_id
    q = q_filter(q, svc_field=db.resinfo.svc_id)
    q = apply_filters_id(q, svc_field=db.resinfo.svc_id)

    for f in set(t.cols):
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

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
def resinfo():
    t = SCRIPT(
          """table_resinfo("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def resinfo_load():
    return resinfo()["table"]

