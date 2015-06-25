from gluon.dal import smart_query

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
          tables=["pdns_domains"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.pdns_domains.id > 0
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
          tables=["pdns_records"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.pdns_records.id > 0
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
          tables=["pdns_domains"],
          desc=desc,
          examples=examples,
        )

    def handler(self, domain_id, **vars):
        q = db.pdns_domains.id == domain_id
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
          tables=["pdns_records"],
          desc=desc,
          examples=examples,
        )

    def handler(self, record_id, **vars):
        q = db.pdns_records.id == record_id
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
          tables=["pdns_records"],
          desc=desc,
          examples=examples,
        )

    def handler(self, dom_id, **vars):
        q = db.pdns_records.domain_id == dom_id
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
          tables=["pdns_domains"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        check_privilege("DnsManager")
        if len(vars) == 0:
            raise Exception("Insufficient data")
        q = db.pdns_domains.id > 0
        for v in vars:
            q &= db.pdns_domains[v] == vars[v]
        row = db(q).select().first()
        if row is not None:
            return dict(info="Domain already exists")
        response = db.pdns_domains.validate_and_insert(**vars)
        raise_on_error(response)
        row = db(q).select().first()
        _log('rest.dns.domains.create',
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
          tables=["pdns_domains"],
          desc=desc,
          examples=examples,
        )

    def handler(self, domain_id, **vars):
        check_privilege("DnsManager")
        q = db.pdns_domains.id == domain_id
        row = db(q).select().first()
        if row is None:
            return dict(error="Domain %s does not exist"%domain_id)
        response = db(q).validate_and_update(**vars)
        raise_on_error(response)
        _log('rest.dns.domains.change',
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
          tables=["pdns_records"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        check_privilege("DnsOperator")
        if len(vars) == 0:
            raise Exception("Insufficient data")
        q = db.pdns_records.id > 0
        for v in vars:
            q &= db.pdns_records[v] == vars[v]
        row = db(q).select().first()
        if row is not None:
            return dict(info="Record already exists")
        dns_record_responsible(vars)
        response = db.pdns_records.validate_and_insert(**vars)
        raise_on_error(response)
        row = db(q).select().first()
        _log('rest.dns.records.create',
             'record %(name)s %(type)s %(content)s created. data %(data)s',
             dict(name=row.name, type=row.type, content=row.content, data=str(vars)),
            )
        l = {
          'event': 'pdns_records_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return rest_get_dns_record().handler(row.id)


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
          tables=["pdns_records"],
          desc=desc,
          examples=examples,
        )

    def handler(self, record_id, **vars):
        check_privilege("DnsOperator")
        q = db.pdns_records.id == record_id
        row = db(q).select().first()
        if row is None:
            return dict(error="Record %s does not exist"%record_id)
        dns_record_responsible(row)
        dns_record_responsible(vars, current=row)
        response = db(q).validate_and_update(**vars)
        raise_on_error(response)
        _log('rest.dns.records.change',
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

        q = db.pdns_domains.id == domain_id
        row = db(q).select().first()
        if row is None:
            return dict(info="Domain %s does not exist"%record_id)
        db(q).delete()

        q = db.pdns_records.domain_id == domain_id
        q = db(q).delete()

        # todo lookup nodename, svcname for logging
        _log('rest.dns.domains.delete',
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
        q = db.pdns_records.id == record_id
        row = db(q).select().first()
        if row is None:
            return dict(info="Record %s does not exist"%record_id)
        dns_record_responsible(row)
        db(q).delete()
        # todo lookup nodename, svcname for logging
        _log('rest.dns.records.delete',
             'record %(name)s %(type)s %(content)s deleted',
             dict(name=row.name, type=row.type, content=row.content),
            )
        l = {
          'event': 'pdns_records_change',
          'data': {'foo': 'bar'},
        }
        _websocket_send(event_msg(l))
        return dict(info="Record %s %s %s deleted" % (row.name, row.type, row.content))

