def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget(response)
    return service()

class col_app_key(HtmlTableColumn):
    def html(self, o):
       d = self.get(o)
       if d == "Error":
           return DIV(d, _class="boxed_small bgred")
       return DIV(d, _class="boxed_small bgblack")

class col_app_value(HtmlTableColumn):
    def chart(self, o):
        id = self.t.extra_line_key(o)
        return SPAN(
          IMG(_src=URL(c='static', f='spark16.png')),
          _class="clickable",
          _onclick="""toggle_extra('%(url)s', '%(id)s', this, 0);
          """%dict(
                  url=URL(r=request, c='appinfo',f='ajax_appinfo_log',
                          vars={'svcname': o.app_svcname,
                                'nodename': o.app_nodename,
                                'launcher': o.app_launcher,
                                'key': o.app_key,
                                'rowid': id,
                               }
                      ),
                  id=id,
              ),
        )

    def html(self, o):
       d = self.get(o)
       try:
           v = float(d)
           c = self.chart(o)
       except:
           c = ""
       return DIV(
         d,
         c,
       )

@auth.requires_login()
@service.json
def json_appinfo_log():
    q = db.appinfo_log.app_nodename == request.vars.nodename
    q &= db.appinfo_log.app_svcname == request.vars.svcname
    q &= db.appinfo_log.app_launcher == request.vars.launcher
    q &= db.appinfo_log.app_key == request.vars.key

    # permission validation
    if 'Manager' not in user_groups():
        q1 = db.appinfo_log.app_svcname == db.services.svc_name
        q1 &= db.services.svc_app == db.apps.app
        q1 &= db.apps.id == db.apps_responsibles.app_id
        q1 &= db.apps_responsibles.group_id.belongs(user_group_ids())
        n = db(q&q1).count()
        if n == 0:
            return "Permission denied"

    rows = db(q).select(db.appinfo_log.app_updated,
                        db.appinfo_log.app_value)
    data = []
    for row in rows:
        data.append([row.app_updated, row.app_value])
    return [data]

@auth.requires_login()
def ajax_appinfo_log():
    session.forget(response)
    row_id = request.vars.rowid
    id = 'chart_'+request.vars.nodename.replace(" ", "").replace("-", "").replace('.', '_')
    id += '_'+request.vars.svcname.replace(" ", "").replace("-", "").replace('.', '_')
    id += '_'+request.vars.launcher.replace(" ", "").replace("-", "").replace('.', '_')
    id += '_'+request.vars.key.replace(" ", "").replace("-", "").replace('.', '_')

    return DIV(
      H3(T("History of key '%(key)s' from launcher '%(launcher)s'", dict(launcher=request.vars.launcher, key=request.vars.key))),
      DIV(
        _id=id,
      ),
      SCRIPT(
       "stats_appinfo('%(url)s', '%(id)s');"%dict(
              id=id,
              url=URL(r=request,
                      f='call/json/json_appinfo_log',
                      vars={'svcname': request.vars.svcname,
                            'nodename': request.vars.nodename,
                            'launcher': request.vars.launcher,
                            'key': request.vars.key},
                  )
            ),
        _name='%s_to_eval'%row_id,
      ),
      _style="float:left;width:500px",
    )

class table_appinfo(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['app_svcname',
                     'app_nodename',
                     'app_launcher',
                     'app_key',
                     'app_value',
                     'app_updated']
        self.colprops = {
            'id': HtmlTableColumn(
                     title='Network Id',
                     field='id',
                     img='svc',
                     display=True,
                    ),
            'app_svcname': HtmlTableColumn(
                     title='Service',
                     field='app_svcname',
                     img='svc',
                     display=True,
                     _class="svcname",
                    ),
            'app_nodename': HtmlTableColumn(
                     title='Node',
                     field='app_nodename',
                     img='hw16',
                     display=True,
                     _class="nodename",
                    ),
            'app_launcher': HtmlTableColumn(
                     title='Launcher',
                     field='app_launcher',
                     img='svc',
                     display=True,
                    ),
            'app_key': col_app_key(
                     title='Key',
                     field='app_key',
                     img='svc',
                     display=True,
                    ),
            'app_value': col_app_value(
                     title='Value',
                     field='app_value',
                     img='svc',
                     display=True,
                    ),
            'app_updated': HtmlTableColumn(
                     title='Last update',
                     field='app_updated',
                     img='svc',
                     display=True,
                     _class='datetime_daily',
                    ),
        }
        for c in self.cols:
            self.colprops[c].t = self
        self.extraline = True
        self.dbfilterable = True
        self.ajax_col_values = 'ajax_appinfo_col_values'
        self.span = ['app_svcname', 'app_nodename', 'app_launcher']

@auth.requires_login()
def ajax_appinfo_col_values():
    t = table_appinfo('appinfo', 'ajax_appinfo')
    col = request.args[0]
    o = db.appinfo[col]
    q = db.appinfo.id > 0
    q = apply_filters(q, None, db.appinfo.app_svcname)
    q = _where(q, 'appinfo', domain_perms(), 'app_svcname')

    for f in t.cols:
        q = _where(q, 'appinfo', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_appinfo():
    t = table_appinfo('appinfo', 'ajax_appinfo')

    o = db.appinfo.app_svcname | db.appinfo.app_nodename | db.appinfo.app_launcher | db.appinfo.app_key
    q = db.appinfo.id > 0
    q = apply_filters(q, None, db.appinfo.app_svcname)
    q = _where(q, 'appinfo', domain_perms(), 'app_svcname')

    for f in set(t.cols):
        q = _where(q, 'appinfo', t.filter_parse(f), f)

    t.csv_q = q
    t.csv_orderby = o

    if len(request.args) == 1 and request.args[0] == 'csv':
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'line':
        if request.vars.volatile_filters is None:
            n = db(q).count()
            limitby = (t.pager_start,t.pager_end)
        else:
            n = 0
            limitby = (0, 500)
        t.object_list = db(q).select(orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n)

    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)

    return t.html()

@auth.requires_login()
def appinfo():
    t = DIV(
          ajax_appinfo(),
          _id='appinfo',
        )
    return dict(table=t)


