# coding: utf8

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

@auth.requires_login()
def index():
    redirect(URL(r=request, c='dashboard'))

@auth.requires_login()
def envfile(svcname):
    query = _where(None, 'services', svcname, 'svc_name')
    query &= _where(None, 'services', domain_perms(), 'svc_name')
    rows = db(query).select()
    if len(rows) == 0:
        return "None"
    #return dict(svc=rows[0])
    envfile = rows[0]['svc_envfile']
    if envfile is None:
        return "None"

    envfile = envfile.replace('\\n', '\n')
    envfile = re.sub(r'([@\w]+)\s*\=\s*', r'<span class=syntax_green>\1</span> = ', envfile)
    envfile = re.sub(r'(\[[#\w]+\])', r'<br><span class=syntax_red>\1</span>', envfile)
    envfile = re.sub(r'(@\w+)', r'<span class=syntax_blue>\1</span>', envfile)
    envfile = re.sub(r'\n', r'<br>', envfile)

    return DIV(
             P(T("updated: %(upd)s",dict(
                     upd=rows[0]['updated']
                   ),
                ),
                _style='text-align:center',
             ),
             #envfile,
             TT(XML(envfile), _style="text-align:left"),
           )

class viz(object):
    import os
    vizdir = os.path.join(os.getcwd(), 'applications', 'init', 'static')
    vizprefix = 'tempviz'
    loc = {
        'country': {},
        'city': {},
        'building': {},
        'floor': {},
        'room': {},
        'rack': {},
    }
    svcclu = {}
    services = set([])
    resources = {}
    nodes = set([])
    disks = {}
    cdg = {}
    cdgdg = {}
    vidcdg = {}
    array = {}
    arrayinfo = {}
    disk2svc = set([])
    node2disk = set([])
    node2svc = set([])
    data = ""
    img_node = 'applications'+str(URL(r=request,c='static',f='node.png'))
    img_disk = 'applications'+str(URL(r=request,c='static',f='hd.png'))

    def __str__(self):
        buff = """
        graph G {
                //size=12;
                rankdir=LR;
                ranksep=2.5;
                //nodesep = 0.1;
                //sep=0.1;
                splines=false;
                penwidth=1;
                //center=true;
                fontsize=8;
                compound=true;
                node [shape=plaintext, fontsize=8];
                edge [fontsize=8];
                bgcolor=white;

        """
        self.add_services()
        self.add_arrays()
        self.add_citys()
        #self.rank(['cluster_'+s for s in self.array])
        #self.rank(self.services)
        buff += self.data
        buff += "}"
        return buff

    def write(self, type):
        import tempfile
        f = tempfile.NamedTemporaryFile(dir=self.vizdir, prefix=self.vizprefix)
        f.close()
        dot = f.name + '.dot'
        f = open(dot, 'w')
        f.write(str(self))
        f.close()
        if type == 'dot':
            return dot
        from subprocess import Popen
        dst = f.name + '.' + type
        cmd = [ 'dot', '-T'+type, '-o', dst, dot ]
        process = Popen(cmd, stdout=None, stderr=None)
        process.communicate()
        return dst

    def viz_cron_cleanup(self):
        """ unlink static/tempviz*.png
        """
        import os
        import glob
        files = []
        for name in glob.glob(os.path.join(self.vizdir, self.vizprefix+'*.png')):
            files.append(name)
            os.unlink(name)
        for name in glob.glob(os.path.join(self.vizdir, self.vizprefix+'*.dot')):
            files.append(name)
            os.unlink(name)
        for name in glob.glob(os.path.join(self.vizdir, 'stats_*_[0-9]*.png')):
            files.append(name)
            os.unlink(name)
        for name in glob.glob(os.path.join(self.vizdir, 'stat_*_[0-9]*.png')):
            files.append(name)
            os.unlink(name)
        for name in glob.glob(os.path.join(self.vizdir, 'stats_*_[0-9]*.svg')):
            files.append(name)
            os.unlink(name)
        return files

    def __init__(self):
        pass

    def vid_svc(self, svc, nodename):
        if nodename is None or svc is None:
            return "unknown"
        return "svc_"+nodename.replace(".", "_").replace("-", "_")+"_"+svc.replace(".", "_").replace("-", "_")

    def vid_svc_dg(self, svc, dg):
        if svc is None:
            return "unknown"
        return "dg_"+svc.replace(".", "_").replace("-", "_")+"_"+dg

    def vid_node(self, node):
        if node is None:
            return "unknown"
        return 'node_'+node.replace(".", "_").replace("-", "_")

    def vid_disk(self, id):
        if id is None:
            return "unknown"
        return 'disk_'+str(id).replace(".", "_").replace("-", "_")

    def vid_loc(self, id):
        if id is None:
            return "unknown"
        return str(id).replace(".", "_").replace("-", "_").replace(" ", "_")

    def add_service(self, svc):
        vid = self.vid_svc(svc.svc_name, svc.mon_nodname)
        if vid in self.services: return
        self.services = set([vid])
        if svc.mon_overallstatus == "warn":
            color = "orange"
        elif svc.mon_overallstatus == "up":
            color = "green"
        else:
            color = "grey"
        servicesdata = r"""
        %(v)s [label="%(s)s", style="rounded,filled", fillcolor="%(color)s", fontsize="12"];
        """%(dict(v=vid, s=svc.svc_name, color=color))
        if svc.mon_nodname not in self.svcclu:
            self.svcclu[svc.mon_nodname] = {}
        if svc.mon_overallstatus not in self.svcclu[svc.mon_nodname]:
            self.svcclu[svc.mon_nodname][svc.mon_overallstatus] = set([])
        self.svcclu[svc.mon_nodname][svc.mon_overallstatus] |= set([servicesdata])

    def add_node(self, svc):
        vid = self.vid_node(svc.mon_nodname)
        if vid in self.nodes: return
        self.nodes |= set([vid])
        if svc.loc_city not in self.loc['city']:
            self.loc['city'][svc.loc_city] = ""
        self.loc['city'][svc.loc_city] += r"""
        %(v)s [label="", image="%(img)s"];
        subgraph cluster_%(v)s {fontsize=8; penwidth=0; label="%(n)s\n%(model)s\n%(mem)s MB"; labelloc=b; %(v)s};
        """%(dict(v=vid, n=svc.mon_nodname, model=svc.model, mem=svc.mem_bytes, img=self.img_node))

    def add_disk(self, id, disk, size="", vendor="", model="", arrayid="", devid=""):
        vid = self.vid_disk(id)
        if disk in self.disks: return
        self.disks[disk]= vid
        self.add_array(vid, arrayid, vendor, model)
        self.data += r"""
        %(id)s [label="%(name)s\n%(devid)s\n%(size)s GB", image="%(img)s"];
        """%(dict(id=vid, name=disk, size=size, img=self.img_disk, devid=devid))

    def add_array(self, vid, arrayid="", vendor="", model=""):
        if arrayid == "" or arrayid is None:
            return
        if arrayid not in self.array:
            self.array[arrayid] = set([vid])
        else:
            self.array[arrayid] |= set([vid])
        if arrayid not in self.arrayinfo:
            title = arrayid
            self.arrayinfo[arrayid] = r"%s\n%s - %s"%(title, vendor.strip(), model.strip())

    def add_services(self):
        for n in self.svcclu:
            for s in self.svcclu[n]:
                self.data += r"""subgraph cluster_%(n)s_%(s)s {penwidth=0;
                %(svcs)s
        };"""%dict(n=n.replace('.','_').replace('-','_'), s=s.replace(' ','_'), svcs=''.join(self.svcclu[n][s]))

    def add_citys(self):
        for a in self.loc['city']:
            self.data += r"""
        subgraph cluster_%(a)s {label="%(l)s"; color=grey; style=rounded; fontsize=12; %(n)s};
        """%(dict(a=self.vid_loc(a), l=a, n=self.loc['city'][a]))

    def add_arrays(self):
        for a in self.array:
            if a is None:
                continue
            nodes = [self.cdg_cluster(v) for v in self.array[a] if "cdg_" in v]
            nodes += [v for v in self.array[a] if "cdg_" not in v]
            self.data += r"""
        subgraph cluster_%(a)s {label="%(l)s"; fillcolor=lightgrey; style="rounded,filled"; fontsize=12; %(disks)s};
        """%(dict(a=a.replace("-","_"), l=self.arrayinfo[a], disks=';'.join(nodes)))

    def rank(self, list):
        return """{ rank=same; %s };
               """%'; '.join(list)

    def add_node2svc(self, svc):
        vid1 = self.vid_node(svc.mon_nodname)
        vid2 = self.vid_svc(svc.svc_name, svc.mon_nodname)
        key = vid1+vid2
        if key in self.node2svc: return
        if svc.mon_overallstatus == "up":
            color = "darkgreen"
        else:
            color = "grey"
        self.node2svc |= set([key])
        self.data += """
        edge [color=%(c)s, label="", arrowsize=0, penwidth=1]; %(n)s -- %(d)s;
        """%(dict(c=color, n=vid1, d=vid2))

    def add_disk2svc(self, disk, svc, dg=""):
        vid1 = self.disks[disk]
        if dg == "":
            vid2 = self.vid_svc(svc.svc_name, svc.mon_nodname)
        else:
            vid2 = self.vid_svc_dg(svc.svc_name, dg)
        key = vid1+vid2
        if key in self.disk2svc: return
        self.disk2svc |= set([key])
        if svc.mon_overallstatus == "up":
            color = "darkgreen"
        else:
            color = "grey"
        self.data += """
        edge [color=%(c)s, label="", arrowsize=0, penwidth=1]; %(s)s -- %(d)s;
        """%(dict(c=color, d=vid1, s=vid2))

    def cdg_cluster(self, cdg):
        if cdg not in self.cdg or len(self.cdg[cdg]) == 0:
            return ""
        if cdg in self.cdgdg:
            dg = self.cdgdg[cdg]
        else:
            dg = cdg

        return r"""
            %(cdg)s [shape="plaintext"; label=<<table color="white"
            cellspacing="0" cellpadding="2" cellborder="1">
            <tr><td colspan="3">%(dg)s</td></tr>
            <tr><td>wwid</td><td>devid</td><td>size</td></tr>
            %(n)s
            </table>>]"""%dict(dg=dg, cdg=cdg, n=''.join(self.cdg[cdg]))

    def vid_cdg(self, d):
        if d.disk_id.startswith(d.disk_nodename):
            key = d.disk_arrayid,d.disk_nodename,d.disk_dg
        else:
            key = d.disk_arrayid,d.disk_dg
        cdg = 'cdg_'+str(len(self.vidcdg))
        if key not in self.vidcdg:
            self.vidcdg[key] = cdg
            self.cdgdg[cdg] = d.disk_dg
        return self.vidcdg[key]

    def add_dgdisk(self, d):
        cdg = self.vid_cdg(d)
        vid = self.vid_disk(d.id)
        self.disks[d.disk_id] = vid
        self.add_array(cdg, d.disk_arrayid, d.disk_vendor, d.disk_model)
        if cdg not in self.cdg:
            self.cdg[cdg] = []
        label="<tr><td>%(name)s</td><td>%(devid)s</td><td>%(size)s MB</td></tr>"%(dict(id=vid, name=d.disk_id, size=d.disk_size, img=self.img_disk, devid=d.disk_devid))
        if label not in self.cdg[cdg]:
            self.cdg[cdg].append(label)

    def add_dg2svc(self, cdg, svc, dg=""):
        vid1 = cdg
        if dg == "":
            vid2 = self.vid_svc(svc.svc_name, svc.mon_nodname)
        else:
            vid2 = self.vid_svc_dg(svc.svc_name, dg)
        key = cdg+vid2
        if key in self.disk2svc: return
        self.disk2svc |= set([key])
        if svc.mon_overallstatus == "up":
            color = "darkgreen"
        else:
            color = "grey"
        self.data += """
        edge [color=%(c)s, label="", arrowsize=0, penwidth=1]; %(s)s -- %(cdg)s;
        """%(dict(c=color, d=vid1, s=vid2, cdg=cdg))

    def add_disks(self, svc):
        svccdg = set([])
        q = (db.v_svcdisks.disk_svcname==svc.svc_name)
        q &= (db.v_svcdisks.disk_nodename==svc.mon_nodname)
        q &= (db.v_svcdisks.disk_id!="")
        dl = db(q).select()
        if len(dl) == 0:
            disk_id = svc.mon_nodname + "_unknown"
            self.add_disk(svc.mon_nodname, disk_id, size="?")
            self.add_disk2svc(disk_id, svc)
        else:
            for d in dl:
                if d.disk_dg is None or d.disk_dg == "":
                    disk_id = svc.mon_nodname + "_unknown"
                    self.add_disk(svc.mon_nodname, disk_id, size="?")
                    self.add_disk2svc(disk_id, svc)
                else:
                    svccdg |= set([self.vid_cdg(d)])
                    self.add_dgdisk(d)
        for cdg in svccdg:
            self.add_dg2svc(cdg, svc)

