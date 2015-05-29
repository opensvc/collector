def svc_status(svc, cellclass="cell2"):
    cl = {}
    if svc['mon_updated'] < now - datetime.timedelta(minutes=15):
        outdated = True
    else:
        outdated = False

    for k in ['mon_overallstatus',
              'mon_containerstatus',
              'mon_ipstatus',
              'mon_fsstatus',
              'mon_diskstatus',
              'mon_syncstatus',
              'mon_appstatus',
              'mon_hbstatus']:
        if svc[k] is None or outdated:
            cl[k] = 'status_undef'
        else:
            cl[k] = 'status_'+svc[k].replace(" ", "_")

    t = TABLE(
      TR(
        TD(svc.mon_overallstatus,
           _colspan=7,
           _class=cellclass+' status '+cl['mon_overallstatus'],
        ),
      ),
      TR(
        TD("vm", _class=cellclass+' '+cl['mon_containerstatus']),
        TD("ip", _class=cellclass+' '+cl['mon_ipstatus']),
        TD("fs", _class=cellclass+' '+cl['mon_fsstatus']),
        TD("dg", _class=cellclass+' '+cl['mon_diskstatus']),
        TD("sync", _class=cellclass+' '+cl['mon_syncstatus']),
        TD("app", _class=cellclass+' '+cl['mon_appstatus']),
        TD("hb", _class=cellclass+' '+cl['mon_hbstatus']),
      ),
    )
    return t

def dash_purge_svc(svcname):
    q = db.dashboard.dash_svcname == svcname
    db(q).delete()

def check_purge_svc(svcname):
    q = db.checks_live.chk_svcname == svcname
    db(q).delete()

def appinfo_purge_svc(svcname):
    q = db.appinfo.app_svcname == svcname
    db(q).delete()

def purge_svc(svcname):
    q = db.svcmon.mon_svcname == svcname
    if db(q).count() > 0:
        return
    dash_purge_svc(svcname)
    check_purge_svc(svcname)
    appinfo_purge_svc(svcname)
    update_dash_compdiff_svc(svcname)
    update_dash_moddiff(svcname)
    update_dash_rsetdiff(svcname)

    q = db.services.svc_name == svcname
    db(q).delete()


