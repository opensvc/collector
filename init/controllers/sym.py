import os
import re
from subprocess import *
from xml.etree.ElementTree import ElementTree, SubElement

symmetrix = local_import('symmetrix', reload=True)
config = local_import('config', reload=True)

@auth.requires_login()
def index():
    """
    Format an upload form and a list of known symmetrix arrays.
    Each array can be drilled-down (ajax)
    """
    form = SQLFORM(db.sym_upload,
                   fields=['archive'],
                   col3={'archive': """An archive produced from the 'se' directory of an emcgrab file tree by the command 'tar cf - */*bin */*aclx *bin | gzip -c >foo.tar.gz'"""},
                   labels={'archive': 'archive'},
           )
    if form.accepts(request.vars, session):
        try:
            batch_files()
            response.flash = T('file uploaded')
        except:
            import sys
            e = sys.exc_info()
            response.flash = str(e[1])

    import glob
    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
    pattern = "[0-9]*"
    sym_dirs = glob.glob(os.path.join(dir, pattern))
    syms = []
    perms = _domain_perms().split('|')

    for d in sym_dirs:
        if '%' not in perms and os.path.basename(d) not in perms:
            continue
        d = sym_info(os.path.basename(d))
        if d is not None:
            syms.append(d)

    return dict(syms=syms, form=form)

def write_csv(fname, buff):
    try:
        f = open(fname, 'w')
        f.write(buff)
        f.close()
    except:
        return []
    return [fname]

def write_all_csv(dir):
    files = []
    files += write_csv(os.path.join(dir, 'sym_dev.csv'), _sym_dev_csv())
    files += write_csv(os.path.join(dir, 'sym_disk.csv'), _sym_disk_csv())
    return files

@auth.requires_login()
def sym_all_csv():
    """
    Create a tarball containing all data in csv format for a given symid.
    """
    import os
    import tarfile
    import tempfile
    import gluon.contenttype
    dir = tempfile.mkdtemp()
    files = write_all_csv(dir)
    olddir = os.getcwd()
    os.chdir(dir)
    try:
        tarpath = "sym_csv.tar"
        tar = tarfile.open(tarpath, "w")
        for f in files:
            tar.add(os.path.basename(f))
        tar.close()
        response.headers['Content-Type']=gluon.contenttype.contenttype('.tar')
        f = open(tarpath, 'r')
        buff = f.read()
        f.close()
        for f in files:
            os.unlink(os.path.basename(f))
        os.unlink(tarpath)
    except:
        pass
    os.chdir(olddir)
    os.rmdir(dir)
    return buff

