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
def stats():
    d = {}
    return d

@auth.requires_login()
def ajax_perfcmp_plot():
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
            _id=add_rowid('avg_cpu_for_nodes_plot'),
            _class='float',
          ),
          DIV(
            _id=add_rowid('avg_mem_for_nodes_plot'),
            _class='float',
          ),
          DIV(
            _id=add_rowid('avg_swp_for_nodes_plot'),
            _class='float',
          ),
          DIV(
            _id=add_rowid('avg_proc_for_nodes_plot_runq_sz'),
            _class='float',
          ),
          DIV(
            _id=add_rowid('avg_proc_for_nodes_plot_plist_sz'),
            _class='float',
          ),
          DIV(
            _id=add_rowid('avg_block_for_nodes_plot_tps'),
            _class='float',
          ),
          DIV(
            _id=add_rowid('avg_block_for_nodes_plot_bps'),
            _class='float',
          ),
          DIV(
            _id=add_rowid('disk_for_svc_plot'),
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

#
# raw data extractors
#
@auth.requires_login()
def rows_stat_day():
    o = db.stat_day.id
    q = o > 0
    b = db(q).select(orderby=o, limitby=(0,1)).first().day
    e = db(q).select(orderby=~o, limitby=(0,1)).first().day
    sql = """select *, %(d)s as d
             from stat_day
             group by d
             order by d"""%dict(d=period_concat(b, e, field='day'))
    return db.executesql(sql)

@auth.requires_login()
def rows_stats_disks_per_svc(nodes=[], begin=None, end=None, lower=None, higher=None):
    if len(nodes) > 0:
        nodes = map(repr, nodes)
        nodes = 'and v.mon_nodname in (%s)'%','.join(nodes)
    else:
        nodes = ''
    dom = _domain_perms()
    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
    sql = """select concat(
                      s.svcname, '@',
                      group_concat(v.mon_nodname separator ',')
                    ),
                    s.disk_size
             from stat_day_svc s, svcmon v
             where day=(select max(day)
                        from stat_day_svc
                        where day>'%(begin)s'
                              and day<'%(end)s')
                   and s.day>'%(begin)s'
                   and s.day<'%(end)s'
                   and s.svcname=v.mon_svcname
                   and v.mon_nodname like '%(dom)s'
                   %(nodes)s
             group by s.svcname
             order by s.disk_size
          """%dict(dom=dom, begin=begin, end=end, nodes=nodes)

    if lower is not None:
        sql += ' desc limit %d;'%int(lower)
    elif higher is not None:
        sql += ' limit %d;'%int(higher)
    else:
        sql += ' desc;'

    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_avg_cpu_for_nodes(nodes=[], begin=None, end=None, lower=None, higher=None):
    """ last day avg cpu usage per node
    """
    if len(nodes) > 0:
        nodes = map(repr, nodes)
        nodes = 'and nodename in (%s)'%','.join(nodes)
    else:
        nodes = ''
    dom = _domain_perms()
    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
    sql = """select nodename,
                    100-avg(idle) as avg,
                    cpu,
                    avg(usr) as avg_usr,
                    avg(nice) as avg_nice,
                    avg(sys) as avg_sys,
                    avg(iowait) as avg_iowait,
                    avg(steal) as avg_steal,
                    avg(irq) as avg_irq,
                    avg(soft) as avg_soft,
                    avg(guest) as avg_guest
             from stats_cpu
             where cpu='all'
               and date>'%(begin)s'
               and date<'%(end)s'
               and nodename like '%(dom)s'
               %(nodes)s
             group by nodename
             order by avg"""%dict(begin=str(begin),end=str(end),dom=dom,nodes=nodes)

    if lower is not None:
        sql += ' desc limit %d;'%int(lower)
    elif higher is not None:
        sql += ' limit %d;'%int(higher)
    else:
        sql += ' desc;'

    return db.executesql(sql)

@auth.requires_login()
def rows_avg_mem_for_nodes(nodes=[], begin=None, end=None, lower=None, higher=None):
    """ available mem
    """
    if len(nodes) > 0:
        nodes = map(repr, nodes)
        nodes = 'and nodename in (%s)'%','.join(nodes)
    else:
        nodes = ''
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
               from stats_mem_u
               where nodename like '%(dom)s'
               %(nodes)s
               and date>'%(begin)s'
               and date<'%(end)s'
               group by nodename
               order by nodename, date
             ) tmp
             order by avail
          """%dict(dom=dom, nodes=nodes, begin=str(begin), end=str(end))

    if lower is not None:
        sql += ' desc limit %d;'%int(lower)
    elif higher is not None:
        sql += ' limit %d;'%int(higher)
    else:
        sql += ' desc;'

    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_avg_swp_for_nodes(nodes=[], begin=None, end=None, lower=None, higher=None):
    if len(nodes) > 0:
        nodes = map(repr, nodes)
        nodes = 'and nodename in (%s)'%','.join(nodes)
    else:
        nodes = ''
    dom = _domain_perms()
    if begin is None or end is None:
        now = datetime.datetime.now()
        end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
        begin = end - datetime.timedelta(days=1)
    sql = """select * from (
               select nodename,
                      avg(kbswpfree) as avail,
                      avg(kbswpused)
               from stats_swap
               where nodename like '%(dom)s'
               %(nodes)s
               and date>'%(begin)s'
               and date<'%(end)s'
               group by nodename
               order by nodename, date
             ) tmp
             order by avail
          """%dict(dom=dom, nodes=nodes, begin=str(begin), end=str(end))

    if lower is not None:
        sql += ' desc limit %d;'%int(lower)
    elif higher is not None:
        sql += ' limit %d;'%int(higher)
    else:
        sql += ' desc;'

    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_avg_proc_for_nodes(nodes=[], begin=None, end=None, lower=None, higher=None):
    if len(nodes) > 0:
        nodes = map(repr, nodes)
        nodes = 'and nodename in (%s)'%','.join(nodes)
    else:
        nodes = ''
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
               from stats_proc
               where nodename like '%(dom)s'
               %(nodes)s
               and date>'%(begin)s'
               and date<'%(end)s'
               group by nodename
               order by nodename, date
             ) tmp
             order by o
          """%dict(dom=dom, nodes=nodes, begin=str(begin), end=str(end))

    if lower is not None:
        sql += ' desc limit %d;'%int(lower)
    elif higher is not None:
        sql += ' limit %d;'%int(higher)
    else:
        sql += ' desc;'

    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def rows_avg_block_for_nodes(nodes=[], begin=None, end=None, lower=None, higher=None):
    if len(nodes) > 0:
        nodes = map(repr, nodes)
        nodes = 'and nodename in (%s)'%','.join(nodes)
    else:
        nodes = ''
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
             from stats_block
             where date>'%(begin)s'
               and date<'%(end)s'
               and nodename like '%(dom)s'
               %(nodes)s
             group by nodename
             order by avg(rtps)+avg(wtps)"""%dict(begin=str(begin),end=str(end),dom=dom,nodes=nodes)

    if lower is not None:
        sql += ' desc limit %d;'%int(lower)
    elif higher is not None:
        sql += ' limit %d;'%int(higher)
    else:
        sql += ' desc;'

    return db.executesql(sql)

#
# json data servers
#
@service.json
def json_stat_day():
    rows = rows_stat_day()
    d = []
    nb_svc_not_prd = []
    nb_action = []
    nb_action_err = []
    nb_action_warn = []
    nb_action_ok = []
    disk_size = []
    ram_size = []
    nb_cpu_core = []
    nb_cpu_die = []
    watt = []
    rackunit = []
    nb_apps = []
    nb_accounts = []
    nb_svc_with_drp = []
    nb_nodes_not_prd = []
    nb_svc_prd = []
    nb_svc_cluster = []
    nb_nodes_prd = []
    nb_svc_not_cluster = []
    nb_svc_without_drp = []
    for r in rows:
        if r[2] is None or r[17] is None:
            v = None
        else:
            v = r[2] - r[17]
        nb_svc_not_prd.append([r[1], v])
        nb_action.append([r[1], r[3]])
        nb_action_err.append([r[1], r[4]])
        nb_action_warn.append([r[1], r[5]])
        nb_action_ok.append([r[1], r[6]])
        disk_size.append([r[1], r[7]])
        ram_size.append([r[1], r[8]])
        nb_cpu_core.append([r[1], r[9]])
        nb_cpu_die.append([r[1], r[10]])
        watt.append([r[1], r[11]])
        rackunit.append([r[1], r[12]])
        nb_apps.append([r[1], r[13]])
        nb_accounts.append([r[1], r[14]])
        nb_svc_with_drp.append([r[1], r[15]])
        if r[16] is None or r[19] is None:
            v = None
        else:
            v = r[16]-r[19]
        nb_nodes_not_prd.append([r[1], v])
        nb_svc_prd.append([r[1], r[17]])
        nb_svc_cluster.append([r[1], r[18]])
        nb_nodes_prd.append([r[1], r[19]])
        if r[15] is None or r[2] is None:
            v = None
        else:
            v = r[2]-r[15]
        nb_svc_without_drp.append([r[1], v])
        if r[18] is None or r[2] is None:
            v = None
        else:
            v = r[2]-r[18]
        nb_svc_not_cluster.append([r[1], v])
    return [nb_svc_not_prd,
            nb_action,
            nb_action_err,
            nb_action_warn,
            nb_action_ok,
            disk_size,
            ram_size,
            nb_cpu_core,
            nb_cpu_die,
            watt,
            rackunit,
            nb_apps,
            nb_accounts,
            nb_svc_with_drp,
            nb_nodes_not_prd,
            nb_svc_prd,
            nb_svc_cluster,
            nb_nodes_prd,
            nb_svc_not_cluster,
            nb_svc_without_drp]

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

    rows = rows_stats_disks_per_svc(nodes, begin, end, lower, higher)
    d = []
    disk_size = []
    for i, r in enumerate(rows):
        j = i+1
        d.append(r[0])
        disk_size.append([r[1], j])
    return [d, [disk_size]]


