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
@service.xmlrpc
def delete_services(hostid=None):
    if hostid is None:
        return 0
    db(db.services.svc_hostid==hostid).delete()
    db.commit()
    return 0

@service.xmlrpc
def delete_service_list(hostid=None, svcnames=[]):
    if hostid is None or len(svcnames) == 0:
        return 0
    for svcname in svcnames:
        q = (db.services.svc_name==svcname)
        q &= (db.services.svc_hostid==hostid)
        db(q).delete()
        db.commit()
    return 0

@service.xmlrpc
def begin_action(vars, vals):
    sql="""insert delayed into SVCactions (%s) values (%s)""" % (','.join(vars), ','.join(vals))
    db.executesql(sql)
    db.commit()
    return 0

@service.xmlrpc
def res_action(vars, vals):
    upd = []
    for a, b in zip(vars, vals):
        upd.append("%s=%s" % (a, b))
    sql="""insert delayed into SVCactions (%s) values (%s)""" % (','.join(vars), ','.join(vals))
    db.executesql(sql)
    db.commit()
    return 0

@service.xmlrpc
def end_action(vars, vals):
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
    return 0

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

@service.xmlrpc
def update_service(vars, vals):
    if 'svc_hostid' not in vars:
        return
    if 'updated' not in vars:
        vars += ['updated']
        vals += [datetime.datetime.now()]
    generic_insert('services', vars, vals)

@service.xmlrpc
def push_checks(vars, vals):
    generic_insert('checks_live', vars, vals)

@service.xmlrpc
def update_asset(vars, vals):
    now = datetime.datetime.now()
    vars.append('updated')
    vals.append(now)
    generic_insert('nodes', vars, vals)

@service.xmlrpc
def res_action_batch(vars, vals):
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

@service.xmlrpc
def resmon_update(vars, vals):
    if len(vals) == 0:
        return
    if isinstance(vals[0], list):
        for v in vals:
            _resmon_update(vars, v)
    else:
        _resmon_update(vars, vals)

def _resmon_update(vars, vals):
    h = {}
    for a,b in zip(vars, vals[0]):
        h[a] = b
    if 'nodename' in h and 'svcname' in h:
        _resmon_clean(h['nodename'], h['svcname'])
    generic_insert('resmon', vars, vals)

@service.xmlrpc
def svcmon_update_combo(g_vars, g_vals, r_vars, r_vals):
    svcmon_update(g_vars, g_vals)
    resmon_update(r_vars, r_vals)

@service.xmlrpc
def register_disk(vars, vals):
    generic_insert('svcdisks', vars, vals)

@service.xmlrpc
def register_sync(vars, vals):
    pass

@service.xmlrpc
def register_ip(vars, vals):
    pass

@service.xmlrpc
def register_fs(vars, vals):
    pass

@service.xmlrpc
def insert_stats_fs_u(vars, vals):
    generic_insert('stats_fs_u', vars, vals)

@service.xmlrpc
def insert_stats_cpu(vars, vals):
    generic_insert('stats_cpu', vars, vals)

@service.xmlrpc
def insert_stats_mem_u(vars, vals):
    generic_insert('stats_mem_u', vars, vals)

@service.xmlrpc
def insert_stats_proc(vars, vals):
    generic_insert('stats_proc', vars, vals)

@service.xmlrpc
def insert_stats_swap(vars, vals):
    generic_insert('stats_swap', vars, vals)

@service.xmlrpc
def insert_stats_block(vars, vals):
    generic_insert('stats_block', vars, vals)

@service.xmlrpc
def insert_stats_blockdev(vars, vals):
    generic_insert('stats_blockdev', vars, vals)

@service.xmlrpc
def insert_stats_netdev(vars, vals):
    generic_insert('stats_netdev', vars, vals)

@service.xmlrpc
def insert_stats_netdev_err(vars, vals):
    generic_insert('stats_netdev_err', vars, vals)

@service.xmlrpc
def insert_stats(data):
    import cPickle
    h = cPickle.loads(data)
    for stat in h:
        vars, vals = h[stat]
        generic_insert('stats_'+stat, vars, vals)

@service.xmlrpc
def insert_pkg(vars, vals):
    generic_insert('packages', vars, vals)

@service.xmlrpc
def update_sym_xml(symid, vars, vals):
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

@service.xmlrpc
def delete_pkg(node):
    if node is None or node == '':
        return 0
    db(db.packages.pkg_nodename==node).delete()
    db.commit()

@service.xmlrpc
def insert_patch(vars, vals):
    generic_insert('patches', vars, vals)

@service.xmlrpc
def delete_patch(node):
    if node is None or node == '':
        return 0
    db(db.patches.patch_nodename==node).delete()
    db.commit()

@service.xmlrpc
def delete_syncs(svcname):
    pass

@service.xmlrpc
def delete_ips(svcname, node):
    pass

@service.xmlrpc
def delete_fss(svcname):
    pass

@service.xmlrpc
def delete_disks(svcname, node):
    if svcname is None or svcname == '':
        return 0
    db((db.svcdisks.disk_svcname==svcname)&(db.svcdisks.disk_nodename==node)).delete()
    db.commit()

@service.xmlrpc
def svcmon_update(vars, vals):
    if len(vals) == 0:
        return
    if isinstance(vals[0], list):
        for v in vals:
            _svcmon_update(vars, v)
    else:
        _svcmon_update(vars, vals)

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
                        db.svcmon.mon_updated)

    tlim = datetime.datetime.now() - datetime.timedelta(minutes=18)
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

    db(db.services.svc_name==svcname).update(
      svc_status=ostatus,
      svc_availstatus=astatus)

def _svcmon_update(vars, vals):
    # don't trust the server's time
    h = {}
    for a,b in zip(vars, vals):
        if a == 'mon_updated':
            continue
        h[a] = b
    now = datetime.datetime.now()
    tmo = now - datetime.timedelta(minutes=18)
    h['mon_updated'] = now
    if 'mon_hbstatus' not in h:
        h['mon_hbstatus'] = 'undef'
    if 'mon_availstatus' not in h:
        h['mon_availstatus'] = compute_availstatus(h)
    generic_insert('svcmon', h.keys(), h.values())
    svc_status_update(h['mon_svcname'])

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
    elif h['mon_ipstatus'] != last[0].mon_ipstatus or \
         h['mon_fsstatus'] != last[0].mon_fsstatus or \
         h['mon_diskstatus'] != last[0].mon_diskstatus or \
         h['mon_containerstatus'] != last[0].mon_containerstatus or \
         h['mon_appstatus'] != last[0].mon_appstatus or \
         h['mon_hbstatus'] != last[0].mon_hbstatus or \
         h['mon_syncstatus'] != last[0].mon_syncstatus:
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
    else:
        db(db.svcmon_log.id==last[0].id).update(mon_end=h['mon_updated'])


