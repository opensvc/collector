# coding: utf8

import datetime
import hashlib

def git_commit(sysreport_d, git_d, nodename):
    import os
    cwd = os.getcwd()

    if not os.path.exists(git_d):
        from applications.init.modules import config
        print "init sysreport git project"
        os.system("git --git-dir=%s init" % git_d)
        os.system("git --git-dir=%s config user.email %s" % (git_d, config.email_from))
        os.system("git --git-dir=%s config user.name collector" % git_d)

    if not os.path.exists(os.path.join(sysreport_d, nodename)):
        print nodename, "dir does not exist in", sysreport_d
        return 0

    os.chdir(sysreport_d)
    os.system("git add %s" % nodename)
    os.system('git commit -m"" %s' % nodename)
    os.chdir(cwd)

    return 0

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
    _websocket_send(event_msg({
                 'event': 'begin_action',
                 'data': h
                }), schedule=False)
    if 'cron' not in h or h['cron'] == '0':
        _log("service.action",
             "action '%(a)s' on %(svc)s@%(node)s",
             dict(a=h['action'],
                  svc=h['svcname'],
                  node=h['hostname']),
             svcname=h['svcname'],
             nodename=h['hostname'])
    return 0

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

    # strip microseconds
    h['begin'] = repr(str(h['begin'].strip("'").split('.')[0]))

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

    _websocket_send(event_msg({
             'event': 'end_action',
             'data': h
            }), schedule=False)

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
    node = db(q).select(cacheable=True).first()
    if node is None:
        return
    fields = ['loc_addr', 'loc_city', 'loc_zip', 'loc_room', 'loc_building',
              'loc_floor', 'loc_rack', 'power_cabinet1', 'power_cabinet2',
              'power_supply_nb', 'power_protect', 'power_protect_breaker',
              'power_breaker1', 'power_breaker2', 'loc_country', 'enclosure']
    sql = "update nodes set "
    for f in fields:
        sql += "%s='%s',"%(f, node[f])
    sql = sql.rstrip(',')
    sql += "where nodename='%s'"%svc.mon_vmname
    db.executesql(sql)

def _update_service(vars, vals, auth):
    if 'svc_hostid' not in vars:
        return
    if 'updated' not in vars:
        vars += ['updated']
        vals += [datetime.datetime.now()]
    h = {}
    for a,b in zip(vars, vals):
        h[a] = b
    if 'svc_version' in h:
        del(h['svc_version'])
    if 'svc_drnoaction' in h:
        if h['svc_drnoaction'] == 'False': h['svc_drnoaction'] = 'F'
        elif h['svc_drnoaction'] == 'True': h['svc_drnoaction'] = 'T'
    vars = []
    vals = []
    for var, val in h.items():
        if var not in ('svc_vmname', 'svc_guestos', 'svc_vcpus', 'svc_vmem', 'svc_containerpath'):
            vars.append(var)
            vals.append(val)
    generic_insert('services', vars, vals)
    db.commit()
    update_dash_service_not_updated(h['svc_name'].strip("'"))
    nodename, vmname, vmtype = translate_encap_nodename(h['svc_name'], auth[1])
    if nodename is not None:
        return
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

