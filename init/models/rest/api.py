import re
import pydal
from urllib import unquote

def convert_bool(v):
    if v in ("True", "true", True, "y", "Y", "yes", "Yes", "1"):
        return True
    else:
        return False

def markup_result(result, markup):
    for p in ("info", "error"):
        if p in result:
            if type(result[p]) == list:
                for i, s in enumerate(result[p]):
                    result[p][i] = "%s: %s" % (markup, s)
            else:
                result[p] = "%s: %s" % (markup, result[p])
    return result

def merge_results(result, _result):
    if _result is None:
        return result
    if not isinstance(_result, dict) and result == {}:
        return _result
    if "ret" not in result:
        if "ret" not in _result:
            pass
        else:
            result["ret"] = _result["ret"]
    else:
        if "ret" not in _result:
            pass
        else:
            result["ret"] += _result["ret"]
    for p in ("info", "error"):
        if p not in result:
            if p not in _result:
                continue
            else:
                result[p] = _result[p]
        else:
            if p not in _result:
                continue
            else:
                if result[p] != list:
                    result[p] = [result[p]]
                if _result[p] != list:
                    _result[p] = [_result[p]]
                result[p] += _result[p]
    for p in _result:
        if p in ("info", "error", "ret"):
            continue
        if p not in result:
            result[p] = _result[p]
    return result

def get_handlers(action=None, prefix=None):
    if action == "GET":
        return get_get_handlers(prefix=prefix)
    elif action == "POST":
        return get_post_handlers(prefix=prefix)
    elif action == "DELETE":
        return get_delete_handlers(prefix=prefix)
    elif action == "PUT":
        return get_put_handlers(prefix=prefix)
    else:
        return {
            "GET": get_get_handlers(),
            "POST": get_post_handlers(),
            "DELETE": get_delete_handlers(),
            "PUT": get_put_handlers(),
        }

def get_handler(action, url):
    """ Support url with or without the leading /
    """
    url = url.lstrip("/")
    prefix = url.split("/")[0]
    for handler in get_handlers(action, prefix):
        if handler.match("/"+url):
            return handler

