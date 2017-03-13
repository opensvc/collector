import os
from xml.etree.ElementTree import ElementTree, SubElement

class SymTDev(object):
    def __init__(self, xml):
        self.dev_name = xml.find("dev_name").text
        self.total_tracks_mb = int(xml.find("total_tracks_mb").text)
        self.alloc_tracks_mb = int(xml.find("alloc_tracks_mb").text)
        self.pools = []
        for e in xml.findall("pool"):
            pool_name = e.find("pool_name").text
            if pool_name == "N/A":
                continue
            self.pools.append(pool_name)

    def prefix(self, text=""):
        if len(text) == 0:
            return ""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            lines[i] = "tdev[%s].%s"%(self.dev_name, line)
        return lines

    def __str__(self):
        l = []
        l += self.prefix("total_tracks_mb: "+str(self.total_tracks_mb))
        l += self.prefix("alloc_tracks_mb: "+str(self.alloc_tracks_mb))
        l += self.prefix("pools: "+','.join(self.pools))
        return '\n'.join(l)

class SymMask(object):
    def __init__(self, director, port, xml):
        self.director = director
        self.port = port
        self.originator_port_wwn = xml.find('originator_port_wwn').text
        self.id = ':'.join([director, port, self.originator_port_wwn])
        self.dev = []
        for e in xml.findall("Device"):
            start_dev_e = e.find("start_dev")
            if start_dev_e is None:
                # this really can happen
                continue
            start_dev = int(start_dev_e.text, 16)
            end_dev = int(e.find("end_dev").text, 16)
            devs = range(start_dev, end_dev+1)
            self.dev += map(lambda x: str('%04X'%x).replace('0x',''), devs)

    def prefix(self, text=""):
        if len(text) == 0:
            return ""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            lines[i] = "mask[%s].%s"%(self.id, line)
        return lines

    def __str__(self):
        l = []
        l += self.prefix("dev: "+','.join(self.dev))
        return '\n'.join(l)

class SymDirector(object):
    def __init__(self, xml):
        self.port_wwn = [m.text for m in xml.findall("Port/Port_Info/port_wwn")]
        self.info = {}
        for e in list(xml.find("Dir_Info")):
            self.info[e.tag] = e.text

    def prefix(self, text=""):
        if len(text) == 0:
            return ""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            lines[i] = "dir[%s].%s"%(self.info['id'], line)
        return lines

    def __str__(self):
        l = []
        l += self.prefix("type: "+self.info['type'])
        l += self.prefix("slot: "+self.info['slot'])
        l += self.prefix("port_wwn: "+','.join(self.port_wwn))
        return '\n'.join(l)

class SymMeta(object):
    def __init__(self, xml):
        self.dev_name = xml.find("Dev_Info/dev_name").text
        self.meta = [ m.text for m in xml.findall("Meta/Meta_Device/dev_name")]

        try:
            self.tracks_per_stripe = int(xml.find('RAID-5_Device/RAID5_Dev_Info/tracks_per_stripe').text)
        except:
            # 2-way Mir
            self.tracks_per_stripe = 2

        try:
            self.wwn = xml.find("Product/wwn").text
        except:
            self.wwn = ""

    def prefix(self, text=""):
        if len(text) == 0:
            return ""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            lines[i] = "meta.%s"%(line)
        return lines

    def __str__(self):
        l = []
        l += self.prefix("head: "+self.dev_name)
        l += self.prefix("members: "+','.join(self.meta))
        l += self.prefix("wwn: "+self.wwn)
        return '\n'.join(l)

