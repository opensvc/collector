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
import os
import logging

from applications.init.modules import timeseries

R_DAEMON_STATUS_HASH = "osvc:h:daemon_status"
R_DAEMON_STATUS_CHANGES_HASH = "osvc:h:daemon_status_changes"
R_DAEMON_STATUS = "osvc:q:daemon_status"
R_DAEMON_PING = "osvc:q:daemon_ping"
R_PACKAGES_HASH = "osvc:h:packages"
R_PACKAGES = "osvc:q:packages"
R_PATCHES_HASH = "osvc:h:patches"
R_PATCHES = "osvc:q:patches"
R_RESINFO_HASH = "osvc:h:resinfo"
R_RESINFO = "osvc:q:resinfo"
R_SVCMON_UPDATE = "osvc:q:svcmon_update"
R_SYSREPORT = "osvc:q:sysreport"
R_ASSET_HASH = "osvc:h:asset"
R_ASSET = "osvc:q:asset"
R_SVCCONF_HASH = "osvc:h:svcconf"
R_SVCCONF = "osvc:q:svcconf"
R_GENERIC = "osvc:q:generic"
R_CHECKS_HASH = "osvc:h:checks"
R_CHECKS = "osvc:q:checks"
R_UPDATE_DASH_NETDEV_ERRORS = "osvc:q:update_dash_netdev_errors"
R_SVCMON = "osvc:q:svcmon"
R_SVCACTIONS = "osvc:q:svcactions"
R_STORAGE = "osvc:q:storage"

stats_options = {
    "cpu": {
        "discard": ["nodename"],
        "sub": "cpu",
        "datecol": "date",
    },
    "fs_u": {
        "discard": ["nodename"],
        "sub": "mntpt",
        "datecol": "date",
    },
    "mem_u": {
        "discard": ["nodename"],
        "datecol": "date",
    },
    "swap": {
        "discard": ["nodename"],
        "datecol": "date",
    },
    "proc": {
        "discard": ["nodename"],
        "datecol": "date",
    },
    "block": {
        "discard": ["nodename"],
        "datecol": "date",
    },
    "svc": {
        "discard": ["nodename"],
        "sub": "svcname",
        "datecol": "date",
    },
    "blockdev": {
        "discard": ["nodename"],
        "sub": "dev",
        "datecol": "date",
    },
    "netdev": {
        "discard": ["nodename"],
        "sub": "dev",
        "datecol": "date",
    },
    "netdev_err": {
        "discard": ["nodename"],
        "sub": "dev",
        "datecol": "date",
    },
}

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
@service.jsonrpc2
def begin_action(vars, vals, auth):
    return rpc_begin_action(vars, vals, auth)

@auth_uuid
def rpc_begin_action(vars, vals, auth):
    rconn.rpush(R_SVCACTIONS, json.dumps(["_begin_action", vars, vals, auth]))

@service.xmlrpc
@service.jsonrpc2
def res_action(vars, vals, auth):
    return rpc_res_action(vars, vals, auth)

@auth_uuid
def rpc_res_action(vars, vals, auth):
    vars, vals = replace_nodename_in_data(vars, vals, auth)
    vars, vals = replace_svcname_in_data(vars, vals, auth)
    generic_insert('svcactions', vars, vals, node_id=auth_to_node_id(auth))
    return 0

@service.xmlrpc
@service.jsonrpc2
def end_action(vars, vals, auth):
    return rpc_end_action(vars, vals, auth)

@auth_uuid
def rpc_end_action(vars, vals, auth):
    rconn.rpush(R_SVCACTIONS, json.dumps(["_end_action", vars, vals, auth]))

@service.xmlrpc
@service.jsonrpc2
def update_appinfo(vars, vals, auth):
    """
    'svcmgr push resinfo' data feeder.

    Compatibilty entrypoint with old agents.
    The up-to-date entrypoint is update_resinfo.
    """
    return rpc_update_resinfo(vars, vals, auth)

@service.xmlrpc
@service.jsonrpc2
def update_resinfo(vars, vals, auth):
    """
    'svcmgr push resinfo' asynchronous data feeder.
    """
    return rpc_update_resinfo(vars, vals, auth)

@service.xmlrpc
@service.jsonrpc2
def update_resinfo_sync(vars, vals, auth):
    """
    'svcmgr push resinfo' synchronous data feeder.
    """
    return __update_resinfo(vars, vals, auth)

@auth_uuid
def rpc_update_resinfo(vars, vals, auth):
    key = json.dumps([vals[0][0], auth])
    rconn.hset(R_RESINFO_HASH, key, json.dumps([vars, vals]))
    rconn.lrem(R_RESINFO, 0, key)
    rconn.lpush(R_RESINFO, key)

@service.xmlrpc
@service.jsonrpc2
def update_service(vars, vals, auth):
    return rpc_update_service(vars, vals, auth)

@auth_uuid
def rpc_update_service(vars, vals, auth):
    key = json.dumps([vals[0], auth])
    rconn.hset(R_SVCCONF_HASH, key, json.dumps([vars, vals]))
    rconn.lrem(R_SVCCONF, 0, key)
    rconn.lpush(R_SVCCONF, key)

@service.xmlrpc
@service.jsonrpc2
def push_checks(vars, vals, auth):
    return rpc_push_checks(vars, vals, auth)

@auth_uuid
def rpc_push_checks(vars, vals, auth):
    key = json.dumps([auth])
    rconn.hset(R_CHECKS_HASH, key, json.dumps([vars, vals]))
    rconn.lrem(R_CHECKS, 0, key)
    rconn.lpush(R_CHECKS, key)

@service.xmlrpc
@service.jsonrpc2
def insert_generic(data, auth):
    return rpc_insert_generic(data, auth)

@auth_uuid
def rpc_insert_generic(data, auth):
    rconn.rpush(R_GENERIC, json.dumps([data, auth]))

@service.xmlrpc
@service.jsonrpc2
def update_asset(vars, vals, auth):
    return rpc_update_asset(vars, vals, auth)

@auth_uuid
def rpc_update_asset(vars, vals, auth):
    key = json.dumps([auth])
    rconn.hset(R_ASSET_HASH, key, json.dumps([vars, vals]))
    rconn.lrem(R_ASSET, 0, key)
    rconn.lpush(R_ASSET, key)

@service.xmlrpc
@service.jsonrpc2
def update_asset_sync(vars, vals, auth):
    return rpc_update_asset_sync(vars, vals, auth)

@auth_uuid
def rpc_update_asset_sync(vars, vals, auth):
    __update_asset(vars, vals, auth)

@service.xmlrpc
@service.jsonrpc2
def res_action_batch(vars, vals, auth):
    return rpc_res_action_batch(vars, vals, auth)

@auth_uuid
def rpc_res_action_batch(vars, vals, auth):
    vars, vals = replace_nodename_in_data(vars, vals, auth, fieldname="hostname")
    vars, vals = replace_svcname_in_data(vars, vals, auth)
    generic_insert('svcactions', vars, vals, node_id=auth_to_node_id(auth))

@service.xmlrpc
@service.jsonrpc2
def resmon_update(vars, vals, auth):
    return rpc_resmon_update(vars, vals, auth)

@auth_uuid
def rpc_resmon_update(vars, vals, auth):
    _resmon_update(vars, vals, auth)

@service.xmlrpc
@service.jsonrpc2
def svcmon_update_combo(g_vars, g_vals, r_vars, r_vals, auth):
    return rpc_svcmon_update_combo(g_vars, g_vals, r_vars, r_vals, auth)

@auth_uuid
def rpc_svcmon_update_combo(g_vars, g_vals, r_vars, r_vals, auth):
    rconn.rpush(R_SVCMON, json.dumps([g_vars, g_vals, r_vars, r_vals, auth]))

@service.xmlrpc
@service.jsonrpc2
def register_disks(vars, vals, auth):
    return rpc_register_disks(vars, vals, auth)

@auth_uuid
def rpc_register_disks(vars, vals, auth):
    node = auth_to_node(auth)
    node_id = node.node_id
    nodename = node.nodename
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    idx_disk_svcname = vars.index("disk_svcname")
    svc_ids = {}

    def _svc_id(disk_svcname):
        """local cache function for disk_svcname to svc_id"""
        if disk_svcname in svc_ids:
            return svc_ids[disk_svcname]
        svc_id = node_svc_id(node_id, disk_svcname)
        if len(svc_id) == 0:
            # if no service name is provided and the node is actually
            # a service encpasulated vm, add the encapsulating svcname
            q = db.svcmon.mon_vmname == db.nodes.nodename
            q &= db.nodes.node_id == node_id
            row = db(q).select(db.svcmon.svc_id, cacheable=True).first()
            if row is not None:
                svc_id = repr(row.svc_id)
        svc_ids[disk_svcname] = svc_id
        return svc_id

    for v in vals:
        disk_svcname = v[idx_disk_svcname].strip("'")
        svc_id = _svc_id(disk_svcname)
        _register_disk(vars, v, auth, node_id=node_id, disk_nodename=nodename, svc_id=svc_id)

    # purge svcdisks
    sql = """ delete from svcdisks
              where
                node_id = "%(node_id)s" and
                disk_updated < "%(now)s"
          """ % dict(node_id=node_id, now=now)
    db.executesql(sql)

    # purge diskinfo stubs
    sql = """ delete from diskinfo
              where
                (disk_arrayid = "%(node_id)s" or
                 disk_arrayid = "" or
                 disk_arrayid = "None" or
                 disk_arrayid is NULL) and
                disk_updated < "%(now)s"
          """ % dict(node_id=node_id, now=now)
    db.executesql(sql)

    db.commit()
    table_modified("diskinfo")
    table_modified("svcdisks")

