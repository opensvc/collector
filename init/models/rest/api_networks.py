import datetime

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
        q = q_filter(q, app_field=db.v_nodenetworks.app)
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
        id = get_network_id(id)
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
        net_id = get_network_id(net_id)
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
        net_id = get_network_id(net_id)
        ipl = get_network_ips(net_id)
        return dict(data=ipl)

#
class rest_post_network_allocate(rest_post_handler):
    def __init__(self):
        desc = [
          "Allocate a free ip in the specified network",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/networks/10/allocate",
        ]
        rest_post_handler.__init__(
          self,
          path="/networks/<id>/allocate",
          desc=desc,
          examples=examples,
        )

    def handler(self, net_id, **vars):
        instance_name = vars.get("name")
        ip = allocate_network_ip(net_id, instance_name)
        return dict(data=ip)

#
class rest_post_network_release(rest_post_handler):
    def __init__(self):
        desc = [
          "Release an ip address",
          "The ip to release is used as <id> in the request path",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/networks/10.0.0.3/release",
        ]
        rest_post_handler.__init__(
          self,
          path="/networks/<id>/release",
          desc=desc,
          examples=examples,
        )

    def handler(self, ipaddr, **vars):
        instance_name = vars.get("name")
        net_id = get_network_id(ipaddr)
        if auth_is_svc():
            ret = delete_service_dns_record(
                instance_name=instance_name,
                content=ipaddr,
            )
        elif auth_is_node():
            raise HTTP(404, "Ip release for nodes is not implemented")
        else:
            raise HTTP(404, "Ip release for users is not implemented")
        return ret

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
        net_id = get_network_id(net_id)
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

class rest_post_networks_segments_responsibles(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach responsible groups to network segments.",
          "A segment is an ip range suppporting management delegation and ip provisioning properties.",
          "Members of responsible groups are allowed to allocate ips in the segment",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/networks/segments_responsibles",
        ]
        rest_post_handler.__init__(
          self,
          path="/networks/segments_responsibles",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        return rest_post_network_segment_responsible().handler(vars["net_id"], vars["seg_id"], vars["group_id"])

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

class rest_delete_networks_segments_responsibles(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach responsible groups from network segments.",
          "A segment is an ip range suppporting management delegation and ip provisioning properties.",
          "Members of responsible groups are allowed to allocate ips in the segment",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/networks/segments_responsibles",
        ]
        rest_delete_handler.__init__(
          self,
          path="/networks/segments_responsibles",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        return rest_delete_network_segment_responsible().handler(vars["net_id"], vars["seg_id"], vars["group_id"])


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
        ws_send('networks_change')
        return rest_get_network().handler(id, props=','.join(["id","updated"]+vars.keys()))


#
class rest_delete_networks_segments(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete networks segments",
          "A segment is an ip range suppporting management delegation and ip provisioning properties.",
          "Attached responsible group are also detached.",
          "The NetworkManager privilege is required.",
          "The segment's parent network ownership is required.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/networks/segments""",
        ]
        rest_delete_handler.__init__(
          self,
          path="/networks/segments",
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        if "net_id" not in vars:
            raise HTTP(400, "the 'net_id' parameter is required")
        if "seg_id" not in vars:
            raise HTTP(400, "the 'seg_id' parameter is required")
        return rest_delete_network_segment().handler(vars["net_id"], vars["seg_id"])

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
            raise HTTP(404, "Network %s not found" % net_id)

        q = db.network_segments.id == seg_id
        seg = db(q).select().first()
        if seg is None:
            raise HTTP(404, "Network segment %s not found" % seg_id)
        db(q).delete()

        q = db.network_segment_responsibles.seg_id == seg_id
        db(q).delete()

        _log('networks.segment.delete',
             'delete segment %(s)s of network %(n)s',
             dict(s="-".join((seg.seg_begin, seg.seg_end)), n="/".join((net.network, str(net.netmask))))
            )
        ws_send("network_segments_delete", {"seg_id": seg_id})
        return dict(info='deleted segment %(s)s of network %(n)s' % dict(s="-".join((seg.seg_begin, seg.seg_end)), n="/".join((net.network, str(net.netmask)))))

#
class rest_post_network_segments(rest_post_handler):
    def __init__(self):
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
          props_blacklist=["net_id", "id"],
          examples=examples
        )

    def handler(self, net_id, **vars):
        check_privilege("NetworkManager")
        network_responsible(net_id)
        vars["net_id"] = net_id
        for i in ["seg_begin", "seg_end"]:
            if i not in vars:
                raise HTTP(400, "missing '%s' parameter" % i)

        q = db.networks.id == net_id
        row = db(q).select().first()
        if row is None:
            raise HTTP(404, "Network %s not found" % net_id)

        self.validate_range(net_id, vars)
        seg_id = db.network_segments.insert(**vars)
        db.network_segment_responsibles.insert(seg_id=seg_id,
                                               group_id=user_primary_group_id())

        _log('networks.segment.create',
             'create segment of network %(n)s with properties %(data)s',
             dict(n="/".join((row.network, str(row.netmask))), data=str(vars))
            )
        ws_send("network_segments_change", {"seg_id": seg_id})
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
                raise HTTP(409, "Range begin conflicts with an existing segment")
            if _end >= row[0] and _end <= row[1]:
                raise HTTP(409, "Range end conflicts with an existing segment")

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
        ws_send('network_segments_change')
        return rest_get_network().handler(id, props=','.join(["id"]+vars.keys()))


#
class rest_post_networks(rest_post_handler):
    def __init__(self):
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
        ws_send('networks_change')
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
        ws_send('networks_change')
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
            raise HTTP(400, "The 'id' key is mandatory")
        id = vars["id"]
        del(vars["id"])
        return rest_delete_network().handler(id, **vars)

