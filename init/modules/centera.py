import os
from xml.etree.ElementTree import ElementTree, SubElement

class Centera(object):
    def __init__(self, dir=None):
        if dir is None:
            return
        self.dir = dir
        self.model = "Centera"
        self.cache = 0
        self.firmware = ""
        self.name = os.path.basename(os.path.realpath(dir))
        f = os.path.join(dir, 'discover.xml')
        self.tree = ElementTree()
        self.tree.parse(f)
        self.load()

    def load(self):
        self.array_name = self.name
        self.cache = 0
        self.pool = []
        self.profiles = {}
        self.load_info()
        self.load_app()
        self.load_pool()

    def load_info(self):
        self.serial = self.tree.find("cluster/clusterIdentification").get("serialNumber")
        self.firmware = self.tree.find("cluster/clusterServiceSettings").get("activeSoftwareVersion")

    def load_app(self):
        for e in self.tree.findall("cluster/registeredApplicationList/application"):
            profile = e.get("profile")
            app = {
              "hostname": e.get("hostname"),
            }
            if profile not in self.profiles:
                self.profiles[profile] = [app]
            else:
                self.profiles[profile] += [app]

    def load_pool(self):
        for e in self.tree.findall("cluster/poolList/pool"):
            pool = {
              "profiles": [],
              "hostnames": set([])
            }
            identification = e.find("poolIdentification")
            pc = e.find("poolCapacity")
            pool["name"] = identification.get("name")
            pool["id"] = identification.get("id")
            pool["used"] = int(pc.get("usedCapacity")) / 1024 / 1024
            pool["free"] = int(pc.get("hardStopFreeCapacity")) / 1024 / 1024
            pool["size"] = pool["used"] + pool["free"]
            for p_ref in e.findall("profileRefList"):
                _p_ref = p_ref.find("profileRef")
                if _p_ref is None:
                    continue
                p_ref_name = _p_ref.get("name")
                pool["profiles"].append(p_ref_name)
                if p_ref_name in self.profiles:
                    pool["hostnames"] |= set([a["hostname"].lower() for a in self.profiles[p_ref_name]])
            self.pool.append(pool)


    def __str__(self):
        s = "name: %s\n" % self.name
        s += "model: %s\n" % self.model
        s += "cache: %d\n" % self.cache
        s += "firmware: %s\n" % self.firmware
        for d in self.pool:
            s += "pool %s: size %d MB, used %d MB, free %d MB\n"%(d['name'], d['size'], d['used'], d['free'])
            s += " users:\n"
            for h in d["hostnames"]:
                s += "  %s\n" % h
        return s


def get_centera(dir=None):
    try:
        return Centera(dir)
    except:
        return None

def main():
    import sys
    s = Centera(sys.argv[1])
    print s

if __name__ == "__main__":
    main()


