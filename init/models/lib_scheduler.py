import os

def get_new_node_id():
    import uuid
    while True:
        u = str(uuid.uuid4())
        q = db.nodes.node_id == u
        if db(q).count() == 0:
            return u

def get_new_svc_id():
    import uuid
    while True:
        u = str(uuid.uuid4())
        q = db.services.svc_id == u
        if db(q).count() == 0:
            return u

def get_preferred_app(node_id, svc_id):
    if svc_id is None:
        q = db.nodes.node_id == node_id
        q &= db.apps.app == db.nodes.app
        return db(q).select(db.apps.ALL).first()
    else:
        q = db.services.svc_id == svc_id
        q &= db.services.svc_app == db.apps.app
        row = db(q).select(db.apps.ALL).first()
        if row is None:
            q = db.nodes.node_id == node_id
            q &= db.apps.app == db.nodes.app
            return db(q).select(db.apps.ALL).first()
        return row

def add_app_id_in_data(vars, vals, app_key="app_id", node_key="node_id", svc_key="svc_id"):
    if len(vals) == 0:
        return vars, vals
    if node_key not in vars and svc_key not in vars:
        return vars, vals

    if type(vals[0]) != list:
        vals = [vals]
        single = True
    else:
        single = False

    if node_key in vars:
        node_idx = vars.index(node_key)
        node_id = vals[0][node_idx]
    else:
        node_id = None
        node_idx = None

    if svc_key in vars:
        svc_idx = vars.index(svc_key)
        svc_id = vals[0][svc_idx]
    else:
        svc_id = None
        svc_idx = None

    if app_key not in vars:
        vars.append(app_key)

    app_idx = vars.index(app_key)
    app_id = get_preferred_app(node_id, svc_id).id

    for i, _vals in enumerate(vals):
        if svc_idx:
            _svc_id = _vals[svc_idx]
        else:
            _svc_id = None
        if node_idx:
            _node_id = _vals[node_idx]
        else:
            _node_id = None

        if _svc_id != svc_id or _node_id != node_id:
            app_id = get_preferred_app(node_id, svc_id).id
            svc_id = _svc_id
            node_id = _node_id

        try:
            vals[i][app_idx] = app_id
        except IndexError:
            vals[i].append(app_id)

    if single:
        return vars, vals[0]
    else:
        return vars, vals

def replace_nodename_in_data(vars, vals, auth, fieldname="nodename"):
    if len(vals) == 0:
        return vars, vals
    node_id = auth_to_node_id(auth)
    if node_id is None:
        return
    try:
        idx = vars.index(fieldname)
        del(vars[idx])
        if type(vals[0]) != list:
            del(vals[idx])
        else:
            for i, l in enumerate(vals):
                del(vals[i][idx])
    except:
        pass
    if "node_id" not in vars:
        vars.append("node_id")
        if type(vals[0]) != list:
            vals.append(node_id)
        else:
            for i, l in enumerate(vals):
                vals[i].append(node_id)
    return vars, vals

def replace_svcname_in_data(vars, vals, auth, fieldname="svcname"):
    if len(vals) == 0:
        return vars, vals
    try:
        idx = vars.index(fieldname)
        del(vars[idx])
        if type(vals[0]) != list:
            svcname = vals[idx]
            del(vals[idx])
        else:
            svcname = vals[0][idx]
            for i, l in enumerate(vals):
                del(vals[i][idx])
    except Exception as e:
        return vars, vals
    node_id = auth_to_node_id(auth)
    svc_id = node_svc_id(node_id, svcname)
    if svc_id is None:
        return
    if "svc_id" not in vars:
        vars.append("svc_id")
        if type(vals[0]) != list:
            vals.append(svc_id)
        else:
            for i, l in enumerate(vals):
                vals[i].append(svc_id)
    return vars, vals

def replace_svcnames_in_data(vars, vals, auth, fieldname="svcname"):
    if len(vals) == 0:
        return vars, vals
    h = {}
    svcnames = []
    try:
        idx = vars.index(fieldname)
        del(vars[idx])
        if type(vals[0]) != list:
            svcnames.append(vals[idx])
            del(vals[idx])
        else:
            for i, l in enumerate(vals):
                svcnames.append(vals[i][idx])
                del(vals[i][idx])
    except:
        pass
    node_id = auth_to_node_id(auth)
    for i, svcname in enumerate(svcnames):
        if svcname in h:
            continue
        h[svcname] = node_svc_id(node_id, svcname)
    if "svc_id" not in vars:
        vars.append("svc_id")
        if type(vals[0]) != list:
            vals.append(h[svcnames[0]])
        else:
            for i, l in enumerate(vals):
                vals[i].append(h[svcnames[i]])
    return vars, vals

def is_exe(fpath):
    """Returns True if file path is executable, False otherwize
    does not follow symlink
    """
    return os.path.exists(fpath) and os.access(fpath, os.X_OK)

def which(program):
    def ext_candidates(fpath):
        yield fpath
        for ext in os.environ.get("PATHEXT", "").split(os.pathsep):
            yield fpath + ext

    fpath, fname = os.path.split(program)
    if fpath:
        if os.path.isfile(program) and is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            for candidate in ext_candidates(exe_file):
                if is_exe(candidate):
                    return candidate

    return None

def check_or_fix_node_cluster_id(node_id, expected_cluster_id):
    """
    check or fix unexpected node cluster id value, it may be outdated after daemon join new cluster.
    Outdated node cluster_id values may lead to unexpected services creation during next node_svc_id call.
    :return: True when outdated node cluster id value has been fixed
    """
    if node_id and expected_cluster_id:
        row = db(db.nodes.node_id == node_id).select(db.nodes.cluster_id).first()
        if row and row.cluster_id != expected_cluster_id:
            db(db.nodes.node_id == node_id).update(cluster_id=expected_cluster_id)
            db.commit()
            return True
    return False
