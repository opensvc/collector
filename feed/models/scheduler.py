# coding: utf8

import datetime
import hashlib
import os
import copy
import logging

log = logging.getLogger("web2py.app.feed")

def send_sysreport_delete(deleted, sysreport_d, node_id):
    if len(deleted) == 0:
        return False
    node_d = os.path.join(sysreport_d, node_id)
    for fpath in deleted:
        if fpath.startswith("/"):
            fpath = "file" + fpath
        fpath = os.path.join(node_d, fpath)
        print fpath
        os.unlink(fpath)
    return True

def send_sysreport_archive(fname, binary, sysreport_d, node_id):
    if fname == "":
        return False

    import codecs
    import stat

    fpath = os.path.join(sysreport_d, fname)

    if not fpath.endswith('.tar'):
        # don't know how to treat that sysreport format: don't care to save it
        return False

    try:
        f = codecs.open(fpath, "wb")
        f.write(binary.data)
        f.close()
    except Exception as e:
        print e
        return False

    if fpath.endswith('.tar'):
        import tarfile
        try:
            tar = tarfile.open(fpath, 'r')
        except Exception as e:
            print e
            os.unlink(fpath)
            return False
        for member in tar.getmembers():
            """
            {
             'uid': 0,
             'chksum': 7426,
             'uname': 'root',
             'gname': 'root',
             'size': 14178,
             'devmajor': 0,
             'name': 'foo/file/proc/cpuinfo',
             'devminor': 0,
             'gid': 0,
             'mtime': 1421159135,
             'mode': 292,
             'linkname': '',
             'type': '0'
            }
            """
            member.name = node_id+member.name[member.name.index("/"):]
            mi = member.get_info("utf-8", "ignore")
            mp = os.path.join(sysreport_d, mi['name'])
            if os.path.exists(mp):
                st = os.stat(mp)
                os.chmod(mp, st.st_mode | stat.S_IWRITE)
            tar.extract(member, path=sysreport_d)
            if os.path.exists(mp):
                st = os.stat(mp)
                os.chmod(mp, st.st_mode | stat.S_IREAD)
        tar.close()
        os.unlink(fpath)
    else:
        return False

    return True

def git_commit(git_d):
    if which('git') is None:
        print "git not found"
        return

    node_d = os.path.join(git_d, "..")

    if not os.path.exists(git_d):
        from applications.init.modules import config
        print "init sysreport git project"
        if hasattr(config, "email_from"):
            email = config.email_from
        else:
            email = "nobody@localhost.localdomain"
        os.system("git --git-dir=%s init" % git_d)
        os.system("git --git-dir=%s config user.email %s" % (git_d, email))
        os.system("git --git-dir=%s config user.name collector" % git_d)

    if not os.path.exists(node_d):
        print "dir does not exist:", node_d
        return 0

    os.system('cd %s && (rm -f .git/index.lock && git add . ; git commit -m"" -a)' % node_d)

    return 0

def task_send_sysreport(need_commit, deleted, node_id):
    sysreport_d = os.path.join(os.path.dirname(__file__), "..", "..", "init", 'uploads', 'sysreport')
    git_d = os.path.join(sysreport_d, node_id, ".git")

    if not need_commit:
        print "commit not needed"
        return
    git_commit(git_d)

    return 0

def _begin_action(vars, vals, auth):
    node_id = auth_to_node_id(auth)
    vars, vals = replace_nodename_in_data(vars, vals, auth, fieldname="hostname")
    vars, vals = replace_svcname_in_data(vars, vals, auth, fieldname="svcname")
    i = generic_insert("svcactions", vars, vals, node_id=node_id, get_last_id=True)
    row = db(db.svcactions.id==i).select().first()
    ws_send('begin_action', {
      'svc_id': row.svc_id,
      'node_id': row.node_id,
      'action': row.action,
      'begin': row.begin.strftime("%Y-%m-%d %H:%M:%S"),
      'id': row.id,
    })
    if row.cron == 0:
        _log("service.action",
             "initialized service action %(a)s",
             dict(a=row.action),
             svc_id=row.svc_id,
             node_id=node_id)
    return 0

def _action_wrapper(a, vars, vals, auth):
    if a == "_end_action":
        _end_action(vars, vals, auth)
    elif a == "_begin_action":
        _begin_action(vars, vals, auth)

def _end_action(vars, vals, auth):
    upd = []
    h = {}
    for a, b in zip(vars, vals):
        h[a] = str(b).strip("'")

    vars, vals = replace_nodename_in_data(vars, vals, auth)
    node_id = auth_to_node_id(auth)
    svc_id = node_svc_id(node_id, h["svcname"])
    vars, vals = replace_svcname_in_data(vars, vals, auth)

    node = db(db.nodes.node_id==node_id).select().first()
    if node:
        tz = node.tz
        # convert to local time and strip microseconds
        h['begin'] = 'convert_tz("%s", "%s", @@time_zone)' % (str(h['begin'].split('.')[0]), tz)
        h['end'] = 'convert_tz("%s", "%s", @@time_zone)' % (str(h['end']), tz)
    else:
        # strip microseconds
        h['begin'] = repr(str(h['begin'].split('.')[0]))
        h['end'] = repr(str(h['end'].split('.')[0]))

    for a, b in h.items():
        if a not in ['hostname', 'node_id', 'svc_id', 'svcname', 'begin', 'action', 'hostid']:
            if b.startswith("'") or b.startswith("convert"):
                upd.append('%s=%s' % (a, b))
            else:
                upd.append('%s="%s"' % (a, b))

    sql = """select id from svcactions where node_id="%s" and svc_id="%s" and begin=%s and action="%s" """ %\
          (node_id, svc_id, h['begin'], h['action'])
    ids = map(lambda x: x[0], db.executesql(sql))
    if len(ids) == 0:
        return

    sql="""update svcactions set %s where id in (%s)""" %\
        (','.join(upd), ','.join(map(str, ids)))
    db.executesql(sql)
    db.commit()

    sql = """select * from svcactions where id in (%s)""" %\
          ','.join(map(str, ids))
    h = db.executesql(sql, as_dict=True)[0]
    h['begin'] = h['begin'].strftime("%Y-%m-%d %H:%M:%S")
    h['end'] = h['end'].strftime("%Y-%m-%d %H:%M:%S")

    ws_send('end_action', h)

    if h['action'] in ('start', 'startcontainer') and \
       h['status'] == 'ok':
        update_virtual_asset(node_id, svc_id)
    if h['status'] == 'err':
        update_action_errors(svc_id, node_id)
        update_dash_action_errors(svc_id, node_id)
        _log("service.action",
             "action '%(a)s' error",
             dict(a=h['action']),
             svc_id=svc_id,
             node_id=node_id,
             level="error")
    return 0

def update_action_errors(svc_id, node_id):
    sql = """select count(id) from svcactions a
             where
               a.svc_id = "%(svc_id)s" and
               a.node_id = "%(node_id)s" and
               a.status = "err" and
               ((a.ack <> 1) or isnull(a.ack)) and
               a.begin > date_sub(now(), interval 2 day)
    """%dict(svc_id=svc_id, node_id=node_id)
    err = db.executesql(sql)[0][0]

    if err == 0:
         sql = """delete from b_action_errors
                  where
                    svc_id = "%(svc_id)s" and
                    node_id = "%(node_id)s"
         """%dict(svc_id=svc_id, node_id=node_id)
    else:
        sql = """insert into b_action_errors
                 set
                   svc_id="%(svc_id)s",
                   node_id="%(node_id)s",
                   err=%(err)d
                 on duplicate key update
                   err=%(err)d
              """%dict(svc_id=svc_id, node_id=node_id, err=err)
    db.executesql(sql)
    db.commit()

def update_virtual_asset(node_id, svc_id):
    q = db.svcmon.svc_id == svc_id
    q &= db.svcmon.node_id == node_id
    q &= db.svcmon.svc_id == db.services.svc_id
    svc = db(q).select(db.svcmon.mon_vmname, db.services.svc_app).first()
    if svc is None:
        return
    q = db.nodes.node_id == node_id
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
    sql += "where nodename='%s'"%svc.svcmon.mon_vmname
    sql += " and app in ('%(app1)s', '%(app2)s')" % dict(app1=svc.services.svc_app, app2=node.app)
    db.executesql(sql)

def _update_service(vars, vals, auth):
    if 'updated' not in vars:
        vars += ['updated']
        vals += [datetime.datetime.now()]
    node_id = auth_to_node_id(auth)
    h = {}
    for a,b in zip(vars, vals):
        h[a] = b
    if "svc_name" in h:
        # agent compat
        h["svcname"] = h["svc_name"]
        del(h["svc_name"])
    if "svc_envfile" in h:
        # agent compat
        h["svc_config"] = h["svc_envfile"]
        del(h["svc_envfile"])
    if "svc_cluster_type" in h:
        # agent compat
        h["svc_topology"] = h["svc_cluster_type"]
        del(h["svc_cluster_type"])
    svcname = h["svcname"].strip("'")
    svc_id = node_svc_id(node_id, svcname)
    h["svc_id"] = svc_id
    if 'svc_app' in h:
        if h['svc_app'] is None or h['svc_app'].strip("'") == "" or not common_responsible(node_id=node_id, app=h['svc_app'].strip("'")):
            q = db.nodes.node_id == node_id
            new_app = db(q).select().first().app
            _log("service.change",
                 "advertized app %(app)s remapped to %(new_app)s",
                 dict(
                   app=h['svc_app'].strip("'"),
                   new_app=new_app,
                 ),
                 svc_id=svc_id,
                 node_id=node_id,
                 level="warning")
            h['svc_app'] = new_app
    if 'svc_type' in h:
        h['svc_env'] = h['svc_type']
        del(h['svc_type'])
    if 'svc_version' in h:
        del(h['svc_version'])
    if 'svc_drnoaction' in h:
        if h['svc_drnoaction'] == 'False': h['svc_drnoaction'] = 'F'
        elif h['svc_drnoaction'] == 'True': h['svc_drnoaction'] = 'T'
    for var in ('svc_vmname', 'svc_guestos', 'svc_vcpus', 'svc_vmem', 'svc_containerpath'):
       if var in h:
            del(h[var])
    generic_insert('services', h.keys(), h.values())
    db.commit()
    ws_send('services_change', {'svc_id': svc_id})

    update_dash_service_not_updated(svc_id)
    _node_id, vmname, vmtype = translate_encap_nodename(svc_id, node_id)
    if _node_id is not None and node_id != _node_id:
        return
    h = {}
    for a,b in zip(vars, vals):
        h[a] = b

    # redirect old agent container info to svcmon
    if 'svc_vmname' in h:
        vars = ['svc_id',
                'node_id',
                'mon_vmname',
                'mon_guestos',
                'mon_vcpus',
                'mon_vmem',
                'mon_containerpath']
        vals = [svc_id,
                _node_id,
                h['svc_vmname'],
                h['svc_guestos'] if 'svc_guestos' in h else '',
                h['svc_vcpus'] if 'svc_vcpus' in h else '0',
                h['svc_vmem'] if 'svc_vmem' in h else '0',
                h['svc_containerpath'] if 'svc_containerpath' in h else '',
               ]
        generic_insert('svcmon', vars, vals)

def _push_checks(vars, vals, auth):
    """
        chk_svcname
        chk_type
        chk_instance
        chk_value
        chk_updated
    """

    n = len(vals)
    node_id = auth_to_node_id(auth)
    vars, vals = replace_nodename_in_data(vars, vals, auth, fieldname="chk_nodename")
    vars, vals = replace_svcnames_in_data(vars, vals, auth, fieldname="chk_svcname")

    # purge old checks
    if n > 0:
        where = ""
        for v in vals:
             where += """ and not (chk_type="%(chk_type)s" and chk_instance="%(chk_instance)s") """%dict(chk_type=v[2], chk_instance=v[3])
        sql = """delete from checks_live
                 where
                   node_id="%(node_id)s" and
                   chk_type not in ("netdev_err", "save")
                   %(where)s
              """%dict(node_id=node_id, where=where)
        db.executesql(sql)
        db.commit()

        # for checks coming from vservice, update the svcname field
        svc_id_idx = vars.index("svc_id")
        svc_id = vals[0][svc_id_idx]
        if svc_id == "":
            q = db.svcmon.mon_vmname == auth[1]
            row = db(q).select(db.svcmon.svc_id, limitby=(0,1)).first()
            if row is not None:
                svc_id = row.svc_id
                for i, val in enumerate(vals):
                    vals[i][svc_id_idx] = svc_id
    else:
        return

    # insert new checks
    while len(vals) > 100:
        generic_insert('checks_live', vars, vals[:100])
        vals = vals[100:]
    generic_insert('checks_live', vars, vals)
    db.commit()

    q = db.checks_live.node_id == node_id
    q &= db.checks_live.chk_type != "netdev_err"
    q &= db.checks_live.chk_type != "save"
    rows = db(q).select()

    update_thresholds_batch(rows, one_source=True)

    # update dashboard alerts
    if n > 0:
        update_dash_checks(node_id)
        ws_send('checks_change', {'node_id': node_id})

