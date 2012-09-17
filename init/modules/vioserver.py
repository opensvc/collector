import os

class VioServer(object):
    def __init__(self, dir=None):
        if dir is None:
            return
        self.dir = dir
        self.name = os.path.basename(dir)
        self.load_controller()
        self.load_bootinfo()
        self.load_pdisk()
        self.load_vdisk()

    def readfile(self, fname):
        fpath = os.path.join(self.dir, fname)
        with open(fpath, 'r') as f:
            buff = f.read()
        return buff

    def load_controller(self):
        self.array_name = self.name
        l = self.readfile('lsfware').strip().split()
        self.modelnumber = "vioserver"
        self.controllermainmemory = 0
        self.firmwareversion = l[2]

        lines = self.readfile('lsmap').split('\n')
        self.vpartid = set([])
        for line in lines:
            l = line.split(':')
            if len(l) < 3:
                continue
            self.vpartid.add(int(l[2], 16))
        self.vpartid = list(self.vpartid)

    def load_bootinfo(self):
        self.disk_size = {}
        lines = self.readfile('bootinfo').split('\n')
        for line in lines:
            l = line.split()
            if len(l) != 2:
                continue
            self.disk_size[l[0]] = l[1]

    def load_pdisk(self):
        self.load_lsdevvpd()
        self.load_devsize()

    def load_devsize(self):
        lines = self.readfile('devsize').split('\n')
        for line in lines:
            l = line.split()
            if len(l) != 2:
                continue
            if l[0] not in self.pdisk:
                continue
            self.pdisk[l[0]]['size'] = l[1]

    def load_lsdevvpd(self):
        self.pdisk = {}
        lines = self.readfile('lsdevvpd').split('\n')

        def get_val(line):
            s = line[36:].strip()
            return s

        for line in lines:
            if len(line) == 0:
                continue
            elif line[0] != " ":
                disk = line
            elif "Manufacturer" in line:
                manufacturer = get_val(line)
            elif "Model" in line:
                model = get_val(line)
            elif "Serial" in line:
                serial = get_val(line)
                if model == "OPEN-V":
                    serial = serial.split()[-1]
                    serial = int(serial, 16)
            elif "(Z1)" in line:
                dev = get_val(line)
                if model == "OPEN-V":
                    dev = dev.split()[0]
                    dev = int(dev, 16)
                    wwid = '.'.join((str(serial), str(dev)))
                    self.pdisk[disk] = {'dev': disk, 'wwid': wwid, 'vendor': manufacturer, 'model': model}
            elif "(Z9)" in line:
                wwid = get_val(line)
                self.pdisk[disk] = {'dev': disk, 'wwid': wwid, 'vendor': manufacturer, 'model': model}

    def load_vdisk(self):
        """vhost0:U7778.23X.0682A6A-V1-C11:0x00000006:vd_sys_ene:Available:0x8100000000000000:hdisk1:U78A5.001.WIH6A76-P1-C11-L1-T1-W50060E80164DAB01-L0:false"""
        self.vdisk = []
        lines = self.readfile('lsmap').split('\n')
        for line in lines:
            l = line.split(':')
            if len(l) < 4:
                continue
            svsa, svsa_physloc, vpartid = l[0:3]
            svsa_physloc = svsa_physloc.split('-')[0]
            vpartid = int(vpartid, 16)
            l = l[3:]
            while len(l) > 0:
                vtd, status, lun, backingdev, physloc, mirrored = l[0:6]
                if backingdev in self.disk_size:
                    size = self.disk_size[backingdev]
                else:
                    size = 0
                if backingdev in self.pdisk:
                    backingdevid = self.pdisk[backingdev]['wwid']
                else:
                    backingdevid = backingdev

                self.vdisk.append({"did": '-'.join((svsa_physloc, "V%d"%vpartid, "L%s"%lun.replace("0x",""))),
                                   "vtd": vtd,
                                   "status": status,
                                   "lun": lun,
                                   "backingdev": backingdev,
                                   "backingdevid": backingdevid,
                                   "physloc": physloc,
                                   "mirrored": mirrored,
                                   "size": size})
                if len(l) < 12:
                    break
                l = l[6:]

    def __str__(self):
        s = "name: %s\n" % self.name
        s += "modelnumber: %s\n" % self.modelnumber
        s += "controllermainmemory: %d\n" % self.controllermainmemory
        s += "firmwareversion: %s\n" % self.firmwareversion
        s += "vpartid: %s\n"%str(self.vpartid)
        for d in self.vdisk:
            s += "vdisk %s: size %s MB\n"%(d['did'], str(d['size']))
        for d in self.pdisk.values():
            s += "pdisk %s: size %s MB\n"%(d['wwid'], str(d['size']))
        return s


def get_vioserver(dir=None):
    try:
        return VioServer(dir)
    except:
        return None

import sys
def main():
    s = VioServer(sys.argv[1])
    print s

if __name__ == "__main__":
    main()

