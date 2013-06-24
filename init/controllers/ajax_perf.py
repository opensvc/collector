def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

@auth.requires_login()
def perf_stats_netdev_one(node, s, e, dev):
    q = db.stats_netdev.nodename == node
    q &= db.stats_netdev.date > s
    q &= db.stats_netdev.date < e
    q &= db.stats_netdev.dev == dev
    rows = db(q).select(orderby=db.stats_netdev.date)
    return rows

@auth.requires_login()
def perf_stats_mem_trend_data(node, s, e, p):
    sql = """select cast(max(kbmemfree+kbcached) as unsigned),
                    cast(min(kbmemfree+kbcached) as unsigned),
                    cast(avg(kbmemfree+kbcached) as unsigned)
             from stats_mem_u
             where nodename="%(node)s"
               and date>date_sub("%(s)s", interval %(p)s)
               and date<date_sub("%(e)s", interval %(p)s)
          """%dict(s=s,e=e,node=node,p=p)
    rows = db.executesql(sql)
    if len(rows) != 1:
        return [(p, 0, 0, 0)]
    r = rows[0]
    if r[0] is None or r[1] is None or r[2] is None:
        return [(p, 0, 0, 0)]
    return [(p, r[0], r[1], r[2])]

@auth.requires_login()
def perf_stats_mem_trend(node, s, e):
    data = []
    start = str_to_date(s)
    end = str_to_date(e)
    period = end - start
    for p in period_to_range(period):
        data += perf_stats_mem_trend_data(node, s, e, p)
    return data

@auth.requires_login()
def perf_stats_cpu_trend_data(node, s, e, p):
    sql = """select 100-max(idle),100-min(idle),100-avg(idle)
             from stats_cpu
             where cpu="all"
               and nodename="%(node)s"
               and date>date_sub("%(s)s", interval %(p)s)
               and date<date_sub("%(e)s", interval %(p)s)
          """%dict(s=s,e=e,node=node,p=p)
    rows = db.executesql(sql)
    if len(rows) != 1:
        return [(p, 0, 0, 0)]
    r = rows[0]
    if r[0] is None or r[1] is None or r[2] is None:
        return [(p, 0, 0, 0)]
    return [(p, r[0], r[1], r[2])]

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
    where = "svcname = '%s' and"%container
    col = 'mem'

    sql = """select mem_bytes from nodes
             where
               nodename="%(node)s"
          """%dict(node=node)
    mem = db.executesql(sql)[0][0]

    sql = """select
               "global",
               %(d)s,
               %(col)s
             from stats_svc
             where
               %(where)s
               nodename="%(node)s"
               and date>"%(s)s"
               and date<"%(e)s"
             union
             select
               "normalized",
               %(d)s,
               (%(col)s / cap * %(mem)d) - %(col)s
             from stats_svc
             where
               %(where)s
               nodename="%(node)s"
               and date>"%(s)s"
               and date<"%(e)s"
          """%dict(mem=mem, where=where,s=s,e=e,node=node,col=col, d=period_concat(s, e, field='date'))
    rows = db.executesql(sql)
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

    return h.keys(), map(lambda x: x.items(), h.values())

@auth.requires_login()
def perf_stats_svc_data_cpu_normalize(node, s, e):
    container = request.vars.container
    where = "svcname = '%s' and"%container
    col = 'cpu'

    sql = """select cpu_cores from nodes
             where
               nodename="%(node)s"
          """%dict(node=node)
    cpus = db.executesql(sql)[0][0]

    sql = """select
               "global",
               %(d)s,
               %(col)s
             from stats_svc
             where
               %(where)s
               nodename="%(node)s"
               and date>"%(s)s"
               and date<"%(e)s"
             union
             select
               "normalized",
               %(d)s,
               (%(col)s / cap_cpu * %(cpus)d) - %(col)s
             from stats_svc
             where
               %(where)s
               nodename="%(node)s"
               and date>"%(s)s"
               and date<"%(e)s"
          """%dict(cpus=cpus, where=where,s=s,e=e,node=node,col=col, d=period_concat(s, e, field='date'))
    rows = db.executesql(sql)
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

    return h.keys(), map(lambda x: x.items(), h.values())

@auth.requires_login()
def perf_stats_svc_data(node, s, e, col):
    container = request.vars.container
    if container == "None":
        where = ''
    else:
        where = "svcname = '%s' and"%container
    sql = """select
               svcname,
               %(d)s,
               %(col)s
             from stats_svc
             where
               %(where)s
               nodename="%(node)s"
               and date>"%(s)s"
               and date<"%(e)s"
          """%dict(where=where,s=s,e=e,node=node,col=col, d=period_concat(s, e, field='date'))
    rows = db.executesql(sql)
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

    return h.keys(), map(lambda x: x.items(), h.values())