def _insert_generic(data, auth):
    now = datetime.datetime.now()
    node = auth_to_node(auth)
    node_id = node.node_id
    if type(data) != dict:
        return
    if 'hba' in data:
        vars, vals = data['hba']
        if 'updated' not in vars:
            vars.append('updated')
            for i, val in enumerate(vals):
                vals[i].append(now)
        sql = """delete from node_hba where node_id="%s" """%node_id
        db.executesql(sql)
        vars, vals = replace_nodename_in_data(vars, vals, auth)
        generic_insert('node_hba', vars, vals)
        ws_send('node_hba_change')
    if 'targets' in data:
        vars, vals = data['targets']
        if 'updated' not in vars:
            vars.append('updated')
            for i, val in enumerate(vals):
                vals[i].append(now)
                print vals[i]
                if vals[i][0] == auth[1]:
                    # virt => add to vswitch
                    _vars = [
                      "sw_name",
                      "sw_slot",
                      "sw_port",
                      "sw_rportname",
                      "sw_updated"
                    ]
                    _vals = [[
                      "virtual",
                      "0",
                      "0",
                      auth[1],
                      str(datetime.datetime.now())
                    ]]
                    _vars, _vals = replace_nodename_in_data(_vars, _vals, auth)
                    generic_insert('switches', _vars, _vals)
        if 'nodename' not in vars and 'node_id' not in vars:
            vars.append('node_id')
            for i, val in enumerate(vals):
                vals[i].append(node_id)
        sql = """delete from stor_zone where node_id="%s" """%node_id
        db.executesql(sql)
        generic_insert('stor_zone', vars, vals)
        ws_send('stor_zone_change',{'node_id': node_id})
    if 'lan' in data:
        vars, vals = data['lan']
        if 'updated' not in vars:
            vars.append('updated')
            for i, val in enumerate(vals):
                vals[i].append(now)
        vars, vals = replace_nodename_in_data(vars, vals, auth)

        # ip addr returns 802.11q intf names with a @<base intf> suffix. remove it.
        idx_intf = vars.index("intf")
        for i, val in enumerate(vals):
            vals[i][idx_intf] = vals[i][idx_intf].split("@")[0]

        try:
            idx = vars.index("mask")
            for i, val in enumerate(vals):
                vals[i][idx] = vals[i][idx].lstrip("0x")
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
        sql = """delete from node_ip where node_id="%s" """%node_id
        db.executesql(sql)
        generic_insert('node_ip', vars, _vals)
        ws_send('node_ip_change', {'node_id': node_id})
        create_node_dns_records(node, vars, vals)
    if 'uids' in data:
        vars, vals = data['uids']
        if 'updated' not in vars:
            vars.append('updated')
            for i, val in enumerate(vals):
                vals[i].append(now)
        vars, vals = replace_nodename_in_data(vars, vals, auth)
        sql = """delete from node_users where node_id="%s" """%node_id
        db.executesql(sql)
        generic_insert('node_users', vars, vals)
        node_users_alerts(node_id)
        ws_send('node_users_change', {'node_id': node_id})
    if 'gids' in data:
        vars, vals = data['gids']
        if 'updated' not in vars:
            vars.append('updated')
            for i, val in enumerate(vals):
                vals[i].append(now)
        vars, vals = replace_nodename_in_data(vars, vals, auth)
        sql = """delete from node_groups where node_id="%s" """%node_id
        db.executesql(sql)
        generic_insert('node_groups', vars, vals)
        ws_send('node_groups_change', {'node_id': node_id})
        node_groups_alerts(node_id)

    db.commit()

def node_users_alerts(node_id):
    sql = """insert into dashboard
             select
                 NULL,
                 "duplicate uid",
                 NULL,
                 if(t.node_env="PRD", 1, 0),
                 "uid %%(uid)s is used by users %%(usernames)s",
                 concat('{"uid": ', t.user_id, ', "usernames": "', t.usernames, '"}'),
                 now(),
                 NULL,
                 t.node_env,
                 now(),
                 "%(node_id)s",
                 NULL
               from (
                 select
                   *,
                   (select node_env from nodes where node_id="%(node_id)s") as node_env
                 from (
                   select
                     node_id,
                     user_id,
                     group_concat(user_name) as usernames,
                     count(id) as n
                   from node_users
                   where node_id="%(node_id)s"
                   group by node_id, user_id
                 ) u
                 where u.n > 1
               ) t
               on duplicate key update
               dash_updated=now()
               """ % dict(node_id=node_id)
    n = db.executesql(sql)
    db.commit()

    # purge old alerts
    sql = """delete from dashboard where
               node_id="%(node_id)s" and
               dash_type="duplicate uid" and
               dash_updated < date_sub(now(), interval 20 second)
          """ % dict(node_id=node_id)
    n = db.executesql(sql)
    db.commit()

def node_groups_alerts(node_id):
    sql = """insert into dashboard
             select
                 NULL,
                 "duplicate gid",
                 NULL,
                 if(t.node_env="PRD", 1, 0),
                 "gid %%(gid)s is used by users %%(groupnames)s",
                 concat('{"gid": ', t.group_id, ', "groupnames": "', t.groupnames, '"}'),
                 now(),
                 NULL,
                 t.node_env,
                 now(),
                 "%(node_id)s",
                 NULL
               from (
                 select
                   *,
                   (select node_env from nodes where node_id="%(node_id)s") as node_env
                 from (
                   select
                     node_id,
                     group_id,
                     group_concat(group_name) as groupnames,
                     count(id) as n
                   from node_groups
                   where node_id="%(node_id)s"
                   group by node_id, group_id
                 ) u
                 where u.n > 1
               ) t
               on duplicate key update
               dash_updated=now()
               """ % dict(node_id=node_id)
    n = db.executesql(sql)
    db.commit()

    # purge old alerts
    sql = """delete from dashboard where
               node_id="%(node_id)s" and
               dash_type="duplicate gid" and
               dash_updated < date_sub(now(), interval 20 second)
          """ % dict(node_id=node_id)
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
    node_id = auth_to_node_id(auth)
    vars.append("node_id")
    vals.append(node_id)
    h = {}
    for a,b in zip(vars, vals):
        h[a] = b
    now = datetime.datetime.now()
    h['updated'] = now
    if 'host_mode' in h:
        # compat
        h['node_env'] = h['host_mode']
        del(h['host_mode'])
    if 'environnement' in h:
        # compat
        if 'asset_env' not in h:
            h['asset_env'] = h['environnement']
        del(h['environnement'])
    if 'environment' in h:
        # compat
        if 'asset_env' not in h:
            h['asset_env'] = h['environment']
        del(h['environment'])
    if 'enclosure' in h and h['enclosure'] == 'Unknown':
        del(h['enclosure'])
    if 'team_responsible' in h:
        # security model
        del(h['team_responsible'])
    if 'project' in h:
        # security model
        del(h['project'])

    # add obsolescence info
    os_obs_warn_date, os_obs_alert_date = get_os_obs_dates(' '.join((h['os_name'], h['os_vendor'], h['os_release'])))
    hw_obs_warn_date, hw_obs_alert_date = get_hw_obs_dates(h['model'])
    h['os_obs_warn_date'] = os_obs_warn_date
    h['os_obs_alert_date'] = os_obs_alert_date
    h['hw_obs_warn_date'] = hw_obs_warn_date
    h['hw_obs_alert_date'] = hw_obs_alert_date

    generic_insert('nodes', h.keys(), h.values())
    ws_send('nodes_change')
    node_dashboard_updates(node_id)

def _resmon_clean(node_id, svc_id, threshold=None):
    try:
        threshold = datetime.datetime.strptime(threshold.strip("'").split(".")[0], "%Y-%m-%d %H:%M:%S")
    except:
        threshold = datetime.datetime.now()
    if node_id is None or node_id == '':
        return
    if svc_id is None or svc_id == '':
        return
    q = db.resmon.node_id==node_id
    q &= db.resmon.svc_id==svc_id
    q &= db.resmon.updated < threshold - datetime.timedelta(minutes=20)
    db(q).delete()
    db.commit()

def _resmon_update(vars, vals, auth, cache=None):
    if len(vals) == 0:
        return cache
    if cache is None:
        head = True
        cache = {
          "node_id": auth_to_node_id(auth),
          "svc_id": set([]),
          "translate": {},
          "vals": [],
        }
    else:
        head = False
    if type(vals[0]) in (str, unicode):
        cache = __resmon_update(vars, vals, auth, cache=cache)
    else:
        for v in vals:
            cache = _resmon_update(vars, v, auth, cache=cache)
    if head:
        for svc_id in cache["svc_id"]:
            _resmon_clean(cache['node_id'], svc_id)
        if "vars" in cache:
            print "insert resmon"
            generic_insert('resmon', cache["vars"], cache["vals"])
        if "resmon_log_changed" in cache and "resmon_log" in cache["resmon_log_changed"]:
            db.commit()
            table_modified("resmon_log")
        ws_send('resmon_change')
    return cache

def __resmon_update(vars, vals, auth, cache=cache):
    node_id = cache["node_id"]
    _now = datetime.datetime.now()
    h = {}
    if len(vals) == 0:
        return cache
    vars, vals = replace_svcname_in_data(copy.copy(vars), vals, auth)
    for a,b in zip(vars, vals):
        h[a] = b
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)
    if 'svc_id' not in h:
        return cache

    cache["svc_id"].add(h["svc_id"])

    if (h['svc_id'], node_id) in cache["translate"]:
        _node_id, vmname, vmtype = cache["translate"][(h['svc_id'], node_id)]
    else:
        _node_id, vmname, vmtype = translate_encap_nodename(h['svc_id'], node_id)
        cache["translate"][(h['svc_id'], node_id)] = _node_id, vmname, vmtype

    if _node_id is not None:
        h['vmname'] = vmname
        h['node_id'] = _node_id
    else:
        h['node_id'] = node_id
    if 'vmname' not in h:
        h['vmname'] = ""
    if 'nodename' in h:
        del(h['nodename'])

    h['updated'] = now
    if h['res_status'] == "'None'":
        h['res_status'] = "n/a"

    if "vars" not in cache:
        cache["vars"] = h.keys()
    cache["vals"].append(h.values())
    cache["resmon_log_changed"] = resmon_log_update(h['node_id'], h['svc_id'], h['rid'], h['res_status'], deferred=True)
    print datetime.datetime.now() - _now, "__resmon_update", h['rid']
    return cache

