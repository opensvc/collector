class log_vfields(object):
        def log_icons(self):
            return self.log.log_action

        def log_evt(self):
            try:
                d = json.loads(self.log.log_dict)
                for k in d:
                    if not isinstance(d[k], str):
                        d[k] = str(d[k])
                    d[k] = d[k].encode('utf8')
                s = T.translate(self.log.log_fmt,d)
            except KeyError:
                s = 'error parsing: %s'%self.log.log_dict
            except json.decoder.JSONDecodeError:
                s = 'error loading JSON: %s'%self.log.log_dict
            except UnicodeEncodeError:
                s = 'error transcoding: %s'%self.log.log_dict
            return s

db.log.virtualfields.append(log_vfields())

img_h = {
  'service': 'svc.png',
  'apps': 'svc.png',
  'auth': 'guys16.png',
  'users': 'guys16.png',
  'group': 'guys16.png',
  'user': 'guy16.png',
  'ack': 'check16.png',
  'compliance': 'check16.png',
  'moduleset': 'action16.png',
  'module': 'action16.png',
  'action': 'action16.png',
  'filterset': 'filter16.png',
  'filter': 'filter16.png',
  'add': 'add16.png',
  'delete': 'del16.png',
  'change': 'rename16.png',
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
        self.dbfilterable = False
        self.ajax_col_values = 'ajax_log_col_values'
        self.special_filtered_cols = ['log_icons', 'log_evt']

@auth.requires_login()
def ajax_log_col_values():
    t = table_log('log', 'ajax_log')
    col = request.args[0]
    o = db.log[col]
    q = db.log.id > 0
    t.object_list = db(q).select(orderby=o, groupby=o)
    for f in set(t.cols)-set(t.special_filtered_cols):
        q = _where(q, 'log', t.filter_parse(f), f)
    all = db(q).select()
    ids = []
    for i, row in enumerate(all):
        for f in t.special_filtered_cols:
            if not t.match_col(t.filter_parse(f), row, f):
                ids.append(row.id)
    if len(ids) > 0:
        q = ~db.log.id.belongs(ids)

    rows = db(q).select(orderby=o)
    t.object_list = map(lambda x: {col: x}, set([r[col] for r in rows]))

    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_log():
    t = table_log('log', 'ajax_log')
    o = ~db.log.log_date
    q = db.log.id > 0
    for f in set(t.cols)-set(t.special_filtered_cols):
        q = _where(q, 'log', t.filter_parse(f), f)
    n = db(q).count()
    t.setup_pager(n)

    all = db(q).select()
    ids = []
    for i, row in enumerate(all):
        for f in t.special_filtered_cols:
            if not t.match_col(t.filter_parse(f), row, f):
                ids.append(row.id)
    if len(ids) > 0:
        q = ~db.log.id.belongs(ids)

    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)

    return t.html()

@auth.requires_login()
def log():
    t = DIV(
          ajax_log(),
          _id='log',
        )
    return dict(table=t)


