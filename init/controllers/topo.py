def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

class viz(object):
    status_color = {
      "up": "darkgreen",
      "stdby up": "darkgreen",
      "down": "darkred",
      "stdby down": "darkred",
      "warn": "orange",
    }

    edge_len_base = 100

    def get_img(self, t, v=""):
        if t == "nodes":
            return str(URL(r=request,c='static',f='node48.png'))
        elif t == "disks":
            return str(URL(r=request,c='static',f='disk48.png'))
        elif t == "services":
            return str(URL(r=request,c='static',f='svc48o.png'))
        elif t == "resources":
            return str(URL(r=request,c='static',f='action48.png'))
        elif t == "arrays":
            return str(URL(r=request,c='static',f='array.png'))
        elif t == "apps":
            return str(URL(r=request,c='static',f='pkg48.png'))
        elif t == "envs":
            return str(URL(r=request,c='static',f='array.png'))
        elif t == "countries":
            v = v.lower()
            if v == "france":
                return str(URL(r=request,c='static',f='flags/fr.png'))
            else:
                return str(URL(r=request,c='static',f='flag16.png'))
        elif t == "cities":
            return str(URL(r=request,c='static',f='city48.png'))
        elif t == "buildings":
            return str(URL(r=request,c='static',f='building48.png'))
        elif t == "rooms":
            return str(URL(r=request,c='static',f='room48.png'))
        elif t == "racks":
            return str(URL(r=request,c='static',f='rack48.png'))
        elif t == "enclosures":
            return str(URL(r=request,c='static',f='enclosure48.jpg'))
        else:
            return str(URL(r=request,c='static',f='action48.png'))

    def add_visnode(self, node_type, name):
        n = "_".join((node_type, name))
        if n in self.nodes:
            return -1
        else:
            self.nodes.append(n)
            return len(self.nodes)-1

    def get_visnode_id(self, node_type, name):
        n = "_".join((node_type, name))
        try:
            return self.nodes.index(n)
        except ValueError:
            return -1

    def get_data(self):
        return self.data

    def __init__(self, svcnames=[], nodenames=[],
                 display=[]):
        self.svcnames = set(svcnames) - set([""])
        self.nodenames = set(nodenames) - set([""])
        self.display = set(display) - set([""])
        self.nodes = []
        self.edges = []
        self.data = {"nodes": [], "edges": []}
        self.nodenames_to_svcnames()
        self.svcnames_to_nodenames()

        # data cache
        self.rs = {}
        self.locs = self.get_locs()

        # fix deps
        if "nodes" in self.display or \
           set(["countries", "cities", "buildings", "rooms", "racks", "enclosures"]) & self.display != set([]):
            self.data_nodes()
            self.data_nodes_services()

        # populate caches and vis data
        if "nodes" in self.display:
            self.add_nodes()

        if "services" in self.display:
            self.data_services()
            self.add_services()
            if "nodes" in self.display:
                self.data_nodes_services()
                self.add_nodes_services()

        if "disks" in self.display:
            self.data_disks()
            self.add_disks()
            self.add_arrays()
            self.add_arrays_disks()
            if "nodes" in self.display:
                self.add_nodes_disks()
            if "services" in self.display:
                self.add_services_disks()

        self.add_locs()
        if "nodes" in self.display:
            self.add_nodes_loc()
        elif "services" in self.display:
            self.add_services_loc()

        if "envs" in self.display:
            self.data_envs()
            self.add_envs()
            if "services" in self.display:
                self.data_services_envs()
                self.add_services_envs()
            if "nodes" in self.display:
                self.data_nodes_envs()
                self.add_nodes_envs()

        if "apps" in self.display:
            self.data_apps()
            self.add_apps()
            if "services" in self.display:
                self.data_services_apps()
                self.add_services_apps()
            if "nodes" in self.display:
                self.data_nodes_apps()
                self.add_nodes_apps()

        if "resources" in self.display:
            self.data_resources()
            self.add_resources()
            if "services" in self.display and "nodes" in self.display:
                self.add_services_resources()
                self.add_nodes_services_resources()

    def get_locs(self):
        l = []
        for t in [
              ("enclosures", "enclosure"),
              ("racks", "loc_rack"),
              ("rooms", "loc_room"),
              ("buildings", "loc_building"),
              ("cities", "loc_city"),
              ("countries", "loc_country"),
            ]:
            if t[0] in self.display:
                l.append(t)
        return l

    def nodenames_to_svcnames(self):
        q = db.svcmon.mon_nodname.belongs(self.nodenames)
        self.svcnames |= set([r.mon_svcname for r in db(q).select(db.svcmon.mon_svcname)])

    def svcnames_to_nodenames(self):
        q = db.svcmon.mon_svcname.belongs(self.svcnames)
        self.nodenames |= set([r.mon_nodname for r in db(q).select(db.svcmon.mon_nodname)])

    def data_apps(self):
        apps = set([])
        if "nodes" in self.display:
            apps |= set([r.project if r.project else "unknown" for r in self.rs["nodes"].values()])
        if "services" in self.display:
            apps |= set([r.svc_app if r.svc_app else "unknown" for r in self.rs["services"].values()])
        self.rs["apps"] = apps

    def data_services_apps(self):
        d = []
        for row in self.rs["services"].values():
            t = (row.svc_name, row.svc_app if row.svc_app else "unknown")
            if t not in d:
                d.append(t)
        self.rs["services_apps"] = d

    def data_nodes_apps(self):
        d = []
        for row in self.rs["nodes"].values():
            t = (row.nodename, row.project if row.project else "unknown")
            if t not in d:
                d.append(t)
        self.rs["nodes_apps"] = d

    def data_envs(self):
        envs = set([])
        if "nodes" in self.display:
            envs |= set([r.environnement if r.environnement else "unknown" for r in self.rs["nodes"].values()])
        if "services" in self.display:
            envs |= set([r.svc_type if r.svc_type else "unknown" for r in self.rs["services"].values()])
        self.rs["envs"] = envs

    def data_services_envs(self):
        d = []
        for row in self.rs["services"].values():
            t = (row.svc_name, row.svc_type if row.svc_type else "unknown")
            if t not in d:
                d.append(t)
        self.rs["services_envs"] = d

    def data_nodes_envs(self):
        d = []
        for row in self.rs["nodes"].values():
            t = (row.nodename, row.environnement if row.environnement else "unknown")
            if t not in d:
                d.append(t)
        self.rs["nodes_envs"] = d

    def data_services(self):
        q = db.services.svc_name.belongs(self.svcnames)
        rows = db(q).select(db.services.svc_name,
                            db.services.svc_availstatus,
                            db.services.svc_type,
                            db.services.svc_app,
                           )
        d = {}
        for row in rows:
            if row.svc_name not in d:
                d[row.svc_name] = row

        self.rs["services"] = d

    def data_nodes(self):
        q = db.nodes.nodename.belongs(self.nodenames)
        rows = db(q).select(db.nodes.nodename,
                            db.nodes.model,
                            db.nodes.os_name,
                            db.nodes.environnement,
                            db.nodes.project,
                            db.nodes.loc_country,
                            db.nodes.loc_city,
                            db.nodes.loc_building,
                            db.nodes.loc_room,
                            db.nodes.loc_rack,
                            db.nodes.enclosure,
                           )
        d = {}
        for row in rows:
            if row.nodename not in d:
                d[row.nodename] = row

        self.rs["nodes"] = d

    def data_disks(self):
        q = db.b_disk_app.disk_svcname.belongs(self.svcnames) & \
            db.b_disk_app.disk_nodename.belongs(self.nodenames)
        rows = db(q).select(db.b_disk_app.disk_id,
                            db.b_disk_app.disk_size,
                            db.b_disk_app.disk_arrayid,
                            db.b_disk_app.disk_nodename,
                            db.b_disk_app.disk_svcname)
        d = {}
        for row in rows:
            t = (row.disk_nodename, row.disk_svcname, row.disk_arrayid)
            if t not in d:
                d[t] = [row]
            else:
                d[t] += [row]

        self.rs["disks"] = d

    def data_nodes_services(self):
        q = db.svcmon.mon_svcname.belongs(self.svcnames) | \
            db.svcmon.mon_nodname.belongs(self.nodenames)
        rows = db(q).select(db.svcmon.mon_nodname,
                            db.svcmon.mon_svcname,
                            db.svcmon.mon_availstatus)
        d = {}
        for row in rows:
            t = (row.mon_nodname, row.mon_svcname)
            if t not in d:
                d[t] = row

        self.rs["nodes_services"] = d

    def data_resources(self):
        q = db.resmon.svcname.belongs(self.svcnames) & db.resmon.nodename.belongs(self.nodenames)
        rows = db(q).select(db.resmon.svcname,
                            db.resmon.nodename,
                            db.resmon.rid,
                            db.resmon.res_status,
                           )
        d = {}
        for row in rows:
            t = (row.svcname, row.rid)
            if t not in d:
                d[t] = row
        self.rs["services_resources"] = d

        d = {}
        for row in rows:
            t = (row.nodename, row.svcname, row.rid)
            if t not in d:
                d[t] = row
        self.rs["nodes_services_resources"] = d

    def add_apps(self):
        for app in self.rs['apps']:
            _id = self.add_visnode("app", app)
            self.data["nodes"].append({
              "mass": 16,
              "id": _id,
              "label": app,
              "image": self.get_img("apps"),
              "shape": "image"
            })

    def add_envs(self):
        for env in self.rs['envs']:
            _id = self.add_visnode("env", env)
            self.data["nodes"].append({
              "mass": 16,
              "id": _id,
              "label": env,
              "image": self.get_img("envs"),
              "shape": "image"
            })

    def add_locs(self):
        if "nodes" not in self.rs:
            return
        for row in self.rs['nodes'].values():
            for i, (p, col) in enumerate(self.locs):
                loc = row[col]
                if loc is None or loc == "" or loc == "Unknown":
                    continue
                _id = self.add_visnode(p, loc)
                if _id < 0:
                    continue
                self.data["nodes"].append({
                  "mass": 2+i,
                  "id": _id,
                  "label": loc,
                  "image": self.get_img(p, loc),
                  "shape": "image"
                })
        cache = []
        for row in self.rs['nodes'].values():
            for i, (p1, col1) in enumerate(self.locs[:-1]):
                v1 = row[col1]
                if v1 is None:
                    continue
                i1 = self.get_visnode_id(p1, v1)
                if i1 < 0:
                    continue
                for j, (p2, col2) in enumerate(self.locs[i+1:]):
                    v2 = row[col2]
                    if v2 is None:
                        continue
                    i2 = self.get_visnode_id(p2, v2)
                    if i2 < 0:
                        continue
                    t = (i1, i2)
                    if t in cache:
                        break
                    cache.append(t)
                    self.add_edge(i1, i2, color="lightgrey")
                    break

    def add_nodes_loc(self):
        for row in self.rs['nodes'].values():
            for p, col in self.locs:
                parent_loc = row[col]
                if parent_loc is None:
                    continue
                parent_id = self.get_visnode_id(p, parent_loc)
                if parent_id > 0:
                    nodename_id = self.get_visnode_id("node", row.nodename)
                    self.add_edge(nodename_id, parent_id, color="lightgrey")
                    break

    def add_services_loc(self):
        if "nodes_services" not in self.rs:
            return
        for (nodename, svcname), _row in self.rs["nodes_services"].items():
            row = self.rs['nodes'][nodename]
            for p, col in self.locs:
                parent_loc = row[col]
                if parent_loc is None:
                    continue
                parent_id = self.get_visnode_id(p, parent_loc)
                if parent_id > 0:
                    svcname_id = self.get_visnode_id("svc", svcname)
                    self.add_edge(
                      svcname_id, parent_id,
                      length=2,
                      color=self.status_color.get(_row.mon_availstatus, "grey"),
                      label=_row.mon_availstatus,
                    )
                    break

    def add_resources(self):
        for (svcname, rid), row in self.rs['services_resources'].items():
            rid_id = self.add_visnode("resource", svcname+"."+rid)
            self.data["nodes"].append({
              "mass": 3,
              "id": rid_id,
              "label": rid,
              "image": self.get_img("resources"),
              "shape": "image"
            })

    def add_disks(self):
        for (nodename, svcname, arrayid), rows in self.rs['disks'].items():
            if svcname is None:
                svcname = ""
            label = self.fmt_disk_label(arrayid, rows)
            disk_id = self.get_visnode_id("disk", label)
            if disk_id < 0:
                disk_id = self.add_visnode("disk", label)
                self.data["nodes"].append({
                  "mass": 3,
                  "id": disk_id,
                  "label": label,
                  "image": self.get_img("disks"),
                  "shape": "image"
                })

    def add_nodes(self):
        for nodename in self.nodenames:
            self.add_node(nodename)

    def add_node(self, nodename):
        d = self.rs["nodes"].get(nodename, {})
        label = nodename+"\n"+', '.join((d.get("os_name"), d.get("model", "")))
        nodename_id = self.add_visnode("node", nodename)
        self.data["nodes"].append({
          "mass": 3,
          "id": nodename_id,
          "label": label,
          "image": self.get_img("nodes"),
          "shape": "image"
        })

    def add_edge(self, from_node, to_node, color="#555555", label="", length=1):
        edge = {
         "from": from_node,
         "to": to_node,
         "length": self.edge_len_base*length,
         "color": color,
         "fontColor": color,
         "label": label,
         "width": 2
        }
        sig = (from_node, to_node)
        if sig in self.edges:
            return
        self.edges.append(sig)
        self.data["edges"].append(edge)

    def add_services(self):
        for svcname in self.svcnames:
            self.add_service(svcname)

    def add_service(self, svcname):
        node_id = self.add_visnode("svc", svcname)
        if node_id < 0:
            return
        row = self.rs["services"][svcname]
        self.data["nodes"].append({
          "mass": 8,
          "id": node_id,
          "label": svcname,
          "image": self.get_img("services"),
          "shape": "image",
          "fontColor": self.status_color.get(row["svc_availstatus"], "grey"),
        })

    def add_arrays(self):
        for (nodename, svcname, arrayid), rows in self.rs["disks"].items():
            if arrayid in self.nodenames:
                continue
            visnode_id = self.add_visnode("array", arrayid)
            if visnode_id < 0:
                continue
            self.data["nodes"].append({
              "mass": 4,
              "id": visnode_id,
              "label": arrayid,
              "image": self.get_img("arrays"),
              "shape": "image"
            })

    def add_nodes_services_resources(self):
        for (nodename, svcname, rid), row in self.rs["nodes_services_resources"].items():
            nodename_id = self.get_visnode_id("node", nodename)
            rid_id = self.get_visnode_id("resource", svcname+"."+rid)
            self.add_edge(nodename_id, rid_id,
                          length=1,
                          color=self.status_color.get(row.res_status, "grey"),
                          label=row.res_status,
                         )

    def add_services_resources(self):
        for (svcname, rid), row in self.rs["services_resources"].items():
            svcname_id = self.get_visnode_id("svc", svcname)
            rid_id = self.get_visnode_id("resource", svcname+"."+rid)
            self.add_edge(svcname_id, rid_id,
                          length=1,
                          color="grey",
                          label=row.res_status,
                         )

    def add_nodes_apps(self):
        for (nodename, app) in self.rs["nodes_apps"]:
            nodename_id = self.get_visnode_id("node", nodename)
            app_id = self.get_visnode_id("app", app)
            self.add_edge(nodename_id, app_id,
                          color="lightgrey",
                         )

    def add_services_apps(self):
        for (svcname, app) in self.rs["services_apps"]:
            svcname_id = self.get_visnode_id("svc", svcname)
            app_id = self.get_visnode_id("app", app)
            self.add_edge(svcname_id, app_id,
                          color="lightgrey",
                         )

    def add_nodes_envs(self):
        for (nodename, env) in self.rs["nodes_envs"]:
            nodename_id = self.get_visnode_id("node", nodename)
            env_id = self.get_visnode_id("env", env)
            self.add_edge(nodename_id, env_id,
                          color="lightgrey",
                         )

    def add_services_envs(self):
        for (svcname, env) in self.rs["services_envs"]:
            svcname_id = self.get_visnode_id("svc", svcname)
            env_id = self.get_visnode_id("env", env)
            self.add_edge(svcname_id, env_id,
                          color="lightgrey",
                         )

    def add_nodes_services(self):
        for (nodename, svcname), row in self.rs["nodes_services"].items():
            nodename_id = self.get_visnode_id("node", nodename)
            svcname_id = self.get_visnode_id("svc", svcname)
            self.add_edge(nodename_id, svcname_id,
                          length=2,
                          color=self.status_color.get(row.mon_availstatus, "grey"),
                          label=row.mon_availstatus,
                         )

    def fmt_disk_label(self, arrayid, rows):
        label = ""
        for row in rows:
            label += "\n"+row.disk_id+"\t"+beautify_size_mb(row.disk_size)
        return label

    def add_services_disks(self):
        for (nodename, svcname, arrayid), rows in self.rs["disks"].items():
            if svcname == "":
                continue
            svcname_id = self.get_visnode_id("svc", svcname)
            disk_id = self.get_visnode_id("disk", self.fmt_disk_label(arrayid, rows))
            self.add_edge(svcname_id, disk_id)

            if nodename == arrayid:
                nodename_id = self.get_visnode_id("node", nodename)
                disk_id = self.get_visnode_id("disk", self.fmt_disk_label(arrayid, rows))
                self.add_edge(nodename_id, disk_id)

    def add_nodes_disks(self):
        for (nodename, svcname, arrayid), rows in self.rs["disks"].items():
            if svcname != "":
                continue
            nodename_id = self.get_visnode_id("node", nodename)
            disk_id = self.get_visnode_id("disk", self.fmt_disk_label(arrayid, rows))
            self.add_edge(nodename_id, disk_id)

    def add_arrays_disks(self):
        for (nodename, svcname, arrayid), rows in self.rs["disks"].items():
            if arrayid in self.nodenames:
                continue
            array_id = self.get_visnode_id("array", arrayid)
            disk_id = self.get_visnode_id("disk", self.fmt_disk_label(arrayid, rows))
            self.add_edge(array_id, disk_id)

