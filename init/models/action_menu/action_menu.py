config = local_import('config', reload=True)

try:
    remote_cmd_prepend = config.remote_cmd_prepend
except:
    remote_cmd_prepend = []

ssh_cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                  '-o', 'ForwardX11=no',
                  '-o', 'ConnectTimeout=5',
                  '-o', 'PasswordAuthentication=no']
#                  '-tt']

def get_ssh_cmd(node):
    try:
        return config.remote_cmd_ssh.get(node.os_name, ssh_cmd)
    except:
        return ssh_cmd

def known_ip(nodename, addr):
    q = db.node_ip.nodename == nodename
    q &= db.node_ip.addr == addr
    row = db(q).select().first()
    if row is None:
        return False
    return True

def get_reachable_name(node):
    q = db.v_nodenetworks.nodename == node.nodename
    q &= db.v_nodenetworks.mask != None
    q &= db.v_nodenetworks.mask != ""
    q &= db.v_nodenetworks.net_gateway != None
    q &= db.v_nodenetworks.net_gateway != ""
    q &= db.v_nodenetworks.net_gateway != "0.0.0.0"
    o = ~db.v_nodenetworks.prio | db.v_nodenetworks.type
    row = db(q).select(db.v_nodenetworks.addr, orderby=o, limitby=(0,1)).first()
    if row is None:
        return node.nodename
    return row.addr

def get_action_type(node):
    if node.action_type is not None:
        return node.action_type
    if node.os_name == "Windows":
        action_type = "pull"
    else:
        action_type = "push"
    return action_type

def start_actiond():
    from subprocess import Popen
    import sys
    purge_action_queue()
    actiond = 'applications'+str(URL(r=request,c='actiond',f='actiond.py'))
    process = Popen([sys.executable, actiond])
    process.communicate()

def enqueue_node_action(node, action):
    action_type = get_action_type(node)
    connect_to = get_reachable_name(node)
    command = fmt_node_action(node, action, action_type, connect_to=connect_to)
    vars = ['nodename', 'svcname', 'action_type', 'command', 'user_id', 'connect_to']
    vals = [node.nodename, "", action_type, command, str(auth.user_id), connect_to]
    generic_insert('action_queue', vars, vals)

def enqueue_node_comp_action(node, action, mode, mod):
    action_type = get_action_type(node)
    connect_to = get_reachable_name(node)
    command = fmt_node_comp_action(node, action, mode, mod, action_type, connect_to=connect_to)
    vars = ['nodename', 'svcname', 'action_type', 'command', 'user_id', 'connect_to']
    vals = [node.nodename, "", action_type, command, str(auth.user_id), connect_to]
    generic_insert('action_queue', vars, vals)

def enqueue_svc_action(node, svc, action, rid=None):
    action_type = get_action_type(node)
    connect_to = get_reachable_name(node)
    command = fmt_svc_action(node, svc, action, action_type, rid=rid, connect_to=connect_to)
    vars = ['nodename', 'svcname', 'action_type', 'command', 'user_id', 'connect_to']
    vals = [node.nodename, svc, action_type, command, str(auth.user_id), connect_to]
    generic_insert('action_queue', vars, vals)

def enqueue_svc_comp_action(node, svc, action, mode, mod):
    action_type = get_action_type(node)
    connect_to = get_reachable_name(node)
    command = fmt_svc_comp_action(node, svc, action, mode, mod, action_type, connect_to=connect_to)
    vars = ['nodename', 'svcname', 'action_type', 'command', 'user_id', 'connect_to']
    vals = [node.nodename, svc, action_type, command, str(auth.user_id), connect_to]
    generic_insert('action_queue', vars, vals)

def fmt_svc_action(node, svc, action, action_type, rid=None, connect_to=None):
    action = action.replace('"', '\"').replace("'", "\'")
    if connect_to is None:
        connect_to = get_reachable_name(node)
    if action_type == "pull":
        cmd = []
    else:
        cmd = get_ssh_cmd(node) + ['opensvc@'+connect_to, '--'] + remote_cmd_prepend
        cmd += ['sudo', '/opt/opensvc/bin/svcmgr', '--service', svc]
    cmd += [action]
    if rid is not None:
        cmd += ["--rid", rid]
    return ' '.join(cmd)

def fmt_node_comp_action(node, action, mode, mod, action_type, connect_to=None):
    if connect_to is None:
        connect_to = get_reachable_name(node)
    if action_type == "pull":
        cmd = []
    else:
        cmd = get_ssh_cmd(node) + ['opensvc@'+connect_to, '--'] + remote_cmd_prepend
        cmd += ['sudo', '/opt/opensvc/bin/nodemgr']
    cmd += ['compliance', action, '--'+mode, mod]
    return ' '.join(cmd)

