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
                 img='generic', _class='', _dataclass='', filter_redirect=None):
        Column.__init__(self, title, display, img, _class, _dataclass)
        self.table = table
        self.field = field
        self.filter_redirect = filter_redirect

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

        for s in sorted(h.keys()):
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

    def link(self):
        if not self.linkable:
            return SPAN()
        d = DIV(
              A(
                SPAN(
                  T('Link'),
                  _title=T("Share your view using this hyperlink"),
                  _onclick="""js_link("%s")"""%self.id,
                  _class='link16',
                  _id='link_'+self.id,
                ),
                SCRIPT(
                 """$(this).keypress(function(event) {
  if ($('input').is(":focus")) { return ; } ;
  if ($('textarea').is(":focus")) { return ; } ;
  if ( event.which == 108 ) {
     event.preventDefault();
     js_link("%s");
   }
});"""%self.id,
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
                  _onclick="ajax_table_refresh('%(url)s', '%(id)s')"%dict(
                    url=url,
                    id=self.id,
                  ),
                  _class='refresh16',
                  _id='refresh_'+self.id,
                ),
                _class='floatw',
              ),
              SCRIPT(
                 """$(this).keypress(function(event) {
  if ($('input').is(":focus")) { return ; } ;
  if ($('textarea').is(":focus")) { return ; } ;
  if ( event.which == 114 ) {
     //event.preventDefault();
     ajax_table_refresh("%(url)s", "%(id)s")
   }
});"""% dict(
                    url=url,
                    id=self.id,
                  ),
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
                  _onKeyUp="""if(is_enter(event)){%s}"""%self.ajax_submit(additional_inputs=['bookmark_name_input'+self.id]),
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
                        _onclick=self.ajax_submit(vars={'bookmark': row.bookmark}),
                      ),
                      A(
                        _class="del16",
                        _style="float:right;",
                        _onclick=self.ajax_submit(vars={'bookmark_del': row.bookmark}),
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

    def table_lines_data(self, n=0):
        wsenabled = self.get_wsenabled()
        if wsenabled == 'on' and self.perpage > self.max_live_perpage:
            max_perpage = self.max_live_perpage
        else:
            max_perpage = 500
        self.setup_pager(n, max_perpage=max_perpage)
        self.set_column_visibility()
        d = {
          'wsenabled': wsenabled,
          'pager': self.pager_info(),
          'table_lines': TABLE(self.table_lines()[0]).xml(),
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
        if hasattr(self.colprops[f], 'filter_redirect') and self.colprops[f].filter_redirect is not None:
            f = self.colprops[f].filter_redirect
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
        if len(db(q).select()) > 0:
            db(q).update(col_filter=v)
        else:
            db.column_filters.insert(col_tableid=self.id,
                                     col_name=field,
                                     col_filter=v,
                                     bookmark=bookmark,
                                     user_id=session.auth.user.id)

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
        bookmark_add = request.vars.get("bookmark_name_input"+self.id, "current")

        bookmark_del = request.vars.get("bookmark_del")
        if bookmark_del is not None:
            self.drop_filter_value(f, bookmark_del)

        bookmark = request.vars.get("bookmark", "current")
        if bookmark != "current":
            return self.stored_filter_value(f, bookmark)

        v = self._filter_parse(f)
        if v == self.column_filter_reset:
            self.drop_filter_value(f)
            key = self.filter_key(f)
            del(request.vars[key])
            return ""
        if request.vars.volatile_filters:
            _v = self.stored_filter_value(f, bookmark)
            if _v != "" and v != "":
                return v+"&"+_v
            if v == "":
                return _v
            return v
        if v == "":
            return self.stored_filter_value(f, bookmark)
        self.store_filter_value(f, v, bookmark_add)
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
                                 _onclick='this.value=this.checked',
                                 value=checked,
                               ),
                             ))

        if self.extrarow:
            cells.append(TD(self.format_extrarow(o)))

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
            _style=self.col_hide(c)
            classes = []
            if colprops._class != "":
                classes.append(colprops._class)
            if colprops._dataclass != "":
                classes.append(colprops._dataclass)
            if _style != '':
                classes.append("hidden")
            if len(classes) > 0:
                attrs['_class'] = ' '.join(classes)
            cells.append(TD(content, **attrs))
            if self.highlight:
                cl = "tl "
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

        if self.nodatabanner and len(object_list) == 0:
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
                            _onclick="filter_submit('%(id)s','%(k)s','%(v)s')"%dict(
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
        js ="""ajax("%(url)s/%(table)s/wsenabled/"+this.checked, [], "set_col_dummy");
            """%dict(url=URL(r=request,c='ajax',f='ajax_set_user_prefs_column2'),
                     table= self.upc_table,
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
              self.right_click_menu(),
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
                DIV(
                  XML("&nbsp;"),
                  _id="table_"+self.id+"_left",
                  _style="width:1em;position:absolute;left:0;z-index:1000;display:none",
                  _class="scroll_left",
                ),
                TABLE(
                   table_lines,
                   **table_attrs
                ),
                DIV(
                  XML("&nbsp;"),
                  _id="table_"+self.id+"_right",
                  _style="width:1em;position:absolute;right:0;z-index:1000;display:none",
                  _class="scroll_right",
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
table_cell_decorator("%(id)s")
$("input").each(function(){
 attr = $(this).attr('id')
 if ( typeof(attr) == 'undefined' || attr == false ) {return}
 if ( ! $(this).attr('id').match(/nodename/gi) && \
      ! $(this).attr('id').match(/svcname/gi) && \
      ! $(this).attr('id').match(/assetname/gi) && \
      ! $(this).attr('id').match(/mon_nodname/gi) && \
      ! $(this).attr('id').match(/disk_nodename/gi) && \
      ! $(this).attr('id').match(/disk_id/gi) && \
      ! $(this).attr('id').match(/disk_svcname/gi) && \
      ! $(this).attr('id').match(/save_nodename/gi) && \
      ! $(this).attr('id').match(/save_svcname/gi)
    ) {return}
 $(this).bind("change keyup input", function(){
  if (this.value.match(/ /g)) {
    if (this.value.match(/^\(/)) {return}
    this.value = this.value.replace(/ /g, ',')
    if (!this.value.match(/^\(/)) {
      this.value = '(' + this.value
    }
    if (!this.value.match(/\)$/)) {
      this.value = this.value + ')'
    }
  }
 })
})
$("select").parent().css("white-space", "nowrap");
$("select:visible").combobox();
function ajax_submit_%(id)s(){%(ajax_submit)s};
function ajax_enter_submit_%(id)s(event){%(ajax_enter_submit)s};

var inputs_%(id)s = %(a)s;
bind_filter_selector("%(id)s");
function scroll_%(id)s(){
  to=$("#table_%(id)s")
  to_p=to.parent()
  ww=$(window).width()
  tw=to.width()
  if (ww>=tw) {
    $("#table_%(id)s_left").hide()
    $("#table_%(id)s_right").hide()
    return
  }
  if (to_p.scrollLeft()>0) {
    $("#table_%(id)s_left").show()
    $("#table_%(id)s_left").height(to.height())
  } else {
    $("#table_%(id)s_left").hide()
  }
  if (to_p.scrollLeft()+ww<tw) {
    $("#table_%(id)s_right").show()
    $("#table_%(id)s_right").height(to.height())
    $("#table_%(id)s_right").css({'top': to.position().top})
  } else {
    $("#table_%(id)s_right").hide()
  }
}
$("#table_%(id)s_left").click(function(){
  $("#table_%(id)s").parent().animate({'scrollLeft': '-='+$(window).width()}, 500)
})
$("#table_%(id)s_right").click(function(){
  $("#table_%(id)s").parent().animate({'scrollLeft': '+='+$(window).width()}, 500)
})
$("#table_%(id)s").parent().scroll(function(){
  scroll_%(id)s()
})
$(window).resize(function(){
  scroll_%(id)s()
})
$(window).bind("DOMNodeInserted", function() {
  scroll_%(id)s()
})
$(".down16,.right16").click(function() {
  scroll_%(id)s()
})
scroll_%(id)s()
table_pager("%(id)s")
restripe_table_lines("%(id)s")
"""%dict(
                   id=self.id,
                   a=self.ajax_inputs(),
                   ajax_submit=self.ajax_submit(),
                   ajax_enter_submit=self.ajax_enter_submit(),
                ),
              ),
              _class='tableo',
            )
        return d

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

class col_date(HtmlTableColumn):
    def html(self, o):
       d = self.get(o)
       if d is None:
           return ''
       elif isinstance(d, datetime.datetime):
           return d.strftime('%Y-%m-%d')
       else:
           return d

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

class col_status(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        if 'mon_updated' in self.t.colprops:
            key = 'mon_updated'
        elif 'updated' in self.t.colprops:
            key = 'updated'
        else:
            raise Exception("no known updated key name")
        if s is None or (type(self.t.colprops[key].get(o)) == datetime.datetime and self.t.colprops[key].get(o) < now - datetime.timedelta(minutes=15)):
            c = 'boxed_small boxed_status boxed_status_undef'
        else:
            c = 'boxed_small boxed_status boxed_status_'+s.replace(" ", "_")
        return DIV(s, _class=c)

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
    'svc_containertype': HtmlTableColumn(
             title = 'Service mode',
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
    'svc_envdate': HtmlTableColumn(
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
    'mon_svctype': col_env(
             title = 'Service type',
             field='mon_svctype',
             display = False,
             img = 'svc',
             table = 'svcmon',
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
    'mon_updated': col_updated(
             title = 'Last status update',
             field='mon_updated',
             display = False,
             img = 'time16',
             table = 'svcmon',
             _class = 'datetime',
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
    'mon_availstatus': HtmlTableColumn(
             title = 'Availability status',
             field='mon_availstatus',
             display = True,
             img = 'svc',
             table = 'svcmon',
             _class = 'availstatus',
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
    'mon_sharestatus': col_status(
             title = 'Share status',
             field='mon_sharestatus',
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
    'node_updated': col_updated(
             title = 'Last node update',
             field='node_updated',
             display = False,
             img = 'time16',
             table = 'v_nodes',
             _class = 'datetime',
            ),
    'updated': col_updated(
             title = 'Last node update',
             field='updated',
             display = False,
             img = 'time16',
             table = 'v_nodes',
             _class = 'datetime',
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
    'warranty_end': col_date(
             title = 'Warranty end',
             field='warranty_end',
             display = False,
             img = 'time16',
             table = 'v_nodes',
             _class = 'datetime',
            ),
    'os_obs_warn_date': col_date(
             title = 'OS obsolescence warning date',
             field='os_obs_warn_date',
             display = False,
             img = 'time16',
             table = 'v_nodes',
             _class = 'datetime',
            ),
    'os_obs_alert_date': col_date(
             title = 'OS obsolescence alert date',
             field='os_obs_alert_date',
             display = False,
             img = 'time16',
             table = 'v_nodes',
             _class = 'datetime',
            ),
    'hw_obs_warn_date': col_date(
             title = 'Hardware obsolescence warning date',
             field='hw_obs_warn_date',
             display = False,
             img = 'time16',
             table = 'v_nodes',
             _class = 'datetime',
            ),
    'hw_obs_alert_date': col_date(
             title = 'Hardware obsolescence alert date',
             field='hw_obs_alert_date',
             display = False,
             img = 'time16',
             table = 'v_nodes',
             _class = 'datetime',
            ),
    'maintenance_end': col_date(
             title = 'Maintenance end',
             field='maintenance_end',
             display = False,
             img = 'time16',
             table = 'v_nodes',
             _class = 'datetime',
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
            ),
}

class col_disk_id(HtmlTableColumn):
    def html(self, o):
       d = self.get(o)
       return PRE(d)

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

class col_array_dg(HtmlTableColumn):
    def html(self, o):
        id = self.t.extra_line_key(o)
        dg = self.get(o)
        try:
            s = self.t.colprops['disk_arrayid'].get(o)
        except:
            s = self.t.colprops['array_name'].get(o)
        if dg is None or len(dg) == 0:
            return ''
        d = DIV(
              A(
                dg,
                _onclick="toggle_extra('%(url)s', '%(id)s', this, %(ncols)s);"%dict(
                  url=URL(r=request, c='disks',f='ajax_array_dg',
                          vars={'array': s, 'dg': dg, 'rowid': id}),
                  ncols=len(self.t.cols),
                  id=id,
                ),
                _class="bluer",
              ),
              _class='nowrap',
            )
        return d

class col_array(HtmlTableColumn):
    def html(self, o):
        id = self.t.extra_line_key(o)
        s = self.get(o)
        if s is None or len(s) == 0:
            return ''
        if 'array_model' in self.t.colprops:
            img = array_icon(self.t.colprops['array_model'].get(o))
        else:
            img = ''
        d = DIV(
              img,
              A(
                s,
                _onclick="toggle_extra('%(url)s', '%(id)s', this, %(ncols)s);"%dict(
                  url=URL(r=request, c='disks',f='ajax_array',
                          vars={'array': s, 'rowid': id}),
                  id=id,
                  ncols=len(self.t.cols),
                ),
                _class="bluer",
              ),
              _class='nowrap',
            )
        return d

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
    'disk_region': col_disk_id(
             title='Disk Region',
             table='b_disk_app',
             field='disk_region',
             img='hd16',
             display=False,
            ),
    'disk_id': col_disk_id(
             title='Disk Id',
             table='b_disk_app',
             field='disk_id',
             img='hd16',
             display=True,
             _dataclass="bluer",
            ),
    'disk_name': col_disk_id(
             title='Disk Name',
             table='b_disk_app',
             field='disk_name',
             img='hd16',
             display=True,
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
    'disk_used': col_size_mb(
             title='Disk Used',
             table='b_disk_app',
             field='disk_used',
             img='hd16',
             display=True,
            ),
    'disk_local': HtmlTableColumn(
             title='Disk Local',
             table='b_disk_app',
             field='disk_local',
             img='hd16',
             display=True,
            ),
    'disk_size': col_size_mb(
             title='Disk Size',
             table='b_disk_app',
             field='disk_size',
             img='hd16',
             display=True,
             _dataclass="bluer",
            ),
    'disk_alloc': col_size_mb(
             title='Disk Allocation',
             table='b_disk_app',
             field='disk_alloc',
             img='hd16',
             display=True,
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
    'disk_group': col_array_dg(
             title='Array disk group',
             table='b_disk_app',
             field='disk_group',
             img='hd16',
             display=True,
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
             _dataclass="bluer",
            ),
    'svcdisk_id': col_array(
             title='System Disk Id',
             table='b_disk_app',
             field='svcdisk_id',
             img='hd16',
             display=True,
             _dataclass="bluer",
            ),
    'disk_arrayid': col_array(
             title='Array Id',
             table='b_disk_app',
             field='disk_arrayid',
             img='hd16',
             display=True,
             _dataclass="bluer",
            ),
    'disk_devid': col_disk_id(
             title='Array device Id',
             table='b_disk_app',
             field='disk_devid',
             img='hd16',
             display=True,
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