def _push_checks(vars, vals):
    """
        chk_nodename
        chk_svcname
        chk_type
        chk_instance
        chk_value
        chk_updated
    """

    n = len(vals)

    # purge old checks
    if n > 0:
        nodename = vals[0][0]
        where = ""
        for v in vals:
             where += """ and not (chk_type="%(chk_type)s" and chk_instance="%(chk_instance)s") """%dict(chk_type=v[2], chk_instance=v[3])
        sql = """delete from checks_live
                 where
                   chk_nodename="%(nodename)s" and
                   chk_type not in ("netdev_err", "save")
                   %(where)s
              """%dict(nodename=nodename, where=where)
        db.executesql(sql)
        db.commit()

        # for checks coming from vservice, update the svcname field
        svcname = vals[0][1]
        if svcname == "":
            q = db.svcmon.mon_vmname == nodename
            row = db(q).select(db.svcmon.mon_svcname, limitby=(0,1)).first()
            if row is not None:
                svcname = row.mon_svcname
                for i, val in enumerate(vals):
                    vals[i][1] = svcname
    else:
        return

     # insert new checks
    while len(vals) > 100:
        generic_insert('checks_live', vars, vals[:100])
        vals = vals[100:]
    generic_insert('checks_live', vars, vals)
    db.commit()

    q = db.checks_live.chk_nodename==nodename
    q &= db.checks_live.chk_type != "netdev_err"
    q &= db.checks_live.chk_type != "save"
    rows = db(q).select()

    update_thresholds_batch(rows, one_source=True)

    # update dashboard alerts
    if n > 0:
        update_dash_checks(nodename)

        _websocket_send(event_msg({
                     'event': 'checks_change',
                     'data': {
                       'chk_nodename': nodename,
                     }
                    }))

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
        try:
            idx = vars.index("mask")
            for i, val in enumerate(vals):
                if vals[i][idx].count(".") == 3:
                    l = vals[i][idx].split(".")
                elif len(vals[i][idx]) == 8:
                    l = (
                     int(vals[i][idx][0:2], base=16),
                     int(vals[i][idx][2:4], base=16),
                     int(vals[i][idx][4:6], base=16),
                     int(vals[i][idx][6:], base=16)
                    )
                else:
                    continue
                s = bin(int(l[0]))[2:]+bin(int(l[1]))[2:]+bin(int(l[2]))[2:]+bin(int(l[3]))[2:]
                vals[i][idx] = str(s.count("1"))
        except ValueError:
            print "value error"
            pass
        except Exception as e:
            print str(e)
        ip_blist = ["224.0.0.1", "ff02::1"]
        _vals = []
        i = vars.index("addr")
        for val in vals:
            if val[i] in ip_blist:
                continue
            _vals.append(val)
        sql = """delete from node_ip where nodename="%s" """%auth[1]
        db.executesql(sql)
        generic_insert('node_ip', vars, _vals)
    if 'uids' in data:
        vars, vals = data['uids']
        if 'updated' not in vars:
            vars.append('updated')
            for i, val in enumerate(vals):
                vals[i].append(now)
        if 'nodename' not in vars:
            vars.append('nodename')
            for i, val in enumerate(vals):
                vals[i].append(auth[1])
        sql = """delete from node_users where nodename="%s" """%auth[1]
        db.executesql(sql)
        generic_insert('node_users', vars, vals)
        node_users_alerts(auth[1])
    if 'gids' in data:
        vars, vals = data['gids']
        if 'updated' not in vars:
            vars.append('updated')
            for i, val in enumerate(vals):
                vals[i].append(now)
        if 'nodename' not in vars:
            vars.append('nodename')
            for i, val in enumerate(vals):
                vals[i].append(auth[1])
        sql = """delete from node_groups where nodename="%s" """%auth[1]
        db.executesql(sql)
        generic_insert('node_groups', vars, vals)
        node_groups_alerts(auth[1])

    db.commit()

def node_users_alerts(nodename):
    sql = """insert into dashboard
             select
                 NULL,
                 "duplicate uid",
                 NULL,
                 "%(nodename)s",
                 if(t.host_mode="PRD", 1, 0),
                 "uid %%(uid)s is used by users %%(usernames)s",
                 concat('{"uid": ', t.user_id, ', "usernames": "', t.usernames, '"}'),
                 now(),
                 NULL,
                 t.host_mode,
                 NULL,
                 now()
               from (
                 select
                   *,
                   (select host_mode from nodes where nodename="%(nodename)s") as host_mode
                 from (
                   select
                     nodename,
                     user_id,
                     group_concat(user_name) as usernames,
                     count(id) as n
                   from node_users
                   where nodename="%(nodename)s"
                   group by nodename, user_id
                 ) u
                 where u.n > 1
               ) t
               on duplicate key update
               dash_updated=now()
               """ % dict(nodename=nodename)
    n = db.executesql(sql)
    db.commit()

    # purge old alerts
    sql = """delete from dashboard where
               dash_nodename="%(nodename)s" and
               dash_type="duplicate uid" and
               dash_updated < date_sub(now(), interval 20 second)
          """ % dict(nodename=nodename)
    n = db.executesql(sql)
    db.commit()

def node_groups_alerts(nodename):
    sql = """insert into dashboard
             select
                 NULL,
                 "duplicate gid",
                 NULL,
                 "%(nodename)s",
                 if(t.host_mode="PRD", 1, 0),
                 "gid %%(gid)s is used by users %%(groupnames)s",
                 concat('{"gid": ', t.group_id, ', "groupnames": "', t.groupnames, '"}'),
                 now(),
                 NULL,
                 t.host_mode,
                 NULL,
                 now()
               from (
                 select
                   *,
                   (select host_mode from nodes where nodename="%(nodename)s") as host_mode
                 from (
                   select
                     nodename,
                     group_id,
                     group_concat(group_name) as groupnames,
                     count(id) as n
                   from node_groups
                   where nodename="%(nodename)s"
                   group by nodename, group_id
                 ) u
                 where u.n > 1
               ) t
               on duplicate key update
               dash_updated=now()
               """ % dict(nodename=nodename)
    n = db.executesql(sql)
    db.commit()

    # purge old alerts
    sql = """delete from dashboard where
               dash_nodename="%(nodename)s" and
               dash_type="duplicate gid" and
               dash_updated < date_sub(now(), interval 20 second)
          """ % dict(nodename=nodename)
    n = db.executesql(sql)
    db.commit()
    dashboard_events()


