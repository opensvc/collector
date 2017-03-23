import os
import json

class Freenas(object):
    def __init__(self, dir=None):
        if dir is None:
            return
        self.dir = dir
        self.name = os.path.basename(dir)
        self.load_version()
        self.load_volumes()
        self.load_iscsi_targets()
        self.load_iscsi_extents()
        self.load_iscsi_targettoextents()

    def fpath(self, fname):
        return os.path.join(self.dir, fname)

    def readfile(self, fname):
        fpath = self.fpath(fname)
        with open(fpath, 'r') as f:
            buff = f.read()
        return buff

    def load_version(self):
        buff = self.readfile('version')
        print buff
        self.version = json.loads(buff)

    def load_volumes(self):
        buff = self.readfile('volumes')
        self.volumes = json.loads(buff)

    def load_iscsi_targets(self):
        buff = self.readfile('iscsi_targets')
        try:
            self.iscsi_targets = json.loads(buff)
        except Exception as exc:
            print "failed to load iscsi_targets:", str(exc)
            self.iscsi_targets = []

    def load_iscsi_extents(self):
        buff = self.readfile('iscsi_extents')
        try:
            self.iscsi_extents = json.loads(buff)
        except Exception as exc:
            print "failed to load iscsi_extents:", str(exc)
            self.iscsi_extents = []

    def load_iscsi_targettoextents(self):
        buff = self.readfile('iscsi_targettoextents')
        try:
            self.iscsi_targettoextents = json.loads(buff)
        except Exception as exc:
            print "failed to load iscsi_targettoextents:", str(exc)
            self.iscsi_targettoextents = []

    def __str__(self):
        s = json.dumps(self.version, indent=4)
        s += json.dumps(self.volumes, indent=4)
        s += json.dumps(self.iscsi_targets, indent=4)
        s += json.dumps(self.iscsi_extents, indent=4)
        s += json.dumps(self.iscsi_targettoextents, indent=4)
        return s


def get_freenas(dir=None):
    try:
        return Freenas(dir)
    except:
        return None

import sys
def main():
    s = Freenas(sys.argv[1])
    print s

if __name__ == "__main__":
    main()

