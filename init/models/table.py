import re

class ToolError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

class Column(object):
    def __init__(self, title, display=False, img='generic', _class=''):
        self.title = title
        self.display = display
        self.img = img
        self._class = _class

class HtmlTableColumn(Column):
    def __init__(self, title, field, table=None, display=False,
                 img='generic', _class=''):
        Column.__init__(self, title, display, img, _class)
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
        self.additional_filters = []
        self.cols = []
        self.colprops = {}

        # to be set be instanciers
        self.checkboxes = False
        self.checkbox_names = [self.id+'_ck']
        self.checkbox_id_col = 'id'
        self.checkbox_id_table = None
        self.extraline = False
        self.extrarow = False
        self.filterable = True
        self.dbfilterable = True
        self.pageable = True
        self.exportable = True
        self.colored_lines = True
        self.additional_tools = []
        self.span = None
        self.flash = None
        self.sub_span = []

        # initialize the pager, to be re-executed by instanciers
        self.setup_pager()

        # drop stored filters if request asks for it
        self.drop_filters()

    def setup_pager(self, n=0):
        self.totalrecs = n
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
            l.append(A(
                       self.colprops[c].get(o),
                       ' ',
                       _class="cloud_tag",
                       _onclick="""
                         getElementById('%(id)s').value='%(val)s';
                       """%dict(id=self.filter_key(c),
                                val=self.colprops[c].get(o),
                               )+self.ajax_submit(),
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

    def persistent_filters(self):
        if not self.dbfilterable:
            return SPAN()

        id_session_div = '_'.join((self.id, 'session_div'))
        filters_count = active_db_filters_count()
        if filters_count > 0:
            filters_count = ' (%d)'%filters_count
        else:
            filters_count = ''

        s = SPAN(
              A(
                SPAN(
                  T('Persistent filters'),
                  _class='filters',
                ),
                filters_count,
                _onclick="""
                  click_toggle_vis('session_filters', 'block');
                  getElementById("%(div)s").innerHTML='%(spinner)s';
                  ajax('%(url)s', [], '%(div)s');
                """%dict(div=id_session_div,
                         spinner=IMG(_src=URL(r=request,c='static',f='spinner.gif')),
                         url=URL(r=request,c='ajax', f='ajax_db_filters', args=[id_session_div]),
                        ),
              ),
              DIV(
                _style='display:none',
                _class='white_float',
                _name='session_filters',
                _id=id_session_div,
              ),
              _class='floatw',
            )
        return s

    def columns_selector(self):
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
                    _onclick="""if (getElementById('%(fid)s').value.length==0) {
                                 check_toggle_vis(this.checked, "%(col_name)s");
                                 getElementById("%(id_set_col_table)s").value="%(table)s";
                                 getElementById("%(id_set_col_field)s").value="%(field)s";
                                 getElementById("%(id_set_col_value)s").value=this.checked;
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
                _onclick="click_toggle_vis('%(div)s', 'block')"%dict(
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

    def refresh(self):
        d = DIV(
              A(
                SPAN(
                  T('Refresh'),
                  _onclick=self.ajax_submit(),
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
            js = 'getElementById("%(id)s").value=%(n)s;'%dict(
                   id=self.id_perpage,
                   n=n)
            return js

        def set_page_js(page):
            js = 'getElementById("%(id)s").value=%(page)s;'%dict(
                   id=self.id_page,
                   page=page)
            js += self.ajax_submit()
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
        if end > self.totalrecs:
            end = self.totalrecs

        pager = []
        if page != 1:
            pager.append(A(
                           '<< ',
                           _class="current_page",
                           _onclick=set_page_js(page-1),
                         ))
        pager.append(A(
                      '%d-%d/%d '%(start+1, end, self.totalrecs),
                       _class="current_page",
                       _onclick="""click_toggle_vis('%(div)s','block');"""%dict(
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
                            _onclick=set_perpage_js(o)+self.ajax_submit()
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
            id = str(self.span_line_id(o)).replace('.','_')
        else:
            id = str(self.line_id(o)).replace('.','_')
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
        cp = self.colprops[f]
        if cp.table is None:
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
        q = db.column_filters.col_tableid==self.id
        q &= db.column_filters.col_name==field
        q &= db.column_filters.user_id==session.auth.user.id
        db(q).delete()

    def store_filter_value(self, f, v):
        field = self.stored_filter_field(f)
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
                            _class=self.colprops[c]._class,
                            _ondblclick="getElementById('%(k)s').value='%(v)s';"%dict(
                              k=self.filter_key(c),
                              v=v,
                             )+self.ajax_submit(),
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
        return TR(
                 TD(
                   _colspan=n,
                   _id=self.extra_line_key(o),
                   _style='display:none',
                 ),
                 _class=self.cellclass,
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
                clear = IMG(
                          _src=URL(r=request,c='static',f='clear16.png'),
                          _onclick="getElementById('%s').value='%s';"%(
                             self.filter_key(c),
                             self.column_filter_reset)+self.ajax_submit(),
                          _style="margin-right:4px",
                        )
            else:
                clear = SPAN()
            inputs.append(TD(
                            SPAN(
                              IMG(
                                _src=URL(r=request,c='static',f='filter16.png'),
                                _onClick="""click_toggle_vis('%(div)s','block');getElementById('%(input)s').focus();ajax('%(url)s', inputs_%(id)s, '%(cloud)s');"""%dict(
                                    id=self.id,
                                    div=self.filter_div_key(c),
                                    url=URL(r=request,f=self.ajax_col_values, args=[c]),
                                    cloud=self.filter_cloud_key(c),
                                    input=self.filter_key(c),
                                  ),
                                _class='clickable',
                              ),
                              clear,
                              self.filter_parse(c),
                              _style="vertical-align:top",
                            ),
                            DIV(
                              INPUT(
                                _id=self.filter_key(c),
                                _value=self.filter_parse(c),
                                _onKeyPress=self.ajax_enter_submit(),
                                _onKeyUp="""clearTimeout(timer);timer=setTimeout(function validate(){ajax('%(url)s', inputs_%(id)s, '%(cloud)s')}, 800);"""%dict(
                                    id=self.id,
                                    url=URL(r=request,f=self.func+'_col_values', args=[c]),
                                    inputs=','.join(map(repr, self.ajax_inputs())),
                                    cloud=self.filter_cloud_key(c)
                                  ),
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
                          ))
        return TR(inputs, _class='sym_headers')

    def table_additional_inputs(self):
        inputs = []
        for c in self.additional_filters:
            inputs.append(INPUT(
                    _id=self.filter_key(c),
                    _value=self.filter_parse(c),
                    _onKeyPress=self.ajax_enter_submit()
                  ))
        return inputs

    def ajax_submit(self, args=[], vars={}, additional_inputs=[]):
        return """table_ajax_submit('%(url)s', '%(id)s', %(inputs)s, %(additional_inputs)s, %(input_name)s);"""%dict(
                         url=URL(r=request,f=self.func, args=args, vars=vars),
                         id=self.innerhtml,
                         inputs = 'inputs_'+self.id,
                         additional_inputs = str(additional_inputs),
                         input_name=str(self.checkbox_names),
                        )

    def ajax_enter_submit(self, args=[], additional_inputs=[]):
        return """if (is_enter(event)){getElementById("tableid").value="%(id)s";%(ajax)s};"""%dict(
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

    def html(self):
        if len(request.args) == 1 and request.args[0] == 'csv':
            return self.csv()

        self.set_column_visibility()
        lines, line_count = self.table_lines()

        if self.filterable:
            inputs = self.table_inputs()
        else:
            inputs = SPAN()

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

        if len(self.additional_tools) > 0:
            additional_tools = SPAN(map(lambda x: getattr(self, x)(),
                                   self.additional_tools))
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
                  ),
                  _class='floatw',
                )
        else:
            export = SPAN()

        d = DIV(
              self.show_flash(),
              DIV(
                self.pager(),
                self.refresh(),
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
                  [self.table_header(),
                   inputs]+lines,
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
                "var inputs_%(id)s = %(a)s;"%dict(
                   id=self.id,
                   a=self.ajax_inputs(),
                ),
              ),
              _class='tableo',
            )
        return d

    def change_line_data(self, o):
        pass

    def _csv(self):
        lines = [';'.join(self.cols)]
        for i in self.object_list:
            if isinstance(i, str) or isinstance(i, unicode) or isinstance(i, int):
                o = self.object_list[i]
            else:
                o = i
            inf = []
            for c in self.cols:
                inf.append(repr(str(self.colprops[c].get(o))))
            lines.append(';'.join(inf))
        return '\n'.join(lines)

    def csv(self):
        import gluon.contenttype
        response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
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
    'stop': 'action_stop_16.png',
    'stopapp': 'action_stop_16.png',
    'stopdisk': 'action_stop_16.png',
    'stoploop': 'action_stop_16.png',
    'stopip': 'action_stop_16.png',
    'umount': 'action_stop_16.png',
    'start': 'action_start_16.png',
    'startstandby': 'action_start_16.png',
    'startapp': 'action_start_16.png',
    'startdisk': 'action_start_16.png',
    'startloop': 'action_start_16.png',
    'startip': 'action_start_16.png',
    'mount': 'action_start_16.png',
    'restart': 'action_restart_16.png',
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
}

os_img_h = {
  'darwin': 'darwin',
  'linux': 'linux',
  'hp-ux': 'hpux',
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
        os = self.t.colprops['svc_guestos'].get(o)
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
                          vars={'node': self.t.colprops['svc_vmname'].get(o),
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
                _onclick="toggle_extra('%(url)s', '%(id)s');"%dict(
                  url=URL(r=request, c='ajax_node',f='ajax_node',
                          vars={'node': s, 'rowid': id}),
                  id=id,
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
        d = DIV(
              A(
                s,
                _onclick="toggle_extra('%(url)s', '%(id)s');"%dict(
                  url=URL(r=request, c='default',f='ajax_service',
                          vars={'node': s, 'rowid': id}),
                  id=id,
                ),
              ),
            )
        return d

class col_status(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        c = 'status_undef'
        if s is not None:
            c = 'status_'+s.replace(" ", "_")
        return SPAN(s, _class=c)

class col_overallstatus(HtmlTableColumn):
    def html(self, o):
        cl = {}
        for k in ['mon_overallstatus',
                  'mon_containerstatus',
                  'mon_ipstatus',
                  'mon_fsstatus',
                  'mon_diskstatus',
                  'mon_syncstatus',
                  'mon_appstatus']:
            s = self.t.colprops[k].get(o)
            if s is None:
                cl[k] = 'status_undef'
            else:
                cl[k] = 'status_'+s.replace(" ", "_")

        t = TABLE(
          TR(
            TD(self.t.colprops['mon_overallstatus'].get(o),
               _colspan=6,
               _class='status '+cl['mon_overallstatus'],
            ),
          ),
          TR(
            TD("vm", _class=cl['mon_containerstatus']),
            TD("ip", _class=cl['mon_ipstatus']),
            TD("fs", _class=cl['mon_fsstatus']),
            TD("dg", _class=cl['mon_diskstatus']),
            TD("sync", _class=cl['mon_syncstatus']),
            TD("app", _class=cl['mon_appstatus']),
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
    'serial',
    'model',
    'role',
    'environnement',
    'warranty_end',
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
    'svc_app',
    'svc_type',
    'svc_drptype',
    'svc_containertype',
    'svc_vmname',
    'svc_vcpus',
    'svc_vmem',
    'svc_guestos',
    'svc_autostart',
    'svc_nodes',
    'svc_drpnode',
    'svc_drpnodes',
    'svc_comment',
    'svc_updated',
    'responsibles',
    'mailto'
]

svcmon_cols = [
    'mon_overallstatus',
    'mon_updated',
    'mon_frozen',
    'mon_containerstatus',
    'mon_ipstatus',
    'mon_fsstatus',
    'mon_diskstatus',
    'mon_syncstatus',
    'mon_appstatus'
]

v_services_colprops = {
    'svc_name': col_svc(
             title = 'Service',
             field='svc_name',
             display = False,
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
    'svc_vmname': col_node(
             title = 'Container name',
             field='svc_vmname',
             display = False,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_vcpus': HtmlTableColumn(
             title = 'Vcpus',
             field='svc_vcpus',
             display = False,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_vmem': HtmlTableColumn(
             title = 'Vmem',
             field='svc_vmem',
             display = False,
             img = 'svc',
             table = 'v_services',
            ),
    'svc_guestos': HtmlTableColumn(
             title = 'Guest OS',
             field='svc_guestos',
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
}

svcmon_colprops = {
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
}

v_nodes_colprops = {
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
    'role': HtmlTableColumn(
             title = 'Role',
             field='role',
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


