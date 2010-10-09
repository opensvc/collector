import os
import re
from xml.etree.ElementTree import ElementTree, SubElement
symmetrix = local_import('symmetrix', reload=True)
config = local_import('config', reload=True)

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

from subprocess import *

def batch_files():
    if not hasattr(config, 'sym_node'):
        return
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

@auth.requires_login()
def index():
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

def html_dev(dev):
    view = ', '.join(dev.view)

    l = TR(
          TD(dev.info['dev_name']),
          TD(dev.info['configuration']),
          TD(dev.meta_count, _class='numeric'),
          TD(dev.megabytes,' ',T('MB'), _class='numeric'),
          TD(dev.diskgroup_name),
          TD(view),
          TD(dev.wwn),
        )
    return l

def filter_parse(symid, f):
    key = 'filter_%s_%s'%(f,symid)
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

def sym_dev():
    symid = request.vars.arrayid

    filter_dev_key, filter_dev_value = filter_parse(symid, 'dev')
    filter_wwn_key, filter_wwn_value = filter_parse(symid, 'wwn')
    filter_conf_key, filter_conf_value = filter_parse(symid, 'conf')
    filter_meta_key, filter_meta_value = filter_parse(symid, 'meta')
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
        if not int_filter(filter_size_value, s.dev[dev].megabytes):
            continue
        if not str_filter(filter_dg_value, s.dev[dev].diskgroup_name):
            continue
        if len(s.dev[dev].view) == 0:
            s.dev[dev].view = ['free']
        if not str_filter(filter_view_value, ', '.join(s.dev[dev].view)):
            continue
        lines.append(html_dev(s.dev[dev]))

    def _ajax():
        return """if (is_enter(event)) {
                    getElementById("arrayid").value="%(symid)s";
                    ajax("%(url)s",
                         ["arrayid",
                          "filter_conf_%(symid)s",
                          "filter_meta_%(symid)s",
                          "filter_size_%(symid)s",
                          "filter_dg_%(symid)s",
                          "filter_view_%(symid)s",
                          "filter_wwn_%(symid)s",
                          "filter_dev_%(symid)s"],
                         "sym_dev_%(symid)s");
                    getElementById("sym_dev_%(symid)s").innerHTML='%(spinner)s';
                  };
                  """%dict(url=URL(r=request,f='sym_dev'),
                           spinner=IMG(_src=URL(r=request,c='static',f='spinner_16.png')),
                           symid=symid)
    d = DIV(
          TABLE(
            TR(
              TH('dev (%d)'%len(lines)),
              TH('conf'),
              TH('meta'),
              TH('size'),
              TH('diskgroup'),
              TH('view'),
              TH('wwn'),
            ),
            TR(
              INPUT(
                _id='filter_dev_'+symid,
                _value=filter_dev_value,
                _size=5,
                _onKeyPress=_ajax()
              ),
              INPUT(
                _id='filter_conf_'+symid,
                _value=filter_conf_value,
                _size=5,
                _onKeyPress=_ajax()
              ),
              INPUT(
                _id='filter_meta_'+symid,
                _value=filter_meta_value,
                _size=3,
                _onKeyPress=_ajax()
              ),
              INPUT(
                _id='filter_size_'+symid,
                _value=filter_size_value,
                _size=7,
                _onKeyPress=_ajax()
              ),
              INPUT(
                _id='filter_dg_'+symid,
                _value=filter_dg_value,
                _size=10,
                _onKeyPress=_ajax()
              ),
              INPUT(
                _id='filter_view_'+symid,
                _value=filter_view_value,
                _size=10,
                _onKeyPress=_ajax()
              ),
              INPUT(
                _id='filter_wwn_'+symid,
                _value=filter_wwn_value,
                _size=32,
                _onKeyPress=_ajax()
              ),
            ),
            SPAN(map(SPAN, lines)),
          ),
          _class='sym_diskgroup',
        )
    return d

def sym_overview():
    symid = request.vars.arrayid
    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
    p = os.path.join(dir, symid)
    s = symmetrix.Vmax(p)
    info = s.get_sym_info()
    d = DIV(
          H2(
            'diskgroup (%d)'%info['diskgroup_count'],
            _onclick="""if (getElementById("sym_diskgroup_%(symid)s").innerHTML=="") {
                          getElementById("sym_diskgroup_%(symid)s").innerHTML='%(spinner)s';
                          getElementById("arrayid").value="%(symid)s";
                          ajax("%(url)s",["arrayid"],"sym_diskgroup_%(symid)s");
                        };
                        toggle_vis("sym_diskgroup_%(symid)s");
                     """%dict(url=URL(r=request,f='sym_diskgroup'),
                              spinner=IMG(_src=URL(r=request,c='static',f='spinner_16.png')),
                              symid=symid),
            _onmouseover="this.style.color='orange'",
            _onmouseout="this.style.color='inherit'",
          ),
          DIV(
            _id='sym_diskgroup_'+symid,
            _name='sym_diskgroup_'+symid,
          ),
          H2('disks (%d)'%info['disk_count']),
          H2(
            'dev (%d)'%info['dev_count'],
            _onclick="""if (getElementById("sym_dev_%(symid)s").innerHTML=="") {
                          getElementById("sym_dev_%(symid)s").innerHTML='%(spinner)s';
                          getElementById("arrayid").value="%(symid)s";
                          ajax("%(url)s",["arrayid"],"sym_dev_%(symid)s");
                        };
                        toggle_vis("sym_dev_%(symid)s");
                     """%dict(url=URL(r=request,f='sym_dev'),
                              spinner=IMG(_src=URL(r=request,c='static',f='spinner_16.png')),
                              symid=symid),
            _onmouseover="this.style.color='orange'",
            _onmouseout="this.style.color='inherit'",
          ),
          DIV(
            _id='sym_dev_'+symid,
            _name='sym_dev_'+symid,
            _style='display:none',
          ),
          H2('view (%d)'%info['view_count']),
          H2('initator group (%d)'%info['ig_count']),
          H2('port group (%d)'%info['pg_count']),
          H2('storage group (%d)'%info['sg_count']),
          _onclick="event.cancelBubble = true;",
        )
    return d


