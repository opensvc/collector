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
regex = re.compile("\x1b\[([0-9]{1,3}(;[0-9]{1,3})*)?[m|K]", re.UNICODE)

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
              _class='menu_item',
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
     'power_supply_nb',
     'power_cabinet1',
     'power_cabinet2',
     'power_protect',
     'power_protect_breaker',
     'power_breaker1',
     'power_breaker2'
]

v_nodes_colprops = {
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
            'nodename': HtmlTableColumn(
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
            'environnement': HtmlTableColumn(
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
    r.set_pager_max(n)

    if r.pager_start == 0 and r.pager_end == 0:
        r.object_list = db(q).select(orderby=o)
    else:
        r.object_list = db(q).select(limitby=(r.pager_start,r.pager_end), orderby=o)

    r_html = r.html()

    o = db.v_comp_nodes.nodename
    q = _where(None, 'v_comp_nodes', domain_perms(), 'nodename')
    for f in t.cols:
        q = _where(q, 'v_comp_nodes', t.filter_parse_glob(f), f)
    q = apply_db_filters(q, 'v_comp_nodes')

    n = db(q).count()
    t.set_pager_max(n)

    if t.pager_start == 0 and t.pager_end == 0:
        t.object_list = db(q).select(orderby=o)
    else:
        t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)

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
                     title='Rule set',
                     field='ruleset_name',
                     display=True,
                     img='action16',
                    ),
            'fset_name': HtmlTableColumn(
                     title='Filter set',
                     field='fset_name',
                     display=True,
                     img='filter16',
                    ),
            'var_value': HtmlTableColumn(
                     title='Value',
                     field='var_value',
                     display=True,
                     img='action16',
                    ),
            'var_name': HtmlTableColumn(
                     title='Variable',
                     field='var_name',
                     display=True,
                     img='action16',
                    ),
        }
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
        self.ajax_col_values = 'ajax_comp_rulesets_col_values'

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
        f = SQLFORM(
                 db.comp_rulesets,
                 labels={'ruleset_name': T('Ruleset name')},
                 _name='form_ruleset_add',
            )
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
                    db,
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

def comp_rename_ruleset(ids):
    if len(ids) != 1:
        response.flash = T("one and only one ruleset must be selected")
        return
    if 'comp_ruleset_rename_input' not in request.vars:
        response.flash = T("new ruleset name is empty")
        return
    ids = map(lambda x: int(x.split('_')[0]), ids)
    new = request.vars['comp_ruleset_rename_input']
    id = ids[0]
    rows = db(db.comp_rulesets.id == id).select(db.comp_rulesets.ruleset_name)
    if len(rows) != 1:
        return
    old = rows[0].ruleset_name
    n = db(db.comp_rulesets.id == id).update(ruleset_name=new)
    response.flash = T("ruleset renamed", dict(n=n))
    _log('compliance.ruleset.rename',
        'renamed ruleset %(old)s as %(new)s',
        dict(old=old, new=new))

@auth.requires_login()
def comp_delete_ruleset(ids=[]):
    if len(ids) == 0:
        response.flash = T("no ruleset selected")
        return
    ids = map(lambda x: int(x.split('_')[0]), ids)
    rows = db(db.comp_rulesets.id.belongs(ids)).select(db.comp_rulesets.ruleset_name)
    x = ', '.join([r.ruleset_name for r in rows])
    n = db(db.comp_rulesets_filtersets.ruleset_id.belongs(ids)).delete()
    n = db(db.comp_rulesets_variables.ruleset_id.belongs(ids)).delete()
    n = db(db.comp_rulesets.id.belongs(ids)).delete()
    response.flash = T("deleted %(n)d ruleset(s)", dict(n=n))
    _log('compliance.ruleset.delete',
         'deleted rulesets %(x)s',
         dict(x=x))

