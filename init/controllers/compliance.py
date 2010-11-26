import datetime
now=datetime.datetime.today()
sevendays = str(now-datetime.timedelta(days=7,
                                       hours=now.hour,
                                       minutes=now.minute,
                                       seconds=now.second,
                                       microseconds=now.microsecond))

img_h = {0: 'check16.png',
         1: 'nok.png',
         2: 'na.png'}

import re
# ex: \x1b[37;44m\x1b[1mContact List\x1b[0m\n
regex = re.compile("\x1b\[([0-9]{1,3}(;[0-9]{1,3})*)?[m|K|G]", re.UNICODE)

def strip_unprintable(s):
    return regex.sub('', s)

#
# Sub-view menu
#
def comp_menu(current):
    m = [{
          'title': 'Status',
          'url': URL(
                   request.application,
                   'compliance',
                   'comp_status?ajax_comp_status_filter_run_date=>'+sevendays
                 ),
         },
         {
          'title': 'Log',
          'url': URL(
                   request.application,
                   'compliance',
                   'comp_log'
                 ),
         },
         {
          'title': 'Rules',
          'url': URL(
                   request.application,
                   'compliance',
                   'comp_rules'
                 ),
         },
         {
          'title': 'Modules',
          'url': URL(
                   request.application,
                   'compliance',
                   'comp_modules'
                 ),
         },
         {
          'title': 'Filters',
          'url': URL(
                   request.application,
                   'compliance',
                   'comp_filters'
                 ),
         },
        ]

    def item(i):
        if i['title'] == current:
            bg = 'orange'
        else:
            bg = '#DCDDE6'
        d = DIV(
              i['title'],
              _class='menu_item clickable',
              _style='background-color:%s'%bg,
              _onclick="location.href='%s'"%i['url'],
              _onmouseover="this.style.backgroundColor='orange'",
              _onmouseout="this.style.backgroundColor='%s'"%bg,
            )
        return d

    d = SPAN(map(lambda x: item(x), m))
    return d

#
# custom column formatting
#
class col_comp_node_status(HtmlTableColumn):
    def html(self, o):
        return DIV(
                 _id=nod_plot_id(o['mod_node']),
                 _style="height:50px;width:300px;",
               )

class col_comp_mod_status(HtmlTableColumn):
    def html(self, o):
        return DIV(
                 _id=mod_plot_id(o['mod_name']),
                 _style="height:50px;width:300px;",
               )

class col_variables(HtmlTableColumn):
    def html(self, o):
        val = self.get(o)
        if val is None:
            return SPAN()
        return PRE(val.replace('|','\n'))

class col_run_log(HtmlTableColumn):
    def html(self, o):
        lines = self.get(o).split('\n')
        for i, line in enumerate(lines):
            if line.startswith('ERR: '):
                lines[i] = PRE(
                             SPAN('ERR: ', _class='err'),
                             line[5:]+'\n',
                           )
            else:
                lines[i] = PRE(
                             line,
                           )
        return SPAN(lines)

class col_run_ruleset(HtmlTableColumn):
    def html(self, o):
        val = self.get(o)
        if val is None:
            return SPAN()
        return val.replace(',',', ')

class col_concat_list(HtmlTableColumn):
    def html(self, o):
        return ', '.join(self.get(o))

class col_mod_percent(HtmlTableColumn):
    def html(self, o):
        p = self.get(o)
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

class col_run_status(HtmlTableColumn):
    def html(self, o):
        val = self.get(o)
        if val in img_h:
            r = IMG(
                  _src=URL(r=request,c='static',f=img_h[val]),
                  _title=val,
                )
        else:
            r = val
        return r

