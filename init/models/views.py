def user_name():
    if not hasattr(session.auth, 'user'):
        return 'Unknown'
    return ' '.join([session.auth.user.first_name,
                     session.auth.user.last_name])

def _where(query, table, var, field):
    if query is None:
        query = (db[table].id > 0)
    if var is None: return query
    if len(var) == 0: return query

    if '&' in var and '|' in var:
        """don't even try to guess order
        """
        return query

    done = False

    if var[0] == '|':
        _or=True
        var = var[1:]
    elif var[0] == '&':
        _or=False
        var = var[1:]
    else:
        _or=False

    if '&' in var:
        i = var.index('&')
        chunk = var[:i]
        var = var[i:]
    elif '|' in var:
        i = var.index('|')
        chunk = var[:i]
        var = var[i:]
    else:
        done = True
        chunk = var

    if len(chunk) == 0:
        return query

    if chunk[0] == '!':
        _not = True
        chunk = chunk[1:]
    else:
        _not = False

    if len(chunk) == 0:
        return query

    # initialize a restrictive filter
    q = db[table].id < 0

    if chunk == 'empty':
        q = (db[table][field]==None)|(db[table][field]=='')
    elif chunk[0] not in '<>=':
        if db[table][field].type == 'string':
            q = db[table][field].like(chunk)
        elif db[table][field].type in ('id', 'integer'):
            try:
               c = int(chunk)
               q = db[table][field]==c
            except:
               pass
        elif db[table][field].type in ('float'):
            try:
               c = float(chunk)
               q = db[table][field]==c
            except:
               pass
    else:
        _op = chunk[0]

        if len(chunk) == 0:
            return query

        chunk = chunk[1:]
        if _op == '>':
            q = db[table][field]>chunk
        elif _op == '<':
            q = db[table][field]<chunk
        elif _op == '=':
            q = db[table][field]==chunk

    if _not:
        q = ~q

    if not done:
        q = _where(q, table, var, field)

    if _or:
        return query|q
    else:
        return query&q

def domainname(fqdn):
    if fqdn is None or fqdn == "":
        return
    l = fqdn.split('.')
    if len(l) < 2:
        return
    l[0] = ""
    return '.'.join(l)

def apply_db_filters(query, table=None):
    q = db.auth_filters.fil_uid==session.auth.user.id
    q &= db.auth_filters.fil_active==1
    q &= db.filters.fil_table==table
    filters = db(q).select(db.auth_filters.fil_value,
                           db.filters.fil_name,
                           db.filters.fil_table,
                           db.filters.fil_column,
                           left=db.filters.on(db.filters.id==db.auth_filters.fil_id))
    for f in filters:
        if 'ref' not in f.filters.fil_column:
            if table not in db or f.filters.fil_column not in db[table]:
                continue
            query &= _where(None, table, f.auth_filters.fil_value, f.filters.fil_column)
        elif f.filters.fil_column == 'ref1':
            """ only primary nodes
            """
            query &= db.v_svcmon.mon_nodname==db.v_svcmon.svc_autostart
        elif f.filters.fil_column == 'ref2':
            """ only nodes with services
            """
            query &= db.v_nodes.nodename.belongs(db()._select(db.svcmon.mon_nodname))
        elif f.filters.fil_column == 'ref3':
            """ only not acknowledged actions
            """
            q1 = db.v_svcactions.ack!=1
            q2 = db.v_svcactions.ack==None
            q3 = db.v_svcactions.status=='err'
            query = (q1 | q2) & q3
    return query

def avail_db_filters(table=None):
    o = db.filters.fil_pos|db.filters.fil_img|db.filters.fil_name
    active_fid = db(db.auth_filters.fil_uid==session.auth.user.id)._select(db.auth_filters.fil_id)
    q = ~db.filters.id.belongs(active_fid)
    filters = db(q).select(db.filters.id,
                           db.filters.fil_name,
                           db.filters.fil_img,
                           db.filters.fil_table,
                           db.filters.fil_column,
                           db.filters.fil_need_value,
                           db.filters.fil_pos,
                           db.filters.fil_search_table,
                           orderby=o,
                           groupby=db.filters.fil_name|db.filters.fil_search_table,
                          )
    return filters

def active_db_filters(table=None):
    o = db.filters.fil_pos|db.filters.fil_img|db.filters.fil_name
    q = db.auth_filters.fil_uid==session.auth.user.id
    filters = db(q).select(db.auth_filters.fil_value,
                           db.auth_filters.id,
                           db.auth_filters.fil_active,
                           db.filters.fil_name,
                           db.filters.fil_img,
                           db.filters.fil_table,
                           db.filters.fil_column,
                           left=db.filters.on(db.filters.id==db.auth_filters.fil_id),
                           groupby=db.filters.fil_name,
                           orderby=o
                          )
    return filters

def active_db_filters_count():
    g = db.filters.fil_name
    q = db.auth_filters.fil_uid==session.auth.user.id
    rows = db(q).select(g,
                        left=db.filters.on(db.filters.id==db.auth_filters.fil_id),
                        orderby=g,
                        groupby=g)
    return len(rows)

