class col_form_id(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        return A(s, _href=URL(c='forms', f='workflow', vars={'wfid': s}))

class col_std(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        return PRE(s)

class col_ret(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        if s == 0:
            return DIV(s, _class="boxed_small bggreen")
        return DIV(s, _class="boxed_small bgred")

class col_action_status(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        if s == 'T':
            return DIV(T('done'), _class="boxed_small bggreen")
        elif s == 'R':
            return DIV(T('running'), _class="boxed_small bgred")
        elif s == 'W':
            return DIV(T('waiting'), _class="boxed_small")
        elif s == 'Q':
            return DIV(T('queued'), _class="boxed_small")
        elif s == 'C':
            return DIV(T('cancelled'), _class="boxed_small bgdarkred")
        else:
            return DIV(s, _class="boxed_small")

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
            'form_id': col_form_id(
                     title='Request form id',
                     field='form_id',
                     img='wf16',
                     display=True,
                    ),
            'status': col_action_status(
                     title='Status',
                     field='status',
                     img='action16',
                     display=True,
                    ),
            'ret': col_ret(
                     title='Return code',
                     field='ret',
                     img='action16',
                     display=True,
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
            'stdout': col_std(
                     title='Stdout',
                     field='stdout',
                     img='action16',
                     display=True,
                    ),
            'stderr': col_std(
                     title='Stderr',
                     field='stderr',
                     img='action16',
                     display=True,
                    ),
        }
        for col in self.cols:
            self.colprops[col].t = self
        self.dbfilterable = False
        self.extraline = True
        self.checkboxes = True
        self.ajax_col_values = 'ajax_actions_col_values'
        self.additional_tools.append('cancel_actions')

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

    if len(request.args) == 1 and request.args[0] == 'line':
        if request.vars.volatile_filters is None:
            n = db(q).count()
            t.setup_pager(n)
            limitby = (t.pager_start,t.pager_end)
        else:
            limitby = (0, 500)
        t.object_list = db(q).select(limitby=limitby, orderby=o, cacheable=False)
        t.set_column_visibility()
        return TABLE(t.table_lines()[0])

    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(orderby=o, cacheable=True)
    return t.html()

@auth.requires_login()
def action_queue():
    t = DIV(
          ajax_actions(),
          _id='action_queue',
        )
    return dict(table=t)

