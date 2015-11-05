@auth.requires_login()
def save_bookmark():
    table_id = request.vars.table_id
    bookmark = request.vars.bookmark
    sql = """delete from column_filters
             where
               col_tableid="%(table_id)s" and
               user_id=%(user_id)d and
               bookmark="%(bookmark)s"
          """ % dict(
                  user_id=session.auth.user.id,
                  table_id=table_id,
                  bookmark=bookmark
                )
    db.executesql(sql)
    db.commit()

    sql = """insert into column_filters
             (
               col_tableid,
               col_name,
               col_filter,
               user_id,
               bookmark
             )
             select
               col_tableid,
               col_name,
               col_filter,
               user_id,
               "%(bookmark)s"
             from column_filters
             where
               col_tableid="%(table_id)s" and
               user_id=%(user_id)d and
               bookmark="current"
          """ % dict(
                  user_id=session.auth.user.id,
                  table_id=table_id,
                  bookmark=bookmark
                )
    db.executesql(sql)
    db.commit()

@auth.requires_login()
def ajax_set_user_prefs_column2():
    table = request.args[0]
    field = request.args[1]
    visible = request.args[2]
    if visible == "true":
        visible = 1
    else:
        visible = 0
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
def ajax_set_user_prefs_column():
    field = request.vars.get("set_col_field")
    table = request.vars.get("set_col_table")
    visible = request.vars.get("set_col_value")

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
