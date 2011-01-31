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
    q = db.upc_dashboard.upc_user_id==auth.user_id
    rows = db(q).select(db.upc_dashboard.upc_dashboard)
    active = map(lambda x: x.upc_dashboard, rows)

    def js(item):
        if item in active:
            checked = 'false'
        else:
            checked = 'true'
        return """dashboard_item('%(item)s', '%(url)s', '%(toggle_url)s', %(checked)s);"""%dict(
                    item=item,
                    checked=checked,
                    url=URL(r=request, c='dashboard', f='call/json/'+item),
                    toggle_url=URL(r=request, c='dashboard', f='call/json/toggle'),
                  )

    d = DIV(
          DIV(
            DIV(
              H2(T('Summary')),
              DIV(
                DIV(
                  DIV(B(T('Report')), _class='title summary_header'),
                  DIV(B(T('Status')), _class='summary_header'),
                  DIV(_class='summary_header'),
                  DIV(_class='summary_header'),
                  DIV(_class='summary_header'),
                  DIV(B(T('Updated')), _class='summary_header'),
                  DIV(B(T('History')), _class='summary_header'),
                ),
                DIV(_id='sum_checks'),
                DIV(_id='sum_svcnotup'),
                DIV(_id='sum_frozen'),
                DIV(_id='sum_svcnotupdated'),
                DIV(_id='sum_svcwitherrors'),
                DIV(_id='sum_svcnotonprimary'),
                DIV(_id='sum_lastchanges'),
                DIV(_id='sum_appwithoutresp'),
                DIV(_id='sum_warrantyend'),
                DIV(_id='sum_obsoswarn'),
                DIV(_id='sum_obsosalert'),
                DIV(_id='sum_obshwwarn'),
                DIV(_id='sum_obshwalert'),
                DIV(_id='sum_obsmiss'),
                DIV(_id='sum_nodeswithoutasset'),
                DIV(_id='sum_pkgdiff'),
                DIV(_id='sum_netdeverrs'),
                _class='summary',
              ),
              _style='padding:1em;margin:1em',
            ),
            _class='container',
          ),
          DIV(_id='checks'),
          DIV(_id='svcnotup'),
          DIV(_id='frozen'),
          DIV(_id='svcnotupdated'),
          DIV(_id='svcwitherrors'),
          DIV(_id='svcnotonprimary'),
          DIV(_id='lastchanges'),
          DIV(_id='appwithoutresp'),
          DIV(_id='warrantyend'),
          DIV(_id='obsoswarn'),
          DIV(_id='obsosalert'),
          DIV(_id='obshwwarn'),
          DIV(_id='obshwalert'),
          DIV(_id='obsmiss'),
          DIV(_id='nodeswithoutasset'),
          DIV(_id='pkgdiff'),
          DIV(_id='netdeverrs'),
          SCRIPT(
            js('svcnotupdated'),
            js('checks'),
            js('frozen'),
            js('lastchanges'),
            js('svcwitherrors'),
            js('pkgdiff'),
            js('svcnotup'),
            js('svcnotonprimary'),
            js('appwithoutresp'),
            js('warrantyend'),
            js('obsosalert'),
            js('obsoswarn'),
            js('obshwalert'),
            js('obshwwarn'),
            js('obsmiss'),
            js('nodeswithoutasset'),
            js('netdeverrs'),
          ),
          _style="""
            column-width:50em;
            -moz-column-width:50em;
            -webkit-column-width:50em;
          """
        )
    return dict(dashboard=d)

