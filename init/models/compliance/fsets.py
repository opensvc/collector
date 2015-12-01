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

def comp_get_matching_filters(fset_ids, fset_data=None, nodename=None, svcname=None, slave=False):
    sql_l = []

    if svcname == "":
        svcname = None

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

        if slave:
            svcmon_nodname_field = "svcmon.mon_vmname"
        else:
            svcmon_nodname_field = "svcmon.mon_nodname"

        if nodename is not None:
            if table in ("nodes", 'node_hba', "b_disk_app", "svcdisks", "svcmon", "svcmon_log", "resmon"):
                if table in ("nodes", "packages", "patches", 'node_hba', "resmon"):
                    _field = "nodename"
                elif table in ("b_disk_app", "svcdisks"):
                    _field = "disk_nodename"
                elif table in ("svcmon", "svcmon_log"):
                    _field = "mon_nodname"
                else:
                    print "unknown table", table
                    return sql_l
                where_ext += " and %s.%s = '%s'" % (table, _field, nodename)
            elif table == "v_comp_moduleset_attachments" and svcname is None:
                _field = "nodename"
                where_ext += " and %s.%s = '%s'" % (table, _field, nodename)
            elif table == "v_tags" and svcname is None:
                _field = "nodename"
                where_ext += " and %s.%s = '%s'" % (table, _field, nodename)
            elif table == "packages" and svcname is None:
                _field = "pkg_nodename"
            elif table == "patches" and svcname is None:
                _field = "patch_nodename"
                where_ext += " and %s.%s = '%s'" % (table, _field, nodename)
            elif table in ("services"):
                where_ext += " and services.svc_name=svcmon.mon_svcname and %s = '%s'" % (svcmon_nodname_field, nodename)
                join_table += ", svcmon"
            elif table in ("apps"):
                where_ext += " and apps.app=nodes.project and nodes.nodename = '%s'" % nodename
                join_table += ", nodes"

        if svcname is not None:
            if table in ("services", "b_disk_app", "svcdisks", "svcmon",
                         "svcmon_log", "v_comp_moduleset_attachments",
                         "v_tags", "resmon"):
                if table in ("services"):
                    _field = "svc_name"
                elif table in ("b_disk_app", "svcdisks"):
                    _field = "disk_svcname"
                elif table in ("svcmon", "svcmon_log"):
                    _field = "mon_svcname"
                elif table in ("v_comp_moduleset_attachments", "v_tags", "resmon"):
                    _field = "svcname"
                else:
                    print "unknown table", table
                    return sql_l
                where_ext += " and %s = '%s'" % (_field, svcname)
            elif table in ("nodes", "packages", "patches", "node_hba"):
                if table == "nodes":
                    where_ext += " and nodes.nodename=%s and svcmon.mon_svcname = '%s'" % (svcmon_nodname_field, svcname)
                    join_table += ", svcmon"
                elif table == "packages":
                    where_ext += " and packages.pkg_nodename=%s and svcmon.mon_svcname = '%s'" % (svcmon_nodname_field, svcname)
                    join_table += ", svcmon"
                elif table == "patches":
                    where_ext += " and patches.patch_nodename=%s and svcmon.mon_svcname = '%s'" % (svcmon_nodname_field, svcname)
                    join_table += ", svcmon"
                elif table == "node_hba":
                    where_ext += " and node_hba.nodename=%s and svcmon.mon_svcname = '%s'" % (svcmon_nodname_field, svcname)
                    join_table += ", svcmon"
            elif table == "apps":
                where_ext += " and apps.app=services.svc_app and services.svc_name='%s'" % svcname
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

def comp_get_matching_fset_ids(fset_ids=None, nodename=None, svcname=None, slave=False):
    if fset_ids is None:
        fset_ids = comp_get_rulesets_fset_ids(nodename=nodename, svcname=svcname)
    fset_data = comp_get_fset_data()
    matching_filters = comp_get_matching_filters(fset_ids, fset_data, nodename=nodename, svcname=svcname, slave=slave)
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


