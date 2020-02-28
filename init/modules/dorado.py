import sys
import os
import json

class Dorado(object):
    def __init__(self, dir=None):
        if dir is None:
            return
        self.dir = dir
        self.name = os.path.basename(dir)
        self.load_system()
        self.load_storagepools()
        self.load_luns()
        self.load_fc_ports()

    def readfile(self, fname):
        fpath = os.path.join(self.dir, fname)
        with open(fpath, 'r') as f:
            buff = f.read()
        return buff

    def load_system(self):
        buff = self.readfile('system')
        self.system = json.loads(buff)

    def load_storagepools(self):
        buff = self.readfile('storagepools')
        self.storagepools = json.loads(buff)

    def load_luns(self):
        buff = self.readfile('luns')
        self.luns = json.loads(buff)

    def load_fc_ports(self):
        buff = self.readfile('fc_ports')
        self.fc_ports = json.loads(buff)

    def __str__(self):
        return json.dumps({
	    "system": self.system,
	    "storagepools": self.storagepools,
	    "luns": self.luns,
	    "fc_ports": self.fc_ports,
	}, indent=4)


def get_dorado(dir=None):
    try:
        return Dorado(dir)
    except:
        return None

def main():
    s = Dorado(sys.argv[1])
    print s

if __name__ == "__main__":
    main()

