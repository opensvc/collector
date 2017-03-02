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
def begin_action(vars, vals, auth):
    return rpc_begin_action(vars, vals, auth)

@auth_uuid
def rpc_begin_action(vars, vals, auth):
    rconn.rpush("osvc:q:svcactions", json.dumps(["_begin_action", vars, vals, auth]))

@service.xmlrpc
def res_action(vars, vals, auth):
    return rpc_res_action(vars, vals, auth)

@auth_uuid
def rpc_res_action(vars, vals, auth):
    vars, vals = replace_nodename_in_data(vars, vals, auth)
    vars, vals = replace_svcname_in_data(vars, vals, auth)
    generic_insert('svcactions', vars, vals, node_id=auth_to_node_id(auth))
    return 0

@service.xmlrpc
def end_action(vars, vals, auth):
    return rpc_end_action(vars, vals, auth)

@auth_uuid
def rpc_end_action(vars, vals, auth):
    rconn.rpush("osvc:q:svcactions", json.dumps(["_end_action", vars, vals, auth]))

@service.xmlrpc
def update_appinfo(vars, vals, auth):
    """
    'svcmgr push resinfo' data feeder.

    Compatibilty entrypoint with old agents.
    The up-to-date entrypoint is update_resinfo.
    """
    return rpc_update_resinfo(vars, vals, auth)

@service.xmlrpc
def update_resinfo(vars, vals, auth):
    """
    'svcmgr push resinfo' data feeder.
    """
    return rpc_update_resinfo(vars, vals, auth)

@auth_uuid
def rpc_update_resinfo(vars, vals, auth):
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)
    if len(vals) == 0:
        return
    h = {}
    if "app_nodename" in vars:
        node_k = "app_nodename"
    else:
        node_k = "res_nodename"
    if "app_svcname" in vars:
        svc_k = "app_svcname"
    else:
        svc_k = "res_svcname"
    vars, vals = replace_nodename_in_data(vars, vals, auth, fieldname=node_k)
    vars, vals = replace_svcname_in_data(vars, vals, auth, fieldname=svc_k)
    updated_idx = None
    for i, v in enumerate(vars):
        if v == "app_launcher":
            vars[i] = "rid"
        elif v == "app_key":
            vars[i] = "res_key"
        elif v == "app_value":
            vars[i] = "res_value"
        elif v == "app_updated":
            updated_idx = i
            vars[i] = "updated"
    if not updated_idx:
        vars.append("updated")
        updated_idx = len(vars) - 1
    for i, v in enumerate(vals):
        vals[i].append(now)
    for a,b in zip(vars, vals[0]):
        h[a] = b
    generic_insert('resinfo', vars, vals)
    if "cluster_type" in h and "flex" in h["cluster_type"]:
        db.executesql("""delete from resinfo where svc_id='%s' and node_id="%s" and updated<'%s' """%(h["svc_id"], h["node_id"], str(now)))
    else:
        db.executesql("""delete from resinfo where svc_id='%s' and updated<'%s' """%(h["svc_id"], str(now)))
    ws_send("resinfo_change")

    i = vars.index('res_value')
    vals_log = []
    for _vals in vals:
        try:
            n = float(_vals[i])
            vals_log.append(_vals)
        except:
            pass

    if len(vals_log) > 0:
        generic_insert('resinfo_log', vars, vals_log)

@service.xmlrpc
def update_service(vars, vals, auth):
    return rpc_update_service(vars, vals, auth)

@auth_uuid
def rpc_update_service(vars, vals, auth):
    rconn.rpush("osvc:q:svcconf", json.dumps([vars, vals, auth]))

@service.xmlrpc
def push_checks(vars, vals, auth):
    return rpc_push_checks(vars, vals, auth)

@auth_uuid
def rpc_push_checks(vars, vals, auth):
    rconn.rpush("osvc:q:checks", json.dumps([vars, vals, auth]))

@service.xmlrpc
def insert_generic(data, auth):
    return rpc_insert_generic(data, auth)

@auth_uuid
def rpc_insert_generic(data, auth):
    rconn.rpush("osvc:q:generic", json.dumps([data, auth]))

@service.xmlrpc
def update_asset(vars, vals, auth):
    return rpc_update_asset(vars, vals, auth)