@auth.requires_login()
def comp_delete_ruleset_var(ids=[]):
    if len(ids) == 0:
        response.flash = T("no ruleset variable selected")
        return
    ids = map(lambda x: int(x.split('_')[2]), ids)
    rows = db(db.v_comp_rulesets.id.belongs(ids)).select()
    x = map(lambda r: ' '.join((
                       r.var_name+'.'+r.var_value,
                       'from ruleset',
                       r.ruleset_name)), rows)
    x = ', '.join(set(x))
    n = db(db.comp_rulesets_variables.id.belongs(ids)).delete()
    response.flash = T("deleted %(n)d", dict(n=n))
    _log('compliance.ruleset.variable.delete',
         'deleted ruleset variables %(x)s',
         dict(x=x))

@auth.requires_login()
def comp_detach_filterset(ids=[]):
    if len(ids) == 0:
        response.flash = T("no filterset selected")
        return
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
    response.flash = T("detached %(n)d filtersets", dict(n=n))
    _log('compliance.ruleset.filterset.detach',
         'detached filterset %(x)s',
         dict(x=x))

@auth.requires_login()
def comp_detach_rulesets(node_ids=[], ruleset_ids=[]):
    if len(node_ids) == 0:
        response.flash = T("no node selected")
        return
    if len(ruleset_ids) == 0:
        response.flash = T("no ruleset selected")
        return

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

@auth.requires_login()
def comp_attach_rulesets(node_ids=[], ruleset_ids=[]):
    if len(node_ids) == 0:
        response.flash = T("no node selected")
        return
    if len(ruleset_ids) == 0:
        response.flash = T("no ruleset selected")
        return

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
    v.sub_span = ['fset_name']
    v.checkboxes = True

    if len(request.args) == 1 and request.args[0] == 'filterset_detach':
        comp_detach_filterset(v.get_checked())
    if len(request.args) == 1 and request.args[0] == 'ruleset_var_del':
        comp_delete_ruleset_var(v.get_checked())
    if len(request.args) == 1 and request.args[0] == 'ruleset_del':
        comp_delete_ruleset(v.get_checked())
        v.form_filterset_attach = v.comp_filterset_attach_sqlform()
        v.form_ruleset_var_add = v.comp_ruleset_var_add_sqlform()
    if len(request.args) == 1 and request.args[0] == 'ruleset_rename':
        comp_rename_ruleset(v.get_checked())
        v.form_filterset_attach = v.comp_filterset_attach_sqlform()
        v.form_ruleset_var_add = v.comp_ruleset_var_add_sqlform()

    if v.form_ruleset_add.accepts(request.vars, formname='add_ruleset'):
        response.flash = T("ruleset added")
        # refresh forms ruleset comboboxes
        v.form_filterset_attach = v.comp_filterset_attach_sqlform()
        v.form_ruleset_var_add = v.comp_ruleset_var_add_sqlform()
        _log('compliance.ruleset.add',
             'added ruleset %(ruleset)s',
             dict(ruleset=request.vars.ruleset_name))
    elif v.form_ruleset_add.errors:
        response.flash = T("errors in form")

    if v.form_filterset_attach.accepts(request.vars):
        response.flash = T("filterset attached")
        q = db.v_comp_rulesets.fset_id == request.vars.fset_id
        q &= db.v_comp_rulesets.ruleset_id == request.vars.ruleset_id
        rows = db(q).select()
        if len(rows) != 1:
            return
        fset = rows[0].fset_name
        ruleset = rows[0].ruleset_name
        _log('compliance.ruleset.filterset.attach',
             'attached filterset %(fset)s to ruleset %(ruleset)s',
             dict(fset=fset, ruleset=ruleset))
    elif v.form_filterset_attach.errors:
        response.flash = T("errors in form")

    if v.form_ruleset_var_add.accepts(request.vars):
        response.flash = T("rule added")
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
    v.set_pager_max(n)

    if v.pager_start == 0 and v.pager_end == 0:
        v.object_list = db(q).select(orderby=o)
    else:
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
            q = db.gen_filtersets_filters.fset_id == request.vars.fset_id
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

