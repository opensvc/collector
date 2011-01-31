@auth.requires_login()
def ajax_set_user_prefs_column():
    for v in request.vars:
        if 'set_col_field' in v:
            field = request.vars[v]
        elif 'set_col_table' in v:
            table = request.vars[v]
        elif 'set_col_value' in v:
            visible = request.vars[v]
    if field is None or table is None or visible is None:
        raise Exception("missing args: (field, table, visible) = ",
                        (field, table, visible))
    sql = """replace into user_prefs_columns
             (upc_user_id, upc_table, upc_field, upc_visible)
             values
             (%(uid)s, '%(table)s', '%(field)s', %(visible)s)
          """%dict(uid=session.auth.user.id,
                   table=table, field=field, visible=visible)
    try:
        db.executesql(sql)
    except:
        raise Exception(sql)

def ajax_filter_cloud():
    fil = request.vars['id_new_filter_name']
    val = request.vars['id_new_filter_value']
    filters = db(db.filters.fil_name==fil).select()
    if len(filters) == 0:
        return DIV()
    if filters[0].fil_need_value != 1:
        return DIV()
    if filters[0].fil_search_table is None:
        return DIV()
    n = {}
    f = filters[0]
    col = db[f.fil_search_table][f.fil_column]
    q = col.like('%'+val+'%')
    rows = db(q).select(col)
    for i in [r[f.fil_column] for r in rows]:
        if i in n:
            n[i] += 1
        else:
            n[i] = 1
    if len(n) == 0:
        return DIV()
    c_max = max(n.values())
    def format_item(i, c, c_max):
        s = float(c) / c_max * 100 + 70
        return SPAN(i+' ',
                    _onClick="""getElementById("id_new_filter_value").value="%s";
                                getElementById("id_new_filter_value").focus();
                             """%str(i),
                    _style="""font-size:'+str(s)+'%;
                              padding:0.4em;
                              cursor:pointer;
                           """
                   )
    d = []
    for i in sorted(n):
        if i == '':
            continue
        d += [format_item(i, n[i], c_max)]
    return SPAN(H3(T('Candidates')), HR(), *d)

@auth.requires_login()
def ajax_del_db_filters():
    div = request.args(0)
    fil_name = request.vars['id_new_filter_name']
    ids = db(db.filters.fil_name==fil_name)._select(db.filters.id)
    q = db.auth_filters.fil_id.belongs(ids)
    db(q).delete()
    request.args = [div]
    return ajax_db_filters()

@auth.requires_login()
def ajax_add_db_filters():
    div = request.args[0]
    fil_name = request.vars['id_new_filter_name']
    fil_value = request.vars['id_new_filter_value']
    ids = db(db.filters.fil_name==fil_name).select(db.filters.id)
    for id in [r.id for r in ids]:
        try:
            db.auth_filters.insert(fil_uid=session.auth.user.id,
                                   fil_id=id,
                                   fil_value=fil_value)
        except:
            pass
    request.args = [div]
    return ajax_db_filters()

@auth.requires_login()
def ajax_new_db_filters():
    fil_name = request.vars['id_new_filter_name']
    fil_img = request.args[0]
    div = request.args[1]
    s = SPAN(
         DIV(
           IMG(
             _src=URL(r=request,c='static',f=fil_img),
             _style='margin-right:4px;vertical-align:top',
           ),
           T(fil_name),
           _class='float',
           _style='width:14em',
         ),
         DIV(
           INPUT(
             _id='id_new_filter_value',
             _onKeyPress="""
               if (is_enter(event)) {
                   ajax("%(url)s",
                        ["id_new_filter_value", "id_new_filter_name"],
                        "%(div)s");
               };
             """%dict(url=URL(
                           r=request, c='ajax',
                           f='ajax_add_db_filters',
                           args=[div]),
                      div=div),
             _onKeyUp="""
               clearTimeout(timer);
               timer=setTimeout(function validate(){
                 ajax('%(url)s', ["id_new_filter_value", "id_new_filter_name"], 'filter_cloud')
               }, 800);
             """%dict(
                   url=URL(r=request,c='ajax',f='ajax_filter_cloud'),
                 ),
           ),
           _class='float',
         ),
         DIV(
           _class='spacer',
         ),
       )
    return s

@auth.requires_login()
def ajax_db_filters():
    div = request.args[0]
    av_filters = avail_db_filters()
    ac_filters = active_db_filters()
    avh = {}
    av = []
    ac = []

    def format_av_filter(f):
        return SPAN(
                   IMG(
                     _src=URL(r=request,c='static',f=f.fil_img),
                     _style='margin-right:4px',
                   ),
                   A(
                     T(f.fil_name),
                     _onClick="""
                       getElementById('id_new_filter_name').value='%(name)s';
                       $('#filter_cloud').html('');
                       ajax('%(url)s', ['id_new_filter_name'], '%(div)s');
                     """%dict(url=URL(
                                   r=request, c='ajax',
                                   f='ajax_new_db_filters',
                                   args=[f.fil_img,div]),
                              name=f.fil_name,
                              div="id_new_filter"),
                     _style='color:black',
                   ),
                   BR(),
                   _style='vertical-align:top',
                 )

    def format_ac_filter(f):
        return SPAN(
                   DIV(
                     IMG(
                       _src=URL(r=request,c='static',f=f.filters.fil_img),
                       _style='margin-right:4px;vertical-align:top',
                     ),
                     T(f.filters.fil_name),
                     _class='float',
                     _style='width:14em',
                   ),
                   DIV(
                     IMG(
                       _src=URL(r=request,c='static',f='clear16.png'),
                       _style='margin-right:4px;vertical-align:top',
                       _onClick="""
                         getElementById("id_new_filter_name").value='%(name)s';
                         ajax('%(url)s', ["id_new_filter_name"], '%(div)s');
                       """%dict(url=URL(
                                     r=request, c='ajax',
                                     f='ajax_del_db_filters',
                                     args=[div]),
                                name=f.filters.fil_name,
                                div=div),
                     ),
                     f.auth_filters.fil_value,
                     _class='float',
                   ),
                   DIV(
                     _class='spacer',
                   ),
                 )

    table_fancy_name = {
        'nodes': 'Nodes',
        'svcmon': 'Status',
        'services': 'Services',
        'v_services': 'Services',
        'SVCactions': 'Actions',
        None: 'Misc',
    }
    for k in set(table_fancy_name.values()):
        avh[k] = [H3(T(k))]
    for f in av_filters:
        if f.fil_search_table not in table_fancy_name:
            k = 'Misc'
        else:
            k = table_fancy_name[f.fil_search_table]
        avh[k].append(format_av_filter(f))
    for k in avh:
        av += DIV(*avh[k], _style='break-inside:avoid-column;-webkit-column-break-inside:avoid;')

    for f in ac_filters:
        ac.append(format_ac_filter(f))

    s = SPAN(
          INPUT(
            _type='hidden',
            _id='id_new_filter_name',
          ),
          H3(T('Active filters')),
          HR(),
          SPAN(ac),
          DIV(_id='id_new_filter'),
          DIV(_id='filter_cloud'),
          H3(T('Available filters')),
          HR(),
          DIV(*av, _style='width:31em;-webkit-columns:15em 2;-moz-column-width:15em;-moz-column-count:2;columns:2 15em'),
        )
    return s