@service.xmlrpc
@service.jsonrpc2
def register_disk_blacklist(vars, vals, auth):
    return rpc_register_disk_blacklist(vars, vals, auth)

@auth_uuid
def rpc_register_disk_blacklist(vars, vals, auth):
    generic_insert('disk_blacklist', vars, vals)

def disk_level(dev_id, level=0):
    q = db.diskinfo.disk_id == dev_id
    q &= db.diskinfo.disk_id != db.diskinfo.disk_devid
    rows = db(q).select(db.diskinfo.disk_devid)
    if len(rows) == 0:
        return level
    return disk_level(rows.first().disk_devid, level+1)

@service.xmlrpc
@service.jsonrpc2
def register_diskinfo(vars, vals, auth):
    return rpc_register_diskinfo(vars, vals, auth)

@auth_uuid
def rpc_register_diskinfo(vars, vals, auth):
    if len(vals) == 0:
        return

    node_id = auth_to_node_id(auth)
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)
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
    node = db(db.nodes.node_id==node_id).select().first()
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

@service.xmlrpc
@service.jsonrpc2
def register_disk(vars, vals, auth):
    return rpc_register_disk(vars, vals, auth)

@auth_uuid
def rpc_register_disk(vars, vals, auth):
    _register_disk(vars, vals, auth)
    db.commit()
    table_modified("diskinfo")
    table_modified("svcdisks")


@service.xmlrpc
@service.jsonrpc2
def register_sync(vars, vals, auth):
    return rpc_register_sync(vars, vals, auth)

@auth_uuid
def rpc_register_sync(vars, vals, auth):
    pass

@service.xmlrpc
@service.jsonrpc2
def register_ip(vars, vals, auth):
    return rpc_register_ip(vars, vals, auth)

@auth_uuid
def rpc_register_ip(vars, vals, auth):
    pass

@service.xmlrpc
@service.jsonrpc2
def register_fs(vars, vals, auth):
    return rpc_register_fs(vars, vals, auth)

@auth_uuid
def rpc_register_fs(vars, vals, auth):
    pass

@service.xmlrpc
@service.jsonrpc2
def insert_stats_fs_u(vars, vals, auth):
    return rpc_insert_stats_fs_u(vars, vals, auth)

@auth_uuid
def rpc_insert_stats_fs_u(vars, vals, auth):
    node_id = auth_to_node_id(auth)
    timeseries.whisper_update_list("nodes/%s" % node_id, vars, vals, group="fs_u", options=stats_options.get("fs_u"))

@service.xmlrpc
@service.jsonrpc2
def insert_stats_cpu(vars, vals, auth):
    return rpc_insert_stats_cpu(vars, vals, auth)

@auth_uuid
def rpc_insert_stats_cpu(vars, vals, auth):
    node_id = auth_to_node_id(auth)
    timeseries.whisper_update_list("nodes/%s" % node_id, vars, vals, group="cpu", options=stats_options.get("cpu"))

@service.xmlrpc
@service.jsonrpc2
def insert_stats_mem_u(vars, vals, auth):
    return rpc_insert_stats_mem_u(vars, vals, auth)

@auth_uuid
def rpc_insert_stats_mem_u(vars, vals, auth):
    node_id = auth_to_node_id(auth)
    timeseries.whisper_update_list("nodes/%s" % node_id, vars, vals, group="mem_u", options=stats_options.get("mem_u"))

@service.xmlrpc
@service.jsonrpc2
def insert_stats_proc(vars, vals, auth):
    return rpc_insert_stats_proc(vars, vals, auth)

@auth_uuid
def rpc_insert_stats_proc(vars, vals, auth):
    node_id = auth_to_node_id(auth)
    timeseries.whisper_update_list("nodes/%s" % node_id, vars, vals, group="proc", options=stats_options.get("proc"))

@service.xmlrpc
@service.jsonrpc2
def insert_stats_swap(vars, vals, auth):
    return rpc_insert_stats_swap(vars, vals, auth)

@auth_uuid
def rpc_insert_stats_swap(vars, vals, auth):
    node_id = auth_to_node_id(auth)
    timeseries.whisper_update_list("nodes/%s" % node_id, vars, vals, group="swap", options=stats_options.get("swap"))

@service.xmlrpc
@service.jsonrpc2
def insert_stats_block(vars, vals, auth):
    return rpc_insert_stats_block(vars, vals, auth)

@auth_uuid
def rpc_insert_stats_block(vars, vals, auth):
    node_id = auth_to_node_id(auth)
    timeseries.whisper_update_list("nodes/%s" % node_id, vars, vals, group="block", options=stats_options.get("block"))

@service.xmlrpc
@service.jsonrpc2
def insert_stats_blockdev(vars, vals, auth):
    return rpc_insert_stats_blockdev(vars, vals, auth)

@auth_uuid
def rpc_insert_stats_blockdev(vars, vals, auth):
    node_id = auth_to_node_id(auth)
    timeseries.whisper_update_list("nodes/%s" % node_id, vars, vals, group="blockdev", options=stats_options.get("blockdev"))

@service.xmlrpc
@service.jsonrpc2
def insert_stats_netdev(vars, vals, auth):
    return rpc_insert_stats_netdev(vars, vals, auth)

@auth_uuid
def rpc_insert_stats_netdev(vars, vals, auth):
    node_id = auth_to_node_id(auth)
    timeseries.whisper_update_list("nodes/%s" % node_id, vars, vals, group="netdev", options=stats_options.get("netdev"))

@service.xmlrpc
@service.jsonrpc2
def insert_stats_netdev_err(vars, vals, auth):
    return rpc_insert_stats_netdev_err(vars, vals, auth)

@auth_uuid
def rpc_insert_stats_netdev_err(vars, vals, auth):
    node_id = auth_to_node_id(auth)
    timeseries.whisper_update_list("nodes/%s" % node_id, vars, vals, group="netdev_err", options=stats_options.get("netdev_err"))

def get_vcpus(node_id, vmname):
    q = db.nodes.node_id == node_id
    try:
        nodename = db(q).select(db.nodes.nodename).first().nodename
    except:
        return
    if nodename == vmname:
        return

    sql = """select mon_vcpus from svcmon where
               node_id = "%s" and
               mon_vmname = "%s" """%(node_id, vmname)
    try:
        return db.executesql(sql)[0][0]
    except:
        return

@service.xmlrpc
@service.jsonrpc2
def insert_stats(data, auth):
    return rpc_insert_stats(data, auth)

@auth_uuid
def rpc_insert_stats(data, auth):
    try:
        import cPickle
        h = cPickle.loads(data)
    except:
        import json
        h = json.loads(data)

    node_id = auth_to_node_id(auth)
    for stat in h:
        vars, vals = h[stat]
        if stat == "svc" and "cap_cpu" not in vars and len(vals) > 0:
            cache = {}
            vars.append("cap_cpu")
            for idx, k in enumerate(vars):
                if k == "svcname":
                    break
            for i, _vals in enumerate(vals):
                vmname = _vals[idx]
                if vmname in cache:
                    vcpus = cache[vmname]
                else:
                    vcpus = str(get_vcpus(node_id, vmname))
                    cache[vmname] = vcpus
                vals[i].append(vcpus)
        try:
            timeseries.whisper_update_list("nodes/%s" % node_id, vars, vals, group=stat, options=stats_options.get(stat))
        except Exception as exc:
            raise Exception(json.dumps([str(exc), node_id, vars, vals, stat, stats_options.get(stat)]))
    rconn.rpush(R_UPDATE_DASH_NETDEV_ERRORS, json.dumps([node_id]))

@service.xmlrpc
@service.jsonrpc2
def insert_pkg(vars, vals, auth):
    return rpc_insert_pkg(vars, vals, auth)

@auth_uuid
def rpc_insert_pkg(vars, vals, auth):
    key = json.dumps([auth])
    rconn.hset(R_PACKAGES_HASH, key, json.dumps([vars, vals]))
    rconn.lrem(R_PACKAGES, 0, key)
    rconn.lpush(R_PACKAGES, key)

@service.xmlrpc
@service.jsonrpc2
def insert_patch(vars, vals, auth):
    return rpc_insert_patch(vars, vals, auth)

@auth_uuid
def rpc_insert_patch(vars, vals, auth):
    key = json.dumps([auth])
    rconn.hset(R_PATCHES_HASH, key, json.dumps([vars, vals]))
    rconn.lrem(R_PATCHES, 0, key)
    rconn.lpush(R_PATCHES, key)

