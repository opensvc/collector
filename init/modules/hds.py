import os

class Hds(object):
    def __init__(self, dir=None):
        if dir is None:
            return
        self.dir = dir
        self.name = os.path.basename(dir)
        self.lines = self.readfile("lu").split('\n')
        self.load()

    def readfile(self, fname):
        fpath = os.path.join(self.dir, fname)
        with open(fpath, 'r') as f:
            buff = f.read()
        return buff

    def load(self):
        self.array_name = self.name
        self.cache = 0
        self.ports = []
        self.vdisk = []
        self.pool = {}
        self.load_pool()
        self.load_port()
        self.load_lu()

    def load_lu(self):
        n = -1
        for i, line in enumerate(self.lines):
            if "serialNum" in line and self.name in line:
                break
        for j, line in enumerate(self.lines[i+1:]):
            if "serialNum" in line:
                n = i+j
                break
        for _i, line in enumerate(self.lines[i-5:n]):
            if line.startswith("  arrayType"):
                self.model = line.split('=')[1].strip()
            elif line.startswith("  controllerVersion"):
                self.firmware = line.split('=')[1].strip()
            elif line.endswith("An instance of LogicalUnit"):
                self._load_lu(i-5+_i+1,n)

    def _load_lu(self, i, n):
        vdisk = {}
        for line in self.lines[i:n]:
            if line.startswith("      objectID"):
                wwid = line.split('=')[1].strip().split('.')[2:]
                vdisk["wwid"] = '.'.join(wwid)
            if line.startswith("      displayName"):
                vdisk["name"] = line.split('=')[-1].strip()
            if line.startswith("      capacityInKB"):
                s = line.split('=')[-1].strip().replace(',','')
                vdisk["size"] = int(s)//1024
            if line.strip().startswith("consumedSizeInKB"):
                s = line.split('=')[-1].strip().replace(',','')
                vdisk["alloc"] = int(s)//1024
            if line.strip().startswith("label="):
                s = line.split('=')[-1].strip()
                vdisk["label"] = s
            if line.startswith("      dpPoolID"):
                pool_id = line.split('=')[-1].strip()
                if pool_id in self.pool:
                    vdisk["disk_group"] = self.pool[pool_id]['name']
                    vdisk["raid"] = self.pool[pool_id]['raid']
                else:
                    vdisk["disk_group"] = pool_id
                    vdisk["raid"] = ""
            if line.endswith("An instance of LogicalUnit"):
                self.vdisk.append(vdisk)
                return
        if vdisk != {}:
            self.vdisk.append(vdisk)

    def load_pool(self):
        lines = self.readfile("pool").split('\n')
        pool = {}
        n = -1
        for i, line in enumerate(lines):
            if "An instance of Pool" in line:
                break
        for j, line in enumerate(lines[i:]):
            if "An instance of Pool" in line:
                pool = {}
            if line.startswith("      name="):
                pool["name"] = line.split('=')[-1].strip()
            elif line.startswith("      poolID"):
                pool["id"] = line.split('=')[-1].strip()
            elif line.startswith("      capacityInKB"):
                s = line.split('=')[-1].strip().replace(',','')
                pool["size"] = int(s)//1024
            elif line.startswith("      freeCapacityInKB"):
                s = line.split('=')[-1].strip().replace(',','')
                pool["free"] = int(s)//1024
                pool["used"] = pool["size"] - pool["free"]
            elif line.startswith("      raidLevel"):
                pool["raid"] = line.split('=')[-1].strip()
                self.pool[pool["id"]] = pool

    def load_port(self):
        lines = self.readfile("port").split('\n')
        n = -1

        for i, line in enumerate(lines):
            if "serialNum" in line and self.name in line:
                break
        for j, line in enumerate(lines[i+1:]):
            if "serialNum" in line:
                n = i+j
                break
        for line in lines[i+1:n]:
            if line.startswith("      worldWidePortName"):
                self.ports.append(line.split('=')[-1].strip().replace('.','').lower())

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

