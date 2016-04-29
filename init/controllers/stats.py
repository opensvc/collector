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
        node_ids = set(nodes) & set(user_nodes())
        node_ids = map(repr, node_ids)
        svc_ids = ""
    else:
        q = q_filter(svc_field=db.svcmon.svc_id)
        q = apply_filters_id(q, db.svcmon.node_id, db.svcmon.svc_id)
        node_ids = [repr(r.node_id) for r in db(q).select(db.svcmon.node_id)]
        svc_ids = [repr(r.svc_id) for r in db(q).select(db.svcmon.svc_id)]
        svc_ids = 'and v.svc_id in (%s)'%','.join(svc_ids)
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
def rows_avg_cpu_for_nodes(nodes=[], begin=None, end=None, lower=None, higher=None):
    """ last day avg cpu usage per node
    """
    if len(nodes) > 0:
        nodes = set(nodes) & set(user_nodes())
        nodes = map(repr, nodes)
    else:
        q = q_filter(app_field=db.nodes.app)
        q = apply_filters_id(q, db.nodes.node_id)
        nodes = [repr(r.node_id) for r in db(q).select(db.nodes.node_id)]
    nodes = 'and s.node_id in (%s)'%','.join(nodes)

    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
    sql = """select concat(n.nodename, " *", n.app),
                    0,
                    s.cpu,
                    avg(s.usr) as avg_usr,
                    avg(s.nice) as avg_nice,
                    avg(s.sys) as avg_sys,
                    avg(s.iowait) as avg_iowait,
                    avg(s.steal) as avg_steal,
                    avg(s.irq) as avg_irq,
                    avg(s.soft) as avg_soft,
                    avg(s.guest) as avg_guest
             from stats_cpu%(period)s s, nodes n
             where cpu='all'
               and s.node_id=n.node_id
               and s.date>'%(begin)s'
               and s.date<'%(end)s'
               %(nodes)s
             group by s.node_id
             order by 100-avg(s.usr+s.sys)"""%dict(begin=str(begin),end=str(end),nodes=nodes, period=get_period(begin, end))

    if lower is not None:
        sql += ' desc limit %d'%int(lower)
    elif higher is not None:
        sql += ' limit %d'%int(higher)
    else:
        sql += ' desc'

    return db.executesql(sql)

@auth.requires_login()
def rows_avg_mem_for_nodes(nodes=[], begin=None, end=None, lower=None, higher=None):
    """ available mem
    """
    if len(nodes) > 0:
        nodes = set(nodes) & set(user_nodes())
        nodes = map(repr, nodes)
    else:
        q = q_filter(app_field=db.nodes.app)
        q = apply_filters_id(q, db.nodes.node_id)
        nodes = [repr(r.node_id) for r in db(q).select(db.nodes.node_id)]
    nodes = 'and s.node_id in (%s)'%','.join(nodes)

    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
    sql = """select * from (
               select concat(n.nodename, " *", n.app),
                      avg(s.kbmemfree+s.kbcached) as avail,
                      avg(s.kbmemfree),
                      avg(s.kbcached)
               from stats_mem_u%(period)s s, nodes n
               where
                 s.node_id=n.node_id
                 and s.date>'%(begin)s'
                 and s.date<'%(end)s'
                 %(nodes)s
               group by s.node_id
               order by s.node_id, s.date
             ) tmp
             order by avail
          """%dict(nodes=nodes, begin=str(begin), end=str(end), period=get_period(begin, end))

    if lower is not None:
        sql += ' desc limit %d'%int(lower)
    elif higher is not None:
        sql += ' limit %d'%int(higher)
    else:
        sql += ' desc'

    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_avg_swp_for_nodes(nodes=[], begin=None, end=None, lower=None, higher=None):
    if len(nodes) > 0:
        nodes = set(nodes) & set(user_nodes())
        nodes = map(repr, nodes)
    else:
        q = q_filter(app_field=db.nodes.app)
        q = apply_filters_id(q, db.nodes.node_id)
        nodes = [repr(r.node_id) for r in db(q).select(db.nodes.node_id)]
    nodes = 'and s.node_id in (%s)'%','.join(nodes)

    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
    sql = """select * from (
               select concat(n.nodename, " *", n.app),
                      avg(s.kbswpfree) as avail,
                      avg(s.kbswpused)
               from stats_swap%(period)s s, nodes n
               where
                 s.node_id=n.node_id
                 and s.date>'%(begin)s'
                 and s.date<'%(end)s'
               %(nodes)s
               group by s.node_id
               order by s.node_id, s.date
             ) tmp
             order by avail
          """%dict(nodes=nodes, begin=str(begin), end=str(end), period=get_period(begin, end))

    if lower is not None:
        sql += ' desc limit %d'%int(lower)
    elif higher is not None:
        sql += ' limit %d'%int(higher)
    else:
        sql += ' desc'

    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_avg_proc_for_nodes(nodes=[], begin=None, end=None, lower=None, higher=None):
    if len(nodes) > 0:
        nodes = set(nodes) & set(user_nodes())
        nodes = map(repr, nodes)
    else:
        q = q_filter(app_field=db.nodes.app)
        q = apply_filters_id(q, db.nodes.node_id)
        nodes = [repr(r.node_id) for r in db(q).select(db.nodes.node_id)]
    nodes = 'and s.node_id in (%s)'%','.join(nodes)

    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
    sql = """select * from (
               select concat(n.nodename, " *", n.app),
                      avg(s.runq_sz),
                      avg(s.plist_sz),
                      avg(s.ldavg_1),
                      avg(s.ldavg_5),
                      avg(s.ldavg_15) as o
               from stats_proc%(period)s s, nodes n
               where
                 s.node_id=n.node_id
                 and s.date>'%(begin)s'
                 and s.date<'%(end)s'
                 %(nodes)s
               group by s.node_id
               order by s.node_id, s.date
             ) tmp
             order by o
          """%dict(nodes=nodes, begin=str(begin), end=str(end), period=get_period(begin, end))

    if lower is not None:
        sql += ' desc limit %d'%int(lower)
    elif higher is not None:
        sql += ' limit %d'%int(higher)
    else:
        sql += ' desc'

    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_avg_block_for_nodes(nodes=[], begin=None, end=None, lower=None, higher=None):
    if len(nodes) > 0:
        nodes = set(nodes) & set(user_nodes())
        nodes = map(repr, nodes)
    else:
        q = q_filter(app_field=db.nodes.app)
        q = apply_filters_id(q, db.nodes.node_id)
        nodes = [repr(r.node_id) for r in db(q).select(db.nodes.node_id)]
    nodes = 'and s.node_id in (%s)'%','.join(nodes)

    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
    sql = """select concat(n.nodename, " *", n.app),
                    avg(s.rtps),
                    avg(s.wtps),
                    avg(s.rbps),
                    avg(s.wbps)
             from stats_block%(period)s s, nodes n
             where
               s.node_id=n.node_id
               and s.date>'%(begin)s'
               and s.date<'%(end)s'
               %(nodes)s
             group by s.node_id
             order by avg(s.rbps)+avg(s.wbps)"""%dict(begin=str(begin),end=str(end),nodes=nodes, period=get_period(begin, end))

    if lower is not None:
        sql += ' desc limit %d'%int(lower)
    elif higher is not None:
        sql += ' limit %d'%int(higher)
    else:
        sql += ' desc'

    return db.executesql(sql)

