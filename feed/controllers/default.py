# coding: utf8

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
import datetime, time
import re

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
    return

@auth_uuid
@service.xmlrpc
def begin_action(vars, vals, auth):
    feed_enqueue("_action_wrapper", "_begin_action", vars, vals, auth)

def _begin_action(vars, vals, auth):
    sql="""insert into SVCactions (%s) values (%s)""" % (','.join(vars), ','.join(vals))
    db.executesql(sql)
    i = db.executesql("SELECT LAST_INSERT_ID()")[0][0]
    db.commit()
    h = {}
    for a, b in zip(vars, vals):
        h[a] = b
    h['svcname'] = h['svcname'].strip("'")
    h['hostname'] = h['hostname'].strip("'")
    h['action'] = h['action'].strip("'")
    h['begin'] = h['begin'].strip("'").split('.')[0]
    h['id'] = i
    _comet_send(json.dumps({
                 'event': 'begin_action',
                 'data': h
                }))
    if 'cron' not in h or h['cron'] == '0':
        _log("service.action",
             "action '%(a)s' on %(svc)s@%(node)s",
             dict(a=h['action'],
                  svc=h['svcname'],
                  node=h['hostname']),
             svcname=h['svcname'],
             nodename=h['hostname'])
    return 0

@auth_uuid
@service.xmlrpc
def res_action(vars, vals, auth):
    upd = []
    for a, b in zip(vars, vals):
        upd.append("%s=%s" % (a, b))
    sql="""insert into SVCactions (%s) values (%s)""" % (','.join(vars), ','.join(vals))
    db.executesql(sql)
    db.commit()
    return 0

@auth_uuid
@service.xmlrpc
def end_action(vars, vals, auth):
    feed_enqueue("_action_wrapper", "_end_action", vars, vals, auth)

def _action_wrapper(a, vars, vals, auth):
    if a == "_end_action":
        _end_action(vars, vals)
    elif a == "_begin_action":
        _begin_action(vars, vals, auth)

def _end_action(vars, vals):
    upd = []
    h = {}
    for a, b in zip(vars, vals):
        h[a] = b
        if a not in ['hostname', 'svcname', 'begin', 'action', 'hostid']:
            upd.append("%s=%s" % (a, b))
    h['begin'] = repr(h['begin'].strip("'").split('.')[0])
    sql="""select id from SVCactions where hostname=%s and svcname=%s and begin=%s and action=%s""" %\
        (h['hostname'], h['svcname'], h['begin'], h['action'])
    ids = map(lambda x: x[0], db.executesql(sql))
    if len(ids) == 0:
        return

    sql="""update SVCactions set %s where id in (%s)""" %\
        (','.join(upd), ','.join(map(str, ids)))
    db.executesql(sql)
    db.commit()

    sql = """select * from SVCactions where id in (%s)""" %\
          ','.join(map(str, ids))
    h = db.executesql(sql, as_dict=True)[0]
    h['begin'] = h['begin'].strftime("%Y-%m-%d %H:%M:%S")
    h['end'] = h['end'].strftime("%Y-%m-%d %H:%M:%S")
    h['id'] = h['ID']

    try:
        _comet_send(json.dumps({
                 'event': 'end_action',
                 'data': h
                }))
    except:
        pass

    if h['action'] in ('start', 'startcontainer') and \
       h['status'] == 'ok':
        update_virtual_asset(h['hostname'], h['svcname'])
    if h['status'] == 'err':
        update_action_errors(h['svcname'], h['hostname'])
        update_dash_action_errors(h['svcname'], h['hostname'])
        _log("service.action",
             "action '%(a)s' error on %(svc)s@%(node)s",
             dict(a=h['action'],
                  svc=h['svcname'],
                  node=h['hostname']),
             svcname=h['svcname'],
             nodename=h['hostname'],
             level="error")
    return 0

def update_action_errors(svcname, nodename):
    svcname = svcname.strip("'")
    nodename = nodename.strip("'")
    sql = """select count(id) from SVCactions a
             where
               a.svcname = "%(svcname)s" and
               a.hostname = "%(nodename)s" and
               a.status = "err" and
               ((a.ack <> 1) or isnull(a.ack)) and
               a.begin > date_sub(now(), interval 2 day)
    """%dict(svcname=svcname, nodename=nodename)
    err = db.executesql(sql)[0][0]

    if err == 0:
         sql = """delete from b_action_errors
                  where
                    svcname = "%(svcname)s" and
                    nodename = "%(nodename)s"
         """%dict(svcname=svcname, nodename=nodename)
    else:
        sql = """insert into b_action_errors
                 set
                   svcname="%(svcname)s",
                   nodename="%(nodename)s",
                   err=%(err)d
                 on duplicate key update
                   err=%(err)d
              """%dict(svcname=svcname, nodename=nodename, err=err)
    db.executesql(sql)
    db.commit()

def update_virtual_asset(nodename, svcname):
    q = db.svcmon.mon_svcname == svcname
    q &= db.svcmon.mon_nodname == nodename
    svc = db(q).select(db.svcmon.mon_vmname).first()
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
    sql += "where nodename='%s'"%svc.mon_vmname
    db.executesql(sql)

@auth_uuid
@service.xmlrpc
def update_appinfo(vars, vals, auth):
    h = {}
    for a,b in zip(vars, vals[0]):
        h[a] = b
    if "cluster_type" in h and "flex" in h["cluster_type"]:
        db.executesql("delete from appinfo where app_svcname='%s' and app_nodename='%s'"%(h['app_svcname'], h['app_nodename']))
    else:
        db.executesql("delete from appinfo where app_svcname='%s'"%h['app_svcname'])
    generic_insert('appinfo', vars, vals)

@auth_uuid
@service.xmlrpc
def update_service(vars, vals, auth):
    feed_enqueue("_update_service", vars, vals, auth)

def _update_service(vars, vals, auth):
    if 'svc_hostid' not in vars:
        return
    if 'updated' not in vars:
        vars += ['updated']
        vals += [datetime.datetime.now()]
    h = {}
    for a,b in zip(vars, vals):
        h[a] = b
    vars = []
    vals = []
    for var, val in h.items():
        if var not in ('svc_vmname', 'svc_guestos', 'svc_vcpus', 'svc_vmem', 'svc_containerpath'):
            vars.append(var)
            vals.append(val)
    generic_insert('services', vars, vals)
    db.commit()
    update_dash_service_not_updated(h['svc_name'].strip("'"))
    if 'svc_vmname' in h:
        vars = ['mon_svcname',
                'mon_nodname',
                'mon_vmname',
                'mon_guestos',
                'mon_vcpus',
                'mon_vmem',
                'mon_containerpath']
        vals = [h['svc_name'],
                auth[1],
                h['svc_vmname'],
                h['svc_guestos'] if 'svc_guestos' in h else '',
                h['svc_vcpus'] if 'svc_vcpus' in h else '0',
                h['svc_vmem'] if 'svc_vmem' in h else '0',
                h['svc_containerpath'] if 'svc_containerpath' in h else '',
               ]
        generic_insert('svcmon', vars, vals)

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

    # purge old checks
    if len(vals) > 0:
        nodename = vals[0][0]
        q = db.checks_live.chk_nodename==nodename
        q &= db.checks_live.chk_type != "netdev_err"
        q &= db.checks_live.chk_type != "save"
        db(q).delete()
        db.commit()

        # for checks coming from vservice, update the svcname field
        svcname = vals[0][1]
        if svcname == "":
            q = db.svcmon.mon_vmname == nodename
            rows = db(q).select(db.svcmon.mon_svcname)
            if len(rows) > 0:
                svcname = rows[0].mon_svcname
                for i, val in enumerate(vals):
                    vals[i][1] = svcname

    # insert new checks
    while len(vals) > 100:
        generic_insert('checks_live', vars, vals[:100])
        q = db.checks_live.id < 0
        for v in vals[:100]:
            qr = db.checks_live.chk_nodename == v[0]
            qr &= db.checks_live.chk_type == v[2]
            qr &= db.checks_live.chk_instance == v[3]
            q |= qr
        rows = db(q).select()
        update_thresholds_batch(rows)
        vals = vals[100:]
    generic_insert('checks_live', vars, vals)
    q = db.checks_live.id < 0
    for v in vals:
        qr = db.checks_live.chk_nodename == v[0]
        qr &= db.checks_live.chk_type == v[2]
        qr &= db.checks_live.chk_instance == v[3]
        q |= qr
    rows = db(q).select()
    update_thresholds_batch(rows)

    # update dashboard alerts
    if len(vals) > 0:
        update_dash_checks(vals[0][0])

@auth_uuid
@service.xmlrpc
def insert_generic(data, auth):
    feed_enqueue("_insert_generic", data, auth)

def _insert_generic(data, auth):
    now = datetime.datetime.now()
    if type(data) != dict:
        return
    if 'hba' in data:
        vars, vals = data['hba']
        if 'updated' not in vars:
            vars.append('updated')
            for i, val in enumerate(vals):
                vals[i].append(now)
        sql = """delete from node_hba where nodename="%s" """%auth[1]
        db.executesql(sql)
        generic_insert('node_hba', vars, vals)
    if 'targets' in data:
        vars, vals = data['targets']
        if 'updated' not in vars:
            vars.append('updated')
            for i, val in enumerate(vals):
                vals[i].append(now)
        if 'nodename' not in vars:
            vars.append('nodename')
            for i, val in enumerate(vals):
                vals[i].append(auth[1])
        sql = """delete from stor_zone where nodename="%s" """%auth[1]
        db.executesql(sql)
        generic_insert('stor_zone', vars, vals)
    if 'lan' in data:
        vars, vals = data['lan']
        if 'updated' not in vars:
            vars.append('updated')
            for i, val in enumerate(vals):
                vals[i].append(now)
        if 'nodename' not in vars:
            vars.append('nodename')
            for i, val in enumerate(vals):
                vals[i].append(auth[1])
        sql = """delete from node_ip where nodename="%s" """%auth[1]
        db.executesql(sql)
        generic_insert('node_ip', vars, vals)
    db.commit()

@auth_uuid
@service.xmlrpc
def update_asset(vars, vals, auth):
    feed_enqueue("_update_asset", vars, vals, auth)

@auth_uuid
@service.xmlrpc
def update_asset_sync(vars, vals, auth):
    _update_asset(vars, vals, auth)

def _update_asset(vars, vals, auth):
    h = {}
    for a,b in zip(vars, vals):
        h[a] = b
    now = datetime.datetime.now()
    h['updated'] = now
    if 'environnement' in h and 'host_mode' not in h:
        h['host_mode'] = h['environnement']
        del(h['environnement'])
    if 'environment' in h:
        h['environnement'] = h['environment']
        del(h['environment'])
    generic_insert('nodes', h.keys(), h.values())
    update_dash_node_not_updated(auth[1])
    update_dash_node_without_maintenance_end(auth[1])
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
        h['nodename'] = translate_encap_nodename( h['svcname'],  h['nodename'])
        _resmon_clean(h['nodename'], h['svcname'])
    generic_insert('resmon', vars, vals)

@auth_uuid
@service.xmlrpc
def svcmon_update_combo(g_vars, g_vals, r_vars, r_vals, auth):
    feed_enqueue("_svcmon_update", g_vars, g_vals)
    feed_enqueue("_resmon_update", r_vars, r_vals)

@auth_uuid
@service.xmlrpc
def register_disks(vars, vals, auth):
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    for v in vals:
        _register_disk(vars, v, auth)

    nodename = auth[1].strip("'")

    # purge svcdisks
    sql = """ delete from svcdisks
              where
                disk_nodename = "%(nodename)s" and
                disk_updated < "%(now)s"
          """ % dict(nodename=nodename, now=now)
    db.executesql(sql)

    # purge diskinfo stubs
    sql = """ delete from diskinfo
              where
                (disk_arrayid = "%(nodename)s" or
                 disk_arrayid = "" or
                 disk_arrayid = "None" or
                 disk_arrayid is NULL) and
                disk_updated < "%(now)s"
          """ % dict(nodename=nodename, now=now)
    db.executesql(sql)

    db.commit()

@auth_uuid
@service.xmlrpc
def register_disk_blacklist(vars, vals, auth):
    generic_insert('disk_blacklist', vars, vals)

def disk_level(dev_id, level=0):
    q = db.diskinfo.disk_id == dev_id
    q &= db.diskinfo.disk_id != db.diskinfo.disk_devid
    rows = db(q).select(db.diskinfo.disk_devid)
    if len(rows) == 0:
        return level
    return disk_level(rows.first().disk_devid, level+1)

@auth_uuid
@service.xmlrpc
#def register_diskinfo(vars, vals, auth):
#    feed_enqueue("_register_diskinfo", vars, vals, auth)

