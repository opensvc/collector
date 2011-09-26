# coding: utf8

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
import datetime

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

#
# XMLRPC
#
#########
def auth_uuid(fn):
    def new(*args):
        uuid, node = args['auth']
        rows = db(db.auth_node.nodename==node&db.auth_node.uuid==uuid).select()
        if len(rows) != 1:
            return
        return fn(*args)
    return new

@auth_uuid
@service.xmlrpc
def delete_services(hostid=None, auth=("", "")):
    if hostid is None:
        return 0
    db(db.services.svc_hostid==hostid).delete()
    db.commit()
    return 0

@auth_uuid
@service.xmlrpc
def delete_service_list(hostid=None, svcnames=[], auth=("", "")):
    if hostid is None or len(svcnames) == 0:
        return 0
    for svcname in svcnames:
        q = (db.services.svc_name==svcname)
        q &= (db.services.svc_hostid==hostid)
        db(q).delete()
        db.commit()
    return 0

@auth_uuid
@service.xmlrpc
def begin_action(vars, vals, auth):
    sql="""insert into SVCactions (%s) values (%s)""" % (','.join(vars), ','.join(vals))
    db.executesql(sql)
    db.commit()
    h = {}
    for a, b in zip(vars, vals):
        h[a] = b
    if 'cron' not in h or h['cron'] == '0':
        _log("service.action",
             "action '%(a)s' on %(svc)s@%(node)s",
             dict(a=h['action'].strip("'"),
                  svc=h['svcname'].strip("'"),
                  node=h['hostname'].strip("'")),
             svcname=h['svcname'].strip("'"),
             nodename=h['hostname'].strip("'"))
    return 0

@auth_uuid
@service.xmlrpc
def res_action(vars, vals, auth):
    upd = []
    for a, b in zip(vars, vals):
        upd.append("%s=%s" % (a, b))
    sql="""insert delayed into SVCactions (%s) values (%s)""" % (','.join(vars), ','.join(vals))
    db.executesql(sql)
    db.commit()
    return 0

@auth_uuid
@service.xmlrpc
def end_action(vars, vals, auth):
    feed_enqueue("_end_action", vars, vals)

def _end_action(vars, vals):
    upd = []
    h = {}
    for a, b in zip(vars, vals):
        h[a] = b
        if a not in ['hostname', 'svcname', 'begin', 'action', 'hostid']:
            upd.append("%s=%s" % (a, b))
    sql="""update SVCactions set %s where hostname=%s and svcname=%s and begin=%s and action=%s""" %\
        (','.join(upd), h['hostname'], h['svcname'], h['begin'], h['action'])
    #raise Exception(sql)
    db.executesql(sql)
    db.commit()
    if h['action'].strip("'") in ('start', 'startcontainer') and \
       h['status'].strip("'") == 'ok':
        update_virtual_asset(h['hostname'].strip("'"), h['svcname'].strip("'"))
    if h['status'].strip("'") == 'err':
        update_action_errors(h['svcname'], h['hostname'])
        update_dash_action_errors(h['svcname'], h['hostname'])
        h['svcname'] = h['svcname'].strip('\\').strip("'")
        _log("service.action",
             "action '%(a)s' error on %(svc)s@%(node)s",
             dict(a=h['action'].strip("'"),
                  svc=h['svcname'].strip("'"),
                  node=h['hostname'].strip("'")),
             svcname=h['svcname'].strip("'"),
             nodename=h['hostname'].strip("'"),
             level="error")
    return 0

def update_action_errors(svcname, nodename):
    sql = """insert into b_action_errors set svcname=%(svcname)s, nodename=%(nodename)s, err=(
               select count(a.id) from SVCactions a
                 where a.svcname = %(svcname)s and
                       a.hostname = %(nodename)s and
                       a.status = 'err' and
                       ((a.ack <> 1) or isnull(a.ack)))
             on duplicate key update err=(
               select count(a.id) from SVCactions a
                 where a.svcname = %(svcname)s and
                       a.hostname = %(nodename)s and
                       a.status = 'err' and
                       ((a.ack <> 1) or isnull(a.ack)))
          """%dict(svcname=svcname, nodename=nodename)
    #raise Exception(sql)
    db.executesql(sql)

def update_virtual_asset(nodename, svcname):
    q = db.services.svc_name == svcname
    svc = db(q).select(db.services.svc_vmname).first()
    if svc is None:
        return
    q = db.nodes.nodename == nodename
    node = db(q).select().first()
    if node is None:
        return
    fields = ['loc_addr', 'loc_city', 'loc_zip', 'loc_room', 'loc_building',
              'loc_floor', 'loc_rack', 'power_cabinet1', 'power_cabinet2',
              'power_supply_nb', 'power_protect', 'power_protect_breaker',
              'power_breaker1', 'power_breaker2', 'loc_country']
    sql = "update nodes set "
    for f in fields:
        sql += "%s='%s',"%(f, node[f])
    sql = sql.rstrip(',')
    sql += "where nodename='%s'"%svc.svc_vmname
    db.executesql(sql)

@auth_uuid
@service.xmlrpc
def update_appinfo(vars, vals, auth):
    h = {}
    for a,b in zip(vars, vals[0]):
        h[a] = b
    db.executesql("delete from appinfo where app_svcname='%s'"%h['app_svcname'])
    generic_insert('appinfo', vars, vals)

@auth_uuid
@service.xmlrpc
def update_service(vars, vals, auth):
    feed_enqueue("_update_service", vars, vals)

def _update_service(vars, vals):
    h = {}
    for a,b in zip(vars, vals[0]):
        h[a] = b
    if 'svc_hostid' not in vars:
        return
    if 'updated' not in vars:
        vars += ['updated']
        vals += [datetime.datetime.now()]
    generic_insert('services', vars, vals)
    update_dash_service_not_updated(h['svc_name'])

@auth_uuid
@service.xmlrpc
def push_checks(vars, vals, auth):
    feed_enqueue("_push_checks", vars, vals)

def _push_checks(vars, vals):
    """
        chk_nodename
        chk_svcname
        chk_type
        chk_instance
        chk_value
        chk_updated
    """
    generic_insert('checks_live', vars, vals)
    q = db.checks_live.id < 0
    for v in vals:
        qr = db.checks_live.chk_nodename == v[0]
        qr &= db.checks_live.chk_type == v[2]
        qr &= db.checks_live.chk_instance == v[3]
        q |= qr
    rows = db(q).select()
    update_thresholds_batch(rows)
    if len(vals) > 0:
        update_dash_checks(vals[0][0])

@auth_uuid
@service.xmlrpc
def update_asset(vars, vals, auth):
    feed_enqueue("_update_asset", vars, vals, auth)

def _update_asset(vars, vals, auth):
    now = datetime.datetime.now()
    vars.append('updated')
    vals.append(now)
    generic_insert('nodes', vars, vals)
    update_dash_node_not_updated(auth[1])
    update_dash_node_without_warranty_end(auth[1])
    update_dash_node_without_asset(auth[1])

