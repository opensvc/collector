from pychart import *

@auth.requires_login()
def svcmon_log_global_chart(rows):
    import datetime

    begin = rows[0].svcmon_log.mon_begin
    end = rows[-1].svcmon_log.mon_end
    interval = datetime.timedelta(minutes=60)

    """ setup the sampling
    """
    ticks = []
    b = begin
    while b <= end:
        ticks.append(b)
        b += interval

    """ determine the chart stacks
    """
    cols = set([])
    for row in rows:
        cols |= set(['-'.join((row.v_svcmon.mon_nodtype, row.svcmon_log.mon_overallstatus))])

    """ sample
    """
    data = []
    for tick in ticks:
        d = {}
        for row in rows:
            if tick < row.svcmon_log.mon_begin or tick >row.svcmon_log.mon_end:
                continue
            key = '-'.join((row.v_svcmon.mon_nodtype,row.svcmon_log.mon_overallstatus)) 
            if key not in d:
                d[key] = 1
            else:
                d[key] += 1
        u = [tick]
        for col in cols:
            if col in d:
                u.append(d[col])
            else:
                u.append(0)
        data.append(u)

    """ chart
    """
    def tic_start_ts(begin, end):
        from time import mktime
        start_date = mktime(begin.timetuple())
        end_date = mktime(end.timetuple())
        p = end_date - start_date
        if p < 86400:
            """ align start to closest preceding hour
            """
            start_date = ((start_date // 3600) + 1) * 3600
        else:
            """ align start to closest preceding day
            """
            start_date = ((start_date // 86400) + 1) * 86400
        return start_date

    w = __stats_bar_width(data)

    from time import mktime

    start_date = tic_start_ts(begin, end)

    def format_x(ts):
        d = datetime.datetime.fromtimestamp(ts+start_date)
        return "/a50/5{}" + d.strftime("%y-%m-%d %H:%M")

    def format_y(x):
        return "/6{}" + str(x)

    def format2_y(x):
        return "/a50/6{}" + str(x)

    import random
    action = URL(r=request,c='static',f='stats_test.png')
    path = 'applications'+str(action)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    for d in data:
        d[0] = mktime(d[0].timetuple())-start_date

    ar = area.T(
           #x_coord = category_coord.T(data, 0),
           x_coord = linear_coord.T(),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = '',
                      format=format_x,
                      tic_interval=tic_interval_from_ts,
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (None, mktime(end.timetuple())-start_date)
         )
    bar_plot.fill_styles.reset();

    colors = [color.darkolivegreen1,
              color.gray10,
              color.salmon,
              color.gray30,
              color.darkkhaki,
              color.gray50,
              color.sienna1,
              color.gray70,
              color.lightgreen,
              color.gray90,
              color.thistle3,
              color.coral]

    plot = []
    for i, o in enumerate(cols):
        if i == 0:
            stackon = None
        else:
            stackon = plot[i-1]

        plot += [bar_plot.T(label=o.replace('/','//'),
                            hcol=i+1,
                            fill_style=fill_style.Plain(bgcolor=colors[i%len(colors)]),
                            stack_on=stackon,
                            line_style=None,
                            width = w,
                            data = data,
                            data_label_format="",
                            direction='vertical')]
        ar.add_plot(plot[i])

    ar.draw(can)
    can.close()

    return action

@auth.requires_login()
def _svcmon_log_ack(request):
    request.vars.ackflag = "0"
    svcs = set([])

    b = str_to_date(request.vars.ack_begin)
    e = str_to_date(request.vars.ack_end)
    if request.vars.ac == 'true':
        account = 1
    else:
        account = 0

    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        svcs |= set(['_'.join(key.split('_')[1:-1])])
    for svc in svcs:
        svcmon_log_ack_write(svc, b, e, 
                             request.vars.ackcomment,
                             account)

@auth.requires_login()
def service_availability(rows, begin=None, end=None):
    h = {}
    def status_merge_down(s):
        if s == 'up': return 'warn'
        elif s == 'down': return 'down'
        elif s == 'stdby up': return 'stdby up with down'
        elif s == 'stdby up with up': return 'warn'
        elif s == 'stdby up with down': return 'stdby up with down'
        elif s == 'undef': return 'down'
        else: return 'undef'

    def status_merge_up(s):
        if s == 'up': return 'up'
        elif s == 'down': return 'warn'
        elif s == 'stdby up': return 'stdby up with up'
        elif s == 'stdby up with up': return 'stdby up with up'
        elif s == 'stdby up with down': return 'warn'
        elif s == 'undef': return 'up'
        else: return 'undef'

    def status_merge_stdby_up(s):
        if s == 'up': return 'stdby up with up'
        elif s == 'down': return 'stdby up with down'
        elif s == 'stdby up': return 'stdby up'
        elif s == 'stdby up with up': return 'stdby up with up'
        elif s == 'stdby up with down': return 'warn'
        elif s == 'undef': return 'stdby up'
        else: return 'undef'

    def status(row):
        s = 'undef'
        for sn in ['mon_containerstatus',
                  'mon_ipstatus',
                  'mon_fsstatus',
                  'mon_appstatus',
                  'mon_diskstatus']:
            if row.svcmon_log[sn] in ['warn', 'stdby down', 'todo']: return 'warn'
            elif row.svcmon_log[sn] == 'undef': return 'undef'
            elif row.svcmon_log[sn] == 'n/a': continue
            elif row.svcmon_log[sn] == 'up': s = status_merge_up(s)
            elif row.svcmon_log[sn] == 'down': s = status_merge_down(s)
            elif row.svcmon_log[sn] == 'stdby up': s = status_merge_stdby_up(s)
            else: return 'undef'
        return s

    if end is None or begin is None:
        return {}
    period = end - begin

    """ First pass at range construction:
          for each row in resultset, create a new range
    """
    for row in rows:
        if row.svcmon_log.mon_svcname not in h:
            h[row.svcmon_log.mon_svcname] = {'ranges': [],
                                  'range_count': 0,
                                  'holes': [],
                                  'begin': begin,
                                  'end': end,
                                  'period': period,
                                  'downtime': 0,
                                  'discarded': [],
                                 }
        s = status(row)
        if s not in ['up', 'stdby up with up']:
            h[row.svcmon_log.mon_svcname]['discarded'] += [(row.svcmon_log.id, s)]
            continue

        """ First range does not need overlap detection
        """
        (b, e) = (row.svcmon_log.mon_begin, row.svcmon_log.mon_end)
        if len(h[row.svcmon_log.mon_svcname]['ranges']) == 0:
            h[row.svcmon_log.mon_svcname]['ranges'] = [(b, e)]
            h[row.svcmon_log.mon_svcname]['range_count'] += 1
            continue

        """ Overlap detection
        """
        add = False
        for i, (b, e) in enumerate(h[row.svcmon_log.mon_svcname]['ranges']):
            if row.svcmon_log.mon_end < b or row.svcmon_log.mon_begin > e:
                """        XXXXXXXXXXX
                    XXX        or         XXX
                """
                add = True
            elif row.svcmon_log.mon_begin >= b and row.svcmon_log.mon_end <= e:
                """        XXXXXXXXXXX
                              XXX
                """
                add = False
                break
            elif row.svcmon_log.mon_begin <= b and row.svcmon_log.mon_end >= e:
                """        XXXXXXXXXXX
                         XXXXXXXXXXXXXXXXX
                """
                add = False
                b = row.svcmon_log.mon_begin
                e = row.svcmon_log.mon_end
                h[row.svcmon_log.mon_svcname]['ranges'][i] = (b, e)
                break
            elif row.svcmon_log.mon_begin < b and row.svcmon_log.mon_end >= b:
                """        XXXXXXXXXXX
                         XXXXX
                """
                add = False
                b = row.svcmon_log.mon_begin
                h[row.svcmon_log.mon_svcname]['ranges'][i] = (b, e)
                break
            elif row.svcmon_log.mon_begin <= e and row.svcmon_log.mon_end > e:
                """        XXXXXXXXXXX
                                   XXXXX
                """
                add = False
                e = row.svcmon_log.mon_end
                h[row.svcmon_log.mon_svcname]['ranges'][i] = (b, e)
                break


        if add:
            h[row.svcmon_log.mon_svcname]['range_count'] += 1
            h[row.svcmon_log.mon_svcname]['ranges'] += [(row.svcmon_log.mon_begin,row.svcmon_log.mon_end)]

    def delta_to_min(d):
        return (d.days*1440)+(d.seconds//60)

    o = db.svcmon_log_ack.mon_begin
    query = (db.svcmon_log_ack.id>0)
    query &= _where(None, 'svcmon_log_ack', request.vars.mon_svcname, 'mon_svcname')
    query &= _where(None, 'svcmon_log_ack', request.vars.mon_begin, 'mon_end')
    query &= _where(None, 'svcmon_log_ack', request.vars.mon_end, 'mon_begin')
    query &= _where(None, 'svcmon_log_ack', domain_perms(), 'mon_svcname')
    acked = db(query).select(orderby=o)

    def get_holes(svc, _e, b):
        ack_overlap = 0
        holes = []

        def _hole(b, e, acked, a):
            if a is None:
                a = dict(mon_acked_by='',
                         mon_acked_on='',
                         mon_comment='',
                         mon_account=1,
                         id='',
                        )
            h = dict(begin=b,
                     end=e,
                     acked=acked,
                     acked_by=a['mon_acked_by'],
                     acked_on=a['mon_acked_on'],
                     acked_comment=a['mon_comment'],
                     acked_account=a['mon_account'],
                     id=a['id'],
                    )
            return h

        for a in [ack for ack in acked if ack.mon_svcname == svc]:
            (ab, ae) = (a.mon_begin, a.mon_end)

            if _e >= ab and b <= ae:
                """ hole is completely acknowledged
                      XXXXX
                          _e
                                   XXXXXXXXXX
                                   b
                         ============= acked segment
                        ab           ae
                """
                holes += [_hole(_e, b, 1, a)]
                ack_overlap += 1
                break

            elif _e <= ab and ab < b and ae >= b:
                """ hole is partly acknowledged
                      XXXXX
                          _e
                                   XXXXXXXXXX
                                   b
                               =========== acked segment
                              ab         ae
                """
                holes += [_hole(_e, ab, 0, None)]
                holes += [_hole(ab, b, 1, a)]
                ack_overlap += 1

            elif ab <= _e and ae < b and ae > _e:
                """ hole is partly acknowledged
                      XXXXX
                          _e
                                   XXXXXXXXXX
                                   b
                     ========= acked segment
                    ab       ae
                """
                holes += [_hole(_e, ae, 1, a)]
                holes += [_hole(ae, b, 0, None)]
                ack_overlap += 1

            elif ab > _e and ab < b and ae > _e and ae < b:
                """ hole is partly acknowledged
                      XXXXX
                          _e
                                        XXXXXXXXXX
                                        b
                               ====== acked segment
                              ab    ae
                """
                holes += [_hole(_e, ab, 0, None)]
                holes += [_hole(ab, ae, 1, a)]
                holes += [_hole(ae, b, 0, None)]
                ack_overlap += 1

        if ack_overlap == 0:
            holes += [_hole(_e, b, 0, None)]

        return holes


    for svc in h:
        _e = None

        for i, (b, e) in enumerate(h[svc]['ranges']):
            """ Merge overlapping ranges
                      begin                            end
                init:   |                              _e
                        |                               |
                prev:   |   XXXXXXXXXXXXXXXXX           |
                        |                   _e          |
                curr:   |                 XXXXXXXXXXXX  |
                        |                 b          e  |
            """
            if _e is not None and b < _e:
                b = _e

            """ Discard segment heading part outside scope
                      begin                            end
                        |                               |
                    XXXXXXXXXXXXXXXXX                   |
                    b   |           e                   |
            """
            if b < begin:
                b = begin

            """ Discard segment trailing part outside scope
                      begin                            end
                        |                               |
                        |                    XXXXXXXXXXXXXXXX
                        |                    b          |   e
            """
            if e > end:
                e = end

            """ Store changed range
            """
            h[svc]['ranges'][i] = (b, e)

            """ Store holes
            """
            if _e is not None and _e < b:
                h[svc]['holes'] += get_holes(svc, _e, b)

            """ Store the current segment endpoint for use in the
                next loop iteration
            """
            _e = e

        if len(h[svc]['ranges']) == 0:
            h[svc]['holes'] += get_holes(svc, begin, end)
        else:
            """ Add heading hole
            """
            (b, e) = h[svc]['ranges'][0]
            if b > begin:
                h[svc]['holes'] = get_holes(svc, begin, b) + h[svc]['holes']

            """ Add trailing hole
            """
            (b, e) = h[svc]['ranges'][-1]
            if e < end:
                h[svc]['holes'] = h[svc]['holes'] + get_holes(svc, e, end)

        """ Account acknowledged time
        """
        for _h in h[svc]['holes']:
            if _h['acked'] == 1 and _h['acked_account'] == 0:
                continue
            h[svc]['downtime'] += delta_to_min(_h['end'] - _h['begin'])

        """ Compute availability
        """
        h[svc]['period_min'] = delta_to_min(h[svc]['period'])

        if h[svc]['period_min'] == 0:
            h[svc]['availability'] = 0
        else:
            h[svc]['availability'] = (h[svc]['period_min'] - h[svc]['downtime']) * 100.0 / h[svc]['period_min']

    return h

def service_availability_chart(h):
    def format_x(ts):
        d = datetime.date.fromtimestamp(ts)
        return "/a50/5{}" + d.strftime("%y-%m-%d")

    def sort_by_avail(x, y):
        return cmp(h[x]['availability'], h[y]['availability'])

    k = h.keys()
    k.sort(sort_by_avail, reverse=True)

    data = []
    from time import mktime
    x_min = 0
    x_max = 0

    def get_range(holes):
        last = 0
        ticks = []
        for _h in holes:
            tsb = mktime(_h['begin'].timetuple())
            tse = mktime(_h['end'].timetuple())
            d1 = tsb - last
            if d1 < 0:
                continue
            d2 = tse - tsb
            if d2 == 0:
                continue
            last = tse
            ticks += [d1, d2]
        if len(ticks) == 0:
            ticks = [0, 0]
        return ticks

    for svc in k:
        if x_min == 0:
            x_min = mktime(h[svc]['begin'].timetuple())
        else:
            x_min = min(mktime(h[svc]['begin'].timetuple()), x_min)

        if x_max == 0:
            x_max = mktime(h[svc]['end'].timetuple())
        else:
            x_max = min(mktime(h[svc]['end'].timetuple()), x_max)

        ticks = get_range([_h for _h in h[svc]['holes'] if _h['acked']==0 or (_h['acked']==1 and _h['acked_account']==1)])
        ticks_acked = get_range([_h for _h in h[svc]['holes'] if _h['acked']==1 and _h['acked_account']==0])

        data += [(svc, tuple(ticks), tuple(ticks_acked))]

    if len(data) == 0:
        return

    duration = x_max - x_min
    if duration < 691200:
        ti = 86400
    elif duration < 2764800:
        ti = 604800
    else:
        ti = 2592000

    action = str(URL(r=request,c='static',f='avail.png'))
    path = 'applications'+action
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 3
    theme.reinitialize()

    ar = area.T(y_coord = category_coord.T(data, 0),
                size = (150,len(data)*8),
                x_range = (x_min, x_max),
                x_axis = axis.X(label="", format=format_x, tic_interval=ti),
                y_axis = axis.Y(label="",  format="/4{}%s"))
    bar_plot.fill_styles.reset()

    chart_object.set_defaults(interval_bar_plot.T,
                              direction="horizontal",
                              width=3,
                              cluster_sep = 0,
                              data=data)
    plot1 = interval_bar_plot.T(
                fill_styles=[fill_style.Plain(bgcolor=color.salmon), None],
                line_styles=[None, None],
                cluster=(0,2),
                label="/5accounted"
    )
    plot2 = interval_bar_plot.T(
                fill_styles=[fill_style.Plain(bgcolor=color.thistle3), None],
                line_styles=[None, None],
                hcol=2, cluster=(1,2),
                label="/5ignored"
    )
    ar.add_plot(plot1, plot2)
    ar.draw(can)
    can.close()
    return action

@auth.requires_login()
def svcmon_log():
    if request.vars.ackflag == "1":
        _svcmon_log_ack(request)

    now = datetime.datetime.now()
    if request.vars.mon_begin is None or request.vars.mon_begin == "":
        begin = now - datetime.timedelta(days=7, microseconds=now.microsecond)
        request.vars.mon_begin = ">"+str(begin)
    else:
        begin = str_to_date(request.vars.mon_begin)

    if request.vars.mon_end is None or request.vars.mon_end == "":
        end = now - datetime.timedelta(seconds=1200, microseconds=now.microsecond)
        request.vars.mon_end = "<"+str(end)
    else:
        end = str_to_date(request.vars.mon_end)

    toggle_db_filters()

    o = db.svcmon_log.mon_begin|db.svcmon_log.mon_end
    query = db.v_svcmon.mon_svcname==db.svcmon_log.mon_svcname
    query &= db.v_svcmon.mon_nodname==db.svcmon_log.mon_nodname
    query &= _where(None, 'svcmon_log', request.vars.mon_svcname, 'mon_svcname')
    query &= _where(None, 'svcmon_log', request.vars.mon_begin, 'mon_end')
    query &= _where(None, 'svcmon_log', request.vars.mon_end, 'mon_begin')
    query &= _where(None, 'svcmon_log', domain_perms(), 'mon_svcname')

    query = apply_db_filters(query, 'v_svcmon')

    rows = db(query).select(orderby=o)
    nav = DIV()

    h = service_availability(rows, begin, end)
    img = service_availability_chart(h)

    """
    if request.vars.chart == "timeline":
        img = service_availability_chart(h)
    else:
        img = svcmon_log_global_chart(rows)
    """

    return dict(rows=rows,
                h=h,
                nav=nav,
                img=img,
                active_filters=active_db_filters('v_svcmon'),
                available_filters=avail_db_filters('v_svcmon'),
               )

@auth.requires_login()
def ajax_svcmon_log_transition():
    svc = request.vars.svcname
    b = str_to_date(request.vars.begin)
    e = str_to_date(request.vars.end)

    """ real transition dates
    """
    tb = b
    te = e

    def get_states_at(d, svc):
        q = (db.svcmon_log.mon_svcname==svc)
        q &= (db.svcmon_log.mon_begin!=db.svcmon_log.mon_end)

        rows = db(q&(db.svcmon_log.mon_end<=d)).select(orderby=~db.svcmon_log.mon_end, limitby=(0,1))
        n = len(rows)
        if n == 0:
            before = DIV(T("No known state before %(date)s", dict(date=d)))
        else:
            before = svc_status(rows[0])
            tb = rows[0].mon_end

        rows = db(q&(db.svcmon_log.mon_begin>=d)).select(orderby=db.svcmon_log.mon_begin, limitby=(0,1))
        n = len(rows)
        if n == 0:
            after = DIV(T("No known state after %(date)s", dict(date=d)))
        else:
            after = svc_status(rows[0])
            te = rows[0].mon_begin

        return (before, after)

    (bb, ab) = get_states_at(b, svc)
    (be, ae) = get_states_at(e, svc)

    header = DIV(
               H3(T("State transitions for %(svc)s", dict(svc=svc))),
             )
    t = TABLE(
          TR(
            TH(b, _colspan=2, _style="text-align:center"),
            TH(e, _colspan=2, _style="text-align:center"),
          ),
          TR(
            TD(bb),
            TD(ab),
            TD(be),
            TD(ae),
          ),
        )
    return DIV(header, t)

@auth.requires_login()
def ajax_svcmon_log_ack_write():
    svc = request.vars.xi
    b = str_to_date(request.vars.bi)
    e = str_to_date(request.vars.ei)
    comment = request.vars.ci

    if request.vars.ac == 'true':
        account = 1
    else:
        account = 0

    svcmon_log_ack_write(svc, b, e, comment, account)

    input_close = INPUT(_value=T('close & refresh table'), _id='close', _type='submit', _onclick="""
                    getElementById("panel_ack").className="panel";
                  """%dict(url=URL(r=request,f='ajax_svcmon_log_ack_write'),
                           svcname=svc)
                  )
    return DIV(T("saved"), P(input_close))

@auth.requires_login()
def svcmon_log_ack_write(svc, b, e, comment="", account=False):
    def db_insert_ack_segment(svc, begin, end, comment, account):
        r = db.svcmon_log_ack.insert(
            mon_svcname = svc,
            mon_begin = begin,
            mon_end = end,
            mon_comment = comment,
            mon_account = account,
            mon_acked_on = datetime.datetime.now(),
            mon_acked_by = user_name()
        )

    rows = db_select_ack_overlap(svc, b, e)
    l = len(rows)

    if l == 1:
        b = min(rows[0].mon_begin, b)
        e = max(rows[0].mon_end, e)
    elif l > 1:
        b = min(rows[0].mon_begin, b)
        e = max(rows[-1].mon_end, e)

    db_delete_ack_overlap(svc, b, e)
    db_insert_ack_segment(svc, b, e, comment, account)

def db_select_ack_overlap(svc, begin, end):
    b = str(begin)
    e = str(end)
    o = db.svcmon_log_ack.mon_begin
    query = (db.svcmon_log_ack.mon_svcname==svc)
    query &= _where(None, 'svcmon_log_ack', domain_perms(), 'mon_svcname')
    query &= ((db.svcmon_log_ack.mon_end>b)&(db.svcmon_log_ack.mon_end<e))|((db.svcmon_log_ack.mon_begin>b)&(db.svcmon_log_ack.mon_begin<e))
    rows = db(query).select(orderby=o)
    return rows

def db_delete_ack_overlap(svc, begin, end):
    b = str(begin)
    e = str(end)
    query = (db.svcmon_log_ack.mon_svcname==svc)
    query &= _where(None, 'svcmon_log_ack', domain_perms(), 'mon_svcname')
    query &= ((db.svcmon_log_ack.mon_end>b)&(db.svcmon_log_ack.mon_end<=e))|((db.svcmon_log_ack.mon_begin>=b)&(db.svcmon_log_ack.mon_begin<e))
    return db(query).delete()