def get_os_obs_dates(obs_name):
    q = db.obsolescence.obs_type == "os"
    q &= db.obsolescence.obs_name == obs_name
    o = db(q).select(db.obsolescence.obs_warn_date,
                     db.obsolescence.obs_alert_date).first()
    if o is None:
        return None, None
    return o.obs_warn_date, o.obs_alert_date

def get_hw_obs_dates(obs_name):
    q = db.obsolescence.obs_type == "hw"
    q &= db.obsolescence.obs_name == obs_name
    o = db(q).select(db.obsolescence.obs_warn_date,
                     db.obsolescence.obs_alert_date).first()
    if o is None:
        return None, None
    return o.obs_warn_date, o.obs_alert_date

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
    if 'enclosure' in h and h['enclosure'] == 'Unknown':
        del(h['enclosure'])

    # add obsolescence info
    os_obs_warn_date, os_obs_alert_date = get_os_obs_dates(' '.join((h['os_name'], h['os_vendor'], h['os_release'])))
    hw_obs_warn_date, hw_obs_alert_date = get_hw_obs_dates(h['model'])
    h['os_obs_warn_date'] = os_obs_warn_date
    h['os_obs_alert_date'] = os_obs_alert_date
    h['hw_obs_warn_date'] = hw_obs_warn_date
    h['hw_obs_alert_date'] = hw_obs_alert_date

    generic_insert('nodes', h.keys(), h.values())
    _websocket_send(event_msg({
                 'event': 'nodes_change',
                 'data': {'f': 'b'}
                }))
    update_dash_node_not_updated(auth[1])
    update_dash_node_without_maintenance_end(auth[1])
    update_dash_node_without_asset(auth[1])

def _resmon_clean(node, svcname):
    if node is None or node == '':
        return
    if svcname is None or svcname == '':
        return
    q = db.resmon.nodename==node.strip("'")
    q &= db.resmon.svcname==svcname.strip("'")
    q &= db.resmon.updated < datetime.datetime.now() - datetime.timedelta(minutes=10)
    db(q).delete()
    db.commit()

def _resmon_update(vars, vals, auth):
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
        nodename, vmname, vmtype = translate_encap_nodename(h['svcname'], h['nodename'])
        if nodename is not None:
            h['vmname'] = vmname
            h['nodename'] = nodename
        if 'vmname' not in h:
            h['vmname'] = ""
    if len(vals) == 0:
        return
    idx = vars.index("res_status")
    if type(vals[0]) == list:
        for i, v in enumerate(vals):
            if v[idx] == "'None'":
                vals[i][idx] = "n/a"
    elif type(vals) == list:
        vals[idx] = "n/a"
    generic_insert('resmon', vars, vals)
    _resmon_clean(h['nodename'], h['svcname'])

def _register_disk(vars, vals, auth):
    h = {}
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)
    for a,b in zip(vars, vals):
        h[a] = b

    disk_id = h["disk_id"].strip("'")
    disk_svcname = h["disk_svcname"].strip("'")
    disk_nodename = h["disk_nodename"].strip("'")
    disk_model = h['disk_model'].strip("'")

    if len(disk_svcname) == 0:
        # if no service name is provided and the node is actually
        # a service encpasulated vm, add the encapsulating svcname
        q = db.svcmon.mon_vmname == disk_nodename
        row = db(q).select(cacheable=True).first()
        if row is not None:
            h["disk_svcname"] = repr(row.mon_svcname)

    # don't register blacklisted disks (might be VM disks, already accounted)
    #n = db(db.disk_blacklist.disk_id==disk_id).count()
    #if n > 0:
    #    purge_old_disks(h, now)
    #    return

    h['disk_updated'] = now

    # fix naa-16
    if len(disk_id) == 17 and disk_id[0] == '2':
        disk_id = disk_id[1:]
        h['disk_id'] = repr(disk_id)

    # HDS specifics
    if disk_model == "OPEN-V":
        wwid = h['disk_id'].strip("'")
        ldev = wwid[26:28]+":"+wwid[28:30]+":"+wwid[30:]
        ldev = ldev.upper()
        portname_prefix = "50"+wwid[2:12]+"%"
        q = db.diskinfo.disk_devid == ldev
        q &= db.diskinfo.disk_id != wwid
        q &= db.stor_array_tgtid.array_tgtid.like(portname_prefix)
        l1 = db.stor_array.on(db.diskinfo.disk_arrayid == db.stor_array.array_name)
        l2 = db.stor_array_tgtid.on(db.stor_array.id == db.stor_array_tgtid.array_id)
        r = db(q).select(db.diskinfo.disk_id, left=(l1,l2),
                         groupby=db.diskinfo.disk_id).first()
        if r is not None:
            q = db.diskinfo.disk_id == r.disk_id
            db(q).update(disk_id=wwid)

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
                vals = [repr(disk_id), array_id, h['disk_updated']]
                generic_insert('diskinfo', vars, vals)
        else:
            # diskinfo registered by a array parser or an hv pushdisks
            h['disk_local'] = 'F'

    if disk_id.startswith(disk_nodename+'.') and n == 0:
        h['disk_local'] = 'T'
        vars = ['disk_id', 'disk_arrayid', 'disk_devid', 'disk_size',
                'disk_updated']
        vals = [repr(disk_id),
                h['disk_nodename'],
                repr(disk_id.split('.')[-1]),
                h['disk_size'],
                h['disk_updated']]
        generic_insert('diskinfo', vars, vals)
    elif n == 0:
        h['disk_local'] = 'F'
        vars = ['disk_id', 'disk_size', 'disk_updated']
        vals = [repr(disk_id), h['disk_size'], h['disk_updated']]
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

