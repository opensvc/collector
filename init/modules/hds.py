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
        for i, line in enumerate(self.lines):
            if line.startswith("  arrayType"):
                self.model = line.split('=')[1].strip()
            elif line.startswith("  controllerVersion"):
                self.firmware = line.split('=')[1].strip()
            elif line.endswith("An instance of LogicalUnit"):
                self.load_lu(i+1)

    def load_lu(self, i):
        vdisk = {}
        for line in self.lines[i:]:
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
            if line.startswith("      arrayGroupName"):
                vdisk["disk_group"] = line.split('=')[-1].strip()
                if vdisk["disk_group"] in self.pool:
                    vdisk["raid"] = self.pool[vdisk["disk_group"]]['raid']
            if line.endswith("An instance of LogicalUnit"):
                self.vdisk.append(vdisk)
                return
        if vdisk != {}:
            self.vdisk.append(vdisk)

    def load_pool(self):
        lines = self.readfile("arraygroup").split('\n')
        pool = {}
        for line in lines:
            if line.startswith("      dpPoolID"):
                self.pool[pool["name"]] = pool
                pool = {}
            elif line.startswith("      displayName"):
                pool["name"] = line.split('=')[-1].strip()
            elif line.startswith("      totalCapacity"):
                s = line.split('=')[-1].strip().replace(',','')
                pool["size"] = int(s)//1024
            elif line.startswith("      freeCapacity"):
                s = line.split('=')[-1].strip().replace(',','')
                pool["free"] = int(s)//1024
                pool["used"] = pool["size"] - pool["free"]
            elif line.startswith("      raidType"):
                pool["raid"] = line.split('=')[-1].strip()

    def load_port(self):
        lines = self.readfile("port").split('\n')
        n = -1

        for i, line in enumerate(lines):
            if "serialNum" in line and self.name in line:
                break
        for j, line in enumerate(lines[i+1:]):
            if "serialNum" in line:
                n = j
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
            s += "pool %s: size %d MB, used %d MB, free %d MB\n"%(d['name'], d['size'], d['used'], d['free'])
        for d in self.vdisk:
            s += "vdisk %s (%s): size %s MB alloc %s MB raid %s label %s\n"%(d['name'], d['wwid'], str(d['size']), str(d.get('alloc', '')), d['raid'], d.get('label', 'n/a'))
        return s


def get_hds(dir=None):
    try:
        return Hds(dir)
    except:
        return None

import sys
def main():
    s = Hds(sys.argv[1])
    print s

if __name__ == "__main__":
    main()

