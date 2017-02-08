#!/usr/bin/python

"""
This script is called from the add/del/resize collector forms.
It uses the collector API to fetch information about the
array (model, proxy, quota), to queue commands on the proxy
node and to store form results.

It implements a disk naming policy.

It format commands for the OpenSVC agent array drivers.

resize disk form data:
{
    "svcname": "testdisk",
    "svc_id": "9385a587-7c96-4caf-88aa-9ddf4779d467",
    "svc_app": "test",
    "action": "resize_disk",
    "disk": "testdisk_0",
    "array_id": "555",
    "disk_name": "testdisk_0",
    "disk_group": "default",
    "size": "+1g"
}

add disk form data:
{
    "svcname": "colrec",
    "svc_id": "10c1d1ba-051e-46de-9a93-88d419473935",
    "svc_app": "test",
    "app_id": "2",
    "array_name": "xtremio-cot",
    "array_id": "555",
    "dg_name": "default",
    "dg_id": 3,
    "size": 1073741824
}
"""

from __future__ import print_function
import sys
import os
import requests
import json
import time

os.environ["https_proxy"] = ""
os.environ["http_proxy"] = ""

try:
    import requests
except:
    print("This feature requires the python requests module", file=sys.stderr)
    sys.exit(1)

try:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    pass

from core.exceptions import Error, RequestError, RequestDataError
from core.size import convert_size
from config import *

