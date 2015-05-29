class table_services(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols += ['svc_name']
        self.cols += v_services_cols
        self.cols.remove("svc_updated")
        self.cols += ['updated', 'svc_status_updated']
        self.colprops = v_services_colprops
        self.colprops.update({
            'svc_name': HtmlTableColumn(
                     title='Service',
                     table='services',
                     field='svc_name',
                     img='svc',
                     display=True,
                     _class='svcname',
                    ),
            'svc_status_updated': HtmlTableColumn(
                     title='Status updated',
                     table='services',
                     field='svc_status_updated',
                     img='time16',
                     display=True,
                     _class='datetime_status',
                    ),
            'id': HtmlTableColumn(
                     title='Id',
                     table='services',
                     field='id',
                     img='pkg16',
                     display=False,
                    ),
        })
        self.force_cols = ['svc_name', 'Status updated']
        for col in self.colprops:
            self.colprops[col].table = "services"
        self.colprops["updated"] = self.colprops["svc_updated"]
        self.extraline = True
        self.checkboxes = True
        self.checkbox_id_col = 'svc_name'
        self.checkbox_id_table = 'services'
        self.dbfilterable = True
        self.dataable = True
        self.wsable = True
        self.ajax_col_values = 'ajax_services_col_values'
        self.span = ["svc_name"]
        self.keys = ["svc_name"]
        self.additional_tools.append('svc_del')


    def svc_del(self):
        d = DIV(
              A(
                T("Delete service"),
                _class='del16',
                _onclick="""if (confirm("%(text)s")){%(s)s};"""%dict(
                   s=self.ajax_submit(args=['svc_del']),
                   text=T("Please confirm service deletion"),
                ),
              ),
              _class='floatw',
            )
        return d

@auth.requires_login()
def svc_del(ids):
    groups = user_groups()

    q = db.services.svc_name.belongs(ids)
    if 'Manager' not in groups:
        # Manager can delete any svc
        # A user can delete only services he is responsible of
        l1 = db.apps.on(db.services.svc_app == db.apps.app)
        l2 = db.apps_responsibles.on(db.apps.id == db.apps_responsibles.app_id)
        l3 = db.auth_group.on(db.apps_responsibles.group_id == db.auth_group.id)
        q &= (db.auth_group.role.belongs(groups)) | (db.auth_group.role==None)
        ids = map(lambda x: x.id, db(q).select(db.services.id, left=(l1,l2,l3), cacheable=True))
        q = db.services.id.belongs(ids)
    rows = db(q).select(cacheable=True)
    db(q).delete()
    for r in rows:
        _log('service.delete',
             'deleted service %(u)s',
              dict(u=r.svc_name),
             svcname=r.svc_name)
        purge_svc(r.svc_name)
    if len(rows) > 0:
        _websocket_send(event_msg({
             'event': 'services_change',
             'data': {'f': 'b'},
            }))

    svcnames = [r.svc_name for r in rows]
    q = db.svcmon.mon_svcname.belongs(svcnames)
    rows = db(q).select(cacheable=True)
    db(q).delete()
    for r in rows:
        q = db.svcmon.id == r.id
        _log('service.delete',
             'deleted service instance %(u)s',
              dict(u='@'.join((r.mon_svcname, r.mon_nodname))),
             svcname=r.mon_svcname,
             nodename=r.mon_nodname)
    if len(rows) > 0:
        _websocket_send(event_msg({
             'event': 'svcmon_change',
             'data': {'f': 'b'},
            }))

@auth.requires_login()
def ajax_services_col_values():
    t = table_services('services', 'ajax_services')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.services.id > 0
    q = _where(q, 'services', domain_perms(), 'svc_name')
    q = apply_filters(q, None, db.services.svc_name)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_services():
    t = table_services('services', 'ajax_services')

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'svc_del':
                svc_del(t.get_checked())
        except ToolError, e:
            t.flash = str(e)

    o = db.services.svc_name

    q = db.services.id > 0
    q = _where(q, 'services', domain_perms(), 'svc_name')
    q = apply_filters(q, None, db.services.svc_name)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.services.id.count()).first()(db.services.id.count())
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n, html=False)



@auth.requires_login()
def services():
    t = table_services('services', 'ajax_services')
    t = DIV(
          t.html(),
          _id='services',
          )
    return dict(table=t)