def svcmon_viz_img(services):
    v = viz()
    for svc in services:
        v.add_node(svc)
        v.add_disks(svc)
        v.add_service(svc)
        v.add_node2svc(svc)
    fname = v.write('png')
    import os
    img = str(URL(r=request,c='static',f=os.path.basename(fname)))
    return img

def svcmon_viz(ids):
    if len(ids) == 0:
        return SPAN()
    q = db.v_svcmon.id.belongs(ids)
    services = db(q).select()
    return IMG(_src=svcmon_viz_img(services))

def viz_cron_cleanup():
    return viz().viz_cron_cleanup()

@auth.requires_login()
def ajax_res_status():
    svcname = request.vars.mon_svcname
    node = request.vars.node
    return res_status(svcname, node)

def res_status(svcname, node):
    rows = db((db.resmon.svcname==svcname)&(db.resmon.nodename==node)).select(orderby=db.resmon.rid)
    if len(rows) == 0:
        return SPAN()
    updated = rows.first().updated

    def print_row(row):
        if row.updated < now - datetime.timedelta(minutes=15):
            cssclass = 'status_undef'
        else:
            cssclass = 'status_'+row.res_status.replace(" ", "_")
        return (TR(
                 TD(row.rid),
                 TD(row.res_status, _class='%s'%cssclass),
                 TD(row.res_desc),
               ),
               TR(
                 TD(),
                 TD(),
                 TD(PRE(row.res_log)),
               ))
    t = TABLE(
          TR(
            TH('id'),
            TH('status'),
            TH('description'),
          ),
          map(print_row, rows)
    )
    return DIV(
             DIV(
               H2("%(svc)s@%(node)s"%dict(svc=svcname, node=node)),
               T("(updated on %(d)s)", dict(d=str(updated))),
               _style="text-align:center;margin-bottom:20px",
             ),
             t,
             _class="dashboard",
           )