def html_diskgroup(dg):
     """
     Format diskgroup information.
     - disk composition
     - global ressource usage
     - per-size device usage
     """
     l = []
     for key in dg.diskcount:
         if len(key) == 3:
             size, tech, speed = key
             spare = None
         else:
             size, tech, speed, spare = key
         s = '%d x %d GB %s rpm %s'%(dg.diskcount[key],
                                     int(size)//1024, speed, tech)
         if spare is not None:
            sp = SPAN('spare', _class='sym_highlight')
         else:
            sp = SPAN()
         l.append(SPAN(s, sp))
     dev_count = len(dg.dev)
     masked_dev_count = len(dg.masked_dev)
     if dev_count != 0:
         dev_usage = "%d%%"%int(100*masked_dev_count/dev_count)
     else:
         dev_usage = 'n/a'
     if dg.total != 0:
         usage = "%d%%"%int(100*dg.used/dg.total)
     else:
         usage = 'n/a'

     m = []
     for size in sorted(dg.dev_by_size):
         if size in dg.masked_dev_by_size:
             used = len(dg.masked_dev_by_size[size])
         else:
             used = 0
         total = len(dg.dev_by_size[size])
         free = total - used
         if total != 0:
             pct = '%d%%'%int(100*used/total)
         else:
             pct = 'n/a'
         line = TR(
                  TH('%d'%size,' ',T('MB'), _class='numeric'),
                  TD(free, _class='numeric'),
                  TD(used, _class='numeric'),
                  TD(total, _class='numeric'),
                  TD(pct, _class='numeric'),
                )
         m.append(line)

     if dev_count == 0:
         table_usage = SPAN()
     else:
         table_usage = DIV(
            TABLE(
              TR(
                TH(),
                TH(T('GB')),
                TH('dev'),
              ),
              TR(
                TH('free'),
                TD((dg.total-dg.used)//1024, _class='numeric'),
                TD(dev_count-masked_dev_count, _class='numeric'),
              ),
              TR(
                TH('used'),
                TD(dg.used//1024, _class='numeric'),
                TD(masked_dev_count, _class='numeric'),
              ),
              TR(
                TH('total'),
                TD(dg.total//1024, _class='numeric'),
                TD(dev_count, _class='numeric'),
              ),
              TR(
                TH('%used'),
                TD(usage, _class='numeric'),
                TD(dev_usage, _class='numeric'),
              ),
            ),
            _class='sym_float',
            _style='width:12em',
          )

     if len(m) == 0:
         table_usage_per_size = SPAN()
     else:
         table_usage_per_size = DIV(
            TABLE(
              TR(
                TH('dev size'),
                TH('free'),
                TH('used'),
                TH('total'),
                TH('%used'),
              ),
              SPAN(map(SPAN, m))
            ),
            _class='sym_float',
            _style='width:20em',
          ),

     d = DIV(
            H3(
              dg.info['disk_group_number'],
              ': ',
              dg.info['disk_group_name'],
            ),
          DIV(
            map(P, l),
            _class='sym_float',
            _style='width:18em',
          ),
          SPAN(table_usage),
          SPAN(table_usage_per_size),
          DIV('', _class='spacer'),
          _class='sym_detail_visible',
         )
     return d

def xmltree(symid, xml):
    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
    f = os.path.join(dir, symid, xml)
    tree = ElementTree()
    tree.parse(f)
    return tree

def mtime(symid, xml):
    import datetime
    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
    f = os.path.join(dir, symid, xml)
    statinfo = os.stat(f)
    d = datetime.datetime.fromtimestamp(statinfo.st_mtime)
    d -= datetime.timedelta(microseconds=d.microsecond)
    return d

def sym_info(symid):
    tree = xmltree(symid, 'sym_info')
    for e in tree.getiterator('Symm_Info'): pass
    d = None
    sym_type = e.find("model").text
    del tree
    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
    p = os.path.join(dir, symid)

    s = symmetrix.get_sym(p)
    if s is None:
        response.flash = T('array model not supported: %s, %s'%(symid, sym_type))
    s.get_sym_info()
    d = s.info
    d['mtime'] = mtime(symid, 'sym_info')
    return d

@auth.requires_login()
def batch_files():
    if not hasattr(config, 'sym_node'):
        raise Exception('no known sym compute node. report to site admins.')

    scp = ['scp', '-o', 'StrictHostKeyChecking=no', '-o', 'ForwardX11=no']
    ssh = ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'ForwardX11=no', '-t']

    rows = db(db.sym_upload.batched != 1).select()
    for row in rows:
        # set double batch run protection flag
        db(db.sym_upload.id==row.id).update(batched=1)

        # create a dir on sym node to host data
        dst_dir = os.path.join(os.sep, 'tmp', os.path.basename(row.archive))
        cmd = ssh + [config.sym_node, 'mkdir', '-p', dst_dir]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            db(db.sym_upload.id==row.id).update(batched=0)
            raise Exception('failed create dir %s sym node'%dst_dir)

        # copy the archive to symnode
        if row.archive == "":
            db(db.sym_upload.id==row.id).delete()
            continue
        src = 'applications'+str(URL(r=request,c='uploads', f=row.archive))
        dst = os.path.join(dst_dir, os.path.basename(row.archive))
        cmd = scp + [src, config.sym_node+':'+dst]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            db(db.sym_upload.id==row.id).update(batched=0)
            raise Exception('failed to transfert the archive to sym node')

        # uncompress archive on symnode
        compress_opts = {'gz': '-z',
                         'Z': '-Z',
                         'tar': '',
                         'bz2': '-j'}
        suffix = src.split('.')[-1]
        if suffix not in compress_opts:
            db(db.sym_upload.id==row.id).update(batched=0)
            raise Exception("%s archive format is not supported. try %s"%(suffix, ', '.join(compress_opts.keys())))

        compress_opt = compress_opts[suffix]
        cmd = ssh + [config.sym_node, 'tar', compress_opt, '-xvf', dst,
                     '-C', dst_dir]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            db(db.sym_upload.id==row.id).update(batched=0)
            raise Exception('failed to explode archive')

        # identify the binfile
        files = out.split('\n')
        binfiles = [f for f in files if f=='symapi_db.bin']
        if len(binfiles) == 0:
            db(db.sym_upload.id==row.id).update(batched=0)
            raise Exception('no bin file found in archive')
        elif len(binfiles) > 1:
            db(db.sym_upload.id==row.id).update(batched=0)
            raise Exception('only one bin file is allowed in archive')
        binfile = os.path.join(dst_dir, binfiles[0])

        # run nodemgr on archive content
        cmd = ssh + [config.sym_node, 'sudo', '-E',
                     '/opt/opensvc/bin/nodemgr',
                     '--symcli-db-file', binfile, 'pushsym']
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            db(db.sym_upload.id==row.id).update(batched=0)
            raise Exception('failed to compute the data on sym node')

        # add acl to the uploader
        cmd = ssh + [config.sym_node, 'find', dst_dir, '-name', '[0-9]*',
                     '-type', 'd', '-printf', '%P,']
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            db(db.sym_upload.id==row.id).update(batched=0)
            raise Exception('failed to determine uploader acl')
        for symid in out.split(','):
            if '%' in symid:
                # privilege escalation protection
                continue
            if len(symid) != 12:
                continue
            add_domain_perm(symid)

        # purge the compute job from the queue
        db(db.sym_upload.id==row.id).delete()

@auth.requires_login()
def sym_diskgroup():
    symid = request.vars.arrayid
    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
    p = os.path.join(dir, symid)
    s = symmetrix.get_sym(p)
    s.get_sym_diskgroup()
    d = []
    for dg in s.diskgroup.values():
        d.append(html_diskgroup(dg))
    return DIV(d)

def html_view_devs(symid, innerhtml, devs):
    t = table_dev(symid, innerhtml, devs=devs)
    t.cols += ['view']
    t.filterable = False
    t.pageable = False
    lines = []
    return t.table()

def pretty_size(size, unit):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'EB']
    units_index = {'B':0, 'KB':1, 'MB':2, 'GB':3, 'TB':4, 'EB':5}
    size = float(size)
    for u in units[units_index[unit]:]:
        if size < 1000:
           return '%.2f'%size, ' ', T(u)
        size = size/1024
    return '%.2f'%size, ' ', T(u)

def html_view(symid, view):
    size = 0
    vsize = 0
    dev_count = 0
    vdev_count = 0
    for dev in view.dev:
        if dev.info['configuration'] in ['VDEV', 'THINDEV']:
            vsize += dev.megabytes
            vdev_count += 1
        else:
            size += dev.megabytes
            dev_count += 1

    devs_innerhtml = 'sym_view_devs_%s_%s'%(symid, view.view_name)

    d = DIV(
          DIV(
            H3(view.view_name),
            _class='sym_h2',
          ),
          DIV(
            B('port group: '),
            BR(),
            '%s (%d)'%(view.port_grpname, len(view.pg)),
            HR(),
            SPAN(map(P, view.pg)),
            _class='sym_float',
            _style='min-width:12em',
          ),
          DIV(
            B('initiator group: '),
            BR(),
            '%s (%d)'%(view.init_grpname, len(view.ig)),
            HR(),
            SPAN(map(P, view.ig)),
            _class='sym_float',
            _style='min-width:12em',
          ),
          DIV(
            B('storage group: '),
            BR(),
            view.stor_grpname, BR(),
            'dev count: %d, dev total size: '%dev_count,
            SPAN(pretty_size(size,'MB')),
            BR(),
            'vdev count: %d, vdev total size: '%vdev_count,
            SPAN(pretty_size(vsize,'MB')),
            HR(),
            DIV(
              html_view_devs(symid, devs_innerhtml, view.dev),
              _id=devs_innerhtml,
            ),
            _class='sym_float',
            _style='min-width:12em',
          ),
          DIV(
            '',
            _class='spacer',
          ),
          _class='sym_diskgroup',
        )
    return d

def filter_key(symid, section, f):
    return '%s_filter_%s_%s'%(section, f, symid)

def filter_parse(symid, section, f):
    key = filter_key(symid, section, f)
    if key in request.vars:
        return request.vars[key]
    return ""

@auth.requires_login()
def sym_view():
    symid = request.vars.arrayid
    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))

    def view_filter_parse(key):
        return filter_parse(symid, 'view', key)

    def view_filter_key(key):
        return filter_key(symid, 'view', key)

    filters = ['init', 'port', 'dev', 'wwn']
    ajax_inputs = map(view_filter_key, filters)
    filter_value = {}
    for f in filters:
        filter_value[f] = view_filter_parse(f)

    p = os.path.join(dir, symid)
    s = symmetrix.get_sym(p)
    s.get_sym_view()

    x = DIV(
          DIV(
            T('Filters:'),
            _class='float',
          ),
          DIV(
            T('Initiator'),
            INPUT(
              _id=view_filter_key('init'),
              _value=filter_value['init'],
              _size=10,
              _onKeyPress=_ajax(symid, 'view', ajax_inputs)
            ),
            _class='float',
          ),
          DIV(
            T('Port'),
            INPUT(
              _id=view_filter_key('port'),
              _value=filter_value['port'],
              _size=10,
              _onKeyPress=_ajax(symid, 'view', ajax_inputs)
            ),
            _class='float',
          ),
          DIV(
            T('Dev id'),
            INPUT(
              _id=view_filter_key('dev'),
              _value=filter_value['dev'],
              _size=10,
              _onKeyPress=_ajax(symid, 'view', ajax_inputs)
            ),
            _class='float',
          ),
          DIV(
            T('Dev wwn'),
            INPUT(
              _id=view_filter_key('wwn'),
              _value=filter_value['wwn'],
              _size=10,
              _onKeyPress=_ajax(symid, 'view', ajax_inputs)
            ),
            _class='float',
          ),
          DIV(
            '',
            _class='spacer',
          ),
        )

    d = []
    for view in s.view.values():
        if not str_filter_in_list(filter_value['init'], view.ig):
            continue
        if not str_filter_in_list(filter_value['port'], view.pg):
            continue
        if not str_filter_in_list(filter_value['dev'], view.sg):
            continue
        if not str_filter_in_list(filter_value['wwn'],
                                  [dev.wwn for dev in view.dev]):
            continue
        d.append(html_view(symid, view))
    return DIV(x, SPAN(d))

