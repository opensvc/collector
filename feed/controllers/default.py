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
    def new(*args, **kwargs):
        uuid, node = kwargs['auth']
        rows = db((db.auth_node.nodename==node)&(db.auth_node.uuid==uuid)).select(cacheable=True)
        if len(rows) != 1:
            return "agent authentication error"
        return fn(*args, **kwargs)
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
    scheduler.queue_task("_action_wrapper", ["_begin_action", vars, vals, auth],
                         group_name="actions")

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
    scheduler.queue_task("_action_wrapper", ["_end_action", vars, vals, auth],
                         group_name="actions")

@auth_uuid
@service.xmlrpc
def update_appinfo(vars, vals, auth):
    if len(vals) == 0:
        return
    h = {}
    for a,b in zip(vars, vals[0]):
        h[a] = b
    if "cluster_type" in h and "flex" in h["cluster_type"]:
        db.executesql("delete from appinfo where app_svcname='%s' and app_nodename='%s'"%(h['app_svcname'], h['app_nodename']))
    else:
        db.executesql("delete from appinfo where app_svcname='%s'"%h['app_svcname'])
    generic_insert('appinfo', vars, vals)

    i = vars.index('app_value')
    vals_log = []
    for _vals in vals:
        try:
            n = float(_vals[i])
            vals_log.append(_vals)
        except:
            pass

    if len(vals_log) > 0:
        generic_insert('appinfo_log', vars, vals_log)

@auth_uuid
@service.xmlrpc
def update_service(vars, vals, auth):
    scheduler.queue_task("_update_service", [vars, vals, auth],
                         group_name="_update_service")

@auth_uuid
@service.xmlrpc
def push_checks(vars, vals, auth):
    scheduler.queue_task("_push_checks", [vars, vals],
                         group_name="_push_checks")

@auth_uuid
@service.xmlrpc
def insert_generic(data, auth):
    scheduler.queue_task("_insert_generic", [data, auth],
                         group_name="_insert_generic")

@auth_uuid
@service.xmlrpc
def update_asset(vars, vals, auth):
    scheduler.queue_task("_update_asset", [vars, vals, auth],
                         group_name="_update_asset")

@auth_uuid
@service.xmlrpc
def update_asset_sync(vars, vals, auth):
    _update_asset(vars, vals, auth)

@auth_uuid
@service.xmlrpc
def res_action_batch(vars, vals, auth):
    generic_insert('SVCactions', vars, vals)

@auth_uuid
@service.xmlrpc
def resmon_update(vars, vals, auth):
    _resmon_update(vars, vals, auth)

@auth_uuid
@service.xmlrpc
def svcmon_update_combo(g_vars, g_vals, r_vars, r_vals, auth):
    scheduler.queue_task("_svcmon_update_combo",
                         [g_vars, g_vals, r_vars, r_vals, auth],
                         group_name="_svcmon_update_combo")

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

def get_vcpus(nodename, vmname):
    if nodename == vmname:
        return None

    sql = """select mon_vcpus from svcmon where
               mon_nodname = "%s" and
               mon_vmname = "%s" """%(nodename, vmname)
    try:
        return db.executesql(sql)[0][0]
    except:
        return 1

@auth_uuid
@service.xmlrpc
def insert_stats(data, auth):
    import cPickle
    h = cPickle.loads(data)
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
                    vcpus = str(get_vcpus(auth[1], vmname))
                    cache[vmname] = vcpus
                vals[i].append(vcpus)
        max = 10000
        while len(vals) > max:
            generic_insert('stats_'+stat, vars, vals[:max])
            vals = vals[max:]
        generic_insert('stats_'+stat, vars, vals)
    scheduler.queue_task("update_dash_netdev_errors" , [auth[1]],
                         group_name="update_dash_netdev_errors", timeout=120)

@auth_uuid
@service.xmlrpc
def insert_pkg(vars, vals, auth):
    scheduler.queue_task("_insert_pkg", [vars, vals, auth],
                         group_name="_insert_pkg", timeout=120)

@auth_uuid
@service.xmlrpc
def insert_patch(vars, vals, auth):
    scheduler.queue_task("_insert_patch", [vars, vals, auth],
                         group_name="_insert_patch", timeout=120)

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
def update_hp3par(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "hp3par", insert_hp3par)