class VmaxView(object):
    def __init__(self, xml):
        self.view_name = xml.find('view_name').text
        self.init_grpname = xml.find('init_grpname').text
        self.port_grpname = xml.find('port_grpname').text
        self.stor_grpname = xml.find('stor_grpname').text
        self.dev = []

        self.ig = []
        for e in list(xml.find("Initiators")):
            self.ig.append(e.text)

        self.pg = []
        for pg in list(xml.findall("port_info/Director_Identification")):
            d = {}
            for e in list(pg):
                d[e.tag] = e.text
            self.pg.append(d['dir']+':'+d['port'])

        self.sg = []
        for sg in list(xml.findall("Device")):
            self.sg.append(sg.find('dev_name').text)

    def prefix(self, text=""):
        if len(text) == 0:
            return ""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            lines[i] = "view[%s].%s"%(self.view_name, line)
        return lines

    def __str__(self):
        l = []
        l += self.prefix("view_name: "+self.view_name)
        l += self.prefix("init_grpname: "+self.init_grpname)
        l += self.prefix("initiators: "+','.join(self.ig))
        l += self.prefix("port_grpname: "+self.port_grpname)
        l += self.prefix("ports: "+','.join(self.pg))
        l += self.prefix("stor_grpname: "+self.stor_grpname)
        l += self.prefix("devices: "+','.join(self.sg))
        return '\n'.join(l)

class SymFiconDev(object):
    def __init__(self, xml):
        self.devname = xml.find("Dev_Info/dev_name").text

class SymDevRdf(object):
    def __init__(self, xml=None):
        if xml is None:
            self.devname = ''
            self.pair_state = ''
            self.mode = ''
            self.ra_group_num = ''
            self.remote_symid = ''
            self.remote_devname = ''
            return
        self.devname = xml.find("Dev_Info/dev_name").text
        self.pair_state = xml.find("RDF/RDF_Info/pair_state").text
        self.mode = xml.find("RDF/Mode/mode").text
        self.ra_group_num = xml.find("RDF/Local/ra_group_num").text
        self.remote_symid = xml.find("RDF/Remote/remote_symid").text
        self.remote_devname = xml.find("RDF/Remote/dev_name").text

    def prefix(self, text=""):
        if len(text) == 0:
            return ""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            lines[i] = "rdf.%s"%line
        return lines

    def __str__(self):
        l = []
        l += self.prefix("pair_state: "+self.pair_state)
        l += self.prefix("mode: "+self.mode)
        l += self.prefix("ra_group_num: "+self.ra_group_num)
        l += self.prefix("remote_symid: "+self.remote_symid)
        l += self.prefix("remote_devname: "+self.remote_devname)
        return '\n'.join(l)

