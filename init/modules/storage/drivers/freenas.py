import json
from core.exceptions import Error, RequestDataError

class Driver(object):
    def __init__(self, storage):
        self.storage = storage

    def add_disk(self):
        if "dg_name" not in self.storage.request_data:
            raise RequestDataError("The 'dg_name' key is mandatory in request data")
        mappings = self.storage.get_mappings()
        if len(mappings) == 0:
            raise Error("No mappings found.")
        cmd = [
            "array", "add", "iscsi", "zvol",
            "-a", self.storage.request_data["array"]["array_name"],
            "--volume", self.storage.request_data["dg_name"],
            "--name", self.storage.disk_name(),
            "--size", self.storage.request_data["size"]
        ] + mappings
        ret = self.storage.proxy_action(" ".join(cmd))
        data = {}
        try:
            return json.loads(ret["data"][0]["stdout"])
        except ValueError:
            Error("unexpected add volume output format: %s" % ret)

    def resize_disk(self):
        if "disk_name" not in self.storage.request_data:
            raise RequestDataError("The 'disk_name' key is mandatory in request data")
        cmd = [
            "array", "resize", "zvol",
            "-a", self.storage.request_data["array"]["array_name"],
            "--name", self.storage.request_data["disk_name"],
            "--size", self.storage.request_data["size"]
        ]
        ret = self.storage.proxy_action(" ".join(cmd))

    def del_disk(self):
        if "disk_name" not in self.storage.request_data:
            raise RequestDataError("The 'disk_name' key is mandatory in request data")
        cmd = [
            "array", "del", "iscsi", "zvol",
            "-a", self.storage.request_data["array"]["array_name"],
            "--name", self.storage.request_data["disk_name"]
        ]
        ret = self.storage.proxy_action(" ".join(cmd))


