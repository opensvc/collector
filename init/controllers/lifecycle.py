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
    fset_id = user_fset_id()
    if fset_id is None:
        fset_id = 0
    q = db.lifecycle_os.lc_os_name==os_name
    q &= db.lifecycle_os.fset_id==fset_id
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
    fset_id = user_fset_id()
    if fset_id is None:
        fset_id = 0
    q = db.v_lifecycle_os_name.fset_id == fset_id
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
    fset_id = user_fset_id()
    if fset_id is None:
        fset_id = 0
    q = db.lifecycle_os.fset_id == fset_id
    rows = db(q).select(orderby=db.lifecycle_os.lc_os_name,
                        groupby=db.lifecycle_os.lc_os_name)
    os = []
    for r in rows:
        if r.lc_os_name == "":
            continue
        os += [r.lc_os_name]
    return os

class table_lifecycle_os(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.dbfilterable = True
        self.refreshable = False
        self.pageable = False
        self.exportable = False
        self.columnable = False
        self.object_list = []
        self.nodatabanner = False

@auth.requires_login()
def lifecycle_os():
    return dict(table=ajax_lifecycle_os())

@auth.requires_login()
def ajax_lifecycle_os():
    t = table_lifecycle_os('lifecycle_os', 'ajax_lifecycle_os')
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
                     _name=t.id+'_to_eval',
                   ),
                 ))

        pass
    h = DIV(
          t.html(),
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
              _name=t.id+'_to_eval',
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
          _id='lifecycle_os',
        )
    return h

