class table_services(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['svc_id', 'svcname']
        self.cols += services_cols
        self.cols.remove("svc_updated")
        self.cols += ['updated', 'svc_status_updated']
        self.colprops = services_colprops
        self.colprops.update({
            'svc_id': HtmlTableColumn(
                     table='services',
                     field='svc_id',
                    ),
            'svcname': HtmlTableColumn(
                     table='services',
                     field='svcname',
                    ),
            'svc_status_updated': HtmlTableColumn(
                     table='services',
                     field='svc_status_updated',
                    ),
            'id': HtmlTableColumn(
                     table='services',
                     field='id',
                    ),
        })
        for col in self.colprops:
            self.colprops[col].table = "services"
        self.colprops["updated"] = self.colprops["svc_updated"]
        self.ajax_col_values = 'ajax_services_col_values'


@auth.requires_login()
def ajax_services_col_values():
    table_id = request.vars.table_id
    t = table_services(table_id, 'ajax_services')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = q_filter(app_field=db.services.svc_app)
    q = apply_filters_id(q, svc_field=db.services.svc_id)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_services():
    table_id = request.vars.table_id
    t = table_services(table_id, 'ajax_services')

    o = t.get_orderby(default=db.services.svcname)
    q = q_filter(app_field=db.services.svc_app)
    q = apply_filters_id(q, svc_field=db.services.svc_id)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.services.id.count()).first()(db.services.id.count())
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n, html=False)


@auth.requires_login()
def services():
    t = SCRIPT(
          """table_services("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def services_load():
    return services()["table"]

