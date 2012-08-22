import re

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
                 img='generic', _class='', _dataclass=''):
        Column.__init__(self, title, display, img, _class, _dataclass)
        self.table = table
        self.field = field

    def get(self, o):
        try:
            if self.table is None or self.table not in o:
                return o[self.field]
            else:
                return o[self.table][self.field]
        except KeyError:
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
        self.id_perpage = '_'.join((self.id, 'perpage'))
        self.id_page = '_'.join((self.id, 'page'))
        self.cellclasses = {'cell1': 'cell2', 'cell2': 'cell1'}
        self.cellclass = 'cell1'
        self.upc_table = self.id
        self.last = None
        self.column_filter_reset = '**clear**'

        # to be set by children
        self.additional_inputs = []
        self.additional_filters = []
        self.cols = []
        self.colprops = {}

        # to be set be instanciers
        self.autorefresh = 0
        self.checkboxes = False
        self.checkbox_names = [self.id+'_ck']
        self.checkbox_id_col = 'id'
        self.checkbox_id_table = None
        self.extraline = False
        self.extrarow = False
        self.filterable = True
        self.hide_tools = False
        self.dbfilterable = True
        self.pageable = True
        self.exportable = True
        self.linkable = True
        self.refreshable = True
        self.columnable = True
        self.headers = True
        self.colored_lines = True
        self.additional_tools = []
        self.span = None
        self.flash = None
        self.sub_span = []
        self.nodatabanner = True

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

    def setup_pager(self, n=0):
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
                    self.perpage = db(q).select().first().perpage
                except:
                    self.perpage = 20

            if self.id_page in request.vars:
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
                self.pager_end = self.pager_start + self.perpage - 1
        else:
            self.perpage = 0
            self.page = 0
            self.pager_start = 0
            self.pager_end = n
        self.page_len = self.pager_end - self.pager_start

    def col_values_cloud(self, c):
        l = []
        for o in self.object_list:
            s = self.colprops[c].get(o)
            if s is None:
                s = 'empty'
            l.append(A(
                       s,
                       ' ',
                       _class="cloud_tag",
                       _onclick="filter_submit_%(id)s('%(iid)s','%(val)s')"%dict(
                                id=self.id,
                                iid=self.filter_key(c),
                                val=self.colprops[c].get(o),
                               ),
                    ))
        return SPAN(l)

    def get_column_visibility(self, c):
        return self.colprops[c].display

    def set_column_visibility(self):
        q = db.user_prefs_columns.upc_user_id==session.auth.user.id
        q &= db.user_prefs_columns.upc_table==self.upc_table
        rows = db(q).select()
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
        rows = db(q).select()
        for row in rows:
            field = row.col_name.split('.')[-1]
            if field not in self.colprops:
                continue
            self.colprops[field].display = True

    def col_hide(self, c):
        id_col = self.col_checkbox_key(c)
        if self.get_column_visibility(c) or \
           (id_col in request.vars and request.vars[id_col] == 'on'):
            return ""
        else:
            return "display:none"

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
        rows = db(q).select(db.auth_user.lock_filter)
        if len(rows) != 1:
            return SPAN()

        if rows.first().lock_filter:
            lock_filter = True
        else:
            lock_filter = False

        q = db.gen_filterset_user.user_id == auth.user_id
        q &= db.gen_filterset_user.fset_id == db.gen_filtersets.id
        rows = db(q).select()
        active_fset_id = 0
        for row in rows:
            active_fset_id = row.gen_filtersets.id
            active_fset_name = row.gen_filtersets.fset_name

        if lock_filter:
            content = active_fset_name
        else:
            o = db.gen_filtersets.fset_name
            q = db.gen_filtersets.id > 0
            rows = db(q).select(orderby=o)
            av = [self.format_av_filter(None)]
            for row in rows:
                av.append(self.format_av_filter(row))
            content = SELECT(
                        av,
                        value=active_fset_id,
                        _onchange="""ajax('%(url)s/'+this.options[this.selectedIndex].value, [], '%(div)s');"""%dict(
                              url=URL(
                                   r=request, c='ajax',
                                   f='ajax_select_filter',
                                  ),
                              div="avs"+self.id,
                             )+self.ajax_submit(),
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
        id_set_col_table = '_'.join((self.id, 'set_col_table'))
        id_set_col_field = '_'.join((self.id, 'set_col_field'))
        id_set_col_value = '_'.join((self.id, 'set_col_value'))
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
                    _onclick="""if (!$("#%(fid)s") || $("#%(fid)s").val().length==0) {
                                 check_toggle_vis(this.checked, "%(col_name)s");
                                 $("#%(id_set_col_table)s").val("%(table)s");
                                 $("#%(id_set_col_field)s").val("%(field)s");
                                 $("#%(id_set_col_value)s").val(this.checked);
                                 ajax("%(url)s",
                                      ["%(id_set_col_table)s",
                                       "%(id_set_col_field)s",
                                       "%(id_set_col_value)s"],
                                      "set_col_dummy");
                                 } else {
                                  this.checked = true
                                 }
                             """%dict(url=URL(r=request,c='ajax',f='ajax_set_user_prefs_column'),
                                      col_name=self.col_key(a),
                                      fid=self.filter_key(a),
                                      id_set_col_table=id_set_col_table,
                                      id_set_col_field=id_set_col_field,
                                      id_set_col_value=id_set_col_value,
                                      table=self.upc_table,
                                      field=a),
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
              INPUT(
                _id=id_set_col_table,
                _type='hidden',
              ),
              INPUT(
                _id=id_set_col_field,
                _type='hidden',
              ),
              INPUT(
                _id=id_set_col_value,
                _type='hidden',
              ),
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

    def countdown(self):
        if not self.autorefresh:
            return SPAN()
        d = SPAN(
              DIV(
                self.autorefresh/1000,
                _id='countdown_'+self.id,
                _class='floatw',
              ),
              DIV(
                0,
                _id='countup_'+self.id,
                _class='floatw',
              ),
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
                  _onclick="js_link_%s()"%self.id,
                  _class='link16',
                  _id='link_'+self.id,
                ),
                _class='floatw',
              ),
            )
        return d

    def refresh(self):
        if not self.refreshable:
            return SPAN()
        d = DIV(
              A(
                SPAN(
                  T('Refresh'),
                  _onclick="ajax_submit_%s()"%self.id,
                  _class='refresh16',
                  _id='refresh_'+self.id,
                ),
                _class='floatw',
              ),
            )
        return d

    def pager(self):
        if not self.pageable:
            return SPAN()

        def set_perpage_js(n):
            js = 'filter_submit_%(id)s("%(iid)s",%(n)s)'%dict(
                   id=self.id,
                   iid=self.id_perpage,
                   n=n)
            return js

        def set_page_js(page):
            js = 'filter_submit_%(id)s("%(iid)s",%(page)s)'%dict(
                   id=self.id,
                   iid=self.id_page,
                   page=page)
            return js

        start = 0
        end = 0

        if self.totalrecs == 0:
            return DIV("No records found matching filters", _class='floatw')
        if self.perpage <= 0:
            return DIV(
                     A(
                       T('Enable paging'),
                       _onclick=set_perpage_js(20)+set_page_js(1),
                     ),
                     _class='floatw',
                   )
        if self.totalrecs == default_max_lines or self.totalrecs < 0:
            # unknown total pages. arbitrary high value.
            totalpages = 999999
        else:
            totalpages = self.totalrecs / self.perpage
            if self.totalrecs % self.perpage > 0:
                totalpages = totalpages + 1

        # out of range conditions
        page = self.page
        if page <= 0:
            page = 1
        if page > totalpages:
            page = 1
        start = (page-1) * self.perpage
        end = start + self.perpage
        if end > self.totalrecs and self.totalrecs != default_max_lines and self.totalrecs > 0:
            end = self.totalrecs

        if self.totalrecs >= 0:
            total = "/%d%s"%(self.totalrecs, self.overlimit)
        else:
            total = ""

        pager = []
        if page != 1:
            pager.append(A(
                           '<< ',
                           _class="current_page",
                           _onclick=set_page_js(page-1),
                         ))
        pager.append(A(
                      '%d-%d%s '%(start+1, end, total),
                       _class="current_page",
                       _onclick="""click_toggle_vis(event, '%(div)s','block');"""%dict(
                          div='perpage',
                       ),
                     ))
        opts_v = [20, 50, 100, 500]
        opts = []
        for o in opts_v:
            if self.perpage == o:
                c = 'current_page'
            else:
                c = ''
            opts.append(SPAN(
                          A(
                            o,
                            _class=c,
                            _onclick=set_perpage_js(o)
                          ),
                          BR(),
                        ))
        pager.append(DIV(
                       SPAN(opts),
                       _name='perpage',
                       _class='white_float',
                       _style='max-width:50%;display:none;text-align:right;',
                     ))
        if page != totalpages:
            pager.append(A(
                           '>> ',
                           _class="current_page",
                           _onclick=set_page_js(page+1),
                         ))

        nav = DIV(pager, _class='floatw')

        return nav

    def rotate_colors(self):
        if not self.colored_lines:
            return
        self.cellclass = self.cellclasses[self.cellclass]

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
        if self.colprops[self.span].table is None or \
           self.colprops[self.span].table not in o:
            return o[self.span]
        else:
            return o[self.colprops[self.span].table][self.span]

    def extra_line_key(self, o):
        if self.span:
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

    def drop_filters(self):
        if request.vars.clear_filters != 'true':
            return
        q = db.column_filters.col_tableid==self.id
        q &= db.column_filters.user_id==session.auth.user.id
        db(q).delete()

    def drop_filter_value(self, f):
        field = self.stored_filter_field(f)
        if field is None:
            return
        q = db.column_filters.col_tableid==self.id
        q &= db.column_filters.col_name==field
        q &= db.column_filters.user_id==session.auth.user.id
        db(q).delete()

    def store_filter_value(self, f, v):
        field = self.stored_filter_field(f)
        if field is None:
            return
        q = db.column_filters.col_tableid==self.id
        q &= db.column_filters.col_name==field
        q &= db.column_filters.user_id==session.auth.user.id
        if len(db(q).select()) > 0:
            db(q).update(col_filter=v)
        else:
            db.column_filters.insert(col_tableid=self.id,
                                     col_name=field,
                                     col_filter=v,
                                     user_id=session.auth.user.id)

    def stored_filter_value(self, f):
        field = self.stored_filter_field(f)
        if field is None:
            return ""
        q = db.column_filters.col_tableid==self.id
        q &= db.column_filters.col_name==field
        q &= db.column_filters.user_id==session.auth.user.id
        rows = db(q).select()
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
        if v == "":
            return self.stored_filter_value(f)
        self.store_filter_value(f, v)
        return v

    def _filter_parse(self, f):
        key = self.filter_key(f)
        if key in request.vars:
            return request.vars[key]
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
                            _style=self.col_hide(c),
                            _class=self.colprops[c]._class,
                            _name=self.col_key(c)))
        return TR(cells, _class='theader')

    def table_line(self, o):
        cells = []
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
                                 _onclick='this.value=this.checked',
                                 value=checked,
                               ),
                             ))

        if self.extrarow:
            cells.append(TD(self.format_extrarow(o)))

        for c in self.cols:
            if self.spaning_cell(c, o):
                content = ''
            else:
                content = self.colprops[c].html(o)
            v = self.colprops[c].get(o)
            if v is None:
                v = 'empty'
            cells.append(TD(content,
                            _name=self.col_key(c),
                            _style=self.col_hide(c),
                            _class=' '.join([self.colprops[c]._class, self.colprops[c]._dataclass]),
                            _onclick="""$("#fsr%(id)s").hide()"""%dict(
                              id=self.id,
                            ),
                            _ONMOUSEUP="filter_selector_%(id)s(event, '%(k)s','%(v)s')"%dict(
                              id=self.id,
                              k=self.filter_key(c),
                              v=v,
                             ),
                            _oncontextmenu="return false;",
                         ))
        return TR(cells, _class=self.cellclass)

    def spaning_line(self, o):
        if self.span is not None and \
           self.last is not None and \
           self.colprops[self.span].get(o) == self.colprops[self.span].get(self.last):
            return True
        return False

    def spaning_cell(self, c, o):
        if not self.spaning_line(o):
           return False
        if (c == self.span or (c in self.sub_span and \
           self.colprops[c].get(o) == self.colprops[c].get(self.last))):
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
                if not self.spaning_line(o):
                    if self.extraline and self.span is not None:
                        lines.append(self.format_extraline(self.last))
                    self.rotate_colors()
                lines.append(self.table_line(o))
                if self.extraline and self.span is None:
                    lines.append(self.format_extraline(o))
                self.last = o
        if self.extraline and self.span is not None:
            lines.append(self.format_extraline(self.last))
        return lines, line_count

    def format_extraline(self, o):
        n = len(self.cols)
        if self.checkboxes:
            n += 1
        if self.extrarow:
            n += 1
        return TR(
                 TD(
                   _colspan=n,
                   _id=self.extra_line_key(o),
                   _style='display:none',
                 ),
                 _class=self.cellclass,
               )

    def header_slim(self):
        inputs = []
        if self.checkboxes:
            inputs.append(TD(''))
        if self.extrarow:
            inputs.append(TD(''))
        for c in self.cols:
            if len(self.filter_parse(c)) > 0:
                cl = 'bgred'
            else:
                cl = ''
            inputs.append(
              TD(
                '',
                 _class=cl,
                 _style=self.col_hide(c),
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
            if len(self.filter_parse(c)) > 0:
                clear = SPAN(
                          IMG(
                            _src=URL(r=request,c='static',f='invert16.png'),
                            _title=T("Invert filter"),
                            _class='clickable',
                            _onclick="""invert_filter("%(did)s");ajax_submit_%(id)s()"""%dict(
                                    id=self.id,
                                    did=self.filter_key(c)),
                          ),
                          IMG(
                            _src=URL(r=request,c='static',f='clear16.png'),
                            _onclick="filter_submit_%(id)s('%(k)s','%(v)s')"%dict(
                               id=self.id,
                               k=self.filter_key(c),
                               v=self.column_filter_reset),
                            _style="margin-right:4px",
                          ),
                        )
            else:
                clear = SPAN()
            filter_text = self.filter_parse(c)
            if len(filter_text) > 20:
                filter_span = SPAN(
                                filter_text[0:17] + "...",
                                _title=filter_text,
                              )
            else:
                filter_span = SPAN(filter_text)
            inputs.append(TD(
                            SPAN(
                              IMG(
                                _src=URL(r=request,c='static',f='filter16.png'),
                                _onClick="""click_toggle_vis(event, '%(div)s','block');$("#%(input)s").focus()"""%dict(
                                    div=self.filter_div_key(c),
                                    input=self.filter_key(c),
                                  ),
                                _class='clickable',
                              ),
                              clear,
                              filter_span,
                              _style="vertical-align:top",
                            ),
                            DIV(
                              INPUT(
                                _id=self.filter_key(c),
                                _name="fi",
                                _value=self.filter_parse(c),
                                _onKeyPress="ajax_enter_submit_%s(event)"%self.id,
                                _onKeyUp="""if(!is_enter(event)){clearTimeout(timer);timer=setTimeout(function validate(){ajax('%(url)s', inputs_%(id)s, '%(cloud)s')}, 1000)}"""%dict(
                                    id=self.id,
                                    url=URL(r=request,f=self.func+'_col_values', args=[c]),
                                    cloud=self.filter_cloud_key(c)
                                  ),
                              ),
                              IMG(
                                _src=URL(r=request,c='static',f='values_to_filter.png'),
                                _title=T("Use column values as filter"),
                                _class='clickable',
                                _onclick="""function f() {values_to_filter("%(iid)s","%(did)s");ajax_submit_%(id)s()};sync_ajax('%(url)s', inputs_%(id)s, '%(did)s', f)"""%dict(
                                        id=self.id,
                                        iid=self.filter_key(c),
                                        url=URL(r=request,f=self.func+'_col_values', args=[c]),
                                        did=self.filter_cloud_key(c)),
                              ),
                              BR(),
                              SPAN(
                                _id=self.filter_cloud_key(c),
                              ),
                              _name=self.filter_div_key(c),
                              _class='white_float',
                              _style='max-width:50%;display:none',
                            ),
                            _name=self.col_key(c),
                            _style=self.col_hide(c),
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
        return """if(typeof(inputs_%(id)s)!='undefined'){i=inputs_%(id)s}else{i=[]};table_ajax_submit('%(url)s', '%(divid)s', i, %(additional_inputs)s, %(input_name)s, "%(additional_input_name)s");"""%dict(
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

    def right_click_menu(self):
        d = SPAN(
              TABLE(
                TR(
                  TD("", _id="fsrview", _colspan=3),
                ),
                TR(
                  TD("clear", _id="fsrclear"),
                  TD("reset", _id="fsrreset"),
                  TD("!", _id="fsrneg"),
                ),
                TR(
                  TD("%..", _id="fsrwildleft"),
                  TD("..%", _id="fsrwildright"),
                  TD("%..%", _id="fsrwildboth"),
                ),
                TR(
                  TD("=", _id="fsreq"),
                  TD("&=", _id="fsrandeq"),
                  TD("|=", _id="fsroreq"),
                ),
                TR(
                  TD(">", _id="fsrsup"),
                  TD("&>", _id="fsrandsup"),
                  TD("|>", _id="fsrorsup"),
                ),
                TR(
                  TD("<", _id="fsrinf"),
                  TD("&<", _id="fsrandinf"),
                  TD("|<", _id="fsrorinf"),
                ),
                TR(
                  TD("empty", _id="fsrempty"),
                  TD("&empty", _id="fsrandempty"),
                  TD("|empty", _id="fsrorempty"),
                ),
              ),
              _class='right_click_menu',
              _id='fsr'+self.id,
            )
        return d

    def show_flash(self):
        if self.flash is None:
            return SPAN()
        d = DIV(
              self.flash,
              _class='tableo_flash',
              _onclick="this.style['display']='none';"
            )
        return d

    def html(self):
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
                            args=['csv']
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

        if inputs is not None:
            table_lines.append(inputs)
            table_lines.append(self.header_slim())

        if len(lines) > 0:
            table_lines += lines
        elif self.nodatabanner:
            table_lines.append(T("no data"))

        d = DIV(
              self.show_flash(),
              self.right_click_menu(),
              DIV(
                self.pager(),
                self.refresh(),
                self.link(),
                self.countdown(),
                export,
                self.columns_selector(),
                self.persistent_filters(),
                additional_tools,
                DIV('', _class='spacer'),
                _class='theader',
              ),
              additional_filters,
              DIV(
                TABLE(
                   table_lines
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
function ajax_submit_%(id)s(){%(ajax_submit)s};
function ajax_enter_submit_%(id)s(event){%(ajax_enter_submit)s};
function filter_submit_%(id)s(k,v){$("#"+k).val(v);ajax_submit_%(id)s()};
function filter_selector_%(id)s(e,k,v){
  if(e.button != 2) {
    return
  }
  $("#fsr%(id)s").each(function() {
    $(this)[0].oncontextmenu = function() {
      return false;
    }
  });
  var sel = window.getSelection().toString()
  if (sel.length == 0) {
    sel = v
  }
  _sel = sel
  cur = $("#fsr%(id)s").find("#fsrview").text()
  if (cur.length==0) {
    cur = $("#"+k).val()
  }
  $("#fsr%(id)s").show()
  if (e.pageX || e.pageY) {
      posx = e.pageX;
      posy = e.pageY;
  }
  else if (e.clientX || e.clientY) {
      posx = e.clientX + document.body.scrollLeft
           + document.documentElement.scrollLeft;
      posy = e.clientY + document.body.scrollTop
           + document.documentElement.scrollTop;
  }
  $("#fsr%(id)s").find(".bgred").each(function(){
    $(this).removeClass("bgred")
  })
  function getsel(){
    __sel = _sel
    if ($("#fsr%(id)s").find("#fsrwildboth").hasClass("bgred")) {
      __sel = '%%' + __sel + '%%'
    } else
    if ($("#fsr%(id)s").find("#fsrwildleft").hasClass("bgred")) {
      __sel = '%%' + __sel
    } else
    if ($("#fsr%(id)s").find("#fsrwildright").hasClass("bgred")) {
      __sel = __sel + '%%'
    }
    if ($("#fsr%(id)s").find("#fsrneg").hasClass("bgred")) {
      __sel = '!' + __sel
    }
    return __sel
  }
  $("#fsr%(id)s").css({"left": posx + "px", "top": posy + "px"})
  $("#fsr%(id)s").find("#fsrview").each(function(){
    $(this).text($("#"+k).val())
    $(this).unbind()
    $(this).bind("dblclick", function(){
      sel = $(this).text()
      $("#"+k).val(sel)
      filter_submit_%(id)s(k,sel)
    })
    $(this).bind("click", function(){
      sel = $(this).text()
      cur = sel
      $("#"+k).val(sel)
      $(this).removeClass("highlight")
      $(this).addClass("b")
      colname = $("#"+k).parents("td").attr("name")
      $(".theader_slim").find("[name="+colname+"]").each(function(){
        $(this).removeClass("bgred")
        $(this).addClass("bgorange")
      })
    })
  })
  $("#fsr%(id)s").find("#fsrreset").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      $("#fsr%(id)s").find("#fsrview").each(function(){
        $(this).text("")
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr%(id)s").find("#fsrclear").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      $("#fsr%(id)s").find("#fsrview").each(function(){
        $(this).text("**clear**")
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr%(id)s").find("#fsrneg").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      if ($(this).hasClass("bgred")) {
        $(this).removeClass("bgred")
      } else {
        $(this).addClass("bgred")
      }
      sel = getsel()
    })
  })
  $("#fsr%(id)s").find("#fsrwildboth").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      if ($(this).hasClass("bgred")) {
        $(this).removeClass("bgred")
      } else {
        $("#fsr%(id)s").find("[id^=fsrwild]").each(function(){
          $(this).removeClass("bgred")
        })
        $(this).addClass("bgred")
      }
      sel = getsel()
    })
  })
  $("#fsr%(id)s").find("#fsrwildleft").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      if ($(this).hasClass("bgred")) {
        $(this).removeClass("bgred")
      } else {
        $("#fsr%(id)s").find("[id^=fsrwild]").each(function(){
          $(this).removeClass("bgred")
        })
        $(this).addClass("bgred")
      }
      sel = getsel()
    })
  })
  $("#fsr%(id)s").find("#fsrwildright").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      if ($(this).hasClass("bgred")) {
        $(this).removeClass("bgred")
      } else {
        $("#fsr%(id)s").find("[id^=fsrwild]").each(function(){
          $(this).removeClass("bgred")
        })
        $(this).addClass("bgred")
      }
      sel = getsel()
    })
  })
  $("#fsr%(id)s").find("#fsreq").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      $("#fsr%(id)s").find("#fsrview").each(function(){
        $(this).text(sel)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr%(id)s").find("#fsrandeq").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = cur + '&' + sel
      $("#fsr%(id)s").find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr%(id)s").find("#fsroreq").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = cur + '|' + sel
      $("#fsr%(id)s").find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr%(id)s").find("#fsrsup").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = '>' + sel
      $("#fsr%(id)s").find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr%(id)s").find("#fsrandsup").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = $("#fsr%(id)s").find("#fsrview").text()
      if (val.length==0) {
        val = $("#"+k).val()
      }
      val = val + '&>' + sel
      $("#fsr%(id)s").find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr%(id)s").find("#fsrorsup").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = $("#fsr%(id)s").find("#fsrview").text()
      if (val.length==0) {
        val = $("#"+k).val()
      }
      val = val + '|>' + sel
      $("#fsr%(id)s").find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr%(id)s").find("#fsrinf").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = '<' + sel
      $("#fsr%(id)s").find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr%(id)s").find("#fsrandinf").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = $("#fsr%(id)s").find("#fsrview").text()
      if (val.length==0) {
        val = $("#"+k).val()
      }
      val = val + '&<' + sel
      $("#fsr%(id)s").find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr%(id)s").find("#fsrorinf").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = $("#fsr%(id)s").find("#fsrview").text()
      if (val.length==0) {
        val = $("#"+k).val()
      }
      val = val + '|<' + sel
      $("#fsr%(id)s").find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr%(id)s").find("#fsrempty").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      if ($("#fsr%(id)s").find("#fsrneg").hasClass("bgred")) {
        val = '!empty'
      } else {
        val = 'empty'
      }
      $("#fsr%(id)s").find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr%(id)s").find("#fsrandempty").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = $("#fsr%(id)s").find("#fsrview").text()
      if (val.length==0) {
        val = $("#"+k).val()
      }
      if ($("#fsr%(id)s").find("#fsrneg").hasClass("bgred")) {
        val = val + '&!empty'
      } else {
        val = val + '&empty'
      }
      $("#fsr%(id)s").find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
  $("#fsr%(id)s").find("#fsrorempty").each(function(){
    $(this).unbind()
    $(this).bind("click", function(){
      val = $("#fsr%(id)s").find("#fsrview").text()
      if (val.length==0) {
        val = $("#"+k).val()
      }
      if ($("#fsr%(id)s").find("#fsrneg").hasClass("bgred")) {
        val = val + '|!empty'
      } else {
        val = val + '|empty'
      }
      $("#fsr%(id)s").find("#fsrview").each(function(){
        $(this).text(val)
        $(this).addClass("highlight")
      })
    })
  })
};
function js_link_%(id)s(){
  url=$(location).attr('href')
  if (url.indexOf('?')>0) {
    url=url.substring(0, url.indexOf('?'))
  }
  url=url+"?"
  args="clear_filters=true"
  $("#%(id)s").find("[name=fi]").each(function(){
    if ($(this).val().length==0) {return}
    args=args+'&'+$(this).attr('id')+"="+encodeURIComponent($(this).val())
  })
  alert(url+args)
}
var inputs_%(id)s = %(a)s;"""%dict(
                   id=self.id,
                   a=self.ajax_inputs(),
                   ajax_submit=self.ajax_submit(),
                   ajax_enter_submit=self.ajax_enter_submit(),
                ),
                self.js_autorefresh(),
                _name=self.id+"_to_eval",
              ),
              _class='tableo',
            )
        return d

    def js_autorefresh(self):
        if self.autorefresh == 0:
            return ""
        else:
            return """
