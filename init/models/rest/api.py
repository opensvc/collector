import re
from pydal.helpers.methods import smart_query

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
        if dbo:
            self.db = dbo
        else:
            self.db = db


    def update_parameters(self):
        self.params = copy.copy(self.init_params)

    def set_q(self, q):
        self.q = q

    def get_pattern(self):
        return "^"+re.sub("\<[-\w]+\>", "[=% ><@\.\-\w]+", self.path)+"$"

    def match(self, args):
        pattern = self.get_pattern()
        regexp = re.compile(pattern)
        return regexp.match(args)

    def handle(self, *args, **vars):
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
            return self.handler(*nargs, **vars)
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

    def prepare_data(self, **vars):
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

        if "orderby" in vars:
            cols = props_to_cols(vars["orderby"], tables=self.tables, blacklist=self.props_blacklist, db=self.db)
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

    def handler(self, **vars):
        return self.prepare_data(**vars)

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
        cols = props_to_cols(None, tables=self.tables, blacklist=self.props_blacklist, db=self.db)
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
        if request.env.http_content_type and "application/json" in request.env.http_content_type:
            data = json.loads(request.body.read())
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
        if request.env.http_content_type and "application/json" in request.env.http_content_type:
            data = json.loads(request.body.read())
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
        if request.env.http_content_type and "application/json" in request.env.http_content_type:
            data = json.loads(request.body.read())
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

    def prepare_data(self, **vars):
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
    if len(data) == 0:
        return dict(data=h)
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
    return dict(data=h)

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
     total=None):
    cols = props_to_cols(props, tables=tables, vprops=vprops, blacklist=props_blacklist, db=db)
    all_cols = props_to_cols(None, tables=tables, blacklist=props_blacklist, db=db)
    false_values = ("0", "f", "F", "False", "false", False)

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
            f_prop = re.findall(r'\w+', f)[0]
            f_val = f[len(f_prop):].strip()
            if '.' in f_prop:
                t, f_col = f_prop.split(".")
            else:
                t = tables[0]
                f_col = f_prop
            q = _where(q, t, f_val, f_col, db=db)
        if query:
            try:
                q &= smart_query(all_cols, query)
            except Exception as e:
                raise Exception(T("smart query error for '%(s)s': %(err)s", dict(s=str(query), err=str(e))))
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
            if groupby:
                total = len(db(q).select(count_col, groupby=groupby, left=left))
            else:
                total = db(q).select(count_col, left=left).first()._extra[count_col]

        limit = int(limit)
        offset = int(offset)

        if limit == 0:
            # no limit. should we limit this to a priv group ?
            limitby = (offset, 2**20)
        else:
            limitby = (offset, offset + limit)

        data = db(q).select(
                       *cols,
                       cacheable=True,
                       left=left,
                       groupby=groupby,
                       orderby=orderby,
                       limitby=limitby
                     ).as_list()
    else:
        return dict(error="failed to prepare data: missing parameter")

    data = mangle_data(data, props=props, vprops=vprops, vprops_fn=vprops_fn)

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
                 offset=offset,
                 limit=limit,
                 total=total,
                 count=len(data),
               )
        d = dict(data=data, meta=meta)
    else:
        d = dict(data=data)

    return d

def mangle_data(data, props=None, vprops={}, vprops_fn=None):
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
            del(data[i][prop])
    return data

def check_privilege(privs):
    ug = user_groups()
    if 'Manager' in ug:
        return
    if type(privs) == list:
        privs = set(privs)
    else:
        privs = set([privs])
    if len(privs & set(ug)) == 0:
        raise Exception("Not authorized: user has no %s privilege" % ", ".join(privs))

def all_props(tables=[], blacklist=[], vprops={}, db=db):
    cols = props_to_cols(None, tables=tables, blacklist=blacklist, db=db)
    return cols_to_props(cols, tables=tables) + vprops.values()

def props_to_cols(props, tables=[], vprops={}, blacklist=[], db=db):
    if props is None:
        cols = []
        for table in tables:
            bl = [f.split(".")[-1] for f in blacklist if f.startswith(table+".") or "." not in f]
            for p in set(db[table].fields) - set(bl):
                cols.append(db[table][p])
        return cols
    cols = []
    props = set(props.split(",")) - set(vprops.keys())
    for _vprops in vprops.values():
        props |= set(_vprops)
    for p in props:
        if p[0] == "~":
            desc = True
            p = p[1:]
        else:
            desc = False
        v = p.split(".")
        if len(v) == 1 and len(tables) == 1:
            v = [tables[0], p]
        col = db[v[0]][v[1]]
        if desc:
            col = ~col
        cols.append(col)
    return cols

def cols_to_props(cols, tables):
    if len(tables) > 1:
        multi = True
    else:
        multi = False
    props = [".".join((c.table._tablename, c.name)) if multi else c.name for c in cols]
    return props



