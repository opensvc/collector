config = local_import('config', reload=True)

remote_cmd_prepend = config_get("remote_cmd_prepend", [])
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

def known_ip(node_id, addr):
    q = db.node_ip.node_id == node_id
    q &= db.node_ip.addr == addr
    row = db(q).select().first()
    if row is None:
        return False
    return True

def get_reachable_name(node):
    q = db.nodes.node_id == node.node_id
    row = db(q).select().first()
    if row and row.connect_to and row.connect_to != "":
        return row.connect_to

    q = db.v_nodenetworks.node_id == node.node_id
    q &= db.v_nodenetworks.mask != None
    q &= db.v_nodenetworks.mask != ""
    q &= db.v_nodenetworks.flag_deprecated == False
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
    vars = ['node_id', 'svc_id', 'action_type', 'command', 'user_id', 'connect_to']
    vals = [node.node_id, "", action_type, command, str(auth.user_id), connect_to]
    if node.collector != "" and node.collector is not None:
        data = {"opensvc.action_queue": (vars, vals)}
        return rpc_push(node.collector, data, mirror=False)
    else:
        return generic_insert('action_queue', vars, vals, get_last_id=True)

def enqueue_node_comp_action(node, action, mode, mod):
    action_type = get_action_type(node)
    connect_to = get_reachable_name(node)
    command = fmt_node_comp_action(node, action, mode, mod, action_type, connect_to=connect_to)
    vars = ['node_id', 'svc_id', 'action_type', 'command', 'user_id', 'connect_to']
    vals = [node.node_id, "", action_type, command, str(auth.user_id), connect_to]
    if node.collector != "" and node.collector is not None:
        data = {"opensvc.action_queue": (vars, vals)}
        return rpc_push(node.collector, data, mirror=False)
    else:
        return generic_insert('action_queue', vars, vals, get_last_id=True)

def enqueue_svc_action(node, svc, action, rid=None):
    action_type = get_action_type(node)
    connect_to = get_reachable_name(node)
    command = fmt_svc_action(node, svc, action, action_type, rid=rid, connect_to=connect_to)
    vars = ['node_id', 'svc_id', 'action_type', 'command', 'user_id', 'connect_to']
    vals = [node.node_id, svc, action_type, command, str(auth.user_id), connect_to]
    if node.collector != "" and node.collector is not None:
        data = {"opensvc.action_queue": (vars, vals)}
        return rpc_push(node.collector, data, mirror=False)
    else:
        return generic_insert('action_queue', vars, vals, get_last_id=True)

def enqueue_svc_comp_action(node, svc, action, mode, mod):
    action_type = get_action_type(node)
    connect_to = get_reachable_name(node)
    command = fmt_svc_comp_action(node, svc, action, mode, mod, action_type, connect_to=connect_to)
    vars = ['node_id', 'svc_id', 'action_type', 'command', 'user_id', 'connect_to']
    vals = [node.node_id, svc, action_type, command, str(auth.user_id), connect_to]
    if node.collector != "" and node.collector is not None:
        data = {"opensvc.action_queue": (vars, vals)}
        return rpc_push(node.collector, data, mirror=False)
    else:
        return generic_insert('action_queue', vars, vals, get_last_id=True)

def fmt_svc_action(node, svc_id, action, action_type, rid=None, connect_to=None):
    action = action.replace('"', '\"').replace("'", "\'")
    if connect_to is None:
        connect_to = get_reachable_name(node)
    q = db.services.svc_id == svc_id
    svc = db(q).select().first()
    if action_type == "pull":
        cmd = []
    else:
        cmd = get_ssh_cmd(node) + ['opensvc@'+connect_to, '--'] + remote_cmd_prepend
        cmd += ['sudo', 'svcmgr', '--service', svc.svcname]
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
        cmd += ['sudo', 'nodemgr']
    cmd += ['compliance', action, '--'+mode, mod]
    return ' '.join(cmd)

def fmt_node_action(node, action, action_type, connect_to=None):
    if connect_to is None:
        connect_to = get_reachable_name(node)
    if action_type == "pull":
        cmd = []
    else:
        cmd = get_ssh_cmd(node) + ['opensvc@'+connect_to, '--'] + remote_cmd_prepend
        cmd += ['sudo', 'nodemgr']
    cmd += [action]
    return ' '.join(cmd)

