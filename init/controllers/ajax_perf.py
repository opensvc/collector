def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget(response)
    return service()


def stats_fetch(nodes, relpath, **kwargs):
    if "," in nodes:
        nodes = nodes.split(",")
    elif not isinstance(nodes, list):
        nodes = [nodes]
    paths = []
    for node in nodes:
        paths.append(["nodes", node] + relpath)
    return timeseries.whisper_xfetch(paths, **kwargs)

@auth.requires_login()
def perf_stats_svc_cpu(node, b, e):
    container = request.vars.container
    if container == "None":
        return perf_stats_svc_data(node, b, e, 'cpu')
    else:
        return perf_stats_svc_data_cpu_normalize(node, b, e)

@auth.requires_login()
def perf_stats_svc_mem(node, b, e):
    container = request.vars.container
    if container == "None":
        return perf_stats_svc_data(node, b, e, 'mem')
    else:
        return perf_stats_svc_data_mem_normalize(node, b, e)

@auth.requires_login()
def perf_stats_svc_pg(node, b, e):
    return perf_stats_svc_data(node, b, e, 'pg')

@auth.requires_login()
def perf_stats_svc_avgpg(node, b, e):
    return perf_stats_svc_data(node, b, e, 'avgpg')

@auth.requires_login()
def perf_stats_svc_at(node, b, e):
    return perf_stats_svc_data(node, b, e, 'at')

@auth.requires_login()
def perf_stats_svc_avgat(node, b, e):
    return perf_stats_svc_data(node, b, e, 'avgat')

@auth.requires_login()
def perf_stats_svc_rss(node, b, e):
    return perf_stats_svc_data(node, b, e, 'rss')

@auth.requires_login()
def perf_stats_svc_swap(node, b, e):
    return perf_stats_svc_data(node, b, e, 'swap')

@auth.requires_login()
def perf_stats_svc_nproc(node, b, e):
    return perf_stats_svc_data(node, b, e, 'nproc')

@auth.requires_login()
def perf_stats_svc_cap(node, b, e):
    return perf_stats_svc_data(node, b, e, 'cap')

@auth.requires_login()
def perf_stats_svc_cap_cpu(node, b, e):
    return perf_stats_svc_data(node, b, e, 'cap_cpu')

@auth.requires_login()
def perf_stats_svc_data_mem_normalize(node, b, e):
    if "," in node:
        return
    container = request.vars.container
    sql = """select mem_bytes from nodes
             where
               node_id="%(node)s"
          """%dict(node=node)
    mem = db.executesql(sql)[0][0]

    data = {}
    svc_id = node_svc_id(node, container)
    data = timeseries.whisper_fetch("nodes", node, "svc", svc_id, "mem", b=b, e=e)
    if len(data) == 0:
        return [], [], 0, 0
    cap = timeseries.whisper_fetch("nodes", node, "svc", svc_id, "cap", b=b, e=e)
    if len(cap) == 0:
        return [], [], 0, 0

    # normalize
    for i, d in enumerate(data):
        d[i][1] = d[i][1] / cap[i][1] * mem - d[i][1]

    _min = data[0][0]
    _max = data[-1][0]
    dates = [r[0] for r in data]

    if dates is None:
        return [], [], 0, 0

    return [svc_id], [data], _min, _max

@auth.requires_login()
def perf_stats_svc_data_cpu_normalize(node, b, e):
    if "," in node:
        return
    container = request.vars.container
    col = 'cpu'

    sql = """select if(cpu_threads is null, cpu_cores, cpu_threads)
             from nodes
             where node_id="%(node)s"
          """%dict(node=node)
    cpus = db.executesql(sql)[0][0]

    data = {}
    svc_id = node_svc_id(node, container)
    data = timeseries.whisper_fetch("nodes", node, "svc", svc_id, "cpu", b=b, e=e)
    if len(data) == 0:
        return [], [], 0, 0
    cap = timeseries.whisper_fetch("nodes", node, "svc", svc_id, "cap_cpu", b=b, e=e)
    if len(cap) == 0:
        return [], [], 0, 0

    # normalize
    for i, d in enumerate(data):
        d[i][1] = d[i][1] / cap[i][1] * cpus - d[i][1]

    _min = data[0][0]
    _max = data[-1][0]
    dates = [r[0] for r in data]

    if dates is None:
        return [], [], 0, 0

    return [svc_id], [data], _min, _max