def _register_disk(vars, vals, auth):
    h = {}
    node_id = auth_to_node_id(auth)

    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)
    for a,b in zip(vars, vals):
        h[a] = b

    disk_id = h["disk_id"].strip("'")
    disk_svcname = h["disk_svcname"].strip("'")
    disk_model = h['disk_model'].strip("'")
    q = db.nodes.node_id == node_id
    disk_nodename = db(q).select().first().nodename

    svc_id = node_svc_id(node_id, disk_svcname)
    h["svc_id"] = svc_id
    del(h["disk_svcname"])

    if disk_id.startswith(disk_nodename+"."):
        disk_id = disk_id.replace(disk_nodename+".", node_id+".")
        h["disk_id"] = disk_id

    if len(svc_id) == 0:
        # if no service name is provided and the node is actually
        # a service encpasulated vm, add the encapsulating svcname
        q = db.svcmon.mon_vmname == db.nodes.nodename
        q &= db.nodes.node_id == node_id
        row = db(q).select(db.svcmon.svc_id, cacheable=True).first()
        if row is not None:
            h["svc_id"] = repr(row.svc_id)

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
        if disk.disk_arrayid == node_id or \
           disk.disk_arrayid is None or \
           disk.disk_arrayid == "NULL" or \
           len(disk.disk_arrayid) == 0:
            # diskinfo registered as a stub for a local disk
            h['disk_local'] = 'T'

            if n == 1:
                # update diskinfo timestamp
                vars = ['disk_id', 'disk_arrayid', 'disk_updated']
                vals = [repr(disk_id), node_id, h['disk_updated']]
                generic_insert('diskinfo', vars, vals)
        else:
            # diskinfo registered by a array parser or an hv pushdisks
            h['disk_local'] = 'F'

    if disk_id.startswith(node_id+'.') and n == 0:
        h['disk_local'] = 'T'
        vars = ['disk_id', 'disk_arrayid', 'disk_devid', 'disk_size',
                'disk_updated']
        vals = [repr(disk_id),
                repr(node_id),
                repr(disk_id.replace(node_id+'.', '')),
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
              """%(node_id, disk_id)
        db.executesql(sql)
        db.commit()

    vars, vals = replace_nodename_in_data(h.keys(), h.values(), auth, fieldname="disk_nodename")
    vars, vals = add_app_id_in_data(vars, vals)
    generic_insert('svcdisks', vars, vals)

def _insert_pkg(vars, vals, auth):
    now = datetime.datetime.now()
    if "pkg_updated" not in vars:
        vars.append("pkg_updated")
        for i, val in enumerate(vals):
            vals[i].append(str(now))
    vars, vals = replace_nodename_in_data(vars, vals, auth, fieldname="pkg_nodename")
    node_id = auth_to_node_id(auth)
    threshold = now - datetime.timedelta(minutes=1)
    generic_insert('packages', vars, vals)
    delete_old_pkg(threshold, node_id)
    update_dash_pkgdiff(node_id)

def delete_old_pkg(threshold, node_id):
    q = db.packages.node_id == node_id
    q &= db.packages.pkg_updated < threshold
    db.commit()
    db(q).delete()
    db.commit()

def delete_old_patches(threshold, node_id):
    q = db.patches.node_id == node_id
    q &= db.patches.patch_updated < threshold
    db.commit()
    db(q).delete()
    db.commit()

def _insert_patch(vars, vals, auth):
    now = datetime.datetime.now()
    vars.append("patch_updated")
    for i, val in enumerate(vals):
        vals[i].append(str(now))

    vars, vals = replace_nodename_in_data(vars, vals, auth, fieldname="patch_nodename")
    node_id = auth_to_node_id(auth)
    threshold = now - datetime.timedelta(minutes=1)
    generic_insert('patches', vars, vals)
    delete_old_patches(threshold, node_id)

def purge_array_dg(vals):
    if len(vals) == 0:
        return
    array_id = vals[0][0]
    dg_names = ['"'+str(val[1])+'"' for val in vals]
    sql = """delete from stor_array_dg where
             array_id=%s and dg_name not in (%s)
          """ % (str(array_id), ','.join(dg_names))
    db.executesql(sql)
    db.commit()

def purge_array_tgtid(vals):
    if len(vals) == 0:
        return
    array_id = vals[0][0]
    tgt_ids = ['"'+str(val[1])+'"' for val in vals]
    sql = """delete from stor_array_tgtid where
             array_id=%s and array_tgtid not in (%s)
          """ % (str(array_id), ','.join(tgt_ids))
    db.executesql(sql)
    db.commit()

def insert_array_proxy(node_id, array_name):
    if node_id is None:
        return
    print " insert %s as proxy node"%node_id
    sql = """select id from stor_array where array_name="%s" """%array_name
    rows = db.executesql(sql)
    if len(rows) == 0:
        return
    array_id = str(rows[0][0])

    vars = ['array_id', 'node_id']
    vals = [array_id, node_id]
    generic_insert('stor_array_proxy', vars, vals)

def insert_gcedisks(name=None, node_id=None):
    import glob
    import os
    from applications.init.modules import gcedisks
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    dir = 'applications'+str(URL(r=request,a='init',c='uploads',f='gcedisks'))
    if name is None:
        pattern = "*"
    else:
        pattern = name
    dirs = glob.glob(os.path.join(dir, pattern))

    for d in dirs:
        print d
        s = gcedisks.get_gcedisks(d)
        if s is None :
            print "error parsing data"
            continue

        # stor_array_proxy
        insert_array_proxy(node_id, s.name)

        # stor_array
        vars = ['array_name', 'array_model', 'array_cache', 'array_firmware', 'array_updated']
        vals = []
        name = s.name
        vals.append([s.name,
                     "",
                     "0",
                     "",
                     now])
        generic_insert('stor_array', vars, vals)

        sql = """select id from stor_array where array_name="%s" """ % s.name
        array_id = str(db.executesql(sql)[0][0])

        # stor_array_tgtid
        vars = ['array_id', 'array_tgtid']
        vals = []
        sw_vars = ["sw_name", "sw_slot", "sw_port", "sw_rportname", "sw_updated"]
        sw_vals = []
        for wwn in s.wwpn:
            vals.append([array_id, wwn])
            sw_vals.append(["virtual", "0", "0", wwn, str(datetime.datetime.now())])
        generic_insert('stor_array_tgtid', vars, vals)
        purge_array_tgtid(vals)
        generic_insert('switches', sw_vars, sw_vals)

        # stor_array_dg
        vars = ['array_id', 'dg_name', 'dg_free', 'dg_used', 'dg_size', 'dg_updated']
        vals = []
        for dgname, dg in s.dg.items():
            avail = int(dg['limit'] - dg['usage'])
            used = int(dg['usage'])
            total = int(dg['limit'])
            vals.append([array_id,
                         dgname,
                         str(avail),
                         str(used),
                         str(total),
                         now])
        generic_insert('stor_array_dg', vars, vals)
        purge_array_dg(vals)

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
        for d in s.disks:
            vals.append([d['disk_id'],
                         name,
                         d['disk_name'],
                         str(d['disk_devid']),
                         str(d['disk_size']),
                         str(d['disk_alloc']),
                         d['disk_raid'],
                         d['disk_group'],
                         now])
        generic_insert('diskinfo', vars, vals)
        sql = """delete from diskinfo where disk_arrayid="%s" and (disk_updated < "%s" or disk_updated is NULL)"""%(name, str(now))
        db.executesql(sql)
        db.commit()

def insert_freenas(name=None, node_id=None):
    import glob
    import os
    from applications.init.modules import freenas
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    dir = 'applications'+str(URL(r=request,a='init',c='uploads',f='freenas'))
    if name is None:
        pattern = "*"
    else:
        pattern = name
    dirs = glob.glob(os.path.join(dir, pattern))

    for d in dirs:
        print d
        s = freenas.get_freenas(d)
        if s is None :
            print "error parsing data"
            continue

        # stor_array_proxy
        insert_array_proxy(node_id, s.name)

        # stor_array
        vars = ['array_name', 'array_model', 'array_cache', 'array_firmware', 'array_updated']
        vals = []
        name = s.name
        vals.append([s.name,
                     s.version['name'],
                     "0",
                     s.version['fullversion'],
                     now])
        generic_insert('stor_array', vars, vals)

        sql = """select id from stor_array where array_name="%s" """ % s.name
        array_id = str(db.executesql(sql)[0][0])

        # stor_array_dg
        vars = ['array_id', 'dg_name', 'dg_free', 'dg_used', 'dg_size', 'dg_updated']
        vals = []
        for dg in s.volumes:
            avail = int(dg['avail']) // 1024 // 1024
            used = int(dg['used']) // 1024 // 1024
            vals.append([array_id,
                         dg['name'],
                         str(avail),
                         str(used),
                         str(avail+used),
                         now])
        generic_insert('stor_array_dg', vars, vals)
        purge_array_dg(vals)

        # stor_array_tgtid
        vars = ['array_id', 'array_tgtid']
        vals = []
        for target in s.iscsi_targets:
            vals.append([array_id, target['iscsi_target_name']])
        generic_insert('stor_array_tgtid', vars, vals)
        purge_array_tgtid(vals)

        # load cache
        devices = {}
        for v in s.volumes:
            for ds in v['children']:
                for d in ds['children']:
                    if d['type'] == "zvol":
                        path = "/dev/zvol/"+d['path']
                        devices[path] = d

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
        for d in s.iscsi_extents:
            if d['iscsi_target_extent_path'] not in devices:
                continue
            device = devices[d['iscsi_target_extent_path']]
            size = int(device['used'])
            alloc = size * device['used_pct'] // 100
            disk_group = d['iscsi_target_extent_path']
            disk_group = disk_group.replace("/dev/zvol/", "")
            disk_group = disk_group.replace("/mnt/", "")
            disk_group = disk_group[:disk_group.index("/")]
            vals.append([d['iscsi_target_extent_naa'][2:],
                         name,
                         d['iscsi_target_extent_name'],
                         str(d['id']),
                         str(size // 1024 // 1024),
                         str(alloc // 1024 // 1024),
                         d['iscsi_target_extent_type'],
                         disk_group,
                         now])
        generic_insert('diskinfo', vars, vals)
        sql = """delete from diskinfo where disk_arrayid="%s" and (disk_updated < "%s" or disk_updated is NULL)"""%(name, str(now))
        db.executesql(sql)
        db.commit()

def insert_xtremio(name=None, node_id=None):
    import glob
    import os
    from applications.init.modules import xtremio
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    dir = 'applications'+str(URL(r=request,a='init',c='uploads',f='xtremio'))
    if name is None:
        pattern = "*"
    else:
        pattern = name
    dirs = glob.glob(os.path.join(dir, pattern))

    for d in dirs:
        print d
        s = xtremio.get_xtremio(d)
        if s is None :
            print "error parsing data"
            continue

        name = s.clusters[0]["name"]
        version = s.clusters[0]["sys-sw-version"]
        total = int(s.clusters[0]["ud-ssd-space"])/1024
        used = int(s.clusters[0]["ud-ssd-space-in-use"])/1024

        # stor_array_proxy
        insert_array_proxy(node_id, name)

        # stor_array
        vars = ['array_name', 'array_model', 'array_cache', 'array_firmware', 'array_updated']
        vals = []
        vals.append([name,
                     "XtremIO",
                     "0",
                     version,
                     now])
        generic_insert('stor_array', vars, vals)

        sql = """select id from stor_array where array_name="%s" """ % s.name
        array_id = str(db.executesql(sql)[0][0])

        # stor_array_dg
        vars = ['array_id', 'dg_name', 'dg_free', 'dg_used', 'dg_size', 'dg_updated']
        vals = []
        vals.append([array_id,
                     "default",
                     str(total-used),
                     str(used),
                     str(total),
                     now])
        generic_insert('stor_array_dg', vars, vals)
        purge_array_dg(vals)

        # stor_array_tgtid
        vars = ['array_id', 'array_tgtid']
        vals = []
        for target in s.targets:
            port_type = target["port-type"]
            if port_type == "iscsi":
                tgt_id = target["port-address"]
            if port_type == "fc":
                tgt_id = target["port-address"].replace(":", "").lower()
            else:
                continue
            vals.append([array_id, tgt_id])
        generic_insert('stor_array_tgtid', vars, vals)
        purge_array_tgtid(vals)

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
        for d in s.volumes:
            if d["created-from-volume"] == "":
                d_type = "volume"
            else:
                d_type = "snapshot"
            vals.append([
                d["naa-name"],
                name,
                d["name"],
                d["index"],
                int(d["vol-size"]) // 1024,
                int(d["logical-space-in-use"]) // 1024,
                d_type,
                "default",
                now
        ])
        generic_insert('diskinfo', vars, vals)
        sql = """delete from diskinfo where disk_arrayid="%s" and (disk_updated < "%s" or disk_updated is NULL)"""%(name, str(now))
        db.executesql(sql)
        db.commit()

def insert_dcs(name=None, node_id=None):
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
        insert_array_proxy(node_id, s.sg['caption'])

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
        purge_array_dg(vals)

        # stor_array_tgtid
        vars = ['array_id', 'array_tgtid']
        vals = []
        for wwn in s.port_list:
            vals.append([array_id, wwn])
        generic_insert('stor_array_tgtid', vars, vals)
        purge_array_tgtid(vals)

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
        sql = """delete from diskinfo where disk_arrayid="%s" and (disk_updated < "%s" or disk_updated is NULL)"""%(name, str(now))
        db.executesql(sql)
        db.commit()

def insert_hds(name=None, node_id=None):
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

        if s is None:
            continue

        # stor_array_proxy
        insert_array_proxy(node_id, s.name)

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
        purge_array_dg(vals)

        # stor_array_tgtid
        vars = ['array_id', 'array_tgtid', 'updated']
        vals = []
        for wwn in s.ports:
            vals.append([array_id, wwn, now])
        generic_insert('stor_array_tgtid', vars, vals)
        purge_array_tgtid(vals)

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
        sql = """delete from diskinfo where disk_arrayid="%s" and (disk_updated < "%s" or disk_updated is NULL)"""%(s.name, str(now))
        db.executesql(sql)
        db.commit()

def insert_centera(name=None, node_id=None):
    import glob
    import os
    from applications.init.modules import centera
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    dir = 'applications'+str(URL(r=request,a='init',c='uploads',f='centera'))
    if name is None:
        pattern = "*"
    else:
        pattern = name
    dirs = glob.glob(os.path.join(dir, pattern))

    node_id = {}
    for row in db(db.nodes.id>0).select(db.nodes.node_id, db.nodes.nodename):
        node_id[row.nodename] = row.node_id

    for d in dirs:
        print d
        s = centera.get_centera(d)

        # stor_array_proxy
        insert_array_proxy(node_id, s.name)

        if s is not None:
            # stor_array
            print s.name, "insert array info"
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
            print s.name, "insert dg info"
            vars = ['array_id', 'dg_name', 'dg_free', 'dg_used', 'dg_size', 'dg_updated']
            vals = []
            for dg in s.pool:
                if dg['name'] == "cluster":
                    continue
                vals.append([array_id,
                             dg['name'],
                             str(dg['free']),
                             str(dg['used']),
                             str(dg['size']),
                             now])
            generic_insert('stor_array_dg', vars, vals)
            purge_array_dg(vals)

            # diskinfo
            print s.name, "insert disk info"
            vars = ['disk_id',
                    'disk_arrayid',
                    'disk_devid',
                    'disk_size',
                    'disk_alloc',
                    'disk_raid',
                    'disk_group',
                    'disk_updated']
            vals = []
            for d in s.pool:
                if d['name'] == "cluster":
                    continue
                vals.append(['.'.join((s.name, d['name'])),
                             s.name,
                             d['id'],
                             str(d['size']),
                             str(d['used']),
                             "",
                             d['name'],
                             now])
            generic_insert('diskinfo', vars, vals)
            sql = """delete from diskinfo where disk_arrayid="%s" and (disk_updated < "%s" or disk_updated is NULL)"""%(s.name, str(now))
            db.executesql(sql)

            # svcdisks
            print s.name, "insert svcdisk info"
            vars = ['disk_id',
                    'disk_svcname',
                    'node_id',
                    'disk_size',
                    'disk_vendor',
                    'disk_model',
                    'disk_dg',
                    'disk_updated',
                    'disk_local',
                    'disk_used',
                    'disk_region']
            vals = []
            for d in s.pool:
                for h in set(d["hostnames"]) & node_id.keys():
                    vals.append(['.'.join((s.name, d['name'])),
                                 "",
                                 node_id[h],
                                 str(d['size']),
                                 "EMC",
                                 "Centera",
                                 s.name,
                                 now,
                                 'F',
                                 str(d['size']),
                                 "0"])
            generic_insert('svcdisks', vars, vals)
            sql = """delete from svcdisks where disk_model="Centera" and disk_dg="%s" and disk_updated < "%s" """%(s.name, str(now))
            db.executesql(sql)
            db.commit()

def insert_emcvnx(name=None, node_id=None):
    import glob
    import os
    from applications.init.modules import emcvnx
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    dir = 'applications'+str(URL(r=request,a='init',c='uploads',f='emcvnx'))
    if name is None:
        pattern = "*"
    else:
        pattern = name
    dirs = glob.glob(os.path.join(dir, pattern))

    for d in dirs:
        print d
        s = emcvnx.get_vnx(d)

        # stor_array_proxy
        insert_array_proxy(node_id, s.name)

        if s is not None:
            # stor_array
            print s.name, "insert array info"
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
            print s.name, "insert dg info"
            vars = ['array_id', 'dg_name', 'dg_free', 'dg_used', 'dg_size', 'dg_updated']
            vals = []
            for dg in s.pool.values():
                vals.append([array_id,
                             dg['name'],
                             str(dg['free']),
                             str(dg['used']),
                             str(dg['size']),
                             now])
            generic_insert('stor_array_dg', vars, vals)
            purge_array_dg(vals)

            # stor_array_tgtid
            print s.name, "insert port info"
            vars = ['array_id', 'array_tgtid']
            vals = []
            for wwn in s.ports:
                vals.append([array_id, wwn])
            generic_insert('stor_array_tgtid', vars, vals)
            purge_array_tgtid(vals)

            # diskinfo
            print s.name, "insert disk info"
            vars = ['disk_id',
                    'disk_arrayid',
                    'disk_devid',
                    'disk_size',
                    'disk_alloc',
                    'disk_raid',
                    'disk_group',
                    'disk_updated']
            vals = []
            for d in s.vdisk:
                vals.append([d['wwid'],
                             s.name,
                             d['name'],
                             str(d['size']),
                             str(d['alloc']),
                             d['raid'],
                             d['disk_group'],
                             now])
            generic_insert('diskinfo', vars, vals)
            sql = """delete from diskinfo where disk_arrayid="%s" and (disk_updated < "%s" or disk_updated is NULL)"""%(s.name, str(now))
            db.executesql(sql)
            db.commit()

def insert_necism(name=None, node_id=None):
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

        # stor_array_proxy
        insert_array_proxy(node_id, s.name)

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
            purge_array_dg(vals)

            # stor_array_tgtid
            vars = ['array_id', 'array_tgtid']
            vals = []
            for wwn in s.ports:
                vals.append([array_id, wwn])
            generic_insert('stor_array_tgtid', vars, vals)
            purge_array_tgtid(vals)

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
            sql = """delete from diskinfo where disk_arrayid="%s" and (disk_updated < "%s" or disk_updated is NULL)"""%(s.name, str(now))
            db.executesql(sql)
            db.commit()

def insert_brocade(name=None, node_id=None):
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
        db.commit()

def insert_vioserver(name=None, node_id=None):
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
        sql = """delete from diskinfo where disk_arrayid="%s" and (disk_updated < "%s" or disk_updated is NULL)"""%(s.array_name, str(now))
        db.executesql(sql)

        # svcdisks
        vars = ['disk_id',
                'disk_size',
                'disk_used',
                'disk_vendor',
                'disk_model',
                'node_id']
        vals = []
        node_id = get_array_node_id(s.array_name)
        for d in s.pdisk.values():
            vals.append([d['wwid'],
                         d['size'],
                         d['size'],
                         d['vendor'],
                         d['model'],
                         node_id])
        generic_insert('svcdisks', vars, vals)
        sql = """delete from svcdisks where disk_nodename="%s" and disk_updated < "%s" """%(s.array_name, str(now))
        db.executesql(sql)
        db.commit()

def get_array_node_id(array_name, array_type=None):
    q = db.nodes.nodename == name
    node = db(q).select(db.nodes.node_id)
    if node:
        return node.node_id
    node_id = get_new_node_id()
    db.nodes.insert(nodename=array_name, type="storage", node_id=node_id)
    return node_id

def insert_nsr(name=None, node_id=None):
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
    sql = "select node_id, addr from node_ip"
    rows = db.executesql(sql)
    node_ip = {}
    for row in rows:
        node_ip[row[1]] = row[0]

    # load svc ip cache
    sql = """select svc_id, res_desc from resmon where rid like "%ip#%" """
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
    sql = """select svc_id, node_id, res_desc from resmon where rid like "%fs#%" """
    rows = db.executesql(sql)
    svc_mnt = {}
    for row in rows:
        try:
            mnt = row[2].split('@')[1]
            svc_mnt[(row[1], mnt)] = row[0]
        except:
            continue

    # load app cache
    sql = """select svc_id, svc_app from services"""
    rows = db.executesql(sql)
    svc_app = {}
    for row in rows:
        svc_app[row[0]] = row[1]

    sql = """select node_id, app from nodes"""
    rows = db.executesql(sql)
    node_app = {}
    for row in rows:
        node_app[row[0]] = row[1]

    for d in dirs:
        server = os.path.basename(d)
        fpath = os.path.join(d, "mminfo")

        vars = ['save_server', 'node_id', 'svc_id', 'save_name',
                'save_group', 'save_size', 'save_date', 'save_retention',
                'save_volume', 'save_level', 'save_id', 'save_app']
        vals = []

        with open(fpath, 'r') as f:
            lines = f.read().split('\n')

        i = 0
	# 0  10.198.234.6;
	# 1  /fsmntpt;
	# 2  DAY_savegroup;
	# 3  129138964;
	# 4  05/29/15 00:41:49;
	# 5  06/19/15 23:59:59;
	# 6  DDCLONEMAR.001;
	# 7  incr;
	# 8  2e0d2628-00000006-796799ac-556799ac-b298000b-5de57314
        for line in lines:
            l = line.split(';')
            if len(l) != 9:
                continue
            if l[6].endswith('.RO'):
                # nsr read-lonly device. don't import as it would
                # account twice the size.
                continue
            if l[0] in node_ip:
                node_id = node_ip[l[0]]
            else:
                node_id = l[0]
            if l[0] in svc_ip:
                svc_id = svc_ip[l[0]]
            elif (node_id, l[1]) in svc_mnt:
                svc_id = svc_mnt[(node_id, l[1])]
            else:
                svc_id = ''
            if svc_id != '' and svc_id in svc_app:
                app = svc_app[svc_id]
            elif node_id in node_app:
                app = node_app[node_id]
            else:
                app = ''
	    try:
	        l[4] = datetime.datetime.strptime(l[4], "%m/%d/%y %H:%M:%S")
	    except:
	        pass
	    try:
	        l[5] = datetime.datetime.strptime(l[5], "%m/%d/%y %H:%M:%S")
	    except:
	        pass
            vals.append([server, node_id, svc_id]+l[1:]+[app])
            i += 1
            if i > 300:
                i = 0
                generic_insert('saves', vars, vals)
                generic_insert('saves_last', vars, vals)
                vals = []
        generic_insert('saves', vars, vals)
        generic_insert('saves_last', vars, vals)
        db.commit()

    q = db.scheduler_task.status.belongs(("QUEUED", "ASSIGNED", "RUNNING"))
    q &= db.scheduler_task.function_name == "async_post_insert_nsr"
    if db(q).count() < 2:
        scheduler.queue_task("async_post_insert_nsr", [], group_name="slow", timeout=1200)
        db.commit()

def async_post_insert_nsr():
    print "starting purge_saves", datetime.datetime.now()
    purge_saves()
    print "starting update_save_checks", datetime.datetime.now()
    update_save_checks()
    print "starting update_thresholds_batch_type", datetime.datetime.now()
    update_thresholds_batch_type("save")
    print "starting update_dash_checks_all", datetime.datetime.now()
    update_dash_checks_all()
    print "end", datetime.datetime.now()

def purge_saves():
    sql = """delete from saves where
             save_retention < now()"""
    db.executesql(sql)
    sql = """delete from saves_last where
             save_retention < now()"""
    db.executesql(sql)
    db.commit()

def update_save_checks():
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)

    # fs known to have fs_u checks but not in saves index
    print "== not saved", datetime.datetime.now()
    sql = """
           insert into checks_live (node_id, svc_id, chk_type, chk_updated, chk_value, chk_created, chk_instance)
             select
               t.node_id as node_id,
               t.svc_id as svc_id,
               "save",
               now(),
               1000000 as chk_value,
               now(),
               t.chk_instance as chk_instance
             from  (
               select * from checks_live where
                 chk_type="fs_u" and
                 chk_instance not like "/run/%" and
                 chk_instance like "/%" and
                 chk_instance not like "%docker%aufs%" and
                 chk_instance not in ("/run", "/dev/shm", "/tmp", "/var/lib/xenstored", "/var/adm/crash", "/var/adm/ras/livedump")
               ) t
               left join saves_last on
                 t.node_id = saves_last.node_id and
                 (t.svc_id = saves_last.svc_id or saves_last.svc_id = "" or t.svc_id = "") and
                 t.chk_instance = saves_last.save_name
             where
               saves_last.save_name is null
           on duplicate key update
             chk_updated=now(),
             chk_value=1000000
          """
    db.executesql(sql)
    db.commit()

    print "== saved", datetime.datetime.now()
    sql = """
           insert into checks_live (node_id, svc_id, chk_type, chk_updated, chk_value, chk_created, chk_instance)
             select
               saves_last.node_id as node_id,
               saves_last.svc_id as svc_id,
               "save",
               now(),
               datediff(now(), saves_last.save_date) as chk_value,
               now(),
               saves_last.chk_instance
             from
               saves_last
             where
               saves_last.save_resolved=1 and
               saves_last.chk_instance not like "/run/%" and
               saves_last.chk_instance like "/%" and
               saves_last.chk_instance not like "%docker%aufs%" and
               saves_last.chk_instance not in ("/run", "/dev/shm", "/tmp", "/var/lib/xenstored", "/var/adm/crash", "/var/adm/ras/livedump")
           on duplicate key update
             chk_updated=now(),
             chk_value=datediff(now(), saves_last.save_date)
          """
    db.executesql(sql)
    db.commit()

    print "== purge checks_live", datetime.datetime.now()
    sql = """delete from checks_live
             where
               chk_type="save" and
               chk_updated < "%(now)s"
          """%dict(now=now)
    db.executesql(sql)
    db.commit()

    # remove checks from shared fs saved from passive cluster nodes
    # those fs should have a more recent save on the active node
    now2 = datetime.datetime.now()
    now2 -= datetime.timedelta(microseconds=now.microsecond)

    print "== update clustered save checks", datetime.datetime.now()
    sql = """update checks_live inner join (
               select t.* from (
                 select
                   count(id) as n,
                   svc_id,
                   chk_instance,
                   min(chk_value) as chk_value
                 from checks_live
                 where
                   chk_type="save"
                 group by svc_id, chk_instance
               ) t
               join services s on
                 t.svc_id = s.svc_id and
                 s.svc_topology="failover"
               where t.n>1
             ) u on
               checks_live.svc_id=u.svc_id and
               checks_live.chk_instance=u.chk_instance and
               checks_live.chk_value=u.chk_value and
               checks_live.chk_type="save"
             set checks_live.chk_updated=now()
    """
    db.executesql(sql)
    db.commit()

    print "== purge non updated clustered save checks", datetime.datetime.now()
    sql = """delete from checks_live
             where
               chk_type="save" and
               chk_updated < "%(now)s" and
               concat(svc_id, chk_instance) in (
                 select concat(t.svc_id, t.chk_instance) from (
                 select
                   svc_id,
                   chk_instance
                 from checks_live
                 where
                   chk_type="save"
                 group by svc_id, chk_instance
                 having count(id)>1
               ) t
               join services s on
                 t.svc_id = s.svc_id and
                 s.svc_topology="failover"
             )
          """%dict(now=now2)

    db.executesql(sql)
    db.commit()

def insert_netapp(name=None, node_id=None):
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

        # stor_array_proxy
        insert_array_proxy(node_id, s.array_name)

        if s is not None:
            # stor_array
            vars = ['array_name', 'array_model', 'array_cache', 'array_firmware', 'array_updated']
            vals = []
            vals.append([s.array_name,
                         s.model,
                         str(s.cache),
                         s.firmwareversion,
                         now])
            generic_insert('stor_array', vars, vals)

            sql = """select id from stor_array where array_name="%s" """%s.array_name
            array_id = str(db.executesql(sql)[0][0])

            # stor_array_dg
            vars = ['array_id', 'dg_name', 'dg_free', 'dg_used', 'dg_size', 'dg_updated']
            vals = []
            for dg in s.dgs:
                vals.append([array_id,
                             dg['name'],
                             str(dg['free']),
                             str(dg['used']),
                             str(dg['size']),
                             now])
            generic_insert('stor_array_dg', vars, vals)
            purge_array_dg(vals)

            # stor_array_tgtid
            vars = ['array_id', 'array_tgtid']
            vals = []
            for wwn in s.ports:
                vals.append([array_id, wwn])
            generic_insert('stor_array_tgtid', vars, vals)
            purge_array_tgtid(vals)

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
            for d in s.luns:
                vals.append([d['wwid'],
                             s.array_name,
                             d["id"],
                             d.get('name', ''),
                             str(d['size']),
                             str(d['alloc']),
                             "",
                             d['aggr'],
                             now])
            generic_insert('diskinfo', vars, vals)
            sql = """delete from diskinfo where disk_arrayid="%s" and (disk_updated < "%s" or disk_updated is NULL)"""%(s.array_name, str(now))
            db.executesql(sql)
            db.commit()

def insert_hp3par(name=None, node_id=None):
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

        # stor_array_proxy
        insert_array_proxy(node_id, s.name)

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
            purge_array_dg(vals)

            # stor_array_tgtid
            vars = ['array_id', 'array_tgtid']
            vals = []
            for wwn in s.ports:
                vals.append([array_id, wwn.lower()])
            generic_insert('stor_array_tgtid', vars, vals)
            purge_array_tgtid(vals)

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
            sql = """delete from diskinfo where disk_arrayid="%s" and (disk_updated < "%s" or disk_updated is NULL)"""%(s.name, str(now))
            db.executesql(sql)
            db.commit()

def insert_ibmds(name=None, node_id=None):
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

        # stor_array_proxy
        insert_array_proxy(node_id, s.si['ID'])

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
            purge_array_dg(vals)

            # stor_array_tgtid
            vars = ['array_id', 'array_tgtid']
            vals = []
            for ioport in s.ioport:
                vals.append([array_id, ioport['WWPN'].lower()])
            generic_insert('stor_array_tgtid', vars, vals)
            purge_array_tgtid(vals)

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
            sql = """delete from diskinfo where disk_arrayid="%s" and (disk_updated < "%s" or disk_updated is NULL)"""%(s.si['ID'], str(now))
            db.executesql(sql)
            db.commit()

def insert_ibmsvc(name=None, node_id=None):
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

        # stor_array_proxy
        insert_array_proxy(node_id, s.array_name)

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
            purge_array_dg(vals)

            # stor_array_tgtid
            vars = ['array_id', 'array_tgtid']
            vals = []
            for wwn in s.ports:
                vals.append([array_id, wwn])
            generic_insert('stor_array_tgtid', vars, vals)
            purge_array_tgtid(vals)

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
            sql = """delete from diskinfo where disk_arrayid="%s" and (disk_updated < "%s" or disk_updated is NULL)"""%(s.array_name, str(now))
            db.executesql(sql)
            db.commit()

def insert_eva(name=None, node_id=None):
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

        # stor_array_proxy
        insert_array_proxy(node_id, s.name)

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
            purge_array_dg(vals)

            # stor_array_tgtid
            vars = ['array_id', 'array_tgtid']
            vals = []
            for wwn in s.ports:
                vals.append([array_id, wwn])
            generic_insert('stor_array_tgtid', vars, vals)
            purge_array_tgtid(vals)

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
            sql = """delete from diskinfo where disk_arrayid="%s" and (disk_updated < "%s" or disk_updated is NULL)"""%(s.name, str(now))
            db.executesql(sql)
            db.commit()

def insert_sym(symid=None, node_id=None):
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
	s.init_data()

        if s is None:
            continue

        if "model" not in s.info:
            continue

        # stor_array_proxy
        print s.info['symid']
        print " model", s.info['model']
        insert_array_proxy(node_id, s.info['symid'])

        if "version" not in s.info:
            continue

        # stor_array
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
        vars = ['array_id', 'dg_name', 'dg_free', 'dg_used', 'dg_size', 'dg_updated']
        vals = []
        print " dg"
        for dg in s.diskgroup.values():
            print "  ", dg.info['disk_group_name']
            vals.append([array_id,
                         dg.info['disk_group_name'],
                         str(dg.total-dg.used),
                         str(dg.used),
                         str(dg.total),
                         now])
        for pool in s.pool.values():
            print "  ", pool.info['pool_name']
            if "total_used_tracks_mb" not in pool.totals:
                continue
            vals.append([array_id,
                         pool.info['pool_name'],
                         str(pool.totals["total_free_tracks_mb"]),
                         str(pool.totals["total_used_tracks_mb"]),
                         str(pool.totals["total_tracks_mb"]),
                         now])

        for srp in s.srp.values():
            print "  ", srp.info['name']
            if "allocated_capacity_gigabytes" not in srp.info:
                continue
            vals.append([array_id,
                         srp.info['name'],
                         str(float(srp.info["free_capacity_gigabytes"])*1024),
                         str(float(srp.info["allocated_capacity_gigabytes"])*1024),
                         str(float(srp.info["usable_capacity_gigabytes"])*1024),
                         now])

        generic_insert('stor_array_dg', vars, vals)
        purge_array_dg(vals)
        del(s.diskgroup)

        # stor_array_tgtid
        vars = ['array_id', 'array_tgtid']
        vals = []
        print " targets"
        for dir in s.director.values():
            for wwn in dir.port_wwn:
                if wwn == "N/A":
                    continue
                print "  ", wwn
                vals.append([array_id, wwn])
        generic_insert('stor_array_tgtid', vars, vals)
        purge_array_tgtid(vals)
        del(s.director)

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
        for dev in s.dev.values():
            if dev.flags['meta'] not in ('Head', 'None'):
                continue
            vals.append([dev.wwn,
                         s.info['symid'],
                         dev.ident_name,
                         dev.info['dev_name'],
                         str(dev.megabytes),
                         str(dev.alloc),
                         "Meta-%d %s"%(dev.meta_count, dev.info['configuration']),
                         dev.diskgroup_name,
                         now])
        generic_insert('diskinfo', vars, vals)
        del(s.dev)
        sql = """delete from diskinfo where disk_arrayid="%s" and (disk_updated < "%s" or disk_updated is NULL)"""%(s.info['symid'], str(now))
        db.executesql(sql)
        db.commit()

        del(s)

def _svcmon_update_combo(g_vars, g_vals, r_vars, r_vals, auth):
    _svcmon_update(g_vars, g_vals, auth)
    _resmon_update(r_vars, r_vals, auth)

def unfold_svcmon_update(vars, vals, auth):
    if len(vals) == 0:
        return
    if isinstance(vals[0], list):
        for v in vals:
            unfold_svcmon_update(vars, v, auth)
    else:
        __svcmon_update(vars, vals, auth)

def _svcmon_update(vars, vals, auth):
    unfold_svcmon_update(vars, vals, auth)
    ws_send('svcmon_change')
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

def translate_encap_nodename(svc_id, node_id):
    q = db.svcmon.mon_vmname == db.nodes.nodename
    q &= db.nodes.node_id == node_id
    q &= db.svcmon.svc_id == svc_id
    rows = db(q).select(db.svcmon.node_id,
                        db.svcmon.mon_vmname,
                        db.svcmon.mon_vmtype,
                        db.svcmon.mon_containerstatus)

    if len(rows) == 0:
        # not encap
        return None, None, None

    for row in rows:
        if row.mon_containerstatus in ('up', 'stdby up', 'n/a'):
            return row.node_id, row.mon_vmname, row.mon_vmtype

    row = rows.first()
    return row.node_id, row.mon_vmname, row.mon_vmtype

def __svcmon_update(vars, vals, auth):
    _now = datetime.datetime.now()

    # fix agent formatted dataset bug
    if len(vars) == len(vals) - 1:
        del(vals[-1])

    node_id = auth_to_node_id(auth)
    vars, vals = replace_svcname_in_data(copy.copy(vars), vals, auth, fieldname="mon_svcname")
    vars, vals = replace_nodename_in_data(vars, vals, auth, fieldname="mon_nodname")

    print datetime.datetime.now() - _now, "mangle"
    _now = datetime.datetime.now()

    h = {}
    for a,b in zip(vars, vals):
        h[a] = b
    print datetime.datetime.now() - _now, "gen hashed data"
    _now = datetime.datetime.now()

    if h["node_id"] is None:
        return

    # set the collector update timestamp
    now = datetime.datetime.now()
    h['mon_updated'] = now

    if 'mon_nodtype' in h:
        del(h['mon_nodtype'])
    if 'mon_prinodes' in h:
        del(h['mon_prinodes'])
    if 'mon_containerpath' in h and "mon_frozen" not in h:
        # update container info only
        generic_insert('svcmon', h.keys(), h.values())
        return
    print datetime.datetime.now() - _now, "update container info only"
    _now = datetime.datetime.now()

    if 'mon_vmname' not in h:
        # COMPAT: old mono-container agent. fetch vmname from svcmon.
        q = db.svcmon.svc_id == h['svc_id']
        q &= db.svcmon.node_id == node_id
        q &= db.svcmon.mon_vmname != None
        q &= db.svcmon.mon_vmname != ""
        row = db(q).select(db.svcmon.mon_vmname).first()
        if row is not None:
            h['mon_vmname'] = row.mon_vmname
    print datetime.datetime.now() - _now, "COMPAT: old mono-container agent. fetch vmname from svcmon."
    _now = datetime.datetime.now()

    # mangle datasets received from the encap node
    _node_id, vmname, vmtype = translate_encap_nodename(h['svc_id'], node_id)
    if _node_id is not None and _node_id != "" and node_id != _node_id:
        h['mon_vmname'] = vmname
        h['mon_vmtype'] = vmtype
        h['node_id'] = _node_id
    print datetime.datetime.now() - _now, "mangle datasets received from the encap node"
    _now = datetime.datetime.now()

    if h["node_id"] is None:
        return

    # set the hv field of container nodes
    if 'mon_vmname' in h and h['mon_vmname'] is not None and len(h['mon_vmname']) > 0 and h['mon_containerstatus'] == "up":
        node = get_node(node_id)
        q = db.nodes.nodename == h['mon_vmname']
        q &= db.nodes.app == node.app
        if db(q).count() == 0:
            svc = get_svc(h["svc_id"])
            q = db.nodes.nodename == h['mon_vmname']
            q &= db.nodes.app == svc.svc_app
        if db(q).count() == 0:
            q = db.nodes.nodename == h['mon_vmname']
            q &= db.nodes.app.belongs(node_responsibles_apps(node_id))
        db(q).update(
            hv=node.nodename,
            loc_city=node.loc_city,
            loc_country=node.loc_country,
            loc_zip=node.loc_zip,
            loc_floor=node.loc_floor,
            loc_rack=node.loc_rack,
            loc_room=node.loc_room,
            loc_building=node.loc_building,
            loc_addr=node.loc_addr,
            enclosure=node.enclosure,
            enclosureslot=node.enclosureslot,
        )
    print datetime.datetime.now() - _now, "set the hv field of container nodes"
    _now = datetime.datetime.now()

    # compat with old agent
    if 'mon_hbstatus' not in h:
        h['mon_hbstatus'] = 'undef'
    if 'mon_sharestatus' not in h:
        h['mon_sharestatus'] = 'undef'
    if 'mon_availstatus' not in h:
        h['mon_availstatus'] = compute_availstatus(h)

    generic_insert('svcmon', h.keys(), h.values())
    print datetime.datetime.now() - _now, "insert"
    _now = datetime.datetime.now()

    # dashboard janitoring
    svc_status_update(h['svc_id'])

    print datetime.datetime.now() - _now, "svc_status_update"
    _now = datetime.datetime.now()
    if "mon_svctype" in h:
        svc_env = h['mon_svctype']
    else:
        svc_env = db(db.services.svc_id==h['svc_id']).select(db.services.svc_env).first().svc_env
    print datetime.datetime.now() - _now, "get svc_env"
    _now = datetime.datetime.now()

    update_dash_service_frozen(h['svc_id'], node_id, svc_env, h['mon_frozen'])
    print datetime.datetime.now() - _now, "update_dash_service_frozen"
    _now = datetime.datetime.now()
    update_dash_service_not_on_primary(h['svc_id'], node_id, svc_env, h['mon_availstatus'])
    print datetime.datetime.now() - _now, "update_dash_service_not_on_primary"
    _now = datetime.datetime.now()
    update_dash_svcmon_not_updated(h['svc_id'], node_id)
    print datetime.datetime.now() - _now, "update_dash_svcmon_not_updated"
    _now = datetime.datetime.now()

    sql = """select svc_topology from services where svc_id="%s" """ % h['svc_id']
    rows = db.executesql(sql, as_dict=True)
    if len(rows) > 0 and rows[0]['svc_topology'] == 'flex':
        update_dash_flex_instances_started(h['svc_id'])
        update_dash_flex_cpu(h['svc_id'])
    else:
        sql = """delete from dashboard where
                 svc_id="%(svc_id)s" and dash_type="flex error"
              """ % dict(svc_id=h['svc_id'])
        db.executesql(sql)
        db.commit()
    print datetime.datetime.now() - _now, "flex janitoring"
    _now = datetime.datetime.now()

    # service instance status history janitoring
    tmo = now - datetime.timedelta(minutes=15)

    sql = """select * from svcmon_log_last where
               svc_id="%(svc_id)s" and
               node_id="%(node_id)s"
          """ % dict(svc_id=h["svc_id"], node_id=node_id)
    rows = db.executesql(sql, as_dict=True)
    print datetime.datetime.now() - _now, "get last"
    _now = datetime.datetime.now()
    if len(rows) == 0:
        last = None
    else:
        last = rows[0]

    if last is None:
        _vars = ['mon_begin',
                 'mon_end',
                 'svc_id',
                 'node_id',
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
                 h['svc_id'],
                 h['node_id'],
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
        generic_insert('svcmon_log_last', _vars, _vals)
        if h['mon_overallstatus'] == 'warn':
            level = "warning"
        else:
            level = "info"
        _log("service.status",
             "service state initialized: avail(%(a1)s=>%(a2)s) overall(%(o1)s=>%(o2)s)",
             dict(
               a1="none",
               a2=h['mon_availstatus'],
               o1="none",
               o2=h['mon_overallstatus']),
             svc_id=h['svc_id'],
             node_id=node_id,
             level=level)
    elif last["mon_end"] < tmo:
        _vars = ['mon_begin',
                 'mon_end',
                 'svc_id',
                 'node_id',
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
        _vals = [last["mon_end"],
                 h['mon_updated'],
                 h['svc_id'],
                 node_id,
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
                 'svc_id',
                 'node_id',
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
                 h['svc_id'],
                 node_id,
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
        generic_insert('svcmon_log_last', _vars, _vals)
        if h['mon_overallstatus'] == 'warn':
            level = "warning"
        else:
            level = "info"
        _log("service.status",
             "service state changed: avail(%(a1)s=>%(a2)s) overall(%(o1)s=>%(o2)s)",
             dict(
               a1="undef",
               a2=h['mon_availstatus'],
               o1="undef",
               o2=h['mon_overallstatus']),
             svc_id=h['svc_id'],
             node_id=node_id,
             level=level)
    elif h['mon_overallstatus'] != last["mon_overallstatus"] or \
         h['mon_availstatus'] != last["mon_availstatus"]:
        _vars = ['mon_begin',
                 'mon_end',
                 'svc_id',
                 'node_id',
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
        _vals = [last['mon_begin'],
                 now,
                 last['svc_id'],
                 node_id,
                 last['mon_overallstatus'],
                 last['mon_availstatus'],
                 last['mon_ipstatus'],
                 last['mon_fsstatus'],
                 last['mon_diskstatus'],
                 last['mon_sharestatus'],
                 last['mon_containerstatus'],
                 last['mon_appstatus'],
                 last['mon_syncstatus'],
                 last['mon_hbstatus']]
        generic_insert('svcmon_log', _vars, _vals)
        _vals = [h['mon_updated'],
                 h['mon_updated'],
                 h['svc_id'],
                 node_id,
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
        generic_insert('svcmon_log_last', _vars, _vals)
        if h['mon_overallstatus'] == 'warn':
            level = "warning"
        else:
            level = "info"
        _log("service.status",
             "service state changed: avail(%(a1)s=>%(a2)s) overall(%(o1)s=>%(o2)s)",
             dict(
               a1=last["mon_availstatus"],
               a2=h['mon_availstatus'],
               o1=last["mon_overallstatus"],
               o2=h['mon_overallstatus']),
             svc_id=h['svc_id'],
             node_id=node_id,
             level=level)
    else:
        db.executesql("""update svcmon_log_last set mon_end=now() where id=%d"""%last["id"])
        db.commit()
        table_modified("svcmon_log_last")
    print datetime.datetime.now() - _now, "update svcmon_log"



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
                 svc_id,
                 if(svc_env="PRD", 1, 0),
                 "",
                 "",
                 updated,
                 "",
                 svc_env,
                 now(),
                 "",
                 NULL
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
               dashboard.svc_id=svcmon.svc_id and
               dashboard.node_id=svcmon.node_id
             where
               dashboard.svc_id!="" and
               dashboard.node_id!="" and
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
                 svc_id,
                 if(mon_svctype="PRD", 1, 0),
                 "",
                 "",
                 mon_updated,
                 "",
                 mon_svctype,
                 now(),
                 node_id,
                 NULL
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
                 0,
                 "",
                 "",
                 updated,
                 "",
                 node_env,
                 now(),
                 node_id,
                 NULL
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
                 0,
                 "",
                 "",
                 now(),
                 "",
                 mon_svctype,
                 now(),
                 node_id,
                 NULL
               from svcmon
               where
                 node_id not in (
                   select node_id from nodes
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
                 1,
                 "",
                 "",
                 "%(now)s",
                 "",
                 node_env,
                 "%(now)s",
                 node_id,
                 NULL
               from nodes
               where
                 maintenance_end is not NULL and
                 maintenance_end != "0000-00-00 00:00:00" and
                 maintenance_end < now()
               on duplicate key update
                 dash_updated="%(now)s"
          """%dict(now=str(now))
    db.executesql(sql)

    sql = """delete from dashboard where
               dash_type="node maintenance expired" and
               (
                 dash_updated < "%(now)s" or
                 dash_updated is null
               )
          """%dict(now=str(now))
    db.executesql(sql)
    db.commit()

def cron_dash_node_near_maintenance_date():
    sql = """insert into dashboard
               select
                 NULL,
                 "node close to maintenance end",
                 "",
                 0,
                 "",
                 "",
                 now(),
                 "",
                 node_env,
                 now(),
                 node_id,
                 NULL
               from nodes
               where
                 maintenance_end is not NULL and
                 maintenance_end != "0000-00-00 00:00:00" and
                 maintenance_end > date_sub(now(), interval 30 day) and
                 maintenance_end < now()
               on duplicate key update
                 dash_updated=now()
          """
    db.executesql(sql)
    db.commit()

def cron_dash_node_without_maintenance_date():
    # do not alert for nodes under warranty
    sql = """insert into dashboard
               select
                 NULL,
                 "node without maintenance end date",
                 "",
                 0,
                 "",
                 "",
                 now(),
                 "",
                 node_env,
                 now(),
                 node_id,
                 NULL
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
               and node_id not in (
                 select distinct node_id from checks_live
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
               and d.node_id=c.node_id
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
               and d.node_id=c.node_id
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
                 if(n.node_env="PRD", 1, 0),
                 "%(t)s:%(i)s",
                 concat('{"i":"', chk_instance, '", "t":"', chk_type, '"}'),
                 chk_updated,
                 md5(concat('{"i":"', chk_instance, '", "t":"', chk_type, '"}')),
                 n.node_env,
                 now(),
                 c.node_id,
                 NULL
               from checks_live c
                 join nodes n on c.node_id=n.node_id
               where
                 chk_updated < date_sub(now(), interval 1 day)
               on duplicate key update
                 dash_updated=now()"""
    db.executesql(sql)
    db.commit()

def cron_dash_app_without_responsible():
    # purge alerts for app that now have a responsible
    sql = """delete from dashboard where
             dash_type="application code without responsible" and
             (dash_dict in (
               select
                 concat('{"a":"', a.app, '"}')
               from apps a join apps_responsibles ar on a.id=ar.app_id
             ) or dash_dict = "" or dash_dict is NULL)
          """
    db.executesql(sql)

    # purge alerts for deleted app codes
    sql = """delete from dashboard where
             dash_type="application code without responsible" and
             dash_dict not in (
               select
                 concat('{"a":"', a.app, '"}')
               from apps a
             )
          """
    db.executesql(sql)

    sql = """insert into dashboard
               select
                 NULL,
                 "application code without responsible",
                 "",
                 2,
                 "%(a)s",
                 concat('{"a":"', a.app, '"}'),
                 now(),
                 md5(concat('{"a":"', a.app, '"}')),
                 "",
                 now(),
                 "",
                 NULL
               from apps a left join apps_responsibles ar on a.id=ar.app_id
               where
                 ar.group_id is NULL
               on duplicate key update
                 dash_updated=now()
          """
    db.executesql(sql)
    ws_send("dashboard_change")
    db.commit()

def cron_dash_purge():
    sql = """delete from dashboard where
              svc_id != "" and
              svc_id not in (
                select distinct svc_id from svcmon
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
                 0,
                 "%(t)s: %%(o)s",
                 concat('{"o": "', o.obs_name, '"}'),
                 now(),
                 md5(concat('{"o": "', o.obs_name, '"}')),
                 "",
                 now(),
                 n.node_id,
                 NULL
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
                 1,
                 "%(o)s obsolete since %(a)s",
                 concat('{"a": "', o.obs_alert_date,
                        '", "o": "', o.obs_name,
                        '"}'),
                 now(),
                 "",
                 "",
                 now(),
                 n.node_id,
                 NULL
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
                 0,
                 "%(o)s warning since %(a)s",
                 concat('{"a": "', o.obs_warn_date,
                        '", "o": "', o.obs_name,
                        '"}'),
                 now(),
                 "",
                 "",
                 now(),
                 n.node_id,
                 NULL
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
                 1,
                 "%(o)s obsolete since %(a)s",
                 concat('{"a": "', o.obs_alert_date,
                        '", "o": "', o.obs_name,
                        '"}'),
                 now(),
                 "",
                 "",
                 now(),
                 n.node_id,
                 NULL
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
                 0,
                 "%(o)s warning since %(a)s",
                 concat('{"a": "', o.obs_warn_date,
                        '", "o": "', o.obs_name,
                        '"}'),
                 now(),
                 "",
                 "",
                 now(),
                 n.node_id,
                 NULL
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
def update_dash_service_not_updated(svc_id):
    sql = """delete from dashboard
               where
                 svc_id = "%(svc_id)s" and
                 dash_type = "service configuration not updated"
          """%dict(svc_id=svc_id)
    rows = db.executesql(sql)
    db.commit()
    dashboard_events()

def update_dash_pkgdiff(node_id):
    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)

    q = db.nodes.node_id == db.svcmon.node_id
    q &= db.svcmon.mon_updated > datetime.datetime.now() - datetime.timedelta(minutes=20)
    rows = db(q).select(db.svcmon.svc_id, db.svcmon.mon_svctype)
    svc_ids = map(lambda x: x.svc_id, rows)

    for row in rows:
        svc_id = row.svc_id

        q = db.svcmon.svc_id == svc_id
        q &= db.svcmon.node_id == db.nodes.node_id
        q &= db.svcmon.mon_updated > datetime.datetime.now() - datetime.timedelta(minutes=20)
        nodes = db(q).select(db.nodes.node_id, db.nodes.nodename,
                             orderby=db.nodes.nodename,
                             groupby=db.nodes.node_id)
        node_ids = map(lambda x: str(x.node_id), nodes)
        nodenames = map(lambda x: str(x.nodename), nodes)
        n = len(nodes)

        if n < 2:
            continue

        sql = """select count(id) from (
                   select
                     id,
                     count(node_id) as c
                   from packages
                   where
                     node_id in (%(node_ids)s)
                   group by
                     pkg_name,
                     pkg_version,
                     pkg_arch,
                     pkg_type
                  ) as t
                  where
                    t.c!=%(n)s
              """%dict(node_ids=','.join(map(lambda x: repr(x), node_ids)), n=n)

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
            nodes_s = ','.join(nodenames)+trail
            if len(nodes_s) < 50:
                break
            skip += 1
            nodenames = nodenames[:-1]
            trail = ", ... (+%d)"%skip

        sql = """insert into dashboard
                 set
                   dash_type="package differences in cluster",
                   svc_id="%(svc_id)s",
                   node_id="",
                   dash_severity=%(sev)d,
                   dash_fmt="%%(n)s package differences in cluster %%(nodes)s",
                   dash_dict='{"n": %(n)d, "nodes": "%(nodes)s"}',
                   dash_dict_md5=md5('{"n": %(n)d, "nodes": "%(nodes)s"}'),
                   dash_created="%(now)s",
                   dash_updated="%(now)s",
                   dash_env="%(env)s"
                 on duplicate key update
                   dash_updated="%(now)s"
              """%dict(svc_id=svc_id,
                       now=str(now),
                       sev=sev,
                       env=row.mon_svctype,
                       n=rows[0][0],
                       nodes=nodes_s)

        rows = db.executesql(sql)
        db.commit()

    # clean old
    if len(svc_ids) > 0:
	q = db.dashboard.svc_id.belongs(svc_ids)
	q &= db.dashboard.dash_type == "package differences in cluster"
	q &= db.dashboard.dash_updated < now - datetime.timedelta(seconds=1)
	db(q).delete()
	db.commit()
    dashboard_events()

def update_dash_flex_cpu(svc_id):
    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)

    sql = """select svc_env from services
             where
               svc_id="%(svc_id)s"
          """%dict(svc_id=svc_id)
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
                 "%(svc_id)s",
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
                 now(),
                 "",
                 NULL
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
                     c.svc_id = "%(svc_id)s" and
                     c.mon_availstatus = 'up'
                   ) AS up,
                   (
                    select
                     (100 - c.idle)
                    from stats_cpu c join svcmon m
                    where
                     c.node_id = m.node_id and
                     m.svc_id = "%(svc_id)s" and
                     c.date > (now() + interval -(15) minute) and
                     c.cpu = 'all' and
                     m.mon_overallstatus = 'up'
                    group by m.svc_id
                   ) AS cpu
                  from v_svcmon p
                  where
                   p.svc_id="%(svc_id)s"
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
          """%dict(svc_id=svc_id,
                   sev=sev,
                   env=rows[0][0],
                  )
    db.executesql(sql)
    db.commit()

    sql = """delete from dashboard
               where
                 svc_id = "%(svc_id)s" and
                 dash_type = "flex error" and
                 dash_updated < "%(now)s" and
                 dash_fmt like "%%average cpu usage%%"
          """%dict(svc_id=svc_id, now=str(now))
    rows = db.executesql(sql)
    db.commit()

    dashboard_events()

def update_dash_flex_instances_started(svc_id):
    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)
    sql = """select svc_env from services
             where
               svc_id="%(svc_id)s"
          """%dict(svc_id=svc_id)
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
                 "%(svc_id)s",
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
                 now(),
                 "",
                 NULL
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
                     c.svc_id = "%(svc_id)s" and
                     c.mon_availstatus = 'up'
                   ) AS up
                  from v_svcmon p
                  where
                   p.svc_id="%(svc_id)s"
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
          """%dict(svc_id=svc_id,
                   sev=sev,
                   env=rows[0][0],
                  )
    db.executesql(sql)
    db.commit()

    sql = """delete from dashboard
               where
                 svc_id = "%(svc_id)s" and
                 dash_type = "flex error" and
                 dash_updated < "%(now)s" and
                 dash_fmt like "%%instances started%%"
          """%dict(svc_id=svc_id, now=str(now))
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
                 t.svc_id,
                 if (t.node_env="PRD", 3, 2),
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
                 t.node_env,
                 "%(now)s",
                 t.node_id,
                 NULL
               from (
                 select
                   c.svc_id as svc_id,
                   c.node_id as node_id,
                   c.chk_type as ctype,
                   c.chk_instance as inst,
                   c.chk_threshold_provider as ttype,
                   c.chk_value as val,
                   c.chk_low as min,
                   c.chk_high as max,
                   n.node_env
                 from checks_live c left join nodes n on c.node_id=n.node_id
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

def update_dash_checks(node_id):
    try:
        q = db.nodes.node_id == node_id
        env = db(q).select().first().node_env
    except:
        env = 'TST'
    if env == 'PRD':
        sev = 3
    else:
        sev = 2

    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)

    sql = """insert into dashboard
               select
                 NULL,
                 "check out of bounds",
                 t.svc_id,
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
                 "%(now)s",
                 t.node_id,
                 NULL
               from (
                 select
                   svc_id as svc_id,
                   node_id as node_id,
                   chk_type as ctype,
                   chk_instance as inst,
                   chk_threshold_provider as ttype,
                   chk_value as val,
                   chk_low as min,
                   chk_high as max
                 from checks_live
                 where
                   node_id = "%(node_id)s" and
                   chk_updated >= date_sub(now(), interval 1 day) and
                   (
                     chk_value < chk_low or
                     chk_value > chk_high
                   )
               ) t
               on duplicate key update
                 dash_updated="%(now)s"
          """%dict(node_id=node_id,
                   sev=sev,
                   env=env,
                   now=str(now),
                  )
    db.executesql(sql)
    db.commit()

    sql = """delete from dashboard
               where
                 node_id = "%(node_id)s" and
                 (
                   (
                     dash_type = "check out of bounds" and
                     ( dash_updated < "%(now)s" or dash_updated is null )
                   ) or
                   dash_type = "check value not updated"
                 )
          """%dict(node_id=node_id, now=str(now))

    rows = db.executesql(sql)
    db.commit()
    dashboard_events()

def update_dash_netdev_errors(node_id):
    now = datetime.datetime.now()
    now -= datetime.timedelta(microseconds=now.microsecond)
    sql = """select dev, sum(rxerrps+txerrps+collps+rxdropps+rxdropps) as errs
               from stats_netdev_err_hour
               where
                 node_id = "%(node_id)s" and
                 date > date_sub(now(), interval 1 day)
               group by dev
          """%dict(node_id=node_id)
    rows = db.executesql(sql, as_dict=True)

    if len(rows) == 0:
        sql = """delete from checks_live
                 where
                  node_id="%(node_id)s" and
                  chk_type = "netdev_err"
              """ % dict(node_id=node_id)
        db.executesql(sql)
        db.commit()
        return

    for row in rows:
        sql = """insert into checks_live
                 set
                   chk_type="netdev_err",
                   svc_id="",
                   node_id="%(node_id)s",
                   chk_value=%(errs)d,
                   chk_updated="%(now)s",
                   chk_instance="%(dev)s"
                 on duplicate key update
                   chk_type="netdev_err",
                   svc_id="",
                   node_id="%(node_id)s",
                   chk_value=%(errs)d,
                   chk_updated="%(now)s",
                   chk_instance="%(dev)s"
              """%dict(node_id=node_id,
                       now=now,
                       dev=row['dev'],
                       errs=int(row['errs']))
        db.executesql(sql)
        db.commit()

    sql = """delete from checks_live
             where
               chk_type="netdev_err" and
               chk_updated < "%(now)s" and
               node_id="%(node_id)s"
          """%dict(node_id=node_id,
                   now=now,
                  )
    db.executesql(sql)
    db.commit()

    q = db.checks_live.node_id == node_id
    q &= db.checks_live.chk_type == "netdev_err"
    checks = db(q).select()
    update_thresholds_batch(checks, one_source=True)

    update_dash_checks(node_id)


def update_dash_action_errors(svc_id, node_id):
    sql = """select e.err, s.svc_env from b_action_errors e
             join services s on e.svc_id=s.svc_id
             where
               e.svc_id="%(svc_id)s" and
               e.node_id="%(node_id)s"
          """%dict(svc_id=svc_id, node_id=node_id)
    rows = db.executesql(sql)

    if len(rows) == 1:
        if rows[0][1] == 'PRD':
            sev = 4
        else:
            sev = 3
        sql = """insert into dashboard
                 set
                   dash_type="action errors",
                   svc_id="%(svc_id)s",
                   node_id="%(node_id)s",
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
              """%dict(svc_id=svc_id,
                       node_id=node_id,
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
                     svc_id="%(svc_id)s" and
                     node_id="%(node_id)s" and
                     dash_fmt="%%(err)s action errors"
              """%dict(svc_id=svc_id,
                       node_id=node_id,
                  )
        rows = db.executesql(sqlws)
        if len(rows) > 0:
            ws_send('dash_change', {'dash_md5': rows[0][0]})

    else:
        sqlws = """select dash_md5 from dashboard
                 where
                   dash_type="action errors" and
                   svc_id="%(svc_id)s" and
                   node_id="%(node_id)s"
              """%dict(svc_id=svc_id,
                       node_id=node_id)
        rows = db.executesql(sqlws)
        if len(rows) > 0:
            ws_send('dash_delete', {'dash_md5': rows[0][0]})
        sql = """delete from dashboard
                 where
                   dash_type="action errors" and
                   svc_id="%(svc_id)s" and
                   node_id="%(node_id)s"
              """%dict(svc_id=svc_id,
                       node_id=node_id)
        db.executesql(sql)
        db.commit()

