from core.exceptions import Error

class DiskNamingPolicy(object):
    def __init__(self, storage):
        self.storage = storage

    def disk_name(self):
        if "svcname" in self.storage.request_data:
            name = self.storage.request_data["svcname"] + "_"
        elif "nodename" in self.storage.request_data:
            name = self.storage.request_data["nodename"] + "_"
        else:
            raise Error("simple disk naming error: 'svcname' or 'nodename' not found in request data")
        name = name.replace("-", "_")
        disk_names = [r["disk_name"] for r in self.storage.request_data["disks"]]
        inc = 0
        while True:
            _name = name + str(inc)
            if _name not in disk_names:
                return _name
            inc += 1
        raise Error("unable to find a disk name")


