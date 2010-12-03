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

def period_to_range(period):
    if period <= datetime.timedelta(days=1):
        return ["6 day", "5 day", "4 day", "3 day",
                "2 day", "1 day", "0 day"]
    elif period <= datetime.timedelta(days=7):
        return ["3 week", "2 week", "1 week", "0 week"]
    elif period <= datetime.timedelta(days=30):
        return ["2 month", "1 month", "0 month"]
    else:
        return []

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
    return _ajax_perf_plot('blockdev', sub=['_tps', '_avgrq_sz', '_await', '_svctm', '_pct_util', '_secps'], last=True)

def ajax_perf_block_plot():
    return _ajax_perf_plot('block', sub=['_tps', '_bps'], last=True)

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

@auth.requires_login()
def ajax_perf_cpu_plot():
    return _ajax_perf_plot('cpu', last=True)

@auth.requires_login()
def _ajax_perf_plot(group, sub=[''], last=False, base=None):
    if base is None:
        base = group
    node = request.args[0]
    rowid = request.args[1]
    begin = None
    end = None
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
              vars={'node':node, 'b':b, 'e':e}
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
                  _id='perf_%s_%s%s'%(group,rowid,s),
                  _class='float',
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
def rows_cpu_one(node, s, e, cpu):
    q = db.stats_cpu.nodename == node
    q &= db.stats_cpu.date > s
    q &= db.stats_cpu.date < e
    q &= db.stats_cpu.cpu == cpu
    rows = db(q).select(orderby=db.stats_cpu.date)
    return rows

@auth.requires_login()
def rows_cpu(node, s, e):
    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
    q = db.stats_cpu.nodename == node
    q &= db.stats_cpu.date > s
    q &= db.stats_cpu.date < e
    rows = db(q).select(db.stats_cpu.cpu,
                        groupby=db.stats_cpu.cpu,
                        orderby=db.stats_cpu.cpu,
                       )
    cpus = [r.cpu for r in rows]

    t = []
    for cpu in cpus:
        t += perf_stats_cpu_one(node, s, e, cpu)
    return t

@auth.requires_login()
def rows_proc(node, s, e):
    q = db.stats_proc.nodename == node
    q &= db.stats_proc.date > s
    q &= db.stats_proc.date < e
    rows = db(q).select(orderby=db.stats_proc.date)
    return rows

@auth.requires_login()
def rows_swap(node, s, e):
    q = db.stats_swap.nodename == node
    q &= db.stats_swap.date > s
    q &= db.stats_swap.date < e
    rows = db(q).select(orderby=db.stats_swap.date)
    return rows

@auth.requires_login()
def rows_block(node, s, e):
    q = db.stats_block.nodename == node
    q &= db.stats_block.date > s
    q &= db.stats_block.date < e
    rows = db(q).select(orderby=db.stats_block.date)
    return rows

@auth.requires_login()
def rows_mem(node, s, e):
    q = db.stats_mem_u.nodename == node
    q &= db.stats_mem_u.date > s
    q &= db.stats_mem_u.date < e
    rows = db(q).select(orderby=db.stats_mem_u.date)
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
      from stats_blockdev
      where date >= "%(s)s" and
            date <= "%(e)s" and
            nodename = "%(node)s"
      group by dev;
    """%dict(node=node, s=s, e=e))
    return rows

@auth.requires_login()
def rows_netdev(node, s, e):
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

@auth.requires_login()
def perf_stats_netdev(node, s, e):
    q = db.stats_netdev.nodename == node
    q &= db.stats_netdev.date > s
    q &= db.stats_netdev.date < e
    rows = db(q).select(db.stats_netdev.dev,
                        groupby=db.stats_netdev.dev,
                        orderby=db.stats_netdev.dev,
                       )
    devs = [r.dev for r in rows]

    t = []
    for dev in devs:
        t += perf_stats_netdev_one(node, s, e, dev)
    return t

#
# json servers
#
###############

@service.json
def json_cpu():
    node = request.vars.node
    begin = request.vars.b
    end = request.vars.e

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

    rows = rows_cpu_one(node, begin, end, 'all')
    for r in rows:
        usr.append((r.date, r.usr))
        nice.append((r.date, r.nice))
        sys.append((r.date, r.sys))
        iowait.append((r.date, r.iowait))
        steal.append((r.date, r.steal))
        irq.append((r.date, r.irq))
        soft.append((r.date, r.soft))
        guest.append((r.date, r.guest))
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
        runq_sz.append((r.date, r.runq_sz))
        plist_sz.append((r.date, r.plist_sz))
        loadavg_1.append((r.date, r.ldavg_1))
        loadavg_5.append((r.date, r.ldavg_5))
        loadavg_15.append((r.date, r.ldavg_15))
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
        kbswpfree.append((r.date, r.kbswpfree))
        kbswpused.append((r.date, r.kbswpused-r.kbswpcad))
        pct_swpused.append((r.date, r.pct_swpused))
        kbswpcad.append((r.date, r.kbswpcad))
        pct_swpcad.append((r.date, r.pct_swpcad))
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
        rtps.append((r.date, r.rtps))
        wtps.append((r.date, r.wtps))
        rbps.append((r.date, r.rbps/2))
        wbps.append((r.date, r.wbps/2))
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
        kbmemfree.append((r.date, r.kbmemfree))
        kbmemused.append((r.date, r.kbmemused-r.kbbuffers-r.kbcached-r.kbmemsys))
        pct_memused.append((r.date, r.pct_memused))
        kbbuffers.append((r.date, r.kbbuffers))
        kbcached.append((r.date, r.kbcached))
        kbcommit.append((r.date, r.kbcommit))
        pct_commit.append((r.date, r.pct_commit))
        kbmemsys.append((r.date, r.kbmemsys))
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
def json_netdev():
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

    rows = rows_netdev(node, begin, end)
    for r in rows:
        dev.append(r[0])
        rxkBps.append(r[1])
        txkBps.append(r[2])
        rxpckps.append(r[3])
        txpckps.append(r[4])
    return [dev, [rxkBps, txkBps], [rxpckps, txpckps]]

@service.json
def json_blockdev():
    node = request.vars.node
    begin = request.vars.b
    end = request.vars.e

    dev = []
    tps = []
    rsecps = []
    wsecps = []
    avgrq_sz = []
    await = []
    svctm = []
    pct_util = []

    if node is None:
        return [dev, tps, avgrq_sz, await, svctm, pct_util, [rsecps, wsecps]]

    rows = rows_blockdev(node, begin, end)
    for r in rows:
        dev.append(r[0])
        rsecps.append(r[4])
        wsecps.append(r[5])
        tps.append((r[0],r[3],r[2],r[1]))
        avgrq_sz.append((r[0], r[8],r[7],r[6]))
        await.append((r[0], r[11],r[10],r[9]))
        svctm.append((r[0], r[14],r[13],r[12]))
        pct_util.append((r[0], r[17],r[16],r[15]))
    return [dev, tps, avgrq_sz, await, svctm, pct_util, [rsecps, wsecps]]

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


