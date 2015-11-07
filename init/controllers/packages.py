class table_packages(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['nodename']
        self.cols += ['id',
                      'pkg_name',
                      'pkg_version',
                      'pkg_arch',
                      'pkg_type',
                      'sig_provider',
                      'pkg_sig',
                      'pkg_install_date',
                      'pkg_updated']
        self.cols += v_nodes_cols
        self.colprops = v_nodes_colprops
        self.colprops.update({
            'pkg_name': HtmlTableColumn(
                     title='Package',
                     table='packages',
                     field='pkg_name',
                     img='pkg16',
                     display=True,
                    ),
            'sig_provider': HtmlTableColumn(
                     title='Signature provider',
                     table='pkg_sig_provider',
                     field='sig_provider',
                     img='pkg16',
                     display=False,
                    ),
            'pkg_sig': HtmlTableColumn(
                     title='Signature',
                     table='packages',
                     field='pkg_sig',
                     img='pkg16',
                     display=False,
                     _class='pre',
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
            'pkg_type': HtmlTableColumn(
                     title='Type',
                     table='packages',
                     field='pkg_type',
                     img='pkg16',
                     display=True,
                    ),
            'pkg_install_date': HtmlTableColumn(
                     title='Install date',
                     table='packages',
                     field='pkg_install_date',
                     img='time16',
                     display=True,
                     _class='datetime_no_age',
                    ),
            'pkg_updated': HtmlTableColumn(
                     title='Updated',
                     table='packages',
                     field='pkg_updated',
                     img='time16',
                     display=True,
                     _class='datetime_daily',
                    ),
            'id': HtmlTableColumn(
                     title='Id',
                     table='packages',
                     field='id',
                     img='pkg16',
                     display=False,
                    ),
        })
        self.force_cols = ['os_name']
        self.colprops['nodename'].display = True
        self.colprops['nodename'].t = self
        self.extraline = True
        self.checkboxes = True
        self.checkbox_id_col = 'id'
        self.checkbox_id_table = 'packages'
        self.dbfilterable = True
        self.dataable = True
        self.ajax_col_values = 'ajax_packages_col_values'
        self.span = ["id"]
        self.keys = ["id"]

@auth.requires_login()
def ajax_packages_col_values():
    t = table_packages('packages', 'ajax_packages')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.packages.pkg_nodename==db.v_nodes.nodename
    q = _where(q, 'packages', domain_perms(), 'pkg_nodename')
    q = apply_filters(q, db.packages.pkg_nodename, None)
    j = db.packages.pkg_sig == db.pkg_sig_provider.sig_id
    l = db.pkg_sig_provider.on(j)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, left=l)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_packages():
    t = table_packages('packages', 'ajax_packages')
    o = db.packages.pkg_nodename
    o |= db.packages.pkg_name
    o |= db.packages.pkg_arch

    q = db.packages.id>0
    q &= db.packages.pkg_nodename==db.v_nodes.nodename
    q = _where(q, 'packages', domain_perms(), 'pkg_nodename')
    q = apply_filters(q, db.packages.pkg_nodename, None)
    j = db.packages.pkg_sig == db.pkg_sig_provider.sig_id
    l = db.pkg_sig_provider.on(j)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_left = l
        t.csv_orderby = o
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        t.csv_left = l
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.packages.id.count(), left=l).first()(db.packages.id.count())
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=False, left=l)
        return t.table_lines_data(n, html=False)



@auth.requires_login()
def packages():
    t = table_packages('packages', 'ajax_packages')
    t = DIV(
          t.html(),
          _id='packages',
        )
    return dict(table=t)

def packages_load():
    return packages()["table"]

