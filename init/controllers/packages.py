class table_packages(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['nodename']+v_nodes_cols
        self.cols += ['pkg_name',
                      'pkg_version',
                      'pkg_arch',
                      'pkg_updated']
        self.colprops = v_nodes_colprops
        self.colprops.update({
            'pkg_name': HtmlTableColumn(
                     title='Package',
                     table='packages',
                     field='pkg_name',
                     img='pkg16',
                     display=True,
                    ),
            'pkg_version': HtmlTableColumn(
                     title='Version',
                     table='packages',
                     field='pkg_version',
                     img='pkg16',
                     display=True,
                    ),
            'pkg_arch': HtmlTableColumn(
                     title='Arch',
                     table='packages',
                     field='pkg_arch',
                     img='pkg16',
                     display=True,
                    ),
            'pkg_updated': col_updated(
                     title='Updated',
                     table='packages',
                     field='pkg_updated',
                     img='pkg16',
                     display=True,
                    ),
        })
        self.colprops['nodename'].display = True
        self.colprops['nodename'].t = self
        self.extraline = True
        self.checkbox_id_col = 'id'
        self.checkbox_id_table = 'packages'
        self.dbfilterable = True
        self.ajax_col_values = 'ajax_packages_col_values'

@auth.requires_login()
def ajax_packages_col_values():
    t = table_packages('packages', 'ajax_packages')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.packages.pkg_nodename==db.v_nodes.nodename
    q = _where(q, 'packages', domain_perms(), 'pkg_nodename')
    q = apply_db_filters(q, 'v_nodes')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_packages():
    t = table_packages('packages', 'ajax_packages')
    o = db.packages.pkg_nodename
    o |= db.packages.pkg_name
    o |= db.packages.pkg_arch

    q = db.packages.id>0
    q &= db.packages.pkg_nodename==db.v_nodes.nodename
    q = _where(q, 'packages', domain_perms(), 'pkg_nodename')
    q = apply_db_filters(q, 'v_nodes')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return t.html()

@auth.requires_login()
def packages():
    t = DIV(
          ajax_packages(),
          _id='packages',
        )
    return dict(table=t)


