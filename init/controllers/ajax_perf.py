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
def perf_stats_netdev_one(node, s, e, dev):
    q = db.stats_netdev.node_id == node
    q &= db.stats_netdev.date > s
    q &= db.stats_netdev.date < e
    q &= db.stats_netdev.dev == dev
    rows = db(q).select(orderby=db.stats_netdev.date)
    return rows

@auth.requires_login()
def perf_stats_svc_cpu(node, s, e):
    container = request.vars.container
    if container == "None":
        return perf_stats_svc_data(node, s, e, 'cpu')
    else:
        return perf_stats_svc_data_cpu_normalize(node, s, e)

@auth.requires_login()
def perf_stats_svc_mem(node, s, e):
    container = request.vars.container
    if container == "None":
        return perf_stats_svc_data(node, s, e, 'mem')
    else:
        return perf_stats_svc_data_mem_normalize(node, s, e)

@auth.requires_login()
def perf_stats_svc_pg(node, s, e):
    return perf_stats_svc_data(node, s, e, 'pg')

@auth.requires_login()
def perf_stats_svc_avgpg(node, s, e):
    return perf_stats_svc_data(node, s, e, 'avgpg')

@auth.requires_login()
def perf_stats_svc_at(node, s, e):
    return perf_stats_svc_data(node, s, e, 'at')

@auth.requires_login()
def perf_stats_svc_avgat(node, s, e):
    return perf_stats_svc_data(node, s, e, 'avgat')

@auth.requires_login()
def perf_stats_svc_rss(node, s, e):
    return perf_stats_svc_data(node, s, e, 'rss')

@auth.requires_login()
def perf_stats_svc_swap(node, s, e):
    return perf_stats_svc_data(node, s, e, 'swap')

@auth.requires_login()
def perf_stats_svc_nproc(node, s, e):
    return perf_stats_svc_data(node, s, e, 'nproc')

@auth.requires_login()
def perf_stats_svc_cap(node, s, e):
    return perf_stats_svc_data(node, s, e, 'cap')

@auth.requires_login()
def perf_stats_svc_cap_cpu(node, s, e):
    return perf_stats_svc_data(node, s, e, 'cap_cpu')

@auth.requires_login()
def perf_stats_svc_data_mem_normalize(node, s, e):
    container = request.vars.container
    where = "stats_svc%(period)s.svc_id = '%(svc_id)s' and"%dict(svc_id=node_svc_id(node, container), period=get_period(s, e))
    col = 'mem'

    sql = """select mem_bytes from nodes
             where
               node_id="%(node)s"
          """%dict(node=node)
    mem = db.executesql(sql)[0][0]

    sql = """select
               "global",
               date,
               %(col)s
             from stats_svc%(period)s
             where
               %(where)s
               node_id="%(node)s"
               and date>"%(s)s"
               and date<"%(e)s"
             union
             select
               "normalized",
               date,
               (%(col)s / cap * %(mem)d) - %(col)s
             from stats_svc%(period)s
             where
               %(where)s
               node_id="%(node)s"
               and date>"%(s)s"
               and date<"%(e)s"
          """%dict(mem=mem, where=where,s=s,e=e,node=node,col=col, period=get_period(s, e))
    rows = db.executesql(sql)
    if len(rows) == 0:
        return [], [], 0, 0
    min = rows[0][1]
    max = rows[-1][1]
    dates = set([r[1] for r in rows])
    svcnames = set([r[0] for r in rows])

    h = {}
    import copy
    d = {}

    for date in dates:
        d[date] = 0

    for svcname in svcnames:
        h[svcname] = copy.copy(d)

    for row in rows:
        svcname = row[0]
        date = row[1]
        data = row[2]

        h[svcname][date] = data

    return h.keys(), map(lambda x: x.items(), h.values()), min, max

