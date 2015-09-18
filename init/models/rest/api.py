import re

class rest_handler(object):
    def __init__(self,
                 path=None,
                 tables=[],
                 dbo=None,
                 props_blacklist=[],
                 count_prop="id",
                 q=None,
                 left=None,
                 groupby=None,
                 desc=[], params={}, examples=[], data={}):
        self.path = path.rstrip("/")
        self.tables = tables
        self.props_blacklist = props_blacklist
        self.desc = desc
        self.examples = examples
        self.params = params
        self.data = data
        self.count_prop = count_prop
        self.q = q
        self.left = left
        self.groupby = groupby
        if dbo:
            self.db = dbo
        else:
            self.db = db

        self.pattern = "^"+re.sub("\<[-\w]+\>", "[=% ><@\.\-\w]+", path)+"$"
        self.regexp = re.compile(self.pattern)

    def set_q(self, q):
        self.q = q

    def match_doc(self, args):
        if args == self.path:
            return True
        return False

    def match(self, args):
        return self.regexp.match(args)

    def handle(self, *args, **vars):
        # extract args from the path
        # /a/<b>/c/<d> => [b, d]
        nargs = []
        for i, a in enumerate(self.path.split("/")):
            if a.startswith("<") and a.endswith(">"):
                nargs.append(args[i-1])
        return self.handler(*nargs, **vars)

    def doc(self):
        s = self.fmt_title()
        s += self.fmt_desc()
        s += self.fmt_parameters()
        s += self.fmt_data()
        s += self.fmt_examples()
        return s

    def fmt_title(self):
        s = "[[%s]]\n" % (self.action)
        s += "## ``%s :: %s``:red\n" % (self.path, self.action)
        return s

    def fmt_desc(self):
        s = ""
        if len(self.desc) > 0:
           s += "\n".join(map(lambda x: "- "+x, self.desc))
        if len(s) > 0:
           s = "### Description\n"+s+"\n"
        return s

    def fmt_parameters(self):
        s = ""
        if len(self.params) > 0:
           s += "\n".join(map(lambda x: "- **%s**\n. %s"%(x[0], x[1].get("desc", "")), self.params.items()))
        if hasattr(self, "fmt_standard_parameters"):
           s += self.fmt_standard_parameters()
        if len(s) > 0:
           s = "### Parameters\n"+s+"\n"
        return s

    def fmt_data(self):
        if type(self.data) in (str, unicode):
            return "### Data\n"+self.data
        self.update_data()
        if self.data is None:
            return ""
        s = ""
        for key in sorted(set(self.data.keys())-set(["_extra"])):
            d = self.data[key]
            _writable = d.get("writable", True)
            if not _writable:
                continue
            l = []
            img = d.get("img", "")
            if len(img) > 0:
                l.append("[[ https://%s/init/static/%s.png left 16px]]" % (request.env.http_host, img))
            else:
                l.append("")
            l.append("**%s**"%key)
            _type = d.get("type", "")
            if len(_type) > 0:
                l.append("type: %s" % _type)
            else:
                l.append("")
            _unique = d.get("unique", False)
            if _unique:
                l.append("unique")
            else:
                l.append("")
            desc = d.get("desc", "")
            if len(desc) > 0:
                l.append("%s " % desc)
            else:
                l.append("")
            s += " | ".join(l)+"\n"
        if len(s) > 0:
           s = "### Data\n-----\n"+s+"-----\n"
        return s

    def fmt_examples(self):
        if len(self.examples) == 0:
            return ""
        s = "### Examples\n"
        for ex in self.examples:
            s += self.fmt_example(ex)
        return s

    def fmt_example(self, ex):
        s = ex % dict(email=user_email(), collector=request.env.http_host)
        return "``" + s + "``\n"

    def prepare_data(self, **vars):
        for v in ["q", "groupby", "left", "count_prop", "props_blacklist", "tables", "db"]:
            if hasattr(self, v) and vars.get(v) is None:
                vars[v] = getattr(self, v)
        return prepare_data(**vars)

    def handler(self, **vars):
        return self.prepare_data(**vars)

    def update_data(self):
        if len(self.tables) == 0 or self.action != "POST":
            return
        for prop in all_props(tables=self.tables, blacklist=self.props_blacklist, db=self.db):
            if prop in self.data:
                # suppose the caller knows better
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

            self.data[prop] = {
              "desc":  getattr(colprops, "title") if hasattr(colprops, "title") else "",
              "img":  getattr(colprops, "img") if hasattr(colprops, "img") else "",
              "type": self.db[_table][_prop].type,
              "requires": self.db[_table][_prop].requires,
              "default": self.db[_table][_prop].default,
              "unique": self.db[_table][_prop].unique,
              "writable": self.db[_table][_prop].writable,
            }