@auth.requires_login()
def comp_detach_filters(ids=[]):
    if len(ids) == 0:
        response.flash = T("no filters selected")
        return
    ids = map(lambda x: int(x.split('_')[1]), ids)
    q = db.v_gen_filtersets.id.belongs(ids)
    rows = db(q).select()
    if len(rows) == 0:
        return
    f_names = ', '.join(map(lambda f: ' '.join([
                       f.f_table+'.'+f.f_field,
                       f.f_op,
                       f.f_value,
                       'from',
                       f.fset_name]), rows))
    n = db(db.gen_filtersets_filters.id.belongs(ids)).delete()
    response.flash = T("detached %(n)d filters(s)", dict(n=n))
    _log('compliance.filterset.filter.detach',
        'detached filters %(f_names)s',
        dict(f_names=f_names))

@auth.requires_login()
def comp_delete_filterset(ids=[]):
    if len(ids) == 0:
        response.flash = T("no filterset selected")
        return
    ids = map(lambda x: int(x.split('_')[0]), ids)
    q = db.gen_filtersets.id.belongs(ids)
    rows = db(q).select()
    if len(rows) == 0:
        return
    fset_names = ', '.join([r.fset_name for r in rows])
    n = db(q).delete()
    response.flash = T("deleted %(n)d filterset(s)", dict(n=n))
    _log('compliance.filterset.delete',
        'deleted filtersets %(fset_names)s',
        dict(fset_names=fset_names))

def comp_rename_filterset(ids):
    if len(ids) != 1:
        response.flash = T("one and only one filterset must be selected")
        return
    if 'comp_filterset_rename_input' not in request.vars:
        response.flash = T("new filterset name is empty")
        return
    ids = map(lambda x: int(x.split('_')[0]), ids)
    new = request.vars['comp_filterset_rename_input']
    id = ids[0]
    rows = db(db.gen_filtersets.id == id).select(db.gen_filtersets.fset_name)
    if len(rows) != 1:
        return
    old = rows[0].fset_name
    n = db(db.gen_filtersets.id == id).update(fset_name=new)
    response.flash = T("filterset renamed", dict(n=n))
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

@auth.requires_login()
def comp_delete_filter(ids=[]):
    if len(ids) == 0:
        response.flash = T("no filter selected")
        return
    q = db.gen_filters.id.belongs(ids)
    rows = db(q).select()
    if len(rows) == 0:
        return
    f_names = ', '.join(map(lambda f: ' '.join([
                       f.f_table+'.'+f.f_field,
                       f.f_op,
                       f.f_value]), rows))
    n = db(q).delete()
    response.flash = T("deleted %(n)d filter(s)", dict(n=n))
    _log('compliance.filter.delete',
        'deleted filters %(f_names)s',
        dict(f_names=f_names))

@auth.requires_login()
def ajax_comp_filters():
    v = table_comp_filters('ajax_comp_filters',
                           'ajax_comp_filters')
    v.span = 'f_table'
    v.checkboxes = True

    if len(request.args) == 1 and request.args[0] == 'delete_filter':
        comp_delete_filter(v.get_checked())

    if v.form_filter_add.accepts(request.vars):
        response.flash = T("filter added")
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
    v.set_pager_max(n)

    if v.pager_start == 0 and v.pager_end == 0:
        v.object_list = db(q).select(orderby=o)
    else:
        v.object_list = db(q).select(limitby=(v.pager_start,v.pager_end), orderby=o)

    return v.html()

