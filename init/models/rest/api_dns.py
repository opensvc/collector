
def raise_on_error(response):
    if response.errors:
        s = ", ".join(map(lambda x: ": ".join(x), response.errors.items()))
        raise Exception(s)

def dns_record_responsible(row, current={}):
    if "Manager" in user_groups():
        return
    t = row.get("type")
    if t is None:
        t = current.get("type")
    t = str(t)
    name = row.get("name")
    if name is None:
        name = current.get("name")
    name = str(name)
    content = row.get("content")
    if content is None:
        content = current.get("content")
    content = str(content)

    if t in ("A", "AAAA"):
        addr = content
    elif t in ("PTR"):
        addr = name.split(".in-addr.")[0]
        v = addr.split(".")
        v.reverse()
        addr = ".".join(v)
    else:
        raise Exception("Manager privilege required to handle the %s record type"%t)
    sql = """
      select networks.id from
      networks, auth_group, auth_membership, auth_user where
        auth_user.id=%(user_id)d and
        auth_user.id=auth_membership.user_id and
        auth_membership.group_id=auth_group.id and
        auth_group.role=networks.team_responsible and
        inet_aton("%(addr)s") >= inet_aton(networks.begin) and
        inet_aton("%(addr)s") <= inet_aton(networks.end)
    """ % dict(addr=addr, user_id=auth.user_id)
    networks = db.executesql(sql)
    if len(networks) > 0:
        return

    sql = """
      select network_segments.id from
      network_segments, networks, network_segment_responsibles, auth_group, auth_membership, auth_user where
        auth_user.id=%(user_id)d and
        auth_user.id=auth_membership.user_id and
        auth_membership.group_id=auth_group.id and
        auth_group.role=networks.team_responsible and
        networks.id=network_segments.net_id and
        network_segments.id=network_segment_responsibles.seg_id and
        inet_aton("%(addr)s") >= inet_aton(network_segments.seg_begin) and
        inet_aton("%(addr)s") <= inet_aton(network_segments.seg_end)
    """ % dict(addr=addr, user_id=auth.user_id)
    segments = db.executesql(sql)
    if len(segments) > 0:
        return

    raise Exception("Not allowed to manage the record %s %s %s"%(name, t, content))

