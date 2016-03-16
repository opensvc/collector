import datetime

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
             inet_aton("%(ip)s") <= inet_aton(end) and
             inet_aton("%(ip)s") >= inet_aton(begin)""" % dict(ip=id)
    rows = db.executesql(sql)
    if len(rows) == 0:
        raise Exception("%s not found in any known network"%id)
    if len(rows) > 1:
        raise Exception("%s found in multiple networks"%id)
    return rows[0][0]


#
class rest_get_network_nodes(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List nodes on the specified network.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/networks/10/nodes",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/networks/<id>/nodes",
          tables=["nodes"],
          desc=desc,
          examples=examples,
        )

    def handler(self, net_id, **vars):
        q = db.networks.id == net_id
        net = db(q).select().first()
        if net is None:
            return dict(data=[])
        q = db.v_nodenetworks.net_network == net.network
        q &= db.v_nodenetworks.net_netmask == net.netmask
        q &= _where(None, 'v_nodenetworks', domain_perms(), 'nodename')
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_network(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display all network properties.",
          "Display selected network properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/networks/10?props=id,netmask",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/networks/<id>",
          tables=["networks"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        id = get_network_id(id)
        q = db.networks.id == id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_networks(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List all networks and their selected properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/networks?props=id,network,netmask,gateway",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/networks",
          tables=["networks"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.networks.id > 0
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_network_segments(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List all segments of a network.",
          "A segment is an ip range suppporting management delegation and ip provisioning properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/networks/10/segments",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/networks/<id>/segments",
          tables=["network_segments"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.networks.id == id
        q &= db.networks.id == db.network_segments.net_id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_network_segment(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display a segment of a network.",
          "A segment is an ip range suppporting management delegation and ip provisioning properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/networks/10/segments/10",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/networks/<id>/segments/<id>",
          tables=["network_segments"],
          desc=desc,
          examples=examples,
        )

    def handler(self, net_id, seg_id, **vars):
        q = db.networks.id == net_id
        q &= db.networks.id == db.network_segments.net_id
        q &= db.network_segments.id == seg_id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_network_ips(rest_get_handler):
    def __init__(self):
        desc = [
          "Display ips of a network.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/networks/10/ips",
        ]
        rest_get_handler.__init__(
          self,
          path="/networks/<id>/ips",
          desc=desc,
          examples=examples,
        )

    def handler(self, net_id, **vars):
        from socket import inet_ntoa
        from struct import pack
        sql = """select count(id) from network_segments where net_id=%s"""%net_id
        n_segs = db.executesql(sql)[0][0]

        sql = """select
                   inet_aton(s.seg_begin),
                   inet_aton(s.seg_end),
                   s.seg_type
                 from
                   network_segments s,
                   network_segment_responsibles sr,
                   auth_group g
                 where
                   s.net_id = %s and
                   s.id = sr.seg_id and
                   sr.group_id = g.id and
                   g.role in (%s)
                 group by s.id
                 order by inet_aton(seg_begin)
              """%(net_id, ','.join(map(lambda x: "'"+x+"'", user_groups())))
        rows = db.executesql(sql)
        ipl = []

        if n_segs > 0:
            if len(rows) == 0:
                raise Exception("you are owner of no segment of this network")
            for row in rows:
                ipl += map(lambda x: {"ip": inet_ntoa(pack('>L', x)), "type": row[2]}, range(row[0], row[1]))
        else:
            sql = """select inet_aton(network), inet_aton(broadcast) from networks where id=%s"""%net_id
            rows = db.executesql(sql)
            if len(rows) == 0:
                return T("network not found")
            ipl = map(lambda x: {"ip": inet_ntoa(pack('>L', x)), "type": ""}, range(rows[0][0], rows[0][1]))
        if len(ipl) == 0:
            return []

        sql = """select content,name from records where content in (%s)"""%','.join(map(lambda x: repr(x["ip"]), ipl))
        rows = dbdns.executesql(sql)
        alloc_ips = {}
        for content, name in rows:
            alloc_ips[content] = name
        for i, ip in enumerate(ipl):
            if ip["ip"] in alloc_ips:
               ipl[i]["record_name"] = alloc_ips[ip["ip"]]
            else:
               ipl[i]["record_name"] = ""

        sql = """select nodename, addr from v_nodenetworks where net_id=%s"""%net_id
        rows = db.executesql(sql)
        alloc_ips = {}
        for nodename, addr in rows:
            alloc_ips[addr] = nodename
        for i, ip in enumerate(ipl):
            if ip["ip"] in alloc_ips:
               ipl[i]["nodename"] = alloc_ips[ip["ip"]]
            else:
               ipl[i]["nodename"] = ""

        return dict(data=ipl)

#
class rest_get_network_segment_responsibles(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List a network segments responsibles.",
          "A segment is an ip range suppporting management delegation and ip provisioning properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/networks/10/segments/10/responsibles",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/networks/<id>/segments/<id>/responsibles",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, net_id, seg_id, **vars):
        q = db.networks.id == net_id
        q &= db.networks.id == db.network_segments.net_id
        q &= db.network_segments.id == db.network_segment_responsibles.seg_id
        q &= db.network_segment_responsibles.group_id == db.auth_group.id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_post_network_segment_responsible(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach a group to network segments responsibles.",
          "A segment is an ip range suppporting management delegation and ip provisioning properties.",
          "Members of responsible groups are allowed to allocate ips in the segment",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/networks/10/segments/10/responsibles/2",
        ]
        rest_post_handler.__init__(
          self,
          path="/networks/<id>/segments/<id>/responsibles/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, net_id, seg_id, group_id, **vars):
        network_segment_responsible(seg_id)
        q = db.network_segments.id == seg_id
        row = db(q).select().first()
        q = db.auth_group.id == group_id
        row_role = db(q).select().first()
        if row_role is None:
            return dict(error="group %s not found" % group_id)
        role = row_role.role
        q = db.network_segment_responsibles.seg_id==seg_id
        q &= db.network_segment_responsibles.group_id==group_id
        n = db(q).count()
        if n > 0:
            return dict(info="group %(r)s is already responsible for segment %(u)s" % dict(r=role, u='-'.join((row.seg_begin, row.seg_end))))
        db.network_segment_responsibles.insert(seg_id=seg_id, group_id=group_id)
        _log('networks.segment.attach',
             'attached group %(r)s to network segment %(u)s',
             dict(r=role, u='-'.join((row.seg_begin, row.seg_end))))
        return dict(info="attached group %(r)s to network segment %(u)s" % dict(r=role, u='-'.join((row.seg_begin, row.seg_end))))


#
class rest_delete_network_segment_responsible(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach a group from network segments responsibles.",
          "A segment is an ip range suppporting management delegation and ip provisioning properties.",
          "Members of responsible groups are allowed to allocate ips in the segment",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/networks/10/segments/10/responsibles/2",
        ]
        rest_delete_handler.__init__(
          self,
          path="/networks/<id>/segments/<id>/responsibles/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, net_id, seg_id, group_id, **vars):
        network_segment_responsible(seg_id)
        q = db.network_segments.id == seg_id
        row = db(q).select().first()
        q = db.auth_group.id == group_id
        row_role = db(q).select().first()
        role = row_role.role
        if row_role is None:
            return dict(error="group %s not found" % group_id)
        q = db.network_segment_responsibles.seg_id==seg_id
        q &= db.network_segment_responsibles.group_id==group_id
        n = db(q).count()
        if n == 0:
            return dict(error="group %(r)s is not responsible for segment %(u)s" % dict(r=role, u='-'.join((row.seg_begin, row.seg_end))))
        db(q).delete()
        _log('networks.segment.detach',
             'detached group %(r)s from network segment %(u)s',
             dict(r=role, u='-'.join((row.seg_begin, row.seg_end))))
        return dict(info="detached group %(r)s from network segment %(u)s" % dict(r=role, u='-'.join((row.seg_begin, row.seg_end))))


#
class rest_post_network(rest_post_handler):
    def __init__(self):
        desc = [
          "Update a set of network properties.",
          "The user must be responsible for the network",
          "The user must be in the NetworkManager privilege group",
          "The updated timestamp is automatically updated.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the networks table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -d pvid=12 -d comment="foo" https://%(collector)s/init/rest/api/networks/10""",
        ]
        rest_post_handler.__init__(
          self,
          path="/networks/<id>",
          desc=desc,
          tables=["networks"],
          props_blacklist=["begin", "end"],
          examples=examples
        )

    def handler(self, id, **vars):
        check_privilege("NetworkManager")
        network_responsible(id)
        q = db.networks.id == id
        vars["updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if "team_responsible" not in vars:
            vars["team_responsible"] = user_primary_group()
        db(q).update(**vars)
        _log('networks.update',
             'update properties %(data)s',
             dict(data=str(vars)),
            )
        l = {
          'event': 'networks_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return rest_get_network().handler(id, props=','.join(["id","updated"]+vars.keys()))


#
class rest_delete_network_segment(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a new network segment",
          "A segment is an ip range suppporting management delegation and ip provisioning properties.",
          "Attached responsible group are also detached.",
          "The NetworkManager privilege is required.",
          "The segment's parent network ownership is required.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/networks/<id>/segments/<id>""",
        ]
        rest_delete_handler.__init__(
          self,
          path="/networks/<id>/segments/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, net_id, seg_id, **vars):
        check_privilege("NetworkManager")
        network_responsible(net_id)
        q = db.networks.id == net_id
        net = db(q).select().first()
        if net is None:
            raise Exception("Network %s not found" % net_id)

        q = db.network_segments.id == seg_id
        seg = db(q).select().first()
        if seg is None:
            raise Exception("Network segment %s not found" % seg_id)
        db(q).delete()

        q = db.network_segment_responsibles.seg_id == seg_id
        db(q).delete()

        _log('networks.segment.delete',
             'delete segment %(s)s of network %(n)s',
             dict(s="-".join((seg.seg_begin, seg.seg_end)), n="/".join((net.network, str(net.netmask))))
            )
        return dict(info='deleted segment %(s)s of network %(n)s' % dict(s="-".join((seg.seg_begin, seg.seg_end)), n="/".join((net.network, str(net.netmask)))))

#
class rest_post_network_segments(rest_post_handler):
    def __init__(self):
        self.get_handler = rest_get_network_segments()
        self.update_one_handler = rest_post_network_segment()
        self.update_one_param = "id"
        desc = [
          "Create a new network segment",
          "Update network segments matching the specified query.",
          "A segment is an ip range suppporting management delegation and ip provisioning properties.",
          "The default segment type is 'static'.",
          "The NetworkManager privilege is required.",
          "The segment's parent network ownership is required.",
        ]
        examples = [
          """# curl -u %(email)s -o- -d comment="foo" -d seg_begin="192.168.0.0" -d seg_end="192.168.0.10" https://%(collector)s/init/rest/api/networks/10/segments""",
        ]
        rest_post_handler.__init__(
          self,
          path="/networks/<id>/segments",
          desc=desc,
          tables=["network_segments"],
          examples=examples
        )

    def handler(self, net_id, **vars):
        check_privilege("NetworkManager")
        network_responsible(net_id)
        vars["net_id"] = net_id
        for i in ["seg_begin", "seg_end"]:
            if i not in vars:
                raise Exception("missing '%s' parameter" % i)

        q = db.networks.id == net_id
        row = db(q).select().first()
        if row is None:
            raise Exception("Network %s not found" % net_id)

        self.validate_range(net_id, vars)
        seg_id = db.network_segments.insert(**vars)
        _log('networks.segment.create',
             'create segment of network %(n)s with properties %(data)s',
             dict(n="/".join((row.network, str(row.netmask))), data=str(vars))
            )
        return rest_get_network_segment().handler(net_id, seg_id)

    def ip2long(self, s):
        import socket, struct
        p = socket.inet_aton(s)
        return struct.unpack("!L", p)[0]

    def validate_range(self, net_id, vars):
        import socket
        sql = """select inet_aton(seg_begin), inet_aton(seg_end) from network_segments where net_id=%s """%net_id
        rows = db.executesql(sql)
        begin = vars.get("seg_begin")
        end = vars.get("seg_end")
        if begin is None or end is None:
            return
        _begin = self.ip2long(begin)
        _end = self.ip2long(end)
        for row in rows:
            if _begin >= row[0] and _begin <= row[1]:
                raise Exception("Range begin conflicts with an existing segment")
            if _end >= row[0] and _end <= row[1]:
                raise Exception("Range end conflicts with an existing segment")

#
class rest_post_network_segment(rest_post_handler):
    def __init__(self):
        desc = [
          "Update a set of network segment properties.",
          "The user must be responsible for the network segment.",
          "The user must be in the NetworkManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the networks table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -d seg_type=static https://%(collector)s/init/rest/api/network_segments/10""",
        ]
        rest_post_handler.__init__(
          self,
          path="/networks/<id>/segments/<id>",
          desc=desc,
          tables=["network_segments"],
          props_blacklist=["net_id", "id"],
          examples=examples
        )

    def handler(self, net_id, seg_id, **vars):
        check_privilege("NetworkManager")
        network_segment_responsible(seg_id)
        q = db.network_segments.id == seg_id
        db(q).update(**vars)
        _log('networks.update',
             'update properties %(data)s of segment %(seg_id)s',
             dict(data=str(vars), seg_id=seg_id),
            )
        l = {
          'event': 'network_segments_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return rest_get_network().handler(id, props=','.join(["id"]+vars.keys()))


#
class rest_post_networks(rest_post_handler):
    def __init__(self):
        self.get_handler = rest_get_networks()
        self.update_one_handler = rest_post_network()
        self.update_one_param = "id"
        desc = [
          "Create a new network",
          "Update network matching the specified query.",
          "If ``team_responsible``:green is not specified, default to user's primary group",
        ]
        examples = [
          """# curl -u %(email)s -o- -d comment="foo" -d network="192.168.0.0" -d netmask=22 -d team_responsible="SYSADM" https://%(collector)s/init/rest/api/networks""",
        ]
        rest_post_handler.__init__(
          self,
          path="/networks",
          desc=desc,
          tables=["networks"],
          props_blacklist=["begin", "end"],
          examples=examples
        )

    def handler(self, **vars):
        check_privilege("NetworkManager")
        vars["updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if "team_responsible" not in vars:
            vars["team_responsible"] = user_primary_group()
        id = db.networks.validate_and_insert(**vars)
        _log('networks.create',
             'create properties %(data)s',
             dict(data=str(vars))
            )
        l = {
          'event': 'networks_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return rest_get_network().handler(id, props=','.join(["id","updated"]+vars.keys()))


#
class rest_delete_network(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a network.",
          "The user must be responsible for the network.",
          "The user must be in the NetworkManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the networks table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/networks/10",
        ]
        rest_delete_handler.__init__(
          self,
          path="/networks/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        network_responsible(id)
        check_privilege("NetworkManager")
        q = db.networks.id == id
        net = db(q).select().first()
        if net is None:
            return dict(info="network does not exist")
        db(q).delete()
        _log('networks.delete',
             '%(network)s/%(netmask)s',
             dict(network=net.network, netmask=net.netmask),
            )
        l = {
          'event': 'networks_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return dict(info="Network %s deleted" % id)

#
class rest_delete_networks(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete networks.",
          "The user must be responsible for the networks.",
          "The user must be in the NetworkManager privilege group.",
          "The action is logged in the collector's log.",
          "Websocket events are sent to announce the changes in the networks table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X DELETE "https://%(collector)s/init/rest/api/networks?filters[]=pvid 10" """,
        ]
        rest_delete_handler.__init__(
          self,
          path="/networks",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "id" not in vars:
            raise Exception("The 'id' key is mandatory")
        id = vars["id"]
        del(vars["id"])
        return rest_delete_network().handler(id, **vars)

