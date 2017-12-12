from applications.init.modules import timeseries

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
def ajax_containerperf_plot():
    session.forget(response)
    containers = []
    for s in request.vars.node.split(','):
        l = s.split('@')
        if len(l) == 2:
            containers.append(l)

    b = None
    e = None
    bs = ''
    es = ''
    rowid = request.vars.rowid
    if rowid is None:
        import uuid
        rowid = str(uuid.uuid4())

    for v in request.vars:
       if 'begin' in v:
           bs = v
           l = v.split('_')
           if l > 1: rowid = l[-1]
       if 'end' in v:
           es = v

    if len(containers) == 0:
         return DIV(T("No data"))


    sc = ""
    l = []
    for container_name, node_id in containers:
        did = '_'.join((rowid, node_id, str(container_name).replace('.','_')))
        l.append(H3('@'.join((container_name, node_id))))
        l.append(DIV(_id=did))
        sc += """sync_ajax('%(url)s', ['%(bs)s', '%(es)s'], '%(did)s', function(){});"""%dict(
                             url=URL(r=request,c='ajax_perf',f='ajax_perf_svc_plot_short',
                                     args=[node_id, did, container_name]),
                             rowid=rowid,
                             did=did,
                             bs=bs,
                             es=es,
             )

    d = DIV(
          SPAN(l),
          SCRIPT(
            sc,
            _name='plot_to_eval',
          ),
        )

    return d

@auth.requires_login()
def ajax_perfcmp_plot():
    session.forget(response)
    nodes = request.vars.node
    b = None
    e = None
    rowid = ''

    def add_rowid(s):
        if rowid is None: return s
        return '_'.join((s, rowid))

    for v in request.vars:
       if 'begin' in v:
           b = request.vars[v]
           l = v.split('_')
           if l > 1: rowid = l[-1]
       if 'end' in v:
           e = request.vars[v]

    if len(request.vars.node.split(',')) == 0:
         return DIV(T("No nodes selected"))

    plots = []
    plots.append("stats_avg_cpu_for_nodes('%(url)s', '%(did)s');"%dict(
      did=add_rowid('avg_cpu_for_nodes_plot'),
      url=URL(r=request,
              f='call/json/json_avg_cpu_for_nodes',
              vars={'node':nodes, 'b':b, 'e':e}
          )
    ))
    plots.append("stats_avg_mem_for_nodes('%(url)s', '%(did)s');"%dict(
      did=add_rowid('avg_mem_for_nodes_plot'),
      url=URL(r=request,
              f='call/json/json_avg_mem_for_nodes',
              vars={'node':nodes, 'b':b, 'e':e}
          )
    ))
    plots.append("stats_avg_swp_for_nodes('%(url)s', '%(did)s');"%dict(
      did=add_rowid('avg_swp_for_nodes_plot'),
      url=URL(r=request,
              f='call/json/json_avg_swp_for_nodes',
              vars={'node':nodes, 'b':b, 'e':e}
          )
    ))
    plots.append("stats_avg_proc_for_nodes('%(url)s', '%(did)s');"%dict(
      did=add_rowid('avg_proc_for_nodes_plot'),
      url=URL(r=request,
              f='call/json/json_avg_proc_for_nodes',
              vars={'node':nodes, 'b':b, 'e':e}
          )
    ))
    plots.append("stats_avg_block_for_nodes('%(url)s', '%(did)s');"%dict(
      did=add_rowid('avg_block_for_nodes_plot'),
      url=URL(r=request,
              f='call/json/json_avg_block_for_nodes',
              vars={'node':nodes, 'b':b, 'e':e}
          )
    ))
    plots.append("stats_disk_for_svc('%(url)s', '%(did)s');"%dict(
      did=add_rowid('disk_for_svc_plot'),
      url=URL(r=request,
              f='call/json/json_disk_for_svc',
              vars={'node':nodes, 'b':b, 'e':e}
          )
    ))

    d = DIV(
          DIV(
            DIV(_id=add_rowid('avg_cpu_for_nodes_plot')),
            _class='float',
          ),
          DIV(
            DIV(_id=add_rowid('avg_mem_for_nodes_plot')),
            _class='float',
          ),
          DIV(
            DIV(_id=add_rowid('avg_swp_for_nodes_plot')),
            _class='float',
          ),
          DIV(
            DIV(_id=add_rowid('runq_sz_avg_proc_for_nodes_plot')),
            _class='float',
          ),
          DIV(
            DIV(_id=add_rowid('plist_sz_avg_proc_for_nodes_plot')),
            _class='float',
          ),
          DIV(
            DIV(_id=add_rowid('tps_avg_block_for_nodes_plot')),
            _class='float',
          ),
          DIV(
            DIV(_id=add_rowid('bps_avg_block_for_nodes_plot')),
            _class='float',
          ),
          DIV(
            DIV(_id=add_rowid('disk_for_svc_plot')),
            _class='float',
          ),
          DIV(
            XML('&nbsp;'),
            _class='spacer',
          ),
          SCRIPT(
            plots,
            _name='plot_to_eval',
          ),
        )

    return d

