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
                                'cpu_threads',
                                'cpu_model',
                                'cpu_vendor',
                                'host_mode',
                                'serial',
                                'model'],
                 fields=['nodename',
                         'assetname',
                         'fqdn',
                         'team_responsible',
                         'team_integ',
                         'team_support',
                         'project',
                         'warranty_end',
                         'maintenance_end',
                         'status',
                         'role',
                         'type',
                         'enclosure',
                         'enclosureslot',
                         'sec_zone',
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
                         'assetname': _label('assetname'),
                         'fqdn': _label('fqdn'),
                         'team_responsible': _label('team_responsible'),
                         'team_integ': _label('team_integ'),
                         'team_support': _label('team_support'),
                         'project': _label('project'),
                         'warranty_end': _label('warranty_end'),
                         'maintenance_end': _label('maintenance_end'),
                         'status': _label('status'),
                         'role': _label('role'),
                         'type': _label('type'),
                         'enclosure': _label('enclosure'),
                         'enclosureslot': _label('enclosureslot'),
                         'loc_country': _label('loc_country'),
                         'sec_zone': _label('sec_zone'),
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
    import gluon.contrib.pymysql.err
    try:
        if form.accepts(request.vars):
            table_modified("nodes")
            update_dash_node_without_maintenance_end(request.vars.nodename)
            update_dash_node_beyond_maintenance_end(request.vars.nodename)
            update_dash_node_near_maintenance_end(request.vars.nodename)
            delete_dash_node_not_updated(request.vars.nodename)
            delete_dash_node_without_asset(request.vars.nodename)
            table_modified("dashboard")
            response.flash = T("edition recorded")
            redirect(URL(r=request, f='nodes'))
        elif form.errors:
            response.flash = T("errors in form")
    except gluon.contrib.pymysql.err.IntegrityError:
        response.flash = T("Integrity Error")
    return dict(form=form)

@auth.requires_login()
def node_edit():
    query = (db.v_nodes.id>0)
    query &= _where(None, 'v_nodes', request.vars.node, 'nodename')
    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
    groups = user_groups()
    if 'Manager' not in groups:
        # Manager+NodeManager can edit any node
        # NodeManager can edit the nodes they are responsible of
        query &= db.v_nodes.team_responsible.belongs(groups)
    rows = db(query).select()
    if len(rows) != 1:
        response.flash = "node %s not found or insufficient privileges"%request.vars.node
        return dict(form=None)
    record = rows[0]
    id = record.id
    record = db(db.v_nodes.id==id).select()[0]
    form = _node_form(record)
    if form.accepts(request.vars):
        # update dashboard
        table_modified("nodes")
        update_dash_node_without_maintenance_end(request.vars.node)
        update_dash_node_beyond_maintenance_end(request.vars.node)
        update_dash_node_near_maintenance_end(request.vars.node)
        delete_dash_node_not_updated(request.vars.node)
        delete_dash_node_without_asset(request.vars.node)
        table_modified("dashboard")

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
        self.span = ["nodename"]
        self.keys = ["nodename"]
        self.colprops.update({
            'nodename': HtmlTableColumn(
                     title='Nodename',
                     field='nodename',
                     img='node16',
                     display=True,
                     _class='nodename',
                    ),
        })
        for c in self.cols:
            self.colprops[c].table = 'v_nodes'

        self.colprops.update({
            'app_domain': HtmlTableColumn(
                     title='App domain',
                     field='app_domain',
                     img='svc',
                     table='apps',
                     display=False,
                    ),
            'app_team_ops': HtmlTableColumn(
                     title='Ops team',
                     field='app_team_ops',
                     img='guys16',
                     table='apps',
                     display=False,
                    ),
        })
        self.cols.insert(self.cols.index('team_integ')+1, 'app_team_ops')
        self.cols.insert(self.cols.index('project')+1, 'app_domain')

        for c in ['loc_building', 'loc_floor', 'loc_rack',
                  'cpu_dies', 'cpu_cores', 'cpu_model', 'mem_bytes',
                  'serial', 'team_responsible', 'host_mode', 'status']:
            self.colprops[c].display = True
        self.colprops['nodename'].t = self
        self.extraline = True
        self.extrarow = True
        self.checkboxes = True
        self.checkbox_id_col = 'nodename'
        self.checkbox_id_table = 'v_nodes'
        self.dbfilterable = True
        self.ajax_col_values = 'ajax_nodes_col_values'
        if 'NodeManager' in user_groups():
            self.additional_tools.append('node_add')
            self.additional_tools.append('node_del')
        self.additional_tools.append('nodediff')
        self.additional_tools.append('grpperf')
        self.additional_tools.append('santopo')
        if member_of(('Manager', 'CompExec')):
            self += HtmlTableMenu('Action', 'action16', ['tool_action_node', 'tool_action_module', 'tool_action_moduleset'], id='menu_comp_action')

    def tool_action_node(self):
        return self._tool_action("node")

    def tool_action_module(self):
        return self._tool_action("module")

    def tool_action_moduleset(self):
        return self._tool_action("moduleset")

    def _tool_action(self, mode):
        if mode in ["module", "moduleset"]:
            cmd = [
              'check',
              'fixable',
              'fix',
            ]
            cl = "comp16"
        else:
            cmd = [
              'checks',
              'pushasset',
              'pushservices',
              'pushstats',
              'pushpkg',
              'pushpatch',
              'reboot',
              'shutdown',
              'syncservices',
              'updatecomp',
              'updatepkg',
              'updateservices',
            ]
            cl = "node16"

        sid = 'action_s_'+mode
        s = []
        for c in cmd:
            if mode in ["module", "moduleset"]:
                confirm=T("""Are you sure you want to execute a %(a)s action on all selected nodes. Please confirm action""",dict(a=c))
            else:
                confirm=T("""Are you sure you want to execute a compliance %(a)s action on all selected nodes. Please confirm action""",dict(a=c))
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
                             s=self.ajax_submit(additional_inputs=[sid], args=['do_action', c, mode]),
                             text=confirm,
                           ),
                         ),
                       ),
                     ))

        if mode == "module":
            q = db.comp_moduleset_modules.id > 0
            o = db.comp_moduleset_modules.modset_mod_name
            rows = db(q).select(orderby=o, groupby=o)
            options = [OPTION(g.modset_mod_name,_value=g.modset_mod_name) for g in rows]
            id_col = 'comp_modules.id'
        elif mode == "moduleset":
            q = db.comp_moduleset.id > 0
            o = db.comp_moduleset.modset_name
            rows = db(q).select(orderby=o)
            options = [OPTION(g.modset_name,_value=g.modset_name) for g in rows]
            id_col = 'comp_moduleset.id'

        if mode in ["module", "moduleset"]:
            fancy_mode = mode[0].upper()+mode[1:].lower()
            actions = TABLE(
                          TR(
                            TH(
                              T("Action"),
                            ),
                            TD(
                              TABLE(*s),
                            ),
                          ),
                        )
            selector = TABLE(
                          TR(
                            TH(
                              T(fancy_mode),
                            ),
                            TD(
                              SELECT(
                                *options,
                                **dict(_id=sid,
                                       _requires=IS_IN_DB(db, id_col))
                              ),
                            ),
                          ),
                        )
        else:
            actions = TABLE(*s)
            selector = SPAN()

        d = DIV(
              A(
                T("Run "+mode),
                _class=cl,
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='tool_action_'+mode),
              ),
              DIV(
                actions,
                selector,
                _style='display:none',
                _class='white_float',
                _name='tool_action_'+mode,
                _id='tool_action_'+mode,
              ),
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
                   text=T("Deleting a node also deletes all its asset information. Please confirm node deletion"),
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
                  ),
                  INPUT(
                    _value=e.strftime("%Y-%m-%d %H:%M"),
                    _id='end',
                    _class='datetime',
                  ),
                  INPUT(
                    _value='gen',
                    _type='button',
                    _onClick="""sync_ajax("%(url)s?node="+checked_nodes(),['begin', 'end'],"%(div)s",function(){});"""%dict(url=URL(r=request,c='stats',f='ajax_perfcmp_plot'),
                             div="prf_cont"),
                  ),
                  DIV(
                    _id="prf_cont"
                  ),
                  SCRIPT(
                    """$(".datetime").datetimepicker({dateFormat: "yy-mm-dd"})""",
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

    def santopo(self):
        divid = 'santopo'
        d = DIV(
              A(
                T("SAN topology"),
                _class='hd16',
                _onclick="""click_toggle_vis(event,'%(div)s', 'block');
                            ajax('%(url)s?nodes='+checked_nodes(), [], '%(div)s');"""%dict(
                              url=URL(r=request,c='ajax_node',f='ajax_nodes_stor'),
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

    def nodediff(self):
        divid = 'nodediff'
        d = DIV(
              A(
                T("Node differences"),
                _class='common16',
                _onclick="""click_toggle_vis(event,'%(div)s', 'block');
                            sync_ajax('%(url)s?node='+checked_nodes(), [], '%(div)s', function(){});"""%dict(
                              url=URL(r=request,c='nodediff',f='ajax_nodediff'),
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
def do_action(ids, action=None, mode=None):
    if mode not in ("module", "moduleset", "node"):
        raise ToolError("unsupported mode")
    if action is None or len(action) == 0:
        raise ToolError("no action specified")
    if len(ids) == 0:
        raise ToolError("no target to execute %s on"%action)

    if mode in ("module", "moduleset"):
        if not hasattr(request.vars, 'action_s_'+mode):
            raise ToolError("no module or moduleset selected")
        mod = request.vars['action_s_'+mode]

        def fmt_action(node, action, mode):
            cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                          '-o', 'ForwardX11=no',
                          '-o', 'PasswordAuthentication=no',
                          '-tt',
                   'opensvc@'+node,
                   '--',
                   'sudo', '/opt/opensvc/bin/nodemgr', 'compliance', action,
                   '--'+mode, mod]
            return ' '.join(cmd)
    elif mode == "node":
        def fmt_action(node, action, mode):
            cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                          '-o', 'ForwardX11=no',
                          '-o', 'PasswordAuthentication=no',
                          '-tt',
                   'opensvc@'+node,
                   '--',
                   'sudo', '/opt/opensvc/bin/nodemgr', action,
                   '--force']
            return ' '.join(cmd)

    q = db.nodes.nodename.belongs(ids)
    q &= db.nodes.team_responsible.belongs(user_groups())
    rows = db(q).select(db.nodes.nodename, db.nodes.fqdn, db.nodes.os_name)

    vals = []
    vars = ['nodename', 'action_type', 'command', 'user_id']

    for row in rows:
        if row.fqdn is not None and len(row.fqdn) > 0:
            node = row.fqdn
        else:
            node = row.nodename

        if row.os_name == "Windows":
            action_type = "pull"
            command = action
        else:
            action_type = "push"
            command = fmt_action(node, action, mode)

        vals.append([row.nodename, action_type, command, str(auth.user_id)])

    purge_action_queue()
    generic_insert('action_queue', vars, vals)

    from subprocess import Popen
    actiond = 'applications'+str(URL(r=request,c='actiond',f='actiond.py'))
    process = Popen(actiond)
    process.communicate()

    if mode in ("module", "moduleset"):
        _log('node.action', 'run %(a)s of %(mode)s %(m)s on nodes %(s)s', dict(
              a=action,
              mode=mode,
              s=','.join(map(lambda x: x.nodename, rows)),
              m=mod))
    elif mode == "node":
        _log('node.action', 'run %(a)s on nodes %(s)s', dict(
              a=action,
              s=','.join(map(lambda x: x.nodename, rows)),
              ))

@auth.requires_membership('NodeManager')
def node_del(ids):
    q = db.nodes.nodename.belongs(ids)
    groups = user_groups()
    if 'Manager' not in groups:
        # Manager+NodeManager can delete any node
        # NodeManager can delete the nodes they are responsible of
        q &= db.nodes.team_responsible.belongs(groups)
    rows = db(q).select(db.nodes.nodename)
    u = ', '.join([r.nodename for r in rows])
    for nodename in [r.nodename for r in rows]:
        delete_dash_node(nodename)
        delete_svcmon(nodename)
        delete_pkg(nodename)
        delete_patches(nodename)
        delete_checks(nodename)

    db(q).delete()
    table_modified("nodes")
    _log('nodes.delete',
         'deleted nodes %(u)s',
         dict(u=u))

@auth.requires_login()
def ajax_nodes_col_values():
    t = table_nodes('nodes', 'ajax_nodes')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.v_nodes.id > 0
    j = db.apps.app == db.v_nodes.project
    l = db.apps.on(j)
    q = _where(q, 'v_nodes', domain_perms(), 'nodename')
    q = apply_filters(q, db.v_nodes.nodename, None)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, left=l)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_nodes():
    t = table_nodes('nodes', 'ajax_nodes')

    if len(request.args) >= 1:
        action = request.args[0]
        try:
            if action == 'node_del':
                node_del(t.get_checked())
            elif action == 'do_action' and len(request.args) == 3:
                saction = request.args[1]
                mode = request.args[2]
                do_action(t.get_checked(), saction, mode)
        except ToolError, e:
            t.flash = str(e)

    o = db.v_nodes.nodename
    q = db.v_nodes.id>0
    j = db.apps.app == db.v_nodes.project
    l = db.apps.on(j)
    q = _where(q, 'v_nodes', domain_perms(), 'nodename')
    q = apply_filters(q, db.v_nodes.nodename, None)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'line':
        if request.vars.volatile_filters is None:
            n = db(q).select(db.v_nodes.id.count(), left=l).first()(db.v_nodes.id.count())
            limitby = (t.pager_start,t.pager_end)
        else:
            n = 0
            limitby = (0, 500)
        t.object_list = db(q).select(orderby=o, limitby=limitby, cacheable=False, left=l)
        return t.table_lines_data(n)

    n = db(q).select(db.v_nodes.id.count(), left=l).first()(db.v_nodes.id.count())
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o, left=l)

    t.csv_q = q
    t.csv_orderby = o
    t.csv_limit = 10000
    t.csv_left = l
    if len(request.args) == 1 and request.args[0] == 'csv':
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        return t.do_commonality()

    mt = table_obs_agg('obs_agg', 'ajax_obs_agg')
    ut = table_uids('uids', 'ajax_uids')
    gt = table_gids('gids', 'ajax_gids')
    return DIV(
             DIV(
               T("Obsolescence Statistics"),
               _style="text-align:left;font-size:120%;background-color:#e0e1cd",
               _class="right16 clickable",
               _onclick="""
               if (!$("#obs_agg").is(":visible")) {
                 $(this).addClass("down16");
                 $(this).removeClass("right16");
                 $("#obs_agg").show(); %s ;
               } else {
                 $(this).addClass("right16");
                 $(this).removeClass("down16");
                 $("#obs_agg").hide();
               }"""%mt.ajax_submit(additional_inputs=t.ajax_inputs()),
             ),
             DIV(
               IMG(_src=URL(r=request,c='static',f='spinner.gif')),
                _style="display:none",
               _id="obs_agg",
             ),
             DIV(
               T("User mapping"),
               _style="text-align:left;font-size:120%;background-color:#e0e1cd",
               _class="right16 clickable",
               _onclick="""
               if (!$("#uids").is(":visible")) {
                 $(this).addClass("down16");
                 $(this).removeClass("right16");
                 $("#uids").show(); %s ;
               } else {
                 $(this).addClass("right16");
                 $(this).removeClass("down16");
                 $("#uids").hide();
               }"""%ut.ajax_submit(additional_inputs=t.ajax_inputs()),
             ),
             DIV(
               IMG(_src=URL(r=request,c='static',f='spinner.gif')),
                _style="display:none",
               _id="uids",
             ),
             DIV(
               T("Group mapping"),
               _style="text-align:left;font-size:120%;background-color:#e0e1cd",
               _class="right16 clickable",
               _onclick="""
               if (!$("#gids").is(":visible")) {
                 $(this).addClass("down16");
                 $(this).removeClass("right16");
                 $("#gids").show(); %s ;
               } else {
                 $(this).addClass("right16");
                 $(this).removeClass("down16");
                 $("#gids").hide();
               }"""%gt.ajax_submit(additional_inputs=t.ajax_inputs()),
             ),
             DIV(
               IMG(_src=URL(r=request,c='static',f='spinner.gif')),
                _style="display:none",
               _id="gids",
             ),
             t.html(),
           )

@auth.requires_login()
def nodes():
    t = DIV(
          ajax_nodes(),
          _id='nodes',
        )
    return dict(table=t)

def delete_pkg(nodename):
    q = db.packages.pkg_nodename == nodename
    db(q).delete()
    table_modified("packages")

def delete_patches(nodename):
    q = db.patches.patch_nodename == nodename
    db(q).delete()
    table_modified("patches")

def delete_checks(nodename):
    q = db.checks_live.chk_nodename == nodename
    db(q).delete()
    table_modified("checks_live")

def delete_svcmon(nodename):
    sql = """delete from svcmon
               where
                 mon_nodname="%(nodename)s"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)
    db.commit()
    table_modified("svcmon")

class col_obs_chart(HtmlTableColumn):
    def html(self, o):
       h = self.get(o)
       return DIV(
                DIV(
                  H3(T("Hardware obsolescence warning roadmap")),
                  DIV(
                    json.dumps(h['hw_warn_chart_data']),
                    _id='hw_warn_chart',
                  ),
                  _style="float:left;width:350px",
                ),
              )

class col_user_id(HtmlTableColumn):
    def html(self, o):
        id = self.t.extra_line_key(o)
        h = self.get(o)
        d = DIV(
              A(
                o['user_id'],
                _onclick="toggle_extra('%(url)s', '%(id)s', this, 0);"%dict(
                  url=URL(r=request, c='nodes',f='ajax_uid_dispatch',
                          vars={'user_id': o['user_id']}),
                  id=id,
                ),
              ),
              _class='nowrap',
            )
        return d

class table_uids(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['user_id',
                     'user_id_count',
                     'user_name']
        self.keys = ["user_id"]
        self.span = ["user_id"]
        self.colprops = {
            'user_id': col_user_id(
                     title='User id',
                     field='user_id',
                     table='v_uids',
                     img='guy16',
                     display=True,
                    ),
            'user_id_count': HtmlTableColumn(
                     title='User count',
                     field='user_id_count',
                     table='v_uids',
                     img='guy16',
                     display=True,
                    ),
            'user_name': HtmlTableColumn(
                     title='User name',
                     field='user_name',
                     table='v_uids',
                     img='guy16',
                     display=True,
                    ),
        }
        self.colprops['user_id'].t = self
        self.extraline = True
        self.dbfilterable = True
        self.ajax_col_values = 'ajax_uids_col_values'
        self.additional_tools.append('free_uids')

    def extra_line_key(self, o):
        return "uid_"+str(o['user_id'])

    def free_uids(self):
        divid = 'free_uids'
        d = DIV(
              A(
                T("Free uids"),
               _class='guy16',
               _onclick="""click_toggle_vis(event, '%(div)s', 'block')"""%dict(div=divid),
              ),
              DIV(
                T("User id range start"),
                INPUT(
                  _id="uid_start",
                  _onkeypress="if (is_enter(event)) {sync_ajax('%(url)s', ['uid_start'], '%(div)s', function(){})};"""%dict(
                                url=URL(r=request,c='nodes',f='ajax_free_uids'),
                                div='r'+divid,
                              ),
                 ),
                 DIV(
                   _id='r'+divid,
                 ),
                 _style='display:none',
                 _class='white_float',
                 _id=divid,
                 _name=divid,
              ),
              _class='floatw',
            )
        return d