class rest_handler(object):
    def __init__(self,
                 action="GET",
                 path=None,
                 tables=[],
                 dbo=None,
                 props_blacklist=[],
                 vprops={},
                 vprops_fn=None,
                 count_prop="id",
                 q=None,
                 left=None,
                 groupby=None,
                 orderby=None,
                 replication=["local"],
                 allow_fset_id=False,
                 _cache=None,
                 desc=[], params={}, examples=[], data={}):
        self._cache = _cache
        self.action = action
        self.path = path
        self.tables = tables
        self.props_blacklist = props_blacklist
        self.desc = desc
        self.examples = examples
        self.init_params = params
        self.init_data = data
        self.count_prop = count_prop
        self.vprops = vprops
        self.vprops_fn = vprops_fn
        self.q = q
        self.left = left
        self.groupby = groupby
        self.orderby = orderby
        self.replication = replication
        self.allow_fset_id = allow_fset_id
        if dbo:
            self.db = dbo
        else:
            self.db = db


    def update_parameters(self):
        self.params = copy.copy(self.init_params)

    def set_q(self, q):
        self.q = q

    def get_pattern(self):
        return "^"+re.sub("\<[-\w]+\>", "[\$\#\:=% ><@\.\-\w\(\){slash,percent}*]+", self.path)+"$"

    def match(self, args):
        pattern = self.get_pattern()
        regexp = re.compile(pattern)
        return regexp.match(args)

    def replication_relay(self, collector, data):
        try:
            replication_config_mod = local_import('replication_config', reload=True)
        except ImportError:
            return
        try:
            repl_config = replication_config_mod.repl_config
        except AttributeError:
            return
        if len(repl_config) == 0 or "push" not in repl_config or len(repl_config["push"]) == 0:
            return

        p = get_proxy(collector, controller="rest")
        try:
            ret = p.relay_rest_request(auth.user_id, self.action, self.path, data)
            ret = markup_result(ret, collector)
            return ret
        except Exception as e:
            return {"ret": 1, "error": "remote collector %s raised %s" % (collector, str(e))}

    def replication_pull(self, collectors):
        for collector in collectors:
            pull_all_table_from_remote(collector)

    def get_svc_collectors(self, svc_id):
        q = db.svcmon.svc_id == svc_id
        q &= db.svcmon.node_id == db.nodes.node_id
        rows = db(q).select(db.nodes.collector, groupby=db.nodes.collector)
        return [r.collector for r in rows if r.collector is not None]

    def get_node_collectors(self, node_id):
        q = db.nodes.node_id == node_id
        node = db(q).select(db.nodes.collector).first()
        if node is None:
            return []
        if node.collector is None:
            return []
        return [node.collector]

    def get_collectors(self, *args, **vars):
        try:
            if "node_id" in vars:
                return self.get_node_collectors(get_node_id(vars["node_id"]))
            if "nodes" in args:
                idx = args.index("nodes")
                if len(args) > idx+1:
                    return self.get_node_collectors(get_node_id(args[idx+1]))
            if "svc_id" in vars:
                return self.get_svc_collectors(get_svc_id(vars["svc_id"]))
            if "services" in args:
                idx = args.index("services")
                if len(args) > idx+1:
                    return self.get_svc_collectors(get_svc_id(args[idx+1]))
        except:
            # object not found
            return []
        return []

    def handle(self, *args, **vars):
        if "local" not in self.replication and "relay" not in self.replication:
            return {"ret": 1, "error": "both local and remote handler skipped"}

        result = {}

        if "pull" in self.replication or "relay" in self.replication:
            collectors = self.get_collectors(*args, **vars)

        for repl_action in self.replication:
            if repl_action == "relay":
                for collector in collectors:
                    _result = self.replication_relay(collector, [args, vars])
                    result = merge_results(result, _result)
            elif repl_action == "pull":
                self.replication_pull(collectors)
            elif repl_action == "local":
                _result = self.handle_local(*args, **vars)
                result = merge_results(result, _result)

        return result

    def handle_local(self, *args, **vars):
        response.headers["Content-Type"] = "application/json"
        # extract args from the path
        # /a/<b>/c/<d> => [b, d]
        nargs = []
        for i, a in enumerate(self.path.rstrip("/").split("/")):
            if a.startswith("<") and a.endswith(">"):
                nargs.append(args[i-1])
        if "filters[]" in vars:
            if "filters" in vars:
                vars["filters"] += vars["filters[]"]
            else:
                vars["filters"] = vars["filters[]"]
            del(vars["filters[]"])

        if self._cache is None:
            try:
                return self.handler(*nargs, **vars)
            except TypeError as exc:
                raise Exception(exc)
        if self._cache is True:
            time_expire = 14400
        elif type(self._cache) == int:
            time_expire = self._cache
        key = self.get_cache_key(*nargs, **vars)
        return cache.redis(key, lambda: self.handler(*nargs, **vars), time_expire=time_expire)

    def cache_clear(self, keys):
        for key in keys:
            cache.redis.clear(regex="rest:.*:"+key+":.*")

    def get_cache_key(self, *nargs, **vars):
        import json
        from hashlib import md5
        sign = md5(json.dumps({"args": nargs, "vars": vars})).hexdigest()
        key = "rest:%s:%s:%s" % (auth.user_id, type(self).__name__, sign)
        return key

    def prepare_data(self, *args, **vars):
        add_to_vars = [
          "q",
          "orderby",
          "groupby",
          "left",
          "vprops",
          "vprops_fn",
          "count_prop",
          "props_blacklist",
          "tables",
          "db"
        ]

        if "fset-id" in vars:
            del(vars["fset-id"])

        if "orderby" in vars:
            cols, translations = props_to_cols(vars["orderby"], tables=self.tables, blacklist=self.props_blacklist, db=self.db)
            if len(cols) == 0:
                pass
            else:
                add_to_vars.remove("orderby")
                o = cols[0]
                if len(cols) > 1:
                   for col in cols[1:]:
                       o |= col
                vars["orderby"] = o

        for v in add_to_vars:
            if hasattr(self, v) and vars.get(v) is None:
                vars[v] = getattr(self, v)
        return prepare_data(**vars)

    def handler(self, *args, **vars):
        return self.prepare_data(*args, **vars)

    def update_data(self):
        self.data = {}
        if type(self.init_data) in (str, unicode):
            for i in re.findall("\*\*(\w+)\*\*", self.init_data):
                self.data[i] = {"desc": ""}
        elif type(self.init_data) == dict:
                self.data.update(self.init_data)
        if len(self.tables) == 0 or self.action not in ("POST", "PUT"):
            return
        for prop in all_props(tables=self.tables, vprops=self.vprops, blacklist=self.props_blacklist, db=self.db):
            if prop in self.data:
                # init data takes precedence
                continue

            v = prop.split(".")
            if len(v) == 2:
                _table, _prop = v
            else:
                _table = self.tables[0]
                _prop = prop
            if _prop == "id":
                continue
            colprops = globals().get(_table+"_colprops", {}).get(_prop, {})
            if colprops is None:
                colprops = globals().get("v_"+_table+"_colprops", {}).get(_prop, {})

            self.data[prop] = {
              "desc":  getattr(colprops, "title") if hasattr(colprops, "title") else "",
              "img":  getattr(colprops, "img") if hasattr(colprops, "img") else "",
              "type": self.db[_table][_prop].type,
              "table": _table,
              #"requires": self.db[_table][_prop].requires,
              #"default": self.db[_table][_prop].default,
              "unique": self.db[_table][_prop].unique,
              "writable": self.db[_table][_prop].writable,
            }

    def fmt_props_props_desc(self):
        cols, translations = props_to_cols(None, tables=self.tables, blacklist=self.props_blacklist, db=self.db)
        props = cols_to_props(cols, self.tables)
        s = """
A list of properties to include in each data dictionnary.

If omitted, all properties are included.

The separator is ','.

Available properties are: ``%(props)s``:green.

""" % dict(props=", ".join(sorted(props)))
        return s

    def handle_list(self, data, args, vars):
        rdata = {
          "info": [],
          "error": [],
          "data": [],
        }
        for entry in data:
            if type(entry) != dict:
                rdata["error"].append("skip '%s': not a dict" % str(entry))
                continue
            try:
                r = rest_handler.handle(self, *args, **entry)
            except HTTP as e:
                r = dict(error=str(e)+": "+e.body)
            except Exception as e:
                r = dict(error=str(e))
            for key in ("info", "error", "data"):
               if key in r:
                   d = r[key]
                   if type(d) == list:
                       rdata[key] += d
                   else:
                       rdata[key] += [d]
        return rdata

