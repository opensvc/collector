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
                     'nodename',
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
                    ),
            'form_id': HtmlTableColumn(
                     field='form_id',
                    ),
            'status': HtmlTableColumn(
                     field='status',
                    ),
            'ret': HtmlTableColumn(
                     field='ret',
                    ),
            'date_queued': HtmlTableColumn(
                     field='date_queued',
                    ),
            'date_dequeued': HtmlTableColumn(
                     field='date_dequeued',
                    ),
            'nodename': HtmlTableColumn(
                     field='nodename',
                    ),
            'svcname': HtmlTableColumn(
                     field='svcname',
                    ),
            'username': HtmlTableColumn(
                     field='username',
                    ),
            'action_type': HtmlTableColumn(
                     field='action_type',
                    ),
            'connect_to': HtmlTableColumn(
                     field='connect_to',
                    ),
            'command': HtmlTableColumn(
                     field='command',
                    ),
            'stdout': HtmlTableColumn(
                     field='stdout',
                    ),
            'stderr': HtmlTableColumn(
                     field='stderr',
                    ),
        }
        self.keys = ["id"]
        self.span = ["id"]
        self.ajax_col_values = 'ajax_actions_col_values'


@auth.requires_login()
def ajax_actions_col_values():
    table_id = request.vars.table_id
    t = table_actions(table_id, 'ajax_actions')
    col = request.args[0]
    o = db['v_action_queue'][col]
    q = db.v_action_queue.id > 0
    for f in t.cols:
        q = _where(q, 'v_action_queue', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_actions():
    table_id = request.vars.table_id
    t = table_actions(table_id, 'ajax_actions')
    o = ~db.v_action_queue.id
    q = db.v_action_queue.id>0
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