@auth_uuid
@service.xmlrpc
def res_action_batch(vars, vals, auth):
    generic_insert('SVCactions', vars, vals)

def _resmon_clean(node, svcname):
    if node is None or node == '':
        return 0
    if svcname is None or svcname == '':
        return 0
    q = db.resmon.nodename==node.strip("'")
    q &= db.resmon.svcname==svcname.strip("'")
    db(q).delete()
    db.commit()

@auth_uuid
@service.xmlrpc
def resmon_update(vars, vals, auth):
    _resmon_update(vars, vals)

def _resmon_update(vars, vals):
    if len(vals) == 0:
        return
    if isinstance(vals[0], list):
        for v in vals:
            __resmon_update(vars, v)
    else:
        __resmon_update(vars, vals)

def __resmon_update(vars, vals):
    h = {}
    for a,b in zip(vars, vals[0]):
        h[a] = b
    if 'nodename' in h and 'svcname' in h:
        _resmon_clean(h['nodename'], h['svcname'])
    generic_insert('resmon', vars, vals)

@auth_uuid
@service.xmlrpc
def svcmon_update_combo(g_vars, g_vals, r_vars, r_vals, auth):
    feed_enqueue("_svcmon_update", g_vars, g_vals)
    feed_enqueue("_resmon_update", r_vars, r_vals)

@auth_uuid
@service.xmlrpc
def register_disk(vars, vals, auth):
    generic_insert('svcdisks', vars, vals)

@auth_uuid
@service.xmlrpc
def register_sync(vars, vals, auth):
    pass

@auth_uuid
@service.xmlrpc
def register_ip(vars, vals, auth):
    pass

@auth_uuid
@service.xmlrpc
def register_fs(vars, vals, auth):
    pass

@auth_uuid
@service.xmlrpc
def insert_stats_fs_u(vars, vals, auth):
    generic_insert('stats_fs_u', vars, vals)

@auth_uuid
@service.xmlrpc
def insert_stats_cpu(vars, vals, auth):
    generic_insert('stats_cpu', vars, vals)

@auth_uuid
@service.xmlrpc
def insert_stats_mem_u(vars, vals, auth):
    generic_insert('stats_mem_u', vars, vals)

@auth_uuid
@service.xmlrpc
def insert_stats_proc(vars, vals, auth):
    generic_insert('stats_proc', vars, vals)

@auth_uuid
@service.xmlrpc
def insert_stats_swap(vars, vals, auth):
    generic_insert('stats_swap', vars, vals)

@auth_uuid
@service.xmlrpc
def insert_stats_block(vars, vals, auth):
    generic_insert('stats_block', vars, vals)

@auth_uuid
@service.xmlrpc
def insert_stats_blockdev(vars, vals, auth):
    generic_insert('stats_blockdev', vars, vals)

@auth_uuid
@service.xmlrpc
def insert_stats_netdev(vars, vals, auth):
    generic_insert('stats_netdev', vars, vals)

@auth_uuid
@service.xmlrpc
def insert_stats_netdev_err(vars, vals, auth):
    generic_insert('stats_netdev_err', vars, vals)

@auth_uuid
@service.xmlrpc
def insert_stats(data, auth):
    feed_enqueue("_insert_stats", data, auth)

def _insert_stats(data, auth):
    import cPickle
    h = cPickle.loads(data)
    for stat in h:
        vars, vals = h[stat]
        generic_insert('stats_'+stat, vars, vals)
    update_dash_netdev_errors(auth[1])

@auth_uuid
@service.xmlrpc
def insert_pkg(vars, vals, auth):
    feed_enqueue("_insert_pkg", vars, vals, auth)

def _insert_pkg(vars, vals, auth):
    generic_insert('packages', vars, vals)
    update_dash_pkgdiff(auth[1])

@auth_uuid
@service.xmlrpc
def update_sym_xml(symid, vars, vals, auth):
    import os

    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
    if not os.path.exists(dir):
        os.makedirs(dir)

    dir = os.path.join(dir, symid)
    if not os.path.exists(dir):
        os.makedirs(dir)

    for a,b in zip(vars, vals):
        a = os.path.join(dir, a)
        try:
            f = open(a, 'w')
            f.write(b)
            f.close()
        except:
            pass

    symmetrix = local_import('symmetrix', reload=True)
    s = symmetrix.get_sym(dir)
    if s is None:
        return

    #
    # better to create hashes from the batch rather than
    # during an interactive session
    #
    s.get_sym_all()

    #
    # populate the diskinfo table
    #
    vars = ['disk_id', 'disk_devid', 'disk_arrayid']
    vals = []
    for devname, dev in s.dev.items():
        vals.append([dev.wwn, devname, symid])
    generic_insert('diskinfo', vars, vals)

@auth_uuid
@service.xmlrpc
def delete_pkg(node, auth):
    if node is None or node == '':
        return 0
    db(db.packages.pkg_nodename==node).delete()
    db.commit()

@auth_uuid
@service.xmlrpc
def insert_patch(vars, vals, auth):
    generic_insert('patches', vars, vals)

@auth_uuid
@service.xmlrpc
def delete_patch(node, auth):
    if node is None or node == '':
        return 0
    db(db.patches.patch_nodename==node).delete()
    db.commit()

@auth_uuid
@service.xmlrpc
def delete_syncs(svcname, auth):
    pass

@auth_uuid
@service.xmlrpc
def delete_ips(svcname, node, auth):
    pass

@auth_uuid
@service.xmlrpc
def delete_fss(svcname, auth):
    pass

@auth_uuid
@service.xmlrpc
def delete_disks(svcname, node, auth):
    if svcname is None or svcname == '':
        return 0
    db((db.svcdisks.disk_svcname==svcname)&(db.svcdisks.disk_nodename==node)).delete()
    db.commit()

@service.xmlrpc
def register_node(node):
    if node is None or node == '':
        return ["no node name provided"]
    q = db.auth_node.nodename == node
    rows = db(q).select()
    if len(rows) != 0:
        _log("node.register",
             "node '%(node)s' double registration attempt",
             dict(node=node),
             nodename=node,
             level="warning")
        return ["already registered"]
    import uuid
    u = str(uuid.uuid4())
    db.auth_node.insert(nodename=node, uuid=u)
    db.commit()
    _log("node.register",
         "node '%(node)s' registered",
         dict(node=node),
         nodename=node)
    return u

@auth_uuid
@service.xmlrpc
def svcmon_update(vars, vals, auth):
    feed_enqueue("_svcmon_update", vars, vals)

def _svcmon_update(vars, vals):
    if len(vals) == 0:
        return
    if isinstance(vals[0], list):
        for v in vals:
            __svcmon_update(vars, v)
    else:
        __svcmon_update(vars, vals)

