class table_scheduler_tasks(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = [
            'id',
            'function_name',
            'status',
            'period',
            'next_run_time',
            'last_run_time',
            'times_run',
            'times_failed',
        ]
        self.colprops = {
            'id': HtmlTableColumn(
                field='id',
                table = 'scheduler_task',
            ),
            'function_name': HtmlTableColumn(
                field='function_name',
                table = 'scheduler_task',
            ),
            'status': HtmlTableColumn(
                field='status',
                table = 'scheduler_task',
            ),
            'period': HtmlTableColumn(
                field='period',
                table = 'scheduler_task',
            ),
            'next_run_time': HtmlTableColumn(
                field='next_run_time',
                table = 'scheduler_task',
            ),
            'last_run_time': HtmlTableColumn(
                field='last_run_time',
                table = 'scheduler_task',
            ),
            'times_run': HtmlTableColumn(
                field='times_run',
                table = 'scheduler_task',
            ),
            'times_failed': HtmlTableColumn(
                field='times_failed',
                table = 'scheduler_task',
            ),
        }
        self.ajax_col_values = 'ajax_scheduler_tasks_col_values'

@auth.requires_login()
def ajax_scheduler_tasks_col_values():
    table_id = request.vars.table_id
    t = table_scheduler_tasks(table_id, 'ajax_scheduler_tasks')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = None
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o,
                                 db.scheduler_task.id.count(),
                                 groupby=o,
                                 orderby=~db.scheduler_task.id.count(),
                                 left=l)
    return t.col_values_cloud_grouped(col)

@auth.requires_login()
def ajax_scheduler_tasks():
    table_id = request.vars.table_id
    t = table_scheduler_tasks(table_id, 'ajax_scheduler_tasks')
    o = t.get_orderby(default=db.scheduler_task.id)

    q = db.scheduler_task.id>0
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.scheduler_task.id.count()).first()(db.scheduler_task.id.count())
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def scheduler_tasks():
    t = SCRIPT(
          """table_scheduler_tasks("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def scheduler_tasks_load():
    return scheduler_tasks()["table"]