def int_filter(value, num):
    if len(value) == 0:
        return True
    if not isinstance(num, int):
        return False

    negate = False
    inf = False
    sup = False
    inf_e = False
    sup_e = False

    if value[0] == '!':
        negate = True
        value = value[1:]
    if value[0] == '<':
        if len(value) > 2 and value[1] == '=':
            inf_e = True
            value = value[2:]
        else:
            inf = True
            value = value[1:]
    elif value[0] == '>':
        if len(value) > 2 and value[1] == '=':
            sup_e = True
            value = value[2:]
        else:
            sup = True
            value = value[1:]
    try:
        v = int(value)
    except:
        return str_filter(value, str(num))

    if sup:
        if num > v:
            r = True
        else:
            r = False
    elif inf:
        if num < v:
            r = True
        else:
            r = False
    elif sup_e:
        if num >= v:
            r = True
        else:
            r = False
    elif inf_e:
        if num <= v:
            r = True
        else:
            r = False
    elif num == v:
        r = True
    else:
        r = False

    if negate:
        return not r
    else:
        return r

def str_filter(value, text):
    negate = False
    if len(value) == 0:
        return True
    if value[0] == '!':
        negate = True
        value = value[1:]
    if value == "empty":
        if text == "":
            r = True
        else:
            r = False
    else:
        reg = value.replace('%', '.*')
        if reg[-1] != '$':
            reg = reg+'$'
        r = re.match(reg, text)
        if r is None:
            r = False
        else:
            r = True
    if negate:
        return not r
    else:
        return r

