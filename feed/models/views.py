def apply_filters(q, fset_id, node_field, service_field):
    nodes = set([])
    services = set([])
    qr = db.v_gen_filtersets.fset_id == fset_id
    rows = db(qr).select()
    for row in rows:
        nodes, services = filterset_query(row, nodes, services)

    n_nodes = len(nodes)
    n_services = len(services)

    if n_nodes > 0 and n_services > 0:
        q &= (node_field.belongs(nodes)) | (service_field.belongs(services))
    elif len(nodes) > 0:
        q &= node_field.belongs(nodes)
    elif len(services) > 0:
        q &= service_field.belongs(services)

    return q

def filterset_query(row, nodes, services):
    if 'v_gen_filtersets' in row:
        v = row.v_gen_filtersets
    else:
        v = row

    if v.encap_fset_id > 0:
        o = db.v_gen_filtersets.f_order
        qr = db.v_gen_filtersets.fset_id == v.encap_fset_id
        rows = db(qr).select(orderby=o)
        for r in rows:
            nodes, services = filterset_query(r, nodes, services)
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
            rows = db(qry).select(db.services.svc_name,
                                  groupby=db.services.svc_name)
            n_nodes = set([])
            n_services = set(map(lambda x: x.svc_name, rows))
        elif v.f_table == 'nodes':
            rows = db(qry).select(db.nodes.nodename,
                                  groupby=db.nodes.nodename)
            n_nodes = set(map(lambda x: x.nodename, rows))
            n_services = set([])
        elif v.f_table == 'svcmon':
            rows = db(qry).select(db.svcmon.mon_nodname,
                                  db.svcmon.mon_svcname,
                                  groupby=db.nodes.nodename)
            n_nodes = set(map(lambda x: x.mon_nodname, rows))
            n_services = set(map(lambda x: x.mon_svcname, rows))
        else:
            raise Exception(str(v))

        if 'AND' in v.f_log_op:
            if v.f_table == 'nodes' or v.f_table == 'svcmon':
                if nodes == set([]):
                    nodes = n_nodes
                else:
                    nodes &= n_nodes
            elif v.f_table == 'services' or v.f_table == 'svcmon':
                if services == set([]):
                    services = n_services
                else:
                    services &= n_services
        elif 'OR' in v.f_log_op:
            if v.f_table == 'nodes' or v.f_table == 'svcmon':
                if nodes == set([]):
                    nodes = n_nodes
                else:
                    nodes |= n_nodes
            elif v.f_table == 'services' or v.f_table == 'svcmon':
                if services == set([]):
                    services = n_services
                else:
                    services |= n_services

    return nodes, services