def fmt_node_action(node, action, action_type, connect_to=None):
    if connect_to is None:
        connect_to = get_reachable_name(node)
    if action_type == "pull":
        cmd = []
    else:
        cmd = get_ssh_cmd(node) + ['opensvc@'+connect_to, '--'] + remote_cmd_prepend
        cmd += ['sudo', '/opt/opensvc/bin/nodemgr']
    cmd += [action]
    return ' '.join(cmd)

def fmt_svc_comp_action(node, service, action, mode, mod, action_type, connect_to=None):
    if connect_to is None:
        connect_to = get_reachable_name(node)
    if action_type == "pull":
        cmd = []
    else:
        cmd = get_ssh_cmd(node) + ['opensvc@'+connect_to, '--'] + remote_cmd_prepend
        cmd += ['sudo', '/opt/opensvc/bin/svcmgr', '-s', service]
    cmd += ['compliance', action, '--'+mode, mod]
    return ' '.join(cmd)

@auth.requires_membership('CompExec')
def do_node_comp_action(nodename, action, mode, obj):
    if action.startswith("compliance_"):
        action = action.replace("compliance_", "")
    if mode not in ("module", "moduleset"):
        raise ToolError("unsupported mode")
    if action not in ("check", "fix"):
        raise ToolError("unsupported action")

    q = db.nodes.nodename == nodename
    q &= db.nodes.team_responsible.belongs(user_groups())
    node = db(q).select(db.nodes.nodename, db.nodes.os_name, db.nodes.action_type, cacheable=True).first()

    if node is None:
        return 0

    enqueue_node_comp_action(node, action, mode, obj)
    _log('node.action', 'run %(a)s of %(mode)s %(m)s',
         dict(a=action, mode=mode, m=obj),
         nodename=node.nodename
    )
    return 1

def do_node_action(nodename, action=None):
    if action is None or len(action) == 0:
        raise ToolError("no action specified")

    q = db.nodes.nodename == nodename
    q &= db.nodes.team_responsible.belongs(user_groups())
    node = db(q).select(db.nodes.nodename, db.nodes.os_name, db.nodes.action_type, cacheable=True).first()

    if node is None:
        return 0

    if action == "wol":
        return do_node_wol_action(nodename)

    enqueue_node_action(node, action)
    _log('node.action', 'run %(a)s',
         dict(a=action),
         nodename=node.nodename
    )
    return 1

def do_node_wol_action(nodename):
    candidates = wol_candidates(nodename)
    n = 0
    for candidate in candidates:
        action = "wol --mac %s --broadcast %s"%(candidate["mac"], candidate["broadcast"])
        node = db(db.nodes.nodename==candidate['proxy_nodename']).select().first()
        if node is None:
            continue
        n += do_node_action(node, action)
    return n

@auth.requires_membership('CompExec')
def do_svc_comp_action(nodename, svcname, action, mode, obj):
    if action.startswith("compliance_"):
        action = action.replace("compliance_", "")
    if mode not in ("module", "moduleset"):
        raise ToolError("unsupported mode")
    if action not in ("check", "fix"):
        raise ToolError("unsupported action")

    # filter out services we are not responsible for
    sql = """select m.os_name
             from v_svcmon m
             join apps a on m.svc_app=a.app
             join apps_responsibles ar on a.id=ar.app_id
             join auth_group g on ar.group_id=g.id and g.id in (%(gids)s)
             where
               m.mon_svcname="%(svcname)s" and
               (mon_nodname="%(nodename)s" or mon_vmname="%(nodename)s")
             group by m.mon_nodname, m.mon_svcname
          """%dict(nodename=nodename,
                   svcname=svcname,
                   gids=",".join(map(lambda x: str(x), user_group_ids())))
    rows = db.executesql(sql, as_dict=True)
    if len(rows) == 0:
        return 0

    row = rows[0]
    node = db(db.nodes.nodename==nodename).select().first()
    if node is None:
        return 0
    enqueue_svc_comp_action(node, svcname, action, mode, obj)
    _log('service.action',
         'run %(a)s of %(mode)s %(m)s',
         dict(a=action, mode=mode, m=obj),
         svcname=svcname,
         nodename=nodename
    )
    return 1

