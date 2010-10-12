import pickle
import os
from xml.etree.ElementTree import ElementTree, SubElement

class VmaxDirector(object):
    def __init__(self, xml):
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
        return '\n'.join(l)

class VmaxMeta(object):
    def __init__(self, xml):
        self.dev_name = xml.find("Dev_Info/dev_name").text
        self.meta = [ m.text for m in xml.findall("Meta/Meta_Device/dev_name")]
        try:
            self.wwn = xml.find("Product/wwn").text
        except:
            self.wwn = ""

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

class VmaxFiconDev(object):
    def __init__(self, xml):
        self.devname = xml.find("Dev_Info/dev_name").text

class VmaxDevRdf(object):
    def __init__(self, xml):
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

class VmaxDev(object):
    def __init__(self, xml):
        self.info = {}
        self.flags = {}
        self.backend = []
        self.frontend = []
        self.meta = []
        self.meta_count = 0
        self.diskgroup = None
        self.diskgroup_name = ""
        self.view = []
        self.wwn = ""
        self.ficon = False

        try:
            self.megabytes = int(xml.find("Capacity/megabytes").text)
        except:
            self.megabytes = 0
        for e in list(xml.find("Dev_Info")):
            self.info[e.tag] = e.text
        for e in list(xml.find("Flags")):
            self.flags[e.tag] = e.text
        for port in list(xml.find("Front_End")):
            d = {}
            for e in list(port):
                d[e.tag] = e.text
            self.frontend += [d]
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
        for i, fe in enumerate(self.frontend):
            for key in fe:
                l += self.prefix("fe[%d].%s: %s"%(i, key, fe[key]))
        for i, be in enumerate(self.backend):
            for key in be:
                l += self.prefix("be[%d].%s: %s"%(i, key, be[key]))
        l += self.prefix('megabytes: %d'%self.megabytes)
        l += self.prefix('diskgroup: %s'%str(self.diskgroup))
        l += self.prefix('diskgroup_name: %s'%str(self.diskgroup_name))
        l += self.prefix('meta: %s'%','.join(self.meta))
        l += self.prefix('view: %s'%','.join(self.view))
        l += self.prefix('wwn: %s'%self.wwn)
        l += self.prefix('ficon: %s'%self.ficon)
        if hasattr(self, 'rdf'):
            l += self.prefix(str(self.rdf))
        return '\n'.join(l)

    def __iadd__(self, o):
        if isinstance(o, VmaxMeta):
            self.meta = o.meta
            self.meta_count = len(o.meta)
            self.wwn = o.wwn
        elif isinstance(o, VmaxDevRdf):
            self.rdf = o
        return self

class VmaxDiskGroup(object):
    def __init__(self, xml):
        self.total = 0
        self.used = 0
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
        l += self.prefix('disks: %s'%','.join(self.disk))
        l += self.prefix('devs: %s'%','.join(self.dev))
        l += self.prefix('masked_devs: %s'%','.join(self.masked_dev))
        for size in self.dev_by_size:
            l += self.prefix('devs[%dMB]: %s'%(size, ','.join(self.dev)))
        for size in self.masked_dev_by_size:
            l += self.prefix('masked_devs[%dMB]: %s'%(size, ','.join(self.dev)))
        return '\n'.join(l)

    def __iadd__(self, o):
        if isinstance(o, VmaxDisk):
            self.disk.append(o.id)
            if o.info['hot_spare'] == 'True':
                key = o.info['actual_megabytes'], o.info['technology'], o.info['speed'], "hot spare"
            else:
                key = o.info['actual_megabytes'], o.info['technology'], o.info['speed']
            if key not in self.diskcount:
                self.diskcount[key] = 1
            else:
                self.diskcount[key] += 1
        if isinstance(o, VmaxDev):
            self.dev.append(o.info['dev_name'])
            if o.info['configuration'] != 'VDEV':
                self.total += o.megabytes
            if o.megabytes not in self.dev_by_size:
                self.dev_by_size[o.megabytes] = set([o.info['dev_name']])
            else:
                self.dev_by_size[o.megabytes] |= set([o.info['dev_name']])
        return self

    def add_masked_dev(self, o):
        if o.info['dev_name'] in self.masked_dev:
            return
        self.masked_dev.append(o.info['dev_name'])
        if o.info['configuration'] != 'VDEV':
            self.used += o.megabytes
        if o.megabytes not in self.masked_dev_by_size:
            self.masked_dev_by_size[o.megabytes] = set([o.info['dev_name']])
        else:
            self.masked_dev_by_size[o.megabytes] |= set([o.info['dev_name']])