class rest_post_handler(rest_handler):
    def __init__(self, **vars):
        vars["action"] = "POST"
        rest_handler.__init__(self, **vars)

    def handle(self, *args, **vars):
        response.headers["Content-Type"] = "application/json"
        if request.env.http_content_type and "application/json" in request.env.http_content_type or \
           request.env.content_type and "application/json" in request.env.content_type:
            try:
                data = json.loads(request.body.read())
            except:
                return rest_handler.handle(self, *args, **vars)
            if type(data) == list:
                return self.handle_list(data, args, vars)
            elif type(data) == dict:
                return rest_handler.handle(self, *args, **data)
        if "filters" in vars and hasattr(self, "get_handler"):
            return self.handle_multi_update(*args, **vars)
        if "query" in vars and hasattr(self, "get_handler"):
            return self.handle_multi_update(*args, **vars)
        return rest_handler.handle(self, *args, **vars)

    def handle_multi_update(self, *args, **vars):
        _vars = {
          "limit": 0,
          "props": self.update_one_param,
        }
        if "query" in vars:
            _vars["query"] = vars["query"]
            del(vars["query"])
        if "filters" in vars:
            _vars["filters"] = vars["filters"]
            del(vars["filters"])
        l = self.get_handler.handler(**vars)["data"]
        result = {"data": []}
        for e in l:
            try:
                r = self.update_one_handler.handler(e.get(self.update_one_param), **vars)
                result["data"] += r["data"] if "data" in r else r
            except HTTP as e:
                d = dict(error=str(e)+": "+e.body)
                d[self.update_one_param] = e[self.update_one_param]
                result["data"] += [d]
            except Exception as ex:
                d = {"error": str(ex)}
                d[self.update_one_param] = e[self.update_one_param]
                result["data"] += [d]
        return result

    def update_parameters(self):
        self.params = copy.copy(self.init_params)
        if len(self.tables) == 0:
            return
        self.params.update({
          "filters": {
            "desc": """
An opensvc property values filter.

""",
          },
          "query": {
            "desc": """
A web2py smart query.

""",
          },
        })


