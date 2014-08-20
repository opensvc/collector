config = local_import('config', reload=True)

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget(response)
    return service()

@auth.requires_login()
def ack(ids=[]):
    if len(ids) == 0:
        raise ToolError("no range selected")

    if request.vars.ac == 'true':
        account = 1
    else:
        account = 0

    log = ''
    for id in ids:
        i = id.split('_')
        if len(i) != 3:
            continue
        svc = i[0]
        b = str_to_date(i[1])
        e = str_to_date(i[2])
        log += '%s (%s>%s) '%(svc, b, e)
        svcmon_log_ack_write(svc, b, e,
                             request.vars.ackcomment,
                             account)

    if 'ackcomment' in request.vars:
        del request.vars.ackcomment

    _log('availability.ack',
         'acknowledged unavailability range: %(g)s',
         dict(g=log))

def migrate_to_services_log():
    q = db.svcmon_log.id > 0
    q = db.svcmon_log.mon_svcname == db.services.svc_name
    rows = db(q).select(orderby=db.svcmon_log.id)
    begin = rows.first().svcmon_log.mon_begin
    end = rows.last().svcmon_log.mon_end
    h = service_availability(rows, begin, end)
    for svcname in h:
        ranges = h[svcname]['ranges']
        if len(ranges) == 0:
            # no ranges: service always down
            db.services_log.insert(svc_name=svcname,
                                   svc_begin=begin,
                                   svc_end=end,
                                   svc_availstatus="down")
            continue
        first_range_begin = ranges[0][0]
        last_range_end = ranges[-1][1]
        prev_end = begin
        if first_range_begin > begin:
            # create heading unvail segment
            db.services_log.insert(svc_name=svcname,
                                   svc_begin=begin,
                                   svc_end=first_range_begin,
                                   svc_availstatus="down")
            prev_end = first_range_begin
        for b, e in h[svcname]['ranges']:
            if prev_end < b:
                db.services_log.insert(svc_name=svcname,
                                       svc_begin=prev_end,
                                       svc_end=b,
                                       svc_availstatus="down")
            db.services_log.insert(svc_name=svcname,
                                   svc_begin=b,
                                   svc_end=e,
                                   svc_availstatus="up")
            prev_end = e
        if last_range_end < end:
            # create trailing unvail segment
            db.services_log.insert(svc_name=svcname,
                                   svc_begin=last_range_end,
                                   svc_end=end,
                                   svc_availstatus="down")

def get_svc_created(svc):
    q = db.services.svc_name == svc
    row = db(q).select(db.services.svc_created).first()
    if row is not None:
        return row.svc_created
    return datetime.datetime(year=1900, month=1, day=1)

class precreation_acked_range(object):
    def __init__(self, svc):
        self.mon_svcname = svc
        self.mon_begin = datetime.datetime(year=1900, month=1, day=1)
        self.mon_end = get_svc_created(svc)
        self.mon_acked_by = 'opensvc'
        self.mon_acked_on = now
        self.mon_account = 0
        self.mon_comment = 'Service did not exist'
        self.id = 0

    def __getitem__(self, i):
        return getattr(self, i)