@auth.requires_login()
def perf_stats_svc_data_cpu_normalize(node, s, e):
    container = request.vars.container
    where = "stats_svc%(period)s.svc_id = '%(svc_id)s' and"%dict(svc_id=node_svc_id(node, container), period=get_period(s, e))
    col = 'cpu'

    sql = """select if(cpu_threads is null, cpu_cores, cpu_threads)
             from nodes
             where node_id="%(node)s"
          """%dict(node=node)
    cpus = db.executesql(sql)[0][0]

    sql = """select
               "global",
               date,
               %(col)s
             from stats_svc%(period)s
             where
               %(where)s
               node_id="%(node)s"
               and date>"%(s)s"
               and date<"%(e)s"
             union
             select
               "normalized",
               date,
               (%(col)s / cap_cpu * %(cpus)d) - %(col)s
             from stats_svc%(period)s
             where
               %(where)s
               node_id="%(node)s"
               and date>"%(s)s"
               and date<"%(e)s"
          """%dict(cpus=cpus, where=where,s=s,e=e,node=node,col=col, period=get_period(s, e))
    rows = db.executesql(sql)
    if len(rows) == 0:
        return [], [], 0, 0
    min = rows[0][1]
    max = rows[-1][1]
    dates = set([r[1] for r in rows])
    svcnames = set([r[0] for r in rows])

    h = {}
    import copy
    d = {}

    for date in dates:
        d[date] = 0

    for svcname in svcnames:
        h[svcname] = copy.copy(d)

    for row in rows:
        svcname = row[0]
        date = row[1]
        data = row[2]

        h[svcname][date] = data

    return h.keys(), map(lambda x: x.items(), h.values()), min, max

@auth.requires_login()
def perf_stats_svc_data(node, s, e, col):
    container = request.vars.container
    if container == "None":
        where = ''
    else:
        where = "services.svc_id = '%s' and"%node_svc_id(node, container)
    sql = """select
               services.svcname,
               date,
               %(col)s
             from stats_svc%(period)s, services
             where
               %(where)s
               node_id="%(node)s"
               and date>"%(s)s"
               and date<"%(e)s"
             order by date
          """%dict(where=where,s=s,e=e,node=node,col=col, period=get_period(s, e))
    rows = db.executesql(sql)
    if len(rows) == 0:
        return [], [], 0, 0
    min = rows[0][1]
    max = rows[-1][1]
    dates = set([r[1] for r in rows])
    svcnames = set([r[0] for r in rows])

    h = {}
    import copy
    d = {}

    for date in dates:
        d[date] = 0

    for svcname in svcnames:
        h[svcname] = copy.copy(d)

    for row in rows:
        svcname = row[0]
        date = row[1]
        data = row[2]

        h[svcname][date] = data

    return h.keys(), map(lambda x: x.items(), h.values()), min, max

def ajax_perf_svc_plot_short():
    return SPAN(
             _ajax_perf_plot('svc_cpu', base='svc'),
             _ajax_perf_plot('svc_cap_cpu', base='svc'),
             _ajax_perf_plot('svc_mem', base='svc'),
             _ajax_perf_plot('svc_cap', base='svc'),
             _ajax_perf_plot('svc_swap', base='svc'),
             _ajax_perf_plot('svc_rss', base='svc'),
             _ajax_perf_plot('svc_nproc', base='svc', last=True),
           )

@auth.requires_login()
def _ajax_perf_plot(group, sub=[''], last=False, base=None, container=None):
    session.forget(response)
    if base is None:
        base = group
    node = request.args[0]
    rowid = request.args[1]
    begin = datetime.datetime.now() - datetime.timedelta(days=1)
    end = datetime.datetime.now()
    try:
        container = request.args[2]
    except:
        container = None

    for k in request.vars:
        if 'begin_' in k:
            begin = request.vars[k]
        elif 'end_' in k:
            end = request.vars[k]
    if node is None:
        return SPAN()

    plots = []
    plots.append("stats_%(group)s('%(url)s', 'perf_%(group)s_%(rowid)s');"%dict(
      url=URL(r=request,
              f='call/json/json_%s'%group,
              vars={'node':node, 'b':begin, 'e':end, 'container':container}
          ),
      rowid=rowid,
      group=group,
    ))

    if last:
        spacer = DIV(
                   XML('&nbsp;'),
                   _class='spacer',
                 ),
    else:
        spacer = ''
    l = []
    for s in sub:
        l.append(DIV(
                  DIV(_id='perf_%s_%s%s'%(group,rowid,s)),
                  _class='float perf_plot',
                 ))
    l.append(SPAN(spacer))
    l.append(SCRIPT(
               plots,
               _name="prf_cont_%s_%s_to_eval"%(base,rowid)
             ))
    return SPAN(*l)


