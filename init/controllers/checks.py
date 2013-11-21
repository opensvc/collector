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
        redirect(URL(r=request, c='checks', f='checks'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)

@auth.requires_membership('CheckManager')
def checks_settings_insert():
    q = (db.checks_settings.chk_nodename==request.vars.chk_nodename)
    q &= (db.checks_settings.chk_svcname==request.vars.chk_svcname)
    q &= (db.checks_settings.chk_type==request.vars.chk_type)
    q &= (db.checks_settings.chk_instance==request.vars.chk_instance)
    rows = db(q).select()
    if len(rows) == 0:
        chk = {
         'chk_type': request.vars.chk_type,
         'chk_instance': request.vars.chk_instance,
        }
        defaults = get_defaults(chk)
        db.checks_settings.insert(chk_nodename=request.vars.chk_nodename,
                                  chk_svcname=request.vars.chk_svcname,
                                  chk_type=request.vars.chk_type,
                                  chk_instance=request.vars.chk_instance,
                                  chk_low=defaults[0],
                                  chk_high=defaults[1],
                                 )
        rows = db(q).select()
    record = rows[0]

    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)
    form = SQLFORM(db.checks_settings,
                 record=record,
                 deletable=True,
                 hidden_fields=['chk_changed',
                                'chk_changed_by'],
                 fields=['chk_nodename',
                         'chk_svcname',
                         'chk_type',
                         'chk_instance',
                         'chk_changed',
                         'chk_changed_by',
                         'chk_low',
                         'chk_high'],
                 labels={'chk_nodename': T('Node'),
                         'chk_svcname': T('Service'),
                         'chk_type': T('Check type'),
                         'chk_instance': T('Check instance'),
                         'chk_changed': T('Change date'),
                         'chk_changed_by': T('Change author'),
                         'chk_low': T('Low threshold'),
                         'chk_high': T('High threshold')},
                )
    request.vars['chk_changed_by'] = user_name()
    request.vars['chk_changed'] = str(now)
    if form.accepts(request.vars):
        response.flash = T("edition recorded")
        update_thresholds_batch()
        db(q).update(chk_changed=now,
                     chk_changed_by=user_name())
        redirect(URL(r=request, c='checks', f='checks'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form, record=record)

def update_thresholds_batch2():
    # maintenance batch
    q = db.checks_live.chk_threshold_provider.like("fset%")
    q |= db.checks_live.chk_threshold_provider == "defaults"
    if len(request.args) == 1:
        node = request.args[0]
        q &= db.checks_live.chk_nodename == node
    rows = db(q).select()
    for row in rows:
        update_thresholds(row)

def update_thresholds_batch(rows=None):
    # maintenance batch
    if rows is None:
        q = db.checks_live.chk_threshold_provider.like("fset%")
        q |= db.checks_live.chk_threshold_provider == "defaults"
        rows = db(q).select()
    for row in rows:
        update_thresholds(row)

def update_thresholds(row):
    # try to find most precise settings
    t = get_settings(row)
    if t is not None:
        db(db.checks_live.id==row.id).update(chk_low=t[0], chk_high=t[1], chk_threshold_provider=t[2])
        update_dash_checks(row.chk_nodename)
        return

    # try to find filter-match thresholds
    t = get_filters(row)
    if t is not None:
        db(db.checks_live.id==row.id).update(chk_low=t[0], chk_high=t[1], chk_threshold_provider=t[2])
        update_dash_checks(row.chk_nodename)
        return

    # try to find least precise settings (ie defaults)
    t = get_defaults(row)
    if t is not None:
        db(db.checks_live.id==row.id).update(chk_low=t[0], chk_high=t[1], chk_threshold_provider=t[2])
        update_dash_checks(row.chk_nodename)
        return

    # no threshold found, leave as-is
    return

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

def get_settings(row):
    q = db.checks_settings.chk_nodename == row.chk_nodename
    q &= db.checks_settings.chk_type == row.chk_type
    q &= db.checks_settings.chk_instance == row.chk_instance
    rows = db(q).select()
    if len(rows) == 0:
        return
    return (rows[0].chk_low, rows[0].chk_high, 'settings')

def get_filters(row):
    qr = db.gen_filterset_check_threshold.chk_type == row.chk_type
    q1 = db.gen_filterset_check_threshold.chk_instance == row.chk_instance
    q2 = db.gen_filterset_check_threshold.chk_instance == None
    q3 = db.gen_filterset_check_threshold.chk_instance == ""
    qr &= (q1|q2|q3)
    qr &= db.gen_filterset_check_threshold.fset_id == db.gen_filtersets.id
    fsets = db(qr).select()
    if len(fsets) == 0:
        return
    for fset in fsets:
        qr = db.checks_live.id == row.id
        qr = apply_filters(qr, db.checks_live.chk_nodename, None, fset.gen_filtersets.id)
        n = db(qr).count()
        if n == 0:
            continue
        return (fset.gen_filterset_check_threshold.chk_low,
                fset.gen_filterset_check_threshold.chk_high,
                'fset: '+fset.gen_filtersets.fset_name)
    return

def comp_query(q, row):
    if 'v_gen_filtersets' in row:
        v = row.v_gen_filtersets
    else:
        v = row
    if v.encap_fset_id > 0:
        o = db.v_gen_filtersets.f_order
        qr = db.v_gen_filtersets.fset_id == v.encap_fset_id
        rows = db(qr).select(orderby=o)
        qry = None
        for r in rows:
            qry = comp_query(qry, r)
    else:
        if v.f_op == '=':
            qry = db[v.f_table][v.f_field] == v.f_value
        elif v.f_op == '!=':
            qry = db[v.f_table][v.f_field] != v.f_value
        elif v.f_op == 'LIKE':
            qry = db[v.f_table][v.f_field].like(v.f_value)
        elif v.f_op == 'NOT LIKE':
            qry = ~db[v.f_table][v.f_field].like(v.f_value)
        elif v.f_op == 'IN':
            qry = db[v.f_table][v.f_field].belongs(v.f_value.split(','))
        elif v.f_op == 'NOT IN':
            qry = ~db[v.f_table][v.f_field].belongs(v.f_value.split(','))
        elif v.f_op == '>=':
            qry = db[v.f_table][v.f_field] >= v.f_value
        elif v.f_op == '>':
            qry = db[v.f_table][v.f_field] > v.f_value
        elif v.f_op == '<=':
            qry = db[v.f_table][v.f_field] <= v.f_value
        elif v.f_op == '<':
            qry = db[v.f_table][v.f_field] < v.f_value
        else:
            return q
    if q is None:
        q = qry
    elif v.f_log_op == 'AND':
        q &= qry
    elif v.f_log_op == 'AND NOT':
        q &= ~qry
    elif v.f_log_op == 'OR':
        q |= qry
    elif v.f_log_op == 'OR NOT':
        q |= ~qry
    return q

@auth.requires_membership('CheckManager')
def del_fset_threshold(id):
    q = db.gen_filterset_check_threshold.id == id
    db(q).delete()

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
        update_thresholds(rows[0])
        where = ""
        if len(chk.chk_svcname) > 0: where = chk.chk_svcname + "@"
        where += chk.chk_nodename
        _log('checks.thresholds.set',
             'set high threshold to %(val)d for check %(inst)s on %(where)s',
             dict(val=val, where=where, inst='.'.join((chk.chk_type, chk.chk_instance))))

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
        update_thresholds(rows[0])
        where = ""
        if len(chk.chk_svcname) > 0: where = chk.chk_svcname + "@"
        where += chk.chk_nodename
        _log('checks.thresholds.set',
             'set high threshold to %(val)d for check %(inst)s on %(where)s',
             dict(val=val, where=where, inst='.'.join((chk.chk_type, chk.chk_instance))))

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
        update_thresholds(chk)
        where = ""
        if len(chk.chk_svcname) > 0: where = chk.chk_svcname + "@"
        where += chk.chk_nodename
        _log('checks.thresholds.reset',
             'reset thresholds for check %(inst)s on %(where)s',
             dict(where=where, inst='.'.join((chk.chk_type, chk.chk_instance))))

class col_chk_value(HtmlTableColumn):
    def html(self, o):
        val = self.get(o)
        high = self.t.colprops['chk_high'].get(o)
        low = self.t.colprops['chk_low'].get(o)
        if val > high or val < low:
            return SPAN(val, _style='font-weight:bold;color:darkred')
        return val

class col_chk_high(HtmlTableColumn):
    def html(self, o):
        high = self.get(o)
        val = self.t.colprops['chk_value'].get(o)
        if val > high:
            return SPAN(high, _style='font-weight:bold')
        return high

class col_chk_low(HtmlTableColumn):
    def html(self, o):
        low = self.get(o)
        val = self.t.colprops['chk_value'].get(o)
        if val < low:
            return SPAN(low, _style='font-weight:bold')
        return low

class col_chk_instance(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        chk_type = self.t.colprops["chk_type"].get(o)
        if chk_type == 'mpath':
            ln = A(
              IMG(
                _src=URL(c='static', f='hd16.png'),
                _style="vertical-align:top;padding-right:0.4em",
              ),
              _href=URL(c="disks", f="disks", vars={'disks_f_disk_id': s, 'clear_filters': 'true'}),
            )
            return SPAN(
                     ln,
                     s,
                     _style="white-space:nowrap",
                   )
        else:
            return s

class col_chk_type(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        nodename = self.t.colprops["chk_nodename"].get(o)

        d = DIV(
              A(
                s,
                _onclick="""
if ($("#checks_x_%(nodename)s").is(":visible")) {
  $("#checks_x_%(nodename)s").hide()
} else {
  $("#checks_x_%(nodename)s").show()
  ajax("%(url)s", [], "checks_x_%(nodename)s")
}
"""%dict(nodename=nodename.replace('.','_'),
         url=URL(r=request, f="ajax_chk_type_defaults", args=[s]),
        ),
              ),
            )
        return d

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
                     IMG(_src=URL(r=request, c='static', f='edit.png')),
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
                 IMG(_src=URL(r=request, c='static', f='add16.png')),
                 _href=URL(r=request, f='checks_defaults_insert', vars={'chk_type': chk_type}),
               ),
             ),
             DIV(
               T("Add threshold defaults"),
             ),
           ))


    return DIV(
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
        self.colprops = {
            'chk_nodename': col_node(
                title = 'Nodename',
                field = 'chk_nodename',
                display = True,
                table = 'checks_live',
                img = 'node16'
            ),
            'chk_svcname': col_svc(
                title = 'Service',
                field = 'chk_svcname',
                display = True,
                table = 'checks_live',
                img = 'check16'
            ),
            'chk_type': col_chk_type(
                title = 'Type',
                field = 'chk_type',
                display = True,
                table = 'checks_live',
                img = 'check16'
            ),
            'chk_instance': col_chk_instance(
                title = 'Instance',
                field = 'chk_instance',
                display = True,
                table = 'checks_live',
                img = 'check16'
            ),
            'chk_err': HtmlTableColumn(
                title = 'Error',
                field = 'chk_err',
                display = True,
                table = 'checks_live',
                img = 'check16'
            ),
            'chk_value': col_chk_value(
                title = 'Value',
                field = 'chk_value',
                display = True,
                table = 'checks_live',
                img = 'check16'
            ),
            'chk_low': col_chk_low(
                title = 'Low threshold',
                field = 'chk_low',
                display = True,
                table = 'checks_live',
                img = 'check16'
            ),
            'chk_high': col_chk_high(
                title = 'High threshold',
                field = 'chk_high',
                display = True,
                table = 'checks_live',
                img = 'check16'
            ),
            'chk_created': HtmlTableColumn(
                title = 'Created',
                field = 'chk_created',
                display = False,
                table = 'checks_live',
                img = 'check16'
            ),
            'chk_updated': col_updated(
                title = 'Last check update',
                field = 'chk_updated',
                display = True,
                table = 'checks_live',
                img = 'check16'
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
        self.dbfilterable = True
        self.checkbox_id_table = 'checks_live'
        self.checkboxes = True
        self.extraline = True
        self.span = 'chk_nodename'

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
    actiond = 'applications'+str(URL(r=request,c='actiond',f='actiond.py'))
    process = Popen(actiond)
    process.communicate()

    _log('node.action', 'run %(a)s on nodes %(s)s', dict(
          a=action,
          s=','.join(map(lambda x: x.nodename, rows)),
          ))

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
                update_thresholds_batch()
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
                db.commit()
                r = True
        if r:
            update_thresholds_batch()
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

    t.csv_q = q
    t.csv_orderby = o
    t.csv_limit = 15000
    t.csv_left = l

    if len(request.args) == 1 and request.args[0] == 'csv':
        return t.csv()

    n = db(q).select(db.checks_live.id.count(), left=l).first()(db.checks_live.id.count())
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end),
                                 orderby=o, left=l)
    return t.html()

@auth.requires_login()
def checks():
    t = DIV(
          ajax_checks(),
          _id='checks',
        )
    return dict(table=t)

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
    rows = db.executesql(sql)
    db.commit()


@auth.requires_login()
def checks_node():
    node = request.args[0]
    tid = 'checks_'+node
    t = table_checks(tid, 'ajax_checks')
    #t.cols.remove('mon_nodname')

    q = _where(None, 'checks_live', domain_perms(), 'chk_nodename')
    q &= db.checks_live.chk_nodename == node
    q &= db.checks_live.chk_nodename == db.v_nodes.nodename
    t.object_list = db(q).select()
    t.hide_tools = True
    t.pageable = False
    t.bookmarkable = False
    t.commonalityable = False
    t.linkable = False
    t.filterable = False
    t.exportable = False
    t.dbfilterable = False
    t.columnable = False
    t.refreshable = False
    t.checkboxes = False
    return t.html()

