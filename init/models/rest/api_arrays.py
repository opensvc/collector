
#
class rest_get_arrays(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List storage arrays.",
        ]
        examples = [
          """# curl -u %(email)s -o- "https://%(collector)s/init/rest/api/arrays?props=array_name&query=array_model contains hitachi"""
        ]
        q = db.stor_array.id > 0
        rest_get_table_handler.__init__(
          self,
          path="/arrays",
          tables=["stor_array"],
          q=q,
          desc=desc,
          examples=examples,
        )


#
class rest_get_array(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display a storage array properties.",
          "<id> can be either the id or the array name.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/arrays/myarray?props=array_name,array_model"
        ]
        rest_get_line_handler.__init__(
          self,
          path="/arrays/<id>",
          tables=["stor_array"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.stor_array.array_name == id
        n = db(q).count()
        if n == 0:
            try: id = int(id)
            except: return dict(data=[])
            q = db.stor_array.id == id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_array_diskgroups(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List storage array diskgroups.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/arrays/myarray/diskgroups"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/arrays/<id>/diskgroups",
          tables=["stor_array_dg"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.stor_array.array_name == id
        try:
            array_id = db(q).select().first().id
        except:
            array_id = int(id)
        q = db.stor_array_dg.array_id == array_id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_array_proxies(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List storage array proxies.",
          "Proxies are OpenSVC agent inventoring the array.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/arrays/myarray/proxies"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/arrays/<id>/proxies",
          tables=["stor_array_proxy"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.stor_array.array_name == id
        try:
            array_id = db(q).select().first().id
        except:
            array_id = int(id)
        q = db.stor_array_proxy.array_id == array_id
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_array_targets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List storage array target ports.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/arrays/myarray/targets"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/arrays/<id>/targets",
          tables=["stor_array_tgtid"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.stor_array.array_name == id
        try:
            array_id = db(q).select().first().id
        except:
            array_id = int(id)
        q = db.stor_array_tgtid.array_id == array_id
        self.set_q(q)
        return self.prepare_data(**vars)


