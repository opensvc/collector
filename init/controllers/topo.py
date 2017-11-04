import hashlib

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
        return

    def add_visnode(self, node_type, name, data=None):
        if data:
            cksum = hashlib.md5()
            for e in data:
                for _e in e:
                    try:
                        cksum.update(str(e[_e]))
                    except:
                        pass
            n = cksum.hexdigest()
        else:
            n = "_".join((node_type, name.lower()))
        if n in self.nodes:
            return -1
        else:
            self.nodes.append(n)
            return len(self.nodes)-1

    def country_name_to_code(self, cn):
        cn = cn.lower()
        if cn == "france":
            return "fr"
        elif cn == "united kingdom":
            return "gb"
        elif cn == "canada":
            return "ca"
        elif cn == "luxembourg":
            return "lu"
        elif cn == "espagne":
            return "es"
        elif len(cn) == 2:
            return cn

    def add_visnode_node(self, visnode_id, visnode_type="", label="", mass=1, image=None, fontColor=None):
        if visnode_type in self.visnode_id_per_type:
            self.visnode_id_per_type[visnode_type].add(visnode_id)
        else:
            self.visnode_id_per_type[visnode_type] = set([visnode_id])

        group = visnode_type
        if visnode_type == "countries":
            v = self.country_name_to_code(label)
            if v:
                group = "flag-"+v

        d = {
          "mass": 3,
          "id": visnode_id,
          "label": label,
          "group": group
        }

        if fontColor is not None:
            d["fontColor"] = fontColor

        self.data["nodes"].append(d)

    def get_visnode_ids(self, visnode_type):
        if visnode_type not in self.visnode_id_per_type:
            return set([])
        return self.visnode_id_per_type[visnode_type]

    def get_visnode_id(self, node_type, name, data=None):
        if data:
            cksum = hashlib.md5()
            for e in data:
                for _e in e:
                    try:
                        cksum.update(str(e[_e]))
                    except:
                        pass
            n = cksum.hexdigest()
        else:
            n = "_".join((node_type, name.lower()))
        try:
            return self.nodes.index(n)
        except ValueError:
            return -1

    def get_data(self):
        return self.data

    def __init__(self, svc_ids=[], node_ids=[], display=[]):
        self.svc_ids = set(svc_ids) - set([""])
        self.node_ids = set(node_ids) - set([""])
        self.display = set(display) - set([""])
        self.nodes = []
        self.edges = {}
        self.visnode_id_per_type = {}
        self.data = {"nodes": [], "edges": []}
        self.node_ids_to_svc_ids()
        self.svc_ids_to_node_ids()

        # data cache
        self.rs = {}
        self.locs = self.get_locs()

        # fix deps
        if "nodes" in self.display or \
           set(["countries", "cities", "buildings", "rooms", "racks", "enclosures", "hvvdcs", "hvpools", "hvs"]) & self.display != set([]):
            self.data_nodes()
            self.data_nodes_services()

        if "resources" in self.display:
            self.data_resources()

        # populate caches and vis data
        if "nodes" in self.display:
            self.add_nodes()

        if "services" in self.display:
            self.data_services()
            self.add_services()
            if "nodes" in self.display:
                self.add_nodes_services()

        if "arrays" in self.display:
            self.data_disks()
            self.add_arrays()

        if "disks" in self.display:
            self.data_disks()
            self.add_disks()
            if "arrays" in self.display:
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
            elif "nodes" in self.display:
                self.data_nodes_envs()
                self.add_nodes_envs()

        if "apps" in self.display:
            self.data_apps()
            self.add_apps()
            if "services" in self.display:
                self.data_services_apps()
                self.add_services_apps()
            elif "nodes" in self.display:
                self.data_nodes_apps()
                self.add_nodes_apps()

        if "resources" in self.display:
            self.add_resources()
            self.add_services_resources()
            if "services" in self.display and "nodes" in self.display:
                self.add_nodes_services_resources()

        if "san" in self.display:
            self.add_san()

    def get_locs(self):
        l = []
        for t in [
              ("hvs", "hv"),
              ("hvpools", "hvpool"),
              ("hvvdcs", "hvvdc"),
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

    def node_ids_to_svc_ids(self):
        q = db.svcmon.node_id.belongs(self.node_ids)
        self.svc_ids |= set([r.svc_id for r in db(q).select(db.svcmon.svc_id)])

    def svc_ids_to_node_ids(self):
        q = db.svcmon.svc_id.belongs(self.svc_ids)
        self.node_ids |= set([r.node_id for r in db(q).select(db.svcmon.node_id)])

    def data_apps(self):
        apps = set([])
        if "services" in self.display:
            apps |= set([r.svc_app if r.svc_app else "unknown" for r in self.rs["services"].values()])
        elif "nodes" in self.display:
            apps |= set([r.app if r.app else "unknown" for r in self.rs["nodes"].values()])
        self.rs["apps"] = apps

    def data_services_apps(self):
        d = []
        for row in self.rs["services"].values():
            t = (row.svc_id, row.svc_app if row.svc_app else "unknown")
            if t not in d:
                d.append(t)
        self.rs["services_apps"] = d

    def data_nodes_apps(self):
        d = []
        for row in self.rs["nodes"].values():
            t = (row.node_id, row.app if row.app else "unknown")
            if t not in d:
                d.append(t)
        self.rs["nodes_apps"] = d

    def data_envs(self):
        envs = set([])
        if "services" in self.display:
            envs |= set([r.svc_env if r.svc_env else "unknown" for r in self.rs["services"].values()])
        elif "nodes" in self.display:
            envs |= set([r.asset_env if r.asset_env else "unknown" for r in self.rs["nodes"].values()])
        self.rs["envs"] = envs

    def data_services_envs(self):
        d = []
        for row in self.rs["services"].values():
            t = (row.svc_id, row.svc_env if row.svc_env else "unknown")
            if t not in d:
                d.append(t)
        self.rs["services_envs"] = d

    def data_nodes_envs(self):
        d = []
        for row in self.rs["nodes"].values():
            t = (row.node_id, row.asset_env if row.asset_env else "unknown")
            if t not in d:
                d.append(t)
        self.rs["nodes_envs"] = d

    def data_services(self):
        q = db.services.svc_id.belongs(self.svc_ids)
        rows = db(q).select(db.services.svc_id,
                            db.services.svc_availstatus,
                            db.services.svc_env,
                            db.services.svc_app,
                           )
        d = {}
        for row in rows:
            if row.svc_id not in d:
                d[row.svc_id] = row

        self.rs["services"] = d

    def data_nodes(self):
        q = db.nodes.node_id.belongs(self.node_ids)
        rows = db(q).select(db.nodes.node_id,
                            db.nodes.nodename,
                            db.nodes.model,
                            db.nodes.os_name,
                            db.nodes.asset_env,
                            db.nodes.app,
                            db.nodes.loc_country,
                            db.nodes.loc_city,
                            db.nodes.loc_building,
                            db.nodes.loc_room,
                            db.nodes.loc_rack,
                            db.nodes.enclosure,
                            db.nodes.hv,
                            db.nodes.hvpool,
                            db.nodes.hvvdc,
                           )
        d = {}
        for row in rows:
            if row.node_id not in d:
                d[row.node_id] = row

        self.rs["nodes"] = d

    def data_disks(self):
        if "disks" in self.rs:
            return
        q = db.svcdisks.svc_id.belongs(self.svc_ids)
        q &= db.svcdisks.node_id.belongs(self.node_ids)
        l = db.diskinfo.on(db.svcdisks.disk_id == db.diskinfo.disk_id)
        rows = db(q).select(db.svcdisks.disk_id,
                            db.svcdisks.node_id,
                            db.svcdisks.svc_id,
                            db.svcdisks.disk_size,
                            db.diskinfo.disk_arrayid,
                            db.svcdisks.node_id,
                            left=l)
        d = {}
        for row in rows:
            t = (row.svcdisks.node_id, row.svcdisks.svc_id, row.diskinfo.disk_arrayid)
            if t not in d:
                d[t] = [row]
            else:
                d[t] += [row]

        self.rs["disks"] = d

    def data_nodes_services(self):
        q = db.svcmon.svc_id.belongs(self.svc_ids)
        rows = db(q).select(db.svcmon.node_id,
                            db.svcmon.svc_id,
                            db.svcmon.mon_availstatus)
        d = {}
        for row in rows:
            t = (row.node_id, row.svc_id)
            if t not in d:
                d[t] = row

        self.rs["nodes_services"] = d

    def data_resources(self):
        q = db.resmon.svc_id.belongs(self.svc_ids)
	q &= db.resmon.node_id.belongs(self.node_ids)
        q &= db.resmon.res_disable == 0
        g = db.resmon.node_id | db.resmon.svc_id | db.resmon.res_type | db.resmon.res_status
        rows = db(q).select(db.resmon.svc_id,
                            db.resmon.node_id,
                            db.resmon.rid,
                            db.resmon.res_type,
                            db.resmon.res_status,
                            db.resmon.id.count(),
                            groupby=g,
                           )
        self.rs["services_resources"] = {}
        self.rs["nodes_services_resources_count"] = {}
        self.rs["nodes_services_resources"] = {}
        for row in rows:
            t = (row.resmon.node_id, row.resmon.svc_id, row.resmon.res_type)
            if t not in self.rs["nodes_services_resources"]:
                self.rs["nodes_services_resources"][t] = [row]
            else:
                self.rs["nodes_services_resources"][t] += [row]

            t = (row.resmon.node_id, row.resmon.svc_id)
            if t in self.rs["nodes_services_resources_count"]:
                self.rs["nodes_services_resources_count"][t] += 1
            else:
                self.rs["nodes_services_resources_count"][t] = 1

            t = (row.resmon.svc_id, row.resmon.res_type)
            if t not in self.rs["services_resources"]:
                self.rs["services_resources"][t] = [row]
            else:
                self.rs["services_resources"][t] += [row]


    def add_apps(self):
        for app in self.rs['apps']:
            _id = self.add_visnode("app", app)
            self.add_visnode_node(_id, "apps", label=app, mass=16)

    def add_envs(self):
        for env in self.rs['envs']:
            _id = self.add_visnode("env", env)
            self.add_visnode_node(_id, "envs", label=env, mass=16)

    def add_san(self):
        # hba_ids
        q = db.node_hba.node_id.belongs(self.node_ids)
        rows = db(q).select(cacheable=True)
        hba_ids = [r.hba_id for r in rows]

        # tgt_ids
        q = db.stor_zone.node_id.belongs(self.node_ids)
        rows = db(q).select(db.stor_zone.tgt_id)
        tgt_ids = [r.tgt_id for r in rows]

        # edge switchs
        q = db.switches.sw_rportname.belongs(hba_ids+tgt_ids)
        rows = db(q).select(db.switches.sw_name, groupby=db.switches.sw_name)
        edge_switches = [r.sw_name for r in rows]
        if len(edge_switches) == 0:
            return

        # switchs
        q = db.switches.id > 0
        #q = db.switches.sw_portname.belongs(hba_ids+tgt_ids)
        #q |= db.switches.sw_rportname.belongs(hba_ids+tgt_ids)
        #q |= db.switches.sw_porttype == "E-Port"
        rows = db(q).select(db.switches.sw_name, groupby=db.switches.sw_name)
        switches = [r.sw_name for r in rows]

        q = db.switches.sw_name.belongs(switches)
        ports = db(q).select(db.switches.sw_portname,
                            db.switches.sw_rportname,
                            db.switches.sw_portspeed,
                            db.switches.sw_name,
                            cacheable=True)
        portsw = {}
        rportsw = {}
        for i, row in enumerate(ports):
            visnode_id = self.get_visnode_id("sansw", row.sw_name)
            if visnode_id < 0:
                visnode_id = self.add_visnode("sansw", row.sw_name)
                self.add_visnode_node(visnode_id, "sansw", label=row.sw_name, mass=3)
            portsw[row.sw_portname] = (visnode_id, i)
            rportsw[row.sw_rportname] = (visnode_id, i)

        for row in ports:
            i1, idx = portsw.get(row.sw_portname, (-1, -1))
            i2, idx = portsw.get(row.sw_rportname, (-1, -1))
            if i1 < 0 or i2 < 0:
                continue
            self.add_edge(i1, i2, label=row.sw_portspeed, color="lightgrey", multi=True)

        # node -> sw
        q = db.node_hba.node_id.belongs(self.node_ids)
        rows = db(q).select(
            db.node_hba.hba_id,
            db.node_hba.hba_type,
            db.node_hba.node_id,
            cacheable=True,
        )
        for row in rows:
            i1 = self.get_visnode_id("node", row.node_id)
            i2, idx = rportsw.get(row.hba_id, (-1, -1))
            if i1 < 0 or i2 < 0:
                continue
            self.add_edge(i1, i2, label=row.hba_type+"/"+str(ports[idx].sw_portspeed), color="lightgrey", multi=True)

        # array -> sw
        q = db.stor_zone.node_id.belongs(self.node_ids)
        q &= db.stor_zone.tgt_id == db.stor_array_tgtid.array_tgtid
        q &= db.stor_array_tgtid.array_id == db.stor_array.id
        rows = db(q).select(db.stor_zone.tgt_id,
                            db.stor_array.array_name,
                            groupby=db.stor_zone.tgt_id,
                            cacheable=True)
        for row in rows:
            i1 = self.get_visnode_id("array", row.stor_array.array_name)
            i2, idx = rportsw.get(row.stor_zone.tgt_id, (-1, -1))
	    if i1 < 0 or i2 < 0:
                continue
            self.add_edge(i1, i2, label=str(ports[idx].sw_portspeed), color="lightgrey", multi=True)

        # purge unrelevant edge switches
        sw_ids = self.get_visnode_ids("sansw")
        node_vids = self.get_visnode_ids("node")
        array_ids = self.get_visnode_ids("array")
        all_ids = sw_ids | node_vids | array_ids
        rels = {}
        for i1, i2 in self.edges.keys():
            if i1 not in all_ids or i2 not in all_ids:
                continue
            if i1 not in rels:
                rels[i1] = set([])
            if i2 not in rels:
                rels[i2] = set([])
            rels[i1].add(i2)
            rels[i2].add(i1)
        purge_ids = []
        for i, l in rels.items():
            if i in sw_ids and len(l) < 2:
                purge_ids.append(i)

        # remove relations with purge_ids
        for i, l in rels.items():
            rels[i] = list(set(rels[i]) - set(purge_ids))
            if len(rels[i]) == 0:
                del(rels[i])

        # purge orphaned switches
        for i in sw_ids:
            if i not in rels:
                purge_ids.append(i)

        # also purge sw with no rels at all
        purge_ids = set(purge_ids) | (sw_ids - set(rels.keys()))
        self.delete_ids(purge_ids)

    def delete_ids(self, ids):
        for i in range(len(self.data["nodes"])-1, 0, -1):
            if self.data["nodes"][i]["id"] in ids:
                del(self.data["nodes"][i])
        for i in range(len(self.data["edges"])-1, 0, -1):
            if self.data["edges"][i]["to"] in ids or \
               self.data["edges"][i]["from"] in ids:
                del(self.data["edges"][i])

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
                self.add_visnode_node(_id, p, label=loc, mass=2+i, image=self.get_img(p, loc))
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
                    nodename_id = self.get_visnode_id("node", row.node_id)
                    self.add_edge(nodename_id, parent_id, color="lightgrey")
                    break

    def add_services_loc(self):
        if "nodes_services" not in self.rs:
            return
        for (node_id, svc_id), _row in self.rs["nodes_services"].items():
            row = self.rs['nodes'][node_id]
            for p, col in self.locs:
                parent_loc = row[col]
                if parent_loc is None:
                    continue
                parent_id = self.get_visnode_id(p, parent_loc)
                if parent_id > 0:
                    svcname_id = self.get_visnode_id("svc", svc_id)
                    self.add_edge(
                      svcname_id, parent_id,
                      #length=2,
                      color=self.status_color.get(_row.mon_availstatus, "grey"),
                      label=_row.mon_availstatus,
                    )
                    break

    def add_resources(self):
        for (svc_id, res_type), rows in self.rs['services_resources'].items():
            if res_type is None:
                continue
            svc = get_svc(svc_id)
            rid = "%s.%s" % (svc.svc_id, res_type)
            n = 0
            for row in rows:
                n += row._extra[db.resmon.id.count()]
            label = "%s (%d)" % (res_type, n)
            rid_id = self.add_visnode("resource", rid)
            if res_type in ("container.docker", "ip", "disk.scsireserv", "disk", "fs"):
                t = res_type
            else:
                t = res_type.split(".")[0]
            self.add_visnode_node(rid_id, t, label=label, mass=3)

    def add_disks(self):
        for (node_id, svc_id, arrayid), rows in self.rs['disks'].items():
            if "services" in self.display and not svc_id in self.svc_ids:
                continue
            disk_id = self.get_visnode_id("disk", "", data=rows)
            if disk_id < 0:
                label = self.fmt_disk_label(node_id, svc_id, arrayid, rows)
                disk_id = self.add_visnode("disk", label, data=rows)
                self.add_visnode_node(disk_id, "disks", label=label, mass=3)

    def add_nodes(self):
        for node_id in self.rs["nodes"]:
            self.add_node(node_id)

    def add_node(self, node_id):
        d = self.rs["nodes"].get(node_id, {})
        label = d.get("nodename", "") + "\n" + ', '.join((d.get("os_name", ""), d.get("model", "")))
        nodename_id = self.add_visnode("node", node_id)
        self.add_visnode_node(nodename_id, "node", label=label, mass=3)

    def add_edge(self, from_node, to_node, color="#555555", label="", multi=False):
        def format_label(l):
            if len(l) == 0:
                return ""
            _l = []
            for s in sorted(list(set(l))):
                i = l.count(s)
                _l.append("%(i)dx%(v)s" % dict(i=i, v=s))
            return ' + '.join(_l)

        sig = tuple(sorted([from_node, to_node]))
        if sig in self.edges:
            if not multi:
                return
            else:
                i = self.edges[sig]
                self.data["edges"][i]["_label"].append(label)
                self.data["edges"][i]["label"] = format_label(self.data["edges"][i]["_label"])
                return
        edge = {
         "from": from_node,
         "to": to_node,
         #"length": self.edge_len_base*length,
         "color": color,
         "font": {"color": color},
         "label": str(label),
         "width": 2,
         "_label": [label],
        }
        self.data["edges"].append(edge)
        self.edges[sig] = len(self.data["edges"])-1

    def add_services(self):
        for svc_id in self.svc_ids:
            self.add_service(svc_id)

    def add_service(self, svc_id):
        vnode_id = self.add_visnode("svc", svc_id)
        if vnode_id < 0:
            return
        if svc_id not in self.rs["services"]:
            return
        row = self.rs["services"][svc_id]
        self.add_visnode_node(vnode_id, "svc", label=get_svc(svc_id).svcname, mass=8, fontColor=self.status_color.get(row["svc_availstatus"], "grey"))

    def add_arrays(self):
        for (node_id, svc_id, arrayid), rows in self.rs["disks"].items():
            if arrayid in self.node_ids:
                continue
            if "nodes" in self.display and not node_id in self.node_ids:
                continue
            if "services" in self.display and svc_id != "" and not svc_id in self.svc_ids:
                continue
            visnode_id = self.add_visnode("array", arrayid)
            if visnode_id < 0:
                continue
            self.add_visnode_node(visnode_id, "array", label=arrayid, mass=4)

    def add_nodes_services_resources(self):
        for (node_id, svc_id, res_type), rows in self.rs["nodes_services_resources"].items():
            vnode_id = self.get_visnode_id("node", node_id)
            rid = "%s.%s" % (svc_id, res_type)
            res_type_id = self.get_visnode_id("resource", rid)
            n = 0
            for row in rows:
                n += row._extra[db.resmon.id.count()]
            for row in rows:
                self.add_edge(vnode_id, res_type_id,
                              color=self.status_color.get(row.resmon.res_status, "grey"),
                              label=n,
                             )

    def add_services_resources(self):
        for (svc_id, res_type), rows in self.rs["services_resources"].items():
            svcname_id = self.get_visnode_id("svc", svc_id)
            rid = "%s.%s" % (svc_id, res_type)
            res_type_id = self.get_visnode_id("resource", rid)
            for row in rows:
                self.add_edge(svcname_id, res_type_id,
                              color=self.status_color.get(row.resmon.res_status, "grey"),
                              label="",
                             )

    def add_nodes_apps(self):
        for (node_id, app) in self.rs["nodes_apps"]:
            nodename_id = self.get_visnode_id("node", node_id)
            app_id = self.get_visnode_id("app", app)
            self.add_edge(nodename_id, app_id,
                          color="lightgrey",
                         )

    def add_services_apps(self):
        for (svc_id, app) in self.rs["services_apps"]:
            svcname_id = self.get_visnode_id("svc", svc_id)
            app_id = self.get_visnode_id("app", app)
            self.add_edge(svcname_id, app_id,
                          color="lightgrey",
                         )

    def add_nodes_envs(self):
        for (node_id, env) in self.rs["nodes_envs"]:
            nodename_id = self.get_visnode_id("node", node_id)
            env_id = self.get_visnode_id("env", env)
            self.add_edge(nodename_id, env_id,
                          color="lightgrey",
                         )

    def add_services_envs(self):
        for (svc_id, env) in self.rs["services_envs"]:
            svcname_id = self.get_visnode_id("svc", svc_id)
            env_id = self.get_visnode_id("env", env)
            self.add_edge(svcname_id, env_id,
                          color="lightgrey",
                         )

    def add_nodes_services(self):
        for (node_id, svc_id), row in self.rs["nodes_services"].items():
            if "resources" in self.display and (node_id, svc_id) in self.rs["nodes_services_resources_count"]:
                continue
            vnode_id = self.get_visnode_id("node", node_id)
            vsvc_id = self.get_visnode_id("svc", svc_id)
            self.add_edge(vnode_id, vsvc_id,
                          #length=2,
                          color=self.status_color.get(row.mon_availstatus, "grey"),
                          label=row.mon_availstatus,
                         )

    def fmt_disk_label(self, node_id, svc_id, arrayid, rows):
        svc = get_svc(svc_id)
        label = "svc:%s\n" % svc.svcname
        if len(rows) > 3:
            total = 0
            for row in rows:
                total += row.svcdisks.disk_size
            label += "%d disks, total %s"%(len(rows), beautify_size_mb(total))
        else:
            for row in rows:
                label += row.svcdisks.disk_id+"\t"+beautify_size_mb(row.svcdisks.disk_size)+"\n"
        return label

    def add_services_disks(self):
        for (node_id, svc_id, arrayid), rows in self.rs["disks"].items():
            #if svcname == "":
            #    continue
            svcname_id = self.get_visnode_id("svc", svc_id)
            disk_id = self.get_visnode_id("disk", self.fmt_disk_label(node_id, svc_id, arrayid, rows), data=rows)
            self.add_edge(svcname_id, disk_id)

            if node_id == arrayid:
                nodename_id = self.get_visnode_id("node", node_id)
                disk_id = self.get_visnode_id("disk", self.fmt_disk_label(node_id, svc_id, arrayid, rows), data=rows)
                self.add_edge(nodename_id, disk_id)

    def add_nodes_disks(self):
        for (node_id, svc_id, arrayid), rows in self.rs["disks"].items():
            #if svcname != "" and "services" in self.display:
            #    continue
            nodename_id = self.get_visnode_id("node", node_id)
            disk_id = self.get_visnode_id("disk", self.fmt_disk_label(node_id, svc_id, arrayid, rows), data=rows)
            self.add_edge(nodename_id, disk_id)

    def add_arrays_disks(self):
        for (node_id, svc_id, arrayid), rows in self.rs["disks"].items():
            if arrayid in self.node_ids:
                continue
            if "services" in self.display and not svc_id in self.svc_ids:
                continue
            array_id = self.get_visnode_id("array", arrayid)
            disk_id = self.get_visnode_id("disk", self.fmt_disk_label(node_id, svc_id, arrayid, rows), data=rows)
            self.add_edge(array_id, disk_id)

@auth.requires_login()
@service.json
def json_topo_data():
    svc_ids = set()
    node_ids = set()

    app_ids = request.vars.get("app_ids[]", [])
    if type(app_ids) != list:
        app_ids = [app_ids]
    if len(app_ids) > 0:
        q = db.apps.id.belongs(app_ids)
        q &= db.services.svc_app == db.apps.app
        q = q_filter(q, app_field=db.apps.app)
        svc_ids |= set([r.svc_id for r in db(q).select(db.services.svc_id)])

        q = db.apps.id.belongs(app_ids)
        q &= db.nodes.app == db.apps.app
        q = q_filter(q, app_field=db.apps.app)
        node_ids |= set([r.node_id for r in db(q).select(db.nodes.node_id)])

    _svc_ids = request.vars.get("svc_ids[]", [])
    if type(_svc_ids) != list:
        svc_ids |= set([_svc_ids])
    if len(_svc_ids) > 0:
        q = db.services.svc_id.belongs(svc_ids)
        q = q_filter(q, app_field=db.services.svc_app)
        svc_ids |= set([r.svc_id for r in db(q).select(db.services.svc_id)])

    _node_ids = request.vars.get("node_ids[]", [])
    if type(_node_ids) != list:
        node_ids |= set([_node_ids])
    if len(node_ids) > 0:
        q = db.nodes.node_id.belongs(node_ids)
        q = q_filter(q, app_field=db.nodes.app)
        node_ids = [r.node_id for r in db(q).select(db.nodes.node_id)]

    svc_ids = list(svc_ids)
    node_ids = list(node_ids)

    display = request._vars.get("display[]", [])
    return viz(svc_ids, node_ids, display).get_data()

@auth.requires_login()
def topo():
    svc_ids = request.vars.get("svc_ids", "").split(",")
    node_ids = request.vars.get("node_ids", "").split(",")
    display = request.vars.get("display", "").split(",")
    s = """topology("topo", %(options)s)""" % dict(
         options=str({
           "svc_ids": svc_ids,
           "node_ids": node_ids,
           "display": display,
         })
    )
    d = DIV(
      SCRIPT(s),
      _id="topo",
    )
    return dict(table=d)

@auth.requires_login()
def startup():
    svc_ids = request.vars.get("svc_ids", "").split(",")
    display = request.vars.get("display", "").split(",")
    show_disabled = request.vars.get("show_disabled", "false")

    s = """startup("startup", %(options)s)"""%dict(
         options=str({
          "svc_ids": svc_ids,
          "display": display,
          "show_disabled": show_disabled,
         })
       )
    d = DIV(
      SCRIPT(s),
      _id="startup",
    )
    return dict(table=d)

@auth.requires_login()
@service.json
def json_startup_data():
    svc_ids = request.vars.get("svc_ids[]", [])
    if type(svc_ids) != list:
        svc_ids = [svc_ids]
    if len(svc_ids) > 0:
        q = db.services.svc_id.belongs(svc_ids)
        q = q_filter(q, app_field=db.services.svc_app)
        svc_ids = [r.svc_id for r in db(q).select(db.services.svc_id)]

    node_ids = request.vars.get("node_ids[]", [])
    if type(node_ids) != list:
        node_ids = [node_ids]
    if len(node_ids) > 0:
        q = db.nodes.node_id.belongs(node_ids)
        q = q_filter(q, app_field=db.nodes.app)
        node_ids = [r.node_id for r in db(q).select(db.nodes.node_id)]

    if len(node_ids) == 0:
        q = db.svcmon.svc_id.belongs(svc_ids)
        row = db(q).select(db.svcmon.node_id).first()
        if row is not None:
            node_ids = [row.node_id]

    show_disabled = request.vars.get("show_disabled", False)
    if show_disabled == "false":
        show_disabled = False
    else:
        show_disabled = True

    data = {
      "nodes": [],
      "edges": [],
    }

    if len(svc_ids) == 0:
        return data

    svc_id = svc_ids[0]
    q = db.services.svc_id.belongs(svc_ids)
    config = db(q).select(db.services.svc_config).first().svc_config
    if config is None:
        return data

    q = db.resmon.svc_id == svc_id
    q &= db.resmon.node_id.belongs(node_ids)
    q &= db.resmon.node_id == db.nodes.node_id
    rows = db(q).select()
    resmon = {}
    for row in rows:
        if row.nodes.id not in resmon:
            resmon[row.nodes.id] = {}
        resmon[row.nodes.id][row.resmon.rid] = row
        if row.resmon.vmname:
            if row.resmon.vmname not in resmon:
                resmon[row.resmon.vmname] = {}
            resmon[row.resmon.vmname][row.resmon.rid] = row

    import os
    import StringIO
    import ConfigParser
    config = config.replace("\\n", "\n")
    buf = StringIO.StringIO(config)
    config = ConfigParser.RawConfigParser()
    config.readfp(buf)

    vis_node_ids = []
    edge_ids = []
    node_tail = 0

    imgs = {
      (None, None): URL(r=request,c='static',f='images/action48.png'),
      ("ip.container", None): URL(r=request,c='static',f='images/net48.png'),
      ("ip", None): URL(r=request,c='static',f='images/net48.png'),
      ("fs", None): URL(r=request,c='static',f='images/fs.png'),
      ("disk", None): URL(r=request,c='static',f='images/disk48.png'),
      ("container", "docker"): URL(r=request,c='static',f='images/docker48.png'),
    }
    def get_img(family, t):
        i = imgs.get((family, t))
        if i:
            return i
        i = imgs.get((family, None))
        if i:
            return i
        return imgs.get((None, None))

    def get_label(node_id, nodename, section, family, t="", monitor=False, optional=False):
        s = section

        if get_disabled(section, nodename):
            s += " (disabled)"
        if monitor:
            s += " (monitored)"
        if optional:
            s += " (optional)"

        try:
            tags = get_scoped(section, "tags", nodename).split()
        except ConfigParser.NoOptionError:
            tags = []
        if "noaction" in tags:
            s += " (no action)"

        s += "\n"
        if node_id in resmon and section in resmon[node_id]:
            s += resmon[node_id][section].resmon.res_desc
        return s

    def get_disabled(s, nodename):
        try:
            return getboolean_scoped(s, "disable", nodename)
        except ConfigParser.NoOptionError:
            pass
        if config.has_option(s, "disable_on"):
            disable_on = config.get(s, "disable_on").split()
            l = []
            if "nodes" in disable_on: l += nodes
            if "drpnodes" in disable_on: l += drpnodes
            if "encapnodes" in disable_on: l += encapnodes
            if nodename in l:
                return True
        return False

    def _get_scoped(s, o, nodename, fn):
        _o = o+"@"+nodename
        if config.has_option(s, _o):
            return fn(s, _o)
        if nodename in nodes:
            _o = o+"@nodes"
        elif nodename in drpnodes:
            _o = o+"@drpnodes"
        elif nodename in encapnodes:
            _o = o+"@encapnodes"
        else:
            _o = o
        if config.has_option(s, _o):
            return fn(s, _o)
        return fn(s, o)

    def get_scoped(s, o, nodename):
        return _get_scoped(s, o, nodename, config.get)

    def getboolean_scoped(s, o, nodename):
        return _get_scoped(s, o, nodename, config.getboolean)

    def container_rid(nodename, hv):
        nodename = nodename.split(".")[0]
        for section in config.sections():
            if section.startswith("container#"):
                try:
                    name = get_scoped(section, "name", hv).split(".")[0]
                    if name == nodename:
                        return section
                except ConfigParser.NoOptionError:
                    pass

    def trigger_add_node(node_id, nodename, s, t, node_tail):
        try:
            script = get_scoped(s, t, nodename)
            trigger_id = s + "_" + t
            if (node_id, trigger_id) not in vis_node_ids:
                triggers.append(trigger_id)
                label = s + " " + t + "\n" + script
                d = {
                  "mass": 3,
                  "id": node_tail,
                  "label": label,
                  "font": {"color": "grey"},
                  "group": "trigger"
                }
                vis_node_ids.append((node_id, trigger_id))
                node_tail += 1
                data["nodes"].append(d)
        except ConfigParser.NoOptionError:
            pass
        return node_tail

    def add_edge(from_node, to_node, node_id, color="grey"):
        _to = vis_node_ids[to_node][1]
        _from = vis_node_ids[from_node][1]
        if str(_to) + "_pre_start" in triggers and \
           _from + "_post_start" in triggers:
            from_trigger_name = _from + "_post_start"
            from_trigger_node = vis_node_ids.index((node_id, from_trigger_name))
            to_trigger_name = _to + "_pre_start"
            to_trigger_node = vis_node_ids.index((node_id, to_trigger_name))
            _add_edge(from_node, from_trigger_node, color=color)
            _add_edge(from_trigger_node, to_trigger_node)
            _add_edge(to_trigger_node, to_node)
            return _to
        if str(_to) + "_pre_start" in triggers:
            name = _to + "_pre_start"
            trigger_node = vis_node_ids.index((node_id, name))
            _add_edge(from_node, trigger_node, color=color)
            _add_edge(trigger_node, to_node)
            return _to
        if str(_from) + "_post_start" in triggers:
            name = _from + "_post_start"
            trigger_node = vis_node_ids.index((node_id, name))
            _add_edge(from_node, trigger_node, color=color)
            _add_edge(trigger_node, to_node)
            return _to
        _add_edge(from_node, to_node, color=color)
        return _to

    def _add_edge(from_node, to_node, color="grey"):
        label = ""
        edge = {
         "from": from_node,
         "to": to_node,
         "length": 100,
         "color": color,
         "font": {"color": color},
         "label": str(label),
         "width": 2,
         "style": "arrow",
         "_label": [label],
        }
        if (from_node, to_node) not in edge_ids:
            data["edges"].append(edge)
            edge_ids.append((from_node, to_node))

    def do_resource_edges(node_id, nodename, family, rs, s, hv, prev, i, last, _prev=None, subsets={}):
        subset = "subset#"+family+":"+rs
        color = "grey"
        try:
            tags = get_scoped(s, "tags", nodename).split()
        except ConfigParser.NoOptionError:
            tags = []
        if hv is None and "encap" in tags:
            return prev, _prev
        if family in ("ip", "fs", "disk") and "zone" in tags:
            return prev, _prev
        if subset in subsets:
            subset_data = subsets[subset]
            if "done" not in subset_data:
                # prev to new subset extra edge
                subsets[subset]["done"] = True
                from_node = vis_node_ids.index((node_id, prev))
                to_node = vis_node_ids.index((node_id, subset))
                add_edge(from_node, to_node, node_id)
                _prev = subset
                prev = subset
            if subset_data["parallel"]:
                # //-subset to resource (star-like)
                from_node = vis_node_ids.index((node_id, subset))
                try:
                    to_node = vis_node_ids.index((node_id, s))
                    add_edge(from_node, to_node, node_id)
                except ValueError:
                    pass
            else:
                if i == 0:
                    # highlight edge to first resource of a serial subset
                    color = "black"
                if i == last:
                    # last resource to serial-subset extra edge
                    from_node = vis_node_ids.index((node_id, s))
                    to_node = vis_node_ids.index((node_id, subset))
                    add_edge(from_node, to_node, node_id)
                from_node = vis_node_ids.index((node_id, _prev))
                to_node = vis_node_ids.index((node_id, s))
                _prev = add_edge(from_node, to_node, node_id, color=color)
        else:
            from_node = vis_node_ids.index((node_id, prev))
            try:
                to_node = vis_node_ids.index((node_id, s))
                prev = add_edge(from_node, to_node, node_id)
            except ValueError:
                pass
        return prev, _prev


    # header parser
    triggers = []
    nodes = []
    if config.has_option("DEFAULT", "nodes"):
        nodes = config.get("DEFAULT", "nodes").split()
    drpnodes = []
    if config.has_option("DEFAULT", "drpnodes"):
        drpnodes = config.get("DEFAULT", "drpnodes").split()
    if config.has_option("DEFAULT", "drpnode"):
        drpnode = config.get("DEFAULT", "drpnode").split()
        drpnodes = list(set(drpnode) | set(drpnodes))
    encapnodes = []
    if config.has_option("DEFAULT", "encapnodes"):
        encapnodes = config.get("DEFAULT", "encapnodes").split()

    # add root node
    d = {
      "mass": 3,
      "id": node_tail,
      "label": get_svc(svc_id).svcname,
      "group": "svc"
    }
    node_tail += 1
    vis_node_ids.append(svc_id)
    data["nodes"].append(d)

    status_color = {
      "up": "darkgreen",
      "stdby up": "darkgreen",
      "down": "darkred",
      "stdby down": "darkred",
      "warn": "orange",
    }

    levels = [
      "hb",
      "stonith",
      "ip",
      "disk",
      "fs",
      "share",
      "container",
      "ip.container",
      "app",
    ]

    disk_types = [
      "vg",
      "drbd",
      "pool",
      "zpool",
      "loop",
      "raw",
      "rados",
      "lock",
      "vg",
      "gandi",
    ]

    def do_node(node_id, vis_node_ids, node_tail, hv=None, show_disabled=False):
        sections = {}
        nodename = db(db.nodes.node_id==node_id).select().first().nodename
        for family in levels:
          sections[family] = {}
          sections[family][family] = []

        data = {
          "edges": [],
          "nodes": [],
        }
        subsets = {
        }

        if (node_id, node_id) not in vis_node_ids:
            d = {
              "mass": 3,
              "id": node_tail,
              "label": get_nodename(node_id),
              "group": "node"
            }
            node_tail += 1
            vis_node_ids.append((node_id, node_id))
            data["nodes"].append(d)

        if hv:
            rid = container_rid(nodename, hv)
            from_node = vis_node_ids.index((hv, rid))
        else:
            from_node = vis_node_ids.index(svc_id)
        to_node = vis_node_ids.index((node_id, node_id))
        label = ""
        edge = {
          "from": from_node,
          "to": to_node,
          "length": 100,
          "color": "grey",
          "label": str(label),
          "width": 2,
          "style": "arrow",
          "_label": [label],
        }
        if (from_node, to_node) not in edge_ids:
            data["edges"].append(edge)
            edge_ids.append((from_node, to_node))

        for s in config.sections():
            if "sync#" in s or s == "env":
                continue

            try:
                tags = get_scoped(s, "tags", nodename).split()
            except ConfigParser.NoOptionError:
                tags = []

            if hv and not "encap" in tags:
                continue
            elif hv is None and "encap" in tags:
                continue

            try:
                t = get_scoped(s, "type", nodename)
            except ConfigParser.NoOptionError:
                t = None

            if s.startswith("subset#") and ":" in s:
                # subset
                try:
                    parallel = getboolean_scoped(s, "parallel", nodename)
                except ConfigParser.NoOptionError:
                    parallel = False
                family, name = s.replace("subset#", "").split(":")
                subsets[s] = {
                  "parallel": parallel,
                  "family": family,
                  "name": family,
                }
                d = {
                  "mass": 3,
                  "id": node_tail,
                  "label": s,
                  "group": "subset"
                }
                vis_node_ids.append((node_id, s))
                node_tail += 1
                data["nodes"].append(d)
                continue

            family = s.split("#")[0]

            if family == "task":
                continue

            if family in disk_types:
                family = "disk"

            if t and family == "ip" and t == "docker":
                family = "ip.container"

            try:
                subset = get_scoped(s, "subset", nodename)
                if subset not in sections[family]:
                    sections[family][subset] = []
                sections[family][subset].append(s)
            except ConfigParser.NoOptionError:
                sections[family][family].append(s)

            disabled = get_disabled(s, nodename)
            if disabled and not show_disabled:
                continue
            try:
                res_status = resmon[node_id][s].resmon.res_status
                color = status_color.get(res_status, "grey")
            except KeyError:
                color = "grey"
            try:
                monitor = getboolean_scoped(s, "monitor", nodename)
            except ConfigParser.NoOptionError:
                monitor = False
            try:
                optional = getboolean_scoped(s, "optional", nodename)
            except ConfigParser.NoOptionError:
                optional = False
            """
            if monitor:
                fcolor = "red"
            if optional:
                fcolor = "blue"
            else:
                fcolor = "transparent"
            """
            label = get_label(node_id, nodename, s, family, t, monitor=monitor, optional=optional)
            if family in ("ip", "disk.scsireserv", "disk", "fs"):
                g = family
            elif family+'.'+str(t) in ("container.docker"):
                g = family+'.'+t
            else:
                g = family.split(".")[0]

            if (node_id, s) not in vis_node_ids:
                d = {
                  "mass": 3,
                  "id": node_tail,
                  "label": label,
                  "group": g,
                  "font": {"color": color},
                }
                if disabled:
                    d["icon"] = {"color": "lightgray"}
                vis_node_ids.append((node_id, s))
                node_tail += 1
                data["nodes"].append(d)

            node_tail = trigger_add_node(node_id, nodename, s, "pre_start", node_tail)
            node_tail = trigger_add_node(node_id, nodename, s, "post_start", node_tail)

        prev = node_id
        _prev = None
        for family in levels:
            for rs in sorted(sections[family].keys()):
                rset_resources = sections[family][rs]
                last = len(rset_resources) - 1

                # sort resources
                if rs.startswith("fs#"):
                    # fs resourceset are sorted by mnt deepness
                    fs_mnt = {}
                    for s in rset_resources:
                        try:
                            mnt = get_scoped(s, "mnt", nodename)
                            fs_mnt[mnt] = s
                        except ConfigParser.NoOptionError:
                            pass
                    rset_resources = []
                    for mnt in sorted(fs_mnt.keys()):
                        rset_resources.append(fs_mnt[mnt])
                else:
                    # other resourceset are sorted by rid (alphnum)
                    rset_resources.sort()

                for i, s in enumerate(rset_resources):
                    prev, _prev = do_resource_edges(node_id, nodename, family, rs, s, hv, prev, i, last, _prev=_prev, subsets=subsets)

        if hv is None:
            for container in encapnodes:
                q = db.nodes.nodename == container
                q &= db.nodes.app.belongs(node_responsibles_apps(node_id))
                container_node = db(q).select().first()
                if container_node is None:
                    continue
                _nodes, _edges, vis_node_ids, node_tail = do_node(container_node.node_id, vis_node_ids, node_tail, hv=node_id, show_disabled=show_disabled)
                data["nodes"] += _nodes
                data["edges"] += _edges

        return data["nodes"], data["edges"], vis_node_ids, node_tail

    for node_id in node_ids:
        nodes, edges, vis_node_ids, node_tail = do_node(node_id, vis_node_ids, node_tail, show_disabled=show_disabled)
        data["nodes"] += nodes
        data["edges"] += edges

    return data


