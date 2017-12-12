from __future__ import print_function
import os
import whisper
import datetime
import time
import fnmatch

default_retentions = [
    whisper.parseRetentionDef("1m:30m"),
    whisper.parseRetentionDef("10m:3d"),
    whisper.parseRetentionDef("1h:90d"),
    whisper.parseRetentionDef("1d:3y"),
]
formats = [
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d %H",
    "%Y-%m-%d",
]
time_format = "%Y-%m-%d %H:%M:%S"

here_d = os.path.dirname(__file__)
store_d = os.path.join(here_d, '..', "uploads", "stats")

def wsp_find(*args):
    args = [store_d] + list(args)
    head = os.path.join(*args)
    return recurse_wsp_find(head)

def recurse_wsp_find(head):
    matches = []
    for root, dirnames, filenames in os.walk(head):
        for filename in fnmatch.filter(filenames, '*.wsp'):
            matches.append(os.path.join(root, filename))
        for dirname in dirnames:
            matches += recurse_wsp_find(dirname)
    return matches

def sub_find(*args, **kwargs):
    prefix = kwargs.get("prefix", "")
    args = [store_d] + list(args)
    head = os.path.join(*args)
    head_len = len(head)
    wsps = recurse_wsp_find(head)
    subs = set()
    for wsp in wsps:
        wsp_d = os.path.dirname(wsp)
        sub = prefix + wsp_d[head_len+1:]
        subs.add(sub)
    return subs

def wsp_path(*args):
    _args = [store_d]
    for arg in args:
        _args += arg.split(os.sep)
    return os.path.join(*_args)+".wsp"

def whisper_create(wsp, retentions=None, xFilesFactor=0.0):
    if os.path.exists(wsp):
        return
    wsp_d = os.path.dirname(wsp)
    if not os.path.exists(wsp_d):
        os.makedirs(wsp_d)
    if retentions is None:
        retentions = default_retentions
    else:
        retentions = map(whisper.parseRetentionDef, retentions)
    print("create %s" % wsp)
    whisper.create(wsp, retentions, xFilesFactor=xFilesFactor)

def to_tstamp(s):
    for fmt in formats:
        try:
            return int(time.mktime(datetime.datetime.strptime(s, fmt).timetuple()))
        except ValueError:
            pass

def whisper_fetch_avg(*args, **kwargs):
    data = whisper_fetch(*args, **kwargs)
    total = 0
    count = 0
    for ts, value in data:
        if value is None:
            continue
        count += 1
        total += value
    if count == 0:
        return 0
    return total/count

def whisper_fetch_avg_min_max(*args, **kwargs):
    data = whisper_fetch(*args, **kwargs)
    total = 0
    count = 0
    _min = None
    _max = None
    for ts, value in data:
        if value is None:
            continue
        if _min is None or value < _min:
            _min = value
        if _max is None or value > _max:
            _max = value
        count += 1
        total += value
    if count == 0:
        return 0
    return total/count, _min, _max

def whisper_fetch(*args, **kwargs):
    b = kwargs.get("b")
    e = kwargs.get("e")
    wsp = wsp_path(*args)
    if not os.path.exists(wsp):
        return []
    if isinstance(b, (str, unicode)):
        b = to_tstamp(b)
    if isinstance(e, (str, unicode)):
        e = to_tstamp(e)
    (start, end, step), values = whisper.fetch(wsp, b, e)
    t = start
    data = []
    for value in values:
        timestr = time.strftime(time_format, time.localtime(t))
        t += step
        data.append([timestr, value])
    return data

def whisper_update_list(head, vars, vals, group="", options=None):
    if options is None:
        options = {}
    if vals == []:
        return
    sub = options.get("sub")
    ndiscard = options.get("discard", [])
    discard = [vars.index(col) for col in ndiscard if col in vars]
    datecol = options.get("datecol", "date")
    if datecol not in vars:
        print("date column %s is not in vars" % datecol)
        return
    datecol = vars.index(datecol)
    if datecol not in discard:
        discard.append(datecol)

    if sub is not None:
        sub = vars.index(sub)
        if sub not in discard:
            discard.append(sub)
        whisper_update_list_sub(head, vars, vals, group=group, discard=discard, datecol=datecol, sub=sub)
    else:
        whisper_update_list_no_sub(head, vars, vals, group=group, discard=discard, datecol=datecol)

def whisper_update_list_sub(head, vars, vals, group="", discard=None, datecol=0, sub=None):
    subs = set()
    for val in vals:
        subs.add(val[sub])
    for _sub in subs:
        try:
            whisper_update_list_no_sub(head, vars, [val for val in vals if val[sub]==_sub], group="%s/%s"%(group, _sub), discard=discard, datecol=datecol)
        except Exception as exc:
            print(exc)

def whisper_update_list_no_sub(head, vars, vals, group="", discard=None, datecol=0):
    for i, metric in enumerate(vars):
        if i in discard:
            continue
        wsp = wsp_path(head, group, metric)
        whisper_create(wsp)
        datapoints = []
        for val in vals:
            tstamp = to_tstamp(val[datecol])
            if tstamp is None:
                print("invalid date in datapoint %s" % val)
                continue
            try:
                _val = float(val[i])
            except ValueError:
                continue
            datapoints.append((tstamp, _val))
        print("insert %d values in %s" % (len(datapoints), wsp))
        whisper.update_many(wsp, datapoints)


if __name__ == "__main__":
    """
    node_id = "test"
    vars = ["date", "m1", "m2"]
    vals = [
        ["2017-01-01", 1, 2],
        ["2017-03-01", 3, 4],
        ["2017-04-01 00:00", 5, 4],
        ["2017-02-01 00:00:01", 3, 4],
    ]
    whisper_update_list(node_id, vars, vals, "g1")

    options = {
        "datecol": "time",
        "discard": ["time", "sub"],
        "sub": "sub",
    }
    node_id = "test"
    vars = ["time", "sub", "m1", "m2"]
    vals = [
        ["2017-01-01", "sub1", 1, 2],
        ["2017-03-01", "sub2", 3, 4],
        ["2017-04-01 00:00", "sub1", 5, 4],
        ["2017-02-01 00:00:01", "sub2", 3, 4],
    ]
    whisper_update_list(node_id, vars, vals, "g2", options=options)

    node_id = "a3d3634b-51d1-4ce7-a844-6daa6cc49280"
    vars = ["date", "nodename", "mntpt", "size", "used"]
    vals = [[u'2017-12-11 18:26:20.949018', u'aubergine', u'/dev', u'8052744', u'0'], [u'2017-12-11 18:16:20.949018', u'aubergine', u'/dev', u'8052744', u'0']]
    group = "fs_u" 
    options = {'discard': ['nodename'], 'sub': 'mntpt', 'datecol': 'date'}
    whisper_update_list("nodes/%s" % node_id, vars, vals, group, options=options)

#    whisper_fetch("nodes/%s" % node_id, "cpu", "all", "idle", b="2017-12-09 13:41", e="2017-12-10 13:41")
    whisper_create("/tmp/foo1")
    whisper_create("/tmp/fooo", ["1d:3y"], 0.5)
    """
    node_id = "a3d3634b-51d1-4ce7-a844-6daa6cc49280"
    print(sub_find("nodes/%s" % node_id, "fs_u", prefix="/"))
    print(wsp_find("nodes/%s" % node_id, "cpu"))
    print(sub_find("nodes/%s" % node_id, "cpu"))
