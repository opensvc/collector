@auth.requires_login()
def alerts():
    columns = dict(
        id = dict(
            pos = 1,
            title = T('Alert Id'),
            img = '',
            size = 3
        ),
        sent_at = dict(
            pos = 4,
            title = T('Sent at'),
            img = '',
            size = 10
        ),
        sent_to = dict(
            pos = 5,
            title = T('Assigned to'),
            img = '',
            size = 7
        ),
        subject = dict(
            pos = 6,
            title = T('Subject'),
            img = '',
            size = 30
        ),
        body = dict(
            pos = 7,
            title = T('Description'),
            img = '',
            size = 30
        ),
    )
    def _sort_cols(x, y):
        return cmp(columns[x]['pos'], columns[y]['pos'])
    colkeys = columns.keys()
    colkeys.sort(_sort_cols)

    query = _where(None, 'alerts', request.vars.id, 'id')
    query &= _where(None, 'alerts', request.vars.sent_at, 'sent_at')
    query &= _where(None, 'alerts', request.vars.responsibles, 'responsibles')
    query &= _where(None, 'alerts', request.vars.subject, 'subject')
    query &= _where(None, 'alerts', request.vars.body, 'body')
    query &= _where(None, 'alerts', domain_perms(), 'domain')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select(orderby=~db.alerts.id)
    else:
        rows = db(query).select(limitby=(start,end), orderby=~db.alerts.id)

    return dict(alerts=rows,
                nav=nav,
                columns=columns, colkeys=colkeys)