class rest_put_handler(rest_handler):
    def __init__(self, **vars):
        vars["action"] = "PUT"
        rest_handler.__init__(self, **vars)

    def handle(self, *args, **vars):
        response.headers["Content-Type"] = "application/json"
        if request.env.http_content_type and "application/json" in request.env.http_content_type or \
           request.env.content_type and "application/json" in request.env.content_type:
            try:
                data = json.loads(request.body.read())
            except:
                return rest_handler.handle(self, *args, **vars)
            if type(data) == list:
                return self.handle_list(data, args, vars)
            elif type(data) == dict:
                return rest_handler.handle(self, *args, **data)
        if "filters" in vars and hasattr(self, "get_handler"):
            return self.handle_multi_update(*args, **vars)
        if "query" in vars and hasattr(self, "get_handler"):
            return self.handle_multi_update(*args, **vars)
        return rest_handler.handle(self, *args, **vars)


class rest_delete_handler(rest_handler):
    def __init__(self, **vars):
        vars["action"] = "DELETE"
        rest_handler.__init__(self, **vars)

    def handle(self, *args, **vars):
        response.headers["Content-Type"] = "application/json"
        if request.env.http_content_type and "application/json" in request.env.http_content_type or \
           request.env.content_type and "application/json" in request.env.content_type:
            try:
                data = json.loads(request.body.read())
            except:
                return rest_handler.handle(self, *args, **vars)
            if type(data) == list:
                return self.handle_list(data, args, vars)
            elif type(data) == dict:
                return rest_handler.handle(self, *args, **data)
        return rest_handler.handle(self, *args, **vars)

    def update_parameters(self):
        self.params = copy.copy(self.init_params)

    def update_data(self):
        self.data = copy.copy(self.init_data)

class rest_get_handler(rest_handler):
    def __init__(self, **vars):
        vars["action"] = "GET"
        rest_handler.__init__(self, **vars)

    def update_data(self):
        self.data = copy.copy(self.init_data)

class rest_get_table_handler(rest_handler):
    def __init__(self, **vars):
        vars["action"] = "GET"
        rest_handler.__init__(self, **vars)

    def update_parameters(self):
        self.params = copy.copy(self.init_params)
        self.params.update({
          "commonality": {
            "desc": """
Controls the inclusion in the returned dictionnary of a "commonality" key, containing the selected properties most frequent value with its occurence percentile.
* true: include.
* false: do not include.
""",
          },
          "data_format": {
            "desc": """
If set to "table", the structure in the "data" key value is formatted as a list of list instead of a list of dict. This parameter is used by the collector's javascript tables.
""",
          },
          "stats": {
            "desc": """
Controls the inclusion in the returned dictionnary of a "stats" key, containing the selected properties distinct values counts.
* true: include.
* false: do not include.
""",
          },
          "meta": {
            "desc": """
Controls the inclusion in the returned dictionnary of a "meta" key, whose parameter is a dictionnary containing the following properties: displayed entry count, total entry count, displayed properties, available properties, offset and limit.
* true: include.
* false: do not include.

""",
          },
          "limit": {
            "desc": """
The maximum number of entries to return. 0 means no limit.

""",
          },
          "offset": {
            "desc": """
Skip the first <offset> entries of the data cursor.

""",
          },
          "query": {
            "desc": """
A web2py smart query

""",
          },
          "filters": {
            "type": "list",
            "desc": """
An opensvc property values filter. Example: "updated>-2d".

""",
          },
          "groupby": {
            "desc": """
A comma-separated list of properties.

Group the resultset using the specified properties.
""",
          },
          "orderby": {
            "desc": """
A comma-separated list of properties.

Sort the resultset using the specified properties.

Property sorting priority decreases from left to right.

The order is descending by default.

A property can be prefixed by '~' to activate the ascending order.

""",
          },
          "props": {
            "desc": self.fmt_props_props_desc(),
          },
        })
        if self.allow_fset_id:
            self.params.update({
              "fset-id": {
                "desc": "Filter the list using the filterset identified by fset-id."
              }
            })

    def update_data(self):
        self.data = copy.copy(self.init_data)


