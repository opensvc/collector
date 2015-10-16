#
class rest_get_search(rest_get_table_handler):
    def __init__(self):
        desc = [
          "Search the collector data for objects with name containing the substring.",
        ]
        examples = [
          """# curl -u %(email)s -o- https://%(collector)s/init/rest/api/search?substring=manager""",
        ]
        params = {
          "substring": {
             "desc": "The substring to search.",
          },
        }
        rest_get_table_handler.__init__(
          self,
          path="/search",
          desc=desc,
          params=params,
          examples=examples,
        )

    def handler(self, **vars):
        data = {}
        substring = vars.get("substring")
        if substring is None:
            return dict(data=data)
        substring = "%" + substring + "%"
        data["filtersets"] = lib_search_fset(substring)
        data["disks"] = lib_search_disk(substring)
        data["apps"] = lib_search_app(substring)
        data["services"] = lib_search_service(substring)
        data["vms"] = lib_search_vm(substring)
        data["ips"] = lib_search_ip(substring)
        data["nodes"] = lib_search_node(substring)
        data["users"] = lib_search_user(substring)
        data["groups"] = lib_search_group(substring)
        data["safe_files"] = lib_search_safe_file(substring)
        return dict(data=data)

