def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

@service.json
def json_action_queue_stats():
    return action_queue_ws_data()

class table_actions(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'status',
                     'node_id',
                     'nodename',
                     'svc_id',
                     'svcname',
                     'connect_to',
                     'username',
                     'form_id',
                     'action_type',
                     'date_queued',
                     'date_dequeued',
                     'ret',
                     'command',
                     'stdout',
                     'stderr']
        self.colprops = {
            'id': HtmlTableColumn(
                     field='id',
                     table='v_action_queue',
                    ),
            'form_id': HtmlTableColumn(
                     field='form_id',
                     table='v_action_queue',
                    ),
            'status': HtmlTableColumn(
                     field='status',
                     table='v_action_queue',
                    ),
            'ret': HtmlTableColumn(
                     field='ret',
                     table='v_action_queue',
                    ),
            'date_queued': HtmlTableColumn(
                     field='date_queued',
                     table='v_action_queue',
                    ),
            'date_dequeued': HtmlTableColumn(
                     field='date_dequeued',
                     table='v_action_queue',
                    ),
            'node_id': HtmlTableColumn(
                     field='node_id',
                     table='v_action_queue',
                    ),
            'nodename': HtmlTableColumn(
                     field='nodename',
                     table='v_action_queue',
                    ),
            'svc_id': HtmlTableColumn(
                     field='svc_id',
                     table='v_action_queue',
                    ),
            'svcname': HtmlTableColumn(
                     field='svcname',
                     table='v_action_queue',
                    ),
            'username': HtmlTableColumn(
                     field='username',
                     table='v_action_queue',
                    ),
            'action_type': HtmlTableColumn(
                     field='action_type',
                     table='v_action_queue',
                    ),
            'connect_to': HtmlTableColumn(
                     field='connect_to',
                     table='v_action_queue',
                    ),
            'command': HtmlTableColumn(
                     field='command',
                     table='v_action_queue',
                    ),
            'stdout': HtmlTableColumn(
                     field='stdout',
                     table='v_action_queue',
                    ),
            'stderr': HtmlTableColumn(
                     field='stderr',
                     table='v_action_queue',
                    ),
        }
        self.ajax_col_values = 'ajax_actions_col_values'


@auth.requires_login()
def ajax_actions_col_values():
    table_id = request.vars.table_id
    t = table_actions(table_id, 'ajax_actions')
    col = request.args[0]
    o = db['v_action_queue'][col]
    q = q_filter(node_field=db.v_action_queue.node_id)
    for f in t.cols:
        q = _where(q, 'v_action_queue', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_actions():
    table_id = request.vars.table_id
    t = table_actions(table_id, 'ajax_actions')
    o = t.get_orderby(default=~db.v_action_queue.id)
    q = q_filter(node_field=db.v_action_queue.node_id)
    for f in t.cols:
        q = _where(q, 'v_action_queue', t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        return t.csv()

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        t.object_list = db(q).select(limitby=limitby, orderby=o, cacheable=False)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def action_queue():
    t = SCRIPT(
          """table_action_queue("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

