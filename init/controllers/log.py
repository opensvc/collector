class table_log(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'log_date',
                     'log_icons',
                     'log_level',
                     'svc_id',
                     'svcname',
                     'node_id',
                     'nodename',
                     'node_app',
                     'log_user',
                     'log_action',
                     'log_evt',
                     'log_fmt',
                     'log_dict',
                     'log_gtalk_sent',
                     'log_email_sent']
        self.colprops = {
            'id': HtmlTableColumn(
                     table='log',
                     field='id',
                    ),
            'svc_id': HtmlTableColumn(
                     table='log',
                     field='svc_id',
                    ),
            'node_id': HtmlTableColumn(
                     table='log',
                     field='node_id',
                    ),
            'node_app': HtmlTableColumn(
                     table='nodes',
                     field='app',
                    ),
            'nodename': HtmlTableColumn(
                     table='nodes',
                     field='nodename',
                    ),
            'log_date': HtmlTableColumn(
                     table='log',
                     field='log_date',
                    ),
            'log_icons': HtmlTableColumn(
                     table='log',
                     field='log_icons',
                    ),
            'log_level': HtmlTableColumn(
                     table='log',
                     field='log_level',
                    ),
            'log_action': HtmlTableColumn(
                     table='log',
                     field='log_action',
                    ),
            'svcname': HtmlTableColumn(
                     table='services',
                     field='svcname',
                    ),
            'log_user': HtmlTableColumn(
                     table='log',
                     field='log_user',
                    ),
            'log_evt': HtmlTableColumn(
                     table='log',
                     field='dummy',
                     filter_redirect='log_dict',
                    ),
            'log_fmt': HtmlTableColumn(
                     table='log',
                     field='log_fmt',
                    ),
            'log_dict': HtmlTableColumn(
                     table='log',
                     field='log_dict',
                    ),
            'log_entry_id': HtmlTableColumn(
                     table='log',
                     field='log_entry_id',
                    ),
            'log_gtalk_sent': HtmlTableColumn(
                     table='log',
                     field='log_gtalk_sent',
                    ),
            'log_email_sent': HtmlTableColumn(
                     table='log',
                     field='log_email_sent',
                    ),
        }
        self.ajax_col_values = 'ajax_log_col_values'

@auth.requires_login()
def ajax_log_col_values():
    table_id = request.vars.table_id
    t = table_log(table_id, 'ajax_log')
    col = request.args[0]
    if t.colprops[col].filter_redirect is None:
        o = db[t.colprops[col].table][t.colprops[col].field]
        s = [db[t.colprops[col].table][t.colprops[col].field]]
    else:
        o = db.log[t.colprops[col].filter_redirect]
        s = [db.log.log_fmt, db.log.log_dict]
    s += [db.log.id.count()]
    q = db.log.id > 0
    l1 = db.nodes.on(db.log.node_id == db.nodes.node_id)
    l2 = db.services.on(db.log.svc_id == db.services.svc_id)
    f1 = q_filter(q, app_field=db.nodes.app)
    f2 = q_filter(q, app_field=db.services.svc_app)
    q &= (f1|f2)
    for f in set(t.cols)-set(['log_evt']):
        q = _where(q, t.colprops[f].table, t.filter_parse(f),  f)
    q = _where(q, 'log', t.filter_parse('log_evt'),  'log_dict')
    t.object_list = db(q).select(*s,
                                 orderby=~db.log.id.count(),
                                 groupby=o,
                                 left=(l1,l2))
    return t.col_values_cloud_grouped(col)

@auth.requires_login()
def ajax_log():
    table_id = request.vars.table_id
    t = table_log(table_id, 'ajax_log')

    o = ~db.log.log_date
    q = db.log.id > 0
    l1 = db.nodes.on(db.log.node_id == db.nodes.node_id)
    l2 = db.services.on(db.log.svc_id == db.services.svc_id)
    f1 = q_filter(q, app_field=db.nodes.app)
    f2 = q_filter(q, app_field=db.services.svc_app)
    q &= (f1|f2)
    for f in set(t.cols):
        q = _where(q, t.colprops[f].table, t.filter_parse(f),  f if t.colprops[f].filter_redirect is None else t.colprops[f].filter_redirect)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_left = (l1,l2)
        t.csv_orderby = o
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        t.csv_left = (l1,l2)
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.log.id.count()).first()._extra[db.log.id.count()]
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, limitby=limitby, orderby=o, left=(l1,l2), cacheable=False)
        return t.table_lines_data(n)

@auth.requires_login()
def log():
    t = SCRIPT(
          """table_log("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def log_load():
    return log()["table"]