class col_modset_mod_name(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        if s == '':
            ss = '(no name)'
        else:
            ss = s
        tid = 'd_t_%s_%s'%(o.comp_moduleset.id, o.comp_moduleset_modules.id)
        iid = 'd_i_%s_%s'%(o.comp_moduleset.id, o.comp_moduleset_modules.id)
        sid = 'd_s_%s_%s'%(o.comp_moduleset.id, o.comp_moduleset_modules.id)
        d = SPAN(
              SPAN(
                ss,
                _id=tid,
                _onclick="""hide_eid('%(tid)s');show_eid('%(sid)s');getElementById('%(iid)s').focus()"""%dict(tid=tid,
sid=sid, iid=iid),
                _class="clickable",
              ),
              SPAN(
                INPUT(
                  value=s,
                  _id=iid,
                  _onblur="""hide_eid('%(sid)s');show_eid('%(tid)s');"""%dict(sid=sid,
tid=tid),
                  _onkeypress="if (is_enter(event)) {%s};"%\
                     self.t.ajax_submit(additional_inputs=[iid],
                                        args="mod_name_set"),
                ),
                _id=sid,
                _style="display:none",
              ),
            )
        return d

class col_var_name(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        if s == '':
            ss = '(no name)'
        else:
            ss = s
        tid = 'nd_t_%s_%s'%(o.id, o.ruleset_id)
        iid = 'nd_i_%s_%s'%(o.id, o.ruleset_id)
        sid = 'nd_s_%s_%s'%(o.id, o.ruleset_id)
        d = SPAN(
              SPAN(
                ss,
                _id=tid,
                _onclick="""hide_eid('%(tid)s');show_eid('%(sid)s');getElementById('%(iid)s').focus()"""%dict(tid=tid,
sid=sid, iid=iid),
                _class="clickable",
              ),
              SPAN(
                INPUT(
                  value=s,
                  _id=iid,
                  _onblur="""hide_eid('%(sid)s');show_eid('%(tid)s');"""%dict(sid=sid,
tid=tid),
                  _onkeypress="if (is_enter(event)) {%s};"%\
                     self.t.ajax_submit(additional_inputs=[iid],
                                        args="var_name_set"),
                ),
                _id=sid,
                _style="display:none",
              ),
            )
        return d

class col_var_value(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        if s == '':
            ss = '(no value)'
        else:
            ss = s
        tid = 'vd_t_%s_%s'%(o.id, o.ruleset_id)
        iid = 'vd_i_%s_%s'%(o.id, o.ruleset_id)
        sid = 'vd_s_%s_%s'%(o.id, o.ruleset_id)
        d = SPAN(
              SPAN(
                ss,
                _id=tid,
                _onclick="""hide_eid('%(tid)s');show_eid('%(sid)s');getElementById('%(iid)s').focus()"""%dict(tid=tid,
sid=sid, iid=iid),
                _class="clickable",
              ),
              SPAN(
                INPUT(
                  value=s,
                  _id=iid,
                  _onblur="""hide_eid('%(sid)s');show_eid('%(tid)s');"""%dict(sid=sid,
tid=tid),
                  _onkeypress="if (is_enter(event)) {%s};"%\
                     self.t.ajax_submit(additional_inputs=[iid],
                                        args="var_value_set"),
                ),
                _id=sid,
                _style="display:none",
              ),
            )
        return d

#
# Rules sub-view
#
class table_comp_rulesets_nodes(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['nodename', 'rulesets'] + v_nodes_cols
        self.colprops = v_nodes_colprops
        self.colprops['rulesets'] = col_run_ruleset(
                     title='Rule set',
                     field='rulesets',
                     img='action16',
                     display=True,
                    )
        self.colprops['nodename'].display = True
        self.checkboxes = True
        self.additional_tools.append('ruleset_attach')
        self.additional_tools.append('ruleset_detach')
        self.ajax_col_values = 'ajax_comp_rulesets_rules_col_values'

    def ruleset_detach(self):
        d = DIV(
              A(
                T("Detach ruleset"),
                _onclick=self.ajax_submit(args=['detach_ruleset'],
                                          additional_inputs=self.rulesets.ajax_inputs()),
              ),
              _class='floatw',
            )
        return d

    def ruleset_attach(self):
        d = DIV(
              A(
                T("Attach ruleset"),
                _onclick=self.ajax_submit(args=['attach_ruleset'],
                                          additional_inputs=self.rulesets.ajax_inputs()),
              ),
              _class='floatw',
            )
        return d


class table_comp_explicit_rules(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['ruleset_name', 'variables']
        self.colprops = {
            'ruleset_name': HtmlTableColumn(
                     title='Rule set',
                     field='ruleset_name',
                     display=True,
                     img='action16',
                    ),
            'variables': col_variables(
                     title='Variables',
                     field='variables',
                     display=True,
                     img='action16',
                    ),
        }
        self.checkboxes = True
        self.dbfilterable = False
        self.exportable = False
        self.ajax_col_values = 'ajax_comp_explicit_rules_col_values'

@auth.requires_login()
def ajax_comp_explicit_rules_col_values():
    t = table_comp_explicit_rules('1', 'ajax_comp_rulesets_nodes',
                                  innerhtml='1')
    col = request.args[0]
    o = db.v_comp_explicit_rulesets[col]
    q = db.v_comp_explicit_rulesets.id > 0
    for f in t.cols:
        q = _where(q, 'v_comp_explicit_rulesets', t.filter_parse_glob(f), f)
    t.object_list = db(q).select(orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_comp_rulesets_rules_col_values():
    t = table_comp_rulesets_nodes('2', 'ajax_comp_rulesets_nodes',
                                  innerhtml='1')
    col = request.args[0]
    o = db.v_comp_nodes[col]
    q = _where(None, 'v_comp_nodes', domain_perms(), 'nodename')
    for f in t.cols:
        q = _where(q, 'v_comp_nodes', t.filter_parse_glob(f), f)
    t.object_list = db(q).select(orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_comp_rulesets_nodes():
    r = table_comp_explicit_rules('1', 'ajax_comp_rulesets_nodes',
                                  innerhtml='1')
    t = table_comp_rulesets_nodes('2', 'ajax_comp_rulesets_nodes',
                                  innerhtml='1')
    t.rulesets = r
    t.checkbox_names.append(r.id+'_ck')

    if len(request.args) == 1 and request.args[0] == 'attach_ruleset':
        comp_attach_rulesets(t.get_checked(), r.get_checked())
    elif len(request.args) == 1 and request.args[0] == 'detach_ruleset':
        comp_detach_rulesets(t.get_checked(), r.get_checked())

    o = db.v_comp_explicit_rulesets.ruleset_name
    q = db.v_comp_explicit_rulesets.id > 0
    for f in r.cols:
        q = _where(q, 'v_comp_explicit_rulesets', r.filter_parse_glob(f), f)

    n = db(q).count()
    r.setup_pager(n)
    r.object_list = db(q).select(limitby=(r.pager_start,r.pager_end), orderby=o)

    r_html = r.html()

    o = db.v_comp_nodes.nodename
    q = _where(None, 'v_comp_nodes', domain_perms(), 'nodename')
    for f in t.cols:
        q = _where(q, 'v_comp_nodes', t.filter_parse_glob(f), f)
    q = apply_db_filters(q, 'v_comp_nodes')

    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)

    if len(request.args) == 1 and request.args[0] == 'csv':
        return t.csv()

    return DIV(
             DIV(
               t.html(),
               _style="""min-width:60%;
                         max-width:60%;
                         float:left;
                         border-right:0px solid;
                      """,
             ),
             DIV(
               r_html,
               _style="""min-width:40%;
                         max-width:40%;
                         float:left;
                      """,
             ),
           )

class table_comp_rulesets(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['ruleset_name',
                     'ruleset_type',
                     'fset_name',
                     'var_name',
                     'var_value',
                     'var_updated',
                     'var_author',
                    ]
        self.colprops = {
            'var_updated': HtmlTableColumn(
                     title='Updated',
                     field='var_updated',
                     display=True,
                     img='action16',
                    ),
            'var_author': HtmlTableColumn(
                     title='Author',
                     field='var_author',
                     display=True,
                     img='guy16',
                    ),
            'ruleset_name': HtmlTableColumn(
                     title='Ruleset',
                     field='ruleset_name',
                     display=True,
                     img='action16',
                    ),
            'ruleset_type': HtmlTableColumn(
                     title='Ruleset type',
                     field='ruleset_type',
                     display=True,
                     img='action16',
                    ),
            'fset_name': HtmlTableColumn(
                     title='Filterset',
                     field='fset_name',
                     display=True,
                     img='filter16',
                    ),
            'var_value': col_var_value(
                     title='Value',
                     field='var_value',
                     display=True,
                     img='action16',
                    ),
            'var_name': col_var_name(
                     title='Variable',
                     field='var_name',
                     display=True,
                     img='action16',
                    ),
        }
        self.colprops['var_name'].t = self
        self.colprops['var_value'].t = self
        self.form_filterset_attach = self.comp_filterset_attach_sqlform()
        self.form_ruleset_var_add = self.comp_ruleset_var_add_sqlform()
        self.form_ruleset_add = self.comp_ruleset_add_sqlform()
        self.additional_tools.append('filterset_attach')
        self.additional_tools.append('filterset_detach')
        self.additional_tools.append('ruleset_var_add')
        self.additional_tools.append('ruleset_var_del')
        self.additional_tools.append('ruleset_del')
        self.additional_tools.append('ruleset_add')
        self.additional_tools.append('ruleset_rename')
        self.additional_tools.append('ruleset_clone')
        self.additional_tools.append('ruleset_change_type')
        self.ajax_col_values = 'ajax_comp_rulesets_col_values'

    def ruleset_change_type(self):
        label = 'Change ruleset type'
        action = 'ruleset_change_type'
        divid = 'rset_type_change'
        sid = 'rset_type_change_s'
        options = ['contextual', 'explicit']
        d = DIV(
              A(
                T(label),
                _onclick="""
                  click_toggle_vis('%(div)s', 'block');
                """%dict(div=divid),
              ),
              DIV(
                TABLE(
                  TR(
                    TH(T('Ruleset type')),
                    TD(
                      SELECT(
                        *options,
                        **dict(_id=sid)
                      ),
                    ),
                  ),
                  TR(
                    TH(),
                    TD(
                      INPUT(
                        _type='submit',
                        _onclick=self.ajax_submit(additional_inputs=[sid],
                                                  args=action),
                      ),
                    ),
                  ),
                ),
                _style='display:none',
                _class='white_float',
                _name=divid,
              ),
              _class='floatw',
            )
        return d

    def ruleset_clone(self):
        label = 'Clone ruleset'
        action = 'ruleset_clone'
        divid = 'rset_clone'
        sid = 'rset_clone_s'
        iid = 'rset_clone_i'
        q = db.comp_rulesets.id > 0
        o = db.comp_rulesets.ruleset_name
        options = [OPTION(g.ruleset_name,_value=g.id) for g in db(q).select(orderby=o)]
        d = DIV(
              A(
                T(label),
                _onclick="""
                  click_toggle_vis('%(div)s', 'block');
                """%dict(div=divid),
              ),
              DIV(
                TABLE(
                  TR(
                    TH(T('Ruleset')),
                    TD(
                      SELECT(
                        *options,
                        **dict(_id=sid,
                               _requires=IS_IN_DB(db, 'comp_rulesets.id'))
                      ),
                    ),
                  ),
                  TR(
                    TH(T('Clone name')),
                    TD(
                      INPUT(
                        _id=iid,
                        _requires=IS_NOT_IN_DB(db, 'comp_rulesets.ruleset_name')
                      ),
                    ),
                  ),
                  TR(
                    TH(),
                    TD(
                      INPUT(
                        _type='submit',
                        _onclick=self.ajax_submit(additional_inputs=[sid,iid],
                                                  args=action),
                      ),
                    ),
                  ),
                ),
                _style='display:none',
                _class='white_float',
                _name=divid,
              ),
              _class='floatw',
            )
        return d

    def checkbox_key(self, o):
        if o is None:
            return '_'.join((self.id, 'ckid', ''))
        ids = []
        ids.append(o['ruleset_id'])
        ids.append(o['fset_id'])
        ids.append(o['id'])
        return '_'.join([self.id, 'ckid']+map(str,ids))

    def ruleset_rename(self):
        d = DIV(
              A(
                T("Rename ruleset"),
                _onclick="""click_toggle_vis('%(div)s', 'block');
                         """%dict(div='comp_ruleset_rename'),
              ),
              DIV(
                INPUT(
                  _id='comp_ruleset_rename_input',
                  _onKeyPress=self.ajax_enter_submit(additional_inputs=['comp_ruleset_rename_input'],
                                                     args=['ruleset_rename']),
                ),
                _style='display:none',
                _class='white_float',
                _name='comp_ruleset_rename',
                _id='comp_ruleset_rename',
              ),
              _class='floatw',
            )
        return d

    def ruleset_del(self):
        d = DIV(
              A(
                T("Delete ruleset"),
                _onclick="""if (confirm("%(text)s")){%(s)s};
                         """%dict(s=self.ajax_submit(args=['ruleset_del']),
                                  text=T("Deleting a ruleset also deletes the ruleset variables, filters attachments and node attachments. Please confirm ruleset deletion."),
                                 ),
              ),
              _class='floatw',
            )
        return d

    def filterset_attach(self):
        d = DIV(
              A(
                T("Attach filterset"),
                _onclick="""
                  click_toggle_vis('%(div)s', 'block');
                """%dict(div='comp_filterset_attach'),
              ),
              DIV(
                self.form_filterset_attach,
                _style='display:none',
                _class='white_float',
                _name='comp_filterset_attach',
                _id='comp_filterset_attach',
              ),
              _class='floatw',
            )
        return d

    def filterset_detach(self):
        d = DIV(
              A(
                T("Detach filterset"),
                _onclick=self.ajax_submit(args=['filterset_detach']),
              ),
              _class='floatw',
            )
        return d

    def ruleset_add(self):
        d = DIV(
              A(
                T("Add ruleset"),
                _onclick="""
                  click_toggle_vis('%(div)s', 'block');
                """%dict(div='comp_ruleset_add'),
              ),
              DIV(
                self.form_ruleset_add,
                _style='display:none',
                _class='white_float',
                _name='comp_ruleset_add',
                _id='comp_ruleset_add',
              ),
              _class='floatw',
            )
        return d

    def comp_ruleset_add_sqlform(self):
        db.comp_rulesets.ruleset_name.readable = True
        db.comp_rulesets.ruleset_name.writable = True
        #db.comp_rulesets.ruleset_author.readable = False
        #db.comp_rulesets.ruleset_author.writable = False
        #db.comp_rulesets.ruleset_updated.readable = False
        #db.comp_rulesets.ruleset_updated.writable = False
        db.comp_rulesets.ruleset_name.requires = IS_NOT_IN_DB(db,
                                                db.comp_rulesets.ruleset_name)
        db.comp_rulesets.ruleset_type.requires = IS_IN_SET(['contextual',
                                                            'explicit'])
        f = SQLFORM(
                 db.comp_rulesets,
                 labels={'ruleset_name': T('Ruleset name')},
                 _name='form_ruleset_add',
            )
        f.vars.ruleset_type = 'explicit'
        #f.vars.ruleset_author = user_name()
        return f

    def ruleset_var_del(self):
        d = DIV(
              A(
                T("Delete variable"),
                _onclick=self.ajax_submit(args=['ruleset_var_del']),
              ),
              _class='floatw',
            )
        return d

    def ruleset_var_add(self):
        d = DIV(
              A(
                T("Add variable"),
                _onclick="""
                  click_toggle_vis('%(div)s', 'block');
                """%dict(div='comp_ruleset_var_add'),
              ),
              DIV(
                self.form_ruleset_var_add,
                _style='display:none',
                _class='white_float',
                _name='comp_ruleset_var_add',
                _id='comp_ruleset_var_add',
              ),
              _class='floatw',
            )
        return d

    def comp_filterset_attach_sqlform(self):
        if 'ruleset_id' in request.vars:
            ruleset_validator = IS_NOT_IN_DB(
                    db,
                    'comp_rulesets_filtersets.ruleset_id'
            )
        else:
            ruleset_validator = None
        db.comp_rulesets_filtersets.ruleset_id.requires = IS_IN_DB(
                    db(db.comp_rulesets.ruleset_type=='contextual'),
                    db.comp_rulesets.id,
                    "%(ruleset_name)s",
                    zero=T('choose one'),
                    _and=ruleset_validator)
        db.comp_rulesets_filtersets.fset_id.requires = IS_IN_DB(
                    db,
                    db.gen_filtersets.id,
                    "%(fset_name)s",
                    zero=T('choose one')
        )
        f = SQLFORM(
                 db.comp_rulesets_filtersets,
                 fields=['ruleset_id', 'fset_id'],
                 labels={'fset_id': T('Filter set name'),
                         'ruleset_id': T('Rule set name')},
                 _name='form_filterset_attach',
            )
        return f

    def comp_ruleset_var_add_sqlform(self):
        db.comp_rulesets_variables.id.readable = False
        db.comp_rulesets_variables.id.writable = False
        db.comp_rulesets_variables.ruleset_id.requires = IS_IN_DB(db,
                    db.comp_rulesets.id, "%(ruleset_name)s", zero=T('choose one'))
        f = SQLFORM(
                 db.comp_rulesets_variables,
                 labels={'ruleset_id': T('Ruleset name'),
                         'var_name': T('Variable'),
                         'var_value': T('Value')},
                 _name='form_var_add',
            )
        f.vars.var_author = user_name()
        return f

@auth.requires_membership('CompManager')
def ruleset_change_type(ids):
    sid = request.vars.rset_type_change_s
    if len(sid) == 0:
        raise ToolError("change ruleset type failed: target type is empty")
    if len(ids) == 0:
        raise ToolError("change ruleset type failed: no ruleset selected")
    ids = map(lambda x: int(x.split('_')[0]), ids)

    q = db.comp_rulesets.id.belongs(ids)
    rows = db(q).select()
    if len(rows) == 0:
        raise ToolError("change ruleset type failed: can't find ruleset")

    x = ', '.join(['from %s on %s'%(r.ruleset_type,r.ruleset_name) for r in rows])
    db(q).update(ruleset_type=sid)
    _log('comp.ruleset.type.change',
         'changed ruleset type to %(s)s %(x)s',
         dict(s=sid, x=x))

@auth.requires_membership('CompManager')
def ruleset_clone():
    sid = request.vars.rset_clone_s
    iid = request.vars.rset_clone_i
    if len(iid) == 0:
        raise ToolError("clone ruleset failed: invalid target name")
    if len(db(db.comp_rulesets.ruleset_name==iid).select()) > 0:
        raise ToolError("clone ruleset failed: target name already exists")
    q = db.v_comp_rulesets.ruleset_id==sid
    rows = db(q).select()
    if len(rows) == 0:
        raise ToolError("clone ruleset failed: can't find source ruleset")
    orig = rows[0].ruleset_name
    newid = db.comp_rulesets.insert(ruleset_name=iid,
                                    ruleset_type=rows[0].ruleset_type)
    if rows[0].ruleset_type == 'contextual':
        db.comp_rulesets_filtersets.insert(ruleset_id=newid,
                                           fset_id=rows[0].fset_id)
    for row in rows:
        db.comp_rulesets_variables.insert(ruleset_id=newid,
                                          var_name=row.var_name,
                                          var_value=row.var_value,
                                          var_author=user_name())
    _log('comp.ruleset.clone',
         'cloned ruleset %(o)s from %(n)s',
         dict(o=orig, n=iid))

@auth.requires_membership('CompManager')
def comp_rename_ruleset(ids):
    if len(ids) != 1:
        raise ToolError("rename ruleset failed: one ruleset must be selected")
    if 'comp_ruleset_rename_input' not in request.vars or \
       len(request.vars['comp_ruleset_rename_input']) == 0:
        raise ToolError("rename ruleset failed: new ruleset name is empty")
    new = request.vars['comp_ruleset_rename_input']
    if len(db(db.comp_rulesets.ruleset_name==new).select()) > 0:
        raise ToolError("rename ruleset failed: new ruleset name already exists")
    ids = map(lambda x: int(x.split('_')[0]), ids)
    id = ids[0]
    rows = db(db.comp_rulesets.id == id).select(db.comp_rulesets.ruleset_name)
    if len(rows) != 1:
        raise ToolError("rename ruleset failed: can't find source ruleset")
    old = rows[0].ruleset_name
    n = db(db.comp_rulesets.id == id).update(ruleset_name=new)
    _log('compliance.ruleset.rename',
        'renamed ruleset %(old)s as %(new)s',
        dict(old=old, new=new))

@auth.requires_membership('CompManager')
def comp_delete_ruleset(ids=[]):
    if len(ids) == 0:
        raise ToolError("delete ruleset failed: no ruleset selected")
    ids = map(lambda x: int(x.split('_')[0]), ids)
    rows = db(db.comp_rulesets.id.belongs(ids)).select(db.comp_rulesets.ruleset_name)
    x = ', '.join([str(r.ruleset_name) for r in rows])
    n = db(db.comp_rulesets_filtersets.ruleset_id.belongs(ids)).delete()
    n = db(db.comp_rulesets_variables.ruleset_id.belongs(ids)).delete()
    n = db(db.comp_rulesets.id.belongs(ids)).delete()
    _log('compliance.ruleset.delete',
         'deleted rulesets %(x)s',
         dict(x=x))

@auth.requires_membership('CompManager')
def comp_delete_ruleset_var(ids=[]):
    if len(ids) == 0:
        raise ToolError("delete variables failed: no variable selected")
    ids = map(lambda x: x.split('_')[2], ids)
    ids = [id for id in ids if id != 'None']
    ids = map(lambda x: int(x), ids)
    if len(ids) == 0:
        raise ToolError("delete variables failed: no variable selected")
    rows = db(db.v_comp_rulesets.id.belongs(ids)).select()
    x = map(lambda r: ' '.join((
                       r.var_name+'.'+r.var_value,
                       'from ruleset',
                       r.ruleset_name)), rows)
    x = ', '.join(set(x))
    n = db(db.comp_rulesets_variables.id.belongs(ids)).delete()
    _log('compliance.ruleset.variable.delete',
         'deleted ruleset variables %(x)s',
         dict(x=x))

@auth.requires_membership('CompManager')
def comp_detach_filterset(ids=[]):
    if len(ids) == 0:
        raise ToolError("detach filterset failed: no filterset selected")
    ruleset_ids = map(lambda x: int(x.split('_')[0]), ids)
    fset_ids = map(lambda x: int(x.split('_')[1]), ids)
    q = db.v_comp_rulesets.id < 0
    for ruleset_id, fset_id in zip(ruleset_ids, fset_ids):
        q |= ((db.v_comp_rulesets.ruleset_id == ruleset_id) & \
              (db.v_comp_rulesets.fset_id == fset_id))
    rows = db(q).select()
    x = map(lambda r: ' '.join((
                       r.fset_name,
                       'from ruleset',
                       r.ruleset_name)), rows)
    x = ', '.join(set(x))
    n = 0
    for ruleset_id, fset_id in zip(ruleset_ids, fset_ids):
        q = db.comp_rulesets_filtersets.fset_id == fset_id
        q &= db.comp_rulesets_filtersets.ruleset_id == ruleset_id
        n += db(q).delete()
    _log('compliance.ruleset.filterset.detach',
         'detached filterset %(x)s',
         dict(x=x))

@auth.requires_membership('CompManager')
def comp_detach_rulesets(node_ids=[], ruleset_ids=[]):
    if len(node_ids) == 0:
        raise ToolError("detach ruleset failed: no node selected")
    if len(ruleset_ids) == 0:
        raise ToolError("detach ruleset failed: no ruleset selected")

    q = db.v_nodes.id.belongs(node_ids)
    rows = db(q).select(db.v_nodes.nodename)
    node_names = [r.nodename for r in rows]
    nodes = ', '.join(node_names)

    for rsid in ruleset_ids:
        for node in node_names:
            q = db.comp_rulesets_nodes.nodename == node
            q &= db.comp_rulesets_nodes.ruleset_id == rsid
            db(q).delete()
    q = db.comp_rulesets.id.belongs(ruleset_ids)
    rows = db(q).select(db.comp_rulesets.ruleset_name)
    rulesets = ', '.join([r.ruleset_name for r in rows])
    _log('compliance.ruleset.node.detach',
         'detached rulesets %(rulesets)s from nodes %(nodes)s',
         dict(rulesets=rulesets, nodes=nodes))

@auth.requires_membership('CompManager')
def comp_attach_rulesets(node_ids=[], ruleset_ids=[]):
    if len(node_ids) == 0:
        raise ToolError("detach ruleset failed: no node selected")
    if len(ruleset_ids) == 0:
        raise ToolError("detach ruleset failed: no ruleset selected")

    q = db.v_nodes.id.belongs(node_ids)
    rows = db(q).select(db.v_nodes.nodename)
    node_names = [r.nodename for r in rows]
    nodes = ', '.join(node_names)

    for rsid in ruleset_ids:
        for node in node_names:
            q = db.comp_rulesets_nodes.nodename == node
            q &= db.comp_rulesets_nodes.ruleset_id == rsid
            if db(q).count() == 0:
                db.comp_rulesets_nodes.insert(nodename=node,
                                            ruleset_id=rsid)

    q = db.comp_rulesets.id.belongs(ruleset_ids)
    rows = db(q).select(db.comp_rulesets.ruleset_name)
    rulesets = ', '.join([r.ruleset_name for r in rows])
    _log('compliance.ruleset.node.attach',
         'attached rulesets %(rulesets)s to nodes %(nodes)s',
         dict(rulesets=rulesets, nodes=nodes))

@auth.requires_login()
def ajax_comp_rulesets_col_values():
    t = table_comp_rulesets('0', 'ajax_comp_rulesets')
    col = request.args[0]
    o = db.v_comp_rulesets[col]
    q = db.v_comp_rulesets.id > 0
    for f in t.cols:
        q = _where(q, 'v_comp_rulesets', t.filter_parse_glob(f), f)
    t.object_list = db(q).select(orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_comp_rulesets():
    v = table_comp_rulesets('0', 'ajax_comp_rulesets')
    v.span = 'ruleset_name'
    v.sub_span = ['ruleset_type', 'fset_name']
    v.checkboxes = True

    err = None
    if len(request.args) == 1:
       action = request.args[0]
       try:
           if action == 'filterset_detach':
               comp_detach_filterset(v.get_checked())
           elif action == 'var_name_set':
               var_name_set()
           elif action == 'var_value_set':
               var_value_set()
           elif action == 'ruleset_var_del':
               comp_delete_ruleset_var(v.get_checked())
           elif action == 'ruleset_change_type':
               ruleset_change_type(v.get_checked())
           elif action == 'ruleset_clone':
               ruleset_clone()
               v.form_filterset_attach = v.comp_filterset_attach_sqlform()
               v.form_ruleset_var_add = v.comp_ruleset_var_add_sqlform()
           elif action == 'ruleset_del':
               comp_delete_ruleset(v.get_checked())
               v.form_filterset_attach = v.comp_filterset_attach_sqlform()
               v.form_ruleset_var_add = v.comp_ruleset_var_add_sqlform()
           elif action == 'ruleset_rename':
               comp_rename_ruleset(v.get_checked())
               v.form_filterset_attach = v.comp_filterset_attach_sqlform()
               v.form_ruleset_var_add = v.comp_ruleset_var_add_sqlform()
       except ToolError, e:
           v.flash = str(e)

    if v.form_ruleset_add.accepts(request.vars, formname='add_ruleset'):
        # refresh forms ruleset comboboxes
        v.form_filterset_attach = v.comp_filterset_attach_sqlform()
        v.form_ruleset_var_add = v.comp_ruleset_var_add_sqlform()
        _log('compliance.ruleset.add',
             'added ruleset %(ruleset)s',
             dict(ruleset=request.vars.ruleset_name))
    elif v.form_ruleset_add.errors:
        response.flash = T("errors in form")

    if v.form_filterset_attach.accepts(request.vars):
        q = db.v_comp_rulesets.fset_id == request.vars.fset_id
        q &= db.v_comp_rulesets.ruleset_id == request.vars.ruleset_id
        rows = db(q).select()
        if len(rows) != 1:
            raise ToolError("filterset attach failed: can't find filterset")
        fset = rows[0].fset_name
        ruleset = rows[0].ruleset_name
        _log('compliance.ruleset.filterset.attach',
             'attached filterset %(fset)s to ruleset %(ruleset)s',
             dict(fset=fset, ruleset=ruleset))
    elif v.form_filterset_attach.errors:
        response.flash = T("errors in form")

    if v.form_ruleset_var_add.accepts(request.vars):
        var = '='.join((request.vars.var_name,
                        request.vars.var_value))
        ruleset = db(db.comp_rulesets.id==request.vars.ruleset_id).select(db.comp_rulesets.ruleset_name)[0].ruleset_name
        _log('compliance.ruleset.variable.add',
             'added ruleset variable %(var)s to ruleset %(ruleset)s',
             dict(var=var, ruleset=ruleset))
    elif v.form_ruleset_var_add.errors:
        response.flash = T("errors in form")

    o = db.v_comp_rulesets.ruleset_name|db.v_comp_rulesets.var_name
    q = db.v_comp_rulesets.ruleset_id > 0
    for f in v.cols:
        q = _where(q, 'v_comp_rulesets', v.filter_parse(f), f)

    n = db(q).count()
    v.setup_pager(n)
    v.object_list = db(q).select(limitby=(v.pager_start,v.pager_end), orderby=o)

    return v.html()

@auth.requires_login()
def comp_rules():
    t = DIV(
          comp_menu('Rules'),
          DIV(
            ajax_comp_rulesets(),
            _id='0',
          ),
          DIV(
            ajax_comp_rulesets_nodes(),
            _id='1',
          ),
        )
    return dict(table=t)

#
# Filters sub-view
#
filters_colprops = {
    'f_table': HtmlTableColumn(
             title='Table',
             field='f_table',
             display=True,
             img='filter16',
            ),
    'f_field': HtmlTableColumn(
             title='Field',
             field='f_field',
             display=True,
             img='filter16',
            ),
    'f_value': HtmlTableColumn(
             title='Value',
             field='f_value',
             display=True,
             img='filter16',
            ),
    'f_updated': HtmlTableColumn(
             title='Updated',
             field='f_updated',
             display=True,
             img='action16',
            ),
    'f_author': HtmlTableColumn(
             title='Author',
             field='f_author',
             display=True,
             img='guy16',
            ),
    'f_op': HtmlTableColumn(
             title='Operator',
             field='f_op',
             display=True,
             img='filter16',
            ),
}

filters_cols = ['f_table',
                'f_field',
                'f_op',
                'f_value',
                'f_updated',
                'f_author']

class table_comp_filtersets(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['fset_name',
                     'fset_updated',
                     'fset_author',
                     'f_log_op']
        self.cols += filters_cols

        self.colprops = {
            'fset_name': HtmlTableColumn(
                     title='Filterset',
                     field='fset_name',
                     display=True,
                     img='filter16',
                    ),
            'fset_updated': HtmlTableColumn(
                     title='Fset updated',
                     field='fset_updated',
                     display=False,
                     img='action16',
                    ),
            'fset_author': HtmlTableColumn(
                     title='Fset author',
                     field='fset_author',
                     display=False,
                     img='guy16',
                    ),
            'f_log_op': HtmlTableColumn(
                     title='Operator',
                     field='f_log_op',
                     display=True,
                     img='filter16',
                    ),
        }
        self.colprops.update(filters_colprops)
        self.form_filterset_add = self.comp_filterset_add_sqlform()
        self.form_filter_attach = self.comp_filter_attach_sqlform()
        self.additional_tools.append('filterset_rename')
        self.additional_tools.append('filterset_add')
        self.additional_tools.append('filterset_del')
        self.additional_tools.append('filter_attach')
        self.additional_tools.append('filter_detach')
        self.ajax_col_values = ajax_comp_filtersets_col_values

    def checkbox_key(self, o):
        if o is None:
            return '_'.join((self.id, 'ckid', ''))
        ids = []
        ids.append(o['fset_id'])
        ids.append(o['id'])
        return '_'.join([self.id, 'ckid']+map(str,ids))

    def filter_detach(self):
        d = DIV(
              A(
                T("Detach filters"),
                _onclick=self.ajax_submit(args=['detach_filters'])
              ),
              _class='floatw',
            )
        return d

    def filterset_rename(self):
        d = DIV(
              A(
                T("Rename filterset"),
                _onclick="""click_toggle_vis('%(div)s', 'block');
                         """%dict(div='comp_filterset_rename'),
              ),
              DIV(
                INPUT(
                  _id='comp_filterset_rename_input',
                  _onKeyPress=self.ajax_enter_submit(additional_inputs=['comp_filterset_rename_input'],
                                                     args=['filterset_rename']),
                ),
                _style='display:none',
                _class='white_float',
                _name='comp_filterset_rename',
                _id='comp_filterset_rename',
              ),
              _class='floatw',
            )
        return d

    def filterset_del(self):
        d = DIV(
              A(
                T("Delete filterset"),
                _onclick="""if (confirm("%(text)s")){%(s)s};
                         """%dict(s=self.ajax_submit(args=['delete_filterset']),
                                  text=T("Deleting a filterset also deletes the filterset filter attachments. Please confirm filterset deletion."),
                                 ),
              ),
              _class='floatw',
            )
        return d

    def filter_attach(self):
        d = DIV(
              A(
                T("Attach filter"),
                _onclick="""
                  click_toggle_vis('%(div)s', 'block');
                """%dict(div='comp_filter_attach'),
              ),
              DIV(
                self.form_filter_attach,
                _style='display:none',
                _class='white_float',
                _name='comp_filter_attach',
                _id='comp_filter_attach',
              ),
              _class='floatw',
            )
        return d

    def filterset_add(self):
        d = DIV(
              A(
                T("Add filterset"),
                _onclick="""
                  click_toggle_vis('%(div)s', 'block');
                """%dict(div='comp_filterset_add'),
              ),
              DIV(
                self.form_filterset_add,
                _style='display:none',
                _class='white_float',
                _name='comp_filterset_add',
                _id='comp_filterset_add',
              ),
              _class='floatw',
            )
        return d

    def comp_filter_attach_sqlform(self):
        db.gen_filtersets_filters.fset_id.readable = True
        db.gen_filtersets_filters.fset_id.writable = True
        db.gen_filtersets_filters.f_id.readable = True
        db.gen_filtersets_filters.f_id.writable = True
        db.gen_filtersets_filters.f_log_op.readable = True
        db.gen_filtersets_filters.f_log_op.writable = True
        db.gen_filtersets_filters.fset_id.requires = IS_IN_DB(
            db,
            db.gen_filtersets.id,
            "%(fset_name)s",
            zero=T('choose one')
        )
        if 'fset_id' in request.vars:
            q = db.gen_filtersets_filters.f_id == request.vars.f_id
            q &= db.gen_filtersets_filters.fset_id == request.vars.fset_id
            existing = db(q)
            f_id_validator = IS_NOT_IN_DB(existing, 'gen_filtersets_filters.f_id')
        else:
            f_id_validator = None

        db.gen_filtersets_filters.f_id.requires = IS_IN_DB(
            db,
            db.gen_filters.id,
            "%(f_table)s.%(f_field)s %(f_op)s %(f_value)s",
            zero=T('choose one'),
            _and=f_id_validator
        )


        f = SQLFORM(
                 db.gen_filtersets_filters,
                 labels={'fset_id': T('Filterset'),
                         'f_id': T('Filter'),
                         'f_log_op': T('Operator'),
                        },
                 _name='form_filterset_add',
            )

        # default values
        f.vars.f_log_op = 'AND'

        return f

    def comp_filterset_add_sqlform(self):
        db.gen_filtersets.fset_name.readable = True
        db.gen_filtersets.fset_name.writable = True
        db.gen_filtersets.fset_author.readable = False
        db.gen_filtersets.fset_author.writable = False
        db.gen_filtersets.fset_updated.readable = False
        db.gen_filtersets.fset_updated.writable = False
        db.gen_filtersets.fset_name.requires = IS_NOT_IN_DB(db, 'gen_filtersets.fset_name')

        f = SQLFORM(
                 db.gen_filtersets,
                 labels={'fset_name': T('Filterset name')},
                 _name='form_filterset_add',
            )

        # default values
        f.vars.fset_author = user_name()

        return f

@auth.requires_membership('CompManager')
def comp_detach_filters(ids=[]):
    if len(ids) == 0:
        raise ToolError("detach filter failed: no filter selected")
    ids = map(lambda x: int(x.split('_')[1]), ids)
    q = db.v_gen_filtersets.id.belongs(ids)
    rows = db(q).select()
    if len(rows) == 0:
        raise ToolError("detach filter failed: can't find selected filters")
    f_names = ', '.join(map(lambda f: ' '.join([
                       f.f_table+'.'+f.f_field,
                       f.f_op,
                       f.f_value,
                       'from',
                       f.fset_name]), rows))
    n = db(db.gen_filtersets_filters.id.belongs(ids)).delete()
    _log('compliance.filterset.filter.detach',
        'detached filters %(f_names)s',
        dict(f_names=f_names))

@auth.requires_membership('CompManager')
def comp_delete_filterset(ids=[]):
    if len(ids) == 0:
        raise ToolError("delete filterset failed: no filterset selected")
    ids = map(lambda x: int(x.split('_')[0]), ids)
    q = db.gen_filtersets.id.belongs(ids)
    rows = db(q).select()
    if len(rows) == 0:
        raise ToolError("delete filterset failed: can't find selected filtersets")
    fset_names = ', '.join([r.fset_name for r in rows])
    n = db(q).delete()
    _log('compliance.filterset.delete',
        'deleted filtersets %(fset_names)s',
        dict(fset_names=fset_names))

@auth.requires_membership('CompManager')
def comp_rename_filterset(ids):
    if len(ids) != 1:
        raise ToolError("rename filterset failed: one filterset must be selected")
    if 'comp_filterset_rename_input' not in request.vars or \
       len(request.vars['comp_filterset_rename_input']) == 0:
        raise ToolError("rename filterset failed: new filterset name is empty")
    new = request.vars['comp_filterset_rename_input']
    if len(db(db.comp_filtersets.fset_name==new).select()) > 0:
        raise ToolError("rename filterset failed: new filterset name already exists")
    ids = map(lambda x: int(x.split('_')[0]), ids)
    id = ids[0]
    rows = db(db.gen_filtersets.id == id).select(db.gen_filtersets.fset_name)
    if len(rows) != 1:
        raise ToolError("rename filterset failed: can't find selected filterset")
    old = rows[0].fset_name
    n = db(db.gen_filtersets.id == id).update(fset_name=new)
    _log('compliance.filterset.rename',
        'renamed filterset %(old)s as %(new)s',
        dict(old=old, new=new))

class table_comp_filters(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = filters_cols
        self.colprops = filters_colprops
        self.form_filter_add = self.comp_filters_add_sqlform()
        self.additional_tools.append('filter_add')
        self.additional_tools.append('filter_del')
        self.ajax_col_values = 'ajax_comp_filters_col_values'

    def filter_del(self):
        d = DIV(
              A(
                T("Delete filters"),
                _onclick=self.ajax_submit(args=['delete_filter']),
              ),
              _class='floatw',
            )
        return d

    def filter_add(self):
        d = DIV(
              A(
                T("Add filter"),
                _onclick="""
                  click_toggle_vis('%(div)s', 'block');
                """%dict(div='comp_filter_add'),
              ),
              DIV(
                self.form_filter_add,
                _style='display:none',
                _class='white_float',
                _name='comp_filter_add',
                _id='comp_filter_add',
              ),
              _class='floatw',
            )
        return d

    def comp_filters_add_sqlform(self):
        db.gen_filters.f_op.readable = True
        db.gen_filters.f_op.writable = True
        db.gen_filters.f_table.readable = True
        db.gen_filters.f_table.writable = True
        db.gen_filters.f_field.readable = True
        db.gen_filters.f_field.writable = True
        db.gen_filters.f_value.readable = True
        db.gen_filters.f_value.writable = True

        if 'f_op' in request.vars:
            q = db.gen_filters.f_op == request.vars.f_op
            q = db.gen_filters.f_table == request.vars.f_table
            q = db.gen_filters.f_field == request.vars.f_field
            q = db.gen_filters.f_value == request.vars.f_value
            existing = db(q)
            db.gen_filters.f_value.requires = IS_NOT_IN_DB(existing,
                                                          'gen_filters.f_value')

        f = SQLFORM(
                 db.gen_filters,
                 fields=['f_table',
                         'f_field',
                         'f_op',
                         'f_value'],
                 labels={'f_table': T('Table'),
                         'f_field': T('Field'),
                         'f_op': T('Operator'),
                         'f_value': T('Value')},
                 _name='form_filter_add',
            )

        # default values
        f.vars.f_op = '='
        f.vars.f_author = user_name()

        return f

@auth.requires_membership('CompManager')
def comp_delete_filter(ids=[]):
    if len(ids) == 0:
        raise ToolError("delete filter failed: no filter selected")
    q = db.gen_filters.id.belongs(ids)
    rows = db(q).select()
    if len(rows) == 0:
        raise ToolError("delete filter failed: can't find selected filters")
    f_names = ', '.join(map(lambda f: ' '.join([
                       f.f_table+'.'+f.f_field,
                       f.f_op,
                       f.f_value]), rows))
    n = db(q).delete()
    _log('compliance.filter.delete',
        'deleted filters %(f_names)s',
        dict(f_names=f_names))

@auth.requires_login()
def ajax_comp_filters_col_values():
    t = table_comp_filters('ajax_comp_filters', 'ajax_comp_filters')
    col = request.args[0]
    o = db.gen_filters[col]
    q = db.gen_filters.id > 0
    for f in t.cols:
        q = _where(q, 'gen_filters', t.filter_parse(f), f)
    t.object_list = db(q).select(orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_comp_filters():
    v = table_comp_filters('ajax_comp_filters',
                           'ajax_comp_filters')
    v.span = 'f_table'
    v.checkboxes = True

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'delete_filter':
                comp_delete_filter(v.get_checked())
        except ToolError, e:
            v.flash = str(e)

    if v.form_filter_add.accepts(request.vars):
        f_name = ' '.join([request.vars.f_table+'.'+request.vars.f_field,
                           request.vars.f_op,
                           request.vars.f_value])
        _log('compliance.filter.add',
            'added filter %(f_name)s',
            dict(f_name=f_name))
    elif v.form_filter_add.errors:
        response.flash = T("errors in form")

    o = db.gen_filters.f_table|db.gen_filters.f_field|db.gen_filters.f_op|db.gen_filters.f_field
    q = db.gen_filters.id > 0
    for f in v.cols:
        q = _where(q, 'gen_filters', v.filter_parse(f), f)

    n = db(q).count()
    v.setup_pager(n)
    v.object_list = db(q).select(limitby=(v.pager_start,v.pager_end), orderby=o)

    return v.html()

@auth.requires_login()
def ajax_comp_filtersets_col_values():
    t = table_comp_filtersets('ajax_comp_filtersets', 'ajax_comp_filtersets')
    col = request.args[0]
    o = db.v_gen_filtersets[col]
    q = db.v_gen_filtersets.fset_id > 0
    for f in t.cols:
        q = _where(q, 'v_gen_filtersets', t.filter_parse(f), f)
    t.object_list = db(q).select(orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_comp_filtersets():
    t = table_comp_filtersets('ajax_comp_filtersets',
                              'ajax_comp_filtersets')
    t.span = 'fset_name'
    t.checkboxes = True

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'delete_filterset':
                comp_delete_filterset(t.get_checked())
                t.form_filter_attach = t.comp_filter_attach_sqlform()
            elif action == 'detach_filters':
                comp_detach_filters(t.get_checked())
            elif action == 'filterset_rename':
                comp_rename_filterset(t.get_checked())
                t.form_filter_attach = t.comp_filter_attach_sqlform()
        except ToolError, e:
            t.flash = str(e)

    if t.form_filterset_add.accepts(request.vars):
        t.form_filter_attach = t.comp_filter_attach_sqlform()
        _log('compliance.filterset.add',
            'added filterset %(fset_name)s',
            dict(fset_name=request.vars.fset_name))
    elif t.form_filterset_add.errors:
        response.flash = T("errors in form")

    if t.form_filter_attach.accepts(request.vars):
        q = db.v_gen_filtersets.f_id==request.vars.f_id
        q &= db.v_gen_filtersets.fset_id==request.vars.fset_id
        f = db(db.v_gen_filtersets.f_id==request.vars.f_id).select()[0]
        f_name = ' '.join([request.vars.f_log_op,
                           f.f_table+'.'+f.f_field,
                           f.f_op,
                           f.f_value])
        _log('compliance.filterset.filter.attach',
            'filter %(f_name)s attached to filterset %(fset_name)s',
            dict(f_name=f_name, fset_name=f.fset_name))
    elif t.form_filter_attach.errors:
        response.flash = T("errors in form")

    o = db.v_gen_filtersets.fset_name|db.v_gen_filtersets.f_id
    q = db.v_gen_filtersets.fset_id > 0
    for f in t.cols:
        q = _where(q, 'v_gen_filtersets', t.filter_parse(f), f)

    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)

    return t.html()

@auth.requires_login()
def comp_filters():
    t = DIV(
          comp_menu('Filters'),
          DIV(
            ajax_comp_filters(),
            _id='ajax_comp_filters',
          ),
          DIV(
            ajax_comp_filtersets(),
            _id='ajax_comp_filtersets',
          ),
        )
    return dict(table=t)

#
# Modules sub-view
#
class table_comp_moduleset(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['modset_name',
                     'modset_mod_name',
                     'modset_mod_updated',
                     'modset_mod_author']
        self.colprops = {
            'modset_name': HtmlTableColumn(
                     title='Moduleset',
                     table='comp_moduleset',
                     field='modset_name',
                     display=True,
                     img='action16',
                    ),
            'modset_mod_name': col_modset_mod_name(
                     title='Module',
                     table='comp_moduleset_modules',
                     field='modset_mod_name',
                     display=True,
                     img='action16',
                    ),
            'modset_mod_updated': HtmlTableColumn(
                     title='Updated',
                     table='comp_moduleset_modules',
                     field='modset_mod_updated',
                     display=True,
                     img='action16',
                    ),
            'modset_mod_author': HtmlTableColumn(
                     title='Author',
                     table='comp_moduleset_modules',
                     field='modset_mod_author',
                     display=True,
                     img='guy16',
                    ),
        }
        self.colprops['modset_mod_name'].t = self
        self.form_module_add = self.comp_module_add_sqlform()
        self.form_moduleset_add = self.comp_moduleset_add_sqlform()
        self.additional_tools.append('module_add')
        self.additional_tools.append('module_del')
        self.additional_tools.append('moduleset_add')
        self.additional_tools.append('moduleset_del')
        self.additional_tools.append('moduleset_rename')

    def checkbox_key(self, o):
        if o is None:
            return '_'.join((self.id, 'ckid', ''))
        id1 = o['comp_moduleset']['id']
        id2 = o['comp_moduleset_modules']['id']
        return '_'.join((self.id, 'ckid', str(id1), str(id2)))

    def moduleset_rename(self):
        d = DIV(
              A(
                T("Rename moduleset"),
                _onclick="""click_toggle_vis('%(div)s', 'block');
                         """%dict(div='comp_moduleset_rename'),
              ),
              DIV(
                INPUT(
                  _id='comp_moduleset_rename_input',
                  _onKeyPress=self.ajax_enter_submit(additional_inputs=['comp_moduleset_rename_input'],
                                                     args=['moduleset_rename']),
                ),
                _style='display:none',
                _class='white_float',
                _name='comp_moduleset_rename',
                _id='comp_moduleset_rename',
              ),
              _class='floatw',
            )
        return d

    def moduleset_del(self):
        d = DIV(
              A(
                T("Delete moduleset"),
                _onclick="""if (confirm("%(text)s")){%(s)s};
                         """%dict(s=self.ajax_submit(args=['moduleset_del']),
                                  text=T("Deleting a moduleset also deletes the moduleset module attachments. Please confirm moduleset deletion."),
                                 ),
              ),
              _class='floatw',
            )
        return d

    def moduleset_add(self):
        d = DIV(
              A(
                T("Add moduleset"),
                _onclick="""
                  click_toggle_vis('%(div)s', 'block');
                """%dict(div='comp_moduleset_add'),
              ),
              DIV(
                self.form_moduleset_add,
                _style='display:none',
                _class='white_float',
                _name='comp_moduleset_add',
                _id='comp_moduleset_add',
              ),
              _class='floatw',
            )
        return d


    def module_del(self):
        d = DIV(
              A(
                T("Delete modules"),
                _onclick=self.ajax_submit(args=['module_del']),
              ),
              _class='floatw',
            )
        return d

    def module_add(self):
        d = DIV(
              A(
                T("Add module"),
                _onclick="""
                  click_toggle_vis('%(div)s', 'block');
                """%dict(div='comp_module_add'),
              ),
              DIV(
                self.form_module_add,
                _style='display:none',
                _class='white_float',
                _name='comp_module_add',
                _id='comp_module_add',
              ),
              _class='floatw',
            )
        return d

    def comp_moduleset_add_sqlform(self):
        db.comp_moduleset.modset_name.readable = True
        db.comp_moduleset.modset_name.writable = True
        db.comp_moduleset.modset_author.readable = False
        db.comp_moduleset.modset_author.writable = False
        db.comp_moduleset.modset_updated.readable = False
        db.comp_moduleset.modset_updated.writable = False
        db.comp_moduleset.modset_name.requires = IS_NOT_IN_DB(db,
                                                db.comp_moduleset.modset_name)
        f = SQLFORM(
                 db.comp_moduleset,
                 labels={'modset_name': T('Moduleset name')},
                 _name='form_moduleset_add',
            )
        f.vars.modset_author = user_name()
        return f

    def comp_module_add_sqlform(self):
        db.comp_moduleset_modules.modset_id.readable = True
        db.comp_moduleset_modules.modset_id.writable = True
        db.comp_moduleset_modules.modset_mod_name.readable = True
        db.comp_moduleset_modules.modset_mod_name.writable = True
        db.comp_moduleset_modules.modset_mod_author.readable = False
        db.comp_moduleset_modules.modset_mod_author.writable = False
        db.comp_moduleset_modules.modset_mod_updated.readable = False
        db.comp_moduleset_modules.modset_mod_updated.writable = False
        db.comp_moduleset_modules.modset_id.requires = IS_IN_DB(db,
                                                db.comp_moduleset.id,
                                                "%(modset_name)s",
                                                zero=T('choose one'))
        if 'modset_id' in request.vars:
            q = db.comp_moduleset_modules.modset_id == request.vars.modset_id
            db.comp_moduleset_modules.modset_mod_name.requires = IS_NOT_IN_DB(
                                db(q), 'comp_moduleset_modules.modset_mod_name')
        f = SQLFORM(
                 db.comp_moduleset_modules,
                 labels={'modset_id': T('Moduleset name'),
                         'modset_mod_name': T('Module name')},
                 _name='form_module_add',
            )
        f.vars.modset_mod_author = user_name()
        return f

@auth.requires_membership('CompManager')
def comp_delete_module(ids=[]):
    if len(ids) == 0:
        raise ToolError("delete module failed: no module selected")
    ids = map(lambda x: int(x.split('_')[1]), ids)
    rows = db(db.comp_moduleset_modules.id.belongs(ids)).select(db.comp_moduleset_modules.modset_mod_name)
    if len(rows) == 0:
        raise ToolError("delete module failed: can't find selected modules")
    mod_names = ', '.join([r.modset_mod_name for r in rows])
    n = db(db.comp_moduleset_modules.id.belongs(ids)).delete()
    _log('compliance.moduleset.module.delete',
        'deleted modules %(mod_names)s',
        dict(mod_names=mod_names))

@auth.requires_membership('CompManager')
def comp_delete_moduleset(ids=[]):
    if len(ids) == 0:
        raise ToolError("delete moduleset failed: no moduleset selected")
    ids = map(lambda x: int(x.split('_')[0]), ids)
    rows = db(db.comp_moduleset.id.belongs(ids)).select(db.comp_moduleset.modset_name)
    if len(rows) == 0:
        raise ToolError("delete moduleset failed: can't find selected modulesets")
    modset_names = ', '.join([r.modset_name for r in rows])
    n = db(db.comp_moduleset_modules.modset_id.belongs(ids)).delete()
    n = db(db.comp_node_moduleset.id.belongs(ids)).delete()
    n = db(db.comp_moduleset.id.belongs(ids)).delete()
    _log('compliance.moduleset.delete',
        'deleted modulesets %(modset_names)s',
        dict(modset_names=modset_names))

@auth.requires_membership('CompManager')
def comp_rename_moduleset(ids):
    if len(ids) != 1:
        raise ToolError("rename moduleset failed: one moduleset must be selected")
    if 'comp_moduleset_rename_input' not in request.vars:
        raise ToolError("rename moduleset failed: new moduleset name is empty")
    new = request.vars['comp_moduleset_rename_input']
    if len(db(db.comp_modulesets.modset_name==new).select()) > 0:
        raise ToolError("rename moduleset failed: new moduleset name already exists")
    id = int(ids[0].split('_')[0])
    rows = db(db.comp_moduleset.id == id).select(db.comp_moduleset.modset_name)
    if len(rows) != 1:
        raise ToolError("rename moduleset failed: can't find selected moduleset")
    old = rows[0].modset_name
    n = db(db.comp_moduleset.id == id).update(modset_name=new)
    _log('compliance.moduleset.rename',
         'renamed moduleset %(old)s as %(new)s',
         dict(old=old, new=new))

@auth.requires_membership('CompManager')
def mod_name_set():
    prefix = 'd_i_'
    l = [k for k in request.vars if prefix in k]
    if len(l) != 1:
        raise ToolError("set module name failed: misformated request")
    new = request.vars[l[0]]
    ids = l[0].replace(prefix,'').split('_')
    modset_id = int(ids[0])
    if ids[1] == 'None':
        # insert
        q = db.comp_moduleset.id==modset_id
        rows = db(q).select()
        modset_name = rows[0].modset_name
        db.comp_moduleset_modules.insert(modset_mod_name=new,
                                         modset_id=modset_id,
                                         modset_mod_author=user_name())
        _log('comp.moduleset.module.add',
             'add module %(d)s in moduleset %(x)s',
             dict(x=modset_name, d=new))
    else:
        # update
        id = int(ids[1])
        q = db.comp_moduleset_modules.id==id
        q1 = db.comp_moduleset_modules.modset_id==db.comp_moduleset.id
        rows = db(q&q1).select()
        n = len(rows)
        if n != 1:
            raise ToolError("set module name failed: can't find moduleset")
        modset_name = rows[0].comp_moduleset.modset_name
        q2 = db.comp_moduleset_modules.modset_mod_name==new
        q3 = db.comp_moduleset_modules.modset_id==modset_id
        n = len(db(q3&q2).select())
        if n != 0:
            raise ToolError("set module name failed: target module is already in moduleset")
        oldn = rows[0].comp_moduleset_modules.modset_mod_name
        db(q).update(modset_mod_name=new,
                     modset_mod_author=user_name(),
                     modset_mod_updated=now)
        _log('comp.moduleset.module.change',
             'change module name from %(on)s to %(d)s in moduleset %(x)s',
             dict(on=oldn, x=modset_name, d=new))

@auth.requires_login()
def ajax_comp_moduleset():
    t = table_comp_moduleset('ajax_comp_moduleset', 'ajax_comp_moduleset')
    t.span = 'modset_name'
    t.checkboxes = True
    t.checkbox_id_table = 'comp_moduleset_modules'

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'mod_name_set':
                mod_name_set()
                t.form_module_add = t.comp_module_add_sqlform()
            elif action == 'module_del':
                comp_delete_module(t.get_checked())
            elif action == 'moduleset_del':
                comp_delete_moduleset(t.get_checked())
                t.form_module_add = t.comp_module_add_sqlform()
            elif action == 'moduleset_rename':
                comp_rename_moduleset(t.get_checked())
                t.form_module_add = t.comp_module_add_sqlform()
        except ToolError, e:
            t.flash = str(e)

    if t.form_moduleset_add.accepts(request.vars, formname='add_moduleset'):
        t.form_module_add = t.comp_module_add_sqlform()
        _log('compliance.moduleset.add',
            'added moduleset %(modset_name)s',
            dict(modset_name=request.vars.modset_name))
    elif t.form_moduleset_add.errors:
        response.flash = T("errors in form")

    if t.form_module_add.accepts(request.vars, formname='add_module'):
        modset_name = db(db.comp_moduleset.id==request.vars.modset_id).select(db.comp_moduleset.modset_name)[0].modset_name
        _log('compliance.moduleset.module.add',
            'added module %(mod_name)s to moduleset %(modset_name)s',
            dict(mod_name=request.vars.modset_mod_name, modset_name=modset_name))
    elif t.form_module_add.errors:
        response.flash = T("errors in form")

    o = db.comp_moduleset.modset_name
    q = db.comp_moduleset.id > 0
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    join = db.comp_moduleset_modules.modset_id == db.comp_moduleset.id
    left = db.comp_moduleset_modules.on(join)
    rows = db(q).select(db.comp_moduleset_modules.id, left=left)
    t.setup_pager(len(rows))
    t.object_list = db(q).select(db.comp_moduleset_modules.ALL,
                                 db.comp_moduleset.modset_name,
                                 db.comp_moduleset.id,
                                 orderby=o,
                                 left=left,
                                 limitby=(t.pager_start,t.pager_end))

    return t.html()

@auth.requires_login()
def comp_modules():
    t = DIV(
          comp_menu('Modules'),
          DIV(
            ajax_comp_moduleset(),
            _id='ajax_comp_moduleset',
          ),
          DIV(
            #ajax_comp_modules_nodes(),
            _id='ajax_comp_modules_nodes',
          ),
        )
    return dict(table=t)

#
# Status sub-view
#
class table_comp_mod_status(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['mod_name', 'mod_total', 'mod_ok', 'mod_percent',
                     'mod_log', 'mod_nodes']
        self.colprops = {
            'mod_name': HtmlTableColumn(
                     title='Module',
                     field='mod_name',
                     display=True,
                     img='check16',
                    ),
            'mod_total': HtmlTableColumn(
                     title='Total',
                     field='mod_total',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'mod_ok': HtmlTableColumn(
                     title='Ok',
                     field='mod_ok',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'mod_percent': col_mod_percent(
                     title='Percent',
                     field='mod_percent',
                     display=True,
                     img='check16',
                     _class='comp_pct',
                    ),
            'mod_nodes': col_concat_list(
                     title='Nodes',
                     field='mod_nodes',
                     display=False,
                     img='node16',
                    ),
            'mod_log': col_comp_mod_status(
                     title='History',
                     field='mod_name',
                     display=True,
                     img='log16',
                     _class='comp_plot',
                    ),
        }

class table_comp_node_status(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['mod_node', 'mod_total', 'mod_ok', 'mod_percent',
                     'mod_log', 'mod_names']
        self.colprops = {
            'mod_node': HtmlTableColumn(
                     title='Node',
                     field='mod_node',
                     display=True,
                     img='node16',
                    ),
            'mod_total': HtmlTableColumn(
                     title='Total',
                     field='mod_total',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'mod_ok': HtmlTableColumn(
                     title='Ok',
                     field='mod_ok',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'mod_percent': col_mod_percent(
                     title='Percent',
                     field='mod_percent',
                     display=True,
                     img='check16',
                     _class='comp_pct',
                    ),
            'mod_names': col_concat_list(
                     title='Modules',
                     field='mod_names',
                     display=False,
                     img='check16',
                    ),
            'mod_log': col_comp_node_status(
                     title='History',
                     field='mod_node',
                     display=True,
                     img='log16',
                     _class='comp_plot',
                    ),
        }

@service.json
def json_nod_status_log(nodename):
    t = db.v_comp_node_status_weekly
    o = ~t.year|~t.week
    q = t.run_nodename == nodename
    d = []
    d_ok = []
    d_nok = []
    d_na = []
    rows = db(q).select(orderby=o, limitby=(0,50))
    for i in range(len(rows)-1, -1, -1):
        r = rows[i]
        d.append('w%d'%r.week)
        d_ok.append(int(r.nb_ok))
        d_nok.append(int(r.nb_nok))
        d_na.append(int(r.nb_na))
    return [d, [d_ok, d_nok, d_na]]

@service.json
def json_mod_status_log(module):
    t = db.v_comp_module_status_weekly
    o = ~t.year|~t.week
    q = t.run_module == module
    d = []
    d_ok = []
    d_nok = []
    d_na = []
    rows = db(q).select(orderby=o, limitby=(0,50))
    for i in range(len(rows)-1, -1, -1):
        r = rows[i]
        d.append('w%d'%r.week)
        d_ok.append(int(r.nb_ok))
        d_nok.append(int(r.nb_nok))
        d_na.append(int(r.nb_na))
    return [d, [d_ok, d_nok, d_na]]

@service.json
def json_run_status_log(nodename, module):
    c = db.comp_log.run_status
    o = db.comp_log.run_date
    q = db.comp_log.run_nodename == nodename
    q &= db.comp_log.run_action == 'check'
    q &= db.comp_log.run_module == module
    q &= db.comp_log.run_date > datetime.datetime.now() - datetime.timedelta(days=90)
    data = [r.run_status for r in db(q).select(c, orderby=o)]
    def enc(v):
        if v == 0: return 1
        elif v == 1: return -1
        else: return 0
    data = map(lambda x: enc(x), data)
    return data

def nod_plot_id(nodename):
    return 'nod_sparkl_%s'%(nodename).replace('.','_')

def nod_plot_url(nodename):
    return URL(r=request,
               f='call/json/json_nod_status_log/%(nodename)s'%dict(
                 nodename=nodename)
           )

def mod_plot_id(module):
    return 'mod_plot_%s'%(module).replace('.','_')

def mod_plot_url(module):
    return URL(r=request,
               f='call/json/json_mod_status_log/%(module)s'%dict(
                 module=module)
           )

def spark_id(nodename, module):
    return 'rh_%s_%s'%(nodename, module)

def spark_url(nodename, module):
    return URL(r=request,
               f='call/json/json_run_status_log/%(node)s/%(module)s'%dict(
                 node=nodename,
                 module=module)
           )

class table_comp_status_vfields(object):
        def run_status_log(self):
            return SPAN(
                     _id=spark_id(self.comp_status.run_nodename,
                                  self.comp_status.run_module)
                   )

def table_comp_status_add_vfields(t):
    db.comp_status.virtualfields.append(table_comp_status_vfields())
    t.cols.insert(5, 'run_status_log')

class table_comp_status(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['run_date',
                     'run_nodename',
                     'run_module',
                     'run_action',
                     'run_status',
                     'run_ruleset']
        self.cols += v_nodes_cols
        self.colprops = {
            'run_date': HtmlTableColumn(
                     title='Run date',
                     field='run_date',
                     table='comp_status',
                     img='check16',
                     display=True,
                    ),
            'run_nodename': HtmlTableColumn(
                     title='Node name',
                     field='run_nodename',
                     table='comp_status',
                     img='node16',
                     display=True,
                    ),
            'run_action': HtmlTableColumn(
                     title='Action',
                     field='run_action',
                     table='comp_status',
                     img='node16',
                     display=True,
                    ),
            'run_module': HtmlTableColumn(
                     title='Module',
                     field='run_module',
                     table='comp_status',
                     img='check16',
                     display=True,
                    ),
            'run_status': col_run_status(
                     title='Status',
                     field='run_status',
                     table='comp_status',
                     img='check16',
                     display=True,
                    ),
            'run_status_log': col_run_status(
                     title='History',
                     field='run_status_log',
                     table='comp_status',
                     img='check16',
                     display=True,
                    ),
            'run_log': col_run_log(
                     title='Log',
                     field='run_log',
                     table='comp_status',
                     img='check16',
                     display=True,
                    ),
            'run_ruleset': col_run_ruleset(
                     title='Rule set',
                     field='run_ruleset',
                     table='comp_status',
                     img='check16',
                     display=False,
                    ),
        }
        self.colprops.update(v_nodes_colprops)
        self.ajax_col_values = 'ajax_comp_status_col_values'

@auth.requires_membership('CompManager')
def var_name_set():
    var_set('name')

@auth.requires_membership('CompManager')
def var_value_set():
    var_set('value')

@auth.requires_membership('CompManager')
def var_set(t):
    prefix = t[0]+'d_i_'
    l = [k for k in request.vars if prefix in k]
    if len(l) != 1:
        raise ToolError("set variable name failed: misformated request")
    new = request.vars[l[0]]
    ids = l[0].replace(prefix,'').split('_')
    if ids[0] == 'None':
        # insert
        id = int(ids[1])
        q = db.v_comp_rulesets.ruleset_id==id
        rows = db(q).select()
        iid = rows[0].ruleset_name
        if t == 'name':
            db.comp_rulesets_variables.insert(var_name=new,
                                              ruleset_id=id,
                                              var_author=user_name())
        elif t == 'value':
            db.comp_rulesets_variables.insert(var_value=new,
                                              ruleset_id=id,
                                              var_author=user_name())
        else:
            raise Exception()
        _log('comp.ruleset.variable.add',
             'add variable %(t)s %(d)s for ruleset %(x)s',
             dict(t=t, x=iid, d=new))
    else:
        # update
        id = int(ids[0])
        q = db.comp_rulesets_variables.id==id
        q1 = db.comp_rulesets_variables.ruleset_id==db.comp_rulesets.id
        rows = db(q&q1).select()
        n = len(rows)
        if n != 1:
            raise ToolError("set variable name failed: can't find ruleset")
        iid = rows[0].comp_rulesets.ruleset_name
        oldn = rows[0].comp_rulesets_variables.var_name
        oldv = rows[0].comp_rulesets_variables.var_value
        if t == 'name':
            db(q).update(var_name=new,
                         var_author=user_name(),
                         var_updated=now)
            _log('comp.ruleset.variable.change',
                 'renamed variable %(on)s to %(d)s in ruleset %(x)s',
                 dict(on=oldn, x=iid, d=new))
        elif t == 'value':
            db(q).update(var_value=new,
                         var_author=user_name(),
                         var_updated=now)
            _log('comp.ruleset.variable.change',
                 'change variable %(on)s value from %(ov)s to %(d)s in ruleset %(x)s',
                 dict(on=oldn, ov=oldv, x=iid, d=new))
        else:
            raise Exception()

@auth.requires_login()
def ajax_comp_log_col_values():
    t = table_comp_log('ajax_comp_log', 'ajax_comp_log')
    col = request.args[0]
    o = db.comp_log[col]
    q = _where(None, 'comp_log', domain_perms(), 'run_nodename')
    q &= db.comp_log.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_db_filters(q, 'v_nodes')
    t.object_list = db(q).select(orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_comp_status_col_values():
    t = table_comp_status('0', 'ajax_comp_status')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    q &= db.comp_status.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_db_filters(q, 'v_nodes')
    t.object_list = db(q).select(orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_comp_status():
    t = table_comp_status('0', 'ajax_comp_status')

    o = ~db.comp_status.run_nodename
    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    q &= db.comp_status.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_db_filters(q, 'v_nodes')

    n = db(q).count()
    t.setup_pager(n)
    all = db(q).select(db.comp_status.ALL, db.v_nodes.id)
    table_comp_status_add_vfields(t)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)

    mt = table_comp_mod_status('1', 'ajax_comp_mod_status')
    mt.object_list = compute_mod_status(all)
    mt.pageable = False
    mt.filterable = False
    mt.exportable = False
    mt.dbfilterable = False

    nt = table_comp_node_status('2', 'ajax_comp_node_status')
    nt.object_list = compute_node_status(all)
    nt.pageable = False
    nt.filterable = False
    nt.exportable = False
    nt.dbfilterable = False

    if len(request.args) == 1 and request.args[0] == 'csv':
        return t.csv()

    spark_cmds = ""
    for r in t.object_list:
        spark_cmds += "sparkl('%(url)s', '%(id)s');"%dict(
          url=spark_url(r.comp_status.run_nodename, r.comp_status.run_module),
          id=spark_id(r.comp_status.run_nodename, r.comp_status.run_module),
        )
    for r in mt.object_list:
        spark_cmds += "comp_status_plot('%(url)s', '%(id)s');"%dict(
          url=mod_plot_url(r['mod_name']),
          id=mod_plot_id(r['mod_name']),
        )
    for r in nt.object_list:
        spark_cmds += "comp_status_plot('%(url)s', '%(id)s');"%dict(
          url=nod_plot_url(r['mod_node']),
          id=nod_plot_id(r['mod_node']),
        )
    return DIV(
             SCRIPT(spark_cmds, _name=t.id+"_to_eval"),
             mt.html(),
             nt.html(),
             t.html(),
           )

def compute_mod_status(rows):
    h = {}
    for r in rows:
        if r.comp_status.run_module not in h:
            h[r.comp_status.run_module] = {
              'mod_name': r.comp_status.run_module,
              'mod_total': 0,
              'mod_ok': 0,
              'mod_percent': 0,
              'mod_nodes': [],
            }
        h[r.comp_status.run_module]['mod_total'] += 1
        h[r.comp_status.run_module]['mod_nodes'].append(r.comp_status.run_nodename)
        if r.comp_status.run_status == 0:
            h[r.comp_status.run_module]['mod_ok'] += 1
    for m in h.values():
        if m['mod_total'] == 0:
            continue
        m['mod_percent'] = int(100*m['mod_ok']/m['mod_total'])
    return sorted(h.values(), key=lambda x: (x['mod_percent'], x['mod_name']))

def compute_node_status(rows):
    h = {}
    for r in rows:
        if r.comp_status.run_nodename not in h:
            h[r.comp_status.run_nodename] = {
              'mod_names': [],
              'mod_total': 0,
              'mod_ok': 0,
              'mod_percent': 0,
              'mod_node': r.comp_status.run_nodename,
            }
        h[r.comp_status.run_nodename]['mod_total'] += 1
        h[r.comp_status.run_nodename]['mod_names'].append(r.comp_status.run_module)
        if r.comp_status.run_status == 0:
            h[r.comp_status.run_nodename]['mod_ok'] += 1
    for m in h.values():
        if m['mod_total'] == 0:
            continue
        m['mod_percent'] = int(100*m['mod_ok']/m['mod_total'])
    return sorted(h.values(), key=lambda x: (x['mod_percent'],x['mod_node']))

@auth.requires_login()
def comp_status():
    t = DIV(
          comp_menu('Status'),
          DIV(
            ajax_comp_status(),
            _id='0',
          ),
        )
    return dict(table=t)

class table_comp_log(table_comp_status):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        table_comp_status.__init__(self, id, 'ajax_comp_log', innerhtml)
        self.cols = ['run_date', 'run_nodename', 'run_module', 'run_action',
                     'run_status', 'run_log', 'run_ruleset']
        self.cols += v_nodes_cols
        for c in self.colprops:
            if 'run_' in c:
                self.colprops[c].table = 'comp_log'
        self.ajax_col_values = 'ajax_comp_log_col_values'

@auth.requires_login()
def ajax_comp_log():
    t = table_comp_log('ajax_comp_log', 'ajax_comp_log')

    db.commit()
    o = ~db.comp_log.run_date
    q = _where(None, 'comp_log', domain_perms(), 'run_nodename')
    q &= db.comp_log.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_db_filters(q, 'v_nodes')

    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return t.html()


@auth.requires_login()
def comp_log():
    t = DIV(
          comp_menu('Log'),
          DIV(
            ajax_comp_log(),
            _id='ajax_comp_log',
          ),
        )
    return dict(table=t)

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

@service.xmlrpc
def comp_get_moduleset_modules(moduleset):
    if isinstance(moduleset, list):
        if len(moduleset) == 0:
            return []
        q = db.comp_moduleset.modset_name.belongs(moduleset)
    elif isinstance(moduleset, str):
        q = db.comp_moduleset.modset_name == moduleset
    else:
        return []
    q &= db.comp_moduleset_modules.modset_id == db.comp_moduleset.id
    rows = db(q).select(db.comp_moduleset_modules.modset_mod_name,
                        groupby=db.comp_moduleset_modules.modset_mod_name)
    return [r.modset_mod_name for r in rows]

def comp_moduleset_id(moduleset):
    q = db.comp_moduleset.modset_name == moduleset
    rows = db(q).select(db.comp_moduleset.id)
    if len(rows) == 0:
        return None
    return rows[0].id

def comp_moduleset_attached(nodename, modset_id):
    q = db.comp_node_moduleset.modset_node == nodename
    q &= db.comp_node_moduleset.modset_id == modset_id
    if len(db(q).select(db.comp_node_moduleset.id)) == 0:
        return False
    return True

def comp_ruleset_exists(ruleset):
    q = db.v_comp_explicit_rulesets.ruleset_name == ruleset
    rows = db(q).select(db.v_comp_explicit_rulesets.id)
    if len(rows) != 1:
        return None
    return rows[0].id

def comp_ruleset_attached(nodename, ruleset_id):
    q = db.comp_rulesets_nodes.nodename == nodename
    q &= db.comp_rulesets_nodes.ruleset_id == ruleset_id
    if len(db(q).select(db.comp_rulesets_nodes.id)) == 0:
        return False
    return True

@service.xmlrpc
def comp_attach_moduleset(nodename, moduleset):
    if len(moduleset) == 0:
        return dict(status=False, msg="no moduleset specified"%moduleset)
    modset_id = comp_moduleset_id(moduleset)
    if modset_id is None:
        return dict(status=False, msg="moduleset %s does not exist"%moduleset)
    if comp_moduleset_attached(nodename, modset_id):
        return dict(status=True,
                    msg="moduleset %s is already attached to this node"%moduleset)

    n = db.comp_node_moduleset.insert(modset_node=nodename,
                                      modset_id=modset_id)
    if n == 0:
        return dict(status=False, msg="failed to attach moduleset %s"%moduleset)
    _log('compliance.moduleset.node.attach',
        '%(moduleset)s attached to node %(node)s',
        dict(node=nodename, moduleset=moduleset),
        user='root@'+nodename)
    return dict(status=True, msg="moduleset %s attached"%moduleset)

@service.xmlrpc
def comp_detach_moduleset(nodename, moduleset):
    if len(moduleset) == 0:
        return dict(status=False, msg="no moduleset specified"%moduleset)
    modset_id = comp_moduleset_id(moduleset)
    if modset_id is None:
        return dict(status=True, msg="moduleset %s does not exist"%moduleset)
    if not comp_moduleset_attached(nodename, modset_id):
        return dict(status=True,
                    msg="moduleset %s is not attached to this node"%moduleset)
    q = db.comp_node_moduleset.modset_node == nodename
    q &= db.comp_node_moduleset.modset_id == modset_id
    n = db(q).delete()
    if n == 0:
        return dict(status=False, msg="failed to detach the moduleset")
    _log('compliance.moduleset.node.detach',
        '%(moduleset)s detached from node %(node)s',
        dict(node=nodename, moduleset=moduleset),
        user='root@'+nodename)
    return dict(status=True, msg="moduleset %s detached"%moduleset)

@service.xmlrpc
def comp_attach_ruleset(nodename, ruleset):
    if len(ruleset) == 0:
        return dict(status=False, msg="no ruleset specified"%ruleset)
    ruleset_id = comp_ruleset_exists(ruleset)
    if ruleset_id is None:
        return dict(status=False, msg="ruleset %s does not exist"%ruleset)
    if comp_ruleset_attached(nodename, ruleset_id):
        return dict(status=True,
                    msg="ruleset %s is already attached to this node"%ruleset)

    q = db.comp_rulesets_nodes.nodename == nodename
    q &= db.comp_rulesets_nodes.ruleset_id == ruleset_id
    if db(q).count() > 0:
        return dict(status=True, msg="ruleset %s already attached"%ruleset)

    n = db.comp_rulesets_nodes.insert(nodename=nodename,
                                      ruleset_id=ruleset_id)
    if n == 0:
        return dict(status=False, msg="failed to attach ruleset %s"%ruleset)
    _log('compliance.ruleset.node.attach',
        '%(ruleset)s attached to node %(node)s',
        dict(node=nodename, ruleset=ruleset),
        user='root@'+nodename)
    return dict(status=True, msg="ruleset %s attached"%ruleset)

@service.xmlrpc
def comp_detach_ruleset(nodename, ruleset):
    if len(ruleset) == 0:
        return dict(status=False, msg="no ruleset specified"%ruleset)
    ruleset_id = comp_ruleset_exists(ruleset)
    if ruleset_id is None:
        return dict(status=False, msg="ruleset %s does not exist"%ruleset)
    if not comp_ruleset_attached(nodename, ruleset_id):
        return dict(status=True,
                    msg="ruleset %s is not attached to this node"%ruleset)
    q = db.comp_rulesets_nodes.nodename == nodename
    q &= db.comp_rulesets_nodes.ruleset_id == ruleset_id
    n = db(q).delete()
    if n == 0:
        return dict(status=False, msg="failed to detach the ruleset")
    _log('compliance.ruleset.node.detach',
        '%(ruleset)s detached from node %(node)s',
        dict(node=nodename, ruleset=ruleset),
        user='root@'+nodename)
    return dict(status=True, msg="ruleset %s detached"%ruleset)

@service.xmlrpc
def comp_list_rulesets(pattern='%'):
    q = db.v_comp_explicit_rulesets.ruleset_name.like(pattern)
    rows = db(q).select(groupby=db.v_comp_explicit_rulesets.ruleset_name)
    return [r.ruleset_name for r in rows]

@service.xmlrpc
def comp_list_modulesets(pattern='%'):
    q = db.comp_moduleset.modset_name.like(pattern)
    rows = db(q).select()
    return [r.modset_name for r in rows]

@service.xmlrpc
def comp_get_moduleset(nodename):
    q = db.comp_node_moduleset.modset_node == nodename
    q &= db.comp_node_moduleset.modset_id == db.comp_moduleset.id
    rows = db(q).select(db.comp_moduleset.modset_name,
                        groupby=db.comp_node_moduleset.modset_id)
    return [r.modset_name for r in rows]

@service.xmlrpc
def comp_log_action(vars, vals):
    now = datetime.datetime.now()
    for i, (a, b) in enumerate(zip(vars, vals)):
        if a == 'run_action':
            action = b
        elif a == 'run_log':
            vals[i] = strip_unprintable(b)
    vars.append('run_date')
    vals.append(now)
    generic_insert('comp_log', vars, vals)
    if action == 'check':
        generic_insert('comp_status', vars, vals)

def comp_query(q, row):
    f = row.gen_filters
    fset = row.gen_filtersets_filters
    if f.f_op == '=':
        qry = db[f.f_table][f.f_field] == f.f_value
    elif f.f_op == 'LIKE':
        qry = db[f.f_table][f.f_field].like(f.f_value)
    elif f.f_op == 'IN':
        qry = db[f.f_table][f.f_field].belongs(f.f_value.split(','))
    elif f.f_op == '>=':
        qry = db[f.f_table][f.f_field] >= f.f_value
    elif f.f_op == '>':
        qry = db[f.f_table][f.f_field] > f.f_value
    elif f.f_op == '<=':
        qry = db[f.f_table][f.f_field] <= f.f_value
    elif f.f_op == '<':
        qry = db[f.f_table][f.f_field] < f.f_value
    else:
        return q
    if fset.f_log_op == 'AND':
        q &= qry
    elif fset.f_log_op == 'OR':
        q |= qry
    return q

def comp_format_filter(q):
    s = str(q)
    if 'comp_node_ruleset' in s:
        return ''
    s = s.replace('(','')
    s = s.replace(')','')
    s = s.replace('nodes.id>0 AND ','')
    return s

def comp_get_node_ruleset(nodename):
    q = db.v_nodes.nodename == nodename
    rows = db(q).select()
    if len(rows) != 1:
        return {}
    ruleset = {'name': 'osvc_node', 
               'filter': str(q),
               'vars': []}
    for f in db.nodes.fields:
        ruleset['vars'].append(('nodes.'+f, rows[0][f]))
    return {'osvc_node':ruleset}

def comp_ruleset_vars(ruleset_id, qr=None):
    if qr is None:
        f = 'explicit attachment'
    else:
        f = comp_format_filter(qr)
    q = db.comp_rulesets_variables.ruleset_id==ruleset_id
    q &= db.comp_rulesets.id == db.comp_rulesets_variables.ruleset_id
    rows = db(q).select()
    if len(rows) == 0:
        return dict()
    ruleset_name = rows[0].comp_rulesets.ruleset_name
    d = dict(
          name=ruleset_name,
          filter=f,
          vars=[]
        )
    for row in rows:
        d['vars'].append((row.comp_rulesets_variables.var_name,
                          row.comp_rulesets_variables.var_value))
    return {ruleset_name: d}

@service.xmlrpc
def comp_get_dated_ruleset(nodename, date):
    # initialize ruleset with asset variables
    ruleset = comp_get_node_ruleset(nodename)

    # lookup the rulesets valid for specified date
    o = db.comp_log.run_date
    q = db.comp_log.run_date >= date
    q &= db.comp_log.run_nodename == nodename
    rows = db(q).select(limitby=(0,1))
    if len(rows) == 0:
        # no trace of a previous run
        return ruleset
    found_date = rows[0].run_date
    dated_ruleset_names = rows[0].run_ruleset.split(',')
    q = db.comp_rulesets.ruleset_name.belongs(dated_ruleset_names)
    q &= db.comp_rulesets.ruleset_type=='explicit'
    dated_explicit_ruleset_ids = [r.id for r in db(q).select()]

    # add contextual rulesets variables
    q = db.comp_rulesets.id>0
    q &= db.comp_rulesets.id == db.comp_rulesets_filtersets.ruleset_id
    q &= db.gen_filtersets_filters.fset_id == db.comp_rulesets_filtersets.fset_id
    q &= db.gen_filtersets_filters.f_id == db.gen_filters.id
    rows = db(q).select(orderby=db.comp_rulesets.ruleset_name)

    q = db.nodes.nodename == nodename
    last_index = len(rows)-1
    qr = db.nodes.id > 0

    for i, row in enumerate(rows):
        if i == last_index:
            end_seq = True
        elif rows[i].comp_rulesets.ruleset_name != rows[i+1].comp_rulesets.ruleset_name:
            end_seq = True
        else:
            end_seq = False
        qr = comp_query(qr, row)
        if end_seq:
            match = db(q&qr).select(db.nodes.id)
            if len(match) == 1:
                ruleset.update(comp_ruleset_vars(row.comp_rulesets.id, qr=qr))
            qr = db.nodes.id > 0

    # add explicit rulesets variables
    for id in dated_explicit_ruleset_ids:
        ruleset.update(comp_ruleset_vars(id))

    return ruleset

@service.xmlrpc
def comp_get_ruleset(nodename):
    # initialize ruleset with asset variables
    ruleset = comp_get_node_ruleset(nodename)

    # add contextual rulesets variables
    q = db.comp_rulesets.id>0
    q &= db.comp_rulesets.id == db.comp_rulesets_filtersets.ruleset_id
    q &= db.gen_filtersets_filters.fset_id == db.comp_rulesets_filtersets.fset_id
    q &= db.gen_filtersets_filters.f_id == db.gen_filters.id
    rows = db(q).select(orderby=db.comp_rulesets.ruleset_name)

    q = db.nodes.nodename == nodename
    last_index = len(rows)-1
    qr = db.nodes.id > 0

    for i, row in enumerate(rows):
        if i == last_index:
            end_seq = True
        elif rows[i].comp_rulesets.ruleset_name != rows[i+1].comp_rulesets.ruleset_name:
            end_seq = True
        else:
            end_seq = False
        qr = comp_query(qr, row)
        if end_seq:
            match = db(q&qr).select(db.nodes.id)
            if len(match) == 1:
                ruleset.update(comp_ruleset_vars(row.comp_rulesets.id, qr=qr))
            qr = db.nodes.id > 0

    # add explicit rulesets variables
    q = db.comp_rulesets_nodes.nodename == nodename
    rows = db(q).select(db.comp_rulesets_nodes.ruleset_id,
                        orderby=db.comp_rulesets_nodes.ruleset_id)
    for row in rows:
        ruleset.update(comp_ruleset_vars(row.ruleset_id))

    return ruleset


