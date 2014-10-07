import re
import hashlib

def print_duration(begin, s):
    end = datetime.datetime.now()
    duration = datetime.datetime.now() - begin
    print s, duration
    return end

def select_filter(fset_id):
    # refuse to change filter for locked-filter users
    q = db.auth_user.id == auth.user_id
    rows = db(q).select(db.auth_user.lock_filter, cacheable=True)
    if len(rows) != 1:
        return
    if rows.first().lock_filter:
        return

    try:
        cast_fset_id = int(fset_id)
    except:
        return

    # ok, let's do it
    q = db.gen_filterset_user.user_id == auth.user_id
    if fset_id == "0":
        db(q).delete()
    else:
        n = db(q).count()
        if n > 1:
            db(q).delete()
            n = 0
        if n == 1:
            try:
                db(q).update(fset_id=fset_id)
            except:
                pass
        elif n == 0:
            try:
                db.gen_filterset_user.insert(user_id=auth.user_id, fset_id=fset_id)
            except:
                pass

class ToolError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

class HtmlTableMenu(object):
    def __init__(self, title, img='default', options=[], id=None):
        self.title = title
        self.options = options
        self.img = img
        if id is not None:
           self.mid = id
        else:
            self.mid = 'menu_'+str(self.title.replace(' ','_'))

    def html(self):
        l = []
        for o in self.options:
             l.append(getattr(self.table, o)())
        return DIV(
                 A(
                   SPAN(
                     T(self.title),
                     _class=self.img
                   ),
                   _onclick="click_toggle_vis(event,'%s','block')"%self.mid,
                 ),
                 DIV(
                   l,
                   _name=self.mid,
                   _style='display:none;position:absolute',
                   _class='white_float',
                 ),
                 _class='floatw',
               )

class Column(object):
    def __init__(self, title, display=False, img='generic', _class='', _dataclass=''):
        self.title = title
        self.display = display
        self.img = img
        self._class = _class
        self._dataclass = _dataclass

