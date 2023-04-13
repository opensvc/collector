import re
import datetime

def user_name(email=False):
    if session.auth is not None:
        _auth = session.auth
    else:
        _auth = auth
    if not hasattr(_auth, 'user'):
        return 'Unknown'
    if auth_is_node():
        return 'agent'
    if auth.user is None:
        return 'Unknown'
    first_name = _auth.user.first_name if _auth.user.first_name else ""
    last_name = _auth.user.last_name if _auth.user.last_name else ""
    user = ' '.join([first_name, last_name])
    if email:
        user += " <%s>" % _auth.user.email
    try:
        user = user.decode("utf8")
    except:
        pass
    return user

def delta_to_date(s):
    if len(s) == 0:
        return s

    regex = re.compile(r"[-]{0,1}([0-9]+w){0,1}([0-9]+d){0,1}([0-9]+h){0,1}([0-9]+m){0,1}([0-9]+s){0,1}")
    _s = regex.match(s)
    if _s is None:
        return s
    if len(_s.group(0)) == 0:
        return s

    argv = {}

    regex = re.compile(r"[0-9]+w")
    _s = regex.search(s)
    if _s is not None:
        argv["weeks"] = int(_s.group(0)[:-1])

    regex = re.compile(r"[0-9]+d")
    _s = regex.search(s)
    if _s is not None:
        argv["days"] = int(_s.group(0)[:-1])

    regex = re.compile(r"[0-9]+h")
    _s = regex.search(s)
    if _s is not None:
        argv["hours"] = int(_s.group(0)[:-1])

    regex = re.compile(r"[0-9]+m")
    _s = regex.search(s)
    if _s is not None:
        argv["minutes"] = int(_s.group(0)[:-1])

    regex = re.compile(r"[0-9]+s")
    _s = regex.search(s)
    if _s is not None:
        argv["seconds"] = int(_s.group(0)[:-1])

    d = datetime.timedelta(**argv)
    now = datetime.datetime.now()

    if s[0] == '-':
        r = now - d
    else:
        r = now + d

    return str(r)


def domainname(fqdn):
    if fqdn is None or fqdn == "":
        return
    l = fqdn.split('.')
    if len(l) < 2:
        return
    l[0] = ""
    return '.'.join(l)

def user_fset_id():
    q = db.gen_filterset_user.user_id == auth.user_id
    row = db(q).select(db.gen_filterset_user.fset_id).first()
    if row is None:
        return 0
    return row.fset_id

def user_fset_name():
    q = db.gen_filterset_user.user_id == auth.user_id
    q &= db.gen_filterset_user.fset_id == db.gen_filtersets.id
    row = db(q).select(db.gen_filtersets.fset_name).first()
    if row is None:
        return 0
    return row.gen_filtersets.fset_name

def apply_filters_id(q, node_field=None, svc_field=None, fset_id=None,
                     node_ids=None, svc_ids=None):
    if fset_id is None or fset_id == 0:
        if auth.user_id is None:
            return q
        fset_id = user_fset_id()
        if fset_id is None or fset_id == 0:
            return q

    node_ids, svc_ids = filterset_encap_query_id(fset_id, node_ids=node_ids, svc_ids=svc_ids)

    n_nodes = len(node_ids)
    n_services = len(svc_ids)

    if n_nodes > 0 and n_services > 0 and node_field is not None and svc_field is not None:
        q &= ((node_field=="")|(node_field.belongs(node_ids))) & ((svc_field=="")|(svc_field.belongs(svc_ids)))
    elif n_nodes == 1 and node_field is not None:
        q &= node_field == list(node_ids)[0]
    elif n_nodes > 0 and node_field is not None:
        q &= node_field.belongs(node_ids)
    elif n_services == 1 and svc_field is not None:
        q &= svc_field == list(svc_ids)[0]
    elif n_services > 0 and svc_field is not None:
        q &= svc_field.belongs(svc_ids)
    elif n_nodes == 0 and node_field is not None:
        q &= node_field == None
    elif n_services == 0 and svc_field is not None:
        q &= svc_field == None

    return q

