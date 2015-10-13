@auth.requires_membership('CheckManager')
def checks_defaults_insert():
    record = None
    if request.vars.chk_id is not None:
        q = db.checks_defaults.id==request.vars.chk_id
        rows = db(q).select()
        if len(rows) == 1:
            record = rows[0]

    db.checks_defaults.chk_type.default = request.vars.chk_type
    db.checks_defaults.chk_prio.default = 0

    form = SQLFORM(db.checks_defaults,
                 record=record,
                 deletable=True,
                 fields=['chk_type',
                         'chk_inst',
                         'chk_low',
                         'chk_high',
                         'chk_prio'],
                 labels={'chk_type': T('Check type'),
                         'chk_inst': T('Instance'),
                         'chk_low': T('Low threshold'),
                         'chk_high': T('High threshold'),
                         'chk_prio': T('Evaluation priority')},
                )

    if request.vars.chk_prio is None and request.vars.chk_inst is not None:
        request.vars.chk_prio = len(request.vars.chk_inst)

    if form.accepts(request.vars):
        response.flash = T("edition recorded")
        table_modified("checks_defaults")
        enqueue_update_thresholds_batch(request.vars.chk_type)
        redirect(URL(r=request, c='checks', f='checks'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)

def enqueue_update_thresholds_batch(chk_type=None):
    if chk_type is None:
        q_fn = 'update_thresholds_batch'
        q_args = []
        task = scheduler.task_status(
          (db.scheduler_task.function_name == q_fn) & \
          (db.scheduler_task.status == "QUEUED")
        )
    else:
        q_fn = 'update_thresholds_batch_type'
        q_args = [chk_type]
        task = scheduler.task_status(
          (db.scheduler_task.function_name == q_fn) & \
          (db.scheduler_task.args.like('%'+chk_type+'%')) & \
          (db.scheduler_task.status == "QUEUED")
        )

    if task is not None:
        return
    scheduler.queue_task(q_fn, q_args, group_name="slow")
    db.commit()

@auth.requires_membership('CheckManager')
def del_fset_threshold(id):
    q = db.gen_filterset_check_threshold.id == id
    db(q).delete()
    table_modified("gen_filterset_check_threshold")

def get_defaults(row):
    if row['chk_instance'] is not None:
        q = db.checks_defaults.chk_type == row['chk_type']
        q &= db.checks_defaults.chk_inst != None
        o = ~db.checks_defaults.chk_prio
        rows = db(q).select(orderby=o)
        for r in rows:
            pattern = str(r.chk_inst)
            if not pattern.endswith('$'):
                pattern += '$'
            if re.match(pattern, row['chk_instance']) is not None:
                return (r.chk_low, r.chk_high, 'defaults')

    q = db.checks_defaults.chk_type == row.chk_type
    q &= (db.checks_defaults.chk_inst == None) | (db.checks_defaults.chk_inst == "")
    rows = db(q).select()
    if len(rows) == 0:
        return
    return (rows[0].chk_low, rows[0].chk_high, 'defaults')

@auth.requires_membership('CheckExec')
def set_low_threshold(ids):
    if len(ids) == 0:
        raise ToolError("No check selected")
    val = request.vars.set_low_threshold
    if val is None or len(val) == 0:
        raise ToolError("New threshold value invalid")
    val = int(val)
    ugroups = user_groups()
    for i in ids:
        q = db.checks_live.id==i
        if 'Manager' not in ugroups:
            q &= db.nodes.nodename == db.checks_live.chk_nodename
            q &= (db.nodes.team_responsible.belongs(ugroups)) | (db.nodes.team_integ.belongs(ugroups))
        rows = db(q).select(db.checks_live.ALL)
        if len(rows) != 1:
            continue
        chk = rows[0]
        q = db.checks_settings.chk_nodename==chk.chk_nodename
        q &= db.checks_settings.chk_type==chk.chk_type
        q &= db.checks_settings.chk_instance==chk.chk_instance
        settings = db(q).select()
        if len(settings) == 0:
            # insert
            chk_default = get_defaults(chk)
            db.checks_settings.insert(chk_nodename=chk.chk_nodename,
                                      chk_type=chk.chk_type,
                                      chk_instance=chk.chk_instance,
                                      chk_low=val,
                                      chk_high=chk_default[1],
                                      chk_changed_by=user_name(),
                                      chk_changed=now)
        elif len(settings) == 1:
            # update
            if settings[0].chk_high < val:
                high = val
            else:
                high = settings[0].chk_high
            db(q).update(chk_low=val,
                         chk_high=high,
                         chk_changed_by=user_name(),
                         chk_changed=now)
        where = ""
        if len(chk.chk_svcname) > 0: where = chk.chk_svcname + "@"
        where += chk.chk_nodename
        _log('checks.thresholds.set',
             'set high threshold to %(val)d for check %(inst)s on %(where)s',
             dict(val=val, where=where, inst='.'.join((chk.chk_type, chk.chk_instance))))
    table_modified("checks_settings")
    q = db.checks_live.id.belongs(ids)
    rows = db(q).select()
    update_thresholds_batch(rows)
    update_dash_checks_nodes(map(lambda x: x.chk_nodename, rows))

@auth.requires_membership('CheckExec')
def set_high_threshold(ids):
    if len(ids) == 0:
        raise ToolError("No check selected")
    val = request.vars.set_high_threshold
    if val is None or len(val) == 0:
        raise ToolError("New threshold value invalid")
    val = int(val)
    ugroups = user_groups()
    for i in ids:
        q = db.checks_live.id==i
        if 'Manager' not in ugroups:
            q &= db.nodes.nodename == db.checks_live.chk_nodename
            q &= (db.nodes.team_responsible.belongs(ugroups)) | (db.nodes.team_integ.belongs(ugroups))
        rows = db(q).select(db.checks_live.ALL)
        if len(rows) != 1:
            continue
        chk = rows[0]
        q = db.checks_settings.chk_nodename==chk.chk_nodename
        q &= db.checks_settings.chk_type==chk.chk_type
        q &= db.checks_settings.chk_instance==chk.chk_instance
        settings = db(q).select()
        if len(settings) == 0:
            # insert
            chk_default = get_defaults(chk)
            db.checks_settings.insert(chk_nodename=chk.chk_nodename,
                                      chk_type=chk.chk_type,
                                      chk_instance=chk.chk_instance,
                                      chk_high=val,
                                      chk_low=chk_default[0],
                                      chk_changed_by=user_name(),
                                      chk_changed=now)
        elif len(settings) == 1:
            # update
            if settings[0].chk_low > val:
                low = val
            else:
                low = settings[0].chk_low
            db(q).update(chk_high=val,
                         chk_low=low,
                         chk_changed_by=user_name(),
                         chk_changed=now)
        where = ""
        if len(chk.chk_svcname) > 0: where = chk.chk_svcname + "@"
        where += chk.chk_nodename
        _log('checks.thresholds.set',
             'set high threshold to %(val)d for check %(inst)s on %(where)s',
             dict(val=val, where=where, inst='.'.join((chk.chk_type, chk.chk_instance))))
    table_modified("checks_settings")
    q = db.checks_live.id.belongs(ids)
    rows = db(q).select()
    update_thresholds_batch(rows)
    update_dash_checks_nodes(map(lambda x: x.chk_nodename, rows))

@auth.requires_membership('CheckExec')
def reset_thresholds(ids):
    if len(ids) == 0:
        raise ToolError("No check selected")
    ugroups = user_groups()
    for i in ids:
        q = db.checks_live.id==i
        if 'Manager' not in ugroups:
            q &= db.nodes.nodename == db.checks_live.chk_nodename
            q &= (db.nodes.team_responsible.belongs(ugroups)) | (db.nodes.team_integ.belongs(ugroups))
        rows = db(q).select(db.checks_live.ALL)
        if len(rows) != 1:
            continue
        chk = rows[0]
        q = db.checks_settings.chk_nodename==chk.chk_nodename
        q &= db.checks_settings.chk_type==chk.chk_type
        q &= db.checks_settings.chk_instance==chk.chk_instance
        settings = db(q).delete()
        where = ""
        if len(chk.chk_svcname) > 0: where = chk.chk_svcname + "@"
        where += chk.chk_nodename
        _log('checks.thresholds.reset',
             'reset thresholds for check %(inst)s on %(where)s',
             dict(where=where, inst='.'.join((chk.chk_type, chk.chk_instance))))
    q = db.checks_live.id.belongs(ids)
    rows = db(q).select()
    table_modified("checks_settings")
    update_thresholds_batch(rows)

@auth.requires_login()
def ajax_chk_type_defaults():
    chk_type = request.args[0]
    q = db.checks_defaults.chk_type == chk_type
    o = ~db.checks_defaults.chk_prio
    rows = db(q).select(orderby=o)

    l = []
    l.append(DIV(
                 DIV(
                   T("Edit"),
                   _style="font-weight:bold"
                 ),
                 DIV(
                   T("Type"),
                   _style="font-weight:bold"
                 ),
                 DIV(
                   T("Prio"),
                   _style="font-weight:bold"
                 ),
                 DIV(
                   T("Instance"),
                   _style="font-weight:bold"
                 ),
                 DIV(
                   T("Low threshold"),
                   _style="font-weight:bold"
                 ),
                 DIV(
                   T("High threshold"),
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
                   "-",
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

    for row in rows:
        l.append(DIV(
                 DIV(
                   A(
                     IMG(_src=URL(r=request, c='static', f='images/edit.png')),
                     _href=URL(r=request, f='checks_defaults_insert', vars={'chk_type': row.chk_type, 'chk_id': row.id}),
                   ),
                 ),
                 DIV(
                   row.chk_type,
                 ),
                 DIV(
                   row.chk_prio,
                 ),
                 DIV(
                   row.chk_inst if row.chk_inst is not None else "",
                 ),
                 DIV(
                   row.chk_low,
                 ),
                 DIV(
                   row.chk_high,
                 ),
               ))

    l.append(DIV(
             DIV(
               A(
                 IMG(_src=URL(r=request, c='static', f='images/add16.png')),
                 _href=URL(r=request, f='checks_defaults_insert', vars={'chk_type': chk_type}),
               ),
             ),
             DIV(
               T("Add threshold defaults"),
             ),
           ))


    return TABLE(
             DIV(
               H3(T("Threshold defaults")),
             ),
             DIV(
               DIV(l, _class="table0"),
             ),
           )

class table_checks(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['chk_nodename',
                     'chk_svcname',
                     'chk_type',
                     'chk_instance',
                     'chk_value',
                     'chk_low',
                     'chk_high',
                     'chk_err',
                     'chk_threshold_provider',
                     'chk_created',
                     'chk_updated']
        self.force_cols = ['os_name',
                     'chk_type',
                     'chk_instance',
                     'chk_value',
                     'chk_high',
                     'chk_low']
        self.keys = ['chk_nodename',
                     'chk_svcname',
                     'chk_type',
                     'chk_instance']
        self.colprops = {
            'chk_nodename': HtmlTableColumn(
                title = 'Nodename',
                field = 'chk_nodename',
                display = True,
                table = 'checks_live',
                img = 'node16',
                _class = 'nodename',
            ),
            'chk_svcname': HtmlTableColumn(
                title = 'Service',
                field = 'chk_svcname',
                display = True,
                table = 'checks_live',
                img = 'check16',
                _class = 'svcname',
            ),
            'chk_type': HtmlTableColumn(
                title = 'Type',
                field = 'chk_type',
                display = True,
                table = 'checks_live',
                img = 'check16',
                _class = "chk_type",
            ),
            'chk_instance': HtmlTableColumn(
                title = 'Instance',
                field = 'chk_instance',
                display = True,
                table = 'checks_live',
                img = 'check16',
                _class = "chk_instance",
            ),
            'chk_err': HtmlTableColumn(
                title = 'Error',
                field = 'chk_err',
                display = True,
                table = 'checks_live',
                img = 'check16'
            ),
            'chk_value': HtmlTableColumn(
                title = 'Value',
                field = 'chk_value',
                display = True,
                table = 'checks_live',
                img = 'check16',
                _class = 'chk_value',
            ),
            'chk_low': HtmlTableColumn(
                title = 'Low threshold',
                field = 'chk_low',
                display = True,
                table = 'checks_live',
                img = 'check16',
                _class = 'chk_low',
            ),
            'chk_high': HtmlTableColumn(
                title = 'High threshold',
                field = 'chk_high',
                display = True,
                table = 'checks_live',
                img = 'check16',
                _class = 'chk_high',
            ),
            'chk_created': HtmlTableColumn(
                title = 'Created',
                field = 'chk_created',
                display = False,
                table = 'checks_live',
                img = 'check16'
            ),
            'chk_updated': HtmlTableColumn(
                title = 'Last check update',
                field = 'chk_updated',
                display = True,
                table = 'checks_live',
                img = 'check16',
                _class = 'datetime_daily',
            ),
            'chk_threshold_provider': HtmlTableColumn(
                title = 'Threshold provider',
                field = 'chk_threshold_provider',
                display = True,
                table = 'checks_live',
                img = 'check16'
            ),
        }
        self.colprops.update(v_nodes_colprops)
        self.cols += v_nodes_cols

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

        for c in self.cols:
            self.colprops[c].t = self
        self.ajax_col_values = 'ajax_checks_col_values'
        self.wsable = True
        self.dataable = True
        self.dbfilterable = True
        self.checkbox_id_table = 'checks_live'
        self.checkboxes = True
        self.extraline = True
        self.span = ['chk_nodename']

        ug = user_groups()
        if 'CheckManager' in ug:
            self.form_add_fset_threshold = self.add_fset_threshold_sqlform()
            self.form_del_fset_threshold = self.del_fset_threshold()
            self += HtmlTableMenu('Contuextual threshold', 'filter16', ['add_fset_threshold', 'del_fset_threshold'])
        if 'CheckManager' in ug or 'CheckExec' in ug:
            self.additional_tools.append('set_high_threshold')
            self.additional_tools.append('set_low_threshold')
            self.additional_tools.append('reset_thresholds')
            self.additional_tools.append('delete_checks')
        if 'NodeManager' in ug or 'NodeExec' in ug or 'CheckRefresh' in ug:
            self.additional_tools.append('refresh_checks')

    def set_low_threshold(self):
        return self.set_threshold('low')

    def set_high_threshold(self):
        return self.set_threshold('high')

    def add_fset_threshold(self):
        d = DIV(
              A(
                T("Add"),
                _class='add16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='add_fset_threshold_d'),
              ),
              DIV(
                self.form_add_fset_threshold,
                _style='display:none',
                _class='white_float',
                _name='add_fset_threshold_d',
                _id='add_fset_threshold_d',
              ),
            )
        return d

    def refresh_checks(self):
        d = DIV(
              A(
                T("Refresh check values"),
                _class='refresh16',
                _onclick=self.ajax_submit(args=['check_refresh']),
              ),
              _class='floatw',
            )
        return d

    def delete_checks(self):
        d = DIV(
              A(
                T("Delete"),
                _class='del16',
                _onclick=self.ajax_submit(args=['check_del']),
              ),
              _class='floatw',
            )
        return d

    @auth.requires_membership('CheckManager')
    def add_fset_threshold_sqlform(self):
        db.gen_filterset_check_threshold.fset_id.requires = IS_IN_DB(db, db.gen_filtersets.id, "%(fset_name)s", zero=T('choose one'))
        allowed = db(db.checks_live.id>0).select(db.checks_live.chk_type, groupby=db.checks_live.chk_type, orderby=db.checks_live.chk_type)
        allowed = map(lambda x: x.chk_type, allowed)
        db.gen_filterset_check_threshold.chk_type.requires = IS_IN_SET(allowed, zero=T('choose one'))
        f = SQLFORM(
                 db.gen_filterset_check_threshold,
                 labels={'fset_id': T('Filterset'),
                         'chk_type': T('Type'),
                         'chk_low': T('Low threshold'),
                         'chk_high': T('High threshold'),
                         'chk_instance': T('Instance')},
                 _name='form_add_fset_threshold',
            )
        return f

    @auth.requires_membership('CheckManager')
    def del_fset_threshold(self):
        q = db.gen_filterset_check_threshold.id > 0
        q &= db.gen_filterset_check_threshold.fset_id == db.gen_filtersets.id
        rows = db(q).select()

        if len(rows) == 0:
            d = DIV("No contuextual thresholds")

        options = map(lambda x: OPTION("%d: %s - %s:%s %d<>%d "%(
                    x.gen_filterset_check_threshold.id,
                    x.gen_filtersets.fset_name,
                    x.gen_filterset_check_threshold.chk_type,
                    x.gen_filterset_check_threshold.chk_instance,
                    x.gen_filterset_check_threshold.chk_low,
                    x.gen_filterset_check_threshold.chk_high),
                    _value=x.gen_filterset_check_threshold.id), rows)

        label = 'Delete'
        action = 'del_fset_threshold'
        divid = 'del_fset_threshold'
        sid = 'del_fset_threshold_s'
        d = DIV(
              A(
                T(label),
                _class='del16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div=divid),
              ),
              DIV(
                TABLE(
                  TR(
                    TH(T('Thresholds')),
                    TD(
                      SELECT(
                        *options,
                        **dict(_id=sid)
                      ),
                    ),
                  ),
                  TR(
                    TH(),
                    TD(
                      INPUT(
                        _type='submit',
                        _onclick=self.ajax_submit(additional_inputs=[sid],
                                                  args=action),
                      ),
                    ),
                  ),
                ),
                _style='display:none',
                _class='white_float',
                _name=divid,
              ),
            )
        return d

    def set_threshold(self, t):
        d = DIV(
              A(
                T("Set %s threshold"%t),
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='set_%s_threshold_d'%t),
              ),
              DIV(
                TABLE(
                  TR(
                    TD(
                      T('New threshold value'),
                    ),
                    TD(
                      INPUT(
                       _id='set_%s_threshold'%t,
                       _onkeypress="if (is_enter(event)) {%s};"%\
                          self.ajax_submit(additional_inputs=['set_%s_threshold'%t],
                                           args="set_%s_threshold"%t),

                      ),
                    ),
                  ),
                ),
                _style='display:none',
                _class='white_float',
                _name='set_%s_threshold_d'%t,
                _id='set_%s_threshold_d'%t,
              ),
              _class='floatw',
            )
        return d

    def reset_thresholds(self):
        d = DIV(
              A(
                T("Reset thresholds"),
                _onclick="""if (confirm("%(text)s")){%(s)s};
                         """%dict(s=self.ajax_submit(args=['reset_thresholds']),
                                  text=T("Resetting thresholds will definitively lose the custom thresholds of the selected checks. Please confirm reset"),
                                 ),
              ),
              _class='floatw',
            )
        return d


def queue_check_refresh(rows):
    vals = []
    vars = ['nodename', 'action_type', 'command', 'user_id']
    action = "checks"

    def fmt_action(node, action):
        cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                      '-o', 'ForwardX11=no',
                      '-o', 'PasswordAuthentication=no',
                      '-o', 'ConnectTimeout=5',
                      '-tt',
               'opensvc@'+node,
               '--',
               'sudo', '/opt/opensvc/bin/nodemgr', action,
               '--force']
        return ' '.join(cmd)

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
            command = fmt_action(node, action)

        vals.append([row.nodename, action_type, command, str(auth.user_id)])

    generic_insert('action_queue', vars, vals)

    from subprocess import Popen
    import sys
    actiond = 'applications'+str(URL(r=request,c='actiond',f='actiond.py'))
    process = Popen([sys.executable, actiond])
    process.communicate()

    _log('node.action', 'run %(a)s on nodes %(s)s', dict(
          a=action,
          s=','.join(map(lambda x: x.nodename, rows)),
          ))
    if len(vals) > 0:
        l = {
          'event': 'action_q_change',
          'data': action_queue_ws_data(),
        }
        _websocket_send(event_msg(l))


@auth.requires(auth.has_membership('Manager') or auth.has_membership('CheckRefresh') or auth.has_membership('NodeManager') or auth.has_membership('NodeExec'))
def check_refresh():
    q = db.checks_live.chk_nodename == db.v_nodes.nodename
    groups = user_groups()
    if 'Manager' not in groups:
        q &= (db.v_nodes.team_responsible.belongs(groups)) | \
             (db.v_nodes.team_integ.belongs(groups)) | \
             (db.v_nodes.team_support.belongs(groups))
    q = _where(q, 'checks_live', domain_perms(), 'chk_nodename')
    q = apply_filters(q, db.checks_live.chk_nodename, None)
    t = table_checks('checks', 'ajax_checks')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    rows = db(q).select(db.v_nodes.nodename,
                        db.v_nodes.fqdn,
                        db.v_nodes.os_name,
                        groupby=db.v_nodes.nodename)
    if len(rows) == 0:
        raise ToolError("No node to refresh checks on")

    u = ', '.join([r.nodename for r in rows])

    purge_action_queue()
    queue_check_refresh(rows)

    _log('checks.refresh',
         'refresh checks sent to nodes %(u)s',
         dict(u=u))

    return T("checks refresh queued on %(n)d nodes", dict(n=len(rows)))

@auth.requires_membership('CheckExec')
def check_del(ids):
    if len(ids) == 0:
        raise ToolError("No check selected")

    q = db.checks_live.id.belongs(ids)
    q &= db.checks_live.chk_nodename == db.nodes.nodename
    groups = user_groups()
    if 'Manager' not in groups:
        q &= (db.nodes.team_responsible.belongs(groups)) | \
             (db.nodes.team_integ.belongs(groups))
    rows = db(q).select(db.checks_live.ALL)
    if len(rows) == 0:
        return
    u = ', '.join([":".join((r.chk_nodename,
                             r.chk_type,
                             r.chk_instance)) for r in rows])

    ids = [r.id for r in rows]
    q = db.checks_live.id.belongs(ids)
    db(q).delete()
    table_modified("checks_live")

    for nodename in set([r.chk_nodename for r in rows]):
        update_dash_checks(nodename)

    _log('checks.delete',
         'deleted checks %(u)s',
         dict(u=u))

@auth.requires_login()
def ajax_checks_col_values():
    t = table_checks('checks', 'ajax_checks')
    col = request.args[0]
    q = db.checks_live.id>0
    q = _where(q, 'checks_live', domain_perms(), 'chk_nodename')
    q = apply_filters(q, db.checks_live.chk_nodename, None)
    q &= db.checks_live.chk_nodename==db.v_nodes.nodename
    j = db.apps.app == db.v_nodes.project
    l = db.apps.on(j)

    o = db[t.colprops[col].table][col]
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, left=l)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_checks():
    t = table_checks('checks', 'ajax_checks')

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'check_del':
                check_del(t.get_checked())
            elif action == 'check_refresh':
                t.flash = check_refresh()
            elif action == 'set_low_threshold':
                set_low_threshold(t.get_checked())
            elif action == 'set_high_threshold':
                set_high_threshold(t.get_checked())
            elif action == 'reset_thresholds':
                reset_thresholds(t.get_checked())
            elif action == 'del_fset_threshold':
                del_fset_threshold(request.vars.del_fset_threshold_s)
                enqueue_update_thresholds_batch()
        except ToolError, e:
            t.flash = str(e)

    try:
        r = False
        try:
            r = t.form_add_fset_threshold.accepts(request.vars)
        except:
            if request.vars.fset_id is not None and \
               request.vars.chk_type is not None and \
               request.vars.chk_instance is not None and \
               request.vars.chk_low is not None and \
               request.vars.chk_high is not None:
                sql = """insert into gen_filterset_check_threshold
                         set
                           fset_id=%(fset_id)s,
                           chk_type="%(chk_type)s",
                           chk_instance="%(chk_instance)s",
                           chk_low=%(chk_low)s,
                           chk_high=%(chk_high)s
                         on duplicate key update
                           chk_low=%(chk_low)s,
                           chk_high=%(chk_high)s
                """%dict(fset_id=request.vars.fset_id,
                         chk_type=request.vars.chk_type,
                         chk_instance=request.vars.chk_instance,
                         chk_low=request.vars.chk_low,
                         chk_high=request.vars.chk_high)
                db.executesql(sql)
                table_modified("gen_filterset_check_threshold")
                db.commit()
                r = True
        if r:
            enqueue_update_thresholds_batch()
            _log('checks.threshold.add',
                 'added threshold %(low)s,%(high)s to check %(chk_type)s.%(chk_instance)s matching fset %(fset_id)s',
                 dict(low=request.vars.chk_low,
                      high=request.vars.chk_high,
                      chk_type=request.vars.chk_type,
                      chk_instance=request.vars.chk_instance or '*',
                      fset_id=request.vars.fset_id))
        elif t.form_add_fset_threshold.errors:
            response.flash = T("errors in form")
    except AttributeError:
        pass
    except ToolError, e:
        t.flash = str(e)

    o = db.checks_live.chk_nodename
    o |= db.checks_live.chk_type
    o |= db.checks_live.chk_instance
    q = db.checks_live.id>0
    q = _where(q, 'checks_live', domain_perms(), 'chk_nodename')
    q = apply_filters(q, db.checks_live.chk_nodename, None)
    q &= db.checks_live.chk_nodename==db.v_nodes.nodename
    j = db.apps.app == db.v_nodes.project
    l = db.apps.on(j)

    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        t.csv_limit = 15000
        t.csv_left = l
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        t.csv_left = l
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.checks_live.id.count(), left=l).first()(db.checks_live.id.count())
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, limitby=limitby, orderby=o, cacheable=False, left=l)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def checks():
    t = table_checks('checks', 'ajax_checks')
    t = DIV(
          DIV(
            t.html(),
            _id='checks',
          ),
          SCRIPT("""
function ws_action_switch_%(id)s(data) {
        if (data["event"] == "checks_change") {
          osvc.tables["%(id)s"].refresh();
        }
}
wsh["%(id)s"] = ws_action_switch_%(id)s
              """ % dict(
                     id=t.innerhtml,
                    )
          ),
        )
    return dict(table=t)