@auth_uuid
def rpc_update_asset(vars, vals, auth):
    rconn.rpush("osvc:q:asset", json.dumps([vars, vals, auth]))

@service.xmlrpc
def update_asset_sync(vars, vals, auth):
    return rpc_update_asset_sync(vars, vals, auth)

@auth_uuid
def rpc_update_asset_sync(vars, vals, auth):
    _update_asset(vars, vals, auth)

@service.xmlrpc
def res_action_batch(vars, vals, auth):
    return rpc_res_action_batch(vars, vals, auth)

@auth_uuid
def rpc_res_action_batch(vars, vals, auth):
    vars, vals = replace_nodename_in_data(vars, vals, auth, fieldname="hostname")
    vars, vals = replace_svcname_in_data(vars, vals, auth)
    generic_insert('svcactions', vars, vals, node_id=auth_to_node_id(auth))

@service.xmlrpc
def resmon_update(vars, vals, auth):
    return rpc_resmon_update(vars, vals, auth)

@auth_uuid
def rpc_resmon_update(vars, vals, auth):
    _resmon_update(vars, vals, auth)

@service.xmlrpc
def svcmon_update_combo(g_vars, g_vals, r_vars, r_vals, auth):
    return rpc_svcmon_update_combo(g_vars, g_vals, r_vars, r_vals, auth)

@auth_uuid
def rpc_svcmon_update_combo(g_vars, g_vals, r_vars, r_vals, auth):
    rconn.rpush("osvc:q:svcmon", json.dumps([g_vars, g_vals, r_vars, r_vals, auth]))

