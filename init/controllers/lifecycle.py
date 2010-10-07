from pychart import *

def __get_lifecycle_os():
    rows = db(db.lifecycle_os.id>0).select(orderby=db.lifecycle_os.lc_os_name,
                                           groupby=db.lifecycle_os.lc_os_name)
    os = []
    for r in rows:
        if r.lc_os_name == "":
            continue
        os += [r.lc_os_name]
    return os

@auth.requires_login()
def lifecycle_os():
    os = __get_lifecycle_os()
    return dict(os=os)

def stats_lifecycle_os():
    __stats_lifecycle_os_name()
    for o in __get_lifecycle_os():
        __stats_lifecycle_os_release(o)

def __stats_lifecycle_os_name():
    from time import mktime
    import datetime

    today = datetime.datetime.today().toordinal()

    rows = db(db.v_lifecycle_os_name.id>0).select(orderby=db.v_lifecycle_os_name.lc_date)
    if len(rows) == 0:
        return

    h = {}
    os = set()
    data = []
    for r in rows:
        o = r.lc_os_name
        os |= set([o])
        day = r.lc_date.toordinal()
        if day not in h:
            h[day] = {}
        h[day][o] = int(r.lc_count)
    for day in h:
        e = [day]
        for o in os:
            if o not in h[day]:
                e += [0]
            else:
                e += [h[day][o]]
        data += [tuple(e)]

    action = str(URL(r=request,c='static',f='stat_lifecycle_os_name.png'))
    path = 'applications'+action
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(legend = legend.T(loc=(0,-30-10*len(os))),
                x_coord = linear_coord.T(),
                y_coord = linear_coord.T(),
                x_axis = axis.X(label="", format=format_x,
                                tic_interval=tic_interval_from_ord),
                x_range = (None, today),
                y_range = (0, None),
                y_axis = axis.Y(label="", format=format_y))
    bar_plot.fill_styles.reset();

    colors = [color.darkolivegreen1,
              color.gray10,
              color.salmon,
              color.gray30,
              color.darkkhaki,
              color.gray50,
              color.sienna1,
              color.gray70,
              color.lightgreen,
              color.gray90,
              color.thistle3,
              color.coral]

    w = 120/len(data)
    if w < 1: w = 1

    plot = []
    for i, o in enumerate(os):
        if i == 0:
            stackon = None
        else:
            stackon = plot[i-1]

        plot += [bar_plot.T(label=o,
                            hcol=i+1,
                            fill_style=fill_style.Plain(bgcolor=colors[i%len(colors)]),
                            stack_on=stackon,
                            line_style=None,
                            width = w,
                            data = data,
                            data_label_format="",
                            direction='vertical')]
        ar.add_plot(plot[i])

    ar.draw(can)
    can.close()

def __stats_lifecycle_os_release(os_name=None):
    if os_name is None or os_name == "":
        return

    from time import mktime
    import datetime

    today = datetime.datetime.today().toordinal()

    rows = db(db.lifecycle_os.lc_os_name==os_name).select(orderby=db.lifecycle_os.lc_date)
    if len(rows) == 0:
        return

    h = {}
    os = set()
    data = []
    for r in rows:
        o = r.lc_os_concat.replace('/', '//')
        os |= set([o])
        day = r.lc_date.toordinal()
        if day not in h:
            h[day] = {}
        h[day][o] = r.lc_count
    for day in h:
        e = [day]
        for o in os:
            if o not in h[day]:
                e += [0]
            else:
                e += [h[day][o]]
        data += [tuple(e)]

    action = str(URL(r=request,c='static',f='stat_lifecycle_'+os_name+'.png'))
    path = 'applications'+action
    can = canvas.init(path)
    theme.use_color = True
    theme.scale_factor = 2
    theme.reinitialize()

    ar = area.T(legend = legend.T(loc=(0,-30-10*len(os))),
                x_coord = linear_coord.T(),
                y_coord = linear_coord.T(),
                x_axis = axis.X(label="", format=format_x,
                                tic_interval=tic_interval_from_ord),
                x_range = (None, today),
                y_range = (0, None),
                y_axis = axis.Y(label="", format=format_y))
    bar_plot.fill_styles.reset();

    colors = [color.darkolivegreen1,
              color.gray10,
              color.salmon,
              color.gray30,
              color.darkkhaki,
              color.gray50,
              color.sienna1,
              color.gray70,
              color.lightgreen,
              color.gray90,
              color.thistle3,
              color.coral]

    w = 120/len(data)
    if w < 1: w = 1

    plot = []
    for i, o in enumerate(os):
        if i == 0:
            stackon = None
        else:
            stackon = plot[i-1]

        plot += [bar_plot.T(label=o,
                            hcol=i+1,
                            fill_style=fill_style.Plain(bgcolor=colors[i%len(colors)]),
                            stack_on=stackon,
                            line_style=None,
                            width = w,
                            data = data,
                            data_label_format="",
                            direction='vertical')]
        ar.add_plot(plot[i])

    ar.draw(can)
    can.close()