def update_dash_service_placement(svc_id, env, placement):
    if placement == "optimal":
        sql = """delete from dashboard
                 where
                   dash_type="service placement" and
                   svc_id="%(svc_id)s"
              """%dict(svc_id=svc_id)
    else:
        sql = """insert into dashboard
                 set
                   dash_type="service placement",
                   svc_id="%(svc_id)s",
                   dash_severity=1,
                   dash_fmt="%%(placement)s",
                   dash_dict='{"placement": "%(placement)s"}',
                   dash_created=now(),
                   dash_updated=now(),
                   dash_env="%(env)s"
                 on duplicate key update
                   dash_severity=1,
                   dash_updated=now(),
                   dash_env="%(env)s"
              """%dict(svc_id=svc_id,
                       placement=placement,
                       env=env,
                      )
    ret = db.executesql(sql)
    if ret:
        return set(["dashboard"])
    return set()

def update_dash_service_frozen(svc_id, node_id, env, frozen):
    if int(frozen) == 0:
        sql = """delete from dashboard
                 where
                   dash_type="service frozen" and
                   node_id="%(node_id)s" and
                   svc_id="%(svc_id)s"
              """%dict(svc_id=svc_id, node_id=node_id)
    else:
        sql = """insert into dashboard
                 set
                   dash_type="service frozen",
                   svc_id="%(svc_id)s",
                   node_id="%(node_id)s",
                   dash_severity=1,
                   dash_fmt="",
                   dash_dict="",
                   dash_created=now(),
                   dash_updated=now(),
                   dash_env="%(env)s"
                 on duplicate key update
                   dash_severity=1,
                   dash_fmt="",
                   dash_updated=now(),
                   dash_env="%(env)s"
              """%dict(svc_id=svc_id,
                       node_id=node_id,
                       env=env,
                      )
    ret = db.executesql(sql)
    if ret:
        return set(["dashboard"])
    return set()

