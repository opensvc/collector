class table_disks(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['disk_id',
                     'disk_svcname',
                     'disk_nodename',
                     'disk_size',
                     'disk_vendor',
                     'disk_model',
                     'disk_dg',
                     'disk_target_port_id',
                     'disk_updated']
        self.colprops.update({
            'disk_id': HtmlTableColumn(
                     title='Disk Id',
                     table='svcdisks',
                     field='disk_id',
                     img='hd16',
                     display=True,
                    ),
            'disk_svcname': HtmlTableColumn(
                     title='Service',
                     table='svcdisks',
                     field='disk_svcname',
                     img='svc',
                     display=True,
                    ),
            'disk_nodename': HtmlTableColumn(
                     title='Nodename',
                     table='svcdisks',
                     field='disk_nodename',
                     img='hw16',
                     display=True,
                    ),
            'disk_size': HtmlTableColumn(
                     title='Size (GB)',
                     table='svcdisks',
                     field='disk_size',
                     img='hd16',
                     display=True,
                    ),
            'disk_vendor': HtmlTableColumn(
                     title='Vendor',
                     table='svcdisks',
                     field='disk_vendor',
                     img='hd16',
                     display=True,
                    ),
            'disk_model': HtmlTableColumn(
                     title='Model',
                     table='svcdisks',
                     field='disk_model',
                     img='hd16',
                     display=True,
                    ),
            'disk_dg': HtmlTableColumn(
                     title='Disk group',
                     table='svcdisks',
                     field='disk_dg',
                     img='hd16',
                     display=True,
                    ),
            'disk_target_port_id': HtmlTableColumn(
                     title='Target port Id',
                     table='svcdisks',
                     field='disk_target_port_id',
                     img='hd16',
                     display=True,
                    ),
            'disk_updated': HtmlTableColumn(
                     title='Updated',
                     table='svcdisks',
                     field='disk_updated',
                     img='time16',
                     display=True,
                    ),
        })
        self.extraline = True
        #self.checkbox_id_col = 'id'
        #self.checkbox_id_table = 'svcdisks'
        self.dbfilterable = True
        self.ajax_col_values = 'ajax_disks_col_values'

@auth.requires_login()
def ajax_disks_col_values():
    t = table_disks('disks', 'ajax_disks')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.svcdisks.id > 0
    q = _where(q, 'svcdisks', domain_perms(), 'disk_nodename')
    q = apply_filters(q, db.svcdisks.disk_nodename, db.svcdisks.disk_svcname)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_disks():
    t = table_disks('disks', 'ajax_disks')
    o = db.svcdisks.disk_id
    q = db.svcdisks.id>0
    #q &= db.svcdisks.disk_nodename==db.v_nodes.nodename
    q = _where(q, 'svcdisks', domain_perms(), 'disk_nodename')
    q = apply_filters(q, db.svcdisks.disk_nodename, db.svcdisks.disk_svcname)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)

    t.csv_q = q
    t.csv_orderby = o

    return t.html()

@auth.requires_login()
def disks():
    t = DIV(
          ajax_disks(),
          _id='disks',
        )
    return dict(table=t)