def _insert_pkg(vars, vals, auth):
    now = datetime.datetime.now()
    if "pkg_updated" not in vars:
        vars.append("pkg_updated")
        for i, val in enumerate(vals):
            vals[i].append(str(now))
    threshold = now - datetime.timedelta(minutes=1)
    generic_insert('packages', vars, vals)
    nodename = auth[1].strip("'")
    delete_old_pkg(threshold, nodename)
    table_modified("packages")
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

def _insert_patch(vars, vals, auth):
    now = datetime.datetime.now()
    vars.append("patch_updated")
    for i, val in enumerate(vals):
        vals[i].append(str(now))
    threshold = now - datetime.timedelta(minutes=1)
    generic_insert('patches', vars, vals)
    nodename = auth[1].strip("'")
    table_modified("patches")
    delete_old_patches(threshold, nodename)

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
        if s is None or len(s.sg) == 0:
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
        sql = """delete from stor_array_dg where array_id=%s and dg_updated < date_sub(now(), interval 24 hour) """%array_id
        db.executesql(sql)

        # stor_array_tgtid
        vars = ['array_id', 'array_tgtid']
        vals = []
        for wwn in s.port_list:
            vals.append([array_id, wwn])
        generic_insert('stor_array_tgtid', vars, vals)
        sql = """delete from stor_array_tgtid where array_id=%s and updated < date_sub(now(), interval 24 hour) """%array_id
        db.executesql(sql)

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
    queue_refresh_b_disk_app()

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

            # load all of this array devs seens by the nodes
            # index by ldev
            r = s.ports[0]
            r = "60" + r[2:12] + "%"
            q = db.svcdisks.disk_id.like(r)
            ldev_wwid = {}
            for row in db(q).select(db.svcdisks.disk_id, cacheable=False):
                ldev_wwid[row.disk_id[26:]] = row.disk_id

            # diskinfo
            vars = ['disk_id',
                    'disk_arrayid',
                    'disk_devid',
                    'disk_name',
                    'disk_size',
                    'disk_alloc',
                    'disk_raid',
                    'disk_group',
                    'disk_updated']
            vals = []
            for d in s.vdisk:
                ldev = d['name'].replace(":", "").lower()
                if ldev in ldev_wwid:
                    wwid = ldev_wwid[ldev]
                else:
                    wwid = d['wwid']
                vals.append([wwid,
                             s.name,
                             d['name'],
                             d.get('label', ''),
                             str(d['size']),
                             str(d.get('alloc', '')),
                             d['raid'],
                             d['disk_group'],
                             now])
            generic_insert('diskinfo', vars, vals)
            sql = """delete from diskinfo where disk_arrayid="%s" and disk_updated < "%s" """%(s.name, str(now))
            db.executesql(sql)
    queue_refresh_b_disk_app()

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
    queue_refresh_b_disk_app()

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
            _vals = []
            for nse in p['nse']:
                if nse == p['RemotePortName']:
                    continue
                _vals.append([
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
            if len(_vals) == 0:
                _vals.append([
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
            vals += _vals
        generic_insert('switches', vars, vals)
        sql = """delete from switches where sw_name="%s" and sw_updated < "%s" """%(s.name, str(now))
        db.executesql(sql)

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
    queue_refresh_b_disk_app()

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

    # load svc mnt cache
    sql = """select svcname, nodename, res_desc from resmon where rid like "%fs#%" """
    rows = db.executesql(sql)
    svc_mnt = {}
    for row in rows:
        try:
            mnt = row[2].split('@')[1]
            svc_mnt[(row[1], mnt)] = row[0]
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
            elif (nodename, l[1]) in svc_mnt:
                svcname = svc_mnt[(nodename, l[1])]
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

    q = db.scheduler_task.status.belongs(("QUEUED", "ASSIGNED", "RUNNING"))
    q &= db.scheduler_task.function_name == "async_post_insert_nsr"
    if db(q).count() < 2:
        scheduler.queue_task("async_post_insert_nsr", [], group_name="slow", timeout=1200)
        db.commit()

def async_post_insert_nsr():
    purge_saves()
    update_save_checks()
    update_thresholds_batch_type("save")
    update_dash_checks_all()

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
    queue_refresh_b_disk_app()

def insert_hp3par(name=None, nodename=None):
    import glob
    import os
    from applications.init.modules import hp3par
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    raid_type = ["raid0", "raid1", "raid1", "raid5", "raid6"]
    dir = 'applications'+str(URL(r=request,a='init',c='uploads',f='hp3par'))
    if name is None:
        pattern = "*"
    else:
        pattern = name
    dirs = glob.glob(os.path.join(dir, pattern))

    for d in dirs:
        s = hp3par.get_hp3par(d)
        if s is not None:
            # stor_array
            vars = ['array_name', 'array_model', 'array_cache', 'array_firmware', 'array_updated']
            vals = []
            mem = 0
            for d in s.shownode:
                mem += int(d['Data_Mem'])
                mem += int(d['Control_Mem'])
            vals.append([s.name,
                         s.showsys[0]['Model'],
                         str(mem),
                         s.showversion['Version'],
                         now])
            generic_insert('stor_array', vars, vals)

            sql = """select id from stor_array where array_name="%s" """%s.name
            array_id = str(db.executesql(sql)[0][0])

            # stor_array_dg
            vars = ['array_id', 'dg_name', 'dg_free', 'dg_used', 'dg_size', 'dg_updated']
            vals = []
            for d in s.showcpg:
                vals.append([array_id,
                             d['Name'],
                             "",
                             "",
                             "",
                             now])
            generic_insert('stor_array_dg', vars, vals)
            sql = """delete from stor_array_dg where array_id=%s and dg_updated < "%s" """%(array_id, str(now))
            db.executesql(sql)

            # stor_array_tgtid
            vars = ['array_id', 'array_tgtid']
            vals = []
            for wwn in s.ports:
                vals.append([array_id, wwn.lower()])
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
            for d in s.showvv:
                t = ""
                vals.append([d['VV_WWN'].lower(),
                             s.name,
                             d['Name'],
                             "",
                             d['VSize_MB'],
                             d['Tot_Rsvd_MB'],
                             t,
                             d['UsrCPG'],
                             now])
            generic_insert('diskinfo', vars, vals)
            sql = """delete from diskinfo where disk_arrayid="%s" and disk_updated < "%s" """%(s.name, str(now))
            db.executesql(sql)
    queue_refresh_b_disk_app()

def insert_ibmds(name=None, nodename=None):
    import glob
    import os
    from applications.init.modules import ibmds
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    dir = 'applications'+str(URL(r=request,a='init',c='uploads',f='ibmds'))
    if name is None:
        pattern = "*"
    else:
        pattern = name
    dirs = glob.glob(os.path.join(dir, pattern))

    for d in dirs:
        s = ibmds.get_ibmds(d)
        if s is not None:
            # stor_array
            vars = ['array_name', 'array_model', 'array_cache', 'array_firmware', 'array_updated']
            vals = []
            vals.append([s.si['ID'],
                         s.si['Model'],
                         '0',
                         '',
                         now])
            generic_insert('stor_array', vars, vals)

            sql = """select id from stor_array where array_name="%s" """%s.si['ID']
            array_id = str(db.executesql(sql)[0][0])

            # stor_array_dg
            vars = ['array_id', 'dg_name', 'dg_free', 'dg_used', 'dg_size', 'dg_updated']
            vals = []
            for dg in s.dg:
                usedpct = int(dg['%allocated'])
                vals.append([array_id,
                             dg['Name'],
                             str(dg['availstor']),
                             '1',
                             '1',
                             now])
            generic_insert('stor_array_dg', vars, vals)
            sql = """delete from stor_array_dg where array_id=%s and dg_updated < "%s" """%(array_id, str(now))
            db.executesql(sql)

            # stor_array_tgtid
            vars = ['array_id', 'array_tgtid']
            vals = []
            for ioport in s.ioport:
                vals.append([array_id, ioport['WWPN'].lower()])
            generic_insert('stor_array_tgtid', vars, vals)

            # diskinfo
            vars = ['disk_id',
                    'disk_arrayid',
                    'disk_devid',
                    'disk_name',
                    'disk_size',
                    'disk_raid',
                    'disk_group',
                    'disk_updated']
            vals = []
            for d in s.vdisk:
                vals.append([d['wwid'],
                             s.si['ID'],
                             d['ID'],
                             d['Name'],
                             str(d['cap']),
                             d['Raid'],
                             d['PoolName'],
                             now])
            generic_insert('diskinfo', vars, vals)
            sql = """delete from diskinfo where disk_arrayid="%s" and disk_updated < "%s" """%(s.si['ID'], str(now))
            db.executesql(sql)
            db.commit()
    queue_refresh_b_disk_app()

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
    queue_refresh_b_disk_app()

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
    queue_refresh_b_disk_app()

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
    queue_refresh_b_disk_app()

def _svcmon_update_combo(g_vars, g_vals, r_vars, r_vals, auth):
    _svcmon_update(g_vars, g_vals, auth)
    _resmon_update(r_vars, r_vals, auth)

def _svcmon_update(vars, vals, auth):
    if len(vals) == 0:
        return
    if isinstance(vals[0], list):
        for v in vals:
            _svcmon_update(vars, v, auth)
    else:
        __svcmon_update(vars, vals)

    _websocket_send(event_msg({
                 'event': 'svcmon_change',
                 'data': {
                   'mon_nodname': auth[1],
                 },
                }))
    dashboard_events()

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
              'mon_sharestatus',
              'mon_appstatus',
              'mon_diskstatus']:
        if sn not in h:
            h[sn] = 'n/a'
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

    db(db.services.svc_name==svcname).update(
      svc_status=ostatus,
      svc_availstatus=astatus)
    db.commit()

    update_dash_service_unavailable(svcname, svctype, astatus)
    update_dash_service_available_but_degraded(svcname, svctype, astatus, ostatus)

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
    q = (db.svcmon.mon_vmname == nodename) | (db.svcmon.mon_vmname == nodename.split('.')[0])
    q &= db.svcmon.mon_svcname == svcname
    rows = db(q).select(db.svcmon.mon_nodname,
                        db.svcmon.mon_vmname,
                        db.svcmon.mon_vmtype,
                        db.svcmon.mon_containerstatus)

    if len(rows) == 0:
        # not encap
        return None, None, None

    for row in rows:
        if row.mon_containerstatus in ('up', 'stdby up', 'n/a'):
            return row.mon_nodname, row.mon_vmname, row.mon_vmtype

    row = rows.first()
    return row.mon_nodname, row.mon_vmname, row.mon_vmtype

def __svcmon_update(vars, vals):
    # don't trust the server's time
    h = {}
    for a,b in zip(vars, vals):
        if a == 'mon_updated':
            continue
        h[a] = b

    nodename, vmname, vmtype = translate_encap_nodename(h['mon_svcname'], h['mon_nodname'])

    if 'mon_containerpath' in h and nodename is None:
        # update container info only
        generic_insert('svcmon', vars, vals)
        return

    if 'mon_vmname' not in h:
        # COMPAT: old mono-container agent. fetch vmname from svcmon.
        q = db.svcmon.mon_svcname == h['mon_svcname']
        q &= db.svcmon.mon_nodname == h['mon_nodname']
        q &= db.svcmon.mon_vmname != None
        q &= db.svcmon.mon_vmname != ""
        row = db(q).select(db.svcmon.mon_vmname).first()
        if row is not None:
            h['mon_vmname'] = row.mon_vmname
        q = db.services.svc_name == h['mon_svcname']
        row = db(q).select(db.services.svc_containertype).first()
        if row is not None:
            h['mon_vmtype'] = row.svc_containertype

    if nodename is not None:
        h['mon_vmname'] = vmname
        h['mon_vmtype'] = vmtype
        h['mon_nodname'] = nodename

    if 'mon_vmname' in h and h['mon_vmname'] is not None and len(h['mon_vmname']) > 0:
        q = db.nodes.nodename == h['mon_vmname']
        db(q).update(hv=h['mon_nodname'])

    now = datetime.datetime.now()
    tmo = now - datetime.timedelta(minutes=15)
    h['mon_updated'] = now
    if 'mon_hbstatus' not in h:
        h['mon_hbstatus'] = 'undef'
    if 'mon_sharestatus' not in h:
        h['mon_sharestatus'] = 'undef'
    if 'mon_availstatus' not in h:
        h['mon_availstatus'] = compute_availstatus(h)
    generic_insert('svcmon', h.keys(), h.values())
    svc_status_update(h['mon_svcname'])
    update_dash_service_frozen(h['mon_svcname'], h['mon_nodname'], h['mon_svctype'], h['mon_frozen'])
    update_dash_service_not_on_primary(h['mon_svcname'], h['mon_nodname'], h['mon_svctype'], h['mon_availstatus'])
    update_dash_svcmon_not_updated(h['mon_svcname'], h['mon_nodname'])

    sql = """select svc_cluster_type from services where svc_name="%s" """ % h['mon_svcname']
    rows = db.executesql(sql, as_dict=True)
    if len(rows) > 0 and rows[0]['svc_cluster_type'] == 'flex':
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
                 'mon_sharestatus',
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
                 h['mon_sharestatus'],
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
                 'mon_sharestatus',
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
                 'mon_sharestatus',
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
                 h['mon_sharestatus'],
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
                 'mon_sharestatus',
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
                 h['mon_sharestatus'],
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
    dashboard_events()

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
    dashboard_events()

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
    dashboard_events()

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
    dashboard_events()

def update_dash_service_not_updated(svcname):
    sql = """delete from dashboard
               where
                 dash_svcname = "%(svcname)s" and
                 dash_type = "service configuration not updated"
          """%dict(svcname=svcname)
    rows = db.executesql(sql)
    db.commit()
    dashboard_events()

def update_dash_svcmon_not_updated(svcname, nodename):
    sql = """delete from dashboard
               where
                 dash_svcname = "%(svcname)s" and
                 dash_nodename = "%(nodename)s" and
                 dash_type = "service status not updated"
          """%dict(svcname=svcname, nodename=nodename)
    rows = db.executesql(sql)
    db.commit()
    # dashboard_events() called from __svcmon_update

def update_dash_node_not_updated(nodename):
    sql = """delete from dashboard
               where
                 dash_nodename = "%(nodename)s" and
                 dash_type = "node information not updated"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)
    db.commit()
    dashboard_events()

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
                     pkg_arch,
                     pkg_type
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
    dashboard_events()

def update_dash_flex_cpu(svcname):
    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)

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
                 concat('{"n": ', round(t.cpu),
                        ', "cmin": ', t.svc_flex_cpu_low_threshold,
                        ', "cmax": ', t.svc_flex_cpu_high_threshold,
                        '}'),
                 now(),
                 md5(concat('{"n": ', round(t.cpu),
                        ', "cmin": ', t.svc_flex_cpu_low_threshold,
                        ', "cmax": ', t.svc_flex_cpu_high_threshold,
                        '}')),
                 "%(env)s",
                 "",
                 now()
               from (
                 select *
                 from (
                  select
                   p.svc_flex_cpu_low_threshold AS svc_flex_cpu_low_threshold,
                   p.svc_flex_cpu_high_threshold AS svc_flex_cpu_high_threshold,
                   (
                    select
                     count(1)
                    from svcmon c
                    where
                     c.mon_svcname = "%(svcname)s" and
                     c.mon_availstatus = 'up'
                   ) AS up,
                   (
                    select
                     (100 - c.idle)
                    from stats_cpu c join svcmon m
                    where
                     c.nodename = m.mon_nodname and
                     m.mon_svcname = "%(svcname)s" and
                     c.date > (now() + interval -(15) minute) and
                     c.cpu = 'all' and
                     m.mon_overallstatus = 'up'
                    group by m.mon_svcname
                   ) AS cpu
                  from v_svcmon p
                  where
                   p.mon_svcname="%(svcname)s"
                 ) w
                 where
                   w.up > 0 and
                   (
                     (
                       w.svc_flex_cpu_high_threshold > 0 and
                       w.cpu > w.svc_flex_cpu_high_threshold
                     ) or
                     (
                       w.svc_flex_cpu_low_threshold > 0 and
                       w.cpu < w.svc_flex_cpu_low_threshold
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

    sql = """delete from dashboard
               where
                 dash_svcname = "%(svcname)s" and
                 dash_type = "flex error" and
                 dash_updated < "%(now)s" and
                 dash_fmt like "%%average cpu usage%%"
          """%dict(svcname=svcname, now=str(now))
    rows = db.executesql(sql)
    db.commit()

    dashboard_events()

def update_dash_flex_instances_started(svcname):
    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)
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
                 from (
                  select
                   p.svc_flex_min_nodes AS svc_flex_min_nodes,
                   p.svc_flex_max_nodes AS svc_flex_max_nodes,
                   (
                    select
                     count(1)
                    from svcmon c
                    where
                     c.mon_svcname = "%(svcname)s" and
                     c.mon_availstatus = 'up'
                   ) AS up
                  from v_svcmon p
                  where
                   p.mon_svcname="%(svcname)s"
                 ) w
                 where
                   ((
                     w.svc_flex_min_nodes > 0 and
                     w.up < w.svc_flex_min_nodes
                   ) or
                   (
                     w.svc_flex_max_nodes > 0 and
                     w.up > w.svc_flex_max_nodes
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

    sql = """delete from dashboard
               where
                 dash_svcname = "%(svcname)s" and
                 dash_type = "flex error" and
                 dash_updated < "%(now)s" and
                 dash_fmt like "%%instances started%%"
          """%dict(svcname=svcname, now=str(now))
    rows = db.executesql(sql)
    db.commit()

    dashboard_events()

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
    dashboard_events()

def update_dash_checks(nodename):
    nodename = nodename.strip("'")
    sql = """select host_mode from nodes
             where
               nodename="%(nodename)s"
          """%dict(nodename=nodename)
    rows = db.executesql(sql)

    if len(rows) == 0:
        sev = 2
        host_mode = 'TST'
    elif len(rows) == 1 and rows[0][0] == 'PRD':
        sev = 3
        host_mode = rows[0][0]
    else:
        sev = 2
        host_mode = rows[0][0]

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
                   env=host_mode,
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
    dashboard_events()

def update_dash_netdev_errors(nodename):
    nodename = nodename.strip("'")
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)
    sql = """select dev, sum(rxerrps+txerrps+collps+rxdropps+rxdropps) as errs
               from stats_netdev_err_hour
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
    update_thresholds_batch(checks, one_source=True)

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
        db.executesql(sql)
        db.commit()
        sqlws = """select
                     dash_md5
                   from
                     dashboard
                   where
                     dash_type="action errors" and
                     dash_svcname="%(svcname)s" and
                     dash_nodename="%(nodename)s" and
                     dash_fmt="%%(err)s action errors"
              """%dict(svcname=svc_name,
                       nodename=nodename,
                  )
        rows = db.executesql(sqlws)
        if len(rows) > 0:
            _websocket_send(event_msg({
              'event': 'dash_change',
              'data': {
                'dash_md5': rows[0][0],
              }
            }))

    else:
        sqlws = """select dash_md5 from dashboard
                 where
                   dash_type="action errors" and
                   dash_svcname="%(svcname)s" and
                   dash_nodename="%(nodename)s"
              """%dict(svcname=svc_name,
                       nodename=nodename)
        rows = db.executesql(sqlws)
        if len(rows) > 0:
            _websocket_send(event_msg({
              'event': 'dash_delete',
              'data': {
                'dash_md5': rows[0][0],
              }
            }))
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
                   dash_dict='{"s": "%(status)s"}',
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
    # dashboard_events() called from __svcmon_update

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

        sql = """insert into dashboard
                 set
                   dash_type="service unavailable",
                   dash_svcname="%(svcname)s",
                   dash_nodename="",
                   dash_severity=%(sev)d,
                   dash_fmt="current availability status: %%(s)s",
                   dash_dict='{"s": "%(status)s", "svcname": "%(svcname)s"}',
                   dash_created=now(),
                   dash_updated=now(),
                   dash_env="%(env)s"
                 on duplicate key update
                   dash_severity=%(sev)d,
                   dash_fmt="current availability status: %%(s)s",
                   dash_dict='{"s": "%(status)s", "svcname": "%(svcname)s"}',
                   dash_updated=now(),
                   dash_env="%(env)s"
              """%dict(svcname=svc_name,
                       sev=sev,
                       env=svc_type,
                       status=svc_availstatus)
        db.executesql(sql)
        db.commit()
    # dashboard_events() called from __svcmon_update

def update_dash_service_frozen(svc_name, nodename, svc_type, frozen):
    if svc_type == 'PRD':
        sev = 2
    else:
        sev = 1
    if frozen == "0":
        sql = """delete from dashboard
                 where
                   dash_type="service frozen" and
                   dash_nodename="%(nodename)s" and
                   dash_svcname="%(svcname)s"
              """%dict(svcname=svc_name, nodename=nodename)
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
    # dashboard_events() called from __svcmon_update

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
                   dash_nodename="%(nodename)s" and
                   dash_svcname="%(svcname)s"
              """%dict(svcname=svc_name, nodename=nodename)
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
    # dashboard_events() called from __svcmon_update

def task_dash_daily():
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
    dashboard_events()

def task_dash_hourly():
    cron_dash_checks_not_updated()
    cron_dash_service_not_updated()
    cron_dash_app_without_responsible()
    cron_dash_node_not_updated()
    cron_dash_node_without_asset()
    cron_dash_action_errors_cleanup()
    dashboard_events()

def task_dash_min():
    # ~1/min
    cron_dash_svcmon_not_updated()
    dashboard_events()



from gluon.scheduler import Scheduler
scheduler = Scheduler(db, migrate=False)