def register_diskinfo(vars, vals, auth):
    if len(vals) == 0:
        return

    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)
    nodename = auth[1]
    vars.append("disk_updated")
    vars.append("disk_level")

    # insert diskinfo
    # here the array can be a cluster. the field contains the member list.
    # in this case, the node has to be added to the cluster members when the
    # disk id is already known in diskinfo
    arrays = set([])
    for val in vals:
        cluster = val[1]
        dev_id = val[2]
        val.append(now)
        val.append(str(disk_level(dev_id)))
        generic_insert('diskinfo', vars, val)

    # purge diskinfo
    sql = """ delete from diskinfo
              where
                disk_arrayid = "%(cluster)s" and
                disk_updated < "%(now)s"
          """ % dict(cluster=val[1], now=now)
    db.executesql(sql)

    # register cluster as array
    node = db(db.nodes.nodename==nodename).select().first()
    if node is not None:
        array_cache = node.mem_bytes
        array_firmware = " ".join((node.os_name, node.os_vendor, node.os_release, node.os_kernel))
    else:
        array_cache = 0
        array_firwmare = "unknown"

    vars = ['array_name', 'array_model', 'array_cache', 'array_firmware', 'array_updated']
    vals = [
      cluster,
      "vdisk provider",
      str(array_cache),
      array_firmware,
      now
    ]
    generic_insert('stor_array', vars, vals)
    sql = """ delete from stor_array where array_name = "%s" and array_updated < "%s" """%(cluster, now)
    db.executesql(sql)
    db.commit()

@auth_uuid
@service.xmlrpc
def register_disk(vars, vals, auth):
    _register_disk(vars, vals, auth)

def _register_disk(vars, vals, auth):
    h = {}
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)
    for a,b in zip(vars, vals):
        h[a] = b

    disk_id = h["disk_id"].strip("'")
    disk_svcname = h["disk_svcname"].strip("'")
    disk_nodename = h["disk_nodename"].strip("'")

    if len(disk_svcname) == 0:
        # if no service name is provided and the node is actually
        # a service encpasulated vm, add the encapsulating svcname
        q = db.svcmon.mon_vmname == disk_nodename
        row = db(q).select().first()
        if row is not None:
            h["disk_svcname"] = repr(row.mon_svcname)

    # don't register blacklisted disks (might be VM disks, already accounted)
    #n = db(db.disk_blacklist.disk_id==disk_id).count()
    #if n > 0:
    #    purge_old_disks(h, now)
    #    return

    h['disk_updated'] = now

    q = db.diskinfo.disk_id==disk_id
    disks = db(q).select()
    n = len(disks)

    if n > 0:
        # diskinfo exists. is it a local or remote disk
        disk = disks.first()
        if disk.disk_arrayid == disk_nodename or \
           disk.disk_arrayid is None or \
           len(disk.disk_arrayid) == 0:
            # diskinfo registered as a stub for a local disk
            h['disk_local'] = 'T'

            if n == 1:
                # update diskinfo timestamp
                if disk.disk_arrayid is None:
                    array_id = 'NULL'
                else:
                    array_id = disk.disk_arrayid
                vars = ['disk_id', 'disk_arrayid', 'disk_updated']
                vals = [h["disk_id"], array_id, h['disk_updated']]
                generic_insert('diskinfo', vars, vals)
        else:
            # diskinfo registered by a array parser or an hv pushdisks
            h['disk_local'] = 'F'

    if disk_id.startswith(disk_nodename+'.') and n == 0:
        h['disk_local'] = 'T'
        vars = ['disk_id', 'disk_arrayid', 'disk_devid', 'disk_size']
        vals = [h["disk_id"],
                h['disk_nodename'],
                repr(disk_id.split('.')[-1]),
                h['disk_size']]
        generic_insert('diskinfo', vars, vals)
    elif n == 0:
        h['disk_local'] = 'F'
        vars = ['disk_id', 'disk_size']
        vals = [h["disk_id"], h['disk_size']]
        generic_insert('diskinfo', vars, vals)

        # if no array claimed that disk, give it to the node
        sql = """update diskinfo
                 set disk_arrayid="%s"
                 where
                   disk_id="%s" and
                   (disk_arrayid = "" or disk_arrayid is NULL)
              """%(h['disk_nodename'].strip("'"), disk_id)
        db.executesql(sql)
        db.commit()

    try:
        generic_insert('svcdisks', h.keys(), h.values())
    except:
        # the foreign key on svcdisk may prevent insertion if svcmon is not yet
        # populated
        pass
    purge_old_disks(h, now)

def purge_old_disks(h, now):
    if 'disk_nodename' in h and h['disk_nodename'] is not None and h['disk_nodename'] != '':
        q = db.svcdisks.disk_nodename==h['disk_nodename']
        q &= db.svcdisks.disk_updated<now
        db(q).delete()
        db.commit()

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
    import cPickle
    h = cPickle.loads(data)
    for stat in h:
        vars, vals = h[stat]
        generic_insert('stats_'+stat, vars, vals)
    feed_enqueue("update_dash_netdev_errors" , auth[1])

@auth_uuid
@service.xmlrpc
def insert_pkg(vars, vals, auth):
    feed_enqueue("_insert_pkg", vars, vals, auth)

def _insert_pkg(vars, vals, auth):
    now = datetime.datetime.now()
    vars.append("pkg_updated")
    for i, val in enumerate(vals):
        vals[i].append(str(now))
    threshold = now - datetime.timedelta(minutes=1)
    generic_insert('packages', vars, vals)
    nodename = auth[1].strip("'")
    delete_old_pkg(threshold, nodename)
    update_dash_pkgdiff(nodename)

def delete_old_pkg(threshold, nodename):
    q = db.packages.pkg_nodename == nodename
    q &= db.packages.pkg_updated < threshold
    db.commit()
    db(q).delete()
    db.commit()

def delete_old_patches(threshold, nodename):
    q = db.patches.patch_nodename == nodename
    q &= db.patches.patch_updated < threshold
    db.commit()
    db(q).delete()
    db.commit()

@auth_uuid
@service.xmlrpc
def insert_patch(vars, vals, auth):
    feed_enqueue("_insert_patch", vars, vals, auth)

def _insert_patch(vars, vals, auth):
    now = datetime.datetime.now()
    vars.append("patch_updated")
    for i, val in enumerate(vals):
        vals[i].append(str(now))
    threshold = now - datetime.timedelta(minutes=1)
    generic_insert('patches', vars, vals)
    nodename = auth[1].strip("'")
    delete_old_patches(threshold, nodename)

@auth_uuid
@service.xmlrpc
def update_hds(symid, vars, vals, auth):
    update_array_xml(symid, vars, vals, auth, "hds", insert_hds)

@auth_uuid
@service.xmlrpc
def update_sym_xml(symid, vars, vals, auth):
    update_array_xml(symid, vars, vals, auth, "symmetrix", insert_sym)

@auth_uuid
@service.xmlrpc
def update_eva_xml(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "eva", insert_eva)

@auth_uuid
@service.xmlrpc
def update_nsr(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "nsr", insert_nsr)

@auth_uuid
@service.xmlrpc
def update_netapp(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "netapp", insert_netapp)

@auth_uuid
@service.xmlrpc
def update_ibmsvc(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "ibmsvc", insert_ibmsvc)

@auth_uuid
@service.xmlrpc
def update_brocade(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "brocade", insert_brocade)

@auth_uuid
@service.xmlrpc
def update_vioserver(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "vioserver", insert_vioserver)

@auth_uuid
@service.xmlrpc
def update_necism(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "necism", insert_necism)

@auth_uuid
@service.xmlrpc
def update_dcs(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "dcs", insert_dcs)

def update_array_xml(arrayid, vars, vals, auth, subdir, fn):
    import os
    import codecs

    dir = 'applications'+str(URL(r=request,a='init', c='uploads',f=subdir))
    if not os.path.exists(dir):
        os.makedirs(dir)

    dir = os.path.join(dir, arrayid)
    if not os.path.exists(dir):
        os.makedirs(dir)

    for a,b in zip(vars, vals):
        a = os.path.join(dir, a)
        try:
            f = codecs.open(a, "w", "utf-8")
            f.write(b)
            f.sync()
            f.close()
        except:
            pass

    #fn(arrayid)
    feed_enqueue(fn.__name__, arrayid, auth[1])

    # stor_array_proxy
    insert_array_proxy(auth[1], arrayid)

def insert_dcss():
    return insert_dcs()

def insert_array_proxy(nodename, array_name):
    sql = """select id from stor_array where array_name="%s" """%array_name
    rows = db.executesql(sql)
    if len(rows) == 0:
        return
    array_id = str(rows[0][0])

    vars = ['array_id', 'nodename']
    vals = [array_id, nodename]
    generic_insert('stor_array_proxy', vars, vals)

def insert_dcs(name=None, nodename=None):
    import glob
    import os
    from applications.init.modules import dcs
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    dir = 'applications'+str(URL(r=request,a='init',c='uploads',f='dcs'))
    if name is None:
        pattern = "*"
    else:
        pattern = name
    dirs = glob.glob(os.path.join(dir, pattern))

    for d in dirs:
        print d
        s = dcs.get_dcs(d)
        if s is None:
            print "error parsing data"
            continue

        # stor_array_proxy
        if nodename is not None:
            print " insert %s as proxy node"%nodename
            insert_array_proxy(nodename, s.sg['caption'])

        # stor_array
        vars = ['array_name', 'array_model', 'array_cache', 'array_firmware', 'array_updated']
        vals = []
        name = s.sg['caption']
        for server in s.server.values():
            if len(server['model']) > 0:
                break
        vals.append([s.sg['caption'],
                     server['model'],
                     str(s.sg['memory']),
                     server['productbuild'],
                     now])
        generic_insert('stor_array', vars, vals)

        sql = """select id from stor_array where array_name="%s" """%name
        array_id = str(db.executesql(sql)[0][0])

        # stor_array_dg
        vars = ['array_id', 'dg_name', 'dg_free', 'dg_used', 'dg_size', 'dg_updated']
        vals = []
        for dg in s.pool.values():
            vals.append([array_id,
                         dg['caption'],
                         str(dg['avail']),
                         str(dg['alloc']),
                         str(dg['total']),
                         now])
        generic_insert('stor_array_dg', vars, vals)
        sql = """delete from stor_array_dg where array_id=%s and dg_updated < "%s" """%(array_id, str(now))
        db.executesql(sql)

        # stor_array_tgtid
        vars = ['array_id', 'array_tgtid']
        vals = []
        for wwn in s.port_list:
            vals.append([array_id, wwn])
        generic_insert('stor_array_tgtid', vars, vals)

        # diskinfo
        vars = ['disk_id',
                'disk_arrayid',
                'disk_name',
                'disk_devid',
                'disk_size',
                'disk_alloc',
                'disk_raid',
                'disk_group',
                'disk_updated']
        vals = []
        for d in s.vdisk.values():
            for poolid in d['poolid']:
                vals.append([d['wwid'],
                             name,
                             d['caption'],
                             d['id'],
                             str(d['size']),
                             str(d['alloc']),
                             d['type'],
                             s.pool[poolid]['caption'],
                             now])
        generic_insert('diskinfo', vars, vals)
        sql = """delete from diskinfo where disk_arrayid="%s" and disk_updated < "%s" """%(name, str(now))
        db.executesql(sql)

def insert_hdss():
    return insert_hds()

def insert_hds(name=None, nodename=None):
    import glob
    import os
    from applications.init.modules import hds
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    dir = 'applications'+str(URL(r=request,a='init',c='uploads',f='hds'))
    if name is None:
        pattern = "*"
    else:
        pattern = name
    dirs = glob.glob(os.path.join(dir, pattern))

    for d in dirs:
        s = hds.get_hds(d)
        if s is not None:
            # stor_array
            vars = ['array_name', 'array_model', 'array_cache', 'array_firmware', 'array_updated']
            vals = []
            vals.append([s.name,
                         s.model,
                         str(s.cache),
                         s.firmware,
                         now])
            generic_insert('stor_array', vars, vals)

            sql = """select id from stor_array where array_name="%s" """%s.name
            array_id = str(db.executesql(sql)[0][0])

            # stor_array_dg
            vars = ['array_id', 'dg_name', 'dg_free', 'dg_used', 'dg_size', 'dg_updated']
            vals = []
            for pname, dg in s.pool.items():
                vals.append([array_id,
                             dg['name'],
                             str(dg['free']),
                             str(dg['used']),
                             str(dg['size']),
                             now])
            generic_insert('stor_array_dg', vars, vals)
            sql = """delete from stor_array_dg where array_id=%s and dg_updated < "%s" """%(array_id, str(now))
            db.executesql(sql)

            # stor_array_tgtid
            vars = ['array_id', 'array_tgtid']
            vals = []
            for wwn in s.ports:
                vals.append([array_id, wwn])
            generic_insert('stor_array_tgtid', vars, vals)

            # diskinfo
            vars = ['disk_id',
                    'disk_arrayid',
                    'disk_devid',
                    'disk_size',
                    'disk_raid',
                    'disk_group',
                    'disk_updated']
            vals = []
            for d in s.vdisk:
                vals.append([d['wwid'],
                             s.name,
                             d['name'],
                             str(d['size']),
                             d['raid'],
                             d['disk_group'],
                             now])
            generic_insert('diskinfo', vars, vals)
            sql = """delete from diskinfo where disk_arrayid="%s" and disk_updated < "%s" """%(s.name, str(now))
            db.executesql(sql)