#
# raw data extractors
#
######################

@auth.requires_login()
def rows_cpu(node, s, e):
    sql = """select date,
                    usr,
                    nice,
                    sys,
                    iowait,
                    steal,
                    irq,
                    soft,
                    guest,
                    idle
             from stats_cpu%(period)s
             where date>='%(s)s'
               and date<='%(e)s'
               and cpu='ALL'
               and node_id="%(n)s"
          """%dict(
                period = get_period(s, e),
                s = s,
                e = e,
                n = node,
              )
    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_proc(node, s, e):
    sql = """select date,
                    runq_sz,
                    plist_sz,
                    ldavg_1,
                    ldavg_5,
                    ldavg_15
             from stats_proc%(period)s
             where date>='%(s)s'
               and date<='%(e)s'
               and node_id="%(n)s"
          """%dict(
                period = get_period(s, e),
                s = s,
                e = e,
                n = node,
              )
    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_swap(node, s, e):
    sql = """select date,
                    kbswpfree,
                    kbswpused,
                    pct_swpused,
                    kbswpcad,
                    pct_swpcad
             from stats_swap%(period)s
             where date>='%(s)s'
               and date<='%(e)s'
               and node_id="%(n)s"
          """%dict(
                period = get_period(s, e),
                s = s,
                e = e,
                n = node,
              )
    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_block(node, s, e):
    sql = """select date,
                    rtps,
                    wtps,
                    rbps,
                    wbps
             from stats_block%(period)s
             where date>='%(s)s'
               and date<='%(e)s'
               and node_id="%(n)s"
          """%dict(
                period = get_period(s, e),
                s = s,
                e = e,
                n = node,
              )
    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_mem(node, s, e):
    sql = """select date,
                    kbmemfree,
                    kbmemused,
                    pct_memused,
                    kbbuffers,
                    kbcached,
                    kbcommit,
                    pct_commit,
                    kbmemsys,
                    kbactive,
                    kbinact,
                    kbdirty
             from stats_mem_u%(period)s
             where date>='%(s)s'
               and date<='%(e)s'
               and node_id="%(n)s"
          """%dict(
                period = get_period(s, e),
                s = s,
                e = e,
                n = node,
              )
    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_fs_u(node, s, e):
    sql = """select date,
                    mntpt,
                    size,
                    used
             from stats_fs_u%(period)s
             where date>='%(s)s'
               and date<='%(e)s'
               and node_id="%(n)s"
          """%dict(
                period = get_period(s, e),
                s = s,
                e = e,
                n = node,
              )
    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_blockdev(node, s, e):
    rows = db.executesql("""
      select dev,
             avg(tps) as avg_tps,
             min(tps) as min_tps,
             max(tps) as max_tps,
             avg(rsecps) as rsecps,
             avg(wsecps) as wsecps,
             avg(avgrq_sz) as avg_avgrq_sz,
             min(avgrq_sz) as min_avgrq_sz,
             max(avgrq_sz) as max_avgrq_sz,
             avg(await) as avg_await,
             min(await) as min_await,
             max(await) as max_await,
             avg(svctm) as avg_svctm,
             min(svctm) as min_svctm,
             max(svctm) as max_svctm,
             avg(pct_util) as avg_pct_util,
             min(pct_util) as min_pct_util,
             max(pct_util) as max_pct_util
      from stats_blockdev%(period)s
      where date >= "%(s)s" and
            date <= "%(e)s" and
            node_id = "%(node)s"
      group by dev
    """%dict(node=node, s=s, e=e, period=get_period(s, e)))

    rows_time = db.executesql("""
      select date,
             dev,
             tps,
             rsecps,
             wsecps,
             avgrq_sz,
             await,
             svctm,
             pct_util
      from stats_blockdev%(period)s
      where date >= "%(s)s" and
            date <= "%(e)s" and
            node_id = "%(node)s"
    """%dict(
      period = get_period(s, e),
      node=node,
      s=s,
      e=e))
    return rows, rows_time

