#
class rest_get_packages_diff(rest_get_handler):
    def __init__(self):
        desc = [
          "List differences in installed packages between nodes.",
        ]
        params = {
          "node_ids": {
            "desc": "A comma-separated list of node ids to compare",
          },
          "svc_ids": {
            "desc": "A comma-separated list of service whose nodes to compare",
          },
          "encap": {
            "desc": "A boolean that can be set alongside svc_ids to indicate we want to compare services encap nodes instead of their hosts.",
          }
        }
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/packages/diff?node_ids=5c977246-0562-11e6-8c70-7e9e6cf13c8a,5c977246-0563-11e6-8c70-7e9e6cf13c8a",
        ]

        rest_get_handler.__init__(
          self,
          path="/packages/diff",
          desc=desc,
          params=params,
          examples=examples,
        )

    def handler(self, **vars):
        if "node_ids" in vars:
            node_ids = vars.get("node_ids", "").split(",")
        elif "nodes_ids[]" in vars:
            node_ids = vars.get("node_ids[]", [])
            if not type(node_ids) == list:
                node_ids = [node_ids]
        else:
            node_ids = []

        if "svc_ids" in vars:
            svc_ids = vars.get("svc_ids", "").split(",")
        elif "svc_ids[]" in vars:
            svc_ids = vars.get("svc_ids[]", [])
            if not type(svc_ids) == list:
                svc_ids = [svc_ids]
        else:
            svc_ids = []

        encap = vars.get("encap", False)
        data = lib_packages_diff(node_ids=node_ids, svc_ids=svc_ids, encap=encap)
        return dict(data=data, meta={"node_ids": node_ids})