@auth.requires_login()
def perf_stats_svc_data(node, b, e, col):
    container = request.vars.container
    data = {}
    dates = None
    if container == "None":
        svc_ids = timeseries.sub_find("nodes", node, "svc")
    else:
        svc_ids = [node_svc_id(node, container)]
    for svc_id in svc_ids:
        data[svc_id] = timeseries.whisper_fetch("nodes", node, "svc", svc_id, col, b=b, e=e)
        if len(data[svc_id]) == 0:
            return [], [], 0, 0
        if dates is None:
            _min = data[svc_id][0][0]
            _max = data[svc_id][-1][0]
            dates = [r[0] for r in data[svc_id]]

    if dates is None:
        return [], [], 0, 0

    return svc_ids, [data[svc_id] for svc_id in svc_ids], _min, _max

def ajax_perf_svc_plot_short():
    return SPAN(
             _ajax_perf_plot('svc_cpu', base='svc'),
             _ajax_perf_plot('svc_cap_cpu', base='svc'),
             _ajax_perf_plot('svc_mem', base='svc'),
             _ajax_perf_plot('svc_cap', base='svc'),
             _ajax_perf_plot('svc_swap', base='svc'),
             _ajax_perf_plot('svc_rss', base='svc'),
             _ajax_perf_plot('svc_nproc', base='svc', last=True),
           )

@auth.requires_login()
def _ajax_perf_plot(group, sub=[''], last=False, base=None, container=None):
    session.forget(response)
    if base is None:
        base = group
    node = request.args[0]
    rowid = request.args[1]
    begin = datetime.datetime.now() - datetime.timedelta(days=1)
    end = datetime.datetime.now()
    try:
        container = request.args[2]
    except:
        container = None

    for k in request.vars:
        if 'begin_' in k:
            begin = request.vars[k]
        elif 'end_' in k:
            end = request.vars[k]
    if node is None:
        return SPAN()

    plots = []
    plots.append("stats_%(group)s('%(url)s', 'perf_%(group)s_%(rowid)s');"%dict(
      url=URL(r=request,
              f='call/json/json_%s'%group,
              vars={'node':node, 'b':begin, 'e':end, 'container':container}
          ),
      rowid=rowid,
      group=group,
    ))

    if last:
        spacer = DIV(
                   XML('&nbsp;'),
                   _class='spacer',
                 ),
    else:
        spacer = ''
    l = []
    for s in sub:
        l.append(DIV(
                  DIV(_id='perf_%s_%s%s'%(group,rowid,s)),
                  _class='float perf_plot',
                 ))
    l.append(SPAN(spacer))
    l.append(SCRIPT(
               plots,
               _name="prf_cont_%s_%s_to_eval"%(base,rowid)
             ))
    return SPAN(*l)


from applications.init.modules import timeseries
import whisper


#
# json servers
#
###############

@service.json
def json_svc_cpu():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_cpu(node, b, e)

@service.json
def json_svc_mem():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_mem(node, b, e)

@service.json
def json_svc_at():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_at(node, b, e)

@service.json
def json_svc_avgat():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_avgat(node, b, e)

@service.json
def json_svc_pg():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_pg(node, b, e)

@service.json
def json_svc_avgpg():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_avgpg(node, b, e)

@service.json
def json_svc_rss():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_rss(node, b, e)

@service.json
def json_svc_swap():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_swap(node, b, e)

@service.json
def json_svc_cap_cpu():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_cap_cpu(node, b, e)