class SymDev(object):
    def __init__(self, xml):
        self.info = {}
        self.flags = {}
        self.backend = []
        self.frontend = []
        self.masking = []
        self.meta = []
        self.meta_count = 0
        self.diskgroup = None
        self.diskgroup_name = ""
        self.view = []
        self.wwn = ""
        self.ficon = False
        self.rdf = SymDevRdf()
        self.memberof = ""
        self.alloc = 0
        self.backend_alloc = 0
        self.ident_name = ""

        try:
            self.megabytes = int(xml.find("Capacity/megabytes").text)
        except:
            self.megabytes = 0
        self.alloc = self.megabytes
        for e in list(xml.find("Dev_Info")):
            self.info[e.tag] = e.text
        for e in list(xml.find("Flags")):
            self.flags[e.tag] = e.text
        for disk in list(xml.find("Back_End")):
            d = {}
            for e in list(disk):
                d[e.tag] = e.text
            d['id'] = ':'.join((d['director'],
                                d['interface'],
                                d['tid']))
            self.backend += [d]

    def prefix(self, text=""):
        if len(text) == 0:
            return ""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            lines[i] = "dev[%s].%s"%(self.info['dev_name'], line)
        return lines

    def __str__(self):
        l = []
        for key in self.info:
            l += self.prefix(key+": "+self.info[key])
        for key in self.flags:
            l += self.prefix("flags."+key+": "+self.flags[key])
        l += self.prefix("frontend: %s"%','.join(self.frontend))
        l += self.prefix("masking: %s"%','.join(self.masking))
        for i, be in enumerate(self.backend):
            for key in be:
                l += self.prefix("be[%d].%s: %s"%(i, key, be[key]))
        l += self.prefix('megabytes: %d'%self.megabytes)
        l += self.prefix('alloc megabytes: %d'%self.alloc)
        l += self.prefix('backend megabytes: %d'%self.backend_alloc)
        l += self.prefix('diskgroup: %s'%str(self.diskgroup))
        l += self.prefix('diskgroup_name: %s'%str(self.diskgroup_name))
        l += self.prefix('meta: %s'%','.join(self.meta))
        l += self.prefix('member of: %s'%self.memberof)
        l += self.prefix('view: %s'%','.join(self.view))
        l += self.prefix('wwn: %s'%self.wwn)
        l += self.prefix('ficon: %s'%self.ficon)
        if hasattr(self, 'rdf'):
            l += self.prefix(str(self.rdf))
        return '\n'.join(l)

    def __iadd__(self, o):
        if isinstance(o, SymMeta):
            self.tracks_per_stripe = o.tracks_per_stripe
            if self.info['configuration'] == "RAID-5" and self.tracks_per_stripe == 4:
                self.backend_alloc = int(1. * self.megabytes * 4 / 3)
            elif self.info['configuration'] == "RAID-5" and self.tracks_per_stripe == 8:
                self.backend_alloc = int(1. * self.megabytes * 8 / 7)
            elif self.info['configuration'] == "RAID-6" and self.tracks_per_stripe == 8:
                self.backend_alloc = int(1. * self.megabytes * 8 / 6)
            elif self.info['configuration'] == "RAID-6" and self.tracks_per_stripe == 16:
                self.backend_alloc = int(1. * self.megabytes * 16 / 14)
            elif self.info['configuration'] == "2-Way Mir":
                self.backend_alloc = 2 * self.megabytes
            elif 'TDEV' in self.info['configuration']:
                # backend_alloc is brought through SymTDev
                pass
            else:
                self.backend_alloc = 0
                print "could not determine backend allocation for ", self.info['dev_name'], self.tracks_per_stripe, self.info['configuration']

            self.meta = o.meta
            self.meta_count = len(o.meta)
        elif isinstance(o, SymDevWwn):
            self.wwn = o.wwn
        elif isinstance(o, SymDevRdf):
            self.rdf = o
        elif isinstance(o, SymTDev):
            self.megabytes = o.total_tracks_mb
            self.alloc = o.alloc_tracks_mb
            self.backend_alloc = 0
        return self

    def set_membership(self, devname):
        self.memberof = devname

class SymDevWwn(object):
    def __init__(self, xml):
        self.dev_name = xml.find("dev_name").text
        self.wwn = xml.find("wwn").text

    def __str__(self):
        return ''

class SymPool(object):
    def __init__(self, xml):
        self.info = {}
	self.totals = {}
        for e in list(xml):
            if e.tag == "SaveDev":
                continue
            elif e.tag == "Totals":
                for _e in list(e):
                    self.totals[_e.tag] = _e.text
            else:
                self.info[e.tag] = e.text

    def prefix(self, text=""):
        if len(text) == 0:
            return ""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            lines[i] = "pool[%s].%s"%(self.info['pool_name'], line)
        return lines

    def __str__(self):
        l = []
        for key in self.info:
            l += self.prefix(key+": "+self.info[key])
        l += self.prefix('total: %d' % int(self.totals["total_tracks_mb"]))
        l += self.prefix('free: %d' % int(self.totals["total_free_tracks_mb"]))
        l += self.prefix('used: %d' % int(self.totals["total_used_tracks_mb"]))
        return '\n'.join(l)

