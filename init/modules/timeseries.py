from __future__ import print_function
import os
import whisper
import datetime
import time
import fnmatch
from collections import OrderedDict

default_retentions = [
    whisper.parseRetentionDef("1m:30m"),
    whisper.parseRetentionDef("10m:3d"),
    whisper.parseRetentionDef("1h:90d"),
    whisper.parseRetentionDef("1d:3y"),
]
daily_retentions = ["1d:5y"]
formats = [
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d %H",
    "%Y-%m-%d",
]
time_format = "%Y-%m-%d %H:%M:%S"

here_d = os.path.dirname(__file__)
store_d = os.path.join(here_d, "..", "uploads", "stats")
temp_d = os.path.join(store_d, "temp")

def wsp_delete(*args):
    if '..' in args:
        print("'..' is not allowed in wsp_delete args")
        return 1
    args = [store_d] + list(args)
    cmd = "rm -rf " + os.path.join(*args)
    if len(args) < 3:
        print("cowardy refuse to %s: min depth 2 under %s" % (cmd, store_d))
        return 1
    print(cmd)
    os.system(cmd)

def wsp_find(*args):
    args = [store_d] + [str(arg) for arg in args]
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
    args = [store_d] + [str(arg) for arg in args]
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
    if len(args) > 0 and not str(args[0]).startswith(store_d):
        _args = [store_d]
    else:
        _args = []
    for arg in args:
        _args += str(arg).strip("\0").split(os.sep)
    fpath = os.path.join(*_args)
    if not fpath.endswith(".wsp"):
        fpath += ".wsp"
    return fpath

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
    if s is None:
        return time.time()
    if isinstance(s, datetime.datetime):
        return int(time.mktime(s.timetuple()))
    if isinstance(s, datetime.date):
        return int(time.mktime(s.timetuple()))
    if isinstance(s, int):
        return s
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
        return 0, 0, 0
    return total/count, _min, _max

def whisper_xfetch(paths, **kwargs):
    """
    args: a list of paths [["nodes", "aa", "cpu"], ...]
    kwargs:

    * b: begin
    * e: end
    * agg: average|sum|max|min
    """
    if not paths:
        return []
    _data = whisper_fetch(*paths[0], **kwargs)
    count = len(paths)
    if count == 1:
        return _data
    agg = kwargs.get("agg", "sum")

    def sum(x, y):
        if x is None and y is None:
            return
        if x is None:
            return y
        if y is None:
            return x
        return x + y

    def min(x, y):
        if x is None and y is None:
            return
        if x is None:
            return y
        if y is None:
            return x
        return x if x < y else y

    def max(x, y):
        if x is None and y is None:
            return
        if x is None:
            return y
        if y is None:
            return x
        return x if x > y else y

    average = sum
    fn = locals()[agg]
    data = OrderedDict()
    counts = dict()
    for path in paths:
        _data = whisper_fetch(*path, **kwargs)
        for ts, val in _data:
            cur = data.get(ts)
            if cur is None:
                data[ts] = val
                counts[ts] = 1 if val is not None else 0
            elif val is None:
                pass
            else:
                data[ts] = fn(cur, val)
                counts[ts] += 1
    if agg == "average":
        for ts, val in data.items():
            if data[ts] and counts.get(ts):
                data[ts] /= counts[ts]
    return [[ts, val] for ts, val in data.items()]

def whisper_fetch(*args, **kwargs):
    b = kwargs.get("b")
    e = kwargs.get("e")
    wsp = wsp_path(*args)
    _args = [wsp]
    if not os.path.exists(wsp):
        return []
    if b is None:
        b = 0
    if not isinstance(b, (int, float)):
        b = to_tstamp(b)
    _args.append(b)
    if e is not None:
        if not isinstance(e, (int, float)):
            e = to_tstamp(e)
        _args.append(e)
    (start, end, step), values = whisper.fetch(*_args)
    t = start
    data = []
    for value in values:
        timestr = time.strftime(time_format, time.localtime(t))
        t += step
        data.append([timestr, value])
    return data

def whisper_update(wsp, value, tstamp=None, retentions=None):
    whisper_create(wsp, retentions=retentions)
    whisper.update(wsp, value, to_tstamp(tstamp))

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
        #print("insert %d values in %s" % (len(datapoints), wsp))
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
    node_id = "a3d3634b-51d1-4ce7-a844-6daa6cc49280"
    print(sub_find("nodes/%s" % node_id, "fs_u", prefix="/"))
    print(wsp_find("nodes/%s" % node_id, "cpu"))
    print(sub_find("nodes/%s" % node_id, "cpu"))
    wsp_delete("nodes", "41667c07-9197-408f-9487-08ca540410f0")
    """
    import glob
    paths = [["nodes", os.path.basename(path), "cpu", "all", "idle"] for path in glob.glob(os.path.join(store_d, "nodes", "*"))]
    for ts, val in whisper_xfetch(paths, b=time.time()-72000):
        print("%s %s" % (ts, val))