def update_dash_service_not_on_primary(svc_id, node_id, env, availstatus):
    if env == 'PRD':
        sev = 1
    else:
        sev = 0

    sql = """ select
                n.nodename as nodename,
                s.svc_autostart as svc_autostart,
                s.svc_availstatus as svc_availstatus
              from nodes n, services s, svcmon m where
                s.svc_id="%(svc_id)s" and
                s.svc_topology="failover" and
                s.svc_id=m.svc_id and
                m.node_id=n.node_id and
                n.node_id="%(node_id)s"
          """ % dict(
                  svc_id=svc_id,
                  node_id=node_id,
                )
    rows = db.executesql(sql, as_dict=True)

    if len(rows) == 0:
        return set()

    if rows[0]["svc_autostart"] != rows[0]["nodename"] or \
       availstatus == "up" or \
       rows[0]["svc_availstatus"] != "up" or \
       rows[0]["svc_autostart"] is None or \
       rows[0]["svc_autostart"] == "":
        sql = """delete from dashboard
                 where
                   dash_type="service not started on primary node" and
                   node_id="%(node_id)s" and
                   svc_id="%(svc_id)s"
              """%dict(svc_id=svc_id, node_id=node_id)
        db.executesql(sql)
        return set()

    sql = """insert into dashboard
             set
               dash_type="service not started on primary node",
               svc_id="%(svc_id)s",
               node_id="%(node_id)s",
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

          """%dict(svc_id=svc_id,
                   node_id=node_id,
                   sev=sev,
                   env=env,
                  )
    db.executesql(sql)
    db.commit()
    # dashboard_events() called from __svcmon_update
    return set(["dashboard"])

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

