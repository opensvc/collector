def q_filter(query=None, svc_field=None, node_field=None, group_field=None, app_field=None, db=db):
    q = None
    t = None
    if not auth_is_node() and "Manager" in user_groups():
        manager = True
    else:
        manager = False
    if svc_field:
        if auth_is_node():
            node_svc_ids = [r.svc_id for r in db(db.svcmon.node_id==auth.user.node_id).select()]
            q = svc_field.belongs(node_svc_ids)
        elif not manager:
            q = svc_field.belongs(user_published_services())
        if t is None:
            t = db[svc_field.tablename]
    if node_field:
        if auth_is_node():
            q = node_field == auth.user.node_id
        elif not manager:
            q = node_field.belongs(user_published_nodes())
        if t is None:
            t = db[node_field.tablename]
    if app_field:
        if auth_is_node():
            node_apps = node_responsibles_apps(auth.user.node_id)
            q = app_field.belongs(node_apps)
        elif not manager:
            q = app_field.belongs(user_published_apps())
        if t is None:
            t = db[app_field.tablename]
    if group_field:
        if not manager:
            q = group_field.belongs(user_groups())
        if t is None:
            t = db[group_field.tablename]
    if query is None:
        query = t.id > 0
    if q is None:
        return query
    return query & q

def _where(query, table, var, field, depth=0, db=db):
    if table not in db:
        return query
    if field not in db[table]:
        return query

    if depth == 0 and var and len(var) > 0 and var[0] == "|":
       var = var[1:]

    if query is None:
        query = (db[table].id >= 0)
    if var is None:
        return query
    if len(var) == 0:
        return query
    if var == "%":
        return query

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
        if db[table][field].type == "string":
            q = (db[table][field]==None)|(db[table][field]=='')
        else:
            q = db[table][field]==None
    elif chunk[0] == '(' and chunk[-1] == ')' and len(chunk) > 2:
        chunk = chunk[1:-1]
        if field not in db[table]:
            pass
        q = db[table][field].belongs(chunk.split(','))
    elif chunk[0] not in '<>=':
        if chunk[0] == "~":
            chunk = chunk[1:]
        if field not in db[table]:
            pass
        elif db[table][field].type in ('string', 'text', 'date', 'upload'):
            if '%' in chunk:
                q = db[table][field].like(chunk)
            else:
                q = db[table][field]==chunk
        elif db[table][field].type in ('id', 'integer'):
            try:
               c = int(chunk)
               q = db[table][field]==c
            except:
               pass
        elif db[table][field].type == 'float':
            try:
               c = float(chunk)
               q = db[table][field]==c
            except:
               pass
        elif db[table][field].type == 'boolean':
            if chunk in ('T', 't', "true", "True", True, "yes", "Yes", "YES", "Y", "y"):
               q = db[table][field]==True
            elif chunk == "%":
               q = db[table].id >= 0
            else:
               q = db[table][field]==False
    else:
        _op = chunk[0]

        if len(chunk) == 0:
            return query

        chunk = chunk[1:]

        if field not in db[table]:
            pass
        elif db[table][field].type in ('datetime', 'timestamp', 'date'):
            chunk = delta_to_date(chunk)

        if _op == '>':
            q = db[table][field]>chunk
        elif _op == '<':
            q = db[table][field]<chunk
        elif _op == '=':
            q = db[table][field]==chunk

    if _not:
        q = ~q

    if not done:
        q = _where(q, table, var, field, depth=depth+1)

    if _or:
        return query|q
    else:
        return query&q

def table_where(query, table, field):
    return _where(query,
                  table.colprops[field].table,
                  table.filter_parse(field),
                  table.colprops[field].field if table.colprops[field].filter_redirect is None else table.colprops[field].filter_redirect
                 )