class rest_get_line_handler(rest_handler):
    def __init__(self, **vars):
        vars["action"] = "GET"
        rest_handler.__init__(self, **vars)

    def update_parameters(self):
        self.params = copy.copy(self.init_params)
        self.params.update({
          "props": {
            "desc": self.fmt_props_props_desc(),
          },
        })

    def update_data(self):
        self.data = copy.copy(self.init_data)

    def prepare_data(self, *args, **vars):
        vars["meta"] = False
        vars["stats"] = False
        vars["commonality"] = False
        if "filters" in vars:
            del(vars["filters"])
        if "query" in vars:
            del(vars["query"])
        return rest_handler.prepare_data(self, **vars)

def data_commonality(cols, data):
    total = len(data)
    data = data_stats(cols, data)["data"]
    top = []
    for col in data:
        l = data[col].items()
        if len(l) == 0:
            continue
        l.sort(lambda x, y: cmp(x[1], y[1]), reverse=True)
        v, n = l[0]
        pct = 100*n//total
        if pct == 0 or n == 1:
            continue
        top.append({
          "prop": col,
          "value": v,
          "percent": pct,
        })
    top.sort(lambda x, y: cmp(x["percent"], y["percent"]), reverse=True)
    return dict(data=top)

def data_stats(cols, data):
    h = {}
    meta = {"distinct": {}}
    meta["total"] = len(data)
    if meta["total"] == 0:
        return dict(data=h, meta=meta)
    for c in cols:
        _col = ".".join((c.table._tablename, c.name))
        if _col not in data[0]:
            _col = c.name
        h[_col] = {}
        for d in data:
            val = d[_col]
            if val is None or val == "":
                val = 'empty'
            elif type(val) == datetime.datetime:
                val = val.strftime("%Y-%m-%d %H:%M:%S")
            elif type(val) == datetime.date:
                val = val.strftime("%Y-%m-%d")
            if val not in h[_col]:
                h[_col][val] = 1
            else:
                h[_col][val] += 1

    for _col in h:
        meta["distinct"][_col] = len(h[_col])
    return dict(data=h, meta=meta)