@auth.requires_login()
def rows_stats_disks_per_svc(nodes=[], begin=None, end=None, lower=None, higher=None):
    if len(nodes) > 0:
        node_ids = set(nodes) & set(user_published_nodes())
        node_ids = map(repr, node_ids)
        svc_ids = ""
    else:
        q = q_filter(svc_field=db.svcmon.svc_id)
        q = apply_filters_id(q, db.svcmon.node_id, db.svcmon.svc_id)
        node_ids = [repr(r.node_id) for r in db(q).select(db.svcmon.node_id)]
        svc_ids = [repr(r.svc_id) for r in db(q).select(db.svcmon.svc_id)]
        svc_ids = 'and v.svc_id in (%s)'%','.join(svc_ids)
    if len(svc_ids) == 0:
        return []
    if len(node_ids) == 0:
        return []
    node_ids = 'and v.node_id in (%s)'%','.join(node_ids)

    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
        end = end + datetime.timedelta(days=0,
                                       hours=23-end.hour,
                                       minutes=59-end.minute,
                                       seconds=59-end.second,
                                      )
    sql = """select concat(c.svcname, " *", c.svc_app),
                    s.disk_size
             from stat_day_svc s, svcmon v, services c
             where day=(select max(day)
                        from stat_day_svc
                        where day>'%(begin)s'
                              and day<='%(end)s')
                   and s.day>'%(begin)s'
                   and s.day<='%(end)s'
                   and s.svc_id=v.svc_id
                   and s.svc_id=c.svc_id
                   %(node_ids)s
                   %(svc_ids)s
             group by s.svc_id
             order by s.disk_size
          """%dict(begin=begin, end=end, node_ids=node_ids, svc_ids=svc_ids)

    if lower is not None:
        sql += ' desc limit %d'%int(lower)
    elif higher is not None:
        sql += ' limit %d'%int(higher)
    else:
        sql += ' desc'

    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def avg_cpu_for_nodes_data(nodes=[], begin=None, end=None):
    if len(nodes) > 0:
        nodes = set(nodes) & set(user_published_nodes())
    data = {}
    metrics = [
        "usr",
        "nice",
        "sys",
        "iowait",
        "steal",
        "irq",
        "soft",
        "guest",
    ]
    for node in nodes:
        data[node] = {}
        for metric in metrics:
            data[node][metric] = timeseries.whisper_fetch_avg("nodes", node, "cpu", "all", metric, b=begin, e=end)
    return data

@auth.requires_login()
def avg_swp_for_nodes_data(nodes=[], begin=None, end=None, lower=None, higher=None):
    if len(nodes) > 0:
        nodes = set(nodes) & set(user_published_nodes())
    data = {}
    metrics = [
        "kbswpfree",
        "kbswpused",
    ]
    for node in nodes:
        data[node] = {}
        for metric in metrics:
            data[node][metric] = timeseries.whisper_fetch_avg("nodes", node, "swap", metric, b=begin, e=end)
    return data

@auth.requires_login()
def avg_proc_for_nodes_data(nodes=[], begin=None, end=None):
    if len(nodes) > 0:
        nodes = set(nodes) & set(user_published_nodes())
    data = {}
    metrics = [
        "runq_sz",
        "plist_sz",
        "ldavg_1",
        "ldavg_5",
        "ldavg_15",
    ]
    for node in nodes:
        data[node] = {}
        for metric in metrics:
            data[node][metric] = timeseries.whisper_fetch_avg("nodes", node, "proc", metric, b=begin, e=end)
    return data

@auth.requires_login()
def avg_mem_for_nodes_data(nodes=[], begin=None, end=None, lower=None, higher=None):
    if len(nodes) > 0:
        nodes = set(nodes) & set(user_published_nodes())
    data = {}
    metrics = [
        "kbmemfree",
        "kbcached",
    ]
    for node in nodes:
        data[node] = {}
        for metric in metrics:
            data[node][metric] = timeseries.whisper_fetch_avg("nodes", node, "mem_u", metric, b=begin, e=end)
    return data

@auth.requires_login()
def avg_block_for_nodes_data(nodes=[], begin=None, end=None, lower=None, higher=None):
    if len(nodes) > 0:
        nodes = set(nodes) & set(user_published_nodes())
    data = {}
    metrics = [
        "rtps",
        "wtps",
        "rbps",
        "wbps",
    ]
    for node in nodes:
        data[node] = {}
        for metric in metrics:
            data[node][metric] = timeseries.whisper_fetch_avg("nodes", node, "block", metric, b=begin, e=end)
    return data