def ping_svc(svc, now):
    changed = set()
    q = db.services.svc_id == svc.svc_id
    result = db(q).update(svc_status_updated=now)
    if result:
        changed.add("services")
    q = db.services_log_last.svc_id == svc.svc_id
    result = db(q).update(svc_end=now)
    return changed

##############################################################################
#
# agent daemon rpc
#
##############################################################################

UP = 0
DOWN = 1
WARN = 2
NA = 3
UNDEF = 5
STDBY_UP = 6
STDBY_DOWN = 7

STATUS_VALUE = {
    'up': UP,
    'down': DOWN,
    'warn': WARN,
    'n/a': NA,
    'undef': UNDEF,
    'stdby up': STDBY_UP,
    'stdby down': STDBY_DOWN,
}

STATUS_STR = {v: k for k, v in STATUS_VALUE.items()}

def encode_pair(status1, status2):
    """
    Return a hashable code unique for the set([status1, status2]).
    """
    return (1 << status1) | (1 << status2)

MERGE_RULES = {
    encode_pair(UP, UP): UP,
    encode_pair(UP, DOWN): WARN,
    encode_pair(UP, WARN): WARN,
    encode_pair(UP, NA): UP,
    encode_pair(UP, STDBY_UP): UP,
    encode_pair(UP, STDBY_DOWN): WARN,
    encode_pair(DOWN, DOWN): DOWN,
    encode_pair(DOWN, WARN): WARN,
    encode_pair(DOWN, NA): DOWN,
    encode_pair(DOWN, STDBY_UP): STDBY_UP,
    encode_pair(DOWN, STDBY_DOWN): STDBY_DOWN,
    encode_pair(WARN, WARN): WARN,
    encode_pair(WARN, NA): WARN,
    encode_pair(WARN, STDBY_UP): WARN,
    encode_pair(WARN, STDBY_DOWN): WARN,
    encode_pair(NA, NA): NA,
    encode_pair(NA, STDBY_UP): STDBY_UP,
    encode_pair(NA, STDBY_DOWN): STDBY_DOWN,
    encode_pair(STDBY_UP, STDBY_UP): STDBY_UP,
    encode_pair(STDBY_UP, STDBY_DOWN): WARN,
    encode_pair(STDBY_DOWN, STDBY_DOWN): STDBY_DOWN,
}