@auth.requires_login()
def service_availability(rows, begin=None, end=None):
    h = {}
    def status_merge_down(s):
        if s == 'up': return 'warn'
        elif s == 'down': return 'down'
        elif s == 'stdby up': return 'stdby up with down'
        elif s == 'stdby up with up': return 'warn'
        elif s == 'stdby up with down': return 'stdby up with down'
        elif s in ['undef', 'n/a']: return 'down'
        else: return 'undef'

    def status_merge_up(s):
        if s == 'up': return 'up'
        elif s == 'down': return 'warn'
        elif s == 'stdby up': return 'stdby up with up'
        elif s == 'stdby up with up': return 'stdby up with up'
        elif s == 'stdby up with down': return 'warn'
        elif s in ['undef', 'n/a']: return 'up'
        else: return 'undef'

    def status_merge_stdby_up(s):
        if s == 'up': return 'stdby up with up'
        elif s == 'down': return 'stdby up with down'
        elif s == 'stdby up': return 'stdby up'
        elif s == 'stdby up with up': return 'stdby up with up'
        elif s == 'stdby up with down': return 'stdby up with down'
        elif s in ['undef', 'n/a']: return 'stdby up'
        else: return 'undef'

    def status(row):
        if row.svcmon_log.mon_availstatus != 'undef':
            return row.svcmon_log.mon_availstatus
        s = 'undef'
        for sn in ['mon_containerstatus',
                  'mon_ipstatus',
                  'mon_fsstatus',
                  'mon_appstatus',
                  'mon_diskstatus']:
            if row.svcmon_log[sn] in ['warn', 'stdby down', 'todo']: return 'warn'
            elif row.svcmon_log[sn] == 'undef': return 'undef'
            elif row.svcmon_log[sn] == 'n/a':
                if s == 'undef': s = 'n/a'
                else: continue
            elif row.svcmon_log[sn] == 'up': s = status_merge_up(s)
            elif row.svcmon_log[sn] == 'down': s = status_merge_down(s)
            elif row.svcmon_log[sn] == 'stdby up': s = status_merge_stdby_up(s)
            else: return 'undef'
        if s == 'stdby up with up':
            s = 'up'
        elif s == 'stdby up with down':
            s = 'stdby up'
        db(db.svcmon_log.id==row.svcmon_log.id).update(mon_availstatus=s)
        return s

    if end is None or begin is None:
        return {}
    period = end - begin

    """ First pass at range construction:
          for each row in resultset, create a new range
    """
    for row in rows:
        if row.svcmon_log.mon_svcname not in h:
            h[row.svcmon_log.mon_svcname] = {
              'svcname': row.svcmon_log.mon_svcname,
              'ranges': [],
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
    query = _where(query, 'svcmon_log_ack', domain_perms(), 'mon_svcname')
    query = _where(query, 'svcmon_log_ack', request.vars.mon_svcname, 'mon_svcname')
    query = _where(query, 'svcmon_log_ack', '>%s'%begin, 'mon_end')
    query = _where(query, 'svcmon_log_ack', '<%s'%end, 'mon_begin')
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

        for a in [precreation_acked_range(svc)] + [ack for ack in acked if ack.mon_svcname == svc]:
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
                break

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
                holes += get_holes(svc, ae, b)
                ack_overlap += 1
                break

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
                holes += get_holes(svc, ae, b)
                ack_overlap += 1
                break

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

@auth.requires_login()
def service_availability_2(rows, begin=None, end=None):
    h = {}

    if end is None or begin is None:
        return {}
    period = end - begin

    """ First pass at range construction:
        for each row in resultset, create a new range
    """
    for row in rows:
        if row.services_log.svc_name not in h:
            h[row.services_log.svc_name] = {
              'svcname': row.services_log.svc_name,
              'ranges': [],
              'range_count': 0,
              'holes': [],
              'begin': begin,
              'end': end,
              'period': period,
              'downtime': 0,
             }
        if row.services_log.svc_availstatus not in ['up']:
            continue

        (b, e) = (row.services_log.svc_begin, row.services_log.svc_end)
        h[row.services_log.svc_name]['ranges'] += [(b, e)]
        h[row.services_log.svc_name]['range_count'] += 1

    def delta_to_min(d):
        return (d.days*1440)+(d.seconds//60)

    o = db.svcmon_log_ack.mon_begin
    query = (db.svcmon_log_ack.id>0)
    query = _where(query, 'svcmon_log_ack', domain_perms(), 'mon_svcname')
    query = _where(query, 'svcmon_log_ack', request.vars.mon_svcname, 'mon_svcname')
    query = _where(query, 'svcmon_log_ack', '>%s'%begin, 'mon_end')
    query = _where(query, 'svcmon_log_ack', '<%s'%end, 'mon_begin')
    acked = db(query).select(orderby=o)

    if hasattr(config, 'account_appstatus_in_service_avail') and \
       not config.account_appstatus_in_service_avail:
        o = db.svcmon_log.mon_begin
        query = (db.svcmon_log.id>0)
        query = _where(query, 'svcmon_log', domain_perms(), 'mon_svcname')
        query = _where(query, 'svcmon_log', request.vars.mon_svcname, 'mon_svcname')
        query = _where(query, 'svcmon_log', '>%s'%begin, 'mon_end')
        query = _where(query, 'svcmon_log', '<%s'%end, 'mon_begin')
        query &= db.svcmon_log.mon_appstatus.belongs(["warn", "down"])
        query &= ~db.svcmon_log.mon_ipstatus.belongs(["warn", "down"])
        query &= ~db.svcmon_log.mon_fsstatus.belongs(["warn", "down"])
        query &= ~db.svcmon_log.mon_containerstatus.belongs(["warn", "down"])
        query &= ~db.svcmon_log.mon_diskstatus.belongs(["warn", "down"])
        appdown = db(query).select(orderby=o)

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

        for a in [precreation_acked_range(svc)] + [ack for ack in acked if ack.mon_svcname == svc]:
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
                break

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
                holes += get_holes(svc, ae, b)
                ack_overlap += 1
                break

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
                holes += get_holes(svc, ae, b)
                ack_overlap += 1
                break

        if ack_overlap == 0:
            holes += [_hole(_e, b, 0, None)]

        if hasattr(config, 'account_appstatus_in_service_avail') and \
           not config.account_appstatus_in_service_avail:
            delta = datetime.timedelta(minutes=2)
            for i, hole in enumerate(holes):
                for ad in appdown:
                     if ad.mon_begin + delta > hole['end']:
                         break
                     if ad.mon_svcname != svc:
                         continue
                     if ad.mon_end - delta < hole['begin']:
                         continue
                     if hole['end'] <= ad.mon_end + delta:
                         holes[i]['acked'] = 1
                         holes[i]['account'] = 0
                         holes[i]['acked_by'] = "opensvc"
                         holes[i]['acked_on'] = now
                         holes[i]['acked_comment'] = "Application issue"
                         holes[i]['acked_account'] = 0
                     break

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


#####

class col_avail_svcname(Column):
    def get(self, o):
        return o['svcname']

    def html(self, o):
        val = self.get(o)
        if val is None:
            return ''
        return val

@service.json
def json_availability(svcname):
    begin = now - datetime.timedelta(days=7, microseconds=now.microsecond)
    end = now - datetime.timedelta(seconds=1200, microseconds=now.microsecond)

    o = db.services_log.svc_name|db.services_log.svc_begin|db.services_log.svc_end
    q = db.v_services.svc_name==db.services_log.svc_name
    q = _where(q, 'services_log', domain_perms(), 'svc_name')
    q &= db.services_log.svc_name == svcname
    q &= db.services_log.svc_begin <= end
    q &= db.services_log.svc_end >= begin

    o = service_availability_2(db(q).select(orderby=o), begin, end)[svcname]

    if len(o) == 0:
        return ""
    down = []
    acked = []
    s = ''
    dh = [h for h in o['holes'] if h['acked'] == 0]
    last = len(dh)-1
    for i, r in enumerate(dh):
        down.append([r['begin'], 1])
        down.append([r['end'], 1])
        if i < last:
            down.append([r['end']+(dh[i+1]['begin']-r['end'])/2, None])
    dh = [h for h in o['holes'] if h['acked'] == 1]
    last = len(dh)-1
    for i, r in enumerate(dh):
        acked.append([r['begin'], 1])
        acked.append([r['end'], 1])
        if i < last:
            acked.append([r['end']+(dh[i+1]['begin']-r['end'])/2, None])
    if len(down) == 0:
        down = [[o['begin'], None]]
    if len(acked) == 0:
        acked = [[o['begin'], None]]
    return [down, acked]

class col_avail_holes(Column):
    def get(self, o):
        return o['holes']

    def format_hole(self, svcname, hole):
        out = """data_%(svc)s[2]=[];$('#%(id)s').empty();avail_plot('%(id)s', data_%(svc)s);"""%dict(
           id='plot_%s'%svcname.replace('.','_'),
           svc=svcname.replace('.','_').replace('-','_'),
         )
        over = """data_%(svc)s[2]=[['%(b)s',2],['%(e)s',2]];$('#%(id)s').empty();avail_plot('%(id)s', data_%(svc)s);"""%dict(
           id='plot_%s'%svcname.replace('.','_'),
           b=hole['begin'],
           e=hole['end'],
           svc=svcname.replace('.','_').replace('-','_'),
         )
        if hole['acked'] == 1:
            if hole['acked_account'] == 0:
                c = 'ack_1'
            else:
                c = 'ack_2'
            msg = SPAN(
                    B("acked by "),
                    hole['acked_by'],
                    B(" on "),
                    hole['acked_on'],
                    B(" with comment: "),
                    hole['acked_comment'],
                  )
            over += """ackpanel(event, true, '%s')"""%msg
            out += """ackpanel(event, false, '%s')"""%msg
            disabled = 'disabled'
            click = ''
        else:
            c = ''
            disabled = False
            click='this.value=this.checked'

        ckid = '_'.join(('svcmon_log', 'ckid',
                         svcname,
                         str(hole['begin']),
                         str(hole['end'])))

        checked = getattr(request.vars, ckid)
        if disabled or checked is None or checked == 'false':
            checked = False
            value = 'false'
        else:
            checked = True
            value = 'true'


        d = DIV(
              INPUT(
                _type='checkbox',
                _id=ckid,
                _name='avail_ck',
                _disabled=disabled,
                _onclick=click,
                _value=value,
                value=checked,
              ),
              DIV(
                hole['begin'],
                _style='display:table-cell;white-space:nowrap;padding-right:1em',
              ),
              DIV(
                '>',
                _style='display:table-cell',
              ),
              DIV(
                hole['end'],
                _style='display:table-cell;white-space:nowrap;padding-left:1em;padding-right:1em',
              ),
              DIV(
                '(', hole['end']-hole['begin'], ')',
                _style='display:table-cell',
              ),
              _style='display:table-row',
              _class=c,
              _onmouseover=over,
              _onmouseout=out,
            )
        return d

    def html(self, o):
        val = self.get(o)
        if len(val) == 0:
            return ''
        l = []
        for hole in val:
            l.append(self.format_hole(o['svcname'], hole))
        return SPAN(*l)

class col_avail_pct(Column):
    def get(self, o):
        return "%0.2f%%"%o['availability']

    def html(self, o):
        val = self.get(o)
        if val is None:
            return ''
        return val

class col_avail_downtime(Column):
    def get(self, o):
        return o['downtime']

    def html(self, o):
        val = self.get(o)
        if val is None:
            return ''
        d = datetime.timedelta(minutes=val)
        return d

class col_avail_plot(Column):
    def get(self, o):
        return None

    def html(self, o):
        if len(o['holes']) == 0:
            return ""
        down = []
        acked = []
        s = ''
        dh = [h for h in o['holes'] if h['acked'] == 0]
        last = len(dh)-1
        for i, r in enumerate(dh):
            down.append([str(r['begin']), 1])
            down.append([str(r['end']), 1])
            if i < last:
                down.append([str(r['end']+(dh[i+1]['begin']-r['end'])/2), 'null'])
        dh = [h for h in o['holes'] if h['acked'] == 1]
        last = len(dh)-1
        for i, r in enumerate(dh):
            acked.append([str(r['begin']), 1])
            acked.append([str(r['end']), 1])
            if i < last:
                acked.append([str(r['end']+(dh[i+1]['begin']-r['end'])/2), 'null'])
        if len(down) == 0:
            down = [[str(o['begin']),'null']]
        if len(acked) == 0:
            acked = [[str(o['begin']),'null']]
        s += """data_%(svc)s=%(data)s;$('#%(id)s').empty();avail_plot('%(id)s', data_%(svc)s)"""%dict(
               data=str([str(down).replace("'null'","null"),
                         str(acked).replace("'null'","null")]).replace('"',''),
               id='plot_%s'%o['svcname'].replace('.','_'),
               svc=o['svcname'].replace('.','_').replace('-','_'),
             )
        return DIV(
                 DIV(
                   _id='plot_%s'%o['svcname'].replace('.','_'),
                   _style='width:300px;height:50px',
                 ),
                 SCRIPT(s, _name=self.t.id+'_to_eval'),
               )

class table_avail(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.keys = ['avail_svcname']
        self.span = ['avail_svcname']
        self.cols = ['avail_svcname',
                     'avail_holes',
                     'avail_pct',
                     'avail_downtime',
                     'avail_plot']
        self.colprops = {
            'avail_svcname': col_avail_svcname(
                     title='Service',
                     img='svc',
                     display=True,
                    ),
            'avail_holes': col_avail_holes(
                     title='Unavailabity ranges',
                     img='time16',
                     display=True,
                    ),
            'avail_pct': col_avail_pct(
                     title='Availabity',
                     img='spark16',
                     display=True,
                    ),
            'avail_downtime': col_avail_downtime(
                     title='Downtime',
                     img='spark16',
                     display=True,
                    ),
            'avail_plot': col_avail_plot(
                     title='History',
                     img='spark16',
                     display=True,
                    ),
        }
        for c in self.cols:
            self.colprops[c].t = self
        self.dbfilterable = False
        self.filterable = False
        self.pageable = False
        self.additional_tools.append('ack')
        self.checkbox_names = ['avail_ck']

    def sort_objects(self, x, y):
        return cmp(self.object_list[x]['availability'], self.object_list[y]['availability'])

    def ack(self):
        d = DIV(
              A(
                T("Acknowledge unavailabity"),
                _onclick="""click_toggle_vis(event,'%(div)s', 'block');$('#ackcomment').focus();"""%dict(div='ackcomment_d_'+self.id),
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
                          self.ajax_submit(additional_inputs=['ackcomment', 'ac'],
                                           args="ack"),

                      ),
                    ),
                  ),
                  TR(
                    TD(
                      T('Account as unavailable'),
                    ),
                    TD(
                      INPUT(
                       _type='checkbox',
                       _id='ac',
                       _onclick='this.value=this.checked',
                      ),
                    ),
                  ),
                  TR(
                    TD(
                      T('Check/Uncheck all'),
                    ),
                    TD(
                      INPUT(
                        _type='checkbox',
                        _onclick="check_all('avail_ck',this.checked);",
                      ),
                    ),
                  ),
                ),
                _style='display:none',
                _class='white_float',
                _name='ackcomment_d_'+self.id,
                _id='ackcomment_d_'+self.id,
              ),
              _class='floatw',
            )
        return d