@service.xmlrpc
@service.jsonrpc2
def update_hcs(symid, vars, vals, auth):
    return rpc_update_hcs(symid, vars, vals, auth)

@auth_uuid
def rpc_update_hcs(symid, vars, vals, auth):
    update_array_xml(symid, vars, vals, auth, "hcs", insert_hcs)

@service.xmlrpc
@service.jsonrpc2
def update_hds(symid, vars, vals, auth):
    return rpc_update_hds(symid, vars, vals, auth)

@auth_uuid
def rpc_update_hds(symid, vars, vals, auth):
    update_array_xml(symid, vars, vals, auth, "hds", insert_hds)

@service.xmlrpc
@service.jsonrpc2
def update_sym_xml(symid, vars, vals, auth):
    return rpc_update_sym_xml(symid, vars, vals, auth)

@auth_uuid
def rpc_update_sym_xml(symid, vars, vals, auth):
    if len(vars) == 1:
        update_array_xml(symid, vars, vals, auth, "symmetrix", None)
    else:
        update_array_xml(symid, vars, vals, auth, "symmetrix", insert_sym)

@service.xmlrpc
@service.jsonrpc2
def update_dorado_xml(name, vars, vals, auth):
    return rpc_update_dorado_xml(name, vars, vals, auth)

@auth_uuid
def rpc_update_dorado_xml(name, vars, vals, auth):
    if len(vars) == 1:
        update_array_xml(name, vars, vals, auth, "dorado", None)
    else:
        update_array_xml(name, vars, vals, auth, "dorado", insert_dorado)

@service.xmlrpc
@service.jsonrpc2
def update_eva_xml(name, vars, vals, auth):
    return rpc_update_eva_xml(name, vars, vals, auth)

@auth_uuid
def rpc_update_eva_xml(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "eva", insert_eva)

@service.xmlrpc
@service.jsonrpc2
def update_nsr(name, vars, vals, auth):
    return rpc_update_nsr(name, vars, vals, auth)

@auth_uuid
def rpc_update_nsr(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "nsr", insert_nsr)

@service.xmlrpc
@service.jsonrpc2
def update_netapp(name, vars, vals, auth):
    return rpc_update_netapp(name, vars, vals, auth)

@auth_uuid
def rpc_update_netapp(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "netapp", insert_netapp)

@service.xmlrpc
@service.jsonrpc2
def update_hp3par(name, vars, vals, auth):
    return rpc_update_hp3par(name, vars, vals, auth)

@auth_uuid
def rpc_update_hp3par(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "hp3par", insert_hp3par)

@service.xmlrpc
@service.jsonrpc2
def update_ibmsvc(name, vars, vals, auth):
    return rpc_update_ibmsvc(name, vars, vals, auth)

@auth_uuid
def rpc_update_ibmsvc(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "ibmsvc", insert_ibmsvc)

@service.xmlrpc
@service.jsonrpc2
def update_ibmds(name, vars, vals, auth):
    return rpc_update_ibmds(name, vars, vals, auth)

@auth_uuid
def rpc_update_ibmds(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "ibmds", insert_ibmds)

@service.xmlrpc
@service.jsonrpc2
def update_brocade(name, vars, vals, auth):
    return rpc_update_brocade(name, vars, vals, auth)

@auth_uuid
def rpc_update_brocade(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "brocade", insert_brocade)

@service.xmlrpc
@service.jsonrpc2
def update_vioserver(name, vars, vals, auth):
    return rpc_update_vioserver(name, vars, vals, auth)

@auth_uuid
def rpc_update_vioserver(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "vioserver", insert_vioserver)

@service.xmlrpc
@service.jsonrpc2
def update_centera(name, vars, vals, auth):
    return rpc_update_centera(name, vars, vals, auth)

@auth_uuid
def rpc_update_centera(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "centera", insert_centera)

@service.xmlrpc
@service.jsonrpc2
def update_emcvnx(name, vars, vals, auth):
    return rpc_update_emcvnx(name, vars, vals, auth)

@auth_uuid
def rpc_update_emcvnx(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "emcvnx", insert_emcvnx)

@service.xmlrpc
@service.jsonrpc2
def update_necism(name, vars, vals, auth):
    return rpc_update_necism(name, vars, vals, auth)

@auth_uuid
def rpc_update_necism(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "necism", insert_necism)

@service.xmlrpc
@service.jsonrpc2
def update_freenas(name, vars, vals, auth):
    return rpc_update_freenas(name, vars, vals, auth)

@auth_uuid
def rpc_update_freenas(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "freenas", insert_freenas)

@service.xmlrpc
@service.jsonrpc2
def update_xtremio(name, vars, vals, auth):
    return rpc_update_xtremio(name, vars, vals, auth)

@auth_uuid
def rpc_update_xtremio(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "xtremio", insert_xtremio)

@service.xmlrpc
@service.jsonrpc2
def update_gcedisks(name, vars, vals, auth):
    return rpc_update_gcedisks(name, vars, vals, auth)

@auth_uuid
def rpc_update_gcedisks(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "gcedisks", insert_gcedisks)

@service.xmlrpc
@service.jsonrpc2
def update_dcs(name, vars, vals, auth):
    return rpc_update_dcs(name, vars, vals, auth)

@auth_uuid
def rpc_update_dcs(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "dcs", insert_dcs)

def update_array_xml(arrayid, vars, vals, auth, subdir, fn):
    import codecs

    dir = 'applications'+str(URL(r=request,a='init', c='uploads',f=subdir))
    if not os.path.exists(dir):
        os.makedirs(dir)

    dir = os.path.join(dir, arrayid)
    if not os.path.exists(dir):
        os.makedirs(dir)

    for a,b in zip(vars, vals):
        a = os.path.join(dir, a)
        if hasattr(b, "data"):
            import zlib
            b = zlib.decompress(b.data)
        f = codecs.open(a, "w", "utf-8")
        f.write(b)
        f.flush()
        os.fsync(f)
        f.close()

    if fn is None:
        return

    #fn(arrayid)
    node_id = auth_to_node_id(auth)
    rconn.rpush(R_STORAGE, json.dumps([fn.__name__, arrayid, node_id]))

    # stor_array_proxy
    insert_array_proxy(node_id, arrayid)

    # clean up stor_array_*
    sql = "delete from stor_array_dg where array_id not in (select id from stor_array)"
    db.executesql(sql)

    sql = "delete from stor_array_tgtid where array_id not in (select id from stor_array)"
    db.executesql(sql)

    sql = "delete from stor_array_proxy where array_id not in (select id from stor_array)"
    db.executesql(sql)

    sql = "delete from stor_array_dg_quota where stor_array_dg_quota.dg_id not in (select id from stor_array_dg)"
    db.executesql(sql)

@service.xmlrpc
@service.jsonrpc2
def send_sysreport(fname, binary, deleted, auth):
    return rpc_send_sysreport(fname, binary, deleted, auth)

@auth_uuid
def rpc_send_sysreport(fname, binary, deleted, auth):
    need_commit = False
    sysreport_d = os.path.join(os.path.dirname(__file__), "..", "..", "init", 'uploads', 'sysreport')
    node_id = auth_to_node_id(auth)

    if not os.path.exists(sysreport_d):
        os.makedirs(sysreport_d)

    need_commit |= send_sysreport_delete(deleted, sysreport_d, node_id)
    need_commit |= send_sysreport_archive(fname, binary, sysreport_d, node_id)

    rconn.rpush(R_SYSREPORT, json.dumps([need_commit, deleted, node_id]))

def insert_gcediskss():
    return insert_gcedisks()

def insert_freenass():
    return insert_freenas()

def insert_xtremios():
    return insert_xtremio()

def insert_dcss():
    return insert_dcs()

def insert_hdss():
    return insert_hds()

def insert_centeras():
    return insert_centera()

def insert_emcvnxs():
    return insert_emcvnx()

def insert_necisms():
    return insert_necism()

def insert_brocades():
    return insert_brocade()

def insert_vioservers():
    return insert_vioserver()

def insert_nsrs():
    return insert_nsr()

def insert_netapps():
    return insert_netapp()

def insert_hp3pars():
    return insert_hp3par()

def insert_ibmdss():
    return insert_ibmds()

def insert_ibmsvcs():
    return insert_ibmsvc()

def insert_evas():
    return insert_eva()

def insert_syms():
    return insert_sym()

def insert_dorados():
    return insert_dorado()

@service.xmlrpc
@service.jsonrpc2
def delete_pkg(node, auth):
    pass

@service.xmlrpc
@service.jsonrpc2
def delete_patch(node, auth):
    pass

@service.xmlrpc
@service.jsonrpc2
def delete_syncs(svcname, auth):
    pass

@service.xmlrpc
@service.jsonrpc2
def delete_ips(svcname, node, auth):
    pass

@service.xmlrpc
@service.jsonrpc2
def delete_fss(svcname, auth):
    pass

@service.xmlrpc
@service.jsonrpc2
def register_node(node):
    if config_get("refuse_anon_register", False):
        return ["This collector refuses anonymous register. Please use 'nodemgr register --user <user>'."]
    return _register_node(node)

