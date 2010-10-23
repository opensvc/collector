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
    val = request.vars.filtervalue
    fil = request.vars.addfilter
    filters = db(db.filters.id==fil).select()
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
                    _onClick="""getElementById("filtervalue").value="%s";
                                getElementById("filtervalue").focus();
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
    return SPAN(d)

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
                           args=[fil_name, div]),
                      div=div),
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
    av = []
    ac = []

    for f in av_filters:
        av.append(SPAN(
                   IMG(
                     _src=URL(r=request,c='static',f=f.fil_img),
                     _style='margin-right:4px',
                   ),
                   A(
                     T(f.fil_name),
                     _onClick="""
                       getElementById('id_new_filter_name').value='%(name)s';
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
        )
    for f in ac_filters:
        ac.append(SPAN(
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
                     T(f.auth_filters.fil_value),
                     _class='float',
                   ),
                   DIV(
                     _class='spacer',
                   ),
                 )
        )
    s = SPAN(
          INPUT(
            _type='hidden',
            _id='id_new_filter_name',
          ),
          H3(T('Active filters')),
          SPAN(ac+[DIV(_id='id_new_filter')]),
          H3(T('Available filters')),
          SPAN(av),
        )
    return s
