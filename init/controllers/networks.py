@auth.requires_membership('NetworkManager')
def _network_form(record=None):
    if record is not None:
        deletable = True
    else:
        deletable = False
    return SQLFORM(db.networks,
                 record=record,
                 deletable=deletable,
                 hidden_fields=['id'],
                 fields=[
                     'name',
                     'network',
                     'broadcast',
                     'netmask',
                     'team_responsible'],
                 labels={
                     'name': 'Name',
                     'network': 'Network',
                     'broadcast': 'Broadcast',
                     'netmask': 'Netmask',
                     'team_responsible': 'Team Responsible',
                 })

class table_networks(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'name',
                     'network',
                     'broadcast',
                     'netmask',
                     'team_responsible']
        self.colprops = {
            'id': HtmlTableColumn(
                     title='Network Id',
                     field='id',
                     img='network16',
                     display=True,
                    ),
            'name': HtmlTableColumn(
                     title='Name',
                     field='name',
                     img='network16',
                     display=True,
                    ),
            'network': HtmlTableColumn(
                     title='Network',
                     field='network',
                     img='network16',
                     display=True,
                    ),
            'broadcast': HtmlTableColumn(
                     title='Broadcast',
                     field='broadcast',
                     img='network16',
                     display=True,
                    ),
            'netmask': HtmlTableColumn(
                     title='Netmask',
                     field='netmask',
                     img='network16',
                     display=True,
                    ),
            'team_responsible': HtmlTableColumn(
                     title='Team Responsible',
                     field='team_responsible',
                     img='network16',
                     display=True,
                    ),
        }
        self.extrarow = True
        self.checkboxes = True
        self.dbfilterable = False
        self.ajax_col_values = 'ajax_networks_col_values'
        if 'NetworkManager' in user_groups():
            self.additional_tools.append('network_add')
            self.additional_tools.append('network_del')

    def format_extrarow(self, o):
        id = self.extra_line_key(o)
        s = self.colprops['id'].get(o)
        d = DIV(
              A(
                IMG(
                  _src=URL(r=request, c='static', f='edit.png'),
                  _style='vertical-align:middle',
                ),
                _href=URL(r=request, c='networks', f='network_edit',
                          vars={'network_id':s,
                                '_next': URL(r=request)}
                      ),
              ),
            )
        return d

    def network_del(self):
        d = DIV(
              A(
                T("Delete networks"),
                _class='del16',
                _onclick="""if (confirm("%(text)s")){%(s)s};"""%dict(
                   s=self.ajax_submit(args=['network_del']),
                   text=T("Please confirm network deletion"),
                ),
              ),
              _class='floatw',
            )
        return d

    def network_add(self):
        d = DIV(
              A(
                T("Add network"),
                _class='add16',
                _onclick="""location.href='network_add?_next=%s'"""%URL(r=request),
              ),
              _class='floatw',
            )
        return d

@auth.requires_login()
def network_add():
    form = _network_form()
    if form.accepts(request.vars):
        response.flash = T("edition recorded")
        _log('networks.add',
             'added network %(u)s',
             dict(u='/'.join((request.vars.network, request.vars.netmask))))
        redirect(URL(r=request, f='networks'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)

@auth.requires_membership('NetworkManager')
def network_del(ids):
    q = db.networks.id.belongs(ids)
    groups = user_groups()
    if 'Manager' not in groups:
        # Manager+NetworkManager can delete any network
        # NetworkManager can delete the networks they are responsible of
        q &= db.networks.team_responsible.belongs(groups)
    u = ', '.join(['/'.join((r.network, r.netmask)) for r in db(q).select()])
    db(q).delete()
    _log('networks.delete',
         'deleted networks %(u)s',
         dict(u=u))

@auth.requires_login()
def network_edit():
    query = (db.networks.id>0)
    query &= _where(None, 'networks', request.vars.network_id, 'id')
    groups = user_groups()
    if 'Manager' not in groups:
        # Manager+NetworkManager can edit any network
        # NetworkManager can edit the networks they are responsible of
        query &= db.networks.team_responsible.belongs(groups)
    rows = db(query).select()
    if len(rows) != 1:
        response.flash = "network %d not found or insufficient privileges"%request.vars.network_id
        return dict(form=None)
    record = rows[0]
    form = _network_form(record)
    if form.accepts(request.vars):
        response.flash = T("edition recorded")
        _log('networks.change',
             'edited network %(u)s',
             dict(u='/'.join((request.vars.network, request.vars.netmask))))
        redirect(URL(r=request, f='networks'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)

@auth.requires_login()
def ajax_networks_col_values():
    t = table_dns_domains('networks', 'ajax_networks')
    col = request.args[0]
    o = db.networks[col]
    q = db.networks.id > 0
    for f in set(t.cols)-set(t.special_filtered_cols):
        q = _where(q, 'networks', t.filter_parse(f), f)
    t.object_list = db(q).select(orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_networks():
    t = table_networks('networks', 'ajax_networks')

    if len(request.args) >= 1:
        action = request.args[0]
        try:
            if action == 'network_del':
                network_del(t.get_checked())
        except ToolError, e:
            t.flash = str(e)

    o = ~db.networks.name
    q = db.networks.id > 0
    for f in set(t.cols):
        q = _where(q, 'networks', t.filter_parse(f), f)
    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)

    return t.html()

@auth.requires_login()
def networks():
    t = DIV(
          ajax_networks(),
          _id='networks',
        )
    return dict(table=t)