def _register_node(node):
    # anonymous register: don't allow nodename conflicts
    if node is None or node == '':
        return ["no node name provided"]
    q = db.nodes.nodename == node
    row = db(q).select().first()
    if row is None:
        node_id = get_new_node_id()
        db.nodes.insert(nodename=node, node_id=node_id)
    else:
        node_id = row.node_id

    q = db.auth_node.node_id == node_id
    row = db(q).select().first()
    if row is not None:
        _log("node.register",
             "node '%(node)s' double registration attempt",
             dict(node=node),
             node_id=node_id,
             level="warning")
        return ["already registered"]
    import uuid
    u = str(uuid.uuid4())
    db.auth_node.insert(nodename=node, uuid=u, node_id=node_id)
    db.commit()
    _log("node.register",
         "node '%(node)s' registered with id %(node_id)s",
         dict(node=node, node_id=node_id),
         node_id=node_id)
    return u

@service.xmlrpc
@service.jsonrpc2
def svcmon_update(vars, vals, auth):
    return rpc_svcmon_update(vars, vals, auth)

@auth_uuid
def rpc_svcmon_update(vars, vals, auth):
    rconn.rpush(R_SVCMON_UPDATE, json.dumps([vars, vals, auth]))


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

@service.xmlrpc
@service.jsonrpc2
def collector_list_tags(cmd, auth):
    return rpc_collector_list_tags(cmd, auth)

@auth_uuid
def rpc_collector_list_tags(cmd, auth):
    d = {}
    q = db.tags.id > 0
    if "pattern" in cmd and len(cmd["pattern"]) > 0:
        pattern = cmd["pattern"]
        if pattern[0] != "%":
            pattern = "%" + pattern
        if pattern[-1] != "%":
            pattern = pattern + "%"
        q &= db.tags.tag_name.like(pattern)
    rows = db(q).select(orderby=db.tags.tag_name)
    if len(rows) == 0:
        return {"ret": 1, "msg": "no tags found"}
    tags = [r.tag_name.lower() for r in rows]
    return {"ret": 0, "msg": "", "data": tags}

@service.xmlrpc
@service.jsonrpc2
def collector_show_tags(cmd, auth):
    return rpc_collector_show_tags(cmd, auth)

@auth_uuid
def rpc_collector_show_tags(cmd, auth):
    d = {}
    node_id = auth_to_node_id(auth)
    if "svcname" in cmd:
        svcname = cmd["svcname"]
        svc_id = node_svc_id(node_id, svcname)
        q = db.svc_tags.svc_id == svc_id
        q &= db.svc_tags.tag_id == db.tags.tag_id
        rows = db(q).select(db.tags.tag_name, orderby=db.tags.tag_name)
    else:
        q = db.node_tags.node_id == node_id
        q &= db.node_tags.tag_id == db.tags.tag_id
        rows = db(q).select(db.tags.tag_name, orderby=db.tags.tag_name)
    if len(rows) == 0:
        return {"ret": 1, "msg": "no tags found"}
    tags = [r.tag_name.lower() for r in rows]
    return {"ret": 0, "msg": "", "data": tags}

@service.xmlrpc
@service.jsonrpc2
def collector_create_tag(data, auth):
    return rpc_collector_create_tag(data, auth)

@auth_uuid
def rpc_collector_create_tag(data, auth):
    tag_name = data.get('tag_name')
    tag_exclude = data.get('tag_exclude')
    if tag_name is None:
        return {"ret": 1, "msg": "misformatted data"}
    q = db.tags.tag_name == tag_name
    rows = db(q).select()
    if len(rows) != 0:
        return {"ret": 0, "msg": "tag already exists"}

    db.tags.insert(
       tag_name=tag_name,
       tag_exclude=tag_exclude
    )
    _log("tag",
         "tag '%(tag_name)s' created",
         dict(tag_name=tag_name)
    )
    ws_send("tags_change")
    table_modified("tags")
    return {"ret": 0, "msg": "tag successfully created"}

def tag_allowed(node_id=None, svc_id=None, tag_name=None):
    if node_id is None and svc_id is None:
        return False
    if tag_name is None:
        return False
    if node_id:
        q = db.node_tags.node_id == node_id
        q &= db.node_tags.tag_id == db.tags.tag_id
        q &= db.tags.tag_exclude != None
        q &= db.tags.tag_exclude != ""
        rows = db(q).select(db.tags.tag_exclude,
                            groupby=db.tags.tag_exclude)
    elif svc_id:
        q = db.svc_tags.svc_id == svc_id
        q &= db.svc_tags.tag_id == db.tags.tag_id
        q &= db.tags.tag_exclude != None
        q &= db.tags.tag_exclude != ""
        rows = db(q).select(db.tags.tag_exclude,
                            groupby=db.tags.tag_exclude)
    if len(rows) == 0:
        return True

    pattern = '|'.join([r.tag_exclude for r in rows])
    q = db.tags.tag_name == tag_name
    qx = _where(None, "tags", pattern, "tag_name")
    q &= ~qx
    if db(q).count() == 0:
        return False
    return True

@service.xmlrpc
@service.jsonrpc2
def collector_tag(data, auth):
    return rpc_collector_tag(data, auth)

@auth_uuid
def rpc_collector_tag(data, auth):
    tag_name = data.get('tag_name')
    if tag_name is None:
        return {"ret": 1, "msg": "misformatted data"}
    q = db.tags.tag_name == tag_name
    rows = db(q).select()
    if len(rows) == 0:
        return {"ret": 1, "msg": "tag does not exist. you have to create it first."}
    tag = rows.first()

    if "svcname" in data:
        svcname = data["svcname"]
        node_id = auth_to_node_id(auth)
        svc_id = node_svc_id(node_id, svcname)
        if not tag_allowed(svc_id=svc_id, tag_name=tag_name):
            return {"ret": 1, "msg": "tag incompatible with other attached tags."}
        q = db.svc_tags.svc_id == svc_id
        q &= db.svc_tags.tag_id == tag.tag_id
        rows = db(q).select()
        if len(rows) > 0:
            return {"ret": 0, "msg": "tag is already attached"}

        db.svc_tags.insert(
           svc_id=svc_id,
           tag_id=tag.tag_id
        )
        _log("service.tag",
             "tag '%(tag_name)s' attached",
             dict(tag_name=tag_name),
             svc_id=svc_id)
        ws_send("tags",  {'action': 'attach', 'tag_name': tag_name, 'tag_id': tag.id, 'svc_id': svc_id})
        table_modified("svc_tags")
    else:
        node_id = auth_to_node_id(auth)
        if not tag_allowed(node_id=node_id, tag_name=tag_name):
            return {"ret": 1, "msg": "tag incompatible with other attached tags."}
        q = db.node_tags.node_id == node_id
        q &= db.node_tags.tag_id == tag.tag_id
        rows = db(q).select()
        if len(rows) > 0:
            return {"ret": 0, "msg": "tag is already attached"}

        db.node_tags.insert(
           node_id=node_id,
           tag_id=tag.tag_id
        )
        _log("node.tag",
             "tag '%(tag_name)s' attached",
             dict(tag_name=tag_name),
             node_id=node_id)
        ws_send("tags",  {'action': 'attach', 'tag_name': tag_name, 'tag_id': tag.id, 'node_id': node_id})
        table_modified("node_tags")
    return {"ret": 0, "msg": "tag successfully attached"}

@service.xmlrpc
@service.jsonrpc2
def collector_untag(data, auth):
    return rpc_collector_untag(data, auth)

@auth_uuid
def rpc_collector_untag(data, auth):
    tag_name = data.get('tag_name')
    if tag_name is None:
        return {"ret": 1, "msg": "misformatted data"}
    q = db.tags.tag_name == tag_name
    rows = db(q).select()
    if len(rows) == 0:
        return {"ret": 1, "msg": "tag does not exist"}
    tag = rows.first()

    if "svcname" in data:
        svcname = data["svcname"]
        node_id = auth_to_node_id(auth)
        svc_id = node_svc_id(node_id, svcname)
        q = db.svc_tags.svc_id == svc_id
        q &= db.svc_tags.tag_id == tag.tag_id
        rows = db(q).select()
        if len(rows) == 0:
            return {"ret": 0, "msg": "tag is already detached"}

        db(q).delete()
        _log("service.tag",
             "tag '%(tag_name)s' detached",
             dict(tag_name=tag_name),
             svc_id=svc_id)
        ws_send("tags",  {'action': 'detach', 'tag_id': tag.id, 'svc_id': svc_id})
        table_modified("svc_tags")
    else:
        node_id = auth_to_node_id(auth)
        q = db.node_tags.node_id == node_id
        q &= db.node_tags.tag_id == tag.tag_id
        rows = db(q).select()
        if len(rows) == 0:
            return {"ret": 0, "msg": "tag is already detached"}

        db(q).delete()
        _log("node.tag",
             "tag '%(tag_name)s' detached",
             dict(tag_name=tag_name),
             node_id=node_id)
        ws_send("tags",  {'action': 'detach', 'tag_id': tag.id, 'node_id': node_id})
        table_modified("node_tags")
    return {"ret": 0, "msg": "tag successfully detached"}



