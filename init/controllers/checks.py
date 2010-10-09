@auth.requires_login()
def checks_defaults_insert():
    q = (db.checks_defaults.chk_type==request.vars.chk_type)
    rows = db(q).select()
    if len(rows) == 1:
        record = rows[0]
    else:
        record = None

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
def _checks_set_low_threshold(request):
    val = int(request.vars.val)
    ids = ([])
    now = datetime.datetime.now()
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        ids += ([key[6:]])
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

def _checks_set_high_threshold(request):
    val = int(request.vars.val)
    ids = ([])
    now = datetime.datetime.now()
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        ids += ([key[6:]])
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

def _checks_reset_settings(request):
    ids = ([])
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        ids += ([key[6:]])
    for i in ids:
        rows = db(db.checks_live.id==i).select()
        if len(rows) != 1:
            continue
        chk = rows[0]
        q = db.checks_settings.chk_nodename==chk.chk_nodename
        q &= db.checks_settings.chk_type==chk.chk_type
        q &= db.checks_settings.chk_instance==chk.chk_instance
        settings = db(q).delete()

@auth.requires_login()
def checks():
    if request.vars.action == "set_low_thres":
        _checks_set_low_threshold(request)
    elif request.vars.action == "set_high_thres":
        _checks_set_high_threshold(request)
    elif request.vars.action == "reset":
        _checks_reset_settings(request)

    d1 = dict(
        chk_nodename = dict(
            pos = 1,
            title = T('Nodename'),
            display = True,
            nestedin = 'v_checks',
            img = 'node16',
            size = 10
        ),
        chk_svcname = dict(
            pos = 2,
            title = T('Service'),
            display = True,
            nestedin = 'v_checks',
            img = 'check16',
            size = 10
        ),
        chk_type = dict(
            pos = 3,
            title = T('Type'),
            display = True,
            nestedin = 'v_checks',
            img = 'check16',
            size = 3
        ),
        chk_instance = dict(
            pos = 4,
            title = T('Instance'),
            display = True,
            nestedin = 'v_checks',
            img = 'check16',
            size = 10
        ),
        chk_value = dict(
            pos = 5,
            title = T('Value'),
            display = True,
            nestedin = 'v_checks',
            img = 'check16',
            size = 3
        ),
        chk_low = dict(
            pos = 6,
            title = T('Low threshold'),
            display = True,
            nestedin = 'v_checks',
            img = 'check16',
            size = 3
        ),
        chk_high = dict(
            pos = 7,
            title = T('High threshold'),
            display = True,
            nestedin = 'v_checks',
            img = 'check16',
            size = 10
        ),
        chk_created = dict(
            pos = 8,
            title = T('Created'),
            display = False,
            nestedin = 'v_checks',
            img = 'check16',
            size = 6
        ),
        chk_updated = dict(
            pos = 9,
            title = T('Updated'),
            display = True,
            nestedin = 'v_checks',
            img = 'check16',
            size = 6
        ),
    )
    d2 = v_nodes_columns()
    for k in d2:
        d2[k]['pos'] += 10
        d2[k]['display'] = False
        d2[k]['nestedin'] = 'v_nodes'
    del(d2['nodename'])

    columns = d1.copy()
    columns.update(d2)

    def _sort_cols(x, y):
        return cmp(columns[x]['pos'], columns[y]['pos'])

    colkeys = columns.keys()
    colkeys.sort(_sort_cols)
    __update_columns(columns, 'checks')

    o = db.v_checks.chk_nodename
    o |= db.v_checks.chk_type
    o |= db.v_checks.chk_instance

    toggle_db_filters()

    # filtering
    query = db.v_checks.id>0
    query &= db.v_checks.chk_nodename==db.v_nodes.nodename
    for key in d1.keys():
        if key not in request.vars.keys():
            continue
        query &= _where(None, 'v_checks', request.vars[key], key)
    for key in d2.keys():
        if key not in request.vars.keys():
            continue
        query &= _where(None, 'v_nodes', request.vars[key], key)

    query &= _where(None, 'v_checks', domain_perms(), 'chk_nodename')

    query = apply_db_filters(query, 'v_nodes')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select(orderby=o)
    else:
        rows = db(query).select(limitby=(start,end), orderby=o)

    return dict(columns=columns, colkeys=colkeys,
                checks=rows,
                nav=nav,
                active_filters=active_db_filters('v_nodes'),
                available_filters=avail_db_filters('v_nodes'),
               )

def checks_csv():
    import gluon.contenttype
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    request.vars['perpage'] = 0
    return str(checks()['checks'])


