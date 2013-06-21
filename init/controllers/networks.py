@auth.requires_membership('NetworkManager')
def _segment_form(record=None, net_id=None):
    if record is not None:
        deletable = True
    else:
        deletable = False
    f = SQLFORM(db.network_segments,
                 record=record,
                 deletable=deletable,
                 hidden_fields=['id'],
                 fields=[
                     'net_id',
                     'seg_begin',
                     'seg_end',
                     'seg_type'],
                 labels={
                     'net_id': 'Network id',
                     'seg_begin': 'Begin',
                     'seg_end': 'End',
                     'seg_type': 'Allocation type',
                 })
    f.vars.net_id = net_id
    f.vars.seg_type = "static"
    q = db.networks.id == net_id
    rows = db(q).select()
    if len(rows) == 1:
        f.vars.seg_begin = rows[0].network
        f.vars.seg_end = rows[0].broadcast
    return f

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
                     'pvid',
                     'network',
                     'broadcast',
                     'netmask',
                     'gateway',
                     'begin',
                     'end',
                     'team_responsible',
                     'comment'],
                 labels={
                     'name': 'Name',
                     'pvid': 'VLAN id',
                     'network': 'Network',
                     'broadcast': 'Broadcast',
                     'netmask': 'Netmask',
                     'gateway': 'Gateway',
                     'begin': 'Ip range begin',
                     'end': 'Ip range end',
                     'team_responsible': 'Team Responsible',
                     'comment': 'Comment',
                 })