@auth_uuid
@service.xmlrpc
def update_ibmsvc(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "ibmsvc", insert_ibmsvc)

@auth_uuid
@service.xmlrpc
def update_ibmds(name, vars, vals, auth):
    update_array_xml(name, vars, vals, auth, "ibmds", insert_ibmds)

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
    scheduler.queue_task(fn.__name__, [arrayid, auth[1]], group_name="slow", timeout=600)

    # stor_array_proxy
    insert_array_proxy(auth[1], arrayid)

    # clean up stor_array_*
    sql = "delete from stor_array_dg where array_id not in (select id from stor_array)"
    db.executesql(sql)

    sql = "delete from stor_array_tgtid where array_id not in (select id from stor_array)"
    db.executesql(sql)

    sql = "delete from stor_array_proxy where array_id not in (select id from stor_array)"
    db.executesql(sql)

    sql = "delete from stor_array_dg_quota where stor_array_dg_quota.dg_id not in (select id from stor_array_dg)"
    db.executesql(sql)

def insert_dcss():
    return insert_dcs()

def insert_hdss():
    return insert_hds()

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
    scheduler.queue_task("_svcmon_update", [vars, vals, auth],
                         group_name="_svcmon_update_combo")


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
def collector_update_root_pw(data, auth):
    nodename = auth[1]
    pw = data.get('pw')
    if pw is None:
        return {"ret": 1, "msg": "misformatted data"}
    sql = """select uuid from auth_node where nodename="%(nodename)s"
          """ % dict(nodename=nodename)
    rows = db.executesql(sql)
    if len(rows) == 0:
        return {"ret": 1, "msg": "node is not registered"}
    uuid = rows[0][0]

    #config = local_import('config', reload=True)
    from applications.init.modules import config
    try:
        salt = config.aes_salt
    except Exception as e:
        salt = "tlas"

    sql = """insert into node_pw set
              nodename="%(nodename)s",
              pw=aes_encrypt("%(pw)s", "%(uuid)s")
             on duplicate key update
              pw=aes_encrypt("%(pw)s", "%(uuid)s"),
              updated=now()
          """ % dict(nodename=nodename, pw=pw, uuid=uuid+salt)
    db.executesql(sql)
    return {"ret": 0, "msg": "password updated succesfully"}

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
    data = [["action id",
             "node name",
             "service name",
             "begin",
             "action",
             "status",
             "acknowledged",
             "log"]]
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
def collector_update_action_queue(data, auth):
    nodename = auth[1]
    for id, ret, out, err in data:
        q = db.action_queue.id == id
        q &= db.action_queue.nodename == nodename
        db(q).update(stdout=out, stderr=err, ret=ret, status="T", date_dequeued=datetime.datetime.now())

@auth_uuid
@service.xmlrpc
def collector_get_action_queue(nodename, auth):
    q = db.action_queue.nodename == nodename
    q &= db.action_queue.action_type == "pull"
    q &= db.action_queue.status == "W"
    sql = db(q)._select()
    data = db.executesql(sql, as_dict=True)
    if len(data) > 0:
        db(q).update(status="Q")
        db.commit()
    return data

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
    header = ['action id',
              'node name',
              'service name',
              'begin',
              'end',
              'action',
              'status',
              'acknowledged',
              'scheduled']
    data = [header]
    for row in rows:
        data.append([
          str(row.id),
          str(row.hostname),
          str(row.svcname),
          str(row.begin),
          str(row.end),
          str(row.action),
          str(row.status),
          str(row.ack),
          str(row.cron)
        ])

    return {"ret": 0, "msg": "", "data":data}

@auth_uuid
@service.xmlrpc
def collector_status(cmd, auth):
    d = {}
    nodename = auth[1]

    if "svcname" in cmd:
        q = db.svcmon.mon_svcname == cmd["svcname"]
        q &= (db.svcmon.mon_nodname == nodename) | (db.svcmon.mon_vmname == nodename)
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%cmd["svcname"]}

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
    header = ['node name',
              'service instance',
              'host mode',
              'availability status',
              'overall status',
              'status last update']
    data = [header]
    for row in rows:
        data.append([
          str(row.svcmon.mon_nodname),
          str(row.svcmon.mon_svcname),
          str(row.nodes.host_mode),
          str(row.svcmon.mon_availstatus),
          str(row.svcmon.mon_overallstatus),
          str(row.svcmon.mon_updated)
        ])

    return {"ret": 0, "msg": "", "data":data}

