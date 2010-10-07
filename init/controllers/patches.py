@auth.requires_login()
def patches():
    d1 = dict(
        patch_nodename = dict(
            pos = 1,
            title = T('Nodename'),
            display = True,
            nestedin = 'patches',
            img = 'node16',
            size = 10
        ),
        patch_num = dict(
            pos = 2,
            title = T('Patchnum'),
            display = True,
            nestedin = 'patches',
            img = 'pkg16',
            size = 10
        ),
        patch_rev = dict(
            pos = 3,
            title = T('Patchrev'),
            display = True,
            nestedin = 'patches',
            img = 'pkg16',
            size = 4
        ),
        patch_updated = dict(
            pos = 4,
            title = T('Updated'),
            display = True,
            nestedin = 'patches',
            img = 'pkg16',
            size = 6
        ),
    )

    d2 = v_nodes_columns()
    for k in d2:
        d2[k]['pos'] += 10
        d2[k]['display'] = False
        d2[k]['nestedin'] = 'v_nodes'

    del(d2['nodename'])
    columns = d1.copy()
    columns.update(d2)

    def _sort_cols(x, y):
        return cmp(columns[x]['pos'], columns[y]['pos'])

    colkeys = columns.keys()
    colkeys.sort(_sort_cols)
    __update_columns(columns, 'patches')

    o = db.patches.patch_nodename
    o |= db.patches.patch_num
    o |= db.patches.patch_rev

    toggle_db_filters()

    # filtering
    query = db.patches.id>0
    query &= db.patches.patch_nodename==db.v_nodes.nodename
    for key in d1.keys():
        if key not in request.vars.keys():
            continue
        query &= _where(None, 'patches', request.vars[key], key)
    for key in d2.keys():
        if key not in request.vars.keys():
            continue
        query &= _where(None, 'v_nodes', request.vars[key], key)

    query &= _where(None, 'patches', domain_perms(), 'patch_nodename')

    query = apply_db_filters(query, 'v_nodes')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select(orderby=o)
    else:
        rows = db(query).select(limitby=(start,end), orderby=o)

    return dict(columns=columns, colkeys=colkeys,
                patches=rows,
                nav=nav,
                active_filters=active_db_filters('v_nodes'),
                available_filters=avail_db_filters('v_nodes'),
               )

@auth.requires_login()
def patches_csv():
    import gluon.contenttype
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    request.vars['perpage'] = 0
    return str(checks()['patches'])


