import os

class Dcs(object):
    def __init__(self, dir=None):
        if dir is None:
            return
        self.dir = dir
        self.name = os.path.basename(dir)
        self.servergroup()
        self.server()
        self.port()
        self.pool()
        #self.pool_member()
        self.pool_perf()
        self.vdisk()
        self.physical_disk()
        self.logical_disk()
        self.logical_disk_perf()
        self.purge_vdisk()

    def readfile(self, fname):
        fpath = os.path.join(self.dir, fname)
        with open(fpath, 'r') as f:
            buff = f.read()
        return buff

    def purge_vdisk(self):
        purge = []
        for k in self.vdisk:
            if len(self.vdisk[k]['poolid']) == 0:
                purge.append(k)
        for k in purge:
            del(self.vdisk[k])

    def servergroup(self):
        buff = self.readfile('dcsservergroup')
        sg = {}
        for line in buff.split('\n'):
            if line.startswith('OurGroup'):
                if len(sg) > 0 and sg['ourgroup'] == "True":
                    self.sg = sg
                    sg = {}
                sg['ourgroup'] = line.split(": ")[-1].strip()
            elif line.startswith('Caption'):
                sg['caption'] = line.split(": ")[-1].strip()
            elif line.startswith('Id'):
                sg['id'] = line.split(": ")[-1].strip()
            elif line.startswith('StorageUsed'):
                sg["used"] = self.to_mb(line.split(': ')[-1].strip())
                sg["memory"] = 0
        if len(sg) > 0 and sg['ourgroup'] == "True":
            self.sg = sg

    def server(self):
        buff = self.readfile('dcsserver')
        server = {}
        self.server = {}
        for line in buff.split('\n'):
            if line.startswith('GroupId'):
                if len(server) > 0:
                    self.server[server['id']] = server
                    server = {}
            if line.startswith('ProductName'):
                server['model'] = line.split(": ")[-1].strip()
            elif line.startswith('ProductType'):
                server['producttype'] = " "+line.split(": ")[-1].strip()
            elif line.startswith('ProductVersion'):
                server['productversion'] = line.split(": ")[-1].strip()
            elif line.startswith('ProductBuild'):
                server['productbuild'] = line.split(": ")[-1].strip()
            elif line.startswith('TotalSystemMemory'):
                n, u = line.split(": ")[-1].strip().split()
                n = float(n.replace(',', '.'))
                if u == 'GB':
                    n = n * 1024
                server['memory'] = n
                self.sg['memory'] += n
            elif line.startswith('HostName'):
                server['hostname'] = line.split(": ")[-1].strip().lower()
            elif line.startswith('Id'):
                server['id'] = line.split(": ")[-1].strip()
        if len(server) > 0:
            self.server[server['id']] = server

        self.ports = list()

    def to_mb(self, size):
        size = size.replace(",", ".")
        if "PB" in size:
            size = float(size.replace(" PB", "")) * 1024 * 1024 * 1024
        elif "TB" in size:
            size = float(size.replace(" TB", "")) * 1024 * 1024
        elif "GB" in size:
            size = float(size.replace(" GB", "")) * 1024
        elif "MB" in size:
            size = float(size.replace(" MB", ""))
        elif "KB" in size:
            size = float(size.replace(" MB", "")) // 1024
        elif "B" in size:
            size = float(size.replace(" B", "")) // 1024 // 1024
        else:
            size = float(size.replace(" MB", "")) // 1024 // 1024
        return size

    def port(self):
        """
StateInfo            : DataCore.Executive.FC.FcPortStateInfo
CurrentConfigInfo    : DataCore.Executive.FC.FcPortConfigInfo
IdInfo               : DataCore.Executive.FC.FcPortIdInfo
CapabilityInfo       : DataCore.Executive.FC.FcPortCapabilityInfo
PresenceStatus       : Present
PhysicalName         : 5001438018694A0A
ServerPortProperties : DataCore.Executive.ServerFcPortPropertiesData
RoleCapability       : Frontend, Mirror
AluaId               : 2062
PortName             : 50-01-43-80-18-69-4A-0A
Alias                : SDSERT02_FE_SLOT02_P1
Description          : 
PortType             : FibreChannel
PortMode             : Target
HostId               : E1505D31-44D1-4219-9741-4E1263B05195
Connected            : True
Id                   : edd5274a-cc85-462c-aa42-a154b0ea98c4
Caption              : SDSERT02_FE_SLOT02_P1
ExtendedCaption      : SDSERT02_FE_SLOT02_P1 on SDSERT02
Internal             : False
        """
        buff = self.readfile('dcsport')
        self.port_list = []
        port = {}
        lines = buff.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('Internal'):
                if len(port) > 0 and \
                   (port['porttype'] == "FibreChannel" or port['porttype'] =='iSCSI') and \
                   port['portmode'] == "Target":
                    if port['porttype'] == "FibreChannel":
                        port["portname"] = port["portname"].replace('-', '')
                    self.port_list.append(port["portname"])
                port = {}
            elif line.startswith('PortType'):
                port["porttype"] = self.get_val(lines, i)
            elif line.startswith('PortMode'):
                port["portmode"] = self.get_val(lines, i)
            elif line.startswith('PortName'):
                port["portname"] = self.get_val(lines, i)
        if len(port) > 0 and \
           (port['porttype'] == "FibreChannel" or port['porttype'] =='iSCSI') and \
           port['portmode'] == "Target":
            if port['porttype'] == "FibreChannel":
                port["portname"] = port["portname"].replace('-', '')
            self.port_list.append(port["portname"])

    def pool(self):
        """
ServerId        : 6FC0981F-4668-441D-907F-EFF6346BCBE2
Alias           : SDSERT01_SAS01
Description     : 
PresenceStatus  : Present
PoolStatus      : Running
PoolMode        : ReadWrite
Type            : Dynamic
ChunkSize       : 128,00 MB
MaxTierNumber   : 1
Id              : 6FC0981F-4668-441D-907F-EFF6346BCBE2:{0db47608-8eec-11e1-9b73
                  -441ea14c69ea}
Caption         : SDSERT01_SAS01
ExtendedCaption : SDSERT01_SAS01 on SDSERT01
Internal        : False
        """
        buff = self.readfile('dcspool')
        self.pool = {}
        self.pool_list = []
        pool = {}
        lines = buff.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('ServerId'):
                if len(pool) > 0:
                    self.pool[pool["id"]] = pool
                    self.pool_list.append(pool["id"])
                pool = {'size': 0}
            elif line.startswith('Caption'):
                pool["caption"] = self.get_val(lines, i)
            elif line.startswith('Size'):
                pool["size"] = self.to_mb(self.get_val(lines, i))
            elif line.startswith('Id'):
                pool["id"] = self.get_val(lines, i)
        if len(pool) > 0:
            self.pool[pool["id"]] = pool
            self.pool_list.append(pool["id"])

    def pool_perf(self):
        """
TotalBytesTransferred : 0
TotalBytesRead        : 0
TotalBytesWritten     : 0
TotalBytesMigrated    : 0
TotalReads            : 0
TotalWrites           : 0
TotalOperations       : 0
BytesAllocated        : 0
BytesAvailable        : 4397765492736
BytesInReclamation    : 0
BytesTotal            : 4397765492736
PercentAllocated      : 0
PercentAvailable      : 100
TotalReadTime         : 0
TotalWriteTime        : 0
MaxReadTime           : 0
MaxWriteTime          : 0
MaxReadWriteTime      : 0
MaxNumberChunks       : 8290176
BytesReserved         : 0
CollectionTime        : 23/05/2012 08:20:10
        """
        buff = self.readfile('dcspoolperf')
        lines = buff.split('\n')
        i = -1
        for line in lines:
            if line.startswith('TotalBytesTransferred'):
                i += 1
            elif line.startswith('BytesAllocated'):
                self.pool[self.pool_list[i]]['alloc'] = self.to_mb(line.split(': ')[-1].strip())
            elif line.startswith('BytesAvailable'):
                self.pool[self.pool_list[i]]['avail'] = self.to_mb(line.split(': ')[-1].strip())
            elif line.startswith('BytesTotal'):
                self.pool[self.pool_list[i]]['total'] = self.to_mb(line.split(': ')[-1].strip())
            elif line.startswith('BytesReserved'):
                self.pool[self.pool_list[i]]['reserved'] = self.to_mb(line.split(': ')[-1].strip())

    def pool_member(self):
        """
DiskPoolId       : 6FC0981F-4668-441D-907F-EFF6346BCBE2:{bceca3a2-8fa1-11e1-9e1
                   2-441ea14c69ea}
DiskInRecoveryId : 
DiskTier         : 1
RecoveryState    : Healthy
Size             : 1,04 TB
IsMirrored       : False
Id               : 55eead37-d823-48f7-93a8-07f6b7624f7b
Caption          : Disk 68
ExtendedCaption  : Pool Disk 68 on SDSERT01
Internal         : False
        """
        buff = self.readfile('dcspoolmember')
        lines = buff.split('\n')
        member = {}
        for i, line in enumerate(lines):
            if line.startswith('DiskPoolId'):
                member = {}
                member["poolid"] = self.get_val(lines, i)
            elif line.startswith('Size'):
                member["size"] = self.to_mb(self.get_val(lines, i))

    def logical_disk_perf(self):
        buff = self.readfile('dcslogicaldiskperf')
        lines = buff.split('\n')
        i = -1
        for line in lines:
            if line.startswith('DestageTime'):
                i += 1
            elif line.startswith('BytesAllocated'):
                self.vdisk[self.ld[self.ld_list[i]]['vdiskid']]['alloc'] = self.to_mb(line.split(': ')[-1].strip())


    def get_val(self, lines, i):
        line = lines[i]
        val = line.split(': ')[-1].strip()
        if len(lines) < i:
            return val
        next = lines[i+1]
        if len(next) > 0 and next.startswith(" "):
            val += next.strip()
        return val

    def physical_disk(self):
        """
PoolMemberId     : 643135e6-66c1-40a8-a5b0-eda75534eb32
HostId           : 6FC0981F-4668-441D-907F-EFF6346BCBE2
PresenceStatus   : Present
Size             : 1,04 TB
FreeSpace        : 0,00 B
InquiryData      : NEC      DISK ARRAY       1000 0000943000010020
ScsiPath         : Port 4, Bus 0, Target 2, LUN 1
DiskIndex        : 28
SystemName       :
DiskHealth       : Healthy
BusType          : Unknown
Type             : Pool
DiskStatus       : Online
Partitioned      : True
InUse            : True
IsBootDisk       : False
Protected        : False
UniqueIdentifier : eui.00255c3a11010020
Id               : {5c20afb9-61cc-4b26-8be4-9afe912a7559}
Caption          : Disk 28
ExtendedCaption  : Disk 28 on SDSERT01
Internal         : False

LocalLogicalDiskId  : LD:E1505D31-44D1-4219-9741-4E1263B05195_V.{7f4f2e6b-8fa4-
                      11e1-a292-441ea14c8982}-00000025
RemoteLogicalDiskId : LD:6FC0981F-4668-441D-907F-EFF6346BCBE2_V.{0db47608-8eec-
                      11e1-9b73-441ea14c69ea}-0000002E
PresenceStatus      : Present
Size                : 0,00 B
FreeSpace           : 0,00 B
InquiryData         :    
ScsiPath            : Port 0, Bus 0, Target 0, LUN 0
DiskIndex           : 84
SystemName          : 
DiskHealth          : Healthy
BusType             : Unknown
Type                : MirrorDisk
DiskStatus          : Online
PoolMemberId        : 
Partitioned         : True
InUse               : True
IsBootDisk          : False
Protected           : False
HostId              : E1505D31-44D1-4219-9741-4E1263B05195
UniqueIdentifier    : naa.60030d90d650fe015195013693e59e9b
Id                  : V.{0db47608-8eec-11e1-9b73-441ea14c69ea}-0000002E_N.22FE0
                      030D9311308
Caption             : Mirror of S64ertbicbh_01
ExtendedCaption     : Mirror of S64ertbicbh_01 on SDSERT02
Internal            : False
        """
        buff = self.readfile('dcsphysicaldisk')
        lines = buff.strip().split('\n')
        self.pd = {}
        pd = {}
        for i, line in enumerate(lines):
            if len(line) == 0:
                if 'id' in pd:
                    self.pd[pd["id"]] = pd
                pd = {}
            elif line.startswith('LocalLogicalDiskId'):
                pd["id"] = self.get_val(lines, i)
            elif line.startswith('UniqueIdentifier'):
                pd["wwid"] = self.get_val(lines, i).split('.')[-1].lower()
        if 'id' in pd:
            self.pd[pd["id"]] = pd

    def logical_disk(self):
        """
StreamDiskId       : 
RetentionTime      : 0
StreamSize         : 0,00 B
StreamState        : NotPresent
PoolId             : 6FC0981F-4668-441D-907F-EFF6346BCBE2:{0db47608-8eec-11e1-9
                     b73-441ea14c69ea}
VolumeIndex        : 46
MinQuota           : 0,00 B
MaxQuota           : 0,00 B
TierAffinity       : {1}
StorageName        : 
InReclamation      : False
DataStatus         : UpToDate
PresenceStatus     : Present
Size               : 1,00 PB
Description        : 
DiskStatus         : Online
Virtualized        : True
ClientAccessRights : ReadWrite
Failure            : Healthy
VirtualDiskId      : ba80a4fb7efd40d7bb81d74512084a39
DiskRole           : First
ServerHostId       : 6FC0981F-4668-441D-907F-EFF6346BCBE2
IsMapped           : True
Protected          : True
Id                 : LD:6FC0981F-4668-441D-907F-EFF6346BCBE2_V.{0db47608-8eec-1
                     1e1-9b73-441ea14c69ea}-0000002E
Caption            : S64ertbicbh_01 on SDSERT01
ExtendedCaption    : S64ertbicbh_01 on SDSERT01
Internal           : False
        """
        buff = self.readfile('dcslogicaldisk')
        lines = buff.split('\n')
        self.ld = {}
        self.ld_list = []
        ld = {}
        for i, line in enumerate(lines):
            if line.startswith('StreamDiskId'):
                if len(ld) > 0:
                    self.ld[ld["id"]] = ld
                    self.ld_list.append(ld["id"])
                    if ld["poolid"] in self.pool and ld["vdiskid"] in self.vdisk:
                        if 'poolid' not in self.vdisk[ld["vdiskid"]]:
                            self.vdisk[ld["vdiskid"]]['poolid'] = []
                        self.vdisk[ld["vdiskid"]]['poolid'].append(ld["poolid"])
                        self.vdisk[ld["vdiskid"]]['poolid'] = sorted(self.vdisk[ld["vdiskid"]]['poolid'])
                ld = {}
            elif line.startswith('Size'):
                ld["size"] = self.to_mb(self.get_val(lines, i))
            elif line.startswith('Id'):
                ld["id"] = self.get_val(lines, i)
                if ld["id"] in self.pd and \
                   ld["vdiskid"] in self.vdisk and \
                   'wwid' in self.pd[ld["id"]] and \
                   len(self.pd[ld["id"]]['wwid']) > 0:
                    self.vdisk[ld["vdiskid"]]['wwid'] = self.pd[ld["id"]]['wwid']
            elif line.startswith('PoolId'):
                ld["poolid"] = self.get_val(lines, i)
            elif line.startswith('VirtualDiskId'):
                ld["vdiskid"] = self.get_val(lines, i).lower()
        if len(ld) > 0:
            self.ld[ld["id"]] = ld
            self.ld_list.append(ld["id"])
            if ld["poolid"] in self.pool and ld["vdiskid"] in self.vdisk:
                if 'poolid' not in self.vdisk[ld["vdiskid"]]:
                    self.vdisk[ld["vdiskid"]]['poolid'] = []
                self.vdisk[ld["vdiskid"]]['poolid'].append(ld["poolid"])
                self.vdisk[ld["vdiskid"]]['poolid'] = sorted(self.vdisk[ld["vdiskid"]]['poolid'])
        for k in self.vdisk:
            if 'poolid' not in self.vdisk[k]:
                self.vdisk[k]['poolid'] = []
            if 'wwid' not in self.vdisk[k] or len(self.vdisk[k]['wwid']) == 0:
                self.vdisk[k]['wwid'] = self.vdisk[k]['id']

    def vdisk(self):
        """
VirtualDiskGroupId       : 
FirstHostId              : 6FC0981F-4668-441D-907F-EFF6346BCBE2
SecondHostId             : E1505D31-44D1-4219-9741-4E1263B05195
BackupHostId             : 
StorageProfileId         : 100469DF-0BE1-40DA-874E-9F1DA5A259E3
Alias                    : Sitertbic9z_01
Description              : Sitertbic9z / Sitertbica0
Size                     : 1,00 GB
Type                     : MultiPathMirrored
DiskStatus               : Online
InquiryData              : DataCore Virtual Disk DCS 
ScsiDeviceId             : {96, 3, 13, 144...}
RemovableMedia           : False
WriteThrough             : True
Offline                  : False
DiskLayout               : DataCore.Executive.PhysicalDiskLayout
PersistentReserveEnabled : True
RecoveryPriority         : Regular
IsServed                 : False
Id                       : 19511b5ebef14b9b9030827c1bf71e3c
Caption                  : Sitertbic9z_01
ExtendedCaption          : Sitertbic9z_01 from ERMONT - PRA2
Internal                 : False

        """
        buff = self.readfile('dcsvirtualdisk')
        self.vdisk = {}
        vdisk = {}
        lines = buff.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('VirtualDiskGroupId'):
                if len(vdisk) > 0:
                    self.vdisk[vdisk['id']] = vdisk
                vdisk = {}
            elif line.startswith('Size'):
                vdisk["size"] = self.to_mb(self.get_val(lines, i))
            elif line.startswith('Id'):
                vdisk["id"] = self.get_val(lines, i)
            elif line.startswith('caption'):
                vdisk["caption"] = self.get_val(lines, i)
            elif line.startswith('Type'):
                vdisk["type"] = self.get_val(lines, i)
            elif line.startswith('ScsiDeviceIdString'):
                vdisk["wwid"] = self.get_val(lines, i).lower()
        if len(vdisk) > 0:
            self.vdisk[vdisk['id']] = vdisk
        for k in self.vdisk:
            if 'alloc' not in self.vdisk[k]:
                self.vdisk[k]['alloc'] = 0

    def __str__(self):
        s = "servergroup: %s (%s) used %d MB\n" % (self.sg['caption'], self.sg['id'], self.sg['used'])
        s += "ports:\n"
        for port in self.port_list:
            s += " %s\n" % port
        for server in self.server.values():
            s += " hostname: %s\n" % server['hostname']
            s += "  model: %s\n" % server['model']
            s += "  producttype: %s\n" % server['producttype']
            s += "  productversion: %s\n" % server['productversion']
            s += "  memory: %d\n" % server['memory']
            s += "  productbuild: %s\n" % server['productbuild']
        for pool in self.pool.values():
            s += "pool %s (%s)\n"%(pool['caption'], pool['id'])
            s += " alloc: %d MB\n"%pool['alloc']
            s += " reserved: %d MB\n"%pool['reserved']
            s += " avail: %d MB\n"%pool['avail']
            s += " total: %d MB\n"%pool['total']
        for d in self.vdisk.values():
            poolcap = []
            for poolid in d['poolid']:
                poolcap.append(self.pool[poolid]['caption'])
            s += "vdisk %s %s: size %d/%d MB\n"%(','.join(poolcap), d['wwid'], d['alloc'], d['size'])
        return s


def get_dcs(dir=None):
    try:
        return Dcs(dir)
    except:
        return None

import sys
def main():
    s = Dcs(sys.argv[1])
    print s

if __name__ == "__main__":
    main()

