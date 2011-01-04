class table_actions(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id', 'status', 'date_queued', 'date_dequeued', 'command']
        self.colprops = {
            'id': HtmlTableColumn(
                     title='Id',
                     field='id',
                     img='action16',
                     display=False,
                    ),
            'status': HtmlTableColumn(
                     title='Status',
                     field='status',
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
            'command': HtmlTableColumn(
                     title='Commande',
                     field='command',
                     img='action16',
                     display=True,
                    ),
        }
        self.dbfilterable = False
        self.filterable = False
        self.pageable = False

@auth.requires_login()
def ajax_actions():
    t = table_actions('action_queue', 'ajax_actions')
    o = ~db.action_queue.id

    q = db.action_queue.id>0
    t.object_list = db(q).select(orderby=o)
    return t.html()

