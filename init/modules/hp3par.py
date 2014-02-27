import sys
import os
import json

class Hp3par(object):
    def __init__(self, dir=None):
        if dir is None:
            return
        self.dir = dir
        self.name = os.path.basename(dir)
        self.keys = ["showvv", "showcpg", "showsys", "shownode", "showport"]
        for key in self.keys:
            setattr(self, key, self.readfile(key))
        self.ports = []
        for d in self.showport:
            self.ports.append(d["Port_WWN"])

    def readfile(self, fname):
        fpath = os.path.join(self.dir, fname)
        with open(fpath, 'r') as f:
            data = json.loads(f.read())
        return data

    def __str__(self):
        s = "name: %s\n" % self.name
        s += "modelnumber: %s\n" % self.showsys[0]['Serial']
        s += "controllermainmemory: %d\n" % 0
        s += "firmwareversion: %s\n" % ""
        s += "ports: %s\n"%','.join(self.ports)
        for cpg in self.showcpg:
            s += "dg %s\n"%(cpg['Name'])
        for d in self.showvv:
            s += "vdisk %s: vsize %s MB\n"%(d['Name'], str(d['VSize_MB']))
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