@auth.requires_login()
def ajax_service():
    rowid = request.vars.rowid
    tab = request.vars.tab
    if tab is None:
        tab = "tab1"

    rows = db(db.services.svc_name==request.vars.node).select()
    if len(rows) == 0:
        return DIV(
                 T("No service information for %(node)s",
                   dict(node=request.vars.node)),
               )

    rows = db(db.v_svcmon.mon_svcname==request.vars.node).select()
    if len(rows) == 0:
        return DIV(
                 T("No service information for %(node)s",
                   dict(node=request.vars.node)),
               )

    viz = svcmon_viz_img(rows)
    s = rows[0]

    t_misc = TABLE(
      TR(
        TD(T('opensvc version'), _style='font-style:italic'),
        TD(s['svc_version'])
      ),
      TR(
        TD(T('unacknowledged errors'), _style='font-style:italic'),
        TD(s['err'])
      ),
      TR(
        TD(T('type'), _style='font-style:italic'),
        TD(s['svc_type'])
      ),
      TR(
        TD(T('HA'), _style='font-style:italic'),
        TD(T('yes') if s['svc_ha'] == 1 else T('no'))
      ),
      TR(
        TD(T('application'), _style='font-style:italic'),
        TD(s['svc_app'])
      ),
      TR(
        TD(T('comment'), _style='font-style:italic'),
        TD(s['svc_comment'])
      ),
      TR(
        TD(T('created'), _style='font-style:italic'),
        TD(s['svc_created'])
      ),
      TR(
        TD(T('last update'), _style='font-style:italic'),
        TD(s['svc_updated'])
      ),
      TR(
        TD(T('container type'), _style='font-style:italic'),
        TD(s['svc_containertype'])
      ),
      TR(
        TD(T('container name'), _style='font-style:italic'),
        TD(s['mon_vmname'])
      ),
      TR(
        TD(T('responsibles'), _style='font-style:italic'),
        TD(s['responsibles'])
      ),
      TR(
        TD(T('responsibles mail'), _style='font-style:italic'),
        TD(s['mailto'])
      ),
      TR(
        TD(T('primary node'), _style='font-style:italic'),
        TD(s['svc_autostart'])
      ),
      TR(
        TD(T('nodes'), _style='font-style:italic'),
        TD(s['svc_nodes'])
      ),
      TR(
        TD(T('drp node'), _style='font-style:italic'),
        TD(s['svc_drpnode'])
      ),
      TR(
        TD(T('drp nodes'), _style='font-style:italic'),
        TD(s['svc_drpnodes'])
      ),
      TR(
        TD(T('vcpus'), _style='font-style:italic'),
        TD(s['mon_vcpus'])
      ),
      TR(
        TD(T('vmem'), _style='font-style:italic'),
        TD(s['mon_vmem'])
      ),
    )

    def print_status_row(row):
        r = DIV(
              H2(row.mon_nodname, _style='text-align:center'),
              svc_status(row),
              _style='float:left; padding:0 1em',
            )
        return r
    status = map(print_status_row, rows)
    t_status = SPAN(
                 status,
               )

    def print_rstatus_row(row):
        r = DIV(
              res_status(row.mon_svcname, row.mon_nodname),
              _style='float:left',
            )
        return r
    rstatus = map(print_rstatus_row, rows)
    t_rstatus = SPAN(
                  rstatus,
                )

    def js(tab, rowid):
        buff = ""
        for i in range(1, 12):
            buff += """$('#%(tab)s_%(id)s').hide();
                       $('#li%(tab)s_%(id)s').removeClass('tab_active');
                    """%dict(tab='tab'+str(i), id=rowid)
        buff += """$('#%(tab)s_%(id)s').show();
                   $('#li%(tab)s_%(id)s').addClass('tab_active');
                   if ("%(tab)s" in callbacks) {
                     callbacks["%(tab)s"]();
                     delete callbacks["%(tab)s"];
                   }
                """%dict(tab=tab, id=rowid)
        return buff

    def grpprf(rowid):
        if s['svc_nodes'] is None or s['svc_drpnodes'] is None:
            return SPAN()
        now = datetime.datetime.now()
        b = now - datetime.timedelta(days=0,
                                     hours=now.hour,
                                     minutes=now.minute,
                                     microseconds=now.microsecond)
        e = b + datetime.timedelta(days=1)

        timepicker = """Calendar.setup({inputField:this.id, ifFormat:"%Y-%m-%d %H:%M:%S", showsTime: true,timeFormat: "24" });"""
        d = DIV(
              SPAN(
                IMG(
                  _title=T('Start'),
                  _src=URL(r=request, c='static', f='begin16.png'),
                  _style="vertical-align:middle",
                ),
                INPUT(
                  _value=b.strftime("%Y-%m-%d %H:%M"),
                  _id='grpprf_begin_'+str(rowid),
                  _class='datetime',
                  _onfocus=timepicker,
                ),
                INPUT(
                  _value=e.strftime("%Y-%m-%d %H:%M"),
                  _id='grpprf_end_'+str(rowid),
                  _class='datetime',
                  _onfocus=timepicker,
                ),
                IMG(
                  _title=T('End'),
                  _src=URL(r=request, c='static', f='end16.png'),
                  _style="vertical-align:middle",
                ),
                IMG(
                  _title=T('Refresh'),
                  _src=URL(r=request, c='static', f='refresh16.png'),
                  _style="vertical-align:middle",
                  _onclick="sync_ajax('%(url)s', ['grpprf_begin_%(id)s', 'grpprf_end_%(id)s'], 'grpprf_%(id)s', function(){eval_js_in_ajax_response('plot')});"%dict(
                    id=str(rowid),
                    url=URL(r=request, c='stats', f='ajax_perfcmp_plot?node=%s'%','.join(s['svc_nodes'].split()+s['svc_drpnodes'].split())),
                  ),
                ),
                SPAN(
                  _id='grpprf_'+str(rowid),
                ),
              ),
            )
        return d

    t = TABLE(
      TR(
        TD(
          UL(
            LI(
              P(
                T("%(n)s", dict(n=request.vars.node)),
                _class='nok',
              ),
              _onclick="""$('#%(id)s').hide()"""%dict(id=rowid),
              _class="closetab",
            ),
            LI(
              P(
                T("properties"),
                _class='svc',
                _onclick=js('tab1', rowid)
               ),
              _id="litab1_"+str(rowid),
              _class="tab_active",
            ),
            LI(P(T("status"), _class='svc', _onclick=js('tab2', rowid)), _id="litab2_"+str(rowid)),
            LI(P(T("resources"), _class='svc', _onclick=js('tab3', rowid)), _id="litab3_"+str(rowid)),
            LI(P(T("env"), _class='log16', _onclick=js('tab4', rowid)), _id="litab4_"+str(rowid)),
            LI(P(T("topology"), _class='dia16', _onclick=js('tab5', rowid)), _id="litab5_"+str(rowid)),
            LI(P(T("storage"), _class='net16', _onclick=js('tab6', rowid)), _id="litab6_"+str(rowid)),
            LI(P(T("stats"), _class='spark16', _onclick=js('tab7', rowid)), _id="litab7_"+str(rowid)),
            LI(P(T("wiki"), _class='edit', _onclick=js('tab8', rowid)), _id="litab8_"+str(rowid)),
            LI(P(T("avail"), _class='svc', _onclick=js('tab9', rowid)), _id="litab9_"+str(rowid)),
            LI(P(T("pkgdiff"), _class='pkg16', _onclick=js('tab10', rowid)), _id="litab10_"+str(rowid)),
            LI(P(T("compliance"), _class='comp16', _onclick=js('tab11', rowid)), _id="litab11_"+str(rowid)),
          ),
          _class="tab",
        ),
      ),
      TR(
        TD(
          DIV(
            t_misc,
            _id='tab1_'+str(rowid),
            _class='cloud_shown',
          ),
          DIV(
            t_status,
            _id='tab2_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            t_rstatus,
            _id='tab3_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            envfile(request.vars.node),
            _id='tab4_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=viz),
            _id='tab5_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='spinner.gif')),
            _id='tab6_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            grpprf(rowid),
            _id='tab7_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            _id='tab8_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='spinner.gif')),
            _id='tab9_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='spinner.gif')),
            _id='tab10_'+str(rowid),
            _class='cloud',
          ),
          DIV(
            IMG(_src=URL(r=request,c='static',f='spinner.gif')),
            _id='tab11_'+str(rowid),
            _class='cloud',
            _style='max-width:80em',
          ),
          SCRIPT(
            """function s%(rid)s_load_svcmon_log(){sync_ajax('%(url)s', [], '%(id)s', function(){eval_js_in_ajax_response('%(rowid)s')});}"""%dict(
               id='tab9_'+str(rowid),
               rid=str(rowid),
               rowid='avail_'+rowid,
               url=URL(r=request, c='svcmon_log', f='ajax_svcmon_log_1',
                       vars={'svcname':request.vars.node, 'rowid':'avail_'+rowid})
            ),
            "function s%(rid)s_load_wiki(){ajax('%(url)s', [], '%(id)s')}"%dict(
               id='tab8_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='wiki', f='ajax_wiki',
                       args=['tab8_'+str(rowid), request.vars.node])
            ),
            "function s%(rid)s_load_grpprf() {sync_ajax('%(url)s', ['grpprf_begin_%(id)s', 'grpprf_end_%(id)s'], 'grpprf_%(id)s', function(){eval_js_in_ajax_response('plot')})};"%dict(
               id=str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='stats', f='ajax_perfcmp_plot?node=%s'%','.join(str(s['svc_nodes']).split()+str(s['svc_drpnodes']).split())),
            ),
            "function s%(rid)s_load_pkgdiff(){ajax('%(url)s', [], '%(id)s')}"%dict(
               id='tab10_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='pkgdiff', f='svc_pkgdiff',
                       args=[request.vars.node])
            ),
            "function s%(rid)s_load_comp(){ajax('%(url)s', [], '%(id)s')}"%dict(
               id='tab11_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='compliance', f='ajax_compliance_svc',
                       args=[request.vars.node])
            ),
            "function s%(rid)s_load_stor(){ajax('%(url)s', [], '%(id)s')}"%dict(
               id='tab6_'+str(rowid),
               rid=str(rowid),
               url=URL(r=request, c='ajax_node', f='ajax_svc_stor',
                       args=['tab6_'+str(rowid), request.vars.node])
            ),
            """callbacks = {"tab6": %(id)s_load_stor,
                            "tab7": %(id)s_load_grpprf,
                            "tab8": %(id)s_load_wiki,
                            "tab9": %(id)s_load_svcmon_log,
                            "tab10": %(id)s_load_pkgdiff,
                            "tab11": %(id)s_load_comp}"""%dict(id='s'+str(rowid)),
            js(tab, rowid),
            _name='%s_to_eval'%rowid,
          ),
        ),
      ),
    )
    return t

