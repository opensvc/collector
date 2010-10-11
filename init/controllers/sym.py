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
        syms.append(sym_info(os.path.basename(d)))

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
    files += write_csv(os.path.join(dir, 'sym_dev.csv'), sym_dev_csv())
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
            s += " (spare)"
         l.append(s)
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
         table_usage = TABLE(
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
            )

     if len(m) == 0:
         table_usage_per_size = SPAN()
     else:
         table_usage_per_size = TABLE(
              TR(
                TH('dev size'),
                TH('free'),
                TH('used'),
                TH('total'),
                TH('%used'),
              ),
              SPAN(map(SPAN, m))
            ),

     d = DIV(
          DIV(
            H3(
              dg.info['disk_group_number'],
              ': ',
              dg.info['disk_group_name'],
            ),
            SPAN(map(P, l)),
            _class='sym_float',
            _style='width:18em',
          ),
          DIV(
            table_usage,
            _class='sym_float',
            _style='width:12em',
          ),
          DIV(
            table_usage_per_size,
            _class='sym_float',
            _style='width:20em',
          ),
          DIV(
            '',
            _class='spacer',
          ),
          _class='sym_diskgroup',
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
    d = {}
    for se in list(e):
      d[se.tag] = se.text
    del tree
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
    s = symmetrix.Vmax(p)
    s.get_sym_diskgroup()
    d = []
    for dg in s.diskgroup.values():
        d.append(html_diskgroup(dg))
    return DIV(d)

def html_view_devs(devs):
    lines = []
    for dev in devs:
        lines.append(html_dev(dev))
    t = TABLE(
          html_dev_header(),
          SPAN(map(TR, lines)),
        )
    return t

def pretty_size(size, unit):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'EB']
    units_index = {'B':0, 'KB':1, 'MB':2, 'GB':3, 'TB':4, 'EB':5}
    for u in units[units_index[unit]:]:
        if size < 1000:
           return size, ' ', T(u)
        size = size/1024
    return size, ' ', T(u)