def insert_necisms():
    return insert_necism()

def insert_necism(name=None, nodename=None):
    import glob
    import os
    from applications.init.modules import necism
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    dir = 'applications'+str(URL(r=request,a='init',c='uploads',f='necism'))
    if name is None:
        pattern = "*"
    else:
        pattern = name
    dirs = glob.glob(os.path.join(dir, pattern))

    for d in dirs:
        s = necism.get_necism(d)
        if s is not None:
            # stor_array
            vars = ['array_name', 'array_model', 'array_cache', 'array_firmware', 'array_updated']
            vals = []
            vals.append([s.name,
                         s.model,
                         str(s.cache),
                         s.firmware,
                         now])
            generic_insert('stor_array', vars, vals)

            sql = """select id from stor_array where array_name="%s" """%s.name
            array_id = str(db.executesql(sql)[0][0])

            # stor_array_dg
            vars = ['array_id', 'dg_name', 'dg_free', 'dg_used', 'dg_size', 'dg_updated']
            vals = []
            for dg in s.pool:
                vals.append([array_id,
                             dg['name'],
                             str(dg['free']),
                             str(dg['used']),
                             str(dg['size']),
                             now])
            generic_insert('stor_array_dg', vars, vals)
            sql = """delete from stor_array_dg where array_id=%s and dg_updated < "%s" """%(array_id, str(now))
            db.executesql(sql)

            # stor_array_tgtid
            vars = ['array_id', 'array_tgtid']
            vals = []
            for wwn in s.ports:
                vals.append([array_id, wwn])
            generic_insert('stor_array_tgtid', vars, vals)

            # diskinfo
            vars = ['disk_id',
                    'disk_arrayid',
                    'disk_devid',
                    'disk_size',
                    'disk_raid',
                    'disk_group',
                    'disk_updated']
            vals = []
            for d in s.vdisk:
                vals.append([d['wwid'],
                             s.name,
                             d['name'],
                             str(d['size']),
                             d['raid'],
                             d['disk_group'],
                             now])
            generic_insert('diskinfo', vars, vals)
            sql = """delete from diskinfo where disk_arrayid="%s" and disk_updated < "%s" """%(s.name, str(now))
            db.executesql(sql)


def insert_brocades():
    return insert_brocade()

def insert_brocade(name=None, nodename=None):
    import glob
    import os
    from applications.init.modules import brocade
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    dir = 'applications'+str(URL(r=request,a='init',c='uploads',f='brocade'))
    if name is None:
        pattern = "*"
    else:
        pattern = name
    dirs = glob.glob(os.path.join(dir, pattern))

    vars = ['sw_name',
            'sw_portname',
            'sw_index',
            'sw_slot',
            'sw_port',
            'sw_portspeed',
            'sw_portnego',
            'sw_portstate',
            'sw_porttype',
            'sw_rportname',
            'sw_updated']
    avars = ['cfg',
             'alias',
             'port',
             'updated']
    zvars = ['cfg',
             'zone',
             'port',
             'updated']
    for d in dirs:
        s = brocade.get_brocade(d)

        if s is None:
            print "get_brocade: %s is corrupted"%d
            continue

        # alias
        for cfg in s.alias:
            vals = []
            for alias, ports in s.alias[cfg].items():
                for port in ports:
                    vals.append([
                        cfg,
                        alias,
                        port,
                        now
                    ])
            generic_insert('san_zone_alias', avars, vals)
            sql = """delete from san_zone_alias where cfg="%s" and updated < "%s" """%(cfg, str(now))
            db.executesql(sql)

        # zones
        vals = []
        if s is None:
            continue
        if s.cfg is not None:
            for zone, ports in s.zone.items():
                for port in ports:
                    vals.append([
                        s.cfg,
                        zone,
                        port,
                        now
                    ])
            generic_insert('san_zone', zvars, vals)
            sql = """delete from san_zone where cfg="%s" and updated < "%s" """%(s.cfg, str(now))
            db.executesql(sql)

        # ports-portname
        vals = []
        for p in s.ports.values():
            vals.append([
                s.name,
                s.wwn,
                str(p['Index']),
                str(p['Slot']),
                str(p['Port']),
                str(p['Speed']),
                str(p['Nego']),
                str(p['State']),
                str(p['Type']),
                str(p['RemotePortName']),
                now
            ])
            for nse in p['nse']:
                if nse == p['RemotePortName']:
                    continue
                vals.append([
                    s.name,
                    s.wwn,
                    str(p['Index']),
                    str(p['Slot']),
                    str(p['Port']),
                    str(p['Speed']),
                    str(p['Nego']),
                    str(p['State']),
                    str(p['Type']),
                    nse,
                    now
                ])
        generic_insert('switches', vars, vals)
        sql = """delete from switches where sw_name="%s" and sw_updated < "%s" """%(s.name, str(now))
        db.executesql(sql)

def insert_vioservers():
    return insert_vioserver()

def insert_vioserver(name=None, nodename=None):
    import glob
    import os
    from applications.init.modules import vioserver
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    dir = 'applications'+str(URL(r=request,a='init',c='uploads',f='vioserver'))
    if name is None:
        pattern = "*"
    else:
        pattern = name
    dirs = glob.glob(os.path.join(dir, pattern))

    for d in dirs:
        s = vioserver.get_vioserver(d)
        if s is None:
            continue

        # stor_array
        vars = ['array_name', 'array_model', 'array_cache', 'array_firmware', 'array_updated']
        vals = []
        vals.append([s.array_name,
                     s.modelnumber,
                     str(s.controllermainmemory),
                     s.firmwareversion,
                     now])
        generic_insert('stor_array', vars, vals)

        sql = """select id from stor_array where array_name="%s" """%s.array_name
        array_id = str(db.executesql(sql)[0][0])

        # diskinfo
        vars = ['disk_id',
                'disk_arrayid',
                'disk_devid',
                'disk_size',
                'disk_alloc',
                'disk_raid',
                'disk_group',
                'disk_level',
                'disk_updated']
        vals = []
        for d in s.vdisk:
            vals.append([d['did'],
                         s.array_name,
                         d['backingdevid'],
                         str(d['size']),
                         str(d['size']),
                         "",
                         "",
                         str(disk_level(d['backingdevid'])),
                         now])
        generic_insert('diskinfo', vars, vals)
        sql = """delete from diskinfo where disk_arrayid="%s" and disk_updated < "%s" """%(s.array_name, str(now))
        db.executesql(sql)

        # svcdisks
        vars = ['disk_id',
                'disk_size',
                'disk_used',
                'disk_vendor',
                'disk_model',
                'disk_nodename']
        vals = []
        for d in s.pdisk.values():
            vals.append([d['wwid'],
                         d['size'],
                         d['size'],
                         d['vendor'],
                         d['model'],
                         s.array_name])
        generic_insert('svcdisks', vars, vals)
        sql = """delete from svcdisks where disk_nodename="%s" and disk_updated < "%s" """%(s.array_name, str(now))
        db.executesql(sql)


def insert_nsrs():
    return insert_nsr()

def insert_nsr(name=None, nodename=None):
    import glob
    import os
    import socket

    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    dir = 'applications'+str(URL(r=request,a='init',c='uploads',f='nsr'))
    if name is None:
        pattern = "*"
    else:
        pattern = name
    dirs = glob.glob(os.path.join(dir, pattern))

    # load node ip cache
    sql = "select nodename, addr from node_ip"
    rows = db.executesql(sql)
    node_ip = {}
    for row in rows:
        node_ip[row[1]] = row[0]

    # load svc ip cache
    sql = """select svcname, res_desc from resmon where rid like "%ip#%" """
    rows = db.executesql(sql)
    svc_ip = {}
    for row in rows:
        try:
            addr = row[1].split('@')[0]
            a = socket.getaddrinfo(addr, None)
            ip = a[0][-1][0]
            svc_ip[ip] = row[0]
        except:
            continue

    # load app cache
    sql = """select svc_name, svc_app from services"""
    rows = db.executesql(sql)
    svc_app = {}
    for row in rows:
        svc_app[row[0]] = row[1]

    sql = """select nodename, project from nodes"""
    rows = db.executesql(sql)
    node_app = {}
    for row in rows:
        node_app[row[0]] = row[1]

    for d in dirs:
        server = os.path.basename(d)
        fpath = os.path.join(d, "mminfo")

        vars = ['save_server', 'save_nodename', 'save_svcname', 'save_name',
                'save_group', 'save_size', 'save_date', 'save_retention',
                'save_volume', 'save_level', 'save_id', 'save_app']
        vals = []

        with open(fpath, 'r') as f:
            lines = f.read().split('\n')

        i = 0
        for line in lines:
            l = line.split(';')
            if len(l) != 9:
                continue
            if l[6].endswith('.RO'):
                # nsr read-lonly device. don't import as it would
                # account twice the size.
                continue
            if l[0] in node_ip:
                nodename = node_ip[l[0]]
            else:
                nodename = l[0]
            if l[0] in svc_ip:
                svcname = svc_ip[l[0]]
            else:
                svcname = ''
            if svcname != '' and svcname in svc_app:
                app = svc_app[svcname]
            elif nodename in node_app:
                app = node_app[nodename]
            else:
                app = ''
            vals.append([server, nodename, svcname]+l[1:]+[app])
            i += 1
            if i > 300:
                i = 0
                generic_insert('saves', vars, vals)
                vals = []
        generic_insert('saves', vars, vals)
        db.commit()

    purge_saves()
    update_save_checks()

def purge_saves():
    sql = """delete from saves where
             save_retention < now()"""
    db.executesql(sql)
    db.commit()

def update_save_checks():
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    sql = """
           insert into checks_live (chk_nodename, chk_svcname, chk_type, chk_updated, chk_value, chk_created, chk_instance)
             select
               checks_live.chk_nodename as chk_nodename,
               checks_live.chk_svcname as chk_svcname,
               "save",
               now(),
               1000000 as chk_value,
               now(),
               checks_live.chk_instance as chk_instance
             from
               checks_live
               left join saves on
                 checks_live.chk_nodename = saves.save_nodename and
                 (checks_live.chk_svcname = saves.save_svcname or saves.save_svcname = "" or checks_live.chk_svcname = "") and
                 checks_live.chk_instance = saves.save_name
             where
               checks_live.chk_type="fs_u" and
               checks_live.chk_instance not in ("/dev/shm", "/tmp", "/var/lib/xenstored", "/var/adm/crash", "/var/adm/ras/livedump") and
               saves.save_name is null
           on duplicate key update
             chk_updated=now(),
             chk_value=if(datediff(now(), saves.save_date) is null, 1000000, datediff(now(), saves.save_date))
          """
    db.executesql(sql)
    db.commit()

    sql = """
           insert into checks_live (chk_nodename, chk_svcname, chk_type, chk_updated, chk_value, chk_created, chk_instance)
             select
               saves.save_nodename as chk_nodename,
               saves.save_svcname as chk_svcname,
               "save",
               now(),
               datediff(now(), saves.save_date) as chk_value,
               now(),
               if (substring(saves.save_name, 1, 4) = "RMAN", substring_index(saves.save_name, '_', 1), saves.save_name) as chk_instance
             from
               saves
             where
               not substring(lower(saves.save_nodename),1,1) between '0' and '9' and
               saves.save_name not in ("/dev/shm", "/tmp", "/var/lib/xenstored", "/var/adm/crash", "/var/adm/ras/livedump", "bootstrap") and
               saves.save_name not like "index%"
             order by
               saves.save_date
           on duplicate key update
             chk_updated=now(),
             chk_value=datediff(now(), saves.save_date)
          """
    db.executesql(sql)
    db.commit()

    sql = """delete from checks_live
             where
               chk_type="save" and
               chk_updated < "%(now)s"
          """%dict(now=now)
    db.executesql(sql)
    db.commit()

    q = db.checks_live.chk_type == "save"
    checks = db(q).select()
    update_thresholds_batch(checks)

    update_dash_checks_all()


def insert_netapps():
    return insert_netapp()

