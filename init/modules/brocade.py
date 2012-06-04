import os

class Brocade(object):
    def __init__(self, dir=None):
        if dir is None:
            return
        self.dir = dir
        self.name = os.path.basename(dir)
        self.load_switchshow()

    def readfile(self, fname):
        fpath = os.path.join(self.dir, fname)
        with open(fpath, 'r') as f:
            buff = f.read()
        return buff

    def load_switchshow(self):
        lines = self.readfile("brocadeswitchshow").split('\n')
        self.ports = []
        for i, line in enumerate(lines):
            if line.startswith("switchName:"):
                self.name = line.split(':')[1].strip().lower()
            elif line.startswith("switchType"):
                self.model = line.split(':')[1].strip()
            elif line.startswith("===="):
                start = i + 1
                cols = lines[i-1].split()
                n_cols = len(cols)
                break
        for line in lines[start:]:
            l = line.split()
            if len(l) < n_cols:
                continue
            port = {}
            for i, col in enumerate(cols):
                port[col] = l[i]
            if len(l) > n_cols:
                l = l[i+1:]
                if 'E-Port' in l:
                    port['Type'] = 'E-Port'
                if 'F-Port' in l:
                    port['Type'] = 'F-Port'
                if len(l) == 2 and ':' in l[1]:
                    port['RemotePortName'] = l[1].replace(':','').lower()
            if 'Slot' not in port:
                port['Slot'] = ""
            if 'Type' not in port:
                port['Type'] = ""
            if 'RemotePortName' not in port:
                port['RemotePortName'] = ""
            port['Nego'] = ""
            if port['Speed'].startswith('N'):
                port['Speed'] = int(port['Speed'].replace('N',''))
                port['Nego'] = True
            elif port['Speed'].endswith('G'):
                port['Speed'] = int(port['Speed'].replace('G',''))
                port['Nego'] = False
            else:
                port['Speed'] = 0
            self.ports.append(port)

    def __str__(self):
        s = "name: %s\n" % self.name
        s += "model: %s\n" % self.model
        for d in self.ports:
            s += "slot %s port %s: type %s, remote %s, speed %d, nego %s\n"%(str(d['Slot']), str(d['Port']), str(d['Type']), str(d['RemotePortName']), d['Speed'], str(d['Nego']))
        return s


def get_brocade(dir=None):
    try:
        return Brocade(dir)
    except:
        return None

import sys
def main():
    s = Brocade(sys.argv[1])
    print s

if __name__ == "__main__":
    main()

