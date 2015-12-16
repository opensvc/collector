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
         'svcname',
         'nodename',
         'vmname',
         'rid',
         'res_status',
         'res_desc',
         'res_log',
         'res_monitor',
         'res_disable',
         'res_optional',
         #'changed',
         'updated'
        ]
        for col in v_nodes_cols:
            if col not in self.cols:
                self.cols.append(col)
        self.colprops = v_nodes_colprops
        self.colprops.update({
            'svcname': HtmlTableColumn(
                     title='Service',
                     table='resmon',
                     field='svcname',
                     img='svc',
                     display=True,
                     _class='svcname',
                    ),
            'nodename': HtmlTableColumn(
                     title='Nodename',
                     table='resmon',
                     field='nodename',
                     img='node16',
                     display=True,
                     _class='nodename',
                    ),
            'vmname': HtmlTableColumn(
                     title='Container name',
                     table='resmon',
                     field='vmname',
                     img='node16',
                     display=True,
                     _class='nodename_no_os',
                    ),
            'rid': HtmlTableColumn(
                     title='Resource id',
                     table='resmon',
                     field='rid',
                     img='svc',
                     display=True,
                    ),
            'res_monitor': HtmlTableColumn(
                     title='Monitor',
                     table='resmon',
                     field='res_monitor',
                     img='svc',
                     display=True,
                     _class="boolean",
                    ),
            'res_disable': HtmlTableColumn(
                     title='Disable',
                     table='resmon',
                     field='res_disable',
                     img='svc',
                     display=True,
                     _class="boolean",
                    ),
            'res_optional': HtmlTableColumn(
                     title='Optional',
                     table='resmon',
                     field='res_optional',
                     img='svc',
                     display=True,
                     _class="boolean",
                    ),
            'res_desc': HtmlTableColumn(
                     title='Description',
                     table='resmon',
                     field='res_desc',
                     img='svc',
                     display=True,
                    ),
            'res_status': HtmlTableColumn(
                     title='Status',
                     table='resmon',
                     field='res_status',
                     img='svc',
                     display=True,
                     _class="status",
                    ),
            'res_log': col_res_log(
                     title='Log',
                     table='resmon',
                     field='res_log',
                     img='svc',
                     display=True,
                    ),
            'changed': HtmlTableColumn(
                     title='Last change',
                     table='resmon',
                     field='changed',
                     img='time16',
                     display=True,
                     _class='datetime_no_age',
                    ),
            'updated': HtmlTableColumn(
                     title='Updated',
                     table='resmon',
                     field='updated',
                     img='time16',
                     display=True,
                     _class='datetime_status',
                    ),
        })
        self.colprops['svcname'].t = self
        self.colprops['nodename'].t = self
        self.colprops['vmname'].t = self
        self.colprops['res_status'].t = self
        self.extraline = True
        self.checkbox_id_col = 'id'
        self.checkbox_id_table = 'resmon'
        self.dbfilterable = True
        self.ajax_col_values = 'ajax_resmon_col_values'
        self.span = ['nodename', 'svcname']
        self.keys = ['nodename', 'svcname', 'rid']
        self.dataable = True
        self.checkboxes = True
        self.wsable = True
        self.events = ["resmon_change"]

@auth.requires_login()
def ajax_resmon_col_values():
    table_id = request.vars.table_id
    t = table_resmon(table_id, 'ajax_resmon')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.resmon.nodename==db.v_nodes.nodename
    q = _where(q, 'resmon', domain_perms(), 'nodename')
    q = apply_filters(q, db.resmon.nodename, db.resmon.svcname)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_resmon():
    table_id = request.vars.table_id
    t = table_resmon(table_id, 'ajax_resmon')
    o = db.resmon.svcname
    o |= db.resmon.nodename
    o |= db.resmon.vmname
    o |= db.resmon.rid

    q = db.resmon.id>0
    q &= db.resmon.nodename==db.v_nodes.nodename
    q = _where(q, 'resmon', domain_perms(), 'nodename')
    q = apply_filters(q, db.resmon.nodename, db.resmon.svcname)
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
          """$.when(osvc.app_started).then(function(){ table_resources("layout", %s) })""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def resmon_load():
    return resmon()["table"]

