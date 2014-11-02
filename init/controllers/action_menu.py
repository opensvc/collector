ssh_cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                  '-o', 'ForwardX11=no',
                  '-o', 'PasswordAuthentication=no',
                  '-tt']

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

def action_q_event():
    l = {
      'event': 'action_q_change',
      'data': {'f': 'b'},
    }
    _websocket_send(event_msg(l))

def start_actiond():
    from subprocess import Popen
    import sys
    purge_action_queue()
    actiond = 'applications'+str(URL(r=request,c='actiond',f='actiond.py'))
    process = Popen([sys.executable, actiond])
    process.communicate()

def enqueue_node_action(node, action, os):
    if os == "Windows":
        action_type = "pull"
    else:
        action_type = "push"
    command = fmt_node_action(node, action, action_type)
    vars = ['nodename', 'svcname', 'action_type', 'command', 'user_id']
    vals = [node, "", action_type, command, str(auth.user_id)]
    generic_insert('action_queue', vars, vals)

def enqueue_node_comp_action(node, action, mode, mod, os):
    if os == "Windows":
        action_type = "pull"
    else:
        action_type = "push"
    command = fmt_node_comp_action(node, action, mode, mod, action_type)
    vars = ['nodename', 'svcname', 'action_type', 'command', 'user_id']
    vals = [node, "", action_type, command, str(auth.user_id)]
    generic_insert('action_queue', vars, vals)

def enqueue_svc_action(node, svc, action, os, rid=None):
    if os == "Windows":
        action_type = "pull"
    else:
        action_type = "push"
    command = fmt_svc_action(node, svc, action, action_type, rid=rid)
    vars = ['nodename', 'svcname', 'action_type', 'command', 'user_id']
    vals = [node, svc, action_type, command, str(auth.user_id)]
    generic_insert('action_queue', vars, vals)

def enqueue_svc_comp_action(node, svc, action, mode, mod, os):
    if os == "Windows":
        action_type = "pull"
    else:
        action_type = "push"
    command = fmt_svc_comp_action(node, svc, action, mode, mod, action_type)
    vars = ['nodename', 'svcname', 'action_type', 'command', 'user_id']
    vals = [node, svc, action_type, command, str(auth.user_id)]
    generic_insert('action_queue', vars, vals)

def fmt_svc_action(node, svc, action, action_type, rid=None):
    action = action.replace('"', '\"').replace("'", "\'")
    if action_type == "pull":
        cmd = []
    else:
        cmd = ssh_cmd + ['opensvc@'+node, '--']
    cmd += ['sudo', '/opt/opensvc/bin/svcmgr', '--service', svc, action]
    if rid is not None:
        cmd += ["--rid", rid]
    return ' '.join(cmd)

def fmt_node_comp_action(node, action, mode, mod, action_type):
    if action_type == "pull":
        cmd = []
    else:
        cmd = ssh_cmd + ['opensvc@'+node, '--']
    cmd += ['sudo', '/opt/opensvc/bin/nodemgr', 'compliance', action,
            '--'+mode, mod]
    return ' '.join(cmd)

def fmt_node_action(node, action, action_type):
    if action_type == "pull":
        cmd = []
    else:
        cmd = ssh_cmd + ['opensvc@'+node, '--']
    cmd += ['sudo', '/opt/opensvc/bin/nodemgr', action]
    return ' '.join(cmd)

def fmt_svc_comp_action(node, service, action, mode, mod, action_type):
    if action_type == "pull":
        cmd = []
    else:
        cmd = ssh_cmd + ['opensvc@'+node, '--']
    cmd += ['sudo', '/opt/opensvc/bin/svcmgr', '-s', service, 'compliance', action,
            '--'+mode, mod]
    return ' '.join(cmd)

@auth.requires_membership('CompExec')
def do_node_comp_action(nodename, action, mode, obj):
    if mode not in ("module", "moduleset"):
        raise ToolError("unsupported mode")
    if action not in ("check", "fix"):
        raise ToolError("unsupported action")

    q = db.nodes.nodename == nodename
    q &= db.nodes.team_responsible.belongs(user_groups())
    node = db(q).select(db.nodes.nodename, db.nodes.os_name, cacheable=True).first()

    if node is None:
        return 0

    enqueue_node_comp_action(node.nodename, action, mode, obj, node.os_name)
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
    node = db(q).select(db.nodes.nodename, db.nodes.os_name, cacheable=True).first()

    if node is None:
        return 0

    enqueue_node_action(node.nodename, action, node.os_name)
    _log('node.action', 'run %(a)s',
         dict(a=action),
         nodename=node.nodename
    )
    return 1

@auth.requires_membership('CompExec')
def do_svc_comp_action(nodename, svcname, action, mode, obj):
    if mode not in ("module", "moduleset"):
        raise ToolError("unsupported mode")
    if action not in ("check", "fix"):
        raise ToolError("unsupported action")

    # filter out services we are not responsible for
    sql = """select m.os_name
             from v_svcmon m
             join v_apps_flat a on m.svc_app=a.app
             where m.mon_svcname="%(svcname)s" and mon_nodname="%(nodename)s"
             and responsible="%(user)s"
             group by m.mon_nodname, m.mon_svcname
          """%dict(nodename=nodename,
                   svcname=svcname,
                   user=user_name())
    rows = db.executesql(sql, as_dict=True)
    if len(rows) == 0:
        return 0

    row = rows[0]
    enqueue_svc_comp_action(nodename, svcname, action, mode, obj, row['os_name'])
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

    # filter out services we are not responsible for
    sql = """select m.mon_nodname, m.mon_svcname, m.os_name
             from v_svcmon m
             join v_apps_flat a on m.svc_app=a.app
             where m.mon_svcname="%(svcname)s" and mon_nodname="%(nodename)s"
             and responsible='%(user)s'
             group by m.mon_nodname, m.mon_svcname
          """%dict(nodename=nodename,
                   svcname=svcname,
                   user=user_name())
    rows = db.executesql(sql)
    if len(rows) == 0:
        return 0

    row = rows[0]
    enqueue_svc_action(row[0], row[1], action, row[2], rid=rid)
    if rid is None:
        _log('service.action',
             'run %(a)s',
             dict(a=action),
             svcname=row[1],
             nodename=row[0]
        )
    else:
        _log('service.resource.action',
             'run %(a)s on rid %(r)s',
             dict(a=action, r=rid),
             svcname=row[1],
             nodename=row[0]
        )
    return 1

def json_action_one(d):
    if "rid" in d and "svcname" in d and "nodename" in d:
        if "action" in d:
            return do_svc_action(d["nodename"], d["svcname"], d["action"], rid=d["rid"])
    if "svcname" in d and d["svcname"] != "" and "nodename" in d:
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

@service.json
def json_action():
    data = json.loads(request.vars.data)
    n = 0 # accepted actions count
    n_raw = len(data)

    data = factorize_actions(data)
    n_factorized = len(data)

    for d in data:
        n += json_action_one(d)

    start_actiond()

    if n > 0:
        action_q_event()

    return {
      "accepted": n,
      "rejected": n_factorized-n,
      "factorized": n_raw-n_factorized,
    }

