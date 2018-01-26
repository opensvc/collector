data = {
 'nodes': {
   'title': 'Nodes',
   'batchs': [
     {
       'url': URL(r=request, c='cron', f='cron_update_virtual_asset'),
       'comment': "Copy the location and power feed information from hypervisors to virtual machine nodes table entries",
     },
   ],
 },
 'parsers': {
   'title': 'Parsers',
   'batchs': [
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_centeras'),
       'comment': "Insert Centera arrays data from uploads",
     },
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_dcss'),
       'comment': "Insert DataCore arrays data from uploads",
     },
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_emcvnxs'),
       'comment': "Insert VNX arrays data from uploads",
     },
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_evas'),
       'comment': "Insert EVA arrays data from uploads",
     },
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_freenass'),
       'comment': "Insert FreeNAS arrays data from uploads",
     },
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_gcediskss'),
       'comment': "Insert GCloud arrays data from uploads",
     },
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_hdss'),
       'comment': "Insert Hitachi arrays data from uploads",
     },
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_hp3pars'),
       'comment': "Insert HP 3par arrays data from uploads",
     },
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_ibmsvcs'),
       'comment': "Insert IBM SVC arrays data from uploads",
     },
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_necisms'),
       'comment': "Insert NEC ISM arrays data from uploads",
     },
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_netapps'),
       'comment': "Insert NetApp arrays data from uploads",
     },
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_syms'),
       'comment': "Insert Symmetrix arrays data from uploads",
     },
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_vioservers'),
       'comment': "Insert IBM VirtualIO arrays data from uploads",
     },
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_xtremios'),
       'comment': "Insert XtremIO arrays data from uploads",
     },
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_brocades'),
       'comment': "Insert Brocade switches data from uploads",
     },
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_nsrs'),
       'comment': "Insert Networker Backup index data from uploads",
     },
   ],
 },
 'disks': {
   'title': 'Disks',
   'batchs': [
     {
       'url': URL(r=request, c='disks', f='purge_diskinfo'),
       'comment': "Purge the disk information table",
     },
   ],
 },
 'stats': {
   'title': 'Statistics',
   'batchs': [
     {
       'url': URL(r=request, c='cron', f='cron_stat_day'),
       'comment': "Collect per filterset site statistics",
     },
     {
       'url': URL(r=request, c='cron', f='cron_stat_day_svc'),
       'comment': "Collect per filterset service statistics",
     },
     {
       'url': URL(r=request, c='cron', f='cron_stat_day_disk_app'),
       'comment': "Collect per application code disk allocations",
     },
   ],
 },
 'alerts': {
   'title': 'Alerts',
   'batchs': [
     {
       'url': URL(r=request, c='cron', f='cron_alerts_hourly'),
       'comment': "Hourly alert janitoring",
     },
     {
       'url': URL(r=request, c='cron', f='cron_alerts_daily'),
       'comment': "Daily alert janitoring",
     },
     {
       'url': URL(r=request, a='feed', c='default', f='batch_update_save_checks'),
       'comment': "Refresh save checks thresholds and alerts",
     },
     {
       'url': URL(r=request, a='feed', c='default', f='batch_update_dash_checks_all'),
       'comment': "Refresh checks alerts",
     },
   ],
 },
 'obsolescence': {
   'title': 'Obsolescence',
   'batchs': [
     {
       'url': URL(r=request, c='obsolescence', f='_update_dash_obs_os_alert'),
       'comment': "Refresh os alerts",
     },
     {
       'url': URL(r=request, c='obsolescence', f='_update_dash_obs_os_warn'),
       'comment': "Refresh os warnings",
     },
     {
       'url': URL(r=request, c='obsolescence', f='_update_dash_obs_hw_alert'),
       'comment': "Refresh hardware alerts",
     },
     {
       'url': URL(r=request, c='obsolescence', f='_update_dash_obs_hw_warn'),
       'comment': "Refresh hardware warnings",
     },
     {
       'url': URL(r=request, c='obsolescence', f='purge_dash_obs_without'),
       'comment': "Purge obsolescence alerts and warnings",
     },
   ],
 },
 'docker': {
   'title': 'Docker Registries',
   'batchs': [
     {
       'url': URL(r=request, c='registry', f='discover_registries'),
       'comment': "Refresh docker registries indexes",
     },
   ],
 },
}

def batchs():
    d = []
    for section, sdata in data.items():
        d.append(H1(T(sdata['title'])))
        l = []
        for bdata in sdata['batchs']:
            _d = LI(A(
               bdata['comment'],
               _href=bdata['url'],
               _class="clickable",
            ))
            l.append(_d)
        d.append(P(l))
    return dict(table=DIV(d, _class="batchs"))

def batchs_load():
    return batchs()["table"]

def migrate_metrics_wsp():
    from applications.init.modules import timeseries
    sql = """select metric_id, fset_id, instance, value, date from metrics_log"""
    for row in db.executesql(sql):
        if row[3] is None:
            continue
        path = timeseries.wsp_path("metrics", row[0], "fsets", row[1], row[2])
        timeseries.whisper_update(path, row[3], row[4], retentions=timeseries.daily_retentions)

