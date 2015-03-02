def apply_filters(q, fset_id, node_field=None, service_field=None, nodename=None, svcname=None):
    qry = db.v_gen_filtersets.fset_id == fset_id

    rows = db(qry).select(orderby=db.v_gen_filtersets.f_order)
    if len(rows) == 0:
        return q

    nodes = set([])
    services = set([])
    i = 0
    for row in rows:
        nodes, services = filterset_query(row, nodes, services, i=i, nodename=nodename, svcname=svcname)
        i += 1

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

def filterset_query(row, nodes, services, i=0, nodename=None, svcname=None):
    if 'v_gen_filtersets' in row:
        v = row.v_gen_filtersets
    else:
        v = row

    if v.encap_fset_id > 0:
        o = db.v_gen_filtersets.f_order
        qr = db.v_gen_filtersets.fset_id == v.encap_fset_id
        rows = db(qr).select(orderby=o)
        n_nodes = set([])
        n_services = set([])
        j = 0
        for r in rows:
            n_nodes, n_services = filterset_query(r, n_nodes, n_services, i=j, nodename=nodename, svcname=svcname)
            j += 1
        if 'NOT' in v.f_log_op:
            all_nodes = set([r.nodename for r in db(db.nodes.id>0).select(db.nodes.nodename)])
            all_services = set([r.svc_name for r in db(db.services.id>0).select(db.services.svc_name)])
            n_nodes = all_nodes - n_nodes
            n_services = all_services - n_services
        if v.f_log_op == 'AND':
            if i == 0:
                nodes = n_nodes
            else:
                nodes &= n_nodes
            if i == 0:
                services = n_services
            else:
                services &= n_services
        elif v.f_log_op == 'OR':
            if i == 0:
                nodes = n_nodes
            else:
                nodes |= n_nodes
            if i == 0:
                services = n_services
            else:
                services |= n_services
        return nodes, services

    elif v.f_table is None or v.f_field is None:
        return nodes, services

    else:
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
                                  left=db.svcmon.on(db.services.svc_name==db.svcmon.mon_svcname))
            n_nodes = set(map(lambda x: x.svcmon.mon_nodname, rows)) - set([None])
            n_services = set(map(lambda x: x.services.svc_name, rows)) - set([None])
        elif v.f_table == 'nodes':
            if svcname is not None:
                qry &= db.svcmon.mon_svcname == svcname
            if nodename is not None:
                qry &= db.nodes.nodename == nodename
            rows = db(qry).select(db.svcmon.mon_svcname, db.nodes.nodename,
                                  left=db.svcmon.on(db.nodes.nodename==db.svcmon.mon_nodname))
            n_nodes = set(map(lambda x: x.nodes.nodename, rows)) - set([None])
            n_services = set(map(lambda x: x.svcmon.mon_svcname, rows)) - set([None])
        elif v.f_table == 'svcmon':
            if svcname is not None:
                qry &= db.svcmon.mon_svcname == svcname
            if nodename is not None:
                qry &= db.svcmon.mon_nodname == nodename
            rows = db(qry).select(db.svcmon.mon_nodname, db.svcmon.mon_svcname)
            n_nodes = set(map(lambda x: x.mon_nodname, rows)) - set([None])
            n_services = set(map(lambda x: x.mon_svcname, rows)) - set([None])
        elif v.f_table == 'v_tags':
            if svcname is not None:
                qry &= db.v_tags.svcname == svcname
            if nodename is not None:
                qry &= db.v_tags.nodename == nodename
            rows = db(qry).select(db.v_tags.nodename, db.v_tags.svcname)
            n_nodes = set(map(lambda x: x.nodename, rows)) - set([None])
            n_services = set(map(lambda x: x.svcname, rows)) - set([None])
        elif v.f_table == 'v_comp_moduleset_attachments':
            if svcname is not None:
                qry &= db.v_comp_moduleset_attachments.svcname == svcname
            if nodename is not None:
                qry &= db.v_comp_moduleset_attachments.nodename == nodename
            rows = db(qry).select(db.v_comp_moduleset_attachments.nodename, db.v_comp_moduleset_attachments.svcname)
            n_nodes = set(map(lambda x: x.nodename, rows)) - set([None])
            n_services = set(map(lambda x: x.svcname, rows)) - set([None])
        elif v.f_table == 'b_disk_app':
            if svcname is not None:
                qry &= db.b_disk_app.disk_svcname == svcname
            if nodename is not None:
                qry &= db.b_disk_app.disk_nodename == nodename
            rows = db(qry).select(db.b_disk_app.disk_nodename, db.b_disk_app.disk_svcname)
            n_nodes = set(map(lambda x: x.disk_nodename, rows)) - set([None])
            n_services = set(map(lambda x: x.disk_svcname, rows)) - set([None])
        elif v.f_table == 'node_hba':
            if svcname is not None:
                qry &= db.svcmon.mon_svcname == svcname
            if nodename is not None:
                qry &= db.node_hba.nodename == nodename
            rows = db(qry).select(db.svcmon.mon_svcname, db.node_hba.nodename,
                                  left=db.svcmon.on(db.node_hba.nodename==db.svcmon.mon_nodname))
            n_nodes = set(map(lambda x: x.node_hba.nodename, rows)) - set([None])
            n_services = set(map(lambda x: x.svcmon.mon_svcname, rows)) - set([None])
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

