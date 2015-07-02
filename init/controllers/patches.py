class table_patches(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['nodename']+v_nodes_cols
        self.cols += ['id',
                      'patch_num',
                      'patch_rev',
                      'patch_install_date',
                      'patch_updated']
        self.colprops = v_nodes_colprops
        self.colprops.update({
            'nodename': HtmlTableColumn(
                     title='Nodename',
                     table='v_nodes',
                     field='nodename',
                     img='node16',
                     display=True,
                     _class='nodename',
                    ),
            'patch_num': HtmlTableColumn(
                     title='Patchnum',
                     table='patches',
                     field='patch_num',
                     img='pkg16',
                     display=True,
                    ),
            'patch_rev': HtmlTableColumn(
                     title='Patchrev',
                     table='patches',
                     field='patch_rev',
                     img='pkg16',
                     display=True,
                    ),
            'patch_updated': HtmlTableColumn(
                     title='Updated',
                     table='patches',
                     field='patch_updated',
                     img='time16',
                     display=True,
                     _class='datetime_daily',
                    ),
            'patch_install_date': HtmlTableColumn(
                     title='Install date',
                     table='patches',
                     field='patch_install_date',
                     img='time16',
                     display=True,
                    ),
            'id': HtmlTableColumn(
                     title='Id',
                     table='patches',
                     field='id',
                     img='pkg16',
                     display=False,
                    ),
        })
        self.colprops['nodename'].display = True
        self.colprops['nodename'].t = self
        self.force_cols = ['os_name']
        self.dbfilterable = True
        self.dataable = True
        self.extraline = True
        self.checkboxes = True
        self.checkbox_id_col = 'id'
        self.checkbox_id_table = 'patches'
        self.ajax_col_values = 'ajax_patches_col_values'
        self.span = ["id"]
        self.keys = ["id"]

@auth.requires_login()
def ajax_patches_col_values():
    t = table_patches('patches', 'ajax_patches')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.patches.patch_nodename==db.v_nodes.nodename
    q = _where(q, 'patches', domain_perms(), 'patch_nodename')
    q = apply_filters(q, db.patches.patch_nodename, None)

    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_patches():
    t = table_patches('patches', 'ajax_patches')
    o = db.patches.patch_nodename
    o |= db.patches.patch_num
    o |= db.patches.patch_rev

    q = db.patches.id>0
    q &= db.patches.patch_nodename==db.v_nodes.nodename
    q = _where(q, 'patches', domain_perms(), 'patch_nodename')
    q = apply_filters(q, db.patches.patch_nodename, None)

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
        n = db(q).select(db.patches.id.count()).first()(db.patches.id.count())
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def patches():
    t = table_patches('patches', 'ajax_patches')
    t = DIV(
          t.html(),
          _id='patches',
        )
    return dict(table=t)


