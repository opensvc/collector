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


