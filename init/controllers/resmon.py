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
                     img='svc16',
                     display=True,
                     _class='svcname',
                    ),
            'nodename': HtmlTableColumn(
                     title='Nodename',
                     table='resmon',
                     field='nodename',
                     img='hw16',
                     display=True,
                     _class='nodename',
                    ),
            'vmname': HtmlTableColumn(
                     title='Container name',
                     table='resmon',
                     field='vmname',
                     img='svc16',
                     display=True,
                     _class='nodename_no_os',
                    ),
            'rid': HtmlTableColumn(
                     title='Resource id',
                     table='resmon',
                     field='rid',
                     img='svc16',
                     display=True,
                    ),
            'res_desc': HtmlTableColumn(
                     title='Description',
                     table='resmon',
                     field='res_desc',
                     img='svc16',
                     display=True,
                    ),
            'res_status': HtmlTableColumn(
                     title='Status',
                     table='resmon',
                     field='res_status',
                     img='svc16',
                     display=True,
                     _class="status",
                    ),
            'res_log': col_res_log(
                     title='Log',
                     table='resmon',
                     field='res_log',
                     img='svc16',
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

@auth.requires_login()
def ajax_resmon_col_values():
    t = table_resmon('resmon', 'ajax_resmon')
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
    t = table_resmon('resmon', 'ajax_resmon')
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
        if request.vars.volatile_filters is None:
            n = db(q).count()
            t.setup_pager(n)
            limitby = (t.pager_start,t.pager_end)
        else:
            n = 0
            limitby = (0, 500)
        t.object_list = db(q).select(limitby=limitby, orderby=o, cacheable=False)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def resmon():
    t = table_resmon('resmon', 'ajax_resmon')
    t = DIV(
          t.html(),
          SCRIPT("""
function ws_action_switch_%(divid)s(data) {
        if (data["event"] == "svcmon_change") {
          osvc.tables["%(divid)s"].refresh()
        }
}
wsh["%(divid)s"] = ws_action_switch_%(divid)s
           """ % dict(
                  divid=t.innerhtml,
                 )
          ),
          _id='resmon',
        )
    return dict(table=t)

class table_resmon_svc(table_resmon):
    def __init__(self, id=None, func=None, innerhtml=None):
        table_resmon.__init__(self, id, func, innerhtml)
        self.dbfilterable = False
        self.filterable = False
        self.exportable = False
        self.columnable = False
        self.refreshable = False
        self.pageable = False
        self.linkable = False
        self.bookmarkable = False
        self.commonalityable = False
        self.wsable = False
        self.colprops['svcname'].display=False

@auth.requires_login()
def resmon_svc():
    tid = request.args[0]
    t = table_resmon_svc(tid, 'ajax_resmon_svc')
    svcname = request.args[1]
    t.colprops['svcname'].force_filter = svcname
    return t.html()
 
@auth.requires_login()
def ajax_resmon_svc():
    tid = request.vars.table_id
    t = table_resmon_svc(tid, 'ajax_resmon_svc')

    o = db.resmon.svcname
    o |= db.resmon.nodename
    o |= db.resmon.vmname
    o |= db.resmon.rid

    q = db.resmon.id>0
    q &= db.resmon.nodename==db.v_nodes.nodename
    q = _where(q, 'resmon', domain_perms(), 'nodename')
    for f in ['svcname']:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    t.object_list = db(q).select(orderby=o, cacheable=True)
    return t.table_lines_data(-1, html=False)

