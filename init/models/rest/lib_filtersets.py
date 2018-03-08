def lib_fset_name(id):
    q = db.gen_filtersets.id == id
    row = db(q).select().first()
    if row is None:
        return
    return row.fset_name

def lib_fset_id(name):
    q = db.gen_filtersets.fset_name == name
    row = db(q).select().first()
    if row is None:
        return
    return row.id


def comp_get_fset_data():
    #
    # load filtersets in a hierarchical structure:
    #
    # {
    #  fset_id: [
    #    {
    #     'type': 'filter',
    #     'op': <operator>,
    #     'data': <row>,
    #    },
    #    {
    #     'type': 'filterset',
    #     'op': <operator>,
    #     'fset_id': <fset_id>,
    #     'data': [
    #      {
    #       'type': 'filter',
    #       'data': <row>,
    #      },
    #     ],
    #    },
    #  ],
    # }
    #
    data = {}
    q = db.gen_filtersets_filters.id > 0
    j = db.gen_filtersets_filters.f_id == db.gen_filters.id
    l = db.gen_filters.on(j)
    o = db.gen_filtersets_filters.fset_id | db.gen_filtersets_filters.f_order
    rows = db(q).select(cacheable=True, orderby=o, left=l)
    for row in rows:
        r = row.gen_filtersets_filters
        if r.fset_id not in data:
            data[r.fset_id] = []
        if r.f_id is not None and r.f_id != 0:
            _data = {'type': 'filter', 'op': r.f_log_op, 'data': row}
            data[r.fset_id].append(_data)
        elif r.encap_fset_id is not None:
            if r.encap_fset_id in data:
                _data = {'type': 'filterset', 'op': r.f_log_op, 'fset_id': r.encap_fset_id, 'data': data[r.encap_fset_id]}
            else:
                _data = {'type': 'filterset', 'op': r.f_log_op, 'fset_id': r.encap_fset_id, 'data': None}
            data[r.fset_id].append(_data)

    def recurse_fset(_data, depth=0):
        if depth > 10:
            raise Exception("filterset recursion limit")
        for i, __data in enumerate(_data):
            if __data['type'] != 'filterset':
                continue
            if __data['data'] is not None:
                recurse_fset(__data['data'], depth=depth+1)
                continue
            encap_fset_id = __data['fset_id']
            if encap_fset_id in data:
                __data['data'] = data[encap_fset_id]
                recurse_fset(__data['data'], depth=depth+1)

    for fset_id in data:
        recurse_fset(data[fset_id])

    #print_fset_data(data)
    return data

def print_fset_data(data):
    def recurse_print_fset(_data, depth=0):
        for i, __data in enumerate(_data):
            d = __data['data']
            padding = ''
            for i in range(depth):
                padding += " "
            if __data['type'] == 'filter':
                print padding, __data['op'], d.gen_filters.f_field, d.gen_filters.f_op, d.gen_filters.f_value
            elif __data['type'] == 'filterset':
                print padding, __data['fset_id']
                recurse_print_fset(__data['data'], depth=depth+1)

    for fset_id in data:
        print fset_id
        recurse_print_fset(data[fset_id])