def current_fset_node_ids():
    return current_fset_objects()[0]

def current_fset_svc_ids():
    return current_fset_objects()[1]

def current_fset_objects():
    """
     return the a (node_ids, svc_ids) tuple of objects matching the currently
     selected user's filterset
    """
    fset_id = user_fset_id()
    return filterset_encap_query_id(fset_id)

def filterset_encap_query_id(fset_id, f_log_op='AND', node_ids=set([]), svc_ids=set([]), i=0, node_id=None, svc_id=None):
    if fset_id == 0:
        all_nodes = set([r.node_id for r in db(db.nodes.id>0).select(db.nodes.node_id, cacheable=True)])
        all_services = set([r.svc_id for r in db(db.services.id>0).select(db.services.svc_id, cacheable=True)])
        return all_nodes, all_services

    o = db.v_gen_filtersets.f_order
    qr = db.v_gen_filtersets.fset_id == fset_id
    rows = db(qr).select(orderby=o, cacheable=True)
    n_nodes = set([])
    n_services = set([])
    j = 0
    encap_done = []

    for r in rows:
        if r.encap_fset_id > 0 and r.encap_fset_id not in encap_done:
            n_nodes, n_services = filterset_encap_query_id(r.encap_fset_id, r.f_log_op, n_nodes, n_services, i=j, node_id=node_id, svc_id=svc_id)
            encap_done.append(r.encap_fset_id)
        else:
            n_nodes, n_services = filterset_query_id(r, n_nodes, n_services, i=j, node_id=node_id, svc_id=svc_id)
        j += 1

    if 'NOT' in f_log_op:
        all_nodes = set([_r.node_id for _r in db(db.nodes.id>0).select(db.nodes.node_id, cacheable=True)])
        all_services = set([_r.svc_id for _r in db(db.services.id>0).select(db.services.svc_id, cacheable=True)])
        n_nodes = all_nodes - n_nodes
        n_services = all_services - n_services

    if f_log_op in ('AND', 'AND NOT'):
        if i == 0:
            node_ids = n_nodes
        else:
            node_ids &= n_nodes
        if i == 0:
            svc_ids = n_services
        else:
            svc_ids &= n_services
    elif f_log_op in ('OR', 'OR NOT'):
        if i == 0:
            node_ids = n_nodes
        else:
            node_ids |= n_nodes
        if i == 0:
            svc_ids = n_services
        else:
            svc_ids |= n_services

    return node_ids, svc_ids

