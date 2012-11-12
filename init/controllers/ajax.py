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
    select_filter(fset_id)
    return "saved fset id %s"%fset_id

@auth.requires_login()
def ajax_del_compare():
    compare_id = request.args[0]

    # delete user ownership
    q = db.stats_compare_user.user_id == auth.user_id
    q &= db.stats_compare_user.id == compare_id
    db(q).delete()

    # get scenario ref count
    q &= db.stats_compare_user.id == compare_id
    n_refs = db(q).count()
    if n_refs > 0:
        return

    # delete the scenario if we are the last user
    q = db.stats_compare_fset.id == compare_id
    db(q).delete()
    q = db.stats_compare.id == compare_id
    db(q).delete()

@auth.requires_login()
def ajax_select_compare():
    compare_id = request.args[0]
    q = db.stats_compare_user.user_id == auth.user_id
    if compare_id == "0":
        db(q).delete()
    else:
        n = db(q).count()
        if n > 1:
            db(q).delete()
            n = 0
        if n == 1:
            db(q).update(compare_id=compare_id)
        elif n == 0:
            db.stats_compare_user.insert(user_id=auth.user_id, compare_id=compare_id)