def html_view(view):
    size = 0
    for dev in view.dev:
        size += dev.megabytes

    d = DIV(
          DIV(
            H3(view.view_name),
            _class='sym_float',
            _style='width:18em',
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
            '%s (%d)'%(view.stor_grpname, len(view.sg)),
            '(', SPAN(pretty_size(size, 'MB')), ')',
            HR(),
            html_view_devs(view.dev),
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
    s = symmetrix.Vmax(p)
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
        d.append(html_view(view))
    return DIV(x, SPAN(d))

def html_dev_header(info=None):
    if info is not None:
        dev = 'dev (%s)'%info
    else:
        dev = 'dev'
    l = TR(
          TH(dev),
          TH('conf'),
          TH('meta'),
          TH('meta flag'),
          TH('size'),
          TH('diskgroup'),
          TH('view'),
          TH('wwn'),
        )
    return l

def html_dev(dev):
    view = ', '.join(dev.view)

    l = TR(
          TD(dev.info['dev_name']),
          TD(dev.info['configuration']),
          TD(dev.meta_count, _class='numeric'),
          TD(dev.flags['meta']),
          TD(dev.megabytes,' ',T('MB'), _class='numeric'),
          TD(dev.diskgroup_name),
          TD(view),
          TD(dev.wwn),
        )
    return l

def filter_key(symid, section, f):
    return '%s_filter_%s_%s'%(section, f, symid)

def filter_parse(symid, section, f):
    key = filter_key(symid, section, f)
    if key in request.vars:
        return request.vars[key]
    return ""

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
    if value[0] == '>':
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

    if sup and num > v:
        r = True
    elif inf and num < v:
        r = True
    elif sup_e and num >= v:
        r = True
    elif inf_e and num <= v:
        r = True
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
    for i in l:
        if str_filter(value, i):
            return True
    return False

@auth.requires_login()
def sym_dev_csv():
    symid = request.vars.arrayid
    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
    p = os.path.join(dir, symid)
    s = symmetrix.Vmax(p)
    s.get_sym_dev()
    lines = ['devname;config;meta_count;meta_flag;size_mb;dgname;views;wwn']
    for d in sorted(s.dev):
        dev = s.dev[d]
        inf = [repr(dev.info['dev_name']),
               dev.info['configuration'],
               str(dev.meta_count),
               dev.flags['meta'],
               str(dev.megabytes),
               dev.diskgroup_name,
               ','.join(dev.view),
               dev.wwn]
        lines.append(';'.join(inf))
    return '\n'.join(lines)

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

@auth.requires_login()
def sym_dev():
    symid = request.vars.arrayid
    if 'dev_perpage_'+symid in request.vars:
        perpage = int(request.vars['dev_perpage_'+symid])
    else:
        perpage = 20
    line_count = 0

    def dev_filter_key(key):
        return filter_key(symid, 'dev', key)

    def dev_filter_parse(key):
        return filter_parse(symid, 'dev', key)

    filters = ['dev', 'wwn', 'conf', 'meta', 'metaflag', 'size', 'dg', 'view']
    filter_value = {}
    ajax_inputs = map(dev_filter_key, filters)
    for f in filters:
        filter_value[f] = dev_filter_parse(f)

    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
    p = os.path.join(dir, symid)
    s = symmetrix.Vmax(p)
    s.get_sym_dev()
    lines = []
    for dev in sorted(s.dev):
        if not str_filter(filter_value['dev'], s.dev[dev].info['dev_name']):
            continue
        if not str_filter(filter_value['wwn'], s.dev[dev].wwn):
            continue
        if not str_filter(filter_value['conf'], s.dev[dev].info['configuration']):
            continue
        if s.dev[dev].meta_count == 0:
            s.dev[dev].meta_count = 'n/a'
        if not int_filter(filter_value['meta'], s.dev[dev].meta_count):
            continue
        if not str_filter(filter_value['metaflag'], s.dev[dev].flags['meta']):
            continue
        if not int_filter(filter_value['size'], s.dev[dev].megabytes):
            continue
        if not str_filter(filter_value['dg'], s.dev[dev].diskgroup_name):
            continue
        if not str_filter_in_list(filter_value['view'], s.dev[dev].view):
            continue
        line_count += 1
        if line_count <= perpage:
            lines.append(html_dev(s.dev[dev]))

    d = DIV(
          TABLE(
            html_dev_header('%d/%d'%(len(lines),line_count)),
            TR(
              INPUT(
                _id='dev_filter_dev_'+symid,
                _value=filter_value['dev'],
                _size=5,
                _onKeyPress=_ajax(symid, 'dev', ajax_inputs)
              ),
              INPUT(
                _id='dev_filter_conf_'+symid,
                _value=filter_value['conf'],
                _size=5,
                _onKeyPress=_ajax(symid, 'dev', ajax_inputs)
              ),
              INPUT(
                _id='dev_filter_meta_'+symid,
                _value=filter_value['meta'],
                _size=3,
                _onKeyPress=_ajax(symid, 'dev', ajax_inputs)
              ),
              INPUT(
                _id='dev_filter_metaflag_'+symid,
                _value=filter_value['metaflag'],
                _size=4,
                _onKeyPress=_ajax(symid, 'dev', ajax_inputs)
              ),
              INPUT(
                _id='dev_filter_size_'+symid,
                _value=filter_value['size'],
                _size=7,
                _onKeyPress=_ajax(symid, 'dev', ajax_inputs)
              ),
              INPUT(
                _id='dev_filter_dg_'+symid,
                _value=filter_value['dg'],
                _size=10,
                _onKeyPress=_ajax(symid, 'dev', ajax_inputs)
              ),
              INPUT(
                _id='dev_filter_view_'+symid,
                _value=filter_value['view'],
                _size=10,
                _onKeyPress=_ajax(symid, 'dev', ajax_inputs)
              ),
              INPUT(
                _id='dev_filter_wwn_'+symid,
                _value=filter_value['wwn'],
                _size=32,
                _onKeyPress=_ajax(symid, 'dev', ajax_inputs)
              ),
            ),
            SPAN(map(SPAN, lines)),
          ),
          DIV(
            INPUT(
              _id='dev_perpage_'+symid,
              _type='hidden',
              _value=perpage,
            ),
            DIV(
              A(
                T('Display all lines'),
              ),
              _onclick="""
                getElementById("dev_perpage_%(symid)s").value="%(count)s";
              """%dict(count=line_count,
                       symid=symid)+__ajax(symid, 'dev', ajax_inputs),
              _class='sym_float',
            ),
            DIV(
              A(
                T('Export to csv'),
                _href=URL(r=request,f='sym_dev_csv', vars=request.vars),
              ),
              _class='sym_float',
            ),
          ),
          _class='sym_diskgroup',
        )
    return d

@auth.requires_login()
def sym_overview_item(symid, title, count):
    """
    Format a H2 list item title with a child object count.
    Also append a DIV whose innerHTML will receive the ajax data
    container child objects info.
    """
    h = H2(
         '%s (%d)'%(title, count),
         _onclick="""
           if (getElementById("sym_%(title)s_%(symid)s").innerHTML=="") {
             getElementById("sym_%(title)s_%(symid)s").innerHTML='%(spinner)s';
             getElementById("arrayid").value="%(symid)s";
             ajax("%(url)s",["arrayid"],"sym_%(title)s_%(symid)s");
           };
           toggle_vis("sym_%(title)s_%(symid)s");
         """%dict(url=URL(r=request,f='sym_'+title), title=title,
                  spinner=IMG(_src=URL(r=request,c='static',f='spinner_16.png')),
                  symid=symid),
        _onmouseover="this.style.color='orange'",
        _onmouseout="this.style.color='inherit'",
      )
    d = DIV(
          _id='sym_%s_%s'%(title, symid),
          _name='sym_%s_%s'%(title, symid),
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
    s = symmetrix.Vmax(p)
    info = s.get_sym_info()
    d = DIV(
          sym_overview_item(symid, 'diskgroup', info['diskgroup_count']),
          H2('disk (%d)'%info['disk_count']),
          sym_overview_item(symid, 'dev', info['dev_count']),
          sym_overview_item(symid, 'view', info['view_count']),
          H2('initator group (%d)'%info['ig_count']),
          H2('port group (%d)'%info['pg_count']),
          H2('storage group (%d)'%info['sg_count']),
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


