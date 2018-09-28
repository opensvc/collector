def dash_purge_svc(svc_id):
    q = db.dashboard.svc_id == svc_id
    db(q).delete()

def check_purge_svc(svc_id):
    q = db.checks_live.svc_id == svc_id
    db(q).delete()

def resinfo_purge_svc(svc_id):
    q = db.resinfo.svc_id == svc_id
    db(q).delete()

def purge_svc(svc_id):
    q = db.svcmon.svc_id == svc_id
    if db(q).count() > 0:
        return
    dash_purge_svc(svc_id)
    check_purge_svc(svc_id)
    resinfo_purge_svc(svc_id)
    update_dash_compdiff_svc(svc_id)
    update_dash_moddiff(svc_id)
    update_dash_rsetdiff(svc_id)

    q = db.services.svc_id == svc_id
    db(q).delete()

def delete_svc_from_table(t, svc_id):
    sql = """delete from %s where svc_id="%s" """ % (t, svc_id)
    db.executesql(sql)
    try:
        counter = db._adapter.cursor.rowcount
    except:
        counter = None
    if counter:
        ws_send(t+'_change', {'svc_id': svc_id})