def str_filter_in_list(value, l):
    if value == 'empty':
        if len(l) == 0:
            return True
        else:
            return False
    elif value == '!empty':
        if len(l) == 0:
            return False
        else:
            return True
    if len(value) == 0 and len(l) == 0:
        return True
    for i in l:
        if str_filter(value, i):
            return True
    return False

def __filter(value, o):
    if isinstance(o, str) or isinstance(o, unicode):
        return str_filter(value, o)
    elif isinstance(o, list):
        return str_filter_in_list(value, o)
    elif isinstance(o, int):
        return int_filter(value, o)
    return False

def _filter(value, o):
    if '&' in value:
        for v in value.split('&'):
            if not _filter(v, o):
                return False
        return True
    elif '|' in value:
        for v in value.split('|'):
            if _filter(v, o):
                return True
        return False
    else:
        return __filter(value, o)


@auth.requires_login()
def _sym_disk_csv():
    symid = request.vars.arrayid
    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
    p = os.path.join(dir, symid)
    s = symmetrix.get_sym(p)
    s.get_sym_disk()
    lines = [';'.join(_disk_columns_print.keys())]
    for d in sorted(s.disk):
        dev = s.disk[d]
        inf = []
        for c in _disk_columns_print.keys():
            inf.append(repr(str(_disk_columns_print[c](dev))))
        lines.append(';'.join(inf))
    return '\n'.join(lines)

