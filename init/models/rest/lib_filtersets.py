def lib_fset_name(id):
    q = db.gen_filtersets.id == id
    row = db(q).select().first()
    if row is None:
        return
    return row.fset_name

def lib_fset_id(name):
    q = db.gen_filtersets.fset_name == name
    row = db(q).select().first()
    if row is None:
        return
    return row.id