@auth.requires_login()
def perf_stats_cpu_trend(node, s, e):
    data = []
    start = str_to_date(s)
    end = str_to_date(e)
    period = end - start

    for p in period_to_range(period):
        data += perf_stats_cpu_trend_data(node, s, e, p)
    return data

@auth.requires_login()
def ajax_perf_netdev_err_plot():
    return _ajax_perf_plot('netdev_err', last=True)

@auth.requires_login()
def ajax_perf_netdev_plot():
    return _ajax_perf_plot('netdev', sub=['_kBps', '_pckps'], last=True)

@auth.requires_login()
def ajax_perf_blockdev_plot():
    sub = ['_pct_util', '_pct_util_time', '_tps', '_tps_time', '_secps', '_tm', '_await', '_await_time', '_svctm', '_svctm_time', '_avgrq_sz', '_avgrq_sz_time']
    return _ajax_perf_plot('blockdev', sub=sub, last=True)

def ajax_perf_block_plot():
    return _ajax_perf_plot('block', sub=['_tps', '_bps'], last=True)

def ajax_perf_fs_plot():
    return _ajax_perf_plot('fs', sub=['_u'], last=True)

def ajax_perf_proc_plot():
    return _ajax_perf_plot('proc', sub=['_runq_sz', '_plist_sz', '_loadavg'], last=True)

def ajax_perf_memswap_plot():
    return SPAN(
             _ajax_perf_plot('mem', sub=['_u', '_pct'], base='memswap'),
             _ajax_perf_plot('swap', sub=['_u', '_pct'], last=True, base='memswap')
           )

def ajax_perf_trend_plot():
    return SPAN(
             _ajax_perf_plot('trend_cpu', base='trend'),
             _ajax_perf_plot('trend_mem', last=True, base='trend')
           )

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

def ajax_perf_svc_plot():
    return SPAN(
             _ajax_perf_plot('svc_cpu', base='svc'),
             _ajax_perf_plot('svc_cap_cpu', base='svc'),
             _ajax_perf_plot('svc_mem', base='svc'),
             _ajax_perf_plot('svc_cap', base='svc'),
             _ajax_perf_plot('svc_swap', base='svc'),
             _ajax_perf_plot('svc_rss', base='svc'),
             _ajax_perf_plot('svc_nproc', base='svc'),
             _ajax_perf_plot('svc_pg', base='svc'),
             _ajax_perf_plot('svc_avgpg', base='svc'),
             _ajax_perf_plot('svc_at', base='svc'),
             _ajax_perf_plot('svc_avgat', base='svc', last=True),
           )

@auth.requires_login()
def ajax_perf_cpu_plot():
    return _ajax_perf_plot('cpu', last=True)

