import os

class Netapp(object):
    def __init__(self, dir=None):
        if dir is None:
            return
        self.model = None
        self.dir = dir
        self.ports = []
        self.dgs = []
        self.luns = []
        self.vol_aggr = {}
        self.get_controller()
        self.get_ports()
        self.get_dgs()
        self.get_luns()

    def readfile(self, fname):
        fpath = os.path.join(self.dir, fname)
        with open(fpath, 'r') as f:
            buff = f.read()
        return buff

    def get_controller(self):
        l = self.readfile('sysconfig_a').split("\n")
        if len(l) < 1:
            return
        for line in l:
            if "NetApp Release" in line:
                v = line.split()
                self.firmwareversion = v[2]
                self.mode = v[3].strip(":")
            elif "Memory Size:" in line:
                self.cache = line.split()[-2]
            elif "System Serial Number:" in line:
                v = line.replace("System Serial Number:", "").split()
                self.serial = v[0]
                self.name = v[1].strip("()")
            elif "Model Name:" in line and self.model is None:
                self.model = "NetApp " + line.replace("Model Name:", "").strip()
            elif "System ID:" in line:
                v = line.split("(")
                node1 = v[1].split(")")[0]
                node2 = v[2].split(")")[0]
                v = [node1, node2]
                v.sort()
                self.array_name = "-".join(v)

    def get_ports(self):
        l = self.readfile('fcp_show_adapter').split("\n")
        for line in l:
            if "FC Portname:" not in line:
                continue
            v = line.split()
            wwn = v[-1].strip("()")
            self.ports.append(wwn)

    def get_dgs(self):
        l = self.readfile('aggr_show_space').split("\n")
        for i, line in enumerate(l):
            if line.startswith("Aggregate") and line.count("'") == 2:
                d = {}
                d["name"] = self.name + "." + line.split("'")[1]
            elif line.startswith("    Total space"):
                v = l[i+1].split()
                d["size"] = int(v[0].replace("MB",""))
            elif line.startswith("Total space"):
                v = line.split()
                d["free"] = int(v[-1].replace("MB",""))
                d["used"] = d["size"] - d["free"]
                self.dgs.append(d)
            elif line.count("MB") == 2:
                v = line.split()
                if len(v) == 4:
                    self.vol_aggr[v[0]] = d["name"]

    def to_hex(self, s):
        lst = []
        for ch in s:
            hv = hex(ord(ch)).replace('0x', '')
            if len(hv) == 1:
                hv = '0'+hv
            lst.append(hv)
        return reduce(lambda x,y:x+y, lst)

    def get_luns(self):
        l = self.readfile('lun_show_v').split("\n")
        for line in l:
            line = line.strip()
            if line.startswith("/vol/"):
                d = {}
                v = line.split()
                d["id"] = v[0]
                d["size"] = int(v[2].strip("()"))/1024/1024
                volume = v[0].split("/")[2]
                if volume in self.vol_aggr:
                    d["aggr"] = self.vol_aggr[volume]
                else:
                    d["aggr"] = ""
            elif line.startswith("Occupied Size:"):
                d["alloc"] = int(line.split()[-1].strip("()"))/1024/1024
            elif line.startswith("Serial#:"):
                serial = line.split()[-1]
                d["serial"] = serial
                d["wwid"] = self.to_hex(serial)
                if self.mode == "7-Mode":
                    d["wwid"] = "60a98000" + d["wwid"]
                elif self.mode == "C-Dot":
                    d["wwid"] = "600a0980" + d["wwid"]
            elif line.startswith("Comment:") and line.count('"') == 2:
                d["name"] = line.split('"')[1]
            elif line.startswith("Creation Time:"):
                self.luns.append(d)


    def __str__(self):
        s = "name: %s\n" % self.name
        s += "array_name: %s\n" % self.array_name
        s += "model: %s\n" % self.model
        s += "serial: %s\n" % self.serial
        s += "cache: %s\n" % self.cache
        s += "firmwareversion: %s\n" % self.firmwareversion
        s += "ports:\n"
        for port in self.ports:
            s += "  %s\n" % port
        for dg in self.dgs:
            s += "dg %s: free %d MB used %d MB size %d MB\n"%(dg['name'], dg['free'], dg['used'], dg['size'])
        for d in self.luns:
            s += "lun %s: size %d MB alloc %d MB id %s comment %s aggr %s\n"%(d['wwid'], d['size'], d["alloc"], d["id"], d.get("name", "(none)"), d['aggr'])
        return s


def get_netapp(dir=None):
    try:
        return Netapp(dir)
    except:
        return None

import sys
def main():
    s = Netapp(sys.argv[1])
    print s

if __name__ == "__main__":
    main()

