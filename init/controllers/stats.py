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
    for container_name, nodename in containers:
        did = '_'.join((rowid, nodename.replace('.','_'), container_name.replace('.','_')))
        l.append(H3('@'.join((container_name, nodename))))
        l.append(DIV(_id=did))
        sc += """sync_ajax('%(url)s', ['%(bs)s', '%(es)s'], '%(did)s', function(){});"""%dict(
                             url=URL(r=request,c='ajax_perf',f='ajax_perf_svc_plot_short',
                                     args=[nodename, did, container_name]),
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
        nodes = map(repr, nodes)
        svcnames = ""
    else:
        q = db.svcmon.id > 0
        q = apply_filters(q, db.svcmon.mon_nodname, db.svcmon.mon_svcname)
        nodes = [repr(r.mon_nodname) for r in db(q).select(db.svcmon.mon_nodname)]
        svcnames = [repr(r.mon_svcname) for r in db(q).select(db.svcmon.mon_svcname)]
        svcnames = 'and v.mon_svcname in (%s)'%','.join(svcnames)
    nodes = 'and v.mon_nodname in (%s)'%','.join(nodes)

    dom = _domain_perms()
    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
        end = end + datetime.timedelta(days=0,
                                       hours=23-end.hour,
                                       minutes=59-end.minute,
                                       seconds=59-end.second,
                                      )
    sql = """select s.svcname,
                    s.disk_size
             from stat_day_svc s, svcmon v
             where day=(select max(day)
                        from stat_day_svc
                        where day>'%(begin)s'
                              and day<='%(end)s')
                   and s.day>'%(begin)s'
                   and s.day<='%(end)s'
                   and s.svcname=v.mon_svcname
                   and v.mon_nodname like '%(dom)s'
                   %(nodes)s
                   %(svcnames)s
             group by s.svcname
             order by s.disk_size
          """%dict(dom=dom, begin=begin, end=end, nodes=nodes, svcnames=svcnames)

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
        nodes = map(repr, nodes)
    else:
        q = db.nodes.id > 0
        q = apply_filters(q, db.nodes.nodename)
        nodes = [repr(r.nodename) for r in db(q).select(db.nodes.nodename)]
    nodes = 'and nodename in (%s)'%','.join(nodes)

    dom = _domain_perms()
    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
    sql = """select nodename,
                    0,
                    cpu,
                    avg(usr) as avg_usr,
                    avg(nice) as avg_nice,
                    avg(sys) as avg_sys,
                    avg(iowait) as avg_iowait,
                    avg(steal) as avg_steal,
                    avg(irq) as avg_irq,
                    avg(soft) as avg_soft,
                    avg(guest) as avg_guest
             from stats_cpu%(period)s
             where cpu='all'
               and date>'%(begin)s'
               and date<'%(end)s'
               and nodename like '%(dom)s'
               %(nodes)s
             group by nodename
             order by 100-avg(usr+sys)"""%dict(begin=str(begin),end=str(end),dom=dom,nodes=nodes, period=get_period(begin, end))

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
        nodes = map(repr, nodes)
    else:
        q = db.nodes.id > 0
        q = apply_filters(q, db.nodes.nodename)
        nodes = [repr(r.nodename) for r in db(q).select(db.nodes.nodename)]
    nodes = 'and nodename in (%s)'%','.join(nodes)

    dom = _domain_perms()
    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
    sql = """select * from (
               select nodename,
                      avg(kbmemfree+kbcached) as avail,
                      avg(kbmemfree),
                      avg(kbcached)
               from stats_mem_u%(period)s
               where nodename like '%(dom)s'
               %(nodes)s
               and date>'%(begin)s'
               and date<'%(end)s'
               group by nodename
               order by nodename, date
             ) tmp
             order by avail
          """%dict(dom=dom, nodes=nodes, begin=str(begin), end=str(end), period=get_period(begin, end))

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
        nodes = map(repr, nodes)
    else:
        q = db.nodes.id > 0
        q = apply_filters(q, db.nodes.nodename)
        nodes = [repr(r.nodename) for r in db(q).select(db.nodes.nodename)]
    nodes = 'and nodename in (%s)'%','.join(nodes)

    dom = _domain_perms()
    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
    sql = """select * from (
               select nodename,
                      avg(kbswpfree) as avail,
                      avg(kbswpused)
               from stats_swap%(period)s
               where nodename like '%(dom)s'
               %(nodes)s
               and date>'%(begin)s'
               and date<'%(end)s'
               group by nodename
               order by nodename, date
             ) tmp
             order by avail
          """%dict(dom=dom, nodes=nodes, begin=str(begin), end=str(end), period=get_period(begin, end))

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
        nodes = map(repr, nodes)
    else:
        q = db.nodes.id > 0
        q = apply_filters(q, db.nodes.nodename)
        nodes = [repr(r.nodename) for r in db(q).select(db.nodes.nodename)]
    nodes = 'and nodename in (%s)'%','.join(nodes)

    dom = _domain_perms()
    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
    sql = """select * from (
               select nodename,
                      avg(runq_sz),
                      avg(plist_sz),
                      avg(ldavg_1),
                      avg(ldavg_5),
                      avg(ldavg_15) as o
               from stats_proc%(period)s
               where nodename like '%(dom)s'
               %(nodes)s
               and date>'%(begin)s'
               and date<'%(end)s'
               group by nodename
               order by nodename, date
             ) tmp
             order by o
          """%dict(dom=dom, nodes=nodes, begin=str(begin), end=str(end), period=get_period(begin, end))

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
        nodes = map(repr, nodes)
    else:
        q = db.nodes.id > 0
        q = apply_filters(q, db.nodes.nodename)
        nodes = [repr(r.nodename) for r in db(q).select(db.nodes.nodename)]
    nodes = 'and nodename in (%s)'%','.join(nodes)

    dom = _domain_perms()
    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
    sql = """select nodename,
                    avg(rtps),
                    avg(wtps),
                    avg(rbps),
                    avg(wbps)
             from stats_block%(period)s
             where date>'%(begin)s'
               and date<'%(end)s'
               and nodename like '%(dom)s'
               %(nodes)s
             group by nodename
             order by avg(rbps)+avg(wbps)"""%dict(begin=str(begin),end=str(end),dom=dom,nodes=nodes, period=get_period(begin, end))

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
        """$.when(osvc.app_started).then(function(){ scheduler_stats("layout") }) """
    )
    return dict(table=d)

def scheduler_stats_load():
    return scheduler_stats()["table"]

