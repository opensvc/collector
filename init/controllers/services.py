class table_services(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols += ['svc_name']
        self.cols += v_services_cols
        self.colprops = v_services_colprops
        self.colprops.update({
            'svc_name': HtmlTableColumn(
                     title='Service',
                     table='v_services',
                     field='svc_name',
                     img='svc',
                     display=True,
                     _class='svcname',
                    ),
            'id': HtmlTableColumn(
                     title='Id',
                     table='services',
                     field='id',
                     img='pkg16',
                     display=False,
                    ),
        })
        for col in self.colprops:
            self.colprops[col].table = "services"
        self.extraline = True
        self.checkboxes = True
        self.checkbox_id_col = 'svc_name'
        self.checkbox_id_table = 'services'
        self.dbfilterable = True
        self.dataable = True
        self.ajax_col_values = 'ajax_services_col_values'
        self.span = ["svc_name"]
        self.keys = ["svc_name"]

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