class ex(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


#
# services view
#
################

class table_svcmon(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = [
            'mon_svcname',
            'err',
            'svc_ha',
            'svc_availstatus',
            'svc_status',
            'svc_app',
            'svc_drptype',
            'svc_containertype',
            'svc_flex_min_nodes',
            'svc_flex_max_nodes',
            'svc_flex_cpu_low_threshold',
            'svc_flex_cpu_high_threshold',
            'svc_autostart',
            'svc_nodes',
            'svc_drpnode',
            'svc_drpnodes',
            'svc_comment',
            'svc_created',
            'svc_updated',
            'svc_type',
            'svc_cluster_type',
            'mon_vmtype',
            'mon_vmname',
            'mon_vcpus',
            'mon_vmem',
            'mon_guestos',
            'environnement',
            'host_mode',
            'mon_nodname',
            'mon_availstatus',
            'mon_overallstatus',
            'mon_frozen',
            'mon_containerstatus',
            'mon_ipstatus',
            'mon_fsstatus',
            'mon_diskstatus',
            'mon_syncstatus',
            'mon_appstatus',
            'mon_hbstatus',
            'mon_updated',
            'team_responsible',
            'team_integ',
            'team_support',
            'project',
            'responsibles',
            'mailto',
            'serial',
            'model',
            'role',
            'warranty_end',
            'status',
            'type',
            'node_updated',
            'power_supply_nb',
            'power_cabinet1',
            'power_cabinet2',
            'power_protect',
            'power_protect_breaker',
            'power_breaker1',
            'power_breaker2',
            'loc_country',
            'loc_zip',
            'loc_city',
            'loc_addr',
            'loc_building',
            'loc_floor',
            'loc_room',
            'loc_rack',
            'os_name',
            'os_release',
            'os_vendor',
            'os_arch',
            'os_kernel',
            'cpu_dies',
            'cpu_cores',
            'cpu_model',
            'cpu_freq',
            'mem_banks',
            'mem_slots',
            'mem_bytes',
        ]
        self.colprops = {
            'err': col_err(
                     title = 'Action errors',
                     field='err',
                     display = True,
                     img = 'action16',
                    ),
        }
        self.colprops.update(svcmon_colprops)
        self.colprops.update(v_services_colprops)
        self.colprops.update(v_nodes_colprops)
        self.colprops['svc_updated'].field = 'svc_updated'
        for i in self.cols:
            self.colprops[i].table = 'v_svcmon'
            self.colprops[i].t = self
        for i in ['mon_nodname', 'mon_svcname', 'svc_containertype', 'svc_app',
                  'svc_type', 'host_mode', 'mon_overallstatus',
                  'mon_availstatus', 'mon_syncstatus']:
            self.colprops[i].display = True
        self.span = 'mon_svcname'
        self.sub_span = v_services_cols
        self.dbfilterable = True
        self.extraline = True
        self.extrarow = True
        self.checkboxes = True
        self.checkbox_id_col = 'id'
        self.ajax_col_values = 'ajax_svcmon_col_values'
        self.user_name = user_name()
        self.additional_tools.append('tool_topology')
        self.additional_tools.append('tool_action')
        self += HtmlTableMenu('Node actions', 'action16', [
                               'tool_action_node',
                               'tool_action_module',
                               'tool_action_moduleset'],
                              id='menu_comp_action')
        self.additional_tools.append('tool_provisioning')
        self.additional_tools.append('svc_del')

    def format_extrarow(self, o):
        if not self.spaning_line(o):
            act = A(
                    IMG(
                      _src=URL(r=request,c='static',f='action16.png'),
                      _border=0,
                    ),
                    _href=URL(
                            r=request, c='svcactions',
                            f='svcactions',
                            vars={'actions_f_svcname': o.mon_svcname,
                                  'actions_f_status_log': 'empty',
                                  'actions_f_begin': '>'+yesterday,
                                  'clear_filters': 'true'})
                  )
        else:
            act = ''

        if o.mon_frozen == 1:
            frozen = IMG(
                       _src=URL(r=request,c='static',f='frozen16.png'),
                     )
        else:
            frozen = ''

        return SPAN(
                 act,
                 frozen,
               )

    def tool_action_node(self):
        return self._tool_action("node")

    def tool_action_module(self):
        return self._tool_action("module")

    def tool_action_moduleset(self):
        return self._tool_action("moduleset")

    def _tool_action(self, mode):
        if mode in ["module", "moduleset"]:
            cmd = [
              'check',
              'fixable',
              'fix',
            ]
            cl = "comp16"
        else:
            cmd = [
              'checks',
              'pushasset',
              'pushservices',
              'pushstats',
              'pushpkg',
              'pushpatch',
              'reboot',
              'shutdown',
              'syncservices',
              'updateservices',
            ]
            cl = "node16"

        sid = 'action_s_'+mode
        s = []
        for c in cmd:
            if mode in ["module", "moduleset"]:
                confirm=T("""Are you sure you want to execute a %(a)s action on all selected nodes. Please confirm action""",dict(a=c))
            else:
                confirm=T("""Are you sure you want to execute a compliance %(a)s action on all selected nodes. Please confirm action""",dict(a=c))
            s.append(TR(
                       TD(
                         IMG(
                           _src=URL(r=request,c='static',f=action_img_h[c]),
                         ),
                       ),
                       TD(
                         A(
                           c,
                           _onclick="""if (confirm("%(text)s")){%(s)s};"""%dict(
                             s=self.ajax_submit(additional_inputs=[sid], args=['do_action', c, mode]),
                             text=confirm,
                           ),
                         ),
                       ),
                     ))

        if mode == "module":
            q = db.comp_moduleset_modules.id > 0
            o = db.comp_moduleset_modules.modset_mod_name
            rows = db(q).select(orderby=o, groupby=o)
            options = [OPTION(g.modset_mod_name,_value=g.modset_mod_name) for g in rows]
            id_col = 'comp_modules.id'
        elif mode == "moduleset":
            q = db.comp_moduleset.id > 0
            o = db.comp_moduleset.modset_name
            rows = db(q).select(orderby=o)
            options = [OPTION(g.modset_name,_value=g.modset_name) for g in rows]
            id_col = 'comp_moduleset.id'

        if mode in ["module", "modeleset"]:
            fancy_mode = mode[0].upper()+mode[1:].lower()
            actions = TABLE(
                          TR(
                            TH(
                              T("Action"),
                            ),
                            TD(
                              TABLE(*s),
                            ),
                          ),
                        )
            selector = TABLE(
                          TR(
                            TH(
                              T(fancy_mode),
                            ),
                            TD(
                              SELECT(
                                *options,
                                **dict(_id=sid,
                                       _requires=IS_IN_DB(db, id_col))
                              ),
                            ),
                          ),
                        )
        else:
            actions = TABLE(*s)
            selector = SPAN()

        d = DIV(
              A(
                T("Run "+mode),
                _class=cl,
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='tool_action_'+mode),
              ),
              DIV(
                actions,
                selector,
                _style='display:none',
                _class='white_float',
                _name='tool_action_'+mode,
                _id='tool_action_'+mode,
              ),
            )

        return d


    def svc_del(self):
        d = DIV(
              A(
                T("Delete instance"),
                _class='del16',
                _onclick="""if (confirm("%(text)s")){%(s)s};"""%dict(
                   s=self.ajax_submit(args=['svc_del']),
                   text=T("Please confirm service instances deletion"),
                ),
              ),
              _class='floatw',
            )
        return d

    def tool_topology(self):
        d = DIV(
              A(
                T("Topology"),
                _class='dia16',
                _onclick=self.ajax_submit(args=['topology']),
              ),
              _class='floatw',
            )
        return d

    def tool_provisioning(self):
        d = DIV(
              A(
                T("Provisioning"),
                _class='prov',
                _onclick="""$('#prov_container').toggle();ajax('%(url)s', [], '%(id)s')"""%dict(
                  url=URL(r=request, c='provisioning', f='prov_list'),
                  id="prov_container",
                ),
              ),
              DIV(
                _style='display:none',
                _class='white_float',
                _id="prov_container",
              ),
              _class='floatw',
            )
        return d


    def tool_action(self):
        cmd = [
          'stop',
          'start',
          'startstandby',
          'restart',
          'freeze',
          'thaw',
          'syncall',
          'syncnodes',
          'syncdrp',
          'syncfullsync',
        ]
        more_cmd = [
          'stopapp',
          'startapp',
          'stopcontainer',
          'startcontainer',
          'prstart',
          'prstop',
          'push',
          'syncquiesce',
          'syncresync',
          'syncupdate',
          'syncverify',
        ]
        def format_line(c):
            return TR(
                     TD(
                       IMG(
                         _src=URL(r=request,c='static',f=action_img_h[c]),
                       ),
                     ),
                     TD(
                       A(
                         c,
                         _onclick="""if (confirm("%(text)s")){%(s)s};"""%dict(
                           s=self.ajax_submit(additional_inputs=['force_ck'],
                                              args=['do_action', c]),
                           text=T("""Are you sure you want to execute a %(a)s action on all selected service@node. Please confirm action""",dict(a=c)),
                         ),
                       ),
                     ),
                   )

        s = []
        for c in cmd:
            s.append(format_line(c))

        t = []
        for c in more_cmd:
            t.append(format_line(c))
        t.append(
              TR(
                TD(
                  B(T('Options')),
                  _colspan=2,
                ),
              ))
        t.append(
              TR(
                TD(
                  INPUT(
                    _type='checkbox',
                    _id='force_ck',
                    _onclick='this.value=this.checked',
                    _value='false',
                  ),
                ),
                TD(
                  'force',
                ),
              ))

        d = DIV(
              A(
                T("Service action"),
                _class='action16',
                _onclick="""
                  click_toggle_vis(event, '%(div)s', 'block');
                """%dict(div='tool_action'),
              ),
              DIV(
                TABLE(*s),
                P(
                  A(
                    T('more'),
                    _onclick="""$('#more_actions').toggle('fast');$(this).hide()""",
                  ),
                  _style='text-align:center;',
                ),
                TABLE(
                  SPAN(*t),
                  _id='more_actions',
                  _style='display:none;',
                ),
                _style='display:none',
                _class='white_float',
                _name='tool_action',
                _id='tool_action',
              ),
              _class='floatw',
            )

        return d

def dash_purge_svc(svcname):
    q = db.dashboard.dash_svcname == svcname
    db(q).delete()

def check_purge_svc(svcname):
    q = db.checks_live.chk_svcname == svcname
    db(q).delete()

def appinfo_purge_svc(svcname):
    q = db.appinfo.app_svcname == svcname
    db(q).delete()

def purge_svc(svcname):
    q = db.svcmon.mon_svcname == svcname
    print db(q).count()
    if db(q).count() == 0:
        dash_purge_svc(svcname)
        check_purge_svc(svcname)
        appinfo_purge_svc(svcname)
        q = db.services.svc_name == svcname
        db(q).delete()

@auth.requires_login()
def svc_del(ids):
    groups = user_groups()

    q = db.svcmon.id.belongs(ids)
    if 'Manager' not in groups:
        # Manager can delete any svc
        # A user can delete only services he is responsible of
        l1 = db.services.on(db.svcmon.mon_svcname == db.services.svc_name)
        l2 = db.apps.on(db.services.svc_app == db.apps.app)
        l3 = db.apps_responsibles.on(db.apps.id == db.apps_responsibles.app_id)
        l4 = db.auth_group.on(db.apps_responsibles.group_id == db.auth_group.id)
        q &= (db.auth_group.role.belongs(groups)) | (db.auth_group.role==None)
        ids = map(lambda x: x.id, db(q).select(db.svcmon.id, left=(l1,l2,l3,l4)))
        q = db.svcmon.id.belongs(ids)
    rows = db(q).select()
    for r in rows:
        q = db.svcmon.id == r.id
        db(q).delete()
        _log('service.delete',
             'deleted service instance %(u)s',
              dict(u='@'.join((r.mon_svcname, r.mon_nodname))),
             svcname=r.mon_svcname,
             nodename=r.mon_nodname)
        purge_svc(r.mon_svcname)
        update_dash_compdiff_svc(r.mon_svcname)
        update_dash_moddiff(r.mon_svcname)
        update_dash_rsetdiff(r.mon_svcname)

@auth.requires_login()
def service_action():
    action = request.vars.select_action
    request.vars.select_action = 'choose'

    if action is None or action == '' or action == 'choose':
        return

    ids = ([])
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        ids += ([key[6:]])

@auth.requires_membership('CompExec')
def do_node_action(ids, action=None, mode=None):
    if mode not in ("module", "moduleset", "node"):
        raise ToolError("unsupported mode")
    if action is None or len(action) == 0:
        raise ToolError("no action specified")
    if len(ids) == 0:
        raise ToolError("no target to execute %s on"%action)

    if mode in ("module", "moduleset"):
        if not hasattr(request.vars, 'action_s_'+mode):
            raise ToolError("no module or moduleset selected")
        mod = request.vars['action_s_'+mode]

        def fmt_action(node, action, mode):
            cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                          '-o', 'ForwardX11=no',
                          '-o', 'PasswordAuthentication=no',
                          '-tt',
                   'opensvc@'+node,
                   '--',
                   'sudo', '/opt/opensvc/bin/nodemgr', 'compliance', action,
                   '--force',
                   '--'+mode, mod]
            return ' '.join(cmd)
    elif mode == "node":
        def fmt_action(node, action, mode):
            cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                          '-o', 'ForwardX11=no',
                          '-o', 'PasswordAuthentication=no',
                          '-tt',
                   'opensvc@'+node,
                   '--',
                   'sudo', '/opt/opensvc/bin/nodemgr', action,
                   '--force']
            return ' '.join(cmd)

    q = db.v_svcmon.id.belongs(ids)
    q &= db.v_svcmon.team_responsible.belongs(user_groups())
    rows = db(q).select(db.v_svcmon.mon_nodname)

    vals = []
    vars = ['command']
    for row in rows:
        vals.append([fmt_action(row.mon_nodname, action, mode)])

    purge_action_queue()
    generic_insert('action_queue', vars, vals)
    from subprocess import Popen
    actiond = 'applications'+str(URL(r=request,c='actiond',f='actiond.py'))
    process = Popen(actiond)
    process.communicate()
    if mode in ("module", "moduleset"):
        _log('node.action', 'run %(a)s of %(mode)s %(m)s on nodes %(s)s', dict(
              a=action,
              mode=mode,
              s=','.join(map(lambda x: x.mon_nodname, rows)),
              m=mod))
    elif mode == "node":
        _log('node.action', 'run %(a)s on nodes %(s)s', dict(
              a=action,
              s=','.join(map(lambda x: x.mon_nodname, rows)),
              ))