@auth.requires_login()
def rows_netdev(node, s, e):
    sql = """select date,
                    dev,
                    rxkBps,
                    txkBps,
                    rxpckps,
                    txpckps
             from stats_netdev%(period)s
             where date>='%(s)s'
               and date<='%(e)s'
               and node_id="%(n)s"
          """%dict(
                period = get_period(s, e),
                s = s,
                e = e,
                n = node,
              )
    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_netdev_err(node, s, e):
    rows = db.executesql("""
      select date,
             dev,
             rxerrps,
             txerrps,
             collps,
             rxdropps,
             txdropps
      from stats_netdev_err%(period)s
      where date >= "%(s)s" and
            date <= "%(e)s" and
            node_id = "%(node)s"
    """%dict(
         period = get_period(s, e),
         node=node,
         s=s,
         e=e
        )
    )
    return rows


#
# json servers
#
###############

@service.json
def json_svc_cpu():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_cpu(node, b, e)

@service.json
def json_svc_mem():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_mem(node, b, e)

@service.json
def json_svc_at():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_at(node, b, e)

@service.json
def json_svc_avgat():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_avgat(node, b, e)

@service.json
def json_svc_pg():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_pg(node, b, e)

@service.json
def json_svc_avgpg():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_avgpg(node, b, e)

@service.json
def json_svc_rss():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_rss(node, b, e)

@service.json
def json_svc_swap():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_swap(node, b, e)

@service.json
def json_svc_cap_cpu():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_cap_cpu(node, b, e)

@service.json
def json_svc_cap():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_cap(node, b, e)

@service.json
def json_svc_nproc():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_nproc(node, b, e)

def get_max_interval(b, e):
    period = get_period(b, e)
    if period == '':
        return 11
    elif period == '_hour':
        return 61
    elif period == '_day':
        return 1441
    else:
        return 10081

def add_hole(this_date, prev_date, max_interval, data):
    if prev_date is None:
        return data
    td = this_date - prev_date
    interval = td.days*1440 + td.seconds//60
    if interval > max_interval:
        t0 = prev_date + datetime.timedelta(seconds=1)
        t1 = this_date - datetime.timedelta(seconds=1)
        for i, l in enumerate(data):
            for t in (t0, t1):
                data[i].append((t, None))
    return data

@service.json
def json_cpu():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e

    usr = []
    nice = []
    sys = []
    iowait = []
    steal = []
    irq = []
    soft = []
    guest = []

    if node is None:
        return [usr, nice, sys, iowait, steal, irq, soft, guest]

    rows = rows_cpu(node, b, e)
    prev_date = None
    max_interval = get_max_interval(b, e)

    for r in rows:
        this_date = r[0]
        usr, nice, sys, iowait, steal, irq, soft, guest = add_hole(this_date, prev_date, max_interval, [usr, nice, sys, iowait, steal, irq, soft, guest])
        prev_date = this_date
        usr.append((r[0], r[1]))
        nice.append((r[0], r[2]))
        sys.append((r[0], r[3]))
        iowait.append((r[0], r[4]))
        steal.append((r[0], r[5]))
        irq.append((r[0], r[6]))
        soft.append((r[0], r[7]))
        guest.append((r[0], r[8]))
    return [usr, nice, sys, iowait, steal, irq, soft, guest]