def test_sched():
    s = """[["mon_svcname", "mon_svctype", "mon_nodname", "mon_vmname", "mon_vmtype", "mon_nodtype", "mon_ipstatus", "mon_diskstatus", "mon_syncstatus", "mon_hbstatus", "mon_containerstatus", "mon_fsstatus", "mon_sharestatus", "mon_appstatus", "mon_availstatus", "mon_overallstatus", "mon_updated", "mon_prinodes", "mon_frozen"], [[["collector", "DEV", "clementine", "", "docker", "DEV", "up", "n/a", "n/a", "n/a", "up", "n/a", "n/a", "n/a", "up", "up", "2016-05-27 07:40:29.127541", "clementine", "0"]]], ["svcname", "nodename", "vmname", "rid", "res_type", "res_desc", "res_status", "res_monitor", "res_optional", "res_disable", "updated", "res_log"], [[["'collector'", "'clementine'", "", "'container#0'", "'container.docker'", "'collector.container.0@ubuntu:14.10'", "'up'", "0", "0", "0", "'2016-05-27 07:40:29.127541'", ""], ["'collector'", "'clementine'", "", "'container#1'", "'container.docker'", "'collector.container.1@opensvc/collector_db:build5'", "'up'", "0", "0", "0", "'2016-05-27 07:40:29.127541'", ""], ["'collector'", "'clementine'", "", "'container#2'", "'container.docker'", "'collector.container.2@opensvc/collector_nginx:build1'", "'up'", "0", "0", "0", "'2016-05-27 07:40:29.127541'", ""], ["'collector'", "'clementine'", "", "'container#3'", "'container.docker'", "'collector.container.3@opensvc/collector_redis:build1'", "'up'", "0", "0", "0", "'2016-05-27 07:40:29.127541'", ""], ["'collector'", "'clementine'", "", "'container#4'", "'container.docker'", "'collector.container.4@opensvc/collector_web2py:build8'", "'up'", "0", "0", "0", "'2016-05-27 07:40:29.127541'", ""], ["'collector'", "'clementine'", "", "'ip#0'", "'ip'", "'10.0.3.3@lxcbr0@2d2dd2da46c25fd728ec020957a50be7a5c9d0cad67efd35cc845f3a94655622'", "'up'", "0", "0", "0", "'2016-05-27 07:40:29.127541'", ""], ["'collector'", "'clementine'", "", "'sync#1'", "'sync.rsync'", "'rsync /unxdevweb/apps/ to nodes'", "'None'", "0", "0", "1", "'2016-05-27 07:40:29.127541'", ""], ["'collector'", "'clementine'", "", "'sync#2'", "'sync.s3'", "'s3 backup'", "'None'", "0", "0", "1", "'2016-05-27 07:40:29.127541'", ""], ["'collector'", "'clementine'", "", "'sync#0'", "'sync.docker'", "'docker img sync to nodes'", "'None'", "0", "0", "1", "'2016-05-27 07:40:29.127541'", ""]]], ["d446fee3-328d-4493-9db9-b1118600eee8", "clementine"]]"""
    for i in range(10000):
        rconn.rpush("osvc:q:svcmon", s)

    s = """[["chk_nodename", "chk_svcname", "chk_type", "chk_instance", "chk_value", "chk_updated"], [["clementine", "", "fs_u", "/dev", "0", "2016-05-29 18:53:59.173156"], ["clementine", "", "fs_u", "/", "37", "2016-05-29 18:53:59.173156"], ["clementine", "", "fs_u", "/boot", "72", "2016-05-29 18:53:59.173156"], ["clementine", "", "fs_u", "/boot/efi", "1", "2016-05-29 18:53:59.173156"], ["clementine", "", "fs_u", "/opt/opensvc/var/collector_docker_data_dir/aufs/mnt/2d2dd2da46c25fd728ec020957a50be7a5c9d0cad67efd35cc845f3a94655622", "37", "2016-05-29 18:53:59.173156"], ["clementine", "", "fs_u", "/opt/opensvc/var/collector_docker_data_dir/aufs/mnt/468422df1da19c092b7ac56d0ac2cd58d81902a76e5a76637e50fa86a6933df8", "37", "2016-05-29 18:53:59.173156"], ["clementine", "", "fs_u", "/opt/opensvc/var/collector_docker_data_dir/aufs/mnt/45bbdec90c96812b8cbe5b9292cdd26f1250f2eff302fcc0396b57e05c4a0369", "37", "2016-05-29 18:53:59.173156"], ["clementine", "", "fs_u", "/opt/opensvc/var/collector_docker_data_dir/aufs/mnt/fb5160838b1cc64e5e57d09903cb78dff4b097fc14e62554af26b466dbb7b2f2", "37", "2016-05-29 18:53:59.173156"], ["clementine", "", "fs_u", "/opt/opensvc/var/collector_docker_data_dir/aufs/mnt/3c66df033247306bbd4525d78fe5da71b67d057cabaaf94b0e0574c239eee4e2", "37", "2016-05-29 18:53:59.173156"], ["clementine", "", "fs_i", "/dev", "1", "2016-05-29 18:53:59.173156"], ["clementine", "", "fs_i", "/", "3", "2016-05-29 18:53:59.173156"], ["clementine", "", "fs_i", "/boot", "1", "2016-05-29 18:53:59.173156"], ["clementine", "", "fs_i", "/opt/opensvc/var/collector_docker_data_dir/aufs/mnt/2d2dd2da46c25fd728ec020957a50be7a5c9d0cad67efd35cc845f3a94655622", "3", "2016-05-29 18:53:59.173156"], ["clementine", "", "fs_i", "/opt/opensvc/var/collector_docker_data_dir/aufs/mnt/468422df1da19c092b7ac56d0ac2cd58d81902a76e5a76637e50fa86a6933df8", "3", "2016-05-29 18:53:59.173156"], ["clementine", "", "fs_i", "/opt/opensvc/var/collector_docker_data_dir/aufs/mnt/45bbdec90c96812b8cbe5b9292cdd26f1250f2eff302fcc0396b57e05c4a0369", "3", "2016-05-29 18:53:59.173156"], ["clementine", "", "fs_i", "/opt/opensvc/var/collector_docker_data_dir/aufs/mnt/fb5160838b1cc64e5e57d09903cb78dff4b097fc14e62554af26b466dbb7b2f2", "3", "2016-05-29 18:53:59.173156"], ["clementine", "", "fs_i", "/opt/opensvc/var/collector_docker_data_dir/aufs/mnt/3c66df033247306bbd4525d78fe5da71b67d057cabaaf94b0e0574c239eee4e2", "3", "2016-05-29 18:53:59.173156"], ["clementine", "testmd", "vg_u", "testmd", "14", "2016-05-29 18:53:59.173156"], ["clementine", "", "vg_u", "ubuntu-vg", "99", "2016-05-29 18:53:59.173156"]], ["d446fee3-328d-4493-9db9-b1118600eee8", "clementine"]]"""
    #for i in range(1000):
    #    rconn.rpush("osvc:q:checks", s)

    s = """[["loc_city", "mem_banks", "sec_zone", "mem_bytes", "os_kernel", "cpu_dies", "cpu_cores", "node_env", "serial", "enclosure", "os_vendor", "cpu_freq", "tz", "os_arch", "version", "os_name", "mem_slots", "nodename", "cpu_model", "last_boot", "cpu_threads", "listener_port", "fqdn", "os_release", "model"], ["aubervillier", "2", "d\\u00e4mz\\u00e9", "3863", "4.4.0-22-generic", "1", "2", "DEV", "1005661700762", "Unknown", "Ubuntu", "1616", "+02:00", "x86_64", "1.7-10269", "Linux", "4", "clementine", "Intel(R) Core(TM) i5-4200U CPU @ 1.60GHz", "2016-05-19", "4", "1215", "clementine", "16.04", "20266"], ["d446fee3-328d-4493-9db9-b1118600eee8", "clementine"]]"""
    #for i in range(1000):
    #    rconn.rpush("osvc:q:asset", s)

    s = """[["svc_hostid", "svc_name", "svc_cluster_type", "svc_flex_min_nodes", "svc_flex_max_nodes", "svc_flex_cpu_low_threshold", "svc_flex_cpu_high_threshold", "svc_env", "svc_nodes", "svc_drpnode", "svc_drpnodes", "svc_comment", "svc_drptype", "svc_autostart", "svc_app", "svc_containertype", "svc_config", "svc_drnoaction", "svc_ha"], ["\'78599105757308\'", "\'testmd\'", "\'flex\'", "1", "1", "10", "90", "\'DEV\'", "\'nuc clementine\'", "\'\'", "\'\'", "\'\'", "\'\'", "\'\'", "\'OpenSVC\'", "\'hosted\'", "\'[DEFAULT]\\\\napp = OpenSVC\\\\nservice_type = DEV\\\\nnodes = clementine nuc\\\\nflex_primary = clementine\\\\nmon_schedule = @1\\\\ndisable = False\\\\nrollback = false\\\\ncreate_pg = true\\\\npg_cpu_quota = -1\\\\npg_cpus = 1-2\\\\npg_mem_limit = 3MB\\\\npg_mem_oom_control = 1\\\\nflex_primary = clementine\\\\ncluster_type = flex\\\\n[ip#0]\\\\ndisable = true\\\\ndisable@flex_primary = false\\\\nipname = 128.1.11.1\\\\nnetmask = 32\\\\nipdev = lo\\\\n[subset#disk:g1]\\\\nparallel = false\\\\n[subset#disk:g2]\\\\nparallel = false\\\\n[subset#disk:g3]\\\\nparallel = false\\\\n[subset#app:ga1]\\\\npg_cpu_quota = 10%@all\\\\n[subset#app:ga2]\\\\npg_cpu_quota = 50%\\\\n[disk#05]\\\\nsize = 11mib\\\\ntype = loop\\\\nfile = /opt/testmd/dd6\\\\nsubset = g3\\\\n[disk#04]\\\\ntype = loop\\\\nfile = /opt/testmd/dd5\\\\nsubset = g3\\\\n[disk#03]\\\\ntags = tag1 tag2\\\\ntype = loop\\\\nfile = /opt/testmd/dd4\\\\nsubset = g2\\\\n[disk#02]\\\\ntags = tag1 tag3\\\\ntype = loop\\\\nfile = /opt/testmd/dd3\\\\nsubset = g2\\\\n[disk#01]\\\\ntype = loop\\\\nfile = /opt/testmd/dd2\\\\nsubset = g1\\\\n[disk#00]\\\\ntype = loop\\\\nfile = /opt/testmd/dd1\\\\nsubset = g1\\\\n[disk#10pr]\\\\noptional = true\\\\nrestart = 1\\\\nmonitor = true\\\\ntags = foo\\\\n[disk#10]\\\\ntype = md\\\\nuuid@clementine = b742617b:d8a76908:5ec4db5e:5e4d920b\\\\nsubset = g1\\\\nscsireserv = true\\\\ntags = bar\\\\n[disk#11]\\\\ntype = md\\\\nuuid = c4f79d3d:64d4f8df:8b2d28eb:65997b84\\\\nsubset = g2\\\\n[disk#12]\\\\ntype = md\\\\nuuid = e6a6703e:3919c7e9:fe47185f:6e9d777a\\\\nsubset = g3\\\\npost_start = /bin/true\\\\n[disk#30]\\\\ntype = lvm\\\\nvgname = testmd\\\\nsubset = g3\\\\npre_start = /bin/true\\\\npost_start = kpartx -a /dev/testmd/testmd\\\\n[app#0]\\\\nscript = /bin/true\\\\nstart = 50\\\\nstop = 50\\\\n[disk#100]\\\\ntype = raw\\\\ncreate_char_devices = false\\\\ndevs = /dev/loop0:/opt/testmd/dev/user/disk100.0\\\\n /dev/loop1:/opt/testmd/dev/user/disk100.1\\\\nuser = cvaroqui\\\\ngroup = cvaroqui\\\\nperm = 644\\\\n[disk#101]\\\\ntype = raw\\\\ndevs = /dev/loop2:/opt/testmd/dev/user/disk100.2\\\\n /dev/loop3:/opt/testmd/dev/user/disk100.3\\\\nuser = cvaroqui\\\\ngroup = cvaroqui\\\\nperm = 644\\\\n[disk#102]\\\\ntype = raw\\\\ncreate_char_devices = false\\\\ndevs = /dev/loop4\\\\nuser = cvaroqui\\\\ngroup = cvaroqui\\\\nperm = 644\\\\n[disk#103]\\\\ntype = raw\\\\ndevs = /dev/loop5\\\\nuser = cvaroqui\\\\ngroup = cvaroqui\\\\nperm = 644\\\\n\'", "False", "1"], ["d446fee3-328d-4493-9db9-b1118600eee8", "clementine"]]"""
    #for i in range(1000):
    #    rconn.rpush("osvc:q:svcconf", s)