class Storage(object):
    def __init__(self):
        try:
            mod = __import__("policies.disk.naming."+DISK_NAMING_POLICY,
                             fromlist=["policies.disk.naming"])
        except NameError:
            mod = __import__("policies.disk.naming.simple",
                             fromlist=["policies.disk.naming"])
        self.disk_naming_policy_driver = mod.DiskNamingPolicy(self)

    def select_driver(self):
        array_model = self.request_data["array"]["array_model"].lower()
        try:
            mod = __import__("drivers."+array_model, fromlist=["drivers"])
            self.driver = mod.Driver(self)
        except ImportError:
            raise Error("driver %s not implemented" % array_model)

    def validate_request_data(self):
        if "svcname" not in self.request_data:
            raise RequestDataError("The 'svcname' key is mandatory in request data")
        if "svc_id" not in self.request_data:
            raise RequestDataError("The 'svc_id' key is mandatory in request data")
        if "array_id" not in self.request_data:
            raise RequestDataError("The 'array_id' key is mandatory in request data")

    @staticmethod
    def req_strings(data):
        if not isinstance(data, dict):
            return
        if "error" in data:
            raise RequestError(data["error"])
        if "info" in data:
            print(data["info"])

    def put(self, path, **kwargs):
        response = requests.put(
            API_URL+path,
            auth=(API_USERNAME, API_PASSWORD),
            verify=False,
            **kwargs
        )
        try:
            ret = json.loads(response.content)
        except ValueError:
            raise RequestError(response)
        self.req_strings(ret)
        return ret

    def post(self, path, **kwargs):
        response = requests.post(
            API_URL+path,
            auth=(API_USERNAME, API_PASSWORD),
            verify=False,
            **kwargs
        )
        try:
            ret = json.loads(response.content)
        except ValueError:
            raise RequestError(response)
        self.req_strings(ret)
        return ret

    def get(self, path, **kwargs):
        response = requests.get(
            API_URL+path,
            auth=(API_USERNAME, API_PASSWORD),
            verify=False,
            **kwargs
        )
        try:
            ret = json.loads(response.content)
        except ValueError:
            raise RequestError(response)
        self.req_strings(ret)
        return ret

    def put_result(self, result):
        path = "/form_output_results/%d" % self.results["results_id"]
        data = self.put(path, data={
            "result": json.dumps(result),
            "output_id": self.output_id
        })

    def get_nodes(self):
        path = "/services/%s/nodes" % self.request_data["svc_id"]
        data = self.get(path, params={
            "limit": 0,
            "props": "nodes.node_id,nodes.nodename",
        })
        if len(data["data"]) == 0:
            raise Error("no nodes found for this service")
        for i, node in enumerate(data["data"]):
            print("node", node["nodename"], "targets:")
            node["targets"] = self.get_targets(node["node_id"])
            data["data"][i] = node
        return data["data"]

    def get_targets(self, node_id):
        targets = {}
        path = "/nodes/%s/targets" % node_id
        data = self.get(path, params={
            "limit": 0,
            "meta": 0,
            "props": "stor_zone.tgt_id,stor_zone.hba_id",
        })
        for entry in data["data"]:
            hba_id = entry["hba_id"]
            if hba_id not in targets:
                targets[hba_id] = []
            targets[hba_id].append(entry["tgt_id"])
        for hba_id in targets:
            print(" hba ", hba_id, "targets:", ", ".join(targets[hba_id]))
        return targets

    def get_array_targets(self):
        path = "/arrays/%s/targets" % self.request_data["array_id"]
        data = self.get(path, params={"limit": 0})
        if len(data["data"]) == 0:
            raise Error("array targets not found")
        print("detected array targets:")
        for entry in data["data"]:
            print("  ", entry["array_tgtid"])
        return data["data"]

    def get_array(self):
        path = "/arrays/%s" % self.request_data["array_id"]
        data = self.get(path, params={"limit": 0})
        if len(data["data"]) == 0:
            raise Error("array not found")
        print("detected array:", data["data"][0]["array_name"], "model", data["data"][0]["array_model"])
        return data["data"][0]

    def get_proxy(self):
        path = "/arrays/%s/proxies" % self.request_data["array_id"]
        data = self.get(path, params={
            "meta": 0,
            "limit": 0,
            "props": "nodes.nodename,nodes.node_id",
        })
        if len(data["data"]) == 0:
            raise Error("array proxy not found")
        print("detected array proxy:", data["data"][0]["nodename"])
        return data["data"][0]

    def get_quota(self):
        if "app_id" not in self.request_data:
            raise RequestDataError("The 'app_id' key is mandatory in request data")
        if "dg_id" not in self.request_data:
            raise RequestDataError("The 'dg_id' key is mandatory in request data")
        path = "/apps/%s/quotas" % self.request_data["app_id"]
        data = self.get(path, params={
            "filters": [
                "dg_id=%s" % self.request_data["dg_id"],
            ],
            "limit": 0,
        })
        if len(data["data"]) == 0:
            raise Error("quota not found")
        return data["data"][0]

    def get_disks(self):
        data = self.get("/disks", params={
            "meta": 0,
            "limit": 0,
            "props": "diskinfo.disk_name",
            "filters": ["diskinfo.array_id="+str(self.request_data["array"]["id"])],
        })
        return data["data"]

    def validate_quota(self, need):
        if "size" not in self.request_data:
            raise RequestDataError("The 'size' key is mandatory in request data")
        quota = self.request_data["quota"]["quota"]
        quota_used = self.request_data["quota"]["quota_used"]
        quota_free = quota - quota_used
        size_mb = convert_size(need, _to="MB")
        missing = size_mb - quota_free
        if size_mb > quota_free:
            raise Error("insufficient quota: %d MB free, missing %d MB" %
                        (quota_free, missing))

    def validate_free(self, need):
        dg_free = self.request_data["quota"]["dg_free"]
        size_mb = convert_size(need, _to="MB")
        missing = size_mb - dg_free
        if size_mb > dg_free:
            raise Error("insufficient space in disk group: %d MB free, missing"
                        " %d MB" % (dg_free, missing))

    def disk_name(self):
        return self.disk_naming_policy_driver.disk_name()

    def get_mappings(self):
        mappings = []
        array_targets = set([entry["array_tgtid"] for entry in self.request_data["array"]["targets"]])
        for node in self.request_data["nodes"]:
            for hba_id, targets in node["targets"].items():
                targets = set(targets) & array_targets
                mapping = hba_id + ":" + ",".join(targets)
                mappings += ["--mappings", mapping]
        return mappings

    def proxy_action(self, command):
        return self.node_action(self.request_data["proxy"], command)

    def node_action(self, node, command):
        print("run command on node", node["nodename"], ":", command)
        data = {
            "node_id": node["node_id"],
            "action": command,
        }
        ret = self.put("/actions", data=data)
        action_id = ret["data"][0]["id"]
        for _ in range(ACTION_TIMEOUT):
            path = "/actions/%d" % action_id
            ret = self.get(path)
            if ret["data"][0]["status"] == "T":
                if ret["data"][0]["stderr"] != "":
                    print(ret["data"][0]["stderr"], file=sys.stderr)
                if ret["data"][0]["ret"] != 0:
                    raise Error("command failed")
                return ret
            time.sleep(1)
        raise Error("timeout waiting for node action %d" % action_id)

    def add_disk(self):
        self.request_data["nodes"] = self.get_nodes()
        self.request_data["disks"] = self.get_disks()
        self.request_data["quota"] = self.get_quota()
        self.request_data["array"]["targets"] = self.get_array_targets()
        self.validate_quota(self.request_data["size"])
        self.validate_free(self.request_data["size"])
        data = self.driver.add_disk()
        self.put_result(data)

    def del_disk(self):
        self.driver.del_disk()

    def resize_disk(self):
        self.driver.resize_disk()

    def main(self):
        """
        argv1: the json-formatted form data.

        argv2: the id of the form output this script is run for.

        argv3: the results structure containing a reference to where to store
               out own results and where to access the results of the previous
               form outputs.
        """
        self.request_data = json.loads(sys.argv[1])
        self.output_id = sys.argv[2]
        self.results = json.loads(sys.argv[3])

        self.validate_request_data()
        self.request_data["array"] = self.get_array()
        self.request_data["proxy"] = self.get_proxy()

        self.select_driver()

        if self.request_data["action"] == "add_disk":
            self.add_disk()
        elif self.request_data["action"] == "del_disk":
            self.del_disk()
        elif self.request_data["action"] == "resize_disk":
            self.resize_disk()
        else:
            raise Error("unsupported action: %s" % self.request_data["action"])

if __name__ == "__main__":
    try:
        storage = Storage()
        storage.main()
    except (RequestDataError, RequestError, Error) as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