def merge_status(s1, s2):
    return MERGE_RULES[encode_pair(STATUS_VALUE[s1], STATUS_VALUE[s2])]

def ping_instance(svc, peer, now):
    changed = set()
    q = (db.svcmon.node_id == peer.node_id) & (db.svcmon.svc_id == svc.svc_id)
    result = db(q).update(mon_updated=now)
    if result:
        changed.add("svcmon")

    q = (db.svcmon_log_last.node_id == peer.node_id) & (db.svcmon_log_last.svc_id == svc.svc_id)
    result = db(q).update(mon_end=now)

    q = (db.resmon.node_id == peer.node_id) & (db.resmon.svc_id == svc.svc_id)
    result = db(q).update(updated=now)
    if result:
        changed.add("resmon")

    q = (db.resmon_log_last.node_id == peer.node_id) & (db.resmon_log_last.svc_id == svc.svc_id)
    result = db(q).update(res_end=now)
    return changed

def ping_peer(peer, now):
    changed = set()
    q = db.svcmon.node_id == peer.node_id
    result = db(q).update(mon_updated=now)
    if result:
        changed.add("svcmon")

    q = db.svcmon_log_last.node_id == peer.node_id
    result = db(q).update(mon_end=now)

    q = db.resmon.node_id == peer.node_id
    result = db(q).update(updated=now)
    if result:
        changed.add("resmon")

    q = db.resmon_log_last.node_id == peer.node_id
    result = db(q).update(res_end=now)
    return changed

