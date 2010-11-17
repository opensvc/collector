class log_vfields(object):
        def log_icons(self):
            return self.log.log_action

        def log_evt(self):
            try:
                s = self.log.log_fmt%simplejson.loads(self.log.log_dict)
            except:
                s = 'error parsing: %s'%self.log.log_dict
            return s

db.log.virtualfields.append(log_vfields())

img_h = {
  'compliance': 'check16.png',
  'moduleset': 'action16.png',
  'module': 'action16.png',
  'filterset': 'filter16.png',
  'filter': 'filter16.png',
  'add': 'add16.png',
  'delete': 'del16.png',
  'rename': 'rename16.png',
  'attach': 'attach16.png',
  'detach': 'detach16.png',
}

class col_log_icons(HtmlTableColumn):
    def html(self, o):
        t = self.get(o)
        l = t.split('.')
        i = []
        d = []
        for w in l:
            if w not in img_h or img_h[w] in d:
                continue
            d.append(img_h[w])
            i.append(IMG( _src=URL(r=request,c='static',f=img_h[w])))
        return SPAN(i)

class table_log(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['log_date',
                     'log_icons',
                     'log_action',
                     'log_user',
                     'log_evt']
        self.colprops = {
            'log_date': HtmlTableColumn(
                     title='Date',
                     field='log_date',
                     img='time16',
                     display=True,
                    ),
            'log_icons': col_log_icons(
                     title='Icons',
                     field='log_icons',
                     img='action16',
                     display=True,
                    ),
            'log_action': HtmlTableColumn(
                     title='Action',
                     field='log_action',
                     img='action16',
                     display=True,
                    ),
            'log_user': HtmlTableColumn(
                     title='User',
                     field='log_user',
                     img='guy16',
                     display=True,
                    ),
            'log_evt': HtmlTableColumn(
                     title='Event',
                     field='log_evt',
                     img='log16',
                     display=True,
                    ),
        }

@auth.requires_login()
def ajax_log():
    t = table_log('log', 'ajax_log')

    o = ~db.log.log_date
    q = db.log.id > 0
    for f in t.cols:
        q = _where(q, 'log', t.filter_parse(f), f)

    n = db(q).count()
    t.set_pager_max(n)

    if t.pager_start == 0 and t.pager_end == 0:
        all = db(q).select(orderby=o)
        t.object_list = all
    else:
        all = db(q).select(orderby=o)
        t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)

    return t.html()

@auth.requires_login()
def log():
    t = DIV(
          ajax_log(),
          _id='log',
        )
    return dict(table=t)


