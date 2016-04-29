import re
import datetime

def apply_filters_id(q, node_field=None, svc_field=None, fset_id=None,
                     node_ids=None, svc_ids=None):
    if fset_id is None or fset_id == 0:
        return q

    node_ids, svc_ids = filterset_encap_query_id(fset_id, node_ids=node_ids, svc_ids=svc_ids)

    n_nodes = len(node_ids)
    n_services = len(svc_ids)

    if n_nodes > 0 and n_services > 0 and node_field is not None and svc_field is not None:
        q &= ((node_field==None)|(node_field.belongs(node_ids))) & ((svc_field==None)|(svc_field.belongs(svc_ids)))
    elif n_nodes == 1 and node_field is not None:
        q &= node_field == list(node_ids)[0]
    elif n_nodes > 0 and node_field is not None:
        q &= node_field.belongs(node_ids)
    elif n_services == 1 and svc_field is not None:
        q &= svc_field == list(svc_ids)[0]
    elif n_services > 0 and svc_field is not None:
        q &= svc_field.belongs(svc_ids)
    elif n_nodes == 0 and node_field is not None:
        q &= node_field < 0
    elif n_services == 0 and svc_field is not None:
        q &= svc_field < 0

    return q

def filterset_encap_query_id(fset_id, f_log_op='AND', node_ids=set([]), svc_ids=set([]), i=0, node_id=None, svc_id=None):
    if fset_id == 0:
        all_nodes = set([r.node_id for r in db(db.nodes.id>0).select(db.nodes.node_id, cacheable=True)])
        all_services = set([r.id for r in db(db.services.id>0).select(db.services.id, cacheable=True)])
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
        all_services = set([_r.id for _r in db(db.services.id>0).select(db.services.id, cacheable=True)])
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


def filterset_query_id(row, nodes, services, i=0, node_id=None, svc_id=None):
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
        if svc_id is not None:
            qry &= db.services.id == svc_id
        if node_id is not None:
            qry &= db.svcmon.node_id == node_id
        rows = db(qry).select(db.services.id, db.svcmon.node_id,
                              left=db.svcmon.on(db.services.id==db.svcmon.svc_id),
                              cacheable=True)
        n_nodes = set(map(lambda x: x.svcmon.node_id, rows)) - set([None])
        n_services = set(map(lambda x: x.services.id, rows)) - set([None])
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
    elif v.f_table == 'diskinfo':
        qry = db.diskinfo.disk_id==db.svcdisks.disk_id
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
        if svcname is not None:
            qry &= db.svcmon.svc_id == svc_id
        if nodename is not None:
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
            _qry &= db.services.id == svc_id
        rows = db(_qry).select(db.services.id,
                               cacheable=True)
        n_services = set(map(lambda x: x.id, rows)) - set([None])

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
            qry &= db.svcmon.node_id == db.nodes.node_id
            qry &= db.nodes.nodename == nodename
        rows = db(qry).select(db.services.svc_name, db.nodes.nodename,
                              left=db.svcmon.on(db.services.svc_name==db.svcmon.mon_svcname),
                              cacheable=True)
        n_nodes = set(map(lambda x: x.nodes.nodename, rows)) - set([None])
        n_services = set(map(lambda x: x.services.svc_name, rows)) - set([None])
    elif v.f_table == 'nodes':
        if svcname is not None:
            qry &= db.svcmon.mon_svcname == svcname
        if nodename is not None:
            qry &= db.nodes.nodename == nodename
        rows = db(qry).select(db.svcmon.mon_svcname, db.nodes.nodename,
                              left=db.svcmon.on(db.nodes.node_id==db.svcmon.node_id),
                              cacheable=True)
        n_nodes = set(map(lambda x: x.nodes.nodename, rows)) - set([None])
        n_services = set(map(lambda x: x.svcmon.mon_svcname, rows)) - set([None])
    elif v.f_table == 'packages':
        if svcname is not None:
            qry &= db.svcmon.mon_svcname == svcname
        if nodename is not None:
            qry &= db.packages.node_id == db.nodes.node_id
            qry &= db.nodes.nodename == nodename
        rows = db(qry).select(db.svcmon.mon_svcname, db.nodes.nodename,
                              left=db.svcmon.on((db.packages.node_id==db.svcmon.node_id)&(db.svcmon.node_id==db.nodes.node_id)),
                              cacheable=True)
        n_nodes = set(map(lambda x: x.nodes.nodename, rows)) - set([None])
        n_services = set(map(lambda x: x.svcmon.mon_svcname, rows)) - set([None])
    elif v.f_table == 'svcmon':
        if svcname is not None:
            qry &= db.svcmon.mon_svcname == svcname
        if nodename is not None:
            qry &= db.svcmon.node_id == db.nodes.node_id
            qry &= db.nodes.nodename == nodename
        rows = db(qry).select(db.nodes.nodename, db.svcmon.mon_svcname,
                              cacheable=True)
        n_nodes = set(map(lambda x: x.nodes.nodename, rows)) - set([None])
        n_services = set(map(lambda x: x.svcmon.mon_svcname, rows)) - set([None])
    elif v.f_table == 'svcdisks':
        if svcname is not None:
            qry &= db.svcdisks.disk_svcname == svcname
        if nodename is not None:
            qry &= db.svcdisks.node_id == db.nodes.node_id
            qry &= db.nodes.nodename == nodename
        rows = db(qry).select(db.nodes.nodename,
                              db.svcdisks.disk_svcname,
                              cacheable=True)
        n_nodes = set(map(lambda x: x.nodes.nodename, rows)) - set([None])
        n_services = set(map(lambda x: x.svcdisks.disk_svcname, rows)) - set([None])
    elif v.f_table == 'diskinfo':
        qry &= db.diskinfo.disk_id==db.svcdisks.disk_id
        if svcname is not None:
            qry &= db.svcdisks.disk_svcname == svcname
        if nodename is not None:
            qry &= db.svcdisks.node_id == db.nodes.node_id
            qry &= db.nodes.nodename == nodename
        rows = db(qry).select(db.nodes.nodename,
                              db.svcdisks.disk_svcname,
                              cacheable=True)
        n_nodes = set(map(lambda x: x.nodes.nodename, rows)) - set([None])
        n_services = set(map(lambda x: x.svcdisks.disk_svcname, rows)) - set([None])
    elif v.f_table == 'node_hba':
        if svcname is not None:
            qry &= db.svcmon.mon_svcname == svcname
        if nodename is not None:
            qry &= db.node_hba.nodename == nodename
        rows = db(qry).select(db.svcmon.mon_svcname, db.node_hba.nodename,
                              left=db.svcmon.on((db.node_hba.nodename==db.nodes.nodename)&(db.svcmon.node_id==db.nodes.node_id)),
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
        _qry &= db.apps.app == db.nodes.app
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