def filterset_query_id(row, nodes, services, i=0, node_id=None, svc_id=None):
    if 'v_gen_filtersets' in row:
        v = row.v_gen_filtersets
    else:
        v = row

    if v.f_table is None or v.f_field is None:
        return nodes, services

    try:
        field = db[v.f_table][v.f_field]
    except:
        return nodes, services

    if v.f_op == '=':
        if v.f_value.startswith("$."):
            qry = where_json_chunk(v.f_table, v.f_field, v.f_value, db)
        else:
            qry = field == v.f_value
    elif v.f_op == '!=':
        qry = field != v.f_value
    elif v.f_op == 'LIKE':
        qry = field.like(v.f_value)
    elif v.f_op == 'NOT LIKE':
        qry = ~field.like(v.f_value)
    elif v.f_op == 'IN':
        qry = field.belongs(v.f_value.split(','))
    elif v.f_op == 'NOT IN':
        qry = ~field.belongs(v.f_value.split(','))
    elif v.f_op == '>=':
        qry = field >= v.f_value
    elif v.f_op == '>':
        qry = field > v.f_value
    elif v.f_op == '<=':
        qry = field <= v.f_value
    elif v.f_op == '<':
        qry = field < v.f_value
    else:
        return nodes, services

    if "NOT" in v.f_log_op:
        qry = ~qry

    if v.f_table == 'services':
        if svc_id is not None:
            qry &= db.services.svc_id == svc_id
        if node_id is not None:
            qry &= db.svcmon.node_id == node_id
        rows = db(qry).select(db.services.svc_id, db.svcmon.node_id,
                              left=db.svcmon.on(db.services.svc_id==db.svcmon.svc_id),
                              cacheable=True)
        n_nodes = set(map(lambda x: x.svcmon.node_id, rows)) - set([None])
        n_services = set(map(lambda x: x.services.svc_id, rows)) - set([None])
    elif v.f_table == 'nodes':
        if svc_id is not None:
            qry &= db.svcmon.svc_id == svc_id
        if node_id is not None:
            qry &= db.nodes.node_id == node_id
        rows = db(qry).select(db.svcmon.svc_id, db.nodes.node_id,
                              left=db.svcmon.on(db.nodes.node_id==db.svcmon.node_id),
                              cacheable=True)
        n_nodes = set(map(lambda x: x.nodes.node_id, rows)) - set([None])
        n_services = set(map(lambda x: x.svcmon.svc_id, rows)) - set([None])
    elif v.f_table == 'node_ip':
        if svc_id is not None:
            qry &= db.svcmon.svc_id == svc_id
        if node_id is not None:
            qry &= db.node_ip.node_id == node_id
        rows = db(qry).select(db.svcmon.svc_id, db.node_ip.node_id,
                              left=db.svcmon.on(db.node_ip.node_id==db.svcmon.node_id),
                              cacheable=True)
        n_nodes = set(map(lambda x: x.node_ip.node_id, rows)) - set([None])
        n_services = set(map(lambda x: x.svcmon.svc_id, rows)) - set([None])
    elif v.f_table == 'packages':
        if svc_id is not None:
            qry &= db.svcmon.svc_id == svc_id
        if node_id is not None:
            qry &= db.packages.node_id == node_id
        rows = db(qry).select(db.svcmon.svc_id, db.packages.node_id,
                              left=db.svcmon.on(db.packages.node_id==db.svcmon.node_id),
                              cacheable=True)
        n_nodes = set(map(lambda x: x.packages.node_id, rows)) - set([None])
        n_services = set(map(lambda x: x.svcmon.svc_id, rows)) - set([None])
    elif v.f_table == 'svcmon':
        if svc_id is not None:
            qry &= db.svcmon.svc_id == svc_id
        if node_id is not None:
            qry &= db.svcmon.node_id == node_id
        rows = db(qry).select(db.svcmon.node_id, db.svcmon.svc_id,
                              cacheable=True)
        n_nodes = set(map(lambda x: x.node_id, rows)) - set([None])
        n_services = set(map(lambda x: x.svc_id, rows)) - set([None])
    elif v.f_table == 'diskinfo':
        if svc_id is not None:
            qry &= db.svcdisks.svc_id == svc_id
        if node_id is not None:
            qry &= db.svcdisks.node_id == node_id
        qry &= db.svcdisks.disk_id == db.diskinfo.disk_id
        rows = db(qry).select(db.svcdisks.node_id,
                              db.svcdisks.svc_id,
                              cacheable=True)
        n_nodes = set(map(lambda x: x.node_id, rows)) - set([None])
        n_services = set(map(lambda x: x.svc_id, rows)) - set([None])
    elif v.f_table == 'svcdisks':
        if svc_id is not None:
            qry &= db.svcdisks.svc_id == svc_id
        if node_id is not None:
            qry &= db.svcdisks.node_id == node_id
        rows = db(qry).select(db.svcdisks.node_id,
                              db.svcdisks.svc_id,
                              cacheable=True)
        n_nodes = set(map(lambda x: x.node_id, rows)) - set([None])
        n_services = set(map(lambda x: x.svc_id, rows)) - set([None])
    elif v.f_table == 'node_hba':
        if svc_id is not None:
            qry &= db.svcmon.svc_id == svc_id
        if node_id is not None:
            qry &= db.node_hba.node_id == node_id
        rows = db(qry).select(db.svcmon.svc_id, db.node_hba.node_id,
                              left=db.svcmon.on(db.node_hba.node_id==db.svcmon.node_id),
                              cacheable=True)
        n_nodes = set(map(lambda x: x.node_hba.node_id, rows)) - set([None])
        n_services = set(map(lambda x: x.svcmon.svc_id, rows)) - set([None])
    elif v.f_table == 'apps':
        _qry = qry
        _qry &= db.apps.app == db.services.svc_app
        if svc_id is not None:
            _qry &= db.services.svc_id == svc_id
        rows = db(_qry).select(db.services.svc_id,
                               cacheable=True)
        n_services = set(map(lambda x: x.svc_id, rows)) - set([None])

        _qry = qry
        _qry &= db.apps.app == db.nodes.app
        if node_id is not None:
            _qry &= db.nodes.node_id == node_id
        rows = db(_qry).select(db.nodes.node_id,
                               cacheable=True)
        n_nodes = set(map(lambda x: x.node_id, rows)) - set([None])
    elif v.f_table == 'resmon':
        if svc_id is not None:
            qry &= db.resmon.svc_id == svc_id
        if node_id is not None:
            qry &= db.resmon.node_id == node_id
        rows = db(qry).select(db.resmon.node_id,
                              db.resmon.svc_id,
                              cacheable=True)
        n_nodes = set(map(lambda x: x.node_id, rows)) - set([None])
        n_services = set(map(lambda x: x.svc_id, rows)) - set([None])
    elif v.f_table == 'v_tags':
        if svc_id is not None:
            qry &= db.v_tags.svc_id == svc_id
        if node_id is not None:
            qry &= db.v_tags.node_id == node_id
        rows = db(qry).select(db.v_tags.node_id,
                              db.v_tags.svc_id,
                              cacheable=True)
        n_nodes = set(map(lambda x: x.node_id, rows)) - set([None])
        n_services = set(map(lambda x: x.svc_id, rows)) - set([None])
    elif v.f_table == 'v_comp_moduleset_attachments':
        if svc_id is not None:
            qry &= db.v_comp_moduleset_attachments.svc_id == svc_id
        if node_id is not None:
            qry &= db.v_comp_moduleset_attachments.node_id == node_id
        rows = db(qry).select(db.v_comp_moduleset_attachments.node_id,
                              db.v_comp_moduleset_attachments.svc_id,
                              cacheable=True)
        n_nodes = set(map(lambda x: x.node_id, rows)) - set([None])
        n_services = set(map(lambda x: x.svc_id, rows)) - set([None])
    else:
        raise Exception(str(v))

    if 'AND' in v.f_log_op:
        if i == 0:
            nodes = n_nodes
        else:
            nodes &= n_nodes
        if i == 0:
            services = n_services
        else:
            services &= n_services
    elif 'OR' in v.f_log_op:
        if i == 0:
            nodes = n_nodes
        else:
            nodes |= n_nodes
        if i == 0:
            services = n_services
        else:
            services |= n_services

    return nodes, services