@auth.requires_login()
def _sym_dev_csv():
    symid = request.vars.arrayid
    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
    p = os.path.join(dir, symid)
    s = symmetrix.get_sym(p)
    s.get_sym_dev()
    lines = [';'.join(_dev_columns_print.keys())]
    for d in sorted(s.dev):
        dev = s.dev[d]
        inf = []
        for c in _dev_columns_print.keys():
            inf.append(repr(str(_dev_columns_print[c](dev))))
        lines.append(';'.join(inf))
    return '\n'.join(lines)

@auth.requires_login()
def sym_disk_csv():
    import gluon.contenttype
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    return _sym_disk_csv()

@auth.requires_login()
def sym_dev_csv():
    import gluon.contenttype
    response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
    return _sym_dev_csv()

def __ajax(symid, section, inputs):
    return """ajax("%(url)s",
                   ["arrayid", %(inputs)s],
                   "sym_%(s)s_%(symid)s");
              getElementById("sym_%(s)s_%(symid)s").innerHTML='%(spinner)s';
            """%dict(url=URL(r=request,f='sym_'+section),
                     s=section,
                     inputs = ','.join(map(repr, inputs)),
                     spinner=IMG(_src=URL(r=request,c='static',f='spinner_16.png')),
                     symid=symid)

def _ajax(symid, section, inputs):
    return """if (is_enter(event)) {
                getElementById("arrayid").value="%(symid)s";
                %(ajax)s
              };
              """%dict(ajax=__ajax(symid, section, inputs),
                       symid=symid)

class table(object):
    def __init__(self, symid, func, innerhtml):
        self.symid = symid
        self.innerhtml = innerhtml
        self.id_prefix = innerhtml
        self.func = func
        self.line_count = 0
        self.id_perpage = '_'.join((self.id_prefix, 'perpage'))
        self.filterable = True
        self.pageable = True

        if self.id_perpage in request.vars:
            self.perpage = int(request.vars[self.id_perpage])
        else:
            self.perpage = 20

    def filter_key(self, f):
        return '_'.join((self.id_prefix, 'filter', f))

    def filter_parse(self, f):
        key = self.filter_key(f)
        if key in request.vars:
            return request.vars[key]
        return ""

    def ajax_inputs(self):
        l = []
        if self.pageable:
            l.append(self.id_perpage)
        if self.filterable:
            l += map(self.filter_key, self.cols)
        return l

    def table_header(self):
        titles = map(lambda x: self.colprops[x]['title'], self.cols)
        return TR(map(TH, titles))

    def table_line(self, o):
        cells = []
        for c in self.cols:
            cells.append(TD(self.colprops[c]['str'](o),
                            _class=self.colprops[c]['_class']))
        return TR(cells)

    def table_lines(self):
        lines = []
        line_count = 0
        for i in sorted(self.object_list):
            if isinstance(i, str):
                o = self.object_list[i]
            else:
                o = i
            self.change_line_data(o)
            skip = False
            for c in self.cols:
                if not _filter(self.filter_parse(c), self.colprops[c]['get'](o)):
                    skip = True
                    break
            if skip:
                continue
            line_count += 1
            if not self.pageable or line_count <= self.perpage:
                lines.append(self.table_line(o))
        return lines, line_count

    def table_inputs(self):
        inputs = []
        for c in self.cols:
            inputs.append(INPUT(
                    _id=self.filter_key(c),
                    _value=self.filter_parse(c),
                    _size=self.colprops[c]['size'],
                    _onKeyPress=self._ajax()
                  ))
        return inputs

    def __ajax(self):
        return """ajax("%(url)s",
                       ["arrayid", %(inputs)s],
                       "%(innerhtml)s");
                  getElementById("%(innerhtml)s").innerHTML='%(spinner)s';
                """%dict(url=URL(r=request,f=self.func),
                         innerhtml=self.innerhtml,
                         inputs = ','.join(map(repr, self.ajax_inputs())),
                         spinner=IMG(_src=URL(r=request,c='static',f='spinner_16.png')),
                        )

    def _ajax(self):
        return """if (is_enter(event)) {
                    getElementById("arrayid").value="%(symid)s";
                    %(ajax)s
                  };
                  """%dict(ajax=self.__ajax(),
                           symid=self.symid)

    def table(self):
        lines, line_count = self.table_lines()

        if self.filterable:
            inputs = TR(map(TD, self.table_inputs()))
        else:
            inputs = SPAN()

        if self.pageable:
            paging = DIV(
                  A(
                    T('Display all lines'),
                  ),
                  _onclick="""
                    getElementById("%(id_perpage)s").value="%(count)s";
                  """%dict(count=line_count,
                           id_perpage=self.id_perpage,
                          )+self.__ajax(),
                  _class='sym_float',
                )
        else:
            paging = SPAN()

        d = DIV(
              SPAN('%d/%d'%(len(lines),line_count), _class='sym_highlight'),
              TABLE(
                self.table_header(),
                inputs,
                SPAN(map(SPAN, lines)),
              ),
              DIV(
                INPUT(
                  _id=self.id_perpage,
                  _type='hidden',
                  _value=self.perpage,
                ),
                paging,
                DIV(
                  A(
                    T('Export to csv'),
                    _href=URL(r=request,f=self.csv, vars=request.vars),
                  ),
                  _class='sym_float',
                ),
              ),
              DIV('', _class='spacer'),
              _class='sym_diskgroup',
            )
        return d

    def change_line_data(self, o):
        pass


