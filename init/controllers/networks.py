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

class table_networks(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)

        # from models/colprops/
        self.cols = networks_cols
        self.colprops = networks_colprops

        self.extrarow = False
        self.extraline = True
        self.checkboxes = True
        self.dbfilterable = False
        self.dataable = True
        self.commonalityable = True
        self.span = ["id"]
        self.csv_limit = 30000
        self.force_cols = ['id']
        self.events = ['networks_change']

        for c in self.cols:
            self.colprops[c].table = 'networks'

        self.ajax_col_values = 'ajax_networks_col_values'

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
                     IMG(_src=URL(r=request, c='static', f='images/del16.png')),
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
                         IMG(_src=URL(r=request, c='static', f='images/add16.png')),
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
                     IMG(_src=URL(r=request, c='static', f='images/edit.png')),
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
                     _src=URL(r=request, c='static', f='images/add16.png'),
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
        response.flash = "network segment %s not found or insufficient privileges"%str(request.args[0])
        return dict(form="")
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
def ajax_networks_col_values():
    table_id = request.vars.table_id
    t = table_networks(table_id, 'ajax_networks')
    col = request.args[0]
    o = db.networks[col]
    q = db.networks.id > 0
    for f in t.cols:
        q = _where(q, 'networks', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_networks():
    table_id = request.vars.table_id
    t = table_networks(table_id, 'ajax_networks')

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

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        t.csv_limit = 10000
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=True)
        return t.table_lines_data(n, html=False)


@auth.requires_login()
def networks():
    t = SCRIPT(
          """$.when(osvc.app_started).then(function(){ table_networks("layout") })""",
        )
    return dict(table=t)

def networks_load():
    return networks()["table"]