class SymSrp(object):
    def __init__(self, xml):
        self.info = {}
        for e in xml.findall("SRP_Info"):
	    for _e in list(e):
                self.info[_e.tag] = _e.text

    def prefix(self, text=""):
        if len(text) == 0:
            return ""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            lines[i] = "srp[%s].%s"%(self.info['name'], line)
        return lines

    def __str__(self):
        l = []
        for key in self.info:
            l += self.prefix(key+": "+self.info[key])
        l += self.prefix('total: %d' % int(float(self.info["usable_capacity_gigabytes"]))*1024)
        l += self.prefix('free: %d' % int(float(self.info["free_capacity_gigabytes"]))*1024)
        l += self.prefix('used: %d' % int(float(self.info["allocated_capacity_gigabytes"]))*1024)
        return '\n'.join(l)

class SymDiskGroup(object):
    def __init__(self, xml):
        self.total = 0
        self.vtotal = 0
        self.used = 0
        self.vused = 0
        self.diskcount = {}
        self.info = {}
        self.disk = []
        self.dev = []
        self.masked_dev = []
        self.dev_by_size = {}
        self.masked_dev_by_size = {}

        for e in list(xml):
            for se in list(e):
                self.info[se.tag] = se.text

    def prefix(self, text=""):
        if len(text) == 0:
            return ""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            lines[i] = "diskgroup[%s].%s"%(self.info['disk_group_number'], line)
        return lines

    def __str__(self):
        l = []
        for key in self.info:
            l += self.prefix(key+": "+self.info[key])
        for key in self.diskcount:
            l += self.prefix('diskcount: '+'/'.join(key)+' => '+str(self.diskcount[key]))
        l += self.prefix('total: %d'%(self.total))
        l += self.prefix('free: %d'%(self.total-self.used))
        l += self.prefix('used: %d'%self.used)
        l += self.prefix('vtotal: %d'%(self.total))
        l += self.prefix('vused: %d'%self.vused)
        l += self.prefix('disks: %s'%','.join(self.disk))
        l += self.prefix('devs: %s'%','.join(self.dev))
        l += self.prefix('masked_devs: %s'%','.join(self.masked_dev))
        for size in self.dev_by_size:
            l += self.prefix('devs[%dMB]: %s'%(size, ','.join(self.dev_by_size[size])))
        for size in self.masked_dev_by_size:
            l += self.prefix('masked_devs[%dMB]: %s'%(size, ','.join(self.masked_dev_by_size[size])))
        return '\n'.join(l)

    def __iadd__(self, o):
        if isinstance(o, SymDisk):
            self.disk.append(o.id)
            if o.info['hot_spare'] == 'True':
                key = o.info['actual_megabytes'], o.info['technology'], o.info['speed'], "hot spare"
            else:
                key = o.info['actual_megabytes'], o.info['technology'], o.info['speed']
            if key not in self.diskcount:
                self.diskcount[key] = 1
            else:
                self.diskcount[key] += 1
        if isinstance(o, SymDev):
            devname = o.info['dev_name']
            if devname in self.dev:
                return
            self.dev.append(devname)
            if o.info['configuration'] != 'VDEV':
                self.total += o.megabytes
            else:
                self.vtotal += o.megabytes
            if o.megabytes not in self.dev_by_size:
                self.dev_by_size[o.megabytes] = []
            if devname not in self.dev_by_size[o.megabytes]:
                self.dev_by_size[o.megabytes].append(devname)
        return self

    def add_masked_dev(self, o):
        devname = o.info['dev_name']
        if devname in self.masked_dev:
            return
        self.masked_dev.append(devname)
        if o.info['configuration'] != 'VDEV':
            self.used += o.megabytes
        else:
            self.vused += o.megabytes
        if o.megabytes not in self.masked_dev_by_size:
            self.masked_dev_by_size[o.megabytes] = []
        if devname not in self.masked_dev_by_size[o.megabytes]:
            self.masked_dev_by_size[o.megabytes].append(devname)

