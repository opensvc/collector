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
                     title='Id',
                     field='id',
                     img='action16',
                     display=False,
                    ),
            'form_id': HtmlTableColumn(
                     title='Request form id',
                     field='form_id',
                     img='wf16',
                     display=True,
                     _class='form_id',
                    ),
            'status': HtmlTableColumn(
                     title='Status',
                     field='status',
                     img='action16',
                     display=True,
                     _class='action_q_status',
                    ),
            'ret': HtmlTableColumn(
                     title='Return code',
                     field='ret',
                     img='action16',
                     display=True,
                     _class='action_q_ret',
                    ),
            'date_queued': HtmlTableColumn(
                     title='Queued',
                     field='date_queued',
                     img='time16',
                     display=True,
                     _class="datetime_no_age",
                    ),
            'date_dequeued': HtmlTableColumn(
                     title='Dequeued',
                     field='date_dequeued',
                     img='time16',
                     display=True,
                     _class="datetime_no_age",
                    ),
            'nodename': HtmlTableColumn(
                     title='Nodename',
                     field='nodename',
                     img='hw16',
                     display=True,
                     _class='nodename',
                    ),
            'svcname': HtmlTableColumn(
                     title='Service',
                     field='svcname',
                     img='svc',
                     display=True,
                     _class='svcname',
                    ),
            'username': HtmlTableColumn(
                     title='User name',
                     field='username',
                     img='guy16',
                     display=True,
                     _class='username',
                    ),
            'action_type': HtmlTableColumn(
                     title='Action type',
                     field='action_type',
                     img='action16',
                     display=True,
                    ),
            'connect_to': HtmlTableColumn(
                     title='Connect to',
                     field='connect_to',
                     img='net16',
                     display=True,
                    ),
            'command': HtmlTableColumn(
                     title='Command',
                     field='command',
                     img='action16',
                     display=True,
                    ),
            'stdout': HtmlTableColumn(
                     title='Stdout',
                     field='stdout',
                     img='action16',
                     display=True,
                     _class='pre',
                    ),
            'stderr': HtmlTableColumn(
                     title='Stderr',
                     field='stderr',
                     img='action16',
                     display=True,
                     _class='pre',
                    ),
        }
        for col in self.cols:
            self.colprops[col].t = self
        self.keys = ["id"]
        self.span = ["id"]
        self.dbfilterable = False
        self.extraline = True
        self.checkboxes = True
        self.ajax_col_values = 'ajax_actions_col_values'
        self.dataable = True
        self.wsable = True
        self.events = ["action_q_change"]


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