def fmt_svc_comp_action(node, svc_id, action, mode, mod, action_type, connect_to=None):
    if connect_to is None:
        connect_to = get_reachable_name(node)
    q = db.services.svc_id == svc_id
    svc = db(q).select().first()
    if action_type == "pull":
        cmd = []
    else:
        cmd = get_ssh_cmd(node) + ['opensvc@'+connect_to, '--'] + remote_cmd_prepend
        cmd += ['sudo', 'svcmgr', '--service', svc.svcname]
    cmd += ['compliance', action, '--'+mode, mod]
    return ' '.join(cmd)

def do_node_comp_action(node_id, action, mode, obj):
    check_privilege("CompExec")
    if action.startswith("compliance_"):
        action = action.replace("compliance_", "")
    if mode not in ("module", "moduleset"):
        raise ToolError("unsupported mode")
    if action not in ("check", "fix"):
        raise ToolError("unsupported action")

    q = db.nodes.node_id == node_id
    q &= db.nodes.app.belongs(user_apps())
    node = db(q).select(
      db.nodes.node_id,
      db.nodes.nodename,
      db.nodes.os_name,
      db.nodes.action_type,
      db.nodes.collector,
      cacheable=True
    ).first()

    if node is None:
        return 0

    action_id = enqueue_node_comp_action(node, action, mode, obj)
    _log('node.action', 'run %(a)s of %(mode)s %(m)s',
         dict(a=action, mode=mode, m=obj),
         node_id=node.node_id
    )
    return action_id

def do_node_action(node_id, action=None):
    check_privilege("NodeExec")
    if action is None or len(action) == 0:
        raise ToolError("no action specified")

    q = db.nodes.node_id == node_id
    if "Manager" not in user_groups():
        q &= db.nodes.app.belongs(user_apps())
    node = db(q).select(
      db.nodes.node_id,
      db.nodes.nodename,
      db.nodes.os_name,
      db.nodes.action_type,
      db.nodes.collector,
      cacheable=True
    ).first()

    if node is None:
        return 0

    if action == "wol":
        return do_node_wol_action(node_id)

    action_id = enqueue_node_action(node, action)
    _log('node.action', 'run %(a)s',
         dict(a=action),
         node_id=node.node_id
    )
    return action_id

def do_node_wol_action(node_id):
    candidates = wol_candidates(node_id)
    n = 0
    for candidate in candidates:
        action = "wol --mac %s --broadcast %s"%(candidate["mac"], candidate["broadcast"])
        node = db(db.nodes.node_id==candidate['proxy_node_id']).select().first()
        if node is None:
            continue
        n += do_node_action(candidate['proxy_node_id'], action)
    return n

def do_svc_comp_action(node_id, svc_id, action, mode, obj):
    check_privilege("CompExec")
    if action.startswith("compliance_"):
        action = action.replace("compliance_", "")
    if mode not in ("module", "moduleset"):
        raise ToolError("unsupported mode")
    if action not in ("check", "fix"):
        raise ToolError("unsupported action")

    node = get_node(node_id)
    if node is None:
        return 0

    # filter out services we are not responsible for
    sql = """select s.svc_id
             from services s
             join apps a on s.svc_app=a.app
             join apps_responsibles ar on a.id=ar.app_id
             join auth_group g on ar.group_id=g.id and g.id in (%(gids)s)
             where
               s.svc_id="%(svc_id)s"
          """%dict(node_id=node_id,
                   svc_id=svc_id,
                   gids=",".join(map(lambda x: str(x), user_group_ids())))
    rows = db.executesql(sql, as_dict=True)
    if len(rows) == 0:
        return 0

    action_id = enqueue_svc_comp_action(node, svc_id, action, mode, obj)
    _log('service.action',
         'run %(a)s of %(mode)s %(m)s',
         dict(a=action, mode=mode, m=obj),
         svc_id=svc_id,
         node_id=node_id
    )
    return action_id

