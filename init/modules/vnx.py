import os

class Vnx(object):
    def __init__(self, dir=None):
        if dir is None:
            return
        self.dir = dir
        self.name = os.path.basename(dir)
        self.lines = self.readfile("getall").split('\n')
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
        self.pool = []
        for i, line in enumerate(self.lines):
            if line.startswith("Model:"):
                self.model = line.split(':')[1].strip()
            elif line.startswith("Revision:"):
                self.firmware = line.split(':')[1].strip()
            elif line.startswith("SP UID:"):
                self.ports.append(line.split(': ')[1].strip().replace(":","").lower())
            elif line.startswith("SP Memory:"):
                try:
                    self.cache = int(line.split(':')[-1].strip())
                except:
                    continue
            elif line.startswith("All logical Units Information"):
                self.load_lu_detail(i+2)
            #elif line.startswith("--- Pool Detail Information"):
            #    self.load_pool_detail(i+1)

    def load_lu_detail(self, i):
        vdisk = {}
        for line in self.lines[i:]:
            if line.startswith("Device Map:"):
                self.vdisk.append(vdisk)
            if line.startswith("---"):
                return
            if line.startswith("LOGICAL UNIT NUMBER"):
                vdisk = {}
                vdisk["lunid"] = line.split()[-1].strip()
            if line.startswith("UID:"):
                vdisk["wwid"] = line.replace("UID:","").strip().replace(":","").lower()
            if line.startswith("Name  "):
                vdisk["name"] = line[4:].strip()
            if line.startswith("LUN Capacity(Megabytes):"):
                vdisk["size"] = int(line.split(':')[-1].strip())
            if line.startswith("Pool Name"):
                vdisk["disk_group"] = line.split(':')[-1].strip()
            if line.startswith("RAID Type:"):
                vdisk["raid"] = line.split(':')[-1].strip().lower()

    def load_pool_detail(self, i):
        pool = {}
        for line in self.lines[i:]:
            if line.startswith("---"):
                self.pool.append(pool)
                return
            if line.startswith("Pool Name"):
                pool["name"] = line.split(':')[-1].strip()
            if line.startswith("Pool Capacity"):
                s = line.split(':')[-1].strip()
                s = s[:s.index('G')]
                pool["size"] = int(float(s)*1024)
            if line.startswith("Used Pool Capacity"):
                s = line.split(':')[-1].strip()
                s = s[:s.index('G')]
                pool["used"] = int(float(s)*1024)
            if line.startswith("Free Pool Capacity"):
                s = line.split(':')[-1].strip()
                s = s[:s.index('G')]
                pool["free"] = int(float(s)*1024)

    def __str__(self):
        s = "name: %s\n" % self.name
        s += "model: %s\n" % self.model
        s += "cache: %d\n" % self.cache
        s += "firmware: %s\n" % self.firmware
        for port in self.ports:
            s += "port: %s\n" % port
        for d in self.pool:
            s += "pool %s: size %d MB, used %d MB, free %d MB\n"%(d['name'], d['size'], d['used'], d['free'])
        for d in sorted(self.vdisk, lambda x, y: cmp(x["name"], y["name"])):
            s += "vdisk %s (%s): size %s MB\n"%(d['name'], d['wwid'], str(d['size']))
        return s


def get_vnx(dir=None):
    try:
        return Vnx(dir)
    except:
        return None

import sys
def main():
    s = Vnx(sys.argv[1])
    print s

if __name__ == "__main__":
    main()