def do_action(ids, action=None):
    if action is None or len(action) == 0:
        raise ToolError("no action specified")
    if len(ids) == 0:
        raise ToolError("no target to execute %s on"%action)
    if request.vars.force_ck == 'true':
        force = '--force'
    else:
        force = ''

    # filter out services we are not responsible for
    sql = """select m.mon_nodname, m.mon_svcname
             from v_svcmon m
             join v_apps_flat a on m.svc_app=a.app
             where m.id in (%(ids)s)
             and responsible='%(user)s'
             group by m.mon_nodname, m.mon_svcname
          """%dict(ids=','.join(map(str,ids)),
                   user=user_name())
    rows = db.executesql(sql)

    def fmt_action(node, svc, action):
        action = action.replace('"', '\"').replace("'", "\'")
        cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                      '-o', 'ForwardX11=no',
                      '-o', 'PasswordAuthentication=no',
                      '-tt',
               'opensvc@'+node,
               '--',
               'sudo', '/opt/opensvc/bin/svcmgr', force, '--service', svc, action]
        return ' '.join(cmd)

    vals = []
    vars = ['command']
    for row in rows:
        vals.append([fmt_action(row[0], row[1], action)])

    purge_action_queue()
    generic_insert('action_queue', vars, vals)
    from subprocess import Popen
    actiond = 'applications'+str(URL(r=request,c='actiond',f='actiond.py'))
    process = Popen(actiond)
    process.communicate()
    for row in rows:
        _log('service.action',
             'run %(a)s on %(s)s',
             dict(a=action, s='@'.join((row[1], row[0]))),
             svcname=row[1],
             nodename=row[0])