class col_name(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        domain_id = self.t.colprops["id"].get(o)

        d = DIV(
              A(
                s,
                _onclick="""
if ($("#networks_x_%(domain_id)d").is(":visible")) {
  $("#networks_x_%(domain_id)d").hide()
} else {
  $("#networks_x_%(domain_id)d").show()
  ajax("%(url)s", [], "networks_x_%(domain_id)d")
}
"""%dict(domain_id=domain_id,
         url=URL(r=request, f="segments", args=[domain_id]),
        ),
              ),
            )
        return d

class table_networks(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'name',
                     'pvid',
                     'network',
                     'broadcast',
                     'netmask',
                     'gateway',
                     'begin',
                     'end',
                     'team_responsible',
                     'comment']
        self.colprops = {
            'id': HtmlTableColumn(
                     title='Network Id',
                     field='id',
                     img='net16',
                     display=True,
                    ),
            'pvid': col_name(
                     title='VLAN id',
                     field='pvid',
                     img='net16',
                     display=True,
                    ),
            'begin': col_name(
                     title='Ip range begin',
                     field='begin',
                     img='net16',
                     display=True,
                    ),
            'end': col_name(
                     title='Ip range end',
                     field='end',
                     img='net16',
                     display=True,
                    ),
            'gateway': col_name(
                     title='Gateway',
                     field='gateway',
                     img='net16',
                     display=True,
                    ),
            'comment': col_name(
                     title='Comment',
                     field='comment',
                     img='net16',
                     display=True,
                    ),
            'name': col_name(
                     title='Name',
                     field='name',
                     img='net16',
                     display=True,
                    ),
            'network': HtmlTableColumn(
                     title='Network',
                     field='network',
                     img='net16',
                     display=True,
                    ),
            'broadcast': HtmlTableColumn(
                     title='Broadcast',
                     field='broadcast',
                     img='net16',
                     display=True,
                    ),
            'netmask': HtmlTableColumn(
                     title='Netmask',
                     field='netmask',
                     img='net16',
                     display=True,
                    ),
            'team_responsible': HtmlTableColumn(
                     title='Team Responsible',
                     field='team_responsible',
                     img='guys16',
                     display=True,
                    ),
        }
        for c in self.cols:
            self.colprops[c].t = self
        self.extrarow = True
        self.extraline = True
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
def segments():
    net_id = request.args[0]
    q = db.v_network_segments.net_id == net_id
    rows = db(q).select()
    l = []
    l.append(DIV(
                 DIV(
                   T("Edit"),
                   _style="font-weight:bold"
                 ),
                 DIV(
                   T("Begin"),
                   _style="font-weight:bold"
                 ),
                 DIV(
                   "",
                   _style="font-weight:bold"
                 ),
                 DIV(
                   T("End"),
                   _style="font-weight:bold"
                 ),
                 DIV(
                   T("Allocation type"),
                   _style="font-weight:bold"
                 ),
                 DIV(
                   T("Teams responsible"),
                   _style="font-weight:bold"
                 ),
               ))

    if len(rows) == 0:
        l.append(DIV(
                 DIV(
                   "-",
                 ),
                 DIV(
                   "-",
                 ),
                 DIV(
                   "",
                 ),
                 DIV(
                   "-",
                 ),
                 DIV(
                   "-",
                 ),
                 DIV(
                   "-",
                 ),
               ))

    ug = user_groups()

    for row in rows:
        if row.teams_responsible is None:
            resp_l = []
        else:
            resp_l = row.teams_responsible.split(", ")
        resp = []
        name = '-'.join((row.seg_begin, row.seg_end))
        for i, r in enumerate(resp_l):
            if "Manager" in ug or \
               ("NetworkManager" in ug and network_team_responsible in ug):
                tool_del = DIV(
                   r,
                   A(
                     IMG(_src=URL(r=request, c='static', f='del16.png')),
                     _onclick="""
function f() {
  ajax("%(url1)s", [], "networks_x_%(net_id)s")
}
if (confirm("%(msg)s")) {
  sync_ajax("%(url2)s", [], "networks_x_%(net_id)s", f);
}"""%dict(
                       net_id=net_id,
                       url1=URL(r=request, f="segments", args=[net_id]),
                       url2=URL(r=request, f='detach_group', args=[row.id, r]),
                       msg=T("Please confirm the detachment of group %(r)s from segment %(name)s",dict(r=r, name=name))),
                     _id="dtr_%d_%s"%(row.id, i),
                     _style="display:none;vertical-align:middle;padding-left:0.5em",
                   ),
                   _style="display:table-cell;padding:0 0.5em 0 0",
                   _onmouseover="""$("#dtr_%d_%d").show()"""%(row.id, i),
                   _onmouseout="""$("#dtr_%d_%d").hide()"""%(row.id, i),
              )
            else:
                tool_del = SPAN(
                   r,
                )
            if i > 0:
                resp.append(", ")
            resp.append(tool_del)

        if "Manager" in ug or \
           ("NetworkManager" in ug and network_team_responsible in ug):
            resp_div = DIV(
                       SPAN(resp),
                       A(
                         IMG(_src=URL(r=request, c='static', f='add16.png')),
                         _onclick="""$('#add_group_%(net_id)s').show();
    ajax("%(url)s", [], "add_group_%(net_id)s");"""%dict(
                           net_id=net_id,
                           url=URL(r=request, f='attach_group_form', args=[row.id])),
                         _id="tr_%d"%row.id,
                         _style="display:none;vertical-align:middle;padding-left:0.5em",
                       ),
                       _onmouseover="""$("#tr_%d").show()"""%row.id,
                       _onmouseout="""$("#tr_%d").hide()"""%row.id,
                     )
        else:
            resp_div = DIV(resp)

        l.append(DIV(
                 DIV(
                   A(
                     IMG(_src=URL(r=request, c='static', f='edit.png')),
                     _href=URL(r=request, f='segment_edit', args=[row.id]),
                   ),
                 ),
                 DIV(
                   row.seg_begin,
                 ),
                 DIV(
                   "-",
                 ),
                 DIV(
                   row.seg_end,
                 ),
                 DIV(
                   row.seg_type,
                 ),
                 resp_div,
                 _style="display:table-row",
               ))

    #
    # display the "add segment" tool only if the user has enough privs
    #
    q = db.networks.id == net_id
    network_team_responsible = db(q).select()[0].team_responsible
    if "Manager" in ug or \
       ("NetworkManager" in ug and network_team_responsible in ug):
        tools = DIV(
                 A(
                   IMG(
                     _src=URL(r=request, c='static', f='add16.png'),
                     _style="padding:0 0.5em 0 0;vertical-align:top",
                   ),
                   T("Add segment"),
                   _href=URL(r=request, f='segment_add', args=[net_id]),
                 ),
               )
    else:
        tools = SPAN()

    return DIV(
             DIV(
               H3(T("Segments")),
               tools,
               _style="float:left;padding:0.5em 2em 0.5em 1em",
             ),
             DIV(
               H3(XML("&nbsp;")),
               DIV(l, _class="table0"),
               _style="float:left;padding:0.5em 1em 0.5em 1em",
             ),
             DIV(
               H3(T("Attach group to segment")),
               T("loading"),
               _id="add_group_%s"%net_id,
               _style="float:left;padding:0.5em 1em 0.5em 1em;display:none",
             ),
           )

@auth.requires_login()
def attach_group_form():
    seg_id = request.args[0]

    q = db.network_segments.id == seg_id
    rows = db(q).select()
    net_id = rows[0].net_id
    begin = rows[0].seg_begin
    end = rows[0].seg_end
    name = '-'.join((begin, end))

    q = db.network_segments.id == seg_id
    q &= db.network_segments.id == db.network_segment_responsibles.seg_id
    q &= db.network_segment_responsibles.group_id == db.auth_group.id
    rows = db(q).select()
    already_attached = [r.auth_group.id for r in rows]

    q = ~db.auth_group.role.like("user_%")
    q &= ~db.auth_group.role.like("%Manager")
    q &= ~db.auth_group.role.like("%Exec")
    if len(already_attached) > 0:
        q &= ~db.auth_group.id.belongs(already_attached)
    rows = db(q).select(orderby=db.auth_group.role)

    l = []
    for row in rows:
        l.append(OPTION(row.role, _value=row.id))

    d = DIV(
          H3(T("Attach group to segment %(name)s"%dict(name=name))),
          SELECT(l, _id="add_group_select_%s"%net_id),
          INPUT(
            _type="submit",
            _onclick="""
function f() {
  ajax("%(url1)s", [], "networks_x_%(net_id)s")
}
sync_ajax("%(url2)s", ["add_group_select_%(net_id)s"], "add_group_%(net_id)s", f)"""%dict(
              url2=URL(r=request, f='attach_group', args=[seg_id]),
              url1=URL(r=request, f="segments", args=[net_id]),
              net_id=net_id,
            )
          ),
        )
    return d

@auth.requires_login()
def attach_group():
    seg_id = request.args[0]

    q = db.network_segments.id == seg_id
    rows = db(q).select()
    net_id = rows[0].net_id
    group_id = request.vars["add_group_select_%s"%net_id]

    q = db.auth_group.id == group_id
    role = db(q).select()[0].role

    db.network_segment_responsibles.insert(seg_id=seg_id, group_id=group_id)
    _log('networks.segment.attach',
         'attached group %(r)s to network segment %(u)s',
         dict(r=role, u='-'.join((rows[0].seg_begin, rows[0].seg_end))))
    return ""

@auth.requires_login()
def detach_group():
    seg_id = request.args[0]
    role = request.args[1]

    q = db.auth_group.role == role
    rows = db(q).select()
    group_id = rows[0].id

    q = db.network_segment_responsibles.seg_id == seg_id
    q &= db.network_segment_responsibles.group_id == group_id
    db(q).delete()

    q = db.network_segments.id == seg_id
    rows = db(q).select()

    _log('networks.segment.detach',
         'detached group %(r)s from network segment %(u)s',
         dict(r=role, u='-'.join((rows[0].seg_begin, rows[0].seg_end))))

    return T("loading")

def add_default_team_responsible(b, e):
    q = db.network_segments.seg_begin == b
    q &= db.network_segments.seg_end == e
    seg_id = db(q).select()[0].id
    q = db.auth_membership.user_id == auth.user_id
    q &= db.auth_membership.group_id == db.auth_group.id
    q &= db.auth_group.role.like('user_%')
    try:
        group_id = db(q).select()[0].auth_group.id
    except:
        q = db.auth_group.role == 'Manager'
        group_id = db(q).select()[0].id
    db.network_segment_responsibles.insert(seg_id=seg_id,
                                           group_id=group_id)

@auth.requires_login()
def segment_add():
    form = _segment_form(net_id=request.args[0])
    if form.accepts(request.vars):
        add_default_team_responsible(request.vars.seg_begin, request.vars.seg_end)
        response.flash = T("edition recorded")
        _log('networks.segment.add',
             'added network %(u)s',
             dict(u='-'.join((request.vars.seg_begin, request.vars.seg_end))))
        redirect(URL(r=request, f='networks'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)

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
def segment_edit():
    query = (db.network_segments.id>0)
    query &= _where(None, 'network_segments', request.args[0], 'id')
    groups = user_groups()
    #if 'Manager' not in groups:
        # Manager+NetworkManager can edit any network
        # NetworkManager can edit the networks they are responsible of
    #    query &= db.networks.team_responsible.belongs(groups)
    rows = db(query).select()
    if len(rows) != 1:
        response.flash = "network segment %d not found or insufficient privileges"%request.args[0]
        return dict(form=None)
    record = rows[0]
    form = _segment_form(record=record)
    if form.accepts(request.vars):
        response.flash = T("edition recorded")
        _log('networks.segment.change',
             'edited network segment %(u)s',
             dict(u='-'.join((record.seg_begin, record.seg_end))))
        redirect(URL(r=request, f='networks'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)

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
    t = table_networks('networks', 'ajax_networks')
    col = request.args[0]
    o = db.networks[col]
    q = db.networks.id > 0
    for f in t.cols:
        q = _where(q, 'networks', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

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


