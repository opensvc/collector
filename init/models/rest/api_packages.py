#
class rest_get_packages_diff(rest_get_handler):
    def __init__(self):
        desc = [
          "List differences in installed packages between nodes.",
        ]
        params = {
          "nodenames": {
            "desc": "A comma-separated list of nodes to compare",
          },
          "svcnames": {
            "desc": "A comma-separated list of service whose nodes to compare",
          },
          "encap": {
            "desc": "A boolean that can be set alongside svcnames to indicate we want to compare services encap nodes instead of their hosts.",
          }
        }
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/packages/diff?nodenames=node1,node2",
        ]

        rest_get_handler.__init__(
          self,
          path="/packages/diff",
          desc=desc,
          params=params,
          examples=examples,
        )

    def handler(self, **vars):
        nodenames = vars.get("nodenames", "").split(",")
        svcnames = vars.get("svcnames", "").split(",")
        encap = vars.get("encap", False)
        data = lib_packages_diff(nodenames=nodenames, svcnames=svcnames, encap=encap)
        nodenames = sorted(list(set([ r["pkg_nodename"] for r in data ])))
        return dict(data=data, meta={"nodenames": nodenames})

