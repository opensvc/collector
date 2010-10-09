@auth.requires_login()
def ajax_action_status():
    id = None
    for k in request.vars:
        if 'spin_' in k:
            id = request.vars[k]
            break

    if id is None:
        return SPAN()

    rows = db(db.SVCactions.id==id).select()

    if len(rows) != 1:
        return SPAN()

    status = rows[0].status
    if status is not None:
        def pid_to_filter(pid):
            if pid is None:
                return ''
            return pid.replace(',', '|')

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
                       'pid':pid_to_filter(rows[0].pid),
                       'hostname':rows[0].hostname,
                       'svcname':rows[0].svcname,
                       'begin':'>'+str(rows[0].begin-datetime.timedelta(days=1)),
                       'end':'<'+str(end+datetime.timedelta(days=1)),
                       'perpage':0,
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
                _onload="""
                  var spintimer_%(id)s;
                  clearTimeout(spintimer_%(id)s);
                  spintimer=setTimeout(function validate(){ajax('%(url)s',
['spin_%(id)s'], 'spin_span_%(id)s')}, 3000);
                """%dict(
                      url=URL(r=request,f='ajax_action_status'),
                      id=id,
                    )
              )

@auth.requires_login()
def _svcaction_ack(request):
    action_ids = ([])
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        action_ids += ([key[6:]])
    for action_id in action_ids:
        query = (db.v_svcactions.id == action_id)&(db.v_svcactions.status != "ok")
        rows = db(query).select()
        if len(rows) != 1:
            continue
        a = rows[0]
        _svcaction_ack_one(request, action_id)

    if 'ackcomment' in request.vars:
        del request.vars.ackcomment


@auth.requires_login()
def _svcaction_ack_one(request, action_id):
        query = (db.v_svcactions.id == action_id)&(db.v_svcactions.status != "ok")
        db(query).update(ack=1,
                         acked_comment=request.vars.ackcomment,
                         acked_by=user_name(),
                         acked_date=datetime.datetime.now())

@auth.requires_login()
def svcactions():
    columns = dict(
        svcname = dict(
            pos = 1,
            title = T('Service'),
            display = True,
            img = 'svc',
            size = 10
        ),
        hostname = dict(
            pos = 2,
            title = T('Node name'),
            display = True,
            img = 'node16',
            size = 6
        ),
        pid = dict(
            pos = 3,
            title = T('Pid'),
            display = True,
            img = 'action16',
            size = 4
        ),
        action = dict(
            pos = 4,
            title = T('Action'),
            display = True,
            img = 'action16',
            size = 6
        ),
        status = dict(
            pos = 5,
            title = T('Status'),
            display = True,
            img = 'action16',
            size = 3
        ),
        begin = dict(
            pos = 6,
            title = T('Begin'),
            display = True,
            img = 'action16',
            size = 6
        ),
        end = dict(
            pos = 7,
            title = T('End'),
            display = True,
            img = 'action16',
            size = 6
        ),
        status_log = dict(
            pos = 8,
            title = T('Log'),
            display = True,
            img = 'action16',
            size = 10
        ),
        time = dict(
            pos = 9,
            title = T('Duration'),
            display = False,
            img = 'action16',
            size = 10
        ),
        id = dict(
            pos = 10,
            title = T('Id'),
            display = False,
            img = 'action16',
            size = 3
        ),
        ack = dict(
            pos = 11,
            title = T('Ack'),
            display = False,
            img = 'action16',
            size = 3
        ),
        app = dict(
            pos = 12,
            title = T('App'),
            display = False,
            img = 'svc',
            size = 3
        ),
        responsibles = dict(
            pos = 13,
            title = T('Responsibles'),
            display = False,
            img = 'guy16',
            size = 6
        ),
    )

    def _sort_cols(x, y):
        return cmp(columns[x]['pos'], columns[y]['pos'])
    colkeys = columns.keys()
    colkeys.sort(_sort_cols)
    __update_columns(columns, 'svcactions')

    o = ~db.v_svcactions.begin|~db.v_svcactions.end|~db.v_svcactions.id

    toggle_db_filters()

    if request.vars.ackflag == "1":
        _svcaction_ack(request)

    # filtering
    query = (db.v_svcactions.id>0)
    for key in columns.keys():
        if key not in request.vars.keys():
            continue
        query &= _where(None, 'v_svcactions', request.vars[key], key)

    query &= _where(None, 'v_svcactions', domain_perms(), 'hostname')

    query = apply_db_filters(query, 'v_svcactions')

    (start, end, nav) = _pagination(request, query)
    if start == 0 and end == 0:
        rows = db(query).select(orderby=o)
    else:
        rows = db(query).select(orderby=o, limitby=(start,end))

    return dict(columns=columns, colkeys=colkeys, actions=rows,
                active_filters=active_db_filters('v_svcactions'),
                available_filters=avail_db_filters('v_svcactions'),
                nav=nav)

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

@auth.requires_login()
def svcactions_csv():
    import gluon.contenttype
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    request.vars['perpage'] = 0
    return str(svcactions()['actions'])


