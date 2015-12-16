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
                     _class='datetime_no_age',
                     default_filter='>-1d',
                    ),
            'log_icons': HtmlTableColumn(
                     title='Icons',
                     field='log_icons',
                     img='action16',
                     display=True,
                     _class="log_icons",
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
    table_id = request.vars.table_id
    t = table_log(table_id, 'ajax_log')
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
    table_id = request.vars.table_id
    t = table_log(table_id, 'ajax_log')

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
        n = db(q).count()
        limitby = (t.pager_start,t.pager_end)
        t.object_list = db(q).select(limitby=limitby, orderby=o, cacheable=False)
        return t.table_lines_data(n)

@auth.requires_login()
def log():
    t = SCRIPT(
          """$.when(osvc.app_started).then(function(){ table_log("layout", %s) })""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def log_load():
    return log()["table"]


