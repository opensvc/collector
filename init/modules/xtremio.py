import sys
import os
import json

class Xtremio(object):
    def __init__(self, dir=None):
        if dir is None:
            return
        self.dir = dir
        self.name = os.path.basename(dir)
        self.load_clusters()
        self.load_volumes()
        self.load_targets()

    def readfile(self, fname):
        fpath = os.path.join(self.dir, fname)
        with open(fpath, 'r') as f:
            buff = f.read()
        return buff

    def load_clusters(self):
        buff = self.readfile('clusters_details')
        self.clusters = json.loads(buff)

    def load_volumes(self):
        buff = self.readfile('volumes_details')
        self.volumes = json.loads(buff)

    def load_targets(self):
        buff = self.readfile('targets_details')
        self.targets = json.loads(buff)

    def __str__(self):
        return json.dumps({
	    "clusters": self.clusters,
	    "targets": self.targets,
	    "volumes": self.volumes,
	}, indent=4)


def get_xtremio(dir=None):
    try:
        return Xtremio(dir)
    except:
        return None

def main():
    s = Xtremio(sys.argv[1])
    print s

if __name__ == "__main__":
    main()

