class col_size_b(HtmlTableColumn):
    def html(self, o):
       d = self.get(o)
       try:
           d = int(d)
       except:
           return ''
       c = "nowrap"
       if d < 0:
           c += " highlight"
       if d is None:
           return ''
       return DIV(beautify_size_b(d), _class=c)

def beautify_size_b(d):
       try:
          d = int(d)
       except:
          return '-'
       if d < 0:
           neg = True
           d = -d
       else:
           neg = False
       if d < 1024:
           v = 1.0 * d
           unit = 'B'
       elif d < 1048576:
           v = 1.0 * d / 1024
           unit = 'KB'
       elif d < 1073741824:
           v = 1.0 * d / 1048576
           unit = 'MB'
       elif d < 1099511627776:
           v = 1.0 * d / 1073741824
           unit = 'GB'
       else:
           v = 1.0 * d / 1099511627776
           unit = 'TB'
       if v >= 100:
           fmt = "%d"
       elif v >= 10:
           fmt = "%.1f"
       else:
           fmt = "%.2f"
       fmt = fmt + " %s"
       if neg:
           v = -v
       return fmt%(v, unit)

class table_saves(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols =  ['save_server',
                      'save_nodename',
                      'save_svcname',
                      'save_name',
                      'save_group',
                      'save_level',
                      'save_size',
                      'save_volume',
                      'save_date',
                      'save_retention']
        self.cols += v_nodes_cols
        self.colprops = v_nodes_colprops
        self.colprops.update({
            'save_server': col_node(
                     title='Server',
                     table='saves',
                     field='save_server',
                     img='save16',
                     display=True,
                    ),
            'save_nodename': col_node(
                     title='Nodename',
                     table='saves',
                     field='save_nodename',
                     img='node16',
                     display=True,
                    ),
            'save_svcname': col_svc(
                     title='Service',
                     table='saves',
                     field='save_svcname',
                     img='save16',
                     display=True,
                    ),
            'save_name': HtmlTableColumn(
                     title='Name',
                     table='saves',
                     field='save_name',
                     img='save16',
                     display=True,
                    ),
            'save_group': HtmlTableColumn(
                     title='Group',
                     table='saves',
                     field='save_group',
                     img='save16',
                     display=True,
                    ),
            'save_volume': HtmlTableColumn(
                     title='Volume',
                     table='saves',
                     field='save_volume',
                     img='save16',
                     display=True,
                    ),
            'save_level': HtmlTableColumn(
                     title='Level',
                     table='saves',
                     field='save_level',
                     img='save16',
                     display=True,
                    ),
            'save_size': col_size_b(
                     title='Size',
                     table='saves',
                     field='save_size',
                     img='save16',
                     display=True,
                    ),
            'save_date': HtmlTableColumn(
                     title='Date',
                     table='saves',
                     field='save_date',
                     img='time16',
                     display=True,
                    ),
            'save_retention': HtmlTableColumn(
                     title='Retention',
                     table='saves',
                     field='save_retention',
                     img='time16',
                     display=True,
                    ),
        })
        self.colprops['save_nodename'].display = True
        self.colprops['save_server'].t = self
        self.colprops['save_nodename'].t = self
        self.colprops['save_svcname'].t = self
        self.extraline = True
        self.checkbox_id_col = 'id'
        self.checkbox_id_table = 'saves'
        self.dbfilterable = True
        self.ajax_col_values = 'ajax_saves_col_values'

@auth.requires_login()
def ajax_saves_col_values():
    t = table_saves('saves', 'ajax_saves')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.saves.id > 0
    l = db.v_nodes.on(db.saves.save_nodename==db.v_nodes.nodename)
    q = _where(q, 'saves', domain_perms(), 'save_nodename') | _where(q, 'saves', domain_perms(), 'save_svcname')
    q = apply_filters(q, db.saves.save_nodename, db.saves.save_svcname)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, groupby=o, left=l)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_saves():
    t = table_saves('saves', 'ajax_saves')
    o = ~db.saves.save_date
    o |= db.saves.save_nodename

    q = db.saves.id>0
    l = db.v_nodes.on(db.saves.save_nodename==db.v_nodes.nodename)
    q &= db.saves.save_nodename==db.v_nodes.nodename
    q = _where(q, 'saves', domain_perms(), 'save_nodename') | _where(q, 'saves', domain_perms(), 'save_svcname')
    q = apply_filters(q, db.saves.save_nodename, db.saves.save_svcname)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o, left=l)

    t.csv_q = q
    t.csv_orderby = o

    return t.html()

@auth.requires_login()
def saves():
    t = DIV(
          ajax_saves(),
          _id='saves',
        )
    return dict(table=t)