@service.json
def json_proc():
    node = request.vars.node
    begin = request.vars.b
    end = request.vars.e

    runq_sz = []
    plist_sz = []
    loadavg_1 = []
    loadavg_5 = []
    loadavg_15 = []

    prev_date = None
    max_interval = get_max_interval(begin, end)

    if node is None:
        return [runq_sz, plist_sz, loadavg_1, loadavg_5, loadavg_15]

    rows = rows_proc(node, begin, end)
    for r in rows:
        this_date = r[0]
        runq_sz, plist_sz, loadavg_1, loadavg_5, loadavg_15 = add_hole(this_date, prev_date, max_interval, [runq_sz, plist_sz, loadavg_1, loadavg_5, loadavg_15])
        prev_date = this_date
        runq_sz.append((r[0], float(r[1])))
        plist_sz.append((r[0], int(r[2])))
        loadavg_1.append((r[0], float(r[3])))
        loadavg_5.append((r[0], float(r[4])))
        loadavg_15.append((r[0], float(r[5])))
    return [runq_sz, plist_sz, loadavg_1, loadavg_5, loadavg_15]

@service.json
def json_swap():
    node = request.vars.node
    begin = request.vars.b
    end = request.vars.e

    kbswpfree = []
    kbswpused = []
    pct_swpused = []
    kbswpcad = []
    pct_swpcad = []

    prev_date = None
    max_interval = get_max_interval(begin, end)

    if node is None:
        return [kbswpfree, kbswpused, pct_swpused, kbswpcad, pct_swpcad]

    rows = rows_swap(node, begin, end)
    for r in rows:
        this_date = r[0]
        kbswpfree, kbswpused, pct_swpused, kbswpcad, pct_swpcad = add_hole(this_date, prev_date, max_interval, [kbswpfree, kbswpused, pct_swpused, kbswpcad, pct_swpcad])
        prev_date = this_date
        kbswpfree.append((r[0], int(r[1])))
        kbswpused.append((r[0], int(r[2]-r[4])))
        pct_swpused.append((r[0], int(r[3])))
        kbswpcad.append((r[0], int(r[4])))
        pct_swpcad.append((r[0], int(r[5])))
    return [kbswpfree, kbswpused, pct_swpused, kbswpcad, pct_swpcad]

@service.json
def json_block():
    node = request.vars.node
    begin = request.vars.b
    end = request.vars.e

    rtps = []
    wtps = []
    rbps = []
    wbps = []

    prev_date = None
    max_interval = get_max_interval(begin, end)

    if node is None:
        return [rtps, wtps, rbps, wbps]

    rows = rows_block(node, begin, end)
    for r in rows:
        this_date = r[0]
        rtps, wtps, rbps, wbps = add_hole(this_date, prev_date, max_interval, [rtps, wtps, rbps, wbps])
        prev_date = this_date
        rtps.append((r[0], float(r[1])))
        wtps.append((r[0], float(r[2])))
        rbps.append((r[0], float(r[3]/2)))
        wbps.append((r[0], float(r[4]/2)))
    return [rtps, wtps, rbps, wbps]