@service.xmlrpc
def register_disks(vars, vals, auth):
    return rpc_register_disks(vars, vals, auth)

@auth_uuid
def rpc_register_disks(vars, vals, auth):
    node_id = auth_to_node_id(auth)
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    for v in vals:
        _register_disk(vars, v, auth)

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

@service.xmlrpc
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
def register_disk(vars, vals, auth):
    return rpc_register_disk(vars, vals, auth)

@auth_uuid
def rpc_register_disk(vars, vals, auth):
    _register_disk(vars, vals, auth)

@service.xmlrpc
def register_sync(vars, vals, auth):
    return rpc_register_sync(vars, vals, auth)

@auth_uuid
def rpc_register_sync(vars, vals, auth):
    pass

@service.xmlrpc
def register_ip(vars, vals, auth):
    return rpc_register_ip(vars, vals, auth)

@auth_uuid
def rpc_register_ip(vars, vals, auth):
    pass

@service.xmlrpc
def register_fs(vars, vals, auth):
    return rpc_register_fs(vars, vals, auth)

@auth_uuid
def rpc_register_fs(vars, vals, auth):
    pass

@service.xmlrpc
def insert_stats_fs_u(vars, vals, auth):
    return rpc_insert_stats_fs_u(vars, vals, auth)

@auth_uuid
def rpc_insert_stats_fs_u(vars, vals, auth):
    vars, vals = replace_nodename_in_data(vars, vals, auth)
    generic_insert('stats_fs_u', vars, vals)

