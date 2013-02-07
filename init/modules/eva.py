import os
from xml.etree.ElementTree import ElementTree, SubElement

class Eva(object):
    def __init__(self, xml_dir=None):
        if xml_dir is None:
            return
        self.xml_dir = xml_dir
        self.name = os.path.basename(xml_dir)
        self.get_controller()
        self.get_disk_group()
        self.get_vdisk()
        self.get_snapshots()

    def xmltree(self, xml):
        f = os.path.join(self.xml_dir, xml)
        tree = ElementTree()
        tree.parse(f)
        return tree

    def get_controller(self):
        tree = self.xmltree('controller')
        self.controllermainmemory = 0
        self.ports = []
        for e in tree.getiterator('object'):
            self.modelnumber = e.find("modelnumber").text
            self.controllermainmemory += int(e.find("controllermainmemory").text)
            self.firmwareversion = e.find("firmwareversion").text
            self.ports += [m.text for m in e.findall("hostports/hostport/wwid")]
            self.ports = map(lambda x: x.replace(' ', '').lower(), self.ports)
        del tree

    def get_disk_group(self):
        tree = self.xmltree('disk_group')
        self.dg = []
        for e in tree.getiterator('object'):
            dg = {}
            dg['diskgroupname'] = e.find("diskgroupname").text
            dg['totalstoragespace'] = int(e.find("totalstoragespace").text) / 1024 / 2
            dg['usedstoragespace'] = int(e.find("usedstoragespace").text) / 1024 / 2
            dg['freestoragespace'] = dg['totalstoragespace'] - dg['usedstoragespace']
            self.dg.append(dg)
        del tree

    def get_vdisk(self):
        tree = self.xmltree('vdisk')
        self.vdisk = {}
        for e in tree.getiterator('object'):
            d = {}
            d['wwlunid'] = e.find("wwlunid").text.replace('-', '')
            d['objectid'] = e.find('objectid').text
            d['objecttype'] = e.find('objecttype').text
            if d['objecttype'] == 'snapshot':
                s = e.find('sharinginformation/parentvdiskid')
                if s is not None:
                    d['parentvdiskid'] = s.text
            d['objectname'] = e.find('objectname').text.lstrip("\\Virtual Disk\\").rstrip("\\ACTIVE")
            try:
                d['allocatedcapacity'] = int(e.find('allocatedcapacityblocks').text)//2//1024
            except:
                continue
            d['redundancy'] = e.find('redundancy').text
            d['diskgroupname'] = e.find('diskgroupname').text.split('\\')[-1]
            d['alloc'] = d['allocatedcapacity']
            if d['redundancy'] == 'vraid0':
                d['backend_alloc'] = d['alloc']
            elif d['redundancy'] in ('vraid1', 'vraid10'):
                d['backend_alloc'] = d['alloc'] * 2
            elif d['redundancy'] == 'vraid5':
                d['backend_alloc'] = int(1.*d['alloc']*5/4)
            elif d['redundancy'] == 'vraid6':
                d['backend_alloc'] = int(1.*d['alloc']*6/4)

            self.vdisk[d['objectid']] = d
        del tree

    def get_snapshots(self):
        for d in self.vdisk.values():
            if d['objecttype'] != 'snapshot' or 'parentvdiskid' not in d:
                continue
            _d = d
            while True:
                pid = _d['parentvdiskid']
                p = self.vdisk[pid]
                if p['objecttype'] != 'snapshot':
                    d['allocatedcapacity'] = p['allocatedcapacity']
                    break
                else:
                    _d = p

    def __str__(self):
        s = "name: %s\n" % self.name
        s += "modelnumber: %s\n" % self.modelnumber
        s += "controllermainmemory: %d\n" % self.controllermainmemory
        s += "firmwareversion: %s\n" % self.firmwareversion
        s += "ports: %s\n"%','.join(self.ports)
        for dg in self.dg:
            s += "dg %s: free %s MB\n"%(dg['diskgroupname'], str(dg['freestoragespace']))
            s += "dg %s: used %s MB\n"%(dg['diskgroupname'], str(dg['usedstoragespace']))
            s += "dg %s: total %s MB\n"%(dg['diskgroupname'], str(dg['totalstoragespace']))
        for d in self.vdisk.values():
            s += "vdisk %s: size %s GB\n"%(d['wwlunid'], str(d['allocatedcapacity']))
        return s


def get_eva(xml_dir=None):
    try:
        return Eva(xml_dir)
    except:
        return None

import sys
def main():
    s = Eva(sys.argv[1])
    print s

if __name__ == "__main__":
    main()