class table_disk(table):
    def __init__(self, symid, innerhtml):
        table.__init__(self, symid, 'sym_disk', innerhtml)
        self.csv = 'sym_disk_csv'
        self.cols = ['da_number', 'interface', 'tid', 'dg', 'technology',
                     'speed', 'vendor', 'revision', 'product', 'serial',
                     'megabytes', 'hypers', 'hot_spare', 'failed_disk']
        self.colprops = {
            'da_number': dict(
                     size=3, title='director', _class='',
                     get=lambda x: x.info['da_number'],
                     str=lambda x: x.info['da_number'],
                    ),
            'interface': dict(
                     size=3, title='interface', _class='',
                     get=lambda x: x.info['interface'],
                     str=lambda x: x.info['interface'],
                    ),
            'tid': dict(
                     size=2, title='target id', _class='numeric',
                     get=lambda x: x.info['tid'],
                     str=lambda x: x.info['tid'],
                    ),
            'dg': dict(
                     size=12, title='diskgroup', _class='',
                     get=lambda x: x.info['disk_group_name'],
                     str=lambda x: x.info['disk_group_name'],
                    ),
            'technology': dict(
                     size=4, title='technology', _class='',
                     get=lambda x: x.info['technology'],
                     str=lambda x: x.info['technology'],
                    ),
            'speed': dict(
                     size=3, title='speed', _class='numeric',
                     get=lambda x: x.info['speed'],
                     str=lambda x: x.info['speed'],
                    ),
            'vendor': dict(
                     size=5, title='vendor', _class='',
                     get=lambda x: x.info['vendor'],
                     str=lambda x: x.info['vendor'],
                    ),
            'revision': dict(
                     size=5, title='revision', _class='',
                     get=lambda x: x.info['revision'],
                     str=lambda x: x.info['revision'],
                    ),
            'product': dict(
                     size=12, title='product', _class='',
                     get=lambda x: x.info['product'],
                     str=lambda x: x.info['product'],
                    ),
            'serial': dict(
                     size=5, title='serial', _class='',
                     get=lambda x: x.info['serial'],
                     str=lambda x: x.info['serial'],
                    ),
            'megabytes': dict(
                     size=5, title='size', _class='numeric',
                     get=lambda x: x.info['megabytes'],
                     str=lambda x: x.info['megabytes'],
                    ),
            'hypers': dict(
                     size=2, title='hypers', _class='numeric',
                     get=lambda x: x.info['hypers'],
                     str=lambda x: x.info['hypers'],
                    ),
            'hot_spare': dict(
                     size=4, title='hot spare', _class='',
                     get=lambda x: x.info['hot_spare'],
                     str=lambda x: x.info['hot_spare'],
                    ),
            'failed_disk': dict(
                     size=4, title='failed disk', _class='',
                     get=lambda x: x.info['failed_disk'],
                     str=lambda x: x.info['failed_disk'],
                    ),
        }

        dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
        p = os.path.join(dir, symid)
        s = symmetrix.get_sym(p)
        s.get_sym_disk()
        self.object_list = s.disk