def merge_daemon_ping(node_id):
    print "daemon ping", node_id
    changed = set()
    now = datetime.datetime.now()
    data = rconn.hget(R_DAEMON_STATUS_HASH, node_id)

    if data is None:
        return

    node = get_node(node_id)
    node_ids = {
        node.nodename: node,
    }
    app_q = db.nodes.app == node.app

    def get_cluster_node(nodename):
        try:
            return node_ids[nodename]
        except KeyError:
            q = app_q & (db.nodes.nodename == nodename)
            _node = db(q).select(db.nodes.node_id).first()
            if _node is None:
                node_ids[nodename] = None
            else:
                node_ids[nodename] = _node
            return node_ids[nodename]

    data = json.loads(data)

    for nodename, ndata in data["nodes"].items():
        peer = get_cluster_node(nodename)
        changed |= ping_peer(peer, now)

    peer_node_ids = [node.node_id for node in node_ids.values()]
    for svcname in data["services"].keys():
        for peer_node_id in peer_node_ids:
            svc = node_svc(peer_node_id, svcname)
            if svc:
                break
        print " ping service", svcname, svc.svc_id
        changed |= ping_svc(svc, now)

    print " tables changed:", ",".join(changed)
    for table_name in changed:
        table_modified(table_name)
        ws_send(table_name+'_change')

def merge_daemon_status(node_id, changes):
    print "daemon status", node_id, changes
    now = datetime.datetime.now()
    data = rconn.hget(R_DAEMON_STATUS_HASH, node_id)
    changed = set()

    if data is None:
        return

    data = json.loads(data)
    node = get_node(node_id)
    node_ids = {
        node.nodename: node,
    }
    app_q = db.nodes.app == node.app

    def get_cluster_node(nodename):
        try:
            return node_ids[nodename]
        except KeyError:
            q = app_q & (db.nodes.nodename == nodename)
            _node = db(q).select().first()
            if _node is None:
                node_ids[nodename] = None
            else:
                node_ids[nodename] = _node
            return node_ids[nodename]

    def update_container_node_fields(svc, peer, container_id, idata):
        if idata["resources"][container_id]["status"] != "up":
            return set()
        cname = idata["encap"][container_id]["hostname"]
        q = db.nodes.nodename == cname
        q &= (db.nodes.app == peer.app) | (db.nodes.app == svc.svc_app)
        if db(q).count() == 0:
            q = db.nodes.nodename == cname
            q &= db.nodes.app.belongs(node_responsibles_apps(peer.node_id))
        db(q).update(
            hv=peer.nodename,
            loc_city=peer.loc_city,
            loc_country=peer.loc_country,
            loc_zip=peer.loc_zip,
            loc_floor=peer.loc_floor,
            loc_rack=peer.loc_rack,
            loc_room=peer.loc_room,
            loc_building=peer.loc_building,
            loc_addr=peer.loc_addr,
            enclosure=peer.enclosure,
            enclosureslot=peer.enclosureslot,
            updated=now,
        )
        return set(["nodes"])

    def update_instance(svc, peer, container_id, idata):
        _changed = set()
        if container_id == "":
            cdata = {"resources": {}}
            cname = ""
            ctype = ""
            data = idata
        else:
            cdata = idata["encap"][container_id]
            cname = cdata["hostname"]
            ctype = idata["resources"][container_id]["type"].split(".")[-1]
            data = {}
            for key in ("avail", "overall", "ip", "disk", "fs", "share", "container", "app", "sync"):
                data[key] = STATUS_STR[merge_status(idata.get(key, "n/a"), cdata.get(key, "n/a"))]
            #
            # 0: global thawed + encap thawed
            # 1: global frozen + encap thawed
            # 2: global thawed + encap frozen
            # 3: global frozen + encap frozen
            #
            if cdata.get("frozen"):
                data["frozen"] = int(idata["frozen"]) + 2
            else:
                data["frozen"] = int(idata["frozen"])

        db.svcmon.update_or_insert({
                "node_id": peer.node_id,
                "svc_id": svc.svc_id,
                "mon_vmname": cname,
            },
            node_id=peer.node_id,
            svc_id=svc.svc_id,
            mon_vmname=cname,
            mon_availstatus=data["avail"],
            mon_overallstatus=data["overall"],
            mon_ipstatus=data["ip"],
            mon_diskstatus=data["disk"],
            mon_fsstatus=data["fs"],
            mon_sharestatus=data["share"],
            mon_containerstatus=data["container"],
            mon_appstatus=data["app"],
            mon_syncstatus=data["sync"],
            mon_frozen=int(data["frozen"]),
            mon_vmtype=ctype,
            mon_updated=now,
        )
        _changed.add("svcmon")
        _changed |= update_dash_service_frozen(svc.svc_id, peer.node_id, svc.svc_env, data['frozen'])
        _changed |= update_dash_service_not_on_primary(svc.svc_id, peer.node_id, svc.svc_env, data['avail'])
        _changed |= update_dash_svcmon_not_updated(svc.svc_id, peer.node_id)
        _changed |= update_instance_resources(svc, peer, cname, cdata["resources"])
        return _changed

    def update_instance_resources(svc, peer, cname, resources):
        _changed = set()
        for rid, rdata in resources.items():
            db.resmon.update_or_insert({
                    "node_id": peer.node_id,
                    "svc_id": svc.svc_id,
                    "vmname": cname,
                    "rid": rid,
                },
                node_id=peer.node_id,
                svc_id=svc.svc_id,
                vmname=cname,
                rid=rid,
                res_status=rdata["status"],
                res_type=rdata["type"],
                res_log=rdata["log"],
                res_optional=rdata["optional"],
                res_disable=rdata["disable"],
                res_monitor=rdata["monitor"],
                res_desc=rdata["label"],
                updated=now,
            )
            _changed.add("resmon")
            _changed |= resmon_log_update(peer.node_id, svc.svc_id, rid, rdata['status'], deferred=True)
        return _changed

    def update_service(svc, sdata):
        result = db.services.update_or_insert({
                "svc_id": svc.svc_id,
            },
            svc_id=svc.svc_id,
            svc_availstatus=sdata["avail"],
            svc_status=sdata["overall"],
            svc_placement=sdata["placement"],
            svc_frozen=sdata["frozen"],
            svc_provisioned=sdata["provisioned"],
            svc_status_updated=now,
        )
        return set(["services"])

    for nodename, ndata in data["nodes"].items():
        peer = get_cluster_node(nodename)

    for svcname, sdata in data["services"].items():
        peer_node_ids = [node.node_id for node in node_ids.values()]
        for peer_node_id in peer_node_ids:
            svc = node_svc(peer_node_id, svcname)
            if svc:
                break
        if changes is not None and svcname not in changes and not svc.svc_availstatus == "undef":
            print " ping service", svcname, svc.svc_id
            ping_svc(svc, now)
        else:
            print " update service", svcname, svc.svc_id
            changed |= svc_log_update(svc.svc_id, sdata["avail"], deferred=True)
            changed |= update_service(svc, sdata)

        for nodename, ndata in data["nodes"].items():
            peer = get_cluster_node(nodename)
            if peer is None:
                print "  skip instance on unknwon peer", nodename
                continue
            if changes is not None and svcname+"@"+nodename not in changes and not svc.svc_availstatus == "undef":
                print "  ping service", svcname, svc.svc_id, "instance on node", nodename
                ping_instance(svc, peer, now)
                continue
            try:
                idata = ndata["services"]["status"][svcname]
            except KeyError:
                continue

            print "  update service", svcname, svc.svc_id, "instance on node", nodename
            encap = idata.get("encap")
            if isinstance(encap, bool) or encap is None or len(encap) == 0:
                changed |= update_instance(svc, peer, "", idata)
            else:
                for container_id, cdata in encap.items():
                    changed |= update_container_node_fields(svc, peer, container_id, idata)
                    changed |= update_instance(svc, peer, container_id, idata)

            changed |= update_instance_resources(svc, peer, "", idata["resources"])
            changed |= svcmon_log_update(peer.node_id, svc.svc_id, idata, deferred=True)

        changed |= update_dash_service_unavailable(svc.svc_id, svc.svc_env, sdata["avail"])
        changed |= update_dash_service_placement(svc.svc_id, svc.svc_env, sdata["placement"])
        update_dash_service_available_but_degraded(svc.svc_id, svc.svc_env, sdata["avail"], sdata["overall"])
        # TODO
        # provisioned alerts

    print " tables changed:", ",".join(changed)
    for table_name in changed:
        table_modified(table_name)
        ws_send(table_name+'_change')

from gluon.contrib.redis_scheduler import RScheduler
scheduler = RScheduler(db, migrate=False, redis_conn=rconn)