@service.json
def json_mem():
    node = request.vars.node
    begin = request.vars.b
    end = request.vars.e

    kbmemfree = []
    kbmemused = []
    pct_memused = []
    kbbuffers = []
    kbcached = []
    kbcommit = []
    pct_commit = []
    kbmemsys = []
    kbactive = []
    kbinact = []
    kbdirty = []

    prev_date = None
    max_interval = get_max_interval(begin, end)

    if node is None:
        return [kbmemfree,
                kbmemused,
                pct_memused,
                kbbuffers,
                kbcached,
                kbcommit,
                pct_commit,
                kbmemsys,
                kbactive,
                kbinact,
                kbdirty]

    rows = rows_mem(node, begin, end)
    memtotal = None
    if len(rows) > 0 and (rows[0][3] is None or int(rows[0][3]) == 0):
        q = db.nodes.node_id == node
        asset = db(q).select(db.nodes.mem_bytes, cacheable=True).first()
        if asset is not None:
            memtotal = asset.mem_bytes * 1024
    for r in rows:
        this_date = r[0]
        kbmemfree, kbmemused, pct_memused, kbbuffers, kbcached, kbcommit, pct_commit, kbmemsys, kbactive, kbinact, kbdirty = add_hole(this_date, prev_date, max_interval, [kbmemfree, kbmemused, pct_memused, kbbuffers, kbcached, kbcommit, pct_commit, kbmemsys, kbactive, kbinact, kbdirty])
        prev_date = this_date
        _kbmemfree = int(r[1])
        if memtotal is not None:
            _kbmemused = memtotal - _kbmemfree
            _pct_memused = int(100 * _kbmemused / memtotal)
        else:
            _kbmemused = int(r[2]-r[4]-r[5]-r[8])
            _pct_memused = int(r[3])
        kbmemfree.append((r[0], _kbmemfree))
        kbmemused.append((r[0], _kbmemused))
        pct_memused.append((r[0], _pct_memused))
        kbbuffers.append((r[0], int(r[4]) if r[5] else None))
        kbcached.append((r[0], int(r[5]) if r[5] else None))
        kbcommit.append((r[0], int(r[6]) if r[6] else None))
        pct_commit.append((r[0], int(r[7]) if r[7] else None))
        kbmemsys.append((r[0], int(r[8]) if r[8] else None))
        kbactive.append((r[0], int(r[9]) if r[9] else None))
        kbinact.append((r[0], int(r[10]) if r[10] else None))
        kbdirty.append((r[0], int(r[11]) if r[11] else None))
    return [kbmemfree, kbmemused, pct_memused, kbbuffers, kbcached, kbcommit, pct_commit, kbmemsys, kbactive, kbinact, kbdirty]

@service.json
def json_netdev_err():
    node = request.vars.node
    begin = request.vars.b
    end = request.vars.e

    errps = {}
    collps = {}
    dropps = {}

    if node is None:
        return [rxerrps, txerrps, collps, rxdropps, txdropps]

    rows = rows_netdev_err(node, begin, end)
    for row in rows:
        label = "%s rx"%row[1]
        if label in errps:
            errps[label].append([row[0], -row[2]])
        else:
            errps[label] = [[row[0], -row[2]]]
        label = "%s tx"%row[1]
        if label in errps:
            errps[label].append([row[0], row[3]])
        else:
            errps[label] = [[row[0], row[3]]]
        label = "%s"%row[1]
        if label in collps:
            collps[label].append([row[0], row[4]])
        else:
            collps[label] = [[row[0], row[4]]]
        label = "%s rx"%row[1]
        if label in dropps:
            dropps[label].append([row[0], -row[5]])
        else:
            dropps[label] = [[row[0], -row[5]]]
        label = "%s tx"%row[1]
        if label in dropps:
            dropps[label].append([row[0], row[6]])
        else:
            dropps[label] = [[row[0], row[6]]]
    errps_labels = sorted(errps.keys())
    errps_data = []
    for k in errps_labels:
        errps_data.append(errps[k])
    collps_labels = sorted(collps.keys())
    collps_data = []
    for k in collps_labels:
        collps_data.append(collps[k])
    dropps_labels = sorted(dropps.keys())
    dropps_data = []
    for k in dropps_labels:
        dropps_data.append(dropps[k])
    return [[errps_labels, errps_data],
            [collps_labels, collps_data],
            [dropps_labels, dropps_data]]