class table_dev(table):
    def __init__(self, symid, innerhtml, devs=None):
        table.__init__(self, symid, 'sym_dev', innerhtml)
        self.csv = 'sym_dev_csv'
        self.cols = ['dev', 'wwn', 'conf', 'meta', 'metaflag', 'memberof',
                     'size', 'dg', 'frontend', 'rdf_state', 'rdf_mode',
                     'rdf_group', 'remote_sym', 'remote_dev']
        self.colprops = {
            'dev': dict(
                     size=3, title='dev', _class='',
                     get=lambda x: x.info['dev_name'],
                     str=lambda x: x.info['dev_name'],
                    ),
            'conf': dict(
                     size=5, title='conf', _class='',
                     get=lambda x: x.info['configuration'],
                     str=lambda x: x.info['configuration'],
                    ),
            'meta': dict(
                     size=3, title='meta', _class='numeric',
                     get=lambda x: x.meta_count,
                     str=lambda x: x.meta_count,
                    ),
            'metaflag': dict(
                     size=4, title='meta flag', _class='',
                     get=lambda x: x.flags['meta'],
                     str=lambda x: x.flags['meta'],
                    ),
            'memberof': dict(
                     size=3, title='member of', _class='',
                     get=lambda x: x.memberof,
                     str=lambda x: x.memberof,
                    ),
            'size': dict(
                     size=7, title='size', _class='numeric',
                     get=lambda x: x.megabytes,
                     str=lambda x: T('%(n)s MB', dict(n=x.megabytes)),
                    ),
            'dg': dict(
                     size=12, title='diskgroup', _class='',
                     get=lambda x: x.diskgroup_name,
                     str=lambda x: x.diskgroup_name,
                    ),
            'view': dict(
                     size=10, title='view', _class='',
                     get=lambda x: x.view,
                     str=lambda x: ', '.join(x.view),
                    ),
            'wwn': dict(
                     size=24, title='wwn', _class='',
                     get=lambda x: x.wwn,
                     str=lambda x: x.wwn,
                    ),
            'frontend': dict(
                     size=4, title='frontend', _class='',
                     get=lambda x: x.frontend,
                     str=lambda x: ', '.join(x.frontend),
                    ),
            'rdf_state': dict(
                     size=8, title='rdf state', _class='',
                     get=lambda x: x.rdf.pair_state,
                     str=lambda x: x.rdf.pair_state,
                    ),
            'rdf_mode': dict(
                     size=8, title='rdf mode', _class='',
                     get=lambda x: x.rdf.mode,
                     str=lambda x: x.rdf.mode,
                    ),
            'rdf_group': dict(
                     size=2, title='rdf group', _class='numeric',
                     get=lambda x: x.rdf.ra_group_num,
                     str=lambda x: x.rdf.ra_group_num,
                    ),
            'remote_sym': dict(
                     size=8, title='remote sym', _class='',
                     get=lambda x: x.rdf.remote_symid,
                     str=lambda x: x.rdf.remote_symid,
                    ),
            'remote_dev': dict(
                     pos=13, size=3, title='remote dev', _class='',
                     get=lambda x: x.rdf.remote_devname,
                     str=lambda x: x.rdf.remote_devname,
                    ),
        }

        if devs is None:
            dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
            p = os.path.join(dir, symid)
            s = symmetrix.get_sym(p)
            s.get_sym_dev()
            self.object_list = s.dev
            if isinstance(s, symmetrix.Vmax):
                self.cols += ['view']
        else:
            self.object_list = devs

    def change_line_data(self, dev):
        if dev.meta_count == 0:
            dev.meta_count = 'n/a'

class table_ig(table):
    def __init__(self, symid, innerhtml):
        table.__init__(self, symid, 'sym_ig', innerhtml)
        self.csv = 'sym_ig_csv'
        self.cols = ['init_grpname', 'wwn']
        self.colprops = {
            'init_grpname': dict(
                     size=12, title='initiator group', _class='',
                     get=lambda x: x['init_grpname'],
                     str=lambda x: x['init_grpname'],
                    ),
            'wwn': dict(
                     size=24, title='wwn', _class='',
                     get=lambda x: x['init_list'],
                     str=lambda x: ', '.join(x['init_list']),
                    ),
        }

        dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
        p = os.path.join(dir, symid)
        s = symmetrix.get_sym(p)
        s.get_sym_ig()
        self.object_list = map(lambda x: dict(init_grpname=x, init_list=s.ig[x]), s.ig.keys())

class table_pg(table):
    def __init__(self, symid, innerhtml):
        table.__init__(self, symid, 'sym_pg', innerhtml)
        self.csv = 'sym_pg_csv'
        self.cols = ['port_grpname', 'port']
        self.colprops = {
            'port_grpname': dict(
                     size=12, title='port group', _class='',
                     get=lambda x: x['port_grpname'],
                     str=lambda x: x['port_grpname'],
                    ),
            'port': dict(
                     size=24, title='port', _class='',
                     get=lambda x: x['port_list'],
                     str=lambda x: ', '.join(x['port_list']),
                    ),
        }

        dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
        p = os.path.join(dir, symid)
        s = symmetrix.get_sym(p)
        s.get_sym_pg()
        self.object_list = map(lambda x: dict(port_grpname=x, port_list=s.pg[x]), s.pg.keys())

