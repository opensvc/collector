def str_to_date(s, fmt="%Y-%m-%d %H:%M:%S"):
    if s is None or s == "" or len(fmt) == 0:
        return None
    s = s.strip()
    if "." in s:
        s = s.split(".")[0]
    if s[0] in ["<", ">"]:
        s = s[1:]
    if re.match("[-+]{0,1}[0-9]+[ywdhms]{1}", s):
        # past/future
        if s[0] == "-":
            past = True
            s = s[1:]
        elif s[0] == "+":
            past = False
            s = s[1:]
        else:
            past = False

        p = s[-1]
        n = int(s[:-1])

        # timedelta
        days = 0
        hours = 0
        hours = 0
        minutes = 0
        seconds = 0
        if p == "y":
            days = 365 * n
        elif p == "w":
            days = 7 * n
        elif p == "d":
            days = n
        elif p == "h":
            hours = n
        elif p == "m":
            minutes = n
        elif p == "s":
            seconds = n
        else:
            raise Exception("unknown time delta suffix %s" % p)
        delta = datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

        if past:
            return datetime.datetime.now() - delta
        else:
            return datetime.datetime.now() + delta
    try:
        return datetime.datetime.strptime(s, fmt)
    except:
        return str_to_date(s, fmt[0:-1])

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

def get_period(s, e):
    year = datetime.timedelta(days=365)
    month = datetime.timedelta(days=30)
    day = datetime.timedelta(days=1)
    hour = datetime.timedelta(hours=1)
    if isinstance(s, str):
        s = str_to_date(s)
    if isinstance(e, str):
        e = str_to_date(e)
    period = e - s

    #if period >= 20 * year:
    #    d = "_year"
    #if period >= 3 * year:
    #    d = "_month"
    if period >= 3 * month:
        d = "_day"
    elif period >= 2 * day:
        d = "_hour"
    else:
        d = ""
    return d

def period_sql(period, field='date'):
    if period == "year":
        d = "YEAR(%(f)s)"%dict(f=field)
    elif period == "month":
        d = "concat(YEAR(%(f)s), '-', MONTH(%(f)s))"%dict(f=field)
    elif period == "week":
        d = "concat(YEAR(%(f)s), '-', WEEK(%(f)s))"%dict(f=field)
    elif period == "day":
        d = "concat(YEAR(%(f)s), '-', MONTH(%(f)s), '-', DAY(%(f)s))"%dict(f=field)
    elif period == "hour":
        d = "concat(YEAR(%(f)s), '-', MONTH(%(f)s), '-', DAY(%(f)s), ' ', HOUR(%(f)s), ':00:00')"%dict(f=field)
    else:
        d = field
    return d

def period_concat(s, e, field='date'):
    year = datetime.timedelta(days=365)
    month = datetime.timedelta(days=30)
    day = datetime.timedelta(days=1)
    hour = datetime.timedelta(hours=1)
    if isinstance(s, str):
        s = str_to_date(s)
    if isinstance(e, str):
        e = str_to_date(e)
    period = e - s

    if period >= 20 * year:
        d = "YEAR(%(f)s)"%dict(f=field)
    elif period >= 3 * year:
        d = "concat(YEAR(%(f)s), '-', MONTH(%(f)s))"%dict(f=field)
    elif period >= 6 * month:
        d = "concat(YEAR(%(f)s), '-', WEEK(%(f)s))"%dict(f=field)
    elif period >= month:
        d = "concat(YEAR(%(f)s), '-', MONTH(%(f)s), '-', DAY(%(f)s))"%dict(f=field)
    elif period >= 2 * day:
        d = "concat(YEAR(%(f)s), '-', MONTH(%(f)s), '-', DAY(%(f)s), ' ', HOUR(%(f)s), ':00:00')"%dict(f=field)
    else:
        d = field
    return d

