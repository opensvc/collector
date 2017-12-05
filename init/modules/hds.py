import os
import json

class Hds(object):
    def __init__(self, dir=None):
        if dir is None:
            return
        self.dir = dir
        self.name = os.path.basename(dir)
        self.load()

    def readfile(self, fname):
        fpath = os.path.join(self.dir, fname)
        with open(fpath, "r") as fp:
            return json.load(fp)

    def load(self):
        self.array_name = self.name
        self.cache = 0
        self.ports = []
        self.vdisk = []
        self.pool = {}
        self.load_array()
        self.load_pool()
        self.load_port()
        self.load_lu()

    def load_array(self):
        data = self.readfile("array")[0]
        self.model = data["arrayType"]
        self.firmware = data["controllerVersion"]

    def load_lu(self):
        data = self.readfile("lu")
        for lu in data:
            vdisk = {}
            wwid = lu["objectID"].split(".")[2:]
            vdisk["wwid"] = '.'.join(wwid)
            vdisk["name"] = lu["displayName"]
            vdisk["size"] = int(lu["capacityInKB"])//1024
            vdisk["alloc"] = int(lu["consumedCapacityInKB"])//1024
            if "label" in lu:
                vdisk["label"] = lu["label"]
            pool_id = lu["dpPoolID"]
            if pool_id in self.pool:
                vdisk["disk_group"] = self.pool[pool_id]['name']
                vdisk["raid"] = self.pool[pool_id]['raid']
            else:
                vdisk["disk_group"] = pool_id
                vdisk["raid"] = ""
            self.vdisk.append(vdisk)

    def load_pool(self):
        data = self.readfile("pool")
        for p in data:
            pool = {}
            if "name" not in p:
                continue
            pool["name"] = p["name"]
            pool["id"] = p["poolID"]
            pool["size"] = int(p["capacityInKB"])//1024
            pool["free"] = int(p["freeCapacityInKB"])//1024
            pool["used"] = pool["size"] - pool["free"]
            pool["raid"] = p["raidLevel"]
            self.pool[pool["id"]] = pool

    def load_port(self):
        data = self.readfile("port")
        for port in data:
            self.ports.append(port["worldWidePortName"].replace('.','').lower())

    def __str__(self):
        s = "name: %s\n" % self.name
        s += "model: %s\n" % self.model
        s += "cache: %d\n" % self.cache
        s += "firmware: %s\n" % self.firmware
        s += "ports: %s\n" % ', '.join(self.ports)
        for i, d in self.pool.items():
            s += "pool %s: id %s size %d MB, used %d MB, free %d MB\n"%(d['name'], d["id"], d['size'], d['used'], d['free'])
        for d in self.vdisk:
            s += "vdisk %s (%s): size %s MB alloc %s MB dg %s raid %s label %s\n"%(d['name'], d['wwid'], str(d['size']), str(d.get('alloc', '')), d['disk_group'], d['raid'], d.get('label', 'n/a'))
        return s


def get_hds(dir=None):
    try:
        s = Hds(dir)
        return s
    except Exception as e:
        print e

import sys
def main():
    s = Hds(sys.argv[1])
    print s

if __name__ == "__main__":
    main()