@service.xmlrpc
def insert_stats_cpu(vars, vals, auth):
    return rpc_insert_stats_cpu(vars, vals, auth)

@auth_uuid
def rpc_insert_stats_cpu(vars, vals, auth):
    vars, vals = replace_nodename_in_data(vars, vals, auth)
    generic_insert('stats_cpu', vars, vals)

@service.xmlrpc
def insert_stats_mem_u(vars, vals, auth):
    return rpc_insert_stats_mem_u(vars, vals, auth)

@auth_uuid
def rpc_insert_stats_mem_u(vars, vals, auth):
    vars, vals = replace_nodename_in_data(vars, vals, auth)
    generic_insert('stats_mem_u', vars, vals)

@service.xmlrpc
def insert_stats_proc(vars, vals, auth):
    return rpc_insert_stats_proc(vars, vals, auth)

@auth_uuid
def rpc_insert_stats_proc(vars, vals, auth):
    vars, vals = replace_nodename_in_data(vars, vals, auth)
    generic_insert('stats_proc', vars, vals)

@service.xmlrpc
def insert_stats_swap(vars, vals, auth):
    return rpc_insert_stats_swap(vars, vals, auth)

@auth_uuid
def rpc_insert_stats_swap(vars, vals, auth):
    vars, vals = replace_nodename_in_data(vars, vals, auth)
    generic_insert('stats_swap', vars, vals)

