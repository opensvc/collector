class col_app_key(HtmlTableColumn):
    def html(self, o):
       d = self.get(o)
       if d == "Error":
           return DIV(d, _class="boxed_small bgred")
       return DIV(d, _class="boxed_small bgblack")

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
            'app_svcname': col_svc(
                     title='Service',
                     field='app_svcname',
                     img='svc',
                     display=True,
                    ),
            'app_nodename': col_node(
                     title='Node',
                     field='app_nodename',
                     img='hw16',
                     display=True,
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
            'app_value': HtmlTableColumn(
                     title='Value',
                     field='app_value',
                     img='svc',
                     display=True,
                    ),
            'app_updated': col_updated(
                     title='Last update',
                     field='app_updated',
                     img='svc',
                     display=True,
                    ),
        }
        for c in self.cols:
            self.colprops[c].t = self
        self.extraline = True
        self.dbfilterable = True
        self.ajax_col_values = 'ajax_appinfo_col_values'
        self.span = 'app_svcname'
        self.sub_span = ['app_launcher']

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
    t.object_list = db(q).select(o, orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_appinfo():
    t = table_appinfo('appinfo', 'ajax_appinfo')

    o = db.appinfo.app_svcname | db.appinfo.app_nodename | db.appinfo.app_launcher | db.appinfo.app_key
    q = db.appinfo.id > 0
    q = apply_filters(q, None, db.appinfo.app_svcname)
    q = _where(q, 'appinfo', domain_perms(), 'app_svcname')

    for f in set(t.cols):
        q = _where(q, 'appinfo', t.filter_parse(f), f)
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


