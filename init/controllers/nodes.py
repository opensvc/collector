def nodes_csv():
    import gluon.contenttype
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    request.vars['perpage'] = 0
    return str(nodes()['nodes'])

@auth.requires_membership('Manager')
def _nodes_del(request):
    node_ids = ([])
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        node_ids += ([key[6:]])

    if len(node_ids) == 0:
        response.flash = T('invalid node selection')
        return
    for id in node_ids:
        db(db.nodes.id==id).delete()
    response.flash = T('nodes removed')
    del(request.vars['action'])
    redirect(URL(r=request, f='nodes'))

@auth.requires_login()
def nodes():
    if request.vars.action is not None and request.vars.action == "delnodes":
        _nodes_del(request)

    o = db.v_nodes.nodename

    columns = v_nodes_columns()
    __update_columns(columns, 'nodes')

    def _sort_cols(x, y):
        return cmp(columns[x]['pos'], columns[y]['pos'])
    colkeys = columns.keys()
    colkeys.sort(_sort_cols)

    toggle_db_filters()

    # filtering
    query = (db.v_nodes.id>0)
    for key in columns.keys():
        if key not in request.vars.keys():
            continue
        query &= _where(None, 'v_nodes', request.vars[key], key)

    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')

    query = apply_db_filters(query, 'v_nodes')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select(orderby=o)
    else:
        rows = db(query).select(orderby=o, limitby=(start,end))

    return dict(columns=columns, colkeys=colkeys,
                nodes=rows,
                active_filters=active_db_filters('v_nodes'),
                available_filters=avail_db_filters('v_nodes'),
                nav=nav)

def _label(key):
    d = v_nodes_columns()
    return DIV(
             IMG(
               _src=URL(r=request,c='static',f=d[key]['img']+'.png'),
               _border=0,
               _style='vertical-align:top;margin-right:10px',
             ),
             d[key]['title'],
           )

def _node_form(record=None):
    if record is not None:
        deletable = True
    else:
        deletable = False
    return SQLFORM(db.nodes,
                 record=record,
                 deletable=deletable,
                 hidden_fields=['mem_bytes',
                                'mem_banks',
                                'mem_slots',
                                'os_name',
                                'os_kernel',
                                'os_vendor',
                                'os_release',
                                'os_arch',
                                'cpu_freq',
                                'cpu_dies',
                                'cpu_cores',
                                'cpu_model',
                                'cpu_vendor',
                                'environnement',
                                'serial',
                                'model'],
                 fields=['nodename',
                         'team_responsible',
                         'warranty_end',
                         'status',
                         'role',
                         'type',
                         'loc_country',
                         'loc_zip',
                         'loc_city',
                         'loc_addr',
                         'loc_building',
                         'loc_floor',
                         'loc_room',
                         'loc_rack',
                         'power_supply_nb',
                         'power_cabinet1',
                         'power_cabinet2',
                         'power_protect',
                         'power_protect_breaker',
                         'power_breaker1',
                         'power_breaker2',
                        ],
                 labels={
                         'nodename': _label('nodename'),
                         'team_responsible': _label('team_responsible'),
                         'warranty_end': _label('warranty_end'),
                         'status': _label('status'),
                         'role': _label('role'),
                         'type': _label('type'),
                         'loc_country': _label('loc_country'),
                         'loc_zip': _label('loc_zip'),
                         'loc_city': _label('loc_city'),
                         'loc_addr': _label('loc_addr'),
                         'loc_building': _label('loc_building'),
                         'loc_floor': _label('loc_floor'),
                         'loc_room': _label('loc_room'),
                         'loc_rack': _label('loc_rack'),
                         'power_supply_nb': _label('power_supply_nb'),
                         'power_cabinet1': _label('power_cabinet1'),
                         'power_cabinet2': _label('power_cabinet2'),
                         'power_protect': _label('power_protect'),
                         'power_protect_breaker': _label('power_protect_breaker'),
                         'power_breaker1': _label('power_breaker1'),
                         'power_breaker2': _label('power_breaker2'),
                        },
                )

@auth.requires_login()
def node_insert():
    form = _node_form()
    if form.accepts(request.vars):
        response.flash = T("edition recorded")
        redirect(URL(r=request, f='nodes'))
    elif form.errors:
        response.flash = T("errors in form")
    return dict(form=form)

@auth.requires_login()
def node_edit():
    query = (db.v_nodes.id>0)
    query &= _where(None, 'v_nodes', request.vars.node, 'nodename')
    query &= _where(None, 'v_nodes', domain_perms(), 'nodename')
    rows = db(query).select()
    if len(rows) != 1:
        response.flash = "vars: %s"%str(request.vars)
        return dict(form=None)
    record = rows[0]
    id = record.id
    record = db(db.v_nodes.id==id).select()[0]
    form = _node_form(record)
    if form.accepts(request.vars):
        response.flash = T("edition recorded")
        redirect(URL(r=request, f='nodes'))
    elif form.errors:
        response.flash = T("errors in form")

    return dict(form=form)


