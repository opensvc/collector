def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget(response)
    return service()

class table_checks(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['node_id',
                     'nodename',
                     'svc_id',
                     'svcname',
                     'chk_type',
                     'chk_instance',
                     'chk_value',
                     'chk_low',
                     'chk_high',
                     'chk_err',
                     'chk_threshold_provider',
                     'chk_created',
                     'chk_updated']
        self.colprops = {
            'svc_id': HtmlTableColumn(
                field = 'svc_id',
                table = 'checks_live',
            ),
            'node_id': HtmlTableColumn(
                field = 'node_id',
                table = 'checks_live',
            ),
            'nodename': HtmlTableColumn(
                field = 'nodename',
                table = 'nodes',
            ),
            'svcname': HtmlTableColumn(
                field = 'svcname',
                table = 'services',
            ),
            'chk_type': HtmlTableColumn(
                field = 'chk_type',
                table = 'checks_live',
            ),
            'chk_instance': HtmlTableColumn(
                field = 'chk_instance',
                table = 'checks_live',
            ),
            'chk_err': HtmlTableColumn(
                field = 'chk_err',
                table = 'checks_live',
            ),
            'chk_value': HtmlTableColumn(
                field = 'chk_value',
                table = 'checks_live',
            ),
            'chk_low': HtmlTableColumn(
                field = 'chk_low',
                table = 'checks_live',
            ),
            'chk_high': HtmlTableColumn(
                field = 'chk_high',
                table = 'checks_live',
            ),
            'chk_created': HtmlTableColumn(
                field = 'chk_created',
                table = 'checks_live',
            ),
            'chk_updated': HtmlTableColumn(
                field = 'chk_updated',
                table = 'checks_live',
            ),
            'chk_threshold_provider': HtmlTableColumn(
                field = 'chk_threshold_provider',
                table = 'checks_live',
            ),
        }
        self.colprops.update(nodes_colprops)
        self.cols += nodes_cols

        self.colprops.update({
            'app_domain': HtmlTableColumn(
                     field='app_domain',
                     table='apps',
                    ),
            'app_team_ops': HtmlTableColumn(
                     field='app_team_ops',
                     table='apps',
                    ),
        })
        self.cols.insert(self.cols.index('team_integ')+1, 'app_team_ops')
        self.cols.insert(self.cols.index('app')+1, 'app_domain')

        self.ajax_col_values = 'ajax_checks_col_values'

@auth.requires_login()
def ajax_checks_col_values():
    table_id = request.vars.table_id
    t = table_checks(table_id, 'ajax_checks')
    col = request.args[0]
    q = q_filter(node_field=db.checks_live.node_id)
    q = apply_filters_id(q, db.checks_live.node_id, None)
    q &= db.checks_live.node_id==db.nodes.node_id
    j = db.apps.app == db.nodes.app
    l1 = db.apps.on(j)
    l2 = db.services.on(db.checks_live.svc_id==db.services.svc_id)

    o = db[t.colprops[col].table][col]
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, left=(l1,l2))
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_checks():
    table_id = request.vars.table_id
    t = table_checks(table_id, 'ajax_checks')

    o = t.get_orderby(default=db.nodes.nodename|db.checks_live.chk_type|db.checks_live.chk_instance)
    q = q_filter(node_field=db.checks_live.node_id)
    q = apply_filters_id(q, db.checks_live.node_id)
    q &= db.checks_live.node_id==db.nodes.node_id
    j = db.apps.app == db.nodes.app
    l1 = db.apps.on(j)
    l2 = db.services.on(db.checks_live.svc_id==db.services.svc_id)

    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        t.csv_limit = 15000
        t.csv_left = (l1,l2)
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        t.csv_left = (l1,l2)
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.checks_live.id.count(), left=(l1,l2)).first()(db.checks_live.id.count())
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, limitby=limitby, orderby=o, cacheable=False, left=(l1,l2))
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def checks():
    t = SCRIPT(
          """table_checks("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def checks_load():
    return checks()["table"]

#
@auth.requires_login()
def checks_defaults():
    t = SCRIPT(
          """table_checks_defaults("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def checks_defaults_load():
    return checks_defaults()["table"]

#
def batch_update_thresholds():
    update_thresholds_batch()

@auth.requires_login()
@service.json
def json_check_value_log():
    import base64
    from applications.init.modules import timeseries
    q = db.checks_live.node_id == request.vars.node_id
    q &= db.checks_live.svc_id == request.vars.svc_id
    q &= db.checks_live.chk_type == request.vars.chk_type
    q &= db.checks_live.chk_instance == request.vars.chk_instance
    q = q_filter(node_field=db.checks_live.node_id)
    n = db(q).count()
    if n == 0:
        return "Permission denied"

    return [timeseries.whisper_fetch(
        "nodes", request.vars.node_id,
        "checks", ":".join((
            request.vars.svc_id if request.vars.svc_id else "",
            request.vars.chk_type,
            base64.urlsafe_b64encode(request.vars.chk_instance) if request.vars.chk_instance else "",
        )),
        b=request.vars.b,
        e=request.vars.e,
    )]

