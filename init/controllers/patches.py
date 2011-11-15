import datetime

now = datetime.datetime.now()
deadline = now - datetime.timedelta(days=1)
def outdated(t):
     if t is None: return True
     if t < deadline: return True
     return False

class col_node(HtmlTableColumn):
    def html(self, o):
        id = self.t.extra_line_key(o)
        s = self.get(o)
        d = DIV(
              node_icon(o.v_nodes.os_name),
              A(
                s,
                _onclick="toggle_extra('%(url)s', '%(id)s');"%dict(
                  url=URL(r=request, c='ajax_node',f='ajax_node',
                          vars={'node': s, 'rowid': id}),
                  id=id,
                ),
              ),
            )
        return d

class col_updated(HtmlTableColumn):
    def html(self, o):
       d = self.get(o)
       if outdated(d):
           alert = 'color:darkred;font-weight:bold'
       else:
           alert = ''
       return SPAN(d, _style=alert)

class table_patches(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['nodename']+v_nodes_cols
        self.cols += ['patch_rev',
                      'patch_num',
                      'patch_updated']
        self.colprops = v_nodes_colprops
        self.colprops.update({
            'nodename': col_node(
                     title='Nodename',
                     table='v_nodes',
                     field='nodename',
                     img='node16',
                     display=True,
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
            'patch_updated': col_updated(
                     title='Updated',
                     table='patches',
                     field='patch_updated',
                     img='pkg16',
                     display=True,
                    ),
        })
        self.colprops['nodename'].display = True
        self.colprops['nodename'].t = self
        self.dbfilterable = True
        self.extraline = True
        self.checkbox_id_col = 'id'
        self.checkbox_id_table = 'patches'
        self.ajax_col_values = 'ajax_patches_col_values'

@auth.requires_login()
def ajax_patches_col_values():
    t = table_patches('patches', 'ajax_patches')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.patches.patch_nodename==db.v_nodes.nodename
    q = _where(q, 'patches', domain_perms(), 'patch_nodename')
    q = apply_gen_filters(q, t.tables())

    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_patches():
    t = table_patches('patches', 'ajax_patches')
    o = db.patches.patch_nodename
    o |= db.patches.patch_num
    o |= db.patches.patch_rev

    q = db.patches.id>0
    q &= db.patches.patch_nodename==db.v_nodes.nodename
    q = _where(q, 'patches', domain_perms(), 'patch_nodename')
    q = apply_gen_filters(q, t.tables())

    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return t.html()

@auth.requires_login()
def patches():
    t = DIV(
          ajax_patches(),
          _id='patches',
        )
    return dict(table=t)