@auth.requires_login()
def ajax_comp_filtersets():
    t = table_comp_filtersets('ajax_comp_filtersets',
                              'ajax_comp_filtersets')
    t.span = 'fset_name'
    t.checkboxes = True

    if len(request.args) == 1 and request.args[0] == 'delete_filterset':
        comp_delete_filterset(t.get_checked())
        t.form_filter_attach = t.comp_filter_attach_sqlform()
    elif len(request.args) == 1 and request.args[0] == 'detach_filters':
        comp_detach_filters(t.get_checked())
    elif len(request.args) == 1 and request.args[0] == 'filterset_rename':
        comp_rename_filterset(t.get_checked())
        t.form_filter_attach = t.comp_filter_attach_sqlform()

    if t.form_filterset_add.accepts(request.vars):
        response.flash = T("filterset added")
        t.form_filter_attach = t.comp_filter_attach_sqlform()
        _log('compliance.filterset.add',
            'added filterset %(fset_name)s',
            dict(fset_name=request.vars.fset_name))
    elif t.form_filterset_add.errors:
        response.flash = T("errors in form")

    if t.form_filter_attach.accepts(request.vars):
        response.flash = T("filter attached")
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
    t.set_pager_max(n)

    if t.pager_start == 0 and t.pager_end == 0:
        t.object_list = db(q).select(orderby=o)
    else:
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
            'modset_mod_name': HtmlTableColumn(
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

def comp_delete_module(ids=[]):
    if len(ids) == 0:
        response.flash = T("no module selected")
        return
    ids = map(lambda x: int(x.split('_')[1]), ids)
    rows = db(db.comp_moduleset_modules.id.belongs(ids)).select(db.comp_moduleset_modules.modset_mod_name)
    if len(rows) == 0:
        return
    mod_names = ', '.join([r.modset_mod_name for r in rows])
    n = db(db.comp_moduleset_modules.id.belongs(ids)).delete()
    _log('compliance.moduleset.module.delete',
        'deleted modules %(mod_names)s',
        dict(mod_names=mod_names))
    response.flash = T("deleted %(n)d modules", dict(n=n))

def comp_delete_moduleset(ids=[]):
    if len(ids) == 0:
        response.flash = T("no moduleset selected")
        return
    ids = map(lambda x: int(x.split('_')[0]), ids)
    rows = db(db.comp_moduleset.id.belongs(ids)).select(db.comp_moduleset.modset_name)
    if len(rows) == 0:
        return
    modset_names = ', '.join([r.modset_name for r in rows])
    n = db(db.comp_moduleset_modules.modset_id.belongs(ids)).delete()
    n = db(db.comp_node_moduleset.id.belongs(ids)).delete()
    n = db(db.comp_moduleset.id.belongs(ids)).delete()
    _log('compliance.moduleset.delete',
        'deleted modulesets %(modset_names)s',
        dict(modset_names=modset_names))
    response.flash = T("deleted %(n)d moduleset", dict(n=n))

@auth.requires_login()
def comp_rename_moduleset(ids):
    if len(ids) != 1:
        response.flash = T("one and only one moduleset must be selected")
        return
    if 'comp_moduleset_rename_input' not in request.vars:
        response.flash = T("new moduleset name is empty")
        return
    new = request.vars['comp_moduleset_rename_input']
    id = int(ids[0].split('_')[0])
    rows = db(db.comp_moduleset.id == id).select(db.comp_moduleset.modset_name)
    if len(rows) != 1:
        return
    old = rows[0].modset_name
    n = db(db.comp_moduleset.id == id).update(modset_name=new)
    _log('compliance.moduleset.rename',
         'renamed moduleset %(old)s as %(new)s',
         dict(old=old, new=new))
    response.flash = T("moduleset renamed", dict(n=n))

@auth.requires_login()
def ajax_comp_moduleset():
    t = table_comp_moduleset('ajax_comp_moduleset', 'ajax_comp_moduleset')
    t.span = 'modset_name'
    t.checkboxes = True
    t.checkbox_id_table = 'comp_moduleset_modules'

    if len(request.args) == 1 and request.args[0] == 'module_del':
        comp_delete_module(t.get_checked())
    if len(request.args) == 1 and request.args[0] == 'moduleset_del':
        comp_delete_moduleset(t.get_checked())
        t.form_module_add = t.comp_module_add_sqlform()
    if len(request.args) == 1 and request.args[0] == 'moduleset_rename':
        comp_rename_moduleset(t.get_checked())
        t.form_module_add = t.comp_module_add_sqlform()

    if t.form_moduleset_add.accepts(request.vars, formname='add_moduleset'):
        response.flash = T("moduleset added")
        t.form_module_add = t.comp_module_add_sqlform()
        _log('compliance.moduleset.add',
            'added moduleset %(modset_name)s',
            dict(modset_name=request.vars.modset_name))
    elif t.form_moduleset_add.errors:
        response.flash = T("errors in form")

    if t.form_module_add.accepts(request.vars, formname='add_module'):
        response.flash = T("moduleset added")
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
    t.set_pager_max(len(rows))

    if t.pager_start == 0 and t.pager_end == 0:
        t.object_list = db(q).select(db.comp_moduleset_modules.ALL,
                                     db.comp_moduleset.modset_name,
                                     db.comp_moduleset.id,
                                     orderby=o,
                                     left=left
                                    )
    else:
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
                     'mod_nodes']
        self.colprops = {
            'mod_name': HtmlTableColumn(
                     title='Module',
                     field='mod_name',
                     #table='comp_mod_status',
                     display=True,
                     img='check16',
                    ),
            'mod_total': HtmlTableColumn(
                     title='Total',
                     field='mod_total',
                     #table='comp_mod_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'mod_ok': HtmlTableColumn(
                     title='Ok',
                     field='mod_ok',
                     #table='comp_mod_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'mod_percent': col_mod_percent(
                     title='Percent',
                     field='mod_percent',
                     #table='comp_mod_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'mod_nodes': col_concat_list(
                     title='Nodes',
                     field='mod_nodes',
                     #table='comp_mod_status',
                     display=False,
                     img='node16',
                    ),
        }

