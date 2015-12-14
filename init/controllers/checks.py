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
        self.events = ["checks_change"]

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

@auth.requires_login()
def ajax_checks_col_values():
    table_id = request.vars.table_id
    t = table_checks(table_id, 'ajax_checks')
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
    table_id = request.vars.table_id
    t = table_checks(table_id, 'ajax_checks')

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
    t = SCRIPT(
          """$.when(osvc.app_started).then(function(){ table_checks("layout") })""",
        )
    return dict(table=t)

def checks_load():
    return checks()["table"]

def batch_update_thresholds():
    update_thresholds_batch()

