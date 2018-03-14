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
          "limit": {
             "desc": "Limit the search resultset to <n>. Honored only if 'in' is also set.",
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
        if otype is not None:
            limit = vars.get("limit", max_search_result)
        else:
            limit = max_search_result
        if substring is None:
            return dict(data=data)
        substring = "%" + substring.lower().replace("osvc_comp_", "") + "%"
        if otype is None or otype == "fset":
            data["filtersets"] = lib_search_fset(substring, limit)
        if otype is None or otype == "array":
            data["arrays"] = lib_search_arrays(substring, limit)
        if otype is None or otype == "disk":
            data["disks"] = lib_search_disk(substring, limit)
        if otype is None or otype == "app":
            data["apps"] = lib_search_app(substring, limit)
        if otype is None or otype == "svc":
            data["services"] = lib_search_service(substring, limit)
        if otype is None or otype == "vm":
            data["vms"] = lib_search_vm(substring, limit)
        if otype is None or otype == "ip":
            data["ips"] = lib_search_ip(substring, limit)
        if otype is None or otype == "node":
            data["nodes"] = lib_search_node(substring, limit)
        if otype is None or otype == "user":
            data["users"] = lib_search_user(substring, limit)
        if otype is None or otype == "group":
            data["groups"] = lib_search_group(substring, limit)
        if otype is None or otype == "priv":
            data["privileges"] = lib_search_priv(substring, limit)
        if otype is None or otype == "tag":
            data["tags"] = lib_search_tag(substring, limit)
        if otype is None or otype == "safe":
            data["safe_files"] = lib_search_safe_file(substring, limit)
        if otype is None or otype == "form":
            data["forms"] = lib_search_form(substring, limit)
        if otype is None or otype == "chart":
            data["charts"] = lib_search_chart(substring, limit)
        if otype is None or otype == "metric":
            data["metrics"] = lib_search_metric(substring, limit)
        if otype is None or otype == "report":
            data["reports"] = lib_search_report(substring, limit)
        if otype is None or otype == "modset":
            data["modulesets"] = lib_search_modulesets(substring, limit)
        if otype is None or otype == "rset":
            data["rulesets"] = lib_search_rulesets(substring, limit)
        if otype is None or otype == "prov":
            data["prov_templates"] = lib_search_prov_templates(substring, limit)
        if otype is None or otype == "docker":
            data["docker_registries"] = lib_search_docker_registries(substring, limit)
            data["docker_repositories"] = lib_search_docker_repositories(substring, limit)
        if otype is None or otype == "var":
            data["variables"] = lib_search_variables(substring, limit)
        return dict(data=data)

