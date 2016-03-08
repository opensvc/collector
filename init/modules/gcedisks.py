import os
import json

class GceDisks(object):
    def __init__(self, dir=None):
        if dir is None:
            return
        self.dir = dir
        self.name = os.path.basename(dir)
        self.disks = []
        self.load_quotas()
        self.load_disks()
        self.load_snapshots()

    def readfile(self, fname):
        fpath = os.path.join(self.dir, fname)
        with open(fpath, 'r') as f:
            buff = f.read()
        return buff

    def load_quotas(self):
        buff = self.readfile('quotas')
        data = json.loads(buff)
        self.dg = {}
        self.wwpn = []
        for region in data:
            dgname = region["name"]
            for quota in region["quotas"]:
                if quota["metric"] == "DISKS_TOTAL_GB":
                    self.dg[dgname] = quota
            i = region["selfLink"].index("/projects")
            self.wwpn.append(region["selfLink"][i:].replace("/projects", "").replace("/regions", ""))

    def load_disks(self):
        buff = self.readfile('disks')
        data = json.loads(buff)
        if len(data) == 0:
            return
        for d in data:
            region = self.get_region(d)
            i = d["selfLink"].index("/projects")
            disk_id = d["selfLink"][i:].replace("/projects", "").replace("/zones", "").replace("/disks", "")
            _d = {
              "disk_id": disk_id,
              "disk_name": d["name"],
              "disk_devid": d["id"],
              "disk_size": int(d["sizeGb"])*1024,
              "disk_alloc": int(d["sizeGb"])*1024,
              "disk_group": region,
              "disk_arrayid": self.name,
              "disk_raid": d["type"],
            }
            self.disks.append(_d)

    def load_snapshots(self):
        buff = self.readfile('snapshots')
        data = json.loads(buff)
        if len(data) == 0:
            return
        for d in data:
            region = self.get_region(d)
            i = d["selfLink"].index("/projects")
            disk_id = d["selfLink"][i:].replace("/projects", "").replace("/zones", "").replace("/disks", "")
            _d = {
              "disk_id": disk_id,
              "disk_name": d["name"],
              "disk_devid": d["id"],
              "disk_size": int(d["diskSizeGb"])*1024,
              "disk_alloc": int(d["storageBytes"])/1024/1024,
              "disk_group": region,
              "disk_arrayid": self.name,
              "disk_raid": "snap of "+d["sourceDisk"],
            }
            self.disks.append(_d)

    def get_region(self, data):
        l = data["selfLink"].split("/")
        try:
            i = l.index("zones")
        except:
            return "global"
        zone = l[i+1]
        region = "-".join(zone.split("-")[:-1])
        return region

    def __str__(self):
        s = json.dumps({
          "wwpn": self.wwpn,
          "dg": self.dg,
          "disks": self.disks
        }, indent=4)
        return s


def get_gcedisks(dir=None):
    try:
        return GceDisks(dir)
    except:
        return None

import sys
def main():
    s = GceDisks(sys.argv[1])
    print s

if __name__ == "__main__":
    main()