def do_svc_action(node_id, svc_id, action, rid=None):
    check_privilege("NodeExec")
    if action is None or len(action) == 0:
        raise ToolError("no action specified")

    node = get_node(node_id)
    if node is None:
        return 0

    if not action.startswith("create"):
        # filter out services we are not responsible for
        sql = """select s.svc_id
                 from services s
                 join apps a on s.svc_app=a.app
                 join apps_responsibles ar on a.id=ar.app_id
                 join auth_group g on ar.group_id=g.id and g.id in (%(gids)s)
                 where
                   s.svc_id="%(svc_id)s"
              """%dict(node_id=node_id,
                       svc_id=svc_id,
                       gids=",".join(map(lambda x: str(x), user_group_ids())))
        rows = db.executesql(sql)
        if len(rows) == 0:
            return 0

    # filter out nodes we are not responsible for
    q = db.nodes.node_id == node_id
    if action.startswith("create"):
        q &= db.nodes.app.belongs(user_apps())
    node = db(q).select(
      db.nodes.node_id,
      db.nodes.nodename,
      db.nodes.os_name,
      db.nodes.action_type,
      db.nodes.collector,
      cacheable=True
    ).first()
    if node is None:
        return 0

    action_id = enqueue_svc_action(node, svc_id, action, rid=rid)
    if rid is None:
        _log('service.action',
             'run %(a)s',
             dict(a=action),
             svc_id=svc_id,
             node_id=node_id
        )
    else:
        _log('service.resource.action',
             'run %(a)s on rid %(r)s',
             dict(a=action, r=rid),
             svc_id=svc_id,
             node_id=node_id
        )
    return action_id

def json_action_one(d):
    if "vmname" in d:
        d["node_id"] = db(db.nodes.nodename==d["vmname"]).select().first().node_id
        del(d["vmname"])
    if "rid" in d and "svc_id" in d and "node_id" in d:
        if "action" in d:
            return do_svc_action(d["node_id"], d["svc_id"], d["action"], rid=d["rid"])
    elif "svc_id" in d and d["svc_id"] != "" and "node_id" in d:
        if "ruleset" in d:
            return do_svc_comp_action(d["node_id"], d["svc_id"], d["action"], "ruleset", d["ruleset"])
        elif "moduleset" in d:
            return do_svc_comp_action(d["node_id"], d["svc_id"], d["action"], "moduleset", d["moduleset"])
        elif "module" in d:
            return do_svc_comp_action(d["node_id"], d["svc_id"], d["action"], "module", d["module"])
        elif "action" in d:
            return do_svc_action(d["node_id"], d["svc_id"], d["action"])
    elif "node_id" in d:
        if "ruleset" in d:
            return do_node_comp_action(d["node_id"], d["action"], "ruleset", d["ruleset"])
        elif "moduleset" in d:
            return do_node_comp_action(d["node_id"], d["action"], "moduleset", d["moduleset"])
        elif "module" in d:
            return do_node_comp_action(d["node_id"], d["action"], "module", d["module"])
        elif "action" in d:
            return do_node_action(d["node_id"], d["action"])
    return 0

def factorize_actions(data):
    fdata = []
    rid_h = {}
    for d in data:
        if "rid" in d and "svc_id" in d and "node_id" in d:
            if "vmname" in d and d["vmname"] != "":
                d["node_id"] = db(db.nodes.nodename==d["vmname"]).select().first().node_id
                del(d["vmname"])
            i = (d["svc_id"], d["node_id"], d["action"])
            if i in rid_h:
                rid_h[i].append(d["rid"])
            else:
                rid_h[i] = [d["rid"]]
        else:
            fdata.append(d)
    for (svc_id, node_id, action), rids in rid_h.items():
        fdata.append({"node_id": node_id, "svc_id": svc_id, "rid": ','.join(rids), "action": action})
    return fdata

def wol_candidates(node_id):
    ug = user_groups()
    if "Manager" not in ug:
        proxy_filter = "n2.team_responsible in (%(ug)s) and" % dict(ug=",".join(map(lambda x: repr(x), ug)))
    else:
        proxy_filter = ""

    sql = """
     select
       n1.node_id as node_id,
       n1.mac as mac,
       n1.net_broadcast as broadcast,
       n2.node_id as proxy_node_id,
       n2.version as proxy_version,
       n2.intf as proxy_intf
     from v_nodenetworks n1
     join v_nodenetworks n2 on
       n1.node_id="%(node_id)s" and
       n1.net_broadcast is not NULL and
       n1.intf not like "%%:%%" and
       n1.addr not like "224%%" and
       n1.net_broadcast=n2.net_broadcast and
       n2.intf not like "%%:%%" and
       n2.version is not null and
       n2.last_comm > date_sub(now(), interval 15 minute) and
       n2.last_comm is not NULL and
       %(proxy_filter)s
       n2.node_id!="%(node_id)s"
     group by
       n1.net_broadcast
    """ % dict(
      node_id=node_id,
      v1=1, v2=6, v3=110, proxy_filter=proxy_filter,
    )
    rows = db.executesql(sql, as_dict=True)
    return rows