@service.xmlrpc
@service.jsonrpc2
def collector_update_root_pw(data, auth):
    return rpc_collector_update_root_pw(data, auth)

@auth_uuid
def rpc_collector_update_root_pw(data, auth):
    node_id = auth_to_node_id(auth)
    if node_id is None:
        return {"ret": 1, "msg": "This node is not registered."}

    pw = data.get('pw')
    if pw is None:
        return {"ret": 1, "msg": "Malformatted data."}
    uuid = auth[0]

    #config = local_import('config', reload=True)
    from applications.init.modules import config
    try:
        salt = config.aes_salt
    except Exception as e:
        salt = "tlas"

    sql = """insert into node_pw set
              node_id="%(node_id)s",
              pw=aes_encrypt("%(pw)s", "%(uuid)s")
             on duplicate key update
              pw=aes_encrypt("%(pw)s", "%(uuid)s"),
              updated=now()
          """ % dict(node_id=node_id, pw=pw, uuid=uuid+salt)
    db.executesql(sql)
    table_modified("node_pw")
    return {"ret": 0, "msg": "password updated succesfully"}

@service.xmlrpc
@service.jsonrpc2
def collector_ack_action(cmd, auth):
    return rpc_collector_ack_action(cmd, auth)

@auth_uuid
def rpc_collector_ack_action(cmd, auth):
    d = {}
    node_id = auth_to_node_id(auth)
    nodename = get_nodename(node_id)
    d["acked_date"] = datetime.datetime.now()

    if "svcname" in cmd:
        svcname = cmd["svcname"]
        svc_id = node_svc_id(node_id, svcname)
        q = db.svcactions.svc_id == svc_id
        q &= db.svcactions.node_id == node_id
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%svcname}
        d["svc_id"] = svc_id

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

    q = db.svcactions.status == "err"

    q1 = db.svcactions.id == cmd['id']
    rows = db(q1).select()

    if len(rows) == 0:
        q &= q1
    else:
        if rows[0].status_log is None or rows[0].status_log == "":
            q &= db.svcactions.node_id == node_id
            q &= db.svcactions.svc_id == rows[0].svc_id
            q &= ((db.svcactions.pid.belongs(rows[0].pid.split(',')))|(db.svcactions.id==rows[0].id))
            q &= db.svcactions.begin >= rows[0].begin
            q &= db.svcactions.end <= rows[0].end
        else:
            q &= q1

    if db(q).count() == 0:
        return {"ret": 1, "msg": "action id not found or not ackable"}

    db(q).update(ack=1,
                 acked_comment=d["acked_comment"],
                 acked_date=d["acked_date"],
                 acked_by=d["acked_by"])
    db.commit()

    update_action_errors(rows[0].svc_id, node_id)
    update_dash_action_errors(rows[0].svc_id, node_id)

    return {"ret": 0, "msg": ""}

@service.xmlrpc
@service.jsonrpc2
def collector_ack_unavailability(cmd, auth):
    return rpc_collector_ack_unavailability(cmd, auth)

@auth_uuid
def rpc_collector_ack_unavailability(cmd, auth):
    d = {}
    node_id = auth_to_node_id(auth)
    nodename = get_nodename(node_id)
    d["mon_acked_on"] = datetime.datetime.now()

    if "svcname" not in cmd:
        return {"ret": 1, "msg": "svcname not found in command block"}
    else:
        svc_id = node_svc_id(node_id, cmd["svcname"])
        q = db.svcmon.svc_id == svc_id
        q &= db.svcmon.node_id == node_id
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%cmd["svcname"]}
        d["svc_id"] = svc_id

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

@service.xmlrpc
@service.jsonrpc2
def collector_list_unavailability_ack(cmd, auth):
    return rpc_collector_list_unavailability_ack(cmd, auth)

@auth_uuid
def rpc_collector_list_unavailability_ack(cmd, auth):
    d = {}
    node_id = auth_to_node_id(auth)
    d["mon_acked_on"] = datetime.datetime.now()

    if "svcname" not in cmd:
        return {"ret": 1, "msg": "svcname not found in command block"}
    else:
        svc_id = node_svc_id(node_id, cmd["svcname"])
        q = db.svcmon.svc_id == svc_id
        q &= db.svcmon.node_id == node_id
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%cmd["svcname"]}

    q = db.svcmon_log_ack.svc_id == svc_id

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

@service.xmlrpc
@service.jsonrpc2
def collector_show_actions(cmd, auth):
    return rpc_collector_show_actions(cmd, auth)

@auth_uuid
def rpc_collector_show_actions(cmd, auth):
    d = {}
    node_id = auth_to_node_id(auth)

    if "svcname" in cmd:
        svc_id = node_svc_id(node_id, cmd["svcname"])
        q = db.svcmon.svc_id == svc_id
        q &= db.svcmon.node_id == node_id
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%cmd["svcname"]}

    if "svcname" in cmd:
        q = db.svcactions.svc_id == svc_id
    else:
        q = db.svcactions.node_id == node_id

    if "id" in cmd:
        q1 = db.svcactions.id == cmd['id']
        rows = db(q1).select()
        if len(rows) == 0:
            q &= q1
        else:
            if rows[0].status_log is None or rows[0].status_log == "":
                q &= db.svcactions.node_id == node_id
                q &= db.svcactions.svc_id == rows[0].svc_id
                q &= ((db.svcactions.pid.belongs(rows[0].pid.split(',')))|(db.svcactions.id==rows[0].id))
                q &= db.svcactions.begin >= rows[0].begin
                q &= db.svcactions.end <= rows[0].end
            else:
                q &= q1
    else:
        if "begin" not in cmd:
            b = datetime.datetime.now() - datetime.timedelta(days=7)
        else:
            b = str_to_datetime(cmd["begin"])
            if b is None:
                return {"ret": 1, "msg": "could not parse --begin as a date"}
        q &= db.svcactions.end >= b

        if "end" not in cmd:
            e = datetime.datetime.now()
        else:
            e = str_to_datetime(cmd["end"])
            if e is None:
                return {"ret": 1, "msg": "could not parse --end as a date"}
        q &= db.svcactions.begin <= e
    q &= db.nodes.node_id == db.svcactions.node_id
    q &= db.services.svc_id == db.svcactions.svc_id

    rows = db(q).select(db.svcactions.id,
                        db.nodes.nodename,
                        db.services.svcname,
                        db.svcactions.begin,
                        db.svcactions.action,
                        db.svcactions.status,
                        db.svcactions.ack,
                        db.svcactions.status_log,
                        orderby=db.svcactions.id
                       )
    data = [["action id",
             "node name",
             "service name",
             "begin",
             "action",
             "status",
             "acknowledged",
             "log"]]
    for row in rows:
        data.append([str(row.svcactions.id),
                     str(row.nodes.nodename),
                     str(row.services.svcname),
                     str(row.svcactions.begin),
                     str(row.svcactions.action),
                     str(row.svcactions.status),
                     str(row.svcactions.ack),
                     str(row.svcactions.status_log)])
    return {"ret": 0, "msg": "", "data":data}

@service.xmlrpc
@service.jsonrpc2
def collector_update_action_queue(data, auth):
    return rpc_collector_update_action_queue(data, auth)

@auth_uuid
def rpc_collector_update_action_queue(data, auth):
    node_id = auth_to_node_id(auth)
    for id, ret, out, err in data:
        q = db.action_queue.id == id
        q &= db.action_queue.node_id == node_id
        db(q).update(stdout=out, stderr=err, ret=ret, status="T", date_dequeued=datetime.datetime.now())
        db.commit()
    action_q_event()
    table_modified("action_queue")

@service.xmlrpc
@service.jsonrpc2
def collector_get_action_queue(nodename, auth):
    return rpc_collector_get_action_queue(nodename, auth)

@auth_uuid
def rpc_collector_get_action_queue(nodename, auth):
    node_id = auth_to_node_id(auth)
    q = db.action_queue.node_id == node_id
    q &= db.action_queue.action_type == "pull"
    q &= db.action_queue.status.belongs(["W", "N"])
    l = db.services.on((db.action_queue.svc_id!="") & (db.action_queue.svc_id == db.services.svc_id))
    sql = db(q)._select(db.action_queue.ALL, db.services.svcname, left=l)
    data = db.executesql(sql, as_dict=True)
    if len(data) > 0:
        q = db.action_queue.id.belongs([action["id"] for action in data])
        db(q).update(status="R")
        db.commit()
    return data

@service.xmlrpc
@service.jsonrpc2
def collector_update_action_queue_received(data, auth):
    return rpc_collector_update_action_queue_received(data, auth)

@auth_uuid
def rpc_collector_update_action_queue_received(data, auth):
    node_id = auth_to_node_id(auth)
    for action_id in data:
        q = db.action_queue.id == action_id
        q &= db.action_queue.node_id == node_id
        db(q).update(status="R", date_dequeued=datetime.datetime.now())
        db.commit()
    action_q_event()
    table_modified("action_queue")

