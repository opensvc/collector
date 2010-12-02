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
def json_stat_os_release():
    os_name = request.vars.os_name
    if os_name is None or os_name == "":
        return [[], []]

    today = datetime.datetime.today().toordinal()
    o = db.lifecycle_os.lc_date
    q = db.lifecycle_os.lc_os_name==os_name
    rows = db(q).select(orderby=o)

    if len(rows) == 0:
        return [[], []]

    h = {}
    os = set()
    data = []
    for r in rows:
        o = r.lc_os_concat
        os |= set([o])
        day = r.lc_date.toordinal()
        if day not in h:
            h[day] = {}
        h[day][o] = r.lc_count
    os = list(os)
    for o in os:
        e = []
        for day in h:
            d = datetime.date.fromordinal(day)
            if o not in h[day]:
                e += [(d, 0)]
            else:
                e += [(d, h[day][o])]
        data += [e]
    return [os, data]

@service.json
def json_stat_os_name():
    o = db.v_lifecycle_os_name.lc_date
    q = db.v_lifecycle_os_name.id>0
    rows = db(q).select(orderby=o)

    if len(rows) == 0:
        return []

    h = {}
    os = set()
    data = []
    for r in rows:
        o = r.lc_os_name
        os |= set([o])
        day = r.lc_date.toordinal()
        if day not in h:
            h[day] = {}
        h[day][o] = int(r.lc_count)
    os = list(os)
    for o in os:
        e = []
        for day in h:
            d = datetime.date.fromordinal(day)
            if o not in h[day]:
                e += [(d, 0)]
            else:
                e += [(d, h[day][o])]
        data += [e]
    return [os, data]

def __get_lifecycle_os():
    rows = db(db.lifecycle_os.id>0).select(orderby=db.lifecycle_os.lc_os_name,
                                           groupby=db.lifecycle_os.lc_os_name)
    os = []
    for r in rows:
        if r.lc_os_name == "":
            continue
        os += [r.lc_os_name]
    return os

@auth.requires_login()
def lifecycle_os():
    os = __get_lifecycle_os()
    l = []
    for o in os:
        l.append(SPAN(
                   DIV(
                     _id='stat_os_%s'%o,
                     _class='float',
                   ),
                   SCRIPT(
                     "stat_os('%(url)s', 'stat_os_%(os)s');"%dict(
                       os=o,
                       url=URL(r=request, f='call/json/json_stat_os_release',
                               vars={'os_name':o}),
                     ),
                     _name='_to_eval',
                   ),
                 ))

        pass
    h = DIV(
          DIV(
            H2(T("Operating systems lifecycle")),
            DIV(
              _id='stat_os_name',
              _class='float',
            ),
            DIV(
              XML('&nbsp;'),
              _class='spacer',
            ),
            SCRIPT(
              "stat_os('%(url)s', 'stat_os_name');"%dict(
                url=URL(r=request, f='call/json/json_stat_os_name'),
              ),
              _name='_to_eval',
            ),
            _class='container',
          ),
          DIV(
            H2(T("Per operating system lifecycle")),
            SPAN(l),
            DIV(
              XML('&nbsp;'),
              _class='spacer',
            ),
            _class='container',
          ),
        )
    return dict(os=os, h=h)

