def _label(key):
    return DIV(
             IMG(
               _src=URL(r=request, c='static',
                        f=v_nodes_colprops[key].img+'.png'),
               _style='vertical-align:top;margin-right:10px',
             ),
             v_nodes_colprops[key].title,
           )

@auth.requires_membership('NodeManager')
def _node_form(record=None):
    if record is not None:
        deletable = True
    else:
        deletable = False
    return SQLFORM(db.nodes,
                 record=record,
                 deletable=deletable,
                 hidden_fields=['mem_bytes',
                                'mem_banks',
                                'mem_slots',
                                'os_name',
                                'os_kernel',
                                'os_vendor',
                                'os_release',
                                'os_arch',
                                'cpu_freq',
                                'cpu_dies',
                                'cpu_cores',
                                'cpu_model',
                                'cpu_vendor',
                                'environnement',
                                'serial',
                                'model'],
                 fields=['nodename',
                         'team_responsible',
                         'warranty_end',
                         'status',
                         'role',
                         'type',
                         'loc_country',
                         'loc_zip',
                         'loc_city',
                         'loc_addr',
                         'loc_building',
                         'loc_floor',
                         'loc_room',
                         'loc_rack',
                         'power_supply_nb',
                         'power_cabinet1',
                         'power_cabinet2',
                         'power_protect',
                         'power_protect_breaker',
                         'power_breaker1',
                         'power_breaker2',
                        ],
                 labels={
                         'nodename': _label('nodename'),
                         'team_responsible': _label('team_responsible'),
                         'warranty_end': _label('warranty_end'),
                         'status': _label('status'),
                         'role': _label('role'),
                         'type': _label('type'),
                         'loc_country': _label('loc_country'),
                         'loc_zip': _label('loc_zip'),
                         'loc_city': _label('loc_city'),
                         'loc_addr': _label('loc_addr'),
                         'loc_building': _label('loc_building'),
                         'loc_floor': _label('loc_floor'),
                         'loc_room': _label('loc_room'),
                         'loc_rack': _label('loc_rack'),
                         'power_supply_nb': _label('power_supply_nb'),
                         'power_cabinet1': _label('power_cabinet1'),
                         'power_cabinet2': _label('power_cabinet2'),
                         'power_protect': _label('power_protect'),
                         'power_protect_breaker': _label('power_protect_breaker'),
                         'power_breaker1': _label('power_breaker1'),
                         'power_breaker2': _label('power_breaker2'),
                        },
                )