def compute_availstatus(h):
    def status_merge_down(s):
        if s == 'up': return 'warn'
        elif s == 'down': return 'down'
        elif s == 'stdby down': return 'stdby down'
        elif s == 'stdby up': return 'stdby up with down'
        elif s == 'stdby up with up': return 'warn'
        elif s == 'stdby up with down': return 'stdby up with down'
        elif s in ['undef', 'n/a']: return 'down'
        else: return 'undef'

    def status_merge_up(s):
        if s == 'up': return 'up'
        elif s == 'down': return 'warn'
        elif s == 'stdby down': return 'warn'
        elif s == 'stdby up': return 'stdby up with up'
        elif s == 'stdby up with up': return 'stdby up with up'
        elif s == 'stdby up with down': return 'warn'
        elif s in ['undef', 'n/a']: return 'up'
        else: return 'undef'

    def status_merge_stdby_up(s):
        if s == 'up': return 'stdby up with up'
        elif s == 'down': return 'stdby up with down'
        elif s == 'stdby down': return 'warn'
        elif s == 'stdby up': return 'stdby up'
        elif s == 'stdby up with up': return 'stdby up with up'
        elif s == 'stdby up with down': return 'stdby up with down'
        elif s in ['undef', 'n/a']: return 'stdby up'
        else: return 'undef'

    def status_merge_stdby_down(s):
        if s == 'up': return 'stdby down with up'
        elif s == 'down': return 'stdby down'
        elif s == 'stdby down': return 'stdby down'
        elif s == 'stdby up': return 'warn'
        elif s == 'stdby up with up': return 'warn'
        elif s == 'stdby up with down': return 'warn'
        elif s in ['undef', 'n/a']: return 'stdby down'
        else: return 'undef'

    s = 'undef'
    for sn in ['mon_containerstatus',
              'mon_ipstatus',
              'mon_fsstatus',
              'mon_appstatus',
              'mon_diskstatus']:
        if h[sn] in ['warn', 'todo']: return 'warn'
        elif h[sn] == 'undef': return 'undef'
        elif h[sn] == 'n/a':
            if s == 'undef': s = 'n/a'
            else: continue
        elif h[sn] == 'up': s = status_merge_up(s)
        elif h[sn] == 'down': s = status_merge_down(s)
        elif h[sn] == 'stdby up': s = status_merge_stdby_up(s)
        elif h[sn] == 'stdby down': s = status_merge_stdby_down(s)
        else: return 'undef'
    if s == 'stdby up with up':
        s = 'up'
    elif s == 'stdby up with down':
        s = 'stdby up'
    return s

def svc_status_update(svcname):
    """ avail and overall status can be:
        up, down, stdby up, stdby down, warn, undef
    """
    q = db.svcmon.mon_svcname == svcname
    rows = db(q).select(db.svcmon.mon_overallstatus,
                        db.svcmon.mon_availstatus,
                        db.svcmon.mon_updated,
                        db.svcmon.mon_svctype,
                        db.svcmon.mon_frozen)

    tlim = datetime.datetime.now() - datetime.timedelta(minutes=15)
    ostatus_l = [r.mon_overallstatus for r in rows if r.mon_updated > tlim]
    astatus_l = [r.mon_availstatus for r in rows if r.mon_updated > tlim]
    n_trusted_nodes = len(ostatus_l)
    n_nodes = len(rows)
    ostatus_l = set(ostatus_l)
    astatus_l = set(astatus_l)

    ostatus = 'undef'
    astatus = 'undef'

    if 'up' in astatus_l:
        astatus = 'up'
    elif n_trusted_nodes == 0:
        astatus = 'undef'
    else:
        if astatus_l == set(['n/a']):
            astatus = 'n/a'
        elif 'warn' in astatus_l:
            astatus = 'warn'
        else:
            astatus = 'down'

    if n_trusted_nodes < n_nodes:
        ostatus = 'warn'
    elif n_trusted_nodes == 0:
        ostatus = 'undef'
    elif 'warn' in ostatus_l or \
         'stdby down' in ostatus_l or \
         'undef' in ostatus_l:
        ostatus = 'warn'
    elif set(['up']) == ostatus_l or \
         set(['up', 'down']) == ostatus_l or \
         set(['up', 'stdby up']) == ostatus_l or \
         set(['up', 'down', 'stdby up']) == ostatus_l or \
         set(['up', 'down', 'stdby up', 'n/a']) == ostatus_l:
        ostatus = 'up'
    elif set(['down']) == ostatus_l or \
         set(['down', 'stdby up']) == ostatus_l or \
         set(['down', 'stdby up', 'n/a']) == ostatus_l:
        ostatus = 'down'
    else:
        ostatus = 'undef'

    svc_log_update(svcname, astatus)
    update_dash_service_unavailable(svcname, rows[0].mon_svctype, astatus)
    update_dash_service_available_but_degraded(svcname, rows[0].mon_svctype, astatus, ostatus)

    db(db.services.svc_name==svcname).update(
      svc_status=ostatus,
      svc_availstatus=astatus)

def svc_log_update(svcname, astatus):
    q = db.services_log.svc_name == svcname
    o = ~db.services_log.id
    rows = db(q).select(orderby=o, limitby=(0,1))
    end = datetime.datetime.now()
    if len(rows) == 1:
        prev = rows[0]
        if prev.svc_availstatus == astatus:
            id = prev.id
            q = db.services_log.id == id
            db(q).update(svc_end=end)
        else:
            db.services_log.insert(svc_name=svcname,
                                   svc_begin=prev.svc_end,
                                   svc_end=end,
                                   svc_availstatus=astatus)
    else:
        db.services_log.insert(svc_name=svcname,
                               svc_begin=end,
                               svc_end=end,
                               svc_availstatus=astatus)

