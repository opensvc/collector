from hashlib import md5
import datetime
import json
now=datetime.datetime.today()
sevendays = str(now-datetime.timedelta(days=7,
                                       hours=now.hour,
                                       minutes=now.minute,
                                       seconds=now.second,
                                       microseconds=now.microsecond))

img_h = {0: 'check16.png',
         1: 'nok.png',
         2: 'na.png',
       -15: 'kill16.png'}

tables = {
    'nodes':dict(name='nodes', title='nodes', cl='node16', hide=False),
    'services':dict(name='services', title='services', cl='svc', hide=False),
    'svcmon':dict(name='svcmon', title='service status', cl='svc', hide=False),
}
operators = [dict(id='op0', title='='),
             dict(id='op1', title='LIKE'),
             dict(id='op2', title='>'),
             dict(id='op3', title='>='),
             dict(id='op4', title='<'),
             dict(id='op5', title='<='),
             dict(id='op6', title='IN')]
props = v_services_colprops
props.update(svcmon_colprops)
props.update(v_svcmon_colprops)
props.update(v_nodes_colprops)
fields = {
    'nodes': db.nodes.fields,
    'services': db.services.fields,
    'svcmon': db.svcmon.fields,
}

import re
# ex: \x1b[37;44m\x1b[1mContact List\x1b[0m\n
regex = re.compile("\x1b\[([0-9]{1,3}(;[0-9]{1,3})*)?[m|K|G]", re.UNICODE)

def strip_unprintable(s):
    return regex.sub('', s)

#
# custom column formatting
#
class col_rset_md5(HtmlTableColumn):
    def html(self, o):
        id = self.t.extra_line_key(o)
        s = self.get(o)
        if s is None or len(s) == 0:
            return ''
        d = DIV(
              A(
                s,
                _onclick="toggle_extra('%(url)s', '%(id)s');"%dict(
                  url=URL(r=request, c='compliance',f='ajax_rset_md5',
                          vars={'rset_md5': s}),
                  id=id,
                ),
              ),
              _class='nowrap',
            )
        return d

class col_comp_filters_table(HtmlTableColumn):
    def html(self, o):
        if o.f_table is None:
            return ''
        if o.f_table not in tables:
            return o.f_table
        return DIV(
                 tables[o.f_table]['title'],
                 _class=tables[o.f_table]['cl'],
               )

class col_comp_filters_field(HtmlTableColumn):
    def html(self, o):
        if o.f_field is None:
            return ''
        if o.f_field not in props:
            return o.f_field
        return DIV(
                 props[o.f_field].title,
                 _class=props[o.f_field].img,
               )

def plot_log(s):
    height = 30
    cols = 20
    col_width = 4
    weeks = []
    for i in range(cols-1, -1, -1):
        d = now - datetime.timedelta(days=7*i)
        weeks.append(d.isocalendar()[1])
    try:
        week, ok, nok, na = json.loads(s)
    except:
        return SPAN()
    h = {}
    _max = 0
    for i, v in enumerate(week):
        h[v] = (ok[i], nok[i], na[i])
        total = ok[i] + nok[i] + na[i]
        if total > _max:
            _max = total
    if _max == 0:
        return SPAN("no data")
    ratio = float(height) / _max
    for i in weeks:
        if i not in week:
            h[i] = (0, 0, 0)
    l = []
    for i in weeks:
        if h[i] == (0, 0, 0):
            l.append(DIV(
                   _style="background-color:#ececaa;float:left;width:%dpx;height:%dpx"%(col_width, height),
                 ))
        else:
            h0 = int(h[i][0] * ratio)
            h1 = int(h[i][1] * ratio)
            h2 = int(h[i][2] * ratio)
            cc = height - h0 - h1 - h2
            l.append(DIV(
                   DIV("", _style="background-color:rgba(0,0,0,0);height:%dpx"%cc),
                   DIV("", _style="background-color:lightgreen;height:%dpx"%h0) if h0 > 0 else "",
                   DIV("", _style="background-color:#ff7863;height:%dpx"%h1) if h1 > 0 else "",
                   DIV("", _style="background-color:#008099;height:%dpx"%h2) if h2 > 0 else "",
                   _style="float:left;width:%dpx"%col_width,
                 ))
    return DIV(l)

class col_comp_svc_status(HtmlTableColumn):
    def html(self, o):
        id = self.t.extra_line_key(o)
        return A(
                 IMG(
                   _src=URL(r=request, c="static", f="spark16.png"),
                 ),
                 _onclick="toggle_extra('%(url)s', '%(id)s');"%dict(
                          url=URL(
                                r=request,
                                c='compliance',
                                f='ajax_svc_history',
                                vars={'svcname': self.t.colprops['svc_name'].get(o), 'rowid': id}
                              ),
                          id=id,
                            ),
               )

class col_comp_node_status(HtmlTableColumn):
    def html(self, o):
        id = self.t.extra_line_key(o)
        return A(
                 IMG(
                   _src=URL(r=request, c="static", f="spark16.png"),
                 ),
                 _onclick="toggle_extra('%(url)s', '%(id)s');"%dict(
                          url=URL(
                                r=request,
                                c='compliance',
                                f='ajax_node_history',
                                vars={'nodename': self.t.colprops['node_name'].get(o), 'rowid': id}
                              ),
                          id=id,
                            ),
               )

