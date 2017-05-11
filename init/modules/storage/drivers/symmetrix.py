import json
from core.exceptions import Error, RequestDataError

class Driver(object):
    def __init__(self, storage):
        self.storage = storage

    def map_disk(self):
        mappings = self.storage.get_mappings()
        if len(mappings) == 0:
            raise Error("No mappings found.")
        cmd = [
            "array", "add", "map",
            "-a", self.storage.request_data["array"]["array_name"],
            "--dev", self.storage.request_data["dev"],
        ] + mappings
        if "dg_name" in self.storage.request_data and self.storage.request_data["dg_name"] != "":
            cmd += ["--srp", self.storage.request_data["dg_name"]]
        if "slo" in self.storage.request_data and self.storage.request_data["slo"] != "":
            cmd += ["--slo", self.storage.request_data["slo"]]
        ret = self.storage.proxy_action(" ".join(cmd))
        data = {}
        try:
            return json.loads(ret["data"][0]["stdout"])
        except ValueError:
            Error("unexpected add disk output format: %s" % ret)


    def add_disk(self):
        mappings = self.storage.get_mappings()
        if len(mappings) == 0:
            raise Error("No mappings found.")
        cmd = [
            "array", "add", "disk",
            "-a", self.storage.request_data["array"]["array_name"],
            "--name", self.storage.disk_name(),
            "--size", self.storage.request_data["size"]
        ] + mappings
        if "dg_name" in self.storage.request_data and self.storage.request_data["dg_name"] != "":
            cmd += ["--srp", self.storage.request_data["dg_name"]]
        if "slo" in self.storage.request_data and self.storage.request_data["slo"] != "":
            cmd += ["--slo", self.storage.request_data["slo"]]
        if "srdf" in self.storage.request_data and self.storage.request_data["srdf"] == "Yes":
            cmd += ["--srdf"]
        if "rdfg" in self.storage.request_data:
            cmd += ["--rdfg", self.storage.request_data["rdfg"]]
        ret = self.storage.proxy_action(" ".join(cmd))
        data = {}
        try:
            return json.loads(ret["data"][0]["stdout"])
        except ValueError:
            Error("unexpected add disk output format: %s" % ret)

    def resize_disk(self):
        if "disk_devid" not in self.storage.request_data:
            raise RequestDataError("The 'disk_devid' key is mandatory in request data")
        cmd = [
            "array", "resize", "disk",
            "-a", self.storage.request_data["array"]["array_name"],
            "--dev", self.storage.request_data["disk_devid"],
            "--size", self.storage.request_data["size"]
        ]
        ret = self.storage.proxy_action(" ".join(cmd))

    def del_disk(self):
        if "disk_devid" not in self.storage.request_data:
            raise RequestDataError("The 'disk_devid' key is mandatory in request data")
        self._del_disk(self.storage.request_data["disk_devid"], self.storage.request_data["array"]["array_name"])

    def _del_disk(self, dev, array_name):
        cmd = [
            "array", "del", "disk",
            "-a", array_name,
            "--dev", dev,
        ]
        ret = self.storage.proxy_action(" ".join(cmd))

	if "stdout" not in ret["data"][0]:
            return

        data = json.loads(ret["data"][0]["stdout"])
        if "driver_data" in data and "rdf" in data["driver_data"] and "Remote" in data["driver_data"]["rdf"]:
            self._del_disk(data["driver_data"]["rdf"]["dev_name"], data["driver_data"]["rdf"]["remote_symid"])


