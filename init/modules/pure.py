import sys
import os
import json

class Pure(object):
    def __init__(self, dir=None):
        if dir is None:
            return
        self.dir = dir
        self.name = os.path.basename(dir)
        self.load_arrays()
        self.load_hardware()
        self.load_pods()
        self.load_volumegroups()
        self.load_volumes()
        self.load_ports()

    def readfile(self, fname):
        fpath = os.path.join(self.dir, fname)
        with open(fpath, 'r') as f:
            buff = f.read()
        return buff

    def load_arrays(self):
        buff = self.readfile('arrays')
        self.arrays = json.loads(buff)

    def load_volumes(self):
        buff = self.readfile('volumes')
        self.volumes = json.loads(buff)

    def load_volumegroups(self):
        buff = self.readfile('volumegroups')
        self.volumegroups = json.loads(buff)

    def load_hardware(self):
        buff = self.readfile('hardware')
        self.hardware = json.loads(buff)

    def load_pods(self):
        buff = self.readfile('pods')
        self.pods = json.loads(buff)

    def load_ports(self):
        buff = self.readfile('ports')
        self.ports = json.loads(buff)

    def __str__(self):
        return json.dumps({
	    "arrays": self.arrays,
	    "hardware": self.hardware,
	    "pods": self.pods,
	    "volumes": self.volumes,
	    "volumegroups": self.volumegroups,
	    "ports": self.ports,
	}, indent=4)


def get_pure(dir=None):
    try:
        return Pure(dir)
    except:
        return None

def main():
    s = Pure(sys.argv[1])
    print s

if __name__ == "__main__":
    main()

