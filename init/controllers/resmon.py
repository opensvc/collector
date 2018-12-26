class col_res_log(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        if s is None:
            s = ''
        else:
            s = s.replace('\\n', '\n')
        return PRE(s)

class table_resmon(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = [
         'id',
         'svc_id',
         'svcname',
         'node_id',
         'nodename',
         'vmname',
         'rid',
         'res_type',
         'res_status',
         'res_desc',
         'res_log',
         'res_monitor',
         'res_disable',
         'res_optional',
         'updated'
        ]
        for col in nodes_cols:
            if col not in self.cols:
                self.cols.append(col)
        self.colprops = nodes_colprops
        self.colprops.update({
            'id': HtmlTableColumn(
                     table='resmon',
                     field='id',
                    ),
            'svc_id': HtmlTableColumn(
                     table='resmon',
                     field='svc_id',
                    ),
            'svcname': HtmlTableColumn(
                     table='services',
                     field='svcname',
                    ),
            'node_id': HtmlTableColumn(
                     table='resmon',
                     field='node_id',
                    ),
            'nodename': HtmlTableColumn(
                     table='nodes',
                     field='nodename',
                    ),
            'vmname': HtmlTableColumn(
                     table='resmon',
                     field='vmname',
                    ),
            'rid': HtmlTableColumn(
                     table='resmon',
                     field='rid',
                    ),
            'res_type': HtmlTableColumn(
                     table='resmon',
                     field='res_type',
                    ),
            'res_monitor': HtmlTableColumn(
                     table='resmon',
                     field='res_monitor',
                    ),
            'res_disable': HtmlTableColumn(
                     table='resmon',
                     field='res_disable',
                    ),
            'res_optional': HtmlTableColumn(
                     table='resmon',
                     field='res_optional',
                    ),
            'res_desc': HtmlTableColumn(
                     table='resmon',
                     field='res_desc',
                    ),
            'res_status': HtmlTableColumn(
                     table='resmon',
                     field='res_status',
                    ),
            'res_log': col_res_log(
                     table='resmon',
                     field='res_log',
                    ),
            'changed': HtmlTableColumn(
                     table='resmon',
                     field='changed',
                    ),
            'updated': HtmlTableColumn(
                     table='resmon',
                     field='updated',
                    ),
            'node_updated': HtmlTableColumn(
                     table='nodes',
                     field='updated',
                    ),
        })
        self.ajax_col_values = 'ajax_resmon_col_values'

@auth.requires_login()
def ajax_resmon_col_values():
    table_id = request.vars.table_id
    t = table_resmon(table_id, 'ajax_resmon')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.resmon.node_id==db.nodes.node_id
    q &= db.resmon.svc_id==db.services.svc_id
    q = q_filter(q, svc_field=db.resmon.svc_id)
    q = apply_filters_id(q, db.resmon.node_id, db.resmon.svc_id)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o,
                                 db.resmon.id.count(),
                                 orderby=~db.resmon.id.count(),
                                 groupby=o)
    return t.col_values_cloud_grouped(col)

@auth.requires_login()
def ajax_resmon():
    table_id = request.vars.table_id
    t = table_resmon(table_id, 'ajax_resmon')
    o = t.get_orderby(default=db.services.svcname|db.nodes.nodename|db.resmon.vmname|db.resmon.rid)

    q = db.resmon.id>0
    q &= db.resmon.node_id==db.nodes.node_id
    q &= db.resmon.svc_id==db.services.svc_id
    q = q_filter(q, svc_field=db.resmon.svc_id)
    q = apply_filters_id(q, db.resmon.node_id, db.resmon.svc_id)
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
        n = db(q).count()
        limitby = (t.pager_start,t.pager_end)
        t.object_list = db(q).select(limitby=limitby, orderby=o, cacheable=False)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def resmon():
    t = SCRIPT(
          """table_resources("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def resmon_load():
    return resmon()["table"]

