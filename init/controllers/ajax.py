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


