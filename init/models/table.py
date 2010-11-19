import re

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
        if self.table is None or self.table not in o:
            return o[self.field]
        else:
            return o[self.table][self.field]

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
        self.cellclass = 'cell2'
        self.upc_table = ''
        self.last = None

        # to be set by children
        self.additional_filters = []
        self.cols = []
        self.colprops = {}

        # to be set be instanciers
        self.checkboxes = False
        self.checkbox_names = [self.id+'_ck']
        self.checkbox_id_col = 'id'
        self.checkbox_id_table = None
        self.filterable = True
        self.dbfilterable = True
        self.pageable = True
        self.exportable = True
        self.colored_lines = True
        self.additional_tools = []
        self.span = None
        self.sub_span = []
        self.setup_pager()

    def setup_pager(self, n=0):
        self.totalrecs = n
        if self.pageable:
            if self.id_perpage in request.vars:
                self.perpage = int(request.vars[self.id_perpage])
            else:
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
                T('Persistent filters'),
                filters_count,
                _onclick="""
                  click_toggle_vis('session_filters', 'block');
                  getElementById("%(div)s").innerHTML='%(spinner)s';
                  ajax('%(url)s', [], '%(div)s');
                """%dict(div=id_session_div,
                         spinner=IMG(_src=URL(r=request,c='static',f='spinner_16.png')),
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
                    _onclick="""check_toggle_vis(this.checked, "%(col_name)s");
                                getElementById("%(id_set_col_table)s").value="%(table)s";
                                getElementById("%(id_set_col_field)s").value="%(field)s";
                                getElementById("%(id_set_col_value)s").value=this.checked;
                                ajax("%(url)s",
                                     ["%(id_set_col_table)s",
                                      "%(id_set_col_field)s",
                                      "%(id_set_col_value)s"],
                                     "set_col_dummy");
                             """%dict(url=URL(r=request,c='ajax',f='ajax_set_user_prefs_column'),
                                      col_name=self.col_key(a),
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
                T('Configure columns'),
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

        num_pages = 10
        def page_range():
            s = page - num_pages / 2
            e = page + num_pages / 2
            if s <= 0:
                e = e - s
                s = 1
            if e > totalpages:
                s = s - (e - totalpages)
                e = totalpages
            if s <= 0:
                s = 1
            return range(s, e+1)

        pr = page_range()
        pager = []
        if page != 1:
            pager.append(A(T('<< '), _onclick=set_page_js(page-1)))
        for p in pr:
            if p == page:
                pager.append(A(str(p)+' ', _class="current_page"))
            else:
                pager.append(A(str(p)+' ', _onclick=set_page_js(p)))
        if page != totalpages:
            pager.append(A(T('>> '), _onclick=set_page_js(page+1)))
        pager.append(A(T('all'), _onclick=set_page_js(0)))

        # paging toolbar
        info=T("Showing %(first)d to %(last)d out of %(total)d records",
               dict(first=start+1, last=end, total=self.totalrecs))
        nav = DIV(pager, _class='floatw', _title=info)

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

    def checkbox_key(self, o):
        if o is None:
            return '_'.join((self.id, 'ckid', ''))
        if self.checkbox_id_table is None or \
           self.checkbox_id_table not in o:
            id = o[self.checkbox_id_col]
        else:
            id = o[self.checkbox_id_table][self.checkbox_id_col]
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

    def filter_parse(self, f):
        key = self.filter_key(f)
        if key in request.vars:
            return request.vars[key]
        return ""

    def filter_parse_glob(self, f):
        val = self.filter_parse(f)
        if len(val) != 0:
           val = '%'+val+'%'
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
        for c in self.cols:
            cells.append(TH(T(self.colprops[c].title),
                            _style=self.col_hide(c),
                            _class=self.colprops[c]._class,
                            _name=self.col_key(c)))
        return TR(cells, _class='theader')

    def table_line(self, o):
        cells = []
        if self.checkboxes:
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
        for i in self.object_list:
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
                    self.rotate_colors()
                lines.append(self.table_line(o))
                if hasattr(self, 'format_extra_line'):
                    lines.append(TR(
                                   TD(
                                     self.format_extra_line(o),
                                     _colspan=len(self.cols),
                                   ),
                                   _class=self.cellclass,
                                 ))
                self.last = o
        return lines, line_count

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
        for c in self.cols:
            if len(self.filter_parse(c)) > 0:
                clear = IMG(
                          _src=URL(r=request,c='static',f='clear16.png'),
                          _onclick="getElementById('%s').value='';"%self.filter_key(c)+self.ajax_submit(),
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

    def ajax_submit(self, args=[], additional_inputs=[]):
        return """ajax("%(url)s",inputs_%(id)s.concat([%(inputs)s]).concat(getIdsByName(%(names)s)),"%(innerhtml)s");getElementById("%(innerhtml)s").innerHTML='%(spinner)s';"""%dict(
                         url=URL(r=request,f=self.func, args=args),
                         innerhtml=self.innerhtml,
                         id=self.id,
                         names=str(self.checkbox_names),
                         inputs = ','.join(map(repr, additional_inputs)),
                         spinner=IMG(_src=URL(r=request,c='static',f='spinner_16.png')),
                        )

    def ajax_enter_submit(self, args=[], additional_inputs=[]):
        return """if (is_enter(event)){getElementById("tableid").value="%(id)s";%(ajax)s};"""%dict(
                 ajax=self.ajax_submit(args=args,
                                       additional_inputs=additional_inputs),
                 id=self.id)

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
                    T('Export to csv'),
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
              DIV(
                self.pager(),
                export,
                self.columns_selector(),
                self.persistent_filters(),
                additional_tools,
                DIV('', _class='spacer'),
                _class='theader',
              ),
              additional_filters,
              TABLE(
                [self.table_header(),
                 inputs]+lines,
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
              DIV('', _class='spacer'),
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