#
# json data servers
#
@service.json
def json_avg_cpu_for_nodes():
    nodes = request.vars.node
    begin = request.vars.b
    end = request.vars.e

    if nodes is None:
        nodes = []
    else:
        nodes = nodes.split(',')

    data = avg_cpu_for_nodes_data(nodes, begin, end)
    d = []
    usr = []
    nice = []
    sys = []
    iowait = []
    steal = []
    irq = []
    soft = []
    guest = []

    j = 0
    for node, r in data.items():
        j += 1
        d.append(get_nodename(node))
        usr.append([r["usr"], j])
        nice.append([r["nice"], j])
        sys.append([r["sys"], j])
        iowait.append([r["iowait"], j])
        steal.append([r["steal"], j])
        irq.append([r["irq"], j])
        soft.append([r["soft"], j])
        guest.append([r["guest"], j])
    return [d, [usr, nice, sys, iowait, steal, irq, soft, guest]]

@service.json
def json_avg_swp_for_nodes():
    nodes = request.vars.node
    begin = request.vars.b
    end = request.vars.e

    if nodes is None:
        nodes = []
    else:
        nodes = nodes.split(',')

    data = avg_swp_for_nodes_data(nodes, begin, end)
    d = []
    kbswpfree = []
    kbswpused = []
    j = 0
    for node, r in data.items():
        j += 1
        d.append(get_nodename(node))
        kbswpfree.append([int(r["kbswpfree"]/1024), j])
        kbswpused.append([int(r["kbswpused"]/1024), j])
    return [d, [kbswpfree, kbswpused]]

@service.json
def json_avg_proc_for_nodes():
    nodes = request.vars.node
    begin = request.vars.b
    end = request.vars.e

    if nodes is None:
        nodes = []
    else:
        nodes = nodes.split(',')

    data = avg_proc_for_nodes_data(nodes, begin, end)
    d = []
    runq_sz = []
    plist_sz = []
    ldavg_1 = []
    ldavg_5 = []
    ldavg_15 = []
    j = 0
    for node, r in data.items():
        j += 1
        d.append(get_nodename(node))
        runq_sz.append([float(r["runq_sz"]), j])
        plist_sz.append([float(r["plist_sz"]), j])
        ldavg_1.append([float(r["ldavg_1"]), j])
        ldavg_5.append([float(r["ldavg_5"]), j])
        ldavg_15.append([float(r["ldavg_15"]), j])
    return [d, [runq_sz, plist_sz, ldavg_1, ldavg_5, ldavg_15]]

@service.json
def json_avg_mem_for_nodes():
    begin = request.vars.b
    end = request.vars.e
    nodes = request.vars.node

    if nodes is None:
        nodes = []
    else:
        nodes = nodes.split(',')

    data = avg_mem_for_nodes_data(nodes, begin, end)
    d = []
    free = []
    cache = []
    j = 0
    for node, r in data.items():
        j += 1
        d.append(get_nodename(node))
        free.append([int(r["kbmemfree"]/1024), j])
        cache.append([int(r["kbcached"]/1024), j])
    return [d, [free, cache]]

@service.json
def json_avg_block_for_nodes():
    nodes = request.vars.node
    begin = request.vars.b
    end = request.vars.e

    if nodes is None:
        nodes = []
    else:
        nodes = nodes.split(',')

    data = avg_block_for_nodes_data(nodes, begin, end)
    d = []
    rtps = []
    wtps = []
    rbps = []
    wbps = []
    j = 0
    for node, r in data.items():
        j += 1
        d.append(get_nodename(node))
        rtps.append([r["rtps"]/2, j])
        wtps.append([r["wtps"]/2, j])
        rbps.append([r["rbps"]/2, j])
        wbps.append([r["wbps"]/2, j])
    return [d, [rtps, wtps, rbps, wbps]]

@service.json
def json_disk_for_svc():
    nodes = request.vars.node
    begin = request.vars.b
    end = request.vars.e
    lower = request.vars.lower
    higher = request.vars.higher

    if nodes is None:
        nodes = []
    else:
        nodes = nodes.split(',')

    rows = rows_stats_disks_per_svc(nodes, begin, end, 15, higher)
    d = []
    disk_size = []
    n = len(rows)
    for i, r in enumerate(rows):
        j = n-i
        d.append(r[0])
        disk_size.append([r[1], j])
    d.reverse()
    return [d, [disk_size]]


#
# Scheduler stats
#
def scheduler_stats():
    d = SCRIPT(
        """$.when(osvc.app_started).then(function(){scheduler_stats("layout")})"""
    )
    return dict(table=d)

def scheduler_stats_load():
    return scheduler_stats()["table"]

