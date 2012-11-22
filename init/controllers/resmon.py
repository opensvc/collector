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
            'svcname': col_svc(
                     title='Service',
                     table='resmon',
                     field='svcname',
                     img='svc16',
                     display=True,
                    ),
            'nodename': col_node(
                     title='Nodename',
                     table='resmon',
                     field='nodename',
                     img='hw16',
                     display=True,
                    ),
            'vmname': col_node(
                     title='Container name',
                     table='resmon',
                     field='vmname',
                     img='svc16',
                     display=True,
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
            'res_status': col_status(
                     title='Status',
                     table='resmon',
                     field='res_status',
                     img='svc16',
                     display=True,
                    ),
            'res_log': col_res_log(
                     title='Log',
                     table='resmon',
                     field='res_log',
                     img='svc16',
                     display=True,
                    ),
            'changed': col_updated(
                     title='Last change',
                     table='resmon',
                     field='changed',
                     img='time16',
                     display=True,
                    ),
            'updated': col_updated(
                     title='Updated',
                     table='resmon',
                     field='updated',
                     img='time16',
                     display=True,
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
        self.span = 'nodename'
        self.sub_span = ['svcname']

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
    t.object_list = db(q).select(o, orderby=o, groupby=o)
    return t.col_values_cloud(col)

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
    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)

    t.csv_q = q
    t.csv_orderby = o

    return t.html()

@auth.requires_login()
def resmon():
    t = DIV(
          ajax_resmon(),
          _id='resmon',
        )
    return dict(table=t)

@auth.requires_login()
def ajax_resmon_svc():
    tid = request.args[0]
    svcname = request.args[1]

    t = table_resmon(tid, 'resmon')
    t.cols.remove('svcname')
    t.dbfilterable = False
    t.filterable = False
    t.exportable = False
    t.columnable = False
    t.refreshable = False
    t.pageable = False
    t.linkable = False

    o = db.resmon.svcname
    o |= db.resmon.nodename
    o |= db.resmon.vmname
    o |= db.resmon.rid

    q = db.resmon.id>0
    q &= db.resmon.nodename==db.v_nodes.nodename
    q &= db.resmon.svcname==svcname
    q = _where(q, 'resmon', domain_perms(), 'nodename')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(orderby=o)

    t.csv_q = q
    t.csv_orderby = o

    return t.html()


