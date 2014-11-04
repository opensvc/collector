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
    data = {}
    sql = """select
              (select count(id) from action_queue where status in ('Q', 'W', 'R')) as queued,
              (select count(id) from action_queue where ret!=0) as ko,
              (select count(id) from action_queue where ret=0 and status='T') as ok
          """
    data = db.executesql(sql, as_dict=True)[0]
    return data

class table_actions(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'status',
                     'nodename',
                     'svcname',
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
                    ),
            'date_dequeued': HtmlTableColumn(
                     title='Dequeued',
                     field='date_dequeued',
                     img='time16',
                     display=True,
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
            'command': HtmlTableColumn(
                     title='Commande',
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
        self.additional_tools.append('cancel_actions')
        self.dataable = True
        self.wsable = True

    def cancel_actions(self):
        d = DIV(
              A(
                T("Cancel actions"),
                _class='del16',
                _onclick=self.ajax_submit(args=['cancel_actions']),
              ),
              _class='floatw',
            )
        return d


@auth.requires_login()
def cancel_actions(ids):
    if len(ids) == 0:
        raise ToolError("No actions selected")

    q = db.action_queue.id.belongs(ids)
    q &= db.action_queue.status != 'T'
    if 'Manager' not in user_groups():
        q &= db.action_queue.user_id == auth.user_id
    rows = db(q).select(db.action_queue.id, db.action_queue.command)
    if len(rows) == 0:
        return
    u = ', '.join([r.command for r in rows])

    ids = [r.id for r in rows]
    q = db.action_queue.id.belongs(ids)
    db(q).update(status='C')

    _log('action.delete',
         'deleted actions %(u)s',
         dict(u=u))

@auth.requires_login()
def ajax_actions_col_values():
    t = table_actions('action_queue', 'ajax_actions')
    col = request.args[0]
    o = db['v_action_queue'][col]
    q = db.v_action_queue.id > 0
    for f in t.cols:
        q = _where(q, 'v_action_queue', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_actions():
    t = table_actions('action_queue', 'ajax_actions')

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'cancel_actions':
                cancel_actions(t.get_checked())
        except ToolError, e:
            t.flash = str(e)

    o = ~db.v_action_queue.id

    q = db.v_action_queue.id>0
    for f in t.cols:
        q = _where(q, 'v_action_queue', t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'data':
        if request.vars.volatile_filters is None:
            n = db(q).count()
            limitby = (t.pager_start,t.pager_end)
        else:
            n = 0
            limitby = (0, 500)
        t.object_list = db(q).select(limitby=limitby, orderby=o, cacheable=False)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def action_queue():
    t = table_actions('action_queue', 'ajax_actions')
    t = DIV(
          t.html(),
          SCRIPT("""
function ws_action_switch_%(divid)s(data) {
        if (data["event"] == "action_q_change") {
          osvc.tables["%(divid)s"].refresh()
        }
}
wsh["%(divid)s"] = ws_action_switch_%(divid)s
         """ % dict(divid=t.innerhtml),
          ),
          _id='action_queue',
        )
    return dict(table=t)

