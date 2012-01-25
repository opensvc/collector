import os
from xml.etree.ElementTree import ElementTree, SubElement

class Eva(object):
    def __init__(self, xml_dir=None):
        if xml_dir is None:
            return
        self.xml_dir = xml_dir
        self.name = os.path.basename(xml_dir)
        self.controller()
        self.disk_group()
        self.vdisk()

    def xmltree(self, xml):
        f = os.path.join(self.xml_dir, xml)
        tree = ElementTree()
        tree.parse(f)
        return tree

    def controller(self):
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

    def disk_group(self):
        tree = self.xmltree('disk_group')
        self.dg = []
        for e in tree.getiterator('object'):
            dg = {}
            dg['diskgroupname'] = e.find("diskgroupname").text
            dg['totalstoragespacegb'] = float(e.find("totalstoragespacegb").text)
            dg['usedstoragespacegb'] = float(e.find("usedstoragespacegb").text)
            dg['freestoragespacegb'] = dg['totalstoragespacegb'] - dg['usedstoragespacegb']
            self.dg.append(dg)
        del tree

    def vdisk(self):
        tree = self.xmltree('vdisk')
        self.vdisk = []
        for e in tree.getiterator('object'):
            d = {}
            d['wwlunid'] = e.find("wwlunid").text.replace('-', '')
            d['objectid'] = e.find('objectid').text
            d['allocatedcapacity'] = int(e.find('allocatedcapacity').text)
            d['redundancy'] = e.find('redundancy').text
            d['diskgroupname'] = e.find('diskgroupname').text.split('\\')[-1]
            self.vdisk.append(d)
        del tree

    def __str__(self):
        s = "name: %s\n" % self.name
        s += "modelnumber: %s\n" % self.modelnumber
        s += "controllermainmemory: %d\n" % self.controllermainmemory
        s += "firmwareversion: %s\n" % self.firmwareversion
        s += "ports: %s\n"%','.join(self.ports)
        for dg in self.dg:
            s += "dg %s: free %s\n"%(dg['diskgroupname'], str(dg['freestoragespacegb']))
        for d in self.vdisk:
            s += "vdisk %s: size %s\n"%(d['wwlunid'], str(d['allocatedcapacity']))
        return s


def get_eva(xml_dir=None):
    try:
        return Eva(xml_dir)
    except:
        return None

import sys
def main():
    s = get_eva(sys.argv[1])
    print s

if __name__ == "__main__":
    main()