@auth.requires_login()
def ajax_svcmon_col_values():
    t = table_svcmon('svcmon', 'ajax_svcmon')
    col = request.args[0]
    o = db.v_svcmon[col]
    q = _where(None, 'v_svcmon', domain_perms(), 'mon_nodname')
    q = apply_filters(q, db.v_svcmon.mon_nodname, db.v_svcmon.mon_svcname)
    for f in t.cols:
        q = _where(q, 'v_svcmon', t.filter_parse(f), f)
    t.object_list = db(q).select(db.v_svcmon[col], orderby=o, groupby=o, limitby=default_limitby)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_svcmon():
    t = table_svcmon('svcmon', 'ajax_svcmon')

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'svc_del':
                svc_del(t.get_checked())
        except ToolError, e:
            t.flash = str(e)
    elif len(request.args) == 2:
        action = request.args[0]
        saction = request.args[1]
        try:
            if action == 'do_action':
                do_action(t.get_checked(), saction)
        except ToolError, e:
            t.flash = str(e)
    elif len(request.args) == 3:
        action = request.args[0]
        saction = request.args[1]
        mode = request.args[2]
        try:
            if action == 'do_action':
                do_node_action(t.get_checked(), saction, mode)
        except ToolError, e:
            t.flash = str(e)

    o = db.v_svcmon.mon_svcname
    o |= db.v_svcmon.mon_nodname

    q = _where(None, 'v_svcmon', domain_perms(), 'mon_svcname')
    q = apply_filters(q, db.v_svcmon.mon_nodname, db.v_svcmon.mon_svcname)
    for f in t.cols:
        q = _where(q, 'v_svcmon', t.filter_parse(f), f)

    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'topology':
                t.flash = svcmon_viz(t.get_checked())
        except ToolError, e:
            t.flash = str(e)

    return t.html()

@auth.requires_login()
def svcmon():
    t = DIV(
          ajax_svcmon(),
          _id='svcmon',
        )
    return dict(table=t)

@auth.requires_login()
def svcmon_node():
    node = request.args[0]
    tid = 'svcmon_'+node
    t = table_svcmon(tid, 'ajax_svcmon')
    t.cols.remove('mon_nodname')

    q = _where(None, 'v_svcmon', domain_perms(), 'mon_nodname')
    q &= db.v_svcmon.mon_nodname == node
    t.object_list = db(q).select()
    t.hide_tools = True
    t.pageable = False
    t.linkable = False
    t.filterable = False
    t.exportable = False
    t.dbfilterable = False
    t.columnable = False
    t.refreshable = False
    return t.html()