def prepare_data(
     meta=True,
     count_prop=None,
     query=None,
     stats=False,
     commonality=False,
     filters=[],
     props=None,
     vprops={},
     vprops_fn=None,
     props_blacklist=[],
     tables=[],
     data=None,
     q=None,
     db=db,
     groupby=None,
     orderby=None,
     left=None,
     cols=[],
     offset=0,
     limit=20,
     total=None,
     data_format=None):

    validated_props = []
    mapping = {}

    if left is None:
        left = []
    elif type(left) == pydal.objects.Expression:
        left = [left]
    elif type(left) == tuple:
        left = list(left)
    elif type(left) == list:
        pass
    else:
        raise HTTP(500, "invalid 'left' parameter type: %s" % type(left))

    if props is not None:
        for i, prop in enumerate(props.split(",")):
            if prop.count(":") == 1:
                prop, remap_as = prop.split(":")
            else:
                remap_as = None

            validated_prop = None
            if prop in vprops:
                validated_prop = prop
            elif "." not in prop:
                validated_prop = tables[0] + "." + prop
            else:
                t, c = prop.split(".")
                if t in tables:
                    validated_prop = prop
                elif t == "nodes":
                    for table in tables:
                        if "node_id" in db[table].fields:
                            left.append(db.nodes.on(db.nodes.node_id==db[table].node_id))
                            tables.append("nodes")
                            validated_prop = prop
                            break
                elif t == "services":
                    for table in tables:
                        if "svc_id" in db[table].fields:
                            left.append(db.services.on(db.services.svc_id==db[table].svc_id))
                            tables.append("services")
                            validated_prop = prop
                            break
                elif t == "apps":
                    for table in tables:
                        if "app_id" in db[table].fields:
                            left.append(db.apps.on(db.apps.id==db[table].app_id))
                            tables.append("apps")
                            validated_prop = prop
                            break
                elif t == "stor_array":
                    for table in tables:
                        if "array_id" in db[table].fields:
                            left.append(db.stor_array.on(db.stor_array.id==db[table].array_id))
                            tables.append("stor_array")
                            validated_prop = prop
                            break
                elif t == "tags":
                    for table in tables:
                        if "tag_id" in db[table].fields:
                            left.append(db.tags.on(db.tags.tag_id==db[table].tag_id))
                            tables.append("tags")
                            validated_prop = prop
                            break
                elif t == "comp_rulesets":
                    for table in tables:
                        if "ruleset_id" in db[table].fields:
                            left.append(db.comp_rulesets.on(db.comp_rulesets.id==db[table].ruleset_id))
                            tables.append("comp_rulesets")
                            validated_prop = prop
                            break
                elif t == "node_tags":
                    for table in tables:
                        if "tag_id" in db[table].fields:
                            left.append(db.node_tags.on(db.node_tags.tag_id==db[table].tag_id))
                            tables.append("node_tags")
                            validated_prop = prop
                            break
                elif t == "svc_tags":
                    for table in tables:
                        if "tag_id" in db[table].fields:
                            left.append(db.svc_tags.on(db.svc_tags.tag_id==db[table].tag_id))
                            tables.append("svc_tags")
                            validated_prop = prop
                            break
            if validated_prop:
                validated_props.append(prop)
                if remap_as:
                    mapping[validated_prop] = remap_as

        props = ",".join(validated_props)

    all_cols, translations = props_to_cols(None, tables=tables, blacklist=props_blacklist, db=db)
    cols, translations = props_to_cols(props, tables=tables, vprops=vprops, blacklist=props_blacklist, db=db)
    false_values = ("0", "f", "F", "False", "false", False, "n", "no", "N")

    if meta in false_values:
        meta = False
    else:
        meta = True
    if stats in false_values:
        stats = False
    else:
        stats = True
        limit = 0
    if commonality in false_values:
        commonality = False
    else:
        commonality = True
        limit = 0
    if not data and q:
        if type(filters) in (str, unicode):
            filters = [filters]
        for f in filters:
            f = unquote(f)
            f_prop = re.findall(r'[\.\w]+', f)[0]
            f_val = f[len(f_prop):].strip()
            if '.' in f_prop:
                t, f_col = f_prop.split(".")
            else:
                t = tables[0]
                f_col = f_prop
            q = _where(q, t, f_val, f_col, db=db)
        if query:
            try:
                q &= pydal.helpers.methods.smart_query(all_cols, query)
            except Exception as e:
                raise HTTP(400, T("smart query error for '%(s)s': %(err)s", dict(s=str(query), err=str(e))))
        if meta:
            if count_prop:
                try:
                    table, prop = count_prop.split(".")
                except:
                    table = tables[0]
                    prop = count_prop
                count_col = db[table][prop].count()
            else:
                count_col = cols[0].count()
            try:
                if groupby:
                    total = len(db(q).select(count_col, groupby=groupby, left=left))
                else:
                    total = db(q).select(count_col, left=left).first()._extra[count_col]
            except TypeError as exc:
                # raised when pydal smart query is bogus
                return dict(error="query error: %s" % str(exc))

        limit = int(limit)
        offset = int(offset)

        if limit == 0:
            # no limit. should we limit this to a priv group ?
            limitby = (offset, 2**20)
        else:
            limitby = (offset, offset + limit)

        try:
            data = db(q).select(
                       *cols,
                       cacheable=True,
                       left=left,
                       groupby=groupby,
                       orderby=orderby,
                       limitby=limitby
                     ).as_list()
        except TypeError as exc:
            # raised when pydal smart query is bogus
            return dict(error="query error: %s" % str(exc))
    else:
        return dict(error="failed to prepare data: missing parameter")

    data = mangle_data(data, props=props, vprops=vprops, vprops_fn=vprops_fn, tables=tables)
    if len(mapping) > 0:
        if len(tables) > 1:
            for i, _data in enumerate(data):
                remapped = _data[tables[0]]
                for old, new in mapping.items():
                    t, c = old.split(".")
                    remapped[new] = _data[t][c]
                data[i] = remapped
        else:
            for i, _data in enumerate(data):
                for old, new in mapping.items():
                    try:
                        t, c = old.split(".")
                    except ValueError:
                        c = old
                    data[i][new] = data[i][c]
                    del data[i][c]

    # reverve to deprecated column name
    if len(translations) > 0:
        for orig, translated in translations:
            short_orig = orig.split(".")[-1]
            short_translated = translated.split(".")[-1]
            for i, d in enumerate(data):
                if short_translated in data[i]:
                    data[i][short_orig] = data[i][short_translated]
                    del(data[i][short_translated])
                else:
                    data[i][orig] = data[i][translated]
                    del(data[i][translated])

    if stats:
        return data_stats(cols, data)
    if commonality:
        return data_commonality(cols, data)
    if meta:
        _cols = [".".join((c.table._tablename, c.name)) for c in cols]
        if props is None:
            _cols += vprops.keys()
        else:
            _cols += list(set(props.split(",")) & set(vprops.keys()))
            for _vprops in vprops.values():
                for prop in _vprops:
                    if prop in _cols and prop not in props.split(","):
                        _cols.remove(prop)
                    if len(tables) == 1:
                        prop = tables[0] + "." + prop
                        if prop in _cols and prop not in props.split(","):
                            _cols.remove(prop)
        _all_cols = [".".join((c.table._tablename, c.name)) for c in all_cols] + vprops.keys()
        meta = dict(
                 included_props=_cols,
                 available_props=_all_cols,
                 mapping=mapping,
                 offset=offset,
                 limit=limit,
                 total=total,
                 count=len(data),
                 server_timezone=config_get("server_timezone", "Europe/Paris"),
               )
        d = dict(data=data, meta=meta)
    else:
        d = dict(data=data)

    if data_format == "table":
        d["data"] = []
        for line in data:
            l = []
            for col in validated_props:
                try:
                    table, field = col.split(".")
                except ValueError:
                    table = tables[0]
                    field = col
                if field in line:
                    l.append(line[field])
                else:
                    l.append(line[table][field])
            d["data"].append(l)
    return d

