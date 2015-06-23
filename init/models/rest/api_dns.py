from gluon.dal import smart_query

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