@service.xmlrpc
@service.jsonrpc2
def collector_get_action_queue_v2(nodename, auth):
    return rpc_collector_get_action_queue_v2(nodename, auth)

@auth_uuid
def rpc_collector_get_action_queue_v2(nodename, auth):
    """
    Same as rpc_collector_get_action_queue, but allow clients retry when
    actions are not received correctly by clients.
    This now set sent actions to status 'S'.
    Clients have to notify when action is received with the rpc_collector_update_action_queue_received().
    This will change received action to status 'R'.

    Pull actions in status 'S' are resent if not acknowledge after 20s.
    """
    node_id = auth_to_node_id(auth)
    now = datetime.datetime.now()
    old_date = now - datetime.timedelta(seconds=20)
    q = db.action_queue.node_id == node_id
    q &= db.action_queue.action_type == "pull"
    q &= (db.action_queue.status.belongs(["W", "N"])) \
         | ((db.action_queue.status == "S") & (db.action_queue.date_queued < old_date))
    l = db.services.on((db.action_queue.svc_id != "") & (db.action_queue.svc_id == db.services.svc_id))
    sql = db(q)._select(db.action_queue.ALL, db.services.svcname, left=l)
    data = db.executesql(sql, as_dict=True)
    if len(data) > 0:
        q = db.action_queue.id.belongs([action["id"] for action in data])
        db(q).update(status="S")
        db.commit()
    return data

@service.xmlrpc
@service.jsonrpc2
def collector_list_actions(cmd, auth):
    return rpc_collector_list_actions(cmd, auth)

@auth_uuid
def rpc_collector_list_actions(cmd, auth):
    d = {}
    node_id = auth_to_node_id(auth)
    d["mon_acked_on"] = datetime.datetime.now()

    if "svcname" in cmd:
        svc_id = node_svc_id(node_id, cmd["svcname"])
        q = db.svcmon.svc_id == svc_id
        q &= db.svcmon.node_id == node_id
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%cmd["svcname"]}

    if "svcname" in cmd:
        q = db.svcactions.svc_id == svc_id
    else:
        q = db.svcactions.node_id == node_id

    if "begin" not in cmd:
        b = datetime.datetime.now() - datetime.timedelta(days=7)
    else:
        b = str_to_datetime(cmd["begin"])
        if b is None:
            return {"ret": 1, "msg": "could not parse --begin as a date"}
    q &= db.svcactions.end >= b

    if "end" not in cmd:
        e = datetime.datetime.now()
    else:
        e = str_to_datetime(cmd["end"])
        if e is None:
            return {"ret": 1, "msg": "could not parse --end as a date"}
    q &= db.svcactions.begin <= e

    #q &= (db.svcactions.status_log == "") | (db.svcactions.status_log == None)
    q &= db.nodes.node_id == db.svcactions.node_id
    q &= db.services.svc_id == db.svcactions.svc_id
    rows = db(q).select(db.svcactions.id,
                        db.nodes.nodename,
                        db.svcactions.begin,
                        db.svcactions.end,
                        db.svcactions.action,
                        db.svcactions.status,
                        db.svcactions.ack,
                        db.svcactions.cron,
                        db.svcactions.status_log,
                       )
    header = ['id',
              'node',
              'begin',
              'action',
              'status',
              'ack',
              'sched',
              'log']
    data = [header]
    for row in rows:
        data.append([
          str(row.svcactions.id),
          str(row.nodes.nodename),
          str(row.svcactions.begin),
          str(row.svcactions.action),
          str(row.svcactions.status),
          str(row.svcactions.ack),
          str(row.svcactions.cron),
          str(row.svcactions.status_log),
        ])

    return {"ret": 0, "msg": "", "data":data}

@service.xmlrpc
@service.jsonrpc2
def collector_status(cmd, auth):
    return rpc_collector_status(cmd, auth)

@auth_uuid
def rpc_collector_status(cmd, auth):
    d = {}
    node_id = auth_to_node_id(auth)
    q = db.nodes.node_id == node_id
    nodename = db(q).select(db.nodes.nodename).first().nodename

    if "svcname" in cmd:
        svc_id = node_svc_id(node_id, cmd["svcname"])
        q = db.svcmon.svc_id == svc_id
        q &= (db.svcmon.node_id == node_id) | (db.svcmon.mon_vmname == nodename)
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%cmd["svcname"]}

    o = db.services.svcname
    q = db.svcmon.node_id == db.nodes.node_id
    q &= db.svcmon.svc_id == db.services.svc_id
    if "svcname" in cmd:
        q &= db.svcmon.svc_id == svc_id
    else:
        rows = db(db.svcmon.node_id==node_id).select(db.svcmon.svc_id)
        svc_ids = map(lambda x: x.svc_id, rows)
        if len(svc_ids) > 0:
            q &= db.svcmon.svc_id.belongs(svc_ids)
        else:
            q &= db.svcmon.id < 0
    rows = db(q).select(db.nodes.nodename,
                        db.services.svcname,
                        db.nodes.node_env,
                        db.svcmon.mon_availstatus,
                        db.svcmon.mon_overallstatus,
                        db.svcmon.mon_updated,
                        orderby=o,
                        limitby=(0,100)
                       )
    header = ['node',
              'service',
              'node env',
              'availability status',
              'overall status',
              'status last update']
    data = [header]
    for row in rows:
        data.append([
          str(row.nodes.nodename),
          str(row.services.svcname),
          str(row.nodes.node_env),
          str(row.svcmon.mon_availstatus),
          str(row.svcmon.mon_overallstatus),
          str(row.svcmon.mon_updated)
        ])

    return {"ret": 0, "msg": "", "data":data}

@service.xmlrpc
@service.jsonrpc2
def collector_networks(cmd, auth):
    return rpc_collector_networks(cmd, auth)

@auth_uuid
def rpc_collector_networks(cmd, auth):
    node_id = auth_to_node_id(auth)

    if "svcname" in cmd:
        svc_id = node_svc_id(node_id, cmd["svcname"])
        q = db.svcmon.svc_id == svc_id
        q &= db.svcmon.node_id == node_id
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%cmd["svcname"]}

    if "svcname" in cmd:
        data = []
    else:
        sql = """select
                   node_ip.addr,
                   node_ip.mac,
                   node_ip.intf,
                   networks.name,
                   networks.comment,
                   networks.pvid,
                   networks.network,
                   networks.netmask,
                   networks.gateway,
                   networks.begin,
                   networks.end
                 from node_ip, networks
                 where
                   node_ip.node_id = "%(node_id)s" and
                   inet_aton(node_ip.addr) >= inet_aton(begin) and
                   inet_aton(node_ip.addr)  <= inet_aton(end)
        """ % dict(node_id=node_id)
        rows = db.executesql(sql)
        header = [
          'ip',
          'mac',
          'interface',
          'name',
          'comment',
          'pvid',
          'network',
          'gateway',
          'begin',
          'end'
        ]
        data = [header]
        for row in rows:
            data.append([
                unicode(row[0]),
                unicode(row[1]),
                unicode(row[2]),
                unicode(row[3]),
                unicode(row[4]),
                unicode(row[5]),
                "%s/%d" % (row[6], row[7]),
                unicode(row[8]),
                unicode(row[9]),
                unicode(row[10]),
            ])
    return {"ret": 0, "msg": "", "data": data}


@service.xmlrpc
@service.jsonrpc2
def collector_asset(cmd, auth):
    return rpc_collector_asset(cmd, auth)

