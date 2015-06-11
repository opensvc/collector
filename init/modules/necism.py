import os

class NecIsm(object):
    def __init__(self, dir=None):
        if dir is None:
            return
        self.dir = dir
        self.name = os.path.basename(dir)
        self.lines = self.readfile("all").split('\n')
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
        self.model = None
        self.product = None
        for i, line in enumerate(self.lines):
            if line.startswith("Vendor ID") and self.model is None:
                self.model = line.split(':')[1].strip()
            elif line.startswith("Product ID") and self.product is None:
                self.product = " "+line.split(':')[1].strip()
                self.model += self.product
            elif line.startswith("Product FW Revision"):
                self.firmware = line.split(':')[1].strip()
            elif line.startswith("World Wide Name"):
                self.wwn = line.split(':')[1].strip().lower()
                self.wwn_prefix = self.wwn[4:]
            elif line.startswith("WWPN"):
                self.ports.append(line.split(':')[1].strip().lower())
            elif line.startswith("Cache Module"):
                try:
                    self.cache += int(line.split(':')[-1].strip().replace('GB',''))*1024
                except:
                    continue
            elif line.startswith("--- LD Detail Information"):
                self.load_ld_detail(i+1)
            elif line.startswith("--- Pool Detail Information"):
                self.load_pool_detail(i+1)

    def load_ld_detail(self, i):
        vdisk = {}
        for line in self.lines[i:]:
            if line.startswith("---"):
                self.vdisk.append(vdisk)
                return
            if line.startswith("LDN(h)"):
                vdisk["lunid"] = line.split(':')[-1].strip()
                vdisk["wwid"] = self.wwn_prefix + vdisk["lunid"]
            if line.startswith("LD Name"):
                vdisk["name"] = line.split(':')[-1].strip()
            if line.startswith("LD Capacity"):
                s = line.split(':')[-1].strip()
                if 'M' in s:
                    s = s[:s.index('M')]
                    vdisk["size"] = int(float(s))
                elif 'G' in s:
                    s = s[:s.index('G')]
                    vdisk["size"] = int(float(s)*1024)
                elif 'T' in s:
                    s = s[:s.index('T')]
                    vdisk["size"] = int(float(s)*1024*1024)
            if line.startswith("Pool Name"):
                vdisk["disk_group"] = line.split(':')[-1].strip()
            if line.startswith("RaidType"):
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
        s += "wwn_prefix: %s\n" % self.wwn_prefix
        for d in self.pool:
            s += "pool %s: size %d MB, used %d MB, free %d MB\n"%(d['name'], d['size'], d['used'], d['free'])
        for d in self.vdisk:
            s += "vdisk %s (%s): size %s MB\n"%(d['name'], d['wwid'], str(d['size']))
        return s


def get_necism(dir=None):
    try:
        return NecIsm(dir)
    except:
        return None

import sys
def main():
    s = NecIsm(sys.argv[1])
    print s

if __name__ == "__main__":
    main()

