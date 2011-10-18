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
        update_thresholds_batch()
        db(q).update(chk_changed=now,
                     chk_changed_by=user_name())
        redirect(URL(r=request, c='checks', f='checks'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form, record=record)

def update_thresholds_batch(rows=None):
    # maintenance batch
    if rows is None:
        q = db.checks_live.id > 0
        q = db.checks_live.chk_threshold_provider.like("fset%")|db.checks_live.chk_threshold_provider == "defaults"
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
    q = db.checks_defaults.chk_type == row.chk_type
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
    fsets = db(qr).select()
    if len(fsets) == 0:
        return
    for fset in fsets:
        qr = db.v_gen_filtersets.fset_id == fset.fset_id
        filters = db(qr).select(db.v_gen_filtersets.ALL, orderby=db.v_gen_filtersets.f_order|db.v_gen_filtersets.id)
        if len(filters) == 0:
            continue
        qr = db.nodes.nodename == row.chk_nodename
        qr &= db.nodes.nodename == db.svcmon.mon_nodname
        qr &= db.svcmon.mon_svcname == db.services.svc_name
        for f in filters:
            qr = comp_query(qr, f)
        n = db(qr).count()
        if n == 0:
            continue
        return (fset.chk_low, fset.chk_high, 'fset: '+f.fset_name)
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
        update_thresholds(rows[0])

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
        update_thresholds(rows[0])

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
        update_thresholds(chk)

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
            'chk_instance': HtmlTableColumn(
                title = 'Instance',
                field = 'chk_instance',
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
        for c in self.cols:
            self.colprops[c].t = self
        self.ajax_col_values = 'ajax_checks_col_values'
        self.dbfilterable = False
        self.checkbox_id_table = 'checks_live'
        self.checkboxes = True
        self.extraline = True
        self.span = 'chk_nodename'

        self.form_add_fset_threshold = self.add_fset_threshold_sqlform()

        if 'CheckManager' in user_groups():
            self.additional_tools.append('set_low_threshold')
            self.additional_tools.append('set_high_threshold')
            self.additional_tools.append('reset_thresholds')
            self.additional_tools.append('add_fset_threshold')

    def set_low_threshold(self):
        return self.set_threshold('low')

    def set_high_threshold(self):
        return self.set_threshold('high')

    def add_fset_threshold(self):
        d = DIV(
              A(
                T("Add fset threshold"),
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
    q = db.checks_live.id>0
    q = _where(q, 'checks_live', domain_perms(), 'chk_nodename')
    q = apply_db_filters(q, 'v_nodes')
    q &= db.checks_live.chk_nodename==db.v_nodes.nodename
    o = db.checks_live[col]
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
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

    try:
        if t.form_add_fset_threshold.accepts(request.vars):
            db.gen_filterset_check_threshold.insert(fset_id=request.vars.fset_id,
                                                    chk_type=request.vars.chk_type,
                                                    chk_instance=request.vars.chk_instance,
                                                    chk_low=request.vars.chk_low,
                                                    chk_high=request.vars.chk_high)
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
    q = apply_db_filters(q, 'v_nodes')
    q &= db.checks_live.chk_nodename==db.v_nodes.nodename
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

def update_dash_checks(nodename):
    nodename = nodename.strip("'")
    sql = """delete from dashboard
               where
                 dash_nodename = "%(nodename)s" and
                 dash_type = "check out of bounds"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)

    sql = """select environnement from nodes
             where
               nodename="%(nodename)s"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)

    if len(rows) == 1 and rows[0][0] == 'PRD':
        sev = 3
    else:
        sev = 2

    sql = """insert ignore into dashboard
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
                 now(),
                 md5(concat('{"ctype": "', t.ctype,
                        '", "inst": "', t.inst,
                        '", "ttype": "', t.ttype,
                        '", "val": ', t.val,
                        ', "min": ', t.min,
                        ', "max": ', t.max,
                        '}'))
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
                   chk_updated = date_sub(now(), interval 1 day) and
                   (
                     chk_value < chk_low or
                     chk_value > chk_high
                   )
               ) t
          """%dict(nodename=nodename,
                   sev=sev,
                  )
    db.executesql(sql)

