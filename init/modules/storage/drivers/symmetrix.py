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
            raise Error("unexpected add disk output format: %s" % ret)


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
        if "srdf" in self.storage.request_data and self.storage.request_data["srdf"] in ("Yes", True):
            cmd += ["--srdf"]
            if "rdfg" in self.storage.request_data:
                cmd += ["--rdfg", self.storage.request_data["rdfg"]]
        ret = self.storage.proxy_action(" ".join(cmd))
        data = {}
        try:
            return json.loads(ret["data"][0]["stdout"])
        except ValueError:
            raise Error("unexpected add disk output format: %s" % ret)

    def resize_disk(self):
        if "disk_devid" not in self.storage.request_data:
            raise RequestDataError("The 'disk_devid' key is mandatory in request data")
        return self._resize_disk(
            self.storage.request_data["disk_devid"],
            self.storage.request_data["array"]["array_name"],
            self.storage.request_data["size"]
        )

    def _resize_disk(self, dev, array_name, size):
        cmd = [
            "array", "resize", "disk",
            "-a", array_name,
            "--dev", dev,
            "--size", size,
        ]
        proxy = self.storage.get_proxy(array_name)
        ret = self.storage.proxy_action(" ".join(cmd), proxy=proxy)

	if "stdout" not in ret["data"][0]:
            return

        data = json.loads(ret["data"][0]["stdout"])
        results = [data]
        if "driver_data" in data and "rdf" in data["driver_data"] and "Remote" in data["driver_data"]["rdf"] and data["driver_data"].get("pair_deleted"):
            local_rdf_data = data["driver_data"]["rdf"]["Local"]
            remote_rdf_data = data["driver_data"]["rdf"]["Remote"]
            srdf_mode = data["driver_data"]["rdf"]["Mode"]["mode"]
            _data = self._resize_disk(remote_rdf_data["dev_name"], remote_rdf_data["remote_symid"], size)
            if isinstance(_data, list):
                results += _data
            if srdf_mode == "Synchronous":
                srdf_mode = "sync"
            else:
                raise Error("unknown srdf mode: %s" % srdf_mode)
            self._createpair(
                array_name=array_name,
                dev=dev,
                rdev=remote_rdf_data["dev_name"],
                rdfg=local_rdf_data["ra_group_num"],
                srdf_mode=srdf_mode,
                srdf_type=local_rdf_data["type"]
            )
        return results

    def _createpair(self, array_name=None, dev=None, rdev=None, rdfg=None, srdf_type=None, srdf_mode="sync", invalidate=None):
        if array_name is None:
            raise Error("_createpair: array_name is not set")
        if dev is None:
            raise Error("_createpair: dev is not set")
        if rdev is None:
            raise Error("_createpair: rdev is not set")
        if srdf_type is None:
            raise Error("_createpair: srdf_type is not set")
        pair = ":".join([dev, rdev])
        cmd = [
            "array", "createpair",
            "-a", array_name,
            "--pair", pair,
            "--rdfg", rdfg,
            "--srdf-type", srdf_type,
            "--srdf-mode", srdf_mode,
        ]
        if invalidate in ("R1", "R2"):
            cmd += ["--invalidate", invalidate]
        ret = self.storage.proxy_action(" ".join(cmd))

	if "stdout" not in ret["data"][0]:
            return


    def del_disk(self):
        if "disk_devid" not in self.storage.request_data:
            raise RequestDataError("The 'disk_devid' key is mandatory in request data")
        return self._del_disk(self.storage.request_data["disk_devid"], self.storage.request_data["array"]["array_name"])

    def _del_disk(self, dev, array_name):
        cmd = [
            "array", "del", "disk",
            "-a", array_name,
            "--dev", dev,
        ]
        proxy = self.storage.get_proxy(array_name)
        ret = self.storage.proxy_action(" ".join(cmd), proxy=proxy)

	if "stdout" not in ret["data"][0]:
            return

        data = json.loads(ret["data"][0]["stdout"])
        results = [data]
        if "driver_data" in data and "rdf" in data["driver_data"] and "Remote" in data["driver_data"]["rdf"]:
            remote_rdf_data = data["driver_data"]["rdf"]["Remote"]
            _data = self._del_disk(remote_rdf_data["dev_name"], remote_rdf_data["remote_symid"])
            if isinstance(_data, list):
                results += _data
        return results