@service.json
def json_svc_cap():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_cap(node, b, e)

@service.json
def json_svc_nproc():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e
    return perf_stats_svc_nproc(node, b, e)

def get_max_interval(b, e):
    period = get_period(b, e)
    if period == '':
        return 11
    elif period == '_hour':
        return 61
    elif period == '_day':
        return 1441
    else:
        return 10081

def add_hole(this_date, prev_date, max_interval, data):
    if prev_date is None:
        return data
    td = this_date - prev_date
    interval = td.days*1440 + td.seconds//60
    if interval > max_interval:
        t0 = prev_date + datetime.timedelta(seconds=1)
        t1 = this_date - datetime.timedelta(seconds=1)
        for i, l in enumerate(data):
            for t in (t0, t1):
                data[i].append((t, None))
    return data

@service.json
def json_cpu():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e

    metrics = [
        "usr",
        "nice",
        "sys",
        "iowait",
        "steal",
        "irq",
        "soft",
        "guest",
        "idle",
    ]
    data = {}
    for metric in metrics:
        if node is None:
            return {}
        _data = stats_fetch(node, ["cpu", "all", metric], b=b, e=e)
        if len(_data) > 0:
            data[metric] = _data
    return data

@service.json
def json_mem():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e

    metrics = [
        "kbmemfree",
        "kbmemused",
        "pct_memused",
        "kbbuffers",
        "kbcached",
        "kbcommit",
        "pct_commit",
        "kbmemsys",
        "kbactive",
        "kbinact",
        "kbdirty",
    ]

    data = {}
    for metric in metrics:
        if node is None:
            return {}
        _data = stats_fetch(node, ["mem_u", metric], b=b, e=e)
        if len(_data) > 0:
            data[metric] = _data
    return data

@service.json
def json_swap():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e

    metrics = [
        "kbswpfree",
        "kbswpused",
        "pct_swpused",
        "kbswpcad",
        "pct_swpcad",
    ]

    data = {}
    for metric in metrics:
        if node is None:
            return {}
        _data = stats_fetch(node, ["swap", metric], b=b, e=e)
        if len(_data) > 0:
            data[metric] = _data
    return data

@service.json
def json_proc():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e

    metrics = [
        "runq_sz",
        "plist_sz",
        "ldavg_1",
        "ldavg_5",
        "ldavg_15",
    ]

    data = {}
    for metric in metrics:
        if node is None:
            return {}
        _data = stats_fetch(node, ["proc", metric], b=b, e=e)
        if len(_data) > 0:
            data[metric] = _data
    return data

@service.json
def json_block():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e

    metrics = [
        "rtps",
        "wtps",
        "rbps",
        "wbps",
    ]

    data = {}
    for metric in metrics:
        if node is None:
            return {}
        _data = stats_fetch(node, ["block", metric], b=b, e=e)
        if len(_data) > 0:
            data[metric] = _data
    return data

@service.json
def json_netdev_err():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e

    devs = timeseries.sub_find("nodes", node, "netdev_err")
    metrics = [
        ("rxerrps",  "err",  " rx", -1),
        ("txerrps",  "err",  " tx",  1),
        ("collps",   "coll", "",     1),
        ("rxdropps", "drop", " rx", -1),
        ("txdropps", "drop", " tx",  1),
    ]

    if node is None:
        return [rxerrps, txerrps, collps, rxdropps, txdropps]

    data = {
        "err": {},
        "coll": {},
        "drop": {},
    }
    for dev in devs:
        for metric, cat, suffix, multiplier in metrics:
            ts = timeseries.whisper_fetch("nodes", node, "netdev_err", dev, metric, b=b, e=e)
            label = dev + suffix
            if label not in data[cat]:
                data[cat][label] = []
            for date, value in ts:
                data[cat][label].append([date, value * multiplier if value is not None else None])

    errps_labels = sorted(data["err"].keys())
    errps_data = []
    for k in errps_labels:
        errps_data.append(data["err"][k])
    collps_labels = sorted(data["coll"].keys())
    collps_data = []
    for k in collps_labels:
        collps_data.append(data["coll"][k])
    dropps_labels = sorted(data["drop"].keys())
    dropps_data = []
    for k in dropps_labels:
        dropps_data.append(data["drop"][k])
    return [[errps_labels, errps_data],
            [collps_labels, collps_data],
            [dropps_labels, dropps_data]]