def free_ids(rows, start=500):
    if len(rows) == 0:
        l = range(start, 20)
    else:
        uids = map(lambda x: x[0], rows)
        l = []
        i = start
        while len(l) < 20:
            if i in uids:
                i += 1
                continue
            l.append(i)
            i += 1
    return DIV(
             "\n".join(map(lambda x: str(x), l)),
             _class="pre",
           )

class col_group_id(HtmlTableColumn):
    def html(self, o):
        id = self.t.extra_line_key(o)
        h = self.get(o)
        d = DIV(
              A(
                o['group_id'],
                _onclick="toggle_extra('%(url)s', '%(id)s', this, 0);"%dict(
                  url=URL(r=request, c='nodes',f='ajax_gid_dispatch',
                          vars={'group_id': o['group_id']}),
                  id=id,
                ),
              ),
              _class='nowrap',
            )
        return d

class table_gids(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['group_id',
                     'group_id_count',
                     'group_name']
        self.keys = ["group_id"]
        self.span = ["group_id"]
        self.colprops = {
            'group_id': col_group_id(
                     title='User id',
                     field='group_id',
                     table='v_gids',
                     img='guy16',
                     display=True,
                    ),
            'group_id_count': HtmlTableColumn(
                     title='Group count',
                     field='group_id_count',
                     table='v_gids',
                     img='guy16',
                     display=True,
                    ),
            'group_name': HtmlTableColumn(
                     title='User name',
                     field='group_name',
                     table='v_gids',
                     img='guy16',
                     display=True,
                    ),
        }
        self.colprops['group_id'].t = self
        self.extraline = True
        self.dbfilterable = True
        self.ajax_col_values = 'ajax_gids_col_values'
        self.additional_tools.append('free_gids')

    def extra_line_key(self, o):
        return "gid_"+str(o['group_id'])

    def free_gids(self):
        divid = 'free_gids'
        d = DIV(
              A(
                T("Free gids"),
               _class='guy16',
               _onclick="""click_toggle_vis(event, '%(div)s', 'block')"""%dict(div=divid),
              ),
              DIV(
                T("Group id range start"),
                INPUT(
                  _id="gid_start",
                  _onkeypress="if (is_enter(event)) {sync_ajax('%(url)s', ['gid_start'], '%(div)s', function(){})};"""%dict(
                                url=URL(r=request,c='nodes',f='ajax_free_gids'),
                                div='r'+divid,
                              ),
                 ),
                 DIV(
                   _id='r'+divid,
                 ),
                 _style='display:none',
                 _class='white_float',
                 _id=divid,
                 _name=divid,
              ),
              _class='floatw',
            )
        return d

class table_obs_agg(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['chart']
        self.colprops = {
            'chart': col_obs_chart(
                     title='Chart',
                     field='chart',
                     display=True,
                     img='spark16',
                    ),
        }
        self.dbfilterable = False
        self.filterable = False
        self.pageable = False
        self.bookmarkable = False
        self.commonalityable = False
        self.exportable = False
        self.refreshable = False
        self.columnable = False
        self.headers = False

@auth.requires_login()
def ajax_obs_agg():
    t = table_nodes('nodes', 'ajax_nodes')
    mt = table_obs_agg('obs_agg', 'ajax_obs_agg')

    def get_rows(field_date):
        q = db.v_nodes.id>0
        q = _where(q, 'v_nodes', domain_perms(), 'nodename')
        q = apply_filters(q, db.v_nodes.nodename, None)
        for f in t.cols:
            q = _where(q, 'v_nodes', t.filter_parse(f), f)
        return db(q).select(db.v_nodes.id.count(),
                            db.v_nodes[field_date],
                            groupby=db.v_nodes[field_date],
                            orderby=db.v_nodes[field_date])

    def get_data(field_date):
        data = []
        cumul = []
        prev = 0
        max = 0
        rows = get_rows(field_date)
        for row in rows:
            if row.v_nodes[field_date] is None:
                continue
            val = row(db.v_nodes.id.count())
            if prev+val > max: max = prev+val
            data.append([row.v_nodes[field_date].strftime('%Y-%m-%d %H:%M:%S'),
                         val])
            cumul.append([row.v_nodes[field_date].strftime('%Y-%m-%d %H:%M:%S'),
                          prev+val])
            prev = cumul[-1][1]
        nowserie = [[datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0],
                    [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), max]]
        return [data, cumul, nowserie]

    h = {}
    h['hw_warn_chart_data'] = get_data('hw_obs_warn_date')
    h['hw_alert_chart_data'] = get_data('hw_obs_alert_date')
    h['os_warn_chart_data'] = get_data('os_obs_warn_date')
    h['os_alert_chart_data'] = get_data('os_obs_alert_date')

    return DIV(
             #mt.html(),
             STYLE("""
.chartcontainer {
  float:left;
  width:45%;
  min-width:350px;
  padding:10px;
  padding-left:30px;
  padding-right:30px
}

             """),
             DIV(
               H3(T("Hardware obsolescence warnings roadmap")),
               DIV(
                 XML(json.dumps(h['hw_warn_chart_data'])),
                 _id='hw_warn_chart',
               ),
               _class="chartcontainer",
             ),
             DIV(
               H3(T("Hardware obsolescence alerts roadmap")),
               DIV(
                 XML(json.dumps(h['hw_alert_chart_data'])),
                 _id='hw_alert_chart',
               ),
               _class="chartcontainer",
             ),
             DIV(
               H3(T("Operating system obsolescence warnings roadmap")),
               DIV(
                 XML(json.dumps(h['os_warn_chart_data'])),
                 _id='os_warn_chart',
               ),
               _class="chartcontainer",
             ),
             DIV(
               H3(T("Operating system obsolescence alerts roadmap")),
               DIV(
                 XML(json.dumps(h['os_alert_chart_data'])),
                 _id='os_alert_chart',
               ),
               _class="chartcontainer",
             ),
             DIV(XML('&nbsp;'), _class='spacer'),


             SCRIPT("""
$("#hw_warn_chart").each(function(){
  obsplot($(this))
})
$("#hw_alert_chart").each(function(){
  obsplot($(this))
})
$("#os_warn_chart").each(function(){
  obsplot($(this))
})
$("#os_alert_chart").each(function(){
  obsplot($(this))
})
""",
               _name="obs_agg_to_eval",
             ),
           )

@auth.requires_login()
def ajax_uids_col_values():
    col = request.args[0]
    t = table_nodes('nodes', 'ajax_nodes')
    mt = table_uids('uids', 'ajax_uids')

    q = _where(None, 'v_nodes', domain_perms(), 'nodename')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.nodes.nodename)
    sql1 = db(q)._select(db.v_nodes.nodename).rstrip(';')

    q = db.v_uids.id > 0
    for f in mt.cols:
        q = _where(q, mt.colprops[f].table, mt.filter_parse(f), f)
    where = str(q).replace("v_uids.", "u.")

    o = 'u.'+col

    mt.setup_pager(-1)
    mt.dbfilterable = False
    mt.filterable = True
    mt.additional_inputs = t.ajax_inputs()

    sql2 = """select * from (
                select
                  node_users.id as id,
                  node_users.user_id as user_id,
                  count(distinct node_users.user_name) as user_id_count,
                  group_concat(distinct node_users.user_name order by node_users.user_name separator ',') as user_name
                from node_users
                where
                  node_users.nodename in (%(sql)s)
                group by node_users.user_id
              ) u
              where %(where)s
              order by %(o)s
           """%dict(
                sql=sql1,
                where=where,
                o=o,
           )
    mt.object_list = db.executesql(sql2, as_dict=True)
    return mt.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_uids():
    t = table_nodes('nodes', 'ajax_nodes')
    mt = table_uids('uids', 'ajax_uids')

    o = ~db.comp_status.run_nodename
    q = _where(None, 'v_nodes', domain_perms(), 'nodename')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.nodes.nodename)
    sql1 = db(q)._select(db.v_nodes.nodename).rstrip(';')

    q = db.v_uids.id > 0
    for f in mt.cols:
        q = _where(q, mt.colprops[f].table, mt.filter_parse(f), f)
    where = str(q).replace("v_uids.", "u.")

    mt.setup_pager(-1)
    mt.dbfilterable = False
    mt.filterable = True
    mt.additional_inputs = t.ajax_inputs()

    sql2 = """select * from (
                select
                  node_users.id as id,
                  node_users.user_id as user_id,
                  count(distinct node_users.user_name) as user_id_count,
                  group_concat(distinct node_users.user_name order by node_users.user_name separator ',') as user_name
                from node_users
                where
                  node_users.nodename in (%(sql)s)
                group by node_users.user_id
              ) u
              where %(where)s
              order by user_id
             """%dict(
                sql=sql1,
                where=where,
           )

    if len(request.args) != 1 or (request.args[0] not in ('csv', 'commonality')):
        sql2 += """
              limit %(limit)d
              offset %(offset)d"""%dict(
                limit=mt.perpage,
                offset=mt.pager_start,
           )
    mt.object_list = db.executesql(sql2, as_dict=True)

    if len(request.args) == 1 and request.args[0] == 'csv':
        return mt.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        return mt.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'line':
        return mt.table_lines_data(-1)


    return DIV(
             mt.html(),
           )