def apply_gen_filters(q, tables=[]):
    v = db.v_gen_filtersets
    o = v.f_order
    qry = db.gen_filterset_user.fset_id == v.fset_id
    qry &= db.gen_filterset_user.user_id == auth.user_id
    rows = db(qry).select()
    for row in rows:
        q = gen_filterset_query(q, row, tables)
    return q

joins = {
  'svcmon':{
    'svcmon': None,
    'dashboard': (db.svcmon.svc_id == db.dashboard.svc_id) & \
                 (db.svcmon.node_id == db.dashboard.node_id),
    'v_svcmon': None,
    'checks_live': (db.svcmon.svc_id == db.checks_live.svc_id) & \
                   (db.svcmon.node_id == db.checks_live.node_id),
    'comp_log': (db.svcmon.svc_id == db.comp_log.svc_id) & \
                (db.svcmon.node_id == db.comp_log.node_id),
    'comp_status': (db.svcmon.svc_id == db.comp_status.svc_id) & \
                   (db.svcmon.node_id == db.comp_status.node_id),
    'svcmon_log': (db.svcmon.svc_id == db.svcmon_log.svc_id) & \
                  (db.svcmon.node_id == db.svcmon_log.node_id),
    'v_svcmon_log': (db.svcmon.svc_id == db.v_svcmon_log.svc_id) & \
                  (db.svcmon.node_id == db.v_svcmon_log.node_id),
    'services_log': db.svcmon.svc_id == db.services_log.svc_id,
    'v_services_log': db.svcmon.svc_id == db.v_services_log.svc_id,
    'resmon_log': (db.svcmon.svc_id == db.resmon_log.svc_id) & \
                  (db.svcmon.node_id == db.resmon_log.node_id),
    'v_resmon_log': (db.svcmon.svc_id == db.v_resmon_log.svc_id) & \
                  (db.svcmon.node_id == db.v_resmon_log.node_id),
    'resinfo': (db.resinfo.svc_id == db.svcmon.svc_id) & (db.resinfo.node_id == db.svcmon.node_id),
  },
  'services':{
    'services': None,
    'dashboard': db.services.svc_id == db.dashboard.svc_id,
    'v_svcmon': None,
    'v_comp_services': None,
    'checks_live': db.services.svc_id == db.checks_live.svc_id,
    'resinfo': db.services.svc_id == db.resinfo.svc_id,
    'comp_log': db.services.svc_id == db.comp_log.svc_id,
    'comp_status': db.services.svc_id == db.comp_status.svc_id,
    'resmon_log': db.services.svc_id == db.resmon_log.svc_id,
    'v_resmon_log': db.services.svc_id == db.v_resmon_log.svc_id,
    'svcmon_log': db.services.svc_id == db.svcmon_log.svc_id,
    'v_svcmon_log': db.services.svc_id == db.v_svcmon_log.svc_id,
    'services_log': db.services.svc_id == db.services_log.svc_id,
    'v_services_log': db.services.svc_id == db.v_services_log.svc_id,
    'v_apps': db.services.svc_app == db.apps.app,
    'v_tags': db.v_tags.svc_id == db.services.svc_id,
  },
  'nodes':{
    'nodes': None,
    'clusters': db.nodes.cluster_id == db.clusters.cluster_id,
    'dashboard': db.nodes.node_id == db.dashboard.node_id,
    'v_svcmon': None,
    'v_svcactions': None,
    'checks_live': db.nodes.node_id == db.checks_live.node_id,
    'node_ip': db.nodes.node_id == db.node_ip.node_id,
    'resinfo': db.nodes.node_id == db.resinfo.node_id,
    'packages': db.nodes.node_id == db.packages.node_id,
    'patches': db.nodes.node_id == db.patches.node_id,
    'comp_rulesets_nodes': db.nodes.node_id == db.comp_rulesets_nodes.node_id,
    'v_comp_nodes': None,
    'comp_log': db.nodes.node_id == db.comp_log.node_id,
    'comp_status': db.nodes.node_id == db.comp_status.node_id,
    'resmon_log': db.nodes.node_id == db.resmon_log.node_id,
    'v_resmon_log': db.nodes.node_id == db.v_resmon_log.node_id,
    'svcmon_log': db.nodes.node_id == db.svcmon_log.node_id,
    'v_svcmon_log': db.nodes.node_id == db.v_svcmon_log.node_id,
    'services_log': (db.svcmon.svc_id == db.services_log.svc_id) & (db.svcmon.node_id == db.nodes.node_id),
    'v_services_log': (db.svcmon.svc_id == db.v_services_log.svc_id) & (db.svcmon.node_id == db.nodes.node_id),
    'v_apps': db.nodes.app == db.v_apps.app,
    'v_tags': db.v_tags.node_id == db.nodes.node_id,
  },
  'resinfo': {
    'resinfo': None,
    'svcmon': (db.resinfo.svc_id == db.svcmon.svc_id) & (db.resinfo.node_id == db.svcmon.node_id),
    'nodes': db.resinfo.node_id == db.nodes.node_id,
    'services': db.resinfo.svc_id == db.services.svc_id,
  },
}

