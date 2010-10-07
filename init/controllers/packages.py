@auth.requires_login()
def packages():
    d1 = dict(
        pkg_nodename = dict(
            pos = 1,
            title = T('Nodename'),
            display = True,
            nestedin = 'packages',
            img = 'node16',
            size = 10
        ),
        pkg_name = dict(
            pos = 2,
            title = T('Package'),
            display = True,
            nestedin = 'packages',
            img = 'pkg16',
            size = 10
        ),
        pkg_version = dict(
            pos = 3,
            title = T('Version'),
            display = True,
            nestedin = 'packages',
            img = 'pkg16',
            size = 4
        ),
        pkg_arch = dict(
            pos = 4,
            title = T('Arch'),
            display = True,
            nestedin = 'packages',
            img = 'pkg16',
            size = 10
        ),
        pkg_updated = dict(
            pos = 5,
            title = T('Updated'),
            display = True,
            nestedin = 'packages',
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
    __update_columns(columns, 'packages')

    o = db.packages.pkg_nodename
    o |= db.packages.pkg_name
    o |= db.packages.pkg_arch

    toggle_db_filters()

    # filtering
    query = db.packages.id>0
    query &= db.packages.pkg_nodename==db.v_nodes.nodename
    for key in d1.keys():
        if key not in request.vars.keys():
            continue
        query &= _where(None, 'packages', request.vars[key], key)
    for key in d2.keys():
        if key not in request.vars.keys():
            continue
        query &= _where(None, 'v_nodes', request.vars[key], key)

    query &= _where(None, 'packages', domain_perms(), 'pkg_nodename')

    query = apply_db_filters(query, 'v_nodes')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select(orderby=o)
    else:
        rows = db(query).select(limitby=(start,end), orderby=o)

    return dict(columns=columns, colkeys=colkeys,
                packages=rows,
                nav=nav,
                active_filters=active_db_filters('v_nodes'),
                available_filters=avail_db_filters('v_nodes'),
               )

@auth.requires_login()
def packages_csv():
    import gluon.contenttype
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    request.vars['perpage'] = 0
    return str(packages()['packages'])