class SymDisk(object):
    def __init__(self, xml):
        self.info = {}
        for e in list(xml.find('Disk_Info')):
            self.info[e.tag] = e.text
        self.id = ':'.join((self.info['da_number'],
                            self.info['interface'],
                            self.info['tid']))

    def prefix(self, text=""):
        if len(text) == 0:
            return ""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            lines[i] = "disk[%s].%s"%(self.id, line)
        return lines

    def __str__(self):
        l = []
        for key in self.info:
            l += self.prefix(key+": "+self.info[key])
        return '\n'.join(l)

class Sym(object):
    def __init__(self, xml_dir=None):
        if xml_dir is None:
            return
        self.info = {}
        self.parsers = ['sym_info',
                        'sym_diskgroup',
                        'sym_pool',
                        'sym_srp',
                        'sym_disk',
                        'sym_dev',
                        'sym_dev_ident_name',
                        'sym_dev_wwn',
                        'sym_devrdfa',
                        'sym_ficondev',
                        'sym_meta',
                        'sym_director',
                        'sym_tdev']

        self.xml_dir = xml_dir
        self.xml_mtime = None
        self.info.update({'dev_count':0,
                          'disk_count': 0,
                          'diskgroup_count': 0,
                          'view_count': 0})
        self.dev = {}
        self.disk = {}
        self.diskgroup = {}
        self.director = {}
        self.pool = {}
        self.srp = {}

    def init_data(self):
        for parser in self.parsers:
            getattr(self, parser)()

    def prefix(self, text=""):
        if len(text) == 0:
            return ""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            lines[i] = "sym[%s].%s"%(self.info['symid'], line)
        return lines

    def __str__(self):
        l = []
        for key in self.info:
            l += self.prefix('%s: %s'%(key,self.info[key]))
        for srp in self.srp:
            l += self.prefix(str(self.srp[srp]))
        for pool in self.pool:
            l += self.prefix(str(self.pool[pool]))
        for dg in self.diskgroup:
            l += self.prefix(str(self.diskgroup[dg]))
        for disk in self.disk:
            l += self.prefix(str(self.disk[disk]))
        for dev in self.dev:
            l += self.prefix(str(self.dev[dev]))
        for director in self.director:
            l += self.prefix(str(self.director[director]))
        return '\n'.join(l)

    def __iadd__(self, o):
        if isinstance(o, SymSrp):
            self.add_sym_srp(o)
        if isinstance(o, SymPool):
            self.add_sym_pool(o)
        elif isinstance(o, SymDiskGroup):
            self.add_sym_diskgroup(o)
        elif isinstance(o, SymDisk):
            self.add_sym_disk(o)
        elif isinstance(o, SymFiconDev):
            self.add_sym_ficondev(o)
        elif isinstance(o, SymDevRdf):
            self.add_sym_devrdf(o)
        elif isinstance(o, SymDev):
            self.add_sym_dev(o)
        elif isinstance(o, SymDirector):
            self.add_sym_director(o)
        elif isinstance(o, SymDevWwn):
            self.add_sym_dev_wwn(o)
        elif isinstance(o, SymMeta):
            self.add_sym_meta(o)
        elif isinstance(o, SymTDev):
            self.add_sym_tdev(o)
        return self

    def add_sym_tdev(self, o):
        if o.dev_name not in self.dev:
            return
        self.dev[o.dev_name] += o

    def add_sym_dev_wwn(self, o):
        self.dev[o.dev_name] += o

    def add_sym_meta(self, o):
        self.dev[o.dev_name] += o
        for devname in o.meta:
            self.dev[devname].set_membership(o.dev_name)

    def add_sym_diskgroup(self, o):
        self.diskgroup[int(o.info['disk_group_number'])] = o
        self.info['diskgroup_count'] += 1

    def add_sym_srp(self, o):
        self.srp[o.info['name']] = o

    def add_sym_pool(self, o):
        self.pool[o.info['pool_name']] = o

    def add_sym_disk(self, o):
        self.disk[o.id] = o
        self.info['disk_count'] += 1
        self.diskgroup[int(o.info['disk_group'])] += o

    def add_sym_ficondev(self, o):
        dev = self.dev[o.devname]
        dev.ficon = True
        dg = dev.diskgroup
        if dg is not None:
            self.diskgroup[dg].add_masked_dev(dev)

    def add_sym_devrdf(self, o):
        self.dev[o.devname] += o

    def add_sym_dev(self, o):
        disk_id = o.backend[0]['id']
        if disk_id in self.disk:
            disk = self.disk[disk_id]
            o.diskgroup = int(disk.info['disk_group'])
            o.diskgroup_name = disk.info['disk_group_name']
            self.diskgroup[o.diskgroup] += o
        self.dev[o.info['dev_name']] = o
        self.info['dev_count'] += 1

    def add_sym_director(self, o):
        self.director[o.info['id']] = o

    def xmltree(self, xml):
        f = os.path.join(self.xml_dir, xml)
        tree = ElementTree()
        tree.parse(f)
        return tree

    def sym_info(self):
        tree = self.xmltree('sym_info')
        for e in tree.getiterator('Symm_Info'): pass
        for se in list(e):
          self.info[se.tag] = se.text
        del tree

    def sym_diskgroup(self):
        self.diskgroup = {}
        tree = self.xmltree('sym_diskgroup_info')
        for e in tree.getiterator('Disk_Group'):
            self += SymDiskGroup(e)
        del tree

    def sym_srp(self):
        tree = self.xmltree('sym_srp_info')
        for e in tree.getiterator('SRP'):
            self += SymSrp(e)
        del tree

    def sym_pool(self):
        tree = self.xmltree('sym_pool_info')
        for e in tree.getiterator('DevicePool'):
            self += SymPool(e)
        del tree

    def sym_disk(self):
        tree = self.xmltree('sym_disk_info')
        for e in tree.getiterator('Disk'):
            self += SymDisk(e)
        del tree

    def sym_dev(self):
        tree = self.xmltree('sym_dev_info')
        for e in tree.getiterator('Device'):
            self += SymDev(e)
        del tree

    def sym_dev_ident_name(self):
        tree = self.xmltree('sym_dev_name_info')
        for e in tree.getiterator('Dev_Info'):
            devid = e.find("dev_name").text
            devname = e.find("dev_ident_name").text
            self.dev[devid].ident_name = devname
        del tree

    def sym_tdev(self):
        tree = self.xmltree('sym_tdev_info')
        for e in tree.getiterator('Device'):
            self += SymTDev(e)
        del tree

    def sym_dev_wwn(self):
        tree = self.xmltree('sym_dev_wwn_info')
        for e in tree.getiterator('Device'):
            self += SymDevWwn(e)
        del tree

    def sym_devrdfa(self):
        tree = self.xmltree('sym_devrdfa_info')
        for e in tree.getiterator('Device'):
            self += SymDevRdf(e)
        del tree

    def sym_ficondev(self):
        tree = self.xmltree('sym_ficondev_info')
        for e in tree.getiterator('Device'):
            self += SymFiconDev(e)
        del tree

    def sym_meta(self):
        tree = self.xmltree('sym_meta_info')
        for e in tree.getiterator('Device'):
            self += SymMeta(e)
        del tree

    def sym_director(self):
        tree = self.xmltree('sym_dir_info')
        for e in tree.getiterator('Microcode'):
            for el in list(e):
                self.info[el.tag] = el.text
        for e in tree.getiterator('Symmwin'):
            for el in list(e):
                self.info['symmwin_'+el.tag] = el.text
        for e in tree.getiterator('Director'):
            self += SymDirector(e)
        del tree