@service.json
def json_netdev():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e

    devs = timeseries.sub_find("nodes", node, "netdev")
    metrics = [
        ("rxkBps",   "bw", " rx", -1),
        ("txkBps",   "bw", " tx", 1),
        ("rxpckps",  "pk", " rx", -1),
        ("txpckps",  "pk", " tx", 1),
    ]
    if node is None:
        return []

    data = {
        "bw": {},
        "pk": {},
    }
    for dev in devs:
        for metric, cat, suffix, multiplier in metrics:
            ts = timeseries.whisper_fetch("nodes", node, "netdev", dev, metric, b=b, e=e)
            label = dev + suffix
            if label not in data[cat]:
                data[cat][label] = []
            for date, value in ts:
                data[cat][label].append([date, value * multiplier if value is not None else None])

    bw_labels = sorted(data["bw"].keys())
    bw_data = []
    for k in bw_labels:
        bw_data.append(data["bw"][k])
    pk_labels = sorted(data["pk"].keys())
    pk_data = []
    for k in pk_labels:
        pk_data.append(data["pk"][k])
    return [[bw_labels, bw_data], [pk_labels, pk_data]]

@service.json
def json_netdev_avg():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e

    devs = timeseries.sub_find("nodes", node, "netdev")
    data = {
        "rxkBps": [],
        "rxkBps": [],
        "txkBps": [],
        "rxpckps": [],
        "txpckps": [],
    }

    for dev in devs:
        for metric in data:
            data[metric].append(timeseries.whisper_fetch_avg("nodes", node, "netdev", dev, metric, b=b, e=e))

    if node is None:
        return [dev, [rxkBps, txkBps], [rxpckps, txpckps]]

    return [
        dev,
        [data["rxkBps"], data["txkBps"]],
        [data["rxpckps"], data["txpckps"]],
    ]

