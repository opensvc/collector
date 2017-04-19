import re
import hashlib
import datetime
import gluon.contrib.simplejson as json

def print_duration(begin, s):
    end = datetime.datetime.now()
    duration = datetime.datetime.now() - begin
    print s, duration
    return end

def request_vars_to_table_options():
    o = {'request_vars': {}}
    for key in request.vars:
        if '_f_' in key:
            o["request_vars"][key] = request.vars[key]
    if "volatile_filters" in request.vars:
        o["volatile_filters"] = request.vars.volatile_filters
    return json.dumps(o, use_decimal=True)

class ToolError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

class HtmlTableColumn(object):
    def __init__(self, field, table=None, filter_redirect=None,
                 force_filter=None):
        self.table = table
        self.field = field
        self.filter_redirect = filter_redirect
        self.force_filter = force_filter

    def __repr__(self):
        return str(self.as_dict())

    def __str__(self):
        return str(self.as_dict())

    def as_dict(self):
        data = {
         'field': self.field,
         'table': self.table or "",
         'filter_redirect': self.filter_redirect or "",
         'force_filter': self.force_filter or "",
        }
        return data

    def get(self, o):
        try:
            if self.table is None or self.table not in o:
                return o[self.field]
            else:
                return o[self.table][self.field]
        except (KeyError, AttributeError):
            return ''