class table_svcmon_log(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.keys = ['svc_name', 'svc_begin']
        self.span = ['svc_name']
        self.cols = ['svc_name',
                     'svc_begin',
                     'svc_end']
        self.cols += v_services_cols
        self.cols.remove('svc_status')
        self.colprops = svcmon_colprops
        self.colprops.update(v_services_colprops)
        self.colprops.update({
            'svc_begin': HtmlTableColumn(
                     title='Begin',
                     table='services_log',
                     field='svc_begin',
                     img='time16',
                     display=True,
                    ),
            'svc_end': HtmlTableColumn(
                     title='End',
                     table='services_log',
                     field='svc_end',
                     img='time16',
                     display=True,
                    ),
        })
        self.colprops['svc_updated'].field = 'svc_updated'
        self.colprops['svc_name'].display = True
        for c in self.cols:
            self.colprops[c].t = self
        for c in v_services_cols:
            self.colprops[c].table = 'v_services'
        self.colprops['svc_availstatus'].table = 'services_log'
        self.colprops['svc_availstatus'].display = True
        self.dbfilterable = True
        self.extraline = True
        self.checkbox_id_col = 'id'
        self.checkbox_id_table = 'services_log'
        self.ajax_col_values = 'ajax_svcmon_log_col_values'
        self.span = v_services_cols
        self.span.remove('svc_availstatus')

@auth.requires_login()
def ajax_svcmon_log_col_values():
    t = table_svcmon_log('svcmon_log', 'ajax_svcmon_log')
    col = request.args[0]
    g = db.services_log[col]
    o = db.services_log.svc_name|db.services_log.svc_begin|db.services_log.svc_end

    q = db.v_services.svc_name==db.services_log.svc_name
    q = _where(q, 'services_log', domain_perms(), 'svc_name')

    for f in set(t.cols)-set(['svc_begin', 'svc_end']):
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    q = _where(q, 'services_log', t.filter_parse('svc_begin'), 'svc_end')
    q = _where(q, 'services_log', t.filter_parse('svc_end'), 'svc_begin')

    q = apply_filters(q, None, db.services_log.svc_name)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_svcmon_log():
    t = table_svcmon_log('svcmon_log', 'ajax_svcmon_log')
    v = table_avail('svcmon_log_avail', 'ajax_svcmon_log')

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'ack':
                ack(v.get_checked())
        except ToolError, e:
            t.flash = str(e)

    if t.filter_parse('svc_begin') == "":
        begin = now - datetime.timedelta(days=7, microseconds=now.microsecond)
        t.store_filter_value('svc_begin', ">"+str(begin))
    else:
        begin = str_to_date(t.filter_parse('svc_begin'))

    if t.filter_parse('svc_end') == "":
        end = now - datetime.timedelta(seconds=1200, microseconds=now.microsecond)
        t.store_filter_value('svc_end', "<"+str(end))
    else:
        end = str_to_date(t.filter_parse('svc_end'))

    o = db.services_log.svc_name|db.services_log.svc_begin|db.services_log.svc_end

    q = db.v_services.svc_name==db.services_log.svc_name
    q = _where(q, 'services_log', domain_perms(), 'svc_name')

    for f in set(t.cols)-set(['svc_begin', 'svc_end']):
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    q = _where(q, 'services_log', t.filter_parse('svc_begin'), 'svc_end')
    q = _where(q, 'services_log', t.filter_parse('svc_end'), 'svc_begin')

    q = apply_filters(q, None, db.services_log.svc_name)

    if len(request.args) == 1 and request.args[0] == 'line':
        if request.vars.volatile_filters is None:
            t.setup_pager(-1)
            limitby = (t.pager_start,t.pager_end)
        else:
            limitby = (0, 500)
        t.object_list = db(q).select(orderby=o, limitby=limitby)
        t.set_column_visibility()
        return TABLE(t.table_lines()[0])

    t.setup_pager(-1)
    t.object_list = db(q).select(orderby=o, limitby=(t.pager_start,t.pager_end))
    v.object_list = service_availability_2(db(q).select(orderby=o), begin, end)

    t.csv_q = q
    t.csv_orderby = o
    v.csv_extra_args = ['foo']

    if len(request.args) == 1 and request.args[0] == 'csv':
        return t.csv()
    elif len(request.args) == 2 and request.args[0] == 'csv':
        v.cols.remove('avail_holes')
        v.cols.remove('avail_plot')
        return v.csv()

    return DIV(
             DIV(
               _id='ackpanel',
               _class='ackpanel',
             ),
             v.html(),
             t.html(),
           )

@auth.requires_login()
def ajax_svcmon_log_1():
    session.forget(response)
    v = table_avail(request.vars.rowid, request.vars.rowid)
    v.colprops['avail_svcname'].display = False
    v.columnable = False
    v.refreshable = False
    v.exportable = False
    v.additional_tools = []

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'ack':
                ack(v.get_checked())
        except ToolError, e:
            t.flash = str(e)

    begin = now - datetime.timedelta(days=7, microseconds=now.microsecond)
    end = now - datetime.timedelta(seconds=1200, microseconds=now.microsecond)

    o = db.services_log.svc_begin|db.services_log.svc_end
    q = db.v_services.svc_name==db.services_log.svc_name
    q &= db.services_log.svc_name==request.vars.svcname
    q &= db.services_log.svc_begin<end
    q &= db.services_log.svc_end>begin
    q = _where(q, 'services_log', domain_perms(), 'svc_name')

    v.object_list = service_availability_2(db(q).select(orderby=o), begin, end)

    return DIV(
             DIV(
               _id='ackpanel',
               _class='ackpanel',
             ),
             v.html(),
           )

@auth.requires_login()
def svcmon_log():
    t = DIV(
          ajax_svcmon_log(),
          _id='svcmon_log',
        )
    return dict(table=t)


