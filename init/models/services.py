def svc_status(svc, cellclass="cell2"):
    cl = {}
    for k in ['mon_overallstatus',
              'mon_containerstatus',
              'mon_ipstatus',
              'mon_fsstatus',
              'mon_diskstatus',
              'mon_syncstatus',
              'mon_appstatus',
              'mon_hbstatus']:
        if svc[k] is None:
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

