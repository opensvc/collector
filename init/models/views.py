def _pagination(request, query, groupby=None):
    start = 0
    end = 0
    nav = ''
    perpage = int(request.vars.perpage) if 'perpage' in request.vars.keys() else 20

    if perpage <= 0:
        return (start, end, nav)
    if groupby is not None:
        totalrecs = len(db(query).select(groupby=groupby))
    else:
        totalrecs = db(query).count()
    totalpages = totalrecs / perpage
    if totalrecs % perpage > 0: totalpages = totalpages + 1
    try:
        page = int(request.args[0]) if len(request.args) else 1
    except:
        """ casting error
        """
        page = 1

    # out of range conditions
    if page <= 0: page = 1
    if page > totalpages: page = 1
    start = (page-1)*perpage
    end = start+perpage
    if end > totalrecs:
        end = totalrecs

    num_pages = 10
    def page_range():
        s = page - num_pages/2
        e = page + num_pages/2
        if s <= 0:
            e = e - s
            s = 1
        if e > totalpages:
            s = s - (e - totalpages)
            e = totalpages
        if s <= 0:
            s = 1
        return range(s, e+1)

    pr = page_range()
    pager = []
    if page != 1:
        pager.append(A(T('<< '),_href=URL(r=request,args=[page-1],vars=request.vars)))
    for p in pr:
        if p == page:
            pager.append(A(str(p)+' ', _class="current_page"))
        else:
            pager.append(A(str(p)+' ', _href=URL(r=request,args=[p],vars=request.vars)))
    if page != totalpages:
        pager.append(A(T('>> '),_href=URL(r=request,args=[page+1],vars=request.vars)))
    v = request.vars
    v.perpage = 0
    pager.append(A(T('all'),_href=URL(r=request,vars=v)))

    # paging toolbar
    if totalrecs == 0:
        pager.append(P("No records found matching filters", _style='text-align:center'))
    else:
        info=T("Showing %(first)d to %(last)d out of %(total)d records", dict(first=start+1, last=end, total=totalrecs))
        nav = P(pager, _style='text-align:center', _title=info)

    return (start, end, nav)

def user_name():
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

    if chunk == 'empty':
        q = (db[table][field]==None)|(db[table][field]=='')
    elif chunk[0] not in '<>=':
        q = db[table][field].like(chunk)
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

def toggle_db_filters():
    if request.vars.addfilter is not None and request.vars.addfilter != '':
        filters = db(db.filters.id==request.vars.addfilter).select(db.filters.fil_name)
        if len(filters) == 0:
            return
        name = filters[0].fil_name
        ids = db(db.filters.fil_name==name).select(db.filters.id)
        for id in [r.id for r in ids]:
            try:
                db.auth_filters.insert(fil_uid=session.auth.user.id,
                                  fil_id=id,
                                  fil_value=request.vars.filtervalue)
            except:
                pass

    elif request.vars.delfilter is not None and request.vars.delfilter != '':
        filters = db(db.auth_filters.id==request.vars.delfilter).select(db.filters.fil_name, left=db.filters.on(db.auth_filters.fil_id==db.filters.id))
        if len(filters) == 0:
            return
        name = filters[0].fil_name
        ids = db(db.filters.fil_name==name)._select(db.filters.id)
        q = db.auth_filters.fil_id.belongs(ids)
        db(q).delete()

    elif request.vars.togfilter is not None and request.vars.togfilter != '':
        filters = db(db.auth_filters.id==request.vars.togfilter).select(
                        db.filters.fil_name,
                        db.auth_filters.fil_active,
                        left=db.filters.on(db.auth_filters.fil_id==db.filters.id)
                  )
        if len(filters) == 0:
            return
        name = filters[0].filters.fil_name
        ids = db(db.filters.fil_name==name)._select(db.filters.id)
        cur = filters[0].auth_filters.fil_active
        if cur: tgt = '0'
        else: tgt = '1'
        q = db.auth_filters.fil_id.belongs(ids)
        db(q).update(fil_active=tgt)
        del request.vars.togfilter

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
                           orderby=o,
                           groupby=db.filters.fil_name,
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