def __svcmon_update(vars, vals):
    # don't trust the server's time
    h = {}
    for a,b in zip(vars, vals):
        if a == 'mon_updated':
            continue
        h[a] = b
    now = datetime.datetime.now()
    tmo = now - datetime.timedelta(minutes=15)
    h['mon_updated'] = now
    if 'mon_hbstatus' not in h:
        h['mon_hbstatus'] = 'undef'
    if 'mon_availstatus' not in h:
        h['mon_availstatus'] = compute_availstatus(h)
    generic_insert('svcmon', h.keys(), h.values())
    svc_status_update(h['mon_svcname'])
    update_dash_service_frozen(h['mon_svcname'], h['mon_nodname'], h['mon_svctype'], h['mon_frozen'])
    update_dash_service_not_on_primary(h['mon_svcname'], h['mon_nodname'], h['mon_svctype'], h['mon_availstatus'])
    update_dash_svcmon_not_updated(h['mon_svcname'], h['mon_nodname'])
    update_dash_flex_instances_started(h['mon_svcname'])
    update_dash_flex_cpu(h['mon_svcname'])

    query = db.svcmon_log.mon_svcname==h['mon_svcname']
    query &= db.svcmon_log.mon_nodname==h['mon_nodname']
    last = db(query).select(orderby=~db.svcmon_log.id, limitby=(0,1))
    if len(last) == 0:
        _vars = ['mon_begin',
                 'mon_end',
                 'mon_svcname',
                 'mon_nodname',
                 'mon_overallstatus',
                 'mon_availstatus',
                 'mon_ipstatus',
                 'mon_fsstatus',
                 'mon_diskstatus',
                 'mon_containerstatus',
                 'mon_appstatus',
                 'mon_syncstatus',
                 'mon_hbstatus']
        _vals = [h['mon_updated'],
                 h['mon_updated'],
                 h['mon_svcname'],
                 h['mon_nodname'],
                 h['mon_overallstatus'],
                 h['mon_availstatus'],
                 h['mon_ipstatus'],
                 h['mon_fsstatus'],
                 h['mon_diskstatus'],
                 h['mon_containerstatus'],
                 h['mon_appstatus'],
                 h['mon_syncstatus'],
                 h['mon_hbstatus']]
        generic_insert('svcmon_log', _vars, _vals)
        if h['mon_overallstatus'] == 'warn':
            level = "warning"
        else:
            level = "info"
        _log("service.status",
             "service '%(svc)s' state initialized on '%(node)s': avail(%(a1)s=>%(a2)s) overall(%(o1)s=>%(o2)s)",
             dict(
               svc=h['mon_svcname'],
               node=h['mon_nodname'],
               a1="none",
               a2=h['mon_availstatus'],
               o1="none",
               o2=h['mon_overallstatus']),
             svcname=h['mon_svcname'],
             nodename=h['mon_nodname'],
             level=level)
    elif last[0].mon_end < tmo:
        _vars = ['mon_begin',
                 'mon_end',
                 'mon_svcname',
                 'mon_nodname',
                 'mon_overallstatus',
                 'mon_availstatus',
                 'mon_ipstatus',
                 'mon_fsstatus',
                 'mon_diskstatus',
                 'mon_containerstatus',
                 'mon_appstatus',
                 'mon_syncstatus',
                 'mon_hbstatus']
        _vals = [last[0].mon_end,
                 h['mon_updated'],
                 h['mon_svcname'],
                 h['mon_nodname'],
                 "undef",
                 "undef",
                 "undef",
                 "undef",
                 "undef",
                 "undef",
                 "undef",
                 "undef",
                 "undef"]
        generic_insert('svcmon_log', _vars, _vals)
        _vars = ['mon_begin',
                 'mon_end',
                 'mon_svcname',
                 'mon_nodname',
                 'mon_overallstatus',
                 'mon_availstatus',
                 'mon_ipstatus',
                 'mon_fsstatus',
                 'mon_diskstatus',
                 'mon_containerstatus',
                 'mon_appstatus',
                 'mon_syncstatus',
                 'mon_hbstatus']
        _vals = [h['mon_updated'],
                 h['mon_updated'],
                 h['mon_svcname'],
                 h['mon_nodname'],
                 h['mon_overallstatus'],
                 h['mon_availstatus'],
                 h['mon_ipstatus'],
                 h['mon_fsstatus'],
                 h['mon_diskstatus'],
                 h['mon_containerstatus'],
                 h['mon_appstatus'],
                 h['mon_hbstatus'],
                 h['mon_syncstatus']]
        generic_insert('svcmon_log', _vars, _vals)
        if h['mon_overallstatus'] == 'warn':
            level = "warning"
        else:
            level = "info"
        _log("service.status",
             "service '%(svc)s' state changed on '%(node)s': avail(%(a1)s=>%(a2)s) overall(%(o1)s=>%(o2)s)",
             dict(
               svc=h['mon_svcname'],
               node=h['mon_nodname'],
               a1="undef",
               a2=h['mon_availstatus'],
               o1="undef",
               o2=h['mon_overallstatus']),
             svcname=h['mon_svcname'],
             nodename=h['mon_nodname'],
             level=level)
    elif h['mon_overallstatus'] != last[0].mon_overallstatus or \
         h['mon_availstatus'] != last[0].mon_availstatus:
        _vars = ['mon_begin',
                 'mon_end',
                 'mon_svcname',
                 'mon_nodname',
                 'mon_overallstatus',
                 'mon_availstatus',
                 'mon_ipstatus',
                 'mon_fsstatus',
                 'mon_diskstatus',
                 'mon_containerstatus',
                 'mon_appstatus',
                 'mon_syncstatus',
                 'mon_hbstatus']
        _vals = [h['mon_updated'],
                 h['mon_updated'],
                 h['mon_svcname'],
                 h['mon_nodname'],
                 h['mon_overallstatus'],
                 h['mon_availstatus'],
                 h['mon_ipstatus'],
                 h['mon_fsstatus'],
                 h['mon_diskstatus'],
                 h['mon_containerstatus'],
                 h['mon_appstatus'],
                 h['mon_syncstatus'],
                 h['mon_hbstatus']]
        generic_insert('svcmon_log', _vars, _vals)
        db(db.svcmon_log.id==last[0].id).update(mon_end=h['mon_updated'])
        if h['mon_overallstatus'] == 'warn':
            level = "warning"
        else:
            level = "info"
        _log("service.status",
             "service '%(svc)s' state changed on '%(node)s': avail(%(a1)s=>%(a2)s) overall(%(o1)s=>%(o2)s)",
             dict(
               svc=h['mon_svcname'],
               node=h['mon_nodname'],
               a1=last[0].mon_availstatus,
               a2=h['mon_availstatus'],
               o1=last[0].mon_overallstatus,
               o2=h['mon_overallstatus']),
             svcname=h['mon_svcname'],
             nodename=h['mon_nodname'],
             level=level)
    else:
        db(db.svcmon_log.id==last[0].id).update(mon_end=h['mon_updated'])

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

def update_thresholds_batch(rows=None):
    # maintenance batch
    if rows is None:
        q = db.checks_live.id > 0
        rows = db(q).select()
    for row in rows:
        update_thresholds(row)

def update_thresholds(row):
    # try to find most precise settings
    t = get_settings(row)
    if t is not None:
        db(db.checks_live.id==row.id).update(chk_low=t[0], chk_high=t[1], chk_threshold_provider=t[2])
        return

    # try to find filter-match thresholds
    t = get_filters(row)
    if t is not None:
        db(db.checks_live.id==row.id).update(chk_low=t[0], chk_high=t[1], chk_threshold_provider=t[2])
        return

    # try to find least precise settings (ie defaults)
    t = get_defaults(row)
    if t is not None:
        db(db.checks_live.id==row.id).update(chk_low=t[0], chk_high=t[1], chk_threshold_provider=t[2])
        return

    # no threshold found, leave as-is
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

#
# Dashboard updates
#
#   Used by background feed dequeue process for periodic dashboard alerts
#
def cron_dash_service_not_updated():
    sql = """insert ignore
             into dashboard
               select
                 NULL,
                 "service configuration not updated",
                 svc_name,
                 "",
                 0,
                 "",
                 "",
                 updated,
                 ""
               from services
               where updated < date_sub(now(), interval 25 hour)
          """
    db.executesql(sql)