class HtmlTable(object):
    def __init__(self, id=None, func=None, innerhtml=None):
        if innerhtml is None:
            innerhtml=id
        self.id = id
        self.innerhtml = innerhtml
        self.line_count = 0
        self.id_perpage = 'perpage'
        self.id_page = 'page'
        self.upc_table = self.id
        self.last = None
        self.object_list = []

        # to be set by children
        self.cols = []
        self.colprops = {}

        # column ids to use as keys to detect duplicate lines on
        # websocket triggered updates.
        self.keys = []

        # to be set be instanciers
        self.pageable = True
        self.span = []

        # initialize the pager, to be re-executed by instanciers
        self.setup_pager()

        # csv
        self.csv_q = None
        self.csv_orderby = None
        self.csv_left = None
        self.csv_limit = 20000

    def setup_pager(self, n=0, max_perpage=500):
        """ pass n=-1 to display a simple pager
            to use when computing the total records number is too costly
        """
        self.totalrecs = n
        if n == default_max_lines:
            self.overlimit = "+"
        else:
            self.overlimit = ""
        if self.pageable:
            try:
                self.perpage = int(request.vars[self.id_perpage])
            except:
                self.perpage = 20

            if self.id_page in request.vars and request.vars[self.id_page] != "undefined":
                self.page = int(request.vars[self.id_page])
            else:
                self.page = 1

            if self.page == 0:
                self.perpage = 0
                self.pager_start = 0
                self.pager_end = n
            else:
                self.pager_start = (self.page-1) * self.perpage
                if self.totalrecs > 0 and self.pager_start > self.totalrecs:
                    self.pager_start = 0
                self.pager_end = self.pager_start + self.perpage
        else:
            self.perpage = 0
            self.page = 0
            self.pager_start = 0
            self.pager_end = n
        self.page_len = self.pager_end - self.pager_start

    def repr_val(self, s):
        if s is None or s == "":
            s = 'empty'
        elif type(s) == datetime.datetime:
            try:
                s = s.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                s = ""
        elif type(s) == datetime.date:
            try:
                s = s.strftime("%Y-%m-%d")
            except ValueError:
                s = ""
        return s

    def col_values_cloud_ungrouped(self, c):
        h = {}
        for o in self.object_list:
            s = self.colprops[c].get(o)
            s = self.repr_val(s)
            if s not in h:
                h[s] = 1
            else:
                h[s] += 1
        return json.dumps(h, use_decimal=True)

    def pager_info(self):
        d = {
          'perpage': self.perpage,
          'total': self.totalrecs,
          'start': self.pager_start,
          'end': self.pager_end,
          'page': self.page,
        }
        return d

    def _table_lines_data(self):
        l = []
        for line in self.object_list:
            if len(self.keys) > 0:
                cksum = hashlib.md5()
            else:
                cksum = None
            if len(self.span) > 0:
                spansum = hashlib.md5()
            else:
                spansum = None

            _l = []
            for c in request.vars.visible_columns.split(","):
                v = self.colprops[c].get(line)
                if type(v) == datetime.datetime:
                    try:
                        v = v.strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        v = str(v)
                elif type(v) == datetime.date:
                    try:
                        v = v.strftime("%Y-%m-%d")
                    except ValueError:
                        v = str(v)
                elif v is None:
                    v = 'empty'
                #elif type(v) in (str, unicode):
                #    v = v.replace('"','').replace("'","")
                _l.append(v)
                if c in self.keys:
                    cksum.update(str(v))
                if c in self.span:
                    spansum.update(str(v))
            l.append({
              'cksum': cksum.hexdigest() if cksum else '',
              'spansum': spansum.hexdigest() if spansum else '',
              'cells': _l,
            })
        return l

    def table_lines_data(self, n=0, html=False):
        self.setup_pager(n)
        fmt = "json"
        formatter = self._table_lines_data
        d = {
          'format': fmt,
          'pager': self.pager_info(),
          'table_lines': formatter(),
        }
        return json.dumps(d, use_decimal=True)

    def filter_key(self, f):
        return '_'.join((self.id, 'f', f))

    def filter_parse(self, f):
        v = self._filter_parse(f)
        return v

    def ajax_inputs(self):
        l = map(self.filter_key, self.cols)
        return l

    def _filter_parse(self, f):
        key = self.filter_key(f)
        if key in request.vars:
            v = request.vars[key]
            return v
        return ""

    def csv_object_list(self):
        if self.csv_q is None:
            return self.object_list
        if hasattr(self, "csv_db"):
            _db = self.csv_db
        else:
            _db = db
        if self.csv_left is None:
            if self.csv_orderby is None:
                return _db(self.csv_q).select(cacheable=True, limitby=(0,self.csv_limit))
            else:
                return _db(self.csv_q).select(cacheable=True, orderby=self.csv_orderby, limitby=(0,self.csv_limit))
        else:
            if self.csv_orderby is None:
                return _db(self.csv_q).select(cacheable=True, limitby=(0,self.csv_limit), left=self.csv_left)
            else:
                return _db(self.csv_q).select(cacheable=True, orderby=self.csv_orderby, limitby=(0,self.csv_limit), left=self.csv_left)

    def _csv(self):
        lines = [';'.join(self.cols)]
        object_list = self.csv_object_list()
        for i in object_list:
            if isinstance(i, str) or isinstance(i, unicode) or isinstance(i, int):
                o = object_list[i]
            else:
                o = i
            inf = []
            for c in self.cols:
                v = self.colprops[c].get(o)
                if isinstance(v, str) or isinstance(v, unicode):
                    v = repr(v).replace('\\n', ' | ')
                    if v.startswith("u'"): v = v[1:]
                    v = v.replace("'", "").replace(';','')
                elif isinstance(v, datetime.datetime):
                    try:
                        v = v.strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        v = str(v)
                elif v is None:
                    v = ""
                else:
                    v = str(v)
                inf.append(v)
            lines.append(';'.join(inf))
        return '\n'.join(lines)

    def csv(self):
        import gluon.contenttype
        response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
        response.headers['Content-disposition'] = 'attachment; filename=%s.csv' % self.id
        return self._csv()

    def do_commonality(self):
        object_list = self.csv_object_list()
        total = len(object_list)
        data = {}
        for col in self.cols:
             data[col] = {}
        for o in object_list:
            for col in self.cols:
                v = self.colprops[col].get(o)
                if v in data[col]:
                    data[col][v] += 1
                else:
                    data[col][v] = 1
        top = []
        for col in self.cols:
            l = data[col].items()
            if len(l) == 0:
                continue
            l.sort(lambda x, y: cmp(x[1], y[1]), reverse=True)
            v, n = l[0]
            pct = 100*n//total
            if pct == 0 or n == 1:
                continue
            v = self.repr_val(v)
            top.append((col, v, pct))
        top.sort(lambda x, y: cmp(x[2], y[2]), reverse=True)
        return json.dumps(top, use_decimal=True)

    def get_visible_columns(self, fmt="dal", db=db):
        visible_columns = request.vars.visible_columns.split(',')
        sorted_visible_columns = []
        for c in visible_columns:
            if c not in self.cols or c not in self.colprops:
                continue
            cp = self.colprops[c]
            if cp.table is None:
                continue
            if cp.field not in db[cp.table]:
                continue
            sorted_visible_columns.append(c)
        if fmt == "dal":
            for i, c in enumerate(sorted_visible_columns):
                cp = self.colprops[c]
                sorted_visible_columns[i] = db[cp.table][cp.field]
        elif fmt == "sql":
            for i, c in enumerate(sorted_visible_columns):
                cp = self.colprops[c]
                sorted_visible_columns[i] = cp.table+"."+cp.field
            sorted_visible_columns = ','.join(sorted_visible_columns)

        return sorted_visible_columns

    def get_orderby(self, fmt="dal", db=db, default=None):
        if request.vars.orderby is None:
            return default
        elements = request.vars.orderby.split(',')
        if len(request.vars.orderby) == 0:
            return default
        orderby = []
        for c in elements:
            if c[0] == "~":
                desc = True
                c = c[1:]
            else:
                desc = False
            if c not in self.cols or c not in self.colprops:
                continue
            cp = self.colprops[c]
            if cp.field not in db[cp.table]:
                continue
            if fmt == "dal":
                if desc:
                    f = ~db[cp.table][cp.field]
                else:
                    f = db[cp.table][cp.field]
                orderby.append(f)
            elif fmt == "sql":
                f = cp.table+"."+cp.field
                if desc:
                    f += " desc"
                orderby.append(f)
        if fmt == "sql":
            orderby = ','.join(orderby)

        return orderby


#
# common column formatting
#

now = datetime.datetime.now()

def beautify_size_mb(d):
       try:
          d = int(d)
       except:
          return '-'
       if d < 0:
           neg = True
           d = -d
       else:
           neg = False
       if d < 1024:
           v = 1.0 * d
           unit = 'MB'
       elif d < 1048576:
           v = 1.0 * d / 1024
           unit = 'GB'
       else:
           v = 1.0 * d / 1048576
           unit = 'TB'
       if v >= 100:
           fmt = "%d"
       elif v >= 10:
           fmt = "%.1f"
       else:
           fmt = "%.2f"
       fmt = fmt + " %s"
       if neg:
           v = -v
       return fmt%(v, unit)

