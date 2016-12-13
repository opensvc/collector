def create_zone(zone):
    domain_type = "MASTER"
    data = {
        "name": zone,
        "type": domain_type,
    }
    domain_id = dbdns.domains.insert(**data)

    _log('dns.domains.create',
         'domain %(name)s %(type)s auto created by dns update',
         dict(name=zone, type=domain_type),
        )
    ws_send('pdns_domains_change')

    # SOA
    data = {
        "name": zone,
        "type": "SOA",
        "content": config_get("dns_default_soa_content", config_get("dbopensvc", "")),
        "ttl": 86400,
        "domain_id": domain_id,
        "change_date": int((datetime.datetime.now()-datetime.datetime(1970, 1, 1)).total_seconds())
    }
    dbdns.records.insert(**data)

    fmt = 'record %(name)s %(type)s %(content)s created in domain %(domain)s'
    d = dict(name=data["name"], type=data["type"], content=data["content"], domain=zone)
    _log('dns.records.create', fmt, d)
    ws_send('pdns_records_change')

def sanitize_dns_name(name):
    name = name.lower()
    name = re.sub(r'[^a-z0-9\.]', '-', name)
    return name

def get_dns_domain(zone):
    q = dbdns.domains.name == zone
    return dbdns(q).select().first()

def raise_on_error(response):
    if response.errors:
        s = ", ".join(map(lambda x: ": ".join(x), response.errors.items()))
        raise Exception(s)

def addr_from_reverse(name):
    addr = name.split(".in-addr.")[0]
    v = addr.split(".")
    v.reverse()
    addr = ".".join(v)
    return addr

def dns_record_responsible(row, current={}):
    if not hasattr(auth.user, "node_id") and "Manager" in user_groups():
        return
    group_ids = user_group_ids()
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
        addr = addr_from_reverse(name)
    else:
        raise Exception("Manager privilege required to handle the %s record type"%t)
    sql = """
      select networks.id from
      networks, auth_group, auth_membership, auth_user where
        auth_group.id in (%(group_ids)s) and
        auth_group.role=networks.team_responsible and
        inet_aton("%(addr)s") >= inet_aton(networks.begin) and
        inet_aton("%(addr)s") <= inet_aton(networks.end)
    """ % dict(addr=addr, user_id=auth.user_id,
               group_ids = ','.join([repr(str(gid)) for gid in group_ids]))
    networks = db.executesql(sql)
    if len(networks) > 0:
        return

    sql = """
      select network_segments.id from
      network_segments, networks, network_segment_responsibles, auth_group, auth_membership, auth_user where
        network_segment_responsibles.group_id in (%(group_ids)s) and
        network_segments.id=network_segment_responsibles.seg_id and
        inet_aton("%(addr)s") >= inet_aton(network_segments.seg_begin) and
        inet_aton("%(addr)s") <= inet_aton(network_segments.seg_end)
    """ % dict(addr=addr, user_id=auth.user_id,
               group_ids = ','.join([repr(str(gid)) for gid in group_ids]))
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
        ws_send('pdns_records_change')
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
          "A websocket event is sent to announce the change in the dns domains table.",
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
             'domain %(name)s %(type)s created',
             dict(name=row.name, type=row.type),
            )
        ws_send('pdns_domains_change')
        return rest_get_dns_domain().handler(row.id)


#
class rest_post_dns_domain(rest_post_handler):
    def __init__(self):
        desc = [
          "Change a dns domain.",
          "The user must be in the DnsManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the dns domains table.",
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
        ws_send('pdns_domains_change')
        return rest_get_dns_domain().handler(domain_id)


#
class rest_post_dns_records(rest_post_handler):
    def __init__(self):
        desc = [
          "Create a dns record.",
          "The user must be responsible for the ip address network or segment.",
          "The user must be in the DnsOperator privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the dns records table.",
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
        ws_send('pdns_records_change')
        ret = rest_get_dns_record().handler(row.id)
        ret["info"] = fmt % d
        return ret

#
class rest_post_dns_services_records(rest_post_handler):
    def __init__(self):
        desc = [
          "Create a dns record for a service.",
          "A service app responsible must be responsible for the ip address network or segment.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the dns records table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X POST -d name="mynode.opensvc.com" -d "rid=ip#0" -d content="1.2.3.4" https://%(collector)s/init/rest/api/dns/services/records""",
        ]
        rest_post_handler.__init__(
          self,
          path="/dns/services/records",
          tables=["records"],
          dbo=dbdns,
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if auth.user.svc_id is None:
            raise Exception("Only authenticated services can use this handler")
        if "content" not in vars:
            raise Exception("The 'content' key is mandatory")

        # short record name
        name = auth.user.svcname.split(".")[0]
        instance_name = vars.get("name")
        if instance_name and len(instance_name) > 0:
            name = name + "-" + instance_name
        name = sanitize_dns_name(name)

        # domain
        zone = config_get("dns_managed_zone", "opensvc")
        zone = zone.rstrip(".")
        zone = auth.user.svc_app + "." + zone
        zone = sanitize_dns_name(zone)
        domain = get_dns_domain(zone)
        if domain is None:
            create_zone(zone)
            domain = get_dns_domain(zone)
        if domain is None:
            raise Exception("failed to create the %s zone" % zone)

        # full record name
        name = name + "." + zone

        # content
        content = vars["content"]

        # record type
        if ":" in content:
            record_type = "AAAA"
        elif content.count(".") == 3:
            record_type = "A"
        else:
            raise Exception("invalid content type %s" % str(content))

        # record ttl
        if "ttl" in vars:
            ttl = vars["ttl"]
        else:
            ttl = config_get("dns_default_ttl", 120)

        data = {
            "name": name,
            "type": record_type,
            "content": content,
            "ttl": ttl,
            #"prio": 0,
            "domain_id": domain.id,
            "change_date": int((datetime.datetime.now()-datetime.datetime(1970, 1, 1)).total_seconds())
        }
        dns_record_responsible(data)

        q = dbdns.records.id > 0
        q &= dbdns.records.name == data["name"]
        q &= dbdns.records.domain_id == data["domain_id"]
        row = dbdns(q).select().first()

        if row is not None:
            response = dbdns(q).validate_and_update(**data)
            op = "change"
        else:
            response = dbdns.records.validate_and_insert(**data)
            op = "create"
        raise_on_error(response)
        row = dbdns(q).select().first()

        fmt = 'record %(name)s %(type)s %(content)s %(op)sd in domain %(domain)s'
        d = dict(name=row.name, type=row.type, op=op, content=row.content, domain=str(row.domain_id))
        _log('dns.records.'+op, fmt, d)
        ws_send('pdns_records_change')
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
          "A websocket event is sent to announce the change in the dns records table.",
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
        ws_send('pdns_records_change')
        return rest_get_dns_record().handler(record_id)


#
class rest_delete_dns_domains(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete dns domains.",
          "Also delete dns records in this domain.",
          "The user must be in the DnsManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the dns domains table.",
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
          "A websocket event is sent to announce the change in the dns domains table.",
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
        ws_send('pdns_domains_change')
        ws_send('pdns_records_change')
        return dict(info="Domain %s %s deleted" % (row.name, row.type))

#
class rest_delete_dns_records(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete dns records.",
          "The user must be responsible for the ip address network or segment.",
          "The user must be in the DnsOperator privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the dns records table.",
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
          "A websocket event is sent to announce the change in the dns records table.",
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
        ws_send('pdns_records_change')
        return dict(info="Record %s %s %s deleted" % (row.name, row.type, row.content))