#
class rest_put_dns_domain_sync(rest_put_handler):
    def __init__(self):
        desc = [
          "Increment a domain SOA record serial so that secondary dns refresh the zone content.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X PUT https://%(collector)s/init/rest/api/dns/domains/<id>/sync",
        ]

        rest_put_handler.__init__(
          self,
          path="/dns/domains/<id>/sync",
          desc=desc,
          examples=examples,
        )

    def handler(self, domain_id, **vars):
        q = (dbdns.domains.id>0)
        q &= _where(None, 'domains', domain_id, 'id', db=dbdns)
        domain = dbdns(q).select().first()

        if domain is None:
            raise Exception("domain %s not found" % domain_id)
        dname = domain.name

        q = dbdns.records.name == dname
        q &= dbdns.records.type == "SOA"
        rows = dbdns(q).select()

        if len(rows) != 1:
            raise Exception("no single SOA found for domain %s"%dname)

        l = rows[0].content.split()

        if len(l) < 3:
            raise Exception("SOA record content has less than 3 fields for domain %s"%dname)

        new = int(l[2]) + 1
        l[2] = str(new)
        dbdns(q).update(content=' '.join(l))

        fmt = "SOA incremented to %(new)d for domain %(dname)s"
        d = dict(new=new, dname=dname)

        _log('dns.domain.sync', fmt, d)
        l = {
          'event': 'pdns_records_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return dict(info=fmt%d)

#
class rest_get_dns_domains(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List dns zones.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/dns/domains",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/dns/domains",
          tables=["domains"],
          dbo=dbdns,
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = dbdns.domains.id > 0
        self.set_q(q)
        return self.prepare_data(**vars)
#
class rest_get_dns_records(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List dns records.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/dns/records",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/dns/records",
          tables=["records"],
          dbo=dbdns,
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = dbdns.records.id > 0
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_dns_domain(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display a dns domain.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/dns/domains/5",
        ]

        rest_get_line_handler.__init__(
          self,
          path="/dns/domains/<id>",
          tables=["domains"],
          dbo=dbdns,
          desc=desc,
          examples=examples,
        )

    def handler(self, domain_id, **vars):
        q = dbdns.domains.id == domain_id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_dns_record(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display a dns record.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/dns/records/5",
        ]

        rest_get_line_handler.__init__(
          self,
          path="/dns/records/<id>",
          tables=["records"],
          dbo=dbdns,
          desc=desc,
          examples=examples,
        )

    def handler(self, record_id, **vars):
        q = dbdns.records.id == record_id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_dns_domain_records(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List dns records in a domain.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/dns/domains/10/records",
        ]

        rest_get_table_handler.__init__(
          self,
          path="/dns/domains/<id>/records",
          tables=["records"],
          dbo=dbdns,
          desc=desc,
          examples=examples,
        )

    def handler(self, dom_id, **vars):
        q = dbdns.records.domain_id == dom_id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_post_dns_domains(rest_post_handler):
    def __init__(self):
        desc = [
          "Create a dns domain.",
          "The user must be in the DnsManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the nodes table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X POST -d name="opensvc.com" -d type=MASTER https://%(collector)s/init/rest/api/dns/domains""",
        ]
        rest_post_handler.__init__(
          self,
          path="/dns/domains",
          tables=["domains"],
          dbo=dbdns,
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        check_privilege("DnsManager")
        if len(vars) == 0:
            raise Exception("Insufficient data")
        q = dbdns.domains.id > 0
        for v in vars:
            q &= dbdns.domains[v] == vars[v]
        row = dbdns(q).select().first()
        if row is not None:
            return dict(info="Domain already exists")
        response = dbdns.domains.validate_and_insert(**vars)
        raise_on_error(response)
        row = dbdns(q).select().first()
        _log('dns.domains.create',
             'record %(name)s %(type)s created. data %(data)s',
             dict(name=row.name, type=row.type, data=str(vars)),
            )
        l = {
          'event': 'pdns_domains_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return rest_get_dns_domain().handler(row.id)


#
class rest_post_dns_domain(rest_post_handler):
    def __init__(self):
        desc = [
          "Change a dns domain.",
          "The user must be in the DnsManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the nodes table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X POST -d master="foo" https://%(collector)s/init/rest/api/dns/domains/10""",
        ]
        rest_post_handler.__init__(
          self,
          path="/dns/domains/<id>",
          tables=["domains"],
          dbo=dbdns,
          desc=desc,
          examples=examples,
        )

    def handler(self, domain_id, **vars):
        check_privilege("DnsManager")
        q = dbdns.domains.id == domain_id
        row = dbdns(q).select().first()
        if row is None:
            return dict(error="Domain %s does not exist"%domain_id)
        response = dbdns(q).validate_and_update(**vars)
        raise_on_error(response)
        _log('dns.domains.change',
             'record %(name)s %(type)s changed. data %(data)s',
             dict(name=row.name, type=row.type, data=str(vars)),
            )
        l = {
          'event': 'pdns_domains_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return rest_get_dns_domain().handler(domain_id)


#
class rest_post_dns_records(rest_post_handler):
    def __init__(self):
        desc = [
          "Create a dns record.",
          "The user must be responsible for the ip address network or segment.",
          "The user must be in the DnsOperator privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the nodes table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X POST -d name="mynode.opensvc.com" -d type=A -d content="1.2.3.4" https://%(collector)s/init/rest/api/dns/records""",
        ]
        rest_post_handler.__init__(
          self,
          path="/dns/records",
          tables=["records"],
          dbo=dbdns,
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        check_privilege("DnsOperator")
        if len(vars) == 0:
            raise Exception("Insufficient data")
        vars["change_date"] = int((datetime.datetime.now()-datetime.datetime(1970, 1, 1)).total_seconds())
        q = dbdns.records.id > 0
        for v in vars:
            q &= dbdns.records[v] == vars[v]
        row = dbdns(q).select().first()
        if row is not None:
            return dict(info="Record already exists")
        dns_record_responsible(vars)
        response = dbdns.records.validate_and_insert(**vars)
        raise_on_error(response)
        row = dbdns(q).select().first()

        fmt = 'record %(name)s %(type)s %(content)s created in domain %(domain)s'
        d = dict(name=row.name, type=row.type, content=row.content, domain=str(row.domain_id))
        _log('dns.records.create', fmt, d)
        l = {
          'event': 'pdns_records_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        ret = rest_get_dns_record().handler(row.id)
        ret["info"] = fmt % d
        return ret


#
class rest_post_dns_record(rest_post_handler):
    def __init__(self):
        desc = [
          "Change a dns record.",
          "The user must be responsible for the ip address network or segment.",
          "The user must be in the DnsOperator privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the nodes table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X POST -d comment="foo" https://%(collector)s/init/rest/api/dns/records/10""",
        ]
        rest_post_handler.__init__(
          self,
          path="/dns/records/<id>",
          tables=["records"],
          dbo=dbdns,
          desc=desc,
          examples=examples,
        )

    def handler(self, record_id, **vars):
        check_privilege("DnsOperator")
        q = dbdns.records.id == record_id
        row = dbdns(q).select().first()
        if row is None:
            return dict(error="Record %s does not exist"%record_id)
        dns_record_responsible(row)
        dns_record_responsible(vars, current=row)
        response = dbdns(q).validate_and_update(**vars)
        raise_on_error(response)
        _log('dns.records.change',
             'record %(name)s %(type)s %(content)s changed. data %(data)s',
             dict(name=row.name, type=row.type, content=row.content, data=str(vars)),
            )
        l = {
          'event': 'pdns_records_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return rest_get_dns_record().handler(record_id)


#
class rest_delete_dns_domains(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete dns domains.",
          "Also delete dns records in this domain.",
          "The user must be in the DnsManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the nodes table.",
        ]
        examples = [
          "# curl -u %(email)s -o- --header 'Content-Type: application/json' -d @/tmp/data.json -X DELETE https://%(collector)s/init/rest/api/dns/domains",
        ]
        rest_delete_handler.__init__(
          self,
          path="/dns/domains",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "id" not in vars:
            raise Exception("The 'id' key is mandatory")
        return rest_delete_dns_domain().handler(vars["id"])

#
class rest_delete_dns_domain(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a dns domain.",
          "Also delete dns records in this domain.",
          "The user must be in the DnsManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the nodes table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/dns/domains/10",
        ]
        rest_delete_handler.__init__(
          self,
          path="/dns/domains/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, domain_id, **vars):
        check_privilege("DnsManager")

        q = dbdns.domains.id == domain_id
        row = dbdns(q).select().first()
        if row is None:
            return dict(info="Domain %s does not exist"%record_id)
        dbdns(q).delete()

        q = dbdns.records.domain_id == domain_id
        q = dbdns(q).delete()

        # todo lookup nodename, svcname for logging
        _log('dns.domains.delete',
             'record %(name)s %(type)s deleted',
             dict(name=row.name, type=row.type),
            )
        l = {
          'event': 'pdns_domains_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        l = {
          'event': 'pdns_records_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return dict(info="Domain %s %s deleted" % (row.name, row.type))

#
class rest_delete_dns_records(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete dns records.",
          "The user must be responsible for the ip address network or segment.",
          "The user must be in the DnsOperator privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the nodes table.",
        ]
        examples = [
          "# curl -u %(email)s -o- --header 'Content-Type: application/json' -d @/tmp/data.json -X DELETE https://%(collector)s/init/rest/api/dns/records",
        ]
        rest_delete_handler.__init__(
          self,
          path="/dns/records",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "id" not in vars:
            raise Exception("The 'id' key is mandatory")
        return rest_delete_dns_record().handler(vars["id"])

#
class rest_delete_dns_record(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a dns record.",
          "The user must be responsible for the ip address network or segment.",
          "The user must be in the DnsOperator privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the nodes table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/dns/records/10",
        ]
        rest_delete_handler.__init__(
          self,
          path="/dns/records/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, record_id, **vars):
        check_privilege("DnsOperator")
        q = dbdns.records.id == record_id
        row = dbdns(q).select().first()
        if row is None:
            return dict(info="Record %s does not exist"%record_id)
        dns_record_responsible(row)
        dbdns(q).delete()
        # todo lookup nodename, svcname for logging
        _log('dns.records.delete',
             'record %(name)s %(type)s %(content)s deleted',
             dict(name=row.name, type=row.type, content=row.content),
            )
        l = {
          'event': 'pdns_records_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return dict(info="Record %s %s %s deleted" % (row.name, row.type, row.content))

