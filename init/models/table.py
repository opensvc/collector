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
        self.action_menu = []

        # initialize the pager, to be re-executed by instanciers
        self.setup_pager()

        # drop stored filters if request asks for it
        self.drop_filters()

        # csv
        self.csv_q = None
        self.csv_orderby = None
        self.csv_left = None
        self.csv_limit = 20000

        self.action_menu = {
          'nodes': node_actions,
          'services': svc_actions,
          'resources': resource_actions,
          'modules': module_actions,
        }


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
                    _class='ocb',
                    _id=id_col,
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
                  LABEL(
                    _for=id_col,
                  ),
                  SPAN(
                    T(self.colprops[a].title),
                    _style="""background-image:url(%s);
                              background-repeat:no-repeat;
                              padding-left:18px;
                              margin-left:0.2em;
                           """%URL(r=request,c='static',f='images/'+self.colprops[a].img+'.png'),
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
                    _class="link_ta",
                  ),
                  _class='white_float hidden',
                  _id='link_val_'+self.id,
                ),
              ),
              _class='floatw',
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
              ),
              _class='floatw',
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
                elif type(v) == datetime.date:
                    try:
                        v = v.strftime("%Y-%m-%d")
                    except ValueError:
                        v = str(v)
                elif v is None:
                    v = 'empty'
                elif type(v) in (str, unicode):
                    v = v.replace('"','').replace("'","")
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

        nav = SPAN(_class='pager floatw')

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
        try:
            if self.checkbox_id_table is None or \
               self.checkbox_id_table not in o:
                return o[self.checkbox_id_col]
            else:
                return o[self.checkbox_id_table][self.checkbox_id_col]
        except:
            return '_'.join(map(lambda x: str(o[x]) if x in o else "", self.keys))

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
        if request.vars.volatile_filters is not None:
            return
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
        if request.vars.volatile_filters is not None:
            return ""
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
                                 _class='ocb',
                                 _disabled='disabled',
                                 _id=checkbox_id,
                               ),
                               LABEL(
                                 _for=checkbox_id,
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
                                 _class='ocb',
                                 _id=checkbox_id,
                                 _name=self.checkbox_name_key(),
                                 _value=value,
                                 value=checked,
                               ),
                               LABEL(
                                 _for=checkbox_id,
                               ),
                               _name=self.id+"_tools",
                               _class="tools",
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
                              _class='ocb',
                              _id=self.master_checkbox_key(),
                              _onclick="check_all('%(name)s', this.checked);"%dict(name=self.checkbox_name_key())
                            ),
                            LABEL(
                              _for=self.master_checkbox_key(),
                            ),
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
        d = SPAN(
          INPUT(
            _type="checkbox",
            _class='ocb',
            _id="wsswitch_"+self.id,
            _onclick=js,
            value=wsenabled,
          ),
          LABEL(
            _for="wsswitch_"+self.id,
          ),
          SPAN(T("Live")),
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
 'volatile_filters': "%(volatile_filters)s",
 'visible_columns': %(visible_columns)s,
 'child_tables': %(child_tables)s,
 'action_menu': %(action_menu)s,
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
                   volatile_filters=str(request.vars.get("volatile_filters", "")),
                   visible_columns=str(self.visible_columns()),
                   child_tables=str(self.child_tables),
                   ajax_submit=self.ajax_submit(),
                   ajax_enter_submit=self.ajax_enter_submit(),
                   dataable=str(self.dataable).lower(),
                   action_menu=str(self.action_menu),
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
            if len(l) == 0:
                continue
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

module_actions = [
  {'title': 'Check', 'class': 'check16', 'action': 'check'},
  {'title': 'Fix', 'class': 'comp16', 'action': 'fix'},
]

resource_actions = [
  {'title': 'Start', 'class': 'action_start_16', 'action': 'start'},
  {'title': 'Stop', 'class': 'action_stop_16', 'action': 'stop'},
  {'title': 'Restart', 'class': 'action_restart_16', 'action': 'restart'},
  {'title': 'Enable', 'class': 'check16', 'action': 'enable'},
  {'title': 'Disable', 'class': 'na', 'action': 'disable'},
]

svc_actions = [
  {'title': 'Start', 'class': 'action_start_16', 'action': 'start'},
  {'title': 'Stop', 'class': 'action_stop_16', 'action': 'stop'},
  {'title': 'Restart', 'class': 'action_restart_16', 'action': 'restart'},
  {'title': 'Switch', 'class': 'action_restart_16', 'action': 'switch'},
  {'title': 'Sync all remotes', 'class': 'action_sync_16', 'action': 'syncall'},
  {'title': 'Sync peer remotes', 'class': 'action_sync_16', 'action': 'syncnodes'},
  {'title': 'Sync disaster recovery remotes', 'class': 'action_sync_16', 'action': 'syncdrp'},
  {'title': 'Enable', 'class': 'check16', 'action': 'enable'},
  {'title': 'Disable', 'class': 'na', 'action': 'disable'},
  {'title': 'Freeze', 'class': 'frozen16', 'action': 'freeze'},
  {'title': 'Thaw', 'class': 'frozen16', 'action': 'thaw'},
  {'title': 'Compliance check', 'class': 'comp16', 'action': 'compliance_check', 'params': ["module", "moduleset"]},
  {'title': 'Compliance fix', 'class': 'comp16', 'action': 'compliance_fix', 'params': ["module", "moduleset"]},
]

node_actions = [
  {'title': 'Update node information', 'class': 'hw16', 'action': 'pushasset'},
  {'title': 'Update disks information', 'class': 'hd16', 'action': 'pushdisks'},
  {'title': 'Update app information', 'class': 'svc', 'action': 'push_appinfo'},
  {'title': 'Update services information', 'class': 'svc', 'action': 'pushservices'},
  {'title': 'Update installed packages information', 'class': 'pkg16', 'action': 'pushpkg'},
  {'title': 'Update installed patches information', 'class': 'pkg16', 'action': 'pushpatch'},
  {'title': 'Update stats', 'class': 'spark16', 'action': 'pushstats'},
  {'title': 'Update check values', 'class': 'check16', 'action': 'checks'},
  {'title': 'Update sysreport', 'class': 'log16', 'action': 'sysreport'},
  {'title': 'Update compliance modules', 'class': 'comp16', 'action': 'updatecomp'},
  {'title': 'Update opensvc agent', 'class': 'pkg16', 'action': 'updatepkg'},
  {'title': 'Rotate root password', 'class': 'key16', 'action': 'rotate root pw'},
  {'title': 'Rescan scsi hosts', 'class': 'hd16', 'action': 'scanscsi'},
  {'title': 'Reboot', 'class': 'action_restart_16', 'action': 'reboot'},
  {'title': 'Reboot schedule', 'class': 'action_restart_16', 'action': 'schedule_reboot'},
  {'title': 'Reboot unschedule', 'class': 'action_restart_16', 'action': 'unschedule_reboot'},
  {'title': 'Shutdown', 'class': 'action_stop_16', 'action': 'shutdown'},
  {'title': 'Wake On LAN', 'class': 'action_start_16', 'action': 'wol'},
  {'title': 'Compliance check', 'class': 'comp16', 'action': 'compliance_check', 'params': ["module", "moduleset"]},
  {'title': 'Compliance fix', 'class': 'comp16', 'action': 'compliance_fix', 'params': ["module", "moduleset"]},
]