@service.xmlrpc
def insert_stats_block(vars, vals, auth):
    return rpc_insert_stats_block(vars, vals, auth)

@auth_uuid
def rpc_insert_stats_block(vars, vals, auth):
    vars, vals = replace_nodename_in_data(vars, vals, auth)
    generic_insert('stats_block', vars, vals)

@service.xmlrpc
def insert_stats_blockdev(vars, vals, auth):
    return rpc_insert_stats_blockdev(vars, vals, auth)

@auth_uuid
def rpc_insert_stats_blockdev(vars, vals, auth):
    vars, vals = replace_nodename_in_data(vars, vals, auth)
    generic_insert('stats_blockdev', vars, vals)

@service.xmlrpc
def insert_stats_netdev(vars, vals, auth):
    return rpc_insert_stats_netdev(vars, vals, auth)

@auth_uuid
def rpc_insert_stats_netdev(vars, vals, auth):
    vars, vals = replace_nodename_in_data(vars, vals, auth)
    generic_insert('stats_netdev', vars, vals)

@service.xmlrpc
def insert_stats_netdev_err(vars, vals, auth):
    return rpc_insert_stats_netdev_err(vars, vals, auth)

@auth_uuid
def rpc_insert_stats_netdev_err(vars, vals, auth):
    vars, vals = replace_nodename_in_data(vars, vals, auth)
    generic_insert('stats_netdev_err', vars, vals)

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
        vars, vals = replace_nodename_in_data(vars, vals, auth)
        max = 10000
        while len(vals) > max:
            try:
                generic_insert('stats_'+stat, vars, vals[:max])
            except Exception as e:
                raise Exception("%s: %s" % (stat, str(e)))
            vals = vals[max:]
        try:
            generic_insert('stats_'+stat, vars, vals)
        except Exception as e:
            raise Exception("%s: %s" % (stat, str(e)))
    rconn.rpush("osvc:q:update_dash_netdev_errors", json.dumps([node_id]))

@service.xmlrpc
def insert_pkg(vars, vals, auth):
    return rpc_insert_pkg(vars, vals, auth)

@auth_uuid
def rpc_insert_pkg(vars, vals, auth):
    rconn.rpush("osvc:q:packages", json.dumps([vars, vals, auth]))

@service.xmlrpc
def insert_patch(vars, vals, auth):
    return rpc_insert_patch(vars, vals, auth)

@auth_uuid
def rpc_insert_patch(vars, vals, auth):
    rconn.rpush("osvc:q:patches", json.dumps([vars, vals, auth]))

@service.xmlrpc
def update_hds(symid, vars, vals, auth):
    return rpc_update_hds(symid, vars, vals, auth)

@auth_uuid
def rpc_update_hds(symid, vars, vals, auth):
    update_array_xml(symid, vars, vals, auth, "hds", insert_hds)

@service.xmlrpc
def update_sym_xml(symid, vars, vals, auth):
    return rpc_update_sym_xml(symid, vars, vals, auth)

@auth_uuid
def rpc_update_sym_xml(symid, vars, vals, auth):
    if len(vars) == 1:
        update_array_xml(symid, vars, vals, auth, "symmetrix", None)
    else:
        update_array_xml(symid, vars, vals, auth, "symmetrix", insert_sym)

@service.xmlrpc
def update_eva_xml(name, vars, vals, auth):
    return rpc_update_eva_xml(name, vars, vals, auth)

@auth_uuid
def rpc_update_eva_xml(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "eva", insert_eva)