def mangle_data(data, props=None, vprops={}, vprops_fn=None, tables=None):
    if vprops_fn is None:
        return data
    if props and len(set(vprops) & set(props.split(","))) == 0:
        return data
    data = vprops_fn(data)

    # purge props used to produce vprops
    props_to_purge = set([])
    for _vprops in vprops.values():
        props_to_purge |= set(_vprops)
    if props is not None:
        # unless the user expressly requested them
        props_to_purge -= set(props.split(","))
    for i, d in enumerate(data):
        for prop in props_to_purge:
            if prop in data[i]:
                del data[i][prop]
            if tables is not None and tables[0] in data[i] and prop in data[i][tables[0]]:
                del data[i][tables[0]][prop]
    return data

def all_props(tables=[], blacklist=[], vprops={}, db=db):
    cols, translations = props_to_cols(None, tables=tables, blacklist=blacklist, db=db)
    return cols_to_props(cols, tables=tables) + vprops.values()

def props_to_cols(props, tables=[], vprops={}, blacklist=[], db=db):
    if props is None:
        cols = []
        for table in tables:
            bl = [f.split(".")[-1] for f in blacklist if f.startswith(table+".") or "." not in f]
            for p in set(db[table].fields) - set(bl):
                cols.append(db[table][p])
        return cols, []
    cols = []
    props = set(props.split(",")) - set(vprops.keys())
    for _vprops in vprops.values():
        props |= set(_vprops)
    translations = []
    for p in props:
        if len(p) == 0:
            continue
        if p[0] == "~":
            desc = True
            p = p[1:]
        else:
            desc = False
        v = p.split(".")
        if len(v) == 1:
            v = [tables[0], p]

        # deprecated columns translation
        fullp = '.'.join(v)
        translated = False
        while fullp in deprecated_columns:
            fullp = deprecated_columns[fullp]
            translated = True
        if translated:
            translations.append(('.'.join(v), fullp))
            v = fullp.split(".")

        try:
            col = db[v[0]][v[1]]
        except Exception as e:
            raise HTTP(400, "prop does not exist: %s" % str(v))

        if desc:
            col = ~col
        cols.append(col)
    return cols, translations

def cols_to_props(cols, tables):
    if len(tables) > 1:
        multi = True
    else:
        multi = False
    props = [".".join((c.table._tablename, c.name)) if multi else c.name for c in cols]
    return props



