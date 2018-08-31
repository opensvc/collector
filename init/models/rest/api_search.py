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
        searches = [
            {
                "key": "filtersets",
                "fn": lib_search_fset,
                "otype": "fset",
            },
            {
                "key": "arrays",
                "fn": lib_search_arrays,
                "otype": "array",
            },
            {
                "key": "disks",
                "fn": lib_search_disk,
                "otype": "disk",
            },
            {
                "key": "apps",
                "fn": lib_search_app,
                "otype": "app",
            },
            {
                "key": "services",
                "fn": lib_search_service,
                "otype": "svc",
            },
            {
                "key": "vms",
                "fn": lib_search_vm,
                "otype": "vm",
            },
            {
                "key": "ips",
                "fn": lib_search_ip,
                "otype": "ip",
            },
            {
                "key": "nodes",
                "fn": lib_search_node,
                "otype": "node",
            },
            {
                "key": "users",
                "fn": lib_search_user,
                "otype": "user",
            },
            {
                "key": "groups",
                "fn": lib_search_group,
                "otype": "group",
            },
            {
                "key": "privileges",
                "fn": lib_search_priv,
                "otype": "priv",
            },
            {
                "key": "tags",
                "fn": lib_search_tag,
                "otype": "tag",
            },
            {
                "key": "safe_files",
                "fn": lib_search_safe_file,
                "otype": "safe",
            },
            {
                "key": "forms",
                "fn": lib_search_form,
                "otype": "form",
            },
            {
                "key": "charts",
                "fn": lib_search_chart,
                "otype": "chart",
            },
            {
                "key": "metrics",
                "fn": lib_search_metric,
                "otype": "metric",
            },
            {
                "key": "reports",
                "fn": lib_search_report,
                "otype": "report",
            },
            {
                "key": "modulesets",
                "fn": lib_search_modulesets,
                "otype": "modset",
            },
            {
                "key": "rulesets",
                "fn": lib_search_rulesets,
                "otype": "rset",
            },
            {
                "key": "prov_templates",
                "fn": lib_search_prov_templates,
                "otype": "prov",
            },
            {
                "key": "docker_registries",
                "fn": lib_search_docker_registries,
                "otype": "docker",
            },
            {
                "key": "docker_repositories",
                "fn": lib_search_docker_repositories,
                "otype": "docker",
            },
            {
                "key": "variables",
                "fn": lib_search_variables,
                "otype": "var",
            },
        ]
        for search in searches:
            if otype is None or otype == search["otype"]:
                try:
                    data[search["key"]] = search["fn"](substring, limit)
                except Exception as exc:
                    data[search["key"]] = {
                        "total": 0,
                        "data": [],
                        "fmt": {},
                        "elapsed": 0,
                        "error": str(exc),
                    }
        return dict(data=data)

