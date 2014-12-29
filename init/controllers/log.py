img_h = {
  'checks': 'check16.png',
  'networks': 'net16.png',
  'dns': 'dns16.png',
  'service': 'svc.png',
  'apps': 'svc.png',
  'auth': 'guys16.png',
  'users': 'guys16.png',
  'group': 'guys16.png',
  'user': 'guy16.png',
  'ack': 'check16.png',
  'compliance': 'comp16.png',
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
  'password': 'lock.png',
}

class col_log_evt(HtmlTableColumn):
    def get(self, o):
        try:
            d = json.loads(o.log_dict)
            for k in d:
                if isinstance(d[k], str) or isinstance(d[k], unicode):
                    d[k] = d[k].encode('utf8')
            s = T.translate(o.log_fmt,d)
        except KeyError:
            s = 'error parsing: %s'%o.log_dict
        except json.decoder.JSONDecodeError:
            s = 'error loading JSON: %s'%o.log_dict
        except UnicodeEncodeError:
            s = 'error transcoding: %s'%o.log_dict
        except TypeError:
            s = 'type error: %s'%o.log_dict
        except ValueError:
            s = 'value error: %s %% %s'%(o.log_fmt, o.log_dict)
        except AttributeError as e:
            s = 'attribute error: '+str(e)
        except Exception as e:
            s = str(e)
        return s

class col_log_icons(HtmlTableColumn):
    def get(self, o):
        return o.log_action

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

class col_log_level(HtmlTableColumn):
    def html(self, o):
       d = self.get(o)
       if d == "info":
           return DIV(d, _class="boxed_small bggreen")
       elif d == "warning":
           return DIV(d, _class="boxed_small bgorange")
       elif d == "error":
           return DIV(d, _class="boxed_small bgred")
       else:
           return DIV(d, _class="boxed_small bgblack")

class table_log(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'log_date',
                     'log_icons',
                     'log_level',
                     'log_svcname',
                     'log_nodename',
                     'log_user',
                     'log_action',
                     'log_evt',
                     'log_gtalk_sent',
                     'log_email_sent']
        self.colprops = {
            'id': HtmlTableColumn(
                     title='Id',
                     field='id',
                     img='action16',
                     display=False,
                    ),
            'log_date': HtmlTableColumn(
                     title='Date',
                     field='log_date',
                     img='time16',
                     display=True,
                     default_filter='>-1d',
                    ),
            'log_icons': col_log_icons(
                     title='Icons',
                     field='log_icons',
                     img='action16',
                     display=True,
                    ),
            'log_level': col_log_level(
                     title='Severity',
                     field='log_level',
                     img='action16',
                     display=True,
                    ),
            'log_action': HtmlTableColumn(
                     title='Action',
                     field='log_action',
                     img='action16',
                     display=True,
                    ),
            'log_svcname': HtmlTableColumn(
                     title='Service',
                     field='log_svcname',
                     img='svc',
                     display=True,
                     _class='svcname',
                    ),
            'log_nodename': HtmlTableColumn(
                     title='Node',
                     field='log_nodename',
                     img='node16',
                     display=True,
                     _class='nodename',
                    ),
            'log_user': HtmlTableColumn(
                     title='User',
                     field='log_user',
                     img='guy16',
                     display=True,
                     _class='username',
                    ),
            'log_evt': col_log_evt(
                     title='Event',
                     field='dummy',
                     img='log16',
                     filter_redirect='log_dict',
                     display=True,
                    ),
            'log_fmt': HtmlTableColumn(
                     title='Format',
                     field='log_fmt',
                     img='log16',
                     display=False,
                    ),
            'log_dict': HtmlTableColumn(
                     title='Dictionary',
                     field='log_dict',
                     img='log16',
                     display=False,
                    ),
            'log_entry_id': HtmlTableColumn(
                     title='Entry id',
                     field='log_entry_id',
                     img='log16',
                     display=False,
                    ),
            'log_gtalk_sent': HtmlTableColumn(
                     title='Sent via gtalk',
                     field='log_gtalk_sent',
                     img='log16',
                     display=False,
                    ),
            'log_email_sent': HtmlTableColumn(
                     title='Sent via email',
                     field='log_email_sent',
                     img='log16',
                     display=False,
                    ),
        }
        self.colprops['log_nodename'].t = self
        self.colprops['log_svcname'].t = self
        self.dbfilterable = False
        self.extraline = True
        self.wsable = True
        self.keys = ["id"]
        self.span = ["id"]
        self.ajax_col_values = 'ajax_log_col_values'
        self.special_filtered_cols = ['log_icons', 'log_evt']

