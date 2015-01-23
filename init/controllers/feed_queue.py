import cPickle

class col_q_args(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        try:
            s = cPickle.loads(s)
        except:
            pass
        return PRE(s)

class table_feed_queue(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'q_fn',
                     'q_args',
                     'created']
        self.colprops = {
            'id': HtmlTableColumn(
                     title='Id',
                     field='id',
                     img='action16',
                     display=False,
                    ),
            'q_fn': HtmlTableColumn(
                     title='Function',
                     field='q_fn',
                     img='action16',
                     display=True,
                    ),
            'q_args': col_q_args(
                     title='Arguments',
                     field='q_args',
                     img='action16',
                     display=True,
                    ),
            'created': HtmlTableColumn(
                     title='Queued',
                     field='created',
                     img='time16',
                     display=True,
                    ),
        }
        for col in self.cols:
            self.colprops[col].t = self
        self.dbfilterable = False
        self.checkboxes = True
        self.ajax_col_values = 'ajax_feed_queue_col_values'
        self.additional_tools.append('delete_entry')

    def delete_entry(self):
        d = DIV(
              A(
                T("Delete entries"),
                _class='del16',
                _onclick=self.ajax_submit(args=['delete_entry']),
              ),
              _class='floatw',
            )
        return d


@auth.requires_login()
def delete_entry(ids):
    if len(ids) == 0:
        raise ToolError("No actions selected")
    if 'Manager' not in user_groups():
        raise ToolError("Insufficent privileges to execute this action")

    q = db.feed_queue.id.belongs(ids)
    rows = db(q).select(db.feed_queue.q_fn, cacheable=True)
    if len(rows) == 0:
        return
    u = ', '.join(set([r.q_fn for r in rows]))

    db(q).delete()

    _log('feed.delete',
         'deleted %(n)d feed queue %(u)s entries',
         dict(n=len(rows), u=u))

@auth.requires_login()
def ajax_feed_queue_col_values():
    t = table_feed_queue('feed_queue', 'ajax_feed_queue')
    col = request.args[0]
    o = db['feed_queue'][col]
    q = db.feed_queue.id > 0
    for f in t.cols:
        q = _where(q, 'feed_queue', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_feed_queue():
    t = table_feed_queue('feed_queue', 'ajax_feed_queue')

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'delete_entry':
                delete_entry(t.get_checked())
        except ToolError, e:
            t.flash = str(e)

    o = ~db.feed_queue.id

    q = db.feed_queue.id>0
    for f in t.cols:
        q = _where(q, 'feed_queue', t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'line':
        if request.vars.volatile_filters is None:
            n = db(q).count()
            t.setup_pager(n)
            limitby = (t.pager_start,t.pager_end)
        else:
            n = 0
            limitby = (0, 500)
        t.object_list = db(q).select(limitby=limitby, orderby=o, cacheable=False)
        return t.table_lines_data(n)

    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(orderby=o, cacheable=True)

    return t.html()

@auth.requires_login()
def feed_queue():
    t = DIV(
          ajax_feed_queue(),
          _id='feed_queue',
        )
    return dict(table=t)