class table_comp_node_status(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['mod_node', 'mod_total', 'mod_ok', 'mod_percent',
                     'mod_names']
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
                     _class='numeric',
                    ),
            'mod_names': col_concat_list(
                     title='Modules',
                     field='mod_names',
                     display=False,
                     img='check16',
                    ),
        }

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

@auth.requires_login()
def ajax_comp_log_col_values():
    t = table_comp_log('ajax_comp_log', 'ajax_comp_log')
    col = request.args[0]
    o = db.comp_log[col]
    q = _where(None, 'comp_log', domain_perms(), 'run_nodename')
    q &= db.comp_log.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse_glob(f), f)
    q = apply_db_filters(q, 'v_nodes')
    t.object_list = db(q).select(orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_comp_status_col_values():
    t = table_comp_status('ajax_comp_status', 'ajax_comp_status')
    col = request.args[0]
    o = db.comp_status[col]
    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    q &= db.comp_status.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse_glob(f), f)
    q = apply_db_filters(q, 'v_nodes')
    t.object_list = db(q).select(orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_comp_status():
    t = table_comp_status('ajax_comp_status', 'ajax_comp_status')

    o = ~db.comp_status.run_nodename
    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    q &= db.comp_status.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_db_filters(q, 'v_nodes')

    n = db(q).count()
    t.set_pager_max(n)

    if t.pager_start == 0 and t.pager_end == 0:
        all = db(q).select(orderby=o)
        t.object_list = all
    else:
        all = db(q).select(orderby=o)
        t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)

    mt = table_comp_mod_status('ajax_comp_mod_status', 'ajax_comp_mod_status')
    mt.object_list = compute_mod_status(all)
    mt.pageable = False
    mt.filterable = False
    mt.exportable = False
    mt.dbfilterable = False

    nt = table_comp_node_status('ajax_comp_node_status', 'ajax_comp_node_status')
    nt.object_list = compute_node_status(all)
    nt.pageable = False
    nt.filterable = False
    nt.exportable = False
    nt.dbfilterable = False

    return DIV(
             mt.html(),
             nt.html(),
             t.html()
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
    return sorted(h.values(), key=lambda x: x['mod_percent']+x['mod_name'])

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
    return sorted(h.values(), key=lambda x: x['mod_percent']+x['mod_node'])

@auth.requires_login()
def comp_status():
    t = DIV(
          comp_menu('Status'),
          DIV(
            ajax_comp_status(),
            _id='ajax_comp_status',
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

@auth.requires_login()
def ajax_comp_log():
    t = table_comp_log('ajax_comp_log', 'ajax_comp_log')

    o = ~db.comp_log.run_date
    q = _where(None, 'comp_log', domain_perms(), 'run_nodename')
    q &= db.comp_log.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q = _where(q, 'comp_log', t.filter_parse(f), f)
    q = apply_db_filters(q, 'v_nodes')

    n = db(q).count()
    t.set_pager_max(n)

    if t.pager_start == 0 and t.pager_end == 0:
        t.object_list = db(q).select(orderby=o)
    else:
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


