data = {
 'parsers': {
   'title': 'Parsers',
   'batchs': [
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_eva'),
       'comment': "Insert EVA arrays data from uploads",
     },
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_sym'),
       'comment': "Insert Symmetrix arrays data from uploads",
     },
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_dcs'),
       'comment': "Insert DataCore arrays data from uploads",
     },
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_ibmsvc'),
       'comment': "Insert IBM SVC arrays data from uploads",
     },
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_necism'),
       'comment': "Insert NEC ISM arrays data from uploads",
     },
     {
       'url': URL(r=request, a='feed',  c='default', f='insert_brocade'),
       'comment': "Insert Brocade switches data from uploads",
     },
   ],
 },
 'disks': {
   'title': 'Disks',
   'batchs': [
     {
       'url': URL(r=request, c='disks', f='refresh_b_disk_app'),
       'comment': "Refresh the data table linking disks as viewed by the nodes with the disks as viewed by the storage arrays.",
     },
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
       'url': URL(r=request, c='cron', f='cron_alerts_daily'),
       'comment': "Daily alert janitoring",
     },
   ],
 },
}

def batchs():
    d = []
    for section, sdata in data.items():
        d.append(H1(T(sdata['title'])))
        for bdata in sdata['batchs']:
            _d = LI(A(
               P(bdata['comment']),
               _href=bdata['url'],
               _class="clickable",
            ))
            d.append(_d)
    return dict(table=DIV(d, _class="batchs"))