def cron_dash_svcmon_not_updated():
    sql = """insert ignore
             into dashboard
               select
                 NULL,
                 "service status not updated",
                 mon_svcname,
                 mon_nodname,
                 if(mon_svctype="PRD", 1, 0),
                 "",
                 "",
                 mon_updated,
                 ""
               from svcmon
               where mon_updated < date_sub(now(), interval 15 minute)
          """
    db.executesql(sql)

def cron_dash_node_not_updated():
    sql = """insert ignore
             into dashboard
               select
                 NULL,
                 "node information not updated",
                 "",
                 nodename,
                 0,
                 "",
                 "",
                 updated,
                 ""
               from nodes
               where updated < date_sub(now(), interval 25 hour)
          """
    db.executesql(sql)

def cron_dash_node_without_asset():
    sql = """insert ignore
             into dashboard
               select
                 NULL,
                 "node without asset information",
                 "",
                 mon_nodname,
                 0,
                 "",
                 "",
                 now(),
                 ""
               from svcmon
               where
                 mon_nodname not in (
                   select nodename from nodes
                 )
          """
    db.executesql(sql)

def cron_dash_node_beyond_warranty_date():
    sql = """insert ignore
             into dashboard
               select
                 NULL,
                 "node warranty expired",
                 "",
                 nodename,
                 1,
                 "",
                 "",
                 now(),
                 ""
               from nodes
               where
                 warranty_end is not NULL and
                 warranty_end != "0000-00-00 00:00:00" and
                 warranty_end < now()
          """
    db.executesql(sql)

def cron_dash_node_near_warranty_date():
    sql = """insert ignore
             into dashboard
               select
                 NULL,
                 "node close to warranty end",
                 "",
                 nodename,
                 0,
                 "",
                 "",
                 now(),
                 ""
               from nodes
               where
                 warranty_end is not NULL and
                 warranty_end != "0000-00-00 00:00:00" and
                 warranty_end > date_sub(now(), interval 30 day) and
                 warranty_end < now()
          """
    db.executesql(sql)

def cron_dash_node_without_warranty_date():
    sql = """insert ignore
             into dashboard
               select
                 NULL,
                 "node without warranty end date",
                 "",
                 nodename,
                 0,
                 "",
                 "",
                 now(),
                 ""
               from nodes
               where
                 warranty_end is NULL or
                 warranty_end = "0000-00-00 00:00:00"
          """
    db.executesql(sql)

def cron_dash_checks_not_updated():
    sql = """insert ignore into dashboard
               select
                 NULL,
                 "check value not updated",
                 "",
                 c.chk_nodename,
                 if(n.environnement="PRD", 1, 0),
                 "%(t)s:%(i)s",
                 concat('{"i":"', chk_instance, '", "t":"', chk_type, '"}'),
                 chk_updated,
                 md5(concat('{"i":"', chk_instance, '", "t":"', chk_type, '"}'))
               from checks_live c
                 join nodes n on c.chk_nodename=n.nodename
               where
                 chk_updated < date_sub(now(), interval 15 minute)"""
    db.executesql(sql)

def cron_dash_app_without_responsible():
    sql = """insert ignore into dashboard
               select
                 NULL,
                 "application code without responsible",
                 "",
                 "",
                 2,
                 "%(a)s",
                 concat('{"a":"', app, '"}'),
                 now(),
                 md5(concat('{"a":"', app, '"}'))
               from v_apps
               where
                 roles is NULL
          """
    db.executesql(sql)

def cron_dash_obs_hw_without_alert():
    cron_dash_obs_without('hw', 'alert')

def cron_dash_obs_os_without_alert():
    cron_dash_obs_without('os', 'alert')

def cron_dash_obs_hw_without_warn():
    cron_dash_obs_without('hw', 'warn')

def cron_dash_obs_os_without_warn():
    cron_dash_obs_without('os', 'warn')

def cron_dash_obs_without(t, a):
    if t == "hw":
        tl = "hardware"
    else:
        tl = t
    if a == "warn":
        al = "warning"
    else:
        al = a
    sql = """insert ignore into dashboard
               select
                 NULL,
                 "%(tl)s obsolescence %(al)s date not set",
                 "",
                 "",
                 0,
                 "%(t)s: %%(o)s",
                 concat('{"o": "', o.obs_name, '"}'),
                 now(),
                 md5(concat('{"o": "', o.obs_name, '"}'))
               from obsolescence o
                 join nodes n on
                   o.obs_name = n.model or
                   o.obs_name = concat_ws(' ',n.os_name,n.os_vendor,n.os_release,n.os_update)
               where
                 o.obs_type = "%(t)s" and
                 (
                   o.obs_%(a)s_date is NULL or
                   o.obs_%(a)s_date = "0000-00-00 00:00:00"
                 )
          """%dict(t=t, tl=tl, a=a, al=al)
    db.executesql(sql)

def cron_dash_obs_os_alert():
    sql = """insert ignore into dashboard
               select
                 NULL,
                 "os obsolescence alert",
                 "",
                 n.nodename,
                 1,
                 "%(o)s obsolete since %(a)s",
                 concat('{"a": "', o.obs_alert_date,
                        '", "o": "', o.obs_name,
                        '"}'),
                 now(),
                 ""
               from obsolescence o
                 join nodes n on
                   o.obs_name = concat_ws(' ',n.os_name,n.os_vendor,n.os_release,n.os_update)
               where
                 o.obs_alert_date is not NULL and
                 o.obs_alert_date != "0000-00-00 00:00:00" and
                 o.obs_alert_date < now() and
                 o.obs_type = "os"
          """
    db.executesql(sql)

def cron_dash_obs_os_warn():
    sql = """insert ignore into dashboard
               select
                 NULL,
                 "os obsolescence warning",
                 "",
                 n.nodename,
                 0,
                 "%(o)s warning since %(a)s",
                 concat('{"a": "', o.obs_warn_date,
                        '", "o": "', o.obs_name,
                        '"}'),
                 now(),
                 ""
               from obsolescence o
                 join nodes n on
                   o.obs_name = concat_ws(' ',n.os_name,n.os_vendor,n.os_release,n.os_update)
               where
                 o.obs_alert_date is not NULL and
                 o.obs_alert_date != "0000-00-00 00:00:00" and
                 o.obs_warn_date < now() and
                 o.obs_alert_date > now() and
                 o.obs_type = "os"
          """
    db.executesql(sql)

def cron_dash_obs_hw_alert():
    sql = """insert ignore into dashboard
               select
                 NULL,
                 "hardware obsolescence warning",
                 "",
                 n.nodename,
                 1,
                 "%(o)s obsolete since %(a)s",
                 concat('{"a": "', o.obs_alert_date,
                        '", "o": "', o.obs_name,
                        '"}'),
                 now(),
                 ""
               from obsolescence o
                 join nodes n on
                   o.obs_name = n.model
               where
                 o.obs_alert_date is not NULL and
                 o.obs_alert_date != "0000-00-00 00:00:00" and
                 o.obs_alert_date < now() and
                 o.obs_type = "hw"
          """
    db.executesql(sql)