total=0
function autorefresh_%(id)s(){
  $("#%(id)s").stopTime();
  ajax_submit_%(id)s();
};
function countdown(){
  i=$("#countdown_%(id)s").html();
  if (i==0){
    ajax_changed("%(url)s", total, autorefresh_%(id)s)
    i=%(ar)d/1000;
    $("#countdown_%(id)s").html(i);
  };
  i--;
  total++
  $("#countdown_%(id)s").html(i)
  if (total < 60) {j=total + " seconds"}
  else if (total < 120) {j="1 minute"}
  else if (total < 3600) {j=parseInt(total/60) + " minutes"}
  else if (total < 7200) {j="1 hour"}
  else if (total < 86400) {j=parseInt(total/3600) + " hours"}
  else if (total < 172800) {j="1 day"}
  else {j=parseInt(total/86400) + " days"}
  $("#countup_%(id)s").html("refreshed "+j+" ago")
};
$("#%(id)s").stopTime();
$("#%(id)s").everyTime(1000, function(i){
  countdown()
});
"""%dict(id=self.id, ar=self.autorefresh, url=URL(r=request, c="dashboard", f="dash_changed"))

    def change_line_data(self, o):
        pass

    def csv_object_list(self):
        if self.csv_q is None:
            return self.object_list
        if self.csv_left is None:
            if self.csv_orderby is None:
                return db(self.csv_q).select(limitby=(0,self.csv_limit))
            else:
                return db(self.csv_q).select(orderby=self.csv_orderby, limitby=(0,self.csv_limit))
        else:
            if self.csv_orderby is None:
                return db(self.csv_q).select(limitby=(0,self.csv_limit), left=self.csv_left)
            else:
                return db(self.csv_q).select(orderby=self.csv_orderby, limitby=(0,self.csv_limit), left=self.csv_left)

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
                    v = repr(v).replace('\\n', '&#10;')
                    if v.startswith("u'"): v = v[1:]
                elif isinstance(v, datetime.datetime):
                    v = v.strftime("%Y-%m-%d %H:%M:%S")
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

#
# common column formatting
#
action_img_h = {
    'checks': 'check16.png',
    'pushservices': 'svc.png',
    'pushpkg': 'pkg16.png',
    'pushpatch': 'pkg16.png',
    'reboot': 'action_restart_16.png',
    'shutdown': 'action_stop_16.png',
    'syncservices': 'action_sync_16.png',
    'updateservices': 'action16.png',
    'stop': 'action_stop_16.png',
    'stopapp': 'action_stop_16.png',
    'stopdisk': 'action_stop_16.png',
    'stopvg': 'action_stop_16.png',
    'stoploop': 'action_stop_16.png',
    'stopip': 'action_stop_16.png',
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

os_img_h = {
  'darwin': 'darwin',
  'linux': 'linux',
  'hp-ux': 'hpux',
  'osf1': 'tru64',
  'opensolaris': 'opensolaris',
  'solaris': 'solaris',
  'sunos': 'solaris',
  'freebsd': 'freebsd',
  'aix': 'aix24',
  'windows': 'win24',
}

def node_icon(os_name):
    if os_name is None:
        return ''
    os_name = os_name.lower()
    if os_name in os_img_h:
        img = IMG(
                _src=URL(r=request,c='static',f=os_img_h[os_name]+'.png'),
                _class='logo'
              )
    else:
        img = ''
    return img

now = datetime.datetime.now()

class col_err(HtmlTableColumn):
    def html(self, o):
       d = self.get(o)
       if d is not None and d != "" and d != 0:
           return A(
                    DIV(d, _class="boxed_small bgred"),
                    _href=URL(r=request,c='svcactions',f='svcactions',
                              vars={'actions_f_svcname': o.svc_name,
                                    'actions_f_status': 'err',
                                    'actions_f_ack': '!1|empty',
                                    'clear_filters': 'true'}),
                  )

       return ""

class col_svc_ha(HtmlTableColumn):
    def html(self, o):
       d = self.get(o)
       if d == 1:
           return DIV("HA", _class="boxed_small")
       return ""

class col_updated(HtmlTableColumn):
    deadline = now - datetime.timedelta(days=1)

    def outdated(self, t):
         if t is None or t == '': return True
         if t < self.deadline: return True
         return False

    def html(self, o):
       d = self.get(o)
       if self.outdated(d):
           alert = 'color:darkred;font-weight:bold'
       else:
           alert = ''
       return SPAN(d, _style=alert)

class col_containertype(HtmlTableColumn):
    def html(self, o):
        id = self.t.extra_line_key(o)
        s = self.get(o)
        os = self.t.colprops['mon_guestos'].get(o)
        if (os is None or len(os) == 0):
            key = None
            if 'os_name' in self.t.cols:
                key = 'os_name'
            if key is not None:
                os = self.t.colprops[key].get(o)
        d = DIV(
              node_icon(os),
              A(
                s,
                _onclick="toggle_extra('%(url)s', '%(id)s');"%dict(
                  url=URL(r=request, c='ajax_node',f='ajax_node',
                          vars={'node': self.t.colprops['mon_vmname'].get(o),
                                'rowid': id}),
                  id=id,
                ),
              ),
              _class='nowrap',
            )
        return d

class col_node(HtmlTableColumn):
    def html(self, o):
        id = self.t.extra_line_key(o)
        s = self.get(o)
        if s is None or len(s) == 0:
            return ''
        if 'svc_autostart' in self.t.cols and \
           self.t.colprops['svc_autostart'].get(o) == s:
            c = 'font-weight: bold'
        else:
            c = ''
        if 'os_name' in self.t.colprops:
            img = node_icon(self.t.colprops['os_name'].get(o))
        else:
            img = ''
        d = DIV(
              img,
              A(
                s,
                _onclick="getElementById('%(id)s').innerHTML='%(spinner)s';toggle_extra('%(url)s', '%(id)s');"%dict(
                  url=URL(r=request, c='ajax_node',f='ajax_node',
                          vars={'node': s, 'rowid': id}),
                  id=id,
                  spinner=IMG(_src=URL(r=request,c='static',f='spinner.gif')),
                ),
                _style=c,
              ),
              _class='nowrap',
            )
        return d

class col_svc(HtmlTableColumn):
    def html(self, o):
        id = self.t.extra_line_key(o)
        s = self.get(o)
        if s is None:
            return ""
        d = DIV(
              A(
                s,
                _onclick="getElementById('%(id)s').innerHTML='%(spinner)s';toggle_extra('%(url)s', '%(id)s');"%dict(
                  url=URL(r=request, c='default',f='ajax_service',
                          vars={'node': s, 'rowid': id}),
                  id=id,
                  spinner=IMG(_src=URL(r=request,c='static',f='spinner.gif')),
                ),
              ),
            )
        return d

class col_status(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        if s is None or (type(self.t.colprops['mon_updated'].get(o)) == datetime.datetime and self.t.colprops['mon_updated'].get(o) < now - datetime.timedelta(minutes=15)):
            c = 'boxed_small boxed_status boxed_status_undef'
        else:
            c = 'boxed_small boxed_status boxed_status_'+s.replace(" ", "_")
        return DIV(s, _class=c)

class col_availstatus(HtmlTableColumn):
    def status_merge_down(self, s):
        if s == 'up': return 'warn'
        elif s == 'down': return 'down'
        elif s == 'stdby up': return 'stdby up with down'
        elif s == 'stdby up with up': return 'warn'
        elif s == 'stdby up with down': return 'stdby up with down'
        elif s == 'undef': return 'down'
        else: return 'undef'

    def status_merge_up(self, s):
        if s == 'up': return 'up'
        elif s == 'down': return 'warn'
        elif s == 'stdby up': return 'stdby up with up'
        elif s == 'stdby up with up': return 'stdby up with up'
        elif s == 'stdby up with down': return 'warn'
        elif s == 'undef': return 'up'
        else: return 'undef'

    def status_merge_stdby_up(self, s):
        if s == 'up': return 'stdby up with up'
        elif s == 'down': return 'stdby up with down'
        elif s == 'stdby up': return 'stdby up'
        elif s == 'stdby up with up': return 'stdby up with up'
        elif s == 'stdby up with down': return 'stdby up with down'
        elif s == 'undef': return 'stdby up'
        else: return 'undef'

    def get(self, o):
        # backward compat: mon_availstatus was not always available
        v = HtmlTableColumn.get(self, o)
        if v != 'undef':
            return v
        s = 'undef'
        for sn in ['mon_containerstatus',
                  'mon_ipstatus',
                  'mon_fsstatus',
                  'mon_appstatus',
                  'mon_diskstatus']:
            if self.t.colprops[sn].get(o) in ['warn', 'stdby down', 'todo']: return 'warn'
            elif self.t.colprops[sn].get(o) == 'undef': return 'undef'
            elif self.t.colprops[sn].get(o) == 'n/a': continue
            elif self.t.colprops[sn].get(o) == 'up': s = self.status_merge_up(s)
            elif self.t.colprops[sn].get(o) == 'down': s = self.status_merge_down(s)
            elif self.t.colprops[sn].get(o) == 'stdby up': s = self.status_merge_stdby_up(s)
            else: return 'undef'
        if s == 'stdby up with down':
            s = 'stdby up'
        elif s == 'stdby up with up':
            s = 'up'
        return s

    def html(self, o):
        cl = {}
        if self.t.colprops['mon_updated'].get(o) < now - datetime.timedelta(minutes=15):
            outdated = True
        else:
            outdated = False
        for k in ['mon_availstatus',
                  'mon_containerstatus',
                  'mon_ipstatus',
                  'mon_fsstatus',
                  'mon_diskstatus',
                  'mon_appstatus']:
            if k == 'mon_availstatus':
                s = self.get(o)
                a = s
            else:
                s = self.t.colprops[k].get(o)
            if s is None or outdated:
                cl[k] = 'status_undef'
            else:
                cl[k] = 'status_'+s.replace(" ", "_")

        t = TABLE(
          TR(
            TD(a,
               _colspan=5,
               _class='status '+cl['mon_availstatus'],
            ),
          ),
          TR(
            TD("vm", _class=cl['mon_containerstatus']),
            TD("ip", _class=cl['mon_ipstatus']),
            TD("fs", _class=cl['mon_fsstatus']),
            TD("dg", _class=cl['mon_diskstatus']),
            TD("app", _class=cl['mon_appstatus']),
          ),
        )
        return t

class col_overallstatus(HtmlTableColumn):
    def html(self, o):
        cl = {}
        if self.t.colprops['mon_updated'].get(o) < now - datetime.timedelta(minutes=15):
            outdated = True
        else:
            outdated = False
        for k in ['mon_overallstatus',
                  'mon_availstatus',
                  'mon_hbstatus',
                  'mon_syncstatus']:
            s = self.t.colprops[k].get(o)
            if s is None or outdated:
                cl[k] = 'status_undef'
            else:
                cl[k] = 'status_'+s.replace(" ", "_")

        t = TABLE(
          TR(
            TD(self.t.colprops['mon_overallstatus'].get(o),
               _colspan=3,
               _class='status '+cl['mon_overallstatus'],
            ),
          ),
          TR(
            TD("avail", _class=cl['mon_availstatus']),
            TD("hb", _class=cl['mon_hbstatus']),
            TD("sync", _class=cl['mon_syncstatus']),
          ),
        )
        return t

class col_env(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        c = ''
        if s == 'PRD':
            c = 'b'
        return SPAN(s, _class=c)

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
    'team_responsible',
    'team_integ',
    'team_support',
    'project',
    'serial',
    'model',
    'role',
    'host_mode',
    'environnement',
    'warranty_end',
    'maintenance_end',
    'status',
    'type',
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
    'responsibles',
    'mailto'
]

svcmon_cols = [
    'mon_vmname',
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
    'mon_syncstatus',
    'mon_appstatus',
    'mon_hbstatus'
]

v_services_colprops = {
    'svc_name': col_svc(
             title = 'Service',
             field='svc_name',
             display = False,
             img = 'svc',
             table = 'v_services',
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
    'svc_availstatus': col_status(
             title = 'Service availability status',
             field='svc_availstatus',
             display = True,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_status': col_status(
             title = 'Service overall status',
             field='svc_status',
             display = True,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_app': HtmlTableColumn(
             title = 'App',
             field='svc_app',
             display = False,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_ha': col_svc_ha(
             title = 'HA',
             field='svc_ha',
             display = True,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_containertype': col_containertype(
             title = 'Container type',
             field='svc_containertype',
             display = False,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_type': col_env(
             title = 'Service type',
             field='svc_type',
             display = False,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_autostart': col_node(
             title = 'Primary node',
             field='svc_autostart',
             display = False,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_nodes': HtmlTableColumn(
             title = 'Nodes',
             field='svc_nodes',
             display = False,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_drpnode': col_node(
             title = 'DRP node',
             field='svc_drpnode',
             display = False,
             img = 'svc',
             table = 'v_services',
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
    'svc_updated': col_updated(
             title = 'Last service update',
             field='updated',
             display = False,
             img = 'time16',
             table = 'v_services',
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
    'svc_version': col_svc(
             title = 'OpenSVC version',
             field='svc_version',
             display = False,
             img = 'pkg16',
             table = 'v_svcmon',
            ),
    'svc_envdate': col_svc(
             title = 'Env file date',
             field='svc_envdate',
             display = False,
             img = 'time16',
             table = 'v_svcmon',
            ),
}

v_svcmon_colprops = {
    'err': col_err(
             title = 'Action errors',
             field='err',
             display = False,
             img = 'action16',
             table = 'v_svcmon',
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
    'mon_svcname': col_svc(
             title = 'Service',
             field='mon_svcname',
             display = False,
             img = 'svc',
             table = 'svcmon',
            ),
    'mon_nodname': col_node(
             title = 'Node',
             field='mon_nodname',
             display = False,
             img = 'node16',
             table = 'svcmon',
            ),
    'mon_overallstatus': col_overallstatus(
             title = 'Status',
             field='mon_overallstatus',
             display = False,
             img = 'svc',
             table = 'svcmon',
            ),
    'mon_changed': HtmlTableColumn(
             title = 'Last status change',
             field='mon_changed',
             display = False,
             img = 'time16',
             table = 'svcmon',
            ),
    'mon_updated': col_updated(
             title = 'Last status update',
             field='mon_updated',
             display = False,
             img = 'time16',
             table = 'svcmon',
            ),
    'mon_frozen': HtmlTableColumn(
             title = 'Frozen',
             field='mon_frozen',
             display = False,
             img = 'svc',
             table = 'svcmon',
            ),
    'mon_containerstatus': col_status(
             title = 'Container status',
             field='mon_containerstatus',
             display = False,
             img = 'svc',
             table = 'svcmon',
            ),
    'mon_availstatus': col_availstatus(
             title = 'Availability status',
             field='mon_availstatus',
             display = True,
             img = 'svc',
             table = 'svcmon',
            ),
    'mon_ipstatus': col_status(
             title = 'Ip status',
             field='mon_ipstatus',
             display = False,
             img = 'svc',
             table = 'svcmon',
            ),
    'mon_fsstatus': col_status(
             title = 'Fs status',
             field='mon_fsstatus',
             display = False,
             img = 'svc',
             table = 'svcmon',
            ),
    'mon_diskstatus': col_status(
             title = 'Disk status',
             field='mon_diskstatus',
             display = False,
             img = 'svc',
             table = 'svcmon',
            ),
    'mon_syncstatus': col_status(
             title = 'Sync status',
             field='mon_syncstatus',
             display = False,
             img = 'svc',
             table = 'svcmon',
            ),
    'mon_appstatus': col_status(
             title = 'App status',
             field='mon_appstatus',
             display = False,
             img = 'svc',
             table = 'svcmon',
            ),
    'mon_hbstatus': col_status(
             title = 'Hb status',
             field='mon_hbstatus',
             display = False,
             img = 'svc',
             table = 'svcmon',
            ),
    'mon_vmname': col_node(
             title = 'Container name',
             field='mon_vmname',
             display = False,
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
    'node_updated': col_updated(
             title = 'Last node update',
             field='node_updated',
             display = False,
             img = 'time16',
             table = 'v_nodes',
            ),
    'updated': col_updated(
             title = 'Last node update',
             field='updated',
             display = False,
             img = 'time16',
             table = 'v_nodes',
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
    'nodename': col_node(
             title = 'Node name',
             field='nodename',
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
    'host_mode': col_env(
             title = 'Host Mode',
             field='host_mode',
             display = False,
             img = 'node16',
             table = 'v_nodes',
            ),
    'environnement': col_env(
             title = 'Env',
             field='environnement',
             display = False,
             img = 'node16',
             table = 'v_nodes',
            ),
    'warranty_end': HtmlTableColumn(
             title = 'Warranty end',
             field='warranty_end',
             display = False,
             img = 'node16',
             table = 'v_nodes',
            ),
    'maintenance_end': HtmlTableColumn(
             title = 'Maintenance end',
             field='maintenance_end',
             display = False,
             img = 'node16',
             table = 'v_nodes',
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