@auth_uuid
@service.xmlrpc
def collector_networks(cmd, auth):
    nodename = auth[1]

    if "svcname" in cmd:
        q = db.svcmon.mon_svcname == cmd["svcname"]
        q &= db.svcmon.mon_nodname == nodename
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%svcname}

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
                   networks.broadcast,
                   networks.netmask,
                   networks.gateway,
                   networks.begin,
                   networks.end
                 from node_ip, networks
                 where
                   node_ip.nodename = "%(nodename)s" and
                   inet_aton(node_ip.addr) > inet_aton(begin) and
                   inet_aton(node_ip.addr)  < inet_aton(end)""" % dict(nodename=nodename)
        rows = db.executesql(sql)
        header = [
          'ip',
          'mac',
          'interface',
          'net name',
          'net comment',
          'net pvid',
          'net base',
          'net broadcast',
          'net mask',
          'net gateway',
          'net begin',
          'net end'
        ]
        data = [header]
        for row in rows:
            data.append(map(lambda x: unicode(x), row))
    return {"ret": 0, "msg": "", "data": data}


@auth_uuid
@service.xmlrpc
def collector_asset(cmd, auth):
    d = {}
    nodename = auth[1]

    if "svcname" in cmd:
        q = db.svcmon.mon_svcname == cmd["svcname"]
        q &= db.svcmon.mon_nodname == nodename
        n = db(q).count()
        if n == 0:
            return {"ret": 1, "msg": "this node is not owner of %s"%svcname}

    if "svcname" in cmd:
        pass
    else:
        q = db.nodes.nodename == nodename
        j = db.nodes.project == db.apps.app
        l = db.apps.on(j)
        rows = db(q).select(
          db.nodes.ALL,
          db.apps.ALL,
          cacheable=True, left=l
        )

        header = [
          'node',
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
          'server, team responsible',
          'server, team support',
          'server, team integration',
          'server, host mode',
          'server, environment',
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
          'app, domain',
          'app, operations team',
          'updated',
        ]
        data = [header]
        for row in rows:
            data.append([
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
              str(row.nodes.team_responsible),
              str(row.nodes.team_support),
              str(row.nodes.team_integ),
              str(row.nodes.host_mode),
              str(row.nodes.environnement),
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
              str(row.apps.app_domain) if row.apps.app_domain is not None else "",
              str(row.apps.app_team_ops) if row.apps.app_team_ops is not None else "",
              str(row.nodes.updated)
            ])


    return {"ret": 0, "msg": "", "data": data}

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
                        db.checks_live.chk_updated,
                        limitby=(0,1000)
                       )
    header = ['service',
              'instance',
              'type',
              'value',
              'low threshold',
              'high threshold',
              'threshold provider',
              'last update date']
    data = [header]
    for row in rows:
        data.append([
          str(row.chk_svcname),
          str(row.chk_instance),
          str(row.chk_type),
          str(row.chk_value),
          str(row.chk_low),
          str(row.chk_high),
          str(row.chk_threshold_provider),
          str(row.chk_updated)
        ])
    return {"ret": 0, "msg": "", "data":data}

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
    data = [["severity", "type", "node", "service", "alert", "created"]]
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
    data = [["date", "node", "service", "level", "action", "event"]]
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
def collector_service_status(cmd, auth):
    d = {}
    svcname = cmd["svcname"]
    q = db.services.svc_name == svcname
    row = db(q).select(db.services.svc_availstatus).first()
    if row is None:
        return {"ret": 1, "msg": "service not found %s"%svcname}
    d[svcname] = {"availstatus": row. svc_availstatus}
    return {"ret": 0, "msg": "", "data": d}

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

    labels = ["node name", "service name", "wwid", "size", "allocated",
              "array device id", "array device name", "raid",
              "array id", "array disk group"]
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


