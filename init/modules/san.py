import copy
import subprocess

class Viz(object):
    switch_opt = ""
    server_opt = "shape=plaintext"
    array_opt = "shape=plaintext"

    def __init__(self, d):
        self.data = d

        # global id cache
        self.index = {}
        for i in ('server', 'switch', 'array'):
            for k, data in d[i].items():
                self.index[k] = data['id']

    def __str__(self):
        s = """
digraph G {
        graph [center rankdir=LR splines=false nodesep=1 ranksep=1 bgcolor=transparent]
        edge [dir=none]
        node [shape=box]
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
            s += """\t\t%s [label="%s" %s]\n"""%(data['id'], data['label'], self.server_opt)
        s += "\t}\n"
        return s

    def fmt_arrays(self):
        s = ""
        s += "\t{\n\t\trank=max\n"
        for array, data in self.data['array'].items():
            s += """\t\t%s [label="%s" %s]\n"""%(data['id'], data['label'], self.array_opt)
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
                if data['rank'] != rank:
                    continue
                s += """\t\t%s [label="%s" %s]\n"""%(data['id'], data['label'], self.switch_opt)
            s += "\t}\n"
        return s

    def fmt_links(self):
        s = ""
        linkcolor = "#dd0000"
        print self.index
        for link in self.data['link'].values():
            l = []
            for i in range(link['count']):
                l.append(linkcolor)
            color = ':'.join(l)
            if not link['tail'] in self.index or not link['head'] in self.index:
                print "discard", link['tail'], link['head']
                continue
            s += """\t%s->%s [color="%s" headlabel="%s" taillabel="%s" fontsize=8]\n"""%(
              self.index[link['tail']],
              self.index[link['head']],
              color,
              link['headlabel'],
              link['taillabel'],
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
'link': {'100000051e36266e-5006048c52a644f9': {'count': 8, 'taillabel': '117',
'tail': '100000051e36266e', 'head': 'a0', 'headlabel': '5006048c52a644f9'},
'100000051e36258c-50060b00006a0990': {'count': 1, 'taillabel': '', 'tail':
'50060b00006a0990', 'head': '100000051e36258c', 'headlabel': '143'},
'100000051e055f2c-100000051e36258c': {'count': 2, 'taillabel': '', 'tail':
'100000051e36258c', 'head': '100000051e055f2c', 'headlabel': '17'},
'100000051e36258c-5006048452a644d7': {'count': 8, 'taillabel': '16', 'tail':
'100000051e36258c', 'head': 'a0', 'headlabel': '5006048452a644d7'},
'100000051e09adf4-100000051e36266e': {'count': 2, 'taillabel': '', 'tail':
'100000051e36266e', 'head': '100000051e09adf4', 'headlabel': '17'},
'100000051e05603f-100000051e36266e': {'count': 2, 'taillabel': '', 'tail':
'100000051e36266e', 'head': '100000051e05603f', 'headlabel': '17'},
'100000051e0f87f0-100000051e36258c': {'count': 2, 'taillabel': '', 'tail':
'100000051e36258c', 'head': '100000051e0f87f0', 'headlabel': '17'},
'100000051e36266e-5006048452a644d8': {'count': 3, 'taillabel': '16', 'tail':
'100000051e36266e', 'head': 'a0', 'headlabel': '5006048452a644d8'},
'100000051e36266e-50060b00006a049a': {'count': 1, 'taillabel': '', 'tail':
'50060b00006a049a', 'head': '100000051e36266e', 'headlabel': '31'},
'100000051e09abbc-100000051e36258c': {'count': 2, 'taillabel': '', 'tail':
'100000051e36258c', 'head': '100000051e09abbc', 'headlabel': '17'},
'100000051e36266e-100000051e573b16': {'count': 2, 'taillabel': '', 'tail':
'100000051e36266e', 'head': '100000051e573b16', 'headlabel': '17'},
'100000051e36258c-50060b00006a0498': {'count': 1, 'taillabel': '', 'tail':
'50060b00006a0498', 'head': '100000051e36258c', 'headlabel': '31'},
'100000051e36266e-50060b00006a0992': {'count': 1, 'taillabel': '', 'tail':
'50060b00006a0992', 'head': '100000051e36266e', 'headlabel': '143'},
'100000051e09aedc-100000051e36258c': {'count': 2, 'taillabel': '', 'tail':
'100000051e36258c', 'head': '100000051e09aedc', 'headlabel': '17'},
'100000051e09adf0-100000051e36266e': {'count': 2, 'taillabel': '', 'tail':
'100000051e36266e', 'head': '100000051e09adf0', 'headlabel': '17'},
'100000051e09adeb-100000051e36266e': {'count': 2, 'taillabel': '', 'tail':
'100000051e36266e', 'head': '100000051e09adeb', 'headlabel': '17'},
'100000051e09ae3e-100000051e36258c': {'count': 2, 'taillabel': '', 'tail':
'100000051e36258c', 'head': '100000051e09ae3e', 'headlabel': '17'},
'100000051e36258c-5006048c52a644f6': {'count': 3, 'taillabel': '117', 'tail':
'100000051e36258c', 'head': 'a0', 'headlabel': '5006048c52a644f6'}}, 'switch':
{'100000051e36266e': {'id': 'sw6', 'rank': 2, 'label': 'director08'},
'100000051e36258c': {'id': 'sw0', 'rank': 2, 'label': 'director07'}}, 'server':
{'lixbi843': {'id': 's0', 'label': 'lixbi843'}}}
    o = Viz(d)
    print o
