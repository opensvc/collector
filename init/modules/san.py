import copy
import subprocess
import re

r = re.compile('(\d)+')

def tonum(x):
    try:
        return int(x)
    except:
        pass
    try:
        return x.decode('hex')
    except:
        pass
    return 9999

class Viz(object):
    switch_opt = "shape=Mrecord"
    server_opt = "shape=Mrecord"
    array_opt = "shape=Mrecord"
    colors = {
      1: '#ffefb6',
      2: '#fec3ac',
      4: '#ff5e4d',
      8: '#b9121b',
      16: '#6b0d0d',
    }
    color_other = '#999999'

    def __init__(self, d):
        self.data = d

        # global id cache
        self.index = {}
        for i in ('server', 'switch', 'array'):
            for k, data in d[i].items():
                self.index[k] = data['id']

        # port indexing
        self.ports = {}
        for link in d['link'].values():
            if link['tail'] not in self.ports:
                self.ports[link['tail']] = set([])
            self.ports[link['tail']] |= set([link['taillabel']])
            if link['head'] not in self.ports:
                self.ports[link['head']] = set([])
            self.ports[link['head']] |= set([link['headlabel']])
        for k in self.ports:
            self.ports[k] = sorted(list(self.ports[k]-set([''])), key=tonum)

    def html_legend(self):
        s = ""
        for i in sorted(self.colors.keys()):
            s += "<span style='padding:0.2em;border-bottom:solid %s'>%d Gb/s</span>"%(self.colors[i], i)
        s += "<span style='padding:0.2em;border-bottom:solid %s'>%s</span>"%(self.color_other, 'other')
        return "<div>"+s+"</div>"

    def __str__(self):
        s = """
digraph G {
        graph [center rankdir=LR splines=true ranksep=2.5 bgcolor=transparent]
        edge [dir=none]
        node [shape=box fontsize=10]
%(servers)s
%(arrays)s
%(switches)s
%(links)s
}
    """%dict(
         servers=self.fmt_servers(),
         arrays=self.fmt_arrays(),
         switches=self.fmt_switches(),
         links=self.fmt_links(),
        )
        return s

    def write(self, fpath, type="png"):
        dot = fpath + '.dot'
        f = open(dot, 'w')
        f.write(str(self))
        f.close()
        if type == 'dot':
            return dot
        from subprocess import Popen
        cmd = [ 'dot', '-T'+type, '-o', fpath, dot ]
        process = Popen(cmd, stdout=None, stderr=None)
        process.communicate()

    def fmt_servers(self):
        s = ""
        s += "\t{\n\t\trank=min\n"
        for server, data in self.data['server'].items():
            l = []
            if server in self.ports:
                ports = self.ports[server]
            else:
                ports = []
            for i, port in enumerate(ports):
                l.append("<p%s> %s"%(i, port))
            if len(l) == 0:
                continue
            ports = '|'.join(l)
            label = data['label']
            if label is None:
                label = "?"
            if ports is not None:
                label += '|'+'|'.join(l)
            s += """\t\t%s [label="%s" %s]\n"""%(data['id'], label, self.server_opt)
        s += "\t}\n"
        return s

    def fmt_arrays(self):
        s = ""
        s += "\t{\n\t\trank=max\n"
        for array, data in self.data['array'].items():
            l = []
            if array in self.ports:
                ports = self.ports[array]
            else:
                ports = []
            for i, port in enumerate(ports):
                l.append("<p%s> %s"%(i, port))
            if len(l) == 0:
                continue
            ports = '|'.join(l)
            label = data['label']
            if label is None:
                label = "?"
            if ports is not None:
                label += '|'+'|'.join(l)
            s += """\t\t%s [label="%s" %s]\n"""%(data['id'], label, self.array_opt)
        s += "\t}\n"
        return s

    def fmt_switches(self):
        s = ""
        ranks = set([d['rank'] for d in self.data['switch'].values()])
        if len(ranks) == 0:
            return s
        list(ranks).sort()
        for rank in ranks:
            s += "\t{\n\t\trank=same\n"
            for switch, data in self.data['switch'].items():
                l = []
                for i, port in enumerate(self.ports[switch]):
                    l.append("<p%s> %s"%(i, port))
                if len(l) == 0:
                    continue
                ports = '|'.join(l)
                label = data['label']
                if label is None:
                    label = "?"
                if ports is not None:
                    label += '|'+'|'.join(l)
                if data['rank'] != rank:
                    continue
                s += """\t\t%s [label="%s" %s]\n"""%(data['id'], label, self.switch_opt)
            s += "\t}\n"
        return s

    def fmt_links(self):
        s = ""
        for link in self.data['link'].values():
            l = []
            for speed in link['speed']:
                l.append(self.colors[speed])
            color = ':'.join(l)
            if not link['tail'] in self.index or not link['head'] in self.index:
                print "discard", link['tail'], link['head']
                continue
            s += """\t%s:p%s->%s:p%s [color="%s"]\n"""%(
              self.index[link['tail']],
              self.ports[link['tail']].index(link['taillabel']),
              self.index[link['head']],
              self.ports[link['head']].index(link['headlabel']),
              color,
            )
        return s

