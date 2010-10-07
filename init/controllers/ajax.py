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