@service.json
def json_blockdev():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e

    devs = timeseries.sub_find("nodes", node, "blockdev")
    metrics = [
        ("tps",      "all", "",     1),
        ("rsecps",   "avg", " rd",  1),
        ("wsecps",   "avg", " wr", -1),
        ("avgrq_sz", "all", "",     1),
        ("await",    "all", "",     1),
        ("svctm",    "all", "",     1),
        ("pct_util", "all", "",     1),
    ]
    data_agg = []
    data_ts = {}
    for dev in devs:
        line = [dev]
        data_ts[dev] = {}
        for metric, what, suffix, multiplier in metrics:
            if what == "all":
                line += timeseries.whisper_fetch_avg_min_max("nodes", node, "blockdev", dev, metric, b=b, e=e)
            else:
                line += [timeseries.whisper_fetch_avg("nodes", node, "blockdev", dev, metric, b=b, e=e)]
            data_ts[dev][metric] = timeseries.whisper_fetch("nodes", node, "blockdev", dev, metric, b=b, e=e)
        data_agg.append(line)

    max_await = 300000

    dev = []
    tm_dev = []

    tps = []
    rsecps = []
    wsecps = []
    avgrq_sz = []
    await = []
    svctm = []
    pct_util = []
    tm_await = []
    tm_svc = []

    if node is None:
        return {
          'avg':[dev, tps, avgrq_sz, await, svctm, pct_util, [rsecps, wsecps],
                 tm_dev, [tm_svc, tm_await]]
        }

    h = {}
    for _dev in data_ts:
        for metric, what, suffix, multiplier in metrics:
            label = _dev + metric
            if label not in h:
                h[label] = []
            for r in data_ts[_dev][metric]:
                value = r[0], r[1] * multiplier if r[1] is not None else None
                h[label].append(value)

    l = sorted(data_agg, key=lambda r: (r[4]+r[5]))
    l.reverse()
    for i, r in enumerate(l):
        dev.append(r[0])
        rsecps.append(r[4])
        wsecps.append(r[5])
        if i >= 10: break
    secps_devs = []
    secps_time = []
    for _dev in dev:
        for metric in ("rsecps", "wsecps"):
            secps_devs.append(_dev+metric)
            secps_time.append(h[_dev+metric])


    l = sorted(data_agg, key=lambda r: r[1])
    l.reverse()
    for i, r in enumerate(l):
        tps.append((r[0],r[3],r[2],r[1]))
        if i >= 10: break
    tps_devs = [r[0] for r in tps]
    tps_time = []
    for _dev in tps_devs:
        tps_time.append(h[_dev+"tps"])

    l = sorted(data_agg, key=lambda r: r[6])
    l.reverse()
    for i, r in enumerate(l):
        avgrq_sz.append((r[0], r[8],r[7],r[6]))
        if i >= 10: break
    avgrq_sz_devs = [r[0] for r in avgrq_sz]
    avgrq_sz_time = []
    for _dev in avgrq_sz_devs:
        avgrq_sz_time.append(h[_dev+"avgrq_sz"])

    l = sorted(data_agg, key=lambda r: r[9])
    l.reverse()
    for i, r in enumerate(l):
        await.append((r[0], r[11],r[10],r[9]))
        if i >= 10: break
    await_devs = [r[0] for r in await]
    await_time = []
    for _dev in await_devs:
        await_time.append(h[_dev+"await"])

    for i, r in enumerate(l):
        tm_dev.append(r[0])
        tm_await.append(r[9]-r[12])
        tm_svc.append(r[12])
        if i >= 10: break

    l = sorted(data_agg, key=lambda r: r[12])
    l.reverse()
    for i, r in enumerate(l):
        svctm.append((r[0], r[14],r[13],r[12]))
        if i >= 10: break
    svctm_devs = [r[0] for r in svctm]
    svctm_time = []
    for _dev in svctm_devs:
        svctm_time.append(h[_dev+"svctm"])

    l = sorted(data_agg, key=lambda r: r[15])
    l.reverse()
    for i, r in enumerate(l):
        pct_util.append((r[0], r[17],r[16],r[15]))
        if i >= 10: break
    pct_util_devs = [r[0] for r in pct_util]
    pct_util_time = []
    for _dev in pct_util_devs:
        pct_util_time.append(h[_dev+"pct_util"])


    return {
             'avg': [dev, tps, avgrq_sz, await, svctm, pct_util, [rsecps, wsecps], tm_dev,[tm_svc, tm_await]],
             'begin': b,
             'end': e,
             'time': {
               'tps': {
                 'labels': tps_devs,
                 'data': tps_time,
               },
               'pct_util': {
                 'labels': pct_util_devs,
                 'data': pct_util_time,
               },
               'await': {
                 'labels': await_devs,
                 'data': await_time,
               },
               'svctm': {
                 'labels': svctm_devs,
                 'data': svctm_time,
               },
               'avgrq_sz': {
                 'labels': avgrq_sz_devs,
                 'data': avgrq_sz_time,
               },
               'secps': {
                 'labels': secps_devs,
                 'data': secps_time,
               },
             }
           }

@service.json
def json_fs():
    node = request.vars.node
    b = request.vars.b
    e = request.vars.e

    if node is None:
        return {}

    metrics = [
        "size",
        "used",
    ]
    data = {}
    fss = timeseries.sub_find("nodes", node, "fs_u", prefix="/")
    for fs in fss:
        data[fs] = {}
        for metric in metrics:
            data[fs][metric] = timeseries.whisper_fetch("nodes", node, "fs_u", fs, metric, b=b, e=e)
    return data