@auth.requires_login()
def node_insert():
    form = _node_form()
    if form.accepts(request.vars):
        response.flash = T("edition recorded")
        redirect(URL(r=request, f='nodes'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)

@auth.requires_login()
def node_edit():
    query = (db.v_nodes.id>0)
    query &= _where(None, 'v_nodes', request.vars.node, 'nodename')
    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
    rows = db(query).select()
    if len(rows) != 1:
        response.flash = "vars: %s"%str(request.vars)
        return dict(form=None)
    record = rows[0]
    id = record.id
    record = db(db.v_nodes.id==id).select()[0]
    form = _node_form(record)
    if form.accepts(request.vars):
        response.flash = T("edition recorded")
        redirect(URL(r=request, f='nodes'))
    elif form.errors:
        response.flash = T("errors in form")

    return dict(form=form)

class table_nodes(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['nodename']+v_nodes_cols
        self.colprops = v_nodes_colprops
        self.colprops.update({
            'nodename': col_node(
                     title='Nodename',
                     field='nodename',
                     img='node16',
                     display=True,
                    ),
        })
        for c in self.cols:
            self.colprops[c].table = None
        for c in ['loc_building', 'loc_floor', 'loc_rack',
                  'cpu_dies', 'cpu_cores', 'cpu_model', 'mem_bytes',
                  'serial', 'team_responsible', 'environnement', 'status']:
            self.colprops[c].display = True
        self.colprops['nodename'].t = self
        self.extraline = True
        self.extrarow = True
        self.checkboxes = True
        self.checkbox_id_col = 'nodename'
        self.dbfilterable = True
        self.ajax_col_values = 'ajax_nodes_col_values'
        if 'NodeManager' in user_groups():
            self.additional_tools.append('node_add')
            self.additional_tools.append('node_del')
        self.additional_tools.append('pkgdiff')
        self.additional_tools.append('grpperf')
        if member_of(('Manager', 'CompExec')):
            self.additional_tools.append('tool_action')

    def tool_action(self):
        cmd = [
          'check',
          'fixable',
          'fix',
        ]
        sid = 'action_s'
        s = []
        for c in cmd:
            s.append(TR(
                       TD(
                         IMG(
                           _src=URL(r=request,c='static',f=action_img_h[c]),
                         ),
                       ),
                       TD(
                         A(
                           c,
                           _onclick="""if (confirm("%(text)s")){%(s)s};"""%dict(
                             s=self.ajax_submit(additional_inputs=[sid], args=['do_action', c]),
                             text=T("""Are you sure you want to execute a compliance %(a)s action on all selected nodes. Please confirm action""",dict(a=c)),
                           ),
                         ),
                       ),
                     ))

        q = db.comp_moduleset_modules.id > 0
        o = db.comp_moduleset_modules.modset_mod_name
        rows = db(q).select(orderby=o, groupby=o)
        options = [OPTION(g.modset_mod_name,_value=g.modset_mod_name) for g in rows]

        d = DIV(
              A(
                T("Compliance action"),
                _class='action16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='tool_action'),
              ),
              DIV(
                TABLE(
                  TR(
                    TH(
                      T("Action"),
                    ),
                    TD(
                      TABLE(*s),
                    ),
                  ),
                ),
                TABLE(
                  TR(
                    TH(
                      T("Module"),
                    ),
                    TD(
                      SELECT(
                        *options,
                        **dict(_id=sid,
                               _requires=IS_IN_DB(db, 'comp_modules.id'))
                      ),
                    ),
                  ),
                ),
                _style='display:none',
                _class='white_float',
                _name='tool_action',
                _id='tool_action',
              ),
              _class='floatw',
            )

        return d

    def format_extrarow(self, o):
        id = self.extra_line_key(o)
        s = self.colprops['nodename'].get(o)
        d = DIV(
              A(
                IMG(
                  _src=URL(r=request, c='static', f='edit.png'),
                  _style='vertical-align:middle',
                ),
                _href=URL(r=request, c='nodes', f='node_edit',
                          vars={'node':s,
                                '_next': URL(r=request)}
                      ),
              ),
            )
        return d

    def node_del(self):
        d = DIV(
              A(
                T("Delete nodes"),
                _class='del16',
                _onclick="""if (confirm("%(text)s")){%(s)s};"""%dict(
                   s=self.ajax_submit(args=['node_del']),
                   text=T("Deleting a node also deletes all its asset information. Please confirm user deletion"),
                ),
              ),
              _class='floatw',
            )
        return d

    def node_add(self):
        d = DIV(
              A(
                T("Add node"),
                _class='add16',
                _onclick="""location.href='node_insert?_next=%s'"""%URL(r=request),
              ),
              _class='floatw',
            )
        return d

    def grpperf(self):
        divid = 'grpperf'
        now = datetime.datetime.now()
        s = now - datetime.timedelta(days=0,
                                     hours=now.hour,
                                     minutes=now.minute,
                                     microseconds=now.microsecond)
        e = s + datetime.timedelta(days=1)
        timepicker = """Calendar.setup({inputField:this.id, ifFormat:"%Y-%m-%d %H:%M:%S", showsTime: true,timeFormat: "24"});"""

        d = DIV(
              A(
                T("Group performance"),
                _class='spark16',
                _onclick="""click_toggle_vis(event,'%(div)s', 'block');"""%dict(
                              div=divid,
                            ),
              ),
              DIV(
                SPAN(
                  INPUT(
                    _value=s.strftime("%Y-%m-%d %H:%M"),
                    _id='begin',
                    _class='datetime',
                    _onfocus=timepicker,
                  ),
                  INPUT(
                    _value=e.strftime("%Y-%m-%d %H:%M"),
                    _id='end',
                    _class='datetime',
                    _onfocus=timepicker,
                  ),
                  INPUT(
                    _value='gen',
                    _type='button',
                    _onClick="""sync_ajax("%(url)s?node="+checked_nodes(),['begin', 'end'],"%(div)s",function(){eval_js_in_ajax_response('plot')});"""%dict(url=URL(r=request,c='stats',f='ajax_perfcmp_plot'),
                             div="prf_cont"),
                  ),
                  DIV(
                    _id="prf_cont"
                  ),
                ),
                _style='display:none',
                _class='white_float',
                _name=divid,
                _id=divid,
              ),
              _class='floatw',
            )
        return d

    def pkgdiff(self):
        divid = 'pkgdiff'
        d = DIV(
              A(
                T("Package differences"),
                _class='pkg16',
                _onclick="""click_toggle_vis(event,'%(div)s', 'block');
                            ajax('%(url)s?node='+checked_nodes(), [], '%(div)s');"""%dict(
                              url=URL(r=request,c='pkgdiff',f='ajax_pkgdiff'),
                              div=divid,
                            ),
              ),
              DIV(
                _style='display:none',
                _class='white_float',
                _name=divid,
                _id=divid,
              ),

              _class='floatw',
            )
        return d

@auth.requires_membership('CompExec')
def do_action(ids, action=None):
    if action is None or len(action) == 0:
        raise ToolError("no action specified")
    if len(ids) == 0:
        raise ToolError("no target to execute %s on"%action)
    module = request.vars.action_s
    if module is None:
        raise ToolError("no module selected"%action)

    q = db.nodes.nodename.belongs(ids)
    q &= db.nodes.team_responsible.belongs(user_groups())
    rows = db(q).select(db.nodes.nodename)

    def fmt_action(node, action, module):
        cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                      '-o', 'ForwardX11=no',
                      '-o', 'PasswordAuthentication=no',
               'opensvc@'+node,
               '--',
               'sudo', '/opt/opensvc/bin/nodemgr', 'compliance', action,
               '--module', module]
        return ' '.join(cmd)

    vals = []
    vars = ['command']
    for row in rows:
        vals.append([fmt_action(row.nodename, action, module)])

    purge_action_queue()
    generic_insert('action_queue', vars, vals)
    from subprocess import Popen
    actiond = 'applications'+str(URL(r=request,c='actiond',f='actiond.py'))
    process = Popen(actiond)
    process.communicate()
    _log('service.action', 'run %(a)s of module %(m)s on nodes %(s)s', dict(
          a=action, s=','.join(map(lambda x: x.nodename, rows)), m=module))

@auth.requires_membership('NodeManager')
def node_del(ids):
    q = db.nodes.nodename.belongs(ids)
    u = ', '.join([r.nodename for r in db(q).select(db.nodes.nodename)])
    db(q).delete()
    _log('nodes.delete',
         'deleted nodes %(u)s',
         dict(u=u))

@auth.requires_login()
def ajax_nodes_col_values():
    t = table_nodes('nodes', 'ajax_nodes')
    col = request.args[0]
    o = db['v_nodes'][col]
    q = db.v_nodes.id > 0
    q = _where(q, 'v_nodes', domain_perms(), 'pkg_nodename')
    q = apply_db_filters(q, 'v_nodes')
    for f in t.cols:
        q = _where(q, 'v_nodes', t.filter_parse(f), f)
    t.object_list = db(q).select(orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_nodes():
    t = table_nodes('nodes', 'ajax_nodes')

    if len(request.args) >= 1:
        action = request.args[0]
        try:
            if action == 'node_del':
                node_del(t.get_checked())
            elif action == 'do_action' and len(request.args) == 2:
                saction = request.args[1]
                do_action(t.get_checked(), saction)
        except ToolError, e:
            t.flash = str(e)

    o = db.v_nodes.nodename
    q = db.v_nodes.id>0
    q = _where(q, 'v_nodes', domain_perms(), 'nodename')
    q = apply_db_filters(q, 'v_nodes')
    for f in t.cols:
        q = _where(q, 'v_nodes', t.filter_parse(f), f)
    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return t.html()

@auth.requires_login()
def nodes():
    t = DIV(
          ajax_nodes(),
          _id='nodes',
        )
    return dict(table=t)


