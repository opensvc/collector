import os

class IbmDs(object):
    def __init__(self, dir=None):
        if dir is None:
            return
        self.dir = dir
        self.name = os.path.basename(dir)
        self.readfile("combo")
        self.parse_disk_group()
        self.parse_vdisk()
        self.parse_ioport()
        self.parse_si()
        self.parse_rank()
        self.set_vdisk_wwn()
        self.set_vdisk_raid()

    def readfile(self, fname):
        fpath = os.path.join(self.dir, fname)
        with open(fpath, 'r') as f:
            buff = f.read()
        self.lines = buff.replace('dscli> ', '').split('\n')

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

    def getblock(self, n):
        begin = None
        end = None
        met = 0
        for i, line in enumerate(self.lines):
             if line.startswith("==="):
                 met += 1
                 if met < n:
                     continue
                 if begin is None:
                     begin = i-1
                 else:
                     end = i-1
                     break
        if end is None:
           end = i
        return self.lines[begin:end]

    def parseblock(self, n):
        data = []
        lines = self.getblock(n)
        if len(lines) < 3:
            return
        headers = lines[0].split(',')
        headers_multipliers = []
        for i, h in enumerate(headers):
            if '^' not in h:
                headers_multipliers.append(None)
                continue
            x = h[h.index('^')+1:h.index('B)')]
            x = int(x)
            headers_multipliers.append((2**x)/1024/1024)
            stripped_header = headers[i][:headers[i].index(' (')]
            while stripped_header in headers:
                stripped_header += "_"
            headers[i] = stripped_header
        for line in lines[2:]:
            d = {}
            l = line.split(',')
            for i, key in enumerate(headers):
                if headers_multipliers[i] is not None:
                    try:
                        d[key] = int(float(l[i]) * headers_multipliers[i])
                    except:
                        d[key] = l[i]
                else:
                    d[key] = l[i]
            data.append(d)
        return data

    def parse_disk_group(self):
        """
Name,ID,stgtype,rankgrp,status,availstor (2^30B),%allocated,available,reserved,numvols
======================================================================================
pool_perf0,P0,fb,0,exceeded,6168,88,6168,0,460
pool_perf1,P1,fb,1,exceeded,6170,88,6170,0,460
pool_perf_basse0,P2,fb,0,below,20494,0,20494,0,0
pool_perf_basse1,P3,fb,1,below,20494,0,20494,0,0
        """
        self.dg = self.parseblock(1)
        self.dgnames = {}
        for dg in self.dg:
            self.dgnames[dg['ID']] = dg['Name']

    def parse_vdisk(self):
        """
dscli> Name,ID,accstate,datastate,configstate,deviceMTM,datatype,extpool,cap (2^30B),cap (10^9B),cap (blocks)
======================================================================================================
perftest0000,0000,Online,Normal,Normal,2107-900,FB 512,P0,100.0,-,209715200
perftest0001,0001,Online,Normal,Normal,2107-900,FB 512,P0,100.0,-,209715200
perftest0002,0002,Online,Normal,Normal,2107-900,FB 512,P0,100.0,-,209715200
perftest0003,0003,Online,Normal,Normal,2107-900,FB 512,P0,100.0,-,209715200
        """
        self.vdisk = self.parseblock(2)
        for vdisk in self.vdisk:
             vdisk['PoolName'] = self.dgnames[vdisk['extpool']]

    def parse_ioport(self):
        """
ID    WWPN             State  Type             topo     portgrp
===============================================================
I0030 50050763040317EA Online Fibre Channel-SW SCSI-FCP 0
I0031 50050763040357EA Online Fibre Channel-SW SCSI-FCP 0
I0032 50050763040397EA Online Fibre Channel-SW SCSI-FCP 0
I0033 500507630403D7EA Online Fibre Channel-SW SCSI-FCP 0
        """
        self.ioport = self.parseblock(3)

    def parse_si(self):
        """
Name ID               Storage Unit     Model WWNN             State  ESSNet Volume Group desc
==============================================================================================
-    IBM.2107-75BXF21 IBM.2107-75BXF20 961   5005076304FFD7EA Online Enabled V0 -
        """
        self.si = self.parseblock(4)[0]

    def set_vdisk_wwn(self):
        prefix = self.si['WWNN'].lower()
        prefix = '6' + prefix[1:]
        for i, vdisk in enumerate(self.vdisk):
            devid = vdisk['ID'].lower()
            padding = "0"*(16-len(devid))
            self.vdisk[i]['wwid'] = prefix + padding + devid

    def parse_array(self):
        """
dscli> Array,State,Data,RAIDtype,arsite,Rank,DA Pair,DDMcap (10^9B)
============================================================
A0,Assigned,Normal,5 (6+P+S),S1,R0,0,400.0 10^9B
A1,Assigned,Normal,5 (6+P+S),S2,R1,0,400.0 10^9B
A2,Assigned,Normal,5 (6+P+S),S3,R2,1,300.0 10^9B
A3,Assigned,Normal,5 (6+P+S),S4,R3,1,300.0 10^9B
        """
        self.array = self.parseblock(5)

    def parse_arraysite(self):
        """
dscli> arsite,DA Pair,dkcap (10^9B),State,Array
========================================
S1,0,400.0 10^9B,Assigned,A0
S2,0,400.0 10^9B,Assigned,A1
S3,1,300.0 10^9B,Assigned,A2
S4,1,300.0 10^9B,Assigned,A3
        """
        self.arraysite = self.parseblock(6)

    def parse_rank(self):
        """
dscli> ID,Group,State,datastate,Array,RAIDtype,extpoolID,stgtype
=========================================================
R0,0,Normal,Normal,A0,5,P0,fb
R1,1,Normal,Normal,A1,5,P1,fb
R2,0,Normal,Normal,A2,5,P0,fb
R3,1,Normal,Normal,A3,5,P1,fb
        """
        self.rank = self.parseblock(7)

    def set_vdisk_raid(self):
        h = {}
        for rank in self.rank:
            poolid = rank['extpoolID']
            poolname = self.dgnames[poolid]
            if poolname in h:
                if rank['RAIDtype'] not in h[poolname]:
                    h[poolname].append(rank['RAIDtype'])
            else:
                h[poolname] = [rank['ID']]
        for i, vdisk in enumerate(self.vdisk):
            poolname = vdisk['PoolName']
            raids = ", ".join(sorted(h[vdisk['PoolName']]))
            self.vdisk[i]['Raid'] = raids

    def __str__(self):
        s = "name: %s\n" % self.si['ID']
        s += "modelnumber: %s\n" % self.si['Model']
        #s += "controllermainmemory: %d\n" % self.controllermainmemory
        #s += "firmwareversion: %s\n" % self.firmwareversion
        for dg in self.dg:
            s += str(dg)+'\n'
        for d in self.vdisk:
            s += str(d)+'\n'
        for d in self.ioport:
            s += str(d)+'\n'
        return s


def get_ibmds(dir=None):
    try:
        return IbmDs(dir)
    except:
        return None

import sys
def main():
    s = IbmDs(sys.argv[1])
    print s

if __name__ == "__main__":
    main()