@service.json
def json_netdev_avg():
    node = request.vars.node
    begin = request.vars.b
    end = request.vars.e

    dev = []
    rxkBps = []
    txkBps = []
    rxpckps = []
    txpckps = []

    if node is None:
        return [dev, [rxkBps, txkBps], [rxpckps, txpckps]]

    rows = rows_netdev_avg(node, begin, end)
    for r in rows:
        dev.append(r[0])
        rxkBps.append(r[1])
        txkBps.append(r[2])
        rxpckps.append(r[3])
        txpckps.append(r[4])
    return [dev, [rxkBps, txkBps], [rxpckps, txpckps]]

@service.json
def json_netdev():
    node = request.vars.node
    begin = request.vars.b
    end = request.vars.e

    if node is None:
        return []

    rows = rows_netdev(node, begin, end)
    bw = {}
    pk = {}

    prev_date = None
    max_interval = get_max_interval(begin, end)

    for row in rows:
        this_date = row[0]

        label = "%s rx"%row[1]
        if label not in bw:
            bw[label] = []
        bw[label] = add_hole(this_date, prev_date, max_interval, [bw[label]])[0]
        bw[label].append([row[0], -row[2]])

        label = "%s tx"%row[1]
        if label not in bw:
            bw[label] = []
        bw[label] = add_hole(this_date, prev_date, max_interval, [bw[label]])[0]
        bw[label].append([row[0], row[3]])

        label = "%s rx"%row[1]
        if label not in pk:
            pk[label] = []
        pk[label] = add_hole(this_date, prev_date, max_interval, [pk[label]])[0]
        pk[label].append([row[0], -row[4]])

        label = "%s tx"%row[1]
        if label not in pk:
            pk[label] = []
        pk[label] = add_hole(this_date, prev_date, max_interval, [pk[label]])[0]
        pk[label].append([row[0], row[5]])

        prev_date = this_date

    bw_labels = sorted(bw.keys())
    bw_data = []
    for k in bw_labels:
        bw_data.append(bw[k])
    pk_labels = sorted(pk.keys())
    pk_data = []
    for k in pk_labels:
        pk_data.append(pk[k])
    return [[bw_labels, bw_data], [pk_labels, pk_data]]