@auth_uuid
def rpc_collector_asset(cmd, auth):
    d = {}
    node_id = auth_to_node_id(auth)

    if "svcname" in cmd:
        svc_id = node_svc_id(node_id, cmd["svcname"])
        q = db.svcmon.svc_id == svc_id
        q &= db.svcmon.node_id == node_id
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%cmd["svcname"]}

    if "svcname" in cmd:
        data = []
    else:
        q = db.nodes.node_id == node_id
        j = db.nodes.app == db.apps.app
        l = db.apps.on(j)
        rows = db(q).select(
          db.nodes.ALL,
          db.apps.ALL,
          cacheable=True, left=l
        )

        header = [
          'node id',
          'node name',
          'fqdn',
          'asset name',
          'security zone',
          'os, name',
          'os, release',
          'os, arch',
          'os, vendor',
          'os, kernel',
          'location, country',
          'location, city',
          'location, zip',
          'location, addr',
          'location, building',
          'location, floor',
          'location, room',
          'location, rack',
          'location, enclosure',
          'location, enclosure slot',
          'power, cabinet1',
          'power, cabinet2',
          'power, supplies',
          'power, protect',
          'power, protect breaker',
          'power, breaker1',
          'power, breaker2',
          'cpu, threads',
          'cpu, cores',
          'cpu, dies',
          'cpu, frequency',
          'cpu, model',
          'mem, banks',
          'mem, slots',
          'mem, size in MB',
          'server, serial',
          'server, model',
          'server, bios version',
          'server, sp version',
          'server, team responsible',
          'server, team support',
          'server, team integration',
          'server, node env',
          'server, asset env',
          'server, type',
          'server, role',
          'server, status',
          'hypervisor',
          'hypervisor pool',
          'hypervisor virtual datacenter',
          'opensvc, version',
          'opensvc, listener port',
          'warranty end',
          'maintenance end',
          'obsolescence, os warning date',
          'obsolescence, os alert date',
          'obsolescence, hw warning date',
          'obsolescence, hw alert date',
          'app, code',
          'app, domain',
          'app, operations team',
          'updated',
        ]
        data = [header]
        for row in rows:
            data.append([
              str(row.nodes.id),
              str(row.nodes.nodename),
              str(row.nodes.fqdn),
              str(row.nodes.assetname),
              str(row.nodes.sec_zone),
              str(row.nodes.os_name),
              str(row.nodes.os_release),
              str(row.nodes.os_arch),
              str(row.nodes.os_vendor),
              str(row.nodes.os_kernel),
              str(row.nodes.loc_country),
              str(row.nodes.loc_city),
              str(row.nodes.loc_zip),
              str(row.nodes.loc_addr),
              str(row.nodes.loc_building),
              str(row.nodes.loc_floor),
              str(row.nodes.loc_room),
              str(row.nodes.loc_rack),
              str(row.nodes.enclosure),
              str(row.nodes.enclosureslot) if row.nodes.enclosureslot is not None else "",
              str(row.nodes.power_cabinet1),
              str(row.nodes.power_cabinet2),
              str(row.nodes.power_supply_nb),
              str(row.nodes.power_protect),
              str(row.nodes.power_protect_breaker),
              str(row.nodes.power_breaker1),
              str(row.nodes.power_breaker2),
              str(row.nodes.cpu_threads),
              str(row.nodes.cpu_cores),
              str(row.nodes.cpu_dies),
              str(row.nodes.cpu_freq),
              str(row.nodes.cpu_model),
              str(row.nodes.mem_banks),
              str(row.nodes.mem_slots),
              str(row.nodes.mem_bytes),
              str(row.nodes.serial),
              str(row.nodes.model),
              str(row.nodes.bios_version),
              str(row.nodes.sp_version),
              str(row.nodes.team_responsible),
              str(row.nodes.team_support),
              str(row.nodes.team_integ),
              str(row.nodes.node_env),
              str(row.nodes.asset_env),
              str(row.nodes.type),
              str(row.nodes.role),
              str(row.nodes.status),
              str(row.nodes.hv) if row.nodes.hv is not None else "",
              str(row.nodes.hvpool) if row.nodes.hvpool is not None else "",
              str(row.nodes.hvvdc) if row.nodes.hvvdc is not None else "",
              str(row.nodes.version),
              str(row.nodes.listener_port),
              str(row.nodes.warranty_end) if row.nodes.warranty_end is not None else "",
              str(row.nodes.maintenance_end) if row.nodes.maintenance_end is not None else "",
              str(row.nodes.os_obs_warn_date) if row.nodes.os_obs_warn_date is not None else "",
              str(row.nodes.os_obs_alert_date) if row.nodes.os_obs_alert_date is not None else "",
              str(row.nodes.hw_obs_warn_date) if row.nodes.hw_obs_warn_date is not None else "",
              str(row.nodes.hw_obs_alert_date) if row.nodes.hw_obs_alert_date is not None else "",
              str(row.apps.app) if row.apps.app is not None else "",
              str(row.apps.app_domain) if row.apps.app_domain is not None else "",
              str(row.apps.app_team_ops) if row.apps.app_team_ops is not None else "",
              str(row.nodes.updated)
            ])


    return {"ret": 0, "msg": "", "data": data}

@service.xmlrpc
@service.jsonrpc2
def collector_checks(cmd, auth):
    return rpc_collector_checks(cmd, auth)

@auth_uuid
def rpc_collector_checks(cmd, auth):
    d = {}
    node_id = auth_to_node_id(auth)

    if "svcname" in cmd:
        svc_id = node_svc_id(node_id, cmd["svcname"])
        q = db.svcmon.svc_id == svc_id
        q &= db.svcmon.node_id == node_id
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%cmd["svcname"]}

    cols = [
        db.checks_live.chk_instance,
        db.checks_live.chk_type,
        db.checks_live.chk_value,
        db.checks_live.chk_low,
        db.checks_live.chk_high,
        db.checks_live.chk_threshold_provider,
        db.checks_live.chk_updated,
    ]
    header = [
        'instance',
        'type',
        'value',
        'thresholds',
        'provider',
        'updated',
    ]

    if "svcname" in cmd:
        q = db.checks_live.svc_id == svc_id
        cols = [db.nodes.nodename] + cols
        header = ["node"] + header
        l = db.nodes.on(db.checks_live.node_id==db.nodes.node_id)
        prop = lambda row: row.nodes.nodename
    else:
        q = db.checks_live.node_id == node_id
        cols = [db.services.svcname] + cols
        header = ["svcname"] + header
        l = db.services.on(db.checks_live.svc_id==db.services.svc_id)
        prop = lambda row: row.services.svcname if row.services.svcname else "-" 

    rows = db(q).select(*cols, limitby=(0,1000), left=l)
    data = [header]

    for row in rows:
        high = str(row.checks_live.chk_high) if row.checks_live.chk_high is not None else "*"
        low = str(row.checks_live.chk_low) if row.checks_live.chk_low is not None else "*"
        data.append([
          str(prop(row)),
          str(row.checks_live.chk_instance),
          str(row.checks_live.chk_type),
          str(row.checks_live.chk_value),
          "%s-%s" % (low, high),
          str(row.checks_live.chk_threshold_provider),
          str(row.checks_live.chk_updated)
        ])
    return {"ret": 0, "msg": "", "data": data}

@service.xmlrpc
@service.jsonrpc2
def collector_alerts(cmd, auth):
    return rpc_collector_alerts(cmd, auth)

@auth_uuid
def rpc_collector_alerts(cmd, auth):
    d = {}
    node_id = auth_to_node_id(auth)

    if "svcname" in cmd:
        svc_id = node_svc_id(node_id, cmd["svcname"])
        q = db.svcmon.svc_id == svc_id
        q &= db.svcmon.node_id == node_id
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%cmd["svcname"]}

    cols = [
        db.dashboard.dash_severity,
        db.dashboard.dash_type,
        db.dashboard.dash_created,
        db.dashboard.dash_fmt,
        db.dashboard.dash_dict,
    ]
    header = [
        "severity",
        "type",
        "alert",
        "created",
    ]

    if "svcname" in cmd:
        q = db.dashboard.svc_id == svc_id
        cols = [db.nodes.nodename] + cols
        l = db.nodes.on(db.nodes.node_id==db.dashboard.node_id)
        header = ["node"] + header
        prop = lambda row: row.nodes.nodename
    else:
        q = db.dashboard.node_id == node_id
        cols = [db.services.svcname] + cols
        l = db.services.on(db.services.svc_id==db.dashboard.svc_id)
        header = ["service"] + header
        prop = lambda row: row.services.svcname if row.services.svcname else "-"

    rows = db(q).select(*cols, left=l, orderby=~db.dashboard.dash_severity)
    data = [header]
    for row in rows:
        fmt = row.dashboard.dash_fmt
        try:
            d = json.loads(row.dashboard.dash_dict)
            alert = fmt % d
        except:
            alert = ""
        data += [[
          str(prop(row)),
          str(row.dashboard.dash_severity),
          str(row.dashboard.dash_type),
          str(alert),
          str(row.dashboard.dash_created)
        ]]

    return {"ret": 0, "msg": "", "data": data}

@service.xmlrpc
@service.jsonrpc2
def collector_events(cmd, auth):
    return rpc_collector_events(cmd, auth)

@auth_uuid
def rpc_collector_events(cmd, auth):
    d = {}
    node_id = auth_to_node_id(auth)

    if "svcname" in cmd:
        svc_id = node_svc_id(node_id, cmd["svcname"])
        q = db.svcmon.svc_id == svc_id
        q &= db.svcmon.node_id == node_id
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%cmd["svcname"]}

    if "svcname" in cmd:
        q = db.log.svc_id == svc_id
    else:
        q = db.log.node_id == node_id

    if "begin" not in cmd:
        b = datetime.datetime.now() - datetime.timedelta(days=7)
    else:
        b = str_to_datetime(cmd["begin"])
        if b is None:
            return {"ret": 1, "msg": "could not parse --begin as a date"}
    q &= db.log.log_date >= b

    if "end" not in cmd:
        e = datetime.datetime.now()
    else:
        e = str_to_datetime(cmd["end"])
        if e is None:
            return {"ret": 1, "msg": "could not parse --end as a date"}
    q &= db.log.log_date <= e

    l1 = db.nodes.on(db.log.node_id==db.nodes.node_id)
    l2 = db.services.on(db.log.svc_id==db.services.svc_id)
    rows = db(q).select(
      db.log.log_date,
      db.nodes.nodename,
      db.services.svcname,
      db.log.log_level,
      db.log.log_action,
      db.log.log_fmt,
      db.log.log_dict,
      left=(l1, l2),
      limitby=(0,1000),
    )
    data = [["date", "node", "service", "level", "action", "event"]]
    for row in rows:
        fmt = row.log.log_fmt
        try:
            d = json.loads(row.log.log_dict)
            msg = fmt%d
        except:
            msg = ""
        data += [[
          str(row.log.log_date),
          str(row.nodes.nodename),
          str(row.services.svcname),
          str(row.log.log_level),
          str(row.log.log_action),
          msg
        ]]
    return {"ret": 0, "msg": "", "data": data}

