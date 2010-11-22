class col_alerts_body(HtmlTableColumn):
    def html(self, o):
       return XML(self.get(o))

class table_alerts(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'sent_at',
                     'sent_to',
                     'subject',
                     'body']
        self.colprops = {
            'id': HtmlTableColumn(
                     title='Alert Id',
                     field='id',
                     img='mail16',
                     display=False,
                    ),
            'sent_at': HtmlTableColumn(
                     title='Sent at',
                     field='sent_at',
                     img='time16',
                     display=True,
                    ),
            'sent_to': HtmlTableColumn(
                     title='Assigned to',
                     field='sent_to',
                     img='guy16',
                     display=True,
                    ),
            'subject': HtmlTableColumn(
                     title='Subject',
                     field='subject',
                     img='mail16',
                     display=True,
                    ),
            'body': col_alerts_body(
                     title='Description',
                     field='body',
                     img='guy16',
                     display=True,
                    ),
        }
        self.dbfilterable = False
        self.ajax_col_values = 'ajax_alerts_col_values'


@auth.requires_login()
def ajax_alerts_col_values():
    t = table_alerts('alerts', 'ajax_alerts')
    col = request.args[0]
    o = db.alerts[col]
    q = _where(None, 'alerts', domain_perms(), 'domain')
    t.object_list = db(q).select(orderby=o, groupby=o)
    for f in t.cols:
        q = _where(q, 'alerts', t.filter_parse(f), f)
    t.object_list = db(q).select(orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_alerts():
    t = table_alerts('alerts', 'ajax_alerts')
    o = ~db.alerts.sent_at
    q = _where(None, 'alerts', domain_perms(), 'domain')
    for f in t.cols:
        q = _where(q, 'alerts', t.filter_parse(f), f)
    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return t.html()

@auth.requires_login()
def alerts():
    t = DIV(
          ajax_alerts(),
          _id='alerts',
        )
    return dict(table=t)