@auth.requires_login()
def ajax_log_col_values():
    t = table_log('log', 'ajax_log')
    col = request.args[0]
    if t.colprops[col].filter_redirect is None:
        o = db.log[col]
        s = [db.log[col]]
    else:
        o = db.log[t.colprops[col].filter_redirect]
        s = [db.log.log_fmt, db.log.log_dict]
    q = db.log.id > 0
    for f in set(t.cols)-set(['log_evt']):
        q = _where(q, 'log', t.filter_parse(f),  f)
    q = _where(q, 'log', t.filter_parse('log_evt'),  'log_dict')
    t.object_list = db(q).select(*s, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_log():
    t = table_log('log', 'ajax_log')

    o = ~db.log.log_date
    q = db.log.id > 0
    for f in set(t.cols):
        q = _where(q, 'log', t.filter_parse(f),  f if t.colprops[f].filter_redirect is None else t.colprops[f].filter_redirect)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'line':
        if request.vars.volatile_filters is None:
            n = db(q).count()
            limitby = (t.pager_start,t.pager_end)
        else:
            n = 0
            limitby = (0, 500)
        t.object_list = db(q).select(limitby=limitby, orderby=o, cacheable=False)
        return t.table_lines_data(n)

    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)

    return DIV(
             t.html(),
             SCRIPT("""
function ws_action_switch_%(divid)s(data) {
        if (data["event"] == "log_change") {
          _data = []
          _data.push({"key": "id", "val": data["data"]["id"], "op": "="})
          osvc.tables["%(divid)s"].insert(_data)
        }
}
wsh["%(divid)s"] = ws_action_switch_%(divid)s
              """ % dict(
                     divid=t.innerhtml,
                    )
              ),
            )


@auth.requires_login()
def log():
    t = DIV(
          ajax_log(),
          _id='log',
        )
    return dict(table=t)


class table_log_node(table_log):
    def __init__(self, id=None, func=None, innerhtml=None):
        table_log.__init__(self, id, func, innerhtml)
        self.hide_tools = True
        self.pageable = False
        self.bookmarkable = False
        self.commonalityable = False
        self.linkable = False
        self.checkboxes = True
        self.filterable = False
        self.exportable = False
        self.dbfilterable = False
        self.columnable = False
        self.refreshable = False
        self.wsable = False
        self.dataable = True
        self.child_tables = []

def ajax_log_node():
    tid = request.vars.table_id
    t = table_log_node(tid, 'ajax_log_node')
    o = ~db.log.log_date
    q = _where(None, 'log', domain_perms(), 'log_nodename')
    for f in ['log_nodename']:
        q = _where(q, 'log', t.filter_parse(f), f)
    if request.args[0] == "data":
        t.object_list = db(q).select(cacheable=True, orderby=o, limitby=(0,20))
        return t.table_lines_data(-1, html=False)

def ajax_log_svc():
    tid = request.vars.table_id
    t = table_log_node(tid, 'ajax_log_svc')
    o = ~db.log.log_date
    q = _where(None, 'log', domain_perms(), 'log_svcname')
    for f in ['svcname']:
        q = _where(q, 'v_svclog', t.filter_parse(f), f)
    if request.args[0] == "data":
        t.object_list = db(q).select(cacheable=True, orderby=o, limitby=(0,20))
        return t.table_lines_data(-1, html=False)

@auth.requires_login()
def log_node():
    node = request.args[0]
    tid = 'log_'+node.replace('-', '_').replace('.', '_')
    t = table_log_node(tid, 'ajax_log_node')
    t.colprops['log_nodename'].force_filter = node

    return DIV(
             t.html(),
             _id=tid,
           )

@auth.requires_login()
def log_svc():
    svcname = request.args[0]
    tid = 'log_'+svcname.replace('-','_').replace('.','_')
    t = table_log_node(tid, 'ajax_log_svc')
    t.colprops['log_svcname'].force_filter = svcname

    return DIV(
             t.html(),
             _id=tid,
           )