def insert_netapp(name=None, nodename=None):
    import glob
    import os
    from applications.init.modules import netapp
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    dir = 'applications'+str(URL(r=request,a='init',c='uploads',f='netapp'))
    if name is None:
        pattern = "*"
    else:
        pattern = name
    dirs = glob.glob(os.path.join(dir, pattern))

    for d in dirs:
        s = netapp.get_netapp(d)
        if s is not None:
            # stor_array
            vars = ['array_name', 'array_model', 'array_cache', 'array_firmware', 'array_updated']
            vals = []
            vals.append([s.array_name,
                         s.modelnumber,
                         str(s.controllermainmemory),
                         s.firmwareversion,
                         now])
            generic_insert('stor_array', vars, vals)

            sql = """select id from stor_array where array_name="%s" """%s.array_name
            array_id = str(db.executesql(sql)[0][0])

            # stor_array_dg
            vars = ['array_id', 'dg_name', 'dg_free', 'dg_used', 'dg_size', 'dg_updated']
            vals = []
            for dg in s.dg:
                vals.append([array_id,
                             dg['name'],
                             str(dg['free_capacity']),
                             str(dg['capacity']-dg['free_capacity']),
                             str(dg['capacity']),
                             now])
            generic_insert('stor_array_dg', vars, vals)
            sql = """delete from stor_array_dg where array_id=%s and dg_updated < "%s" """%(array_id, str(now))
            db.executesql(sql)

            # stor_array_tgtid
            vars = ['array_id', 'array_tgtid']
            vals = []
            for wwn in s.ports:
                vals.append([array_id, wwn])
            generic_insert('stor_array_tgtid', vars, vals)

            # diskinfo
            vars = ['disk_id',
                    'disk_arrayid',
                    'disk_devid',
                    'disk_size',
                    'disk_raid',
                    'disk_group',
                    'disk_updated']
            vals = []
            for d in s.vdisk:
                vals.append([d['vdisk_UID'],
                             s.array_name,
                             d['name'],
                             str(d['capacity']),
                             d['type'],
                             d['mdisk_grp_name'],
                             now])
            generic_insert('diskinfo', vars, vals)
            sql = """delete from diskinfo where disk_arrayid="%s" and disk_updated < "%s" """%(s.array_name, str(now))
            db.executesql(sql)


def insert_ibmsvcs():
    return insert_ibmsvc()

def insert_ibmsvc(name=None, nodename=None):
    import glob
    import os
    from applications.init.modules import ibmsvc
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    dir = 'applications'+str(URL(r=request,a='init',c='uploads',f='ibmsvc'))
    if name is None:
        pattern = "*"
    else:
        pattern = name
    dirs = glob.glob(os.path.join(dir, pattern))

    for d in dirs:
        s = ibmsvc.get_ibmsvc(d)
        if s is not None:
            # stor_array
            vars = ['array_name', 'array_model', 'array_cache', 'array_firmware', 'array_updated']
            vals = []
            vals.append([s.array_name,
                         s.modelnumber,
                         str(s.controllermainmemory),
                         s.firmwareversion,
                         now])
            generic_insert('stor_array', vars, vals)

            sql = """select id from stor_array where array_name="%s" """%s.array_name
            array_id = str(db.executesql(sql)[0][0])

            # stor_array_dg
            vars = ['array_id', 'dg_name', 'dg_free', 'dg_used', 'dg_size', 'dg_updated']
            vals = []
            for dg in s.dg:
                vals.append([array_id,
                             dg['name'],
                             str(dg['free_capacity']),
                             str(dg['capacity']-dg['free_capacity']),
                             str(dg['capacity']),
                             now])
            generic_insert('stor_array_dg', vars, vals)
            sql = """delete from stor_array_dg where array_id=%s and dg_updated < "%s" """%(array_id, str(now))
            db.executesql(sql)

            # stor_array_tgtid
            vars = ['array_id', 'array_tgtid']
            vals = []
            for wwn in s.ports:
                vals.append([array_id, wwn])
            generic_insert('stor_array_tgtid', vars, vals)

            # diskinfo
            vars = ['disk_id',
                    'disk_arrayid',
                    'disk_devid',
                    'disk_size',
                    'disk_raid',
                    'disk_group',
                    'disk_updated']
            vals = []
            for d in s.vdisk:
                vals.append([d['vdisk_UID'],
                             s.array_name,
                             d['name'],
                             str(d['capacity']),
                             d['type'],
                             d['mdisk_grp_name'],
                             now])
            generic_insert('diskinfo', vars, vals)
            sql = """delete from diskinfo where disk_arrayid="%s" and disk_updated < "%s" """%(s.array_name, str(now))
            db.executesql(sql)


def insert_evas():
    return insert_eva()

def insert_eva(name=None, nodename=None):
    import glob
    import os
    from applications.init.modules import eva
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    dir = 'applications'+str(URL(r=request,a='init',c='uploads',f='eva'))
    if name is None:
        pattern = "*"
    else:
        pattern = name
    dirs = glob.glob(os.path.join(dir, pattern))
    evas = []

    for d in dirs:
        s = eva.get_eva(d)
        if s is not None:
            # stor_array
            vars = ['array_name', 'array_model', 'array_cache', 'array_firmware', 'array_updated']
            vals = []
            vals.append([s.name,
                         s.modelnumber,
                         str(s.controllermainmemory),
                         s.firmwareversion,
                         now])
            generic_insert('stor_array', vars, vals)

            sql = """select id from stor_array where array_name="%s" """%s.name
            array_id = str(db.executesql(sql)[0][0])

            # stor_array_dg
            vars = ['array_id', 'dg_name', 'dg_free', 'dg_used', 'dg_size', 'dg_updated']
            vals = []
            for dg in s.dg:
                vals.append([array_id,
                             dg['diskgroupname'],
                             str(dg['freestoragespace']),
                             str(dg['usedstoragespace']),
                             str(dg['totalstoragespace']),
                             now])
            generic_insert('stor_array_dg', vars, vals)
            sql = """delete from stor_array_dg where array_id=%s and dg_updated < "%s" """%(array_id, str(now))
            db.executesql(sql)

            # stor_array_tgtid
            vars = ['array_id', 'array_tgtid']
            vals = []
            for wwn in s.ports:
                vals.append([array_id, wwn])
            generic_insert('stor_array_tgtid', vars, vals)

            # diskinfo
            vars = ['disk_id',
                    'disk_arrayid',
                    'disk_name',
                    'disk_devid',
                    'disk_size',
                    'disk_alloc',
                    'disk_raid',
                    'disk_group',
                    'disk_updated']
            vals = []
            for d in s.vdisk.values():
                vals.append([d['wwlunid'],
                             s.name,
                             d['objectname'],
                             d['objectid'],
                             str(d['allocatedcapacity']),
                             str(d['alloc']),
                             d['redundancy'],
                             d['diskgroupname'],
                             now])
            generic_insert('diskinfo', vars, vals)
            sql = """delete from diskinfo where disk_arrayid="%s" and disk_updated < "%s" """%(s.name, str(now))
            db.executesql(sql)


def insert_syms():
    return insert_sym()

def insert_sym(symid=None, nodename=None):
    import glob
    import os
    from applications.init.modules import symmetrix
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    dir = 'applications'+str(URL(r=request,a='init',c='uploads',f='symmetrix'))
    if symid is None:
        pattern = "[0-9]*"
    else:
        pattern = symid
    sym_dirs = glob.glob(os.path.join(dir, pattern))
    syms = []

    for d in sym_dirs:
        s = symmetrix.get_sym(d)
        if s is not None:
            # stor_array
            s.get_sym_info()
            vars = ['array_name', 'array_model', 'array_cache', 'array_firmware', 'array_updated']
            vals = []
            vals.append([s.info['symid'],
                         s.info['model'],
                         s.info['cache_megabytes'],
                         '.'.join((s.info['version'],
                                   s.info['patch_level'],
                                   s.info['symmwin_version'])),
                         now])
            generic_insert('stor_array', vars, vals)

            sql = """select id from stor_array where array_name="%s" """%s.info['symid']
            array_id = str(db.executesql(sql)[0][0])

            # stor_array_dg
            s.get_sym_diskgroup()
            vars = ['array_id', 'dg_name', 'dg_free', 'dg_used', 'dg_size', 'dg_updated']
            vals = []
            for dg in s.diskgroup.values():
                vals.append([array_id,
                             dg.info['disk_group_name'],
                             str(dg.total-dg.used),
                             str(dg.used),
                             str(dg.total),
                             now])
            generic_insert('stor_array_dg', vars, vals)
            del(s.diskgroup)
            sql = """delete from stor_array_dg where array_id=%s and dg_updated < "%s" """%(array_id, str(now))
            db.executesql(sql)

            # stor_array_tgtid
            s.get_sym_director()
            vars = ['array_id', 'array_tgtid']
            vals = []
            for dir in s.director.values():
                for wwn in dir.port_wwn:
                    vals.append([array_id, wwn])
            generic_insert('stor_array_tgtid', vars, vals)
            del(s.director)

            # diskinfo
            s.get_sym_dev()
            vars = ['disk_id',
                    'disk_arrayid',
                    'disk_devid',
                    'disk_size',
                    'disk_alloc',
                    'disk_raid',
                    'disk_group',
                    'disk_updated']
            vals = []
            for dev in s.dev.values():
                if dev.flags['meta'] not in ('Head', 'None'):
                    continue
                vals.append([dev.wwn,
                             s.info['symid'],
                             dev.info['dev_name'],
                             str(dev.megabytes),
                             str(dev.alloc),
                             "Meta-%d %s"%(dev.meta_count, dev.info['configuration']),
                             dev.diskgroup_name,
                             now])
            generic_insert('diskinfo', vars, vals)
            del(s.dev)
            sql = """delete from diskinfo where disk_arrayid="%s" and disk_updated < "%s" """%(s.info['symid'], str(now))
            db.executesql(sql)

            del(s)

@auth_uuid
@service.xmlrpc
def delete_pkg(node, auth):
    pass

@auth_uuid
@service.xmlrpc
def delete_patch(node, auth):
    pass

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
    ostatus_l = [r.mon_overallstatus for r in rows if r.mon_updated is not None and r.mon_updated > tlim]
    astatus_l = [r.mon_availstatus for r in rows if r.mon_updated is not None and r.mon_updated > tlim]
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
    try:
        svctype = rows[0].mon_svctype
    except:
        svctype = 'TST'
    update_dash_service_unavailable(svcname, svctype, astatus)
    update_dash_service_available_but_degraded(svcname, svctype, astatus, ostatus)

    db(db.services.svc_name==svcname).update(
      svc_status=ostatus,
      svc_availstatus=astatus)
    db.commit()

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
            db.commit()
        else:
            db.services_log.insert(svc_name=svcname,
                                   svc_begin=prev.svc_end,
                                   svc_end=end,
                                   svc_availstatus=astatus)
            db.commit()
    else:
        db.services_log.insert(svc_name=svcname,
                               svc_begin=end,
                               svc_end=end,
                               svc_availstatus=astatus)
        db.commit()

def translate_encap_nodename(svcname, nodename):
    q = db.svcmon.mon_svcname == svcname
    q &= db.svcmon.mon_vmname == nodename
    q &= db.svcmon.mon_containerstatus == 'up'
    rows = db(q).select(db.svcmon.mon_nodname)
    if len(rows) != 1:
        # not encap ot vm started on multiple hv (pb)
        return nodename
    return rows.first().mon_nodname

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
    h['mon_nodname'] = translate_encap_nodename(h['mon_svcname'], h['mon_nodname'])
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
        _comet_send(json.dumps({
                     'nodename': h['mon_nodname'],
                     'svcname': h['mon_svcname'],
                     'table': 'svcmon',
                     'event': 'change'
                    }))
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
        _comet_send({'nodename': h['mon_nodname'],
                     'svcname': h['mon_svcname'],
                     'table': 'svcmon',
                     'event': 'change'})
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
        db.commit()
        if h['mon_overallstatus'] == 'warn':
            level = "warning"
        else:
            level = "info"
        _comet_send({'nodename': h['mon_nodname'],
                     'svcname': h['mon_svcname'],
                     'table': 'svcmon',
                     'event': 'change'})
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
        db.commit()

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
        qr = apply_filters(qr, fset.gen_filtersets.id, db.checks_live.chk_nodename, db.checks_live.chk_svcname)
        n = db(qr).count()
        if n == 0:
            continue
        return (fset.gen_filterset_check_threshold.chk_low,
                fset.gen_filterset_check_threshold.chk_high,
                'fset: '+fset.gen_filtersets.fset_name)
    return

def b_update_thresholds_batch():
    update_thresholds_batch()

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
        db.commit()
        return

    # try to find filter-match thresholds
    t = get_filters(row)
    if t is not None:
        db(db.checks_live.id==row.id).update(chk_low=t[0], chk_high=t[1], chk_threshold_provider=t[2])
        db.commit()
        return

    # try to find least precise settings (ie defaults)
    t = get_defaults(row)
    if t is not None:
        db(db.checks_live.id==row.id).update(chk_low=t[0], chk_high=t[1], chk_threshold_provider=t[2])
        db.commit()
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
# collector actions
#
def str_to_datetime(s):
    time_formats = ["%Y-%m-%d %H:%M:%S","%Y-%m-%d %H:%M","%Y-%m-%d", "%Y-%m"]
    d = None
    for t in time_formats:
       try:
           d = datetime.datetime.fromtimestamp(time.mktime(time.strptime(s, t)))
           break
       except:
           continue
    return d