@auth.requires_login()
def envfile(svcname):
    query = _where(None, 'services', svcname, 'svc_name')
    query &= _where(None, 'v_svcmon', domain_perms(), 'svc_name')
    rows = db(query).select()
    if len(rows) == 0:
        return "None"
    #return dict(svc=rows[0])
    envfile = rows[0]['services']['svc_envfile']
    if envfile is None:
        return "None"
    return DIV(
             P(T("updated: %(upd)s",dict(
                     upd=rows[0]['services']['updated']
                   ),
                ),
                _style='text-align:center',
             ),
             PRE(envfile.replace('\\n','\n'), _style="text-align:left"),
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
        return "svc_"+nodename.replace(".", "_").replace("-", "_")+"_"+svc.replace(".", "_").replace("-", "_")

    def vid_svc_dg(self, svc, dg):
        return "dg_"+svc.replace(".", "_").replace("-", "_")+"_"+dg

    def vid_node(self, node):
        return 'node_'+node.replace(".", "_").replace("-", "_")

    def vid_disk(self, id):
        return 'disk_'+str(id).replace(".", "_").replace("-", "_")

    def vid_loc(self, id):
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
        key = d.disk_arrayid,d.disk_svcname,d.disk_dg
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
        label="<tr><td>%(name)s</td><td>%(devid)s</td><td>%(size)s GB</td></tr>"%(dict(id=vid, name=d.disk_id, size=d.disk_size, img=self.img_disk, devid=d.disk_devid))
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
    def print_row(row):
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
             P(
               H2("%(svc)s@%(node)s"%dict(svc=svcname, node=node),
               _style="text-align:center")
             ),
             t,
             _class="dashboard",
           )