def gen_filterset_query(q, row, tables=[]):
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
            qry = gen_filterset_query(qry, r, tables)
    elif v.f_table is None or v.f_field is None:
        return q
    else:
        f_table = v.f_table
        if v.f_table not in tables:
            joined = False
            for t in tables:
                if t is None:
                    continue
                try:
                    j = joins[v.f_table][t]
                    if j is None:
                        # for views, where the fields of v.f_table are
                        # available through t
                        f_table = t
                    else:
                        if q is None:
                            q = j
                        else:
                            q &= j
                        tables.add(v.f_table)
                    joined = True
                    break
                except KeyError:
                    continue
            if not joined:
                # can not apply filter
                return q
        if v.f_op == '=':
            if v.f_value.startswith("$."):
                qry = where_json_chunk(f_table, v.f_field, v.f_value, db)
            else:
                qry = db[f_table][v.f_field] == v.f_value
        elif v.f_op == '!=':
            qry = db[f_table][v.f_field] != v.f_value
        elif v.f_op == 'LIKE':
            qry = db[f_table][v.f_field].like(v.f_value)
        elif v.f_op == 'NOT LIKE':
            qry = ~db[f_table][v.f_field].like(v.f_value)
        elif v.f_op == 'IN':
            qry = db[f_table][v.f_field].belongs(v.f_value.split(','))
        elif v.f_op == 'NOT IN':
            qry = ~db[f_table][v.f_field].belongs(v.f_value.split(','))
        elif v.f_op == '>=':
            qry = db[f_table][v.f_field] >= v.f_value
        elif v.f_op == '>':
            qry = db[f_table][v.f_field] > v.f_value
        elif v.f_op == '<=':
            qry = db[f_table][v.f_field] <= v.f_value
        elif v.f_op == '<':
            qry = db[f_table][v.f_field] < v.f_value
        else:
            return q
    if qry is None:
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