@auth_uuid
@service.xmlrpc
def collector_ack_action(cmd, auth):
    d = {}
    nodename = auth[1]
    d["acked_date"] = datetime.datetime.now()

    if "svcname" in cmd:
        q = db.SVCactions.svcname == cmd["svcname"]
        q &= db.SVCactions.hostname == nodename
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%svcname}
        d["svcname"] = cmd["svcname"]

    if "id" not in cmd:
        return {"ret": 1, "msg": "no action id specified"}

    if "comment" not in cmd:
        d["acked_comment"] = "no comment"
    else:
        d["acked_comment"] = cmd["comment"]

    if "author" not in cmd:
        d["acked_by"] = "root@%s"%nodename
    else:
        d["acked_by"] = cmd["author"]

    q = db.SVCactions.status == "err"

    q1 = db.SVCactions.id == cmd['id']
    rows = db(q1).select()

    if len(rows) == 0:
        q &= q1
    else:
        if rows[0].status_log is None or rows[0].status_log == "":
            q &= db.SVCactions.hostname == rows[0].hostname
            q &= db.SVCactions.svcname == rows[0].svcname
            q &= ((db.SVCactions.pid.belongs(rows[0].pid.split(',')))|(db.SVCactions.id==rows[0].id))
            q &= db.SVCactions.begin >= rows[0].begin
            q &= db.SVCactions.end <= rows[0].end
        else:
            q &= q1

    if db(q).count() == 0:
        return {"ret": 1, "msg": "action id not found or not ackable"}

    db(q).update(ack=1,
                 acked_comment=d["acked_comment"],
                 acked_date=d["acked_date"],
                 acked_by=d["acked_by"])
    db.commit()

    update_action_errors(rows[0].svcname, nodename)
    update_dash_action_errors(rows[0].svcname, nodename)

    return {"ret": 0, "msg": ""}

@auth_uuid
@service.xmlrpc
def collector_ack_unavailability(cmd, auth):
    d = {}
    nodename = auth[1]
    d["mon_acked_on"] = datetime.datetime.now()

    if "svcname" not in cmd:
        return {"ret": 1, "msg": "svcname not found in command block"}
    else:
        q = db.svcmon.mon_svcname == cmd["svcname"]
        q &= db.svcmon.mon_nodname == nodename
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%svcname}
        d["mon_svcname"] = cmd["svcname"]

    if "begin" not in cmd:
        d["mon_begin"] = d["mon_acked_on"]
    else:
        d["mon_begin"] = str_to_datetime(cmd["begin"])
        if d["mon_begin"] is None:
            return {"ret": 1, "msg": "could not parse --begin as a date"}

    if "end" not in cmd:
        if "duration" in cmd:
            # todo: fancy duration parsing
            d["mon_end"] = d["mon_begin"] + datetime.timedelta(minutes=cmd["duration"])
        else:
            return {"ret": 1, "msg": "need either --end or --duration"}
    else:
        d["mon_end"] = str_to_datetime(cmd["end"])
        if d["mon_end"] is None:
            return {"ret": 1, "msg": "could not parse --end as a date"}

    if "comment" not in cmd:
        d["mon_comment"] = "no comment"
    else:
        d["mon_comment"] = cmd["comment"]

    if "author" not in cmd:
        d["mon_acked_by"] = "root@%s"%nodename
    else:
        d["mon_acked_by"] = cmd["author"]

    if "account" not in cmd:
        d["mon_account"] = "1"
    else:
        d["mon_account"] = cmd["account"]

    generic_insert('svcmon_log_ack', d.keys(), d.values())
    return {"ret": 0, "msg": ""}

@auth_uuid
@service.xmlrpc
def collector_list_unavailability_ack(cmd, auth):
    d = {}
    nodename = auth[1]
    d["mon_acked_on"] = datetime.datetime.now()

    if "svcname" not in cmd:
        return {"ret": 1, "msg": "svcname not found in command block"}
    else:
        q = db.svcmon.mon_svcname == cmd["svcname"]
        q &= db.svcmon.mon_nodname == nodename
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%svcname}

    q = db.svcmon_log_ack.mon_svcname == cmd["svcname"]

    if "begin" not in cmd:
        b = datetime.datetime.now() - datetime.timedelta(days=7)
    else:
        b = str_to_datetime(cmd["begin"])
        if b is None:
            return {"ret": 1, "msg": "could not parse --begin as a date"}
    q &= db.svcmon_log_ack.mon_end >= b

    if "end" not in cmd:
        e = datetime.datetime.now()
    else:
        e = str_to_datetime(cmd["end"])
        if e is None:
            return {"ret": 1, "msg": "could not parse --end as a date"}
    q &= db.svcmon_log_ack.mon_begin <= e

    if "comment" in cmd:
        if '%' in cmd["comment"]:
            q &= db.svcmon_log_ack.mon_comment.like(cmd["comment"])
        else:
            q &= db.svcmon_log_ack.mon_comment == cmd["comment"]

    if "author" in cmd:
        if '%' in cmd["author"]:
            q &= db.svcmon_log_ack.mon_acked_by.like(cmd["author"])
        else:
            q &= db.svcmon_log_ack.mon_acked_by == cmd["author"]

    if "account" in cmd:
        if cmd["account"]:
            q &= db.svcmon_log_ack.mon_account == 0
        else:
            q &= db.svcmon_log_ack.mon_account == 1

    rows = db(q).select()
    return {"ret": 0, "msg": "", "data":str(rows)}

@auth_uuid
@service.xmlrpc
def collector_show_actions(cmd, auth):
    d = {}
    nodename = auth[1]

    if "svcname" in cmd:
        q = db.svcmon.mon_svcname == cmd["svcname"]
        q &= db.svcmon.mon_nodname == nodename
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%svcname}

    if "svcname" in cmd:
        q = db.SVCactions.svcname == cmd["svcname"]
    else:
        q = db.SVCactions.hostname == nodename

    if "id" in cmd:
        q1 = db.SVCactions.id == cmd['id']
        rows = db(q1).select()
        if len(rows) == 0:
            q &= q1
        else:
            if rows[0].status_log is None or rows[0].status_log == "":
                q &= db.SVCactions.hostname == rows[0].hostname
                q &= db.SVCactions.svcname == rows[0].svcname
                q &= ((db.SVCactions.pid.belongs(rows[0].pid.split(',')))|(db.SVCactions.id==rows[0].id))
                q &= db.SVCactions.begin >= rows[0].begin
                q &= db.SVCactions.end <= rows[0].end
            else:
                q &= q1
    else:
        if "begin" not in cmd:
            b = datetime.datetime.now() - datetime.timedelta(days=7)
        else:
            b = str_to_datetime(cmd["begin"])
            if b is None:
                return {"ret": 1, "msg": "could not parse --begin as a date"}
        q &= db.SVCactions.end >= b

        if "end" not in cmd:
            e = datetime.datetime.now()
        else:
            e = str_to_datetime(cmd["end"])
            if e is None:
                return {"ret": 1, "msg": "could not parse --end as a date"}
        q &= db.SVCactions.begin <= e

    rows = db(q).select(db.SVCactions.id,
                        db.SVCactions.hostname,
                        db.SVCactions.svcname,
                        db.SVCactions.begin,
                        db.SVCactions.action,
                        db.SVCactions.status,
                        db.SVCactions.ack,
                        db.SVCactions.status_log,
                        orderby=db.SVCactions.id
                       )
    data = [["id", "hostname", "svcname", "begin", "action", "status", "ack", "log"]]
    for row in rows:
        data.append([str(row.id),
                     str(row.hostname),
                     str(row.svcname),
                     str(row.begin),
                     str(row.action),
                     str(row.status),
                     str(row.ack),
                     str(row.status_log)])
    return {"ret": 0, "msg": "", "data":data}

@auth_uuid
@service.xmlrpc
def collector_list_actions(cmd, auth):
    d = {}
    nodename = auth[1]
    d["mon_acked_on"] = datetime.datetime.now()

    if "svcname" in cmd:
        q = db.svcmon.mon_svcname == cmd["svcname"]
        q &= db.svcmon.mon_nodname == nodename
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%svcname}

    if "svcname" in cmd:
        q = db.SVCactions.svcname == cmd["svcname"]
    else:
        q = db.SVCactions.hostname == nodename

    if "begin" not in cmd:
        b = datetime.datetime.now() - datetime.timedelta(days=7)
    else:
        b = str_to_datetime(cmd["begin"])
        if b is None:
            return {"ret": 1, "msg": "could not parse --begin as a date"}
    q &= db.SVCactions.end >= b

    if "end" not in cmd:
        e = datetime.datetime.now()
    else:
        e = str_to_datetime(cmd["end"])
        if e is None:
            return {"ret": 1, "msg": "could not parse --end as a date"}
    q &= db.SVCactions.begin <= e

    q &= (db.SVCactions.status_log == "") | (db.SVCactions.status_log == None)
    rows = db(q).select(db.SVCactions.id,
                        db.SVCactions.hostname,
                        db.SVCactions.svcname,
                        db.SVCactions.begin,
                        db.SVCactions.end,
                        db.SVCactions.action,
                        db.SVCactions.status,
                        db.SVCactions.ack,
                        db.SVCactions.cron
                       )
    return {"ret": 0, "msg": "", "data":str(rows)}

@auth_uuid
@service.xmlrpc
def collector_status(cmd, auth):
    d = {}
    nodename = auth[1]

    if "svcname" in cmd:
        q = db.svcmon.mon_svcname == cmd["svcname"]
        q &= db.svcmon.mon_nodname == nodename
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%svcname}

    o = db.svcmon.mon_svcname
    q = db.svcmon.mon_nodname == db.nodes.nodename
    if "svcname" in cmd:
        q &= db.svcmon.mon_svcname == cmd["svcname"]
    else:
        rows = db(db.svcmon.mon_nodname==nodename).select(db.svcmon.mon_svcname)
        svcs = map(lambda x: x.mon_svcname, rows)
        if len(svcs) > 0:
            q &= db.svcmon.mon_svcname.belongs(svcs)
        else:
            q &= db.svcmon.id < 0
    rows = db(q).select(db.svcmon.mon_nodname,
                        db.svcmon.mon_svcname,
                        db.nodes.host_mode,
                        db.svcmon.mon_availstatus,
                        db.svcmon.mon_overallstatus,
                        db.svcmon.mon_updated,
                        orderby=o,
                        limitby=(0,100)
                       )
    return {"ret": 0, "msg": "", "data":str(rows)}

@auth_uuid
@service.xmlrpc
def collector_checks(cmd, auth):
    d = {}
    nodename = auth[1]

    if "svcname" in cmd:
        q = db.svcmon.mon_svcname == cmd["svcname"]
        q &= db.svcmon.mon_nodname == nodename
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%svcname}

    if "svcname" in cmd:
        q = db.checks_live.chk_svcname == cmd["svcname"]
    else:
        q = db.checks_live.chk_nodename == nodename

    rows = db(q).select(db.checks_live.chk_svcname,
                        db.checks_live.chk_instance,
                        db.checks_live.chk_type,
                        db.checks_live.chk_value,
                        db.checks_live.chk_low,
                        db.checks_live.chk_high,
                        db.checks_live.chk_threshold_provider,
                        db.checks_live.chk_created,
                        db.checks_live.chk_updated,
                        limitby=(0,1000)
                       )
    return {"ret": 0, "msg": "", "data":str(rows)}

@auth_uuid
@service.xmlrpc
def collector_alerts(cmd, auth):
    d = {}
    nodename = auth[1]

    if "svcname" in cmd:
        q = db.svcmon.mon_svcname == cmd["svcname"]
        q &= db.svcmon.mon_nodname == nodename
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%svcname}

    if "svcname" in cmd:
        where = "where dash_svcname='%s'"%cmd["svcname"]
    else:
        where = "where dash_nodename='%s'"%nodename

    labels = ["dash_severity", "dash_type", "dash_created", "dash_fmt", "dash_dict", "dash_nodename", "dash_svcname"]
    sql = """select %s from dashboard %s order by dash_severity desc limit 0,1000"""%(','.join(labels), where)
    rows = db.executesql(sql)
    data = [["dash_severity", "dash_type", "dash_nodename", "dash_svcname", "dash_alert", "dash_created"]]
    for row in rows:
        fmt = row[3]
        try:
            d = json.loads(row[4])
            alert = fmt%d
        except:
            alert = ""
        data += [[str(row[0]), str(row[1]), row[5], row[6], alert, str(row[2])]]
    return {"ret": 0, "msg": "", "data":data}

