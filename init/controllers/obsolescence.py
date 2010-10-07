def ajax_obsolete_os_nodes():
    if request.vars.obs_type == "os":
        query = (db.obsolescence.obs_type=="os")&(db.v_nodes.os_concat==request.vars.obs_name)
    elif request.vars.obs_type == "hw":
        query = (db.obsolescence.obs_type=="hw")&(db.v_nodes.model==request.vars.obs_name)
    else:
        return DIV()

    query = apply_db_filters(query, 'v_nodes')
    rows = db(query).select(db.v_nodes.nodename, orderby=db.v_nodes.nodename, groupby=db.v_nodes.nodename)
    nodes = [row.nodename for row in rows]
    return DIV(
             H3(T("""Nodes in %(os)s""",dict(os=request.vars.obs_name))),
             PRE('\n'.join(nodes)),
           )

def refresh_obsolescence():
    cron_obsolescence_os()
    cron_obsolescence_hw()

def cron_obsolescence_hw():
    sql = """insert ignore into obsolescence (obs_type, obs_name)
             select "hw", model
             from nodes
             where model!=''
             group by model;
          """
    db.executesql(sql)
    return dict(message=T("done"))

def cron_obsolescence_os():
    sql = """insert ignore into obsolescence (obs_type, obs_name)
             select "os", concat_ws(" ", os_name, os_vendor, os_release, os_update)
             from nodes
             where os_name!='' or os_vendor!='' or os_release!='' or os_update!=''
             group by os_name, os_vendor, os_release, os_update;
          """
    db.executesql(sql)
    return dict(message=T("done"))

@auth.requires_membership('Manager')
def _obs_warn_date_edit(request):
    _obs_date_edit(request, "warn")

@auth.requires_membership('Manager')
def _obs_alert_date_edit(request):
    _obs_date_edit(request, "alert")

@auth.requires_membership('Manager')
def _obs_date_edit(request, what):
    ids = ([])
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        id = int(key[6:])
        date = request.vars[what+"_date_"+str(id)]
        if date is None or len(date) == 0:
            sql = """update obsolescence
                     set obs_%(what)s_date='',
                         obs_%(what)s_date_updated='%(now)s',
                         obs_%(what)s_date_updated_by='%(user)s'
                     where id=%(id)s;
                  """%dict(id=id,
                           now=datetime.datetime.now(),
                           what=what,
                           user=user_name()
                          )
        else:
            sql = """update obsolescence
                     set obs_%(what)s_date='%(date)s',
                         obs_%(what)s_date_updated='%(now)s',
                         obs_%(what)s_date_updated_by='%(user)s'
                     where id=%(id)s;
                  """%dict(id=id,
                           now=datetime.datetime.now(),
                           what=what,
                           date=date,
                           user=user_name()
                          )
        #raise Exception(sql)
        db.executesql(sql)

@auth.requires_membership('Manager')
def _obs_item_del(request):
    ids = ([])
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        ids += ([int(key[6:])])
    sql = "delete from obsolescence where id in (%s)"%','.join(map(str, ids))
    db.executesql(sql)

@auth.requires_membership('Manager')
def obsolescence_config():
    if request.vars.action == "del":
        _obs_item_del(request)
    elif request.vars.action == "set_warn_date":
        _obs_warn_date_edit(request)
    elif request.vars.action == "set_alert_date":
        _obs_alert_date_edit(request)
    elif request.vars.action == "refresh":
        refresh_obsolescence()

    toggle_db_filters()

    o = db.obsolescence.obs_type
    o |= db.obsolescence.obs_name
    o |= db.obsolescence.obs_warn_date
    o |= db.obsolescence.obs_alert_date

    g = db.obsolescence.obs_type|db.obsolescence.obs_name

    query = (db.obsolescence.obs_type=="os")&(db.obsolescence.obs_name==db.v_nodes.os_concat)
    query |= (db.obsolescence.obs_type=="hw")&(db.obsolescence.obs_name==db.v_nodes.model)
    query &= (~db.v_nodes.model.like("%virtual%"))
    query &= (~db.v_nodes.model.like("%virtuel%"))
    query &= (~db.v_nodes.model.like("%cluster%"))
    query &= _where(None, 'obsolescence', request.vars.obs_type, 'obs_type')
    query &= _where(None, 'obsolescence', request.vars.obs_name, 'obs_name')
    query &= _where(None, 'obsolescence', request.vars.obs_warn_date, 'obs_warn_date')
    query &= _where(None, 'obsolescence', request.vars.obs_alert_date, 'obs_alert_date')

    query = apply_db_filters(query, 'v_nodes')

    (start, end, nav) = _pagination(request, query, groupby=g)
    if start == 0 and end == 0:
        rows = db(query).select(db.obsolescence.ALL, db.v_nodes.id.count(), orderby=o, groupby=g)
    else:
        rows = db(query).select(db.obsolescence.ALL, db.v_nodes.id.count(), limitby=(start,end), orderby=o, groupby=g)

    return dict(obsitems=rows,
                active_filters=active_db_filters('v_nodes'),
                available_filters=avail_db_filters('v_nodes'),
                nav=nav)


