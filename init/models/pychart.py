def format_x(ordinal):
    d = datetime.date.fromordinal(int(ordinal))
    return "/a50/6{}" + d.strftime("%y-%m-%d")

def format_y(x):
    return "/6{}" + str(x)

def format2_y(x):
    return "/a50/6{}" + str(x)

def tic_interval_from_ts(_min, _max):
    """ choose an interval to display a minimum of 5 marks on the axis
    """
    p = _max - _min
    r = []
    intervals = [2419200, 1209600, 604800, 86400, 21600, 7200, 3600, 1800, 600]
    for i in intervals:
        if p / i >= 6:
            break
    return range(_min, _max, i)

def tic_interval_from_ord(_min, _max):
    """ choose interval to display a minimum of 5 marks on the axis
    """
    p = _max - _min
    r = []
    intervals = [720, 360, 30, 14, 7, 2, 1]
    for i in intervals:
        if p / i >= 6:
            break
    return range(_min, _max, i)

def tic_interval_from_rows(rows):
    _min = rows[0].day.toordinal()
    _max = rows[-1].day.toordinal()
    p = _max - _min
    r = []
    i = p // 10
    if i == 0:
        i = 1
    return i

def tic_start_ts(rows):
    from time import mktime
    start_date = mktime(rows[0].date.timetuple())
    end_date = mktime(rows[-1].date.timetuple())
    p = end_date - start_date
    if p < 86400:
        """ align start to closest preceding hour
        """
        start_date = ((start_date // 3600) + 1) * 3600
    else:
        """ align start to closest preceding day
        """
        start_date = ((start_date // 86400) + 1) * 86400
    return start_date

