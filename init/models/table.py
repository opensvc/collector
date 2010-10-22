class table(object):
    def __init__(self, id=None, func=None, innerhtml=None):
        if innerhtml is None:
            innerhtml=id
        self.id = id
        self.innerhtml = innerhtml
        self.id_prefix = innerhtml
        self.func = func
        self.line_count = 0
        self.id_perpage = '_'.join((self.id_prefix, 'perpage'))
        self.id_page = '_'.join((self.id_prefix, 'page'))
        self.cellclasses = {'cell1': 'cell2', 'cell2': 'cell1'}
        self.cellclass = 'cell2'
        self.upc_table = ''

        # to be set by children
        self.additional_filters = []
        self.cols = []
        self.colprops = {}

        # to be set be instanciers
        self.filterable = True
        self.pageable = True
        self.exportable = True
        self.colored_lines = True

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
                self.pager_end = 0
            else:
                self.pager_start = (self.page-1) * self.perpage
                self.pager_end = self.pager_start + self.perpage - 1
        else:
            self.perpage = 0
            self.page = 0
            self.pager_start = 0
            self.pager_end = 0

    def get_column_visibility(self, c):
        if 'display' not in self.colprops[c]:
            return True
        return self.colprops[c]['display']

    def set_column_visibility(self):
        q = db.user_prefs_columns.upc_user_id==session.auth.user.id
        q &= db.user_prefs_columns.upc_table==self.upc_table
        rows = db(q).select()
        for row in rows:
            self.colprops[row.upc_field]['display'] = row.upc_visible

    def col_hide(self, c):
        id_col = self.col_checkbox_key(c)
        if self.get_column_visibility(c) or \
           (id_col in request.vars and request.vars[id_col] == 'on'):
            return ""
        else:
            return "display:none"

    def columns_selector(self):
        id_set_col_table = '_'.join((self.id_prefix, 'set_col_table'))
        id_set_col_field = '_'.join((self.id_prefix, 'set_col_field'))
        id_set_col_value = '_'.join((self.id_prefix, 'set_col_value'))
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
                    _onclick="""toggleVis(this.checked, "%(col_name)s");
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
                    self.colprops[a]['title'],
                    _style="""background-image:url(%s);
                              background-repeat:no-repeat;
                              padding-left:18px;
                              margin-left:0.2em;
                           """%URL(r=request,c='static',f=self.colprops[a]['img']+'.png'),
                  ),
                  BR(),
                )
            return s

        a = DIV(
              SCRIPT(
                """
                var showMode = 'table-cell';
                if (document.all) showMode='block';
                function toggleVis(checked, col){
                    cells = document.getElementsByName(col);
                    mode = checked ? showMode : 'none';
                    for(j = 0; j < cells.length; j++) {
                        cells[j].style.display = mode;
                    }
                }
                """
              ),
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
        return a

    def set_pager_max(self, n):
        self.totalrecs = n

    def pager(self):
        def set_perpage_js(n):
            js = 'getElementById("%(id)s").value=%(n)s;'%dict(
                   id=self.id_perpage,
                   n=n)
            return js

        def set_page_js(page):
            js = 'getElementById("%(id)s").value=%(page)s;'%dict(
                   id=self.id_page,
                   page=page)
            js += self.__ajax()
            return js

        start = 0
        end = 0

        if self.totalrecs == 0:
            return P("No records found matching filters", _style='text-align:center')
        if self.perpage <= 0:
            return P(
                     A(
                       T('reactivate paging'),
                       _onclick=set_perpage_js(20)+set_page_js(1),
                     ),
                     _style='text-align:center',
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
        nav = P(pager, _style='text-align:center', _title=info)

        return nav

    def rotate_colors(self):
        if not self.colored_lines:
            return
        self.cellclass = self.cellclasses[self.cellclass]

    def col_checkbox_key(self, f):
        return '_'.join((self.id_prefix, 'col', f))

    def col_key(self, f):
        return '_'.join((self.id_prefix, 'tcol', f))

    def filter_key(self, f):
        return '_'.join((self.id_prefix, 'filter', f))

    def filter_parse(self, f):
        key = self.filter_key(f)
        if key in request.vars:
            return request.vars[key]
        return ""

    def ajax_inputs(self):
        l = []
        if self.pageable:
            l.append(self.id_perpage)
            l.append(self.id_page)
        if self.filterable:
            l += map(self.filter_key, self.cols+self.additional_filters)
        return l

    def table_header(self):
        cells = []
        for c in self.cols:
            cells.append(TH(self.colprops[c]['title'],
                            _style=self.col_hide(c),
                            _name=self.col_key(c)))
        return TR(cells, _class='sym_headers')

    def table_line(self, o):
        cells = []
        for c in self.cols:
            cells.append(TD(self.colprops[c]['str'](o),
                            _name=self.col_key(c),
                            _style=self.col_hide(c),
                            _class=self.colprops[c]['_class'],
                            _ondblclick="getElementById('%(k)s').value='%(v)s';"%dict(k=self.filter_key(c),
v=self.colprops[c]['get'](o))+self.__ajax(),
                         ))
        return TR(cells, _class=self.cellclass)

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
                    if not _filter(self.filter_parse(c), self.colprops[c]['get'](o)):
                        skip = True
                        break
                if skip:
                    continue
            line_count += 1
            if not self.pageable or self.perpage == 0 or line_count <= self.perpage:
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
        return lines, line_count

    def table_inputs(self):
        inputs = []
        for c in self.cols:
            inputs.append(TD(
                            INPUT(
                              _id=self.filter_key(c),
                              _value=self.filter_parse(c),
                              _size=self.colprops[c]['size'],
                              _onKeyPress=self._ajax()
                            ),
                            _name=self.col_key(c),
                            _style=self.col_hide(c),
                          ))
        return TR(inputs, _class='sym_inputs')

    def table_additional_inputs(self):
        inputs = []
        for c in self.additional_filters:
            inputs.append(INPUT(
                    _id=self.filter_key(c),
                    _value=self.filter_parse(c),
                    _size=self.colprops[c]['size'],
                    _onKeyPress=self._ajax()
                  ))
        return inputs

    def __ajax(self):
        return """ajax("%(url)s",
                       ["tableid", %(inputs)s],
                       "%(innerhtml)s");
                  getElementById("%(innerhtml)s").innerHTML='%(spinner)s';
                """%dict(url=URL(r=request,f=self.func),
                         innerhtml=self.innerhtml,
                         inputs = ','.join(map(repr, self.ajax_inputs())),
                         spinner=IMG(_src=URL(r=request,c='static',f='spinner_16.png')),
                        )

    def _ajax(self):
        return """if (is_enter(event)) {
                    getElementById("tableid").value="%(id)s";
                    %(ajax)s
                  };
                  """%dict(ajax=self.__ajax(),
                           id=self.id)

    def table(self):
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

        if self.exportable:
            export = DIV(
                  A(
                    T('Export to csv'),
                    _href=URL(r=request,f=self.func+'_csv', vars=request.vars),
                  ),
                  _class='sym_float',
                )
        else:
            export = SPAN()

        d = DIV(
              self.columns_selector(),
              additional_filters,
              TABLE(
                self.table_header(),
                inputs,
                lines,
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
                self.pager(),
                export,
              ),
              DIV('', _class='spacer'),
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
                inf.append(repr(str(self.colprops[c]['str'](o))))
            lines.append(';'.join(inf))
        return '\n'.join(lines)

    def csv(self):
        import gluon.contenttype
        response.headers['Content-Type']=gluon.contenttype.contenttype('.csv')
        return self._csv()