class rest_post_handler(rest_handler):
    action = "POST"

    def handle(self, *args, **vars):
        if "query" in vars and hasattr(self, "get_handler"):
            return self.handle_multi_update(*args, **vars)
        return rest_handler.handle(self, *args, **vars)

    def handle_multi_update(self, *args, **vars):
        l = self.get_handler.handler(query=vars["query"], limit=0, props=self.update_one_param)["data"]
        del(vars["query"])
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


class rest_put_handler(rest_handler):
    action = "PUT"

class rest_delete_handler(rest_handler):
    action = "DELETE"

class rest_get_handler(rest_handler):
    action = "GET"

class rest_get_table_handler(rest_handler):
    action = "GET"
    def fmt_standard_parameters(self):
        return doc_fmt_props_get(tables=self.tables, blacklist=self.props_blacklist, db=self.db)

class rest_get_line_handler(rest_handler):
    action = "GET"
    def fmt_standard_parameters(self):
        return doc_fmt_props_get_one(tables=self.tables, blacklist=self.props_blacklist, db=self.db)

    def prepare_data(self, **vars):
        vars["meta"] = False
        if "query" in vars:
            del(vars["query"])
        return rest_handler.prepare_data(self, **vars)

def prepare_data(
     meta=True,
     count_prop=None,
     query=None,
     props=None,
     props_blacklist=[],
     tables=[],
     data=None,
     q=None,
     db=db,
     groupby=None,
     left=None,
     cols=[],
     offset=0,
     limit=20,
     total=None):
    cols = props_to_cols(props, tables=tables, blacklist=props_blacklist, db=db)
    all_cols = props_to_cols(None, tables=tables, blacklist=props_blacklist, db=db)
    if meta in ("0", "f", "F", "False", "false", False):
        meta = False
    else:
        meta = True
    if not data and q:
        if query:
            q &= smart_query(all_cols, query)
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
                       limitby=limitby
                     ).as_list()
    else:
        return dict(error="failed to prepare data: missing parameter")

    if meta:
        _cols = [".".join((c.table._tablename, c.name)) for c in cols]
        _all_cols = [".".join((c.table._tablename, c.name)) for c in all_cols]
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

def check_privilege(priv):
    ug = user_groups()
    if 'Manager' in ug:
        return
    if priv not in ug:
        raise Exception("Not authorized: user has no %s privilege" % priv)

def all_props(tables=[], blacklist=[], db=db):
    cols = props_to_cols(None, tables=tables, blacklist=blacklist, db=db)
    return cols_to_props(cols, tables=tables)

def props_to_cols(props, tables=[], blacklist=[], db=db):
    if props is None:
        cols = []
        for table in tables:
            bl = [f.split(".")[-1] for f in blacklist if f.startswith(table+".") or "." not in f]
            for p in set(db[table].fields) - set(bl):
                cols.append(db[table][p])
        return cols
    cols = []
    for p in props.split(","):
        v = p.split(".")
        if len(v) == 1 and len(tables) == 1:
            v = [tables[0], p]
        cols.append(db[v[0]][v[1]])
    return cols

def cols_to_props(cols, tables):
    if len(tables) > 1:
        multi = True
    else:
        multi = False
    props = [".".join((c.table._tablename, c.name)) if multi else c.name for c in cols]
    return props

def doc_fmt_props_get_one(props=None, tables=[], blacklist=[], db=db):
    s = doc_fmt_props_props(props=props, tables=tables, blacklist=blacklist, db=db)
    return s

def doc_fmt_props_get(props=None, tables=[], blacklist=[], db=db):
    s = doc_fmt_props_meta()
    s += doc_fmt_props_limit()
    s += doc_fmt_props_offset()
    s += doc_fmt_props_props(props=props, tables=tables, blacklist=blacklist, db=db)
    s += doc_fmt_props_query()
    return s

def doc_fmt_props_meta():
    s = """
- **meta**
. Controls the inclusion in the returned dictionnary of a "meta" key, whose parameter is a dictionnary containing the following properties: displayed entry count, total entry count, displayed properties, available properties, offset and limit.
. true: include data cursor metadata.
. false: do no include data cursor metadata.

"""
    return s

def doc_fmt_props_limit():
    s = """
- **limit**
. The maximum number of entries to return.
. 0 means no limit.

"""
    return s

def doc_fmt_props_offset():
    s = """
- **offset**
. Skip the first <offset> entries of the data cursor.

"""
    return s

def doc_fmt_props_query():
    s = """
- **query**
. A web2py smart query

"""
    return s

def doc_fmt_props_props(props=None, tables=[], blacklist=[], db=db):
    cols = props_to_cols(props, tables=tables, blacklist=blacklist, db=db)
    props = cols_to_props(cols, tables)
    s = """
- **props**
. A list of properties to include in each data dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.

""" % dict(props=", ".join(sorted(props)))
    return s

