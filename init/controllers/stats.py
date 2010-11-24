from pychart import *

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
    d.update(stats_disks_per_svc())
    d.update(stats_last_day_avg_cpu())
    d.update(stats_last_day_avg_mem())
    return d

@auth.requires_login()
def stats_disks_per_svc():
    """ disks per svc
    """
    dom = _domain_perms()
    if dom is None:
        dom = '%'
    sql = """select svcname, group_concat(disk_size order by day separator ',')
             from stat_day_svc
             where svcname like '%(dom)s'
             group by svcname
          """%dict(dom=dom)
    rows = db.executesql(sql)

    if len(rows) == 0:
        return dict(stat_disk_svc=None)

    import random
    rand = int(random.random()*1000000)
    img = 'stat_disk_svc_'+str(rand)+'.png'
    action = str(URL(r=request,c='static',f=img))
    path = 'applications'+action
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    def compute_size(s):
        if s is None or len(s) == 0:
            return 0
        l = s.split(',')
        l.reverse()
        for w in l:
            if len(w) > 0: break
        if len(w) == 0:
            return 0
        return int(w)

    data1 = [(row[0], compute_size(row[1])) for row in rows]
    data = sorted(data1, key = lambda x: x[1])[-15:]

    ar = area.T(x_coord = linear_coord.T(),
                y_coord = category_coord.T(data, 0),
                y_axis = axis.Y(label = "", format="/6{}%s"),
                x_axis = axis.X(label = "", format=format2_y)
               )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="disk size (GB)",
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       width = 2,
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()
    return dict(stat_disk_svc=img)

@auth.requires_login()
def stats_last_day_avg_cpu_for_nodes(nodes=[], begin=None, end=None):
    return _stats_last_day_avg_cpu(rows_avg_cpu_for_nodes(nodes, begin, end))

@auth.requires_login()
def stats_last_day_avg_cpu():
    """ last day avg cpu usage per node
    """
    dom = _domain_perms()
    now = datetime.datetime.now()
    end = now - datetime.timedelta(days=0, microseconds=now.microsecond)
    begin = end - datetime.timedelta(days=1)
    sql = """select nodename,100-avg(idle) as avg,std(idle) as std
             from stats_cpu
             where cpu='all'
               and date>'%(begin)s'
               and date<'%(end)s'
               and nodename like '%(dom)s'
             group by nodename
             order by avg"""%dict(begin=str(begin),end=str(end),dom=dom)
    rows = db.executesql(sql)
    return _stats_last_day_avg_cpu(rows)

@auth.requires_login()
def _stats_last_day_avg_cpu(rows):
    if len(rows) == 0:
        return dict(stat_cpu_avg_day=None)

    import random
    rand = int(random.random()*1000000)
    img = 'stat_cpu_avg_day_'+str(rand)+'.png'
    action = str(URL(r=request,c='static',f=img))
    path = 'applications'+action
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    data1 = [(row[0], row[1]) for row in rows]
    if len(data1) > 31:
        data = data1[0:15] + [("...", 0)] + data1[-15:]
    else:
        data = data1
    ar = area.T(x_coord = linear_coord.T(),
                size = (150,len(data)*6),
                y_coord = category_coord.T(data, 0),
                y_axis = axis.Y(label = "", format="/6{}%s"),
                x_axis = axis.X(label = "", format=format2_y)
               )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="cpu usage (%)",
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       width = 2,
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()
    return dict(stat_cpu_avg_day=img)

