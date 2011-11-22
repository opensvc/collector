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
    db.commit()

@auth.requires_login()
def ajax_select_filter():
    fset_id = request.args[0]
    q = db.gen_filterset_user.user_id == auth.user_id
    if fset_id == "0":
        db(q).delete()
    else:
        n = db(q).count()
        if n > 1:
            db(q).delete()
            n = 0
        if n == 1:
            db(q).update(fset_id=fset_id)
        elif n == 0:
            db.gen_filterset_user.insert(user_id=auth.user_id, fset_id=fset_id)