def update_dash_checks_nodes(nodenames):
    for nodename in nodenames:
        update_dash_checks(nodename)

def update_dash_checks(nodename):
    nodename = nodename.strip("'")
    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)
    sql = """select host_mode from nodes
             where
               nodename="%(nodename)s"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)

    env = rows[0][0]
    if len(rows) == 1 and env == 'PRD':
        sev = 3
    else:
        sev = 2

    sql = """insert into dashboard
               select
                 NULL,
                 "check out of bounds",
                 t.svcname,
                 t.nodename,
                 %(sev)d,
                 "%%(ctype)s:%%(inst)s check value %%(val)d. %%(ttype)s thresholds: %%(min)d - %%(max)d",
                 concat('{"ctype": "', t.ctype,
                        '", "inst": "', t.inst,
                        '", "ttype": "', t.ttype,
                        '", "val": ', t.val,
                        ', "min": ', t.min,
                        ', "max": ', t.max,
                        '}'),
                 "%(now)s",
                 md5(concat('{"ctype": "', t.ctype,
                        '", "inst": "', t.inst,
                        '", "ttype": "', t.ttype,
                        '", "val": ', t.val,
                        ', "min": ', t.min,
                        ', "max": ', t.max,
                        '}')),
                 "%(env)s",
                 "",
                 "%(now)s"
               from (
                 select
                   chk_svcname as svcname,
                   chk_nodename as nodename,
                   chk_type as ctype,
                   chk_instance as inst,
                   chk_threshold_provider as ttype,
                   chk_value as val,
                   chk_low as min,
                   chk_high as max
                 from checks_live
                 where
                   chk_nodename = "%(nodename)s" and
                   chk_updated >= date_sub(now(), interval 1 day) and
                   (
                     chk_value < chk_low or
                     chk_value > chk_high
                   )
               ) t
               on duplicate key update
                 dash_updated="%(now)s"
          """%dict(nodename=nodename,
                   sev=sev,
                   env=env,
                   now=str(now),
                  )
    db.executesql(sql)
    db.commit()

    sql = """delete from dashboard
               where
                 dash_nodename = "%(nodename)s" and
                 dash_type = "check out of bounds" and
                 dash_updated < "%(now)s"
          """%dict(nodename=nodename, now=str(now))
    n = db.executesql(sql)
    if n > 0:
        table_modified("dashboard")
    db.commit()


class table_checks_node(table_checks):
    def __init__(self, id=None, func=None, innerhtml=None):
        table_checks.__init__(self, id, func, innerhtml)
        self.hide_tools = True
        self.pageable = False
        self.bookmarkable = False
        self.commonalityable = False
        self.linkable = False
        self.checkboxes = False
        self.filterable = False
        self.exportable = False
        self.dbfilterable = False
        self.columnable = False
        self.refreshable = False
        self.wsable = False
        self.dataable = True
        self.child_tables = []
        #self.cols.remove("chk_nodename")

def ajax_checks_node():
    tid = request.vars.table_id
    t = table_checks_node(tid, 'ajax_checks_node')
    q = _where(None, 'checks_live', domain_perms(), 'chk_nodename')
    for f in ['chk_nodename']:
        q = _where(q, 'checks_live', t.filter_parse(f), f)
    if request.args[0] == "data":
        t.object_list = db(q).select(cacheable=True)
        return t.table_lines_data(-1, html=False)

@auth.requires_login()
def checks_node():
    node = request.args[0]
    tid = 'checks_'+node.replace('-', '_').replace('.', '_')
    t = table_checks_node(tid, 'ajax_checks_node')
    t.colprops['chk_nodename'].force_filter = node

    return DIV(
             t.html(),
             _id=tid,
           )

def batch_update_thresholds():
    update_thresholds_batch()

