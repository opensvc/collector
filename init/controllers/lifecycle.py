def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget(response)
    return service()

def get_current_top_ten(fset_id, os_name):
    sql = """select lc_os_concat from lifecycle_os
             where
               fset_id=%(fset_id)d and
               lc_os_name="%(os_name)s"
             group by lc_os_concat
             order by 
               sum(lc_count/(to_days(now())-to_days(lc_date)))
             desc
             limit 10
          """%dict(
               fset_id=fset_id,
               os_name=os_name,
             )
    rows = db.executesql(sql)
    return [r[0] for r in rows]

@service.json
def json_stat_os_release():
    os_name = request.vars.os_name
    if os_name is None or os_name == "":
        return [[], []]

    fset_id = user_fset_id()
    if fset_id is None:
        fset_id = 0

    top = get_current_top_ten(fset_id, os_name)
    if len(top) > 0:
       _top = "lc_os_concat in (%s)"%','.join(map(lambda x: '"'+str(x)+'"', top))
       other = "lc_os_concat not in (%s)"%','.join(map(lambda x: '"'+str(x)+'"', top))
    else:
       _top = "1=1"
       other = "0=0"

    e = now
    b = now - datetime.timedelta(days=1000)
    sql = """select * from (
             select 
               lc_os_concat,
               lc_date,
               lc_count,
               %(d)s as d
             from lifecycle_os
             where
               fset_id=%(fset_id)d and
               lc_os_name="%(os_name)s" and
               %(top)s
             group by d, lc_os_concat
             union all
             select 
               "other",
               lc_date,
               sum(lc_count) as lc_count,
               %(d)s as d
             from lifecycle_os
             where
               fset_id=%(fset_id)d and
               lc_os_name="%(os_name)s" and
               %(other)s
             group by d
             ) t
             order by t.d
          """%dict(
               d=period_concat(b, e, field='lc_date'),
               fset_id=fset_id,
               os_name=os_name,
               top=_top,
               other=other,
             )

    rows = db.executesql(sql, as_dict=True)

    if len(rows) == 0:
        return [[], []]

    h = {}
    os = set()
    data = []
    for r in rows:
        o = r['lc_os_concat']
        os |= set([o])
        day = r['lc_date'].toordinal()
        if day not in h:
            h[day] = {}
        h[day][o] = int(r['lc_count'])
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
    fset_id = user_fset_id()
    if fset_id is None:
        fset_id = 0

    e = now
    b = now - datetime.timedelta(days=1000)
    sql = """select *, %(d)s as d
             from v_lifecycle_os_name
             where
               fset_id=%(fset_id)d
             group by d, lc_os_name
             order by d"""%dict(
               d=period_concat(b, e, field='lc_date'),
               fset_id=fset_id,
             )
    rows = db.executesql(sql, as_dict=True)

    if len(rows) == 0:
        return []

    h = {}
    os = set()
    data = []
    for r in rows:
        o = r['lc_os_name']
        os |= set([o])
        day = r['lc_date'].toordinal()
        if day not in h:
            h[day] = {}
        h[day][o] = int(r['lc_count'])
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
    session.forget(response)
    t = table_lifecycle_os('lifecycle_os', 'ajax_lifecycle_os')
    os = __get_lifecycle_os()
    l = []
    for o in os:
        l.append(SPAN(
                   DIV(
                     DIV(_id='stat_os_%s'%o),
                     _class='float',
                   ),
                   DIV(
                     XML('&nbsp;'),
                     _class='spacer',
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
              DIV(_id='stat_os_name'),
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