def cron_dash_obs_hw_warn():
    sql = """insert ignore into dashboard
               select
                 NULL,
                 "hardware obsolescence warning",
                 "",
                 n.nodename,
                 0,
                 "%(o)s warning since %(a)s",
                 concat('{"a": "', o.obs_warn_date,
                        '", "o": "', o.obs_name,
                        '"}'),
                 now(),
                 ""
               from obsolescence o
                 join nodes n on
                   o.obs_name = n.model
               where
                 o.obs_alert_date is not NULL and
                 o.obs_alert_date != "0000-00-00 00:00:00" and
                 o.obs_warn_date < now() and
                 o.obs_alert_date > now() and
                 o.obs_type = "hw"
          """
    db.executesql(sql)

#
# Dashboard updates
#
#   Used by xmlrpc processors for event based dashboard alerts
#
def update_dash_node_beyond_warranty_end(nodename):
    sql = """delete from dashboard
               where
                 dash_nodename in (
                   select nodename
                   from nodes
                   where
                     nodename="%(nodename)s" and
                     warranty_end is not NULL and
                     warranty_end != "0000-00-00 00:00:00" and
                     warranty_end < now()
                 ) and
                 dash_type = "node warranty expired"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)

def update_dash_node_near_warranty_end(nodename):
    sql = """delete from dashboard
               where
                 dash_nodename in (
                   select nodename
                   from nodes
                   where
                     nodename="%(nodename)s" and
                     warranty_end is not NULL and
                     warranty_end != "0000-00-00 00:00:00" and
                     warranty_end > now() and
                     warranty_end < date_sub(now(), interval 30 day)
                 ) and
                 dash_type = "node warranty expired"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)

def update_dash_node_without_asset(nodename):
    sql = """delete from dashboard
               where
                 dash_nodename in (
                   select nodename
                   from nodes
                   where
                     nodename="%(nodename)s"
                 ) and
                 dash_type = "node without asset information"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)

def update_dash_node_without_warranty_end(nodename):
    sql = """delete from dashboard
               where
                 dash_nodename in (
                   select nodename
                   from nodes
                   where
                     nodename="%(nodename)s" and
                     warranty_end != "0000-00-00 00:00:00" and
                     warranty_end is not NULL
                 ) and
                 dash_type = "node without warranty end date"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)

def update_dash_service_not_updated(svcname):
    sql = """delete from dashboard
               where
                 dash_svcname = "%(svcname)s" and
                 dash_type = "service configuration not updated"
          """%dict(svcname=svcname)
    rows = db.executesql(sql)

def update_dash_svcmon_not_updated(svcname, nodename):
    sql = """delete from dashboard
               where
                 dash_svcname = "%(svcname)s" and
                 dash_nodename = "%(nodename)s" and
                 dash_type = "service status not updated"
          """%dict(svcname=svcname, nodename=nodename)
    rows = db.executesql(sql)