def refresh_fset_cache():
    q = db.gen_filtersets.fset_stats == True
    fset_ids = [r.id for r in db(q).select(db.gen_filtersets.id)]

    sql = "truncate fset_cache"
    db.executesql(sql)

    _refresh_fset_cache(0)
    for fset_id in fset_ids:
        _refresh_fset_cache(fset_id)

    db.commit()

def _refresh_fset_cache(fset_id):
    print "refresh fset_id", fset_id
    node_ids, svc_ids = filterset_encap_query_id(fset_id)

    sql = "delete from fset_cache where fset_id=%d"%fset_id
    db.executesql(sql)

    if len(node_ids)+len(svc_ids) == 0:
        return

    sql = "insert into fset_cache values "
    for node_id in node_ids:
        sql += """(%(fset_id)d, "node_id", "%(node_id)s"),"""%dict(
          fset_id=fset_id,
          node_id=node_id,
        )
    for svc_id in svc_ids:
        sql += """(%(fset_id)d, "svc_id", "%(svc_id)s"),"""%dict(
          fset_id=fset_id,
          svc_id=svc_id,
        )
    sql = sql.rstrip(",")
    try:
        db.executesql(sql)
    except Exception as e:
        print sql
        print e
        raise

def filterset_encap_query_cached(fset_id):
    sql = """select obj_id from fset_cache where fset_id=%d and obj_type="node_id" """%fset_id
    rows = db.executesql(sql)
    node_ids = [str(r[0]) for r in rows]
    sql = """select obj_id from fset_cache where fset_id=%d and obj_type="svc_id" """%fset_id
    rows = db.executesql(sql)
    svc_ids = [str(r[0]) for r in rows]
    return node_ids, svc_ids



