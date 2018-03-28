def convert_duration(s, _to="s", _from="s"):
    """
    Convert a string representation of a duration to seconds.
    Supported units (case insensitive):
      w: week
      d: day
      h: hour
      m: minute
      s: second
    Example:
      1w => 604800
      1d => 86400
      1h => 3600
      1h1m => 3660
      1h2s => 3602
      1 => 1
    """
    if s is None:
        raise ValueError("convert duration error: None is not a valid duration")

    units = {
        "w": 604800,
        "d": 86400,
        "h": 3600,
        "m": 60,
        "s": 1,
    }

    if _from not in units:
        raise ValueError("convert duration error: unsupported input unit %s" % _from)
    if _to not in units:
        raise ValueError("convert duration error: unsupported target unit %s" % _to)

    try:
        s = int(s)
        return s * units[_from] // units[_to]
    except ValueError:
        pass

    s = s.lower()
    duration = 0
    prev = 0
    for idx, unit in enumerate(s):
        if unit not in units:
            continue
        _duration = s[prev:idx]
        try:
            _duration = int(_duration)
        except ValueError:
            raise ValueError("convert duration error: invalid format %s at index %d" % (s, idx))
        duration += _duration * units[unit]
        prev = idx + 1

    return duration // units[_to]


