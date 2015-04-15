import os
import sys

class Brocade(object):
    def __init__(self, dir=None):
        if dir is None:
            return
        self.dir = dir
        self.name = os.path.basename(dir)
        self.load_switchshow()
        self.load_nsshow()
        self.load_zoneshow()

    def readfile(self, fname):
        fpath = os.path.join(self.dir, fname)
        with open(fpath, 'r') as f:
            buff = f.read()
        return buff

    def load_zoneshow(self):
        """
 alias: DMX0197_8A0
                50:06:04:84:52:A4:F9:47
 alias: Wdms01  10:00:00:00:C9:24:32:8C
 alias: EVA04   50:00:1F:E1:50:21:90:19; 50:00:1F:E1:50:21:90:1F; 
                50:00:1F:E1:50:21:90:1B; 50:00:1F:E1:50:21:90:1D

        """
        self.alias = {}
        self.zone = {}
        self.cfg = None
        effective_cfg_offset = 0
        lines = self.readfile("brocadezoneshow").split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('alias:'):
                l = line.split()
                length = len(l)
                if length == 2:
                    alias = l[-1]
                    port = [lines[i+1].strip().replace(':','').lower()]
                elif length == 3:
                    alias = l[-2]
                    port = [l[-1].replace(':','').lower()]
                elif length == 4:
                    alias = l[1]
                    port = [l[2].replace(':','').replace(';','').lower()]
                    port += [l[3].replace(':','').replace(';','').lower()]
                    _line = lines[i+1]
                    j = i+1
                    while 'alias' not in _line and len(_line) > 0:
                        for w in _line.split():
                            port.append(w.replace(':','').replace(';','').lower())
                        j += 1
                        _line = lines[j]
                else:
                    continue
                self.alias[cfg][alias] = port
            elif line.startswith('Effective configuration:'):
                effective_cfg_offset = i
                break
            elif line.startswith('cfg:'):
                cfg = line.split(':')[-1].strip()
                self.alias[cfg] = {}
        #print self.alias

        """
 zone:  Wzzs01_DMX1370_9B1
                50:06:04:84:52:a6:1e:b8
                10:00:00:00:c9:3a:12:72
        """
        lines = lines[effective_cfg_offset:]
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('zone:'):
                l = line.split()
                zone = l[-1]
                self.zone[zone] = []
                for _line in lines[i+1:]:
                    _line = _line.strip()
                    if _line.startswith('zone:') or len(_line) == 0:
                        break
                    port = _line.replace(':','').lower()
                    self.zone[zone].append(port)
            elif line.startswith('cfg:'):
                self.cfg = line.split(':')[-1].strip()
        #print self.zone


    def load_nsshow(self):
        """
 Type Pid    COS     PortName                NodeName                 TTL(sec)
 N    020f01;      3;50:01:43:80:07:2d:f5:e6;50:01:43:80:07:2d:f5:e7; na
    FC4s: FCP 
    NodeSymb: [33] "QMH2462 FW:v5.04.04 DVR:v9.1.9.26"
    Fabric Port Name: 20:20:00:05:33:40:1e:53 
    Permanent Port Name: 20:11:00:05:33:a0:e6:42
    Port Index: 32
    Share Area: No
    Device Shared in Other AD: No
    Redirect: No 
    Partial: No
        """
        lines = self.readfile("brocadensshow").split('\n')
        for i, line in enumerate(lines):
            if len(line) <= 2:
                continue
            if line[1] != ' ':
                # new entry
                l = line.split(';')
                if len(l) != 5:
                    continue
                portname = l[2].replace(':','')
                continue
            elif line.strip().startswith('Port Index:'):
                index = line.split(':')[-1].strip()
                self.ports[index]['nse'].append(portname)

    def load_switchshow(self):
        lines = self.readfile("brocadeswitchshow").split('\n')
        if len(lines) < 2:
            raise Exception("brocadeswitchshow is empty")
        self.ports = {}
        self.rindex = {}
        start = 0
        for i, line in enumerate(lines):
            if line.startswith("switchName:"):
                self.name = line.split(':')[1].strip().lower()
            elif line.startswith("switchType"):
                self.model = line.split(':')[1].strip()
            elif line.startswith("switchWwn"):
                self.wwn = ''.join(line.split(':')[1:]).strip()
            elif line.startswith("===="):
                start = i + 1
                comment_idx = len(line)
                cols = lines[i-1].split()
                n_cols = len(cols)
                break
        for line in lines[start:]:
            if len(line) < comment_idx:
                continue
            l = line.split()
            if len(l) < n_cols + 1:
                comment = ""
            else:
                comment = " ".join(l[n_cols:])
            a = line[:comment_idx]
            l = a.split()
            port = {
              "Index": "",
              "Slot": "0",
              "Port": "",
              "Type": "",
              "RemotePortName": "",
              "Nego": "",
              "Speed": 0,
              "nse": [],
            }
            for i, col in enumerate(cols):
                if len(l)-1 < i:
                    break
                port[col] = l[i]
            if 'Area' in port:
                port['Index'] = port['Area']
            if len(comment) > 0:
                if 'E-Port' in comment:
                    port['Type'] = 'E-Port'
                elif 'F-Port' in comment:
                    port['Type'] = 'F-Port'
                l = comment.split()
                if len(l) >= 2 and ':' in l[1]:
                    port['RemotePortName'] = l[1].replace(':','').lower()
                elif len(l) >= 3 and ':' in l[2]:
                    port['RemotePortName'] = l[2].replace(':','').lower()
                if "master is Port" in comment:
                    master = comment.split('Port')[-1].strip(')').strip()
                    port['TrunkMaster'] = port['Slot'], master
                elif "master is Slot" in comment:
                    # (Trunk port, master is Slot  1 Port  0 )
                    words = comment.split()
                    i = words.index('Slot')
                    _slot = words[i+1].strip(')').strip()
                    i = words.index('Port')
                    _port = words[i+1].strip(')').strip()
                    port['TrunkMaster'] = _slot, _port
            if port['Speed'] == "AN":
                port['Speed'] = 0
                port['Nego'] = False
            elif port['Speed'].startswith('N'):
                port['Speed'] = int(port['Speed'].replace('N',''))
                port['Nego'] = True
            elif port['Speed'].endswith('G'):
                port['Speed'] = int(port['Speed'].replace('G',''))
                port['Nego'] = False
            self.rindex[port['Slot'], port['Port']] = port['Index']
            self.ports[port['Index']] = port

        # assign slave trunk port remote port name
        # E-Port  (Trunk port, master is Port  3 )
        for port in self.ports.values():
            if "TrunkMaster" not in port:
                continue
            i = port['Index']
            ri = self.rindex[port['TrunkMaster']]
            self.ports[i]['RemotePortName'] = self.ports[ri]['RemotePortName']

    def __str__(self):
        s = "name: %s\n" % self.name
        s += "model: %s\n" % self.model
        s += "wwn: %s\n" % self.wwn
        for d in self.ports.values():
            s += "index %s slot %s port %s: type %s, remote %s, speed %d, nego %s\n"%(str(d['Index']), str(d['Slot']), str(d['Port']), str(d['Type']), str(d['RemotePortName']), d['Speed'], str(d['Nego']))
            for nse in d['nse']:
                s += "  ns entry: %s\n" % nse
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

