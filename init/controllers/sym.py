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
    if s is None:
        return SPAN(T("Incomplete information"))
    info = s.get_sym_info()
    if 'ig_count' in info:
        vmax = True
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
        vmax = False
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
              _href=URL(r=request,f='sym_all_csv', vars={'arrayid':symid, 'vmax': vmax}),
            ),
            _class='sym_float',
          ),
          _onclick="event.cancelBubble = true;",
        )
    return d

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
    files += write_csv(os.path.join(dir, 'sym_dev.csv'), table_dev()._csv())
    files += write_csv(os.path.join(dir, 'sym_disk.csv'), table_disk()._csv())
    if 'vmax' in request.vars and request.vars.vmax == 'True':
        files += write_csv(os.path.join(dir, 'sym_ig.csv'), table_ig()._csv())
        files += write_csv(os.path.join(dir, 'sym_pg.csv'), table_pg()._csv())
        files += write_csv(os.path.join(dir, 'sym_sg.csv'), table_sg()._csv())
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
        response.flash = T('array model not supported or incomplete info: %(symid)s, %(model)s',
                           dict(symid=symid, model=sym_type))
        return None
    s.get_sym_info()
    d = s.info
    d['mtime'] = mtime(symid, 'sym_info')
    return d

@auth.requires_login()
def batch_files():
    if not hasattr(config, 'sym_node'):
        raise Exception('no known sym compute node. report to site admins.')

    scp = ['scp', '-o', 'ConnectTimeout=5', '-o', 'StrictHostKeyChecking=no', '-o', 'ForwardX11=no']
    ssh = ['ssh', '-o', 'ConnectTimeout=5', '-o', 'StrictHostKeyChecking=no', '-o', 'ForwardX11=no', '-t']

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
        cmd = ssh + ['-tt', config.sym_node, 'sudo', '-E',
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

def pretty_size(size, unit):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'EB']
    units_index = {'B':0, 'KB':1, 'MB':2, 'GB':3, 'TB':4, 'EB':5}
    size = float(size)
    for u in units[units_index[unit]:]:
        if size < 1000:
           return '%.2f'%size, ' ', T(u)
        size = size/1024
    return '%.2f'%size, ' ', T(u)

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