if __name__ == "__main__":
    d = {
      'server': {
        'lixbia14': {
          'id': 's1',
          'label': 'lixbia14',
        },
      },
      'array': {
        '000290101523': {
          'id': 'a1',
          'label': '000290101523',
        },
      },
      'switch': {
        '100000051e09abbc': {
          'id': 'sw1',
          'rank': 2,
          'label': 'director07',
        },
        '100000051e36258c': {
          'id': 'sw2',
          'rank': 1,
          'label': 'f1blade12',
        },
      },
      'link': {
        'l1': {
          'count': 1,
          'tail': 'lixbia14',
          'taillabel': '500143800221fa0c',
          'head': '100000051e09abbc',
          'headlabel': '6',
        },
        'l2': {
          'count': 1,
          'tail': '100000051e09abbc',
          'taillabel': '17',
          'head': '100000051e36258c',
          'headlabel': '114',
        },
        'l3': {
          'count': 1,
          'tail': '100000051e36258c',
          'taillabel': '16',
          'head': '000290101523',
          'headlabel': '5006048452a644d7',
        },
      },
    }
    #o = Viz(d)
    #print o
    #o.write("/tmp/foo.png")

    d = {'array': {'000290101523': {'id': 'a0', 'label': '000290101523'}},
'link': {'100000051e36266e-5006048c52a644f9': {'count': 1, 'taillabel': '117',
'tail': '100000051e36266e', 'head': '000290101523', 'headlabel':
'5006048c52a644f9'}, '100000051e36258c-50060b00006a0990': {'count': 1,
'taillabel': '50060b00006a0990', 'tail': 'lixbi843', 'head':
'100000051e36258c', 'headlabel': '143'}, '100000051e055f2c-100000051e36258c':
{'count': 1, 'taillabel': '143', 'tail': '100000051e36258c', 'head':
'100000051e055f2c', 'headlabel': '17'}, '100000051e36258c-5006048452a644d7':
{'count': 1, 'taillabel': '16', 'tail': '100000051e36258c', 'head':
'000290101523', 'headlabel': '5006048452a644d7'},
'100000051e09adf4-100000051e36266e': {'count': 1, 'taillabel': '31', 'tail':
'100000051e36266e', 'head': '100000051e09adf4', 'headlabel': '17'},
'100000051e05603f-100000051e36266e': {'count': 1, 'taillabel': '31', 'tail':
'100000051e36266e', 'head': '100000051e05603f', 'headlabel': '17'},
'100000051e0f87f0-100000051e36258c': {'count': 1, 'taillabel': '143', 'tail':
'100000051e36258c', 'head': '100000051e0f87f0', 'headlabel': '17'},
'100000051e36266e-5006048452a644d8': {'count': 1, 'taillabel': '16', 'tail':
'100000051e36266e', 'head': '000290101523', 'headlabel': '5006048452a644d8'},
'100000051e36266e-50060b00006a049a': {'count': 1, 'taillabel':
'50060b00006a049a', 'tail': 'lixbi843', 'head': '100000051e36266e',
'headlabel': '31'}, '100000051e09abbc-100000051e36258c': {'count': 1,
'taillabel': '143', 'tail': '100000051e36258c', 'head': '100000051e09abbc',
'headlabel': '17'}, '100000051e36266e-100000051e573b16': {'count': 1,
'taillabel': '31', 'tail': '100000051e36266e', 'head': '100000051e573b16',
'headlabel': '17'}, '100000051e36258c-50060b00006a0498': {'count': 1,
'taillabel': '50060b00006a0498', 'tail': 'lixbi843', 'head':
'100000051e36258c', 'headlabel': '31'}, '100000051e36266e-50060b00006a0992':
{'count': 1, 'taillabel': '50060b00006a0992', 'tail': 'lixbi843', 'head':
'100000051e36266e', 'headlabel': '143'}, '100000051e36258c-5006048c52a644f6':
{'count': 1, 'taillabel': '117', 'tail': '100000051e36258c', 'head':
'000290101523', 'headlabel': '5006048c52a644f6'},
'100000051e09adf0-100000051e36266e': {'count': 1, 'taillabel': '31', 'tail':
'100000051e36266e', 'head': '100000051e09adf0', 'headlabel': '17'},
'100000051e09adeb-100000051e36266e': {'count': 1, 'taillabel': '31', 'tail':
'100000051e36266e', 'head': '100000051e09adeb', 'headlabel': '17'},
'100000051e09ae3e-100000051e36258c': {'count': 1, 'taillabel': '143', 'tail':
'100000051e36258c', 'head': '100000051e09ae3e', 'headlabel': '17'},
'100000051e09aedc-100000051e36258c': {'count': 1, 'taillabel': '143', 'tail':
'100000051e36258c', 'head': '100000051e09aedc', 'headlabel': '17'}}, 'switch':
{'100000051e36266e': {'id': 'sw6', 'rank': 1, 'label': 'director08'},
'100000051e36258c': {'id': 'sw0', 'rank': 1, 'label': 'director07'}}, 'server':
{'lixbi843': {'id': 's0', 'label': 'lixbi843'}}}

    o = Viz(d)
    print o