@auth.requires_login()
def ajax_gids_col_values():
    col = request.args[0]
    t = table_nodes('nodes', 'ajax_nodes')
    mt = table_gids('gids', 'ajax_gids')

    q = _where(None, 'v_nodes', domain_perms(), 'nodename')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.nodes.nodename)
    sql1 = db(q)._select(db.v_nodes.nodename).rstrip(';')

    q = db.v_gids.id > 0
    for f in mt.cols:
        q = _where(q, mt.colprops[f].table, mt.filter_parse(f), f)
    where = str(q).replace("v_gids.", "u.")

    o = 'u.'+col

    mt.setup_pager(-1)
    mt.dbfilterable = False
    mt.filterable = True
    mt.additional_inputs = t.ajax_inputs()

    sql2 = """select * from (
                select
                  node_groups.id as id,
                  node_groups.group_id as group_id,
                  count(distinct node_groups.group_name) as group_id_count,
                  group_concat(distinct node_groups.group_name order by node_groups.group_name separator ',') as group_name
                from node_groups
                where
                  node_groups.nodename in (%(sql)s)
                group by node_groups.group_id
              ) u
              where %(where)s
              order by %(o)s
           """%dict(
                sql=sql1,
                where=where,
                o=o,
           )
    mt.object_list = db.executesql(sql2, as_dict=True)
    return mt.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_gids():
    t = table_nodes('nodes', 'ajax_nodes')
    mt = table_gids('gids', 'ajax_gids')

    o = ~db.comp_status.run_nodename
    q = _where(None, 'v_nodes', domain_perms(), 'nodename')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.nodes.nodename)
    sql1 = db(q)._select(db.v_nodes.nodename).rstrip(';')

    q = db.v_gids.id > 0
    for f in mt.cols:
        q = _where(q, mt.colprops[f].table, mt.filter_parse(f), f)
    where = str(q).replace("v_gids.", "u.")

    mt.setup_pager(-1)
    mt.dbfilterable = False
    mt.filterable = True
    mt.additional_inputs = t.ajax_inputs()

    sql2 = """select * from (
                select
                  node_groups.id as id,
                  node_groups.group_id as group_id,
                  count(distinct node_groups.group_name) as group_id_count,
                  group_concat(distinct node_groups.group_name order by node_groups.group_name separator ',') as group_name
                from node_groups
                where
                  node_groups.nodename in (%(sql)s)
                group by node_groups.group_id
              ) u
              where %(where)s
              order by group_id
              """%dict(
                sql=sql1,
                where=where,
           )

    if len(request.args) != 1 or (request.args[0] not in ('csv', 'commonality')):
        sql2 += """
              limit %(limit)d
              offset %(offset)d"""%dict(
                limit=mt.perpage,
                offset=mt.pager_start,
           )

    mt.object_list = db.executesql(sql2, as_dict=True)

    if len(request.args) == 1 and request.args[0] == 'csv':
        return mt.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        return mt.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'line':
        return mt.table_lines_data(-1)

    return DIV(
             mt.html(),
           )



