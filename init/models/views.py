import re
import datetime

def user_name():
    if not hasattr(session.auth, 'user'):
        return 'Unknown'
    if auth_is_node():
        return 'agent'
    return ' '.join([session.auth.user.first_name,
                     session.auth.user.last_name])

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

def or_apply_filters(q, node_field=None, service_field=None, fset_id=None):
    if fset_id is None or fset_id == 0:
        if auth.user_id is None:
            if node_field is not None:
                q |= node_field.like('%')
            if service_field is not None:
                q |= service_field.like('%')
            return q
        v = db.v_gen_filtersets
        o = v.f_order
        qry = db.gen_filterset_user.fset_id == v.fset_id
        qry &= db.gen_filterset_user.user_id == auth.user_id
    else:
        qry = db.v_gen_filtersets.fset_id == fset_id

    rows = db(qry).select()
    if len(rows) == 0:
        if node_field is not None:
            q |= node_field.like("%")
        if service_field is not None:
            q |= service_field.like("%")
        return q

    nodes = set([])
    services = set([])
    for row in rows:
        nodes, services = filterset_query(row, nodes, services)

    n_nodes = len(nodes)
    n_services = len(services)

    if n_nodes > 0 and n_services > 0 and node_field is not None and service_field is not None:
        q |= (node_field.belongs(nodes)) & (service_field.belongs(services))
    elif len(nodes) > 0 and node_field is not None:
        q |= node_field.belongs(nodes)
    elif len(services) > 0 and service_field is not None:
        q |= service_field.belongs(services)

    return q

def apply_filters(q, node_field=None, service_field=None, fset_id=None, nodename=None, svcname=None):
    if fset_id is None or fset_id == 0:
        if auth.user_id is None:
            return q
        fset_id = user_fset_id()
        if fset_id is None or fset_id == 0:
            return q

    nodes, services = filterset_encap_query(fset_id, nodename=nodename, svcname=svcname)

    n_nodes = len(nodes)
    n_services = len(services)

    if n_nodes > 0 and n_services > 0 and node_field is not None and service_field is not None:
        q &= ((node_field=="")|(node_field.belongs(nodes))) & ((service_field=="")|(service_field.belongs(services)))
    elif n_nodes == 1 and node_field is not None:
        q &= node_field == list(nodes)[0]
    elif n_nodes > 0 and node_field is not None:
        q &= node_field.belongs(nodes)
    elif n_services == 1 and service_field is not None:
        q &= service_field == list(services)[0]
    elif n_services > 0 and service_field is not None:
        q &= service_field.belongs(services)
    elif n_nodes == 0 and node_field is not None:
        q &= node_field == '.'
    elif n_services == 0 and service_field is not None:
        q &= service_field == '.'

    return q

def current_fset_nodenames():
    return current_fset_objects()[0]

def current_fset_svcnames():
    return current_fset_objects()[1]

def current_fset_objects():
    """
     return the a (nodenames, svcnames) tuple of objects matching the currently
     selected user's filterset
    """
    fset_id = user_fset_id()
    return filterset_encap_query(fset_id)

def filterset_encap_query(fset_id, f_log_op='AND', nodes=set([]), services=set([]), i=0, nodename=None, svcname=None):
    if fset_id == 0:
        all_nodes = set([r.nodename for r in db(db.nodes.id>0).select(db.nodes.nodename, cacheable=True)])
        all_services = set([r.svc_name for r in db(db.services.id>0).select(db.services.svc_name, cacheable=True)])
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
            n_nodes, n_services = filterset_encap_query(r.encap_fset_id, r.f_log_op, n_nodes, n_services, i=j, nodename=nodename, svcname=svcname)
            encap_done.append(r.encap_fset_id)
        else:
            n_nodes, n_services = filterset_query(r, n_nodes, n_services, i=j, nodename=nodename, svcname=svcname)
        j += 1

    if 'NOT' in f_log_op:
        all_nodes = set([_r.nodename for _r in db(db.nodes.id>0).select(db.nodes.nodename, cacheable=True)])
        all_services = set([_r.svc_name for _r in db(db.services.id>0).select(db.services.svc_name, cacheable=True)])
        n_nodes = all_nodes - n_nodes
        n_services = all_services - n_services

    if f_log_op in ('AND', 'AND NOT'):
        if i == 0:
            nodes = n_nodes
        else:
            nodes &= n_nodes
        if i == 0:
            services = n_services
        else:
            services &= n_services
    elif f_log_op in ('OR', 'OR NOT'):
        if i == 0:
            nodes = n_nodes
        else:
            nodes |= n_nodes
        if i == 0:
            services = n_services
        else:
            services |= n_services

    return nodes, services


