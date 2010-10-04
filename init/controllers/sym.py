import os
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
                  TH('%d MB'%size),
                  TD(free),
                  TD(used),
                  TD(total),
                  TD(pct),
                )
         m.append(line)

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
            TABLE(
              TR(
                TH(),
                TH('GB'),
                TH('dev'),
              ),
              TR(
                TH('free'),
                TD((dg.total-dg.used)//1024),
                TD(dev_count-masked_dev_count),
              ),
              TR(
                TH('used'),
                TD(dg.used//1024),
                TD(masked_dev_count),
              ),
              TR(
                TH('total'),
                TD(dg.total//1024),
                TD(dev_count),
              ),
              TR(
                TH('%used'),
                TD(usage),
                TD(dev_usage),
              ),
            ),
            _class='sym_float',
            _style='width:12em',
          ),
          DIV(
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

def sym_info(symid):
    tree = xmltree(symid, 'sym_info')
    for e in tree.getiterator('Symm_Info'): pass
    d = {}
    for se in list(e):
      d[se.tag] = se.text
    del tree
    return d

@auth.requires_login()
def index():
    import glob
    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
    pattern = "[0-9]*"
    sym_dirs = glob.glob(os.path.join(dir, pattern))
    syms = []
    perms = _domain_perms().split('|')
    
    for d in sym_dirs:
        if os.path.basename(d) not in perms:
            continue
        syms.append(sym_info(os.path.basename(d)))

    form = SQLFORM(db.sym_upload)
    if form.accepts(request.vars, session):
        response.flash = T('file uploaded')

    return dict(syms=syms, form=form)

def sym_diskgroup():
    symid = request.vars.arrayid
    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
    p = os.path.join(dir, symid)
    s = symmetrix.Vmax(p)
    d = []
    for dg in s.diskgroup.values():
        d.append(html_diskgroup(dg))
    return DIV(d)

def html_dev(dev):
    if dev.meta_count == 0:
        meta = 'n/a'
    else:
        meta = dev.meta_count

    if len(dev.view) == 0:
        view = 'free'
    else:
        view = ', '.join(dev.view)

    l = TR(
          TD(dev.info['dev_name']),
          TD(dev.info['configuration']),
          TD(meta),
          TD(dev.megabytes),
          TD(dev.diskgroup),
          TD(view),
        )
    return l

def sym_dev():
    symid = request.vars.arrayid

    def filter_parse(symid, f):
        key = 'filter_%s_%s'%(f,symid)
        if key in request.vars:
            value = request.vars[key]
        else: 
            value = ""
        return key, value

    filter_dev_key, filter_dev_value = filter_parse(symid, 'dev')
    filter_conf_key, filter_conf_value = filter_parse(symid, 'conf')
    filter_meta_key, filter_meta_value = filter_parse(symid, 'meta')
    filter_size_key, filter_size_value = filter_parse(symid, 'size')
    filter_dg_key, filter_dg_value = filter_parse(symid, 'dg')
    filter_view_key, filter_view_value = filter_parse(symid, 'view')


    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
    p = os.path.join(dir, symid)
    s = symmetrix.Vmax(p)
    lines = []
    for dev in sorted(s.dev):
        if len(filter_dev_value) > 0 and filter_dev_value not in s.dev[dev].info['dev_name']:
            continue
        if len(filter_conf_value) > 0 and filter_conf_value not in s.dev[dev].info['configuration']:
            continue
        if len(filter_meta_value) > 0 and filter_meta_value != str(s.dev[dev].meta_count):
            continue
        if len(filter_size_value) > 0 and filter_size_value != str(s.dev[dev].megabytes):
            continue
        if len(filter_dg_value) > 0 and filter_dg_value != str(s.dev[dev].diskgroup):
            continue
        if len(filter_view_value) > 0 and filter_view_value not in s.dev[dev].view:
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
              TH('dev'),
              TH('conf'),
              TH('meta'),
              TH('size'),
              TH('diskgroup'),
              TH('view'),
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
                _size=5,
                _onKeyPress=_ajax()
              ),
              INPUT(
                _id='filter_size_'+symid,
                _value=filter_size_value,
                _size=5,
                _onKeyPress=_ajax()
              ),
              INPUT(
                _id='filter_dg_'+symid,
                _value=filter_dg_value,
                _size=5,
                _onKeyPress=_ajax()
              ),
              INPUT(
                _id='filter_view_'+symid,
                _value=filter_view_value,
                _size=10,
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
    d = DIV(
          H2(
            'diskgroup (%d)'%len(s.diskgroup),
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
          H2('disks (%d)'%len(s.disk)),
          H2(
            'dev (%d)'%len(s.dev),
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
          H2('view (%d)'%len(s.view)),
          H2('initator group (%d)'%len(s.ig)),
          H2('port group (%d)'%len(s.pg)),
          H2('storage group (%d)'%len(s.sg)),
          _onclick="event.cancelBubble = true;",
        )
    return d