@auth.requires_login()
def ajax_service():
    rowid = request.vars.rowid
    rows = db(db.v_svcmon.mon_svcname==request.vars.node).select()
    viz = svcmon_viz_img(rows)
    if len(rows) == 0:
        return DIV(
                 T("No service information for %(node)s",
                   dict(node=request.vars.node)),
               )

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
        TD(s['svc_vmname'])
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
        TD(s['svc_vcpus'])
      ),
      TR(
        TD(T('vmem'), _style='font-style:italic'),
        TD(s['svc_vmem'])
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
        for i in range(1, 7):
            buff += """$('#%(tab)s_%(id)s').hide();
                       $('#li%(tab)s_%(id)s').removeClass('tab_active');
                    """%dict(tab='tab'+str(i), id=rowid)
        buff += """$('#%(tab)s_%(id)s').show();
                   $('#li%(tab)s_%(id)s').addClass('tab_active');
                """%dict(tab=tab, id=rowid)
        return buff

    t = TABLE(
      TR(
        TD(
          UL(
            LI(
              P(
                T("%(n)s", dict(n=request.vars.node)),
              ),
              _onclick="""$('#%(id)s').hide()"""%dict(id=rowid),
              _class="closetab",
            ),
            LI(
              P(
                T("properties"),
                _onclick=js('tab1', rowid)
               ),
              _id="litab1_"+str(rowid),
              _class="tab_active",
            ),
            LI(P(T("status"), _onclick=js('tab2', rowid)), _id="litab2_"+str(rowid)),
            LI(P(T("resources"), _onclick=js('tab3', rowid)), _id="litab3_"+str(rowid)),
            LI(P(T("env"), _onclick=js('tab4', rowid)), _id="litab4_"+str(rowid)),
            LI(P(T("topology"), _onclick=js('tab5', rowid)), _id="litab5_"+str(rowid)),
            LI(P(T("wiki"), _onclick=js('tab6', rowid)), _id="litab6_"+str(rowid)),
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
            _id='tab6_'+str(rowid),
            _class='cloud',
          ),
          SCRIPT(
            "ajax('%(url)s', [], '%(id)s')"%dict(
               id='tab6_'+str(rowid),
               url=URL(r=request, c='wiki', f='ajax_wiki',
                       args=['tab6_'+str(rowid), request.vars.node])
            ),
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
# XMLRPC
#
#########
@service.xmlrpc
def delete_services(hostid=None):
    if hostid is None:
        return 0
    db(db.services.svc_hostid==hostid).delete()
    db.commit()
    return 0

@service.xmlrpc
def delete_service_list(hostid=None, svcnames=[]):
    if hostid is None or len(svcnames) == 0:
        return 0
    for svcname in svcnames:
        q = (db.services.svc_name==svcname)
        q &= (db.services.svc_hostid==hostid)
        db(q).delete()
        db.commit()
    return 0

@service.xmlrpc
def begin_action(vars, vals):
    sql="""insert delayed into SVCactions (%s) values (%s)""" % (','.join(vars), ','.join(vals))
    db.executesql(sql)
    db.commit()
    return 0

@service.xmlrpc
def res_action(vars, vals):
    upd = []
    for a, b in zip(vars, vals):
        upd.append("%s=%s" % (a, b))
    sql="""insert delayed into SVCactions (%s) values (%s)""" % (','.join(vars), ','.join(vals))
    db.executesql(sql)
    db.commit()
    return 0

@service.xmlrpc
def end_action(vars, vals):
    upd = []
    h = {}
    for a, b in zip(vars, vals):
        h[a] = b
        if a not in ['hostname', 'svcname', 'begin', 'action', 'hostid']:
            upd.append("%s=%s" % (a, b))
    sql="""update SVCactions set %s where hostname=%s and svcname=%s and begin=%s and action=%s""" %\
        (','.join(upd), h['hostname'], h['svcname'], h['begin'], h['action'])
    #raise Exception(sql)
    db.executesql(sql)
    db.commit()
    if h['action'].strip("'") in ('start', 'startcontainer') and \
       h['status'].strip("'") == 'ok':
        update_virtual_asset(h['hostname'].strip("'"), h['svcname'].strip("'"))
    return 0

def update_virtual_asset(nodename, svcname):
    q = db.services.svc_name == svcname
    svc = db(q).select(db.services.svc_vmname).first()
    if svc is None:
        return
    q = db.nodes.nodename == nodename
    node = db(q).select().first()
    if node is None:
        return
    fields = ['loc_addr', 'loc_city', 'loc_zip', 'loc_room', 'loc_building',
              'loc_floor', 'loc_rack', 'power_cabinet1', 'power_cabinet2',
              'power_supply_nb', 'power_protect', 'power_protect_breaker',
              'power_breaker1', 'power_breaker2', 'loc_country']
    sql = "update nodes set "
    for f in fields:
        sql += "%s='%s',"%(f, node[f])
    sql = sql.rstrip(',')
    sql += "where nodename='%s'"%svc.svc_vmname
    db.executesql(sql)

@service.xmlrpc
def update_service(vars, vals):
    if 'svc_hostid' not in vars:
        return
    if 'updated' not in vars:
        vars += ['updated']
        vals += [datetime.datetime.now()]
    generic_insert('services', vars, vals)

@service.xmlrpc
def push_checks(vars, vals):
    generic_insert('checks_live', vars, vals)

@service.xmlrpc
def update_asset(vars, vals):
    vars.append('updated')
    vals.append(now)
    generic_insert('nodes', vars, vals)

@service.xmlrpc
def res_action_batch(vars, vals):
    generic_insert('SVCactions', vars, vals)

def _resmon_clean(node, svcname):
    if node is None or node == '':
        return 0
    if svcname is None or svcname == '':
        return 0
    q = db.resmon.nodename==node.strip("'")
    q &= db.resmon.svcname==svcname.strip("'")
    db(q).delete()
    db.commit()

@service.xmlrpc
def resmon_update(vars, vals):
    h = {}
    for a,b in zip(vars, vals[0]):
        h[a] = b
    if 'nodename' in h and 'svcname' in h:
        _resmon_clean(h['nodename'], h['svcname'])
    generic_insert('resmon', vars, vals)

@service.xmlrpc
def register_disk(vars, vals):
    generic_insert('svcdisks', vars, vals)

@service.xmlrpc
def register_sync(vars, vals):
    pass

@service.xmlrpc
def register_ip(vars, vals):
    pass

@service.xmlrpc
def register_fs(vars, vals):
    pass

@service.xmlrpc
def insert_stats_fs_u(vars, vals):
    generic_insert('stats_fs_u', vars, vals)

@service.xmlrpc
def insert_stats_cpu(vars, vals):
    generic_insert('stats_cpu', vars, vals)

@service.xmlrpc
def insert_stats_mem_u(vars, vals):
    generic_insert('stats_mem_u', vars, vals)

@service.xmlrpc
def insert_stats_proc(vars, vals):
    generic_insert('stats_proc', vars, vals)

@service.xmlrpc
def insert_stats_swap(vars, vals):
    generic_insert('stats_swap', vars, vals)

@service.xmlrpc
def insert_stats_block(vars, vals):
    generic_insert('stats_block', vars, vals)

@service.xmlrpc
def insert_stats_blockdev(vars, vals):
    generic_insert('stats_blockdev', vars, vals)

@service.xmlrpc
def insert_stats_netdev(vars, vals):
    generic_insert('stats_netdev', vars, vals)

@service.xmlrpc
def insert_stats_netdev_err(vars, vals):
    generic_insert('stats_netdev_err', vars, vals)

@service.xmlrpc
def insert_pkg(vars, vals):
    generic_insert('packages', vars, vals)

@service.xmlrpc
def update_sym_xml(symid, vars, vals):
    import os

    dir = 'applications'+str(URL(r=request,c='uploads',f='symmetrix'))
    if not os.path.exists(dir):
        os.makedirs(dir)

    dir = os.path.join(dir, symid)
    if not os.path.exists(dir):
        os.makedirs(dir)

    for a,b in zip(vars, vals):
        a = os.path.join(dir, a)
        try:
            f = open(a, 'w')
            f.write(b)
            f.close()
        except:
            pass

    symmetrix = local_import('symmetrix', reload=True)
    s = symmetrix.get_sym(dir)
    if s is None:
        return

    #
    # better to create hashes from the batch rather than
    # during an interactive session
    #
    s.get_sym_all()

    #
    # populate the diskinfo table
    #
    vars = ['disk_id', 'disk_devid', 'disk_arrayid']
    vals = []
    for devname, dev in s.dev.items():
        vals.append([dev.wwn, devname, symid])
    generic_insert('diskinfo', vars, vals)

@service.xmlrpc
def delete_pkg(node):
    if node is None or node == '':
        return 0
    db(db.packages.pkg_nodename==node).delete()
    db.commit()

@service.xmlrpc
def insert_patch(vars, vals):
    generic_insert('patches', vars, vals)

@service.xmlrpc
def delete_patch(node):
    if node is None or node == '':
        return 0
    db(db.patches.patch_nodename==node).delete()
    db.commit()

@service.xmlrpc
def delete_syncs(svcname):
    pass

@service.xmlrpc
def delete_ips(svcname, node):
    pass

@service.xmlrpc
def delete_fss(svcname):
    pass

@service.xmlrpc
def delete_disks(svcname, node):
    if svcname is None or svcname == '':
        return 0
    db((db.svcdisks.disk_svcname==svcname)&(db.svcdisks.disk_nodename==node)).delete()
    db.commit()

@service.xmlrpc
def svcmon_update(vars, vals):
    # don't trust the server's time
    h = {}
    for a,b in zip(vars, vals):
        if a == 'mon_updated':
            continue
        h[a] = b
    now = datetime.datetime.now()
    tmo = now - datetime.timedelta(minutes=18)
    h['mon_updated'] = now
    if 'mon_hbstatus' not in h:
        h['mon_hbstatus'] = 'undef'
    generic_insert('svcmon', h.keys(), h.values())

    query = db.svcmon_log.mon_svcname==h['mon_svcname']
    query &= db.svcmon_log.mon_nodname==h['mon_nodname']
    last = db(query).select(orderby=~db.svcmon_log.id, limitby=(0,1))
    if len(last) == 0:
        _vars = ['mon_begin',
                 'mon_end',
                 'mon_svcname',
                 'mon_nodname',
                 'mon_overallstatus',
                 'mon_ipstatus',
                 'mon_fsstatus',
                 'mon_diskstatus',
                 'mon_containerstatus',
                 'mon_appstatus',
                 'mon_syncstatus',
                 'mon_hbstatus']
        _vals = [h['mon_updated'],
                 h['mon_updated'],
                 h['mon_svcname'],
                 h['mon_nodname'],
                 h['mon_overallstatus'],
                 h['mon_ipstatus'],
                 h['mon_fsstatus'],
                 h['mon_diskstatus'],
                 h['mon_containerstatus'],
                 h['mon_appstatus'],
                 h['mon_syncstatus'],
                 h['mon_hbstatus']]
        generic_insert('svcmon_log', _vars, _vals)
    elif last[0].mon_end < tmo:
        _vars = ['mon_begin',
                 'mon_end',
                 'mon_svcname',
                 'mon_nodname',
                 'mon_overallstatus',
                 'mon_ipstatus',
                 'mon_fsstatus',
                 'mon_diskstatus',
                 'mon_containerstatus',
                 'mon_appstatus',
                 'mon_syncstatus',
                 'mon_hbstatus']
        _vals = [last[0].mon_end,
                 h['mon_updated'],
                 h['mon_svcname'],
                 h['mon_nodname'],
                 "undef",
                 "undef",
                 "undef",
                 "undef",
                 "undef",
                 "undef",
                 "undef",
                 "undef"]
        generic_insert('svcmon_log', _vars, _vals)
        _vars = ['mon_begin',
                 'mon_end',
                 'mon_svcname',
                 'mon_nodname',
                 'mon_overallstatus',
                 'mon_ipstatus',
                 'mon_fsstatus',
                 'mon_diskstatus',
                 'mon_containerstatus',
                 'mon_appstatus',
                 'mon_syncstatus',
                 'mon_hbstatus']
        _vals = [h['mon_updated'],
                 h['mon_updated'],
                 h['mon_svcname'],
                 h['mon_nodname'],
                 h['mon_overallstatus'],
                 h['mon_ipstatus'],
                 h['mon_fsstatus'],
                 h['mon_diskstatus'],
                 h['mon_containerstatus'],
                 h['mon_appstatus'],
                 h['mon_hbstatus'],
                 h['mon_syncstatus']]
        generic_insert('svcmon_log', _vars, _vals)
    elif h['mon_overallstatus'] != last[0].mon_overallstatus or \
         h['mon_ipstatus'] != last[0].mon_ipstatus or \
         h['mon_fsstatus'] != last[0].mon_fsstatus or \
         h['mon_diskstatus'] != last[0].mon_diskstatus or \
         h['mon_containerstatus'] != last[0].mon_containerstatus or \
         h['mon_appstatus'] != last[0].mon_appstatus or \
         h['mon_hbstatus'] != last[0].mon_hbstatus or \
         h['mon_syncstatus'] != last[0].mon_syncstatus:
        _vars = ['mon_begin',
                 'mon_end',
                 'mon_svcname',
                 'mon_nodname',
                 'mon_overallstatus',
                 'mon_ipstatus',
                 'mon_fsstatus',
                 'mon_diskstatus',
                 'mon_containerstatus',
                 'mon_appstatus',
                 'mon_syncstatus',
                 'mon_hbstatus']
        _vals = [h['mon_updated'],
                 h['mon_updated'],
                 h['mon_svcname'],
                 h['mon_nodname'],
                 h['mon_overallstatus'],
                 h['mon_ipstatus'],
                 h['mon_fsstatus'],
                 h['mon_diskstatus'],
                 h['mon_containerstatus'],
                 h['mon_appstatus'],
                 h['mon_syncstatus'],
                 h['mon_hbstatus']]
        generic_insert('svcmon_log', _vars, _vals)
        db(db.svcmon_log.id==last[0].id).update(mon_end=h['mon_updated'])
    else:
        db(db.svcmon_log.id==last[0].id).update(mon_end=h['mon_updated'])


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
            'svc_name',
            'err',
            'svc_app',
            'svc_drptype',
            'svc_containertype',
            'svc_vmname',
            'svc_vcpus',
            'svc_vmem',
            'svc_guestos',
            'svc_autostart',
            'svc_nodes',
            'svc_drpnode',
            'svc_drpnodes',
            'svc_comment',
            'svc_created',
            'svc_updated',
            'svc_type',
            'environnement',
            'mon_nodname',
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
            'err': HtmlTableColumn(
                     title = 'Action errors',
                     field='err',
                     display = False,
                     img = 'action16',
                    ),
        }
        self.colprops.update(svcmon_colprops)
        self.colprops.update(v_services_colprops)
        self.colprops.update(v_nodes_colprops)
        self.colprops['svc_updated'].field = 'svc_updated'
        for i in self.cols:
            self.colprops[i].table = None
            self.colprops[i].t = self
        for i in ['mon_nodname', 'svc_name', 'svc_containertype', 'svc_app',
                  'svc_type', 'environnement', 'mon_overallstatus', 'mon_syncstatus']:
            self.colprops[i].display = True
        self.span = 'svc_name'
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

    def checkbox_disabled(self, o):
        responsibles = self.colprops['responsibles'].get(o)
        if responsibles is None:
            return True
        if self.user_name in responsibles.split(', '):
            return False
        return True

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

        if o.err>0:
            err = A(
                    IMG(
                      _src=URL(r=request,c='static',f='exclamation_red.png'),
                      _title="%d unaknowledged errors"%o.err),
                      _href=URL(r=request,c='svcactions',f='svcactions',
                                vars={'actions_f_svcname': o.svc_name,
                                      'actions_f_status': 'err',
                                      'actions_f_ack': '!1|empty',
                                      'clear_filters': 'true'}
                            )
                  )
        else:
            err = ''

        if o.mon_frozen == 1:
            frozen = IMG(
                       _src=URL(r=request,c='static',f='frozen16.png'),
                     )
        else:
            frozen = ''

        return SPAN(
                 act,
                 err,
                 frozen,
               )

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
                  click_toggle_vis('%(div)s', 'block');
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

@auth.requires_login()
def service_action():
    action = request.vars.select_action
    request.vars.select_action = 'choose'

    if action is None or action == '' or action == 'choose':
        return

    ids = ([])
    for key in [ k for k in request.vars.keys() if 'check_' in k ]:
        ids += ([key[6:]])

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
        cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                      '-o', 'ForwardX11=no',
                      '-o', 'PasswordAuthentication=no',
               'opensvc@'+node,
               '--',
               'sudo', '/opt/opensvc/bin/svcmgr', force, '--service', svc, action]
        return ' '.join(cmd)

    s = []
    vals = []
    vars = ['command']
    for row in rows:
        vals.append([fmt_action(row[0], row[1], action)])
        s.append('@'.join((row[0], row[1])))

    purge_action_queue()
    generic_insert('action_queue', vars, vals)
    from subprocess import Popen
    actiond = 'applications'+str(URL(r=request,c='actiond',f='actiond.py'))
    process = Popen(actiond)
    process.communicate()
    _log('service.action', 'run %(a)s on %(s)s', dict(a=action, s=', '.join(s)))


@auth.requires_login()
def ajax_svcmon_col_values():
    t = table_svcmon('svcmon', 'ajax_svcmon')
    col = request.args[0]
    o = db.v_svcmon[col]
    q = _where(None, 'v_svcmon', domain_perms(), 'mod_nodname')
    q = apply_db_filters(q, 'v_svcmon')
    for f in t.cols:
        q = _where(q, 'v_svcmon', t.filter_parse(f), f)
    t.object_list = db(q).select(orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_svcmon():
    t = table_svcmon('svcmon', 'ajax_svcmon')

    if len(request.args) == 2:
        action = request.args[0]
        saction = request.args[1]
        try:
            if action == 'do_action':
                do_action(t.get_checked(), saction)
        except ToolError, e:
            t.flash = str(e)

    o = db.v_svcmon.mon_svcname
    o |= ~db.v_svcmon.mon_nodtype
    o |= db.v_svcmon.mon_nodname
    o |= ~db.v_svcmon.mon_overallstatus

    q = _where(None, 'v_svcmon', domain_perms(), 'mon_svcname')
    q = apply_db_filters(q, 'v_svcmon')
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