@auth.requires_login()
@service.json
def json_topo_data():
    f = request.vars.get("svcnames")
    if f is not None and f != "":
        q = _where(None, 'services', f, 'svc_name')
        svcnames = [r.svc_name for r in db(q).select(db.services.svc_name, cacheable=True)]
    else:
        svcnames = []

    f = request.vars.get("nodenames")
    if f is not None and f != "":
        q = _where(None, 'nodes', f, 'nodename')
        nodenames = [r.nodename for r in db(q).select(db.nodes.nodename, cacheable=True)]
    else:
        nodenames = []

    display = request.vars.get("display", "").split(",")
    return viz(svcnames, nodenames, display).get_data()

@auth.requires_login()
def ajax_topo():
    import uuid
    rowid = uuid.uuid1().hex
    return topo_script(rowid)

@auth.requires_login()
def topo():
    d = topo_script("topo")
    return dict(table=d)

def topo_script(eid):
    svcnames = request.vars.get("svcnames", "")
    nodenames = request.vars.get("nodenames", "")
    display = request.vars.get("display", "").split(",")
    s = SCRIPT("""init_topo("%(eid)s", {
        svcnames: "%(svcnames)s",
        nodenames: "%(nodenames)s"
       }, %(display)s)"""%dict(
         eid=eid,
         svcnames=svcnames,
         nodenames=nodenames,
         display=str(display),
       ),
    )

    def check(label="set me", name="set me", cl="action16"):
        return DIV(
          INPUT(
            _type="checkbox",
            _name=name,
            _style="vertical-align:text-bottom",
            _value="true" if name in display else "false",
            value=True if name in display else False,
          ),
          SPAN(
            T(label),
            _class=cl,
            _style="padding-left:18px;margin-left:0.2em",
          ),
        )

    link = DIV(
      DIV(
        _style="word-break:break-all",
        _class="white_float hidden",
      ),
      DIV(
        _onclick="""
          url = $(location).attr("origin")
          url += "/init/topo/topo?svcnames=%(svcnames)s&nodenames=%(nodenames)s&display=%(display)s"
          $(this).siblings("div").html(url)
          $(this).siblings("div").toggle()
        """ % dict(
          svcnames=request.vars.get("svcnames", ""),
          nodenames=request.vars.get("nodenames", ""),
          display=request.vars.get("display", ""),
        ),
        _class="link16 clickable",
      ),
    )

    d = DIV(
      DIV(
        link,
        check("Services", "services", "svc"),
        check("Apps", "apps", "svc"),
        check("Environment", "envs", "svc"),
        check("Resources", "resources", "svc"),
        check("Nodes", "nodes", "hw16"),
        check("Countries", "countries", "loc"),
        check("Cities", "cities", "loc"),
        check("Buildings", "buildings", "loc"),
        check("Rooms", "rooms", "loc"),
        check("Racks", "racks", "loc"),
        check("Enclosures", "enclosures", "loc"),
        check("Disks", "disks", "hd16"),
        _style="display:table-cell;vertical-align:top;text-align:left;padding:0.3em;min-width:12em",
      ),
      DIV(
        _id=eid,
        _style="display:table-cell;width:100%",
      ),
      s,
      _style="display:table-row",
    )
    return d