def update_dash_node_not_updated(nodename):
    sql = """delete from dashboard
               where
                 dash_nodename = "%(nodename)s" and
                 dash_type = "node information not updated"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)

def update_dash_pkgdiff(nodename):
    nodename = nodename.strip("'")
    q = db.svcmon.mon_nodname == nodename
    q &= db.svcmon.mon_updated > datetime.datetime.now() - datetime.timedelta(minutes=20)
    for row in db(q).select(db.svcmon.mon_svcname,
                            db.svcmon.mon_svctype):
        svcname = row.mon_svcname

        sql = """delete from dashboard
                   where
                     dash_svcname = "%(svcname)s" and
                     dash_type = "package differences in cluster"
              """%dict(svcname=svcname)
        rows = db.executesql(sql)

        q = db.svcmon.mon_svcname == svcname
        q &= db.svcmon.mon_updated > datetime.datetime.now() - datetime.timedelta(minutes=20)
        nodes = map(lambda x: repr(x.mon_nodname),
                    db(q).select(db.svcmon.mon_nodname))
        n = len(nodes)

        sql = """select count(id) from (
                   select
                     id,
                     count(pkg_nodename) as c
                   from packages
                   where
                     pkg_nodename in (%(nodes)s)
                   group by
                     pkg_name,
                     pkg_version,
                     pkg_arch
                  ) as t
                  where
                    t.c!=%(n)s
              """%dict(nodes=','.join(nodes), n=n)

        rows = db.executesql(sql)

        if rows[0][0] == 0:
            continue

        if row.mon_svctype == 'PRD':
            sev = 1
        else:
            sev = 0

        sql = """insert ignore into dashboard
                 set
                   dash_type="package differences in cluster",
                   dash_svcname="%(svcname)s",
                   dash_nodename="",
                   dash_severity=%(sev)d,
                   dash_fmt="%%(n)s package differences in cluster %%(nodes)s",
                   dash_dict='{"n": %(n)d, "nodes": "%(nodes)s"}',
                   dash_dict_md5=md5('{"n": %(n)d, "nodes": "%(nodes)s"}'),
                   dash_created="%(now)s"
              """%dict(svcname=svcname,
                       sev=sev,
                       now=str(datetime.datetime.now()),
                       n=rows[0][0],
                       nodes=','.join(nodes).replace("'", ""))

        with open("/tmp/bar", "a") as f:
            f.write(sql)

        rows = db.executesql(sql)

def update_dash_flex_cpu(svcname):
    sql = """delete from dashboard
               where
                 dash_svcname = "%(svcname)s" and
                 dash_type = "flex error" and
                 dash_fmt like "%%average cpu usage%%"
          """%dict(svcname=svcname)
    rows = db.executesql(sql)

    sql = """select svc_type from services
             where
               svc_name="%(svcname)s"
          """%dict(svcname=svcname)
    rows = db.executesql(sql)

    if len(rows) == 1 and rows[0][0] == 'PRD':
        sev = 2
    else:
        sev = 1

    sql = """insert ignore into dashboard
               select
                 NULL,
                 "flex error",
                 "%(svcname)s",
                 "",
                 %(sev)d,
                 "%%(n)d average cpu usage. thresholds: %%(cmin)d - %%(cmax)d",
                 concat('{"n": "', t.up,
                        ', "cmin": ', t.svc_flex_cpu_low_threshold,
                        ', "cmax": ', t.svc_flex_cpu_high_threshold,
                        '}'),
                 now(),
                 md5(concat('{"n": "', t.cpu,
                        ', "cmin": ', t.svc_flex_cpu_low_threshold,
                        ', "cmax": ', t.svc_flex_cpu_high_threshold,
                        '}'))
               from (
                 select *
                 from v_flex_status
                 where
                   cpu > svc_flex_cpu_high_threshold or
                   (
                      svc_name="%(svcname)s" and
                      up > 1 and
                      cpu < svc_flex_cpu_low_threshold
                   )
               ) t
          """%dict(svcname=svcname,
                   sev=sev,
                  )
    db.executesql(sql)

def update_dash_flex_instances_started(svcname):
    sql = """delete from dashboard
               where
                 dash_svcname = "%(svcname)s" and
                 dash_type = "flex error" and
                 dash_fmt like "%%instances started%%"
          """%dict(svcname=svcname)
    rows = db.executesql(sql)

    sql = """select svc_type from services
             where
               svc_name="%(svcname)s"
          """%dict(svcname=svcname)
    rows = db.executesql(sql)

    if len(rows) == 1 and rows[0][0] == 'PRD':
        sev = 2
    else:
        sev = 1

    sql = """insert ignore into dashboard
               select
                 NULL,
                 "flex error",
                 "%(svcname)s",
                 "",
                 %(sev)d,
                 "%%(n)d instances started. thresholds: %%(smin)d - %%(smax)d",
                 concat('{"n": "', t.up,
                        ', "smin": ', t.svc_flex_min_nodes,
                        ', "smax": ', t.svc_flex_max_nodes,
                        '}'),
                 now(),
                 md5(concat('{"n": "', t.up,
                        ', "smin": ', t.svc_flex_min_nodes,
                        ', "smax": ', t.svc_flex_max_nodes,
                        '}'))
               from (
                 select *
                 from v_flex_status
                 where
                   up < svc_flex_min_nodes or
                   (
                      svc_name="%(svcname)s" and
                      svc_flex_max_nodes > 0 and
                      up > svc_flex_max_nodes
                   )
               ) t
          """%dict(svcname=svcname,
                   sev=sev,
                  )
    db.executesql(sql)

def update_dash_checks(nodename):
    nodename = nodename.strip("'")
    sql = """delete from dashboard
               where
                 dash_nodename = "%(nodename)s" and
                 dash_type = "check out of bounds" or
                 dash_type = "check value not updated"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)

    sql = """select environnement from nodes
             where
               nodename="%(nodename)s"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)

    if len(rows) == 1 and rows[0][0] == 'PRD':
        sev = 1
    else:
        sev = 0

    sql = """insert ignore into dashboard
               select
                 NULL,
                 "check out of bounds",
                 t.svcname,
                 "%(nodename)s",
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
                        '}'))
               from (
                 select
                   chk_svcname as svcname,
                   chk_type as ctype,
                   chk_instance as inst,
                   chk_threshold_provider as ttype,
                   chk_value as val,
                   chk_low as min,
                   chk_high as max
                 from checks_live
                 where
                   chk_value < chk_low or
                   chk_value > chk_high
               ) t
          """%dict(nodename=nodename,
                   sev=sev,
                   now=str(datetime.datetime.now()),
                  )
    db.executesql(sql)

def update_dash_netdev_errors(nodename):
    nodename = nodename.strip("'")
    sql = """select avg(rxerrps+txerrps+collps+rxdropps+rxdropps)
               from stats_netdev_err
               where
                 nodename = "%(nodename)s" and
                 date > "%(date)s"
          """%dict(nodename=nodename,
                   date=str(datetime.datetime.now()-datetime.timedelta(days=1)),
                  )
    rows = db.executesql(sql)

    if len(rows) > 0 and rows[0][0] > 0:
        sql = """select environnement from nodes
                 where
                   nodename="%(nodename)s"
              """%dict(nodename=nodename)
        rows = db.executesql(sql)

        if len(rows) == 1 and rows[0][0] == 'PRD':
            sev = 1
        else:
            sev = 0

        sql = """insert into dashboard
                 set
                   dash_type="network device errors in the last day",
                   dash_svcname="",
                   dash_nodename="%(nodename)s",
                   dash_severity=%(sev)d,
                   dash_fmt="%(err)s errors per second average",
                   dash_dict='{"err": "%(err)d"}',
                   dash_created="%(now)s"
                 on duplicate key update
                   dash_severity=%(sev)d,
                   dash_fmt="%(err)s errors per second average",
                   dash_dict='{"err": "%(err)d"}',
                   dash_created="%(now)s"
              """%dict(nodename=nodename,
                       sev=sev,
                       now=str(datetime.datetime.now()),
                       err=rows[0][0])
    else:
        sql = """delete from dashboard
                 where
                   dash_type="network device errors in the last day" and
                   dash_nodename="%(nodename)s"
              """%dict(nodename=nodename)
    db.executesql(sql)

def update_dash_action_errors(svc_name, nodename):
    svc_name = svc_name.strip("'")
    nodename = nodename.strip("'")
    sql = """select e.err, s.svc_type from b_action_errors e
             join services s on e.svcname=s.svc_name
             where
               svcname="%(svcname)s" and
               nodename="%(nodename)s"
          """%dict(svcname=svc_name, nodename=nodename)
    rows = db.executesql(sql)

    if len(rows) == 1:
        if rows[0][1] == 'PRD':
            sev = 2
        else:
            sev = 1
        sql = """insert into dashboard
                 set
                   dash_type="action errors",
                   dash_svcname="%(svcname)s",
                   dash_nodename="%(nodename)s",
                   dash_severity=%(sev)d,
                   dash_fmt="%(err)s action errors",
                   dash_dict='{"err": "%(err)d"}',
                   dash_created="%(now)s"
                 on duplicate key update
                   dash_severity=%(sev)d,
                   dash_fmt="%(err)s action errors",
                   dash_dict='{"err": "%(err)d"}',
                   dash_created="%(now)s"
              """%dict(svcname=svc_name,
                       nodename=nodename,
                       sev=sev,
                       now=str(datetime.datetime.now()),
                       err=rows[0][0])
    else:
        sql = """delete from dashboard
                 where
                   dash_type="action errors" and
                   dash_svcname="%(svcname)s" and
                   dash_nodename="%(nodename)s"
              """%dict(svcname=svc_name,
                       nodename=nodename)
    db.executesql(sql)

def update_dash_service_available_but_degraded(svc_name, svc_type, svc_availstatus, svc_status):
    if svc_type == 'PRD':
        sev = 1
    else:
        sev = 0
    if svc_availstatus == "up" and svc_status != "up":
        sql = """delete from dashboard
                 where
                   dash_type="service available but degraded" and
                   dash_dict!='{"s": "%s"}' and
                   dash_svcname="%s"
              """%(svc_name,svc_status)
        db.executesql(sql)
        sql = """insert ignore into dashboard
                 set
                   dash_type="service available but degraded",
                   dash_svcname="%(svcname)s",
                   dash_nodename="",
                   dash_severity=%(sev)d,
                   dash_fmt="current overall status: %%(s)s",
                   dash_dict='{"s": "%(status)s"}',
                   dash_created=now()
              """%dict(svcname=svc_name,
                       sev=sev,
                       status=svc_status)
        db.executesql(sql)
    else:
        sql = """delete from dashboard
                 where
                   dash_type="service available but degraded" and
                   dash_svcname="%s"
              """%svc_name
        db.executesql(sql)

def update_dash_service_unavailable(svc_name, svc_type, svc_availstatus):
    if svc_type == 'PRD':
        sev = 2
    else:
        sev = 1
    if svc_availstatus == "up":
        sql = """delete from dashboard
                 where
                   dash_type="service unavailable" and
                   dash_svcname="%s"
              """%svc_name
        db.executesql(sql)
    else:
        sql = """delete from dashboard
                 where
                   dash_type="service unavailable" and
                   dash_svcname="%s" and
                   dash_dict!='{"s": "%s"}'
              """%(svc_name,svc_availstatus)
        db.executesql(sql)
        sql = """insert ignore into dashboard
                 set
                   dash_type="service unavailable",
                   dash_svcname="%(svcname)s",
                   dash_nodename="",
                   dash_severity=%(sev)d,
                   dash_fmt="current availability status: %%(s)s",
                   dash_dict='{"s": "%(status)s"}',
                   dash_created="%(now)s"
              """%dict(svcname=svc_name,
                       sev=sev,
                       now=str(datetime.datetime.now()),
                       status=svc_availstatus)
        db.executesql(sql)

def update_dash_service_frozen(svc_name, nodename, svc_type, frozen):
    if svc_type == 'PRD':
        sev = 1
    else:
        sev = 0
    if frozen == "0":
        sql = """delete from dashboard
                 where
                   dash_type="service frozen" and
                   dash_svcname="%s"
              """%svc_name
    else:
        sql = """insert ignore into dashboard
                 set
                   dash_type="service frozen",
                   dash_svcname="%(svcname)s",
                   dash_nodename="%(nodename)s",
                   dash_severity=%(sev)d,
                   dash_fmt="",
                   dash_dict="",
                   dash_created=now()
              """%dict(svcname=svc_name,
                       nodename=nodename,
                       sev=sev,
                      )
    db.executesql(sql)

def update_dash_service_not_on_primary(svc_name, nodename, svc_type, availstatus):
    if svc_type == 'PRD':
        sev = 1
    else:
        sev = 0

    q = db.services.svc_name == svc_name
    rows = db(q).select(db.services.svc_autostart,
                        db.services.svc_availstatus)

    if len(rows) == 0:
        return

    if rows[0].svc_autostart != nodename or availstatus == "up" or rows[0].svc_availstatus != "up":
        sql = """delete from dashboard
                 where
                   dash_type="service not started on primary node" and
                   dash_svcname="%s" and
                   dash_nodename="%s"
              """%(svc_name,nodename)
        db.executesql(sql)
        return

    sql = """insert ignore into dashboard
             set
               dash_type="service not started on primary node",
               dash_svcname="%(svcname)s",
               dash_nodename="%(nodename)s",
               dash_severity=%(sev)d,
               dash_fmt="",
               dash_dict="",
               dash_created=now()
          """%dict(svcname=svc_name,
                   nodename=nodename,
                   sev=sev,
                  )
    db.executesql(sql)

#
# Feed enqueue/dequeue
#
#   Feed processors can be heavy and suturate the httpd server process/thread
#   pool. Enqueue fast to release the client, then asynchronously dequeue
#   from a single background process.
#
def feed_enqueue(f, *args):
    import cPickle
    db.feed_queue.insert(q_fn=f, q_args=cPickle.dumps(args))

def dash_crons2():
    # ~1/j
    cron_dash_obs_os_alert()
    cron_dash_obs_os_warn()
    cron_dash_obs_hw_alert()
    cron_dash_obs_hw_warn()
    cron_dash_obs_os_without_alert()
    cron_dash_obs_os_without_warn()
    cron_dash_obs_hw_without_alert()
    cron_dash_obs_hw_without_warn()
    cron_dash_node_without_warranty_date()
    cron_dash_node_near_warranty_date()
    cron_dash_node_beyond_warranty_date()

def dash_crons1():
    # ~1/h
    cron_dash_checks_not_updated()
    cron_dash_service_not_updated()
    cron_dash_app_without_responsible()
    cron_dash_node_not_updated()
    cron_dash_node_without_asset()

def dash_crons0():
    # ~1/min
    cron_dash_svcmon_not_updated()

def feed_dequeue():
    """ launched as a background process
    """
    import time
    import cPickle

    class QueueStats(object):
        def __init__(self):
            self.reset_stats()

        def __str__(self):
            s = "feed queue stats since %s\n"%str(self.start)
            for fn in self.s:
                s += "%20s %10d %10f\n"%(fn, self.count(fn), self.avg(fn))
            return s

        def dbdump(self):
            if len(self.s) == 0:
               return
            now = datetime.datetime.now()
            sql = """truncate table feed_queue_stats"""
            db.executesql(sql)
            sql = """insert into feed_queue_stats (q_start, q_end, q_fn, q_count, q_avg) values """
            values = []
            for fn in self.s:
                values.append("""("%s", "%s", "%s", %d, %f)"""%(str(self.start), str(now), fn, self.count(fn), self.avg(fn)))
            sql += ','.join(values)
            print sql
            db.executesql(sql)

        def reset_stats(self):
            self.s = {}
            self.start = datetime.datetime.now()

        def begin(self, fn):
            self.fn = fn
            self.t = datetime.datetime.now()

        def end(self):
            elapsed = datetime.datetime.now() -self.t
            elapsed = elapsed.total_seconds()
            if self.fn not in self.s:
                self.s[self.fn] = {'count': 1, 'cumul': elapsed, 'avg': elapsed}
            else:
                self.s[self.fn]['count'] += 1
                self.s[self.fn]['cumul'] += elapsed
                print self.fn, self.s[self.fn]['count'], "+", elapsed, "cumul", self.s[self.fn]['cumul'], "avg", self.s[self.fn]['cumul']/self.s[self.fn]['count']

        def count(self, fn):
            if self.fn not in self.s:
                return 0
            return self.s[fn]['count']

        def avg(self, fn):
            if self.fn not in self.s:
                return 0
            return self.s[fn]['cumul']/self.s[fn]['count']

    n0 = 0
    n1 = 0
    n2 = 0
    stats = QueueStats()

    while True:
        n0 += 1
        n1 += 1
        n2 += 1

        if n0 == 90:
            n0 = 0
            dash_crons0()

        if n1 == 3600:
            n1 = 0
            dash_crons1()

        if n2 == 86400:
            n2 = 0
            dash_crons2()

        entries = db(db.feed_queue.id>0).select(limitby=(0,20))
        if len(entries) == 0:
            time.sleep(1)
            continue
        elif n1 % 5 == 0:
            # every 100 xmlrpc calls save stats
            stats.dbdump()

        for e in entries:
            try:
                if not e.q_fn in globals():
                    continue
                args = cPickle.loads(e.q_args)
                stats.begin(e.q_fn)
                globals()[e.q_fn](*args)
                stats.end()
                db(db.feed_queue.id==e.id).delete()
            except:
                print "Error: %s(%s)"%(e.q_fn, str(e.q_args))
                db(db.feed_queue.id==e.id).delete()
                import traceback
                traceback.print_exc()