#
# Dashboard updates
#
def delete_dash_node(nodename):
    sql = """delete from dashboard
               where
                 dash_nodename="%(nodename)s"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)
    db.commit()

def delete_dash_node_without_asset(nodename):
    sql = """delete from dashboard
               where
                 dash_nodename="%(nodename)s" and
                 dash_type = "node without asset information"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)
    db.commit()

def update_dash_node_beyond_maintenance_end(nodename):
    sql = """delete from dashboard
               where
                 dash_nodename in (
                   select nodename
                   from nodes
                   where
                     nodename="%(nodename)s" and
                     maintenance_end is not NULL and
                     maintenance_end != "0000-00-00 00:00:00" and
                     maintenance_end > now()
                 ) and
                 dash_type = "node maintenance expired"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)
    db.commit()

def update_dash_node_near_maintenance_end(nodename):
    sql = """delete from dashboard
               where
                 dash_nodename in (
                   select nodename
                   from nodes
                   where
                     nodename="%(nodename)s" and
                     maintenance_end is not NULL and
                     maintenance_end != "0000-00-00 00:00:00" and
                     maintenance_end < now() and
                     maintenance_end > date_sub(now(), interval 30 day)
                 ) and
                 dash_type = "node maintenance expired"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)
    db.commit()

def update_dash_node_without_maintenance_end(nodename):
    sql = """delete from dashboard
               where
                 dash_nodename in (
                   select nodename
                   from nodes
                   where
                     nodename="%(nodename)s" and 
                     maintenance_end != "0000-00-00 00:00:00" and
                     maintenance_end is not NULL
                 ) and
                 dash_type = "node without maintenance end date"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)
    db.commit()

def delete_dash_node_not_updated(nodename):
    sql = """delete from dashboard
               where
                 dash_nodename = "%(nodename)s" and
                 dash_type = "node information not updated"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)
    db.commit()

