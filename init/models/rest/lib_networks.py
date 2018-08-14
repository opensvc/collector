def network_segment_responsible(id):
    try:
        network_responsible(net_id)
    except:
        pass
    q = db.network_segments.id == id
    row = db(q).select().first()
    if row is None:
        raise Exception("Network segment %s does not exist" % id)
    try:
        network_responsible(row.net_id)
    except:
        pass
    ug = user_groups()
    if "Manager" in ug:
        return
    q &= db.network_segment_responsibles.seg_id == db.network_segments.id
    q &= db.network_segment_responsibles.group_id.belongs(ug)
    n = db(q).count()
    if n != 1:
        raise Exception("Not authorized: user is not responsible for network segment %s" % id)

def network_responsible(id):
    q = db.networks.id == id
    n = db(q).count()
    if n == 0:
        raise Exception("Network %s does not exist" % id)
    ug = user_groups()
    if "Manager" in ug:
        return
    q &= db.networks.team_responsible.belongs(ug)
    n = db(q).count()
    if n != 1:
        raise Exception("Not authorized: user is not responsible for network %s" % id)

def get_network_id(id):
    if type(id) not in (unicode, str):
        return id
    regex = re.compile("[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+")
    if not regex.match(id):
        return id
    sql = """select id from networks where
             inet_aton("%(ip)s") <= inet_aton(broadcast) and
             inet_aton("%(ip)s") >= inet_aton(network)""" % dict(ip=id)
    rows = db.executesql(sql)
    if len(rows) == 0:
        raise HTTP(404, "%s not found in any known network"%id)
    if len(rows) > 1:
        raise HTTP(409, "%s found in multiple networks"%id)
    return rows[0][0]


def get_network_ips(net_id):
    from socket import inet_ntoa
    from struct import pack
    sql = """select count(id) from network_segments where net_id=%s"""%net_id
    n_segs = db.executesql(sql)[0][0]

    sql = """select
               inet_aton(s.seg_begin),
               inet_aton(s.seg_end),
               s.seg_type,
               s.id
             from
               network_segments s,
               network_segment_responsibles sr
             where
               s.net_id = %s and
               s.id = sr.seg_id and
               sr.group_id in (%s)
             group by s.id
             order by seg_begin
          """%(net_id, ','.join([repr(str(x)) for x in user_group_ids()]))
    rows = db.executesql(sql)
    ipl = []

    if n_segs > 0:
        if len(rows) == 0:
            raise Exception("you are owner of no segment of this network")
        for row in rows:
            ipl += [{"seg_id": row[3], "ip": inet_ntoa(pack('>L', x)), "type": row[2]} for x in range(row[0], row[1])]
    else:
        sql = """select inet_aton(begin), inet_aton(end) from networks where id=%s"""%net_id
        rows = db.executesql(sql)
        if len(rows) == 0:
            raise Exception("network not found")
        ipl = [{"seg_id": None, "ip": inet_ntoa(pack('>L', x)), "type": ""} for x in range(rows[0][0], rows[0][1])]
    if len(ipl) == 0:
        return []

    sql = """select content,name from records where content in (%s)"""%','.join([repr(x["ip"]) for x in ipl])
    rows = dbdns.executesql(sql)
    alloc_ips = {}
    for content, name in rows:
        alloc_ips[content] = name
    for i, ip in enumerate(ipl):
        if ip["ip"] in alloc_ips:
           ipl[i]["record_name"] = alloc_ips[ip["ip"]]
        else:
           ipl[i]["record_name"] = ""

    sql = """select nodename, node_id, addr from v_nodenetworks where net_id=%s"""%net_id
    rows = db.executesql(sql)
    alloc_ips = {}
    for nodename, node_id, addr in rows:
        alloc_ips[addr] = {"nodename": nodename, "node_id": node_id}
    for i, ip in enumerate(ipl):
        if ip["ip"] in alloc_ips:
           ipl[i]["nodename"] = alloc_ips[ip["ip"]]["nodename"]
           ipl[i]["node_id"] = alloc_ips[ip["ip"]]["node_id"]
        else:
           ipl[i]["nodename"] = ""
           ipl[i]["node_id"] = ""

    return ipl

def allocate_network_ip(net_id, instance_name):
    from applications.init.modules import lock
    here_d = os.path.dirname(__file__)
    lockfile = os.path.join(here_d, '..', 'private', 'allocate_network_ip.lock')

    fd = lock.lock(timeout=5, delay=1, lockfile=lockfile, intent="allocate")
    try:
        return _allocate_network_ip(net_id, instance_name)
    finally:
        lock.unlock(fd)

def _allocate_network_ip(net_id, instance_name):
    net_id = get_network_id(net_id)
    ipl = [ip for ip in get_network_ips(net_id) if ip["record_name"] == "" and ip["nodename"] == ""]
    if len(ipl) == 0:
        raise Exception("No free address in this network")
    ip = ipl[0]
    if auth_is_svc():
        create_service_dns_record(
            instance_name=instance_name,
            content=ip["ip"],
        )
    elif auth_is_node():
        raise Exception("Ip allocation for nodes is not implemented")
    else:
        raise Exception("Ip allocation for users is not implemented")

    ip["network"] = db.networks[net_id].as_dict()
    seg_id = ip["seg_id"]
    if seg_id:
        ip["segment"] = db.network_segments[seg_id].as_dict()
    return ip