@auth_uuid
@service.xmlrpc
def collector_events(cmd, auth):
    d = {}
    nodename = auth[1]

    if "svcname" in cmd:
        q = db.svcmon.mon_svcname == cmd["svcname"]
        q &= db.svcmon.mon_nodname == nodename
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%svcname}

    if "svcname" in cmd:
        where = "where log_svcname='%s'"%cmd["svcname"]
    else:
        where = "where log_nodename='%s'"%nodename

    if "begin" not in cmd:
        b = datetime.datetime.now() - datetime.timedelta(days=7)
    else:
        b = str_to_datetime(cmd["begin"])
        if b is None:
            return {"ret": 1, "msg": "could not parse --begin as a date"}
    where += """ and log_date >= "%s" """%str(b)

    if "end" not in cmd:
        e = datetime.datetime.now()
    else:
        e = str_to_datetime(cmd["end"])
        if e is None:
            return {"ret": 1, "msg": "could not parse --end as a date"}
    where += """ and log_date <= "%s" """%str(e)

    labels = ["log_date", "log_nodename", "log_svcname", "log_level", "log_action", "log_fmt", "log_dict"]
    sql = """select %s from log %s order by log_date limit 0,1000"""%(','.join(labels), where)
    rows = db.executesql(sql)
    data = [["date", "nodename", "svcname", "level", "action", "event"]]
    for row in rows:
        fmt = row[5]
        try:
            d = json.loads(row[6])
            msg = fmt%d
        except:
            msg = ""
        data += [[str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(row[4]), msg]]
    return {"ret": 0, "msg": "", "data":data}

@auth_uuid
@service.xmlrpc
def collector_disks(cmd, auth):
    d = {}
    nodename = auth[1]

    if "svcname" in cmd:
        q = db.svcmon.mon_svcname == cmd["svcname"]
        q &= db.svcmon.mon_nodname == nodename
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%svcname}

    if "svcname" in cmd:
        q = db.b_disk_app.disk_svcname == cmd["svcname"]
    else:
        q = db.b_disk_app.disk_nodename == nodename

    o = db.b_disk_app.disk_id | db.b_disk_app.disk_svcname | db.b_disk_app.disk_nodename
    rows = db(q).select(db.b_disk_app.disk_nodename,
                        db.b_disk_app.disk_svcname,
                        db.b_disk_app.disk_id,
                        db.b_disk_app.disk_size,
                        db.b_disk_app.disk_alloc,
                        db.b_disk_app.disk_devid,
                        db.b_disk_app.disk_name,
                        db.b_disk_app.disk_raid,
                        db.b_disk_app.disk_arrayid,
                        db.b_disk_app.disk_group
                       )

    labels = ["nodename", "svcname", "id", "size", "alloc", "devid", "name", "raid", "arrayid", "group"]
    data = [labels]
    for row in rows:
        data += [[str(row.disk_nodename),
                  str(row.disk_svcname),
                  str(row.disk_id),
                  str(row.disk_size),
                  str(row.disk_alloc),
                  str(row.disk_devid),
                  str(row.disk_name),
                  str(row.disk_raid),
                  str(row.disk_arrayid),
                  str(row.disk_group)]]
    return {"ret": 0, "msg": "", "data":data}

@auth_uuid
@service.xmlrpc
def collector_list_nodes(cmd, auth):
    d = {}
    nodename = auth[1]
    if "fset" not in cmd:
        return {"ret": 1, "msg": "fset not specified"}
    fset = cmd['fset']
    q = db.gen_filtersets.fset_name == fset
    row = db(q).select().first()
    if row is None:
        return {"ret": 1, "msg": "filterset not found"}
    fset_id = row.id
    q = db.nodes.id > 0
    q = apply_filters(q, fset_id, db.nodes.nodename, None)
    rows = db(q).select(db.nodes.nodename, orderby=db.nodes.nodename)
    nodes = [r.nodename.lower() for r in rows]
    return {"ret": 0, "msg": "", "data": nodes}

@auth_uuid
@service.xmlrpc
def collector_list_services(cmd, auth):
    d = {}
    nodename = auth[1]
    if "fset" not in cmd:
        return {"ret": 1, "msg": "fset not specified"}
    fset = cmd['fset']
    q = db.gen_filtersets.fset_name == fset
    row = db(q).select().first()
    if row is None:
        return {"ret": 1, "msg": "filterset not found"}
    fset_id = row.id
    q = db.svcmon.mon_nodname == db.nodes.nodename
    q = apply_filters(q, fset_id, db.svcmon.mon_nodname, db.svcmon.mon_svcname)
    rows = db(q).select(db.svcmon.mon_svcname,
                        orderby=db.svcmon.mon_svcname,
                        groupby=db.svcmon.mon_svcname)
    services = [r.mon_svcname.lower() for r in rows]
    return {"ret": 0, "msg": "", "data": services}

@auth_uuid
@service.xmlrpc
def collector_list_filtersets(cmd, auth):
    d = {}
    nodename = auth[1]
    if "fset" in cmd and len(cmd['fset']) > 0:
        q = db.gen_filtersets.fset_name.like(cmd['fset'])
    else:
        q = db.gen_filtersets.id > 0
    rows = db(q).select(db.gen_filtersets.fset_name,
                        orderby=db.gen_filtersets.fset_name)
    fsets = [r.fset_name.lower() for r in rows]
    return {"ret": 0, "msg": "", "data": fsets}




#
# Dashboard updates
#
#   Used by background feed dequeue process for periodic dashboard alerts
#
def cron_dash_service_not_updated():
    sql = """insert
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
                 "",
                 svc_type,
                 "",
                 now()
               from services
               where updated < date_sub(now(), interval 25 hour)
               on duplicate key update
                 dash_updated=now()
          """
    db.executesql(sql)
    db.commit()

def cron_dash_svcmon_not_updated():
    sql = """select dashboard.id
             from dashboard
             left join svcmon on
               dashboard.dash_svcname=svcmon.mon_svcname and
               dashboard.dash_nodename=svcmon.mon_nodname
             where
               dashboard.dash_svcname!="" and
               dashboard.dash_nodename != "" and
               svcmon.id is NULL"""
    rows = db.executesql(sql)
    ids = map(lambda x: "'%d'"%x[0], rows)

    if len(ids) > 0:
        sql = """delete from dashboard
                 where
                   id in (%s)
              """%','.join(ids)
        db.executesql(sql)

    sql = """insert into dashboard
               select
                 NULL,
                 "service status not updated",
                 mon_svcname,
                 mon_nodname,
                 if(mon_svctype="PRD", 1, 0),
                 "",
                 "",
                 mon_updated,
                 "",
                 mon_svctype,
                 "",
                 now()
               from svcmon
               where mon_updated < date_sub(now(), interval 16 minute)
               on duplicate key update
                 dash_updated=now()
          """
    db.executesql(sql)
    db.commit()

def cron_dash_node_not_updated():
    sql = """insert into dashboard
               select
                 NULL,
                 "node information not updated",
                 "",
                 nodename,
                 0,
                 "",
                 "",
                 updated,
                 "",
                 host_mode,
                 "",
                 now()
               from nodes
               where updated < date_sub(now(), interval 25 hour)
               on duplicate key update
                 dash_updated=now()
          """
    db.executesql(sql)
    db.commit()

def cron_dash_node_without_asset():
    sql = """insert into dashboard
               select
                 NULL,
                 "node without asset information",
                 "",
                 mon_nodname,
                 0,
                 "",
                 "",
                 now(),
                 "",
                 mon_svctype,
                 "",
                 now()
               from svcmon
               where
                 mon_nodname not in (
                   select nodename from nodes
                 )
               on duplicate key update
                 dash_updated=now()
          """
    db.executesql(sql)
    db.commit()

def cron_dash_node_beyond_maintenance_date():
    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)

    sql = """insert into dashboard
               select
                 NULL,
                 "node maintenance expired",
                 "",
                 nodename,
                 1,
                 "",
                 "",
                 "%(now)s",
                 "",
                 host_mode,
                 "",
                 "%(now)s"
               from nodes
               where
                 maintenance_end is not NULL and
                 maintenance_end != "0000-00-00 00:00:00" and
                 maintenance_end < now()
               on duplicate key update
                 dash_updated="%(now)s"
          """%dict(now=str(now))
    db.executesql(sql)
    db.commit()

    sql = """delete from dashboard where
               dash_type="node maintenance expired" and
               (
                 dash_updated < "%(now)s" or
                 dash_updated is null
               )
          """%dict(now=str(now))
    db.executesql(sql)


def cron_dash_node_near_maintenance_date():
    sql = """insert into dashboard
               select
                 NULL,
                 "node close to maintenance end",
                 "",
                 nodename,
                 0,
                 "",
                 "",
                 now(),
                 "",
                 host_mode,
                 "",
                 now()
               from nodes
               where
                 maintenance_end is not NULL and
                 maintenance_end != "0000-00-00 00:00:00" and
                 maintenance_end > date_sub(now(), interval 30 day) and
                 maintenance_end < now()
               on duplicate key update
                 dash_updated=now()
          """
    db.commit()
    db.executesql(sql)

def cron_dash_node_without_maintenance_date():
    # do not alert for nodes under warranty
    sql = """insert into dashboard
               select
                 NULL,
                 "node without maintenance end date",
                 "",
                 nodename,
                 0,
                 "",
                 "",
                 now(),
                 "",
                 host_mode,
                 "",
                 now()
               from nodes
               where
                 (warranty_end is NULL or
                  warranty_end = "0000-00-00 00:00:00" or
                  warranty_end < now()) and
                 (maintenance_end is NULL or
                  maintenance_end = "0000-00-00 00:00:00") and
                 model not like "%virt%" and
                 model not like "%Not Specified%" and
                 model not like "%KVM%"
               on duplicate key update
                 dash_updated=now()
          """
    db.executesql(sql)
    db.commit()

def cron_dash_checks_not_updated():
    sql = """delete from dashboard
             where
               dash_type="check value not updated"
               and dash_nodename not in (
                 select distinct chk_nodename from checks_live
               )
          """
    rows = db.executesql(sql)

    sql = """select d.id from dashboard d
             left join checks_live c on
               d.dash_dict_md5=md5(concat(
                 '{"ctype": "', c.chk_type,
                 '", "inst": "', c.chk_instance,
                 '", "ttype": "', c.chk_threshold_provider,
                 '", "val": ', c.chk_value,
                 ', "min": ', c.chk_low,
                 ', "max": ', c.chk_high, '}'))
               and d.dash_nodename=c.chk_nodename
             where
               d.dash_type="check out of bounds"
               and c.id is NULL
          """
    rows = db.executesql(sql)
    ids = map(lambda x: str(x[0]), rows)
    if len(ids) > 0:
        sql = """delete from dashboard where id in (%s)"""%','.join(ids)
        db.executesql(sql)

    sql = """select d.id from dashboard d
             left join checks_live c on
               d.dash_dict_md5=md5(concat('{"i":"', c.chk_instance, '", "t":"', c.chk_type, '"}'))
               and d.dash_nodename=c.chk_nodename
             where
               d.dash_type="check value not updated"
               and c.id is NULL
          """
    rows = db.executesql(sql)
    ids = map(lambda x: str(x[0]), rows)
    if len(ids) > 0:
        sql = """delete from dashboard where id in (%s)"""%','.join(ids)
        db.executesql(sql)

    sql = """insert into dashboard
               select
                 NULL,
                 "check value not updated",
                 "",
                 c.chk_nodename,
                 if(n.host_mode="PRD", 1, 0),
                 "%(t)s:%(i)s",
                 concat('{"i":"', chk_instance, '", "t":"', chk_type, '"}'),
                 chk_updated,
                 md5(concat('{"i":"', chk_instance, '", "t":"', chk_type, '"}')),
                 n.host_mode,
                 "",
                 now()
               from checks_live c
                 join nodes n on c.chk_nodename=n.nodename
               where
                 chk_updated < date_sub(now(), interval 1 day)
               on duplicate key update
                 dash_updated=now()"""
    db.executesql(sql)
    db.commit()

def cron_dash_app_without_responsible():
    sql = """delete from dashboard where
             dash_type="application code without responsible" and
             dash_dict in (
               select
                 concat('{"a":"', app, '"}')
               from v_apps
               where
                 roles is not NULL
             ) or dash_dict = "" or dash_dict is NULL
          """
    db.executesql(sql)

    sql = """insert into dashboard
               select
                 NULL,
                 "application code without responsible",
                 "",
                 "",
                 2,
                 "%(a)s",
                 concat('{"a":"', app, '"}'),
                 now(),
                 md5(concat('{"a":"', app, '"}')),
                 "",
                 "",
                 now()
               from v_apps
               where
                 roles is NULL
               on duplicate key update
                 dash_updated=now()
          """
    db.executesql(sql)
    db.commit()

def cron_dash_purge():
    sql = """delete from dashboard where
              dash_svcname != "" and
              dash_svcname not in (
                select distinct mon_svcname from svcmon
              )
          """
    db.executesql(sql)
    db.commit()