@auth.requires_login()
def rows_avg_mem_for_nodes(nodes=[], begin=None, end=None):
    """ available mem
    """
    nodes = map(repr, nodes)
    nodes = ','.join(nodes)
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
               and nodename in (%(nodes)s)
               and date>'%(begin)s'
               and date<'%(end)s'
               group by nodename
               order by nodename, date
             ) tmp
             order by avail desc;
          """%dict(dom=dom, nodes=nodes, begin=str(begin), end=str(end))
    rows = db.executesql(sql)
    return rows

@auth.requires_login()
def stats_last_day_avg_mem_for_nodes(nodes=[], begin=None, end=None):
    return _stats_last_day_avg_mem(rows_avg_mem_for_nodes(nodes, begin, end))

@auth.requires_login()
def stats_last_day_avg_mem():
    """ available mem
    """
    dom = _domain_perms()
    sql = """select * from (
               select nodename,(kbmemfree+kbcached) as avail
               from stats_mem_u
               where nodename like '%(dom)s'
               group by nodename
               order by nodename, date
             ) tmp
             order by avail desc;
          """%dict(dom=dom)
    rows = db.executesql(sql)
    return _stats_last_day_avg_mem(rows)

@auth.requires_login()
def _stats_last_day_avg_mem(rows):
    if len(rows) == 0:
        return dict(stat_mem_avail=None)

    import random
    rand = int(random.random()*1000000)
    img = 'stat_mem_avail_'+str(rand)+'.png'
    action = str(URL(r=request,c='static',f=img))
    path = 'applications'+action
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    data1 = [(row[0], int(row[1])) for row in rows]
    if len(data1) > 31:
        data = data1[0:15] + [("...", 0)] + data1[-15:]
    else:
        data = data1
    ar = area.T(x_coord = linear_coord.T(),
                size = (150,len(data)*6),
                y_coord = category_coord.T(data, 0),
                y_axis = axis.Y(label = "", format="/6{}%s"),
                x_axis = axis.X(label = "", format=format2_y)
               )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="available memory (KB)",
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       width = 2,
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()
    return dict(stat_mem_avail=img)

@auth.requires_login()
def ajax_perfcmp_plot():
    nodes = request.vars.node
    b = request.vars.begin
    e = request.vars.end

    if len(request.vars.node.split(',')) == 0:
         return DIV(T("No nodes selected"))

    plots = []
    plots.append("stats_avg_cpu_for_nodes('%(url)s', 'avg_cpu_for_nodes_plot');"%dict(
      url=URL(r=request,
              f='call/json/json_avg_cpu_for_nodes',
              vars={'node':nodes, 'b':b, 'e':e}
          )
    ))
    plots.append("stats_avg_mem_for_nodes('%(url)s', 'avg_mem_for_nodes_plot');"%dict(
      url=URL(r=request,
              f='call/json/json_avg_mem_for_nodes',
              vars={'node':nodes, 'b':b, 'e':e}
          )
    ))
    plots.append("stats_avg_block_for_nodes('%(url)s', 'avg_block_for_nodes_plot');"%dict(
      url=URL(r=request,
              f='call/json/json_avg_block_for_nodes',
              vars={'node':nodes, 'b':b, 'e':e}
          )
    ))

    d = DIV(
          DIV(
            _id='avg_cpu_for_nodes_plot',
            _class='float',
          ),
          DIV(
            _id='avg_mem_for_nodes_plot',
            _class='float',
          ),
          DIV(
            _id='avg_block_for_nodes_plot_tps',
            _class='float',
          ),
          DIV(
            _id='avg_block_for_nodes_plot_bps',
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
def ajax_perfcmp():
    nodes = set(request.vars.node.split(','))
    nodes -= set([""])
    begin = request.vars.begin
    end = request.vars.end
    n = len(nodes)

    if n == 0:
         return DIV(T("No nodes selected"))

    charts = dict()
    charts.update(stats_last_day_avg_cpu_for_nodes(nodes, begin=begin, end=end))
    charts.update(stats_last_day_avg_mem_for_nodes(nodes, begin=begin, end=end))

    img = {}
    for key in charts:
        if charts[key] is None:
            img[key] = SPAN()
        else:
            img[key] = IMG(_src=URL(r=request,c='static',f=charts[key]))

    d = DIV(
          H2(T("Computing ressource usage")),
            DIV(
              img['stat_cpu_avg_day'],
              _class='float',
            ),
            DIV(
              img['stat_mem_avail'],
              _class='float',
            ),
            DIV(
              XML('&nbsp;'),
              _class='spacer',
            ),
          )

    return d

#
# raw data extractors
#
@auth.requires_login()
def rows_avg_cpu_for_nodes(nodes=[], begin=None, end=None):
    """ last day avg cpu usage per node
    """
    nodes = map(repr, nodes)
    nodes = ','.join(nodes)
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
               and nodename in (%(nodes)s)
             group by nodename
             order by avg"""%dict(begin=str(begin),end=str(end),dom=dom,nodes=nodes)
    return db.executesql(sql)

@auth.requires_login()
def rows_avg_cpu_for_nodes(nodes=[], begin=None, end=None):
    """ last day avg cpu usage per node
    """
    nodes = map(repr, nodes)
    nodes = ','.join(nodes)
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
               and nodename in (%(nodes)s)
             group by nodename
             order by avg"""%dict(begin=str(begin),end=str(end),dom=dom,nodes=nodes)
    return db.executesql(sql)

@auth.requires_login()
def rows_avg_block_for_nodes(nodes=[], begin=None, end=None):
    nodes = map(repr, nodes)
    nodes = ','.join(nodes)
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
               and nodename in (%(nodes)s)
             group by nodename
             order by avg(rtps)+avg(wtps)"""%dict(begin=str(begin),end=str(end),dom=dom,nodes=nodes)
    return db.executesql(sql)

#
# json data servers
#
@service.json
def json_avg_cpu_for_nodes():
    nodes = request.vars.node
    begin = request.vars.begin
    end = request.vars.end
    if nodes is None:
        return []
    nodes = nodes.split(',')
    rows = rows_avg_cpu_for_nodes(nodes, begin, end)
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
def json_avg_mem_for_nodes():
    nodes = request.vars.node
    begin = request.vars.begin
    end = request.vars.end
    if nodes is None:
        return []
    nodes = nodes.split(',')
    rows = rows_avg_mem_for_nodes(nodes, begin, end)
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
    begin = request.vars.begin
    end = request.vars.end
    if nodes is None:
        return []
    nodes = nodes.split(',')
    rows = rows_avg_block_for_nodes(nodes, begin, end)
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