class HtmlTableColumn(Column):
    def __init__(self, title, field, table=None, display=False,
                 img='generic', _class='', _dataclass='', filter_redirect=None,
                 default_filter=None, force_filter=None):
        Column.__init__(self, title, display, img, _class, _dataclass)
        self.table = table
        self.field = field
        self.filter_redirect = filter_redirect
        self.default_filter = default_filter
        self.force_filter = force_filter

    def __str__(self):
        return str(self.as_dict())

    def as_dict(self):
        data = {
         '_class': self._class,
         '_dataclass': self._dataclass,
         'title': self.title,
         'field': self.field,
         'table': self.table or "",
         'filter_redirect': self.filter_redirect or "",
         'default_filter': self.default_filter or "",
         'force_filter': self.force_filter or "",
         'img': self.img,
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
            #raise Exception('KeyError:', self.table, self.field, o)

    def html(self, o):
        val = self.get(o)
        if val is None:
            return ''
        return val

class HtmlTable(object):
    def __init__(self, id=None, func=None, innerhtml=None):
        if innerhtml is None:
            innerhtml=id
        self.id = id
        self.innerhtml = innerhtml
        self.func = func
        self.ajax_col_values = func
        self.line_count = 0
        self.max_live_perpage = 50
        self.id_perpage = '_'.join((self.id, 'perpage'))
        self.id_page = '_'.join((self.id, 'page'))
        self.upc_table = self.id
        self.last = None
        self.column_filter_reset = '**clear**'
        self.object_list = []
        self.child_tables = []
        self.force_cols = []

        # to be set by children
        self.additional_inputs = []
        self.additional_filters = []
        self.cols = []
        self.colprops = {}
        self.order = []

        # column ids to use as keys to detect duplicate lines on
        # websocket triggered updates.
        self.keys = []

        # to be set be instanciers
        self.checkboxes = False
        self.checkbox_names = [self.id+'_ck']
        self.checkbox_id_col = 'id'
        self.checkbox_id_table = None
        self.extraline = False
        self.extrarow = False
        self.extrarow_class = None
        self.filterable = True
        self.hide_tools = False
        self.dbfilterable = True
        self.pageable = True
        self.exportable = True
        self.linkable = True
        self.bookmarkable = True
        self.commonalityable = True
        self.refreshable = True
        self.columnable = True
        self.headers = True
        self.colored_lines = True
        self.additional_tools = []
        self.span = []
        self.flash = None
        self.nodatabanner = True
        self.highlight = True
        self.wsable = False
        self.dataable = False

        # initialize the pager, to be re-executed by instanciers
        self.setup_pager()

        # drop stored filters if request asks for it
        self.drop_filters()

        # csv
        self.csv_q = None
        self.csv_orderby = None
        self.csv_left = None
        self.csv_limit = 2000

    def __iadd__(self, o):
        if isinstance(o, HtmlTableMenu):
            o.table = self
            self.additional_tools.append(o)
        return self

    def tables(self):
        t = set([])
        for c in self.cols:
            if c in self.colprops and \
               hasattr(self.colprops[c], 'table') and \
               self.colprops[c].table is not None:
                t.add(self.colprops[c].table)
        return t

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
            if self.id_perpage in request.vars:
                q = db.auth_user.id==auth.user.id
                self.perpage = int(request.vars[self.id_perpage])
                try:
                    db(q).update(perpage=self.perpage)
                except:
                    pass
            else:
                q = db.auth_user.id==auth.user.id
                try:
                    self.perpage = db(q).select(cacheable=True).first().perpage
                except:
                    self.perpage = 20
            if self.perpage > max_perpage:
                self.perpage = max_perpage

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

    def col_values_cloud_ungrouped(self, c):
        h = {}
        l = []
        for o in self.object_list:
            s = self.colprops[c].get(o)
            if s is None or s == "":
                s = 'empty'
            if s not in h:
                h[s] = 1
            else:
                h[s] += 1

        max = 0
        for n in h.values():
            if n > max: max = n
        min = max
        for n in h.values():
            if n < min: min = n
        delta = max - min

        # 'empty' might not be comparable with other keys type
        if 'empty' in h.keys():
            skeys = h.keys()
            skeys.remove('empty')
            skeys = ['empty'] + sorted(skeys)
        else:
            skeys = sorted(h.keys())

        for s in skeys:
            n = h[s]
            if delta > 0:
                size = 100 + 100. * (n - min) / delta
            else:
                size = 100
            if n == 1:
                title = "%d occurence"%n
            else:
                title = "%d occurences"%n
            l.append(A(
                       s,
                       ' ',
                       _class="cloud_tag",
                       _style="font-size:%d%%"%size,
                       _title="%d occurences"%n,
                       _onclick="filter_submit('%(id)s','%(iid)s','%(val)s')"%dict(
                                id=self.id,
                                iid=self.filter_key(c),
                                val=s,
                               ),
                    ))
        return DIV(
                 H3(T("%(n)d unique matching values", dict(n=len(h)))),
                 DIV(l),
               )

    def col_values_cloud(self, c):
        session.forget(response)
        l = []
        for o in self.object_list:
            s = self.colprops[c].get(o)
            if s is None:
                s = 'empty'
            l.append(A(
                       s,
                       ' ',
                       _class="cloud_tag",
                       _onclick="filter_submit('%(id)s','%(iid)s','%(val)s')"%dict(
                                id=self.id,
                                iid=self.filter_key(c),
                                val=self.colprops[c].get(o),
                               ),
                    ))
        return DIV(
                 H3(T("%(n)d unique matching values", dict(n=len(self.object_list)))),
                 DIV(l),
               )

    def visible_columns(self):
        return [k for k, v in self.colprops.items() if v.display]

    def get_column_visibility(self, c):
        return self.colprops[c].display

    def set_column_visibility(self):
        q = db.user_prefs_columns.upc_user_id==session.auth.user.id
        q &= db.user_prefs_columns.upc_table==self.upc_table
        rows = db(q).select(cacheable=True)
        for row in rows:
            if row.upc_field not in self.colprops:
                continue
            self.colprops[row.upc_field].display = row.upc_visible

        #
        # if a column has a filter set, make it visible, even if it
        # marked for hiding.
        #
        q = db.column_filters.user_id==session.auth.user.id
        q &= db.column_filters.col_tableid==self.id
        q &= db.column_filters.bookmark=="current"
        rows = db(q).select(cacheable=True)
        for row in rows:
            field = row.col_name.split('.')[-1]
            if field not in self.colprops:
                continue
            self.colprops[field].display = True

    def format_av_filter(self, f):
        if f is None:
            name = T("None")
            fset_id = 0
        else:
            name = f.fset_name
            fset_id = f.id
        return OPTION(
                 name,
                 _value=fset_id,
               )

    def persistent_filters(self):
        if not self.dbfilterable:
            return SPAN()

        q = db.auth_user.id == auth.user_id
        rows = db(q).select(db.auth_user.lock_filter, cacheable=True)
        if len(rows) != 1:
            return SPAN()

        if rows.first().lock_filter:
            lock_filter = True
        else:
            lock_filter = False

        q = db.gen_filterset_user.user_id == auth.user_id
        q &= db.gen_filterset_user.fset_id == db.gen_filtersets.id
        if hasattr(self, 'fset_stats') and self.fset_stats:
            q &= db.gen_filtersets.fset_stats == True
        rows = db(q).select(cacheable=True)
        active_fset_id = 0
        for row in rows:
            active_fset_id = row.gen_filtersets.id
            active_fset_name = row.gen_filtersets.fset_name

        if lock_filter:
            content = active_fset_name
        else:
            o = db.gen_filtersets.fset_name
            q = db.gen_filtersets.id > 0
            rows = db(q).select(orderby=o, cacheable=True)
            av = [self.format_av_filter(None)]
            for row in rows:
                av.append(self.format_av_filter(row))
            content = SELECT(
                        av,
                        value=active_fset_id,
                        _id="avs"+self.id,
                      )

        s = SPAN(
              T('Filter'),
              ' ',
              content,
              _class='floatw',
            )
        return s

    def columns_selector(self):
        if not self.columnable:
            return SPAN()
        def checkbox(a):
            id_col = self.col_checkbox_key(a)

            if self.get_column_visibility(a) or \
               (id_col in request.vars and request.vars[id_col] == 'on'):
                val = 'on'
            else:
                val = ''

            s = SPAN(
                  INPUT(
                    _type='checkbox',
                    _name=id_col,
                    _onclick="""table_toggle_column("%(id)s","%(column)s", "%(table)s")
                             """%dict(url=URL(r=request,c='ajax',f='ajax_set_user_prefs_column'),
                                      column=a,
                                      id=self.id,
                                      table=self.upc_table,
                                 ),
                    value=val,
                    _style='vertical-align:text-bottom',
                  ),
                  SPAN(
                    T(self.colprops[a].title),
                    _style="""background-image:url(%s);
                              background-repeat:no-repeat;
                              padding-left:18px;
                              margin-left:0.2em;
                           """%URL(r=request,c='static',f=self.colprops[a].img+'.png'),
                  ),
                  BR(),
                  _style='white-space:nowrap',
                )
            return s

        a = DIV(
              SPAN(
                _id='set_col_dummy',
                _style='display:none',
              ),
              SPAN(map(checkbox, self.cols)),
              _style='-moz-column-width:13em;-webkit-column-width:13em;column-width:13em',
            )
        d = DIV(
              A(
                SPAN(T('Configure columns'), _class='columns'),
                _onclick="click_toggle_vis(event, '%(div)s', 'block')"%dict(
                                                          div=self.col_selector_key()),
              ),
              DIV(
                a,
                _style='display:none',
                _class='white_float',
                _name=self.col_selector_key(),
              ),
              _class='floatw',
            )
        return d

    def link(self):
        if not self.linkable:
            return SPAN()
        d = DIV(
              A(
                SPAN(
                  T('Link'),
                  _title=T("Share your view using this hyperlink"),
                  _class='link16',
                  _id='link_'+self.id,
                ),
              DIV(
                TEXTAREA(
                ),
                _class='white_float hidden',
                _id='link_val_'+self.id,
              ),
                _class='floatw',
              ),
            )
        return d

    def refresh(self):
        if not self.refreshable:
            return SPAN()
        url = URL(r=request,f=self.func)
        d = DIV(
              A(
                SPAN(
                  T('Refresh'),
                  _class='refresh16',
                  _id='refresh_'+self.id,
                ),
                _class='floatw',
              ),
            )
        return d

    def commonality(self):
        if not self.commonalityable:
            return SPAN()
        d = DIV(
              A(
                T("Commonality"),
                _class="common16",
                _onclick="""click_toggle_vis(event, '%(div)s','block');ajax('%(url)s', [], '%(div_d)s')"""%dict(
                  url=URL(r=request,f=self.func, args=["commonality"]),
                  div="commonality"+self.id,
                  div_d="commonality_d"+self.id,
                ),
              ),
              DIV(
                DIV(
                  _id='commonality_d'+self.id,
                ),
                _name='commonality'+self.id,
                _class='white_float',
                _style='max-width:50%;display:none;',
              ),
              _class='floatw',
           )
        return d

    def bookmark(self):
        if not self.bookmarkable:
            return SPAN()
        q = db.column_filters.user_id == auth.user_id
        q &= db.column_filters.col_tableid == self.id
        q &= db.column_filters.bookmark != "current"
        rows = db(q).select(cacheable=True,
                            groupby=db.column_filters.bookmark,
                            orderby=db.column_filters.bookmark)
        d = DIV(
              A(
                T("Save current filters as bookmark"),
                _class="bookmark_add16",
                _onclick="""click_toggle_vis(event, '%(div)s','block');"""%dict(
                  div="bookmark_name"+self.id,
                ),
              ),
              DIV(
                DIV(
                  T("Enter new bookmark name"),
                  _style='white-space: nowrap;',
                ),
                INPUT(
                  _value=str(datetime.datetime.now()),
                  _id='bookmark_name_input'+self.id,
                ),
                _name='bookmark_name'+self.id,
                _class='white_float',
                _style='display:none;',
              ),
            )
        l = [d, HR()]
        if len(rows) == 0:
            l.append(T("No saved bookmarks"))
        else:
            for row in rows:
                d = P(
                      A(
                        row.bookmark,
                        _class="bookmark16",
                        _name="bookmark",
                      ),
                      A(
                        _class="del16",
                        _style="float:right;",
                      ),
                    )
                l.append(d)


        d = DIV(
              A(
                T("Bookmarks"),
                _class="bookmark16",
                _onclick="""click_toggle_vis(event, '%(div)s','block');"""%dict(
                  div="bookmarks"+self.id,
                ),
              ),
              DIV(
                SPAN(l),
                _name='bookmarks'+self.id,
                _class='white_float',
                _style='max-width:50%;display:none;',
              ),
              _class='floatw',
            )
        return d

    def pager_info(self):
        d = {
          'perpage': self.perpage,
          'total': self.totalrecs,
          'start': self.pager_start,
          'end': self.pager_end,
          'page': self.page,
        }
        return d

    def _table_lines_data_html(self):
        return TABLE(self.table_lines()[0]).xml()

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
            if not self.checkboxes:
                checked = False
            else:
                checked = getattr(request.vars, self.checkbox_key(line))
                if checked is None or checked == 'false':
                    checked = False
                else:
                    checked = True

            _l = []
            if self.extrarow:
                _l.append(self.format_extrarow(line))
            for c in self.cols:
                v = self.colprops[c].get(line)
                if type(v) == datetime.datetime:
                    try:
                        v = v.strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        v = str(v)
                elif v is None:
                    v = 'empty'
                _l.append(v)
                if c in self.keys:
                    cksum.update(str(v))
                if c in self.span:
                    spansum.update(str(v))
            l.append({
              'id': self.line_id(line),
              'checked': str(checked).lower(),
              'cksum': cksum.hexdigest() if cksum else '',
              'spansum': spansum.hexdigest() if spansum else '',
              'cells': _l,
            })
        return l

    def table_lines_data(self, n=0, html=True):
        wsenabled = self.get_wsenabled()
        if wsenabled == 'on' and self.perpage > self.max_live_perpage:
            max_perpage = self.max_live_perpage
        else:
            max_perpage = 500
        self.setup_pager(n, max_perpage=max_perpage)
        self.set_column_visibility()
        if html:
            fmt = "html"
            formatter = self._table_lines_data_html
        else:
            fmt = "json"
            formatter = self._table_lines_data
        d = {
          'format': fmt,
          'wsenabled': wsenabled,
          'pager': self.pager_info(),
          'table_lines': formatter(),
        }
        return json.dumps(d)

    def pager(self):
        if not self.pageable:
            return SPAN()

        nav = DIV(_class='pager floatw')

        return nav

    def col_checkbox_key(self, f):
        return '_'.join((self.id, 'cc', f))

    def col_selector_key(self):
        return '_'.join((self.id, 'cs'))

    def col_key(self, f):
        return '_'.join((self.id, 'c', f))

    def filter_key(self, f):
        return '_'.join((self.id, 'f', f))

    def filter_div_key(self, f):
        return '_'.join((self.id, 'fd', f))

    def filter_cloud_key(self, f):
        return '_'.join((self.id, 'fc', f))

    def line_id(self, o):
        if o is None:
            return ''
        if self.checkbox_id_table is None or \
           self.checkbox_id_table not in o:
            return o[self.checkbox_id_col]
        else:
            return o[self.checkbox_id_table][self.checkbox_id_col]

    def span_line_id(self, o):
        if o is None:
            return ''
        spansum = hashlib.md5()
        for c in self.span:
            v = self.colprops[c].get(o)
            spansum.update(str(v))
        return spansum.hexdigest()

    def extra_line_key(self, o):
        if len(self.span) > 0:
            id = str(self.span_line_id(o))
        else:
            id = str(self.line_id(o))
        id = id.replace('.','_').replace(',','_').replace('-', '_')
        return '_'.join((self.id, 'x', id))

    def checkbox_key(self, o):
        id = self.line_id(o)
        return '_'.join((self.id, 'ckid', str(id)))

    def checkbox_name_key(self):
        return '_'.join((self.id, 'ck'))

    def master_checkbox_key(self):
        return '_'.join((self.id, 'mck'))

    def get_checked(self):
        prefix = self.checkbox_key(None)
        ids = []
        for key in [ k for k in request.vars.keys() if prefix in k and request.vars[k] == 'true' ]:
            try:
                ids.append(int(key.replace(prefix, '')))
            except:
                ids.append(key.replace(prefix, ''))
        return ids

    def stored_filter_field(self, f):
        if f not in self.colprops:
            return None
        cp = self.colprops[f]
        if not hasattr(cp, 'table') and not hasattr(cp, 'field'):
            return None
        if not hasattr(cp, 'table') or cp.table is None:
            return cp.field
        return '.'.join((cp.table, cp.field))

    def drop_filters(self, bookmark="current"):
        if request.vars.dbfilter is not None:
            select_filter(request.vars.dbfilter)
        if request.vars.clear_filters != 'true':
            return
        q = db.column_filters.col_tableid==self.id
        q &= db.column_filters.user_id==session.auth.user.id
        q &= db.column_filters.bookmark==bookmark
        db(q).delete()

    def drop_filter_value(self, f, bookmark="current"):
        field = self.stored_filter_field(f)
        if field is None:
            return
        q = db.column_filters.col_tableid==self.id
        q &= db.column_filters.col_name==field
        q &= db.column_filters.user_id==session.auth.user.id
        q &= db.column_filters.bookmark==bookmark
        db(q).delete()

    def store_filter_value(self, f, v, bookmark="current"):
        if request.vars.volatile_filters is not None:
            return
        field = self.stored_filter_field(f)
        if field is None:
            return
        q = db.column_filters.col_tableid==self.id
        q &= db.column_filters.col_name==field
        q &= db.column_filters.user_id==session.auth.user.id
        q &= db.column_filters.bookmark==bookmark
        try:
            db.column_filters.insert(col_tableid=self.id,
                                     col_name=field,
                                     col_filter=v,
                                     bookmark=bookmark,
                                     user_id=session.auth.user.id)
        except:
            db(q).update(col_filter=v)

    def stored_filter_value(self, f, bookmark="current"):
        field = self.stored_filter_field(f)
        if field is None:
            return ""
        q = db.column_filters.col_tableid==self.id
        q &= db.column_filters.col_name==field
        q &= db.column_filters.user_id==session.auth.user.id
        q &= db.column_filters.bookmark==bookmark
        rows = db(q).select(cacheable=True)
        if len(rows) == 0:
            return ""
        return rows[0].col_filter

    def filter_parse(self, f):
        v = self._filter_parse(f)
        if v == self.column_filter_reset:
            self.drop_filter_value(f)
            key = self.filter_key(f)
            del(request.vars[key])
            return ""
        if request.vars.volatile_filters:
            _v = self.stored_filter_value(f)
            if _v != "" and v != "":
                return v+"&"+_v
            if v == "":
                return _v
            return v
        if v == "":
            return self.stored_filter_value(f)
        self.store_filter_value(f, v)
        if v == "" and self.colprops[f].default_filter is not None:
            v = self.colprops[f].default_filter
        return v

    def _filter_parse(self, f):
        key = self.filter_key(f)
        if key in request.vars:
            v = request.vars[key]
            if v == "**clear**" and self.colprops[f].default_filter:
                return self.colprops[f].default_filter
            if v == "":
                if self.colprops[f].default_filter is not None:
                    return self.colprops[f].default_filter
                return "**clear**"
            return v
        return ""

    def filter_parse_glob(self, f):
        val = self.filter_parse(f)
        return val

    def ajax_inputs(self):
        l = ['tableid']
        if self.pageable:
            l.append(self.id_perpage)
            l.append(self.id_page)
        if self.filterable:
            l += map(self.filter_key, self.cols+self.additional_filters)
        return l

    def table_header(self):
        cells = []
        if self.checkboxes:
            cells.append(TH(''))
        if self.extrarow:
            cells.append(TD(''))
        for c in self.cols:
            cells.append(TH(T(self.colprops[c].title),
                            _class=self.colprops[c]._class,
                            _name=self.col_key(c)))
        return TR(cells, _class='theader')

    def format_extrarow(self, o):
        return ""

    def table_line(self, o):
        cells = []
        cl = ""
        if self.checkboxes:
            if hasattr(self, 'checkbox_disabled') and \
               self.checkbox_disabled(o):
                cells.append(TD(
                               INPUT(
                                 _type='checkbox',
                                 _disabled='disabled',
                               ),
                             ))
            else:
                checked = getattr(request.vars, self.checkbox_key(o))
                if checked is None or checked == 'false':
                    checked = False
                    value = 'false'
                else:
                    checked = True
                    value = 'true'
                checkbox_id = self.checkbox_key(o)
                cells.append(TD(
                               INPUT(
                                 _type='checkbox',
                                 _id=checkbox_id,
                                 _name=self.checkbox_name_key(),
                                 _value=value,
                                 value=checked,
                               ),
                             ))

        if self.extrarow:
            xrow_attrs = dict(_cell=1)
            if self.extrarow_class:
                xrow_attrs['_class'] = self.extrarow_class
            cells.append(TD(self.format_extrarow(o), **xrow_attrs))

        if len(self.keys) > 0:
            cksum = hashlib.md5()
        else:
            cksum = None
        for c in self.cols:
            colprops = self.colprops[c]
            if self.spaning_cell(c, o):
                content = ''
            else:
                content = colprops.html(o)
            v = colprops.get(o)
            if v is None:
                v = 'empty'
            if c in self.keys:
                cksum.update(str(v))
            attrs = dict(
               _name=self.col_key(c),
               _v=v,
               _cell=1,
            )
            classes = []
            if colprops._class != "":
                classes.append(colprops._class)
            if colprops._dataclass != "":
                classes.append(colprops._dataclass)
            if len(classes) > 0:
                attrs['_class'] = ' '.join(classes)
            cells.append(TD(content, **attrs))
            cl = "tl"
            if self.highlight:
                cl += " h"
        line_attrs = dict(
          _class = cl,
          _spansum = self.span_line_id(o),
        )
        if cksum:
            line_attrs["_cksum"] = cksum.hexdigest()
        return TR(cells, **line_attrs)

    def spaning_line(self, o):
        if len(self.span) > 0 and \
           self.last is not None and \
           self.span_line_id(o) == self.span_line_id(self.last):
            return True
        return False

    def spaning_cell(self, c, o):
        if not self.spaning_line(o):
           return False
        if c in self.span:
            return True
        return False

    def table_lines(self):
        lines = []
        line_count = 0

        if hasattr(self, 'sort_objects'):
            if isinstance(self.object_list, list):
                object_list = self.object_list.sort(self.sort_objects)
            elif isinstance(self.object_list, dict):
                object_list = self.object_list.keys()
                object_list.sort(self.sort_objects)
        else:
            object_list = self.object_list

        if request.vars.volatile_filters is None and self.nodatabanner and len(object_list) == 0:
            lines.append(TR(TD(T("no data"), _colspan=len(self.cols)), _class="tl nodataline"))
            return lines, 0

        for i in object_list:
            if isinstance(i, str) or isinstance(i, unicode) or isinstance(i, int):
                o = self.object_list[i]
            else:
                o = i
            self.change_line_data(o)
            if hasattr(self, 'filter'):
                skip = False
                for c in self.cols+self.additional_filters:
                    if not _filter(self.filter_parse(c), self.colprops[c].get(o)):
                        skip = True
                        break
                if skip:
                    continue
            line_count += 1
            if not self.pageable or self.perpage == 0 or line_count <= self.perpage:
                lines.append(self.table_line(o))
                self.last = o
        return lines, line_count

    def header_slim(self):
        inputs = []
        if self.checkboxes:
            inputs.append(TD(''))
        if self.extrarow:
            inputs.append(TD(''))
        for c in self.cols:
            inputs.append(
              TD(
                '',
                 _name=self.col_key(c),
              ),
            )
        return TR(
          inputs,
          _class='theader_slim',
          _onclick="""$(".sym_headers").toggle()"""
        )

    def table_inputs(self):
        inputs = []
        if self.checkboxes:
            inputs.append(TD(
                            INPUT(
                              _type='checkbox',
                              _id=self.master_checkbox_key(),
                              _onclick="check_all('%(name)s', this.checked);"%dict(name=self.checkbox_name_key())
                            )
                          ))
        if self.extrarow:
            inputs.append(TD(''))
        for c in self.cols:
            filter_text = self.filter_parse(c)
            inputs.append(TD(
                            DIV(
                              INPUT(
                                _id=self.filter_key(c),
                                _name="fi",
                                _value=self.filter_parse(c),
                              ),
                            ),
                            _name=self.col_key(c),
                            _class=self.colprops[c]._class,
                          ))
        return TR(inputs, _class='sym_headers')

    def table_additional_inputs(self):
        inputs = []
        for c in self.additional_filters:
            inputs.append(INPUT(
                    _id=self.filter_key(c),
                    _value=self.filter_parse(c),
                    _onKeyPress="ajax_enter_submit_%s(event)"%self.id,
                  ))
        return inputs

    def ajax_submit(self, args=[], vars={}, additional_inputs=[], additional_input_name=None):
        return """table_ajax_submit('%(url)s', '%(divid)s', %(additional_inputs)s, %(input_name)s, "%(additional_input_name)s");"""%dict(
                         url=URL(r=request,f=self.func, args=args, vars=vars),
                         divid=self.innerhtml,
                         id=self.id,
                         additional_inputs = str(additional_inputs+self.additional_inputs),
                         input_name=str(self.checkbox_names),
                         additional_input_name = str(additional_input_name),
                        )

    def ajax_enter_submit(self, args=[], additional_inputs=[]):
        return """if (is_enter(event)){clearTimeout(timer);$("#tableid").val("%(id)s");%(ajax)s};"""%dict(
                 ajax=self.ajax_submit(args=args,
                                       additional_inputs=additional_inputs),
                 id=self.id)

    def show_flash(self):
        if self.flash is None:
            return SPAN()
        d = DIV(
              self.flash,
              _class='tableo_flash',
              _onclick="this.style['display']='none';"
            )
        return d

    def get_wsenabled(self):
        if hasattr(self, "wsenabled"):
            return self.wsenabled
        q = db.user_prefs_columns.upc_table == self.upc_table
        q &= db.user_prefs_columns.upc_field == "wsenabled"
        q &= db.user_prefs_columns.upc_user_id == auth.user_id
        row = db(q).select(db.user_prefs_columns.upc_visible, cacheable=False).first()
        if row is None or row.upc_visible == 1:
            self.wsenabled = 'on'
        else:
            self.wsenabled = ''
        return self.wsenabled

    def wsswitch(self):
        if not self.wsable:
            return SPAN()
        wsenabled = self.get_wsenabled()
        js ="""ajax("%(url)s/%(table)s/wsenabled/"+this.checked, [], "set_col_dummy"); if (osvc.tables["%(id)s"].need_refresh) {osvc.tables["%(id)s"].refresh()};
            """%dict(url=URL(r=request,c='ajax',f='ajax_set_user_prefs_column2'),
                     table=self.upc_table,
                     id=self.id,
                    )
        d = DIV(
          INPUT(
            _type="checkbox",
            _id="wsswitch_"+self.id,
            _onclick=js,
            value=wsenabled,
          ),
          T("Live"),
          _class='floatw'
        )
        return d

    def html(self):
        if len(request.args) == 1 and request.args[0] == 'commonality':
            return self.do_commonality()
        if len(request.args) == 1 and request.args[0] == 'csv':
            return self.csv()

        self.set_column_visibility()
        lines, line_count = self.table_lines()

        if self.filterable:
            inputs = self.table_inputs()
        else:
            inputs = None

        if self.filterable and len(self.additional_filters) > 0:
            additional_filters = DIV(
              B(T('Additional filters')),
              TABLE(
                TR(map(TH, self.additional_filters)),
                TR(map(TD, self.table_additional_inputs())),
              ),
              _class='sym_highlight',
              _style='margin-bottom:6px',
            )
        else:
            additional_filters = SPAN()

        if not self.hide_tools:
            atl = []
            for o in self.additional_tools:
                if isinstance(o, HtmlTableMenu):
                    atl.append(o.html())
                else:
                    atl.append(getattr(self, o)())
            additional_tools = SPAN(atl)
        else:
            additional_tools = SPAN()

        if self.exportable:
            args = ['csv']
            if hasattr(self, 'csv_extra_args') and type(self.csv_extra_args):
                args += self.csv_extra_args
            export = DIV(
                  A(
                    SPAN(
                      T('Export to csv'),
                      _class='csv',
                    ),
                    _href=URL(
                            r=request,
                            f=self.func,
                            vars=request.vars,
                            args=args
                          ),
                    _onclick="""$(this).hide();$("#csv%(id)s").show()"""%dict(id=self.id),
                  ),
                  DIV(
                    SPAN(
                      T('Export to csv'),
                      _class='csv_disabled',
                    ),
                    _style="display:none",
                    _id="csv"+self.id,
                  ),
                  _class='floatw',
                )
        else:
            export = SPAN()

        table_lines = []
        if self.headers:
            table_lines.append(self.table_header())

        if self.headers and inputs is not None:
            table_lines.append(inputs)
            table_lines.append(self.header_slim())

        if len(lines) > 0:
            table_lines += lines

        table_attrs = dict(
          _id="table_"+self.id,
          _order=",".join(self.order),
          _pager_perpage=self.perpage,
          _pager_page=self.page,
          _pager_start=self.pager_start,
          _pager_end=self.pager_end,
          _pager_total=self.totalrecs,
        )
        d = DIV(
              self.show_flash(),
              DIV(
                self.pager(),
                self.wsswitch(),
                self.refresh(),
                self.link(),
                self.bookmark(),
                export,
                self.columns_selector(),
                self.commonality(),
                self.persistent_filters(),
                additional_tools,
                DIV('', _class='spacer'),
                _class='theader',
              ),
              additional_filters,
              DIV(
                TABLE(
                   table_lines,
                   **table_attrs
                ),
              ),
              DIV(
                INPUT(
                  _id=self.id_perpage,
                  _type='hidden',
                  _value=self.perpage,
                ),
                INPUT(
                  _id=self.id_page,
                  _type='hidden',
                  _value=self.page,
                ),
              ),
              DIV(XML('&nbsp;'), _class='spacer'),
              SCRIPT(
                """
table_init({
 'id': '%(id)s',
 'extrarow': %(extrarow)s,
 'extrarow_class': "%(extrarow_class)s",
 'checkboxes': %(checkboxes)s,
 'ajax_url': '%(ajax_url)s',
 'span': %(span)s,
 'columns': %(columns)s,
 'colprops': %(colprops)s,
 'visible_columns': %(visible_columns)s,
 'child_tables': %(child_tables)s,
 'dataable': %(dataable)s
})
function ajax_submit_%(id)s(){%(ajax_submit)s};
function ajax_enter_submit_%(id)s(event){%(ajax_enter_submit)s};
"""%dict(
                   id=self.id,
                   extrarow=str(self.extrarow).lower(),
                   extrarow_class=self.extrarow_class if self.extrarow_class else "",
                   checkboxes=str(self.checkboxes).lower(),
                   ajax_url=URL(r=request,f=self.func),
                   a=self.ajax_inputs(),
                   span=str(self.span),
                   columns=str(self.cols),
                   colprops=self.serialize_colprops(),
                   visible_columns=str(self.visible_columns()),
                   child_tables=str(self.child_tables),
                   ajax_submit=self.ajax_submit(),
                   ajax_enter_submit=self.ajax_enter_submit(),
                   dataable=str(self.dataable).lower(),
                ),
              ),
              _class='tableo',
            )
        return d

    def serialize_colprops(self):
        data = {}
        for k, cp in self.colprops.items():
            data[k] = cp.as_dict()
        return str(data)

    def change_line_data(self, o):
        pass

    def csv_object_list(self):
        if self.csv_q is None:
            return self.object_list
        if self.csv_left is None:
            if self.csv_orderby is None:
                return db(self.csv_q).select(cacheable=True, limitby=(0,self.csv_limit))
            else:
                return db(self.csv_q).select(cacheable=True, orderby=self.csv_orderby, limitby=(0,self.csv_limit))
        else:
            if self.csv_orderby is None:
                return db(self.csv_q).select(cacheable=True, limitby=(0,self.csv_limit), left=self.csv_left)
            else:
                return db(self.csv_q).select(cacheable=True, orderby=self.csv_orderby, limitby=(0,self.csv_limit), left=self.csv_left)

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
        def fancypct(p):
            p = "%d%%"%int(p)
            d = DIV(
                  DIV(
                    DIV(
                      _style="""font-size: 0px;
                                line-height: 0px;
                                height: 4px;
                                min-width: 0%%;
                                max-width: %(p)s;
                                width: %(p)s;
                                background: #A6FF80;
                             """%dict(p=p),
                    ),
                    _style="""text-align: left;
                              margin: 2px auto;
                              background: #FF7863;
                              overflow: hidden;
                           """,
                  ),
                  DIV(p),
                  _style="""margin: auto;
                            text-align: center;
                            width: 100%;
                         """,
                ),
            return d

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
            l.sort(lambda x, y: cmp(x[1], y[1]), reverse=True)
            v, n = l[0]
            pct = 100*n//total
            if pct == 0 or n == 1:
                continue
            top.append((col, v, pct))
        top.sort(lambda x, y: cmp(x[2], y[2]), reverse=True)

        l = [TR(
               TH(T("Percent")),
               TH(T("Column")),
               TH(T("Value")),
            )]
        for col, v, pct in top:
            line = TR(
               TD(fancypct(pct)),
               TD(DIV(T(self.colprops[col].title), _class=self.colprops[col].img)),
               TD(v),
            )
            l.append(line)
        return TABLE(SPAN(l))

    def int_match(self, value, num):
        if len(value) == 0:
            return True
        if not isinstance(num, int):
            return False

        negate = False
        inf = False
        sup = False
        inf_e = False
        sup_e = False

        if value[0] == '!':
            negate = True
            value = value[1:]
        if value[0] == '<':
            if len(value) > 2 and value[1] == '=':
                inf_e = True
                value = value[2:]
            else:
                inf = True
                value = value[1:]
        elif value[0] == '>':
            if len(value) > 2 and value[1] == '=':
                sup_e = True
                value = value[2:]
            else:
                sup = True
                value = value[1:]
        try:
            v = int(value)
        except:
            return self.str_match(value, str(num))

        if sup:
            if num > v:
                r = True
            else:
                r = False
        elif inf:
            if num < v:
                r = True
            else:
                r = False
        elif sup_e:
            if num >= v:
                r = True
            else:
                r = False
        elif inf_e:
            if num <= v:
                r = True
            else:
                r = False
        elif num == v:
            r = True
        else:
            r = False

        if negate:
            return not r
        else:
            return r

    def str_match(self, value, text):
        negate = False
        if len(value) == 0:
            return True
        if value[0] == '!':
            negate = True
            value = value[1:]
        if value == "empty":
            if text == "":
                r = True
            else:
                r = False
        else:
            reg = value.replace('%', '.*')
            if reg[-1] != '$':
                reg = reg+'$'
            r = re.match(reg, text)
            if r is None:
                r = False
            else:
                r = True
        if negate:
            return not r
        else:
            return r

    def str_match_in_list(self, value, l):
        if value == 'empty':
            if len(l) == 0:
                return True
            else:
                return False
        elif value == '!empty':
            if len(l) == 0:
                return False
            else:
                return True
        if len(value) == 0 and len(l) == 0:
            return True
        for i in l:
            if self.str_match(value, i):
                return True
        return False

    def _match(self, value, o):
        if isinstance(o, str) or isinstance(o, unicode):
            return self.str_match(value, o)
        elif isinstance(o, list):
            return self.str_match_in_list(value, o)
        elif isinstance(o, int):
            return self.int_match(value, o)
        return False

    def match(self, value, o):
        if '&' in value:
            for v in value.split('&'):
                if not self.match(v, o):
                    return False
            return True
        elif '|' in value:
            for v in value.split('|'):
                if self.match(v, o):
                    return True
            return False
        else:
            return self._match(value, o)

    def match_col(self, value, o, f):
        return self.match(value, self.colprops[f].get(o))

    def get_visible_columns(self, fmt="dal", force=[]):
        visible_columns = request.vars.visible_columns.split(',')
        visible_columns = list(set(visible_columns)|set(force)|set(self.force_cols))
        sorted_visible_columns = []
        for c in self.cols:
            if c in visible_columns:
                cp = self.colprops[c]
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
        if self.checkbox_id_col and self.checkbox_id_table:
            if fmt == "dal":
                id_col = db[self.checkbox_id_table][self.checkbox_id_col]
            elif fmt == "sql":
                id_col = self.checkbox_id_table+'.'+self.checkbox_id_col
            sorted_visible_columns = [id_col] + sorted_visible_columns

        return sorted_visible_columns

#
# common column formatting
#
action_img_h = {
    'checks': 'check16.png',
    'enable': 'check16.png',
    'disable': 'nok.png',
    'pushservices': 'svc.png',
    'pushpkg': 'pkg16.png',
    'pushpatch': 'pkg16.png',
    'reboot': 'action_restart_16.png',
    'shutdown': 'action_stop_16.png',
    'syncservices': 'action_sync_16.png',
    'updateservices': 'action16.png',
    'updatepkg': 'pkg16.png',
    'updatecomp': 'pkg16.png',
    'stop': 'action_stop_16.png',
    'stopapp': 'action_stop_16.png',
    'stopdisk': 'action_stop_16.png',
    'stopvg': 'action_stop_16.png',
    'stoploop': 'action_stop_16.png',
    'stopip': 'action_stop_16.png',
    'stopfs': 'action_stop_16.png',
    'umount': 'action_stop_16.png',
    'shutdown': 'action_stop_16.png',
    'boot': 'action_start_16.png',
    'start': 'action_start_16.png',
    'startstandby': 'action_start_16.png',
    'startapp': 'action_start_16.png',
    'startdisk': 'action_start_16.png',
    'startvg': 'action_start_16.png',
    'startloop': 'action_start_16.png',
    'startip': 'action_start_16.png',
    'startfs': 'action_start_16.png',
    'mount': 'action_start_16.png',
    'restart': 'action_restart_16.png',
    'provision': 'prov.png',
    'switch': 'action_restart_16.png',
    'freeze': 'frozen16.png',
    'thaw': 'frozen16.png',
    'syncall': 'action_sync_16.png',
    'syncnodes': 'action_sync_16.png',
    'syncdrp': 'action_sync_16.png',
    'syncfullsync': 'action_sync_16.png',
    'postsync': 'action_sync_16.png',
    'push': 'log16.png',
    'check': 'check16.png',
    'fixable': 'fixable16.png',
    'fix': 'comp16.png',
    'pushstats': 'spark16.png',
    'pushasset': 'node16.png',
    'stopcontainer': 'action_stop_16.png',
    'startcontainer': 'action_start_16.png',
    'stopapp': 'action_stop_16.png',
    'startapp': 'action_start_16.png',
    'prstop': 'action_stop_16.png',
    'prstart': 'action_start_16.png',
    'push': 'svc.png',
    'syncquiesce': 'action_sync_16.png',
    'syncresync': 'action_sync_16.png',
    'syncupdate': 'action_sync_16.png',
    'syncverify': 'action_sync_16.png',
    'toc': 'action_toc_16.png',
    'stonith': 'action_stonith_16.png',
    'switch': 'action_switch_16.png',
}

os_class_h = {
  'darwin': 'os_darwin',
  'linux': 'os_linux',
  'hp-ux': 'os_hpux',
  'osf1': 'os_tru64',
  'opensolaris': 'os_opensolaris',
  'solaris': 'os_solaris',
  'sunos': 'os_solaris',
  'freebsd': 'os_freebsd',
  'aix': 'os_aix',
  'windows': 'os_win',
  'vmware': 'os_vmware',
}

def node_class(os_name):
    if os_name is None:
        return ''
    os_name = os_name.lower()
    if os_name in os_class_h:
        return os_class_h[os_name]
    return ''

now = datetime.datetime.now()

class col_containertype(HtmlTableColumn):
    def html(self, o):
        id = self.t.extra_line_key(o)
        s = self.get(o)
        os = self.t.colprops['mon_guestos'].get(o)
        if (os is None or len(os) == 0):
            key = None
            # TODO: add vmtype icons ?
            if 'os_name' in self.t.cols:
                key = 'os_name'
            if key is not None:
                os = self.t.colprops[key].get(o)
        d = DIV(
              A(
                s,
                _onclick="toggle_extra('%(url)s', '%(id)s', this, %(ncols)s);"%dict(
                  url=URL(r=request, c='ajax_node',f='ajax_node',
                          vars={'node': self.t.colprops['mon_vmname'].get(o),
                                'rowid': id}),
                  id=id,
                  ncols=len(self.t.cols),
                ),
              ),
              _class=' '.join((node_class(os), 'nowrap')),
            )
        return d

class col_vcpus(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        c = ''
        if s > 0:
            c = s
        return SPAN(c, _class=c)

class col_vmem(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        c = ''
        if s > 0:
            c = s
        return SPAN(c, _class=c)

#
# colprops definitions
#
v_nodes_cols = [
    'assetname',
    'fqdn',
    'loc_country',
    'loc_zip',
    'loc_city',
    'loc_addr',
    'loc_building',
    'loc_floor',
    'loc_room',
    'loc_rack',
    'sec_zone',
    'os_name',
    'os_release',
    'os_vendor',
    'os_arch',
    'os_kernel',
    'cpu_dies',
    'cpu_cores',
    'cpu_threads',
    'cpu_model',
    'cpu_freq',
    'mem_banks',
    'mem_slots',
    'mem_bytes',
    'listener_port',
    'version',
    'team_responsible',
    'team_integ',
    'team_support',
    'project',
    'serial',
    'model',
    'enclosure',
    'enclosureslot',
    'hvvdc',
    'hvpool',
    'hv',
    'role',
    'host_mode',
    'environnement',
    'status',
    'type',
    'warranty_end',
    'maintenance_end',
    'os_obs_warn_date',
    'os_obs_alert_date',
    'hw_obs_warn_date',
    'hw_obs_alert_date',
    'updated',
    'power_supply_nb',
    'power_cabinet1',
    'power_cabinet2',
    'power_protect',
    'power_protect_breaker',
    'power_breaker1',
    'power_breaker2'
]

v_services_cols = [
    'svc_status',
    'svc_availstatus',
    'svc_app',
    'svc_type',
    'svc_ha',
    'svc_cluster_type',
    'svc_flex_min_nodes',
    'svc_flex_max_nodes',
    'svc_flex_cpu_low_threshold',
    'svc_flex_cpu_high_threshold',
    'svc_drptype',
    'svc_containertype',
    'svc_autostart',
    'svc_nodes',
    'svc_drpnode',
    'svc_drpnodes',
    'svc_comment',
    'svc_created',
    'svc_updated',
]

svcmon_cols = [
    'mon_vmname',
    'mon_vmtype',
    'mon_guestos',
    'mon_vcpus',
    'mon_vmem',
    'mon_overallstatus',
    'mon_availstatus',
    'mon_updated',
    'mon_changed',
    'mon_frozen',
    'mon_containerstatus',
    'mon_ipstatus',
    'mon_fsstatus',
    'mon_diskstatus',
    'mon_sharestatus',
    'mon_syncstatus',
    'mon_appstatus',
    'mon_hbstatus'
]

v_services_colprops = {
    'svc_name': HtmlTableColumn(
             title = 'Service',
             field='svc_name',
             display = False,
             img = 'svc',
             table = 'v_services',
             _class='svcname',
            ),
    'svc_hostid': HtmlTableColumn(
             title = 'Host id',
             field='svc_hostid',
             display = False,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_wave': HtmlTableColumn(
             title = 'Drp wave',
             field='svc_wave',
             display = False,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_availstatus': HtmlTableColumn(
             title = 'Service availability status',
             field='svc_availstatus',
             display = True,
             img = 'svc',
             table = 'v_services',
             _class = 'status',
            ),
    'svc_status': HtmlTableColumn(
             title = 'Service overall status',
             field='svc_status',
             display = True,
             img = 'svc',
             table = 'v_services',
             _class = 'status',
            ),
    'svc_app': HtmlTableColumn(
             title = 'App',
             field='svc_app',
             display = False,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_ha': HtmlTableColumn(
             title = 'HA',
             field='svc_ha',
             display = True,
             img = 'svc',
             table = 'v_services',
             _class = 'svc_ha',
            ),
    'svc_containertype': HtmlTableColumn(
             title = 'Service mode',
             field='svc_containertype',
             display = False,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_type': HtmlTableColumn(
             title = 'Service type',
             field='svc_type',
             display = False,
             img = 'svc',
             table = 'v_services',
             _class = 'env',
            ),
    'svc_autostart': HtmlTableColumn(
             title = 'Primary node',
             field='svc_autostart',
             display = False,
             img = 'svc',
             table = 'v_services',
             _class = 'svc_autostart',
            ),
    'svc_nodes': HtmlTableColumn(
             title = 'Nodes',
             field='svc_nodes',
             display = False,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_drpnode': HtmlTableColumn(
             title = 'DRP node',
             field='svc_drpnode',
             display = False,
             img = 'svc',
             table = 'v_services',
             _class = 'nodename_no_os',
            ),
    'svc_drpnodes': HtmlTableColumn(
             title = 'DRP nodes',
             field='svc_drpnodes',
             display = False,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_drptype': HtmlTableColumn(
             title = 'DRP type',
             field='svc_drptype',
             display = False,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_comment': HtmlTableColumn(
             title = 'Comment',
             field='svc_comment',
             display = False,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_created': HtmlTableColumn(
             title = 'Service creation date',
             field='svc_created',
             display = False,
             img = 'time16',
             table = 'v_services',
            ),
    'svc_updated': HtmlTableColumn(
             title = 'Last service update',
             field='updated',
             display = False,
             img = 'time16',
             table = 'v_services',
             _class = 'datetime_daily',
            ),
    'responsibles': HtmlTableColumn(
             title = 'Responsibles',
             field='responsibles',
             display = False,
             img = 'guy16',
             table = 'v_services',
            ),
    'mailto': HtmlTableColumn(
             title = 'Responsibles emails',
             field='mailto',
             display = False,
             img = 'guy16',
             table = 'v_services',
            ),
    'svc_cluster_type': HtmlTableColumn(
             title = 'Cluster type',
             field='svc_cluster_type',
             display = True,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_flex_min_nodes': HtmlTableColumn(
             title = 'Flex min nodes',
             field='svc_flex_min_nodes',
             display = False,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_flex_max_nodes': HtmlTableColumn(
             title = 'Flex max nodes',
             field='svc_flex_max_nodes',
             display = False,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_flex_cpu_low_threshold': HtmlTableColumn(
             title = 'Flex cpu low threshold',
             field='svc_flex_cpu_low_threshold',
             display = False,
             img = 'spark16',
             table = 'v_services',
            ),
    'svc_flex_cpu_high_threshold': HtmlTableColumn(
             title = 'Flex cpu high threshold',
             field='svc_flex_cpu_high_threshold',
             display = False,
             img = 'spark16',
             table = 'v_services',
            ),
    'svc_envfile': HtmlTableColumn(
             title = 'Env file',
             field='svc_envfile',
             display = False,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_envdate': HtmlTableColumn(
             title = 'Env file date',
             field='svc_envdate',
             display = False,
             img = 'time16',
             table = 'v_svcmon',
            ),
}

v_svcmon_colprops = {
    'err': HtmlTableColumn(
             title = 'Action errors',
             field='err',
             display = False,
             img = 'action16',
             table = 'v_svcmon',
             _class = 'svc_action_err',
            ),
}

svcmon_colprops = {
    'mon_containerpath': HtmlTableColumn(
             title = 'Container path',
             field='mon_containerpath',
             display = False,
             img = 'svc',
             table = 'svcmon',
            ),
    'mon_svcname': HtmlTableColumn(
             title = 'Service',
             field='mon_svcname',
             display = False,
             img = 'svc',
             table = 'svcmon',
             _class = 'svcname',
            ),
    'mon_nodname': HtmlTableColumn(
             title = 'Node',
             field='mon_nodname',
             display = False,
             img = 'node16',
             table = 'svcmon',
             _class = 'nodename',
            ),
    'mon_svctype': HtmlTableColumn(
             title = 'Service type',
             field='mon_svctype',
             display = False,
             img = 'svc',
             table = 'svcmon',
             _class = 'env',
            ),
    'mon_overallstatus': HtmlTableColumn(
             title = 'Status',
             field='mon_overallstatus',
             display = False,
             img = 'svc',
             table = 'svcmon',
             _class='overallstatus',
            ),
    'mon_changed': HtmlTableColumn(
             title = 'Last status change',
             field='mon_changed',
             display = False,
             img = 'time16',
             table = 'svcmon',
            ),
    'mon_updated': HtmlTableColumn(
             title = 'Last status update',
             field='mon_updated',
             display = False,
             img = 'time16',
             table = 'svcmon',
             _class = 'datetime_daily',
            ),
    'mon_frozen': HtmlTableColumn(
             title = 'Frozen',
             field='mon_frozen',
             display = False,
             img = 'svc',
             table = 'svcmon',
            ),
    'mon_containerstatus': HtmlTableColumn(
             title = 'Container status',
             field='mon_containerstatus',
             display = False,
             img = 'svc',
             table = 'svcmon',
             _class="status",
            ),
    'mon_availstatus': HtmlTableColumn(
             title = 'Availability status',
             field='mon_availstatus',
             display = True,
             img = 'svc',
             table = 'svcmon',
             _class = 'availstatus',
            ),
    'mon_ipstatus': HtmlTableColumn(
             title = 'Ip status',
             field='mon_ipstatus',
             display = False,
             img = 'svc',
             table = 'svcmon',
             _class="status",
            ),
    'mon_fsstatus': HtmlTableColumn(
             title = 'Fs status',
             field='mon_fsstatus',
             display = False,
             img = 'svc',
             table = 'svcmon',
             _class="status",
            ),
    'mon_sharestatus': HtmlTableColumn(
             title = 'Share status',
             field='mon_sharestatus',
             display = False,
             img = 'svc',
             table = 'svcmon',
             _class="status",
            ),
    'mon_diskstatus': HtmlTableColumn(
             title = 'Disk status',
             field='mon_diskstatus',
             display = False,
             img = 'svc',
             table = 'svcmon',
             _class="status",
            ),
    'mon_syncstatus': HtmlTableColumn(
             title = 'Sync status',
             field='mon_syncstatus',
             display = False,
             img = 'svc',
             table = 'svcmon',
             _class="status",
            ),
    'mon_appstatus': HtmlTableColumn(
             title = 'App status',
             field='mon_appstatus',
             display = False,
             img = 'svc',
             table = 'svcmon',
             _class="status",
            ),
    'mon_hbstatus': HtmlTableColumn(
             title = 'Hb status',
             field='mon_hbstatus',
             display = False,
             img = 'svc',
             table = 'svcmon',
             _class="status",
            ),
    'mon_vmname': HtmlTableColumn(
             title = 'Container name',
             field='mon_vmname',
             display = True,
             img = 'svc',
             table = 'svcmon',
             _class = 'nodename_no_os',
            ),
    'mon_vmtype': HtmlTableColumn(
             title = 'Container type',
             field='mon_vmtype',
             display = True,
             img = 'svc',
             table = 'svcmon',
            ),
    'mon_vcpus': col_vcpus(
             title = 'Vcpus',
             field='mon_vcpus',
             display = False,
             img = 'svc',
             table = 'svcmon',
            ),
    'mon_vmem': col_vmem(
             title = 'Vmem',
             field='mon_vmem',
             display = False,
             img = 'svc',
             table = 'svcmon',
            ),
    'mon_guestos': HtmlTableColumn(
             title = 'Guest OS',
             field='mon_guestos',
             display = False,
             img = 'svc',
             table = 'svcmon',
            ),
}

v_nodes_colprops = {
    'id': HtmlTableColumn(
             title = 'Id',
             field='id',
             display = False,
             img = 'columns',
             table = 'v_nodes',
            ),
    'node_updated': HtmlTableColumn(
             title = 'Last node update',
             field='node_updated',
             display = False,
             img = 'time16',
             table = 'v_nodes',
             _class = 'datetime_daily',
            ),
    'updated': HtmlTableColumn(
             title = 'Last node update',
             field='updated',
             display = False,
             img = 'time16',
             table = 'v_nodes',
             _class = 'datetime_daily',
            ),
    'loc_country': HtmlTableColumn(
             title = 'Country',
             field='loc_country',
             display = False,
             img = 'loc',
             table = 'v_nodes',
            ),
    'loc_zip': HtmlTableColumn(
             title = 'ZIP',
             field='loc_zip',
             display = False,
             img = 'loc',
             table = 'v_nodes',
            ),
    'loc_city': HtmlTableColumn(
             title = 'City',
             field='loc_city',
             display = False,
             img = 'loc',
             table = 'v_nodes',
            ),
    'loc_addr': HtmlTableColumn(
             title = 'Address',
             field='loc_addr',
             display = False,
             img = 'loc',
             table = 'v_nodes',
            ),
    'loc_building': HtmlTableColumn(
             title = 'Building',
             field='loc_building',
             display = False,
             img = 'loc',
             table = 'v_nodes',
            ),
    'loc_floor': HtmlTableColumn(
             title = 'Floor',
             field='loc_floor',
             display = False,
             img = 'loc',
             table = 'v_nodes',
            ),
    'loc_room': HtmlTableColumn(
             title = 'Room',
             field='loc_room',
             display = False,
             img = 'loc',
             table = 'v_nodes',
            ),
    'loc_rack': HtmlTableColumn(
             title = 'Rack',
             field='loc_rack',
             display = False,
             img = 'loc',
             table = 'v_nodes',
            ),
    'os_concat': HtmlTableColumn(
             title = 'OS full name',
             field='os_concat',
             display = False,
             img = 'os16',
             table = 'v_nodes',
            ),
    'os_name': HtmlTableColumn(
             title = 'OS name',
             field='os_name',
             display = False,
             img = 'os16',
             table = 'v_nodes',
             _class = 'os_name',
            ),
    'os_release': HtmlTableColumn(
             title = 'OS release',
             field='os_release',
             display = False,
             img = 'os16',
             table = 'v_nodes',
            ),
    'os_vendor': HtmlTableColumn(
             title = 'OS vendor',
             field='os_vendor',
             display = False,
             img = 'os16',
             table = 'v_nodes',
            ),
    'os_arch': HtmlTableColumn(
             title = 'OS arch',
             field='os_arch',
             display = False,
             img = 'os16',
             table = 'v_nodes',
            ),
    'os_kernel': HtmlTableColumn(
             title = 'OS kernel',
             field='os_kernel',
             display = False,
             img = 'os16',
             table = 'v_nodes',
            ),
    'cpu_vendor': HtmlTableColumn(
             title = 'CPU vendor',
             field='cpu_vendor',
             display = False,
             img = 'cpu16',
             table = 'v_nodes',
            ),
    'cpu_dies': HtmlTableColumn(
             title = 'CPU dies',
             field='cpu_dies',
             display = False,
             img = 'cpu16',
             table = 'v_nodes',
            ),
    'cpu_cores': HtmlTableColumn(
             title = 'CPU cores',
             field='cpu_cores',
             display = False,
             img = 'cpu16',
             table = 'v_nodes',
            ),
    'sec_zone': HtmlTableColumn(
             title = 'Security zone',
             field='sec_zone',
             display = False,
             img = 'fw16',
             table = 'v_nodes',
            ),
    'cpu_threads': HtmlTableColumn(
             title = 'CPU threads',
             field='cpu_threads',
             display = False,
             img = 'cpu16',
             table = 'v_nodes',
            ),
    'cpu_model': HtmlTableColumn(
             title = 'CPU model',
             field='cpu_model',
             display = False,
             img = 'cpu16',
             table = 'v_nodes',
            ),
    'cpu_freq': HtmlTableColumn(
             title = 'CPU freq',
             field='cpu_freq',
             display = False,
             img = 'cpu16',
             table = 'v_nodes',
            ),
    'mem_banks': HtmlTableColumn(
             title = 'Memory banks',
             field='mem_banks',
             display = False,
             img = 'mem16',
             table = 'v_nodes',
            ),
    'mem_slots': HtmlTableColumn(
             title = 'Memory slots',
             field='mem_slots',
             display = False,
             img = 'mem16',
             table = 'v_nodes',
            ),
    'mem_bytes': HtmlTableColumn(
             title = 'Memory',
             field='mem_bytes',
             display = False,
             img = 'mem16',
             table = 'v_nodes',
            ),
    'nodename': HtmlTableColumn(
             title = 'Node name',
             field='nodename',
             display = False,
             img = 'node16',
             table = 'v_nodes',
             _class="nodename",
            ),
    'version': HtmlTableColumn(
             title = 'Agent version',
             field='version',
             display = False,
             img = 'svc',
             table = 'v_nodes',
            ),
    'listener_port': HtmlTableColumn(
             title = 'Listener port',
             field='listener_port',
             display = False,
             img = 'node16',
             table = 'v_nodes',
            ),
    'assetname': HtmlTableColumn(
             title = 'Asset name',
             field='assetname',
             display = False,
             img = 'node16',
             table = 'v_nodes',
            ),
    'fqdn': HtmlTableColumn(
             title = 'Fqdn',
             field='fqdn',
             display = False,
             img = 'node16',
             table = 'v_nodes',
            ),
    'hvvdc': HtmlTableColumn(
             title = 'Virtual datacenter',
             field='hvvdc',
             display = False,
             img = 'node16',
             table = 'v_nodes',
            ),
    'hvpool': HtmlTableColumn(
             title = 'Hypervisor pool',
             field='hvpool',
             display = False,
             img = 'node16',
             table = 'v_nodes',
            ),
    'hv': HtmlTableColumn(
             title = 'Hypervisor',
             field='hv',
             display = False,
             img = 'node16',
             table = 'v_nodes',
            ),
    'enclosure': HtmlTableColumn(
             title = 'Enclosure',
             field='enclosure',
             display = False,
             img = 'node16',
             table = 'v_nodes',
            ),
    'enclosureslot': HtmlTableColumn(
             title = 'Enclosure Slot',
             field='enclosureslot',
             display = False,
             img = 'node16',
             table = 'v_nodes',
            ),
    'serial': HtmlTableColumn(
             title = 'Serial',
             field='serial',
             display = False,
             img = 'node16',
             table = 'v_nodes',
            ),
    'model': HtmlTableColumn(
             title = 'Model',
             field='model',
             display = False,
             img = 'node16',
             table = 'v_nodes',
            ),
    'team_responsible': HtmlTableColumn(
             title = 'Team responsible',
             field='team_responsible',
             display = False,
             img = 'guy16',
             table = 'v_nodes',
            ),
    'team_integ': HtmlTableColumn(
             title = 'Integrator',
             field='team_integ',
             display = False,
             img = 'guy16',
             table = 'v_nodes',
            ),
    'team_support': HtmlTableColumn(
             title = 'Support',
             field='team_support',
             display = False,
             img = 'guy16',
             table = 'v_nodes',
            ),
    'project': HtmlTableColumn(
             title = 'Project',
             field='project',
             display = False,
             img = 'svc',
             table = 'v_nodes',
            ),
    'role': HtmlTableColumn(
             title = 'Role',
             field='role',
             display = False,
             img = 'node16',
             table = 'v_nodes',
            ),
    'host_mode': HtmlTableColumn(
             title = 'Host Mode',
             field='host_mode',
             display = False,
             img = 'node16',
             table = 'v_nodes',
             _class = 'env',
            ),
    'environnement': HtmlTableColumn(
             title = 'Env',
             field='environnement',
             display = False,
             img = 'node16',
             table = 'v_nodes',
             _class = 'env',
            ),
    'warranty_end': HtmlTableColumn(
             title = 'Warranty end',
             field='warranty_end',
             display = False,
             img = 'time16',
             table = 'v_nodes',
             _class = 'date_future',
            ),
    'os_obs_warn_date': HtmlTableColumn(
             title = 'OS obsolescence warning date',
             field='os_obs_warn_date',
             display = False,
             img = 'time16',
             table = 'v_nodes',
             _class = 'date_future',
            ),
    'os_obs_alert_date': HtmlTableColumn(
             title = 'OS obsolescence alert date',
             field='os_obs_alert_date',
             display = False,
             img = 'time16',
             table = 'v_nodes',
             _class = 'date_future',
            ),
    'hw_obs_warn_date': HtmlTableColumn(
             title = 'Hardware obsolescence warning date',
             field='hw_obs_warn_date',
             display = False,
             img = 'time16',
             table = 'v_nodes',
             _class = 'date_future',
            ),
    'hw_obs_alert_date': HtmlTableColumn(
             title = 'Hardware obsolescence alert date',
             field='hw_obs_alert_date',
             display = False,
             img = 'time16',
             table = 'v_nodes',
             _class = 'date_future',
            ),
    'maintenance_end': HtmlTableColumn(
             title = 'Maintenance end',
             field='maintenance_end',
             display = False,
             img = 'time16',
             table = 'v_nodes',
             _class = 'date_future',
            ),
    'status': HtmlTableColumn(
             title = 'Status',
             field='status',
             display = False,
             img = 'node16',
             table = 'v_nodes',
            ),
    'type': HtmlTableColumn(
             title = 'Type',
             field='type',
             display = False,
             img = 'node16',
             table = 'v_nodes',
            ),
    'power_supply_nb': HtmlTableColumn(
             title = 'Power supply number',
             field='power_supply_nb',
             display = False,
             img = 'pwr',
             table = 'v_nodes',
            ),
    'power_cabinet1': HtmlTableColumn(
             title = 'Power cabinet #1',
             field='power_cabinet1',
             display = False,
             img = 'pwr',
             table = 'v_nodes',
            ),
    'power_cabinet2': HtmlTableColumn(
             title = 'Power cabinet #2',
             field='power_cabinet2',
             display = False,
             img = 'pwr',
             table = 'v_nodes',
            ),
    'power_protect': HtmlTableColumn(
             title = 'Power protector',
             field='power_protect',
             display = False,
             img = 'pwr',
             table = 'v_nodes',
            ),
    'power_protect_breaker': HtmlTableColumn(
             title = 'Power protector breaker',
             field='power_protect_breaker',
             display = False,
             img = 'pwr',
             table = 'v_nodes',
            ),
    'power_breaker1': HtmlTableColumn(
             title = 'Power breaker #1',
             field='power_breaker1',
             display = False,
             img = 'pwr',
             table = 'v_nodes',
            ),
    'power_breaker2': HtmlTableColumn(
             title = 'Power breaker #2',
             field='power_breaker2',
             display = False,
             img = 'pwr',
             table = 'v_nodes',
            ),
}

node_hba_colprops = {
    'nodename': HtmlTableColumn(
             title='Nodename',
             table='node_hba',
             field='nodename',
             img='hw16',
             display=True,
             _class="nodename",
            ),
    'hba_id': HtmlTableColumn(
             title='Hba id',
             table='node_hba',
             field='hba_id',
             img='hd16',
             display=True,
            ),
    'hba_type': HtmlTableColumn(
             title='Hba type',
             table='node_hba',
             field='hba_type',
             img='hd16',
             display=True,
            ),
    'disk_updated': HtmlTableColumn(
             title='Updated',
             table='node_hba',
             field='updated',
             img='time16',
             display=True,
             _class="datetime_daily",
            ),
}

class col_size_mb(HtmlTableColumn):
    def html(self, o):
       d = self.get(o)
       try:
           d = int(d)
       except:
           return ''
       c = "nowrap"
       if d < 0:
           c += " highlight"
       if d is None:
           return ''
       return DIV(beautify_size_mb(d), _class=c)

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

apps_colprops = {
    'app': HtmlTableColumn(
             title='Application code',
             table='apps',
             field='app',
             img='svc',
             display=True,
            ),
    'app_domain': HtmlTableColumn(
             title='App domain',
             table='apps',
             field='app_domain',
             img='svc',
             display=True,
            ),
    'app_team_ops': HtmlTableColumn(
             title='Ops team',
             table='apps',
             field='app_team_ops',
             img='guys16',
             display=True,
            ),
}

disk_app_colprops = {
    'disk_region': HtmlTableColumn(
             title='Disk Region',
             table='b_disk_app',
             field='disk_region',
             img='hd16',
             display=False,
             _class="pre",
            ),
    'disk_id': HtmlTableColumn(
             title='Disk Id',
             table='b_disk_app',
             field='disk_id',
             img='hd16',
             display=True,
             _class="pre",
             _dataclass="bluer",
            ),
    'disk_name': HtmlTableColumn(
             title='Disk Name',
             table='b_disk_app',
             field='disk_name',
             img='hd16',
             display=True,
             _class="pre",
             _dataclass="bluer",
            ),
    'disk_svcname': HtmlTableColumn(
             title='Service',
             table='b_disk_app',
             field='disk_svcname',
             img='svc',
             display=True,
             _class = 'svcname',
            ),
    'disk_nodename': HtmlTableColumn(
             title='Nodename',
             table='b_disk_app',
             field='disk_nodename',
             img='hw16',
             display=True,
             _class="nodename",
            ),
    'disk_used': HtmlTableColumn(
             title='Disk Used',
             table='b_disk_app',
             field='disk_used',
             img='hd16',
             display=True,
             _class="numeric size_mb",
            ),
    'disk_local': HtmlTableColumn(
             title='Disk Local',
             table='b_disk_app',
             field='disk_local',
             img='hd16',
             display=True,
            ),
    'disk_size': HtmlTableColumn(
             title='Disk Size',
             table='b_disk_app',
             field='disk_size',
             img='hd16',
             display=True,
             _class="numeric size_mb",
             _dataclass="bluer",
            ),
    'disk_alloc': HtmlTableColumn(
             title='Disk Allocation',
             table='b_disk_app',
             field='disk_alloc',
             img='hd16',
             display=True,
             _class="numeric size_mb",
             _dataclass="bluer",
            ),
    'disk_vendor': HtmlTableColumn(
             title='Disk Vendor',
             table='b_disk_app',
             field='disk_vendor',
             img='hd16',
             display=True,
            ),
    'disk_model': HtmlTableColumn(
             title='Disk Model',
             table='b_disk_app',
             field='disk_model',
             img='hd16',
             display=True,
            ),
    'disk_dg': HtmlTableColumn(
             title='System disk group',
             table='b_disk_app',
             field='disk_dg',
             img='hd16',
             display=True,
            ),
    'disk_group': HtmlTableColumn(
             title='Array disk group',
             table='b_disk_app',
             field='disk_group',
             img='hd16',
             display=True,
             _class="disk_array_dg",
             _dataclass="bluer",
            ),
    'disk_level': HtmlTableColumn(
             title='Level',
             table='b_disk_app',
             field='disk_level',
             img='hd16',
             display=True,
             _dataclass="bluer",
            ),
    'disk_raid': HtmlTableColumn(
             title='Raid',
             table='b_disk_app',
             field='disk_raid',
             img='hd16',
             display=True,
             _dataclass="bluer",
            ),
    'svcdisk_updated': HtmlTableColumn(
             title='System Updated',
             table='b_disk_app',
             field='svcdisk_updated',
             img='time16',
             display=True,
             _class="datetime_daily",
            ),
    'disk_created': HtmlTableColumn(
             title='Storage Created',
             table='b_disk_app',
             field='disk_created',
             img='time16',
             display=True,
             _dataclass="bluer",
            ),
    'disk_updated': HtmlTableColumn(
             title='Storage Updated',
             table='b_disk_app',
             field='disk_updated',
             img='time16',
             display=True,
             _dataclass="datetime_daily bluer",
            ),
    'svcdisk_id': HtmlTableColumn(
             title='System Disk Id',
             table='b_disk_app',
             field='svcdisk_id',
             img='hd16',
             display=True,
             _class="disk_array",
             _dataclass="bluer",
            ),
    'disk_arrayid': HtmlTableColumn(
             title='Array Id',
             table='b_disk_app',
             field='disk_arrayid',
             img='hd16',
             display=True,
             _class="disk_array",
             _dataclass="bluer",
            ),
    'disk_devid': HtmlTableColumn(
             title='Array device Id',
             table='b_disk_app',
             field='disk_devid',
             img='hd16',
             display=True,
             _class="pre",
             _dataclass="bluer",
            ),
    'array_model': HtmlTableColumn(
             title='Array Model',
             table='stor_array',
             field='array_model',
             img='hd16',
             display=True,
             _dataclass="bluer",
            ),
    'app': HtmlTableColumn(
             title='App',
             table='b_disk_app',
             field='app',
             img='svc',
             display=True,
            ),
}