def filterset_query(row, nodes, services, i=0, nodename=None, svcname=None):
    if 'v_gen_filtersets' in row:
        v = row.v_gen_filtersets
    else:
        v = row

    if v.f_table is None or v.f_field is None:
        return nodes, services

    if v.f_op == '=':
        qry = db[v.f_table][v.f_field] == v.f_value
    elif v.f_op == '!=':
        qry = db[v.f_table][v.f_field] != v.f_value
    elif v.f_op == 'LIKE':
        qry = db[v.f_table][v.f_field].like(v.f_value)
    elif v.f_op == 'NOT LIKE':
        qry = ~db[v.f_table][v.f_field].like(v.f_value)
    elif v.f_op == 'IN':
        qry = db[v.f_table][v.f_field].belongs(v.f_value.split(','))
    elif v.f_op == 'NOT IN':
        qry = ~db[v.f_table][v.f_field].belongs(v.f_value.split(','))
    elif v.f_op == '>=':
        qry = db[v.f_table][v.f_field] >= v.f_value
    elif v.f_op == '>':
        qry = db[v.f_table][v.f_field] > v.f_value
    elif v.f_op == '<=':
        qry = db[v.f_table][v.f_field] <= v.f_value
    elif v.f_op == '<':
        qry = db[v.f_table][v.f_field] < v.f_value
    else:
        return nodes, services

    if "NOT" in v.f_log_op:
        qry = ~qry

    if v.f_table == 'services':
        if svcname is not None:
            qry &= db.services.svc_name == svcname
        if nodename is not None:
            qry &= db.svcmon.mon_nodname == nodename
        rows = db(qry).select(db.services.svc_name, db.svcmon.mon_nodname,
                              left=db.svcmon.on(db.services.svc_name==db.svcmon.mon_svcname),
                              cacheable=True)
        n_nodes = set(map(lambda x: x.svcmon.mon_nodname, rows)) - set([None])
        n_services = set(map(lambda x: x.services.svc_name, rows)) - set([None])
    elif v.f_table == 'nodes':
        if svcname is not None:
            qry &= db.svcmon.mon_svcname == svcname
        if nodename is not None:
            qry &= db.nodes.nodename == nodename
        rows = db(qry).select(db.svcmon.mon_svcname, db.nodes.nodename,
                              left=db.svcmon.on(db.nodes.nodename==db.svcmon.mon_nodname),
                              cacheable=True)
        n_nodes = set(map(lambda x: x.nodes.nodename, rows)) - set([None])
        n_services = set(map(lambda x: x.svcmon.mon_svcname, rows)) - set([None])
    elif v.f_table == 'packages':
        if svcname is not None:
            qry &= db.svcmon.mon_svcname == svcname
        if nodename is not None:
            qry &= db.packages.pkg_nodename == nodename
        rows = db(qry).select(db.svcmon.mon_svcname, db.packages.pkg_nodename,
                              left=db.svcmon.on(db.packages.pkg_nodename==db.svcmon.mon_nodname),
                              cacheable=True)
        n_nodes = set(map(lambda x: x.packages.pkg_nodename, rows)) - set([None])
        n_services = set(map(lambda x: x.svcmon.mon_svcname, rows)) - set([None])
    elif v.f_table == 'svcmon':
        if svcname is not None:
            qry &= db.svcmon.mon_svcname == svcname
        if nodename is not None:
            qry &= db.svcmon.mon_nodname == nodename
        rows = db(qry).select(db.svcmon.mon_nodname, db.svcmon.mon_svcname,
                              cacheable=True)
        n_nodes = set(map(lambda x: x.mon_nodname, rows)) - set([None])
        n_services = set(map(lambda x: x.mon_svcname, rows)) - set([None])
    elif v.f_table == 'b_disk_app':
        if svcname is not None:
            qry &= db.b_disk_app.disk_svcname == svcname
        if nodename is not None:
            qry &= db.b_disk_app.disk_nodename == nodename
        try:
            rows = db(qry).select(db.b_disk_app.disk_nodename,
                                  db.b_disk_app.disk_svcname,
                                  cacheable=True)
        except Exception as e:
            if "retry" in str(e):
                rows = db(qry).select(db.b_disk_app.disk_nodename,
                                      db.b_disk_app.disk_svcname,
                                      cacheable=True)
            else:
                raise

        n_nodes = set(map(lambda x: x.disk_nodename, rows)) - set([None])
        n_services = set(map(lambda x: x.disk_svcname, rows)) - set([None])
    elif v.f_table == 'node_hba':
        if svcname is not None:
            qry &= db.svcmon.mon_svcname == svcname
        if nodename is not None:
            qry &= db.node_hba.nodename == nodename
        rows = db(qry).select(db.svcmon.mon_svcname, db.node_hba.nodename,
                              left=db.svcmon.on(db.node_hba.nodename==db.svcmon.mon_nodname),
                              cacheable=True)
        n_nodes = set(map(lambda x: x.node_hba.nodename, rows)) - set([None])
        n_services = set(map(lambda x: x.svcmon.mon_svcname, rows)) - set([None])
    elif v.f_table == 'apps':
        _qry = qry
        _qry &= db.apps.app == db.services.svc_app
        if svcname is not None:
            _qry &= db.services.svc_name == svcname
        rows = db(_qry).select(db.services.svc_name,
                               cacheable=True)
        n_services = set(map(lambda x: x.svc_name, rows)) - set([None])

        _qry = qry
        _qry &= db.apps.app == db.nodes.project
        if nodename is not None:
            _qry &= db.nodes.nodename == nodename
        rows = db(_qry).select(db.nodes.nodename,
                               cacheable=True)
        n_nodes = set(map(lambda x: x.nodename, rows)) - set([None])
    elif v.f_table == 'resmon':
        if svcname is not None:
            qry &= db.resmon.svcname == svcname
        if nodename is not None:
            qry &= db.resmon.nodename == nodename
        rows = db(qry).select(db.resmon.nodename,
                              db.resmon.svcname,
                              cacheable=True)
        n_nodes = set(map(lambda x: x.nodename, rows)) - set([None])
        n_services = set(map(lambda x: x.svcname, rows)) - set([None])
    elif v.f_table == 'v_tags':
        if svcname is not None:
            qry &= db.v_tags.svcname == svcname
        if nodename is not None:
            qry &= db.v_tags.nodename == nodename
        rows = db(qry).select(db.v_tags.nodename,
                              db.v_tags.svcname,
                              cacheable=True)
        n_nodes = set(map(lambda x: x.nodename, rows)) - set([None])
        n_services = set(map(lambda x: x.svcname, rows)) - set([None])
    elif v.f_table == 'v_comp_moduleset_attachments':
        if svcname is not None:
            qry &= db.v_comp_moduleset_attachments.svcname == svcname
        if nodename is not None:
            qry &= db.v_comp_moduleset_attachments.nodename == nodename
        rows = db(qry).select(db.v_comp_moduleset_attachments.nodename,
                              db.v_comp_moduleset_attachments.svcname,
                              cacheable=True)
        n_nodes = set(map(lambda x: x.nodename, rows)) - set([None])
        n_services = set(map(lambda x: x.svcname, rows)) - set([None])
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
    'dashboard': (db.svcmon.mon_svcname == db.dashboard.dash_svcname) & \
                 (db.svcmon.mon_nodname == db.dashboard.dash_nodename),
    'v_svcmon': None,
    'checks_live': (db.svcmon.mon_svcname == db.checks_live.chk_svcname) & \
                   (db.svcmon.mon_nodname == db.checks_live.chk_nodename),
    'comp_log': (db.svcmon.mon_svcname == db.comp_log.run_svcname) & \
                (db.svcmon.mon_nodname == db.comp_log.run_nodename),
    'comp_status': (db.svcmon.mon_svcname == db.comp_status.run_svcname) & \
                   (db.svcmon.mon_nodname == db.comp_status.run_nodename),
    'svcmon_log': (db.svcmon.mon_svcname == db.svcmon_log.mon_svcname) & \
                  (db.svcmon.mon_nodname == db.svcmon_log.mon_nodname),
    'services_log': db.svcmon.mon_svcname == db.services_log.svc_name,
    'svcmon_log': (db.svcmon.mon_svcname == db.svcmon_log.mon_svcname) & \
                  (db.svcmon.mon_nodname == db.svcmon_log.mon_nodname),
  },
  'services':{
    'services': None,
    'dashboard': db.services.svc_name == db.dashboard.dash_svcname,
    'v_svcmon': None,
    'checks_live': db.services.svc_name == db.checks_live.chk_svcname,
    'appinfo': db.services.svc_name == db.appinfo.app_svcname,
    'comp_log': db.services.svc_name == db.comp_log.run_svcname,
    'comp_status': db.services.svc_name == db.comp_status.run_svcname,
    'svcmon_log': db.services.svc_name == db.svcmon_log.mon_svcname,
    'services_log': db.services.svc_name == db.services_log.svc_name,
    'v_apps': db.services.svc_app == db.apps.app,
  },
  'nodes':{
    'nodes': None,
    'dashboard': db.nodes.nodename == db.dashboard.dash_nodename,
    'dashboard': db.nodes.nodename == db.dashboard.dash_nodename,
    'v_svcmon': None,
    'v_svcactions': None,
    'checks_live': db.nodes.nodename == db.checks_live.chk_nodename,
    'packages': db.nodes.nodename == db.packages.pkg_nodename,
    'patches': db.nodes.nodename == db.patches.patch_nodename,
    'comp_rulesets_nodes': db.nodes.nodename == db.comp_rulesets_nodes.nodename,
    'v_comp_nodes': None,
    'comp_log': db.nodes.nodename == db.comp_log.run_nodename,
    'comp_status': db.nodes.nodename == db.comp_status.run_nodename,
    'svcmon_log': db.nodes.nodename == db.svcmon_log.mon_nodname,
    'services_log': (db.svcmon.mon_svcname == db.services_log.svc_name) & (db.svcmon.mon_nodname == db.nodes.nodename),
    'v_apps': (db.nodes.team_responsible == db.auth_group.role) & \
              (db.auth_group.id == db.apps_responsibles.group_id) & \
              (db.apps_responsibles.app_id) & (db.apps.id),
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
    q = db.gen_filtersets.id > 0
    fset_ids = [r.id for r in db(q).select(db.gen_filtersets.id)]

    sql = "truncate fset_cache"
    db.executesql(sql)

    _refresh_fset_cache(0)
    for fset_id in fset_ids:
        _refresh_fset_cache(fset_id)

    db.commit()

def _refresh_fset_cache(fset_id):
    print "refresh fset_id", fset_id
    nodenames, svcnames = filterset_encap_query(fset_id)

    sql = "delete from fset_cache where fset_id=%d"%fset_id
    db.executesql(sql)

    if len(nodenames)+len(svcnames) == 0:
        return

    sql = "insert into fset_cache values "
    for nodename in nodenames:
        sql += """(%(fset_id)d, "nodename", "%(nodename)s"),"""%dict(
          fset_id=fset_id,
          nodename=nodename,
        )
    for svcname in svcnames:
        sql += """(%(fset_id)d, "svcname", "%(svcname)s"),"""%dict(
          fset_id=fset_id,
          svcname=svcname,
        )
    sql = sql.rstrip(",")
    try:
        db.executesql(sql)
    except Exception as e:
        print sql
        print e
        raise

def filterset_encap_query_cached(fset_id):
    sql = """select name from fset_cache where fset_id=%d and objtype="nodename" """%fset_id
    rows = db.executesql(sql)
    nodenames = [r[0] for r in rows]
    sql = """select name from fset_cache where fset_id=%d and objtype="svcname" """%fset_id
    rows = db.executesql(sql)
    svcnames = [r[0] for r in rows]
    return nodenames, svcnames



