from pychart import *

@auth.requires_login()
def perf_stats_blockdev(node, s, e):
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

    if len(rows) == 0:
        return SPAN()

    from time import mktime

    def format_x(x):
        return "/6{}" + str(x)

    def format_y(x):
        return "/6{}" + str(x)

    import random
    rand = int(random.random()*1000000)

    """ %util
    """
    data1 = [(row[0],
              row[15],
              row[16],
              row[17],
             ) for row in rows]
    data = sorted(data1, key = lambda x: x[1])

    action1 = URL(r=request,c='static',f='stats_blockdev1_'+str(rand)+'.png')
    path = 'applications'+str(action1)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = category_coord.T(data, 0),
           x_axis = axis.X(label = 'blockdev %util', format=format_x, tic_interval=10),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (0, 100),
           size = (150,len(data)*8),
         )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="avg",
                       line_style=None,
                       width=2,
                       hcol=1,
                       cluster=(1,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot2 = bar_plot.T(label="min",
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       line_style=None,
                       width=2,
                       hcol=2,
                       cluster=(0,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot3 = bar_plot.T(label="max",
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       width=2,
                       hcol=3,
                       cluster=(2,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    ar.add_plot(plot1, plot2, plot3)
    ar.draw(can)
    can.close()

    """ service time
    """
    data1 = [(row[0],
              row[12],
              row[13],
              row[14],
             ) for row in rows]
    data = sorted(data1, key = lambda x: x[1])

    action2 = URL(r=request,c='static',f='stats_blockdev2_'+str(rand)+'.png')
    path = 'applications'+str(action2)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = category_coord.T(data, 0),
           x_axis = axis.X(label = 'blockdev service time (ms)', format=format_x),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (0, None),
           size = (150,len(data)*8),
         )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="avg",
                       line_style=None,
                       width=2,
                       hcol=1,
                       cluster=(1,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot2 = bar_plot.T(label="min",
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       line_style=None,
                       width=2,
                       hcol=2,
                       cluster=(0,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot3 = bar_plot.T(label="max",
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       width=2,
                       hcol=3,
                       cluster=(2,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    ar.add_plot(plot1, plot2, plot3)
    ar.draw(can)
    can.close()

    """ await
    """
    data1 = [(row[0],
              row[9],
              row[10],
              row[11],
             ) for row in rows]
    data = sorted(data1, key = lambda x: x[1])

    action3 = URL(r=request,c='static',f='stats_blockdev3_'+str(rand)+'.png')
    path = 'applications'+str(action3)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = category_coord.T(data, 0),
           x_axis = axis.X(label = 'blockdev wait time (ms)', format=format_x),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (0, None),
           size = (150,len(data)*8),
         )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="avg",
                       line_style=None,
                       width=2,
                       hcol=1,
                       cluster=(1,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot2 = bar_plot.T(label="min",
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       line_style=None,
                       width=2,
                       hcol=2,
                       cluster=(0,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot3 = bar_plot.T(label="max",
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       width=2,
                       hcol=3,
                       cluster=(2,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    ar.add_plot(plot1, plot2, plot3)
    ar.draw(can)
    can.close()

    """ request size
    """
    data1 = [(row[0],
              row[6],
              row[7],
              row[8],
             ) for row in rows]
    data = sorted(data1, key = lambda x: x[1])

    action4 = URL(r=request,c='static',f='stats_blockdev4_'+str(rand)+'.png')
    path = 'applications'+str(action4)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = category_coord.T(data, 0),
           x_axis = axis.X(label = 'blockdev request size (sector)',
                           format=format_x),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (0, None),
           size = (150,len(data)*8),
         )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="avg",
                       line_style=None,
                       width=2,
                       hcol=1,
                       cluster=(1,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot2 = bar_plot.T(label="min",
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       line_style=None,
                       width=2,
                       hcol=2,
                       cluster=(0,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot3 = bar_plot.T(label="max",
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       width=2,
                       hcol=3,
                       cluster=(2,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    ar.add_plot(plot1, plot2, plot3)
    ar.draw(can)
    can.close()

    """ tps
    """
    data1 = [(row[0],
              row[1],
              row[2],
              row[3],
             ) for row in rows]
    data = sorted(data1, key = lambda x: x[1])

    action5 = URL(r=request,c='static',f='stats_blockdev5_'+str(rand)+'.png')
    path = 'applications'+str(action5)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = category_coord.T(data, 0),
           x_axis = axis.X(label = 'blockdev io//s',
                           format=format_x),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (0, None),
           size = (150,len(data)*8),
         )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="avg",
                       line_style=None,
                       width=2,
                       hcol=1,
                       cluster=(1,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot2 = bar_plot.T(label="min",
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       line_style=None,
                       width=2,
                       hcol=2,
                       cluster=(0,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot3 = bar_plot.T(label="max",
                       width=2,
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       hcol=3,
                       cluster=(2,3),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    ar.add_plot(plot1, plot2, plot3)
    ar.draw(can)
    can.close()

    return DIV(
             IMG(_src=action1),
             IMG(_src=action4),
             IMG(_src=action2),
             IMG(_src=action3),
             IMG(_src=action5),
           )

@auth.requires_login()
def perf_stats_proc(node, s, e):
    q = db.stats_proc.nodename == node
    q &= db.stats_proc.date > s
    q &= db.stats_proc.date < e
    rows = db(q).select(orderby=db.stats_proc.date)
    if len(rows) == 0:
        return SPAN()

    from time import mktime

    start_date = tic_start_ts(rows)

    def format_x(ts):
        d = datetime.datetime.fromtimestamp(ts+start_date)
        return "/a50/5{}" + d.strftime("%y-%m-%d %H:%M")

    def format_y(x):
        return "/6{}" + str(x)

    import random
    rand = int(random.random()*1000000)


    """ Usage KB
    """
    action1 = URL(r=request,c='static',f='stats_load_'+str(rand)+'.png')
    path = 'applications'+str(action1)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    data = [(mktime(row.date.timetuple())-start_date,
             row.runq_sz,
             row.plist_sz,
             row.ldavg_1,
             row.ldavg_5,
             row.ldavg_15,
            ) for row in rows]

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'load average',
                      format=format_x,
                      tic_interval=tic_interval_from_ts,
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (None, mktime(rows[-1].date.timetuple())-start_date),
         )
    bar_plot.fill_styles.reset()
    plot1 = line_plot.T(label="ldavg_1",
                       ycol=3,
                       line_style=line_style.T(width=2, color=color.gray30),
                       data = data,
                       data_label_format="",
                       )
    plot2 = line_plot.T(label="ldavg_5",
                       ycol=4,
                       line_style=line_style.T(width=2, color=color.gray50),
                       data = data,
                       data_label_format="",
                       )
    plot3 = line_plot.T(label="ldavg_15",
                       ycol=5,
                       line_style=line_style.T(width=2, color=color.gray70),
                       data = data,
                       data_label_format="",
                       )
    plot4 = line_plot.T(label="runq_sz",
                       ycol=1,
                       line_style=line_style.T(width=1, color=color.salmon),
                       data = data,
                       data_label_format="",
                       )
    ar.add_plot(plot1, plot2, plot3, plot4)
    ar.draw(can)
    can.close()


    """ Usage Percent
    """
    rand = int(random.random()*1000000)
    action2 = URL(r=request,c='static',f='stats_proc_'+str(rand)+'.png')
    path = 'applications'+str(action2)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'process list',
                      format=format_x,
                      tic_interval=tic_interval_from_ts,
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (None, mktime(rows[-1].date.timetuple())-start_date),
         )
    bar_plot.fill_styles.reset()
    plot1 = line_plot.T(label="plist_sz",
                       ycol=2,
                       line_style=line_style.T(width=2, color=color.salmon),
                       data = data,
                       data_label_format="",
                       )
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()
    return DIV(
             IMG(_src=action1),
             IMG(_src=action2),
           )

@auth.requires_login()
def perf_stats_swap(node, s, e):
    q = db.stats_swap.nodename == node
    q &= db.stats_swap.date > s
    q &= db.stats_swap.date < e
    rows = db(q).select(orderby=db.stats_swap.date)
    if len(rows) == 0:
        return SPAN()

    w = __stats_bar_width(rows)

    from time import mktime

    start_date = tic_start_ts(rows)

    def format_x(ts):
        d = datetime.datetime.fromtimestamp(ts+start_date)
        return "/a50/5{}" + d.strftime("%y-%m-%d %H:%M")

    def format_y(x):
        return "/6{}" + str(x)

    import random
    rand = int(random.random()*1000000)


    """ Usage KB
    """
    action1 = URL(r=request,c='static',f='stats_swap_'+str(rand)+'.png')
    path = 'applications'+str(action1)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    data = [(mktime(row.date.timetuple())-start_date,
             row.kbswpused-row.kbswpcad,
             row.kbswpcad,
             row.kbswpfree,
             row.pct_swpused,
             row.pct_swpcad,
            ) for row in rows]

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'swap usage (KB)',
                      format=format_x,
                      tic_interval=tic_interval_from_ts,
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (None, mktime(rows[-1].date.timetuple())-start_date),
         )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="used",
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       hcol=1,
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot2 = bar_plot.T(label="used, cached",
                       hcol=2,
                       stack_on=plot1,
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot3 = bar_plot.T(label="free",
                       hcol=3,
                       stack_on=plot2,
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    ar.add_plot(plot1, plot2, plot3)
    ar.draw(can)
    can.close()


    return DIV(
             IMG(_src=action1),
           )

@auth.requires_login()
def perf_stats_block(node, s, e):
    q = db.stats_block.nodename == node
    q &= db.stats_block.date > s
    q &= db.stats_block.date < e
    rows = db(q).select(orderby=db.stats_block.date)
    if len(rows) == 0:
        return SPAN()

    from time import mktime

    start_date = tic_start_ts(rows)

    def format_x(ts):
        d = datetime.datetime.fromtimestamp(ts+start_date)
        return "/a50/5{}" + d.strftime("%y-%m-%d %H:%M")

    def format_y(x):
        return "/6{}" + str(x)

    import random
    rand = int(random.random()*1000000)


    """ TPS
    """
    action1 = URL(r=request,c='static',f='stats_block1_'+str(rand)+'.png')
    path = 'applications'+str(action1)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    data = [(mktime(row.date.timetuple())-start_date,
             row.tps,
             row.rtps,
             row.wtps,
             row.rbps/2,
             row.wbps/2,
            ) for row in rows]

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'io//s',
                      tic_interval=tic_interval_from_ts,
                      format=format_x
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (None, mktime(rows[-1].date.timetuple())-start_date),
         )
    bar_plot.fill_styles.reset()
    plot1 = line_plot.T(label="read",
                       ycol=2,
                       line_style=line_style.T(color=color.thistle3,
                                               width=2),
                       data = data,
                       data_label_format="",
                       )
    plot2 = line_plot.T(label="write",
                       ycol=3,
                       line_style=line_style.T(color=color.salmon,
                                               width=2),
                       data = data,
                       data_label_format="",
                       )
    ar.add_plot(plot1, plot2)
    ar.draw(can)
    can.close()


    """ BPS
    """
    rand = int(random.random()*1000000)
    action2 = URL(r=request,c='static',f='stats_block2_'+str(rand)+'.png')
    path = 'applications'+str(action2)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'KB//s',
                      tic_interval = tic_interval_from_ts,
                      format=format_x
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (None, mktime(rows[-1].date.timetuple())-start_date),
         )
    bar_plot.fill_styles.reset()
    plot1 = line_plot.T(label="read",
                       ycol=4,
                       line_style=line_style.T(color=color.thistle3,
                                               width=2),
                       data = data,
                       data_label_format="",
                       )
    plot2 = line_plot.T(label="write",
                       ycol=5,
                       line_style=line_style.T(color=color.salmon,
                                               width=2),
                       data = data,
                       data_label_format="",
                       )
    ar.add_plot(plot1, plot2)
    ar.draw(can)
    can.close()

    return DIV(
             IMG(_src=action1),
             IMG(_src=action2),
           )

@auth.requires_login()
def perf_stats_mem_u(node, s, e):
    q = db.stats_mem_u.nodename == node
    q &= db.stats_mem_u.date > s
    q &= db.stats_mem_u.date < e
    rows = db(q).select(orderby=db.stats_mem_u.date)
    if len(rows) == 0:
        return SPAN()

    w = __stats_bar_width(rows)

    from time import mktime

    start_date = tic_start_ts(rows)

    def format_x(ts):
        d = datetime.datetime.fromtimestamp(ts+start_date)
        return "/a50/5{}" + d.strftime("%y-%m-%d %H:%M")

    def format_y(x):
        return "/6{}" + str(x)

    import random
    rand = int(random.random()*1000000)


    """ Usage KB
    """
    action1 = URL(r=request,c='static',f='stats_mem_u_'+str(rand)+'.png')
    path = 'applications'+str(action1)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    data = [(mktime(row.date.timetuple())-start_date,
             row.kbmemfree,
             row.kbmemused-row.kbbuffers-row.kbcached-row.kbmemsys,
             row.pct_memused,
             row.kbbuffers,
             row.kbcached,
             row.kbcommit,
             row.pct_commit,
             row.kbmemsys,
            ) for row in rows]

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'memory usage (KB)',
                      format=format_x,
                      tic_interval=tic_interval_from_ts,
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (None, mktime(rows[-1].date.timetuple())-start_date)
         )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="free",
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       hcol=1,
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot2 = bar_plot.T(label="used",
                       hcol=2,
                       stack_on=plot1,
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot3 = bar_plot.T(label="used, buffer",
                       hcol=4,
                       stack_on=plot2,
                       fill_style=fill_style.black,
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot4 = bar_plot.T(label="used, cache",
                       hcol=5,
                       stack_on=plot3,
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot5 = bar_plot.T(label="used, sys",
                       hcol=8,
                       stack_on=plot4,
                       fill_style=fill_style.Plain(bgcolor=color.coral),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot6 = line_plot.T(label="commit",
                       ycol=6,
                       line_style=line_style.T(color=color.darkkhaki,
                                               width=2),
                       data = data,
                       data_label_format="",
                       )
    ar.add_plot(plot1, plot2, plot3, plot4, plot5, plot6)
    ar.draw(can)
    can.close()


    """ Usage Percent
    """
    rand = int(random.random()*1000000)
    action2 = URL(r=request,c='static',f='stats_mem_u_'+str(rand)+'.png')
    path = 'applications'+str(action2)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'memory usage (%)',
                      tic_interval = tic_interval_from_ts,
                      format=format_x
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (None, mktime(rows[-1].date.timetuple())-start_date)
         )
    bar_plot.fill_styles.reset()
    plot1 = line_plot.T(label="used",
                       ycol=3,
                       line_style=line_style.T(color=color.salmon,
                                               width=2),
                       data = data,
                       data_label_format="",
                       )
    plot2 = line_plot.T(label="commit",
                       ycol=7,
                       line_style=line_style.T(color=color.darkkhaki,
                                               width=2),
                       data = data,
                       data_label_format="",
                       )
    ar.add_plot(plot1, plot2)
    ar.draw(can)
    can.close()
    return DIV(
             IMG(_src=action1),
             IMG(_src=action2),
           )


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
    def format(x):
        return SPAN(x)
    return SPAN(map(format, t))

@auth.requires_login()
def perf_stats_netdev_one(node, s, e, dev):
    q = db.stats_netdev.nodename == node
    q &= db.stats_netdev.date > s
    q &= db.stats_netdev.date < e
    q &= db.stats_netdev.dev == dev
    rows = db(q).select(orderby=db.stats_netdev.date)
    if len(rows) == 0:
        return SPAN()

    from time import mktime

    start_date = tic_start_ts(rows)

    def format_x(ts):
        d = datetime.datetime.fromtimestamp(ts+start_date)
        return "/a50/5{}" + d.strftime("%y-%m-%d %H:%M")

    def format_y(x):
        return "/6{}" + str(x)

    def format2_y(x):
        return "/a50/6{}" + str(x)

    import random
    rand = int(random.random()*1000000)
    action = URL(r=request,c='static',f='stats_netdev_'+str(rand)+'.png')
    path = 'applications'+str(action)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    data = [(mktime(row.date.timetuple())-start_date,
             row.rxpckps,
             row.txpckps,
             row.rxkBps,
             row.txkBps) for row in rows]

    ar = area.T(
           #x_coord = category_coord.T(data, 0),
           x_coord = linear_coord.T(),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'dev '+dev,
                      format=format_x,
                      tic_interval=tic_interval_from_ts,
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (None, mktime(rows[-1].date.timetuple())-start_date)
         )
    bar_plot.fill_styles.reset();
    plot1 = line_plot.T(label="rx kB//s",
                       ycol=3,
                       line_style=line_style.T(color=color.thistle3, width=2),
                       data = data,
                       data_label_format="",
                       )
    plot2 = line_plot.T(label="tx kB//s",
                       ycol=4,
                       line_style=line_style.T(width=2, color=color.salmon),
                       data = data,
                       data_label_format="",
                       )
    ar.add_plot(plot1, plot2)
    ar.draw(can)
    can.close()

    return DIV(IMG(_src=action))

@auth.requires_login()
def perf_stats_netdev_err(node, s, e):
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

    if len(rows) == 0:
        return SPAN()

    from time import mktime

    def format_x(x):
        return "/6{}" + str(x)

    def format_y(x):
        return "/6{}" + str(x)

    import random
    rand = int(random.random()*1000000)

    """ %util
    """
    data1 = [(row[0],
              row[1],
              row[2],
              row[3],
              row[4],
              row[5],
             ) for row in rows]
    data = sorted(data1, key = lambda x: x[1])

    action1 = URL(r=request,c='static',f='stats_netdev_err_'+str(rand)+'.png')
    path = 'applications'+str(action1)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = linear_coord.T(),
           y_coord = category_coord.T(data, 0),
           x_axis = axis.X(label = 'net dev errors', format=format_x, tic_interval=10),
           y_axis = axis.Y(label = "", format=format_y),
           size = (150,len(data)*8),
         )
    bar_plot.fill_styles.reset()
    plot1 = bar_plot.T(label="max rxerr//s",
                       line_style=None,
                       width=2,
                       hcol=1,
                       cluster=(0,5),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot2 = bar_plot.T(label="max txerr//s",
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       line_style=None,
                       width=2,
                       hcol=2,
                       cluster=(1,5),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot3 = bar_plot.T(label="max coll//s",
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       line_style=None,
                       width=2,
                       hcol=3,
                       cluster=(2,5),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot4 = bar_plot.T(label="max rxdrop//s",
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       width=2,
                       hcol=4,
                       cluster=(3,5),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    plot5 = bar_plot.T(label="max txdrop//s",
                       fill_style=fill_style.Plain(bgcolor=color.darkkhaki),
                       line_style=None,
                       width=2,
                       hcol=5,
                       cluster=(4,5),
                       data=data,
                       data_label_format="",
                       direction='horizontal')
    ar.add_plot(plot1, plot2, plot3, plot4, plot5)
    ar.draw(can)
    can.close()

    return DIV(IMG(_src=action1))

@auth.requires_login()
def perf_stats_cpu(node, s, e):
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
    def format(x):
        return SPAN(x)
    return SPAN(map(format, t))

def __stats_bar_width(rows):
    width = 120//len(rows)
    if width == 0:
        return 1
    return width

@auth.requires_login()
def perf_stats_cpu_one(node, s, e, cpu):
    q = db.stats_cpu.nodename == node
    q &= db.stats_cpu.date > s
    q &= db.stats_cpu.date < e
    q &= db.stats_cpu.cpu == cpu
    rows = db(q).select(orderby=db.stats_cpu.date)
    if len(rows) == 0:
        return SPAN()

    w = __stats_bar_width(rows)

    from time import mktime

    start_date = tic_start_ts(rows)

    def format_x(ts):
        d = datetime.datetime.fromtimestamp(ts+start_date)
        return "/a50/5{}" + d.strftime("%y-%m-%d %H:%M")

    def format_y(x):
        return "/6{}" + str(x)

    def format2_y(x):
        return "/a50/6{}" + str(x)

    import random
    rand = int(random.random()*1000000)
    action = URL(r=request,c='static',f='stats_cpu_'+str(rand)+'.png')
    path = 'applications'+str(action)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    data = [(mktime(row.date.timetuple())-start_date,
             row.usr,
             row.nice,
             row.sys,
             row.iowait,
             row.steal,
             row.irq,
             row.soft,
             row.guest,
             row.idle) for row in rows]

    ar = area.T(
           #x_coord = category_coord.T(data, 0),
           x_coord = linear_coord.T(),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'cpu '+cpu,
                      format=format_x,
                      tic_interval=tic_interval_from_ts,
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           x_range = (None, mktime(rows[-1].date.timetuple())-start_date)
         )
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="usr",
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       hcol=1,
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot2 = bar_plot.T(label="nice",
                       hcol=2,
                       stack_on=plot1,
                       fill_style=fill_style.Plain(bgcolor=color.darkkhaki),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot3 = bar_plot.T(label="sys",
                       hcol=3,
                       stack_on=plot2,
                       fill_style=fill_style.black,
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot4 = bar_plot.T(label="iowait",
                       hcol=4,
                       stack_on=plot3,
                       fill_style=fill_style.Plain(bgcolor=color.thistle3),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot5 = bar_plot.T(label="steal",
                       hcol=5,
                       stack_on=plot4,
                       fill_style=fill_style.Plain(bgcolor=color.coral),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot6 = bar_plot.T(label="irq",
                       hcol=6,
                       stack_on=plot5,
                       fill_style=fill_style.Plain(bgcolor=color.darkolivegreen1),
                       line_style=None,
                       data = data,
                       data_label_format="",
                       width=w,
                       direction='vertical')
    plot7 = bar_plot.T(label="soft",
                       hcol=7,
                       stack_on=plot6,
                       fill_style=fill_style.Plain(bgcolor=color.navajowhite2),
                       line_style=None,
                       data = data,
                       width=w,
                       data_label_format="",
                       direction='vertical')
    plot8 = bar_plot.T(label="guest",
                       hcol=8,
                       stack_on=plot7,
                       fill_style=fill_style.Plain(bgcolor=color.plum3),
                       line_style=None,
                       data = data,
                       width=w,
                       data_label_format="",
                       direction='vertical')
    ar.add_plot(plot1, plot2, plot3, plot4, plot5, plot6, plot7, plot8)
    ar.draw(can)
    can.close()

    return DIV(IMG(_src=action))

@auth.requires_login()
def perf_stats_mem_u_trend_data(node, s, e, p):
    sql = """select cast(avg(kbmemfree+kbcached) as unsigned),
                    cast(std(kbmemfree+kbcached) as unsigned)
             from stats_mem_u
             where nodename="%(node)s"
               and date>date_sub("%(s)s", interval %(p)s)
               and date<date_sub("%(e)s", interval %(p)s)
          """%dict(s=s,e=e,node=node,p=p)
    rows = db.executesql(sql)
    if len(rows) != 1:
        return [(p, 0, 0)]
    r = rows[0]
    if r[0] is None or r[1] is None:
        return [(p, 0, 0)]
    return [(p, r[0], r[1])]

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
def perf_stats_mem_u_trend(node, s, e):
    data = []
    start = str_to_date(s)
    end = str_to_date(e)
    period = end - start
    for p in period_to_range(period):
        data += perf_stats_mem_u_trend_data(node, s, e, p)

    if len(data) == 0:
        return SPAN()

    def format_x(x):
        return "/a50/5{}" + str(x)

    def format_y(x):
        return "/6{}" + str(x)

    import random
    rand = int(random.random()*1000000)
    action = URL(r=request,c='static',f='stats_mem_u_trend_'+str(rand)+'.png')
    path = 'applications'+str(action)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = category_coord.T(data, 0),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'period over period available memory (KB)',
                      format=format_x,
                    ),
           y_axis = axis.Y(label = "", format=format_y),
           #y_range = (0, None),
         )
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="avg avail mem (KB)",
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       hcol=1,
                       line_style=None,
                       data = data,
                       data_label_format="",
                       #width=1,
                       direction='vertical')
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()

    return IMG(_src=action)

@auth.requires_login()
def perf_stats_cpu_trend_data(node, s, e, p):
    sql = """select 100-avg(idle),std(idle)
             from stats_cpu
             where cpu="all"
               and nodename="%(node)s"
               and date>date_sub("%(s)s", interval %(p)s)
               and date<date_sub("%(e)s", interval %(p)s)
          """%dict(s=s,e=e,node=node,p=p)
    rows = db.executesql(sql)
    if len(rows) != 1:
        return [(p, 0, 0)]
    r = rows[0]
    if r[0] is None or r[1] is None:
        return [(p, 0, 0)]
    return [(p, r[0], r[1])]

@auth.requires_login()
def perf_stats_cpu_trend(node, s, e):
    data = []
    start = str_to_date(s)
    end = str_to_date(e)
    period = end - start

    for p in period_to_range(period):
        data += perf_stats_cpu_trend_data(node, s, e, p)

    if len(data) == 0:
        return SPAN()

    def format_x(x):
        return "/a50/5{}" + str(x)

    def format_y(x):
        return "/6{}" + str(x)

    import random
    rand = int(random.random()*1000000)
    action = URL(r=request,c='static',f='stats_cpu_trend_'+str(rand)+'.png')
    path = 'applications'+str(action)
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(
           x_coord = category_coord.T(data, 0),
           y_coord = linear_coord.T(),
           x_axis = axis.X(
                      label = 'period over period cpu usage (%)',
                      format=format_x,
                    ),
           y_axis = axis.Y(label = "", format=format_y, tic_interval=10),
           y_range = (0, 100),
           y_grid_interval = 10,
         )
    bar_plot.fill_styles.reset();
    plot1 = bar_plot.T(label="avg cpu usage (%)",
                       fill_style=fill_style.Plain(bgcolor=color.salmon),
                       hcol=1,
                       line_style=None,
                       data = data,
                       data_label_format="",
                       #width=1,
                       error_bar = error_bar.bar2, error_minus_col=2,
                       direction='vertical')
    ar.add_plot(plot1)
    ar.draw(can)
    can.close()

    return IMG(_src=action)

@auth.requires_login()
def perf_stats_trends(node, begin, end):
    return DIV(
              perf_stats_cpu_trend(node, begin, end),
              perf_stats_mem_u_trend(node, begin, end),
           )

@auth.requires_login()
def _ajax_perf_stats(f):
     node = None
     begin = None
     end = None
     for k in request.vars:
         if 'node_' in k:
             node = request.vars[k]
         elif 'begin_' in k:
             begin = request.vars[k]
         elif 'end_' in k:
             end = request.vars[k]
     if node is None or begin is None or end is None:
         return SPAN()
     return f(node, begin, end)

def ajax_perf_stats_trends():
    return _ajax_perf_stats(perf_stats_trends)

def ajax_perf_stats_cpu():
    return _ajax_perf_stats(perf_stats_cpu)

def ajax_perf_stats_mem_u():
    return _ajax_perf_stats(perf_stats_mem_u)

def ajax_perf_stats_swap():
    return _ajax_perf_stats(perf_stats_swap)

def ajax_perf_stats_proc():
    return _ajax_perf_stats(perf_stats_proc)

def ajax_perf_stats_netdev():
    return _ajax_perf_stats(perf_stats_netdev)

def ajax_perf_stats_netdev_err():
    return _ajax_perf_stats(perf_stats_netdev_err)

def ajax_perf_stats_block():
    return _ajax_perf_stats(perf_stats_block)

def ajax_perf_stats_blockdev():
    return _ajax_perf_stats(perf_stats_blockdev)