@auth.requires_login()
def ajax_uid_dispatch():
    uid = request.vars.user_id
    sql = """select
               user_name,
               count(id) as n,
               group_concat(nodename order by nodename separator ", ") as nodes
             from node_users
             where
               user_id = %(uid)s
             group by user_name"""%dict(
            uid=uid,
          )
    rows = db.executesql(sql, as_dict=True)
    header = TR(
               TH(T('User name')),
               TH(T('Number of nodes')),
               TH(T('Nodes')),
             )
    l = [header]
    for row in rows:
        line = TR(
                 TD(row['user_name']),
                 TD(row['n']),
                 TD(row['nodes']),
               )
        l.append(line)
    return TABLE(SPAN(l))

@auth.requires_login()
def ajax_gid_dispatch():
    gid = request.vars.group_id
    sql = """select
               group_name,
               count(id) as n,
               group_concat(nodename order by nodename separator ", ") as nodes
             from node_groups
             where
               group_id = %(gid)s
             group by group_name"""%dict(
            gid=gid,
          )
    rows = db.executesql(sql, as_dict=True)
    header = TR(
               TH(T('Group name')),
               TH(T('Number of nodes')),
               TH(T('Nodes')),
             )
    l = [header]
    for row in rows:
        line = TR(
                 TD(row['group_name']),
                 TD(row['n']),
                 TD(row['nodes']),
               )
        l.append(line)
    return TABLE(SPAN(l))


@auth.requires_login()
def ajax_free_uids():
    start = request.vars.uid_start
    if start is None:
        start = 500
    else:
        start = int(start)
    sql = "select distinct user_id from node_users order by user_id"
    rows = db.executesql(sql)
    return free_ids(rows, start)

@auth.requires_login()
def ajax_free_gids():
    start = request.vars.gid_start
    if start is None:
        start = 500
    else:
        start = int(start)
    sql = "select distinct group_id from node_groups order by group_id"
    rows = db.executesql(sql)
    return free_ids(rows, start)