@service.json
def json_blockdev():
    node = request.vars.node
    begin = request.vars.b
    end = request.vars.e

    max_await = 300000

    dev = []
    tm_dev = []

    tps = []
    rsecps = []
    wsecps = []
    avgrq_sz = []
    await = []
    svctm = []
    pct_util = []
    tm_await = []
    tm_svc = []

    if node is None:
        return {
          'avg':[dev, tps, avgrq_sz, await, svctm, pct_util, [rsecps, wsecps],
                 tm_dev, [tm_svc, tm_await]]
        }

    rows, rows_time = rows_blockdev(node, begin, end)

    l = sorted(rows, key=lambda r: (r[4]+r[5]))
    l.reverse()
    for i, r in enumerate(l):
        dev.append(r[0])
        rsecps.append(r[4])
        wsecps.append(r[5])
        if i >= 10: break
    secps_devs = []
    secps_time = []
    h = {}
    for r in rows_time:
        if r[1] not in dev:
            continue
        label = r[1] + " rd"
        if label not in h:
            h[label] = [[r[0], r[3]]]
        else:
            h[label].append([r[0], r[3]])
        label = r[1] + " wr"
        if label not in h:
            h[label] = [[r[0], -r[4]]]
        else:
            h[label].append([r[0], -r[4]])
    for _dev in dev:
        for dir in (" rd", " wr"):
            secps_devs.append(_dev+dir)
            secps_time.append(h[_dev+dir])


    l = sorted(rows, key=lambda r: r[1])
    l.reverse()
    for i, r in enumerate(l):
        tps.append((r[0],r[3],r[2],r[1]))
        if i >= 10: break
    tps_devs = [r[0] for r in tps]
    tps_time = []
    h = {}
    for r in rows_time:
        if r[1] not in tps_devs:
            continue
        if r[1] not in h:
            h[r[1]] = [[r[0], r[2]]]
        else:
            h[r[1]].append([r[0], r[2]])
    for _dev in tps_devs:
        tps_time.append(h[_dev])

    l = sorted(rows, key=lambda r: r[6])
    l.reverse()
    for i, r in enumerate(l):
        avgrq_sz.append((r[0], r[8],r[7],r[6]))
        if i >= 10: break
    avgrq_sz_devs = [r[0] for r in avgrq_sz]
    avgrq_sz_time = []
    h = {}
    for r in rows_time:
        if r[1] not in avgrq_sz_devs:
            continue
        if r[1] not in h:
            h[r[1]] = [[r[0], r[5]]]
        else:
            h[r[1]].append([r[0], r[5]])
    for _dev in avgrq_sz_devs:
        avgrq_sz_time.append(h[_dev])

    l = sorted(rows, key=lambda r: r[9])
    l.reverse()
    for i, r in enumerate(l):
        await.append((r[0], r[11],r[10],r[9]))
        if i >= 10: break
    await_devs = [r[0] for r in await]
    await_time = []
    h = {}
    for r in rows_time:
        if r[1] not in await_devs:
            continue
        if r[6] > max_await:
            continue
        if r[1] not in h:
            h[r[1]] = [[r[0], r[6]]]
        else:
            h[r[1]].append([r[0], r[6]])
    for _dev in await_devs:
        await_time.append(h[_dev])

    for i, r in enumerate(l):
        tm_dev.append(r[0])
        tm_await.append(r[9]-r[12])
        tm_svc.append(r[12])
        if i >= 10: break

    l = sorted(rows, key=lambda r: r[12])
    l.reverse()
    for i, r in enumerate(l):
        svctm.append((r[0], r[14],r[13],r[12]))
        if i >= 10: break
    svctm_devs = [r[0] for r in svctm]
    svctm_time = []
    h = {}
    for r in rows_time:
        if r[1] not in svctm_devs:
            continue
        if r[1] not in h:
            h[r[1]] = [[r[0], r[7]]]
        else:
            h[r[1]].append([r[0], r[7]])
    for _dev in svctm_devs:
        svctm_time.append(h[_dev])

    l = sorted(rows, key=lambda r: r[15])
    l.reverse()
    for i, r in enumerate(l):
        pct_util.append((r[0], r[17],r[16],r[15]))
        if i >= 10: break
    pct_util_devs = [r[0] for r in pct_util]
    pct_util_time = []
    h = {}
    for r in rows_time:
        if r[1] not in pct_util_devs:
            continue
        if r[1] not in h:
            h[r[1]] = [[r[0], r[8]]]
        else:
            h[r[1]].append([r[0], r[8]])
    for _dev in pct_util_devs:
        pct_util_time.append(h[_dev])


    return {
             'avg': [dev, tps, avgrq_sz, await, svctm, pct_util, [rsecps, wsecps], tm_dev,[tm_svc, tm_await]],
             'begin': begin,
             'end': end,
             'time': {
               'tps': {
                 'labels': tps_devs,
                 'data': tps_time,
               },
               'pct_util': {
                 'labels': pct_util_devs,
                 'data': pct_util_time,
               },
               'await': {
                 'labels': await_devs,
                 'data': await_time,
               },
               'svctm': {
                 'labels': svctm_devs,
                 'data': svctm_time,
               },
               'avgrq_sz': {
                 'labels': avgrq_sz_devs,
                 'data': avgrq_sz_time,
               },
               'secps': {
                 'labels': secps_devs,
                 'data': secps_time,
               },
             }
           }

@service.json
def json_fs():
    node = request.vars.node
    begin = request.vars.b
    end = request.vars.e

    labels = []
    used = {}

    if node is None:
        return [labels, data]

    rows = rows_fs_u(node, begin, end)
    for r in rows:
        label = "%s<br>%d MB" % (r[1], r[2]/1024)
        if label not in labels:
            labels.append(label)
            used[label] = [(r[0], int(r[3]))]
        else:
            used[label].append((r[0],int(r[3])))
    data = []
    for label in labels:
        data.append(used[label])
    return [labels, data]