@service.xmlrpc
def update_nsr(name, vars, vals, auth):
    return rpc_update_nsr(name, vars, vals, auth)

@auth_uuid
def rpc_update_nsr(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "nsr", insert_nsr)

@service.xmlrpc
def update_netapp(name, vars, vals, auth):
    return rpc_update_netapp(name, vars, vals, auth)

@auth_uuid
def rpc_update_netapp(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "netapp", insert_netapp)

@service.xmlrpc
def update_hp3par(name, vars, vals, auth):
    return rpc_update_hp3par(name, vars, vals, auth)

@auth_uuid
def rpc_update_hp3par(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "hp3par", insert_hp3par)

@service.xmlrpc
def update_ibmsvc(name, vars, vals, auth):
    return rpc_update_ibmsvc(name, vars, vals, auth)

@auth_uuid
def rpc_update_ibmsvc(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "ibmsvc", insert_ibmsvc)

@service.xmlrpc
def update_ibmds(name, vars, vals, auth):
    return rpc_update_ibmds(name, vars, vals, auth)

@auth_uuid
def rpc_update_ibmds(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "ibmds", insert_ibmds)

@service.xmlrpc
def update_brocade(name, vars, vals, auth):
    return rpc_update_brocade(name, vars, vals, auth)

@auth_uuid
def rpc_update_brocade(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "brocade", insert_brocade)

@service.xmlrpc
def update_vioserver(name, vars, vals, auth):
    return rpc_update_vioserver(name, vars, vals, auth)

@auth_uuid
def rpc_update_vioserver(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "vioserver", insert_vioserver)

@service.xmlrpc
def update_centera(name, vars, vals, auth):
    return rpc_update_centera(name, vars, vals, auth)

@auth_uuid
def rpc_update_centera(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "centera", insert_centera)

@service.xmlrpc
def update_emcvnx(name, vars, vals, auth):
    return rpc_update_emcvnx(name, vars, vals, auth)

@auth_uuid
def rpc_update_emcvnx(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "emcvnx", insert_emcvnx)

@service.xmlrpc
def update_necism(name, vars, vals, auth):
    return rpc_update_necism(name, vars, vals, auth)

@auth_uuid
def rpc_update_necism(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "necism", insert_necism)

@service.xmlrpc
def update_freenas(name, vars, vals, auth):
    return rpc_update_freenas(name, vars, vals, auth)

@auth_uuid
def rpc_update_freenas(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "freenas", insert_freenas)

@service.xmlrpc
def update_xtremio(name, vars, vals, auth):
    return rpc_update_xtremio(name, vars, vals, auth)

@auth_uuid
def rpc_update_xtremio(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "xtremio", insert_xtremio)

@service.xmlrpc
def update_gcedisks(name, vars, vals, auth):
    return rpc_update_gcedisks(name, vars, vals, auth)

@auth_uuid
def rpc_update_gcedisks(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "gcedisks", insert_gcedisks)

@service.xmlrpc
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
        try:
            f = codecs.open(a, "w", "utf-8")
            f.write(b)
            f.sync()
            f.close()
        except:
            pass

    if fn is None:
        return

    #fn(arrayid)
    node_id = auth_to_node_id(auth)
    rconn.rpush("osvc:q:storage", json.dumps([fn.__name__, arrayid, node_id]))

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

    rconn.rpush("osvc:q:sysreport", json.dumps([need_commit, deleted, node_id]))

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

@service.xmlrpc
def delete_pkg(node, auth):
    pass

@service.xmlrpc
def delete_patch(node, auth):
    pass

@service.xmlrpc
def delete_syncs(svcname, auth):
    pass

@service.xmlrpc
def delete_ips(svcname, node, auth):
    pass

@service.xmlrpc
def delete_fss(svcname, auth):
    pass

@service.xmlrpc
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
def svcmon_update(vars, vals, auth):
    return rpc_svcmon_update(vars, vals, auth)

@auth_uuid
def rpc_svcmon_update(vars, vals, auth):
    rconn.rpush("osvc:q:svcmon_update", json.dumps([vars, vals, auth]))


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
def collector_update_action_queue(data, auth):
    return rpc_collector_update_action_queue(data, auth)