#
# json data servers
#
@service.json
def json_avg_cpu_for_nodes():
    nodes = request.vars.node
    begin = request.vars.b
    end = request.vars.e
    lower = request.vars.lower
    higher = request.vars.higher

    if nodes is None:
        nodes = []
    else:
        nodes = nodes.split(',')

    rows = rows_avg_cpu_for_nodes(nodes, begin, end, lower, higher)
    d = []
    u = []
    usr = []
    nice = []
    sys = []
    iowait = []
    steal = []
    irq = []
    soft = []
    guest = []
    for i, r in enumerate(rows):
        j = i+1
        d.append(r[0])
        usr.append([r[3], j])
        nice.append([r[4], j])
        sys.append([r[5], j])
        iowait.append([r[6], j])
        steal.append([r[7], j])
        irq.append([r[8], j])
        soft.append([r[9], j])
        guest.append([r[10], j])
    return [d, [usr, nice, sys, iowait, steal, irq, soft, guest]]

@service.json
def json_avg_swp_for_nodes():
    nodes = request.vars.node
    begin = request.vars.b
    end = request.vars.e
    lower = request.vars.lower
    higher = request.vars.higher

    if nodes is None:
        nodes = []
    else:
        nodes = nodes.split(',')

    rows = rows_avg_swp_for_nodes(nodes, begin, end, lower, higher)
    d = []
    kbswpfree = []
    kbswpused = []
    for i, r in enumerate(rows):
        j = i+1
        d.append(r[0])
        kbswpfree.append([int(r[1]/1024), j])
        kbswpused.append([int(r[2]/1024), j])
    return [d, [kbswpfree, kbswpused]]

@service.json
def json_avg_proc_for_nodes():
    nodes = request.vars.node
    begin = request.vars.b
    end = request.vars.e
    lower = request.vars.lower
    higher = request.vars.higher

    if nodes is None:
        nodes = []
    else:
        nodes = nodes.split(',')

    rows = rows_avg_proc_for_nodes(nodes, begin, end, lower, higher)
    d = []
    runq_sz = []
    plist_sz = []
    ldavg_1 = []
    ldavg_5 = []
    ldavg_15 = []
    for i, r in enumerate(rows):
        j = i+1
        d.append(r[0])
        runq_sz.append([float(r[1]), j])
        plist_sz.append([float(r[2]), j])
        ldavg_1.append([float(r[3]), j])
        ldavg_5.append([float(r[4]), j])
        ldavg_15.append([float(r[5]), j])
    return [d, [runq_sz, plist_sz, ldavg_1, ldavg_5, ldavg_15]]

@service.json
def json_avg_mem_for_nodes():
    begin = request.vars.b
    end = request.vars.e
    nodes = request.vars.node
    lower = request.vars.lower
    higher = request.vars.higher

    if nodes is None:
        nodes = []
    else:
        nodes = nodes.split(',')

    rows = rows_avg_mem_for_nodes(nodes, begin, end, lower, higher)
    d = []
    free = []
    cache = []
    for i, r in enumerate(rows):
        j = i+1
        d.append(r[0])
        free.append([int(r[2]/1024), j])
        cache.append([int(r[3]/1024), j])
    return [d, [free, cache]]

@service.json
def json_avg_block_for_nodes():
    nodes = request.vars.node
    begin = request.vars.b
    end = request.vars.e
    lower = request.vars.lower
    higher = request.vars.higher

    if nodes is None:
        nodes = []
    else:
        nodes = nodes.split(',')

    rows = rows_avg_block_for_nodes(nodes, begin, end, lower, higher)
    d = []
    rtps = []
    wtps = []
    rbps = []
    wbps = []
    for i, r in enumerate(rows):
        j = i+1
        d.append(r[0])
        rtps.append([r[1]/2, j])
        wtps.append([r[2]/2, j])
        rbps.append([r[3]/2, j])
        wbps.append([r[4]/2, j])
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
        """scheduler_stats("layout")"""
    )
    return dict(table=d)

def scheduler_stats_load():
    return scheduler_stats()["table"]

