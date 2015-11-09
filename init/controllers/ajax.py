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
