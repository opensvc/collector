def pid_to_filter(pid):
    if pid is None:
        return ''
    return pid.replace(',', '|')

@auth.requires_login()
def ajax_action_status():
    if len(request.args) == 0:
        return SPAN()
    id = int(request.args[0])

    rows = db(db.SVCactions.id==id).select()

    if len(rows) != 1:
        return SPAN('action not found')

    status = rows[0].status
    if status is not None:
        if rows[0].end is None:
            end = rows[0].begin
        else:
            end = rows[0].end
            pass

        pid = A(
             rows[0].pid,
             _href=URL(
                     r=request,
                     f='svcactions',
                     vars={
                       'actions_f_pid':pid_to_filter(rows[0].pid),
                       'actions_f_hostname':rows[0].hostname,
                       'actions_f_svcname':rows[0].svcname,
                       'actions_f_begin':'>'+str(rows[0].begin-datetime.timedelta(days=1)),
                       'actions_f_end':'<'+str(end+datetime.timedelta(days=1)),
                       'actions_f_perpage':0,
                       'clear_filters': 'true',
                     }
          ),
        )
        return SPAN(
                 IMG(
                   _src=URL(r=request,c='static',f='action16.png'),
                   _border=0,
                   _onload="""
                     document.getElementById('spin_span_pid_%(id)s').innerHTML='%(pid)s';
                     document.getElementById('spin_span_end_%(id)s').innerHTML='%(end)s';
                   """%dict(
                         id=id,
                         pid=pid,
                         end=rows[0].end,
                       ),
                   _style='display:none',
                 ),
                 status,
                 _class="status_"+status,
               )
    else:
        return IMG(
                _src=URL(r=request,c='static',f='spinner_16.png'),
                _border=0,
                _title=T("unfinished"),
                _onload="""refresh_action('%(url)s', '%(id)s')"""%dict(
                      url=URL(r=request,f='ajax_action_status', args=[id]),
                      id=id,
                    )
              )

def svcactions_rss():
    #return BEAUTIFY(request)
    import gluon.contrib.rss2 as rss2
    import datetime
    d = svcactions()
    url = request.url[:-4]
    items = []
    desc = 'filtering options for this feed: '
    for key in request.vars.keys():
        if request.vars[key] != '': desc += key+'['+request.vars[key]+'] '
    for action in d['actions']:
        items += [rss2.RSSItem(title="""[osvc] %s %s returned %s"""%(action.action,action.svcname,action.status),
                      link = """http://%s%s?id==%s"""%(request.env.http_host,url,action.id),
                      description="""<b>id:</b> %s<br><b>begin:</b> %s<br>%s"""%(action.begin,action.id,action.status_log))]
    rss = rss2.RSS2(title="OpenSVC actions",
                link = """http://%s%s?%s"""%(request.env.http_host,url,request.env.query_string),
                description = desc,
                lastBuildDate = datetime.datetime.now(),
                items = items
    )
    response.headers['Content-Type']='application/rss+xml'
    return rss2.dumps(rss)