@auth.requires_login()
def _ajax_perf_plot(group, sub=[''], last=False, base=None, container=None):
    if base is None:
        base = group
    node = request.args[0]
    rowid = request.args[1]
    begin = None
    end = None
    try:
        container = request.args[2]
    except:
        container = None

    for k in request.vars:
        if 'begin_' in k:
            b = request.vars[k]
        elif 'end_' in k:
            e = request.vars[k]
    if node is None or b is None or e is None:
        return SPAN()

    plots = []
    plots.append("stats_%(group)s('%(url)s', 'perf_%(group)s_%(rowid)s');"%dict(
      url=URL(r=request,
              f='call/json/json_%s'%group,
              vars={'node':node, 'b':b, 'e':e, 'container':container}
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
                    avg(usr),
                    avg(nice),
                    avg(sys),
                    avg(iowait),
                    avg(steal),
                    avg(irq),
                    avg(soft),
                    avg(guest),
                    avg(idle),
                    %(d)s as d
             from stats_cpu
             where date>='%(s)s'
               and date<='%(e)s'
               and cpu='ALL'
               and nodename='%(n)s'
             group by d
          """%dict(
                d = period_concat(s, e),
                s = s,
                e = e,
                n = node,
              )
    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_proc(node, s, e):
    sql = """select date,
                    avg(runq_sz),
                    avg(plist_sz),
                    avg(ldavg_1),
                    avg(ldavg_5),
                    avg(ldavg_15),
                    %(d)s as d
             from stats_proc
             where date>='%(s)s'
               and date<='%(e)s'
               and nodename='%(n)s'
             group by d
          """%dict(
                d = period_concat(s, e),
                s = s,
                e = e,
                n = node,
              )
    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_swap(node, s, e):
    sql = """select date,
                    avg(kbswpfree),
                    avg(kbswpused),
                    avg(pct_swpused),
                    avg(kbswpcad),
                    avg(pct_swpcad),
                    %(d)s as d
             from stats_swap
             where date>='%(s)s'
               and date<='%(e)s'
               and nodename='%(n)s'
             group by d
          """%dict(
                d = period_concat(s, e),
                s = s,
                e = e,
                n = node,
              )
    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_block(node, s, e):
    sql = """select date,
                    avg(rtps),
                    avg(wtps),
                    avg(rbps),
                    avg(wbps),
                    %(d)s as d
             from stats_block
             where date>='%(s)s'
               and date<='%(e)s'
               and nodename='%(n)s'
             group by d
          """%dict(
                d = period_concat(s, e),
                s = s,
                e = e,
                n = node,
              )
    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_mem(node, s, e):
    sql = """select date,
                    avg(kbmemfree),
                    avg(kbmemused),
                    avg(pct_memused),
                    avg(kbbuffers),
                    avg(kbcached),
                    avg(kbcommit),
                    avg(pct_commit),
                    avg(kbmemsys),
                    %(d)s as d
             from stats_mem_u
             where date>='%(s)s'
               and date<='%(e)s'
               and nodename='%(n)s'
             group by d
          """%dict(
                d = period_concat(s, e),
                s = s,
                e = e,
                n = node,
              )
    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_fs_u(node, s, e):
    sql = """select begin,
                    end,
                    mntpt,
                    size,
                    used
             from stats_fs_u_diff
             where end>='%(s)s'
               and begin<='%(e)s'
               and nodename='%(n)s'
             union all
             select begin,
                    end,
                    mntpt,
                    size,
                    used
             from stats_fs_u_last
             where end>='%(s)s'
               and begin<='%(e)s'
               and nodename='%(n)s'
          """%dict(
                d = period_concat(s, e),
                s = s,
                e = e,
                n = node,
              )
    rows = db.executesql(sql)
    _rows = []
    _e = str_to_date(e)
    _s = str_to_date(s)
    for row in rows:
        if row[0] > _s:
            _rows.append([row[0], row[2], row[3], row[4]])
        else:
            _rows.append([_s, row[2], row[3], row[4]])

        if row[1] < _e:
            _rows.append([row[1], row[2], row[3], row[4]])
        else:
            _rows.append([_e, row[2], row[3], row[4]])
    return _rows

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
      from stats_blockdev
      where date >= "%(s)s" and
            date <= "%(e)s" and
            nodename = "%(node)s"
      group by dev;
    """%dict(node=node, s=s, e=e))

    rows_time = db.executesql("""
      select date,
             dev,
             tps,
             rsecps,
             wsecps,
             avgrq_sz,
             await,
             svctm,
             pct_util,
             %(d)s as d
      from stats_blockdev
      where date >= "%(s)s" and
            date <= "%(e)s" and
            nodename = "%(node)s"
      group by d, dev;
    """%dict(
      d = period_concat(s, e),
      node=node,
      s=s,
      e=e))
    return rows, rows_time

@auth.requires_login()
def rows_netdev_avg(node, s, e):
    rows = db.executesql("""
      select dev,
             avg(rxkBps) as rxkBps,
             avg(txkBps) as txkBps,
             avg(rxpckps) as rxpckps,
             avg(txpckps) as txpckps
      from stats_netdev
      where date >= "%(s)s" and
            date <= "%(e)s" and
            nodename = "%(node)s"
      group by dev;
    """%dict(node=node, s=s, e=e))
    return rows

@auth.requires_login()
def rows_netdev(node, s, e):
    sql = """select date,
                    dev,
                    avg(rxkBps),
                    avg(txkBps),
                    avg(rxpckps),
                    avg(txpckps),
                    %(d)s as d
             from stats_netdev
             where date>='%(s)s'
               and date<='%(e)s'
               and nodename='%(n)s'
             group by d,dev
          """%dict(
                d = period_concat(s, e),
                s = s,
                e = e,
                n = node,
              )
    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_netdev_err(node, s, e):
    rows = db.executesql("""
      select dev,
             max(rxerrps) as max_rxerrps,
             max(txerrps) as max_txerrps,
             max(collps) as max_collps,
             max(rxdropps) as max_rxdropps,
             max(txdropps) as max_txdropps
      from stats_netdev_err
      where date >= "%(s)s" and
            date <= "%(e)s" and
            nodename = "%(node)s"
      group by dev;
    """%dict(node=node, s=s, e=e))
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
    for r in rows:
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

    if node is None:
        return [runq_sz, plist_sz, loadavg_1, loadavg_5, loadavg_15]

    rows = rows_proc(node, begin, end)
    for r in rows:
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

    if node is None:
        return [kbswpfree, kbswpused, pct_swpused, kbswpcad, pct_swpcad]

    rows = rows_swap(node, begin, end)
    for r in rows:
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

    if node is None:
        return [rtps, wtps, rbps, wbps]

    rows = rows_block(node, begin, end)
    for r in rows:
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

    if node is None:
        return [kbmemfree,
                kbmemused,
                pct_memused,
                kbbuffers,
                kbcached,
                kbcommit,
                pct_commit,
                kbmemsys]

    rows = rows_mem(node, begin, end)
    for r in rows:
        kbmemfree.append((r[0], int(r[1])))
        kbmemused.append((r[0], int(r[2]-r[4]-r[5]-r[8])))
        pct_memused.append((r[0], int(r[3])))
        kbbuffers.append((r[0], int(r[4])))
        kbcached.append((r[0], int(r[5])))
        kbcommit.append((r[0], int(r[6])))
        pct_commit.append((r[0], int(r[7])))
        kbmemsys.append((r[0], int(r[8])))
    return [kbmemfree,
            kbmemused,
            pct_memused,
            kbbuffers,
            kbcached,
            kbcommit,
            pct_commit,
            kbmemsys]

@service.json
def json_netdev_err():
    node = request.vars.node
    begin = request.vars.b
    end = request.vars.e

    dev = []
    max_rxerrps = []
    max_txerrps = []
    max_collps = []
    max_rxdropps = []
    max_txdropps = []

    if node is None:
        return [dev, [max_rxerrps, max_txerrps, max_collps, max_rxdropps, max_txdropps]]

    rows = rows_netdev_err(node, begin, end)
    for r in rows:
        dev.append(r[0])
        max_rxerrps.append(r[1])
        max_txerrps.append(r[2])
        max_collps.append(r[3])
        max_rxdropps.append(r[4])
        max_txdropps.append(r[5])
    return [dev, [max_rxerrps, max_txerrps, max_collps, max_rxdropps, max_txdropps]]

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
    for row in rows:
        label = "%s rx"%row[1]
        if label in bw:
            bw[label].append([row[0], -row[2]])
        else:
            bw[label] = [[row[0], -row[2]]]
        label = "%s tx"%row[1]
        if label in bw:
            bw[label].append([row[0], row[3]])
        else:
            bw[label] = [[row[0], row[3]]]
        label = "%s rx"%row[1]
        if label in pk:
            pk[label].append([row[0], -row[4]])
        else:
            pk[label] = [[row[0], -row[4]]]
        label = "%s tx"%row[1]
        if label in pk:
            pk[label].append([row[0], row[5]])
        else:
            pk[label] = [[row[0], row[5]]]
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
        return [dev, tps, avgrq_sz, await, svctm, pct_util, [rsecps, wsecps],
                tm_dev, [tm_svc, tm_await]]

    rows, rows_time = rows_blockdev(node, begin, end)

    l = sorted(rows, key=lambda r: (r[4]+r[5]))
    l.reverse()
    for i, r in enumerate(l):
        dev.append(r[0])
        rsecps.append(r[4])
        wsecps.append(r[5])
        if i >= 10: break

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
    await_devs = [r[0] for r in tps]
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
             }
           }

@service.json
def json_fs():
    node = request.vars.node
    begin = request.vars.b
    end = request.vars.e

    mntpt = []
    size = []
    used = {}

    if node is None:
        return [mntpt, size, used]

    rows = rows_fs_u(node, begin, end)
    for r in rows:
        if r[1] not in used:
            used[r[1]] = []
            mntpt.append(r[1])
            size.append(int(r[2]))
        used[r[1]].append((r[0],int(r[3])))
    data = []
    for m in mntpt:
        data.append(used[m])
    return [mntpt, size, data]

@service.json
def json_trend_cpu():
    node = request.vars.node
    begin = request.vars.b
    end = request.vars.e

    if node is None:
        return []

    return perf_stats_cpu_trend(node, begin, end)

@service.json
def json_trend_mem():
    node = request.vars.node
    begin = request.vars.b
    end = request.vars.e

    if node is None:
        return []

    return perf_stats_mem_trend(node, begin, end)