@auth_uuid
def rpc_collector_update_action_queue(data, auth):
    node_id = auth_to_node_id(auth)
    for id, ret, out, err in data:
        q = db.action_queue.id == id
        q &= db.action_queue.node_id == node_id
        db(q).update(stdout=out, stderr=err, ret=ret, status="T", date_dequeued=datetime.datetime.now())
    action_q_event()
    table_modified("action_queue")

@service.xmlrpc
def collector_get_action_queue(nodename, auth):
    return rpc_collector_get_action_queue(nodename, auth)

@auth_uuid
def rpc_collector_get_action_queue(nodename, auth):
    node_id = auth_to_node_id(auth)
    q = db.action_queue.node_id == node_id
    q &= db.action_queue.action_type == "pull"
    q &= db.action_queue.status == "W"
    l = db.services.on(db.action_queue.svc_id == db.services.svc_id)
    sql = db(q)._select(db.action_queue.ALL, db.services.svcname, left=l)
    data = db.executesql(sql, as_dict=True)
    if len(data) > 0:
        db(q).update(status="Q")
        db.commit()
    return data

@service.xmlrpc
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
                        db.services.svcname,
                        db.svcactions.begin,
                        db.svcactions.end,
                        db.svcactions.action,
                        db.svcactions.status,
                        db.svcactions.ack,
                        db.svcactions.cron,
                        db.svcactions.status_log,
                       )
    header = ['action id',
              'node',
              'service',
              'begin',
              'action',
              'status',
              'acknowledged',
              'scheduled',
              'log']
    data = [header]
    for row in rows:
        data.append([
          str(row.svcactions.id),
          str(row.nodes.nodename),
          str(row.services.svcname),
          str(row.svcactions.begin),
          str(row.svcactions.action),
          str(row.svcactions.status),
          str(row.svcactions.ack),
          str(row.svcactions.cron),
          str(row.svcactions.status_log),
        ])

    return {"ret": 0, "msg": "", "data":data}

@service.xmlrpc
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
      left=l,
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
def collector_list_nodes(cmd, auth):
    return rpc_collector_list_nodes(cmd, auth)

@auth_uuid
def rpc_collector_list_nodes(cmd, auth):
    return {"ret": 1, "msg": "This feature is no longer supported. Please use the collector Rest API."}

@service.xmlrpc
def collector_list_services(cmd, auth):
    return rpc_collector_list_services(cmd, auth)

@auth_uuid
def rpc_collector_list_services(cmd, auth):
    return {"ret": 1, "msg": "This feature is no longer supported. Please use the collector Rest API."}

@service.xmlrpc
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
def sysreport_lstree(auth):
    return rpc_sysreport_lstree(auth)

@auth_uuid
def rpc_sysreport_lstree(auth):
    from applications.init.modules import sysreport
    tree_data = sysreport.sysreport().lstree_data("HEAD", auth[1])
    return map(lambda d: d['fpath'], tree_data)

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
    task_rq("osvc:q:storage", lambda q: _task_rq_storage)

def _task_rq_generic(q):
    if q == "osvc:q:svcconf":
        return _update_service
    elif q == "osvc:q:checks":
        return _push_checks
    elif q == "osvc:q:generic":
        return _insert_generic
    elif q == "osvc:q:asset":
        return _update_asset
    elif q == "osvc:q:packages":
        return _insert_pkg
    elif q == "osvc:q:patches":
        return _insert_patch
    elif q == "osvc:q:sysreport":
        return task_send_sysreport
    elif q == "osvc:q:svcmon_update":
        return _svcmon_update

def task_rq_generic():
    task_rq(["osvc:q:svcmon_update", "osvc:q:sysreport", "osvc:q:patches", "osvc:q:packages", "osvc:q:asset", "osvc:q:generic", "osvc:q:checks", "osvc:q:svcconf"], lambda q: _task_rq_generic(q))

def task_rq_dashboard():
    task_rq("osvc:q:update_dash_netdev_errors", lambda q: update_dash_netdev_errors)

def task_rq_svcactions():
    task_rq("osvc:q:svcactions", lambda q: _action_wrapper)

def task_rq_svcmon():
    task_rq("osvc:q:svcmon", lambda q: _svcmon_update_combo)