def cron_dash_obs_purge():
    sql = """delete from dashboard
             where dash_type like "%obsolescence%"
          """
    db.executesql(sql)
    db.commit()

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
    sql = """insert into dashboard
               select
                 NULL,
                 "%(tl)s obsolescence %(al)s date not set",
                 "",
                 n.nodename,
                 0,
                 "%(t)s: %%(o)s",
                 concat('{"o": "', o.obs_name, '"}'),
                 now(),
                 md5(concat('{"o": "', o.obs_name, '"}')),
                 "",
                 "",
                 now()
               from obsolescence o
                 join nodes n on
                   o.obs_name = n.model or
                   o.obs_name = concat_ws(' ',n.os_name,n.os_vendor,n.os_release,n.os_update)
               where
                 o.obs_type = "%(t)s" and
                 o.obs_name not like "%%virtual%%" and
                 o.obs_name not like "%%virtuel%%" and
                 o.obs_name not like "%%cluster%%" and
                 (
                   o.obs_%(a)s_date is NULL or
                   o.obs_%(a)s_date = "0000-00-00 00:00:00"
                 )
               on duplicate key update
                 dash_updated=now()
          """%dict(t=t, tl=tl, a=a, al=al)
    db.executesql(sql)
    db.commit()

def cron_dash_obs_os_alert():
    sql = """insert into dashboard
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
                 "",
                 "",
                 "",
                 now()
               from obsolescence o
                 join nodes n on
                   o.obs_name = concat_ws(' ',n.os_name,n.os_vendor,n.os_release,n.os_update)
               where
                 o.obs_alert_date is not NULL and
                 o.obs_alert_date != "0000-00-00 00:00:00" and
                 o.obs_alert_date < now() and
                 o.obs_type = "os"
               on duplicate key update
                 dash_updated=now()
          """
    db.executesql(sql)
    db.commit()

def cron_dash_obs_os_warn():
    sql = """insert into dashboard
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
                 "",
                 "",
                 "",
                 now()
               from obsolescence o
                 join nodes n on
                   o.obs_name = concat_ws(' ',n.os_name,n.os_vendor,n.os_release,n.os_update)
               where
                 o.obs_alert_date is not NULL and
                 o.obs_alert_date != "0000-00-00 00:00:00" and
                 o.obs_warn_date < now() and
                 o.obs_alert_date > now() and
                 o.obs_type = "os"
               on duplicate key update
                 dash_updated=now()
          """
    db.executesql(sql)
    db.commit()

def cron_dash_obs_hw_alert():
    sql = """insert into dashboard
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
                 "",
                 "",
                 "",
                 now()
               from obsolescence o
                 join nodes n on
                   o.obs_name = n.model
               where
                 o.obs_name not like "%virtual%" and
                 o.obs_name not like "%virtuel%" and
                 o.obs_name not like "%cluster%" and
                 o.obs_alert_date is not NULL and
                 o.obs_alert_date != "0000-00-00 00:00:00" and
                 o.obs_alert_date < now() and
                 o.obs_type = "hw"
               on duplicate key update
                 dash_updated=now()
          """
    db.executesql(sql)
    db.commit()

def cron_dash_obs_hw_warn():
    sql = """insert into dashboard
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
                 "",
                 "",
                 "",
                 now()
               from obsolescence o
                 join nodes n on
                   o.obs_name = n.model
               where
                 o.obs_name not like "%virtual%" and
                 o.obs_name not like "%virtuel%" and
                 o.obs_name not like "%cluster%" and
                 o.obs_alert_date is not NULL and
                 o.obs_alert_date != "0000-00-00 00:00:00" and
                 o.obs_warn_date < now() and
                 o.obs_alert_date > now() and
                 o.obs_type = "hw"
               on duplicate key update
                 dash_updated=now()
          """
    db.executesql(sql)
    db.commit()

def cron_dash_action_errors_cleanup():
    sql = """delete from dashboard
             where
               dash_dict='{"err": "0"}' and
               dash_type='action errors'
          """
    db.executesql(sql)
    db.commit()
#
# Dashboard updates
#
#   Used by xmlrpc processors for event based dashboard alerts
#
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
                     maintenance_end < now()
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
                     maintenance_end > now() and
                     maintenance_end < date_sub(now(), interval 30 day)
                 ) and
                 dash_type = "node maintenance expired"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)
    db.commit()

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
    db.commit()

def update_dash_node_without_maintenance_end(nodename):
    sql = """delete from dashboard
               where
                 dash_nodename in (
                   select nodename
                   from nodes
                   where
                     nodename="%(nodename)s" and
                     ((maintenance_end != "0000-00-00 00:00:00" and
                       maintenance_end is not NULL) or
                       model like "%%virt%%" or
                       model like "%%Not Specified%%" or
                       model like "%%KVM%%")
                 ) and
                 dash_type = "node without maintenance end date"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)
    db.commit()

def update_dash_service_not_updated(svcname):
    sql = """delete from dashboard
               where
                 dash_svcname = "%(svcname)s" and
                 dash_type = "service configuration not updated"
          """%dict(svcname=svcname)
    rows = db.executesql(sql)
    db.commit()

def update_dash_svcmon_not_updated(svcname, nodename):
    sql = """delete from dashboard
               where
                 dash_svcname = "%(svcname)s" and
                 dash_nodename = "%(nodename)s" and
                 dash_type = "service status not updated"
          """%dict(svcname=svcname, nodename=nodename)
    rows = db.executesql(sql)
    db.commit()

def update_dash_node_not_updated(nodename):
    sql = """delete from dashboard
               where
                 dash_nodename = "%(nodename)s" and
                 dash_type = "node information not updated"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)
    db.commit()

def update_dash_pkgdiff(nodename):
    nodename = nodename.strip("'")
    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)

    q = db.svcmon.mon_nodname == nodename
    q &= db.svcmon.mon_updated > datetime.datetime.now() - datetime.timedelta(minutes=20)
    rows = db(q).select(db.svcmon.mon_svcname, db.svcmon.mon_svctype)
    svcnames = map(lambda x: x.mon_svcname, rows)

    for row in rows:
        svcname = row.mon_svcname

        q = db.svcmon.mon_svcname == svcname
        q &= db.svcmon.mon_updated > datetime.datetime.now() - datetime.timedelta(minutes=20)
        nodes = map(lambda x: repr(x.mon_nodname),
                    db(q).select(db.svcmon.mon_nodname,
                                 orderby=db.svcmon.mon_nodname))
        n = len(nodes)

        if n < 2:
            continue

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

        skip = 0
        trail = ""
        while True:
            nodes_s = ','.join(nodes).replace("'", "")+trail
            if len(nodes_s) < 50:
                break
            skip += 1
            nodes = nodes[:-1]
            trail = ", ... (+%d)"%skip

        sql = """insert into dashboard
                 set
                   dash_type="package differences in cluster",
                   dash_svcname="%(svcname)s",
                   dash_nodename="",
                   dash_severity=%(sev)d,
                   dash_fmt="%%(n)s package differences in cluster %%(nodes)s",
                   dash_dict='{"n": %(n)d, "nodes": "%(nodes)s"}',
                   dash_dict_md5=md5('{"n": %(n)d, "nodes": "%(nodes)s"}'),
                   dash_created="%(now)s",
                   dash_updated="%(now)s",
                   dash_env="%(env)s"
                 on duplicate key update
                   dash_updated="%(now)s"
              """%dict(svcname=svcname,
                       now=str(now),
                       sev=sev,
                       env=row.mon_svctype,
                       n=rows[0][0],
                       nodes=nodes_s)

        rows = db.executesql(sql)
        db.commit()

    # clean old
    q = db.dashboard.dash_svcname.belongs(svcnames)
    q &= db.dashboard.dash_type == "package differences in cluster"
    q &= db.dashboard.dash_updated < now
    db(q).delete()
    db.commit()


def update_dash_flex_cpu(svcname):
    sql = """delete from dashboard
               where
                 dash_svcname = "%(svcname)s" and
                 dash_type = "flex error" and
                 dash_fmt like "%%average cpu usage%%"
          """%dict(svcname=svcname)
    rows = db.executesql(sql)
    db.commit()

    sql = """select svc_type from services
             where
               svc_name="%(svcname)s"
          """%dict(svcname=svcname)
    rows = db.executesql(sql)

    if len(rows) == 0:
        return
    elif len(rows) == 1 and rows[0][0] == 'PRD':
        sev = 4
    else:
        sev = 3

    sql = """insert into dashboard
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
                        '}')),
                 "%(env)s",
                 "",
                 now()
               from (
                 select *
                 from v_flex_status
                 where
                   svc_name="%(svcname)s" and
                   up > 0 and
                   (
                     (
                       svc_flex_cpu_high_threshold > 0 and
                       cpu > svc_flex_cpu_high_threshold
                     ) or
                     (
                       svc_flex_cpu_low_threshold > 0 and
                       cpu < svc_flex_cpu_low_threshold
                     )
                   )
               ) t
               on duplicate key update
                 dash_updated=now()
          """%dict(svcname=svcname,
                   sev=sev,
                   env=rows[0][0],
                  )
    db.executesql(sql)
    db.commit()

def update_dash_flex_instances_started(svcname):
    sql = """delete from dashboard
               where
                 dash_svcname = "%(svcname)s" and
                 dash_type = "flex error" and
                 dash_fmt like "%%instances started%%"
          """%dict(svcname=svcname)
    rows = db.executesql(sql)
    db.commit()

    sql = """select svc_type from services
             where
               svc_name="%(svcname)s"
          """%dict(svcname=svcname)
    rows = db.executesql(sql)

    if len(rows) == 1 and rows[0][0] == 'PRD':
        sev = 2
    elif len(rows) == 0:
        return
    else:
        sev = 1

    sql = """insert into dashboard
               select
                 NULL,
                 "flex error",
                 "%(svcname)s",
                 "",
                 %(sev)d,
                 "%%(n)d instances started. thresholds: %%(smin)d - %%(smax)d",
                 concat('{"n": ', t.up,
                        ', "smin": ', t.svc_flex_min_nodes,
                        ', "smax": ', t.svc_flex_max_nodes,
                        '}'),
                 now(),
                 md5(concat('{"n": ', t.up,
                        ', "smin": ', t.svc_flex_min_nodes,
                        ', "smax": ', t.svc_flex_max_nodes,
                        '}')),
                 "%(env)s",
                 "",
                 now()
               from (
                 select *
                 from v_flex_status
                 where
                   svc_name="%(svcname)s" and
                   ((
                     svc_flex_min_nodes > 0 and
                     up < svc_flex_min_nodes
                   ) or
                   (
                     svc_flex_max_nodes > 0 and
                     up > svc_flex_max_nodes
                   ))
               ) t
               on duplicate key update
                 dash_updated=now()
          """%dict(svcname=svcname,
                   sev=sev,
                   env=rows[0][0],
                  )
    db.executesql(sql)
    db.commit()

def update_dash_checks_all():
    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)

    sql = """insert into dashboard
               select
                 NULL,
                 "check out of bounds",
                 t.svcname,
                 t.nodename,
                 if (t.host_mode="PRD", 3, 2),
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
                 t.host_mode,
                 "",
                 "%(now)s"
               from (
                 select
                   c.chk_svcname as svcname,
                   c.chk_nodename as nodename,
                   c.chk_type as ctype,
                   c.chk_instance as inst,
                   c.chk_threshold_provider as ttype,
                   c.chk_value as val,
                   c.chk_low as min,
                   c.chk_high as max,
                   n.host_mode
                 from checks_live c left join nodes n on c.chk_nodename=n.nodename
                 where
                   c.chk_updated >= date_sub(now(), interval 1 day) and
                   (
                     c.chk_value < c.chk_low or
                     c.chk_value > c.chk_high
                   )
               ) t
               on duplicate key update
                 dash_updated="%(now)s"
          """%dict(now=str(now))
    db.executesql(sql)
    db.commit()

    sql = """delete from dashboard
               where
                 (
                   (
                     dash_type = "check out of bounds" and
                     ( dash_updated < "%(now)s" or dash_updated is null )
                   ) or
                   dash_type = "check value not updated"
                 )
          """%dict(now=str(now))

    rows = db.executesql(sql)
    db.commit()

