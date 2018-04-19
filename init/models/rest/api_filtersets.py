
#
class rest_get_filters(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List filters.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/filters?query=f_table=nodes"
        ]
        q = db.gen_filters.id > 0
        rest_get_table_handler.__init__(
          self,
          path="/filters",
          tables=["gen_filters"],
          q=q,
          desc=desc,
          examples=examples,
        )

class rest_get_filter(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display a filter properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/filters/10"
        ]
        rest_get_line_handler.__init__(
          self,
          path="/filters/<id>",
          tables=["gen_filters"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.gen_filters.id == id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_filtersets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List filtersets.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/filtersets?query=fset_name contains aix"
        ]
        q = db.gen_filtersets.id > 0
        rest_get_table_handler.__init__(
          self,
          path="/filtersets",
          tables=["gen_filtersets"],
          q=q,
          desc=desc,
          examples=examples,
        )

class rest_get_filterset(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display a filterset properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/filtersets/10"
        ]
        rest_get_line_handler.__init__(
          self,
          path="/filtersets/<id>",
          tables=["gen_filtersets"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        try:
            id = int(id)
            q = db.gen_filtersets.id == id
        except:
            q = db.gen_filtersets.fset_name == id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_filterset_usage(rest_get_handler):
    def __init__(self):
        desc = [
          "Display a filterset usage.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/filtersets/10/usage"
        ]
        rest_get_handler.__init__(
          self,
          path="/filtersets/<id>/usage",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        try:
            id = int(id)
            q = db.gen_filtersets.id == id
        except:
            q = db.gen_filtersets.fset_name == id
        fset = db(q).select().first()
        if fset is None:
            raise HTTP(404, "fset %s does not exist" % str(id))
        data = {}

        #
        q = db.gen_filtersets_filters.encap_fset_id == fset.id
        q &= db.gen_filtersets.id == db.gen_filtersets_filters.fset_id
        o = db.gen_filtersets.fset_name
        i = db.gen_filtersets.id
        rows = db(q).select(o, i, orderby=o, groupby=o, cacheable=False)
        data["filtersets"] = [ {"fset_name": r.fset_name, "id": r.id} for r in rows ]

        #
        q = db.comp_rulesets_filtersets.fset_id == fset.id
        q &= db.comp_rulesets_filtersets.ruleset_id == db.comp_rulesets.id
        o = db.comp_rulesets.ruleset_name
        i = db.comp_rulesets.id
        rows = db(q).select(o, i, orderby=o, cacheable=False)
        data["rulesets"] = [ {"ruleset_name": r.ruleset_name, "id": r.id} for r in rows ]

        #
        q = db.gen_filterset_check_threshold.fset_id == fset.id
        rows = db(q).select(cacheable=False)
        data["thresholds"] = [ "%(ti)s:%(low)s-%(high)s" % dict(
                 ti='.'.join((r.chk_type, r.chk_instance)),
                 low=str(r.chk_low),
                 high=str(r.chk_high)) for r in rows ]

        return dict(data=data)

class rest_get_filterset_filtersets(rest_get_table_handler):
    def __init__(self):
        desc = [
          "Display a filterset child filtersets.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/filtersets/10/filtersets"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/filtersets/<id>/filtersets",
          tables=["gen_filtersets"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        id = lib_filterset_id(id)
        if id is None:
            return dict(error="filterset not found")
        q = db.gen_filtersets_filters.fset_id == id
        q &= db.gen_filtersets.id == db.gen_filtersets_filters.encap_fset_id
        self.set_q(q)
        return self.prepare_data(**vars)

class rest_get_filterset_filters(rest_get_table_handler):
    def __init__(self):
        desc = [
          "Display a filterset child filters.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/filtersets/10/filters"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/filtersets/<id>/filters",
          tables=["gen_filters", "gen_filtersets_filters"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        id = lib_filterset_id(id)
        if id is None:
            return dict(error="filterset not found")
        q = db.gen_filtersets_filters.fset_id == id
        q &= db.gen_filtersets_filters.f_id == db.gen_filters.id
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_post_filtersets(rest_post_handler):
    def __init__(self):
        desc = [
          "Create a filterset.",
          "The user must be in the CompManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the filtersets table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -d fset_name=\"my fset\" -d fset_stats=false https://%(collector)s/init/rest/api/filtersets",
        ]
        rest_post_handler.__init__(
          self,
          path="/filtersets",
          tables=["gen_filtersets"],
          props_blacklist=["fset_author", "fset_updated", "id"],
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        _vars = {}
        _vars.update(vars)
        fset_id = None
        if "id" in vars:
            fset_id = lib_filterset_id(_vars["id"])
            del _vars["id"]
        if "fset_name" in vars:
            fset_id = lib_filterset_id(_vars["fset_name"])
            del _vars["fset_name"]
        if fset_id is not None:
            return rest_post_filterset().handler(fset_id, **_vars)
        try:
            obj_id = create_filterset(**vars)
        except CompInfo as e:
            return dict(info=str(e))
        return rest_get_filterset().handler(obj_id)


#
class rest_post_filterset(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify a filterset properties.",
          "The user must be in the CompManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the groups table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -d fset_stats=false https://%(collector)s/init/rest/api/filtersets/10",
        ]
        rest_post_handler.__init__(
          self,
          path="/filtersets/<id>",
          tables=["gen_filtersets"],
          desc=desc,
          examples=examples
        )

    def handler(self, id, **vars):
        check_privilege("CompManager")
        try:
            id = int(id)
            q = db.gen_filtersets.id == id
        except:
            q = db.gen_filtersets.fset_name == id
        row = db(q).select().first()
        if row is None:
            return dict(error="filterset %s not found" % str(id))
        if "id" in vars.keys():
            del(vars["id"])
        if len(vars) == 0:
            ret = rest_get_filterset().handler(row.id)
            ret["info"] = "no changes"
            return ret
        db(q).update(**vars)
        l = []
        for key in vars:
            l.append("%s: %s => %s" % (str(key), str(row[key]), str(vars[key])))
        _log('filterset.change',
             'change filterset %(data)s',
             dict(data=beautify_change(row, vars)),
            )
        ws_send('gen_filtersets_change', {'id': row.id})
        return rest_get_filterset().handler(row.id)

#
class rest_delete_filterset(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a filterset.",
          "The user must be in the CompManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the filtersets table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/filtersets/10",
        ]
        rest_delete_handler.__init__(
          self,
          path="/filtersets/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, fset_id, **vars):
        fset_id = lib_filterset_id(fset_id)
        if fset_id is None:
            return dict(error="filterset not found")
        try:
            delete_filterset(fset_id, **vars)
        except CompInfo as e:
            return dict(info=str(e))

#
class rest_delete_filtersets(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete filtersets.",
          "The user must be in the CompManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the filtersets table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/filtersets",
        ]
        rest_delete_handler.__init__(
          self,
          path="/filtersets",
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        if "id" not in vars:
            raise HTTP(400, "The 'id' key is mandatory")
        fset_id = vars["id"]
        del(vars["id"])
        return rest_delete_filterset().handler(fset_id, **vars)

#
class rest_delete_filterset_filterset(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach a filterset from a filterset",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/filtersets/10/filtersets/151",
        ]
        rest_delete_handler.__init__(
          self,
          path="/filtersets/<id>/filtersets/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, parent_fset_id, child_fset_id, **vars):
        parent_fset_id = lib_filterset_id(parent_fset_id)
        child_fset_id = lib_filterset_id(child_fset_id)
        if parent_fset_id is None:
            return dict(error="parent filterset not found")
        if child_fset_id is None:
            return dict(error="child filterset not found")
        try:
            detach_filterset_from_filterset(child_fset_id, parent_fset_id)
        except CompError as e:
            return dict(error=str(e))
        except CompInfo as e:
            return dict(info=str(e))

#
class rest_post_filterset_filterset(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach a filterset to a filterset",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/filtersets/10/filtersets/151",
        ]
        rest_post_handler.__init__(
          self,
          path="/filtersets/<id>/filtersets/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, parent_fset_id, child_fset_id, **vars):
        parent_fset_id = lib_filterset_id(parent_fset_id)
        child_fset_id = lib_filterset_id(child_fset_id)
        if parent_fset_id is None:
            return dict(error="parent filterset not found")
        if child_fset_id is None:
            return dict(error="child filterset not found")
        try:
            attach_filterset_to_filterset(child_fset_id, parent_fset_id, **vars)
        except CompError as e:
            return dict(error=str(e))
        except CompInfo as e:
            return dict(info=str(e))

#
class rest_delete_filtersets_filters(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach filters from filtersets",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/filtersets_filters",
        ]
        rest_delete_handler.__init__(
          self,
          path="/filtersets_filters",
          tables=["gen_filtersets_filters"],
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        if not "fset_id" in vars:
            raise HTTP(400, "The 'fset_id' key is mandatory")
        if not "f_id" in vars:
            raise HTTP(400, "The 'f_id' key is mandatory")
        fset_id = vars["fset_id"]
        del(vars["fset_id"])
        f_id = vars["f_id"]
        del(vars["f_id"])
        return rest_delete_filterset_filter().handler(fset_id, f_id, **vars)

#
class rest_post_filtersets_filters(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach filters to filtersets",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/filtersets_filters",
        ]
        rest_post_handler.__init__(
          self,
          path="/filtersets_filters",
          tables=["gen_filtersets_filters"],
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        if not "fset_id" in vars:
            raise HTTP(400, "The 'fset_id' key is mandatory")
        if not "f_id" in vars:
            raise HTTP(400, "The 'f_id' key is mandatory")
        fset_id = vars["fset_id"]
        del(vars["fset_id"])
        f_id = vars["f_id"]
        del(vars["f_id"])
        return rest_post_filterset_filter().handler(fset_id, f_id, **vars)

#
class rest_delete_filtersets_filtersets(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach filtersets from filtersets",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/filtersets_filtersets",
        ]
        rest_delete_handler.__init__(
          self,
          path="/filtersets_filtersets",
          tables=["gen_filtersets_filters"],
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        if not "parent_fset_id" in vars:
            raise HTTP(400, "The 'parent_fset_id' key is mandatory")
        if not "child_fset_id" in vars:
            raise HTTP(400, "The 'child_fset_id' key is mandatory")
        parent_fset_id = vars["parent_fset_id"]
        del(vars["parent_fset_id"])
        child_fset_id = vars["child_fset_id"]
        del(vars["child_fset_id"])
        return rest_delete_filterset_filterset().handler(parent_fset_id, child_fset_id, **vars)

#
class rest_post_filtersets_filtersets(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach filtersets to filtersets",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/filtersets_filtersets",
        ]
        rest_post_handler.__init__(
          self,
          path="/filtersets_filtersets",
          tables=["gen_filtersets_filters"],
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        if not "parent_fset_id" in vars:
            raise HTTP(400, "The 'parent_fset_id' key is mandatory")
        if not "child_fset_id" in vars:
            raise HTTP(400, "The 'child_fset_id' key is mandatory")
        parent_fset_id = vars["parent_fset_id"]
        del(vars["parent_fset_id"])
        child_fset_id = vars["child_fset_id"]
        del(vars["child_fset_id"])
        return rest_post_filterset_filterset().handler(parent_fset_id, child_fset_id, **vars)

#
class rest_post_filterset_filter(rest_post_handler):
    def __init__(self):
        desc = [
          "Attach a filter to a filterset",
          "Expressions are evaluated as (((1=1 <f_log_op1> expr1) <f_log_op2> expr2) <f_log_op3> expr3)",
        ]
        examples = [
          "# curl -u %(email)s -o- -X POST https://%(collector)s/init/rest/api/filtersets/10/filters/151",
        ]
        data = """
---
| **f_log_op** | The logical operator (AND, OR, AND NOT, OR NOT) to set between this filter and its predecessor |
| **f_order**  | An integer used to sort the filters before formatting the query                                |
---
"""
        rest_post_handler.__init__(
          self,
          path="/filtersets/<id>/filters/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, fset_id, f_id, **vars):
        fset_id = lib_filterset_id(fset_id)
        f_id = lib_filter_id(f_id)
        if fset_id is None:
            return dict(error="filterset not found")
        if f_id is None:
            return dict(error="filter not found")
        try:
            attach_filter_to_filterset(f_id, fset_id, **vars)
        except CompError as e:
            return dict(error=str(e))
        except CompInfo as e:
            return dict(info=str(e))

#
class rest_delete_filterset_filter(rest_delete_handler):
    def __init__(self):
        desc = [
          "Detach a filter from a filterset",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/filtersets/10/filters/151",
        ]
        rest_delete_handler.__init__(
          self,
          path="/filtersets/<id>/filters/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, fset_id, f_id):
        fset_id = lib_filterset_id(fset_id)
        f_id = lib_filter_id(f_id)
        if fset_id is None:
            return dict(error="filterset not found")
        if f_id is None:
            return dict(error="filter not found")
        try:
            detach_filter_from_filterset(f_id, fset_id)
        except CompError as e:
            return dict(error=str(e))
        except CompInfo as e:
            return dict(info=str(e))

#
class rest_get_filterset_export(rest_get_handler):
    def __init__(self):
        desc = [
          "Export the filterset in a JSON format compatible with the import handler.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/filtersets/2/export"
        ]

        rest_get_handler.__init__(
          self,
          path="/filtersets/<id>/export",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        id = lib_filterset_id(id)
        if id is None:
            return dict(error="filterset not found")
        return _export_filtersets([id])

#
class rest_post_filters(rest_post_handler):
    def __init__(self):
        desc = [
          "Create a filter.",
          "The user must be in the CompManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the filtersets table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -d f_table=nodes -d f_field=nodename -d f_op=like -d f_value=\"clem%%\"  https://%(collector)s/init/rest/api/filters",
        ]
        rest_post_handler.__init__(
          self,
          path="/filters",
          tables=["gen_filters"],
          props_blacklist=["f_author", "f_updated", "f_cksum", "id"],
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        try:
            obj_id = create_filter(**vars)
        except CompInfo as e:
            return dict(info=str(e))
        return rest_get_filter().handler(obj_id)


#
class rest_delete_filters(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete filters.",
          "Also delete all filters attachments to filtersets (warning: verify which filtersets embed this filter before deletion).",
          "The user must be in the CompManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the filtersets table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/filters",
        ]
        rest_delete_handler.__init__(
          self,
          path="/filters",
          desc=desc,
          examples=examples
        )

    def handler(self, **vars):
        if not "id" in vars:
            raise HTTP(400, "The 'id' key is mandatory")
        id = vars["id"]
        del(vars["id"])
        return rest_delete_filter().handler(id, **vars)

#
class rest_delete_filter(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a filter.",
          "Also delete all filter attachments to filtersets (warning: verify which filtersets embed this filter before deletion).",
          "The user must be in the CompManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the filtersets table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/filters/10",
        ]
        rest_delete_handler.__init__(
          self,
          path="/filters/<id>",
          desc=desc,
          examples=examples
        )

    def handler(self, id, **vars):
        id = lib_filter_id(id)
        if id is None:
            return dict(error="filter not found")
        try:
            delete_filter(id, **vars)
        except CompInfo as e:
            return dict(info=str(e))

#
class rest_post_filter(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify a filter properties.",
          "The user must be in the CompManager privilege group.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the groups table.",
        ]
        examples = [
          "# curl -u %(email)s -o- -d f_value=\"clem%%\" https://%(collector)s/init/rest/api/filters/10",
        ]
        rest_post_handler.__init__(
          self,
          path="/filters/<id>",
          tables=["gen_filters"],
          desc=desc,
          examples=examples
        )

    def handler(self, id, **vars):
        check_privilege("CompManager")
        id = lib_filter_id(id)
        q = db.gen_filters.id == id
        row = db(q).select().first()
        if row is None:
            return dict(error="filter %s not found" % str(id))
        if "id" in vars.keys():
            del(vars["id"])
        vars["f_updated"] = datetime.datetime.now()
        vars["f_author"] = user_name()
        db(q).update(**vars)
        l = []
        for key in vars:
            l.append("%s: %s => %s" % (str(key), str(row[key]), str(vars[key])))
        _log('filter.change',
             'change filter %(data)s',
             dict(data=', '.join(l)),
            )
        ws_send('gen_filters_change')
        return rest_get_filter().handler(row.id)

#
class rest_get_filterset_nodes(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List nodes matching a filterset.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/filtersets/10/nodes"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/filtersets/<id>/nodes",
          tables=["nodes"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        id = lib_filterset_id(id)
        if id is None:
            return dict(error="filterset not found")
        q = q_filter(app_field=db.nodes.app)
        q = apply_filters_id(q, node_field=db.nodes.node_id, fset_id=id)
        self.set_q(q)
        return self.prepare_data(**vars)

#
class rest_get_filterset_services(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List services matching a filterset.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/filtersets/10/services"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/filtersets/<id>/services",
          tables=["services"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        id = lib_filterset_id(id)
        if id is None:
            return dict(error="filterset not found")
        q = q_filter(app_field=db.services.svc_app)
        q = apply_filters_id(q, svc_field=db.services.svc_id, fset_id=id)
        self.set_q(q)
        return self.prepare_data(**vars)


