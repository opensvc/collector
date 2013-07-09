import sys
import os
import json

class Hp3par(object):
    def __init__(self, dir=None):
        if dir is None:
            return
        self.ports = []
        self.dir = dir
        self.name = os.path.basename(dir)
        self.keys = ["volumes", "vluns", "cpgs"]
        for key in self.keys:
            setattr(self, key, self.readfile(key))

    def readfile(self, fname):
        fpath = os.path.join(self.dir, fname)
        with open(fpath, 'r') as f:
            data = json.loads(f.read())
        return data

    def to_mb(self, size):
        if "TB" in size:
            size = float(size.replace("TB", "")) * 1024 * 1024
        elif "GB" in size:
            size = float(size.replace("GB", "")) * 1024
        elif "MB" in size:
            size = float(size.replace("MB", ""))
        else:
            size = 0
        return size

    def to_gb(self, size):
        if "TB" in size:
            size = float(size.replace("TB", "")) * 1024
        elif "GB" in size:
            size = float(size.replace("GB", ""))
        elif "MB" in size:
            size = float(size.replace("MB", "")) // 1024
        else:
            size = 0
        return size

    def volumes():
        self.volumes = self.readfile("volumes")

    def __str__(self):
        s = "name: %s\n" % self.name
        s += "modelnumber: %s\n" % ""
        s += "controllermainmemory: %d\n" % ""
        s += "firmwareversion: %s\n" % ""
        s += "ports: %s\n"%','.join(self.ports)
        #for dg in self.dg:
        #    s += "dg %s: free %s MB\n"%(dg['name'], str(dg['free_capacity']))
        #    s += "dg %s: total %s MB\n"%(dg['name'], str(dg['capacity']))
        #for d in self.vdisk:
        #    s += "vdisk %s: size %s MB\n"%(d['vdisk_UID'], str(d['capacity']))
        return s


def get_hp3par(dir=None):
    try:
        return Hp3par(dir)
    except Exception as e:
        print e
        return None

def main():
    s = Hp3par(sys.argv[1])
    print s

if __name__ == "__main__":
    main()

