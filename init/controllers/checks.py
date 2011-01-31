@auth.requires_login()
def checks_defaults_insert():
    q = (db.checks_defaults.chk_type==request.vars.chk_type)
    rows = db(q).select()
    if len(rows) == 1:
        record = rows[0]
    else:
        record = None

    db.checks_defaults.chk_type.default = request.vars.chk_type
    form = SQLFORM(db.checks_defaults,
                 record=record,
                 fields=['chk_type',
                         'chk_low',
                         'chk_high'],
                 labels={'chk_type': T('Check type'),
                         'chk_low': T('Low threshold'),
                         'chk_high': T('High threshold')},
                )
    if form.accepts(request.vars):
        response.flash = T("edition recorded")
        redirect(URL(r=request, c='checks', f='checks'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)

@auth.requires_login()
def checks_settings_insert():
    q = (db.checks_settings.chk_nodename==request.vars.chk_nodename)
    q &= (db.checks_settings.chk_svcname==request.vars.chk_svcname)
    q &= (db.checks_settings.chk_type==request.vars.chk_type)
    q &= (db.checks_settings.chk_instance==request.vars.chk_instance)
    rows = db(q).select()
    if len(rows) == 0:
        defaults = db(db.checks_defaults.chk_type==request.vars.chk_type).select().first()
        db.checks_settings.insert(chk_nodename=request.vars.chk_nodename,
                                  chk_svcname=request.vars.chk_svcname,
                                  chk_type=request.vars.chk_type,
                                  chk_instance=request.vars.chk_instance,
                                  chk_low=defaults.chk_low,
                                  chk_high=defaults.chk_high,
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
        db(q).update(chk_changed=now,
                     chk_changed_by=user_name())
        redirect(URL(r=request, c='checks', f='checks'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form, record=record)

@auth.requires_login()
def set_low_threshold(ids):
    if len(ids) == 0:
        raise ToolError("No check selected")
    val = request.vars.set_low_threshold
    if val is None or len(val) == 0:
        raise ToolError("New threshold value invalid")
    val = int(val)
    for i in ids:
        rows = db(db.checks_live.id==i).select()
        if len(rows) != 1:
            continue
        chk = rows[0]
        q = db.checks_settings.chk_nodename==chk.chk_nodename
        q &= db.checks_settings.chk_type==chk.chk_type
        q &= db.checks_settings.chk_instance==chk.chk_instance
        settings = db(q).select()
        if len(settings) == 0:
            # insert
            defq = db.checks_defaults.chk_type==chk.chk_type
            defq &= db.checks_defaults.chk_type==chk.chk_type
            defaults = db(defq).select()
            if len(defaults) != 1:
                continue
            default = defaults[0]
            db.checks_settings.insert(chk_nodename=chk.chk_nodename,
                                      chk_type=chk.chk_type,
                                      chk_instance=chk.chk_instance,
                                      chk_low=val,
                                      chk_high=default.chk_high,
                                      chk_changed_by=user_name(),
                                      chk_changed=now)
        elif len(settings) == 1:
            # update
            db(q).update(chk_low=val,
                         chk_changed_by=user_name(),
                         chk_changed=now)

@auth.requires_login()
def set_high_threshold(ids):
    if len(ids) == 0:
        raise ToolError("No check selected")
    val = request.vars.set_high_threshold
    if val is None or len(val) == 0:
        raise ToolError("New threshold value invalid")
    val = int(val)
    for i in ids:
        rows = db(db.checks_live.id==i).select()
        if len(rows) != 1:
            continue
        chk = rows[0]
        q = db.checks_settings.chk_nodename==chk.chk_nodename
        q &= db.checks_settings.chk_type==chk.chk_type
        q &= db.checks_settings.chk_instance==chk.chk_instance
        settings = db(q).select()
        if len(settings) == 0:
            # insert
            defq = db.checks_defaults.chk_type==chk.chk_type
            defq &= db.checks_defaults.chk_type==chk.chk_type
            chk_defaults = db(defq).select()
            if len(chk_defaults) != 1:
                continue
            chk_default = chk_defaults[0]
            db.checks_settings.insert(chk_nodename=chk.chk_nodename,
                                      chk_type=chk.chk_type,
                                      chk_instance=chk.chk_instance,
                                      chk_high=val,
                                      chk_low=chk_default.chk_low,
                                      chk_changed_by=user_name(),
                                      chk_changed=now)
        elif len(settings) == 1:
            # update
            db(q).update(chk_high=val,
                         chk_changed_by=user_name(),
                         chk_changed=now)

@auth.requires_login()
def reset_thresholds(ids):
    if len(ids) == 0:
        raise ToolError("No check selected")
    for i in ids:
        rows = db(db.checks_live.id==i).select()
        if len(rows) != 1:
            continue
        chk = rows[0]
        q = db.checks_settings.chk_nodename==chk.chk_nodename
        q &= db.checks_settings.chk_type==chk.chk_type
        q &= db.checks_settings.chk_instance==chk.chk_instance
        settings = db(q).delete()

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

class col_chk_type(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        d = A(
              s,
              _href=URL(r=request, c='checks', f='checks_defaults_insert',
                        vars={'chk_type': s})
            )
        return d

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
                     'chk_created',
                     'chk_updated']
        self.colprops = {
            'chk_nodename': col_node(
                title = 'Nodename',
                field = 'chk_nodename',
                display = True,
                table = 'v_checks',
                img = 'node16'
            ),
            'chk_svcname': col_svc(
                title = 'Service',
                field = 'chk_svcname',
                display = True,
                table = 'v_checks',
                img = 'check16'
            ),
            'chk_type': col_chk_type(
                title = 'Type',
                field = 'chk_type',
                display = True,
                table = 'v_checks',
                img = 'check16'
            ),
            'chk_instance': HtmlTableColumn(
                title = 'Instance',
                field = 'chk_instance',
                display = True,
                table = 'v_checks',
                img = 'check16'
            ),
            'chk_value': col_chk_value(
                title = 'Value',
                field = 'chk_value',
                display = True,
                table = 'v_checks',
                img = 'check16'
            ),
            'chk_low': col_chk_low(
                title = 'Low threshold',
                field = 'chk_low',
                display = True,
                table = 'v_checks',
                img = 'check16'
            ),
            'chk_high': col_chk_high(
                title = 'High threshold',
                field = 'chk_high',
                display = True,
                table = 'v_checks',
                img = 'check16'
            ),
            'chk_created': HtmlTableColumn(
                title = 'Created',
                field = 'chk_created',
                display = False,
                table = 'v_checks',
                img = 'check16'
            ),
            'chk_updated': col_updated(
                title = 'Last check update',
                field = 'chk_updated',
                display = True,
                table = 'v_checks',
                img = 'check16'
            ),
        }
        self.colprops.update(v_nodes_colprops)
        self.cols += v_nodes_cols
        for c in self.cols:
            self.colprops[c].t = self
        self.ajax_col_values = 'ajax_checks_col_values'
        self.dbfilterable = False
        self.checkbox_id_table = 'v_checks'
        self.checkboxes = True
        self.extraline = True
        self.span = 'chk_nodename'
        if 'CheckManager' in user_groups():
            self.additional_tools.append('set_low_threshold')
            self.additional_tools.append('set_high_threshold')
            self.additional_tools.append('reset_thresholds')

    def set_low_threshold(self):
        return self.set_threshold('low')

    def set_high_threshold(self):
        return self.set_threshold('high')

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


@auth.requires_login()
def ajax_checks_col_values():
    t = table_checks('checks', 'ajax_checks')
    col = request.args[0]
    o = db.v_users[col]
    q = db.v_users.id > 0
    t.object_list = db(q).select(orderby=o, groupby=o)
    for f in t.cols:
        q = _where(q, 'v_users', t.filter_parse(f), f)
    t.object_list = db(q).select(orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_checks():
    t = table_checks('checks', 'ajax_checks')

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'set_low_threshold':
                set_low_threshold(t.get_checked())
            elif action == 'set_high_threshold':
                set_high_threshold(t.get_checked())
            elif action == 'reset_thresholds':
                reset_thresholds(t.get_checked())
        except ToolError, e:
            t.flash = str(e)

    o = db.v_checks.chk_nodename
    o |= db.v_checks.chk_type
    o |= db.v_checks.chk_instance
    q = db.v_checks.id>0
    q = _where(q, 'v_checks', domain_perms(), 'chk_nodename')
    q = apply_db_filters(q, 'v_nodes')
    q &= db.v_checks.chk_nodename==db.v_nodes.nodename
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return t.html()

@auth.requires_login()
def checks():
    t = DIV(
          ajax_checks(),
          _id='checks',
        )
    return dict(table=t)