def update_dash_checks(nodename):
    nodename = nodename.strip("'")
    sql = """select host_mode from nodes
             where
               nodename="%(nodename)s"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)

    if len(rows) == 1 and rows[0][0] == 'PRD':
        sev = 3
    else:
        sev = 2

    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)

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
                   env=rows[0][0],
                   now=str(now),
                  )
    db.executesql(sql)
    db.commit()

    sql = """delete from dashboard
               where
                 dash_nodename = "%(nodename)s" and
                 (
                   (
                     dash_type = "check out of bounds" and
                     ( dash_updated < "%(now)s" or dash_updated is null )
                   ) or
                   dash_type = "check value not updated"
                 )
          """%dict(nodename=nodename, now=str(now))

    rows = db.executesql(sql)
    db.commit()

def update_dash_netdev_errors(nodename):
    nodename = nodename.strip("'")
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)
    sql = """select dev, sum(rxerrps+txerrps+collps+rxdropps+rxdropps) as errs
               from stats_netdev_err
               where
                 nodename = "%(nodename)s" and
                 date > date_sub(now(), interval 1 day)
               group by dev
          """%dict(nodename=nodename)
    rows = db.executesql(sql, as_dict=True)

    if len(rows) == 0:
        sql = """delete from checks_live
                 where
                  chk_nodename="%(nodename)s" and
                  chk_type = "netdev_err"
              """
        db.executesql(sql)
        return

    for row in rows:
        sql = """insert into checks_live
                 set
                   chk_type="netdev_err",
                   chk_svcname="",
                   chk_nodename="%(nodename)s",
                   chk_value=%(errs)d,
                   chk_updated="%(now)s",
                   chk_instance="%(dev)s"
                 on duplicate key update
                   chk_type="netdev_err",
                   chk_svcname="",
                   chk_nodename="%(nodename)s",
                   chk_value=%(errs)d,
                   chk_updated="%(now)s",
                   chk_instance="%(dev)s"
              """%dict(nodename=nodename,
                       now=now,
                       dev=row['dev'],
                       errs=int(row['errs']))
        db.executesql(sql)

    sql = """delete from checks_live
             where
               chk_type="netdev_err" and
               chk_updated < "%(now)s" and
               chk_nodename="%(nodename)s"
          """%dict(nodename=nodename,
                   now=now,
                  )
    db.executesql(sql)
    db.commit()

    q = db.checks_live.chk_nodename == nodename
    q &= db.checks_live.chk_type == "netdev_err"
    checks = db(q).select()
    update_thresholds_batch(checks)

    update_dash_checks(nodename)


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
            sev = 4
        else:
            sev = 3
        sql = """insert into dashboard
                 set
                   dash_type="action errors",
                   dash_svcname="%(svcname)s",
                   dash_nodename="%(nodename)s",
                   dash_severity=%(sev)d,
                   dash_fmt="%%(err)s action errors",
                   dash_dict='{"err": "%(err)d"}',
                   dash_created=now(),
                   dash_updated=now(),
                   dash_env="%(env)s"
                 on duplicate key update
                   dash_severity=%(sev)d,
                   dash_fmt="%%(err)s action errors",
                   dash_dict='{"err": "%(err)d"}',
                   dash_updated=now(),
                   dash_env="%(env)s"
              """%dict(svcname=svc_name,
                       nodename=nodename,
                       sev=sev,
                       env=rows[0][1],
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
    db.commit()

def update_dash_service_available_but_degraded(svc_name, svc_type, svc_availstatus, svc_status):
    if svc_type == 'PRD':
        sev = 3
    else:
        sev = 2
    if svc_availstatus == "up" and svc_status != "up":
        sql = """delete from dashboard
                 where
                   dash_type="service available but degraded" and
                   dash_dict!='{"s": "%s"}' and
                   dash_svcname="%s"
              """%(svc_name,svc_status)
        db.executesql(sql)
        db.commit()
        sql = """insert into dashboard
                 set
                   dash_type="service available but degraded",
                   dash_svcname="%(svcname)s",
                   dash_nodename="",
                   dash_severity=%(sev)d,
                   dash_fmt="current overall status: %%(s)s",
                   dash_dict='{"s": "%(status)s"}',
                   dash_created=now(),
                   dash_updated=now(),
                   dash_env="%(env)s"
                 on duplicate key update
                   dash_severity=%(sev)d,
                   dash_fmt="current overall status: %%(s)s",
                   dash_updated=now(),
                   dash_env="%(env)s"
              """%dict(svcname=svc_name,
                       sev=sev,
                       env=svc_type,
                       status=svc_status)
        db.executesql(sql)
        db.commit()
    else:
        sql = """delete from dashboard
                 where
                   dash_type="service available but degraded" and
                   dash_svcname="%s"
              """%svc_name
        db.executesql(sql)
        db.commit()

def update_dash_service_unavailable(svc_name, svc_type, svc_availstatus):
    if svc_type == 'PRD':
        sev = 4
    else:
        sev = 3
    if svc_availstatus in ["up", "n/a"]:
        sql = """delete from dashboard
                 where
                   dash_type="service unavailable" and
                   dash_svcname="%s"
              """%svc_name
        db.executesql(sql)
        db.commit()
    else:
        sql = """select count(id) from svcmon_log_ack
                 where
                   mon_svcname="%s" and
                   mon_begin <= now() and
                   mon_end >= now()
              """%(svc_name)
        n = db.executesql(sql)[0][0]
        if n > 0:
            sql = """delete from dashboard
                     where
                       dash_type="service unavailable" and
                       dash_svcname="%s"
                  """%(svc_name)
            db.executesql(sql)
            db.commit()
            return

        sql = """delete from dashboard
                 where
                   dash_type="service unavailable" and
                   dash_svcname="%s" and
                   dash_dict!='{"s": "%s"}'
              """%(svc_name,svc_availstatus)
        db.executesql(sql)
        db.commit()

        sql = """insert into dashboard
                 set
                   dash_type="service unavailable",
                   dash_svcname="%(svcname)s",
                   dash_nodename="",
                   dash_severity=%(sev)d,
                   dash_fmt="current availability status: %%(s)s",
                   dash_dict='{"s": "%(status)s"}',
                   dash_created=now(),
                   dash_updated=now(),
                   dash_env="%(env)s"
                 on duplicate key update
                   dash_severity=%(sev)d,
                   dash_fmt="current availability status: %%(s)s",
                   dash_updated=now(),
                   dash_env="%(env)s"
              """%dict(svcname=svc_name,
                       sev=sev,
                       env=svc_type,
                       status=svc_availstatus)
        db.executesql(sql)
        db.commit()

def update_dash_service_frozen(svc_name, nodename, svc_type, frozen):
    if svc_type == 'PRD':
        sev = 2
    else:
        sev = 1
    if frozen == "0":
        sql = """delete from dashboard
                 where
                   dash_type="service frozen" and
                   dash_svcname="%s"
              """%svc_name
        db.commit()
    else:
        sql = """insert into dashboard
                 set
                   dash_type="service frozen",
                   dash_svcname="%(svcname)s",
                   dash_nodename="%(nodename)s",
                   dash_severity=%(sev)d,
                   dash_fmt="",
                   dash_dict="",
                   dash_created=now(),
                   dash_updated=now(),
                   dash_env="%(env)s"
                 on duplicate key update
                   dash_severity=%(sev)d,
                   dash_fmt="",
                   dash_updated=now(),
                   dash_env="%(env)s"
              """%dict(svcname=svc_name,
                       nodename=nodename,
                       sev=sev,
                       env=svc_type,
                      )
    db.executesql(sql)
    db.commit()

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

    if rows[0].svc_autostart != nodename or \
       availstatus == "up" or \
       rows[0].svc_availstatus != "up" or \
       rows[0].svc_autostart is None or \
       rows[0].svc_autostart == "":
        sql = """delete from dashboard
                 where
                   dash_type="service not started on primary node" and
                   dash_svcname="%s"
              """%svc_name
        db.executesql(sql)
        return

    sql = """insert into dashboard
             set
               dash_type="service not started on primary node",
               dash_svcname="%(svcname)s",
               dash_nodename="%(nodename)s",
               dash_severity=%(sev)d,
               dash_fmt="",
               dash_dict="",
               dash_created=now(),
               dash_updated=now(),
               dash_env="%(env)s"
             on duplicate key update
               dash_severity=%(sev)d,
               dash_fmt="",
               dash_updated=now(),
               dash_env="%(env)s"

          """%dict(svcname=svc_name,
                   nodename=nodename,
                   sev=sev,
                   env=svc_type,
                  )
    db.executesql(sql)
    db.commit()

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
    db.commit()

def dash_crons2():
    # ~1/j
    cron_dash_purge()
    cron_dash_obs_purge()
    cron_dash_obs_os_alert()
    cron_dash_obs_os_warn()
    cron_dash_obs_hw_alert()
    cron_dash_obs_hw_warn()
    cron_dash_obs_os_without_alert()
    cron_dash_obs_os_without_warn()
    cron_dash_obs_hw_without_alert()
    cron_dash_obs_hw_without_warn()
    cron_dash_node_without_maintenance_date()
    cron_dash_node_near_maintenance_date()
    cron_dash_node_beyond_maintenance_date()

def dash_crons1():
    # ~1/h
    cron_dash_checks_not_updated()
    cron_dash_service_not_updated()
    cron_dash_app_without_responsible()
    cron_dash_node_not_updated()
    cron_dash_node_without_asset()
    cron_dash_action_errors_cleanup()

def dash_crons0():
    # ~1/min
    cron_dash_svcmon_not_updated()

def feed_dequeue():
    """ launched as a background process
    """
    import time
    import cPickle
    import multiprocessing

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

        def get_total_seconds(self, td):
            return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 1e6) / 1e6

        def begin(self, fn):
            self.fn = fn
            self.t = datetime.datetime.now()

        def end(self):
            elapsed = datetime.datetime.now() -self.t
            elapsed = self.get_total_seconds(elapsed)
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
    workers = {}
    queues = {}

    import sys
    import logging
    import copy
    import traceback
    from gluon.shell import exec_environment

    log = logging.getLogger('sched')
    #logfile = "/tmp/feed_dequeue.log"
    #logfilehandler = logging.FileHandler(logfile)
    #logfilehandler.setFormatter(logformatter)
    #log.addHandler(logfilehandler)
    log.setLevel(logging.INFO)
    log.info("logger initialized")

    def dequeue_process(name, queue):
        log = logging.getLogger(name)
        log.info("init")
        try:
            _dequeue_process(name, queue)
        except KeyboardInterrupt:
             log.error("exit on KeyboardInterrupt")

    def _dequeue_process(name, queue):
        log = logging.getLogger('sched.'+name)

        m = exec_environment('applications/feed/models/db.py')
        global db
        db = m.db
        log.info("db loaded")
        while True:
            sys.stdout.flush()
            data = queue.get()
            if data is None or type(data) != tuple or len(data) != 3:
                log.info("got poison pill")
                break
            id, fn, args = data
            log.info('process %s %s'%(id, fn))
            if not fn in globals():
                log.error("%s not found in globals"%fn)
                continue
            try:
                args = cPickle.loads(args)
                globals()[fn](*args)
                db(db.feed_queue.id==id).delete()
                db.commit()
            except:
                log.error("%s(%s)"%(fn, str(args)))
                traceback.print_exc()
                return
            if queue.empty():
                log.info("stop idle process")
                break

    do_break = False
    e = None
    last = 0

    while True:
        if do_break:
            break
        n0 += 1
        n1 += 1
        n2 += 1

        try:
            if n0 == 90:
                n0 = 0
                dash_crons0()
            elif n1 == 3600:
                n1 = 0
                dash_crons1()
            elif n2 == 86400:
                n2 = 0
                dash_crons2()
        except:
            traceback.print_exc()


        try:
            #log.info(".")
            db.commit()
            queues_empty = True
            for q in queues.values():
                if not q.empty():
                    queues_empty = False
                    break
            if last > 0 and queues_empty and n0 == 0 and db(db.feed_queue.id<last).count() > 0:
                # once in a while, if queues are empty, retry errored entries
                entries = db(db.feed_queue.id<last).select(limitby=(0,20), orderby=db.feed_queue.id)
                if len(entries) > 0:
                    log.info("got %d stalled entries to dequeue"% len(entries))
            else:
                # don't fetch already scheduled entries
                entries = db(db.feed_queue.id>last).select(limitby=(0,20), orderby=db.feed_queue.id)
                if len(entries) > 0:
                    log.info("got %d entries to dequeue"% len(entries))
        except:
            # lost mysql ?
            traceback.print_exc()
            log.error("lost mysql ? sleep 10 sec")
            try: time.sleep(10)
            except KeyboardInterrupt: break
            continue

        if len(entries) == 0:
            try: time.sleep(1)
            except KeyboardInterrupt: break
            continue
        #elif n1 % 5 == 0:
            # every 100 xmlrpc calls save stats
        #    stats.dbdump()

        for w in copy.copy(workers.keys()):
            if not workers[w].is_alive():
                workers[w].join()
                del(workers[w])

        for e in entries:
            try:
                log.info("dequeue %s (id=%d)" % (e.q_fn, e.id))
                if e.q_fn in workers and not workers[e.q_fn].is_alive():
                    # clean up dead processes, so we can restart them
                    workers[e.q_fn].join()
                    del(workers[e.q_fn])
                if e.q_fn not in workers:
                    log.info("start %s worker" % e.q_fn)
                    queues[e.q_fn] = multiprocessing.Queue()
                    workers[e.q_fn] = multiprocessing.Process(target=dequeue_process, args=(e.q_fn, queues[e.q_fn]))
                    workers[e.q_fn].start()
                queues[e.q_fn].put((e.id, e.q_fn, e.q_args), block=True)
                if e.id > last:
                    last = e.id
            except KeyboardInterrupt:
                for fn in workers:
                    queues[fn].put(None)
                    workers[fn].join()
                do_break = True
                break