def do_svc_action(nodename, svcname, action, rid=None):
    if action is None or len(action) == 0:
        raise ToolError("no action specified")

    if not action.startswith("create"):
        # filter out services we are not responsible for
        sql = """select m.mon_nodname, m.mon_svcname
                 from v_svcmon m
                 join apps a on m.svc_app=a.app
                 join apps_responsibles ar on a.id=ar.app_id
                 join auth_group g on ar.group_id=g.id and g.id in (%(gids)s)
                 where
                   m.mon_svcname="%(svcname)s" and
                   (mon_nodname="%(nodename)s" or mon_vmname="%(nodename)s")
                 group by m.mon_nodname, m.mon_svcname
              """%dict(nodename=nodename,
                       svcname=svcname,
                       gids=",".join(map(lambda x: str(x), user_group_ids())))
        rows = db.executesql(sql)
        if len(rows) == 0:
            return 0

    # filter out nodes we are not responsible for
    q = db.nodes.nodename == nodename
    q &= db.nodes.team_responsible.belongs(user_groups())
    node = db(q).select(db.nodes.nodename, db.nodes.os_name, db.nodes.action_type, cacheable=True).first()
    if node is None:
        return 0

    enqueue_svc_action(node, svcname, action, rid=rid)
    if rid is None:
        _log('service.action',
             'run %(a)s',
             dict(a=action),
             svcname=svcname,
             nodename=nodename
        )
    else:
        _log('service.resource.action',
             'run %(a)s on rid %(r)s',
             dict(a=action, r=rid),
             svcname=svcname,
             nodename=nodename
        )
    return 1

def json_action_one(d):
    if "rid" in d and "svcname" in d and "nodename" in d:
        if "action" in d:
            return do_svc_action(d["nodename"], d["svcname"], d["action"], rid=d["rid"])
    elif "svcname" in d and d["svcname"] != "" and "nodename" in d:
        if "ruleset" in d:
            return do_svc_comp_action(d["nodename"], d["svcname"], d["action"], "ruleset", d["ruleset"])
        elif "moduleset" in d:
            return do_svc_comp_action(d["nodename"], d["svcname"], d["action"], "moduleset", d["moduleset"])
        elif "module" in d:
            return do_svc_comp_action(d["nodename"], d["svcname"], d["action"], "module", d["module"])
        elif "action" in d:
            return do_svc_action(d["nodename"], d["svcname"], d["action"])
    elif "nodename" in d:
        if "ruleset" in d:
            return do_node_comp_action(d["nodename"], d["action"], "ruleset", d["ruleset"])
        elif "moduleset" in d:
            return do_node_comp_action(d["nodename"], d["action"], "moduleset", d["moduleset"])
        elif "module" in d:
            return do_node_comp_action(d["nodename"], d["action"], "module", d["module"])
        elif "action" in d:
            return do_node_action(d["nodename"], d["action"])
    return 0

def factorize_actions(data):
    fdata = []
    rid_h = {}
    for d in data:
        if "rid" in d and "svcname" in d and "nodename" in d:
            i = (d["svcname"], d["nodename"], d["action"])
            if i in rid_h:
                rid_h[i].append(d["rid"])
            else:
                rid_h[i] = [d["rid"]]
        else:
            fdata.append(d)
    for (svcname, nodename, action), rids in rid_h.items():
        fdata.append({"nodename": nodename, "svcname": svcname, "rid": ','.join(rids), "action": action})
    return fdata

def wol_candidates(nodename):
    sql = """
     select
       n1.nodename as nodename,
       n1.mac as mac,
       n1.net_broadcast as broadcast,
       n2.nodename as proxy_nodename,
       n2.version as proxy_version,
       n2.intf as proxy_intf
     from v_nodenetworks n1
     join v_nodenetworks n2 on
       n1.nodename="%(nodename)s" and
       n1.net_broadcast is not NULL and
       n1.intf not like "%%:%%" and
       n1.addr not like "224%%" and
       n1.net_broadcast=n2.net_broadcast and
       n2.intf not like "%%:%%" and
       n2.version is not null and
       n2.team_responsible in (%(ug)s) and
       substring_index(n2.version,".",1) >= %(v1)d and
       substring_index(substring_index(n2.version,".",-1), "-", 1) >= %(v2)d and
       substring_index(n2.version,"-",-1) >= %(v3)d and
       substring_index(n2.version,"-",-1) < 10000 and
       n2.nodename!="%(nodename)s"
     group by
       n1.net_broadcast
    """ % dict(
      nodename=nodename,
      v1=1, v2=6, v3=110,
      ug=",".join(map(lambda x: repr(x), user_groups())),
    )
    rows = db.executesql(sql, as_dict=True)
    return rows

