import os

class IbmSvc(object):
    def __init__(self, dir=None):
        if dir is None:
            return
        self.dir = dir
        self.name = os.path.basename(dir)
        self.controller()
        self.disk_group()
        self.vdisk()

    def readfile(self, fname):
        fpath = os.path.join(self.dir, fname)
        with open(fpath, 'r') as f:
            buff = f.read()
        return buff

    def readlines(self, fname, sep=':'):
        lines = self.readfile(fname).split('\n')
        if len(lines) < 2:
            return
        _l = []
        titles = lines[0].split(sep)
        for line in lines[1:]:
            h = {}
            l = line.split(sep)
            if len(l) != len(titles):
                continue
            for i, t in enumerate(titles):
                h[t] = l[i]
            _l.append(h)
        del lines
        return _l

    def controller(self):
        l = self.readlines('lscluster')
        if len(l) < 1:
            return
        clu1 = l[0]
        self.array_name = clu1['name']
        modelnumber = self.readfile('svc_product_id')
        self.modelnumber = modelnumber.strip()
        self.controllermainmemory = 0
        self.firmwareversion = ""

        l = self.readlines('lsfabric')
        ports = set([])
        for line in l:
            ports.add(line['local_wwpn'])
        self.ports = list(ports)

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

    def disk_group(self):
        """
id:name:status:mdisk_count:vdisk_count:capacity:extent_size:free_capacity:virtual_capacity:used_capacity:real_capacity:overallocation:warning:easy_tier:easy_tier_status
0:STP_V7KDev_A60R5_01:online:7:219:22.90TB:256:3.24TB:26.71TB:19.17TB:19.62TB:116:0:auto:inactive
1:STP_IMAGE_MIG:online:0:0:0:256:0:0.00MB:0.00MB:0.00MB:0:80:auto:inactive
2:STP_CX4240_R5_01:online:14:26:19.26TB:256:11.83TB:10.81TB:7.22TB:7.43TB:56:80:auto:inactive
        """
        self.dg = self.readlines('lsmdiskgrp')
        for dg in self.dg:
            dg["capacity"] = self.to_mb(dg["capacity"])
            dg["free_capacity"] = self.to_mb(dg["free_capacity"])

    def vdisk(self):
        """
id:name:IO_group_id:IO_group_name:status:mdisk_grp_id:mdisk_grp_name:capacity:type:FC_id:FC_name:RC_id:RC_name:vdisk_UID:fc_map_count:copy_count:fast_write_state:se_copy_count
0:VD_CLU_ESXEIFF_lun12:0:io_grp0:online:0:STP_V7KDev_A60R5_01:512.00GB:striped:::::600507680280809AB0000000000000DF:0:1:empty:1
1:VD_vin0002_lun3:0:io_grp0:online:0:STP_V7KDev_A60R5_01:32.00GB:striped:::::600507680280809AB000000000000001:0:1:empty:1
2:VD_vin0002_lun1:0:io_grp0:online:0:STP_V7KDev_A60R5_01:1.00GB:striped:::::600507680280809AB000000000000002:0:1:empty:1
3:VD_vin0002_lun2:0:io_grp0:online:0:STP_V7KDev_A60R5_01:1.00GB:striped:::::600507680280809AB000000000000003:0:1:not_empty:1
        """
        self.vdisk = self.readlines('lsvdisk')
        for vdisk in self.vdisk:
            vdisk["capacity"] = self.to_mb(vdisk["capacity"])

    def __str__(self):
        s = "name: %s\n" % self.name
        s += "modelnumber: %s\n" % self.modelnumber
        s += "controllermainmemory: %d\n" % self.controllermainmemory
        s += "firmwareversion: %s\n" % self.firmwareversion
        s += "ports: %s\n"%','.join(self.ports)
        for dg in self.dg:
            s += "dg %s: free %s MB\n"%(dg['name'], str(dg['free_capacity']))
            s += "dg %s: total %s MB\n"%(dg['name'], str(dg['capacity']))
        for d in self.vdisk:
            s += "vdisk %s: size %s MB\n"%(d['vdisk_UID'], str(d['capacity']))
        return s


def get_ibmsvc(dir=None):
    try:
        return IbmSvc(dir)
    except:
        return None

import sys
def main():
    s = IbmSvc(sys.argv[1])
    print s

if __name__ == "__main__":
    main()