class col_comp_mod_status(HtmlTableColumn):
    def html(self, o):
        id = self.t.extra_line_key(o)
        return A(
                 IMG(
                   _src=URL(r=request, c="static", f="spark16.png"),
                 ),
                 _onclick="toggle_extra('%(url)s', '%(id)s');"%dict(
                          url=URL(
                                r=request,
                                c='compliance',
                                f='ajax_mod_history',
                                vars={'modname': self.t.colprops['mod_name'].get(o), 'rowid': id}
                              ),
                          id=id,
                            ),
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

class col_encap_rset(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        if s is None:
            return ""
        return s

class col_ruleset_name(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        return DIV(s, _class="postit", _style="width:95%")

class col_var_name(HtmlTableColumn):
    def html(self, o):
        s = self.get(o)
        if s == '':
            ss = '(no name)'
        elif s is None:
            ss = ''
        else:
            ss = s
        tid = 'nd_t_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        iid = 'nd_i_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        sid = 'nd_s_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        d = DIV(
              DIV(
                ss,
                _id=tid,
                _onclick="""hide_eid('%(tid)s');show_eid('%(sid)s');getElementById('%(iid)s').focus()"""%dict(tid=tid,
sid=sid, iid=iid),
                _class="clickable",
              ),
              DIV(
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
    def load_form_cache(self):
        if hasattr(self.t, "form_cache"):
            return self.t.form_cache
        q = db.forms.id > 0
        rows = db(q).select()
        data = {}
        for row in rows:
            data[row.form_name] = row
        self.t.form_cache = data
        return self.t.form_cache

    def html(self, o):
        if self.t.colprops['id'].get(o) is None:
            return ""
        hid = 'vd_h_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        fid = 'vd_f_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        cid = 'vd_c_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        eid = 'vd_e_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))

        form_cache = self.load_form_cache()

        ruleset_id = self.t.colprops['ruleset_id'].get(o)
        var_class = self.t.colprops['var_class'].get(o)
        id = self.t.colprops['id'].get(o)

        if 'v_comp_rulesets' in o:
            var = o['v_comp_rulesets']
        else:
            var = o

        if var_class in form_cache:
            form = form_cache[var_class]
        else:
            form = None

        if self.t.colprops['encap_rset_id'].get(o) is not None:
            edit = ""
        else:
            edit = A(
                 IMG(_src=URL(r=request, c='static', f='edit.png')),
                 _id=eid,
                 _onclick="""hide_eid('%(eid)s');show_eid('%(cid)s');show_eid('%(formid)s');sync_ajax('%(url)s', [], '%(formid)s', function(){})"""%dict(
                   formid=hid,
                   eid=eid,
                   cid=cid,
                   url=URL(
                         r=request, c='compliance', f='ajax_forms_inputs',
                         vars={
                           "rset_name": self.t.colprops['ruleset_name'].get(o),
                           "var_id": self.t.colprops['id'].get(o),
                           "form_xid": '_'.join((str(id), str(ruleset_id))),
                           "hid": hid,
                           "showexpert": True,
                         }
                       )
                 ),
                 _label=T("edit"),
                 _style='position: absolute; top: 2px; right: 2px; z-index: 400',
               )

        cancel = A(
                 IMG(_src=URL(r=request, c='static', f='cancel.png')),
                 _id=cid,
                 _onclick="""hide_eid('%(cid)s');show_eid('%(eid)s');show_eid('%(formid)s');ajax('%(url)s', [], '%(formid)s')"""%dict(
                   formid=hid,
                   eid=eid,
                   cid=cid,
                   url=URL(
                         r=request, c='compliance', f='ajax_forms_inputs',
                         vars={
                           "rset_name": self.t.colprops['ruleset_name'].get(o),
                           "var_id": self.t.colprops['id'].get(o),
                           "form_xid": '_'.join((str(id), str(ruleset_id))),
                           "hid": hid,
                           "mode": "show",
                           "showexpert": True,
                         }
                       )
                 ),
                 _label=T("edit"),
                 _style='display:none;position: absolute; top: 2px; right: 2px; z-index: 400',
               )

        val = DIV(
               _ajax_forms_inputs(
                 _mode="show",
                 _rset_name=self.t.colprops['ruleset_name'].get(o),
                 _var_id=self.t.colprops['id'].get(o),
                 _form_xid='_'.join((str(id), str(ruleset_id))),
                 _hid=hid,
                 var=var, form=form, showexpert=True
               ),
               _id=hid,
               _style="position: relative;",
             )

        return DIV(
                 edit,
                 cancel,
                 val,
                 _class="postit",
                 _style="position: relative;",
               )

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
        for c in self.cols:
            self.colprops['nodename'].t = self
        self.colprops['nodename'].display = True
        self.checkboxes = True
        self += HtmlTableMenu('Ruleset', 'comp16', ['ruleset_attach', 'ruleset_detach'], id='menu_ruleset2')
        self.ajax_col_values = 'ajax_comp_rulesets_nodes_col_values'

    def ruleset_detach(self):
        d = DIV(
              A(
                T("Detach ruleset"),
                _class='detach16',
                _onclick=self.ajax_submit(args=['detach_ruleset'],
                                          additional_inputs=self.rulesets.ajax_inputs()),
              ),
            )
        return d

    def ruleset_attach(self):
        d = DIV(
              A(
                T("Attach ruleset"),
                _class='attach16',
                _onclick=self.ajax_submit(args=['attach_ruleset'],
                                          additional_inputs=self.rulesets.ajax_inputs()),
              ),
            )
        return d


class table_comp_explicit_rules(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['ruleset_name', 'variables']
        self.colprops = {
            'id': HtmlTableColumn(
                     title='Ruleset id',
                     field='id',
                     table='v_comp_explicit_rulesets',
                     display=False,
                     img='action16',
                    ),
            'ruleset_name': HtmlTableColumn(
                     title='Rule set',
                     field='ruleset_name',
                     table='v_comp_explicit_rulesets',
                     display=True,
                     img='action16',
                    ),
            'variables': col_variables(
                     title='Variables',
                     field='variables',
                     table='v_comp_explicit_rulesets',
                     display=True,
                     img='action16',
                    ),
        }
        self.checkboxes = True
        self.dbfilterable = False
        self.exportable = False
        self.ajax_col_values = 'ajax_comp_explicit_rules_col_values'
        self.checkbox_id_table = 'v_comp_explicit_rulesets'

@auth.requires_login()
def ajax_comp_explicit_rules_col_values():
    t = table_comp_explicit_rules('crn1', 'ajax_comp_rulesets_nodes',
                                  innerhtml='crn1')
    col = request.args[0]
    o = db.v_comp_explicit_rulesets[col]
    q = db.v_comp_explicit_rulesets.id > 0
    for f in t.cols:
        q = _where(q, 'v_comp_explicit_rulesets', t.filter_parse_glob(f), f)
    t.object_list = db(q).select(o, orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_comp_rulesets_nodes_col_values():
    r = table_comp_explicit_rules('crn1', 'ajax_comp_rulesets_nodes',
                                  innerhtml='crn1')
    t = table_comp_rulesets_nodes('crn2', 'ajax_comp_rulesets_nodes',
                                  innerhtml='crn1')
    col = request.args[0]
    if col in t.cols:
        o = db.v_comp_nodes[col]
        q = _where(None, 'v_comp_nodes', domain_perms(), 'nodename')
        for f in t.cols:
            q = _where(q, 'v_comp_nodes', t.filter_parse_glob(f), f)
        t.object_list = db(q).select(o, orderby=o, groupby=o)
        return t.col_values_cloud(col)
    else:
        o = db.v_comp_explicit_rulesets[col]
        q = db.v_comp_explicit_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
        if 'Manager' not in user_groups():
            q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
        for f in r.cols:
            q = _where(q, 'v_comp_explicit_rulesets', r.filter_parse_glob(f), f)
        r.object_list = db(q).select(o, orderby=o, groupby=o)
        return r.col_values_cloud(col)


@auth.requires_login()
def ajax_comp_rulesets_nodes():
    r = table_comp_explicit_rules('crn1', 'ajax_comp_rulesets_nodes',
                                  innerhtml='crn1')
    t = table_comp_rulesets_nodes('crn2', 'ajax_comp_rulesets_nodes',
                                  innerhtml='crn1')
    t.rulesets = r
    t.checkbox_names.append(r.id+'_ck')

    if len(request.args) == 1 and request.args[0] == 'attach_ruleset':
        comp_attach_rulesets(t.get_checked(), r.get_checked())
    elif len(request.args) == 1 and request.args[0] == 'detach_ruleset':
        comp_detach_rulesets(t.get_checked(), r.get_checked())

    o = db.v_comp_explicit_rulesets.ruleset_name
    q = db.v_comp_explicit_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    for f in r.cols:
        q = _where(q, 'v_comp_explicit_rulesets', r.filter_parse_glob(f), f)

    n = db(q).count()
    r.setup_pager(n)
    r.object_list = db(q).select(limitby=(r.pager_start,r.pager_end), orderby=o, groupby=o)

    r_html = r.html()

    o = db.v_comp_nodes.nodename
    q = _where(None, 'v_comp_nodes', domain_perms(), 'nodename')
    if 'Manager' not in user_groups():
        q &= db.v_comp_nodes.team_responsible.belongs(user_groups())
    for f in t.cols:
        q = _where(q, 'v_comp_nodes', t.filter_parse_glob(f), f)
    q = apply_gen_filters(q, r.tables())

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
             DIV(XML('&nbsp;'), _class='spacer'),
           )

class table_comp_rulesets(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['ruleset_name',
                     'ruleset_type',
                     'ruleset_public',
                     'teams_responsible',
                     'fset_name',
                     'encap_rset',
                     'var_class',
                     'var_name',
                     'var_value',
                     'var_updated',
                     'var_author',
                    ]
        self.colprops = {
            'var_updated': HtmlTableColumn(
                     title='Updated',
                     field='var_updated',
                     table='v_comp_rulesets',
                     display=True,
                     img='action16',
                    ),
            'teams_responsible': HtmlTableColumn(
                     title='Teams responsible',
                     field='teams_responsible',
                     table='v_comp_rulesets',
                     display=True,
                     img='guy16',
                    ),
            'var_author': HtmlTableColumn(
                     title='Author',
                     field='var_author',
                     table='v_comp_rulesets',
                     display=True,
                     img='guy16',
                    ),
            'id': HtmlTableColumn(
                     title='Rule id',
                     field='id',
                     table='v_comp_rulesets',
                     display=False,
                     img='action16',
                    ),
            'fset_id': HtmlTableColumn(
                     title='Filterset id',
                     field='fset_id',
                     table='v_comp_rulesets',
                     display=False,
                     img='action16',
                    ),
            'ruleset_id': HtmlTableColumn(
                     title='Ruleset id',
                     field='ruleset_id',
                     table='v_comp_rulesets',
                     display=False,
                     img='action16',
                    ),
            'encap_rset': col_encap_rset(
                     title='Encapsulated ruleset',
                     field='encap_rset',
                     table='v_comp_rulesets',
                     display=True,
                     img='action16',
                    ),
            'encap_rset_id': HtmlTableColumn(
                     title='Encapsulated ruleset id',
                     field='encap_rset_id',
                     table='v_comp_rulesets',
                     display=False,
                     img='action16',
                    ),
            'ruleset_name': col_ruleset_name(
                     title='Ruleset',
                     field='ruleset_name',
                     table='v_comp_rulesets',
                     display=True,
                     img='action16',
                    ),
            'ruleset_type': HtmlTableColumn(
                     title='Ruleset type',
                     field='ruleset_type',
                     table='v_comp_rulesets',
                     display=True,
                     img='action16',
                    ),
            'ruleset_public': HtmlTableColumn(
                     title='Ruleset public',
                     field='ruleset_public',
                     table='v_comp_rulesets',
                     display=True,
                     img='action16',
                    ),
            'fset_name': HtmlTableColumn(
                     title='Filterset',
                     field='fset_name',
                     table='v_comp_rulesets',
                     display=True,
                     img='filter16',
                    ),
            'var_value': col_var_value(
                     title='Value',
                     field='var_value',
                     table='v_comp_rulesets',
                     display=True,
                     img='action16',
                    ),
            'var_name': col_var_name(
                     title='Variable',
                     field='var_name',
                     table='v_comp_rulesets',
                     display=True,
                     img='action16',
                    ),
            'var_class': HtmlTableColumn(
                     title='Class',
                     field='var_class',
                     table='v_comp_rulesets',
                     display=False,
                     img='action16',
                    ),
        }
        self.colprops['var_name'].t = self
        self.colprops['var_value'].t = self
        if 'CompManager' in user_groups():
            self.form_filterset_attach = self.comp_filterset_attach_sqlform()
            self.form_ruleset_var_add = self.comp_ruleset_var_add_sqlform()
            self.form_ruleset_add = self.comp_ruleset_add_sqlform()
            self.form_ruleset_attach = self.comp_ruleset_attach_sqlform()
            self += HtmlTableMenu('Team responsible', 'guys16', ['team_responsible_attach', 'team_responsible_detach'])
            self += HtmlTableMenu('Filterset', 'filters', ['filterset_attach', 'filterset_detach'])
            self += HtmlTableMenu('Variable', 'comp16', ['ruleset_var_add', 'ruleset_var_del'])
            self += HtmlTableMenu('Ruleset', 'comp16', ['ruleset_add',
                                                        'ruleset_del',
                                                        'ruleset_rename',
                                                        'ruleset_clone',
                                                        'ruleset_change_type',
                                                        'ruleset_change_public',
                                                        'ruleset_attach',
                                                        'ruleset_detach',
                                                        'ruleset_node_attach'])
        self.ajax_col_values = 'ajax_comp_rulesets_col_values'
        self.dbfilterable = False

    def ruleset_node_attach(self):
        return A(
                 T("Rulesets/Nodes attachment"),
                 _href=URL(r=request, f="comp_rulesets_nodes_attachment"),
                 _class="attach16",
               )

    def ruleset_change_public(self):
        label = 'Change ruleset publication'
        action = 'ruleset_change_public'
        divid = 'rset_public_change'
        sid = 'rset_public_change_s'
        options = ['T', 'F']
        d = DIV(
              A(
                T(label),
                _class='edit16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div=divid),
              ),
              DIV(
                TABLE(
                  TR(
                    TH(T('Ruleset publication')),
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
                        _onclick="""if (confirm("%(text)s")){%(s)s};
                                 """%dict(s=self.ajax_submit(additional_inputs=[sid], args=action),
                                          text=T("Changing the ruleset publication resets all attachments to nodes and services. Please confirm ruleset publication change."),
                                 ),
                      ),
                    ),
                  ),
                ),
                _style='display:none',
                _class='white_float',
                _name=divid,
              ),
            )
        return d

    def ruleset_change_type(self):
        label = 'Change ruleset type'
        action = 'ruleset_change_type'
        divid = 'rset_type_change'
        sid = 'rset_type_change_s'
        options = ['contextual', 'explicit']
        d = DIV(
              A(
                T(label),
                _class='edit16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
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
                        _onclick="""if (confirm("%(text)s")){%(s)s};
                                 """%dict(s=self.ajax_submit(additional_inputs=[sid], args=action),
                                          text=T("Changing the ruleset type resets all attachments to nodes and services. Please confirm ruleset type change."),
                                 ),
                      ),
                    ),
                  ),
                ),
                _style='display:none',
                _class='white_float',
                _name=divid,
              ),
            )
        return d

    def ruleset_clone(self):
        label = 'Clone ruleset'
        action = 'ruleset_clone'
        divid = 'rset_clone'
        sid = 'rset_clone_s'
        iid = 'rset_clone_i'
        o = db.comp_rulesets.ruleset_name
        if 'Manager' in user_groups():
            q = db.comp_rulesets.id > 0
            options = [OPTION(g.ruleset_name,_value=g.id) for g in db(q).select(orderby=o)]
        else:
            q = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
            q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
            options = [OPTION(g.comp_rulesets.ruleset_name,_value=g.comp_rulesets.id) for g in db(q).select(orderby=o)]
        d = DIV(
              A(
                T(label),
                _class='add16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
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
            )
        return d

    def checkbox_key(self, o):
        if o is None:
            return '_'.join((self.id, 'ckid', ''))
        ids = []
        ids.append(self.colprops['ruleset_id'].get(o))
        ids.append(self.colprops['fset_id'].get(o))
        ids.append(self.colprops['id'].get(o))
        ids.append(self.colprops['encap_rset_id'].get(o))
        return '_'.join([self.id, 'ckid']+map(str,ids))

    def team_responsible_select_tool(self, label, action, divid, sid, _class=''):
        if 'Manager' not in user_groups():
            s = """and role in (
                     select g.role from
                       auth_group g
                       join auth_membership gm on g.id=gm.group_id
                       join auth_user u on gm.user_id=u.id
                     where
                       u.id=%d
                  )"""%auth.user_id
        else:
            s = ""
        sql = """ select id, role
                  from auth_group
                  where
                    role not like "user_%%" and
                    privilege = 'F'
                    %s
                  group by role order by role
        """%s
        rows = db.executesql(sql)
        options = [OPTION(g[1],_value=g[0]) for g in rows]

        q = db.auth_membership.user_id == auth.user_id
        q &= db.auth_group.id == db.auth_membership.group_id
        q &= db.auth_group.role.like('user_%')
        options += [OPTION(g.auth_group.role,_value=g.auth_group.id) for g in db(q).select()]
        d = DIV(
              A(
                T(label),
                _class=_class,
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div=divid),
              ),
              DIV(
                TABLE(
                  TR(
                    TH(T('Team')),
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
                _id=divid,
              ),
            )
        return d

    def team_responsible_attach(self):
        d = self.team_responsible_select_tool(label="Attach",
                                              action="team_responsible_attach",
                                              divid="team_responsible_attach",
                                              sid="team_responsible_attach_s",
                                              _class="attach16")
        return d

    def team_responsible_detach(self):
        d = self.team_responsible_select_tool(label="Detach",
                                              action="team_responsible_detach",
                                              divid="team_responsible_detach",
                                              sid="team_responsible_detach_s",
                                              _class="detach16")
        return d

    def ruleset_rename(self):
        d = DIV(
              A(
                T("Rename ruleset"),
                _class='edit16',
                _onclick="""click_toggle_vis(event,'%(div)s', 'block');
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
            )
        return d

    def ruleset_del(self):
        d = DIV(
              A(
                T("Delete ruleset"),
                _class='del16',
                _onclick="""if (confirm("%(text)s")){%(s)s};
                         """%dict(s=self.ajax_submit(args=['ruleset_del']),
                                  text=T("Deleting a ruleset also deletes the ruleset variables, filters attachments and node attachments. Please confirm ruleset deletion."),
                                 ),
              ),
            )
        return d

    def filterset_attach(self):
        d = DIV(
              A(
                T("Attach"),
                _class='attach16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='comp_filterset_attach'),
              ),
              DIV(
                self.form_filterset_attach,
                _style='display:none',
                _class='white_float',
                _name='comp_filterset_attach',
                _id='comp_filterset_attach',
              ),
            )
        return d

    def filterset_detach(self):
        d = DIV(
              A(
                T("Detach"),
                _class='detach16',
                _onclick=self.ajax_submit(args=['filterset_detach']),
              ),
            )
        return d

    def ruleset_detach(self):
        d = DIV(
              A(
                T("Detach child ruleset"),
                _class='detach16',
                _onclick=self.ajax_submit(args=['ruleset_detach']),
              ),
            )
        return d

    def ruleset_attach(self):
        d = DIV(
              A(
                T("Attach child ruleset"),
                _class='attach16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='comp_ruleset_attach'),
              ),
              DIV(
                self.form_ruleset_attach,
                _style='display:none',
                _class='white_float',
                _name='comp_ruleset_attach',
                _id='comp_ruleset_attach',
              ),
            )
        return d

    def ruleset_add(self):
        d = DIV(
              A(
                T("Add ruleset"),
                _class='add16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='comp_ruleset_add'),
              ),
              DIV(
                self.form_ruleset_add,
                _style='display:none',
                _class='white_float',
                _name='comp_ruleset_add',
                _id='comp_ruleset_add',
              ),
            )
        return d

    @auth.requires_membership('CompManager')
    def comp_ruleset_attach_sqlform(self):
        if 'Manager' in user_groups():
            qu = db.comp_rulesets.id > 0
        else:
            qu = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
            qu &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
        allowed = db(qu)

        db.comp_rulesets_rulesets.parent_rset_id.requires = IS_IN_DB(
          allowed,
          db.comp_rulesets.id,
          "%(ruleset_name)s",
          zero=T('choose one')
        )
        q = db.comp_rulesets_rulesets.id > 0
        rows = db(q).select(db.comp_rulesets_rulesets.parent_rset_id,
                            groupby=db.comp_rulesets_rulesets.parent_rset_id)
        parent_rset_ids = [r.parent_rset_id for r in rows]
        q = ~db.comp_rulesets.id.belongs(parent_rset_ids)
        q &= db.comp_rulesets.id.belongs(allowed.select(db.comp_rulesets.id))
        db.comp_rulesets_rulesets.child_rset_id.requires = IS_IN_DB(
          db(q),
          db.comp_rulesets.id,
          "%(ruleset_name)s",
          zero=T('choose one'),
        )
        f = SQLFORM(
                 db.comp_rulesets_rulesets,
                 labels={
                         'parent_rset_id': T('Parent ruleset'),
                         'child_rset_id': T('Child ruleset'),
                        },
                 _name='form_ruleset_attach',
            )
        return f

    @auth.requires_membership('CompManager')
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
                T("Delete"),
                _class='del16',
                _onclick=self.ajax_submit(args=['ruleset_var_del']),
              ),
            )
        return d

    def ruleset_var_add(self):
        d = DIV(
              A(
                T("Add"),
                _class='add16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='comp_ruleset_var_add'),
              ),
              DIV(
                self.form_ruleset_var_add,
                _style='display:none',
                _class='white_float',
                _name='comp_ruleset_var_add',
                _id='comp_ruleset_var_add',
              ),
            )
        return d

    @auth.requires_membership('CompManager')
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

    @auth.requires_membership('CompManager')
    def comp_ruleset_var_add_sqlform(self):
        db.comp_rulesets_variables.id.readable = False
        db.comp_rulesets_variables.id.writable = False
        if 'Manager' in user_groups():
            q = db.comp_rulesets.id > 0
        else:
            q = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
            q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
        allowed = db(q)
        db.comp_rulesets_variables.ruleset_id.requires = IS_IN_DB(allowed,
                    db.comp_rulesets.id, "%(ruleset_name)s", zero=T('choose one'))

        q = db.forms.form_type == "obj"
        allowed = db(q)
        db.comp_rulesets_variables.var_class.requires = IS_IN_DB(allowed,
                    db.forms.form_name)
        f = SQLFORM(
                 db.comp_rulesets_variables,
                 labels={'ruleset_id': T('Ruleset name'),
                         'var_name': T('Variable'),
                         'var_value': T('Value')},
                 _name='form_var_add',
            )
        f.vars.var_author = user_name()
        if f.vars.var_name is not None:
            f.vars.var_name = f.vars.var_name.strip()
        return f

@auth.requires_membership('CompManager')
def team_responsible_attach(ids=[]):
    if len(ids) == 0:
        raise ToolError("no ruleset selected")
    ids = map(lambda x: x.split('_')[0], ids)
    group_id = request.vars.team_responsible_attach_s

    done = []
    for id in ids:
        if 'Manager' not in user_groups():
            q = db.comp_ruleset_team_responsible.ruleset_id == id
            q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
            if db(q).count() == 0:
                continue
        q = db.comp_ruleset_team_responsible.ruleset_id == id
        q &= db.comp_ruleset_team_responsible.group_id == group_id
        if db(q).count() != 0:
            continue
        done.append(id)
        db.comp_ruleset_team_responsible.insert(ruleset_id=id, group_id=group_id)
    if len(done) == 0:
        return
    rows = db(db.comp_rulesets.id.belongs(done)).select(db.comp_rulesets.ruleset_name)
    u = ', '.join([r.ruleset_name for r in rows])
    _log('ruleset.group.attach',
         'attached group %(g)s to rulesets %(u)s',
         dict(g=group_role(group_id), u=u))

@auth.requires_membership('CompManager')
def comp_ruleset_detach(ids=[]):
    if len(ids) == 0:
        raise ToolError("no ruleset selected")
    ids = map(lambda x: (x.split('_')[0], x.split('_')[3]), ids)

    done = []
    for parent_rset_id, child_rset_id in ids:
        # skip if not owner or Manager
        if 'Manager' not in user_groups():
            q = db.comp_ruleset_team_responsible.ruleset_id == parent_rset_id
            q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
            if db(q).count() == 0:
                continue

        q = db.comp_rulesets.id == parent_rset_id
        parent_rset_name = db(q).select().first().ruleset_name

        q = db.comp_rulesets.id == child_rset_id
        child_rset_name = db(q).select().first().ruleset_name

        q = db.comp_rulesets_rulesets.parent_rset_id == parent_rset_id
        q &= db.comp_rulesets_rulesets.child_rset_id == child_rset_id
        db(q).delete()

        done.append((parent_rset_name, child_rset_name))
    if len(done) == 0:
        return

    u = ', '.join([r[1]+" from "+r[0] for r in done])
    _log('ruleset.ruleset.detach',
         'detached ruleset %(u)s',
         dict(u=u))

@auth.requires_membership('CompManager')
def team_responsible_detach(ids=[]):
    if len(ids) == 0:
        raise ToolError("no ruleset selected")
    ids = map(lambda x: x.split('_')[0], ids)
    group_id = request.vars.team_responsible_detach_s

    done = []
    for id in ids:
        q = db.comp_ruleset_team_responsible.ruleset_id == id
        q &= db.comp_ruleset_team_responsible.group_id == group_id
        if 'Manager' not in user_groups():
            q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
        if db(q).count() == 0:
            continue
        done.append(id)
        db(q).delete()
    if len(done) == 0:
        return
    rows = db(db.comp_rulesets.id.belongs(done)).select(db.comp_rulesets.ruleset_name)
    u = ', '.join([r.ruleset_name for r in rows])
    _log('ruleset.group.detach',
         'detached group %(g)s from rulesets %(u)s',
         dict(g=group_role(group_id), u=u))

@auth.requires_membership('CompManager')
def ruleset_change_public(ids):
    sid = request.vars.rset_public_change_s
    if len(sid) == 0:
        raise ToolError("change ruleset publication failed: target publication is empty")
    if len(ids) == 0:
        raise ToolError("change ruleset publication failed: no ruleset selected")
    ids = map(lambda x: int(x.split('_')[0]), ids)

    q = db.comp_rulesets.id.belongs(ids)
    rows = db(q).select()
    if len(rows) == 0:
        raise ToolError("change ruleset publication failed: can't find ruleset")

    x = ', '.join(['from %s on %s'%(r.ruleset_public,r.ruleset_name) for r in rows])
    db(q).update(ruleset_public=sid)

    # purge attachments
    if sid == "F":
        q = db.comp_rulesets_nodes.ruleset_id.belongs(ids)
        db(q).delete()
        q = db.comp_rulesets_services.ruleset_id.belongs(ids)
        db(q).delete()

    _log('compliance.ruleset.publication.change',
         'changed ruleset publication to %(s)s %(x)s',
         dict(s=sid, x=x))

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

    # purge attachments
    if sid == "contextual":
        q = db.comp_rulesets_nodes.ruleset_id.belongs(ids)
        db(q).delete()
        q = db.comp_rulesets_services.ruleset_id.belongs(ids)
        db(q).delete()
    elif sid == "explicit":
        q = db.comp_rulesets_filtersets.ruleset_id.belongs(ids)
        db(q).delete()

    _log('compliance.ruleset.type.change',
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
    if rows[0].ruleset_type == 'contextual' and rows[0].fset_id is not None:
        db.comp_rulesets_filtersets.insert(ruleset_id=newid,
                                           fset_id=rows[0].fset_id)
    for row in rows:
        db.comp_rulesets_variables.insert(ruleset_id=newid,
                                          var_name=row.var_name,
                                          var_class=row.var_class,
                                          var_value=row.var_value,
                                          var_author=user_name())
    add_default_team_responsible(iid)

    # clone parent to children relations
    q = db.comp_rulesets_rulesets.parent_rset_id==sid
    rows = db(q).select()
    for child_rset_id in [r.child_rset_id for r in rows]:
        db.comp_rulesets_rulesets.insert(parent_rset_id=newid,
                                         child_rset_id=child_rset_id)

    _log('compliance.ruleset.clone',
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
    if 'Manager' not in user_groups():
        # filter ids to not allow a user to delete a ruleset he does not own
        q = db.comp_ruleset_team_responsible.ruleset_id.belongs(ids)
        q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
        rows = db(q).select(groupby=db.comp_ruleset_team_responsible.ruleset_id)
        ids = [r.ruleset_id for r in rows]
        if len(ids) == 0:
            raise ToolError("delete ruleset failed: no ruleset deletion allowed")
    rows = db(db.comp_rulesets.id.belongs(ids)).select(db.comp_rulesets.ruleset_name)
    x = ', '.join([str(r.ruleset_name) for r in rows])
    n = db(db.comp_ruleset_team_responsible.ruleset_id.belongs(ids)).delete()
    n = db(db.comp_rulesets_filtersets.ruleset_id.belongs(ids)).delete()
    n = db(db.comp_rulesets_variables.ruleset_id.belongs(ids)).delete()
    n = db(db.comp_rulesets.id.belongs(ids)).delete()
    n = db(db.comp_rulesets_nodes.ruleset_id.belongs(ids)).delete()
    n = db(db.comp_rulesets_services.ruleset_id.belongs(ids)).delete()
    _log('compliance.ruleset.delete',
         'deleted rulesets %(x)s',
         dict(x=x))

@auth.requires_membership('CompManager')
def comp_delete_ruleset_var(ids=[]):
    if len(ids) == 0:
        raise ToolError("delete variables failed: no variable selected")
    _ids = []
    for s in ids:
        l = s.split('_')
        if len(l) != 4:
            continue
        if l[2] == "None":
            continue
        if l[3] != "None":
            raise ToolError("Deleting variables in a encapsulated ruleset is not allowed. Please detach the encapsulated ruleset, or delete the variables from the ruleset owning the variables directly.")
        _ids.append(int(l[2]))
    ids = _ids
    if len(ids) == 0:
        raise ToolError("delete variables failed: no variable selected")
    q = db.v_comp_rulesets.id.belongs(ids)
    q &= db.v_comp_rulesets.encap_rset_id == None
    rows = db(q).select()
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
def comp_detach_rulesets(node_ids=[], ruleset_ids=[], node_names=[]):
    if len(node_ids) + len(node_names) == 0:
        raise ToolError("detach ruleset failed: no node selected")
    if len(ruleset_ids) == 0:
        raise ToolError("detach ruleset failed: no ruleset selected")

    if len(node_ids) > 0:
        q = db.v_nodes.id.belongs(node_ids)
        rows = db(q).select(db.v_nodes.nodename)
        node_names += [r.nodename for r in rows]

    nodes = ', '.join(node_names)

    for rsid in ruleset_ids:
        for node in node_names:
            q = db.comp_rulesets_nodes.nodename == node
            q &= db.comp_rulesets_nodes.ruleset_id == rsid
            db(q).delete()

    for node in node_names:
        update_dash_rsetdiff_node(node)

    q = db.comp_rulesets.id.belongs(ruleset_ids)
    rows = db(q).select(db.comp_rulesets.ruleset_name)
    rulesets = ', '.join([r.ruleset_name for r in rows])
    _log('compliance.ruleset.node.detach',
         'detached rulesets %(rulesets)s from nodes %(nodes)s',
         dict(rulesets=rulesets, nodes=nodes))

@auth.requires_membership('CompManager')
def comp_attach_rulesets(node_ids=[], ruleset_ids=[], node_names=[]):
    if len(node_ids) + len(node_names) == 0:
        raise ToolError("attach ruleset failed: no node selected")
    if len(ruleset_ids) == 0:
        raise ToolError("attach ruleset failed: no ruleset selected")

    if len(node_ids) > 0:
        q = db.v_nodes.id.belongs(node_ids)
        rows = db(q).select(db.v_nodes.nodename)
        node_names += [r.nodename for r in rows]

    nodes = ', '.join(node_names)

    for rsid in ruleset_ids:
        for node in node_names:
            q = db.comp_rulesets_nodes.nodename == node
            q &= db.comp_rulesets_nodes.ruleset_id == rsid
            if db(q).count() == 0:
                db.comp_rulesets_nodes.insert(nodename=node,
                                            ruleset_id=rsid)

    for node in node_names:
        update_dash_rsetdiff_node(node)

    q = db.comp_rulesets.id.belongs(ruleset_ids)
    rows = db(q).select(db.comp_rulesets.ruleset_name)
    rulesets = ', '.join([r.ruleset_name for r in rows])
    _log('compliance.ruleset.node.attach',
         'attached rulesets %(rulesets)s to nodes %(nodes)s',
         dict(rulesets=rulesets, nodes=nodes))

@auth.requires_membership('CompManager')
def comp_attach_svc_modulesets(svc_ids=[], modset_ids=[], svc_names=[], slave=True):
    if len(svc_ids) + len(svc_names) == 0:
        raise ToolError("attach moduleset failed: no service selected")
    if len(modset_ids) == 0:
        raise ToolError("attach moduleset failed: no moduleset selected")

    log = []

    if len(svc_ids) > 0:
        q = db.services.id.belongs(svc_ids)
        rows = db(q).select(db.services.svc_name)
        svc_names += [r.svc_name for r in rows]

    # init rset name cache
    q = db.comp_moduleset.id.belongs(modset_ids)
    rows = db(q).select()
    modset_names = {}
    for row in rows:
        modset_names[row.id] = row.modset_name

    for modset_id in modset_ids:
        for svc in svc_names:
            sl = slave
            if slave and not has_slave(svc):
                sl = False
            q = db.comp_modulesets_services.modset_svcname == svc
            q &= db.comp_modulesets_services.modset_id == modset_id
            q &= db.comp_modulesets_services.slave == sl
            row = db(q).select().first()
            if row is not None:
                log.append([
                  'compliance.moduleset.service.attach',
                  'moduleset %(moduleset)s already attached to service %(service)s',
                  dict(moduleset=modset_names[modset_id], service=svc),
                ])
                continue
            db.comp_modulesets_services.insert(modset_svcname=svc,
                                               slave=sl,
                                               modset_id=modset_id)
            log.append([
              'compliance.moduleset.service.attach',
              'moduleset %(moduleset)s attached to service %(service)s',
              dict(moduleset=modset_names[modset_id], service=svc),
            ])

    for action, fmt, d in log:
        _log(action, fmt, d)

    for svc in svc_names:
        update_dash_moddiff(svc)

    return log

@auth.requires_membership('CompManager')
def comp_attach_svc_rulesets(svc_ids=[], ruleset_ids=[], svc_names=[], slave=True):
    if len(svc_ids) + len(svc_names) == 0:
        raise ToolError("attach ruleset failed: no service selected")
    if len(ruleset_ids) == 0:
        raise ToolError("attach ruleset failed: no ruleset selected")

    log = []

    if len(svc_ids) > 0:
        q = db.services.id.belongs(svc_ids)
        rows = db(q).select(db.services.svc_name)
        svc_names += [r.svc_name for r in rows]

    # init rset name cache
    q = db.comp_rulesets.id.belongs(ruleset_ids)
    rows = db(q).select()
    rset_names = {}
    for row in rows:
        rset_names[row.id] = row.ruleset_name

    for rsid in ruleset_ids:
        for svc in svc_names:
            sl = slave
            if slave and not has_slave(svc):
                sl = False
            q = db.comp_rulesets_services.svcname == svc
            q &= db.comp_rulesets_services.ruleset_id == rsid
            q &= db.comp_rulesets_services.slave == sl
            row = db(q).select().first()
            if row is not None:
                log.append([
                  'compliance.ruleset.service.attach',
                  'ruleset %(ruleset)s already attached to service %(service)s',
                  dict(ruleset=rset_names[rsid], service=svc),
                ])
                continue
            db.comp_rulesets_services.insert(svcname=svc,
                                             slave=sl,
                                             ruleset_id=rsid)
            log.append([
              'compliance.ruleset.service.attach',
              'ruleset %(ruleset)s attached to service %(service)s',
              dict(ruleset=rset_names[rsid], service=svc),
            ])

    for action, fmt, d in log:
        _log(action, fmt, d)

    for svc in svc_names:
        update_dash_rsetdiff(svc)

    return log

@auth.requires_login()
def ajax_comp_rulesets_col_values():
    t = table_comp_rulesets('cr0', 'ajax_comp_rulesets')
    col = request.args[0]
    o = db.v_comp_rulesets[col]
    q = db.v_comp_rulesets.id > 0
    for f in t.cols:
        q = _where(q, 'v_comp_rulesets', t.filter_parse_glob(f), f)
    t.object_list = db(q).select(o, orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_comp_rulesets():
    v = table_comp_rulesets('cr0', 'ajax_comp_rulesets')
    v.span = 'ruleset_name'
    v.sub_span = ['ruleset_type', 'ruleset_public', 'fset_name', 'teams_responsible']
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
            elif action == 'ruleset_change_public':
                ruleset_change_public(v.get_checked())
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
            elif action == 'ruleset_detach':
                comp_ruleset_detach(v.get_checked())
            elif action == 'ruleset_rename':
                comp_rename_ruleset(v.get_checked())
                v.form_filterset_attach = v.comp_filterset_attach_sqlform()
                v.form_ruleset_var_add = v.comp_ruleset_var_add_sqlform()
            elif action == 'team_responsible_attach':
                team_responsible_attach(v.get_checked())
            elif action == 'team_responsible_detach':
                team_responsible_detach(v.get_checked())
        except ToolError, e:
            v.flash = str(e)
    elif len(request.args) == 2:
        action = request.args[0]
        name = request.args[1]
        try:
            if action == 'var_value_set_list':
                var_value_set_list(name)
            elif action == 'var_value_set_dict':
                var_value_set_dict(name)
            elif action == 'var_value_set_vuln':
                var_value_set_list_of_dict(name)
            elif action == 'var_value_set_fs':
                var_value_set_list_of_dict(name)
            elif action == 'var_value_set_process':
                var_value_set_list_of_dict(name)
            elif action == 'var_value_set_nodeconf':
                var_value_set_list_of_dict(name)
            elif action == 'var_value_set_etcsystem':
                var_value_set_list_of_dict(name)
            elif action == 'var_value_set_crontabentry':
                var_value_set_list_of_dict(name)
            elif action == 'var_value_set_fileinc':
                var_value_set_list_of_dict(name)
            elif action == 'var_value_set_fileprop':
                var_value_set_list_of_dict(name)
            elif action == 'var_value_set_rc':
                var_value_set_list_of_dict(name)
            elif action == 'var_value_set_user':
                var_value_set_dict_dict(name, 'user')
            elif action == 'var_value_set_cron':
                var_value_set_cron(name)
            elif action == 'var_value_set_group':
                var_value_set_dict_dict(name, 'group')
        except ToolError, e:
            v.flash = str(e)

    try:
        if v.form_ruleset_attach.accepts(request.vars, formname='attach_ruleset'):
            _log('compliance.ruleset.ruleset.attach',
                 'attach ruleset %(child)s to %(parent)s',
                 dict(parent=db(db.comp_rulesets.id==request.vars.parent_rset_id).select().first().ruleset_name,
                      child=db(db.comp_rulesets.id==request.vars.child_rset_id).select().first().ruleset_name))
        elif v.form_ruleset_attach.errors:
            response.flash = T("errors in form")

        if v.form_ruleset_add.accepts(request.vars, formname='add_ruleset'):
            # refresh forms ruleset comboboxes
            v.form_filterset_attach = v.comp_filterset_attach_sqlform()
            v.form_ruleset_var_add = v.comp_ruleset_var_add_sqlform()
            add_default_team_responsible(request.vars.ruleset_name)
            _log('compliance.ruleset.add',
                 'added ruleset %(ruleset)s',
                 dict(ruleset=request.vars.ruleset_name))
        elif v.form_ruleset_add.errors:
            response.flash = T("errors in form")

        if v.form_filterset_attach.accepts(request.vars):
            g = db.v_comp_rulesets.fset_id|db.v_comp_rulesets.ruleset_id
            q = db.v_comp_rulesets.fset_id == request.vars.fset_id
            q &= db.v_comp_rulesets.ruleset_id == request.vars.ruleset_id
            rows = db(q).select(groupby=g)
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
    except AttributeError:
        pass
    except ToolError, e:
        v.flash = str(e)

    o = db.v_comp_rulesets.ruleset_name|db.v_comp_rulesets.var_name
    g = db.v_comp_rulesets.ruleset_id|db.v_comp_rulesets.id
    q = teams_responsible_filter()
    for f in v.cols:
        q = _where(q, 'v_comp_rulesets', v.filter_parse(f), f)

    n = db(q).count()
    v.setup_pager(n)
    v.object_list = db(q).select(limitby=(v.pager_start,v.pager_end), orderby=o, groupby=g)

    return v.html()

def add_default_team_responsible(ruleset_name):
    q = db.comp_rulesets.ruleset_name == ruleset_name
    ruleset_id = db(q).select()[0].id
    q = db.auth_membership.user_id == auth.user_id
    q &= db.auth_membership.group_id == db.auth_group.id
    q &= db.auth_group.role.like('user_%')
    try:
        group_id = db(q).select()[0].auth_group.id
    except:
        q = db.auth_group.role == 'Manager'
        group_id = db(q).select()[0].id
    db.comp_ruleset_team_responsible.insert(ruleset_id=ruleset_id, group_id=group_id)

def teams_responsible_filter():
    if 'Manager' in user_groups():
        q = db.v_comp_rulesets.ruleset_id > 0
    else:
        q = db.v_comp_rulesets.ruleset_id == db.comp_ruleset_team_responsible.ruleset_id
        q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    return q

@auth.requires_login()
def comp_rules():
    t = DIV(
          DIV(
            ajax_comp_rulesets(),
            _id='cr0',
          ),
        )
    return dict(table=t)

@auth.requires_login()
def comp_rulesets_nodes_attachment():
    t = DIV(
          DIV(
            ajax_comp_rulesets_nodes(),
            _id='crn1',
          ),
        )
    return dict(table=t)

#
# Filters sub-view
#
filters_colprops = {
    'f_table': col_comp_filters_table(
             title='Table',
             field='f_table',
             display=True,
             img='filter16',
            ),
    'f_field': col_comp_filters_field(
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
                     'f_log_op',
                     'f_order',
                     'encap_fset_name']
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
            'f_order': HtmlTableColumn(
                     title='Ordering',
                     field='f_order',
                     display=False,
                     img='filter16',
                    ),
            'encap_fset_name': HtmlTableColumn(
                     title='Encap filterset',
                     field='encap_fset_name',
                     display=True,
                     img='filter16',
                    ),
        }
        self.colprops.update(filters_colprops)
        if 'CompManager' in user_groups():
            self.form_encap_filterset_attach = self.comp_encap_filterset_attach_sqlform()
            self.form_filterset_add = self.comp_filterset_add_sqlform()
            self.form_filter_attach = self.comp_filter_attach_sqlform()
            self += HtmlTableMenu('Filter', 'filters', ['filter_attach', 'filter_detach'])
            self += HtmlTableMenu('Filterset', 'filters', ['filterset_add', 'filterset_del', 'filterset_rename', 'encap_filterset_attach', 'filter_detach'])
        self.ajax_col_values = ajax_comp_filtersets_col_values
        self.dbfilterable = False

    def checkbox_key(self, o):
        if o is None:
            return '_'.join((self.id, 'ckid', ''))
        ids = []
        ids.append(o['fset_id'])
        ids.append(o['id'])
        ids.append(o['encap_fset_id'])
        return '_'.join([self.id, 'ckid']+map(str,ids))

    def filter_detach(self):
        d = DIV(
              A(
                T("Detach"),
                _class='detach16',
                _onclick=self.ajax_submit(args=['detach_filters'])
              ),
            )
        return d

    def filterset_rename(self):
        d = DIV(
              A(
                T("Rename"),
                _class='edit16',
                _onclick="""click_toggle_vis(event,'%(div)s', 'block');
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
            )
        return d

    def filterset_del(self):
        d = DIV(
              A(
                T("Delete"),
                _class='del16',
                _onclick="""if (confirm("%(text)s")){%(s)s};
                         """%dict(s=self.ajax_submit(args=['delete_filterset']),
                                  text=T("Deleting a filterset also deletes the filterset filter attachments. Please confirm filterset deletion."),
                                 ),
              ),
            )
        return d

    def encap_filterset_attach(self):
        d = DIV(
              A(
                T("Attach"),
                _class='attach16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='comp_encap_filterset_attach'),
              ),
              DIV(
                self.form_encap_filterset_attach,
                _style='display:none',
                _class='white_float',
                _name='comp_encap_filterset_attach',
                _id='comp_encap_filterset_attach',
              ),
            )
        return d

    def filter_attach(self):
        d = DIV(
              A(
                T("Attach"),
                _class='attach16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='comp_filter_attach'),
              ),
              DIV(
                self.form_filter_attach,
                _style='display:none',
                _class='white_float',
                _name='comp_filter_attach',
                _id='comp_filter_attach',
              ),
            )
        return d

    def filterset_add(self):
        d = DIV(
              A(
                T("Add"),
                _class='add16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='comp_filterset_add'),
              ),
              DIV(
                self.form_filterset_add,
                _style='display:none',
                _class='white_float',
                _name='comp_filterset_add',
                _id='comp_filterset_add',
              ),
            )
        return d

    @auth.requires_membership('CompManager')
    def comp_encap_filterset_attach_sqlform(self):
        db.gen_filtersets_filters.fset_id.readable = True
        db.gen_filtersets_filters.fset_id.writable = True
        db.gen_filtersets_filters.f_log_op.readable = True
        db.gen_filtersets_filters.f_log_op.writable = True
        db.gen_filtersets_filters.f_id.readable = False
        db.gen_filtersets_filters.f_id.writable = True
        db.gen_filtersets_filters.encap_fset_id.readable = True
        db.gen_filtersets_filters.encap_fset_id.writable = True
        db.gen_filtersets_filters.f_order.default = 0
        db.gen_filtersets_filters.fset_id.requires = IS_IN_DB(
            db,
            db.gen_filtersets.id,
            "%(fset_name)s",
            zero=T('choose one')
        )
        if 'fset_id' in request.vars:
            q = db.gen_filtersets_filters.encap_fset_id == request.vars.encap_fset_id
            q &= db.gen_filtersets_filters.fset_id == request.vars.fset_id
            existing = db(q)
            encap_fset_id_validator = IS_NOT_IN_DB(
                existing, 'gen_filtersets_filters.encap_fset_id')
            allowed = db(db.gen_filtersets.id != request.vars.fset_id)
        else:
            encap_fset_id_validator = None
            allowed = db(db.gen_filtersets.id > 0)

        db.gen_filtersets_filters.encap_fset_id.requires = IS_IN_DB(
            allowed,
            db.gen_filtersets.id,
            "%(fset_name)s",
            zero=T('choose one'),
            _and=encap_fset_id_validator
        )

        f = SQLFORM(
                 db.gen_filtersets_filters,
                 fields=['fset_id', 'encap_fset_id', 'f_log_op', 'f_order'],
                 labels={'fset_id': T('Parent filterset'),
                         'encap_fset_id': T('Child filterset'),
                         'f_log_op': T('Operator'),
                         'f_order': T('Order'),
                        },
                 _name='form_encap_filterset_attach',
            )

        # default values
        f.vars.f_log_op = 'AND'

        return f

    @auth.requires_membership('CompManager')
    def comp_filter_attach_sqlform(self):
        db.gen_filtersets_filters.fset_id.readable = True
        db.gen_filtersets_filters.fset_id.writable = True
        db.gen_filtersets_filters.f_id.readable = True
        db.gen_filtersets_filters.f_id.writable = True
        db.gen_filtersets_filters.f_log_op.readable = True
        db.gen_filtersets_filters.f_log_op.writable = True
        db.gen_filtersets_filters.encap_fset_id.readable = False
        db.gen_filtersets_filters.encap_fset_id.writable = True
        db.gen_filtersets_filters.f_order.default = 0
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
                 fields=['fset_id', 'f_id', 'f_log_op', 'f_order'],
                 labels={'fset_id': T('Filterset'),
                         'f_id': T('Filter'),
                         'f_log_op': T('Operator'),
                         'f_order': T('Order'),
                        },
                 _name='form_filterset_add',
            )

        # default values
        f.vars.f_log_op = 'AND'

        return f

    @auth.requires_membership('CompManager')
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
    ids = map(lambda x: map(int, (x.replace('None','0').split('_'))), ids)
    q = db.v_gen_filtersets.id < 0
    for (fset_id, f_id, encap_fset_id) in ids:
        if encap_fset_id > 0:
            q |= ((db.v_gen_filtersets.encap_fset_id == encap_fset_id) & (db.v_gen_filtersets.fset_id == fset_id))
        else:
            q |= ((db.v_gen_filtersets.f_id == f_id) & (db.v_gen_filtersets.fset_id == fset_id))
    rows = db(q).select()
    if len(rows) == 0:
        raise ToolError("detach filter failed: can't find selected filters")

    def print_filter(f):
        if f.encap_fset_id > 0:
            return ' '.join([
                       f.encap_fset_name,
                       'from',
                       f.fset_name])
        else:
            return ' '.join([
                       f.f_table+'.'+f.f_field,
                       f.f_op,
                       f.f_value,
                       'from',
                       f.fset_name])

    f_names = ', '.join(map(print_filter, rows))
    q = db.gen_filtersets_filters.id < 0
    for (fset_id, f_id, encap_fset_id) in ids:
        if encap_fset_id > 0:
            q |= ((db.gen_filtersets_filters.encap_fset_id == encap_fset_id) & (db.gen_filtersets_filters.fset_id == fset_id))
        else:
            q |= ((db.gen_filtersets_filters.f_id == f_id) & (db.gen_filtersets_filters.fset_id == fset_id))
    db(q).delete()
    _log('compliance.filterset.filter.detach',
        'detached filters %(f_names)s',
        dict(f_names=f_names))

@auth.requires_membership('CompManager')
def comp_delete_filterset(ids=[]):
    if len(ids) == 0:
        raise ToolError("delete filterset failed: no filterset selected")
    ids = map(lambda x: int(x.split('_')[0]), ids)

    # purge filters joins
    q = db.gen_filtersets_filters.fset_id.belongs(ids)
    n = db(q).delete()

    # purge ruleset joins
    q = db.comp_rulesets_filtersets.fset_id.belongs(ids)
    n = db(q).delete()

    # delete filtersets
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
    if len(db(db.gen_filtersets.fset_name==new).select()) > 0:
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
        if 'CompManager' in user_groups():
            self += HtmlTableMenu('Filter', 'filters', ['filter_add', 'filter_del'], id='menu_filters1')
        self.ajax_col_values = 'ajax_comp_filters_col_values'
        self.dbfilterable = False

    def filter_del(self):
        d = DIV(
              A(
                T("Delete"),
                _class='del16',
                _onclick="""if (confirm("%(text)s")){%(s)s};"""%dict(
                   s=self.ajax_submit(args=['delete_filter']),
                   text=T("Deleting a filter also deletes its membership in filtersets. Please confirm filter deletion"),
                ),
              ),
            )
        return d

    def filter_add(self):
        d = DIV(
              A(
                T("Add"),
                _class='add16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='comp_filter_add'),
              ),
              DIV(
                self.comp_filter_add(),
                _style='display:none',
                _class='white_float',
                _name='comp_filter_add',
                _id='comp_filter_add',
              ),
            )
        return d

    @auth.requires_membership('CompManager')
    def comp_filter_add(self):
        def format_table(table):
            d = LI(
                  T(table['title']),
                  _class=table['cl'],
                  _name='table_opt',
                  _id=table['name'],
                  _onclick="""$('[name=table_opt]').removeClass("highlight");
                              $('[name=field_opt]').removeClass("highlight");
                              $('[name=fields]').hide();
                              $('#%(id)s').toggleClass("highlight");
                              $('#fields_%(id)s').show();
                              $('#f_table').val('%(id)s');
                           """%dict(id=table['name'])
                )
            return d

        def format_op(op):
            d = LI(
                  T(op['title']),
                  _name='op_opt',
                  _id=op['id'],
                  _onclick="""$('[name=op_opt]').removeClass("highlight");
                              $('#%(id)s').toggleClass("highlight");
                              $('#value').show();
                              $('#f_op').val('%(val)s');
                           """%dict(id=op['id'], val=op['title'])
                )
            return d

        def __format_table_fields(f):
            title = props[f].title
            img = props[f].img
            d = LI(
                  T(title),
                  _class=img.replace('.png',''),
                  _name='field_opt',
                  _id=f,
                  _onclick="""$('[name=field_opt]').removeClass("highlight");
                              $('#%(id)s').toggleClass("highlight");
                              $('#ops').show();
                              $('#f_field').val('%(id)s');
                           """%dict(id=f)
                )
            return d

        def _format_table_fields(table):
            fl = []
            for f in fields[table['name']]:
                fl.append(__format_table_fields(f))
            return fl

        def format_table_fields(table):
            s = SPAN(
                  H3(T('Fields')),
                  UL(_format_table_fields(table)),
                  _id='fields_'+table['name'],
                  _name='fields',
                  _style='display:none',
                )
            return s

        tl = []
        fl = []
        ol = []
        for t in tables.values():
            if t['hide']: continue
            tl.append(format_table(t))
            fl.append(format_table_fields(t))
        for o in operators:
            ol.append(format_op(o))

        d = DIV(
              H3(T('Tables')),
              UL(tl),
              SPAN(fl),
              SPAN(
                H3(T('Operator')),
                UL(ol),
                _id='ops',
                _style='display:none',
              ),
              SPAN(
                H3(T('Value')),
                UL(
                  INPUT(
                    _id='f_value',
                    _onkeypress=self.ajax_enter_submit(additional_inputs=['f_table',
                                                                          'f_field',
                                                                          'f_op',
                                                                          'f_value'],
                                                       args=['add_filter']),
                  ),
                ),
                _id='value',
                _style='display:none',
              ),
              INPUT(
                _id='f_table',
                _style='display:none',
              ),
              INPUT(
                _id='f_field',
                _style='display:none',
              ),
              INPUT(
                _id='f_op',
                _style='display:none',
              ),
              _class='ax_form',
            )
        return d

@auth.requires_membership('CompManager')
def comp_add_filter():
    f_table = request.vars.f_table
    f_field = request.vars.f_field
    f_op = request.vars.f_op
    f_value = request.vars.f_value

    if f_table not in db:
        raise ToolError("add filter failed: table not found")
    if f_field not in db[f_table]:
        raise ToolError("add filter failed: field not found")

    try:
        db.gen_filters.insert(f_table=f_table,
                              f_field=f_field,
                              f_op=f_op,
                              f_value=f_value,
                              f_author=user_name())
    except:
        raise ToolError("add filter failed: already exist ?")

    f_name = ' '.join([f_table+'.'+f_field, f_op, f_value])
    _log('compliance.filter.add', 'added filter %(f_name)s',
         dict(f_name=f_name))

@auth.requires_membership('CompManager')
def comp_delete_filtersets_filters(ids, f_names):
    q = db.gen_filtersets_filters.f_id.belongs(ids)
    rows = db(q).select()
    if len(rows) == 0:
        return
    fset_ids = [r.fset_id for r in rows]
    q2 = db.gen_filtersets.id.belongs(fset_ids)
    fset_names = ', '.join([r.fset_name for r in db(q2).select()])
    n = db(q).delete()
    _log('compliance.filter.delete',
         'deleted filter %(f_names)s membership in filtersets %(fset_names)s',
         dict(f_names=f_names, fset_names=fset_names))


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

    # delete filterset membership for the filters
    comp_delete_filtersets_filters(ids, f_names)

    # delete filters
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
    t.object_list = db(q).select(o, orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_comp_filters():
    extra = SPAN()
    v = table_comp_filters('ajax_comp_filters',
                           'ajax_comp_filters')
    v.span = 'f_table'
    v.checkboxes = True
    reload_fsets = SCRIPT(
                     "table_ajax_submit('/init/compliance/ajax_comp_filtersets', 'ajax_comp_filtersets', inputs_ajax_comp_filtersets, [], ['ajax_comp_filtersets_ck'])",
                     _name=v.id+"_to_eval",
                   )

    if len(request.args) == 1:
        action = request.args[0]
        try:
            if action == 'delete_filter':
                comp_delete_filter(v.get_checked())
                extra = reload_fsets
            elif action == 'add_filter':
                comp_add_filter()
                extra = reload_fsets
        except ToolError, e:
            v.flash = str(e)

    o = db.gen_filters.f_table|db.gen_filters.f_field|db.gen_filters.f_op|db.gen_filters.f_field
    q = db.gen_filters.id > 0
    for f in v.cols:
        q = _where(q, 'gen_filters', v.filter_parse(f), f)

    n = db(q).count()
    v.setup_pager(n)
    v.object_list = db(q).select(limitby=(v.pager_start,v.pager_end), orderby=o)

    return SPAN(v.html(),extra)

@auth.requires_login()
def ajax_comp_filtersets_col_values():
    t = table_comp_filtersets('ajax_comp_filtersets', 'ajax_comp_filtersets')
    col = request.args[0]
    o = db.v_gen_filtersets[col]
    q = db.v_gen_filtersets.fset_id > 0
    for f in t.cols:
        q = _where(q, 'v_gen_filtersets', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, groupby=o)
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
                t.form_encap_filterset_attach = t.comp_encap_filterset_attach_sqlform()
            elif action == 'detach_filters':
                comp_detach_filters(t.get_checked())
            elif action == 'filterset_rename':
                comp_rename_filterset(t.get_checked())
                t.form_filter_attach = t.comp_filter_attach_sqlform()
                t.form_encap_filterset_attach = t.comp_encap_filterset_attach_sqlform()
        except ToolError, e:
            t.flash = str(e)

    try:
        if t.form_filterset_add.accepts(request.vars):
            t.form_filter_attach = t.comp_filter_attach_sqlform()
            t.form_encap_filterset_attach = t.comp_encap_filterset_attach_sqlform()
            _log('compliance.filterset.add',
                'added filterset %(fset_name)s',
                dict(fset_name=request.vars.fset_name))
        elif t.form_filterset_add.errors:
            response.flash = T("errors in form")

        if t.form_encap_filterset_attach.accepts(request.vars, formname='form_encap_filterset_attach'):
            q = db.v_gen_filtersets.encap_fset_id==request.vars.encap_fset_id
            q &= db.v_gen_filtersets.fset_id==request.vars.fset_id
            f = db(q).select()[0]
            f_name = ' '.join([request.vars.f_log_op,
                               f.encap_fset_name])
            _log('compliance.filterset.filterset.attach',
                'filterset %(f_name)s attached to filterset %(fset_name)s',
                dict(f_name=f_name, fset_name=f.fset_name))
        elif t.form_filter_attach.errors:
            response.flash = T("errors in form")

        if t.form_filter_attach.accepts(request.vars, formname='form_filter_attach'):
            q = db.v_gen_filtersets.f_id==request.vars.f_id
            q &= db.v_gen_filtersets.fset_id==request.vars.fset_id
            f = db(q).select()[0]
            f_name = ' '.join([request.vars.f_log_op,
                               f.f_table+'.'+f.f_field,
                               f.f_op,
                               f.f_value])
            _log('compliance.filterset.filter.attach',
                'filter %(f_name)s attached to filterset %(fset_name)s',
                dict(f_name=f_name, fset_name=f.fset_name))
        elif t.form_filter_attach.errors:
            #raise Exception("1:"+str(t.form_filter_attach.errors))
            response.flash = T("errors in form")
    except AttributeError:
        pass

    o = db.v_gen_filtersets.fset_name|db.v_gen_filtersets.f_order|db.v_gen_filtersets.join_id
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
                     'teams_responsible',
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
            'teams_responsible': HtmlTableColumn(
                     title='Teams responsible',
                     table='v_comp_moduleset_teams_responsible',
                     field='teams_responsible',
                     display=True,
                     img='guy16',
                    ),
        }
        self.ajax_col_values = ajax_comp_moduleset_col_values
        self.colprops['modset_mod_name'].t = self
        if 'CompManager' in user_groups():
            self.form_module_add = self.comp_module_add_sqlform()
            self.form_moduleset_add = self.comp_moduleset_add_sqlform()
            self += HtmlTableMenu('Module', 'action16', ['module_add', 'module_del'])
            self += HtmlTableMenu('Moduleset', 'action16', ['moduleset_add',
                                                            'moduleset_del',
                                                            'moduleset_rename',
                                                            'moduleset_node_attach'])
            self += HtmlTableMenu('Team responsible', 'guys16', ['team_responsible_attach', 'team_responsible_detach'])
        self.sub_span = ['teams_responsible']

    def moduleset_node_attach(self):
        return A(
                 T("Modulesets/Nodes attachment"),
                 _href=URL(r=request, f="comp_modulesets_nodes"),
                 _class="attach16",
               )

    def checkbox_key(self, o):
        if o is None:
            return '_'.join((self.id, 'ckid', ''))
        id1 = o['comp_moduleset']['id']
        id2 = o['comp_moduleset_modules']['id']
        return '_'.join((self.id, 'ckid', str(id1), str(id2)))

    def team_responsible_select_tool(self, label, action, divid, sid, _class=''):
        if 'Manager' not in user_groups():
            s = """and role in (
                     select g.role from
                       auth_group g
                       join auth_membership gm on g.id=gm.group_id
                       join auth_user u on gm.user_id=u.id
                     where
                       u.id=%d
                  )"""%auth.user_id
        else:
            s = ""
        sql = """ select id, role
                  from auth_group
                  where
                    role not like "user_%%" and
                    privilege = 'F'
                    %s
                  group by role order by role
        """%s
        rows = db.executesql(sql)
        options = [OPTION(g[1],_value=g[0]) for g in rows]

        q = db.auth_membership.user_id == auth.user_id
        q &= db.auth_group.id == db.auth_membership.group_id
        q &= db.auth_group.role.like('user_%')
        options += [OPTION(g.auth_group.role,_value=g.auth_group.id) for g in db(q).select()]
        d = DIV(
              A(
                T(label),
                _class=_class,
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div=divid),
              ),
              DIV(
                TABLE(
                  TR(
                    TH(T('Team')),
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
                _id=divid,
              ),
            )
        return d

    def team_responsible_attach(self):
        d = self.team_responsible_select_tool(label="Attach",
                                              action="team_responsible_attach",
                                              divid="team_responsible_attach",
                                              sid="team_responsible_attach_s",
                                              _class="attach16")
        return d

    def team_responsible_detach(self):
        d = self.team_responsible_select_tool(label="Detach",
                                              action="team_responsible_detach",
                                              divid="team_responsible_detach",
                                              sid="team_responsible_detach_s",
                                              _class="detach16")
        return d

    def moduleset_rename(self):
        d = DIV(
              A(
                T("Rename"),
                _class='edit16',
                _onclick="""click_toggle_vis(event,'%(div)s', 'block');
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
            )
        return d

    def moduleset_del(self):
        d = DIV(
              A(
                T("Delete"),
                _class='del16',
                _onclick="""if (confirm("%(text)s")){%(s)s};
                         """%dict(s=self.ajax_submit(args=['moduleset_del']),
                                  text=T("Deleting a moduleset also deletes the moduleset module attachments. Please confirm moduleset deletion."),
                                 ),
              ),
            )
        return d

    def moduleset_add(self):
        d = DIV(
              A(
                T("Add"),
                _class='add16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='comp_moduleset_add'),
              ),
              DIV(
                self.form_moduleset_add,
                _style='display:none',
                _class='white_float',
                _name='comp_moduleset_add',
                _id='comp_moduleset_add',
              ),
            )
        return d


    def module_del(self):
        d = DIV(
              A(
                T("Delete"),
                _class='del16',
                _onclick=self.ajax_submit(args=['module_del']),
              ),
            )
        return d

    def module_add(self):
        d = DIV(
              A(
                T("Add"),
                _class='add16',
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='comp_module_add'),
              ),
              DIV(
                self.form_module_add,
                _style='display:none',
                _class='white_float',
                _name='comp_module_add',
                _id='comp_module_add',
              ),
            )
        return d

    @auth.requires_membership('CompManager')
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

    @auth.requires_membership('CompManager')
    def comp_module_add_sqlform(self):
        db.comp_moduleset_modules.modset_id.readable = True
        db.comp_moduleset_modules.modset_id.writable = True
        db.comp_moduleset_modules.modset_mod_name.readable = True
        db.comp_moduleset_modules.modset_mod_name.writable = True
        db.comp_moduleset_modules.modset_mod_author.readable = False
        db.comp_moduleset_modules.modset_mod_author.writable = False
        db.comp_moduleset_modules.modset_mod_updated.readable = False
        db.comp_moduleset_modules.modset_mod_updated.writable = False

        if "Manager" in user_groups():
            q = db.comp_moduleset.id > 0
        else:
            q = db.comp_moduleset_team_responsible.modset_id == db.comp_moduleset.id
            q &= db.comp_moduleset_team_responsible.group_id == db.auth_group.id
            q &= db.auth_group.id == db.auth_membership.group_id
            q &= db.auth_user.id == db.auth_membership.user_id
            q &= db.auth_user.id == auth.user_id

        db.comp_moduleset_modules.modset_id.requires = IS_IN_DB(db(q),
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
    l = []
    for id in ids:
        i = id.split('_')[1]
        if i == "None":
            continue
        l.append(i)
    ids =l
    q = db.comp_moduleset_modules.id.belongs(ids)
    if "Manager" not in user_groups():
        q = db.comp_moduleset_modules.id.belongs(ids)
        q &= db.comp_moduleset_modules.modset_id == db.comp_moduleset.id
        q &= db.comp_moduleset_team_responsible.modset_id == db.comp_moduleset.id
        q &= db.comp_moduleset_team_responsible.group_id == db.auth_group.id
        q &= db.auth_group.id == db.auth_membership.group_id
        q &= db.auth_user.id == db.auth_membership.user_id
        q &= db.auth_user.id == auth.user_id
        rows = db(q).select(db.comp_moduleset_modules.id)
        ids = map(lambda x: x.id, rows)
        q = db.comp_moduleset_modules.id.belongs(ids)

    rows = db(q).select(db.comp_moduleset_modules.modset_mod_name)

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
    if len(db(db.comp_moduleset.modset_name==new).select()) > 0:
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
        _log('compliance.moduleset.module.add',
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
        _log('compliance.moduleset.module.change',
             'change module name from %(on)s to %(d)s in moduleset %(x)s',
             dict(on=oldn, x=modset_name, d=new))

def modset_team_responsible_attach(ids=[]):
    if len(ids) == 0:
        raise ToolError("no moduleset selected")
    ids = map(lambda x: x.split('_')[0], ids)
    group_id = request.vars.team_responsible_attach_s

    done = []
    for id in ids:
        if 'Manager' not in user_groups():
            q = db.comp_moduleset_team_responsible.modset_id == id
            q &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
            if db(q).count() == 0:
                continue
        q = db.comp_moduleset_team_responsible.modset_id == id
        q &= db.comp_moduleset_team_responsible.group_id == group_id
        if db(q).count() != 0:
            continue
        done.append(id)
        db.comp_moduleset_team_responsible.insert(modset_id=id, group_id=group_id)
    if len(done) == 0:
        return
    rows = db(db.comp_moduleset.id.belongs(done)).select(db.comp_moduleset.modset_name)
    u = ', '.join([r.modset_name for r in rows])
    _log('moduleset.group.attach',
         'attached group %(g)s to modulesets %(u)s',
         dict(g=group_role(group_id), u=u))

@auth.requires_membership('CompManager')
def modset_team_responsible_detach(ids=[]):
    if len(ids) == 0:
        raise ToolError("no moduleset selected")
    ids = map(lambda x: x.split('_')[0], ids)
    group_id = request.vars.team_responsible_detach_s

    done = []
    for id in ids:
        q = db.comp_moduleset_team_responsible.modset_id == id
        q &= db.comp_moduleset_team_responsible.group_id == group_id
        if 'Manager' not in user_groups():
            q &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
        if db(q).count() == 0:
            continue
        done.append(id)
        db(q).delete()
    if len(done) == 0:
        return
    rows = db(db.comp_moduleset.id.belongs(done)).select(db.comp_moduleset.modset_name)
    u = ', '.join([r.modset_name for r in rows])
    _log('modset.group.detach',
         'detached group %(g)s from modsets %(u)s',
         dict(g=group_role(group_id), u=u))

@auth.requires_login()
def ajax_comp_moduleset_col_values():
    t = table_comp_moduleset('ajax_comp_moduleset', 'ajax_comp_moduleset')
    col = request.args[0]
    o = db.comp_moduleset[col]

    q = db.comp_moduleset.id > 0
    j = db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    l1 = db.comp_moduleset_team_responsible.on(j)
    j = db.comp_moduleset_modules.modset_id == db.comp_moduleset.id
    l2 = db.comp_moduleset_modules.on(j)
    j = db.comp_moduleset.id == db.v_comp_moduleset_teams_responsible.modset_id
    l3 = db.v_comp_moduleset_teams_responsible.on(j)
    if 'Manager' not in user_groups():
        q &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(db.comp_moduleset_modules.ALL,
                                 db.comp_moduleset.modset_name,
                                 db.comp_moduleset.id,
                                 db.v_comp_moduleset_teams_responsible.teams_responsible,
                                 orderby=o,
                                 groupby=o,
                                 left=(l1,l2,l3)
                                 )
    return t.col_values_cloud(col)

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
            elif action == 'team_responsible_attach':
                modset_team_responsible_attach(t.get_checked())
            elif action == 'team_responsible_detach':
                modset_team_responsible_detach(t.get_checked())
        except ToolError, e:
            t.flash = str(e)

    try:
        if t.form_moduleset_add.accepts(request.vars, formname='add_moduleset'):
            add_modset_default_team_responsible(request.vars.modset_name)
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
    except AttributeError:
        pass

    o = db.comp_moduleset.modset_name
    g = db.comp_moduleset.modset_name|db.comp_moduleset_modules.id
    q = db.comp_moduleset.id > 0
    j = db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    l1 = db.comp_moduleset_team_responsible.on(j)
    j = db.comp_moduleset_modules.modset_id == db.comp_moduleset.id
    l2 = db.comp_moduleset_modules.on(j)
    j = db.comp_moduleset.id == db.v_comp_moduleset_teams_responsible.modset_id
    l3 = db.v_comp_moduleset_teams_responsible.on(j)
    if 'Manager' not in user_groups():
        q &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    rows = db(q).select(db.comp_moduleset_modules.id, left=(l1,l2,l3), groupby=g)
    t.setup_pager(len(rows))
    t.object_list = db(q).select(db.comp_moduleset_modules.ALL,
                                 db.comp_moduleset.modset_name,
                                 db.comp_moduleset.id,
                                 db.v_comp_moduleset_teams_responsible.teams_responsible,
                                 orderby=o,
                                 groupby=g,
                                 left=(l1,l2,l3),
                                 limitby=(t.pager_start,t.pager_end))

    return t.html()

def add_modset_default_team_responsible(modset_name):
    q = db.comp_moduleset.modset_name == modset_name
    modset_id = db(q).select()[0].id
    q = db.auth_membership.user_id == auth.user_id
    q &= db.auth_membership.group_id == db.auth_group.id
    q &= db.auth_group.role.like('user_%')
    try:
        group_id = db(q).select()[0].auth_group.id
    except:
        q = db.auth_group.role == 'Manager'
        group_id = db(q).select()[0].id
    db.comp_moduleset_team_responsible.insert(modset_id=modset_id, group_id=group_id)

class table_comp_moduleset_short(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['modset_name']
        self.colprops = {
            'modset_name': HtmlTableColumn(
                     title='Moduleset',
                     table='comp_moduleset',
                     field='modset_name',
                     display=True,
                     img='action16',
                    ),
        }
        self.checkboxes = True
        self.dbfilterable = False
        self.exportable = False
        self.columnable = False
        self.checkbox_id_table = 'comp_moduleset'

class table_comp_modulesets_nodes(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['nodename', 'modulesets'] + v_nodes_cols
        self.colprops = v_nodes_colprops
        self.colprops['modulesets'] = HtmlTableColumn(
                     title='Module set',
                     table='comp_moduleset',
                     field='modulesets',
                     img='comp16',
                     display=True,
                    )
        self.colprops['nodename'].t = self
        self.colprops['nodename'].display = True
        self.checkboxes = True
        self.dbfilterable = False
        self += HtmlTableMenu('Moduleset', 'action16', ['moduleset_attach', 'moduleset_detach'], id='menu_moduleset2')
        self.ajax_col_values = 'ajax_comp_modulesets_nodes_col_values'

    def moduleset_detach(self):
        d = DIV(
              A(
                T("Detach"),
                _class='detach16',
                _onclick=self.ajax_submit(args=['detach_moduleset'],
                                          additional_inputs=self.modulesets.ajax_inputs()),
              ),
            )
        return d

    def moduleset_attach(self):
        d = DIV(
              A(
                T("Attach"),
                _class='attach16',
                _onclick=self.ajax_submit(args=['attach_moduleset'],
                                          additional_inputs=self.modulesets.ajax_inputs()),
              ),
            )
        return d

@auth.requires_membership('CompManager')
def comp_detach_modulesets(node_ids=[], modset_ids=[]):
    if len(node_ids) == 0:
        raise ToolError("detach modulesets failed: no node selected")
    if len(modset_ids) == 0:
        raise ToolError("detach modulesets failed: no moduleset selected")

    q = db.v_nodes.id.belongs(node_ids)
    rows = db(q).select(db.v_nodes.nodename)
    node_names = [r.nodename for r in rows]
    nodes = ', '.join(node_names)

    for msid in modset_ids:
        for node in node_names:
            q = db.comp_node_moduleset.modset_node == node
            q &= db.comp_node_moduleset.modset_id == msid
            db(q).delete()
    for node in node_names:
        update_dash_moddiff_node(node)

    q = db.comp_moduleset.id.belongs(modset_ids)
    rows = db(q).select(db.comp_moduleset.modset_name)
    modulesets = ', '.join([r.modset_name for r in rows])
    _log('compliance.moduleset.node.detach',
         'detached modulesets %(modulesets)s from nodes %(nodes)s',
         dict(modulesets=modulesets, nodes=nodes))

@auth.requires_membership('CompManager')
def comp_attach_modulesets(node_ids=[], modset_ids=[], node_names=[]):
    if len(node_ids+node_names) == 0:
        raise ToolError("attach modulesets failed: no node selected")
    if len(modset_ids) == 0:
        raise ToolError("attach modulesets failed: no moduleset selected")

    if len(nodes_id) > 0:
        q = db.v_nodes.id.belongs(node_ids)
        rows = db(q).select(db.v_nodes.nodename)
        node_names += [r.nodename for r in rows]

    nodes = ', '.join(node_names)

    for msid in modset_ids:
        for node in node_names:
            q = db.comp_node_moduleset.modset_node == node
            q &= db.comp_node_moduleset.modset_id == msid
            if db(q).count() == 0:
                db.comp_node_moduleset.insert(modset_node=node,
                                            modset_id=msid)
    for node in node_names:
        update_dash_moddiff_node(node)

    q = db.comp_moduleset.id.belongs(modset_ids)
    rows = db(q).select(db.comp_moduleset.modset_name)
    modulesets = ', '.join([r.modset_name for r in rows])
    _log('compliance.moduleset.node.attach',
         'attached modulesets %(modulesets)s to nodes %(nodes)s',
         dict(modulesets=modulesets, nodes=nodes))


@auth.requires_login()
def ajax_comp_modulesets_nodes_col_values():
    r = table_comp_moduleset_short('cmn1', 'ajax_comp_modulesets_nodes',
                                  innerhtml='cmn1')
    t = table_comp_modulesets_nodes('cmn2', 'ajax_comp_modulesets_nodes',
                                  innerhtml='cmn1')
    t.modulesets = r
    col = request.args[0]
    if col in t.cols:
        o = db.v_comp_nodes[col]
        q = _where(None, 'v_comp_nodes', domain_perms(), 'nodename')
        if 'Manager' not in user_groups():
            q &= db.v_comp_nodes.team_responsible.belongs(user_groups())
        for f in t.cols:
            q = _where(q, 'v_comp_nodes', t.filter_parse_glob(f), f)
        q = apply_gen_filters(q, r.tables())
        t.object_list = db(q).select(o, orderby=o, groupby=o)
        return t.col_values_cloud(col)
    else:
        o = db.comp_moduleset[col]
        q = db.comp_moduleset.id > 0
        if 'Manager' not in user_groups():
            q &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
        for f in r.cols:
            q = _where(q, 'comp_moduleset', r.filter_parse_glob(f), f)
        r.object_list = db(q).select(o, orderby=o, groupby=o)
        return r.col_values_cloud(col)

@auth.requires_login()
def ajax_comp_modulesets_nodes():
    r = table_comp_moduleset_short('cmn1', 'ajax_comp_modulesets_nodes',
                                  innerhtml='cmn1')
    t = table_comp_modulesets_nodes('cmn2', 'ajax_comp_modulesets_nodes',
                                  innerhtml='cmn1')
    t.modulesets = r
    t.checkbox_names.append(r.id+'_ck')

    if len(request.args) == 1 and request.args[0] == 'attach_moduleset':
        comp_attach_modulesets(t.get_checked(), r.get_checked())
    elif len(request.args) == 1 and request.args[0] == 'detach_moduleset':
        comp_detach_modulesets(t.get_checked(), r.get_checked())

    o = db.comp_moduleset.modset_name
    j = db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    l = db.comp_moduleset_team_responsible.on(j)
    q = db.comp_moduleset.id > 0
    if 'Manager' not in user_groups():
        q &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    for f in r.cols:
        q = _where(q, 'comp_moduleset', r.filter_parse_glob(f), f)

    n = db(q).count()
    r.setup_pager(n)
    r.object_list = db(q).select(limitby=(r.pager_start,r.pager_end), orderby=o, groupby=o, left=l)

    r_html = r.html()

    o = db.v_comp_nodes.nodename
    q = _where(None, 'v_comp_nodes', domain_perms(), 'nodename')
    if 'Manager' not in user_groups():
        q &= db.v_comp_nodes.team_responsible.belongs(user_groups())
    for f in t.cols:
        q = _where(q, 'v_comp_nodes', t.filter_parse_glob(f), f)
    q = apply_gen_filters(q, r.tables())

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
             DIV(XML('&nbsp;'), _class='spacer'),
           )

@auth.requires_login()
def comp_modules():
    t = DIV(
          DIV(
            ajax_comp_moduleset(),
            _id='ajax_comp_moduleset',
          ),
        )
    return dict(table=t)

@auth.requires_login()
def comp_modulesets_nodes():
    t = DIV(
          DIV(
            ajax_comp_modulesets_nodes(),
            _id='cmn1',
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
        self.cols = ['mod_name', 'total', 'ok', 'nok', 'na', 'obs', 'pct',
                     'mod_log']
        self.colprops = {
            'mod_name': HtmlTableColumn(
                     title='Module',
                     field='mod_name',
                     table='comp_mod_status',
                     display=True,
                     img='check16',
                    ),
            'total': HtmlTableColumn(
                     title='Total',
                     field='total',
                     table='comp_mod_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'ok': HtmlTableColumn(
                     title='Ok',
                     field='ok',
                     table='comp_mod_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'nok': HtmlTableColumn(
                     title='Not Ok',
                     field='nok',
                     table='comp_mod_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'na': HtmlTableColumn(
                     title='N/A',
                     field='na',
                     table='comp_mod_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'obs': HtmlTableColumn(
                     title='Obsolete',
                     field='obs',
                     table='comp_mod_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'pct': col_mod_percent(
                     title='Percent',
                     field='pct',
                     table='comp_mod_status',
                     display=True,
                     img='check16',
                     _class='comp_pct',
                    ),
            'mod_log': col_comp_mod_status(
                     title='History',
                     field='mod_log',
                     display=True,
                     img='log16',
                     _class='comp_plot',
                    ),
        }
        for i in self.cols:
            self.colprops[i].t = self

        self.extraline = True

    def extra_line_key(self, o):
        return self.id+'_'+self.colprops['mod_name'].get(o).replace('.','_')


class table_comp_svc_status(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['svc_name', 'total', 'ok', 'nok', 'na', 'obs', 'pct',
                     "svc_log"]
        self.colprops = {
            'svc_name': col_svc(
                     title='Service',
                     field='svc_name',
                     table='comp_svc_status',
                     display=True,
                     img='node16',
                    ),
            'total': HtmlTableColumn(
                     title='Total',
                     field='total',
                     table='comp_svc_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'ok': HtmlTableColumn(
                     title='Ok',
                     field='ok',
                     table='comp_svc_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'nok': HtmlTableColumn(
                     title='Not Ok',
                     field='nok',
                     table='comp_svc_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'na': HtmlTableColumn(
                     title='N/A',
                     field='na',
                     table='comp_svc_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'obs': HtmlTableColumn(
                     title='Obsolete',
                     field='obs',
                     table='comp_svc_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'pct': col_mod_percent(
                     title='Percent',
                     field='pct',
                     table='comp_svc_status',
                     display=True,
                     img='check16',
                     _class='comp_pct',
                    ),
            'svc_log': col_comp_svc_status(
                     title='History',
                     field='svc_log',
                     display=True,
                     img='log16',
                     _class='comp_plot',
                    ),
        }
        for i in self.cols:
            self.colprops[i].t = self

        self.extraline = True

    def extra_line_key(self, o):
        return self.id+'_'+self.colprops['svc_name'].get(o).replace('.','_')


class table_comp_node_status(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['node_name', 'total', 'ok', 'nok', 'na', 'obs', 'pct',
                     "node_log"]
        self.colprops = {
            'node_name': col_node(
                     title='Node',
                     field='node_name',
                     table='comp_node_status',
                     display=True,
                     img='node16',
                    ),
            'total': HtmlTableColumn(
                     title='Total',
                     field='total',
                     table='comp_node_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'ok': HtmlTableColumn(
                     title='Ok',
                     field='ok',
                     table='comp_node_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'nok': HtmlTableColumn(
                     title='Not Ok',
                     field='nok',
                     table='comp_node_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'na': HtmlTableColumn(
                     title='N/A',
                     field='na',
                     table='comp_node_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'obs': HtmlTableColumn(
                     title='Obsolete',
                     field='obs',
                     table='comp_node_status',
                     display=True,
                     img='check16',
                     _class='numeric',
                    ),
            'pct': col_mod_percent(
                     title='Percent',
                     field='pct',
                     table='comp_node_status',
                     display=True,
                     img='check16',
                     _class='comp_pct',
                    ),
            'node_log': col_comp_node_status(
                     title='History',
                     field='node_log',
                     display=True,
                     img='log16',
                     _class='comp_plot',
                    ),
        }
        for i in self.cols:
            self.colprops[i].t = self

        self.extraline = True

    def extra_line_key(self, o):
        return self.id+'_'+self.colprops['node_name'].get(o).replace('.','_')

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

def spark_id(nodename, module):
    module = module.replace('.', '_')
    module = module.replace('-', '_')
    return 'rh_%s_%s'%(nodename, module)

def spark_url(nodename, module):
    return URL(r=request,
               f='call/json/json_run_status_log/%(node)s/%(module)s'%dict(
                 node=nodename,
                 module=module)
           )

class col_run_status_log(HtmlTableColumn):
    def html(self, o):
        if hasattr(o, 'comp_status'):
            nodename = o.comp_status.run_nodename
            module = o.comp_status.run_module
        else:
            nodename = ""
            module = ""
        return DIV(
                 _id=spark_id(nodename, module)
               )

class col_run_date(HtmlTableColumn):
    deadline = now - datetime.timedelta(days=7)

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

class table_comp_status(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['run_date',
                     'run_nodename',
                     'run_svcname',
                     'run_module',
                     'run_status',
                     'run_status_log',
                     'run_ruleset',
                     'rset_md5',
                     'run_log']
        self.cols += v_nodes_cols
        self.colprops = {
            'run_date': col_run_date(
                     title='Run date',
                     field='run_date',
                     table='comp_status',
                     img='check16',
                     display=True,
                    ),
            'run_nodename': col_node(
                     title='Node',
                     field='run_nodename',
                     table='comp_status',
                     img='node16',
                     display=True,
                    ),
            'run_svcname': col_svc(
                     title='Service',
                     field='run_svcname',
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
            'rset_md5': col_rset_md5(
                     title='Ruleset md5',
                     field='rset_md5',
                     table='comp_status',
                     img='check16',
                     display=False,
                    ),
            'run_status': col_run_status(
                     title='Status',
                     field='run_status',
                     table='comp_status',
                     img='check16',
                     display=True,
                    ),
            'run_status_log': col_run_status_log(
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
                     display=False,
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
        for i in self.cols:
            self.colprops[i].t = self
        self.ajax_col_values = 'ajax_comp_status_col_values'
        self.extraline = True
        self.checkboxes = True
        self.checkbox_id_table = 'comp_status'
        if 'CompManager' in user_groups():
            self.additional_tools.append('check_del')
        if member_of(('Manager', 'CompExec')):
            self += HtmlTableMenu('Action', 'action16', ['tool_action_module'], id='menu_comp_action')

    def tool_action_module(self):
        cmd = [
          'check',
          'fixable',
          'fix',
        ]
        cl = "comp16"

        sid = 'action_s_module'
        s = []
        for c in cmd:
            confirm=T("""Are you sure you want to execute a %(a)s action on all selected objects. Please confirm action""",dict(a=c))
            s.append(TR(
                       TD(
                         IMG(
                           _src=URL(r=request,c='static',f=action_img_h[c]),
                         ),
                       ),
                       TD(
                         A(
                           c,
                           _onclick="""if (confirm("%(text)s")){%(s)s};"""%dict(
                             s=self.ajax_submit(additional_inputs=[sid], args=['do_action', c]),
                             text=confirm,
                           ),
                         ),
                       ),
                     ))

        actions = TABLE(
                      TR(
                        TH(
                          T("Action"),
                        ),
                        TD(
                          TABLE(*s),
                        ),
                      ),
                    )

        d = DIV(
              A(
                T("Run selected modules"),
                _class=cl,
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='tool_action_module'),
              ),
              DIV(
                actions,
                _style='display:none',
                _class='white_float',
                _name='tool_action_module',
                _id='tool_action_module',
              ),
            )

        return d


    def check_del(self):
        d = DIV(
              A(
                T("Delete check"),
                _class='del16',
                _onclick="""if (confirm("%(text)s")){%(s)s};"""%dict(
                   s=self.ajax_submit(args=['check_del']),
                   text=T("Please confirm deletion"),
                ),
              ),
              _class='floatw',
            )
        return d

@auth.requires_login()
def fix_module_on_node():
    nodename = request.args[0]
    module = request.args[1]
    ug = user_groups()
    q = db.comp_status.run_nodename == nodename
    q &= db.comp_status.run_module == module
    q &= db.comp_status.run_nodename == db.nodes.nodename
    q &= (db.nodes.team_responsible.belongs(ug)) | (db.nodes.team_integ.belongs(ug))
    row = db(q).select(db.comp_status.id).first()
    if row is None:
        return
    ids = [row.id]
    do_action(ids, 'fix')

@auth.requires_membership('CompExec')
def do_action(ids, action=None):
    if action is None or len(action) == 0:
        raise ToolError("no action specified")
    if len(ids) == 0:
        raise ToolError("no target to execute %s on"%action)

    def fmt_action(nodename, svcname, action, mod):
        if svcname is None or svcname == "":
            _cmd = ["/opt/opensvc/bin/nodemgr"]
        else:
            _cmd = ["/opt/opensvc/bin/svcmgr", "-s", svcname]
        cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                      '-o', 'ForwardX11=no',
                      '-o', 'PasswordAuthentication=no',
                      '-tt',
               'opensvc@'+nodename,
               '--',
               'sudo'] + _cmd + ['compliance', action,
               '--module', mod]
        return ' '.join(cmd)

    q = db.comp_status.id.belongs(ids)
    q &= db.comp_status.run_nodename == db.nodes.nodename
    q &= (db.nodes.team_responsible.belongs(user_groups())) | \
         (db.nodes.team_integ.belongs(user_groups()))
    rows = db(q).select(db.comp_status.run_nodename,
                        db.comp_status.run_svcname,
                        db.comp_status.run_module)

    vals = []
    vars = ['command']
    tolog_node = []
    tolog_svc = []
    for row in rows:
        if row.run_svcname is None or row.run_svcname == "":
            tolog_node.append([row.run_nodename,
                               row.run_module])
        else:
            tolog_svc.append([row.run_svcname,
                              row.run_module])
        vals.append([fmt_action(row.run_nodename,
                                row.run_svcname,
                                action,
                                row.run_module)])

    purge_action_queue()
    generic_insert('action_queue', vars, vals)
    from subprocess import Popen
    actiond = 'applications'+str(URL(r=request,c='actiond',f='actiond.py'))
    process = Popen(actiond)
    process.communicate()

    if len(tolog_node) > 0:
        tolog_node_s = ', '.join(map(lambda x: "%s:%s"%(x[0], x[1]), tolog_node))
        _log('node.action', 'run compliance %(a)s of %(s)s', dict(
              a=action,
              s=tolog_node_s))
    if len(tolog_svc) > 0:
        tolog_svc_s = ', '.join(map(lambda x: "%s:%s"%(x[0], x[1]), tolog_svc))
        _log('service.action', 'run compliance %(a)s of %(s)s', dict(
              a=action,
              s=tolog_svc_s))

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
    if t == 'name':
        new = new.strip()
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
        _log('compliance.ruleset.variable.add',
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
            _log('compliance.ruleset.variable.change',
                 'renamed variable %(on)s to %(d)s in ruleset %(x)s',
                 dict(on=oldn, x=iid, d=new))
        elif t == 'value':
            db(q).update(var_value=new,
                         var_author=user_name(),
                         var_updated=now)
            _log('compliance.ruleset.variable.change',
                 'change variable %(on)s value from %(ov)s to %(d)s in ruleset %(x)s',
                 dict(on=oldn, ov=oldv, x=iid, d=new))
        else:
            raise Exception()

@auth.requires_membership('CompManager')
def var_value_set_dict_dict(name, mainkey):
    d = {}
    f = {}
    idx = {}
    vid = int(name.split('_')[2])
    for i in [v for v in request.vars if name in v]:
        if request.vars[i] is None or len(request.vars[i]) == 0:
            continue
        s = i[len(name)+1:]
        index = s.split('_')[0]
        key = s[len(index)+1:]
        if key == mainkey and key not in idx:
            idx[index] = request.vars[i]
            continue
        if index not in d:
            d[index] = {}
        try:
            val = int(request.vars[i])
        except:
            val = request.vars[i]
        if key == 'members':
            val = val.split(',')
            val = map(lambda x: x.strip(), val)
        d[index][key] = val
    for i in d:
        if i in idx:
            f[idx[i]] = d[i]
    db(db.comp_rulesets_variables.id==vid).update(var_value=json.dumps(f))

@auth.requires_membership('CompManager')
def var_value_set_cron(name):
    d = {}
    vid = int(name.split('_')[2])
    l = []
    for i in ('action', 'user', 'sched', 'command', 'file'):
        id = '_'.join((name, i))
        if id in request.vars:
            l.append(request.vars[id])
        else:
            l.append("")
    val = ':'.join(l)
    db(db.comp_rulesets_variables.id==vid).update(var_value=val)

@auth.requires_membership('CompManager')
def var_value_set_list_of_dict(name):
    d = {}
    vid = int(name.split('_')[2])
    for i in [v for v in request.vars if name in v]:
        if request.vars[i] is None or len(request.vars[i]) == 0:
            continue
        s = i[len(name)+1:]
        index = s.split('_')[0]
        key = s[len(index)+1:]
        if index not in d:
            d[index] = {}
        if key in ('level', 'seq'):
            val = request.vars[i]
        else:
            try:
                val = int(request.vars[i])
            except:
                val = request.vars[i].strip()
        if key == 'members':
            val = val.split(',')
            val = map(lambda x: x.strip(), val)
        elif key == 'vg':
            val = val.split(',')
            val = map(lambda x: x.strip(), val)
        d[index][key] = val
    db(db.comp_rulesets_variables.id==vid).update(var_value=json.dumps(d.values()))

@auth.requires_membership('CompManager')
def var_value_set_dict(name):
    d = {}
    vid = int(name.split('_')[2])
    for i in [v for v in request.vars if name in v]:
        if request.vars[i] is not None and len(request.vars[i])>0:
            key = i[len(name)+1:]
            try:
                val = int(request.vars[i])
            except:
                val = request.vars[i]
            d[key] = val
    db(db.comp_rulesets_variables.id==vid).update(var_value=json.dumps(d))

@auth.requires_membership('CompManager')
def var_value_set_list(name):
    l = []
    vid = int(name.split('_')[2])
    for i in [v for v in request.vars if name in v]:
        if request.vars[i] is not None and len(request.vars[i])>0:
            l.append(request.vars[i])
    db(db.comp_rulesets_variables.id==vid).update(var_value=json.dumps(l))

@auth.requires_membership('CompManager')
def check_del(ids):
    q = db.comp_status.id.belongs(ids)
    groups = user_groups()
    if 'Manager' not in groups:
        # Manager+CompManager can delete any check
        # CompManager can delete the nodes they are responsible of
        q &= db.comp_status.run_nodename.belongs([r.nodename for r in db(db.nodes.team_responsible.belongs(groups)).select(db.nodes.nodename)])
    rows = db(q).select()
    u = ', '.join([r.run_module+'@'+r.run_nodename for r in rows])

    db(q).delete()
    for node in [r.run_nodename for r in rows]:
        update_dash_compdiff(node)
    _log('compliance.status.delete',
         'deleted module status %(u)s',
         dict(u=u))

@auth.requires_login()
def ajax_comp_log_col_values():
    t = table_comp_log('ajax_comp_log', 'ajax_comp_log')
    col = request.args[0]
    o = db.comp_log[col]
    q = _where(None, 'comp_log', domain_perms(), 'run_nodename')
    q &= db.comp_log.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.comp_log.run_nodename)
    t.object_list = db(q).select(o, orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_comp_status_col_values():
    t = table_comp_status('cs0', 'ajax_comp_status')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    q &= db.comp_status.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.comp_status.run_nodename)
    t.object_list = db(q).select(o, orderby=o, groupby=o)
    return t.col_values_cloud(col)

@auth.requires_login()
def ajax_comp_status():
    t = table_comp_status('cs0', 'ajax_comp_status')

    if len(request.args) >= 1:
        action = request.args[0]
        try:
            if action == 'check_del':
                check_del(t.get_checked())
            elif action == 'do_action' and len(request.args) == 2:
                saction = request.args[1]
                do_action(t.get_checked(), saction)
        except ToolError, e:
            t.flash = str(e)

    o = ~db.comp_status.run_nodename
    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    q &= db.comp_status.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.comp_status.run_nodename)

    n = len(db(q).select(db.comp_status.id, limitby=default_limitby))
    t.setup_pager(n)
    #all = db(q).select(db.comp_status.ALL, db.v_nodes.id)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    t.csv_q = q
    t.csv_orderby = o

    def chart(a, b, c, d):
        total = a + b + c + d
        if total == 0:
            pa = 0
            pb = 0
            pc = 0
        else:
            pa = "%d%%"%int(a*100/total)
            pb = "%d%%"%int(b*100/total)
            pc = "%d%%"%int(c*100/total)

        d = DIV(
              DIV(
                DIV(
                  _style="""font-size: 0px;
                            line-height: 0px;
                            height: 8px;
                            float: left;
                            min-width: 0%%;
                            max-width: %(p)s;
                            width: %(p)s;
                            background: #15367A;
                         """%dict(p=pa),
                ),
                DIV(
                  _style="""font-size: 0px;
                            line-height: 0px;
                            height: 8px;
                            float: left;
                            min-width: 0%%;
                            max-width: %(p)s;
                            width: %(p)s;
                            background: #3aaa50;
                         """%dict(p=pb),
                ),
                DIV(
                  _style="""font-size: 0px;
                            line-height: 0px;
                            height: 8px;
                            float: left;
                            min-width: 0%%;
                            max-width: %(p)s;
                            width: %(p)s;
                            background: #dcdcdc;
                         """%dict(p=pc),
                ),
                _style="""text-align: left;
                          margin: 2px auto;
                          background: #FF7863;
                          overflow: hidden;
                       """,
              ),
              DIV(
                SPAN(a, " ", T("obsolete"), _style="color:#15367A;padding:3px"),
                SPAN(b, " ", T("ok"), _style="color:#3aaa50;padding:3px"),
                SPAN(c, " ", T("n/a"), _style="color:#acacac;padding:3px"),
                SPAN(d, " ", T("not ok"), _style="color:#FF7863;padding:3px"),
              ),
              _style="""margin: auto;
                        text-align: center;
                        width: 100%;
                     """,
            ),
        return d

    q_obs = q & (db.comp_status.run_date < now - datetime.timedelta(days=7))
    q_nok = q & (db.comp_status.run_date > now - datetime.timedelta(days=7)) & (db.comp_status.run_status == 1)
    q_na = q & (db.comp_status.run_date > now - datetime.timedelta(days=7)) & (db.comp_status.run_status == 2)
    q_ok = q & (db.comp_status.run_date > now - datetime.timedelta(days=7)) & (db.comp_status.run_status == 0)

    obs = db(q_obs).count()
    nok = db(q_nok).count()
    na = db(q_na).count()
    ok = db(q_ok).count()

    mt = table_comp_mod_status('cms', 'ajax_comp_mod_status')
    nt = table_comp_node_status('cns', 'ajax_comp_node_status')
    st = table_comp_svc_status('css', 'ajax_comp_svc_status')

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.cols.remove("run_log")
        return t.csv()

    spark_cmds = ""
    for r in t.object_list:
        spark_cmds += "sparkl('%(url)s', '%(id)s');"%dict(
          url=spark_url(r.comp_status.run_nodename, r.comp_status.run_module),
          id=spark_id(r.comp_status.run_nodename, r.comp_status.run_module),
        )
    return DIV(
             SCRIPT(
               "$(document).ready(function(){%s});"%spark_cmds,
               'if ($("#cms").is(":visible")) {',
               mt.ajax_submit(additional_inputs=t.ajax_inputs()),
               "}",
               'if ($("#cns").is(":visible")) {',
               nt.ajax_submit(additional_inputs=t.ajax_inputs()),
               "}",
               'if ($("#css").is(":visible")) {',
               st.ajax_submit(additional_inputs=t.ajax_inputs()),
               "}",
               _name=t.id+"_to_eval"
             ),
             DIV(chart(obs, ok, na, nok), _style="padding:4px"),
             DIV(
               T("Modules aggregation"),
               _style="text-align:left;font-size:120%;background-color:#e0e1cd",
               _class="right16 clickable",
               _onclick="""
               if (!$("#cms").is(":visible")) {
                 $(this).addClass("down16");
                 $(this).removeClass("right16");
                 $("#cms").show(); %s;
               } else {
                 $(this).addClass("right16");
                 $(this).removeClass("down16");
                 $("#cms").hide();
               }"""%mt.ajax_submit(additional_inputs=t.ajax_inputs())
             ),
             DIV(IMG(_src=URL(r=request,c='static',f='spinner.gif')), _id="cms", _style="display:none"),
             DIV(
               T("Nodes aggregation"),
               _style="text-align:left;font-size:120%;background-color:#e0e1cd",
               _class="right16 clickable",
               _onclick="""
               if (!$("#cns").is(":visible")) {
                 $(this).addClass("down16");
                 $(this).removeClass("right16");
                 $("#cns").show(); %s;
               } else {
                 $(this).addClass("right16");
                 $(this).removeClass("down16");
                 $("#cns").hide();
               }"""%nt.ajax_submit(additional_inputs=t.ajax_inputs())
             ),
             DIV(IMG(_src=URL(r=request,c='static',f='spinner.gif')), _id="cns", _style="display:none"),
             DIV(
               T("Services aggregation"),
               _style="text-align:left;font-size:120%;background-color:#e0e1cd",
               _class="right16 clickable",
               _onclick="""
               if (!$("#css").is(":visible")) {
                 $(this).addClass("down16");
                 $(this).removeClass("right16");
                 $("#css").show(); %s;
               } else {
                 $(this).addClass("right16");
                 $(this).removeClass("down16");
                 $("#css").hide();
               }"""%st.ajax_submit(additional_inputs=t.ajax_inputs())
             ),
             DIV(IMG(_src=URL(r=request,c='static',f='spinner.gif')), _id="css", _style="display:none"),
             t.html(),
           )

@auth.requires_login()
def ajax_comp_svc_status():
    t = table_comp_status('cs0', 'ajax_comp_status')
    mt = table_comp_svc_status('css', 'ajax_comp_svc_status')

    o = ~db.comp_status.run_svcname
    q = _where(None, 'comp_status', domain_perms(), 'run_svcname')
    #q &= db.comp_status.run_svcname == db.v_svcmon.mon_svcname
    q &= (db.comp_status.run_svcname != None) & (db.comp_status.run_svcname != "")
    #for f in t.cols:
    #    q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.comp_status.run_nodename)
    sql1 = db(q)._select().rstrip(';').replace('v_svcmon.id, ','').replace('comp_status.id>0 AND', '')
    regex = re.compile("SELECT .* FROM")
    sql1 = regex.sub('', sql1)

    q = db.comp_svc_status.id > 0
    for f in mt.cols:
        q = _where(q, mt.colprops[f].table, mt.filter_parse(f), f)
    where = str(q).replace("comp_svc_status.", "u.")

    mt.setup_pager(-1)
    mt.dbfilterable = False
    mt.filterable = True
    mt.additional_inputs = t.ajax_inputs()

    sql2 = """select * from (
                select t.id,
                     t.run_svcname as svc_name,
                     t.ok+t.nok+t.na+t.obs as total,
                     t.ok,
                     t.nok,
                     t.na,
                     t.obs,
                     floor((t.ok+t.na)*100/(t.ok+t.nok+t.na+t.obs)) as pct
                from (select comp_status.id,
                           run_svcname,
                           sum(if(run_date>="%(d)s" and run_status=0, 1, 0)) as ok,
                           sum(if(run_date>="%(d)s" and run_status=1, 1, 0)) as nok,
                           sum(if(run_date>="%(d)s" and run_status=2, 1, 0)) as na,
                           sum(if(run_date<"%(d)s", 1, 0)) as obs
                    from %(sql)s group by run_svcname) t) u
              where %(where)s
              order by pct, total desc, svc_name
              limit %(limit)d
              offset %(offset)d"""%dict(
                sql=sql1,
                where=where,
                d=(now-datetime.timedelta(days=7)),
                limit=mt.perpage,
                offset=mt.pager_start,
           )

    rows = db.executesql(sql2)

    mt.object_list = map(lambda x: {'svc_name': x[1],
                                    'total':x[2],
                                    'ok':x[3],
                                    'nok': x[4],
                                    'na': x[5],
                                    'obs': x[6],
                                    'pct':x[7]},
                          rows)

    if len(request.args) == 1 and request.args[0] == 'csv':
        return mt.csv()

    return DIV(
             mt.html(),
           )

@auth.requires_login()
def ajax_comp_node_status():
    t = table_comp_status('cs0', 'ajax_comp_status')
    mt = table_comp_node_status('cns', 'ajax_comp_node_status')

    o = ~db.comp_status.run_nodename
    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    q &= db.comp_status.run_nodename == db.v_nodes.nodename
    q &= (db.comp_status.run_svcname == None) | (db.comp_status.run_svcname == "")
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.comp_status.run_nodename)
    sql1 = db(q)._select().rstrip(';').replace('v_nodes.id, ','').replace('comp_status.id>0 AND', '')
    regex = re.compile("SELECT .* FROM")
    sql1 = regex.sub('', sql1)

    q = db.comp_node_status.id > 0
    for f in mt.cols:
        q = _where(q, mt.colprops[f].table, mt.filter_parse(f), f)
    where = str(q).replace("comp_node_status.", "u.")

    mt.setup_pager(-1)
    mt.dbfilterable = False
    mt.filterable = True
    mt.additional_inputs = t.ajax_inputs()

    sql2 = """select * from (
                select t.id,
                     t.run_nodename as node_name,
                     t.ok+t.nok+t.na+t.obs as total,
                     t.ok,
                     t.nok,
                     t.na,
                     t.obs,
                     floor((t.ok+t.na)*100/(t.ok+t.nok+t.na+t.obs)) as pct
                from (select comp_status.id,
                           run_nodename,
                           sum(if(run_date>="%(d)s" and run_status=0, 1, 0)) as ok,
                           sum(if(run_date>="%(d)s" and run_status=1, 1, 0)) as nok,
                           sum(if(run_date>="%(d)s" and run_status=2, 1, 0)) as na,
                           sum(if(run_date<"%(d)s", 1, 0)) as obs
                    from %(sql)s group by run_nodename) t) u
              where %(where)s
              order by pct, total desc, node_name
              limit %(limit)d
              offset %(offset)d"""%dict(
                sql=sql1,
                where=where,
                d=(now-datetime.timedelta(days=7)),
                limit=mt.perpage,
                offset=mt.pager_start,
           )

    rows = db.executesql(sql2)

    mt.object_list = map(lambda x: {'node_name': x[1],
                                    'total':x[2],
                                    'ok':x[3],
                                    'nok': x[4],
                                    'na': x[5],
                                    'obs': x[6],
                                    'pct':x[7]},
                          rows)

    if len(request.args) == 1 and request.args[0] == 'csv':
        return mt.csv()

    return DIV(
             mt.html(),
           )

@auth.requires_login()
def ajax_svc_history():
    id = request.vars.rowid
    id_chart = id+'_chart'
    d = DIV(
          DIV(
            DIV(_id=id_chart),
          ),
          SCRIPT(
            "comp_history('%(url)s', '%(id)s');"%dict(
               url=URL(r=request, f='call/json/json_svc_history', vars={'svcname': request.vars.svcname}),
               id=id_chart,
            ),
            _name=id+'_to_eval'
          ),
        )
    return d

@service.json
def json_svc_history():
    sql = """select
               t.run_date,
               t.week,
               sum(t.ok) as ok,
               sum(t.nok) as nok,
               sum(t.na) as na
              from
              (
                select week(run_date) as week,
                    if(run_status=0, 1, 0) as ok,
                    if(run_status=1, 1, 0) as nok,
                    if(run_status=2, 1, 0) as na,
                    run_date
                from comp_log
                where run_svcname="%(svcname)s" and
                    run_date>date_sub(now(), interval 1 year)
                group by week(run_date), run_module, run_nodename
              ) t
              group by t.week
              order by t.week
             """%dict(svcname=request.vars.svcname)
    ok = []
    nok = []
    na = []
    for r in db.executesql(sql):
        ok.append((r[0], int(r[2])))
        nok.append((r[0], int(r[3])))
        na.append((r[0], int(r[4])))
    return [ok, nok, na]


@auth.requires_login()
def ajax_mod_history():
    id = request.vars.rowid
    id_chart = id+'_chart'
    d = DIV(
          DIV(
            DIV(_id=id_chart),
          ),
          SCRIPT(
            "comp_history('%(url)s', '%(id)s');"%dict(
               url=URL(r=request, f='call/json/json_mod_history', vars={'modname': request.vars.modname}),
               id=id_chart,
            ),
            _name=id+'_to_eval'
          ),
        )
    return d

@service.json
def json_mod_history():
    sql = """select
               t.run_date,
               t.week,
               sum(t.ok) as ok,
               sum(t.nok) as nok,
               sum(t.na) as na
              from
              (
                select week(run_date) as week,
                    if(run_status=0, 1, 0) as ok,
                    if(run_status=1, 1, 0) as nok,
                    if(run_status=2, 1, 0) as na,
                    run_date
                from comp_log
                where run_module="%(mod)s" and
                    run_date>date_sub(now(), interval 1 year)
                group by week(run_date), run_nodename, run_svcname
              ) t
              group by t.week
              order by t.week
             """%dict(mod=request.vars.modname)
    ok = []
    nok = []
    na = []
    for r in db.executesql(sql):
        ok.append((r[0], int(r[2])))
        nok.append((r[0], int(r[3])))
        na.append((r[0], int(r[4])))
    return [ok, nok, na]

@auth.requires_login()
def ajax_node_history():
    id = request.vars.rowid
    id_chart = id+'_chart'
    d = DIV(
          DIV(
            DIV(_id=id_chart),
          ),
          SCRIPT(
            "comp_history('%(url)s', '%(id)s');"%dict(
               url=URL(r=request, f='call/json/json_node_history', vars={'nodename': request.vars.nodename}),
               id=id_chart,
            ),
            _name=id+'_to_eval'
          ),
        )
    return d

@service.json
def json_node_history():
    sql = """select
               t.run_date,
               t.week,
               sum(t.ok) as ok,
               sum(t.nok) as nok,
               sum(t.na) as na
              from
              (
                select week(run_date) as week,
                    if(run_status=0, 1, 0) as ok,
                    if(run_status=1, 1, 0) as nok,
                    if(run_status=2, 1, 0) as na,
                    run_date
                from comp_log
                where run_nodename="%(node)s" and
                    run_date>date_sub(now(), interval 1 year)
                group by week(run_date), run_module
              ) t
              group by t.week
              order by t.week
             """%dict(node=request.vars.nodename)
    ok = []
    nok = []
    na = []
    for r in db.executesql(sql):
        ok.append((r[0], int(r[2])))
        nok.append((r[0], int(r[3])))
        na.append((r[0], int(r[4])))
    return [ok, nok, na]

@auth.requires_login()
def ajax_comp_mod_status():
    t = table_comp_status('cs0', 'ajax_comp_status')
    mt = table_comp_mod_status('cms', 'ajax_comp_mod_status')

    o = ~db.comp_status.run_nodename
    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    q &= db.comp_status.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.comp_status.run_nodename)
    sql1 = db(q)._select().rstrip(';').replace('v_nodes.id, ','').replace('comp_status.id>0 AND', '')
    regex = re.compile("SELECT .* FROM")
    sql1 = regex.sub('', sql1)

    q = db.comp_mod_status.id > 0
    for f in mt.cols:
        q = _where(q, mt.colprops[f].table, mt.filter_parse(f), f)
    where = str(q).replace("comp_mod_status.", "u.")

    mt.setup_pager(-1)
    mt.dbfilterable = False
    mt.filterable = True
    mt.additional_inputs = t.ajax_inputs()

    sql2 = """select * from (
                select t.id,
                     t.run_module as mod_name,
                     t.ok+t.nok+t.na+t.obs as total,
                     t.ok,
                     t.nok,
                     t.na,
                     t.obs,
                     floor((t.ok+t.na)*100/(t.ok+t.nok+t.na+t.obs)) as pct
                from (select comp_status.id,
                           run_module,
                           sum(if(run_date>="%(d)s" and run_status=0, 1, 0)) as ok,
                           sum(if(run_date>="%(d)s" and run_status=1, 1, 0)) as nok,
                           sum(if(run_date>="%(d)s" and run_status=2, 1, 0)) as na,
                           sum(if(run_date<"%(d)s", 1, 0)) as obs
                    from %(sql)s group by run_module) t) u
              where %(where)s
              order by pct, total desc, mod_name
              limit %(limit)d
              offset %(offset)d"""%dict(
                sql=sql1,
                where=where,
                d=(now-datetime.timedelta(days=7)),
                limit=mt.perpage,
                offset=mt.pager_start,
           )

    rows = db.executesql(sql2)

    mt.object_list = map(lambda x: {'mod_name': x[1],
                                    'total':x[2],
                                    'ok':x[3],
                                    'nok': x[4],
                                    'na': x[5],
                                    'obs': x[6],
                                    'pct':x[7]},
                          rows)

    """
    for i, row in enumerate(mt.object_list):
        sql = "select week(run_date) as week,
                        sum(if(run_status=0, 1, 0)) as ok,
                        sum(if(run_status=1, 1, 0)) as nok,
                        sum(if(run_status=2, 1, 0)) as na
                 from comp_log
                 where run_module="%(module)s"
                 group by week(run_date),run_module
                 order by run_date desc
                 limit 20"%dict(module=row['mod_name'])
        week = []
        ok = []
        nok = []
        na = []
        for r in db.executesql(sql):
            week.append(int(r[0]))
            ok.append(int(r[1]))
            nok.append(int(r[2]))
            na.append(int(r[3]))
        mt.object_list[i]['mod_log'] = json.dumps([week, ok, nok, na])
    """

    if len(request.args) == 1 and request.args[0] == 'csv':
        return mt.csv()

    return DIV(
             mt.html(),
           )

@auth.requires_login()
def comp_status():
    t = DIV(
          DIV(
            ajax_comp_status(),
            _id='cs0',
          ),
        )
    return dict(table=t)

class table_comp_log(table_comp_status):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        table_comp_status.__init__(self, id, 'ajax_comp_log', innerhtml)
        self.cols = ['run_date',
                     'run_nodename',
                     'run_svcname',
                     'run_module',
                     'run_action',
                     'run_status',
                     'run_log',
                     'rset_md5',
                     'run_ruleset']
        self.cols += v_nodes_cols
        for c in self.colprops:
            self.colprops[c].t = self
            if 'run_' in c or c == 'rset_md5':
                self.colprops[c].table = 'comp_log'
        self.ajax_col_values = 'ajax_comp_log_col_values'
        self.checkboxes = False
        self.checkbox_id_table = 'comp_log'

@auth.requires_login()
def ajax_comp_log():
    t = table_comp_log('ajax_comp_log', 'ajax_comp_log')

    db.commit()
    if request.vars.ajax_comp_log_f_run_date is None or request.vars.ajax_comp_log_f_run_date == t.column_filter_reset:
        request.vars.ajax_comp_log_f_run_date = '>-1d'
    o = ~db.comp_log.id
    q = _where(None, 'comp_log', domain_perms(), 'run_nodename')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q &= db.comp_log.run_nodename == db.v_nodes.nodename
    q = apply_filters(q, db.comp_log.run_nodename)

    t.setup_pager(-1)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o)
    return t.html()


@auth.requires_login()
def comp_log():
    t = DIV(
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

def auth_uuid(fn):
    def new(*args):
        uuid, node = args['auth']
        rows = db(db.auth_node.nodename==node&db.auth_node.uuid==uuid).select()
        if len(rows) != 1:
            return
        return fn(*args)
    return new

@auth_uuid
@service.xmlrpc
def comp_get_moduleset_modules(moduleset, auth):
    return _comp_get_moduleset_modules(moduleset, auth[1])

def _comp_get_moduleset_modules(moduleset, node):
    if isinstance(moduleset, list):
        if len(moduleset) == 0:
            return []
        q = db.comp_moduleset.modset_name.belongs(moduleset)
    elif isinstance(moduleset, str):
        q = db.comp_moduleset.modset_name == moduleset
    else:
        return []
    q &= db.comp_moduleset_modules.modset_id == db.comp_moduleset.id
    q &= db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    q &= db.auth_group.id == db.comp_moduleset_team_responsible.group_id
    q &= db.nodes.team_responsible == db.auth_group.role
    q &= db.nodes.nodename == node
    rows = db(q).select(db.comp_moduleset_modules.modset_mod_name,
                        groupby=db.comp_moduleset_modules.modset_mod_name)
    return [r.modset_mod_name for r in rows]

def _comp_get_moduleset_svc_modules(moduleset, svcname):
    if isinstance(moduleset, list):
        if len(moduleset) == 0:
            return []
        q = db.comp_moduleset.modset_name.belongs(moduleset)
    elif isinstance(moduleset, str):
        q = db.comp_moduleset.modset_name == moduleset
    else:
        return []
    q &= db.comp_moduleset_modules.modset_id == db.comp_moduleset.id
    q &= db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    q &= db.auth_group.id == db.comp_moduleset_team_responsible.group_id
    q &= db.apps_responsibles.group_id == db.auth_group.id
    q &= db.apps_responsibles.app_id == db.apps.id
    q &= db.apps.app == db.services.svc_app
    q &= db.services.svc_name == svcname
    rows = db(q).select(db.comp_moduleset_modules.modset_mod_name,
                        groupby=db.comp_moduleset_modules.modset_mod_name)
    return [r.modset_mod_name for r in rows]

def comp_attached_ruleset_id(nodename):
    q = db.comp_rulesets_nodes.nodename == nodename
    rows = db(q).select(db.comp_rulesets_nodes.ruleset_id)
    return [r.ruleset_id for r in rows]

def comp_attached_svc_moduleset_id(svcname):
    q = db.comp_modulesets_services.modset_svcname == svcname
    rows = db(q).select(db.comp_modulesets_services.modset_id)
    return [r.modset_id for r in rows]

def comp_attached_moduleset_id(nodename):
    q = db.comp_node_moduleset.modset_node == nodename
    rows = db(q).select(db.comp_node_moduleset.modset_id)
    return [r.modset_id for r in rows]

def comp_ruleset_id(ruleset):
    q = db.comp_rulesets.ruleset_name == ruleset
    rows = db(q).select(db.comp_rulesets.id)
    if len(rows) == 0:
        return None
    return rows[0].id

def comp_moduleset_id(moduleset):
    q = db.comp_moduleset.modset_name == moduleset
    rows = db(q).select(db.comp_moduleset.id)
    if len(rows) == 0:
        return None
    return rows[0].id

def comp_moduleset_exists(moduleset):
    q = db.comp_moduleset.modset_name == moduleset
    rows = db(q).select(db.comp_moduleset.id)
    if len(rows) != 1:
        return None
    return rows[0].id

def comp_ruleset_svc_attached(svcname, rset_id, slave):
    q = db.comp_rulesets_services.svcname == svcname
    q &= db.comp_rulesets_services.ruleset_id == rset_id
    q &= db.comp_rulesets_services.slave == slave
    if len(db(q).select(db.comp_rulesets_services.id)) == 0:
        return False
    return True

def comp_moduleset_svc_attached(svcname, modset_id, slave):
    q = db.comp_modulesets_services.modset_svcname == svcname
    q &= db.comp_modulesets_services.modset_id == modset_id
    q &= db.comp_modulesets_services.slave == slave
    if len(db(q).select(db.comp_modulesets_services.id)) == 0:
        return False
    return True

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

def comp_slave(svcname, nodename):
    q = db.svcmon.mon_vmname == nodename
    q &= db.svcmon.mon_svcname == svcname
    row = db(q).select().first()
    if row is None:
        return False
    return True

def has_slave(svcname):
    q = db.svcmon.mon_svcname == svcname
    q &= db.svcmon.mon_vmname != None
    q &= db.svcmon.mon_vmname != ""
    row = db(q).select().first()
    if row is None:
        return False
    return True

@auth_uuid
@service.xmlrpc
def comp_attach_svc_ruleset(svcname, ruleset, auth):
    if len(ruleset) == 0:
        return dict(status=False, msg="no ruleset specified"%ruleset)
    rset_id = comp_ruleset_id(ruleset)
    slave = comp_slave(svcname, auth[1])
    if rset_id is None:
        return dict(status=False, msg="ruleset %s does not exist"%ruleset)
    if comp_ruleset_svc_attached(svcname, rset_id, slave):
        return dict(status=True, msg="ruleset %s is already attached to this service"%ruleset)
    if not comp_ruleset_svc_attachable(svcname, rset_id):
        return dict(status=False, msg="ruleset %s is not attachable"%ruleset)

    n = db.comp_rulesets_services.insert(svcname=svcname,
                                         ruleset_id=rset_id,
                                         slave=slave)
    if n == 0:
        return dict(status=False, msg="failed to attach ruleset %s"%ruleset)
    _log('compliance.ruleset.service.attach',
         '%(ruleset)s attached to service %(svcname)s',
        dict(svcname=svcname, ruleset=ruleset),
        user='root@'+svcname)
    return dict(status=True, msg="ruleset %s attached"%ruleset)

@auth_uuid
@service.xmlrpc
def comp_attach_svc_moduleset(svcname, moduleset, auth):
    if len(moduleset) == 0:
        return dict(status=False, msg="no moduleset specified"%moduleset)
    modset_id = comp_moduleset_id(moduleset)
    slave = comp_slave(svcname, auth[1])
    if modset_id is None:
        return dict(status=False, msg="moduleset %s does not exist"%moduleset)
    if comp_moduleset_svc_attached(svcname, modset_id, slave):
        return dict(status=True, msg="moduleset %s is already attached to this service"%moduleset)
    if not comp_moduleset_svc_attachable(svcname, modset_id):
        return dict(status=False, msg="moduleset %s is not attachable"%moduleset)

    n = db.comp_modulesets_services.insert(modset_svcname=svcname,
                                           modset_id=modset_id,
                                           slave=slave)
    if n == 0:
        return dict(status=False, msg="failed to attach moduleset %s"%moduleset)
    _log('compliance.moduleset.service.attach',
         '%(moduleset)s attached to service %(svcname)s',
        dict(svcname=svcname, moduleset=moduleset),
        user='root@'+svcname)
    return dict(status=True, msg="moduleset %s attached"%moduleset)

@auth_uuid
@service.xmlrpc
def comp_attach_moduleset(nodename, moduleset, auth):
    if len(moduleset) == 0:
        return dict(status=False, msg="no moduleset specified"%moduleset)
    modset_id = comp_moduleset_id(moduleset)
    if modset_id is None:
        return dict(status=False, msg="moduleset %s does not exist"%moduleset)
    if comp_moduleset_attached(nodename, modset_id):
        return dict(status=True, msg="moduleset %s is already attached to this node"%moduleset)
    if not comp_moduleset_attachable(nodename, modset_id):
        return dict(status=False, msg="moduleset %s is not attachable"%moduleset)

    n = db.comp_node_moduleset.insert(modset_node=nodename,
                                      modset_id=modset_id)
    update_dash_moddiff_node(nodename)

    if n == 0:
        return dict(status=False, msg="failed to attach moduleset %s"%moduleset)
    _log('compliance.moduleset.node.attach',
        '%(moduleset)s attached to node %(node)s',
        dict(node=nodename, moduleset=moduleset),
        user='root@'+nodename)
    return dict(status=True, msg="moduleset %s attached"%moduleset)

@auth_uuid
@service.xmlrpc
def comp_detach_svc_ruleset(svcname, ruleset, auth):
    if len(ruleset) == 0:
        return dict(status=False, msg="no ruleset specified"%ruleset)
    if ruleset == 'all':
        rset_id = comp_attached_svc_ruleset_id(svcname)
    else:
        rset_id = comp_ruleset_id(ruleset)
    slave = comp_slave(svcname, auth[1])
    if rset_id is None:
        return dict(status=True, msg="ruleset %s does not exist"%ruleset)
    elif ruleset == 'all' and len(rset_id) == 0:
        return dict(status=True, msg="this service has no ruleset attached")
    if ruleset != 'all' and not comp_ruleset_svc_attached(svcname, rset_id, slave):
        return dict(status=True,
                    msg="ruleset %s is not attached to this service"%ruleset)
    q = db.comp_rulesets_services.svcname == svcname
    if isinstance(rset_id, list):
        q &= db.comp_rulesets_services.ruleset_id.belongs(rset_id)
    else:
        q &= db.comp_rulesets_services.ruleset_id == rset_id
    n = db(q).delete()
    if n == 0:
        return dict(status=False, msg="failed to detach the ruleset")
    _log('compliance.ruleset.service.detach',
        '%(ruleset)s detached from service %(svcname)s',
        dict(svcname=svcname, ruleset=ruleset),
        user='root@'+svcname)
    return dict(status=True, msg="ruleset %s detached"%ruleset)

@auth_uuid
@service.xmlrpc
def comp_detach_svc_moduleset(svcname, moduleset, auth):
    if len(moduleset) == 0:
        return dict(status=False, msg="no moduleset specified"%moduleset)
    if moduleset == 'all':
        modset_id = comp_attached_svc_moduleset_id(svcname)
    else:
        modset_id = comp_moduleset_id(moduleset)
    slave = comp_slave(svcname, auth[1])
    if modset_id is None:
        return dict(status=True, msg="moduleset %s does not exist"%moduleset)
    elif moduleset == 'all' and len(modset_id) == 0:
        return dict(status=True, msg="this service has no moduleset attached")
    if moduleset != 'all' and not comp_moduleset_svc_attached(svcname, modset_id, slave):
        return dict(status=True,
                    msg="moduleset %s is not attached to this service"%moduleset)
    q = db.comp_modulesets_services.modset_svcname == svcname
    if isinstance(modset_id, list):
        q &= db.comp_modulesets_services.modset_id.belongs(modset_id)
    else:
        q &= db.comp_modulesets_services.modset_id == modset_id
    n = db(q).delete()
    if n == 0:
        return dict(status=False, msg="failed to detach the moduleset")
    _log('compliance.moduleset.service.detach',
        '%(moduleset)s detached from service %(svcname)s',
        dict(svcname=svcname, moduleset=moduleset),
        user='root@'+svcname)
    return dict(status=True, msg="moduleset %s detached"%moduleset)

@auth_uuid
@service.xmlrpc
def comp_detach_moduleset(nodename, moduleset, auth):
    if len(moduleset) == 0:
        return dict(status=False, msg="no moduleset specified"%moduleset)
    if moduleset == 'all':
        modset_id = comp_attached_moduleset_id(nodename)
    else:
        modset_id = comp_moduleset_id(moduleset)
    if modset_id is None:
        return dict(status=True, msg="moduleset %s does not exist"%moduleset)
    elif moduleset == 'all' and len(modset_id) == 0:
        return dict(status=True, msg="this node has no moduleset attached")
    if moduleset != 'all' and not comp_moduleset_attached(nodename, modset_id):
        return dict(status=True,
                    msg="moduleset %s is not attached to this node"%moduleset)
    q = db.comp_node_moduleset.modset_node == nodename
    if isinstance(modset_id, list):
        q &= db.comp_node_moduleset.modset_id.belongs(modset_id)
    else:
        q &= db.comp_node_moduleset.modset_id == modset_id
    n = db(q).delete()
    if n == 0:
        return dict(status=False, msg="failed to detach the moduleset")
    update_dash_moddiff_node(nodename)

    _log('compliance.moduleset.node.detach',
        '%(moduleset)s detached from node %(node)s',
        dict(node=nodename, moduleset=moduleset),
        user='root@'+nodename)
    return dict(status=True, msg="moduleset %s detached"%moduleset)

def comp_moduleset_svc_attachable(svcname, modset_id):
    q = db.services.svc_name == svcname
    q &= db.services.svc_app == db.apps.app
    q &= db.apps.id == db.apps_responsibles.app_id
    q &= db.apps_responsibles.group_id == db.auth_group.id
    q &= db.auth_group.id == db.comp_moduleset_team_responsible.group_id
    q &= db.comp_moduleset_team_responsible.modset_id == db.comp_moduleset.id
    q &= db.comp_moduleset.id == modset_id
    rows = db(q).select(db.nodes.team_responsible)
    if len(rows) == 0:
        return False
    return True

def comp_ruleset_svc_attachable(svcname, rset_id):
    q = db.services.svc_name == svcname
    q &= db.services.svc_app == db.apps.app
    q &= db.apps.id == db.apps_responsibles.app_id
    q &= db.apps_responsibles.group_id == db.auth_group.id
    q &= db.auth_group.id == db.comp_ruleset_team_responsible.group_id
    q &= db.comp_ruleset_team_responsible.ruleset_id == db.comp_rulesets.id
    q &= db.comp_rulesets.id == rset_id
    rows = db(q).select(db.nodes.team_responsible)
    if len(rows) == 0:
        return False
    return True

def comp_moduleset_attachable(nodename, modset_id):
    q = db.nodes.team_responsible == db.auth_group.role
    q &= db.auth_group.id == db.comp_moduleset_team_responsible.group_id
    q &= db.comp_moduleset_team_responsible.modset_id == db.comp_moduleset.id
    q &= db.comp_moduleset.id == modset_id
    q &= db.nodes.nodename == nodename
    rows = db(q).select(db.nodes.team_responsible)
    if len(rows) != 1:
        return False
    return True

def comp_ruleset_attachable(nodename, ruleset_id):
    q = db.nodes.team_responsible == db.auth_group.role
    q &= db.auth_group.id == db.comp_ruleset_team_responsible.group_id
    q &= db.comp_ruleset_team_responsible.ruleset_id == db.comp_rulesets.id
    q &= db.comp_rulesets.id == ruleset_id
    q &= db.nodes.nodename == nodename
    rows = db(q).select()
    if len(rows) != 1:
        return False
    return True

@auth_uuid
@service.xmlrpc
def comp_attach_ruleset(nodename, ruleset, auth):
    if len(ruleset) == 0:
        return dict(status=False, msg="no ruleset specified"%ruleset)
    ruleset_id = comp_ruleset_exists(ruleset)
    if ruleset_id is None:
        return dict(status=False, msg="ruleset %s does not exist"%ruleset)
    if comp_ruleset_attached(nodename, ruleset_id):
        return dict(status=True,
                    msg="ruleset %s is already attached to this node"%ruleset)
    if not comp_ruleset_attachable(nodename, ruleset_id):
        return dict(status=False,
                    msg="ruleset %s is not attachable"%ruleset)

    q = db.comp_rulesets_nodes.nodename == nodename
    q &= db.comp_rulesets_nodes.ruleset_id == ruleset_id
    if db(q).count() > 0:
        return dict(status=True, msg="ruleset %s already attached"%ruleset)

    n = db.comp_rulesets_nodes.insert(nodename=nodename,
                                      ruleset_id=ruleset_id)
    update_dash_rsetdiff_node(nodename)

    if n == 0:
        return dict(status=False, msg="failed to attach ruleset %s"%ruleset)
    _log('compliance.ruleset.node.attach',
        '%(ruleset)s attached to node %(node)s',
        dict(node=nodename, ruleset=ruleset),
        user='root@'+nodename)
    return dict(status=True, msg="ruleset %s attached"%ruleset)

@auth_uuid
@service.xmlrpc
def comp_detach_ruleset(nodename, ruleset, auth):
    if len(ruleset) == 0:
        return dict(status=False, msg="no ruleset specified"%ruleset)
    if ruleset == 'all':
        ruleset_id = comp_attached_ruleset_id(nodename)
    else:
        ruleset_id = comp_ruleset_exists(ruleset)
    if ruleset_id is None:
        return dict(status=False, msg="ruleset %s does not exist"%ruleset)
    elif ruleset == 'all' and len(ruleset_id) == 0:
        return dict(status=True, msg="this node has no ruleset attached")
    if ruleset != 'all' and not comp_ruleset_attached(nodename, ruleset_id):
        return dict(status=True,
                    msg="ruleset %s is not attached to this node"%ruleset)
    q = db.comp_rulesets_nodes.nodename == nodename
    if isinstance(ruleset_id, list):
        q &= db.comp_rulesets_nodes.ruleset_id.belongs(ruleset_id)
    else:
        q &= db.comp_rulesets_nodes.ruleset_id == ruleset_id
    n = db(q).delete()
    if n == 0:
        return dict(status=False, msg="failed to detach the ruleset")
    update_dash_rsetdiff_node(nodename)
    _log('compliance.ruleset.node.detach',
        '%(ruleset)s detached from node %(node)s',
        dict(node=nodename, ruleset=ruleset),
        user='root@'+nodename)
    return dict(status=True, msg="ruleset %s detached"%ruleset)

@auth_uuid
@service.xmlrpc
def comp_list_rulesets(pattern='%', nodename=None, auth=("", "")):
    q = db.comp_rulesets.ruleset_name.like(pattern)
    q &= db.comp_rulesets.ruleset_type == 'explicit'
    q &= db.comp_rulesets.ruleset_public == True
    q &= db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if nodename != None:
        q &= db.nodes.nodename == nodename
        q &= db.nodes.team_responsible == db.auth_group.role
        q &= db.auth_group.id == db.comp_ruleset_team_responsible.group_id
    rows = db(q).select(groupby=db.comp_rulesets.id)
    return sorted([r.comp_rulesets.ruleset_name for r in rows])

@auth_uuid
@service.xmlrpc
def comp_list_modulesets(pattern='%', auth=("", "")):
    node = auth[1]
    q = db.comp_moduleset.modset_name.like(pattern)
    q &= db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    q &= db.auth_group.id == db.comp_moduleset_team_responsible.group_id
    q &= db.nodes.team_responsible == db.auth_group.role
    q &= db.nodes.nodename == node
    rows = db(q).select(db.comp_moduleset.modset_name, groupby=db.comp_moduleset.modset_name)
    return sorted([r.modset_name for r in rows])

@auth_uuid
@service.xmlrpc
def comp_show_status(svcname="", pattern='%', auth=("", "")):
    node = auth[1]
    q = db.comp_status.run_module.like(pattern)
    q &= db.comp_status.run_nodename == node
    q &= db.comp_status.run_svcname == svcname
    rows = db(q).select(orderby=db.comp_status.run_module)
    l = [('module', 'status', 'date', 'log')]
    for row in rows:
        l.append((row.run_module,
                  str(row.run_status),
                  row.run_date.strftime("%Y-%m-%d %H:%M:%S"),
                  row.run_log))
    return l

@auth_uuid
@service.xmlrpc
def comp_get_svc_moduleset(svcname, auth):
    slave = comp_slave(svcname, auth[1])
    return _comp_get_svc_moduleset(svcname, slave)

@auth_uuid
@service.xmlrpc
def comp_get_moduleset(nodename, auth):
    return _comp_get_moduleset(nodename)

def _comp_get_svc_moduleset(svcname, slave=False):
    q = db.comp_modulesets_services.modset_svcname == svcname
    q &= db.comp_modulesets_services.slave == slave
    q &= db.comp_modulesets_services.modset_id == db.comp_moduleset.id
    q &= db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    q &= db.auth_group.id == db.comp_moduleset_team_responsible.group_id
    q &= db.services.svc_name == svcname
    q &= db.services.svc_app == db.apps.app
    q &= db.apps.id == db.apps_responsibles.app_id
    q &= db.apps_responsibles.group_id == db.auth_group.id
    rows = db(q).select(db.comp_moduleset.modset_name, groupby=db.comp_modulesets_services.modset_id)
    return [r.modset_name for r in rows]

def _comp_get_moduleset(nodename):
    q = db.comp_node_moduleset.modset_node == nodename
    q &= db.comp_node_moduleset.modset_id == db.comp_moduleset.id
    q &= db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    q &= db.auth_group.id == db.comp_moduleset_team_responsible.group_id
    q &= db.nodes.team_responsible == db.auth_group.role
    q &= db.nodes.nodename == nodename
    rows = db(q).select(db.comp_moduleset.modset_name, groupby=db.comp_node_moduleset.modset_id)
    return [r.modset_name for r in rows]

@auth_uuid
@service.xmlrpc
def comp_log_action(vars, vals, auth):
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
        update_dash_compdiff(auth[1])

def comp_query(q, row):
    if 'v_gen_filtersets' in row:
        v = row.v_gen_filtersets
    else:
        v = row
    if v.encap_fset_id > 0:
        o = db.v_gen_filtersets.f_order
        qr = db.v_gen_filtersets.fset_id == v.encap_fset_id
        rows = db(qr).select(orderby=o)
        qry = None
        for r in rows:
            qry = comp_query(qry, r)
    else:
        if v.f_op == '=':
            qry = db[v.f_table][v.f_field] == v.f_value
        elif v.f_op == '!=':
            qry = db[v.f_table][v.f_field] != v.f_value
        elif v.f_op == 'LIKE':
            qry = db[v.f_table][v.f_field].like(v.f_value)
        elif v.f_op == 'NOT LIKE':
            qry = ~db[v.f_table][v.f_field].like(v.f_value)
        elif v.f_op == 'IN':
            qry = db[v.f_table][v.f_field].belongs(v.f_value.split(','))
        elif v.f_op == 'NOT IN':
            qry = ~db[v.f_table][v.f_field].belongs(v.f_value.split(','))
        elif v.f_op == '>=':
            qry = db[v.f_table][v.f_field] >= v.f_value
        elif v.f_op == '>':
            qry = db[v.f_table][v.f_field] > v.f_value
        elif v.f_op == '<=':
            qry = db[v.f_table][v.f_field] <= v.f_value
        elif v.f_op == '<':
            qry = db[v.f_table][v.f_field] < v.f_value
        else:
            return q
    if q is None:
        q = qry
    elif v.f_log_op == 'AND':
        q &= qry
    elif v.f_log_op == 'AND NOT':
        q &= ~qry
    elif v.f_log_op == 'OR':
        q |= qry
    elif v.f_log_op == 'OR NOT':
        q |= ~qry
    return q

def comp_format_filter(q):
    s = str(q)
    if 'comp_node_ruleset' in s:
        return ''
    #s = s.replace('(','')
    #s = s.replace(')','')
    s = s.replace('nodes.id>0 AND ','')
    return s

def comp_get_svcmon_ruleset(svcname, nodename):
    q = db.svcmon.mon_svcname == svcname
    q &= db.svcmon.mon_nodname == nodename
    row = db(q).select().first()
    if row is None:
        q = db.svcmon.mon_svcname == svcname
        q &= db.svcmon.mon_vmname == nodename
        q &= db.svcmon.mon_containerstatus == "up"
        row = db(q).select().first()
    if row is None:
        return {}
    ruleset = {'name': 'osvc_svcmon',
               'filter': str(q),
               'vars': []}
    for f in db.svcmon.fields:
        val = row[f]
        ruleset['vars'].append(('svcmon.'+f, val))
    return {'osvc_svcmon':ruleset}

def comp_get_service_ruleset(svcname):
    q = db.services.svc_name == svcname
    rows = db(q).select()
    if len(rows) != 1:
        return {}
    ruleset = {'name': 'osvc_service',
               'filter': str(q),
               'vars': []}
    for f in db.services.fields:
        val = rows[0][f]
        ruleset['vars'].append(('services.'+f, val))
    return {'osvc_service':ruleset}

def comp_get_node_ruleset(nodename):
    q = db.v_nodes.nodename == nodename
    rows = db(q).select()
    if len(rows) != 1:
        return {}
    ruleset = {'name': 'osvc_node',
               'filter': str(q),
               'vars': []}
    for f in db.nodes.fields:
        val = rows[0][f]
        ruleset['vars'].append(('nodes.'+f, val))
    return {'osvc_node':ruleset}

def comp_get_rulesets_filters(rset_ids=None, nodename=None, svcname=None, head=True):
    v = db.v_gen_filtersets
    rset = db.comp_rulesets
    rset_fset = db.comp_rulesets_filtersets
    o = rset.ruleset_name|v.f_order

    if rset_ids is None:
        q = rset.id>0
    else:
        q = rset.id.belongs(rset_ids)

    q &= rset.id == rset_fset.ruleset_id
    q &= rset_fset.fset_id == v.fset_id
    q &= rset.id == db.comp_ruleset_team_responsible.ruleset_id

    if head:
        q &= rset.ruleset_public == True
        if nodename is not None:
            q &= db.comp_ruleset_team_responsible.group_id == node_team_responsible_id(nodename)
        elif svcname is not None:
            q &= db.comp_ruleset_team_responsible.group_id.belongs(svc_team_responsible_id(svcname))

    return db(q).select(orderby=o)

def comp_ruleset_vars(ruleset_id, qr=None, nodename=None, svcname=None, slave=False):
    if qr is None:
        f = 'explicit attachment'
    else:
        f = comp_format_filter(qr)
    q1 = db.comp_rulesets_rulesets.parent_rset_id==ruleset_id
    q1 &= db.comp_rulesets_rulesets.child_rset_id == db.comp_rulesets.id
    q = db.comp_rulesets.id == ruleset_id

    head_rset = db(q).select(db.comp_rulesets.ruleset_name).first()
    if head_rset is None:
        return dict()

    children = []
    rows = db(q1).select(db.comp_rulesets_rulesets.child_rset_id,
                         db.comp_rulesets.ruleset_type)
    for row in rows:
        id = row.comp_rulesets_rulesets.child_rset_id
        if row.comp_rulesets.ruleset_type == "explicit":
            children.append(id)
        elif row.comp_rulesets.ruleset_type == "contextual":
            # don't validate sub ruleset ownership.
            # parent ownership is inherited
            if comp_ruleset_match(id, nodename=nodename, svcname=svcname,
                                  slave=slave, head=False):
                children.append(id)

    if len(children) > 0:
        q |= db.comp_rulesets.id.belongs(children)

    # get variables
    q &= db.comp_rulesets.id == db.comp_rulesets_variables.ruleset_id
    rows = db(q).select()
    ruleset_name = head_rset.ruleset_name
    d = dict(
          name=ruleset_name,
          filter=f,
          vars=[]
        )
    for row in rows:
        d['vars'].append((row.comp_rulesets_variables.var_name,
                          row.comp_rulesets_variables.var_value))
    return {ruleset_name: d}

def ruleset_add_var(d, rset_name, var, val):
    d[rset_name]['vars'].append((var, val))
    return d

@auth_uuid
@service.xmlrpc
def comp_get_ruleset_md5(rset_md5, auth):
    q = db.comp_run_ruleset.rset_md5 == rset_md5
    row = db(q).select(db.comp_run_ruleset.rset).first()
    if row is None:
        return
    import cPickle
    try:
        ruleset = cPickle.loads(row.rset)
    except:
        return
    return ruleset

def svc_team_responsible_id(svcname):
    q = db.services.svc_name == svcname
    q &= db.services.svc_app == db.apps.app
    q &= db.apps.id == db.apps_responsibles.app_id
    q &= db.apps_responsibles.group_id == db.auth_group.id
    rows = db(q).select(db.auth_group.id, groupby=db.auth_group.id)
    return map(lambda x: x['id'], rows)

def node_team_responsible_id(nodename):
    q = db.nodes.nodename == nodename
    q &= db.nodes.team_responsible == db.auth_group.role
    rows = db(q).select(db.auth_group.id)
    if len(rows) != 1:
        return None
    return rows[0].id

@auth_uuid
@service.xmlrpc
def comp_get_ruleset(nodename, auth):
    return _comp_get_ruleset(nodename)

@auth_uuid
@service.xmlrpc
def comp_get_svc_ruleset(svcname, auth):
    slave = comp_slave(svcname, auth[1])
    ruleset = _comp_get_svc_ruleset(svcname, slave=slave)
    ruleset.update(_comp_get_svc_per_node_ruleset(svcname, auth[1], slave))
    ruleset.update(comp_get_svcmon_ruleset(svcname, auth[1]))
    ruleset.update(comp_get_node_ruleset(auth[1]))
    ruleset = _comp_remove_dup_vars(ruleset)
    insert_run_rset(ruleset)
    return ruleset

def comp_ruleset_match(id, svcname=None, nodename=None, slave=False, head=True):
    if svcname is not None:
        return _comp_ruleset_svc_match(id, svcname=svcname, nodename=nodename,
                                       slave=slave,
                                       head=head)
    else:
        return _comp_ruleset_match(id, nodename=nodename,
                                   head=head)

def _comp_ruleset_svc_match(id, svcname=None, nodename=None, slave=False, head=True):
    rows = comp_get_rulesets_filters([id], svcname=svcname,
                                     head=head)
    if len(rows) == 0:
        return False

    q = db.services.svc_name == svcname
    if slave:
        if nodename is not None:
            q &= db.svcmon.mon_vmname == nodename
        j = db.nodes.nodename == db.svcmon.mon_vmname
    else:
        if nodename is not None:
            q &= db.svcmon.mon_nodname == nodename
        j = db.nodes.nodename == db.svcmon.mon_nodname
    l1 = db.nodes.on(j)
    j = db.svcmon.mon_svcname == db.services.svc_name
    l2 = db.svcmon.on(j)
    qr = db.services.id > 0
    need = False

    for i, row in enumerate(rows):
        qr = comp_query(qr, row)
        if row.v_gen_filtersets.f_table in ('svcmon', 'services'):
            need = True

    if not need:
        match = db(q&qr).select(db.nodes.id, db.svcmon.mon_svcname, left=(l2,l1))
        if len(match) > 0:
            return True
    return False

def _comp_ruleset_match(id, nodename=None, head=True):
    rows = comp_get_rulesets_filters([id], nodename=nodename,
                                     head=head)
    if len(rows) == 0:
        return False

    q = db.nodes.nodename == nodename
    j = db.nodes.nodename == db.svcmon.mon_nodname
    l1 = db.svcmon.on(j)
    j = db.svcmon.mon_svcname == db.services.svc_name
    l2 = db.services.on(j)
    qr = db.nodes.id > 0

    for i, row in enumerate(rows):
        qr = comp_query(qr, row)

    match = db(q&qr).select(db.nodes.id, db.svcmon.mon_svcname, left=(l1,l2))
    if len(match) > 0:
        return True
    return False

def _comp_get_svc_per_node_ruleset(svcname, nodename, slave=False):
    ruleset = {}

    # add contextual rulesets variables
    rows = comp_get_rulesets_filters(svcname=svcname)

    q = db.services.svc_name == svcname
    if slave:
        if nodename is not None:
            q &= db.svcmon.mon_vmname == nodename
        j = db.nodes.nodename == db.svcmon.mon_vmname
    else:
        if nodename is not None:
            q &= db.svcmon.mon_nodname == nodename
        j = db.nodes.nodename == db.svcmon.mon_nodname
    l1 = db.nodes.on(j)
    j = db.svcmon.mon_svcname == db.services.svc_name
    l2 = db.svcmon.on(j)
    last_index = len(rows)-1
    qr = db.services.id > 0
    need = False

    for i, row in enumerate(rows):
        if i == last_index:
            end_seq = True
        elif rows[i].comp_rulesets.ruleset_name != rows[i+1].comp_rulesets.ruleset_name:
            end_seq = True
        else:
            end_seq = False
        qr = comp_query(qr, row)
        if row.v_gen_filtersets.f_table in ('svcmon', 'services'):
            need = True
        if end_seq:
            if not need:
                match = db(q&qr).select(db.nodes.id, db.svcmon.mon_svcname,
                                        left=(l2,l1))
                if len(match) > 0:
                    ruleset.update(comp_ruleset_vars(row.comp_rulesets.id, qr=qr, nodename=nodename, svcname=svcname, slave=slave))
                need = False
            qr = db.services.id > 0

    return ruleset

def _comp_get_svc_ruleset(svcname, slave=False):
    # initialize ruleset with asset variables
    ruleset = comp_get_service_ruleset(svcname)

    # add contextual rulesets variables
    rows = comp_get_rulesets_filters(svcname=svcname)

    q = db.services.svc_name == svcname
    if slave:
        j = db.nodes.nodename == db.svcmon.mon_vmname
    else:
        j = db.nodes.nodename == db.svcmon.mon_nodname
    l1 = db.nodes.on(j)
    j = db.svcmon.mon_svcname == db.services.svc_name
    l2 = db.svcmon.on(j)
    last_index = len(rows)-1
    qr = db.services.id > 0
    need = False

    for i, row in enumerate(rows):
        if i == last_index:
            end_seq = True
        elif rows[i].comp_rulesets.ruleset_name != rows[i+1].comp_rulesets.ruleset_name:
            end_seq = True
        else:
            end_seq = False
        qr = comp_query(qr, row)
        if row.v_gen_filtersets.f_table in ('svcmon', 'services'):
            need = True
        if end_seq:
            if need:
                match = db(q&qr).select(db.nodes.id, db.svcmon.mon_svcname,
                                        left=(l2,l1))
                if len(match) > 0:
                    ruleset.update(comp_ruleset_vars(row.comp_rulesets.id, qr=qr, svcname=svcname, slave=slave))
                need = False
            qr = db.services.id > 0

    # add explicit rulesets variables
    q = db.comp_rulesets_services.svcname == svcname
    q &= db.comp_rulesets_services.slave == slave
    rows = db(q).select(db.comp_rulesets_services.ruleset_id,
                        orderby=db.comp_rulesets_services.ruleset_id)
    for row in rows:
        ruleset.update(comp_ruleset_vars(row.ruleset_id, svcname=svcname, slave=slave))

    return ruleset

def insert_run_rset(ruleset):
    import cPickle
    o = md5()
    s = cPickle.dumps(ruleset)
    keys = sorted(ruleset.keys())
    for key in keys:
        o.update(str(ruleset[key]))
    rset_md5 = str(o.hexdigest())
    try:
        db.comp_run_ruleset.insert(rset_md5=rset_md5, rset=s)
    except:
        pass
    rset = {'name': 'osvc_collector',
            'filter': '',
            'vars': [('ruleset_md5', rset_md5)]}
    return ruleset.update({'osvc_collector': rset})

def _comp_remove_dup_vars(ruleset):
    l = {}
    for rset in ruleset.copy():
        for i, (var, val) in enumerate(ruleset[rset]['vars']):
            removed_s = 'Duplicate variable removed'
            if var in l:
                (_rset, _i, _val) = l[var][0]
                if _val != ruleset[rset]['vars'][i][1] or _val == removed_s:
                    for _rset, _i, _val in l[var]:
                        ruleset[_rset]['vars'][_i] = ('xxx_'+var+'_xxx', removed_s)
                    ruleset[rset]['vars'][i] = ('xxx_'+var+'_xxx', removed_s)
            else:
                l[var] = [(rset, i, ruleset[rset]['vars'][i][1])]
    return ruleset

def _comp_get_ruleset(nodename):
    # initialize ruleset with asset variables
    ruleset = comp_get_node_ruleset(nodename)

    # add contextual rulesets variables
    rows = comp_get_rulesets_filters(nodename=nodename)

    q = db.nodes.nodename == nodename
    j = db.nodes.nodename == db.svcmon.mon_nodname
    l1 = db.svcmon.on(j)
    j = db.svcmon.mon_svcname == db.services.svc_name
    l2 = db.services.on(j)
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
            match = db(q&qr).select(db.nodes.id, db.svcmon.mon_svcname,
                                    left=(l1,l2))
            if len(match) > 0:
                ruleset.update(comp_ruleset_vars(row.comp_rulesets.id, qr=qr, nodename=nodename))
            qr = db.nodes.id > 0
    # add explicit rulesets variables
    q = db.comp_rulesets_nodes.nodename == nodename
    rows = db(q).select(db.comp_rulesets_nodes.ruleset_id,
                        orderby=db.comp_rulesets_nodes.ruleset_id)
    for row in rows:
        ruleset.update(comp_ruleset_vars(row.ruleset_id, nodename=nodename))

    ruleset = _comp_remove_dup_vars(ruleset)

    insert_run_rset(ruleset)

    return ruleset


#
# Ajax for node tabs
#
def beautify_var(v):
    var = v[0].upper()
    val = v[1]
    if (isinstance(val, str) or isinstance(val, unicode)) and ' ' in val:
        val = repr(val)
    d = LI('OSVC_COMP_'+var, '=', val, _style="word-wrap:break-word")
    return d

def beautify_ruleset(rset):
    vl = []
    for v in rset['vars']:
        vl.append(beautify_var(v))

    import uuid
    did = "i"+uuid.uuid1().hex
    u = UL(
          LI(
            DIV(
              rset['name'],
              P(rset['filter'], _style='font-weight:normal'),
              _onclick="""$("#%s").toggle();$(this).toggleClass("down16").toggleClass("right16")"""%did,
              _class="right16",
            ),
            UL(
              vl,
              _id=did,
              _style="display:none",
              _class="pre",
            ),
          ),
          _class="clickable",
        )
    return u

def beautify_rulesets(rsets):
    l = []
    for rset in rsets:
        l.append(beautify_ruleset(rsets[rset]))
    return SPAN(l, _class='xset')

def beautify_moduleset(mset, mods):
    ml = []
    for m in mods:
        ml.append(LI(m))

    u = UL(
          LI(
            mset,
            UL(ml),
          ),
        )
    return u

def beautify_svc_modulesets(msets, svcname):
    q = db.svcmon.mon_svcname == svcname
    node = db(q).select()
    if node is None:
        return ""
    node = node.first().mon_nodname
    return beautify_modulesets(msets, node)

def beautify_modulesets(msets, node):
    l = []
    for mset in msets:
        l.append(beautify_moduleset(mset, _comp_get_moduleset_modules(mset, node)))
    return SPAN(l, _class='xset')

def svc_comp_status(svcname):
    tid = 'scs_'+svcname
    t = table_comp_status(tid, 'svc_comp_status')
    t.cols.remove('run_status_log')

    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    q &= db.comp_status.run_svcname == svcname
    t.object_list = db(q).select()
    t.hide_tools = True
    t.pageable = False
    t.linkable = False
    t.filterable = False
    t.exportable = False
    t.dbfilterable = False
    t.columnable = False
    t.refreshable = False
    return t.html()

def node_comp_status(node):
    tid = 'ncs_'+node
    t = table_comp_status(tid, 'node_comp_status')
    t.cols.remove('run_status_log')

    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    q &= db.comp_status.run_nodename == node
    t.object_list = db(q).select()
    t.hide_tools = True
    t.pageable = False
    t.linkable = False
    t.filterable = False
    t.exportable = False
    t.dbfilterable = False
    t.columnable = False
    t.refreshable = False
    return t.html()

@auth.requires_login()
def ajax_rset_md5():
    rset_md5 = request.vars.rset_md5
    row = db(db.comp_run_ruleset.rset_md5==rset_md5).select().first()
    if row is None:
        return ''
    import cPickle
    rsets = cPickle.loads(row.rset)
    d = SPAN(
          H3(T('Ruleset %(rset_md5)s',dict(rset_md5=rset_md5))),
          beautify_rulesets(rsets),
        )
    return d

@auth.requires_login()
def ajax_compliance_svc():
    svcname = request.args[0]
    rsets = _comp_get_svc_ruleset(svcname)
    msets = _comp_get_svc_moduleset(svcname)

    d = []
    q = db.svcmon.mon_svcname==svcname
    q &= db.svcmon.mon_updated > now - datetime.timedelta(days=1)
    rows = db(q).select(db.svcmon.mon_nodname, db.svcmon.mon_vmname)
    nodes = [r.mon_nodname for r in rows]
    vnodes = [r.mon_vmname for r in rows if r.mon_vmname is not None and r.mon_vmname != ""]
    for r in rows:
        if r.mon_vmname is not None and r.mon_vmname not in nodes:
            nodes.append(r.mon_vmname)

    for node in nodes:
        did = 'nrs_'+node.replace('.','').replace('-','')
        n_rsets = comp_get_svcmon_ruleset(svcname, node)
        n_rsets.update(comp_get_node_ruleset(node))
        if node in vnodes:
            slave = True
        else:
            slave = False
        n_rsets.update(_comp_get_svc_per_node_ruleset(svcname, node, slave))
        d.append(DIV(
                   B(node),
                   _onclick="""$("#%s").toggle();$(this).toggleClass("down16").toggleClass("right16")"""%did,
                   _class="clickable right16",
                )
        )
        d.append(DIV(
                   beautify_rulesets(n_rsets),
                   _style="display:none",
                   _id=did,
                 )
        )

    div_ersets = SPAN()
    did = 'esrs_'+svcname.replace('.','').replace('-','')
    if len(vnodes) > 0:
        ersets = _comp_get_svc_ruleset(svcname, slave=True)
        div_ersets = SPAN(
          DIV(
            B(svcname + ' (slave)'),
            _onclick="""$("#%s").toggle();$(this).toggleClass("down16").toggleClass("right16")"""%did,
            _class="clickable right16",
          ),
          DIV(
            beautify_rulesets(ersets),
            _style="display:none",
            _id=did,
          ),
        )

    did = 'srs_'+svcname.replace('.','').replace('-','')
    d = SPAN(
          H3(T('Status')),
          svc_comp_status(svcname),
          H3(T('Modulesets')),
          beautify_svc_modulesets(msets, svcname),
          H3(T('Rulesets')),
          DIV(
            B(svcname),
            _onclick="""$("#%s").toggle();$(this).toggleClass("down16").toggleClass("right16")"""%did,
            _class="clickable right16",
          ),
          DIV(
            beautify_rulesets(rsets),
            _style="display:none",
            _id=did,
          ),
          div_ersets,
          H3(T('Per node additional rulesets')),
          SPAN(d),
          SPAN(show_diff(svcname)),
        )
    return d

def show_diff(svcname):
    l = []
    compdiff = show_compdiff(svcname)
    moddiff = show_moddiff(svcname)
    rsetdiff = show_rsetdiff(svcname)

    if compdiff is not None or moddiff is not None or rsetdiff is not None:
        l.append(HR())

    if compdiff is not None:
        l.append(SPAN(
          H3(T('Module status differences in cluster')),
          compdiff))

    if moddiff is not None:
        l.append(SPAN(
          H3(T('Moduleset attachment differences in cluster')),
          moddiff))

    if rsetdiff is not None:
        l.append(SPAN(
          H3(T('Ruleset attachment differences in cluster')),
          rsetdiff))

    return l

@auth.requires_login()
def ajax_compliance_node():
    node = request.args[0]
    rsets = _comp_get_ruleset(node)
    msets = _comp_get_moduleset(node)
    d = SPAN(
          H3(T('Status')),
          node_comp_status(node),
          H3(T('Modulesets')),
          beautify_modulesets(msets, node),
          H3(T('Rulesets')),
          beautify_rulesets(rsets),
        )
    return d

@service.xmlrpc
def register_node(node):
    """ placeholder to signal the registration support
    """
    pass


#
# CVE batch
#
def run_cve():
    q = db.comp_rulesets_variables.var_class == 'cve'
    rows = db(q).select(db.comp_rulesets_variables.var_name,
                        db.comp_rulesets_variables.var_value)
    for row in rows:
        run_cve_one(row)

def run_cve_one(row):
    try:
        cve = json.loads(row['var_value'])
    except:
        return
    cve['name'] = row['var_name']

    def on_packages(cve):
        sql = """select distinct pkg_nodename
                 from packages
                 where
                   pkg_updated > DATE_SUB(NOW(), INTERVAL 2 DAY) and
                   pkg_name="%s" and
                   greatest(pkg_version, "%s")=pkg_version and
                   least(pkg_version, "%s")=pkg_version
              """%(cve['product'], cve['minver'], cve['maxver'])
        rows = db.executesql(sql)
        if len(rows) == 0:
            return []
        return map(lambda x: x[0], rows)

    nodes = on_packages(cve)
    if len(nodes) > 0:
        where = "where nodename in (%s)"%','.join(map(lambda x: '"'+x+'"', nodes))
        sql = """insert into comp_status
                   select
                     NULL,
                     nodename,
                     "%(cve_name)s",
                     1,
                     "",
                     "%(now)s",
                     "cve",
                     "check"
                   from nodes
                   %(where)s
                   on duplicate key update
                     run_status=1,
                     run_date="%(now)s"
              """%dict(where=where, cve_name=cve['name'], now=now)
        db.executesql(sql)
        db.commit()

    if len(nodes) > 0:
        where = "where nodename not in (%s)"%','.join(map(lambda x: '"'+x+'"', nodes))
    else:
        where = ""
    sql = """insert into comp_status
               select
                 NULL,
                 nodename,
                 "%(cve_name)s",
                 0,
                 "",
                 "%(now)s",
                 "cve",
                 "check"
               from nodes
               %(where)s
               on duplicate key update
                 run_status=0,
                 run_date="%(now)s"
          """%dict(where=where, cve_name=cve['name'], now=now)
    db.executesql(sql)
    db.commit()


#
# Dashboard alerts
#
def cron_dash_comp():
    cron_dash_moddiff()
    cron_dash_rsetdiff()

def show_compdiff(svcname):
    rows = db(db.svcmon.mon_svcname==svcname).select()
    nodes = [r.mon_nodname for r in rows]
    nodes.sort()
    n = len(nodes)

    if n < 2:
        return

    sql = """select t.* from (
               select
                 count(cs.run_nodename) as c,
                 cs.run_module,
                 cs.run_nodename,
                 cs.run_status
               from
                 comp_status cs,
                 svcmon m
               where
                 (cs.run_svcname is NULL or cs.run_svcname="") and
                 m.mon_svcname="%(svcname)s" and
                 m.mon_nodname=cs.run_nodename
               group by
                 cs.run_module,
                 cs.run_status
              ) as t
              where
                t.c!=%(n)s
              order by
                t.run_module,
                t.run_nodename,
                t.run_status
              """%dict(svcname=svcname, n=n)

    _rows = db.executesql(sql)

    if len(_rows) == 0:
        return

    mods = [r[1] for r in _rows]

    sql = """select
               cs.run_nodename,
               cs.run_module,
               cs.run_status,
               cs.run_log,
               cs.run_date
             from
               comp_status cs,
               svcmon m
             where
               (cs.run_svcname is NULL or cs.run_svcname="") and
               cs.run_module in (%(mods)s) and
               m.mon_svcname="%(svcname)s" and
               m.mon_nodname=cs.run_nodename
             order by
               cs.run_module,
               cs.run_nodename
         """%dict(svcname=svcname, mods=','.join(map(lambda x: repr(str(x)), mods)))
    _rows = db.executesql(sql)

    if len(_rows) == 0:
        return

    data = {}
    for row in _rows:
        module = row[1]
        if module not in data:
            data[module] = {}
        data[module][row[0]] = row

    def fmt_header1():
        return TR(
                 TH("", _colspan=1),
                 TH(T("Nodes"), _colspan=n, _style="text-align:center"),
               )

    def fmt_header2():
        h = [TH(T("Module"))]
        for node in nodes:
            h.append(TH(
              node.split('.')[0],
              _style="text-align:center",
            ))
        return TR(h)

    deadline = now - datetime.timedelta(days=7)


    def outdated(t):
         if t is None or t == '': return True
         if t < deadline: return True
         return False

    def fmt_line(module, rows, bg):
        h = [TD(module)]
        for row in rows:
            if outdated(row[4]):
                d = 'background-color:lightgrey'
            else:
                d = ''
            if row[2] == "":
                h.append(TD("", _style="text-align:center"+d))
                continue
            h.append(TD(
              IMG(_src=URL(r=request,c='static',f=img_h[row[2]])),
              _style="text-align:center"+d,
              _title=str(row[4]) + '\n' + row[3],
              _onclick="""if (confirm("%(text)s")){ajax('%(url)s',[], this)};"""%dict(
                  url=URL(r=request, f='fix_module_on_node', args=[row[0], module]),
                  text=T("Please confirm you want to fix the '%(mod)s' compliance module on the node '%(node)s'", dict(mod=str(module), node=str(row[0]))),
              )
            ))
        return TR(h, _class=bg)

    def fmt_table(rows):
        bgl = {'cell1': 'cell3', 'cell3': 'cell1'}
        bg = "cell1"
        lines = [fmt_header1(),
                 fmt_header2()]
        for module in sorted((data.keys())):
            bg = bgl[bg]
            rows = []
            for node in nodes:
                if node not in data[module]:
                    rows.append([node, module, "", "", ""])
                else:
                    rows.append(data[module][node])
            lines.append(fmt_line(module, rows, bg))
        return TABLE(lines)

    return DIV(fmt_table(_rows))


def cron_dash_moddiff():
    q = db.services.updated > now - datetime.timedelta(days=2)
    svcnames = [r.svc_name for r in db(q).select(db.services.svc_name)]

    r = []
    for svcname in svcnames:
        r.append(update_dash_moddiff(svcname))

    return str(r)

def show_moddiff(svcname):
    rows = db(db.svcmon.mon_svcname==svcname).select()
    nodes = [r.mon_nodname for r in rows]
    n = len(nodes)
    nodes.sort()

    if n < 2:
        return

    sql = """
            select t.* from
            (
             select
               count(nm.modset_node) as n,
               group_concat(nm.modset_node) as nodes,
               ms.modset_name as modset
             from
               comp_node_moduleset nm,
               svcmon m,
               comp_moduleset ms
             where
               m.mon_svcname="%(svcname)s" and
               m.mon_nodname=nm.modset_node and
               nm.modset_id=ms.id
             group by
               modset_name
             order by
               modset_name
            ) t
            where t.n != %(n)d
    """%dict(svcname=svcname, n=n)
    _rows = db.executesql(sql)

    if len(_rows) == 0:
        return

    def fmt_header1():
        return TR(
                 TH("", _colspan=1),
                 TH(T("Nodes"), _colspan=n, _style="text-align:center"),
               )

    def fmt_header2():
        h = [TH(T("Moduleset"))]
        for node in nodes:
            h.append(TH(
              node.split('.')[0],
              _style="text-align:center",
            ))
        return TR(h)

    def fmt_line(row, bg):
        h = [TD(row[2])]
        l = row[1].split(',')
        for node in nodes:
            if node in l:
                h.append(TD(
                  IMG(_src=URL(r=request,c='static',f='attach16.png')),
                  _style="text-align:center",
                ))
            else:
                h.append(TD(""))
        return TR(h, _class=bg)

    def fmt_table(rows):
        last = ""
        bgl = {'cell1': 'cell3', 'cell3': 'cell1'}
        bg = "cell1"
        lines = [fmt_header1(),
                 fmt_header2()]
        for row in rows:
            if last != row[2]:
                bg = bgl[bg]
                last = row[2]
            lines.append(fmt_line(row, bg))
        return TABLE(lines)

    return DIV(fmt_table(_rows))

#
def cron_dash_rsetdiff():
    q = db.services.updated > now - datetime.timedelta(days=2)
    svcnames = [r.svc_name for r in db(q).select(db.services.svc_name)]

    r = []
    for svcname in svcnames:
        r.append(update_dash_rsetdiff(svcname))

    return str(r)

def show_rsetdiff(svcname):
    rows = db(db.svcmon.mon_svcname==svcname).select()
    nodes = [r.mon_nodname for r in rows]
    n = len(nodes)
    nodes.sort()

    if n < 2:
        return

    sql = """
            select t.* from
            (
             select
               count(rn.nodename) as n,
               group_concat(rn.nodename) as nodes,
               rs.ruleset_name as ruleset
             from
               comp_rulesets_nodes rn,
               svcmon m,
               comp_rulesets rs
             where
               m.mon_svcname="%(svcname)s" and
               m.mon_nodname=rn.nodename and
               rn.ruleset_id=rs.id
             group by
               ruleset_name
             order by
               ruleset_name
            ) t
            where t.n != %(n)d
    """%dict(svcname=svcname, n=n)
    _rows = db.executesql(sql)

    if len(_rows) == 0:
        return

    def fmt_header1():
        return TR(
                 TH("", _colspan=1),
                 TH(T("Nodes"), _colspan=n, _style="text-align:center"),
               )

    def fmt_header2():
        h = [TH(T("Ruleset"))]
        for node in nodes:
            h.append(TH(
              node.split('.')[0],
              _style="text-align:center",
            ))
        return TR(h)

    def fmt_line(row, bg):
        h = [TD(row[2])]
        l = row[1].split(',')
        for node in nodes:
            if node in l:
                h.append(TD(
                  IMG(_src=URL(r=request,c='static',f='attach16.png')),
                  _style="text-align:center",
                ))
            else:
                h.append(TD(""))
        return TR(h, _class=bg)

    def fmt_table(rows):
        last = ""
        bgl = {'cell1': 'cell3', 'cell3': 'cell1'}
        bg = "cell1"
        lines = [fmt_header1(),
                 fmt_header2()]
        for row in rows:
            if last != row[2]:
                bg = bgl[bg]
                last = row[2]
            lines.append(fmt_line(row, bg))
        return TABLE(lines)

    return DIV(fmt_table(_rows))

def ajax_error(msg):
    return DIV(
             msg,
             _class="box",
             _style="text-align:left;padding:3em",
           )

def inputs_block(data, idx=0, defaults=None, display_mode=False, display_detailed=False, showexpert=False):
    l = []
    if display_mode and \
       len(data.get('Outputs', [])) == 1 and \
       (('Class' in data.get('Outputs', [])[0] and data.get('Outputs',[])[0]['Class'] == 'raw') or \
        ('DisplayClass' in data.get('Outputs', [])[0] and data.get('Outputs', [])[0]['DisplayClass'] == 'raw')):
        return DIV(PRE(defaults), _class="comp16")

    if display_mode and len(data.get('Outputs', [])) == 1 and \
       'Class' in data.get('Outputs', [])[0] and \
       data.get('Outputs', [])[0]['Class'] == 'dict' and \
       (len(data['Inputs']) > 1 or idx==0):
        header = TR(TD(B(data.get('Outputs', [])[0]['Class']), _class="comp16", _colspan=3))
    elif display_mode and not display_detailed and 'Format' in data.get('Outputs', [])[0] and \
         data.get('Outputs', [])[0]['Format'] in ('list of dict', 'dict of dict') and idx==0:
        h = []
        for i, input in enumerate(data['Inputs']):
            if i == 0:
                h.append(TD(input['DisplayModeLabel'], _class='comp16', _style="font-weight:bold"))
            else:
                h.append(TD(input['DisplayModeLabel']))
        header = TR(h)
    else:
        header = ""

    match_default = {}
    if defaults is not None:
        for output in data.get('Outputs', []):
            if 'Template' not in output:
                continue
            s = output['Template']
            for input in data['Inputs']:
                s = s.replace('%%'+input['Id']+'%%', '(?P<'+input['Id']+'>.*)')
            import re
            m = re.match(s, defaults)
            if m is None:
                continue
            for input in data['Inputs']:
                try:
                    match_default[input['Id']] = m.group(input['Id'])
                except:
                    match_default[input['Id']] = "unable to retrieve default"

    for i, input in enumerate(data['Inputs']):
        if type(defaults) == dict:
            default = defaults.get(input['Id'], "")
        elif defaults is not None:
            default = defaults
        elif 'Default' in input and not display_mode:
            default = input['Default']
        else:
            default = ""
        if input['Id'] in match_default:
            default = match_default[input['Id']]

        if type(default) == list:
            default = ','.join(default)

        if 'LabelCss' in input:
            lcl = input['LabelCss']
        else:
            lcl = ""
        if 'Css' in input:
            cl = input['Css']
        else:
            cl = ""

        if 'Help' in input:
            _help = IMG(
              _src=URL(r=request, c='static', f='help.png'),
              _title=input['Help']
            )
        else:
            _help = ""

        trigger_args = input.get('Args', [])
        trigger_args = map(lambda x: x.replace(' ', '').replace('=#', '--'), trigger_args)
        trigger_args = ' '.join(trigger_args)

        if display_mode:
            if default is None or default == "":
                if type(defaults) == dict:
                    default = '-'
                else:
                    continue
            if 'DisplayModeTrim' in input and not display_detailed:
                n = input['DisplayModeTrim']
                if len(default) >= n:
                    default = default[0:n//3] + "..." + default[-n//3*2:]
            if display_mode and not display_detailed and \
               data['Outputs'][0].get('Format') in ('list of dict', 'dict of dict'):
                if type(default) in (unicode, str) and len(default) > 25:
                    s = default[:10]+"..."+default[-12:]
                else:
                    s = default
                _input = SPAN(s, _title=default)
            else:
                _input = SPAN(default)
            _help = ""
        elif 'Candidates' in input:
            if input['Candidates'] == "__node_selector__":
                if 'Manager' not in user_groups():
                    q = db.nodes.team_responsible.belongs(user_groups())
                else:
                    q = db.nodes.id > 0
                o = db.nodes.project | db.nodes.nodename
                rows = db(q).select(db.nodes.project, db.nodes.nodename, orderby=o)
                candidates = [('[%s] %s' % (str(r.project if r.project is not None else ''), str(r.nodename)), r.nodename) for r in rows]
            elif input['Candidates'] == "__service_selector__":
                o = db.services.svc_app | db.services.svc_name
                q = db.services.svc_app == db.apps.app
                q &= db.services.svc_name == db.svcmon.mon_svcname
                if 'Manager' not in user_groups():
                    q &= db.apps_responsibles.app_id == db.apps.id
                    q &= db.apps_responsibles.group_id == db.auth_membership.group_id
                    q &= db.auth_membership.user_id == auth.user_id
                services = db(q).select(db.services.svc_name,
                                        db.services.svc_app,
                                        groupby=o,
                                        orderby=o)
                candidates = [('[%s] %s' % (str(r.svc_app if r.svc_app is not None else ''), str(r.svc_name)), r.svc_name) for r in services]
            else:
                candidates = input['Candidates']
                if candidates is None:
                    candidates = []

            options = []

            # first option should be empty to unset value
            if len(candidates) > 0:
                o = candidates[0]
                if type(o) in (list, tuple) and o[1] != "":
                    candidates = [('','')] + candidates
                elif o != "":
                    candidates = [''] + candidates

            max = 10
            for o in candidates:
                if type(o) in (list, tuple):
                    label, value = o
                else:
                    label = o
                    value = o

                if value == default:
                    selected = True
                else:
                    selected = False
                if 'Translate' in input and input['Translate']:
                    _label = T(label)
                else:
                    _label = label
                options.append(OPTION(_label, _value=value, _selected=selected))
                w = len(_label)
                if w > max:
                    max = w
            attr = {
              '_id': forms_xid(input['Id']+'_'+str(idx)),
              '_name': forms_xid(''),
              '_style': 'width:%(max)dem'%dict(max=max),
              '_trigger_args': trigger_args,
              '_trigger_fn': input.get('Function', ""),
              '_mandatory': input.get('Mandatory', ""),
            }
            _input = SELECT(
                       *options,
                       **attr
                     )
        elif 'Type' not in input:
            return ajax_error(T("'Type' not set for Input '%(name)s'", dict(name=input['Id'])))
        elif input['Type'] == "info":
            attr = {
              '_id': forms_xid(input['Id']+'_'+str(idx)),
              '_name': forms_xid(''),
              '_style': 'padding: 0.3em',
              '_trigger_args': trigger_args,
              '_trigger_fn': input.get('Function', ""),
            }
            _input = DIV(
                   default,
                   **attr
                 )
        elif input['Type'] == "text":
            attr = {
              '_id': forms_xid(input['Id']+'_'+str(idx)),
              '_name': forms_xid(''),
              '_trigger_args': trigger_args,
              '_trigger_fn': input.get('Function', ""),
              '_mandatory': input.get('Mandatory', ""),
            }
            _input = TEXTAREA(
                   default,
                   **attr
                 )
        elif input['Type'] == "date":
            attr = {
              '_id': forms_xid(input['Id']+'_'+str(idx)),
              '_value': default,
              '_name': forms_xid(''),
              '_class': 'date',
              '_trigger_args': trigger_args,
              '_trigger_fn': input.get('Function', ""),
              '_mandatory': input.get('Mandatory', ""),
            }
            _input = INPUT(**attr)
        elif input['Type'] == "datetime":
            attr = {
              '_id': forms_xid(input['Id']+'_'+str(idx)),
              '_value': default,
              '_name': forms_xid(''),
              '_class': 'datetime',
              '_trigger_args': trigger_args,
              '_trigger_fn': input.get('Function', ""),
              '_mandatory': input.get('Mandatory', ""),
            }
            _input = INPUT(**attr)
        elif input['Type'] == "time":
            attr = {
              '_id': forms_xid(input['Id']+'_'+str(idx)),
              '_value': default,
              '_name': forms_xid(''),
              '_class': 'time',
              '_trigger_args': trigger_args,
              '_trigger_fn': input.get('Function', ""),
              '_mandatory': input.get('Mandatory', ""),
            }
            _input = INPUT(**attr)
        else:
            attr = {
              '_id': forms_xid(input['Id']+'_'+str(idx)),
              '_name': forms_xid(''),
              '_trigger_args': trigger_args,
              '_trigger_fn': input.get('Function', ""),
              '_value': default,
              '_mandatory': input.get('Mandatory', ""),
            }
            _input = INPUT(**attr)

        if display_mode and 'DisplayModeLabel' in input:
            label = input['DisplayModeLabel']
        elif 'Label' in input:
            label = input['Label']
        else:
            label = ""

        if label == "":
            label = XML("&nbsp;")

        if display_mode and not display_detailed and \
           data['Outputs'][0].get('Format') in ('list of dict', 'dict of dict'):
            if i == 0:
                l.append(TD(_input, _class=lcl))
            else:
                l.append(TD(_input, _class=cl))
        else:
            if input.get('Hidden'):
                name = forms_xid('hidden')
                style = "display:none"
            elif input.get('Condition'):
                if display_mode and default != "-" and default != "":
                    style = ""
                else:
                    style = "display:none"
            elif input.get('ExpertMode') and not showexpert:
                name = forms_xid('expert')
                style = "display:none"
            else:
                name = ""
                style = ""
            l.append(TR(
                       TD(DIV(label, _class=lcl)),
                       TD(_input, _class=cl),
                       TD(_help),
                       TD(
                         input.get('Condition', ''),
                         _name="cond",
                         _id=forms_xid(str(idx)),
                         _style="display:none",
                       ),
                       TD(
                         input.get('Constraint', ''),
                         _name="constraint",
                         _id=forms_xid(str(idx)),
                         _style="display:none",
                       ),
                       _name=name,
                       _style=style,
                     ))

    if display_mode and not display_detailed and \
       data.get('Outputs')[0].get('Format') in ('list of dict', 'dict of dict'):
        if idx == 0:
            return [header, TR(l)]
        return [TR(l)]

    if header != "":
        l = [header] + l

    if (not display_mode or display_detailed) and \
       data.get('Outputs')[0].get('Format') in ('list of dict', 'dict of dict', 'list'):
        if not display_mode:
            remove = A(
              T("remove"),
              _onclick="""
$(this).parents("[name=instance]").first().siblings('hr').first().remove()
$(this).parents("[name=instance]").first().remove()
""",
            )
        else:
            remove = ""
        instance_counter = DIV(
          DIV(idx),
          remove,
          _class="form_instance_count",
        )
    else:
        instance_counter = ""

    return DIV(
             instance_counter,
             TABLE(l),
             SCRIPT("""
$(".date").datepicker({dateFormat: "yy-mm-dd"})
$(".datetime").datetimepicker({dateFormat: "yy-mm-dd"})
$(".time").timepicker({dateFormat: "yy-mm-dd"})
"""
             ),
             _name="instance",
           )

def ajax_forms_inputs():
    return _ajax_forms_inputs(
             _mode=request.vars.mode,
             _var_id=request.vars.var_id,
             _form_name=request.vars.form_name,
             _form_id=request.vars.form_id,
             _form_xid=request.vars.form_xid,
             _rset_name=request.vars.rset_name,
             _rset_id=request.vars.rset_id,
             _hid=request.vars.hid,
             _wfid=request.vars.wfid,
             _prev_wfid=request.vars.prev_wfid,
             showexpert=request.vars.showexpert,
           )

def _ajax_forms_inputs(_mode=None, _var_id=None, _form_name=None, _form_id=None, _form_xid=None, _rset_name=None, _rset_id=None, _hid=None, var=None, form=None, form_output=None, showexpert=False, current_values=None, _wfid=None, _prev_wfid=None):
    if _mode == "show":
        display_mode = True
        display_detailed = False
    elif _mode == "showdetailed":
        display_mode = True
        display_detailed = True
    else:
        display_mode = False
        display_detailed = False

    if var is None and _var_id is not None:
        q = db.v_comp_rulesets.id == _var_id
        var = db(q).select().first()
        if var is None:
            return ajax_error(T("variable '%(id)s' not found", dict(id=_var_id)))

    if var is not None:
        form_name = var.var_class
    else:
        form_name = _form_name

    if form is not None:
        pass
    elif form_name is not None:
        q = db.forms.form_name == form_name
        form = db(q).select().first()
    elif _form_id is not None:
        q = db.forms.id == _form_id
        form = db(q).select().first()
    elif _wfid is not None:
        q = db.forms_store.id == _wfid
        form = db(q).select().first()
    else:
        return ajax_error(T("No form specified"))

    if form is None:
        return ajax_error(T("form not found")+'\n'+var.var_value)

    form_id = form.id

    s = None
    if 'form_yaml' in form:
        s = form.form_yaml
    elif 'forms_revisions' in form:
        s = form.forms_revisions.form_yaml
    elif 'form_md5' in form:
        q = db.forms_revisions.form_md5 == form.form_md5
        row = db(q).select().first()
        if row is not None:
            s = row.form_yaml
    if s is None:
        return ajax_error(DIV(T("can't find form yaml definition"), BEAUTIFY(form)))

    import yaml
    try:
        data = yaml.load(s)
        if 'Inputs' not in data:
            raise Exception("Inputs definition not found in form definition")
        if 'Outputs' not in data or len(data['Outputs']) == 0:
            raise Exception("Outputs definition not found in form definition")
    except Exception, e:
        return ajax_error(DIV(
                 B(T("%(form)s form definition error", dict(form=form.form_name))),
                 BR(),
                 T("Please report the malfunction to %(author)s", dict(author=form.form_author)),
                 HR(),
                 PRE(str(e)),
                 HR(),
                 PRE(s),
               ))

    if form_output is None:
        form_output = data['Outputs'][0]

    # An existing variable is specified
    # Get input default values from there
    cur = None
    count = None
    if _var_id is not None:
        cur = var.var_value
        if len(cur) > 0 and form_output.get('Type') == 'json':
            try:
                cur = json.loads(cur)
            except:
                return ajax_error("json error parsing current variable value '%s'"%cur)
            if form_output.get('Format') == 'dict':
                input_ids = {}
                for i, input in enumerate(data['Inputs']):
                    input_ids[input['Id']] = i
                for key in cur:
                    if key in input_ids:
                        data['Inputs'][input_ids[key]]['Default'] = cur[key]
            elif form_output.get('Format') == 'list':
                data['Inputs'][0]['Default'] = cur
    elif 'form_data' in form:
        cur = json.loads(form.form_data)
    elif current_values is not None:
        cur = current_values

    l = []
    if form_output.get('Format') == 'dict':
        l = inputs_block(data, defaults=cur, display_mode=display_mode, showexpert=showexpert)
    elif form_output.get('Format') in ('list', 'list of dict', 'dict of dict'):
        if cur is None or len(cur) == 0:
            count = 1
            _l = inputs_block(data, display_mode=display_mode,
                              display_detailed=display_detailed,
                              showexpert=showexpert)
        else:
            count = len(cur)
            _l = []
            for i, default in enumerate(cur):
                if form_output.get('Format') == 'dict of dict':
                    d = cur[default]
                    key = form_output.get('Key')
                    if key is None or key not in d:
                        d[key] = default
                    default = d
                _l.append(inputs_block(data, idx=i, defaults=default,
                                       display_mode=display_mode,
                                       display_detailed=display_detailed,
                                       showexpert=showexpert))
                if not display_mode and i != len(cur) - 1:
                    _l.append(HR())
        if display_mode:
            l = TABLE(_l, _class="nowrap")
        else:
            l = _l
    else:
        l = inputs_block(data, defaults=cur, display_mode=display_mode, showexpert=showexpert)

    if form_output.get('Type') == 'json' and form_output.get('Format') in ('list', 'list of dict', 'dict of dict'):
        add = DIV(
                A(
                 T("Add more"),
                 _class="add16",
                 _onclick="""
ref=$(this).parents("[name=container_head]").find('[name=instance]').last()
count=$("#%(counter)s").val();
var clone = ref.clone();
ref.find("select").each(function(i) {
  var select = this;
  $(clone).find("select").eq(i).val($(select).val());
});
clone.find(".inputOverlayCreated").each(function(){
  $(this).siblings().remove()
  $(this).removeClass("inputOverlayCreated")
  $(this).combobox()
})
clone.find('input,select,textarea,[name=cond],[id^=%(xid)s]').attr('id', function(i, val) {
  try {
    i = val.lastIndexOf('_')
    return val.substring(0, i) + '_' + count;
  } catch(e) {}
  return val
});
clone.find('select').combobox()
clone.find("input[name^=%(xid)s],select[name^=%(xid)s],textarea[name^=%(xid)s]").bind('change', function(){
  form_inputs_trigger(this)
})
clone.find('.form_instance_count').children('div').text(count)
$('#%(container)s').append("<hr />")
clone.appendTo($('#%(container)s'))
count=parseInt(count)+1
$("#%(counter)s").val(count);
"""%dict(xid=forms_xid(''),
         counter=forms_xid('count'),
         expert=forms_xid('expert'),
         container=forms_xid('container'))
               ),
               INPUT(_type="hidden", _id=forms_xid('count'), _value=count)
             )
    else:
        add = ""

    def has_expert(data):
        l = [i for i in data['Inputs'] if 'ExpertMode' in i and i['ExpertMode']]
        if len(l) > 0:
            return True
        return False

    if has_expert(data):
        expert = DIV(
                A(
                 T("Expert mode"),
                 _class="expert16",
                 _onclick="""$("[name=%(expert)s]").each(function(){$(this).toggle(400)});"""%dict(expert=forms_xid('expert')),
               ),
             )
    else:
        expert = ""

    if display_mode:
        footer = ""
    else:
        submit_vars = {"form_id": form_id}
        if _form_xid is not None:
            submit_vars["form_xid"] = _form_xid
        if _rset_name is not None:
            submit_vars["rset_name"] = _rset_name
        if _rset_id is not None:
            submit_vars["rset_id"] = _rset_id
        if _var_id is not None:
            submit_vars["var_id"] = _var_id

        if _prev_wfid is not None and _prev_wfid != 'None':
            submit_vars["prev_wfid"] = _prev_wfid
            callback = """function(){window.location="%s"}"""%request.env.http_referer
        else:
            callback = "reload_ajax_custo"

        footer = SPAN(
             DIV(
               add,
               expert,
               _style="text-align:center;padding:0.3em",
             ),
             DIV(
               INPUT(
                 _type="submit",
                 _onclick="""
ids=[];
$("input[name^=%(xid)s],select[name^=%(xid)s],textarea[name^=%(xid)s]").each(function(){
  ids.push($(this).attr('id'))
});
$("#svcname").each(function(){
  ids.push("svcname")
});
$("#nodename").each(function(){
  ids.push("nodename")
});
function reload_ajax_custo(){
  $("select#svcname").change()
  $("select#nodename").change()
}
sync_ajax('%(url)s', ids, '%(rid)s', %(callback)s)
"""%dict(
                   callback=callback,
                   xid=forms_xid(''),
                   rid=forms_xid('forms_result'),
                   url=URL(r=request, c='compliance', f='ajax_form_submit', vars=submit_vars),
                 ),
                 _style="margin:1em",
               ),
             ),
             DIV(
               _id=forms_xid('forms_result'),
               _style="padding-top:2em",
             ),
             SCRIPT("""
var count=0;
$("select").combobox();

function form_inputs_trigger (o) {
  form_inputs_mandatory(o)
  form_inputs_constraints(o)
  form_inputs_conditions(o)
  form_inputs_resize(o)
  form_inputs_functions(o)
}

function refresh_select(e) {
  return function(data) {
    e.find('option').remove()
    for (i=0;i<data.length;i++) {
      e.find('option').end().append("<option value='"+data[i]+"'>"+data[i]+"</option>")
    }
    e.combobox()
  };
}

function refresh_div(e) {
  return function(data) {
    if (data instanceof Array) {
      s = data.join("\\n")
    } else {
      s = data
    }
    e.html("<pre>"+s+"</pre>")
  };
}

function form_inputs_functions (o) {
  l = $(o).attr("id").split("_")
  index = l[l.length-1]
  l.pop()
  id = l.join("_").replace("%(xid)s", "")
  $(o).parents('table').first().find("[trigger_args*=--"+id+"]").each(function(){
    l = $(this).attr("trigger_args").split(" ")
    args = []
    for (i=0; i<l.length; i++) {
      v = l[i].split("--")
      if (v.length != 2) continue
      param = v[0]
      value = v[1]
      id = "%(xid)s"+value+"_"+index
      if ($(this).get(0).tagName == 'SELECT') {
        val = $("#"+id+" option:selected").val()
      } else {
        val = $("#"+id).val()
      }
      args.push(encodeURIComponent(param)+"="+encodeURIComponent(val))
    }
    args = args.join("&")
    url = "%(url)s/call/json/"+$(this).attr("trigger_fn")+"?"+args
    if ($(this).get(0).tagName == 'SELECT') {
      $.getJSON(url, refresh_select($(this)))
    } else {
      $.getJSON(url, refresh_div($(this)))
    }
  })
}

function form_inputs_mandatory (o) {
  $(o).parents('table').first().find("[mandatory=mandatory]").each(function(){
    val = $(this).val()
    if (val == undefined || val.length == 0) {
      $(this).parents('tr').first().addClass("highlight_input")
    } else {
      $(this).parents('tr').first().removeClass("highlight_input")
    }
  })
}

function form_inputs_resize (o) {
  var max = 0
  $(o).parents('table').first().find('input,textarea,select').each(function(){
    $(this).width('auto')
    w = $(this).width()
    if (w > max) { max = w }
  })
  $(o).parents('table').first().find('input,textarea,select').width(max+'px')
}

function form_inputs_constraints (o) {
  $(o).parents('tr').first().children("[name=constraint]").each(function(){
    constraint = $(this).text()
    l = constraint.split(" ")
    if (l.length!=2) {
      return
    }
    op = l[0]
    tgt = l[1]
    val = $(this).siblings().children('input[name^=%(xid)s],select[name^=%(xid)s],textarea[name^=%(xid)s]').val()
    if (op == ">" && (1.0*val <= 1.0*tgt)) {
      $(this).parents('tr').first().addClass("highlight_input")
      $(this).show()
      return
    }
    $(this).parents('tr').first().removeClass("highlight_input")
    $(this).hide()
  })
};

function form_inputs_conditions (o) {
  $(o).parents('table').first().find("[name=cond]").each(function(){
    condition = $(this).text()
    l = $(this).attr('id').split("_")
    index = l[l.length-1]
    l.pop()
    prefix = l.join("_")
    if (condition.length==0) {
      return
    }
    ops = ["==", "!="]
    op = "not found"
    for (i=0;i<ops.length;i++) {
      l = condition.split(ops[i])
      if (l.length==2) {
        op = ops[i]
        left = $.trim(l[0])
        right = $.trim(l[1])
      }
    }
    if (op == "not found") {
      return
    }
    if (left.charAt(0) == "#"){
      left = left.substr(1);
      v_left = $('#'+prefix+"_"+left+"_"+index).val()
    } else {
      v_left = left
    }
    if (right.charAt(0) == "#"){
      right = right.substr(1);
      v_right = $('#'+prefix+"_"+right+"_"+index).val()
    } else {
      v_right = right
    }
    if (v_right == "empty") {
      v_right = ""
    }
    match = false
    if (op == "==" && v_left == v_right) { match=true }
    else if (op == "!=" && v_left != v_right) { match=true }

    if (!match) {
      $(this).siblings().children('input[name^=%(xid)s],select[name^=%(xid)s],textarea[name^=%(xid)s]').val("")
      $(this).parent('tr').hide()
      return
    }
    $(this).parent('tr').show()
  })
};

$("input[name^=%(xid)s],select[name^=%(xid)s],textarea[name^=%(xid)s]").each(function(){
  form_inputs_resize(this)
})
$("input[name^=%(xid)s],select[name^=%(xid)s],textarea[name^=%(xid)s]").bind('change', function(){
  form_inputs_trigger(this)
})
"""%dict(
     idx=len(l),
     xid=forms_xid(''),
     url=str(URL(r=request, c='forms', f='/'))[:-2],
    ),
               _name=_hid+"_to_eval",
             ),
        )

    if not display_mode and 'form_type' in form and form.form_type == 'custo' and var is None:
        header = ajax_target()
    else:
        header = ""

    return DIV(
             header,
             DIV(
               l,
               _id=forms_xid('container'),
             ),
             footer,
             _name="container_head",
           )

def forms_xid(id=None):
    xid = "forms_"
    if request.vars.form_xid is not None:
        xid += request.vars.form_xid + '_'
    if id is not None:
        xid += str(id)
    return xid

@auth.requires_login()
def ajax_target():
    l = []
    l.append(TR(
          TD(
            H2(T("Choose target to customize")),
            _colspan=4,
          ),
        ))
    l.append(TR(
          TD(
            INPUT(
              _value=False,
              _type='radio',
              _id="radio_service",
              _onclick="""
$("#radio_node").prop('checked',false);
$("#stage2").html("");
sync_ajax('%(url)s', [], '%(id)s', function(){})"""%dict(
                id="stage1",
                url=URL(r=request, c='forms', f='ajax_service_list'),
              ),
            ),
          ),
          TD(
            T("Customize service"),
          ),
          TD(
            INPUT(
              _value=False,
              _type='radio',
              _id="radio_node",
              _onclick="""
$("#radio_service").prop('checked',false);
$("#stage2").html("");
sync_ajax('%(url)s', [], '%(id)s', function(){})"""%dict(
                id="stage1",
                url=URL(r=request, c='forms', f='ajax_node_list'),
              ),
            ),
          ),
          TD(
            T("Outputs node"),
          ),
        ))
    d = DIV(
          TABLE(l),
          DIV(
            _id="stage1",
          ),
          DIV(
            _id="stage2",
            _style="padding:2em",
          ),
        )
    return d

def ajax_custo():
    """
      List all customatizations of a node or a service
       arg[0]: the type of object (svcname or nodename)
       arg[1]: the target object name (svcname or nodename)
    """
    if len(request.args) < 2:
        return ajax_error("Need two parameters")

    target = request.args[0]
    if target is None:
        return ajax_error("No target specified")

    if target == "nodename":
        rset_name = "node." + request.args[1]
    elif target == "svcname":
        rset_name = "svc." + request.args[1]
    else:
        return ajax_error("Incorrect target specified. Must be either 'nodename' or 'svcname'")

    q = db.forms.form_type == "custo"
    q &= db.forms.form_name == db.comp_rulesets_variables.var_class
    q &= db.comp_rulesets_variables.ruleset_id == db.comp_rulesets.id
    q &= db.comp_rulesets.ruleset_name == rset_name
    o = db.comp_rulesets_variables.var_class

    rows = db(q).select(orderby=o)

    l = []
    for row in rows:
        l.append(format_custo(row, target, request.args[1]))

    if len(l) == 0:
        return T("No customization yet")

    return DIV(
             l,
           )

def format_custo(row, objtype, objname):
    s = row.forms.form_yaml
    import yaml
    try:
        data = yaml.load(s)
    except:
        data = {}
    if 'Css' in data:
        cl = data['Css']
    else:
        cl = 'nologo48'

    custo = DIV(
              _ajax_forms_inputs(
                 _mode="show",
                 _rset_name=row.comp_rulesets.ruleset_name,
                 _var_id=row.comp_rulesets_variables.id,
                 _form_xid=row.comp_rulesets_variables.id,
                 _hid='stage2',
                 var=row.comp_rulesets_variables,
                 form=row.forms,
                 showexpert=True,
               ),
    )

    if 'Modulesets' in data:
        if objtype == "svcname":
            l = _comp_get_moduleset_svc_modules(data['Modulesets'], objname)
            q = db.comp_status.run_svcname == objname
        elif objtype == "nodename":
            l = _comp_get_moduleset_modules(data['Modulesets'], objname)
            q = db.comp_status.run_nodename == objname
        else:
            l = []
        q &= db.comp_status.run_module.belongs(l)
        rows = db(q).select()
        _modules = []
        for r in rows:
            val = r.run_status
            if val in img_h:
                status = IMG(
                      _src=URL(r=request,c='static',f=img_h[val]),
                    )
            else:
                status = val

            _modules.append(TR(
              TD(
                status,
                _title=r.run_log,
              ),
              TD(
                r.run_module,
                BR(),
                SPAN(
                  "(%s)" % r.run_date,
                  _style="font-size:80%;font-style:italic",
                ),
              ),
            ))

        if len(_modules) == 0:
            _modules = TR(TD(T("unknown")))

        modules = DIV(
                    BR(),
                    I(T("Status")),
                    TABLE(_modules),
                  )
    else:
        modules = ""

    since = DIV(
              BR(),
              T("Updated: %(date)s", dict(date=row.comp_rulesets_variables.var_updated)),
              BR(),
              T("Author: %(author)s", dict(author=row.comp_rulesets_variables.var_author)),
              _style="font-size:80%;font-style:italic",
            )

    return DIV(
      DIV(
        row.comp_rulesets_variables.var_class,
        HR(),
        _class=cl,
        _style="vertical-align:middle;font-weight:bold;height:48px",
      ),
      custo,
      since,
      modules,
      _style="margin:1em;display:inline-block;vertical-align:top;text-align:left;max-width:40em",
    )

def get_form_formatted_data(output, data):
    output_value = get_form_formatted_data_o(output, data)

    if output.get('Type') == "json":
        output_value = json.dumps(output_value)

    return output_value

def get_form_formatted_data_o(output, data):
    if 'Template' in output:
        output_value = output['Template']
        for input in data['Inputs']:
            val = request.vars.get(forms_xid(input['Id'])+'_0')
            if val is None:
                val = ""
            output_value = output_value.replace('%%'+input['Id']+'%%', str(val))
    elif output.get('Type') in ("json", "object"):
        if output.get('Format') == "list":
            l = []
            input = data['Inputs'][0]
            for v in request.vars.keys():
                if not v.startswith(forms_xid(input['Id'])):
                    continue
                val = request.vars.get(v)
                if len(str(val)) == 0:
                    continue
                try:
                    val = convert_val(val, input['Type'])
                except Exception, e:
                    raise Exception(T(str(e)))
                l.append(val)
            output_value = l
        elif output.get('Format') == "dict":
            h = {}
            for input in data['Inputs']:
                val = request.vars.get(forms_xid(input['Id'])+'_0')
                if val is None:
                    continue
                if len(str(val)) == 0:
                    continue
                try:
                    val = convert_val(val, input['Type'])
                except Exception, e:
                    raise Exception(T(str(e)))
                h[input['Id']] = val
            output_value = h
        elif output.get('Format') == "list of dict":
            h = {}
            for v in request.vars.keys():
                for input in data['Inputs']:
                    if not v.startswith(forms_xid(input['Id'])):
                        continue
                    idx = v.replace(forms_xid(input['Id'])+'_', '')
                    if idx not in h:
                        h[idx] = {}
                    val = request.vars.get(v)
                    if len(str(val)) == 0:
                        if 'Mandatory' in input and input['Mandatory']:
                            raise Exception(T("Input '%(input)s' is mandatory (instance %(inst)s)", dict(input=input.get('Id'), inst=idx)))
                    try:
                        val = convert_val(val, input['Type'])
                    except Exception, e:
                        raise Exception(T(str(e)))
                    h[idx][input['Id']] = val
            output_value = h.values()
        elif output.get('Format') == "dict of dict":
            h = {}
            for v in request.vars.keys():
                for input in data['Inputs']:
                    if not v.startswith(forms_xid(input['Id'])):
                        continue
                    idx = v.replace(forms_xid(input['Id'])+'_', '')
                    if idx not in h:
                        h[idx] = {}
                    val = request.vars.get(v)
                    if len(str(val)) == 0:
                        if 'Mandatory' in input and input['Mandatory']:
                            raise Exception(T("Input '%(input)s' is mandatory (instance %(inst)s)", dict(input=input.get('Id'), inst=idx)))
                        continue
                    try:
                        val = convert_val(val, input['Type'])
                    except Exception, e:
                        raise Exception(T(str(e)))
                    h[idx][input['Id']] = val
            if 'Key' not in output:
                raise Exception(T("'Key' must be defined in form Output of 'dict of dict' format"))
            k = output['Key']
            _h = {}
            for idx, d in h.items():
                if k not in d:
                    continue
                _k = d[k]
                if not output.get('EmbedKey', True):
                    del(d[k])
                _h[_k] = d
            output_value = _h
        else:
            raise Exception(T("Unknown output format: %(fmt)s", dict(fmt=output.get('Format', 'none'))))
    else:
        raise Exception(T("Output must have a Template or Type must be json."))

    return output_value

@auth.requires_login()
def ajax_form_submit():
    q = db.forms.id == request.vars.form_id
    form = db(q).select().first()
    s = form.form_yaml
    import yaml
    try:
        data = yaml.load(s)
    except Exception, e:
        return ajax_error(DIV(
                 B(T("%(form)s form definition error"),
                     dict(form=form.form_name)),
                 BR(),
                 T("Please report the malfunction to %(author)s",
                   dict(author=form.form_author)),
                 HR(),
                 PRE(str(e)),
                 HR(),
                 PRE(s),
               ))

    return ajax_generic_form_submit(form, data)

def insert_form_md5(form):
    o = md5()
    o.update(form.form_yaml)
    form_md5 = str(o.hexdigest())

    q = db.forms_revisions.form_md5 == form_md5
    if db(q).select().first() is not None:
        return form_md5

    db.forms_revisions.insert(
      form_id=form.id,
      form_yaml=form.form_yaml,
      form_folder=form.form_folder,
      form_name=form.form_name,
      form_md5=form_md5
    )
    return form_md5

def ajax_generic_form_submit(form, data):
    log = []
    for output in data.get('Outputs', []):
        dest = output.get('Dest')
        if dest == "db":
            output['Type'] = 'object'
            output['Format'] = 'dict'
            try:
                d = get_form_formatted_data(output, data)
            except Exception, e:
                log.append(("form.submit", str(e), dict()))
                break
            if 'Table' not in output:
                log.append(("form.submit", "Table must be set in db type Output", dict()))
                continue
            table = output['Table']
            if table not in db:
                log.append(("form.submit", "Table %(t)s not found", dict(t=table)))
                continue
            try:
                db[table].insert(**d)
                log.append(("form.submit", "Data inserted in database table", dict()))
            except Exception, e:
                log.append(("form.submit", "Data insertion in database table error: %(err)s", dict(err=str(e))))
        elif dest == "script":
            import os
            import subprocess
            try:
                d = get_form_formatted_data(output, data)
            except Exception, e:
                log.append(("form.submit", str(e), dict()))
                break
            path = output.get('Path')
            if path is None:
                log.append(("form.submit", "Path must be set in script type Output", dict()))
                continue
            if not os.path.exists(path):
                log.append(("form.submit", "Script %(path)s does not exists", dict(path=path)))
                continue
            p = subprocess.Popen([path, d], stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
            out, err = p.communicate()
            if p.returncode != 0:
                log.append(("form.submit", "Script %(path)s returned with error: %(err)s", dict(path=path, err=err)))
                continue
            log.append(("form.submit", "script %(path)s returned on success: %(out)s", dict(path=path, out=out)))
        elif dest == "mail":
            to = output.get('To', set([]))
            if len(to) == 0:
                continue
            label = data.get('Label', form.form_name)
            title = T("form submission: %(n)s", dict(n=label))
            try:
                d = get_form_formatted_data_o(output, data)
            except Exception, e:
                log.append(("form.submit", str(e), dict()))
                break
            message = str(XML(BODY(
              P(T("Form submitted on %(date)s by %(submitter)s", dict(date=str(datetime.datetime.now()), submitter=user_name()))),
              _ajax_forms_inputs(
                 _mode="showdetailed",
                 form=form,
                 form_output=output,
                 showexpert=True,
                 current_values=d,
               ),
            )))
            mail.send(to=to,
                      subject=title,
                      message='<html>%s</html>'%message)
            log.append(("form.submit", "Mail sent to %(to)s on form %(form_name)s submission." , dict(to=', '.join(to), form_name=form.form_name)))
        elif dest == "workflow":
            try:
                d = get_form_formatted_data(output, data)
            except Exception, e:
                log.append(("form.submit", str(e), dict()))
                break
            form_md5 = insert_form_md5(form)

            if len(output.get('NextForms', [])) == 0:
                next_id = 0
                status = "closed"
            else:
                next_id = None
                status = "pending"

            now = datetime.datetime.now()

            if request.vars.prev_wfid is not None and request.vars.prev_wfid != 'None':
                # workflow continuation
                q = db.forms_store.id == request.vars.prev_wfid
                prev_wf = db(q).select().first()
                if prev_wf.form_next_id is not None:
                    log.append(("form.store",  "This step is already completed (id=%(id)d)", dict(id=prev_wf.id)))
                    continue

                form_assignee = output.get('NextAssignee')
                if form_assignee is None:
                    form_assignee = user_primary_group()
                    if form_assignee is None:
                        form_assignee = prev_wf.form_submitter
                if form_assignee is None:
                    form_assignee = ""

                head_id = int(request.vars.prev_wfid)
                max_iter = 100
                iter = 0
                while iter < max_iter:
                    iter += 1
                    q = db.forms_store.id == head_id
                    row = db(q).select().first()
                    if row is None:
                        break
                    if row.form_prev_id is None:
                        head = row
                        break
                    head_id = row.form_prev_id

                record_id = db.forms_store.insert(
                  form_md5=form_md5,
                  form_submitter=user_name(),
                  form_assignee=form_assignee,
                  form_submit_date=now,
                  form_prev_id=request.vars.prev_wfid,
                  form_next_id=next_id,
                  form_head_id=head_id,
                  form_data=d,
                )
                if record_id is not None:
                    q = db.forms_store.id == request.vars.prev_wfid
                    db(q).update(form_next_id=record_id)
                if next_id != 0:
                    log.append(("form.store", "Workflow %(head_id)d step %(form_name)s added with id %(id)d", dict(form_name=form.form_name, head_id=head_id, id=record_id)))
                else:
                    log.append(("form.store", "Workflow %(head_id)d closed on last step %(form_name)s with id %(id)d", dict(form_name=form.form_name, head_id=head_id, id=record_id)))
                q = db.workflows.form_head_id == head_id
                wfrow = db(q).select().first()
                if wfrow is None:
                    # should not happen ... recreate the workflow
                    db.workflows.insert(
                      status=status,
                      form_md5=form_md5,
                      steps=iter+1,
                      last_assignee=form_assignee,
                      last_update=now,
                      form_head_id=head_id,
                      creator=head.form_submitter,
                      create_date=head.form_submit_date,
                    )
                else:
                    db(q).update(
                      status=status,
                      steps=iter+1,
                      last_assignee=form_assignee,
                      last_update=now,
                    )
            else:
                # new workflow
                record_id = db.forms_store.insert(
                  form_md5=form_md5,
                  form_submitter=user_name(),
                  form_assignee=output.get('NextAssignee', ''),
                  form_submit_date=datetime.datetime.now(),
                  form_data=d,
                )
                if record_id is not None:
                    q = db.forms_store.id == record_id
                    db(q).update(form_head_id=record_id)
                log.append(("form.store", "New workflow %(form_name)s created with id %(id)d", dict(form_name=form.form_name, id=record_id)))

                db.workflows.insert(
                  status=status,
                  form_md5=form_md5,
                  steps=1,
                  last_assignee=output.get('NextAssignee', ''),
                  last_update=now,
                  form_head_id=record_id,
                  creator=user_name(),
                  create_date=now,
                )

        elif dest == "compliance variable":
            log += ajax_custo_form_submit(output, data)

    for action, fmt, d in log:
        _log(action, fmt, d)

    return ajax_error(PRE(XML('<br><br>'.join(map(lambda x: x[1]%x[2], log)))))

def ajax_custo_form_submit(output, data):
    rset_name = request.vars.rset_name
    if request.vars.svcname is not None:
        rset_name = "svc."+request.vars.svcname
    elif request.vars.nodename is not None:
        rset_name = "node."+request.vars.nodename

    if rset_name is None:
        raise Exception(T("No ruleset name specified"))

    if request.vars.var_id is not None:
        q = db.comp_rulesets_variables.id == request.vars.var_id
        var = db(q).select().first()
        if var is None:
            raise Exception(T("Specified variable not found (id=%(id)s)", dict(id=request.vars.var_id)))
        var_name = var.var_name
        var_class = var.var_class

    # logging buffer
    log = []

    # validate privs
    groups = []
    common_groups = []
    if request.vars.nodename is not None:
        q = db.nodes.nodename == request.vars.nodename
        q &= db.nodes.team_responsible == db.auth_group.role
        node = db(q).select(db.auth_group.id).first()
        if node is None:
            raise Exception(T("Unknown specified node %(nodename)s", dict(nodename=nodename)))
        groups = [node.id]
        if len(groups) == 0:
            raise Exception(T("Specified node %(nodename)s has no responsible group", dict(nodename=nodename)))
        common_groups = set(user_group_ids()) & set(groups)
        if len(common_groups) == 0:
            raise Exception(T("You are not allowed to create or modify a ruleset for the node %(node)s", dict(nodename=nodename)))
    elif request.vars.svcname is not None:
        q = db.services.svc_name == request.vars.svcname
        svc = db(q).select().first()
        if svc is None:
            raise Exception(T("Unknown specified service %(svcname)s", dict(svcname=svcname)))
        q &= db.services.svc_app == db.apps.app
        q &= db.apps.id == db.apps_responsibles.app_id
        rows = db(q).select()
        groups = map(lambda x: x.apps_responsibles.group_id, rows)
        if len(groups) == 0:
            raise Exception(T("Specified service %(svcname)s has no responsible groups", dict(svcname=svcname)))
        common_groups = set(user_group_ids()) & set(groups)
        if len(common_groups) == 0:
            raise Exception(T("You are not allowed to create or modify a ruleset for the service %(svcname)s", dict(svcname=svcname)))

    # create ruleset
    q = db.comp_rulesets.ruleset_name == rset_name
    rset = db(q).select().first()
    if rset is None:
        db.comp_rulesets.insert(ruleset_name=rset_name,
                                ruleset_type="explicit",
                                ruleset_public="T")
        log.append(("compliance.ruleset.add", "Added explicit published ruleset '%(rset_name)s'", dict(rset_name=rset_name)))
        rset = db(q).select().first()
        for gid in common_groups:
            db.comp_ruleset_team_responsible.insert(
              ruleset_id=rset.id,
              group_id=gid
            )
            log.append(("compliance.ruleset.group.attach", "Added group %(gid)d ruleset '%(rset_name)s' owners", dict(gid=gid, rset_name=rset_name)))
    if rset is None:
        raise Exception(T("error fetching %(rset_name)s ruleset", dict(rset_name=rset_name)))

    if request.vars.var_id is None:
        if 'Class' in output:
            var_class = output['Class']
        else:
            var_class = 'raw'

        if request.vars.var_name is not None:
            var_name_prefix = request.vars.var_name
        elif 'Prefix' in output:
            var_name_prefix = output['Prefix']
        else:
            raise Exception(T("No variable name specified."))

        q = db.comp_rulesets_variables.ruleset_id == rset.id
        q &= db.comp_rulesets_variables.var_name.like(var_name_prefix+'%')
        var_name_suffixes = map(lambda x: x.var_name.replace(var_name_prefix, ''), db(q).select())
        i = 0
        while True:
            _i = str(i)
            if _i not in var_name_suffixes: break
            i += 1
        var_name = var_name_prefix + _i

    try:
        var_value = get_form_formatted_data(output, data)
    except Exception, e:
        log.append(("compliance.ruleset.variable.change", str(e), dict()))
        return log

    q = db.comp_rulesets_variables.ruleset_id == rset.id
    q &= db.comp_rulesets_variables.var_name == var_name
    n = db(q).count()

    if n == 0 and request.vars.var_id is not None:
        log.append(("compliance.ruleset.variable.change", "%(var_class)s' variable '%(var_name)s' does not exist in ruleset %(rset_name)s or invalid attempt to edit a variable in a parent ruleset", dict(var_class=var_class, var_name=var_name, rset_name=rset_name)))
        return log

    q &= db.comp_rulesets_variables.var_value == var_value
    n = db(q).count()

    if n > 0:
        log.append(("compliance.ruleset.variable.add", "'%(var_class)s' variable '%(var_name)s' already exists with the same value in the ruleset '%(rset_name)s': cancel", dict(var_class=var_class, var_name=var_name, rset_name=rset_name)))
    else:
        q = db.comp_rulesets_variables.ruleset_id == rset.id
        q &= db.comp_rulesets_variables.var_name == var_name
        n = db(q).count()
        if n == 0:
            db.comp_rulesets_variables.insert(
              ruleset_id=rset.id,
              var_name=var_name,
              var_value=var_value,
              var_class=var_class,
              var_author=user_name(),
              var_updated=datetime.datetime.now(),
            )
            log.append(("compliance.ruleset.variable.add", "Added '%(var_class)s' variable '%(var_name)s' to ruleset '%(rset_name)s' with value:\n%(var_value)s", dict(var_class=var_class, var_name=var_name, rset_name=rset_name, var_value=var_value)))
        else:
            db(q).update(
              var_value=var_value,
              var_class=var_class,
              var_author=user_name(),
              var_updated=datetime.datetime.now(),
            )
            log.append(("compliance.ruleset.variable.change", "Modified '%(var_class)s' variable '%(var_name)s' in ruleset '%(rset_name)s' with value:\n%(var_value)s", dict(var_class=var_class, var_name=var_name, rset_name=rset_name, var_value=var_value)))

    if request.vars.nodename is not None or request.vars.svcname is not None:
        modset_ids = []
        if 'Modulesets' in data:
            q = db.comp_moduleset.modset_name.belongs(data['Modulesets'])
            rows = db(q).select(db.comp_moduleset.id)
            modset_ids = map(lambda x: x.id, rows)

        rset_ids = []
        if 'Rulesets' in data:
            q = db.comp_rulesets.ruleset_name.belongs(data['Rulesets'])
            q &= db.comp_rulesets.ruleset_type == "explicit"
            q &= db.comp_rulesets.ruleset_public == True
            rows = db(q).select(db.comp_rulesets.id)
            rset_ids = map(lambda x: x.id, rows) + [rset.id]

        if request.vars.nodename is not None:
            # check node_team_responsible_id ?
            try:
                comp_attach_modulesets(node_names=[request.vars.nodename],
                                       modset_ids=modset_ids)
            except ToolError:
                pass
            try:
                comp_attach_rulesets(node_names=[request.vars.nodename],
                                     ruleset_ids=rset_ids)
            except ToolError:
                pass

        if request.vars.svcname is not None:
            # check svc_team_responsible_id ?
            try:
                log += comp_attach_svc_modulesets(svc_names=[request.vars.svcname],
                                                  modset_ids=modset_ids,
                                                  slave=True)
            except ToolError:
                pass
            try:
                log += comp_attach_svc_rulesets(svc_names=[request.vars.svcname],
                                                ruleset_ids=rset_ids,
                                                slave=True)
            except ToolError:
                pass

    return log

def convert_val(val, t):
     if t == 'string':
         val = str(val)
     elif t == 'text':
         val = str(val)
     elif t == 'string or integer':
         try:
             val = int(val)
         except:
             val = str(val)
     elif t == 'integer':
         try:
             val = int(val)
         except:
             raise Exception("Error converting to integer")
     elif t == "list of string":
         l = val.split(',')
         val = map(lambda x: x.strip(), l)
     elif t == "size":
         val = val.strip()
         if len(val) < 2:
             raise Exception("Error converting size. Too short.")
         i = 0
         while val[i].isdigit():
             i += 1
             continue
         unit = val[i:]
         try:
             val = int(val[0:i])
         except:
             raise Exception("Error converting size. Error converting to integer")
         if unit in ("K", "k", "KB"):
             val = val * 1024
         elif unit == "Kib":
             val = val * 1000
         elif unit in ("M", "m", "MB"):
             val = val * 1024 * 1024
         elif unit == "Pib":
             val = val * 1000 * 1000
         elif unit in ("G", "g", "GB"):
             val = val * 1024 * 1024 * 1024
         elif unit == "Gib":
             val = val * 1000 * 1000 * 1000
         elif unit in ("P", "p", "PB"):
             val = val * 1024 * 1024 * 1024 * 1024 
         elif unit == "Pib":
             val = val * 1000 * 1000 * 1000 * 1000
         else:
             raise Exception("Error converting size. Unknown unit.")
     return val

def forms_xid(id=None):
    xid = "forms_"
    if request.vars.form_xid is not None:
        xid += request.vars.form_xid + '_'
    if id is not None:
        xid += str(id)
    return xid

