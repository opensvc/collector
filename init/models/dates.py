def str_to_date(s, fmt="%Y-%m-%d %H:%M:%S"): 
    if s is None or s == "" or len(fmt) == 0:
        return None
    s = s.strip()
    if s[0] in ["<", ">"]:
        s = s[1:]
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

