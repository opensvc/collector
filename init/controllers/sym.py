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
     l = []
     for key in dg.diskcount:
         if len(key) == 3:
             size, tech, speed = key
             spare = None
         else:
             size, tech, speed, spare = key
         s = '%d x %d GB %s rpm %s'%(dg.diskcount[key], int(size)//1024, speed, tech)
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
        cmd = ssh + [config.sym_node, 'mkdir', dst_dir]
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

        db(db.sym_upload.id==row.id).delete()

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

def html_view(view):
    d = DIV(
          DIV(
            H3(view.view_name),
            _class='sym_float',
            _style='width:18em',
          ),
          DIV(
            B('storage group: '),
            BR(),
            '%s (%d)'%(view.stor_grpname, len(view.sg)),
            HR(),
            SPAN(map(P, view.sg)),
            _class='sym_float',
            _style='width:12em',
          ),
          DIV(
            B('port group: '),
            BR(),
            '%s (%d)'%(view.port_grpname, len(view.pg)),
            HR(),
            SPAN(map(P, view.pg)),
            _class='sym_float',
            _style='width:12em',
          ),
          DIV(
            B('initiator group: '),
            BR(),
            '%s (%d)'%(view.init_grpname, len(view.ig)),
            HR(),
            SPAN(map(P, view.ig)),
            _class='sym_float',
            _style='width:12em',
          ),
          DIV(
            '',
            _class='spacer',
          ),
          _class='sym_diskgroup',
        )
    return d

def sym_view():
    symid = request.vars.arrayid
    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
    p = os.path.join(dir, symid)
    s = symmetrix.Vmax(p)
    s.get_sym_view()
    d = []
    for view in s.view.values():
        d.append(html_view(view))
    return DIV(d)

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

def filter_parse(symid, f):
    key = 'dev_filter_%s_%s'%(f,symid)
    if key in request.vars:
        value = request.vars[key]
    else:
        value = ""
    return key, value

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

def sym_dev():
    symid = request.vars.arrayid
    if 'dev_perpage_'+symid in request.vars:
        perpage = int(request.vars['dev_perpage_'+symid])
    else:
        perpage = 20
    line_count = 0

    filter_dev_key, filter_dev_value = filter_parse(symid, 'dev')
    filter_wwn_key, filter_wwn_value = filter_parse(symid, 'wwn')
    filter_conf_key, filter_conf_value = filter_parse(symid, 'conf')
    filter_meta_key, filter_meta_value = filter_parse(symid, 'meta')
    filter_metaflag_key, filter_metaflag_value = filter_parse(symid, 'metaflag')
    filter_size_key, filter_size_value = filter_parse(symid, 'size')
    filter_dg_key, filter_dg_value = filter_parse(symid, 'dg')
    filter_view_key, filter_view_value = filter_parse(symid, 'view')


    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
    p = os.path.join(dir, symid)
    s = symmetrix.Vmax(p)
    s.get_sym_dev()
    lines = []
    for dev in sorted(s.dev):
        if not str_filter(filter_dev_value, s.dev[dev].info['dev_name']):
            continue
        if not str_filter(filter_wwn_value, s.dev[dev].wwn):
            continue
        if not str_filter(filter_conf_value, s.dev[dev].info['configuration']):
            continue
        if s.dev[dev].meta_count == 0:
            s.dev[dev].meta_count = 'n/a'
        if not int_filter(filter_meta_value, s.dev[dev].meta_count):
            continue
        if not str_filter(filter_metaflag_value, s.dev[dev].flags['meta']):
            continue
        if not int_filter(filter_size_value, s.dev[dev].megabytes):
            continue
        if not str_filter(filter_dg_value, s.dev[dev].diskgroup_name):
            continue
        if not str_filter(filter_view_value, ', '.join(s.dev[dev].view)):
            continue
        line_count += 1
        if line_count <= perpage:
            lines.append(html_dev(s.dev[dev]))

    def __ajax():
        return """ajax("%(url)s",
                       ["arrayid",
                        "dev_perpage_%(symid)s",
                        "dev_filter_conf_%(symid)s",
                        "dev_filter_meta_%(symid)s",
                        "dev_filter_metaflag_%(symid)s",
                        "dev_filter_size_%(symid)s",
                        "dev_filter_dg_%(symid)s",
                        "dev_filter_view_%(symid)s",
                        "dev_filter_wwn_%(symid)s",
                        "dev_filter_dev_%(symid)s"],
                       "sym_dev_%(symid)s");
                  getElementById("sym_dev_%(symid)s").innerHTML='%(spinner)s';
                """%dict(url=URL(r=request,f='sym_dev'),
                         spinner=IMG(_src=URL(r=request,c='static',f='spinner_16.png')),
                         symid=symid)

    def _ajax():
        return """if (is_enter(event)) {
                    getElementById("arrayid").value="%(symid)s";
                    %(ajax)s
                  };
                  """%dict(ajax=__ajax(),
                           symid=symid)

    d = DIV(
          TABLE(
            TR(
              TH('dev (%d/%d)'%(len(lines),line_count)),
              TH('conf'),
              TH('meta'),
              TH('meta flag'),
              TH('size'),
              TH('diskgroup'),
              TH('view'),
              TH('wwn'),
            ),
            TR(
              INPUT(
                _id='dev_filter_dev_'+symid,
                _value=filter_dev_value,
                _size=5,
                _onKeyPress=_ajax()
              ),
              INPUT(
                _id='dev_filter_conf_'+symid,
                _value=filter_conf_value,
                _size=5,
                _onKeyPress=_ajax()
              ),
              INPUT(
                _id='dev_filter_meta_'+symid,
                _value=filter_meta_value,
                _size=3,
                _onKeyPress=_ajax()
              ),
              INPUT(
                _id='dev_filter_metaflag_'+symid,
                _value=filter_metaflag_value,
                _size=4,
                _onKeyPress=_ajax()
              ),
              INPUT(
                _id='dev_filter_size_'+symid,
                _value=filter_size_value,
                _size=7,
                _onKeyPress=_ajax()
              ),
              INPUT(
                _id='dev_filter_dg_'+symid,
                _value=filter_dg_value,
                _size=10,
                _onKeyPress=_ajax()
              ),
              INPUT(
                _id='dev_filter_view_'+symid,
                _value=filter_view_value,
                _size=10,
                _onKeyPress=_ajax()
              ),
              INPUT(
                _id='dev_filter_wwn_'+symid,
                _value=filter_wwn_value,
                _size=32,
                _onKeyPress=_ajax()
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
              """%dict(count=line_count, symid=symid)+__ajax(),
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
          H2('disks (%d)'%info['disk_count']),
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