class table_sg(table):
    def __init__(self, symid, innerhtml):
        table.__init__(self, symid, 'sym_sg', innerhtml)
        self.csv = 'sym_sg_csv'
        self.cols = ['stor_grpname', 'dev']
        self.colprops = {
            'stor_grpname': dict(
                     size=12, title='storage group', _class='',
                     get=lambda x: x['stor_grpname'],
                     str=lambda x: x['stor_grpname'],
                    ),
            'dev': dict(
                     size=24, title='devices', _class='',
                     get=lambda x: x['dev_list'],
                     str=lambda x: ', '.join(x['dev_list']),
                    ),
        }

        dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
        p = os.path.join(dir, symid)
        s = symmetrix.get_sym(p)
        s.get_sym_sg()
        self.object_list = map(lambda x: dict(stor_grpname=x, dev_list=s.sg[x]), s.sg.keys())

@auth.requires_login()
def sym_disk():
    symid = request.vars.arrayid
    t = table_disk(symid, 'sym_disk_%s'%symid)
    return t.table()

@auth.requires_login()
def sym_dev():
    symid = request.vars.arrayid
    t = table_dev(symid, 'sym_dev_%s'%symid)
    return t.table()

@auth.requires_login()
def sym_ig():
    symid = request.vars.arrayid
    t = table_ig(symid, 'sym_ig_%s'%symid)
    return t.table()

@auth.requires_login()
def sym_pg():
    symid = request.vars.arrayid
    t = table_pg(symid, 'sym_pg_%s'%symid)
    return t.table()

@auth.requires_login()
def sym_sg():
    symid = request.vars.arrayid
    t = table_sg(symid, 'sym_sg_%s'%symid)
    return t.table()

@auth.requires_login()
def sym_overview_item(symid, func, count, title):
    """
    Format a H2 list item title with a child object count.
    Also append a DIV whose innerHTML will receive the ajax data
    container child objects info.
    """
    h = H2(
         '%s (%d)'%(title, count),
         _onclick="""
           if (getElementById("%(func)s_%(symid)s").innerHTML=="") {
             getElementById("%(func)s_%(symid)s").innerHTML='%(spinner)s';
             getElementById("arrayid").value="%(symid)s";
             ajax("%(url)s",["arrayid"],"%(func)s_%(symid)s");
           };
           toggle_vis_block("%(func)s_%(symid)s");
         """%dict(url=URL(r=request,f=func), func=func,
                  spinner=IMG(_src=URL(r=request,c='static',f='spinner_16.png')),
                  symid=symid),
        _onmouseover="this.style.color='orange'",
        _onmouseout="this.style.color='inherit'",
      )
    d = DIV(
          _id='%s_%s'%(func, symid),
          _name='%s_%s'%(func, symid),
          _class='sym_detail',
        )
    return SPAN(h, d)

@auth.requires_login()
def sym_overview():
    """
    Format a list of top-level Symmetrix objects.
    Each item can be drilled down (ajax)
    """
    symid = request.vars.arrayid
    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
    p = os.path.join(dir, symid)
    s = symmetrix.get_sym(p)
    info = s.get_sym_info()
    if 'ig_count' in info:
       d_vmax = SPAN(
                  sym_overview_item(symid, func='sym_view',
                                    count=info['view_count'],
                                    title='views'),
                  sym_overview_item(symid, func='sym_ig',
                                    count=info['ig_count'],
                                    title='initiator groups'),
                  sym_overview_item(symid, func='sym_pg',
                                    count=info['pg_count'],
                                    title='port groups'),
                  sym_overview_item(symid, func='sym_sg',
                                    count=info['sg_count'],
                                    title='storage groups'),
                )
    else:
        d_vmax = SPAN()
    d = DIV(
          sym_overview_item(symid, func='sym_diskgroup',
                            count=info['diskgroup_count'],
                            title='disk groups'),
          sym_overview_item(symid, func='sym_disk',
                            count=info['disk_count'],
                            title='disks'),
          sym_overview_item(symid, func='sym_dev',
                            count=info['dev_count'],
                            title='devices'),
          d_vmax,
          DIV(
            A(
              T('Export to csv'),
              _href=URL(r=request,f='sym_all_csv', vars={'arrayid':symid}),
            ),
            _class='sym_float',
          ),
          _onclick="event.cancelBubble = true;",
        )
    return d