class Dmx(Sym):
    def __init__(self, xml_dir=None):
        Sym.__init__(self, xml_dir)
        self.parsers += ['sym_maskdb']
        self.maskdb = {}
        self.info.update({'maskdb_count': 0})

    def __str__(self):
        l = []
        for mask in self.maskdb:
            l += self.prefix(str(self.maskdb[mask]))
        return Sym.__str__(self)+'\n'.join(l)

    def __iadd__(self, o):
        if isinstance(o, SymMask):
            self.add_sym_mask(o)
        return Sym.__iadd__(self, o)

    def add_sym_mask(self, o):
        self.maskdb[o.id] = o
        self.info['maskdb_count'] += 1
        for dev_name in o.dev:
            dev = self.dev[dev_name]
            if o.id not in dev.masking:
                dev.masking.append(o.id)
            dg = dev.diskgroup
            if dg is None:
                # VDEV
                continue
            self.diskgroup[dg].add_masked_dev(dev)

    def sym_maskdb(self):
        tree = self.xmltree('sym_maskdb')
        for e in tree.getiterator('Devmask_Database_Record'):
            director = e.find('director').text
            port = e.find('port').text
            for ee in e.findall('Db_Record'):
                self += SymMask(director, port, ee)
        del tree

class Vmax(Sym):
    def __init__(self, xml_dir=None):
        Sym.__init__(self, xml_dir)
        self.parsers += [
            'sym_view',
            'sym_sg',
        ]
        self.ig = {}
        self.pg = {}
        self.sg = {}
        self.view = {}
        self.info.update({'view_count': 0,
                          'ig_count': 0,
                          'pg_count': 0,
                          'sg_count': 0})

    def __str__(self):
        l = []
        for view in self.view:
            l += self.prefix(str(self.view[view]))
        return Sym.__str__(self)+'\n'.join(l)

    def __iadd__(self, o):
        if isinstance(o, VmaxView):
            self.add_sym_view(o)
        return Sym.__iadd__(self, o)

    def add_sym_view(self, o):
        self.view[o.view_name] = o
        self.info['view_count'] += 1
        self.ig[o.init_grpname] = o.ig
        self.info['ig_count'] += 1
        self.pg[o.port_grpname] = o.pg
        self.info['pg_count'] += 1
        self.sg[o.stor_grpname] = o.sg
        self.info['sg_count'] += 1
        for dev_name in o.sg:
            dev = self.dev[dev_name]
            dev.view.append(o.view_name)
            dev.frontend += o.pg
            o.dev.append(dev)
            dg = dev.diskgroup_name
            if dg is None:
                # VDEV
                continue
            for _dg in dg.split(", "):
                if _dg in self.diskgroup:
                    self.diskgroup[_dg].add_masked_dev(dev)

    def sym_view(self):
        tree = self.xmltree('sym_view_aclx')
        for e in tree.getiterator('View_Info'):
            self += VmaxView(e)
        del tree

    def sym_sg(self):
        tree = self.xmltree('sym_sg_info')
        for e in tree.findall('SG'):
            sg = e.find("SG_Info/name").text
            srp = e.find("SG_Info/SRP_name").text
            if srp == "none":
                # skip parent SG
                continue
            for edev in e.findall("DEVS_List/Device"):
                dev = edev.find("dev_name").text
                if dev in self.dev:
                    self.dev[dev].diskgroup_name = srp + "/" +sg
        del tree

def get_sym(xml_dir=None):
        f = os.path.join(xml_dir, 'sym_info')
        tree = ElementTree()
        tree.parse(f)
        for e in tree.getiterator('Symm_Info'): pass
        model = e.find('model').text
        del tree
        if 'VMAX' in model:
            return Vmax(xml_dir)
        elif 'DMX' in model or '3000-M':
            return Dmx(xml_dir)
        return None

import sys
def main():
    s = get_sym(sys.argv[1])
    s.init_data()
    print s

if __name__ == "__main__":
    main()

