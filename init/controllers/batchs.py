data = {
 'disks': {
   'title': 'Disks',
   'batchs': [
     {
       'url': URL(r=request, c='disks', f='b_refresh_app'),
       'comment': "Refresh the data table linking disks as viewed by the nodes with the disks as viewed by the storage arrays.",
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

