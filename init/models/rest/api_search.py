#
class rest_get_search(rest_get_handler):
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
          "in": {
             "desc": "Limit the search to the selected object type: fset, disk, app, svc, vm, ip, node, user, group, safe, form, rset, modset, prov, docker",
          },
        }
        rest_get_handler.__init__(
          self,
          path="/search",
          desc=desc,
          params=params,
          examples=examples,
        )

    def handler(self, **vars):
        data = {}
        substring = vars.get("substring")
        otype = vars.get("in")
        if substring is None:
            return dict(data=data)
        substring = "%" + substring + "%"
        if otype is None or otype == "fset":
            data["filtersets"] = lib_search_fset(substring)
        if otype is None or otype == "array":
            data["arrays"] = lib_search_arrays(substring)
        if otype is None or otype == "disk":
            data["disks"] = lib_search_disk(substring)
        if otype is None or otype == "app":
            data["apps"] = lib_search_app(substring)
        if otype is None or otype == "svc":
            data["services"] = lib_search_service(substring)
        if otype is None or otype == "vm":
            data["vms"] = lib_search_vm(substring)
        if otype is None or otype == "ip":
            data["ips"] = lib_search_ip(substring)
        if otype is None or otype == "node":
            data["nodes"] = lib_search_node(substring)
        if otype is None or otype == "user":
            data["users"] = lib_search_user(substring)
        if otype is None or otype == "group":
            data["groups"] = lib_search_group(substring)
        if otype is None or otype == "safe":
            data["safe_files"] = lib_search_safe_file(substring)
        if otype is None or otype == "form":
            data["forms"] = lib_search_form(substring)
        if otype is None or otype == "chart":
            data["charts"] = lib_search_chart(substring)
        if otype is None or otype == "metric":
            data["metrics"] = lib_search_metric(substring)
        if otype is None or otype == "report":
            data["reports"] = lib_search_report(substring)
        if otype is None or otype == "modset":
            data["modulesets"] = lib_search_modulesets(substring)
        if otype is None or otype == "rset":
            data["rulesets"] = lib_search_rulesets(substring)
        if otype is None or otype == "prov":
            data["prov_templates"] = lib_search_prov_templates(substring)
        if otype is None or otype == "docker":
            data["docker_registries"] = lib_search_docker_registries(substring)
            data["docker_repositories"] = lib_search_docker_repositories(substring)
        if otype is None or otype == "var":
            data["variables"] = lib_search_variables(substring)
        return dict(data=data)