def comp_get_matching_filters(fset_ids, fset_data=None, node_id=None, svc_id=None, slave=False):
    sql_l = []

    if svc_id == "":
        svc_id = None

    if fset_data is None:
        fset_data = comp_get_fset_data()

    def filter_sql(d, sql_l):
        fid = d.gen_filters.id
        table = d.gen_filters.f_table
        field = d.gen_filters.f_field
        value = d.gen_filters.f_value
        op = d.gen_filters.f_op

        if op == 'IN':
            value = value.replace(', ',',')
            l = value.split(',')
            l = map(lambda x: repr(x), l)
            value = "(%s)" % ','.join(l)
        else:
            try:
                value = int(value)
                value = str(value)
            except:
                value = repr(value)

        where_ext = ""
        join_table = ""

        if node_id is not None:
            if table == "nodes":
                where_ext += """ and nodes.node_id = "%s" """ % (node_id)
            elif table in (
              "node_hba",
              "node_ip"
            ):
                join_table += ", nodes"
                where_ext += """ and %s.node_id = "%s" """ % (table, node_id)
            elif table in ("diskinfo"):
                join_table += ", nodes, svcdisks"
                where_ext += """ and svcdisks.node_id=nodes.node_id and nodes.node_id="%s" and svcdisks.disk_id=diskinfo.disk_id""" % node_id
            elif table in (
              "v_comp_moduleset_attachments",
              "v_tags",
              "packages",
              "patches",
              "svcdisks",
              "svcmon",
              "v_svcmon_log",
              "resmon",
              "resinfo"
            ):
                if svc_id is None:
                    join_table += ", nodes"
                    where_ext += """ and %s.node_id="%s" """ % (table, node_id)
                else:
                    pass
            elif table in ("services"):
                if slave:
                    where_ext += """ and services.svc_id=svcmon.svc_id and nodes.node_id="%s" and nodes.nodename=svcmon.mon_vmname """ % node_id
                else:
                    where_ext += """ and services.svc_id=svcmon.svc_id and svcmon.node_id="%s" """ % node_id
                join_table += ", svcmon, nodes"
            elif table in ("apps"):
                where_ext += """ and apps.app=nodes.app and nodes.node_id="%s" """ % node_id
                join_table += ", nodes"
            else:
                print "unknown table", table
                return sql_l

        if svc_id is not None:
            if table in ("services", "svcdisks", "svcmon", "v_svcmon_log", "v_comp_moduleset_attachments", "v_tags", "resmon"):
                where_ext += " and %s.svc_id = '%s'" % (table, svc_id)
            elif table in ("nodes", "packages", "patches", "node_hba"):
                if table == "nodes":
                    if slave:
                        where_ext += " and nodes.nodename=svcmon.mon_vmname and svcmon.svc_id = '%s'" % svc_id
                    else:
                        where_ext += " and nodes.node_id=svcmon.node_id and svcmon.svc_id = '%s'" % svc_id
                    join_table += ", svcmon"
                elif table == "packages":
                    if slave:
                        where_ext += " and packages.node_id=nodes.node_id and nodes.nodename=svcmon.mon_vmname and svcmon.svc_id = '%s'" % svc_id
                    else:
                        where_ext += " and packages.node_id=svcmon.node_id and svcmon.svc_id = '%s'" % svc_id
                    join_table += ", svcmon, nodes"
                elif table == "patches":
                    if slave:
                        where_ext += " and patches.node_id=nodes.node_id and nodes.nodename=svcmon.mon_vmname and svcmon.svc_id = '%s'" % svc_id
                    else:
                        where_ext += " and patches.node_id=svcmon.node_id and svcmon.svc_id = '%s'" % svc_id
                    join_table += ", svcmon, nodes"
                elif table == "node_hba":
                    if slave:
                        where_ext += " and node_hba.node_id=nodes.node_id and nodes.nodename=svcmon.mon_vmname and svcmon.svc_id = '%s'" % svc_id
                    else:
                        where_ext += " and node_hba.node_id=svcmon.node_id and svcmon.svc_id = '%s'" % svc_id
                    join_table += ", svcmon"
            elif table == "diskinfo":
                where_ext += " and diskinfo.disk_id=svcdisks.disk_id and svcdisks.svc_id='%s'" % svc_id
                join_table += ", svcdisks"
            elif table == "apps":
                where_ext += " and apps.app=services.svc_app and services.svc_id='%s'" % svc_id
                join_table += ", services"


        where = "select 1 from %(table)s %(join_table)s where %(table)s.%(field)s %(op)s %(value)s %(where_ext)s" % dict(
          op=op,
          table = table,
          field = field,
          value = value,
          where_ext = where_ext,
          join_table = join_table,
        )

        sql_l += ["select if (exists(%(where)s), %(fid)d, 0)" % dict(
          where = where,
          fid = fid,
        )]

        return sql_l

    def recurse_sql(_data, sql_l):
        for data in _data:
            if data['type'] == 'filter':
                sql_l = filter_sql(data['data'], sql_l)
            elif data['type'] == 'filterset':
                sql_l = recurse_sql(data['data'], sql_l)
        return sql_l

    for fset_id, fset_name in fset_ids:
        if fset_id not in fset_data:
            continue
        sql_l = recurse_sql(fset_data[fset_id], sql_l)

    if len(sql_l) == 0:
        return set([])

    sql = ' union '.join(sql_l)
    rows = db.executesql(sql)
    matching_filters = map(lambda r: r[0], rows)
    matching_filters = set(matching_filters) - set([0])
    return matching_filters

def comp_get_matching_fset_ids(fset_ids=None, node_id=None, svc_id=None, slave=False):
    if fset_ids is None:
        fset_ids = comp_get_rulesets_fset_ids(node_id=node_id, svc_id=svc_id)
    fset_data = comp_get_fset_data()
    matching_filters = comp_get_matching_filters(
      fset_ids, fset_data,
      node_id=node_id, svc_id=svc_id, slave=slave
    )
    matching_fsets = []

    def recurse_match(data, depth=0, match=None):
        for _data in data:
            if _data['type'] == 'filter':
                #print " "*depth, _data['op'], _data['type'], _data['data'].gen_filters.id
                fid = _data['data'].gen_filters.id
                if match is None:
                    # first filter is always an AND
                    match = fid in matching_filters
                    if 'NOT' in _data['op']:
                        match = not match
                elif _data['op'] == 'AND':
                    match &= fid in matching_filters
                elif _data['op'] == 'AND NOT':
                    match &= fid not in matching_filters
                elif _data['op'] == 'OR':
                    match |= fid in matching_filters
                elif _data['op'] == 'OR NOT':
                    match |= fid not in matching_filters
            elif _data['type'] == 'filterset':
                #print " "*depth, _data['op'], _data['type'], _data['fset_id']
                if match is None:
                    match = recurse_match(_data['data'], depth=depth+1)
                    if 'NOT' in _data['op']:
                        match = not match
                elif _data['op'] == 'AND':
                    match &= recurse_match(_data['data'], depth=depth+1)
                elif _data['op'] == 'AND NOT':
                    match &= not recurse_match(_data['data'], depth=depth+1)
                elif _data['op'] == 'OR':
                    match |= recurse_match(_data['data'], depth=depth+1)
                elif _data['op'] == 'OR NOT':
                    match |= not recurse_match(_data['data'], depth=depth+1)
            #print " "*depth, match

        if match is None:
            # empty filterset
            match = False

        return match

    for fset_id, fset_name in fset_ids:
        #print fset_id, fset_name
	if fset_id in fset_data:
            match = recurse_match(fset_data[fset_id])
	else:
	    match = False
        #print "=>", match
        if match:
            matching_fsets.append(fset_id)

    return matching_fsets