class VmaxDisk(object):
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

class Vmax(object):
    def __init__(self, xml_dir=None, preload_data=False):
        if xml_dir is None:
            return
        self.xml_dir = xml_dir
        self.xml_mtime = None
        self.info = {'dev_count':0,
                     'disk_count': 0,
                     'diskgroup_count': 0,
                     'view_count': 0,
                     'ig_count': 0,
                     'sg_count': 0,
                     'pg_count': 0}
        self.ig = {}
        self.pg = {}
        self.sg = {}
        self.dev = {}
        self.disk = {}
        self.diskgroup = {}
        self.view = {}
        self.director = {}

        if self.dump_outdated():
            self.load_xml()
        elif preload_data:
            self.get_sym_all()

    def load_xml(self):
            self.sym_info()
            self.sym_diskgroup()
            self.sym_disk()
            self.sym_dev()
            self.sym_devrdfa()
            self.sym_ficondev()
            self.sym_meta()
            self.sym_view()
            self.sym_dir()

            # restore mtime changed by the parser
            os.utime(os.path.join(self.xml_dir, 'sym_info'),
                     (-1, self.xml_mtime))

            self.dump('info.dump', self.info)
            self.dump('ig.dump', self.ig)
            self.dump('pg.dump', self.pg)
            self.dump('sg.dump', self.sg)
            self.dump('dev.dump', self.dev)
            self.dump('disk.dump', self.disk)
            self.dump('diskgroup.dump', self.diskgroup)
            self.dump('view.dump', self.view)
            self.dump('dir.dump', self.view)

    def dump_outdated(self):
        xml = os.path.join(self.xml_dir, 'sym_info')
        dump = os.path.join(self.xml_dir, 'info.dump')
        self.xml_mtime = os.stat(xml).st_mtime
        dump_mtime = os.stat(dump).st_mtime
        module_mtime = os.stat(__file__).st_mtime
        if self.xml_mtime > dump_mtime:
            return True
        if module_mtime > dump_mtime:
            return True
        return False

    def load(self, f):
        p = os.path.join(self.xml_dir, f)
        fd = open(p, 'r')
        s = pickle.load(fd)
        fd.close()
        return s

    def dump(self, f, o):
        p = os.path.join(self.xml_dir, f)
        fd = open(p, 'w')
        pickle.dump(o, fd)
        fd.close()

    def prefix(self, text=""):
        if len(text) == 0:
            return ""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            lines[i] = "sym[%s].%s"%(self.info['symid'], line)
        return lines

    def __str__(self):
        self.get_sym_all()
        l = []
        for key in self.info:
            l += self.prefix('%s: %s'%(key,self.info[key]))
        for dg in self.diskgroup:
            l += self.prefix(str(self.diskgroup[dg]))
        for disk in self.disk:
            l += self.prefix(str(self.disk[disk]))
        for dev in self.dev:
            l += self.prefix(str(self.dev[dev]))
        for view in self.view:
            l += self.prefix(str(self.view[view]))
        for director in self.director:
            l += self.prefix(str(self.director[director]))
        return '\n'.join(l)

    def __iadd__(self, o):
        if isinstance(o, VmaxDiskGroup):
            self.diskgroup[int(o.info['disk_group_number'])] = o
            self.info['diskgroup_count'] += 1
        elif isinstance(o, VmaxDisk):
            self.disk[o.id] = o
            self.info['disk_count'] += 1
            self.diskgroup[int(o.info['disk_group'])] += o
        elif isinstance(o, VmaxFiconDev):
            dev = self.dev[o.devname]
            dev.ficon = True
            dev.view.append('Mainframe')
            dg = dev.diskgroup
            if dg is not None:
	        self.diskgroup[dg].add_masked_dev(dev)
        elif isinstance(o, VmaxDevRdf):
            self.dev[o.devname] += o
        elif isinstance(o, VmaxDev):
            disk_id = o.backend[0]['id']
            if disk_id in self.disk:
                disk = self.disk[disk_id]
                o.diskgroup = int(disk.info['disk_group'])
                o.diskgroup_name = disk.info['disk_group_name']
                self.diskgroup[o.diskgroup] += o
            else:
                # VDEV
                pass
            self.dev[o.info['dev_name']] = o
            self.info['dev_count'] += 1
        elif isinstance(o, VmaxView):
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
                o.dev.append(dev)
                dg = dev.diskgroup
                if dg is None:
                    # VDEV
                    continue
                self.diskgroup[dg].add_masked_dev(dev)
        elif isinstance(o, VmaxDirector):
           self.director[o.info['id']] = o
        return self

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
        tree = self.xmltree('sym_diskgroup_info')
        self.diskgroup = {}
        for e in tree.getiterator('Disk_Group'):
            self += VmaxDiskGroup(e)
        del tree

    def sym_disk(self):
        tree = self.xmltree('sym_disk_info')
        for e in tree.getiterator('Disk'):
            self += VmaxDisk(e)
        del tree

    def sym_dev(self):
        tree = self.xmltree('sym_dev_info')
        for e in tree.getiterator('Device'):
            self += VmaxDev(e)
        del tree

    def sym_devrdfa(self):
        tree = self.xmltree('sym_devrdfa_info')
        for e in tree.getiterator('Device'):
            self += VmaxDevRdf(e)
        del tree

    def sym_ficondev(self):
        tree = self.xmltree('sym_ficondev_info')
        for e in tree.getiterator('Device'):
            self += VmaxFiconDev(e)
        del tree

    def sym_meta(self):
        tree = self.xmltree('sym_meta_info')
        for e in tree.getiterator('Device'):
            o = VmaxMeta(e)
            self.dev[o.dev_name] += o
        del tree

    def sym_view(self):
        tree = self.xmltree('sym_view_aclx')
        for e in tree.getiterator('View_Info'):
            self += VmaxView(e)
        del tree

    def sym_dir(self):
        tree = self.xmltree('sym_dir_info')
        for e in tree.getiterator('Microcode'):
            for el in list(e):
                self.info[el.tag] = el.text
        for e in tree.getiterator('Symmwin'):
            for el in list(e):
                self.info['symmwin_'+el.tag] = el.text
        for e in tree.getiterator('Director'):
            self += VmaxDirector(e)
        del tree

    """ Accessors
    """
    def get_sym_info(self):
        if 'symid' not in self.info:
            self.info = self.load('info.dump')
        return self.info

    def get_sym_diskgroup(self):
        if len(self.diskgroup) == 0:
            self.diskgroup = self.load('diskgroup.dump')
        return self.diskgroup

    def get_sym_disk(self):
        if len(self.disk) == 0:
            self.disk = self.load('disk.dump')
        return self.disk

    def get_sym_dev(self):
        if len(self.dev) == 0:
            self.dev = self.load('dev.dump')
        return self.dev

    def get_sym_dir(self):
        if len(self.director) == 0:
            self.director = self.load('dir.dump')
        return self.director

    def get_sym_sg(self):
        if len(self.sg) == 0:
            self.sg = self.load('sg.dump')
        return self.sg

    def get_sym_pg(self):
        if len(self.pg) == 0:
            self.pg = self.load('pg.dump')
        return self.pg

    def get_sym_ig(self):
        if len(self.ig) == 0:
            self.ig = self.load('ig.dump')
        return self.ig

    def get_sym_view(self):
        if len(self.view) == 0:
            self.view = self.load('view.dump')
        return self.view

    def get_sym_all(self):
        self.get_sym_info()
        self.get_sym_dev()
        self.get_sym_disk()
        self.get_sym_diskgroup()
        self.get_sym_ig()
        self.get_sym_pg()
        self.get_sym_sg()
        self.get_sym_view()
        self.get_sym_dir()

import sys
def main():
    s = Vmax(sys.argv[1])
    print s

if __name__ == "__main__":
    main()