class col_svcactions_status(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        c = 'status_undef'
        id = self.t.colprops['id'].get(o)
        if s is not None:
            c = 'status_'+s.replace(" ", "_")
        if self.t.colprops['ack'].get(o) == 1:
            c += ' ack_1'
            msg = SPAN(
                    B("acked by "),
                    self.t.colprops['acked_by'].get(o),
                    B(" on "),
                    self.t.colprops['acked_date'].get(o),
                    B(" with comment: "),
                    self.t.colprops['acked_comment'].get(o),
                  )
            over = """ackpanel(true, '%s')"""%msg
            out = """ackpanel(false, '%s')"""%msg
        else:
            over = ''
            out = ''
        if s is None:
            action_status = SPAN(
              SPAN(
                IMG(
                  _src=URL(r=request,c='static',f='spinner_16.png'),
                  _border=0,
                  _title=T("unfinished"),
                  _onload="""refresh_action('%(url)s', '%(id)s')"""%dict(
                        url=URL(r=request,f='ajax_action_status', args=[id]),
                        id=id,
                      )
                ),
                _id="spin_span_"+str(id),
              ),
            )
        else:
            action_status = s

        d = SPAN(
              action_status,
              _onmouseover=over,
              _onmouseout=out,
              _class=c,
            )
        return d

class col_action(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        action = s.split()[-1]
        c ='action'
        if self.t.colprops['status_log'].get(o) is None:
            c = 'metaaction'
        if action in action_img_h:
            img = IMG(_src=URL(r=request,c='static',f=action_img_h[action]))
        else:
            img = ''
        d = SPAN(
              img,
              s,
              _class=c,
              _id='spin_span_%s'%str(id)
            )
        return d

class col_begin(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        return SPAN(
                 s,
                 _class='nowrap',
               )

class col_end(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        id = self.t.colprops['id'].get(o)
        if s is None:
            s = ''
        return SPAN(
                 s,
                 _id='spin_span_end_%s'%id,
                 _class='nowrap',
               )

class col_pid(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        id = self.t.colprops['id'].get(o)
        if s is None:
            pid = ''
        else:
            pid = A(
                 o.pid,
                 _href=URL(
                         r=request,
                         f='svcactions',
                         vars={
                           'actions_f_pid':pid_to_filter(o.pid),
                           'actions_f_hostname':o.hostname,
                           'actions_f_svcname':o.svcname,
                           'actions_f_begin':'>'+str(o.begin-datetime.timedelta(days=1)),
                           'actions_f_end':'<'+str(o.end+datetime.timedelta(days=1)),
                           'actions_f_perpage':0,
                           'clear_filters': 'true',
                         }
              ),
            )
        return SPAN(pid, _id='spin_span_pid_%s'%id)

class col_status_log(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        if s is None:
            s = ''
        return PRE(s)

class table_actions(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['svcname',
                     'hostname',
                     'pid',
                     'action',
                     'status',
                     'begin',
                     'end',
                     'time',
                     'id',
                     'status_log',
                     'ack',
                     'acked_by',
                     'acked_date',
                     'acked_comment',
                    ]
        self.colprops = {
            'svcname': col_svc(
                title = 'Service',
                table = 'v_svcactions',
                field='svcname',
                display = True,
                img = 'svc',
            ),
            'hostname': col_node(
                title = 'Node name',
                table = 'v_svcactions',
                field='hostname',
                display = True,
                img = 'node16',
            ),
            'pid': col_pid(
                title = 'Pid',
                table = 'v_svcactions',
                field='pid',
                display = True,
                img = 'action16',
            ),
            'action': col_action(
                title = 'Action',
                table = 'v_svcactions',
                field='action',
                display = True,
                img = 'action16',
            ),
            'status': col_svcactions_status(
                title = 'Status',
                table = 'v_svcactions',
                field='status',
                display = True,
                img = 'action16',
            ),
            'begin': col_begin(
                title = 'Begin',
                table = 'v_svcactions',
                field='begin',
                display = True,
                img = 'time16',
            ),
            'end': col_end(
                title = 'End',
                table = 'v_svcactions',
                field='end',
                display = False,
                img = 'time16',
            ),
            'status_log': col_status_log(
                title = 'Log',
                table = 'v_svcactions',
                field='status_log',
                display = True,
                img = 'action16',
            ),
            'time': HtmlTableColumn(
                title = 'Duration',
                table = 'v_svcactions',
                field='time',
                display = False,
                img = 'time16',
            ),
            'id': HtmlTableColumn(
                title = 'Id',
                table = 'v_svcactions',
                field='id',
                display = False,
                img = 'action16',
            ),
            'ack': HtmlTableColumn(
                title = 'Ack',
                table = 'v_svcactions',
                field='ack',
                display = False,
                img = 'action16',
            ),
            'acked_comment': HtmlTableColumn(
                title = 'Ack comment',
                table = 'v_svcactions',
                field='acked_comment',
                display = False,
                img = 'action16',
            ),
            'acked_by': HtmlTableColumn(
                title = 'Acked by',
                table = 'v_svcactions',
                field='acked_by',
                display = False,
                img = 'guy16',
            ),
            'acked_date': HtmlTableColumn(
                title = 'Ack date',
                table = 'v_svcactions',
                field='acked_date',
                display = False,
                img = 'time16',
            ),
            'app': HtmlTableColumn(
                title = 'App',
                table = 'v_svcactions',
                field='app',
                display = False,
                img = 'svc',
            ),
        }
        cp = v_nodes_colprops
        del(cp['status'])
        self.colprops.update(cp)
        self.colprops.update(v_services_colprops)
        ncols = v_nodes_cols
        ncols.remove('updated')
        ncols.remove('power_supply_nb')
        ncols.remove('power_cabinet1')
        ncols.remove('power_cabinet2')
        ncols.remove('power_protect')
        ncols.remove('power_protect_breaker')
        ncols.remove('power_breaker1')
        ncols.remove('power_breaker2')
        ncols.remove('status')
        self.cols += ncols
        self.cols.append('responsibles')
        self.cols.append('mailto')
        for c in self.cols:
            self.colprops[c].t = self
        self.ajax_col_values = 'ajax_actions_col_values'
        self.extraline = True
        self.span = 'pid'
        self.sub_span = ['hostname', 'svcname', 'action'] + ncols
        self.dbfilterable = True
        self.checkboxes = True
        self.checkbox_id_table = 'v_svcactions'
        self.additional_tools.append('ack')

    def checkbox_disabled(self, o):
        status = self.colprops['status'].get(o)
        ack = self.colprops['ack'].get(o)
        if status == 'err' and ack != 1:
            return False
        return True

    def ack(self):
        d = DIV(
              A(
                T("Acknowledge error"),
                _onclick="""
                  click_toggle_vis('%(div)s', 'block');
                """%dict(div='ackcomment_d'),
              ),
              DIV(
                TABLE(
                  TR(
                    TD(
                      T('Comment'),
                    ),
                    TD(
                      INPUT(
                       _id='ackcomment',
                       _onkeypress="if (is_enter(event)) {%s};"%\
                          self.ajax_submit(additional_inputs=['ackcomment'],
                                           args="ack"),

                      ),
                    ),
                  ),
                ),
                _style='display:none',
                _class='white_float',
                _name='ackcomment_d',
                _id='ackcomment_d',
              ),
              _class='floatw',
            )
        return d

@auth.requires_login()
def ajax_actions_col_values():
    t = table_actions('actions', 'ajax_actions')
    col = request.args[0]
    o = db.v_svcactions[col]
    q = _where(None, 'v_svcactions', domain_perms(), 'hostname')
    q = apply_db_filters(q, 'v_services')
    for f in t.cols:
        q = _where(q, 'v_svcactions', t.filter_parse(f), f)
    t.object_list = db(q).select(db.v_svcactions[col],
                                 groupby=o,
                                 orderby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ack(ids=[]):
    if len(ids) == 0:
        raise ToolError("no action selected")
    ackcomment = request.vars.ackcomment
    for action_id in ids:
        query = (db.SVCactions.id == action_id)&(db.SVCactions.status != "ok")
        rows = db(query).select()
        if len(rows) != 1:
            continue
        a = rows[0]
        _svcaction_ack_one(ackcomment, action_id)

    if 'ackcomment' in request.vars:
        del request.vars.ackcomment

    _log('action.ack',
         'acknowledged action error with pids %(g)s',
         dict(g=', '.join(map(str, ids))))

@auth.requires_login()
def _svcaction_ack_one(ackcomment, action_id):
        query = (db.SVCactions.id == action_id)&(db.SVCactions.status != "ok")
        db(query).update(ack=1,
                         acked_comment=ackcomment,
                         acked_by=user_name(),
                         acked_date=datetime.datetime.now())

@auth.requires_login()
def ajax_actions():
    t = table_actions('actions', 'ajax_actions')

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'ack':
                ack(t.get_checked())
        except ToolError, e:
            t.flash = str(e)

    o = ~db.v_svcactions.begin|~db.v_svcactions.end|~db.v_svcactions.id
    q = _where(None, 'v_svcactions', domain_perms(), 'hostname')
    q = apply_db_filters(q, 'v_services')
    for f in t.cols:
        q = _where(q, 'v_svcactions', t.filter_parse(f), f)
    n = db(q).count()
    t.setup_pager(n)
    #raise Exception(db(q)._select(limitby=(t.pager_start,t.pager_end), orderby=o))
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return SPAN(
              DIV(
               _id='ackpanel',
               _class='ackpanel',
              ),
              t.html(),
            )

@auth.requires_login()
def svcactions():
    t = DIV(
          ajax_actions(),
          _id='actions',
        )
    return dict(table=t)