@service.xmlrpc
@service.jsonrpc2
def collector_service_status(cmd, auth):
    return rpc_collector_service_status(cmd, auth)

@auth_uuid
def rpc_collector_service_status(cmd, auth):
    d = {}
    node_id = auth_to_node_id(auth)
    svc_id = node_svc_id(node_id, cmd["svcname"])
    q = db.services.svc_id == svc_id
    row = db(q).select(db.services.svc_availstatus).first()
    if row is None:
        return {"ret": 1, "msg": "service not found %s"%cmd["svcname"]}
    d[cmd["svcname"]] = {"availstatus": row.svc_availstatus}
    return {"ret": 0, "msg": "", "data": d}

@service.xmlrpc
@service.jsonrpc2
def collector_disks(cmd, auth):
    return rpc_collector_disks(cmd, auth)

@auth_uuid
def rpc_collector_disks(cmd, auth):
    d = {}
    node_id = auth_to_node_id(auth)

    if "svcname" in cmd:
        svc_id = node_svc_id(node_id, cmd["svcname"])
        q = db.svcmon.svc_id == svc_id
        q &= db.svcmon.node_id == node_id
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%cmd["svcname"]}

    if "svcname" in cmd:
        q = db.svcdisks.svc_id == svc_id
    else:
        q = db.svcdisks.node_id == node_id
    l1 = db.diskinfo.on(db.svcdisks.disk_id==db.diskinfo.disk_id)
    l2 = db.nodes.on(db.nodes.node_id==db.svcdisks.node_id)
    l3 = db.services.on(db.services.svc_id==db.svcdisks.svc_id)

    o = db.svcdisks.disk_id | db.services.svcname | db.nodes.nodename
    rows = db(q).select(
        db.nodes.nodename,
        db.services.svcname,
        db.svcdisks.disk_id,
        db.svcdisks.disk_size,
        db.diskinfo.disk_alloc,
        db.diskinfo.disk_devid,
        db.diskinfo.disk_name,
        db.diskinfo.disk_raid,
        db.diskinfo.disk_arrayid,
        db.diskinfo.disk_group,
        left=(l1,l2,l3),
    )

    labels = ["node name", "service name", "wwid", "size", "allocated",
              "array device id", "array device name", "raid",
              "array id", "array disk group"]
    data = [labels]
    for row in rows:
        data += [[
                  str(row.nodes.nodename),
                  str(row.services.svcname),
                  str(row.svcdisks.disk_id),
                  str(row.svcdisks.disk_size),
                  str(row.diskinfo.disk_alloc),
                  str(row.diskinfo.disk_devid),
                  str(row.diskinfo.disk_name),
                  str(row.diskinfo.disk_raid),
                  str(row.diskinfo.disk_arrayid),
                  str(row.diskinfo.disk_group)]]
    return {"ret": 0, "msg": "", "data": data}

@service.xmlrpc
@service.jsonrpc2
def collector_list_nodes(cmd, auth):
    return rpc_collector_list_nodes(cmd, auth)

@auth_uuid
def rpc_collector_list_nodes(cmd, auth):
    return {"ret": 1, "msg": "This feature is no longer supported. Please use the collector Rest API."}

@service.xmlrpc
@service.jsonrpc2
def collector_list_services(cmd, auth):
    return rpc_collector_list_services(cmd, auth)

@auth_uuid
def rpc_collector_list_services(cmd, auth):
    return {"ret": 1, "msg": "This feature is no longer supported. Please use the collector Rest API."}

@service.xmlrpc
@service.jsonrpc2
def collector_list_filtersets(cmd, auth):
    return rpc_collector_list_filtersets(cmd, auth)

@auth_uuid
def rpc_collector_list_filtersets(cmd, auth):
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

def batch_update_dash_checks_all():
    update_dash_checks_all()

def batch_update_save_checks():
    update_save_checks()

def batch_async_post_insert_nsr():
    async_post_insert_nsr()

@service.xmlrpc
@service.jsonrpc2
def sysreport_lstree(auth):
    return rpc_sysreport_lstree(auth)

@auth_uuid
def rpc_sysreport_lstree(auth):
    from applications.init.modules import gittrack
    node_id = auth_to_node_id(auth)
    tree_data = gittrack.gittrack().lstree_data("HEAD", node_id)
    return map(lambda d: d['fpath'], tree_data)

@service.xmlrpc
@service.jsonrpc2
def push_status(svcname, data, auth):
    return _push_status(svcname, data, auth)

##############################################################################
#
# OpenSVC Daemon feeders
#
##############################################################################
@service.xmlrpc
@service.jsonrpc2
def daemon_ping(auth):
    return rpc_daemon_ping(auth)

@auth_uuid
def rpc_daemon_ping(auth):
    node_id = auth_to_node_id(auth)
    elem = json.dumps([node_id])
    ret = rconn.hexists(R_DAEMON_STATUS_HASH, node_id)
    if not ret:
        return {"ret": 1, "info": "resync"}
    rconn.lrem(R_DAEMON_PING, 0, elem)
    rconn.rpush(R_DAEMON_PING, elem)

@service.xmlrpc
@service.jsonrpc2
def push_daemon_status(data, changes, auth):
    return rpc_push_daemon_status(data, changes, auth)

@auth_uuid
def rpc_push_daemon_status(data, changes, auth):
    """
    Store the json daemon status in a hash indexed by uuid, and add the
    uuid to the set of keys pending merge into db.
    """
    node_id = auth_to_node_id(auth)

    # store daemon status data
    rconn.hset(R_DAEMON_STATUS_HASH, node_id, data)

    # merge changes with pending changes, and store
    changes = set(json.loads(changes))
    pending_changes = rconn.hget(R_DAEMON_STATUS_CHANGES_HASH, node_id)
    if pending_changes:
        changes |= set(json.loads(pending_changes))
    rconn.hset(R_DAEMON_STATUS_CHANGES_HASH, node_id, json.dumps(list(changes)))

    # mark the node as needing attention from task_rq
    key = json.dumps([node_id])
    rconn.lrem(R_DAEMON_STATUS, 0, key)
    rconn.rpush(R_DAEMON_STATUS, key)

##############################################################################
#
# Test functions
#
##############################################################################
def test_task_dash_hourly():
    task_dash_hourly()

def test_cron_dash_app_without_responsible():
    cron_dash_app_without_responsible()

def scheduler_cleanup():
    """
      - Delete scheduler keys in redis.
      - Set the tasks status to QUEUED.

      Used by the scheduler launcher script.
    """
    l = rconn.keys("w2p:rsched:*")
    print "Delete the web2py scheduler redis keys:\n" + "\n ".join(l)
    rconn.delete(l)

    print "Set the web2py scheduler tasks status to QUEUED"
    sql = """ update scheduler_task set status="QUEUED" """
    db.executesql(sql)

    print "Purge the scheduler runs"
    sql = """ truncate scheduler_run """
    db.executesql(sql)
    db.commit()

def _task_rq_storage(*args):
    args = list(args)
    fn = args.pop(0)
    globals()[fn](*args)

def task_rq_storage():
    task_rq(R_STORAGE, lambda q: _task_rq_storage)

def _task_rq_generic(q):
    if q == R_RESINFO:
        return _update_resinfo
    elif q == R_SVCCONF:
        return _update_service
    elif q == R_CHECKS:
        return _push_checks
    elif q == R_GENERIC:
        return _insert_generic
    elif q == R_ASSET:
        return _update_asset
    elif q == R_PACKAGES:
        return _insert_pkg
    elif q == R_PATCHES:
        return _insert_patch
    elif q == R_SYSREPORT:
        return task_send_sysreport

def task_rq_generic():
    task_rq([
        R_ASSET,
        R_SVCCONF,
        R_CHECKS,
        R_RESINFO,
        R_SYSREPORT,
        R_PACKAGES,
        R_PATCHES,
        R_GENERIC,
    ], lambda q: _task_rq_generic(q))

def task_rq_dashboard():
    task_rq(R_UPDATE_DASH_NETDEV_ERRORS, lambda q: update_dash_netdev_errors)

def task_rq_svcactions():
    task_rq(R_SVCACTIONS, lambda q: _action_wrapper)

def task_rq_svcmon():
    task_rq([
        R_DAEMON_PING,
        R_DAEMON_STATUS,
        R_SVCMON,
        R_SVCMON_UPDATE,
    ], lambda q: _task_rq_svcmon(q))

def _task_rq_svcmon(q):
    if q == R_DAEMON_STATUS:
        return merge_daemon_status
    elif q == R_DAEMON_PING:
        return merge_daemon_ping
    elif q == R_SVCMON:
        return _svcmon_update_combo
    elif q == R_SVCMON_UPDATE:
        return _svcmon_update