class table(object):
    def __init__(self, symid=None, func=None, innerhtml=None):
        if innerhtml is None:
            innerhtml='_'.join((func, str(symid)))
        self.symid = symid
        self.innerhtml = innerhtml
        self.id_prefix = innerhtml
        self.func = func
        self.line_count = 0
        self.id_perpage = '_'.join((self.id_prefix, 'perpage'))
        self.cellclasses = {'cell1': 'cell2', 'cell2': 'cell1'}
        self.cellclass = 'cell2'

        if self.id_perpage in request.vars:
            self.perpage = int(request.vars[self.id_perpage])
        else:
            self.perpage = 20

        # to be set by children
        self.additional_filters = []
        self.cols = []
        self.colprops = {}

        # to be set be instanciers
        self.filterable = True
        self.pageable = True
        self.exportable = True
        self.colored_lines = True

    def rotate_colors(self):
        if not self.colored_lines:
            return
        self.cellclass = self.cellclasses[self.cellclass]

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
            l += map(self.filter_key, self.cols+self.additional_filters)
        return l

    def table_header(self):
        titles = map(lambda x: self.colprops[x]['title'], self.cols)
        return TR(map(TH, titles), _class='sym_headers')

    def table_line(self, o):
        cells = []
        for c in self.cols:
            cells.append(TD(self.colprops[c]['str'](o),
                            _class=self.colprops[c]['_class']))
        return TR(cells, _class=self.cellclass)

    def table_lines(self):
        lines = []
        line_count = 0
        for i in sorted(self.object_list):
            if isinstance(i, str) or isinstance(i, unicode) or isinstance(i, int):
                o = self.object_list[i]
            else:
                o = i
            self.change_line_data(o)
            skip = False
            for c in self.cols+self.additional_filters:
                if not _filter(self.filter_parse(c), self.colprops[c]['get'](o)):
                    skip = True
                    break
            if skip:
                continue
            line_count += 1
            if not self.pageable or line_count <= self.perpage:
                self.rotate_colors()
                lines.append(self.table_line(o))
                if hasattr(self, 'format_extra_line'):
                    lines.append(TR(
                                   TD(
                                     self.format_extra_line(o),
                                     _colspan=len(self.cols),
                                   ),
                                   _class=self.cellclass,
                                 ))
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

    def table_additional_inputs(self):
        inputs = []
        for c in self.additional_filters:
            inputs.append(INPUT(
                    _id=self.filter_key(c),
                    _value=self.filter_parse(c),
                    _size=self.colprops[c]['size'],
                    _onKeyPress=self._ajax()
                  ))
        return inputs

    def __ajax(self):
        return """sync_ajax("%(url)s",
                       ["arrayid", %(inputs)s],
                       "%(innerhtml)s", function(){});
                  getElementById("%(innerhtml)s").innerHTML='%(spinner)s';
                """%dict(url=URL(r=request,f=self.func),
                         innerhtml=self.innerhtml,
                         inputs = ','.join(map(repr, self.ajax_inputs())),
                         spinner=IMG(_src=URL(r=request,c='static',f='images/spinner.gif')),
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
            inputs = TR(map(TD, self.table_inputs()), _class='sym_inputs')
        else:
            inputs = SPAN()

        if self.filterable and len(self.additional_filters) > 0:
            additional_filters = DIV(
              B(T('Additional filters')),
              TABLE(
                TR(map(TH, self.additional_filters)),
                TR(map(TD, self.table_additional_inputs())),
              ),
              _class='sym_highlight',
              _style='margin-bottom:6px',
            )
        else:
            additional_filters = SPAN()

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
            if hasattr(self, 'format_extra_line'):
                visible_line_count = len(lines)/2
            else:
                visible_line_count = len(lines)
            counts = SPAN('%d/%d'%(visible_line_count,line_count), _class='sym_highlight')
        else:
            paging = SPAN()
            counts = SPAN()

        if self.exportable:
            export = DIV(
                  A(
                    T('Export to csv'),
                    _href=URL(r=request,f=self.func+'_csv', vars=request.vars),
                  ),
                  _class='sym_float',
                )
        else:
            export = SPAN()

        d = DIV(
              additional_filters,
              counts,
              TABLE(
                self.table_header(),
                inputs,
                lines,
              ),
              DIV(
                INPUT(
                  _id=self.id_perpage,
                  _type='hidden',
                  _value=self.perpage,
                ),
                paging,
                export,
              ),
              DIV('', _class='spacer'),
              _class='sym_diskgroup',
            )
        return d

    def change_line_data(self, o):
        pass

    def _csv(self):
        lines = [';'.join(self.cols)]
        for i in sorted(self.object_list):
            if isinstance(i, str) or isinstance(i, unicode) or isinstance(i, int):
                o = self.object_list[i]
            else:
                o = i
            inf = []
            for c in self.cols:
                inf.append(repr(str(self.colprops[c]['str'](o))))
            lines.append(';'.join(inf))
        return '\n'.join(lines)

    def csv(self):
        import gluon.contenttype
        response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
        return self._csv()


class table_disk(table):
    def __init__(self, symid=None, innerhtml=None):
        if symid is None and 'arrayid' in request.vars:
            symid = request.vars.arrayid
        table.__init__(self, symid, 'sym_disk', innerhtml)
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
    def __init__(self, symid=None, innerhtml=None, devs=None):
        if symid is None and 'arrayid' in request.vars:
            symid = request.vars.arrayid
        table.__init__(self, symid, 'sym_dev', innerhtml)
        self.cols = ['dev', 'wwn', 'conf', 'meta', 'metaflag', 'memberof',
                     'size', 'dg', 'rdf_state', 'rdf_mode',
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
            'masking': dict(
                     size=4, title='masking', _class='',
                     get=lambda x: x.masking,
                     str=lambda x: ', '.join(x.masking),
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
                self.cols += ['frontend', 'view']
            else:
                self.cols += ['masking']
        else:
            self.object_list = devs

    def change_line_data(self, dev):
        if dev.meta_count == 0:
            dev.meta_count = 'n/a'

class table_diskgroup(table):
    def __init__(self, symid=None, innerhtml=None):
        if symid is None and 'arrayid' in request.vars:
            symid = request.vars.arrayid
        table.__init__(self, symid, 'sym_diskgroup', innerhtml)
        self.cols = ['dg_number', 'dg_name', 'composition', 'dev',
                     'masked_dev']
        self.colprops = {
            'dg_number': dict(
                     size=1, title='num', _class='numeric',
                     get=lambda x: x.info['disk_group_number'],
                     str=lambda x: x.info['disk_group_number'],
                    ),
            'dg_name': dict(
                     size=12, title='name', _class='',
                     get=lambda x: x.info['disk_group_name'],
                     str=lambda x: x.info['disk_group_name'],
                    ),
            'composition': dict(
                     size=24, title='composition', _class='',
                     get=lambda x: self.get_composition(x),
                     str=lambda x: self.format_composition(x),
                    ),
            'dev': dict(
                     size=24, title='dev', _class='',
                     get=lambda x: x.dev,
                     str=lambda x: self.format_dev(x.dev),
                    ),
            'masked_dev': dict(
                     size=24, title='masked dev', _class='',
                     get=lambda x: x.masked_dev,
                     str=lambda x: self.format_dev(x.masked_dev),
                    ),
            'used': dict(
                     size=24, title='used', _class='numeric',
                     get=lambda x: x.used,
                     str=lambda x: x.used,
                    ),
            'vused': dict(
                     size=24, title='vused', _class='numeric',
                     get=lambda x: x.vused,
                     str=lambda x: x.vused,
                    ),
        }

        dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
        p = os.path.join(dir, symid)
        s = symmetrix.get_sym(p)
        s.get_sym_diskgroup()
        self.object_list = s.diskgroup

    def format_dev(self, l):
        count = SPAN(len(l), _class='sym_highlight')
        alldevs = ', '.join(l)
        if len(alldevs) < 49:
            return SPAN(count, BR(), alldevs)
        else:
            shortdevs = '('+alldevs[0:48]+' ...)'
            return SPAN(
              count, BR(),
              SPAN(
                shortdevs,
                _onclick="""a=["%s","%s"];
                            if (this.innerHTML==a[0]) {this.innerHTML=a[1]} else {this.innerHTML=a[0]}
                         """%(shortdevs, alldevs),
              ),
            )

    def get_composition(self, dg):
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
               s += ' '+spare
            l.append(s)
        return l

    def format_composition(self, dg):
        l = []
        for key in dg.diskcount:
            if len(key) == 3:
                size, tech, speed = key
                spare = None
            else:
                size, tech, speed, spare = key

            if spare is not None:
                sp = SPAN('spare', _class='sym_highlight')
            else:
                sp = SPAN()

            if tech == 'N/A':
                tech = ''

            line = SPAN(
              TD(dg.diskcount[key], _class='numeric', _style='min-width:2em'),
              TD('x'),
              TD(pretty_size(size, 'MB'), _class='numeric'),
              TD(speed, 'rpm', _class='numeric'),
              TD(tech),
              TD(sp),
            ),
            l.append(line)

        return TABLE(map(TR, l))

    def format_extra_line(self, dg):
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
              )

        d = DIV(
              SPAN(table_usage),
              SPAN(table_usage_per_size),
              DIV('', _class='spacer'),
            )
        return d

class table_ig(table):
    def __init__(self, symid=None, innerhtml=None):
        if symid is None and 'arrayid' in request.vars:
            symid = request.vars.arrayid
        table.__init__(self, symid, 'sym_ig', innerhtml)
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
    def __init__(self, symid=None, innerhtml=None):
        if symid is None and 'arrayid' in request.vars:
            symid = request.vars.arrayid
        table.__init__(self, symid, 'sym_pg', innerhtml)
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
    def __init__(self, symid=None, innerhtml=None):
        if symid is None and 'arrayid' in request.vars:
            symid = request.vars.arrayid
        table.__init__(self, symid, 'sym_sg', innerhtml)
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

class table_view(table):
    def __init__(self, symid=None, innerhtml=None):
        if symid is None and 'arrayid' in request.vars:
            symid = request.vars.arrayid
        table.__init__(self, symid, 'sym_view', innerhtml)
        self.cols = ['view', 'init_grpname', 'port_grpname', 'stor_grpname']
        self.additional_filters = ['initiator', 'port', 'dev', 'wwn',
                                   'diskgroup']
        self.colprops = {
            'init_grpname': dict(
                     size=12, title='initiator group', _class='',
                     get=lambda x: x.init_grpname,
                     str=lambda x: self.format_init_grp(x),
                    ),
            'port_grpname': dict(
                     size=12, title='port group', _class='',
                     get=lambda x: x.port_grpname,
                     str=lambda x: self.format_port_grp(x),
                    ),
            'stor_grpname': dict(
                     size=12, title='storage group', _class='',
                     get=lambda x: x.stor_grpname,
                     str=lambda x: self.format_stor_grp(x),
                    ),
            'view': dict(
                     size=12, title='view', _class='',
                     get=lambda x: x.view_name,
                     str=lambda x: self.format_view(x),
                    ),
            'initiator': dict(
                     size=0, title='initiator', _class='',
                     get=lambda x: x.ig,
                     str=lambda x: ', '.join(x.ig),
                    ),
            'port': dict(
                     size=0, title='port', _class='',
                     get=lambda x: x.pg,
                     str=lambda x: ', '.join(x.pg),
                    ),
            'dev': dict(
                     size=0, title='dev', _class='',
                     get=lambda x: x.sg,
                     str=lambda x: ', '.join(x.sg),
                    ),
            'wwn': dict(
                     size=0, title='wwn', _class='',
                     get=lambda x: [d.wwn for d in x.dev],
                     str=lambda x: ', '.join([d.wwn for d in x.dev]),
                    ),
            'diskgroup': dict(
                     size=0, title='diskgroup', _class='',
                     get=lambda x: [d.diskgroup_name for d in x.dev],
                     str=lambda x: ', '.join([d.diskgroup_name for d in x.dev]),
                    ),
        }

        dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
        p = os.path.join(dir, symid)
        s = symmetrix.get_sym(p)
        s.get_sym_view()
        self.object_list = s.view

    def format_view(self, view):
        return DIV(
            B('%s'%(view.view_name)),
            HR(),
            _style='min-width:12em',
        )

    def format_init_grp(self, view):
        return DIV(
            B(view.init_grpname),
            ' ', SPAN('%d'%len(view.ig), _class='sym_highlight'),
            HR(),
            P(B(T('Initiators'))),
            SPAN(map(P, view.ig)),
            _style='min-width:12em',
        )

    def format_port_grp(self, view):
        return DIV(
            B(view.port_grpname),
            ' ', SPAN('%d'%len(view.pg), _class='sym_highlight'),
            HR(),
            P(B(T('Ports'))),
            SPAN(map(P, view.pg)),
            _style='min-width:12em',
        )

    def format_stor_grp(self, view):
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

        return DIV(
            B(view.stor_grpname),
            ' ', SPAN('%d'%len(view.sg), _class='sym_highlight'),
            HR(),
            TABLE(
              TR(
                TH(),
                TH('count', _class='numeric'),
                TH('size', _class='numeric'),
              ),
              TR(
                TH('dev'),
                TD(dev_count, _class='numeric'),
                TD(pretty_size(size,'MB'), _class='numeric'),
              ),
              TR(
                TH('vdev'),
                TD(vdev_count, _class='numeric'),
                TD(pretty_size(vsize,'MB'), _class='numeric'),
              ),
              TR(
                TH('total'),
                TD(dev_count+vdev_count, _class='numeric'),
                TD(pretty_size(size+vsize,'MB'), _class='numeric'),
              ),
            ),
            _style='min-width:12em',
        )

    def format_extra_line(self, view):
        t = table_dev(devs=view.dev)
        t.cols += ['view']
        t.filterable = False
        t.pageable = False
        t.exportable = False
        short = T('show storage group devices')
        id = '_'.join((self.symid, view.view_name, 'devs'))
        s = SPAN(
              A(short),
              DIV(
                t.table(),
                _id=id,
                _name=id,
                _class='sym_detail',
              ),
              _onclick="""toggle_vis_block("%(id)s");
                       """%dict(id=id)
            )

        return s


@auth.requires_login()
def sym_disk_csv():
    t = table_disk()
    return t.csv()

@auth.requires_login()
def sym_disk():
    t = table_disk()
    return t.table()

@auth.requires_login()
def sym_dev_csv():
    t = table_dev()
    return t.csv()

@auth.requires_login()
def sym_dev():
    t = table_dev()
    return t.table()

@auth.requires_login()
def sym_ig_csv():
    t = table_ig()
    return t.csv()

@auth.requires_login()
def sym_ig():
    t = table_ig()
    return t.table()

@auth.requires_login()
def sym_pg_csv():
    t = table_pg()
    return t.csv()

@auth.requires_login()
def sym_pg():
    t = table_pg()
    return t.table()

@auth.requires_login()
def sym_sg_csv():
    t = table_sg()
    return t.csv()

@auth.requires_login()
def sym_sg():
    t = table_sg()
    return t.table()

@auth.requires_login()
def sym_view_csv():
    t = table_view()
    return t.csv()

@auth.requires_login()
def sym_view():
    t = table_view()
    t.colored_lines = False
    return t.table()

@auth.requires_login()
def sym_diskgroup_csv():
    t = table_diskgroup()
    return t.csv()

@auth.requires_login()
def sym_diskgroup():
    t = table_diskgroup()
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
             sync_ajax("%(url)s",["arrayid"],"%(func)s_%(symid)s", function(){});
           };
           toggle_vis_block("%(func)s_%(symid)s");
         """%dict(url=URL(r=request,f=func), func=func,
                  spinner=IMG(_src=URL(r=request,c='static',f='images/spinner.gif')),
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

