from hashlib import md5
import datetime
import json
import copy
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
    'apps':dict(name='apps', title='apps', cl='svc', hide=False),
    'node_hba':dict(name='node_hba', title='node host bus adapaters', cl='node16', hide=False),
    'b_disk_app':dict(name='b_disk_app', title='disks', cl='hd16', hide=False),
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
props.update(node_hba_colprops)
props.update(disk_app_colprops)
props.update(apps_colprops)
fields = {
    'nodes': db.nodes.fields,
    'services': db.services.fields,
    'svcmon': db.svcmon.fields,
    'b_disk_app': db.b_disk_app.fields,
    'node_hba': db.node_hba.fields,
    'apps': set(db.apps.fields) - set(['updated', 'id']),
}

import re
# ex: \x1b[37;44m\x1b[1mContact List\x1b[0m\n
regex = re.compile("\x1b\[([0-9]{1,3}(;[0-9]{1,3})*)?[m|K|G]", re.UNICODE)

def strip_unprintable(s):
    return regex.sub('', s)

#
# custom column formatting
#
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
                 _onclick="toggle_extra('%(url)s', '%(id)s', this, 0);"%dict(
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
                 _onclick="toggle_extra('%(url)s', '%(id)s', this, 0);"%dict(
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
                 _onclick="toggle_extra('%(url)s', '%(id)s', this, 0);"%dict(
                          url=URL(
                                r=request,
                                c='compliance',
                                f='ajax_mod_history',
                                vars={'modname': self.t.colprops['mod_name'].get(o), 'rowid': id}
                              ),
                          id=id,
                            ),
               )


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
        rows = db(q).select(cacheable=True)
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

        encap_rset_id = self.t.colprops['encap_rset_id'].get(o)
        if encap_rset_id is not None and encap_rset_id != "":
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
class table_comp_rulesets_services(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['svc_name', 'encap', 'rulesets'] + v_services_cols
        self.colprops = v_services_colprops
        self.colprops['rulesets'] = col_run_ruleset(
                     title='Rule set',
                     field='rulesets',
                     img='action16',
                     display=True,
                    )
        self.colprops['encap'] = HtmlTableColumn(
                     title='Encap',
                     field='encap',
                     img='svc',
                     display=True,
                    )
        self.colprops['svc_name'].t = self
        self.colprops['svc_name'].display = True
        for c in self.cols:
            self.colprops[c].table = 'v_comp_services'
        self.span = ['svc_name']
        self.key = ['svc_name']
        self.checkboxes = True
        self.checkbox_id_table = 'v_comp_services'
        self += HtmlTableMenu('Ruleset', 'comp16', ['ruleset_attach', 'ruleset_detach'], id='menu_ruleset2')
        self.ajax_col_values = 'ajax_comp_rulesets_services_col_values'
        self.dataable = True

    def line_id(self, o):
        if o is None:
            return ""
        return '_'.join((str(o.id), str(o.encap)))

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
        self.colprops['nodename'].t = self
        self.colprops['nodename'].display = True
        for c in self.cols:
            self.colprops[c].table = 'v_comp_nodes'
        self.force_cols = ['os_name']
        self.span = ['nodename']
        self.key = ['nodename']
        self.checkboxes = True
        self.checkbox_id_table = 'v_comp_nodes'
        self += HtmlTableMenu('Ruleset', 'comp16', ['ruleset_attach', 'ruleset_detach'], id='menu_ruleset2')
        self.ajax_col_values = 'ajax_comp_rulesets_nodes_col_values'
        self.dataable = True

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
        self.cols = ['id', 'ruleset_name', 'variables']
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
            'variables': HtmlTableColumn(
                     title='Variables',
                     field='variables',
                     table='v_comp_explicit_rulesets',
                     display=True,
                     img='action16',
                     _class='rsetvars',
                    ),
        }
        self.span = ['id']
        self.key = ['id']
        self.checkboxes = True
        self.dbfilterable = False
        self.exportable = False
        self.ajax_col_values = 'ajax_comp_explicit_rules_col_values'
        self.checkbox_id_table = 'v_comp_explicit_rulesets'
        self.dataable = True

@auth.requires_login()
def ajax_comp_explicit_rules_col_values():
    t = table_comp_explicit_rules('crn1', 'ajax_comp_rulesets_nodes',
                                  innerhtml='crn1')
    col = request.args[0]
    o = db.v_comp_explicit_rulesets[col]
    q = db.v_comp_explicit_rulesets.id > 0
    for f in t.cols:
        q = _where(q, 'v_comp_explicit_rulesets', t.filter_parse_glob(f), f)
    q = apply_gen_filters(q, t.tables())
    t.object_list = db(q).select(o, orderby=o, cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_comp_rulesets_services_col_values():
    r = table_comp_explicit_rules('crs1', 'ajax_comp_explicit_rules')
    t = table_comp_rulesets_services('crs2', 'ajax_comp_rulesets_services')
    t.rulesets = r
    col = request.args[0]
    o = db.v_comp_services[col]
    q = _where(None, 'v_comp_services', domain_perms(), 'svc_name')
    for f in t.cols:
        q = _where(q, 'v_comp_services', t.filter_parse_glob(f), f)
    t.object_list = db(q).select(o, orderby=o, cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_comp_rulesets_nodes_col_values():
    r = table_comp_explicit_rules('crn1', 'ajax_comp_explicit_rules')
    t = table_comp_rulesets_nodes('crn2', 'ajax_comp_rulesets_nodes')
    t.rulesets = r
    col = request.args[0]
    o = db.v_comp_nodes[col]
    q = _where(None, 'v_comp_nodes', domain_perms(), 'nodename')
    for f in t.cols:
        q = _where(q, 'v_comp_nodes', t.filter_parse_glob(f), f)
    t.object_list = db(q).select(o, orderby=o, cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_comp_explicit_rules():
    r = table_comp_explicit_rules('crn1', 'ajax_comp_explicit_rules')

    o = db.v_comp_explicit_rulesets.ruleset_name
    q = db.v_comp_explicit_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    for f in r.cols:
        q = _where(q, 'v_comp_explicit_rulesets', r.filter_parse_glob(f), f)

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        r.setup_pager(n)
        cols = r.get_visible_columns()
        r.object_list = db(q).select(*cols, limitby=(r.pager_start,r.pager_end),
                                     orderby=o, groupby=o, cacheable=True)
        return r.table_lines_data(n, html=False)
    if len(request.args) == 1 and request.args[0] == 'csv':
        r.csv_q = q
        r.csv_orderby = o
        r.csv_groupby = o
        return r.csv()

@auth.requires_login()
def ajax_comp_rulesets_services():
    r = table_comp_explicit_rules('crs1', 'ajax_comp_explicit_rules')
    t = table_comp_rulesets_services('crs2', 'ajax_comp_rulesets_services')
    t.rulesets = r

    if len(request.args) == 1 and request.args[0] == 'attach_ruleset':
        l = t.get_checked()
        d = {'True': [] , 'False': []}
        for s in l:
            _id, _encap = s.split("_")
            d[_encap].append(_id)
        if len(d['True']) > 0:
            comp_attach_svc_rulesets(d['True'], r.get_checked(), slave=True)
        if len(d['False']) > 0:
            comp_attach_svc_rulesets(d['False'], r.get_checked(), slave=False)
    elif len(request.args) == 1 and request.args[0] == 'detach_ruleset':
        l = t.get_checked()
        d = {'True': [] , 'False': []}
        for s in l:
            _id, _encap = s.split("_")
            d[_encap].append(_id)
        if len(d['True']) > 0:
            comp_detach_svc_rulesets(d['True'], r.get_checked(), slave=True)
        if len(d['False']) > 0:
            comp_detach_svc_rulesets(d['False'], r.get_checked(), slave=False)

    o = db.v_comp_services.svc_name|db.v_comp_services.encap
    q = _where(None, 'v_comp_services', domain_perms(), 'svc_name')
    for f in t.cols:
        q = _where(q, 'v_comp_services', t.filter_parse_glob(f), f)
    q = apply_gen_filters(q, t.tables())

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        t.setup_pager(n)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, limitby=(t.pager_start,t.pager_end),
                                     orderby=o, cacheable=True)
        return t.table_lines_data(n, html=False)

    if len(request.args) == 1 and request.args[0] == 'csv':
        return t.csv()

@auth.requires_login()
def ajax_comp_rulesets_nodes():
    r = table_comp_explicit_rules('crn1', 'ajax_comp_explicit_rules')
    t = table_comp_rulesets_nodes('crn2', 'ajax_comp_rulesets_nodes')
    t.rulesets = r

    if len(request.args) == 1 and request.args[0] == 'attach_ruleset':
        comp_attach_rulesets(t.get_checked(), r.get_checked())
    elif len(request.args) == 1 and request.args[0] == 'detach_ruleset':
        comp_detach_rulesets(t.get_checked(), r.get_checked())

    o = db.v_comp_nodes.nodename
    q = _where(None, 'v_comp_nodes', domain_perms(), 'nodename')
    if 'Manager' not in user_groups():
        q &= db.v_comp_nodes.team_responsible.belongs(user_groups())
    for f in t.cols:
        q = _where(q, 'v_comp_nodes', t.filter_parse_glob(f), f)
    q = apply_gen_filters(q, t.tables())

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        t.setup_pager(n)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, limitby=(t.pager_start,t.pager_end),
                                     orderby=o, cacheable=True)
        return t.table_lines_data(n, html=False)

    if len(request.args) == 1 and request.args[0] == 'csv':
        return t.csv()

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
                     'chain',
                     'chain_len',
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
            'chain_len': HtmlTableColumn(
                     title='Chain length',
                     field='chain_len',
                     table='v_comp_rulesets',
                     display=False,
                     img='action16',
                    ),
            'chain': HtmlTableColumn(
                     title='Chain',
                     field='chain',
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
        self.span = ['ruleset_name', 'ruleset_type', 'ruleset_public',
                     'fset_name', 'teams_responsible']
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
                                                        'ruleset_detach'])
        self.ajax_col_values = 'ajax_comp_rulesets_col_values'
        self.dbfilterable = False

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
            options = [OPTION(g.ruleset_name,_value=g.id) for g in db(q).select(orderby=o, cacheable=True)]
        else:
            q = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
            q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
            options = [OPTION(g.comp_rulesets.ruleset_name,_value=g.comp_rulesets.id) for g in db(q).select(orderby=o, cacheable=True)]
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
        options += [OPTION(g.auth_group.role,_value=g.auth_group.id) for g in db(q).select(cacheable=True)]
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
                            groupby=db.comp_rulesets_rulesets.parent_rset_id,
                            cacheable=True)
        parent_rset_ids = [r.parent_rset_id for r in rows]
        q = ~db.comp_rulesets.id.belongs(parent_rset_ids)
        q &= db.comp_rulesets.id.belongs(allowed.select(db.comp_rulesets.id, cacheable=True))
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
                    db.comp_rulesets.id, "%(ruleset_name)s", zero=T('choose one'), groupby=db.comp_rulesets.id)

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
        table_modified("comp_ruleset_team_responsible")
    if len(done) == 0:
        return
    rows = db(db.comp_rulesets.id.belongs(done)).select(db.comp_rulesets.ruleset_name, cacheable=True)
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
        parent_rset_name = db(q).select(cacheable=True).first().ruleset_name

        q = db.comp_rulesets.id == child_rset_id
        child_rset_name = db(q).select(cacheable=True).first().ruleset_name

        q = db.comp_rulesets_rulesets.parent_rset_id == parent_rset_id
        q &= db.comp_rulesets_rulesets.child_rset_id == child_rset_id
        db(q).delete()
        table_modified("comp_rulesets_rulesets")

        done.append((parent_rset_name, child_rset_name))
    if len(done) == 0:
        return

    comp_rulesets_chains()

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
        table_modified("comp_ruleset_team_responsible")
    if len(done) == 0:
        return
    rows = db(db.comp_rulesets.id.belongs(done)).select(db.comp_rulesets.ruleset_name, cacheable=True)
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
    rows = db(q).select(cacheable=True)
    if len(rows) == 0:
        raise ToolError("change ruleset publication failed: can't find ruleset")

    x = ', '.join(['from %s on %s'%(r.ruleset_public,r.ruleset_name) for r in rows])
    db(q).update(ruleset_public=sid)

    # purge attachments
    if sid == "F":
        q = db.comp_rulesets_nodes.ruleset_id.belongs(ids)
        db(q).delete()
        table_modified("comp_rulesets_nodes")
        q = db.comp_rulesets_services.ruleset_id.belongs(ids)
        db(q).delete()
        table_modified("comp_rulesets_services")

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
    rows = db(q).select(cacheable=True)
    if len(rows) == 0:
        raise ToolError("change ruleset type failed: can't find ruleset")

    x = ', '.join(['from %s on %s'%(r.ruleset_type,r.ruleset_name) for r in rows])
    db(q).update(ruleset_type=sid)

    # purge attachments
    if sid == "contextual":
        q = db.comp_rulesets_nodes.ruleset_id.belongs(ids)
        db(q).delete()
        table_modified("comp_rulesets_nodes")
        q = db.comp_rulesets_services.ruleset_id.belongs(ids)
        db(q).delete()
        table_modified("comp_rulesets_services")
    elif sid == "explicit":
        q = db.comp_rulesets_filtersets.ruleset_id.belongs(ids)
        db(q).delete()
        table_modified("comp_rulesets_filtersets")

    _log('compliance.ruleset.type.change',
         'changed ruleset type to %(s)s %(x)s',
         dict(s=sid, x=x))

@auth.requires_membership('CompManager')
def ruleset_clone():
    sid = request.vars.rset_clone_s
    iid = request.vars.rset_clone_i
    if len(iid) == 0:
        raise ToolError("clone ruleset failed: invalid target name")
    if len(db(db.comp_rulesets.ruleset_name==iid).select(cacheable=True)) > 0:
        raise ToolError("clone ruleset failed: target name already exists")
    q = db.comp_rulesets.id == sid
    rows = db(q).select(cacheable=True)
    if len(rows) == 0:
        raise ToolError("clone ruleset failed: can't find source ruleset (id %s)"%sid)
    orig = rows[0].ruleset_name
    newid = db.comp_rulesets.insert(ruleset_name=iid,
                                    ruleset_type=rows[0].ruleset_type)

    # clone filterset for contextual rulesets
    if rows[0].ruleset_type == 'contextual':
        q = db.comp_rulesets.id == sid
        q &= db.comp_rulesets.id == db.comp_rulesets_filtersets.ruleset_id
        rows = db(q).select(cacheable=True)
        if len(rows) > 0 and  rows[0].comp_rulesets_filtersets.fset_id is not None:
            db.comp_rulesets_filtersets.insert(ruleset_id=newid,
                                               fset_id=rows[0].comp_rulesets_filtersets.fset_id)
            table_modified("comp_rulesets_filtersets")

    # clone ruleset variables
    q = db.comp_rulesets_variables.ruleset_id == sid
    rows = db(q).select(cacheable=True)
    for row in rows:
        db.comp_rulesets_variables.insert(ruleset_id=newid,
                                          var_name=row.var_name,
                                          var_class=row.var_class,
                                          var_value=row.var_value,
                                          var_author=user_name())
    table_modified("comp_rulesets_variables")
    add_default_team_responsible(iid)

    # clone parent to children relations
    q = db.comp_rulesets_rulesets.parent_rset_id==sid
    rows = db(q).select(cacheable=True)
    for child_rset_id in [r.child_rset_id for r in rows]:
        db.comp_rulesets_rulesets.insert(parent_rset_id=newid,
                                         child_rset_id=child_rset_id)

    table_modified("comp_rulesets_rulesets")
    comp_rulesets_chains()

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
    if len(db(db.comp_rulesets.ruleset_name==new).select(cacheable=True)) > 0:
        raise ToolError("rename ruleset failed: new ruleset name already exists")
    ids = map(lambda x: int(x.split('_')[0]), ids)
    id = ids[0]
    rows = db(db.comp_rulesets.id == id).select(db.comp_rulesets.ruleset_name, cacheable=True)
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
        rows = db(q).select(groupby=db.comp_ruleset_team_responsible.ruleset_id, cacheable=True)
        ids = [r.ruleset_id for r in rows]
        if len(ids) == 0:
            raise ToolError("delete ruleset failed: no ruleset deletion allowed")
    rows = db(db.comp_rulesets.id.belongs(ids)).select(db.comp_rulesets.ruleset_name, cacheable=True)
    x = ', '.join([str(r.ruleset_name) for r in rows])
    n = db(db.comp_ruleset_team_responsible.ruleset_id.belongs(ids)).delete()
    table_modified("comp_ruleset_team_responsible")
    n = db(db.comp_rulesets_filtersets.ruleset_id.belongs(ids)).delete()
    table_modified("comp_rulesets_filtersets")
    n = db(db.comp_rulesets_variables.ruleset_id.belongs(ids)).delete()
    table_modified("comp_rulesets_variables")
    n = db(db.comp_rulesets.id.belongs(ids)).delete()
    table_modified("comp_rulesets")
    n = db(db.comp_rulesets_nodes.ruleset_id.belongs(ids)).delete()
    table_modified("comp_rulesets_nodes")
    n = db(db.comp_rulesets_services.ruleset_id.belongs(ids)).delete()
    table_modified("comp_rulesets_services")
    comp_rulesets_chains()
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
    rows = db(q).select(cacheable=True)
    x = map(lambda r: ' '.join((
                       r.var_name+'.'+r.var_value,
                       'from ruleset',
                       r.ruleset_name)), rows)
    x = ', '.join(set(x))
    n = db(db.comp_rulesets_variables.id.belongs(ids)).delete()
    table_modified("comp_rulesets_variables")
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
    rows = db(q).select(cacheable=True)
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
    table_modified("comp_rulesets_filtersets")
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
        rows = db(q).select(db.v_nodes.nodename, cacheable=True)
        node_names += [r.nodename for r in rows]

    nodes = ', '.join(node_names)

    for rsid in ruleset_ids:
        for node in node_names:
            q = db.comp_rulesets_nodes.nodename == node
            q &= db.comp_rulesets_nodes.ruleset_id == rsid
            db(q).delete()
    table_modified("comp_rulesets_nodes")

    for node in node_names:
        update_dash_rsetdiff_node(node)

    q = db.comp_rulesets.id.belongs(ruleset_ids)
    rows = db(q).select(db.comp_rulesets.ruleset_name, cacheable=True)
    rulesets = ', '.join([r.ruleset_name for r in rows])
    _log('compliance.ruleset.node.detach',
         'detached rulesets %(rulesets)s from nodes %(nodes)s',
         dict(rulesets=rulesets, nodes=nodes))

@auth.requires_membership('CompManager')
def comp_attach_rulesets(node_ids=[], ruleset_ids=[], node_names=[]):
    return internal_comp_attach_rulesets(node_ids, ruleset_ids, node_names)

def internal_comp_attach_rulesets(node_ids=[], ruleset_ids=[], node_names=[]):
    if len(node_ids) + len(node_names) == 0:
        raise ToolError("attach ruleset failed: no node selected")
    if len(ruleset_ids) == 0:
        raise ToolError("attach ruleset failed: no ruleset selected")

    log = []

    if len(node_ids) > 0:
        q = db.v_nodes.id.belongs(node_ids)
        rows = db(q).select(db.v_nodes.nodename, cacheable=True)
        node_names += [r.nodename for r in rows]

    nodes = ', '.join(node_names)

    for rsid in ruleset_ids:
        for node in node_names:
            q = db.comp_rulesets_nodes.nodename == node
            q &= db.comp_rulesets_nodes.ruleset_id == rsid
            if db(q).count() == 0:
                db.comp_rulesets_nodes.insert(nodename=node,
                                            ruleset_id=rsid)
    table_modified("comp_rulesets_nodes")

    for node in node_names:
        update_dash_rsetdiff_node(node)

    q = db.comp_rulesets.id.belongs(ruleset_ids)
    rows = db(q).select(db.comp_rulesets.ruleset_name, cacheable=True)
    rulesets = ', '.join([r.ruleset_name for r in rows])

    log.append([
      0,
      'compliance.ruleset.node.attach',
      'attached rulesets %(rulesets)s to nodes %(nodes)s',
      dict(rulesets=rulesets, nodes=nodes)
    ])

    for ret, action, fmt, d in log:
        _log(action, fmt, d)

    return log

@auth.requires_membership('CompManager')
def comp_detach_svc_modulesets(svc_ids=[], modset_ids=[], svc_names=[], slave=True):
    return internal_comp_detach_svc_modulesets(svc_ids, modset_ids, svc_names, slave)

@auth.requires_membership('CompManager')
def comp_attach_svc_modulesets(svc_ids=[], modset_ids=[], svc_names=[], slave=True):
    return internal_comp_attach_svc_modulesets(svc_ids, modset_ids, svc_names, slave)

def internal_comp_detach_svc_modulesets(svc_ids=[], modset_ids=[], svc_names=[], slave=True):
    if len(svc_ids) + len(svc_names) == 0:
        raise ToolError("detach moduleset failed: no service selected")
    if len(modset_ids) == 0:
        raise ToolError("detach moduleset failed: no moduleset selected")

    log = []

    if len(svc_ids) > 0:
        q = db.services.id.belongs(svc_ids)
        rows = db(q).select(db.services.svc_name, cacheable=True)
        svc_names += [r.svc_name for r in rows]

    # init modset name cache
    modset_names = get_modset_names(modset_ids)

    for modset_id in modset_ids:
        for svc in svc_names:
            sl = slave
            if slave and not has_slave(svc):
                sl = False
            q = db.comp_modulesets_services.modset_svcname == svc
            q &= db.comp_modulesets_services.modset_id == modset_id
            q &= db.comp_modulesets_services.slave == sl
            row = db(q).select(cacheable=True).first()
            if row is None:
                log.append([
                  0,
                  'compliance.moduleset.service.detach',
                  'moduleset %(moduleset)s already detached from service %(service)s (slave=%(slave)s)',
                  dict(moduleset=modset_names[modset_id], service=svc, slave=str(slave)),
                ])
                continue
            db(q).delete()
            log.append([
              0,
              'compliance.moduleset.service.detach',
              'moduleset %(moduleset)s detached from service %(service)s (slave=%(slave)s)',
              dict(moduleset=modset_names[modset_id], service=svc, slave=str(slave)),
            ])

    table_modified("comp_modulesets_services")

    for ret, action, fmt, d in log:
        _log(action, fmt, d)

    for svc in svc_names:
        update_dash_moddiff(svc)

    return log

def internal_comp_attach_svc_modulesets(svc_ids=[], modset_ids=[], svc_names=[], slave=True):
    if len(svc_ids) + len(svc_names) == 0:
        raise ToolError("attach moduleset failed: no service selected")
    if len(modset_ids) == 0:
        raise ToolError("attach moduleset failed: no moduleset selected")

    log = []

    if len(svc_ids) > 0:
        q = db.services.id.belongs(svc_ids)
        rows = db(q).select(db.services.svc_name, cacheable=True)
        svc_names += [r.svc_name for r in rows]

    # init modset name cache
    modset_names = get_modset_names(modset_ids)

    for modset_id in modset_ids:
        for svc in svc_names:
            sl = slave
            if slave and not has_slave(svc):
                sl = False
            q = db.comp_modulesets_services.modset_svcname == svc
            q &= db.comp_modulesets_services.modset_id == modset_id
            q &= db.comp_modulesets_services.slave == sl
            row = db(q).select(cacheable=True).first()
            if row is not None:
                log.append([
                  0,
                  'compliance.moduleset.service.attach',
                  'moduleset %(moduleset)s already attached to service %(service)s (slave=%(slave)s)',
                  dict(moduleset=modset_names[modset_id], service=svc, slave=str(slave)),
                ])
                continue
            db.comp_modulesets_services.insert(modset_svcname=svc,
                                               slave=sl,
                                               modset_id=modset_id)
            log.append([
              0,
              'compliance.moduleset.service.attach',
              'moduleset %(moduleset)s attached to service %(service)s (slave=%(slave)s)',
              dict(moduleset=modset_names[modset_id], service=svc, slave=str(slave)),
            ])

    table_modified("comp_modulesets_services")

    for ret, action, fmt, d in log:
        _log(action, fmt, d)

    for svc in svc_names:
        update_dash_moddiff(svc)

    return log

@auth.requires_membership('CompManager')
def comp_detach_svc_rulesets(svc_ids=[], ruleset_ids=[], svc_names=[], slave=True):
    return internal_comp_detach_svc_rulesets(svc_ids, ruleset_ids, svc_names, slave)

@auth.requires_membership('CompManager')
def comp_attach_svc_rulesets(svc_ids=[], ruleset_ids=[], svc_names=[], slave=True):
    return internal_comp_attach_svc_rulesets(svc_ids, ruleset_ids, svc_names, slave)

def get_rset_names(ruleset_ids=None):
    if ruleset_ids is None:
        q = db.comp_rulesets.id > 0
    elif type(ruleset_ids) == int:
        q = db.comp_rulesets.id = ruleset_ids
    elif type(ruleset_ids) == list:
        q = db.comp_rulesets.id.belongs(ruleset_ids)
    else:
        return {}
    rows = db(q).select(cacheable=True)
    rset_names = {}
    for row in rows:
        rset_names[row.id] = row.ruleset_name
    return rset_names

def internal_comp_detach_svc_rulesets(svc_ids=[], ruleset_ids=[], svc_names=[], slave=True):
    if len(svc_ids) + len(svc_names) == 0:
        raise ToolError("detach ruleset failed: no service selected")
    if len(ruleset_ids) == 0:
        raise ToolError("detach ruleset failed: no ruleset selected")

    log = []

    if len(svc_ids) > 0:
        q = db.services.id.belongs(svc_ids)
        rows = db(q).select(db.services.svc_name, cacheable=True)
        svc_names += [r.svc_name for r in rows]

    # init rset name cache
    rset_names = get_rset_names(ruleset_ids)

    for rsid in ruleset_ids:
        for svc in svc_names:
            sl = slave
            if slave and not has_slave(svc):
                sl = False
            q = db.comp_rulesets_services.svcname == svc
            q &= db.comp_rulesets_services.ruleset_id == rsid
            q &= db.comp_rulesets_services.slave == sl
            row = db(q).select(cacheable=True).first()
            if row is None:
                log.append([
                  0,
                  'compliance.ruleset.service.detach',
                  'ruleset %(ruleset)s already detached from service %(service)s (slave=%(slave)s)',
                  dict(ruleset=rset_names[rsid], service=svc, slave=str(slave)),
                ])
                continue
            db(q).delete()
            log.append([
              0,
              'compliance.ruleset.service.detach',
              'ruleset %(ruleset)s detached from service %(service)s (slave=%(slave)s)',
              dict(ruleset=rset_names[rsid], service=svc, slave=str(slave)),
            ])

    table_modified("comp_rulesets_services")

    for ret, action, fmt, d in log:
        _log(action, fmt, d)

    for svc in svc_names:
        update_dash_rsetdiff(svc)

    return log

def internal_comp_attach_svc_rulesets(svc_ids=[], ruleset_ids=[], svc_names=[], slave=True):
    if len(svc_ids) + len(svc_names) == 0:
        raise ToolError("attach ruleset failed: no service selected")
    if len(ruleset_ids) == 0:
        raise ToolError("attach ruleset failed: no ruleset selected")

    log = []

    if len(svc_ids) > 0:
        q = db.services.id.belongs(svc_ids)
        rows = db(q).select(db.services.svc_name, cacheable=True)
        svc_names += [r.svc_name for r in rows]

    # init rset name cache
    rset_names = get_rset_names(ruleset_ids)

    for rsid in ruleset_ids:
        for svc in svc_names:
            sl = slave
            if slave and not has_slave(svc):
                sl = False
            q = db.comp_rulesets_services.svcname == svc
            q &= db.comp_rulesets_services.ruleset_id == rsid
            q &= db.comp_rulesets_services.slave == sl
            row = db(q).select(cacheable=True).first()
            if row is not None:
                log.append([
                  0,
                  'compliance.ruleset.service.attach',
                  'ruleset %(ruleset)s already attached to service %(service)s (slave=%(slave)s)',
                  dict(ruleset=rset_names[rsid], service=svc, slave=str(slave)),
                ])
                continue
            db.comp_rulesets_services.insert(svcname=svc,
                                             slave=sl,
                                             ruleset_id=rsid)
            log.append([
              0,
              'compliance.ruleset.service.attach',
              'ruleset %(ruleset)s attached to service %(service)s (slave=%(slave)s)',
              dict(ruleset=rset_names[rsid], service=svc, slave=str(slave)),
            ])

    table_modified("comp_rulesets_services")

    for ret, action, fmt, d in log:
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
    t.object_list = db(q).select(o, orderby=o, cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_comp_rulesets():
    v = table_comp_rulesets('cr0', 'ajax_comp_rulesets')
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
            comp_rulesets_chains()
            _log('compliance.ruleset.ruleset.attach',
                 'attach ruleset %(child)s to %(parent)s',
                 dict(parent=db(db.comp_rulesets.id==request.vars.parent_rset_id).select(cacheable=True).first().ruleset_name,
                      child=db(db.comp_rulesets.id==request.vars.child_rset_id).select(cacheable=True).first().ruleset_name))
        elif v.form_ruleset_attach.errors:
            response.flash = T("errors in form")

        if v.form_ruleset_add.accepts(request.vars, formname='add_ruleset'):
            comp_rulesets_chains()
            # refresh forms ruleset comboboxes
            v.form_ruleset_attach = v.comp_ruleset_attach_sqlform()
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
            rows = db(q).select(groupby=g, cacheable=True)
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
            ruleset = db(db.comp_rulesets.id==request.vars.ruleset_id).select(db.comp_rulesets.ruleset_name, cacheable=True)[0].ruleset_name
            _log('compliance.ruleset.variable.add',
                 'added ruleset variable %(var)s to ruleset %(ruleset)s',
                 dict(var=var, ruleset=ruleset))
        elif v.form_ruleset_var_add.errors:
            response.flash = T("errors in form")
    except AttributeError:
        pass
    except ToolError, e:
        v.flash = str(e)

    o = db.v_comp_rulesets.ruleset_name|db.v_comp_rulesets.chain_len|db.v_comp_rulesets.encap_rset|db.v_comp_rulesets.var_name
    g = db.v_comp_rulesets.ruleset_id|db.v_comp_rulesets.id
    q = teams_responsible_filter()
    for f in v.cols:
        q = _where(q, 'v_comp_rulesets', v.filter_parse(f), f)

    v.csv_q = q
    v.csv_orderby = o
    v.csv_groupby = o

    if len(request.args) == 1 and request.args[0] == 'csv':
        return v.csv()
    if len(request.args) == 1 and request.args[0] == 'line':
        if request.vars.volatile_filters is None:
            n = db(q).count()
            limitby = (v.pager_start,v.pager_end)
        else:
            n = 0
            limitby = (0, 500)
        v.object_list = db(q).select(orderby=o, limitby=limitby, cacheable=False)
        return v.table_lines_data(n)

    n = db(q).count()
    v.setup_pager(n)
    v.object_list = db(q).select(limitby=(v.pager_start,v.pager_end), orderby=o, groupby=g, cacheable=True)

    return v.html()

def add_default_team_responsible(ruleset_name):
    q = db.comp_rulesets.ruleset_name == ruleset_name
    ruleset_id = db(q).select(cacheable=True)[0].id
    q = db.auth_membership.user_id == auth.user_id
    q &= db.auth_membership.group_id == db.auth_group.id
    q &= db.auth_group.role.like('user_%')
    try:
        group_id = db(q).select(cacheable=True)[0].auth_group.id
    except:
        q = db.auth_group.role == 'Manager'
        group_id = db(q).select(cacheable=True)[0].id
    db.comp_ruleset_team_responsible.insert(ruleset_id=ruleset_id, group_id=group_id)
    table_modified("comp_ruleset_team_responsible")

def add_default_team_responsible_to_filterset(name):
    q = db.gen_filtersets.fset_name == name
    fset_id = db(q).select(cacheable=True)[0].id
    q = db.auth_membership.user_id == auth.user_id
    q &= db.auth_membership.group_id == db.auth_group.id
    q &= db.auth_group.role.like('user_%')
    try:
        group_id = db(q).select(cacheable=True)[0].auth_group.id
    except:
        q = db.auth_group.role == 'Manager'
        group_id = db(q).select(cacheable=True)[0].id
    db.gen_filterset_team_responsible.insert(fset_id=fset_id, group_id=group_id)
    table_modified("gen_filterset_team_responsible")

def add_default_team_responsible_to_modset(modset_name):
    q = db.comp_moduleset.modset_name == modset_name
    modset_id = db(q).select(cacheable=True)[0].id
    q = db.auth_membership.user_id == auth.user_id
    q &= db.auth_membership.group_id == db.auth_group.id
    q &= db.auth_group.role.like('user_%')
    try:
        group_id = db(q).select(cacheable=True)[0].auth_group.id
    except:
        q = db.auth_group.role == 'Manager'
        group_id = db(q).select(cacheable=True)[0].id
    db.comp_moduleset_team_responsible.insert(modset_id=modset_id, group_id=group_id)
    table_modified("comp_moduleset_team_responsible")

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
def comp_rulesets_services_attachment():
    r = table_comp_explicit_rules('crs1', 'ajax_comp_explicit_rules')
    t = table_comp_rulesets_services('crs2', 'ajax_comp_rulesets_services')
    t.rulesets = r
    t.checkbox_names.append(r.id+'_ck')
    t = DIV(
             DIV(
               t.html(),
               _style="""min-width:60%;
                         max-width:60%;
                         float:left;
                         border-right:0px solid;
                      """,
               _id='crs2',
             ),
             DIV(
               r.html(),
               _style="""min-width:40%;
                         max-width:40%;
                         float:left;
                      """,
               _id='crs1',
             ),
             DIV(XML('&nbsp;'), _class='spacer'),
             SCRIPT("""
             function calign() {
              $("#crs1").find("div.theader").css({height: $("#crs2").find("div.theader").height()})
              $("#crs1").find("tr.theader").css({height: $("#crs2").find("tr.theader").height()})
             }
             osvc.tables["crs2"].on_change = calign
             osvc.tables["crs1"].on_change = calign
             """),
           )
    return dict(table=t)

@auth.requires_login()
def comp_rulesets_nodes_attachment():
    r = table_comp_explicit_rules('crn1', 'ajax_comp_explicit_rules')
    t = table_comp_rulesets_nodes('crn2', 'ajax_comp_rulesets_nodes')
    t.rulesets = r
    t.checkbox_names.append(r.id+'_ck')
    t = DIV(
             DIV(
               t.html(),
               _style="""min-width:60%;
                         max-width:60%;
                         float:left;
                         border-right:0px solid;
                      """,
               _id='crn2',
             ),
             DIV(
               r.html(),
               _style="""min-width:40%;
                         max-width:40%;
                         float:left;
                      """,
               _id='crn1',
             ),
             DIV(XML('&nbsp;'), _class='spacer'),
             SCRIPT("""
             function calign() {
              $("#crn1").find("div.theader").css({height: $("#crn2").find("div.theader").height()})
              $("#crn1").find("tr.theader").css({height: $("#crn2").find("tr.theader").height()})
             }
             osvc.tables["crn2"].on_change = calign
             osvc.tables["crn1"].on_change = calign
             """),
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

class col_fset_stats(HtmlTableColumn):
    def html(self, o):
        val = self.get(o)
        if val is None:
            return SPAN()
        return T(str(val))

class table_comp_filtersets(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['fset_name',
                     'fset_stats',
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
            'fset_stats': col_fset_stats(
                     title='Compute stats',
                     field='fset_stats',
                     display=True,
                     img='spark16',
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
        self.span = ['fset_name']
        self.keys = ['fset_name', 'encap_fset_name'] + filters_cols
        if 'CompManager' in user_groups():
            self.form_encap_filterset_attach = self.comp_encap_filterset_attach_sqlform()
            self.form_filterset_add = self.comp_filterset_add_sqlform()
            self.form_filter_attach = self.comp_filter_attach_sqlform()
            self += HtmlTableMenu('Filter', 'filters', ['filter_attach', 'filter_detach'])
            self += HtmlTableMenu('Filterset', 'filters', ['filterset_add',
                                                           'filterset_del',
                                                           'filterset_rename',
                                                           'encap_filterset_attach',
                                                           'filter_detach',
                                                           'filterset_change_stats'])
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

    def filterset_change_stats(self):
        label = 'Change filterset stats flag'
        action = 'filterset_change_stats'
        divid = 'fset_stats_change'
        sid = 'fset_stats_change_s'
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
                    TH(T('Compute filterset stats')),
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
                        _onclick=self.ajax_submit(additional_inputs=[sid], args=action),
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
def filterset_change_stats(ids):
    sid = request.vars.fset_stats_change_s
    if len(sid) == 0:
        raise ToolError("change filterset stats flag failed: target flag is empty")
    if len(ids) == 0:
        raise ToolError("change filterset stats flag failed: no filterset selected")
    ids = map(lambda x: int(x.split('_')[0]), ids)

    q = db.gen_filtersets.id.belongs(ids)
    rows = db(q).select(cacheable=True)
    if len(rows) == 0:
        raise ToolError("change filterset stats flag failed: can't find filterset")

    x = ', '.join(['from %s on %s'%(r.fset_stats,r.fset_name) for r in rows])
    db(q).update(fset_stats=sid)

    _log('filterset.stats.change',
         'changed filterset stats flag to %(s)s %(x)s',
         dict(s=sid, x=x))

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
    rows = db(q).select(cacheable=True)
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
    table_modified("gen_filtersets_filters")
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
    table_modified("gen_filtersets_filters")

    # purge ruleset joins
    q = db.comp_rulesets_filtersets.fset_id.belongs(ids)
    n = db(q).delete()
    table_modified("comp_rulesets_filtersets")

    # delete filtersets
    q = db.gen_filtersets.id.belongs(ids)
    rows = db(q).select(cacheable=True)
    if len(rows) == 0:
        raise ToolError("delete filterset failed: can't find selected filtersets")
    fset_names = ', '.join([r.fset_name for r in rows])
    n = db(q).delete()
    table_modified("gen_filtersets")
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
    if len(db(db.gen_filtersets.fset_name==new).select(cacheable=True)) > 0:
        raise ToolError("rename filterset failed: new filterset name already exists")
    ids = map(lambda x: int(x.split('_')[0]), ids)
    id = ids[0]
    rows = db(db.gen_filtersets.id == id).select(db.gen_filtersets.fset_name, cacheable=True)
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
        self.keys = ["f_table", "f_field", "f_op", "f_value"]
        self.span = ["f_table", "f_field"]
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
        table_modified("gen_filters")
    except:
        raise ToolError("add filter failed: already exist ?")

    f_name = ' '.join([f_table+'.'+f_field, f_op, f_value])
    _log('compliance.filter.add', 'added filter %(f_name)s',
         dict(f_name=f_name))

@auth.requires_membership('CompManager')
def comp_delete_filtersets_filters(ids, f_names):
    q = db.gen_filtersets_filters.f_id.belongs(ids)
    rows = db(q).select(cacheable=True)
    if len(rows) == 0:
        return
    fset_ids = [r.fset_id for r in rows]
    q2 = db.gen_filtersets.id.belongs(fset_ids)
    fset_names = ', '.join([r.fset_name for r in db(q2).select(cacheable=True)])
    n = db(q).delete()
    table_modified("gen_filtersets")
    _log('compliance.filter.delete',
         'deleted filter %(f_names)s membership in filtersets %(fset_names)s',
         dict(f_names=f_names, fset_names=fset_names))


@auth.requires_membership('CompManager')
def comp_delete_filter(ids=[]):
    if len(ids) == 0:
        raise ToolError("delete filter failed: no filter selected")

    q = db.gen_filters.id.belongs(ids)
    rows = db(q).select(cacheable=True)
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
    table_modified("gen_filters")
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
    t.object_list = db(q).select(o, orderby=o, cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_comp_filters():
    extra = SPAN()
    v = table_comp_filters('ajax_comp_filters',
                           'ajax_comp_filters')
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

    if len(request.args) == 1 and request.args[0] == 'line':
        if request.vars.volatile_filters is None:
            n = db(q).count()
            limitby = (v.pager_start,v.pager_end)
        else:
            n = 0
            limitby = (0, 500)
        v.object_list = db(q).select(orderby=o, limitby=limitby, cacheable=False)
        return v.table_lines_data(n)

    n = db(q).count()
    v.setup_pager(n)
    v.object_list = db(q).select(limitby=(v.pager_start,v.pager_end), orderby=o, cacheable=True)

    return SPAN(v.html(),extra)

@auth.requires_login()
def ajax_comp_filtersets_col_values():
    t = table_comp_filtersets('ajax_comp_filtersets', 'ajax_comp_filtersets')
    col = request.args[0]
    o = db.v_gen_filtersets[col]
    q = db.v_gen_filtersets.fset_id > 0
    for f in t.cols:
        q = _where(q, 'v_gen_filtersets', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_comp_filtersets():
    t = table_comp_filtersets('ajax_comp_filtersets',
                              'ajax_comp_filtersets')
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
            elif action == 'filterset_change_stats':
                filterset_change_stats(t.get_checked())
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
            f = db(q).select(cacheable=True)[0]
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
            f = db(q).select(cacheable=True)[0]
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

    if len(request.args) == 1 and request.args[0] == 'line':
        if request.vars.volatile_filters is None:
            n = db(q).count()
            limitby = (t.pager_start,t.pager_end)
        else:
            n = 0
            limitby = (0, 500)
        t.object_list = db(q).select(orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n)

    n = db(q).count()
    t.setup_pager(n)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end), orderby=o, cacheable=True)

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
                     'autofix',
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
            'autofix': HtmlTableColumn(
                     title='Autofix',
                     table='comp_moduleset_modules',
                     field='autofix',
                     display=True,
                     img='actionred16',
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
                                                            'moduleset_rename'])
            self += HtmlTableMenu('Team responsible', 'guys16', ['team_responsible_attach', 'team_responsible_detach'])
        self.span = ['modset_name', 'teams_responsible']

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
                                                distinct=True,
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
    table_modified("comp_moduleset_modules")
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
    table_modified("comp_moduleset_modules")
    n = db(db.comp_node_moduleset.id.belongs(ids)).delete()
    table_modified("comp_node_moduleset")
    n = db(db.comp_moduleset.id.belongs(ids)).delete()
    table_modified("comp_moduleset")
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
        table_modified("comp_moduleset_modules")
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
    table_modified("comp_moduleset_team_responsible")
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
    table_modified("comp_moduleset_team_responsible")
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
    o = db[t.colprops[col].table][col]

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
                                 left=(l1,l2,l3)
                                 )
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_comp_moduleset():
    t = table_comp_moduleset('ajax_comp_moduleset', 'ajax_comp_moduleset')
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

    o = db.comp_moduleset.modset_name|db.comp_moduleset_modules.modset_mod_name
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

    if len(request.args) == 1 and request.args[0] == 'line':
        if request.vars.volatile_filters is None:

            n = len(db(q).select(db.comp_moduleset_modules.id, left=(l1,l2,l3), groupby=g))
            limitby = (t.pager_start,t.pager_end)
        else:
            n = 0
            limitby = (0, 500)
        t.object_list = db(q).select(
          db.comp_moduleset_modules.ALL,
          db.comp_moduleset.modset_name,
          db.comp_moduleset.id,
          db.v_comp_moduleset_teams_responsible.teams_responsible,
          orderby=o,
          limitby=limitby,
          cacheable=False,
          left=(l1,l2,l3),
          groupby=g
        )
        return t.table_lines_data(n)

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
    table_modified("comp_moduleset_team_responsible")

class table_comp_moduleset_short(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id', 'modset_name']
        self.colprops = {
            'id': HtmlTableColumn(
                     title='Moduleset Id',
                     table='comp_moduleset',
                     field='id',
                     display=False,
                     img='action16',
                    ),
            'modset_name': HtmlTableColumn(
                     title='Moduleset',
                     table='comp_moduleset',
                     field='modset_name',
                     display=True,
                     img='action16',
                    ),
        }
        self.span = ['id']
        self.key = ['id']
        self.checkboxes = True
        self.dbfilterable = False
        self.exportable = False
        self.columnable = False
        self.dataable = True
        self.checkbox_id_table = 'comp_moduleset'
        self.ajax_col_values = 'ajax_comp_modulesets_short_col_values'

class table_comp_modulesets_services(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['svc_name', 'encap', 'modulesets'] + v_services_cols
        self.colprops = v_services_colprops
        self.colprops['modulesets'] = HtmlTableColumn(
                     title='Module set',
                     field='modulesets',
                     img='comp16',
                     display=True,
                    )
        self.colprops['encap'] = HtmlTableColumn(
                     title='Encap',
                     field='encap',
                     img='comp16',
                     display=True,
                    )
        self.colprops['svc_name'].t = self
        self.colprops['svc_name'].display = True
        for c in self.cols:
            self.colprops[c].table = 'v_comp_services'
        self.span = ['svc_name']
        self.key = ['svc_name']
        self.checkbox_id_table = 'v_comp_services'
        self.dataable = True
        self.checkboxes = True
        self.dbfilterable = False
        self += HtmlTableMenu('Moduleset', 'action16', ['moduleset_attach', 'moduleset_detach'], id='menu_moduleset2')
        self.ajax_col_values = 'ajax_comp_modulesets_services_col_values'

    def line_id(self, o):
        if o is None:
            return ""
        return '_'.join((str(o.id), str(o.encap)))

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
        for c in self.cols:
            self.colprops[c].table = 'v_comp_nodes'
        self.force_cols = ['os_name']
        self.span = ['nodename']
        self.key = ['nodename']
        self.checkbox_id_table = 'v_comp_nodes'
        self.dataable = True
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
    table_modified("comp_node_moduleset")
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
    return internal_comp_attach_modulesets(node_ids, modset_ids, node_names)

def internal_comp_attach_modulesets(node_ids=[], modset_ids=[], node_names=[]):
    if len(node_ids+node_names) == 0:
        raise ToolError("attach modulesets failed: no node selected")
    if len(modset_ids) == 0:
        raise ToolError("attach modulesets failed: no moduleset selected")

    log = []

    if len(node_ids) > 0:
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
    table_modified("comp_node_moduleset")
    for node in node_names:
        update_dash_moddiff_node(node)

    q = db.comp_moduleset.id.belongs(modset_ids)
    rows = db(q).select(db.comp_moduleset.modset_name)
    modulesets = ', '.join([r.modset_name for r in rows])

    log.append([
      0,
      'compliance.moduleset.node.attach',
      'attached modulesets %(modulesets)s to nodes %(nodes)s',
      dict(modulesets=modulesets, nodes=nodes)
    ])

    for ret, action, fmt, d in log:
        _log(action, fmt, d)

    return log

@auth.requires_login()
def ajax_comp_modulesets_short_col_values():
    r = table_comp_moduleset_short('cmn1', 'ajax_comp_modulesets_nodes')
    t = table_comp_modulesets_nodes('cmn2', 'ajax_comp_modulesets_nodes')
    t.modulesets = r
    col = request.args[0]
    o = db.comp_moduleset[col]
    q = db.comp_moduleset.id > 0
    if 'Manager' not in user_groups():
        q &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    for f in r.cols:
        q = _where(q, 'comp_moduleset', r.filter_parse_glob(f), f)
    q = apply_gen_filters(q, r.tables())
    r.object_list = db(q).select(o, orderby=o)
    return r.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_comp_modulesets_services_col_values():
    r = table_comp_moduleset_short('cms1', 'ajax_comp_modulesets_services')
    t = table_comp_modulesets_services('cms2', 'ajax_comp_modulesets_services')
    t.modulesets = r
    col = request.args[0]
    o = db.v_comp_services[col]
    q = _where(None, 'v_comp_services', domain_perms(), 'svc_name')
    if 'Manager' not in user_groups():
        q &= db.v_comp_services.team_responsible.belongs(user_groups())
    for f in t.cols:
        q = _where(q, 'v_comp_services', t.filter_parse_glob(f), f)
    q = apply_gen_filters(q, t.tables())
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_comp_modulesets_nodes_col_values():
    r = table_comp_moduleset_short('cmn1', 'ajax_comp_modulesets_nodes')
    t = table_comp_modulesets_nodes('cmn2', 'ajax_comp_modulesets_nodes')
    t.modulesets = r
    col = request.args[0]
    o = db.v_comp_nodes[col]
    q = _where(None, 'v_comp_nodes', domain_perms(), 'nodename')
    if 'Manager' not in user_groups():
        q &= db.v_comp_nodes.team_responsible.belongs(user_groups())
    for f in t.cols:
        q = _where(q, 'v_comp_nodes', t.filter_parse_glob(f), f)
    q = apply_gen_filters(q, t.tables())
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_comp_modulesets_services():
    r = table_comp_moduleset_short('cms1', 'ajax_comp_modulesets_short')
    t = table_comp_modulesets_services('cms2', 'ajax_comp_modulesets_services')
    t.modulesets = r

    if len(request.args) == 1 and request.args[0] == 'attach_moduleset':
        l = t.get_checked()
        d = {'True': [] , 'False': []}
        for s in l:
            _id, _encap = s.split("_")
            d[_encap].append(_id)
        if len(d['True']) > 0:
            comp_attach_svc_modulesets(d['True'], r.get_checked(), slave=True)
        if len(d['False']) > 0:
            comp_attach_svc_modulesets(d['False'], r.get_checked(), slave=False)
    elif len(request.args) == 1 and request.args[0] == 'detach_moduleset':
        l = t.get_checked()
        d = {'True': [] , 'False': []}
        for s in l:
            _id, _encap = s.split("_")
            d[_encap].append(_id)
        if len(d['True']) > 0:
            comp_detach_svc_modulesets(d['True'], r.get_checked(), slave=True)
        if len(d['False']) > 0:
            comp_detach_svc_modulesets(d['False'], r.get_checked(), slave=False)

    o = db.v_comp_services.svc_name
    q = _where(None, 'v_comp_services', domain_perms(), 'svc_name')
    if 'Manager' not in user_groups():
        q &= db.v_comp_services.team_responsible.belongs(user_groups())
    for f in t.cols:
        q = _where(q, 'v_comp_services', t.filter_parse_glob(f), f)
    q = apply_gen_filters(q, t.tables())

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        t.setup_pager(n)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, limitby=(t.pager_start,t.pager_end), orderby=o)
        return t.table_lines_data(n, html=False)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_o = o
        return t.csv()

@auth.requires_login()
def ajax_comp_modulesets_nodes():
    r = table_comp_moduleset_short('cmn1', 'ajax_comp_modulesets_short')
    t = table_comp_modulesets_nodes('cmn2', 'ajax_comp_modulesets_nodes')
    t.modulesets = r

    if len(request.args) == 1 and request.args[0] == 'attach_moduleset':
        comp_attach_modulesets(t.get_checked(), r.get_checked())
    elif len(request.args) == 1 and request.args[0] == 'detach_moduleset':
        comp_detach_modulesets(t.get_checked(), r.get_checked())

    o = db.v_comp_nodes.nodename
    q = _where(None, 'v_comp_nodes', domain_perms(), 'nodename')
    if 'Manager' not in user_groups():
        q &= db.v_comp_nodes.team_responsible.belongs(user_groups())
    for f in t.cols:
        q = _where(q, 'v_comp_nodes', t.filter_parse_glob(f), f)
    q = apply_gen_filters(q, t.tables())

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        t.setup_pager(n)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, limitby=(t.pager_start,t.pager_end), orderby=o)
        return t.table_lines_data(n, html=False)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_o = o
        return t.csv()

@auth.requires_login()
def ajax_comp_modulesets_short():
    r = table_comp_moduleset_short('cmn1', 'ajax_comp_modulesets_short')
    t = table_comp_modulesets_nodes('cmn2', 'ajax_comp_modulesets_nodes')
    t.modulesets = r

    o = db.comp_moduleset.modset_name
    j = db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    l = db.comp_moduleset_team_responsible.on(j)
    q = db.comp_moduleset.id > 0
    if 'Manager' not in user_groups():
        q &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    for f in r.cols:
        q = _where(q, 'comp_moduleset', r.filter_parse_glob(f), f)

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        r.setup_pager(n)
        r.object_list = db(q).select(limitby=(r.pager_start,r.pager_end), orderby=o, groupby=o, left=l)
        return r.table_lines_data(n, html=False)

    if len(request.args) == 1 and request.args[0] == 'csv':
        r.csv_q = q
        r.csv_o = o
        r.csv_left = l
        return r.csv()

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
def comp_modulesets_services():
    r = table_comp_moduleset_short('cms1', 'ajax_comp_modulesets_short')
    t = table_comp_modulesets_services('cms2', 'ajax_comp_modulesets_services')
    t.modulesets = r
    t.checkbox_names.append(r.id+'_ck')
    t = DIV(
             DIV(
               t.html(),
               _style="""min-width:60%;
                         max-width:60%;
                         float:left;
                         border-right:0px solid;
                      """,
               _id='cms2',
             ),
             DIV(
               r.html(),
               _style="""min-width:40%;
                         max-width:40%;
                         float:left;
                      """,
               _id='cms1',
             ),
             DIV(XML('&nbsp;'), _class='spacer'),
             SCRIPT("""
             function calign() {
              $("#cms1").find("div.theader").css({height: $("#cms2").find("div.theader").height()})
              $("#cms1").find("tr.theader").css({height: $("#cms2").find("tr.theader").height()})
             }
             osvc.tables["cms2"].on_change = calign
             osvc.tables["cms1"].on_change = calign
             """),
           )
    return dict(table=t)

@auth.requires_login()
def comp_modulesets_nodes():
    r = table_comp_moduleset_short('cmn1', 'ajax_comp_modulesets_short')
    t = table_comp_modulesets_nodes('cmn2', 'ajax_comp_modulesets_nodes')
    t.modulesets = r
    t.checkbox_names.append(r.id+'_ck')
    t = DIV(
             DIV(
               t.html(),
               _style="""min-width:60%;
                         max-width:60%;
                         float:left;
                         border-right:0px solid;
                      """,
               _id='cmn2',
             ),
             DIV(
               r.html(),
               _style="""min-width:40%;
                         max-width:40%;
                         float:left;
                      """,
               _id='cmn1',
             ),
             DIV(XML('&nbsp;'), _class='spacer'),
             SCRIPT("""
             function calign() {
              $("#cmn1").find("div.theader").css({height: $("#cmn2").find("div.theader").height()})
              $("#cmn1").find("tr.theader").css({height: $("#cmn2").find("tr.theader").height()})
             }
             osvc.tables["cmn2"].on_change = calign
             osvc.tables["cmn1"].on_change = calign
             """),
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
        self.keys = ['mod_name']
        self.span = ['mod_name']
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
        self.dbfilterable = False

    def extra_line_key(self, o):
        return self.id+'_'+self.colprops['mod_name'].get(o).replace('.','_')


class table_comp_svc_status(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.keys = ['svc_name']
        self.span = ['svc_name']
        self.cols = ['svc_name', 'total', 'ok', 'nok', 'na', 'obs', 'pct',
                     "svc_log"]
        self.colprops = {
            'svc_name': HtmlTableColumn(
                     title='Service',
                     field='svc_name',
                     table='comp_svc_status',
                     display=True,
                     img='node16',
                     _class='svcname',
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
        self.dbfilterable = False

    def extra_line_key(self, o):
        return self.id+'_'+self.colprops['svc_name'].get(o).replace('.','_')


class table_comp_node_status(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.keys = ['node_name']
        self.span = ['node_name']
        self.cols = ['node_name', 'total', 'ok', 'nok', 'na', 'obs', 'pct',
                     "node_log"]
        self.colprops = {
            'node_name': HtmlTableColumn(
                     title='Node',
                     field='node_name',
                     table='comp_node_status',
                     display=True,
                     img='node16',
                     _class='nodename',
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
        self.dbfilterable = False

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
                     'rset_md5',
                     'run_log']
        self.cols += v_nodes_cols
        self.colprops = {
            'run_date': HtmlTableColumn(
                     title='Run date',
                     field='run_date',
                     table='comp_status',
                     img='check16',
                     display=True,
                     _class='datetime_weekly',
                    ),
            'run_nodename': HtmlTableColumn(
                     title='Node',
                     field='run_nodename',
                     table='comp_status',
                     img='node16',
                     display=True,
                     _class='nodename',
                    ),
            'run_svcname': HtmlTableColumn(
                     title='Service',
                     field='run_svcname',
                     table='comp_status',
                     img='node16',
                     display=True,
                     _class='svcname',
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
            'rset_md5': HtmlTableColumn(
                     title='Ruleset md5',
                     field='rset_md5',
                     table='comp_status',
                     img='check16',
                     display=False,
                     _class='nowrap pre rset_md5',
                    ),
            'run_status': HtmlTableColumn(
                     title='Status',
                     field='run_status',
                     table='comp_status',
                     img='check16',
                     display=True,
                     _class='run_status',
                    ),
            'run_status_log': HtmlTableColumn(
                     title='History',
                     field='un_status_log',
                     table='comp_status',
                     img='check16',
                     display=False,
                     _class='run_status_log',
                    ),
            'run_log': HtmlTableColumn(
                     title='Log',
                     field='run_log',
                     table='comp_status',
                     img='check16',
                     display=False,
                     _class='run_log',
                    ),
        }
        self.colprops.update(v_nodes_colprops)
        for i in self.cols:
            self.colprops[i].t = self
        self.ajax_col_values = 'ajax_comp_status_col_values'
        self.extraline = True
        self.wsable = True
        self.dataable = True
        self.child_tables = ["agg", "cms", "cns", "css"]
        self.force_cols = ['os_name']
        self.keys = ["run_nodename", "run_svcname", "run_module"]
        self.span = ["run_nodename", "run_svcname", "run_module"]
        self.checkboxes = True
        self.checkbox_id_table = 'comp_status'
        if 'CompManager' in user_groups():
            self.additional_tools.append('check_del')

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

def fmt_action(nodename, svcname, action, action_type="push", mod=[], modset=[]):
    base_cmd = ['compliance', action]
    if len(mod) > 0:
        base_cmd += ['--module', ','.join(mod)]
    if len(modset) > 0:
        base_cmd += ['--moduleset', ','.join(modset)]
    if action_type == "pull":
        return ' '.join(cmd)

    if svcname is None or svcname == "":
        _cmd = ["/opt/opensvc/bin/nodemgr"]
    else:
        _cmd = ["/opt/opensvc/bin/svcmgr", "-s", svcname]

    cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                  '-o', 'ForwardX11=no',
                  '-o', 'PasswordAuthentication=no',
                  '-t',
           'opensvc@'+nodename,
           '--',
           'sudo'] + _cmd + base_cmd
    return ' '.join(cmd)

@auth.requires_membership('CompExec')
def do_action(ids, action=None):
    if action is None or len(action) == 0:
        raise ToolError("no action specified")
    if len(ids) == 0:
        raise ToolError("no target to execute %s on"%action)

    q = db.comp_status.id.belongs(ids)
    q &= db.comp_status.run_nodename == db.nodes.nodename
    q &= (db.nodes.team_responsible.belongs(user_groups())) | \
         (db.nodes.team_integ.belongs(user_groups()))
    rows = db(q).select(db.nodes.os_name,
                        db.nodes.fqdn,
                        db.comp_status.run_nodename,
                        db.comp_status.run_svcname,
                        db.comp_status.run_module)

    vals = []
    vars = ['nodename', 'svcname', 'action_type', 'command', 'user_id']
    tolog_node = []
    tolog_svc = []

    for row in rows:
        if row.nodes.os_name == "Windows":
            action_type = "pull"
        else:
            action_type = "push"

        if row.nodes.fqdn is not None and len(row.nodes.fqdn) > 0:
            node = row.nodes.fqdn
        else:
            node = row.comp_status.run_nodename


        if row.comp_status.run_svcname is None or row.comp_status.run_svcname == "":
            tolog_node.append([row.comp_status.run_nodename,
                               row.comp_status.run_module])
        else:
            tolog_svc.append([row.comp_status.run_svcname,
                              row.comp_status.run_module])

        vals.append([row.comp_status.run_nodename,
                     row.comp_status.run_svcname,
                     action_type,
                     fmt_action(node,
                                row.comp_status.run_svcname,
                                action,
                                action_type,
                                mod=[row.comp_status.run_module]),
                     str(auth.user_id)
                    ])

    purge_action_queue()
    generic_insert('action_queue', vars, vals)

    from subprocess import Popen
    import sys
    actiond = 'applications'+str(URL(r=request,c='actiond',f='actiond.py'))
    process = Popen([sys.executable, actiond])
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
    if len(vals) > 0:
        l = {
          'event': 'action_q_change',
          'data': action_queue_ws_data(),
        }
        _websocket_send(event_msg(l))


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
            table_modified("comp_rulesets_variables")
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
    table_modified("comp_status")
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
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.comp_log.run_nodename)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_comp_status_col_values():
    t = table_comp_status('cs0', 'ajax_comp_status')
    col = request.args[0]
    try:
        o = db[t.colprops[col].table][col]
    except:
        return T("this column is not filterable")
    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    q &= db.comp_status.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.comp_status.run_nodename)
    t.object_list = db(q).select(o, orderby=o, cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_comp_status():
    t = table_comp_status('cs0', 'ajax_comp_status')

    if len(request.args) >= 1:
        action = request.args[0]
        try:
            if action == 'check_del':
                check_del(t.get_checked())
        except ToolError, e:
            t.flash = str(e)

    o = ~db.comp_status.run_nodename
    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    q &= db.comp_status.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.comp_status.run_nodename)


    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        if request.vars.volatile_filters is None:
            n = db(q).select(db.comp_status.id.count(), cacheable=True).first()._extra[db.comp_status.id.count()]
            limitby = (t.pager_start,t.pager_end)
        else:
            n = 0
            limitby = (0, 500)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, limitby=limitby, orderby=o, cacheable=False)
        return t.table_lines_data(n, html=False)

    """
    spark_cmds = ""
    for r in t.object_list:
        spark_cmds += "sparkl('%(url)s', '%(id)s');"%dict(
          url=spark_url(r.comp_status.run_nodename, r.comp_status.run_module),
          id=spark_id(r.comp_status.run_nodename, r.comp_status.run_module),
        )
    """

class col_comp_status_agg(HtmlTableColumn):
    def chart(self, a, b, c, d):
        total = a + b + c + d
        if total == 0:
            pa = 0
            pb = 0
            pc = 0
            pd = 0
            fpa = "0%"
            fpb = "0%"
            fpc = "0%"
            fpd = "0%"
        else:
            fpa = 100.*a/total
            fpb = 100.*b/total
            fpc = 100.*c/total
            fpd = 100.*d/total
            pa = "%d%%"%int(fpa)
            pb = "%d%%"%int(fpb)
            pc = "%d%%"%int(fpc)
            pd = "%d%%"%int(fpd)
            fpa = "%.1f%%"%fpa
            fpb = "%.1f%%"%fpb
            fpc = "%.1f%%"%fpc
            fpd = "%.1f%%"%fpd


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
                SPAN("%d (%s)"%(a, fpa), " ", T("obsolete"), _style="color:#15367A;padding:3px"),
                SPAN("%d (%s)"%(b, fpb), " ", T("ok"), _style="color:#3aaa50;padding:3px"),
                SPAN("%d (%s)"%(c, fpc), " ", T("n/a"), _style="color:#acacac;padding:3px"),
                SPAN("%d (%s)"%(d, fpd), " ", T("not ok"), _style="color:#FF7863;padding:3px"),
              ),
              _style="""margin: auto;
                        text-align: center;
                        width: 100%;
                     """,
            ),
        return d

    def html(self, o):
        obs, ok, na, nok = o['agg']
        return DIV(
                 self.chart(obs, ok, na, nok),
                 _style="padding:4px"
               )


class table_comp_status_agg(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['agg']
        self.colprops = {
            'agg': col_comp_status_agg(
                     title='Aggregation',
                     field='add',
                     display=True,
                     img='spark16',
                    ),
        }
        self.dbfilterable = False
        self.filterable = False
        self.pageable = False
        self.bookmarkable = False
        self.commonalityable = False
        self.exportable = False
        self.bookmarkable = False
        self.linkable = False
        self.refreshable = False
        self.columnable = False
        self.headers = False
        self.highlight = False

@auth.requires_login()
def ajax_comp_status_agg():
    ag = table_comp_status_agg('agg', 'ajax_comp_status_agg')
    t = table_comp_status('cs0', 'ajax_comp_status')
    o = ~db.comp_status.run_nodename
    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    q &= db.comp_status.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.comp_status.run_nodename)

    n = db(q).select(db.comp_status.id.count(), cacheable=True).first()._extra[db.comp_status.id.count()]
    t.setup_pager(n)
    #all = db(q).select(db.comp_status.ALL, db.v_nodes.id)
    t.object_list = db(q).select(limitby=(t.pager_start,t.pager_end),
                                 orderby=o, cacheable=True)

    q_obs = q & (db.comp_status.run_date < now - datetime.timedelta(days=7))
    q_nok = q & (db.comp_status.run_date > now - datetime.timedelta(days=7)) & (db.comp_status.run_status == 1)
    q_na = q & (db.comp_status.run_date > now - datetime.timedelta(days=7)) & (db.comp_status.run_status == 2)
    q_ok = q & (db.comp_status.run_date > now - datetime.timedelta(days=7)) & (db.comp_status.run_status == 0)

    obs = db(q_obs).count()
    nok = db(q_nok).count()
    na = db(q_na).count()
    ok = db(q_ok).count()

    ag.object_list = [{'agg': (obs, ok, na, nok)}]

    if len(request.args) == 1 and request.args[0] == 'line':
        return ag.table_lines_data(-1)

@auth.requires_login()
def comp_status():
    t = table_comp_status('cs0', 'ajax_comp_status')
    ag = table_comp_status_agg('agg', 'ajax_comp_status_agg')
    mt = table_comp_mod_status('cms', 'ajax_comp_mod_status')
    nt = table_comp_node_status('cns', 'ajax_comp_node_status')
    st = table_comp_svc_status('css', 'ajax_comp_svc_status')

    d = DIV(
          DIV(
            ag.html(),
            _id="agg",
          ),
          DIV(
            T("Modules aggregation"),
            _style="text-align:left;font-size:120%;background-color:#e0e1cd",
            _class="right16 clickable",
            _onclick="""
            if (!$("#cms").is(":visible")) {
              $(this).addClass("down16");
              $(this).removeClass("right16");
              $("#cms").show();
              osvc.tables["cms"].refresh()
            } else {
              $(this).addClass("right16");
              $(this).removeClass("down16");
              $("#cms").hide();
            }"""
          ),
          DIV(
            mt.html(),
            _id="cms",
            _style="display:none"
          ),
          DIV(
            T("Nodes aggregation"),
            _style="text-align:left;font-size:120%;background-color:#e0e1cd",
            _class="right16 clickable",
            _onclick="""
            if (!$("#cns").is(":visible")) {
              $(this).addClass("down16");
              $(this).removeClass("right16");
              $("#cns").show();
              osvc.tables["cns"].refresh()
            } else {
              $(this).addClass("right16");
              $(this).removeClass("down16");
              $("#cns").hide();
            }"""
          ),
          DIV(
            nt.html(),
            _id="cns",
            _style="display:none"
          ),
          DIV(
            T("Services aggregation"),
            _style="text-align:left;font-size:120%;background-color:#e0e1cd",
            _class="right16 clickable",
            _onclick="""
            if (!$("#css").is(":visible")) {
              $(this).addClass("down16");
              $(this).removeClass("right16");
              $("#css").show();
              osvc.tables["css"].refresh()
            } else {
              $(this).addClass("right16");
              $(this).removeClass("down16");
              $("#css").hide();
            }"""
          ),
          DIV(
            st.html(),
            _id="css",
            _style="display:none"
          ),
          DIV(
            t.html(),
            _id='cs0',
          ),
          SCRIPT(
               """
function ws_action_switch_%(divid)s(data) {
        if (data["event"] == "comp_status_change") {
          osvc.tables["%(divid)s"].refresh();
        }
}
wsh["%(divid)s"] = ws_action_switch_%(divid)s
              """ % dict(
                     divid=t.innerhtml,
                    ),
          ),
        )
    return dict(table=d)


@auth.requires_login()
def ajax_comp_svc_status():
    t = table_comp_status('cs0', 'ajax_comp_status')
    mt = table_comp_svc_status('css', 'ajax_comp_svc_status')

    o = ~db.comp_status.run_svcname
    q = _where(None, 'comp_status', domain_perms(), 'run_svcname')
    #q &= db.comp_status.run_svcname == db.v_svcmon.mon_svcname
    q &= db.comp_status.run_nodename == db.v_nodes.nodename
    q &= (db.comp_status.run_svcname != None) & (db.comp_status.run_svcname != "")
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
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
                    from %(sql)s and comp_status.run_nodename=v_nodes.nodename group by run_svcname) t) u
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
    if len(request.args) == 1 and request.args[0] == 'line':
        return mt.table_lines_data(-1)

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
    if len(request.args) == 1 and request.args[0] == 'line':
        return mt.table_lines_data(-1)

    return DIV(
             mt.html(),
           )

@auth.requires_login()
def ajax_svc_history():
    session.forget(response)
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
    t = table_comp_status('cs0', 'ajax_comp_status')
    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    q &= db.comp_status.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.comp_status.run_nodename)
    _sql = db(q)._select(db.comp_status.run_module)
    _sql = _sql.rstrip(';')

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
                    run_date>date_sub(now(), interval 1 year) and
                    run_module in (%(_sql)s)
                group by week(run_date), run_module, run_nodename
              ) t
              group by t.week
              order by t.week
             """%dict(svcname=request.vars.svcname, _sql=_sql)
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
    session.forget(response)
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
    t = table_comp_status('cs0', 'ajax_comp_status')
    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    q &= db.comp_status.run_module == request.vars.modname
    q &= db.comp_status.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.comp_status.run_nodename)
    _sql = db(q)._select(db.comp_status.run_nodename)
    _sql = _sql.rstrip(';')
    #nodes = ','.join(map(lambda x: repr(str(x)), [r[0] for r in db.executesql(_sql)]))

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
                    run_date>date_sub(now(), interval 1 year) and
                    run_nodename in (%(_sql)s)
                group by week(run_date), run_nodename, run_svcname
              ) t
              group by t.week
              order by t.week
             """%dict(mod=request.vars.modname, _sql=_sql)
    #raise Exception(sql)
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
    session.forget(response)
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
    t = table_comp_status('cs0', 'ajax_comp_status')
    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    q &= db.comp_status.run_nodename == db.v_nodes.nodename
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.comp_status.run_nodename)
    _sql = db(q)._select(db.comp_status.run_module)
    _sql = _sql.rstrip(';')

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
                    run_date>date_sub(now(), interval 1 year) and
                    run_module in (%(_sql)s)
                group by week(run_date), run_module
              ) t
              group by t.week
              order by t.week
             """%dict(node=request.vars.nodename, _sql=_sql)
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
    if len(request.args) == 1 and request.args[0] == 'line':
        return mt.table_lines_data(-1)

    return DIV(
             mt.html(),
           )

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
                     'rset_md5']
        for c in self.colprops:
            self.colprops[c].t = self
            if 'run_' in c or c == 'rset_md5':
                self.colprops[c].table = 'comp_log'
        self.colprops['run_date'].default_filter = '>-1d'

        self.additional_tools = []
        self.ajax_col_values = 'ajax_comp_log_col_values'
        self.checkboxes = True
        self.checkbox_id_table = 'comp_log'
        self.wsable = True
        self.dataable = True
        self.child_tables = []
        self.keys = ["run_date", "run_nodename", "run_svcname", "run_module", "run_action"]
        self.span = ["run_date", "run_nodename", "run_svcname", "run_module", "run_action"]

@auth.requires_login()
def ajax_comp_log():
    t = table_comp_log('comp_log', 'ajax_comp_log')

    db.commit()
    o = ~db.comp_log.id
    q = _where(None, 'comp_log', domain_perms(), 'run_nodename')
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters(q, db.comp_log.run_nodename)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        if request.vars.volatile_filters is None:
            limitby = (t.pager_start,t.pager_end)
        else:
            limitby = (0, 500)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, limitby=limitby, orderby=o, cacheable=False)
        return t.table_lines_data(-1, html=False)

@auth.requires_login()
def comp_log():
    t = table_comp_log('comp_log', 'ajax_comp_log')
    t = DIV(
          DIV(
            t.html(),
            _id='comp_log',
          ),
          SCRIPT("""
function ws_action_switch_%(divid)s(data) {
        if (data["event"] == "comp_status_change") {
          osvc.tables["%(divid)s"].refresh();
        }
}
wsh["%(divid)s"] = ws_action_switch_%(divid)s
              """ % dict(
                     divid=t.innerhtml,
                    ),
          ),
        )
    return dict(table=t)

def call():
    session.forget(response)
    return service()

def user():
    return auth()

def auth_uuid(fn):
    def new(*args, **kwargs):
        uuid, node = kwargs['auth']
        rows = db((db.auth_node.nodename==node)&(db.auth_node.uuid==uuid)).select(cacheable=True)
        if len(rows) != 1:
            return "agent authentication error"
        return fn(*args, **kwargs)
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
                        groupby=db.comp_moduleset_modules.modset_mod_name,
                        cacheable=True)
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
                        groupby=db.comp_moduleset_modules.modset_mod_name,
                        cacheable=True)
    return [r.modset_mod_name for r in rows]

def comp_attached_svc_ruleset_id(svcname, slave):
    q = db.comp_rulesets_services.svcname == svcname
    q &= db.comp_rulesets_services.slave == slave
    rows = db(q).select(db.comp_rulesets_services.ruleset_id, cacheable=True)
    return [r.ruleset_id for r in rows]

def comp_attached_ruleset_id(nodename):
    q = db.comp_rulesets_nodes.nodename == nodename
    rows = db(q).select(db.comp_rulesets_nodes.ruleset_id, cacheable=True)
    return [r.ruleset_id for r in rows]

def comp_attached_svc_moduleset_id(svcname):
    q = db.comp_modulesets_services.modset_svcname == svcname
    rows = db(q).select(db.comp_modulesets_services.modset_id, cacheable=True)
    return [r.modset_id for r in rows]

def comp_attached_moduleset_id(nodename):
    q = db.comp_node_moduleset.modset_node == nodename
    rows = db(q).select(db.comp_node_moduleset.modset_id, cacheable=True)
    return [r.modset_id for r in rows]

def comp_ruleset_id(ruleset):
    q = db.comp_rulesets.ruleset_name == ruleset
    rows = db(q).select(db.comp_rulesets.id, cacheable=True)
    if len(rows) == 0:
        return None
    return rows[0].id

def comp_moduleset_id(moduleset):
    q = db.comp_moduleset.modset_name == moduleset
    rows = db(q).select(db.comp_moduleset.id, cacheable=True)
    if len(rows) == 0:
        return None
    return rows[0].id

def comp_moduleset_exists(moduleset):
    q = db.comp_moduleset.modset_name == moduleset
    rows = db(q).select(db.comp_moduleset.id, cacheable=True)
    if len(rows) != 1:
        return None
    return rows[0].id

def comp_ruleset_svc_attached(svcname, rset_id, slave):
    q = db.comp_rulesets_services.svcname == svcname
    q &= db.comp_rulesets_services.ruleset_id == rset_id
    q &= db.comp_rulesets_services.slave == slave
    if len(db(q).select(db.comp_rulesets_services.id, cacheable=True)) == 0:
        return False
    return True

def comp_moduleset_svc_attached(svcname, modset_id, slave):
    q = db.comp_modulesets_services.modset_svcname == svcname
    q &= db.comp_modulesets_services.modset_id == modset_id
    q &= db.comp_modulesets_services.slave == slave
    if len(db(q).select(db.comp_modulesets_services.id, cacheable=True)) == 0:
        return False
    return True

def comp_moduleset_attached(nodename, modset_id):
    q = db.comp_node_moduleset.modset_node == nodename
    q &= db.comp_node_moduleset.modset_id == modset_id
    if len(db(q).select(db.comp_node_moduleset.id, cacheable=True)) == 0:
        return False
    return True

def comp_ruleset_exists(ruleset):
    q = db.v_comp_explicit_rulesets.ruleset_name == ruleset
    rows = db(q).select(db.v_comp_explicit_rulesets.id, cacheable=True)
    if len(rows) != 1:
        return None
    return rows[0].id

def comp_ruleset_attached(nodename, ruleset_id):
    q = db.comp_rulesets_nodes.nodename == nodename
    q &= db.comp_rulesets_nodes.ruleset_id == ruleset_id
    if len(db(q).select(db.comp_rulesets_nodes.id, cacheable=True)) == 0:
        return False
    return True

def comp_slave(svcname, nodename):
    q = db.svcmon.mon_vmname == nodename
    q &= db.svcmon.mon_svcname == svcname
    row = db(q).select(cacheable=True).first()
    if row is None:
        return False
    return True

def has_slave(svcname):
    q = db.svcmon.mon_svcname == svcname
    q &= db.svcmon.mon_vmname != None
    q &= db.svcmon.mon_vmname != ""
    row = db(q).select(cacheable=True).first()
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
    table_modified("comp_rulesets_services")
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
    table_modified("comp_modulesets_services")
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
    table_modified("comp_node_moduleset")
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
    slave = comp_slave(svcname, auth[1])
    if ruleset == 'all':
        rset_id = comp_attached_svc_ruleset_id(svcname, slave)
    else:
        rset_id = comp_ruleset_id(ruleset)
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
    table_modified("comp_rulesets_services")
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
    table_modified("comp_modulesets_services")
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
    table_modified("comp_node_moduleset")
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
    rows = db(q).select(db.nodes.team_responsible, cacheable=True)
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
    rows = db(q).select(db.nodes.team_responsible, cacheable=True)
    if len(rows) == 0:
        return False
    return True

def comp_moduleset_attachable(nodename, modset_id):
    q = db.nodes.team_responsible == db.auth_group.role
    q &= db.auth_group.id == db.comp_moduleset_team_responsible.group_id
    q &= db.comp_moduleset_team_responsible.modset_id == db.comp_moduleset.id
    q &= db.comp_moduleset.id == modset_id
    q &= db.nodes.nodename == nodename
    rows = db(q).select(db.nodes.team_responsible, cacheable=True)
    if len(rows) != 1:
        return False
    return True

def comp_ruleset_attachable(nodename, ruleset_id):
    q = db.nodes.team_responsible == db.auth_group.role
    q &= db.auth_group.id == db.comp_ruleset_team_responsible.group_id
    q &= db.comp_ruleset_team_responsible.ruleset_id == db.comp_rulesets.id
    q &= db.comp_rulesets.id == ruleset_id
    q &= db.nodes.nodename == nodename
    rows = db(q).select(cacheable=True)
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
    table_modified("comp_rulesets_nodes")
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
    table_modified("comp_rulesets_nodes")
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
    rows = db(q).select(groupby=db.comp_rulesets.id, cacheable=True)
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
    rows = db(q).select(db.comp_moduleset.modset_name,
                        groupby=db.comp_moduleset.modset_name, cacheable=True)
    return sorted([r.modset_name for r in rows])

@auth_uuid
@service.xmlrpc
def comp_show_status(svcname="", pattern='%', auth=("", "")):
    node = auth[1]
    q = db.comp_status.run_module.like(pattern)
    q &= db.comp_status.run_nodename == node
    q &= db.comp_status.run_svcname == svcname
    rows = db(q).select(orderby=db.comp_status.run_module, cacheable=True)
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
    return _comp_get_svc_moduleset(svcname, slave=slave)

@auth_uuid
@service.xmlrpc
def comp_get_svc_data(nodename, svcname, modulesets, auth):
    return _comp_get_svc_data(nodename, svcname, modulesets)

@auth_uuid
@service.xmlrpc
def comp_get_data(nodename, modulesets, auth):
    return _comp_get_data(nodename, modulesets=modulesets)

def _comp_get_data(nodename, modulesets=[]):
    return {
      'modulesets': _comp_get_moduleset_data(nodename, modulesets=modulesets),
      'rulesets': _comp_get_ruleset(nodename),
      'modset_rset_relations': get_modset_rset_relations_s(),
      'modset_relations': get_modset_relations_s(),
    }

def _comp_get_svc_data(nodename, svcname, modulesets=[]):
    slave = comp_slave(svcname, nodename)
    return {
      'modulesets': _comp_get_svc_moduleset_data(svcname, modulesets=modulesets, slave=slave),
      'rulesets': _comp_get_svc_ruleset(svcname, nodename, slave=slave),
      'modset_rset_relations': get_modset_rset_relations_s(),
      'modset_relations': get_modset_relations_s(),
    }

def test_comp_get_svc_ruleset():
    return _comp_get_svc_ruleset("unxdevweb01", "clementine")

@auth_uuid
@service.xmlrpc
def comp_get_moduleset_data(nodename, auth):
    return _comp_get_moduleset_data(nodename)

@auth_uuid
@service.xmlrpc
def comp_get_data_moduleset(nodename, auth):
    return {
      'root_modulesets': _comp_get_moduleset_names(nodename),
      'modulesets': _comp_get_moduleset_data(nodename),
      'modset_relations': get_modset_relations_s(),
    }

@auth_uuid
@service.xmlrpc
def comp_get_svc_data_moduleset(svcname, auth):
    slave = comp_slave(svcname, auth[1])
    return {
      'root_modulesets': _comp_get_svc_moduleset_names(svcname, slave=slave),
      'modulesets': _comp_get_svc_moduleset_data(svcname, slave=slave),
      'modset_relations': get_modset_relations_s(),
    }

@auth_uuid
@service.xmlrpc
def comp_get_svc_moduleset_data(svcname, auth):
    slave = comp_slave(svcname, auth[1])
    return _comp_get_svc_moduleset_data(svcname, slave=slave)

@auth.requires_membership('NodeExec')
@service.json
def comp_get_all_moduleset():
    return _comp_get_all_moduleset()

@auth.requires_membership('NodeExec')
@service.json
def comp_get_all_module():
    return _comp_get_all_module()

def _comp_get_all_moduleset():
    q = db.comp_moduleset.id > 0
    rows = db(q).select(db.comp_moduleset.id, db.comp_moduleset.modset_name,
                        orderby=db.comp_moduleset.modset_name)
    return [(r.id, r.modset_name) for r in rows]

def _comp_get_all_module():
    q = db.comp_moduleset_modules.id > 0
    q &= db.comp_moduleset_modules.modset_id == db.comp_moduleset.id
    rows = db(q).select(db.comp_moduleset_modules.id,
                        db.comp_moduleset_modules.modset_mod_name,
                        orderby=db.comp_moduleset_modules.modset_mod_name,
                        groupby=db.comp_moduleset_modules.modset_mod_name,
                       )
    return [(r.id, r.modset_mod_name) for r in rows]

@auth_uuid
@service.xmlrpc
def comp_get_moduleset(nodename, auth):
    return _comp_get_moduleset(nodename)

def _comp_get_svc_moduleset_ids_with_children(svcname, modulesets=[], slave=False):
    modset_ids = _comp_get_svc_moduleset_ids(svcname, modulesets=modulesets, slave=slave)
    modset_tree_nodes = get_modset_tree_nodes(modset_ids)
    modset_ids = set(modset_tree_nodes.keys())
    for l in modset_tree_nodes.values():
        modset_ids |= set(l)
    return modset_ids

def _comp_get_svc_moduleset(svcname, modulesets=[], slave=False):
    modset_ids = _comp_get_svc_moduleset_ids(svcname, modulesets=modulesets, slave=slave)
    q = db.comp_moduleset.id.belongs(modset_ids)
    rows = db(q).select(db.comp_moduleset.modset_name, cacheable=True)
    return [r.modset_name for r in rows]

def _comp_get_svc_moduleset_ids(svcname, modulesets=[], slave=False):
    q = db.comp_modulesets_services.modset_svcname == svcname
    q &= db.comp_modulesets_services.slave == slave
    q &= db.comp_modulesets_services.modset_id == db.comp_moduleset.id
    q &= db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    q &= db.auth_group.id == db.comp_moduleset_team_responsible.group_id
    q &= db.services.svc_name == svcname
    q &= db.services.svc_app == db.apps.app
    q &= db.apps.id == db.apps_responsibles.app_id
    q &= db.apps_responsibles.group_id == db.auth_group.id
    if len(modulesets) > 0:
        q &= db.comp_moduleset.modset_name.belongs(modulesets)
    rows = db(q).select(db.comp_moduleset.id, groupby=db.comp_moduleset.id, cacheable=True)
    modset_ids = [r.id for r in rows]
    return modset_ids

def _comp_get_svc_moduleset_names(svcname, modulesets=[], slave=False):
    modset_ids = _comp_get_svc_moduleset_ids(svcname, modulesets=modulesets, slave=slave)
    modset_names = get_modset_names(modset_ids)
    return modset_names.values()

def _comp_get_svc_moduleset_data(svcname, modulesets=[], slave=False):
    modset_ids = _comp_get_svc_moduleset_ids_with_children(svcname, modulesets=modulesets, slave=slave)
    modset_tree_nodes = get_modset_tree_nodes(modset_ids)
    modset_ids = set(modset_tree_nodes.keys())
    for l in modset_tree_nodes.values():
        modset_ids |= set(l)

    q = db.comp_moduleset.id.belongs(modset_ids)
    l = db.comp_moduleset_modules.modset_id == db.comp_moduleset.id
    g = db.comp_moduleset_modules.modset_id|db.comp_moduleset_modules.id
    rows = db(q).select(db.comp_moduleset.modset_name,
                        db.comp_moduleset_modules.autofix,
                        db.comp_moduleset_modules.modset_mod_name,
                        left=db.comp_moduleset_modules.on(l),
                        groupby=g,
                        cacheable=True)
    d = {}
    for row in rows:
        if row.comp_moduleset.modset_name not in d:
            d[row.comp_moduleset.modset_name] = []
        if row.comp_moduleset_modules.modset_mod_name is not None:
            d[row.comp_moduleset.modset_name].append((
              row.comp_moduleset_modules.modset_mod_name,
              row.comp_moduleset_modules.autofix,
            ))
    return d

def _comp_get_moduleset_ids(nodename, modulesets=[]):
    q = db.comp_node_moduleset.modset_node == nodename
    q &= db.comp_node_moduleset.modset_id == db.comp_moduleset.id
    q &= db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    q &= db.auth_group.id == db.comp_moduleset_team_responsible.group_id
    q &= db.nodes.team_responsible == db.auth_group.role
    q &= db.nodes.nodename == nodename
    if len(modulesets) > 0:
        q &= db.comp_moduleset.modset_name.belongs(modulesets)
    rows = db(q).select(db.comp_moduleset.id, groupby=db.comp_moduleset.id, cacheable=True)
    modset_ids = [r.id for r in rows]
    return modset_ids

def _comp_get_moduleset_names(nodename, modulesets=[]):
    modset_ids = _comp_get_moduleset_ids(nodename, modulesets=modulesets)
    modset_names = get_modset_names(modset_ids)
    return modset_names.values()

def _comp_get_moduleset_ids_with_children(nodename, modulesets=[]):
    modset_ids = _comp_get_moduleset_ids(nodename, modulesets=modulesets)
    modset_tree_nodes = get_modset_tree_nodes(modset_ids)
    modset_ids = set(modset_tree_nodes.keys())
    for l in modset_tree_nodes.values():
        modset_ids |= set(l)
    return modset_ids

def _comp_get_moduleset_data(nodename, modulesets=[]):
    modset_ids = _comp_get_moduleset_ids_with_children(nodename, modulesets=modulesets)
    q = db.comp_moduleset.id.belongs(modset_ids)
    l = db.comp_moduleset_modules.modset_id == db.comp_moduleset.id
    g = db.comp_moduleset_modules.modset_id|db.comp_moduleset_modules.id
    rows = db(q).select(db.comp_moduleset.modset_name,
                        db.comp_moduleset_modules.autofix,
                        db.comp_moduleset_modules.modset_mod_name,
                        left=db.comp_moduleset_modules.on(l),
                        groupby=g,
                        cacheable=True)

    d = {}
    for row in rows:
        if row.comp_moduleset.modset_name not in d:
            d[row.comp_moduleset.modset_name] = []
        if row.comp_moduleset_modules.modset_mod_name is not None:
            d[row.comp_moduleset.modset_name].append((
              row.comp_moduleset_modules.modset_mod_name,
              row.comp_moduleset_modules.autofix,
            ))

    return d

def _comp_get_moduleset(nodename):
    modset_ids = _comp_get_moduleset_ids_with_children(nodename)
    q = db.comp_moduleset.id.belongs(modset_ids)
    rows = db(q).select(db.comp_moduleset.modset_name, cacheable=True)
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
        elif a == 'run_ruleset':
            # we have rset_md5 ... no need to store ruleset names
            del(vals[i])
            del(vars[i])
    vars.append('run_date')
    vals.append(now)
    generic_insert('comp_log', vars, vals)
    if action == 'check':
        generic_insert('comp_status', vars, vals)
    update_dash_compdiff(auth[1])
    l = {
      'event': 'comp_status_change',
      'data': {'foo': 'bar'},
    }
    _websocket_send(event_msg(l))


@auth_uuid
@service.xmlrpc
def comp_log_actions(vars, vals, auth):
    if len(vals) == 0:
        return
    now = datetime.datetime.now()
    vars.append('run_date')
    check_vals = []
    try:
        i_run_ruleset = vars.index('run_ruleset')
        del(vars[i_run_ruleset])
    except:
        i_run_ruleset = None
    i_run_log = vars.index('run_log')
    i_run_action = vars.index('run_action')
    for i, _vals in enumerate(vals):
        vals[i][i_run_log] = strip_unprintable(_vals[i_run_log])
        if i_run_ruleset is not None:
            # we have rset_md5 ... no need to store ruleset names
            del(vals[i][i_run_ruleset])
        vals[i].append(now)
        if _vals[i_run_action] == 'check':
            check_vals.append(vals[i])
    generic_insert('comp_log', vars, vals)
    if len(check_vals) > 0:
        generic_insert('comp_status', vars, check_vals)
    l = {
      'event': 'comp_status_change',
      'data': {'foo': 'bar'},
    }
    _websocket_send(event_msg(l))
    update_dash_compdiff(auth[1])

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
    q &= db.svcmon.mon_updated > now - datetime.timedelta(minutes=15)
    row = db(q).select(cacheable=True).first()
    if row is None:
        q = db.svcmon.mon_svcname == svcname
        q &= db.svcmon.mon_vmname == nodename
        q &= db.svcmon.mon_containerstatus == "up"
        row = db(q).select(cacheable=True).first()
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
    rows = db(q).select(cacheable=True)
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
    rows = db(q).select(cacheable=True)
    if len(rows) != 1:
        return {}
    ruleset = {'name': 'osvc_node',
               'filter': str(q),
               'vars': []}
    for f in db.nodes.fields:
        val = rows[0][f]
        ruleset['vars'].append(('nodes.'+f, val))
    return {'osvc_node':ruleset}

def comp_get_rulesets_fset_ids(rset_ids=None, nodename=None, svcname=None):
    if rset_ids is None:
        q = db.comp_rulesets_filtersets.ruleset_id>0
    else:
        q = db.comp_rulesets_filtersets.ruleset_id.belongs(rset_ids)

    q &= db.comp_rulesets.id == db.comp_rulesets_filtersets.ruleset_id
    q &= db.comp_rulesets_filtersets.fset_id == db.gen_filtersets.id

    if nodename is None:
        raise

    q1 = db.comp_rulesets.id == db.comp_rulesets_chains.tail_rset_id
    q1 &= db.comp_rulesets_chains.head_rset_id == db.comp_ruleset_team_responsible.ruleset_id
    q1 &= db.comp_ruleset_team_responsible.group_id == node_team_responsible_id(nodename)

    if svcname is not None:
        q2 = db.comp_rulesets.id == db.comp_rulesets_chains.tail_rset_id
        q2 &= db.comp_rulesets_chains.head_rset_id == db.comp_ruleset_team_responsible.ruleset_id
        q2 &= db.comp_ruleset_team_responsible.group_id.belongs(svc_team_responsible_id(svcname))
        q1 |= q2

    q &= q1

    l = {}
    g = db.comp_rulesets_filtersets.fset_id|db.comp_rulesets.id
    rows = db(q).select(db.comp_rulesets_filtersets.fset_id,
                        db.gen_filtersets.fset_name,
                        db.comp_rulesets.id,
                        groupby=g, cacheable=True)

    fset_ids = [r.comp_rulesets_filtersets.fset_id for r in rows]

    if svcname is None:
        q = db.v_gen_filtersets.fset_id.belongs(fset_ids)
        q &= db.v_gen_filtersets.f_table.belongs(['services', 'svcmon'])
        f_rows = db(q).select(db.v_gen_filtersets.fset_id,
                              groupby=db.v_gen_filtersets.fset_id, cacheable=True)
        fsets_with_svc_tables = [r.fset_id for r in f_rows]

    for row in rows:
        if svcname is None and row.comp_rulesets_filtersets.fset_id in fsets_with_svc_tables:
            # for node compliance, discard fsets services related
            continue

        t = (row.comp_rulesets_filtersets.fset_id,
             row.gen_filtersets.fset_name)
        if t not in l:
            l[t] = [row.comp_rulesets.id]
        else:
            l[t] += [row.comp_rulesets.id]
    return l

def comp_rulesets_chains():
    # populate rset names cache
    rset_names = get_rset_names()

    # populate rset relations cache
    q = db.comp_rulesets_rulesets.id > 0
    q &= db.comp_rulesets_rulesets.child_rset_id == db.comp_rulesets.id
    rows = db(q).select(cacheable=True)
    rset_relations = {}
    for row in rows:
        if row.comp_rulesets_rulesets.parent_rset_id not in rset_relations:
            rset_relations[row.comp_rulesets_rulesets.parent_rset_id] = []
        rset_relations[row.comp_rulesets_rulesets.parent_rset_id].append(row.comp_rulesets_rulesets.child_rset_id)

    def recurse_rel(rset_id, chains, rset_id_chain):
        rset_id_chain += [rset_id]
        if rset_id_chain in chains:
            return chains
        if len(rset_id_chain) > 1:
            chains.append(rset_id_chain)
        if rset_id not in rset_relations:
            return chains
        for child_rset_id in rset_relations[rset_id]:
            chains = recurse_rel(child_rset_id, chains, copy.copy(rset_id_chain))
        return chains

    chains = []
    for ruleset_id in rset_names:
        chains += [[ruleset_id, ruleset_id]]
        chains += recurse_rel(ruleset_id, chains=[], rset_id_chain=[])

    vars = ['head_rset_id', 'tail_rset_id', 'chain_len', 'chain']
    vals = []
    for chain in chains:
        val = [str(chain[0]), str(chain[-1])]
        if chain[0] != chain[-1] or len(chain) != 2:
            _chain_len = str(len(chain))
            _chain = map(lambda x: rset_names[x], chain)
            _chain = ' > '.join(_chain)
        else:
            _chain_len = '1'
            _chain = ''
        val.append(_chain_len)
        val.append(_chain)
        vals.append(val)

    db.executesql("truncate comp_rulesets_chains")
    generic_insert('comp_rulesets_chains', vars, vals)
    db.commit()

def get_rset_relations():
    q1 = db.comp_rulesets_rulesets.child_rset_id == db.comp_rulesets.id
    j = db.comp_rulesets.id == db.comp_rulesets_filtersets.ruleset_id
    l = db.comp_rulesets_filtersets.on(j)
    rows = db(q1).select(
      db.comp_rulesets_rulesets.parent_rset_id,
      db.comp_rulesets_rulesets.child_rset_id,
      db.comp_rulesets_filtersets.fset_id,
      db.comp_rulesets.ruleset_type,
      left=l, cacheable=True
    )
    rset_relations = {}
    for row in rows:
        if row.comp_rulesets_rulesets.parent_rset_id not in rset_relations:
            rset_relations[row.comp_rulesets_rulesets.parent_rset_id] = []
        rset_relations[row.comp_rulesets_rulesets.parent_rset_id].append(row)
    return rset_relations

def comp_ruleset_vars(ruleset_id, qr=None, matching_fsets=[], rset_relations=None, rset_names=None):
    if qr is None:
        f = 'explicit attachment'
    else:
        f = comp_format_filter(qr)

    if rset_names is None:
        rset_names = get_rset_names()
    if ruleset_id not in rset_names:
        return dict()
    ruleset_name = rset_names[ruleset_id]

    if rset_relations is None:
        rset_relations = get_rset_relations()

    def recurse_rel(rset_id, children=[]):
        if rset_id not in rset_relations:
            return children
        for row in rset_relations[rset_id]:
            # don't validate sub ruleset ownership.
            # parent ownership is inherited
            if row.comp_rulesets.ruleset_type == "explicit":
                children.append(row.comp_rulesets_rulesets.child_rset_id)
                children = recurse_rel(row.comp_rulesets_rulesets.child_rset_id, children)
            elif row.comp_rulesets.ruleset_type == "contextual" and \
                 row.comp_rulesets_filtersets.fset_id is not None and \
                 row.comp_rulesets_filtersets.fset_id in matching_fsets:
                children.append(row.comp_rulesets_rulesets.child_rset_id)
                children = recurse_rel(row.comp_rulesets_rulesets.child_rset_id, children)
        return children

    children = recurse_rel(ruleset_id)

    # get variables (pass as arg too ?)
    q = db.comp_rulesets_variables.ruleset_id.belongs([ruleset_id]+children)
    rows = db(q).select(
      db.comp_rulesets_variables.var_name,
      db.comp_rulesets_variables.var_value,
      cacheable=True
    )
    d = dict(
          name=ruleset_name,
          filter=f,
          vars=[]
        )
    for row in rows:
        d['vars'].append((row.var_name,
                          row.var_value))
    return {ruleset_name: d}

def ruleset_add_var(d, rset_name, var, val):
    d[rset_name]['vars'].append((var, val))
    return d

@auth_uuid
@service.xmlrpc
def comp_get_ruleset_md5(rset_md5, auth):
    q = db.comp_run_ruleset.rset_md5 == rset_md5
    row = db(q).select(db.comp_run_ruleset.rset, cacheable=True).first()
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
    rows = db(q).select(db.auth_group.id, groupby=db.auth_group.id,
                        cacheable=True)
    return map(lambda x: x['id'], rows)

def node_team_responsible_id(nodename):
    q = db.nodes.nodename == nodename
    q &= db.nodes.team_responsible == db.auth_group.role
    rows = db(q).select(db.auth_group.id, cacheable=True)
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
    ruleset = _comp_get_svc_ruleset(svcname, auth[1])
    ruleset.update(comp_get_svcmon_ruleset(svcname, auth[1]))
    ruleset.update(comp_get_node_ruleset(auth[1]))
    ruleset = _comp_remove_dup_vars(ruleset)
    insert_run_rset(ruleset)
    return ruleset

def comp_contextual_rulesets(nodename, svcname=None, slave=False, matching_fsets=None, fset_ids=None, rset_relations=None, rset_names=None):
    ruleset = {}

    q = db.comp_rulesets.ruleset_public == True
    rows = db(q).select(db.comp_rulesets.id, cacheable=True)
    public_rsets = [r.id for r in rows]

    for (fset_id, fset_name), rset_ids in fset_ids.items():
        if fset_id not in matching_fsets:
            continue
        for rset_id in rset_ids:
            if rset_id not in public_rsets:
                continue
            ruleset.update(comp_ruleset_vars(rset_id, qr=fset_name, matching_fsets=matching_fsets, rset_relations=rset_relations, rset_names=rset_names))
    return ruleset

def _comp_get_svc_ruleset(svcname, nodename, slave=None):
    if slave is None:
        slave = comp_slave(svcname, nodename)

    rset_relations = get_rset_relations()
    rset_names = get_rset_names()

    # initialize ruleset with asset variables
    ruleset = comp_get_service_ruleset(svcname)

    # add contextual rulesets variables
    l = comp_get_rulesets_fset_ids(svcname=svcname, nodename=nodename)
    matching_fsets = comp_get_matching_fset_ids(fset_ids=l, nodename=nodename, svcname=svcname, slave=slave)
    ruleset.update(comp_contextual_rulesets(nodename=nodename,
                                            svcname=svcname,
                                            slave=slave,
                                            matching_fsets=matching_fsets,
                                            fset_ids=l,
                                            rset_relations=rset_relations,
                                            rset_names=rset_names))

    # add explicit rulesets variables
    rset_ids = _comp_get_explicit_svc_ruleset_ids(svcname, slave=slave)
    for rset_id in rset_ids:
        ruleset.update(comp_ruleset_vars(rset_id,
                                         matching_fsets=matching_fsets,
                                         rset_relations=rset_relations,
                                         rset_names=rset_names))

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
        table_modified("comp_run_ruleset")
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

def _comp_get_explicit_svc_ruleset_ids(svcname, slave=False):
    # attached to the node directly
    q = db.comp_rulesets_services.svcname == svcname
    q &= db.comp_rulesets_services.slave == slave
    rows = db(q).select(db.comp_rulesets_services.ruleset_id, cacheable=True)
    rset_ids = [r.ruleset_id for r in rows]

    # attached to the node through modulesets
    modset_ids = _comp_get_svc_moduleset_ids_with_children(svcname, slave=slave)
    q = db.comp_moduleset_ruleset.modset_id.belongs(modset_ids)
    rows = db(q).select(db.comp_moduleset_ruleset.ruleset_id)
    rset_ids = list(set(rset_ids) | set([r.ruleset_id for r in rows]))

    return rset_ids

def _comp_get_explicit_ruleset_ids(nodename):
    # attached to the node directly
    q = db.comp_rulesets_nodes.nodename == nodename
    rows = db(q).select(db.comp_rulesets_nodes.ruleset_id,
                        orderby=db.comp_rulesets_nodes.ruleset_id,
                        cacheable=True)
    rset_ids = [r.ruleset_id for r in rows]

    # attached to the node through modulesets
    modset_ids = _comp_get_moduleset_ids_with_children(nodename)
    q = db.comp_moduleset_ruleset.modset_id.belongs(modset_ids)
    rows = db(q).select(db.comp_moduleset_ruleset.ruleset_id)
    rset_ids = list(set(rset_ids) | set([r.ruleset_id for r in rows]))

    return rset_ids

def _comp_get_ruleset(nodename):
    # initialize ruleset with asset variables
    ruleset = comp_get_node_ruleset(nodename)

    rset_relations = get_rset_relations()
    rset_names = get_rset_names()

    # add contextual rulesets variables
    l = comp_get_rulesets_fset_ids(nodename=nodename)
    matching_fsets = comp_get_matching_fset_ids(fset_ids=l, nodename=nodename)
    ruleset.update(comp_contextual_rulesets(nodename=nodename,
                                            matching_fsets=matching_fsets,
                                            fset_ids=l,
                                            rset_relations=rset_relations,
                                            rset_names=rset_names))

    # add explicit rulesets variables
    rset_ids = _comp_get_explicit_ruleset_ids(nodename)
    for rset_id in rset_ids:
        ruleset.update(comp_ruleset_vars(rset_id,
                                         matching_fsets=matching_fsets,
                                         rset_relations=rset_relations,
                                         rset_names=rset_names))

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
    node = db(q).select(cacheable=True)
    if node is None:
        return ""
    node = node.first().mon_nodname
    return beautify_modulesets(msets, node)

def beautify_modulesets(msets, node):
    l = []
    for mset in msets:
        l.append(beautify_moduleset(mset, _comp_get_moduleset_modules(mset, node)))
    return SPAN(l, _class='xset')

class table_comp_status_svc(table_comp_status):
    def __init__(self, id=None, func=None, innerhtml=None):
        table_comp_status.__init__(self, id, func, innerhtml)
        self.hide_tools = True
        self.pageable = False
        self.bookmarkable = False
        self.commonalityable = False
        self.linkable = False
        self.checkboxes = False
        self.filterable = False
        self.exportable = False
        self.dbfilterable = False
        self.columnable = False
        self.refreshable = False
        self.wsable = False
        self.dataable = True
        self.cols.remove('run_status_log')
        self.child_tables = []
        self.force_cols = ["os_name"]

def ajax_svc_comp_status():
    tid = request.vars.table_id
    t = table_comp_status_svc(tid, 'ajax_svc_comp_status')
    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    for f in ['run_svcname']:
        q = _where(q, 'comp_status', t.filter_parse(f), f)
    if request.args[0] == "data":
        t.object_list = db(q).select(cacheable=True)
        return t.table_lines_data(-1, html=False)

def svc_comp_status(svcname):
    tid = 'scs_'+svcname
    t = table_comp_status_svc(tid, 'ajax_svc_comp_status')
    t.colprops['run_svcname'].force_filter = svcname

    return DIV(
      t.html(),
      SCRIPT(
        """osvc.tables["%(tid)s"]["on_change"] = function() {
            $("[name=%(tid)s_c_run_status]").bind("mouseover", function(){
             line = $(this).parents("tr")
             var s = line.children("[name=%(tid)s_c_run_status]")
             var e = line.children("[name=%(tid)s_c_run_log]")
             var pos = s.position()
             e.width($(window).width()*0.8)
             e.css({"left": pos.left - e.width() - 10 + "px", "top": pos.top+s.parent().height() + "px"})
             e.addClass("white_float")
             cell_decorator_run_log(e)
             e.show()
            })
            $("[name=%(tid)s_c_run_status]").bind("mouseout", function(){
             $(this).parents("tr").children("[name=%(tid)s_c_run_log]").hide()
            })
           }
        """ % dict(tid=t.id)
      ),
      _id=tid,
    )


class table_comp_status_node(table_comp_status):
    def __init__(self, id=None, func=None, innerhtml=None):
        table_comp_status.__init__(self, id, func, innerhtml)
        self.hide_tools = True
        self.pageable = False
        self.bookmarkable = False
        self.commonalityable = False
        self.linkable = False
        self.checkboxes = False
        self.filterable = False
        self.exportable = False
        self.dbfilterable = False
        self.columnable = False
        self.refreshable = False
        self.wsable = False
        self.dataable = True
        self.cols.remove('run_status_log')
        self.child_tables = []
        self.force_cols = ["os_name"]

def ajax_node_comp_status():
    tid = request.vars.table_id
    t = table_comp_status_node(tid, 'ajax_node_comp_status')
    q = _where(None, 'comp_status', domain_perms(), 'run_nodename')
    for f in ['run_nodename']:
        q = _where(q, 'comp_status', t.filter_parse(f), f)
    if request.args[0] == "data":
        t.object_list = db(q).select(cacheable=True)
        return t.table_lines_data(-1, html=False)

def node_comp_status(node):
    tid = 'ncs_'+node
    t = table_comp_status_node(tid, 'ajax_node_comp_status')
    t.colprops['run_nodename'].force_filter = node
    return DIV(
      t.html(),
      SCRIPT(
        """osvc.tables["%(tid)s"]["on_change"] = function() {
            $("[name=%(tid)s_c_run_status]").bind("mouseover", function(){
             line = $(this).parents("tr")
             var s = line.children("[name=%(tid)s_c_run_status]")
             var e = line.children("[name=%(tid)s_c_run_log]")
             var pos = s.position()
             e.width($(window).width()*0.8)
             e.css({"left": pos.left - e.width() - 10 + "px", "top": pos.top+s.parent().height() + "px"})
             e.addClass("white_float")
             cell_decorator_run_log(e)
             e.show()
            })
            $("[name=%(tid)s_c_run_status]").bind("mouseout", function(){
             $(this).parents("tr").children("[name=%(tid)s_c_run_log]").hide()
            })
           }
        """ % dict(tid=t.id)
      ),
      _id=tid,
    )

@auth.requires_login()
def ajax_rset_md5():
    session.forget(response)
    rset_md5 = request.vars.rset_md5
    row = db(db.comp_run_ruleset.rset_md5==rset_md5).select(cacheable=True).first()
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
    session.forget(response)
    svcname = request.args[0]
    msets = _comp_get_svc_moduleset(svcname)

    d = []
    q = db.svcmon.mon_svcname==svcname
    q &= db.svcmon.mon_updated > now - datetime.timedelta(days=1)
    rows = db(q).select(db.svcmon.mon_nodname, db.svcmon.mon_vmname,
                        cacheable=True)
    vnodes = set([r.mon_vmname for r in rows if r.mon_vmname is not None and r.mon_vmname != ""])
    nodes = set([r.mon_nodname for r in rows]) - vnodes

    vnodes = sorted(list(vnodes))
    nodes = sorted(list(nodes))

    def _one(node, slave=False):
        did = 'nrs_'+svcname.replace('.','').replace('-','')+'_'+node.replace('.','').replace('-','')
        n_rsets = _comp_get_svc_ruleset(svcname, node)
        n_rsets.update(comp_get_svcmon_ruleset(svcname, node))
        n_rsets.update(comp_get_node_ruleset(node))
        if slave:
            title = svcname + ' on slave node ', node
        else:
            title = svcname + ' on node ', node
        d.append(DIV(
                   B(title),
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

    for node in nodes:
        _one(node)
    for vnode in vnodes:
        _one(vnode, slave=True)

    did = 'srs_'+svcname.replace('.','').replace('-','')
    d = SPAN(
          H3(T('Status')),
          svc_comp_status(svcname),
          H3(T('Modulesets')),
          beautify_svc_modulesets(msets, svcname),
          H3(T('Rulesets')),
          SPAN(d),
          SPAN(show_diff(svcname)),
        )
    return d

@auth.requires_login()
def ajax_compliance_nodediff():
    nodes = request.vars.node.split(',')
    l = []
    compdiff = show_nodes_compdiff(nodes)
    moddiff = show_nodes_moddiff(nodes)
    rsetdiff = show_nodes_rsetdiff(nodes)

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

    return SPAN(l)

@auth.requires_login()
def ajax_compliance_svcdiff():
    svcnames = request.vars.node.split(',')
    l = []
    compdiff_svc = show_services_compdiff_svc(svcnames)
    compdiff_svc_encap = show_services_compdiff_svc(svcnames,encap=True)
    compdiff = show_services_compdiff(svcnames)
    compdiff_encap = show_services_compdiff(svcnames, encap=True)

    moddiff_svc = show_services_moddiff_svc(svcnames)
    moddiff_svc_encap = show_services_moddiff_svc(svcnames, encap=True)
    moddiff = show_services_moddiff(svcnames)
    moddiff_encap = show_services_moddiff(svcnames, encap=True)

    rsetdiff_svc = show_services_rsetdiff_svc(svcnames)
    rsetdiff_svc_encap = show_services_rsetdiff_svc(svcnames, encap=True)
    rsetdiff = show_services_rsetdiff(svcnames)
    rsetdiff_encap = show_services_rsetdiff(svcnames, encap=True)

    if compdiff_svc is not None or \
       compdiff_svc_encap is not None or \
       compdiff is not None or \
       compdiff_encap is not None or \
       moddiff_svc is not None or \
       moddiff_svc_encap is not None or \
       moddiff is not None or \
       moddiff_encap is not None or \
       rsetdiff_svc is not None or \
       rsetdiff_svc_encap is not None or \
       rsetdiff is not None or \
       rsetdiff_encap is not None:
        l.append(HR())

    if compdiff_svc is not None:
        l.append(SPAN(
          H3(T('Module status differences amongst services')),
          compdiff_svc))

    if compdiff_svc_encap is not None:
        l.append(SPAN(
          H3(T('Module status differences amongst encapsulated services')),
          compdiff_svc_encap))

    if compdiff is not None:
        l.append(SPAN(
          H3(T('Module status differences in cluster')),
          compdiff))

    if compdiff_encap is not None:
        l.append(SPAN(
          H3(T('Module status differences in encapsulated cluster')),
          compdiff_encap))

    if moddiff_svc is not None:
        l.append(SPAN(
          H3(T('Moduleset attachment differences amongst services')),
          moddiff_svc))

    if moddiff_svc_encap is not None:
        l.append(SPAN(
          H3(T('Moduleset attachment differences amongst encapsulated services')),
          moddiff_svc_encap))

    if moddiff is not None:
        l.append(SPAN(
          H3(T('Moduleset attachment differences in cluster')),
          moddiff))

    if moddiff_encap is not None:
        l.append(SPAN(
          H3(T('Moduleset attachment differences in encapsulated cluster')),
          moddiff_encap))

    if rsetdiff_svc is not None:
        l.append(SPAN(
          H3(T('Ruleset attachment differences amongst services')),
          rsetdiff_svc))

    if rsetdiff_svc_encap is not None:
        l.append(SPAN(
          H3(T('Ruleset attachment differences amongst encapsulated services')),
          rsetdiff_svc_encap))

    if rsetdiff is not None:
        l.append(SPAN(
          H3(T('Ruleset attachment differences in cluster')),
          rsetdiff))

    if rsetdiff_encap is not None:
        l.append(SPAN(
          H3(T('Ruleset attachment differences in encapsulated cluster')),
          rsetdiff_encap))

    return SPAN(l)

def show_diff(svcname):
    l = []
    compdiff = show_compdiff(svcname)
    compdiff_encap = show_compdiff(svcname, encap=True)
    moddiff = show_moddiff(svcname)
    moddiff_encap = show_moddiff(svcname, encap=True)
    rsetdiff = show_rsetdiff(svcname)
    rsetdiff_encap = show_rsetdiff(svcname, encap=True)

    if compdiff is not None or moddiff is not None or rsetdiff is not None or \
       compdiff_encap is not None or moddiff_encap is not None or rsetdiff_encap is not None:
        l.append(HR())

    if compdiff is not None:
        l.append(SPAN(
          H3(T('Module status differences in cluster')),
          compdiff))

    if compdiff_encap is not None:
        l.append(SPAN(
          H3(T('Module status differences in encapsulated cluster')),
          compdiff_encap))

    if moddiff is not None:
        l.append(SPAN(
          H3(T('Moduleset attachment differences in cluster')),
          moddiff))

    if moddiff_encap is not None:
        l.append(SPAN(
          H3(T('Moduleset attachment differences in encapsulated cluster')),
          moddiff_encap))

    if rsetdiff is not None:
        l.append(SPAN(
          H3(T('Ruleset attachment differences in cluster')),
          rsetdiff))

    if rsetdiff_encap is not None:
        l.append(SPAN(
          H3(T('Ruleset attachment differences in encapsulated cluster')),
          rsetdiff_encap))

    return l

@auth.requires_login()
def ajax_compliance_node():
    session.forget(response)
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
                        db.comp_rulesets_variables.var_value,
                        cacheable=True)
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
        table_modified("comp_status")

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
    table_modified("comp_status")


#
# Dashboard alerts
#
def cron_dash_comp():
    cron_dash_moddiff()
    cron_dash_rsetdiff()

def show_nodes_compdiff(nodes):
    nodes = list(set(nodes))
    nodes.sort()
    n = len(nodes)

    if n < 2:
        return

    sql = """select t.* from (
               select
                 count(distinct cs.run_nodename) as c,
                 cs.run_module,
                 cs.run_nodename,
                 cs.run_status
               from
                 comp_status cs
               where
                 cs.run_nodename in (%(nodes)s)
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
              """%dict(nodes=','.join(map(lambda x: repr(str(x)), nodes)), n=n)

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
               comp_status cs
             where
               cs.run_module in (%(mods)s) and
               cs.run_nodename in (%(nodes)s)
             order by
               cs.run_module,
               cs.run_nodename
         """%dict(nodes=','.join(map(lambda x: repr(x), nodes)), mods=','.join(map(lambda x: repr(str(x)), mods)))
    _rows = db.executesql(sql)

    if len(_rows) == 0:
        return

    return _show_compdiff(nodes, n, _rows)

def show_services_compdiff_svc(svcnames, encap=False):
    svcnames = list(set(svcnames))
    svcnames.sort()
    n = len(svcnames)

    if n < 2:
        return

    if encap:
        sql = """select
                   concat(mon_svcname, '@', mon_vmname)
                 from svcmon
                 where
                   mon_vmname is not null and
                   mon_vmname != "" and
                   mon_svcname in (%(svcnames)s)
                 group by
                   mon_svcname, mon_vmname
              """ % dict(svcnames=','.join(map(lambda x: repr(x), svcnames)))
    else:
        sql = """select
                   concat(mon_svcname, '@', mon_nodname)
                 from svcmon
                 where
                   mon_svcname in (%(svcnames)s)
                 group by
                   mon_svcname, mon_nodname
              """ % dict(svcnames=','.join(map(lambda x: repr(x), svcnames)))

    _rows = db.executesql(sql)
    objs = list(set([r[0] for r in _rows]))
    n = len(objs)

    if n < 2:
        return

    sql = """select t.* from (
               select
                 count(distinct u.obj) as c,
                 u.run_module,
                 u.run_svcname,
                 u.run_status
               from (
                 select
                   concat(cs.run_svcname, '@', cs.run_nodename) as obj,
                   cs.run_module,
                   cs.run_svcname,
                   cs.run_status
                 from comp_status cs
                 where
                   concat(cs.run_svcname, '@', cs.run_nodename) in (%(objs)s)
               ) u
               group by
                 u.run_module,
                 u.run_status
              ) as t
              where
                t.c!=%(n)s
              order by
                t.run_module,
                t.run_svcname,
                t.run_status
              """%dict(objs=','.join(map(lambda x: repr(str(x)), objs)), n=n)

    _rows = db.executesql(sql)
    if len(_rows) == 0:
        return

    mods = [r[1] for r in _rows]

    sql = """select
               concat(cs.run_svcname, '@', cs.run_nodename),
               cs.run_module,
               cs.run_status,
               cs.run_log,
               cs.run_date
             from
               comp_status cs
             where
               cs.run_module in (%(mods)s) and
               concat(cs.run_svcname, '@', cs.run_nodename) in (%(objs)s)
             order by
               cs.run_module,
               cs.run_svcname,
               cs.run_nodename
         """%dict(objs=','.join(map(lambda x: repr(str(x)), objs)), mods=','.join(map(lambda x: repr(str(x)), mods)))
    _rows = db.executesql(sql)

    if len(_rows) == 0:
        return

    return _show_compdiff(objs, n, _rows, "Service@Node")

def show_services_compdiff(svcnames, encap=False):
    rows = db(db.svcmon.mon_svcname.belongs(svcnames)).select(cacheable=True)
    if encap:
        nodes = [r.mon_vmname for r in rows if r.mon_vmname != "" and r.mon_vmname is not None]
        f = "mon_vmname"
    else:
        nodes = [r.mon_nodname for r in rows]
        f = "mon_nodname"
    nodes = list(set(nodes))
    nodes.sort()
    n = len(nodes)

    if n < 2:
        return

    sql = """select t.* from (
               select
                 count(distinct cs.run_nodename) as c,
                 cs.run_module,
                 cs.run_nodename,
                 cs.run_status
               from
                 comp_status cs,
                 svcmon m
               where
                 m.mon_svcname in (%(svcnames)s) and
                 m.%(f)s=cs.run_nodename
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
              """%dict(svcnames=','.join(map(lambda x: repr(x), svcnames)), n=n, f=f)

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
               cs.run_module in (%(mods)s) and
               m.mon_svcname in (%(svcnames)s) and
               m.%(f)s=cs.run_nodename
             order by
               cs.run_module,
               cs.run_nodename
         """%dict(svcnames=','.join(map(lambda x: repr(x), svcnames)), mods=','.join(map(lambda x: repr(str(x)), mods)), f=f)
    _rows = db.executesql(sql)

    if len(_rows) == 0:
        return

    return _show_compdiff(nodes, n, _rows)

def show_compdiff(svcname, encap=False):
    rows = db(db.svcmon.mon_svcname==svcname).select(cacheable=True)
    if encap:
        nodes = [r.mon_vmname for r in rows if r.mon_vmname != "" and r.mon_vmname is not None]
        f = "mon_vmname"
    else:
        nodes = [r.mon_nodname for r in rows]
        f = "mon_nodname"
    nodes = list(set(nodes))
    nodes.sort()
    n = len(nodes)

    if n < 2:
        return

    sql = """select t.* from (
               select
                 count(distinct cs.run_nodename) as c,
                 cs.run_module,
                 cs.run_nodename,
                 cs.run_status
               from
                 comp_status cs,
                 svcmon m
               where
                 (cs.run_svcname is NULL or cs.run_svcname="") and
                 m.mon_svcname="%(svcname)s" and
                 m.%(f)s=cs.run_nodename
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
              """%dict(svcname=svcname, n=n, f=f)

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
               m.%(f)s=cs.run_nodename
             order by
               cs.run_module,
               cs.run_nodename
         """%dict(svcname=svcname, mods=','.join(map(lambda x: repr(str(x)), mods)), f=f)
    _rows = db.executesql(sql)

    if len(_rows) == 0:
        return

    return _show_compdiff(nodes, n, _rows)

def _show_compdiff(nodes, n, _rows, objtype="Nodes"):
    data = {}
    for row in _rows:
        module = row[1]
        if module not in data:
            data[module] = {}
        data[module][row[0]] = row

    def fmt_header1():
        return TR(
                 TH("", _colspan=1),
                 TH(T(objtype), _colspan=n, _style="text-align:center"),
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
         if t is None or t == '': return False
         if t < deadline: return True
         return False

    def fmt_line(module, rows, bg):
        h = [TD(module)]
        for row in rows:
            if outdated(row[4]):
                d = ';background-color:lightgrey'
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
    svcnames = [r.svc_name for r in db(q).select(db.services.svc_name, cacheable=True)]

    r = []
    for svcname in svcnames:
        r.append(update_dash_moddiff(svcname))

    return str(r)

def show_nodes_moddiff(nodes):
    nodes = list(set(nodes))
    nodes.sort()
    n = len(nodes)

    if n < 2:
        return

    sql = """
            select t.* from
            (
             select
               count(distinct nm.modset_node) as n,
               group_concat(distinct nm.modset_node) as nodes,
               ms.modset_name as modset
             from
               comp_node_moduleset nm,
               comp_moduleset ms
             where
               nm.modset_node in (%(nodes)s) and
               nm.modset_id=ms.id
             group by
               modset_name
             order by
               modset_name
            ) t
            where t.n != %(n)d
    """%dict(nodes=','.join(map(lambda x: repr(x), nodes)), n=n)
    _rows = db.executesql(sql)
    return _show_moddiff(nodes, n, _rows)

def show_services_moddiff_svc(svcnames, encap=False):
    if encap:
        slave = 'T'
    else:
        slave = 'F'
    svcnames = list(set(svcnames))
    svcnames.sort()
    n = len(svcnames)

    if n < 2:
        return

    sql = """
            select t.* from
            (
             select
               count(distinct ms.modset_svcname) as n,
               group_concat(distinct ms.modset_svcname) as services,
               m.modset_name as modset
             from
               comp_modulesets_services ms,
               comp_moduleset m
             where
               ms.modset_svcname in (%(svcnames)s) and
               ms.slave="%(slave)s" and 
               ms.modset_id=m.id
             group by
               modset_name
             order by
               modset_name
            ) t
            where t.n != %(n)d
    """%dict(svcnames=','.join(map(lambda x: repr(x), svcnames)), n=n, slave=slave)
    _rows = db.executesql(sql)
    return _show_moddiff(svcnames, n, _rows, "Services")

def show_services_moddiff(svcnames, encap=False):
    rows = db(db.svcmon.mon_svcname.belongs(svcnames)).select(cacheable=True)
    if encap:
        nodes = [r.mon_vmname for r in rows if r.mon_vmname != "" and r.mon_vmname is not None]
        f = "mon_vmname"
    else:
        nodes = [r.mon_nodname for r in rows]
        f = "mon_nodname"
    nodes = list(set(nodes))
    nodes.sort()
    n = len(nodes)

    if n < 2:
        return

    sql = """
            select t.* from
            (
             select
               count(distinct nm.modset_node) as n,
               group_concat(distinct nm.modset_node) as nodes,
               ms.modset_name as modset
             from
               comp_node_moduleset nm,
               svcmon m,
               comp_moduleset ms
             where
               m.mon_svcname in (%(svcnames)s) and
               m.%(f)s=nm.modset_node and
               nm.modset_id=ms.id
             group by
               modset_name
             order by
               modset_name
            ) t
            where t.n != %(n)d
    """%dict(svcnames=','.join(map(lambda x: repr(x), svcnames)), n=n, f=f)
    _rows = db.executesql(sql)
    return _show_moddiff(nodes, n, _rows)

def show_moddiff(svcname, encap=False):
    rows = db(db.svcmon.mon_svcname==svcname).select(cacheable=True)
    if encap:
        nodes = [r.mon_vmname for r in rows if r.mon_vmname != "" and r.mon_vmname is not None]
        f = "mon_vmname"
    else:
        nodes = [r.mon_nodname for r in rows]
        f = "mon_nodname"
    nodes = list(set(nodes))
    nodes.sort()
    n = len(nodes)

    if n < 2:
        return

    sql = """
            select t.* from
            (
             select
               count(distinct nm.modset_node) as n,
               group_concat(distinct nm.modset_node) as nodes,
               ms.modset_name as modset
             from
               comp_node_moduleset nm,
               svcmon m,
               comp_moduleset ms
             where
               m.mon_svcname="%(svcname)s" and
               m.%(f)s=nm.modset_node and
               nm.modset_id=ms.id
             group by
               modset_name
             order by
               modset_name
            ) t
            where t.n != %(n)d
    """%dict(svcname=svcname, n=n, f=f)
    _rows = db.executesql(sql)
    return _show_moddiff(nodes, n, _rows)

def _show_moddiff(nodes, n, _rows, objtype="Nodes"):

    if len(_rows) == 0:
        return

    def fmt_header1():
        return TR(
                 TH("", _colspan=1),
                 TH(T(objtype), _colspan=n, _style="text-align:center"),
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
    svcnames = [r.svc_name for r in db(q).select(db.services.svc_name, cacheable=True)]

    r = []
    for svcname in svcnames:
        r.append(update_dash_rsetdiff(svcname))

    return str(r)

def show_nodes_rsetdiff(nodes):
    nodes = list(set(nodes))
    nodes.sort()
    n = len(nodes)

    if n < 2:
        return

    sql = """
            select t.* from
            (
             select
               count(distinct rn.nodename) as n,
               group_concat(distinct rn.nodename) as nodes,
               rs.ruleset_name as ruleset
             from
               comp_rulesets_nodes rn,
               comp_rulesets rs
             where
               rn.nodename in (%(nodes)s) and
               rn.ruleset_id=rs.id
             group by
               ruleset_name
             order by
               ruleset_name
            ) t
            where t.n != %(n)d
    """%dict(nodes=','.join(map(lambda x: repr(str(x)), nodes)), n=n)
    _rows = db.executesql(sql)

    return _show_rsetdiff(nodes, n, _rows)

def show_services_rsetdiff_svc(svcnames, encap=False):
    svcnames = list(set(svcnames))
    svcnames.sort()
    n = len(svcnames)
    if encap:
        slave = 'T'
    else:
        slave = 'F'

    if n < 2:
        return

    sql = """
            select t.* from
            (
             select
               count(distinct rss.svcname) as n,
               group_concat(distinct rss.svcname) as services,
               rs.ruleset_name as ruleset
             from
               comp_rulesets_services rss,
               comp_rulesets rs
             where
               rss.svcname in (%(svcnames)s) and
               rss.slave="%(slave)s" and
               rss.ruleset_id=rs.id
             group by
               ruleset_name
             order by
               ruleset_name
            ) t
            where t.n != %(n)d
    """%dict(svcnames=','.join(map(lambda x: repr(x), svcnames)), n=n, slave=slave)
    _rows = db.executesql(sql)

    return _show_rsetdiff(svcnames, n, _rows, "Services")

def show_services_rsetdiff(svcnames, encap=False):
    rows = db(db.svcmon.mon_svcname.belongs(svcnames)).select(cacheable=True)
    if encap:
        nodes = [r.mon_vmname for r in rows if r.mon_vmname != "" and r.mon_vmname is not None]
        f = "mon_vmname"
    else:
        nodes = [r.mon_nodname for r in rows]
        f = "mon_nodname"
    nodes = list(set(nodes))
    nodes.sort()
    n = len(nodes)

    if n < 2:
        return

    sql = """
            select t.* from
            (
             select
               count(distinct rn.nodename) as n,
               group_concat(distinct rn.nodename) as nodes,
               rs.ruleset_name as ruleset
             from
               comp_rulesets_nodes rn,
               svcmon m,
               comp_rulesets rs
             where
               m.mon_svcname in (%(svcnames)s) and
               m.%(f)s=rn.nodename and
               rn.ruleset_id=rs.id
             group by
               ruleset_name
             order by
               ruleset_name
            ) t
            where t.n != %(n)d
    """%dict(svcnames=','.join(map(lambda x: repr(x), svcnames)), n=n, f=f)
    _rows = db.executesql(sql)

    return _show_rsetdiff(nodes, n, _rows)


def show_rsetdiff(svcname, encap=False):
    rows = db(db.svcmon.mon_svcname==svcname).select(cacheable=True)
    if encap:
        nodes = [r.mon_vmname for r in rows if r.mon_vmname != "" and r.mon_vmname is not None]
        f = "mon_vmname"
    else:
        nodes = [r.mon_nodname for r in rows]
        f = "mon_nodname"
    nodes = list(set(nodes))
    nodes.sort()
    n = len(nodes)

    if n < 2:
        return

    sql = """
            select t.* from
            (
             select
               count(distinct rn.nodename) as n,
               group_concat(distinct rn.nodename) as nodes,
               rs.ruleset_name as ruleset
             from
               comp_rulesets_nodes rn,
               svcmon m,
               comp_rulesets rs
             where
               m.mon_svcname="%(svcname)s" and
               m.%(f)s=rn.nodename and
               rn.ruleset_id=rs.id
             group by
               ruleset_name
             order by
               ruleset_name
            ) t
            where t.n != %(n)d
    """%dict(svcname=svcname, n=n, f=f)
    _rows = db.executesql(sql)

    return _show_rsetdiff(nodes, n, _rows)

def _show_rsetdiff(nodes, n, _rows, objtype="Nodes"):
    if len(_rows) == 0:
        return

    def fmt_header1():
        return TR(
                 TH("", _colspan=1),
                 TH(T(objtype), _colspan=n, _style="text-align:center"),
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

def ajax_info(msg, to_session=False):
    if type(msg) == list:
        l = []
        rets = [0, 0]
        for e in msg:
            rets[e[0]] += 1
            if e[0] == 0:
                img = 'check16.png'
            else:
                img = 'nok.png'
            status = IMG(
                       _src=URL(c='static', f=img),
                       _style="padding-right:0.5em;vertical-align:bottom",
                     )
            try:
                _msg = TT(
                  T(e[2], e[3]),
                  _style="white-space:pre-wrap",
                )
            except Exception as e:
                _msg = str(e)
            d = DIV(
                  status,
                  SPAN(_msg),
                )
            l.append(d)
        if rets[1] == 0:
            img = 'check16.png'
            s = 'Success'
            cl = 'foldme hidden'
        else:
            img = 'nok.png'
            s = 'Errors'
            cl = 'foldme'
        status = DIV(
                   IMG(
                     _src=URL(c='static', f=img),
                     _style="padding-right:0.5em;vertical-align:bottom",
                   ),
                   SPAN(
                     T(s),
                   ),
                   _onclick="if (event.stopPropagation) {event.stopPropagation()};$(this).parent().find('.foldme').toggle(400)",
                   _class="clickable",
                 )
        out = DIV(
                status,
                DIV(
                  HR(),
                  SPAN(l),
                  _class=cl,
                ),
              )
    else:
        out = msg

    d = DIV(
          out,
          _class="box",
          _style="text-align:left;padding:3em",
        )

    if to_session:
        session.flash = d

    return d

def ajax_error(msg):
    if type(msg) == list:
        out = PRE('\n\n'.join(msg))
    else:
        out = msg

    d = DIV(
             out,
             _class="box",
             _style="text-align:left;padding:3em",
           )
    #session.flash = d
    return d

def inputs_block(data, idx=0, defaults=None, display_mode=False, display_detailed=False, showexpert=False, display_digest=False):
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

        if default == '__user_name__':
            default = user_name()
        elif default == '__user_phone_work__':
            default = user_phone_work()
        elif default == '__user_primary_group__':
            default = user_primary_group()
        elif default == '__user_email__':
            default = user_email()

        if type(default) == list:
            default = ','.join(default)

        if type(default) in (str, unicode):
            try:
                default = default.encode('utf-8')
            except:
                pass

        if 'LabelCss' in input:
            lcl = input['LabelCss']
        else:
            lcl = ""
        if 'Css' in input:
            cl = input['Css']
        else:
            cl = ""

        if 'Help' in input and input['Help'] is not None and len(input['Help']) > 0:
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
            #if not display_detailed and \
            #   data['Outputs'][0].get('Format') in ('list of dict', 'dict of dict'):
            #    if type(default) in (unicode, str) and len(default) > 25:
            #        s = default[:10]+"..."+default[-12:]
            #    else:
            #        s = default
            #    _input = SPAN(s, _title=default)
            #else:
            #    _input = SPAN(default)
            _input = SPAN(default)
            _help = ""
        elif 'Candidates' in input and not input.get('ReadOnly', False):
            if input['Candidates'] == "__node_selector__":
                if 'Manager' not in user_groups():
                    q = db.nodes.team_responsible.belongs(user_groups())
                else:
                    q = db.nodes.id > 0
                o = db.nodes.project | db.nodes.nodename
                rows = db(q).select(db.nodes.project, db.nodes.nodename,
                                    orderby=o, cacheable=True)
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
                                        orderby=o,
                                        cacheable=True)
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
                elif type(o) == dict and 'Value' in o and o['Value'] != "":
                    candidates = [{'Value':'','Label':''}] + candidates
                elif o != "":
                    candidates = [''] + candidates

            max = 10
            for o in candidates:
                if type(o) in (list, tuple):
                    label, value = o
                elif type(o) == dict and 'Value' in o and 'Label' in o:
                    value = o['Value']
                    label = o['Label']
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
            if input.get('ReadOnly', False):
                attr['_readonly'] = 'on'
                attr['_style'] = 'height:1.3em'
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
            if input.get('ReadOnly', False):
                attr['_readonly'] = 'on'
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
            if input.get('ReadOnly', False):
                attr['_readonly'] = 'on'
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
            if input.get('ReadOnly', False):
                attr['_readonly'] = 'on'
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
            if input.get('ReadOnly', False):
                attr['_readonly'] = 'on'
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
            elif not input.get('DisplayInDigest', False) and display_digest:
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
$(this).parents("[name=instance]").first().prev('hr').remove()
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
        display_digest = False
    elif _mode == "digest":
        display_mode = True
        display_detailed = False
        display_digest = True
    elif _mode == "showdetailed":
        display_mode = True
        display_detailed = True
        display_digest = False
    else:
        display_mode = False
        display_detailed = False
        display_digest = False

    prev_form = None
    if _var_id is None and _prev_wfid is not None and _prev_wfid != 'None':
        # next step of a workflow use previous form values as defaults
        q = db.forms_store.id == request.vars.prev_wfid
        prev_form = db(q).select(cacheable=True).first()
        if prev_form is not None and prev_form.form_var_id is not None:
            _var_id = prev_form.form_var_id

    if var is None and _var_id is not None:
        q = db.v_comp_rulesets.id == _var_id
        var = db(q).select(cacheable=True).first()
        if var is None:
            if _prev_wfid is not None and _prev_wfid != 'None':
                q = db.forms_store.id == _prev_wfid
                db(q).update(form_next_id=0)
                q = db.workflows.last_form_id == _prev_wfid
                db(q).update(status="closed")
                db.commit()
            return ajax_error(T("variable '%(id)s' not found", dict(id=_var_id)))

    if var is not None and _form_id is None:
        form_name = var.var_class
    else:
        form_name = _form_name

    if form is not None:
        pass
    elif form_name is not None:
        q = db.forms.form_name == form_name
        form = db(q).select(cacheable=True).first()
    elif _form_id is not None:
        q = db.forms.id == _form_id
        form = db(q).select(cacheable=True).first()
    elif _wfid is not None:
        q = db.forms_store.id == _wfid
        form = db(q).select(cacheable=True).first()
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
        row = db(q).select(cacheable=True).first()
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
                cur = {}
                #return ajax_error("json error parsing current variable value '%s'"%cur)
            if form_output.get('Format') == 'dict':
                for i, input in enumerate(data['Inputs']):
                    id = input.get('Id')
                    _def = input.get('Default')
                    if id is None or _def is None:
                        continue
                    if id not in cur or input.get('Override', False):
                        cur[id] = _def
    elif 'form_data' in form:
        cur = json.loads(form.form_data)
    elif prev_form is not None and 'form_data' in prev_form:
        cur = json.loads(prev_form.form_data)
    elif current_values is not None:
        cur = current_values

    l = []
    if form_output.get('Format') == 'dict':
        l = inputs_block(data,
                         defaults=cur,
                         display_mode=display_mode,
                         display_digest=display_digest,
                         showexpert=showexpert)
    elif form_output.get('Format') in ('list', 'list of dict', 'dict of dict'):
        if cur is None or len(cur) == 0:
            count = 1
            _l = inputs_block(data, display_mode=display_mode,
                              display_detailed=display_detailed,
                              display_digest=display_digest,
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
                                       display_digest=display_digest,
                                       showexpert=showexpert))
                if not display_mode and i != len(cur) - 1:
                    _l.append(HR())
        if display_mode:
            l = TABLE(_l, _class="nowrap")
        else:
            l = _l
    else:
        l = inputs_block(data,
                         defaults=cur,
                         display_mode=display_mode,
                         display_digest=display_digest,
                         showexpert=showexpert)

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
container = ref.parents('#%(container)s').first()
container.append("<hr />")
clone.appendTo(container)
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

    if not showexpert and has_expert(data):
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
            callback = """function(){window.location="%s"}"""%URL(c='forms', f='workflow', vars={'wfid': _prev_wfid, 'tail':1})
            #callback = "function(){}"
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
$(this).attr('disabled', true)
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
$("#rset").each(function(){
  ids.push("rset")
});
function reload_ajax_custo(){
  $("select#svcname").change()
  $("select#nodename").change()
  $("select#rset").change()
  $("#%(xid)scontainer").siblings().find("input:submit").attr('disabled', false)
}
$(%(rid)s).html("")
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
  form_submit_toggle(o)
}

function refresh_select(e) {
  return function(data) {
    if (typeof(data) == "string") {
      e.find('option:selected').removeAttr('selected')
      e.val(data).attr('selected', true)
      e.find("option:contains('" + data + "')").each(function(){
        if ($(this).text() == data) {
          $(this).attr('selected', true);
        }
      });
    } else {
      e.find('option').remove()
      for (i=0;i<data.length;i++) {
        if (typeof(data[i]) == "string") {
          var _label = data[i]
          var _value = data[i]
        } else {
          var _value = data[i][0]
          var _label = data[i][1]
        }
        e.find('option').end().append("<option value='"+_value+"'>"+_label+"</option>")
      }
    }
    e.combobox()
    e.trigger('change')
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
    e.trigger('change')
  };
}

function refresh_input(e) {
  return function(data) {
    if (data instanceof Array) {
      s = data.join("\\n")
    } else {
      s = data
    }
    e.val(s)
    e.trigger('change')
  };
}

function refresh_textarea(e) {
  return function(data) {
    h = 1.3
    if (data instanceof Array) {
      s = data.join("\\n")
      if (data.length > 2) {
        h = 1.3 * data.length
      }
    } else {
      s = data
    }
    e.val(s)
    e.height(h+'em')
    e.trigger('change')
  };
}

function form_submit_toggle (o) {
  n = 0
  $(o).parents('table').first().find("tr").each(function(){
    if ($(this).hasClass("highlight_input") || $(this).hasClass("highlight_input1")) {
      $(o).parents('[name=container_head]').first().find("input[type=submit]").attr("disabled", "disabled")
      n++
      return
    }
  })
  if (n==0) {
    $(o).parents('[name=container_head]').first().find("input[type=submit]").removeAttr("disabled")
  }
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
      if ($('#'+id).get(0).tagName == 'SELECT') {
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
    } else if ($(this).get(0).tagName == 'INPUT') {
      $.getJSON(url, refresh_input($(this)))
    } else if ($(this).get(0).tagName == 'TEXTAREA') {
      $.getJSON(url, refresh_textarea($(this)))
    } else {
      $.getJSON(url, refresh_div($(this)))
    }
  })
}

function form_inputs_mandatory (o) {
  $(o).parents('table').first().find("[mandatory=mandatory]").each(function(){
    if ($(this).get(0).tagName == 'SELECT') {
      val = $(this).find("option:selected").val()
    } else {
      val = $(this).val()
    }
    if (val == undefined || val.length == 0) {
      $(this).parents('tr').first().addClass("highlight_input1")
    } else {
      $(this).parents('tr').first().removeClass("highlight_input1")
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
    val = $(this).siblings().children('input[name^=%(xid)s],select[name^=%(xid)s],textarea[name^=%(xid)s]').val()
    if (op == ">") {
      tgt = l[1]
      if (1.0*val <= 1.0*tgt) {
        $(this).parents('tr').first().addClass("highlight_input")
        $(this).show()
        return
      }
    } else if (op == "match") {
      pattern = constraint.replace(/match */, "")
      re = new RegExp(pattern)
      if (!re.test(val)) {
        $(this).parents('tr').first().addClass("highlight_input")
        $(this).show()
        return
      }
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
$("input[name^=%(xid)s][readonly=on],select[name^=%(xid)s][readonly=on],textarea[name^=%(xid)s][readonly=on]").trigger('change')
"""%dict(
     idx=len(l),
     xid=forms_xid(''),
     url=str(URL(r=request, c='forms', f='a'))[:-2],
    ),
               _name=str(_hid)+"_to_eval",
             ),
        )

    return DIV(
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
    form_id = request.vars.form_id
    q = db.forms.id == form_id
    row = db(q).select(cacheable=True).first()
    form_type = row.form_type

    if form_type == "obj":
        q_rset = SPAN(
          TD(
            INPUT(
              _value=False,
              _type='radio',
              _id="radio_rset",
              _onclick="""
$("#radio_service").prop('checked',false);
$("#radio_node").prop('checked',false);
$("#stage2").html("");
sync_ajax('%(url)s', [], '%(id)s', function(){})"""%dict(
                id="stage1",
                url=URL(r=request, c='forms', f='ajax_rset_list', vars={'form_id': request.vars.form_id}),
              ),
            ),
          ),
          TD(
            T("Customize ruleset"),
          ),
        )

    else:
        q_rset = SPAN()

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
$("#radio_rset").prop('checked',false);
$("#stage2").html("");
sync_ajax('%(url)s', [], '%(id)s', function(){})"""%dict(
                id="stage1",
                url=URL(r=request, c='forms', f='ajax_service_list', vars={'form_id': request.vars.form_id}),
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
$("#radio_rset").prop('checked',false);
$("#stage2").html("");
sync_ajax('%(url)s', [], '%(id)s', function(){})"""%dict(
                id="stage1",
                url=URL(r=request, c='forms', f='ajax_node_list', vars={'form_id': request.vars.form_id}),
              ),
            ),
          ),
          TD(
            T("Customize node"),
          ),
          q_rset,
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
    form_id = request.vars.form_id

    if len(request.args) < 2:
        return ajax_error("Need two parameters")

    target = request.args[0]
    if target is None:
        return ajax_error("No target specified")

    if target == "nodename":
        rset_name = "node." + request.args[1]
    elif target == "svcname":
        rset_name = "svc." + request.args[1]
    elif target == "rset":
        rset_name = request.args[1]
    else:
        return ajax_error("Incorrect target specified. Must be either 'nodename' or 'svcname'")

    #q = db.forms.form_type == "custo"
    q = db.forms.form_name == db.comp_rulesets_variables.var_class
    q &= db.comp_rulesets_variables.ruleset_id == db.comp_rulesets.id
    q &= db.comp_rulesets.ruleset_name == rset_name
    o = db.comp_rulesets_variables.var_class

    rows = db(q).select(orderby=o, cacheable=True)

    l = []
    for row in rows:
        l.append(format_custo(row, target, request.args[1], form_id))

    if len(l) == 0:
        return T("No customization yet")

    return DIV(
             H2(T("Current customizations")),
             SPAN(l),
           )

def format_custo(row, objtype, objname, form_id=None):
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
        _mode="digest",
        _rset_name=row.comp_rulesets.ruleset_name,
        _var_id=row.comp_rulesets_variables.id,
        _form_xid=row.comp_rulesets_variables.id,
        _hid='stage2',
        var=row.comp_rulesets_variables,
        form=row.forms,
        showexpert=False,
      ),
      _onclick="""
sync_ajax("%(url)s", [], "forms_inputs", function(){})
""" % dict(
  url=URL(
    r=request, c='compliance', f='ajax_forms_inputs',
    vars={
      "mode": "edit",
      "form_id": form_id,
      "hid": "forms_inputs",
      "rset_name": row.comp_rulesets.ruleset_name,
      "var_id": row.comp_rulesets_variables.id,
    }
  ),
),
    )

    if 'Modulesets' in data:
        q = db.comp_status.id > 0
        if objtype == "svcname":
            l = _comp_get_moduleset_svc_modules(data['Modulesets'], objname)
            q = db.comp_status.run_svcname == objname
        elif objtype == "nodename":
            l = _comp_get_moduleset_modules(data['Modulesets'], objname)
            q = db.comp_status.run_nodename == objname
        else:
            l = []
        q &= db.comp_status.run_module.belongs(l)
        rows = db(q).select(cacheable=True)
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

def get_form_formatted_data(output, data, _d=None):
    output_value = get_form_formatted_data_o(output, data, _d)

    if output.get('Type') == "json":
        output_value = json.dumps(output_value)

    return output_value

def get_form_formatted_data_o(output, data, _d=None):
    if _d is not None:
        return _d

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
            for v in sorted(request.vars.keys()):
                if not v.startswith(forms_xid(input['Id'])):
                    continue
                val = request.vars.get(v)
                if len(str(val)) == 0:
                    if input.get('Mandatory', False):
                        raise Exception(T("Input '%(input)s' is mandatory", dict(input=input.get('Id'))))
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
                    if input.get('Mandatory', False):
                        raise Exception(T("Input '%(input)s' is mandatory", dict(input=input.get('Id'))))
                    continue
                if len(str(val)) == 0:
                    if input.get('Mandatory', False):
                        raise Exception(T("Input '%(input)s' is mandatory", dict(input=input.get('Id'))))
                    continue
                try:
                    val = convert_val(val, input['Type'])
                except Exception, e:
                    raise Exception(T(str(e)))
                if input.get('Type', 'string') != 'integer' or val != "":
                    h[input['Id']] = val
            output_value = h
        elif output.get('Format') == "list of dict":
            h = {}
            idxs = []
            for v in sorted(request.vars.keys()):
                for input in data['Inputs']:
                    if not v.startswith(forms_xid(input['Id'])):
                        continue
                    idx = v.replace(forms_xid(input['Id'])+'_', '')
                    try:
                        int(idx)
                    except:
                        # wrong input, with same prefix.
                        continue
                    if idx not in h:
                        h[idx] = {}
                        idxs.append(idx)
                    val = request.vars.get(v)
                    if len(str(val)) == 0:
                        if 'Mandatory' in input and input['Mandatory']:
                            raise Exception(T("Input '%(input)s' is mandatory (instance %(inst)s)", dict(input=input.get('Id'), inst=idx)))
                    try:
                        val = convert_val(val, input.get('Type', 'string'))
                    except Exception, e:
                        raise Exception(T(str(e)))
                    if input.get('Type', 'string') != 'integer' or val != "":
                        h[idx][input['Id']] = val
            output_value = [h[i] for i in idxs]
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
                    if input.get('Type', 'string') != 'integer' or val != "":
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
    form = db(q).select(cacheable=True).first()
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
    if db(q).select(cacheable=True).first() is not None:
        return form_md5

    db.forms_revisions.insert(
      form_id=form.id,
      form_yaml=form.form_yaml,
      form_folder=form.form_folder,
      form_name=form.form_name,
      form_md5=form_md5
    )
    table_modified("forms_revisions")
    return form_md5

def mail_form(output, data, form, to=None, record_id=None, _d=None):
    if to is None:
        to = output.get('To', set([]))

    if len(to) == 0:
        return [(1, "form.submit", "No mail destination", dict())]

    if '@' not in to:
        to = email_of(to)

    if to is None:
        return [(1, "form.submit", "No mail destination", dict())]

    if type(to) in (str, unicode):
        to = [to]

    label = data.get('Label', form.form_name)
    title = label
    try:
        d = get_form_formatted_data_o(output, data, _d)
    except Exception, e:
        return [(1, "form.submit", str(e), dict())]
    try:
        with open("applications/init/static/mail.css", "r") as f:
            style = f.read()
    except:
        style = ""

    now_s = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if record_id is not None:
        next = A(
          T("Open the workflow"),
          _href=URL(c="forms", f="workflow", vars={'wfid': record_id}, scheme=True),
        )
    else:
        next = ""

    body = BODY(
      P(T("Form submitted on %(date)s by %(submitter)s", dict(date=now_s, submitter=user_name()))),
      _ajax_forms_inputs(
         _mode="showdetailed",
         form=form,
         form_output=output,
         showexpert=True,
         current_values=d,
       ),
       next,
    )

    message = """
<html>
 <head>
  <style _type="text/css">
   %(style)s
  </style>
 </head>
 %(body)s
</html>
""" % dict(style=style, body=XML(body))
    mail.send(to=to,
              subject=title.encode("utf-8"),
              message=message)
    _to = str(', '.join(to))
    return [(0, "form.submit", "Mail sent to %(to)s on form %(form_name)s submission." , dict(to=_to, form_name=form.form_name))]

def check_output_condition(output, form, data, _d=None):
    cond = output.get('Condition', 'none')
    if cond == 'none':
        return True
    if cond is None:
        raise Exception("malformed output condition: %s"%cond)
    if output.get('Format') != "dict":
        raise Exception("Output condition can only be set on dict-format output")

    def get_var_val(op):
        l = cond.split(op)
        if len(l) != 2:
            raise Exception("malformed output condition: %s"%cond)
        var = l[0].strip()
        val = l[1].strip()
        if not var.startswith("#") or len(var) < 2:
            raise Exception("malformed output condition: %s"%cond)
        var = var[1:]
        if var not in o:
            raise Exception("input id %s is not present in submitted data : %s"%(var, str(o)))
        return var, val

    o = get_form_formatted_data_o(output, data, _d)

    if "==" in cond:
        var, val = get_var_val("==")
        if o[var] == val:
            return True
        else:
            return False
    elif "!=" in cond:
        var, val = get_var_val("!=")
        if o[var] != val:
            return True
        else:
            return False

    raise Exception("operator is not supported in output condition %s"%cond)

def ordered_outputs(data):
    l = []
    h = {}

    dest_order = [
     'db',
     'compliance variable',
     'script',
     'workflow',
     'compliance fix',
     'mail',
    ]

    for output in data.get('Outputs', []):
        dest = output.get('Dest')
        if dest not in h:
            h[dest] = [output]
        else:
            h[dest].append(output)

    unclassified = set(h.keys()) - set(dest_order)

    for dest in dest_order + list(unclassified):
        if dest in h:
            l += h[dest]

    return l

def ajax_generic_form_submit(form, data, _d=None):
    log = []
    __var_id = request.vars.var_id
    _scripts = {'returncode': 0}
    for output in data.get('Outputs', []):
        if output.get('Dest') == 'workflow':
            if request.vars.prev_wfid is not None and request.vars.prev_wfid != 'None':
                # workflow continuation
                q = db.forms_store.id == request.vars.prev_wfid
                prev_wf = db(q).select(cacheable=True).first()
                if prev_wf.form_next_id is not None:
                    log.append((1, "form.store",  "This step is already completed (id=%(id)d)", dict(id=prev_wf.id)))
                    return ajax_info(log)

    record_id = None
    for output in ordered_outputs(data):
        try:
            chkcond = check_output_condition(output, form, data, _d)
        except Exception as e:
            log.append((1, "form.submit", str(e), dict()))
            continue
        if not chkcond:
            continue
        dest = output.get('Dest')
        if dest == "db":
            output['Type'] = 'object'
            output['Format'] = 'dict'
            try:
                d = get_form_formatted_data(output, data, _d)
            except Exception, e:
                log.append((1, "form.submit", str(e), dict()))
                break
            if 'Table' not in output:
                log.append((1, "form.submit", "Table must be set in db type Output", dict()))
                continue
            table = output['Table']
            if table not in db:
                log.append((1, "form.submit", "Table %(t)s not found", dict(t=table)))
                continue

            # purge keys not present in table as columns
            keys = d.keys()
            for key in keys:
                if key not in db[table]:
                    del(d[key])

            try:
                db[table].insert(**d)
                table_modified(table)
                log.append((0, "form.submit", "Data inserted in database table", dict()))
            except Exception, e:
                log.append((1, "form.submit", "Data insertion in database table error: %(err)s", dict(err=str(e))))
        elif dest == "compliance fix":
            if record_id is None:
                log.append((1, "form.submit", "Can not execute the 'compliance fix' without a valid workflow", dict()))
                continue
            modsets = data.get("Modulesets", [])
            if len(modsets) == 0:
                log.append((1, "form.submit", "'Modulesets' must be specified in the form definition for the 'compliance fix' output", dict()))
                continue
            vals = []
            vars = ['nodename', 'svcname', 'action_type', 'command', 'user_id', 'form_id']
            svcname = request.vars.svcname
            nodename = request.vars.nodename
            if __var_id is not None:
                q = db.comp_rulesets_variables.id == __var_id
                q &= db.comp_rulesets_variables.ruleset_id == db.comp_rulesets.id
                if "Manager" not in user_groups():
                    q &= db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
                    q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
                row = db(q).select(db.comp_rulesets.ruleset_name, cacheable=True).first()
                if row is None:
                    log.append((1, "form.submit", "Unable to retrieve compliance variable %(var_id)s ruleset name", dict(var_id=__var_id)))
                    continue
                rset_name = row.ruleset_name
                if rset_name.startswith('svc.'):
                    svcname = rset_name.replace('svc.', '')
                elif rset_name.startswith('node.'):
                    nodename = rset_name.replace('node.', '')
                else:
                    log.append((1, "form.submit", "Unable to deduce service or nodename from ruleset name %(rset_name)s", dict(rset_name=rset_name)))
                    continue
            if nodename is None and svcname is None:
                log.append((1, "form.submit", "No nodename nor svcname specified to 'compliance fix' output handler", dict()))
                continue
            nodes = [nodename]
            if nodename is None and svcname is not None:
                q = db.svcmon.mon_svcname == svcname
                rows = db(q).select(db.svcmon.mon_nodname, cacheable=True)
                if len(rows) == 0:
                    log.append((1, "form.submit", "No nodes found running service %(svcname)s", dict(svcname=svcname)))
                    continue
                nodes = [r.mon_nodname for r in rows]

            _scripts['async'] = len(nodes)
            q = db.forms_store.id == record_id
            db(q).update(form_scripts=json.dumps(_scripts))

            for nodename in nodes:
                q = db.nodes.nodename == nodename
                row = db(q).select(db.nodes.os_name, db.nodes.fqdn, cacheable=True).first()
                if row is None:
                    log.append((1, "form.submit", "No asset information found for node %(nodename)s", dict(nodename=nodename)))
                    continue
                if row.fqdn is not None and len(row.fqdn) > 0:
                    node = row.fqdn
                else:
                    node = nodename


                if row.os_name == "Windows":
                    action_type = "pull"
                else:
                    action_type = "push"

                vals.append([nodename,
                             svcname,
                             action_type,
                             fmt_action(node,
                                        svcname,
                                        "check",
                                        action_type,
                                        modset=modsets),
                             str(auth.user_id),
                             str(record_id)
                            ])

            purge_action_queue()
            generic_insert('action_queue', vars, vals)
            log.append((0, "form.submit", "Compliance fix commands queued for asynchronous execution on %(nodes)s", dict(nodes=', '.join(nodes))))

            from subprocess import Popen
            import sys
            actiond = 'applications'+str(URL(r=request,c='actiond',f='actiond.py'))
            process = Popen([sys.executable, actiond])
            process.communicate()
        elif dest == "script":
            import os
            import subprocess
            try:
                d = get_form_formatted_data(output, data, _d)
            except Exception, e:
                log.append((1, "form.submit", str(e), dict()))
                break
            path = output.get('Path')
            if path is None:
                log.append((1, "form.submit", "Path must be set in script type Output", dict()))
                _scripts['returncode'] += 1
                _scripts[path] = {
                  'path': path,
                  'returncode': 1,
                  'stdout': "",
                  'stderr': "Path must be set in script type Output",
                }
                continue
            if not os.path.exists(path):
                log.append((1, "form.submit", "Script %(path)s does not exists", dict(path=path)))
                _scripts['returncode'] += 1
                _scripts[path] = {
                  'path': path,
                  'returncode': 1,
                  'stdout': "",
                  'stderr': "Script %(path)s does not exists"%dict(path=path),
                }
                continue
            try:
                p = subprocess.Popen([path, d], stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
                out, err = p.communicate()
            except Exception as e:
                log.append((1, "form.submit", "Script %(path)s execution error: %(err)s", dict(path=path, err=str(e))))
                _scripts['returncode'] += 1
                _scripts[path] = {
                  'path': path,
                  'returncode': 1,
                  'stdout': "",
                  'stderr': "Script %(path)s execution error: %(err)s "%dict(path=path, err=str(e))
                }
                continue

            _scripts['returncode'] += p.returncode
            _scripts[path] = {
              'path': path,
              'returncode': p.returncode,
              'stdout': out,
              'stderr': err,
            }
            msg = out
            if len(err) > 0:
                msg += err
            if p.returncode != 0:
                log.append((1, "form.submit", "Script %(path)s returned with error:\n%(err)s", dict(path=path, err=msg)))
                continue
            log.append((0, "form.submit", "script %(path)s returned on success:\n%(out)s", dict(path=path, out=msg)))
        elif dest == "mail":
            log += mail_form(output, data, form, _d=_d)
        elif dest == "workflow":
            try:
                d = get_form_formatted_data(output, data, _d)
            except Exception, e:
                log.append((1, "form.submit", str(e), dict()))
                break

            form_md5 = insert_form_md5(form)

            if output.get('Scripts') is not None:
                if _scripts['returncode'] == 0:
                    script_defs = output['Scripts'].get('Success')
                else:
                    script_defs = output['Scripts'].get('Error')

                if 'async' in _scripts:
                    next_forms = ['to be determined']
                    form_assignee = None
                elif script_defs is None:
                    next_forms = None
                    form_assignee = None
                else:
                    next_forms = script_defs.get('NextForms')
                    form_assignee = script_defs.get('NextAssignee')
            else:
                next_forms = output.get('NextForms')
                form_assignee = output.get('NextAssignee')

            if next_forms is None or len(next_forms) == 0:
                next_id = 0
                status = "closed"
            else:
                next_id = None
                status = "pending"

            now = datetime.datetime.now()

            if request.vars.prev_wfid is not None and request.vars.prev_wfid != 'None':
                # workflow continuation
                q = db.forms_store.id == request.vars.prev_wfid
                prev_wf = db(q).select(cacheable=True).first()
                if prev_wf.form_next_id is not None:
                    log.append((0, "form.store",  "This step is already completed (id=%(id)d)", dict(id=prev_wf.id)))
                    continue

                if form_assignee is None:
                    form_assignee = user_primary_group()
                if form_assignee is None:
                    form_assignee = prev_wf.form_submitter
                if form_assignee is None:
                    form_assignee = user_name()

                head_id = int(request.vars.prev_wfid)
                max_iter = 100
                iter = 0
                while iter < max_iter:
                    iter += 1
                    q = db.forms_store.id == head_id
                    row = db(q).select(cacheable=True).first()
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
                  form_scripts=json.dumps(_scripts),
                  form_var_id=__var_id,
                )
                table_modified("forms_store")
                if record_id is not None:
                    q = db.forms_store.id == request.vars.prev_wfid
                    db(q).update(form_next_id=record_id)
                if next_id != 0:
                    log.append((0, "form.store", "Workflow %(head_id)d step %(form_name)s added with id %(id)d", dict(form_name=form.form_name, head_id=head_id, id=record_id)))
                else:
                    log.append((0, "form.store", "Workflow %(head_id)d closed on last step %(form_name)s with id %(id)d", dict(form_name=form.form_name, head_id=head_id, id=record_id)))
                q = db.workflows.form_head_id == head_id
                wfrow = db(q).select(cacheable=True).first()
                if wfrow is None:
                    # should not happen ... recreate the workflow
                    db.workflows.insert(
                      status=status,
                      form_md5=form_md5,
                      steps=iter+1,
                      last_assignee=form_assignee,
                      last_update=now,
                      last_form_id=record_id,
                      last_form_name=form.form_name,
                      form_head_id=head_id,
                      creator=head.form_submitter,
                      create_date=head.form_submit_date,
                    )
                else:
                    db(q).update(
                      status=status,
                      steps=iter+1,
                      last_assignee=form_assignee,
                      last_form_id=record_id,
                      last_form_name=form.form_name,
                      last_update=now,
                    )
                table_modified("workflows")
            else:
                # new workflow
                if form_assignee is None:
                    form_assignee = user_primary_group()
                    if form_assignee is None:
                        form_assignee = user_name()
                record_id = db.forms_store.insert(
                  form_md5=form_md5,
                  form_submitter=user_name(),
                  form_assignee=form_assignee,
                  form_submit_date=datetime.datetime.now(),
                  form_data=d,
                  form_scripts=json.dumps(_scripts),
                  form_var_id=__var_id,
                )
                table_modified("forms_store")
                if record_id is not None:
                    q = db.forms_store.id == record_id
                    db(q).update(form_head_id=record_id)
                log.append((0, "form.store", "New workflow %(form_name)s created with id %(id)d", dict(form_name=form.form_name, id=record_id)))

                db.workflows.insert(
                  status=status,
                  form_md5=form_md5,
                  steps=1,
                  last_assignee=form_assignee,
                  last_update=now,
                  last_form_id=record_id,
                  last_form_name=form.form_name,
                  form_head_id=record_id,
                  creator=user_name(),
                  create_date=now,
                )
                table_modified("workflows")

            if next_id != 0 and output.get('Mail', False):
                log += mail_form(output, data, form, to=form_assignee, record_id=record_id, _d=_d)

            db.commit()

        elif dest == "compliance variable":
            r = ajax_custo_form_submit(output, data)
            if type(r) == dict:
                __log = r.get("log")
                __err = r.get("err")
                __var_id = r.get("var_id")
            else:
                __log = r
                __err = None
                __var_id = request.vars.var_id
            log += __log
            if __err == "break":
                break

        elif dest == "compliance variable delete":
            if __var_id is not None:
                q = db.comp_rulesets_variables.id == __var_id
                skip = False
                if "Manager" not in user_groups():
                    q1 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
                    q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
                    if db(q&q1).count() == 0:
                        skip = True
                if not skip:
                    db(q).delete()
                    table_modified("comp_rulesets_variables")
                    log.append((0, "", "Compliance variable %(id)s deleted", dict(id=__var_id)))
                else:
                    log.append((0, "", "Compliance variable %(id)s not deleted: not owner", dict(id=__var_id)))

    for ret, action, fmt, d in log:
        _log(action, fmt, d)

    if request.vars.prev_wfid is not None and request.vars.prev_wfid != 'None':
        ajax_info(log, to_session=True)

    return ajax_info(log)

def ajax_custo_form_submit(output, data):
    # logging buffer
    log = []

    rset_name = request.vars.rset_name

    # target selectors
    if request.vars.svcname is not None:
        rset_name = "svc."+request.vars.svcname
    elif request.vars.nodename is not None:
        rset_name = "node."+request.vars.nodename
    elif request.vars.rset is not None:
        rset_name = request.vars.rset

    if request.vars.var_id is not None:
        q = db.comp_rulesets_variables.id == request.vars.var_id
        q &= db.comp_rulesets_variables.ruleset_id == db.comp_rulesets.id
        var = db(q).select(cacheable=True).first()
        if var is None:
            log.append((1, "", "Specified variable not found (id=%(id)s)", dict(id=request.vars.var_id)))
            return log
        var_name = var.comp_rulesets_variables.var_name
        var_class = var.comp_rulesets_variables.var_class
        rset_name = var.comp_rulesets.ruleset_name

    if rset_name is None:
        log.append((1, "", "No ruleset name specified. Skip compliance variable creation", dict()))
        return dict(log=log, err="break")

    # validate privs
    groups = []
    common_groups = []
    if request.vars.nodename is not None:
        q = db.nodes.nodename == request.vars.nodename
        q &= db.nodes.team_responsible == db.auth_group.role
        node = db(q).select(db.auth_group.id, cacheable=True).first()
        if node is None:
            log.append((1, "", "Unknown specified node %(nodename)s", dict(nodename=nodename)))
            return log
        groups = [node.id]
        if len(groups) == 0:
            log.append((1, "", "Specified node %(nodename)s has no responsible group", dict(nodename=nodename)))
            return log
        common_groups = set(user_group_ids()) & set(groups)
        if len(common_groups) == 0:
            log.append((1, "", "You are not allowed to create or modify a ruleset for the node %(node)s", dict(nodename=nodename)))
            return log
    elif request.vars.svcname is not None:
        q = db.services.svc_name == request.vars.svcname
        svc = db(q).select(cacheable=True).first()
        if svc is None:
            log.append((1, "", "Unknown specified service %(svcname)s", dict(svcname=svcname)))
            return log
        q &= db.services.svc_app == db.apps.app
        q &= db.apps.id == db.apps_responsibles.app_id
        rows = db(q).select(cacheable=True)
        groups = map(lambda x: x.apps_responsibles.group_id, rows)
        if len(groups) == 0:
            log.append((1, "", "Specified service %(svcname)s has no responsible groups", dict(svcname=svcname)))
            return log
        common_groups = set(user_group_ids()) & set(groups)
        if len(common_groups) == 0:
            log.append((1, "", "You are not allowed to create or modify a ruleset for the service %(svcname)s", dict(svcname=svcname)))
            return log
    elif request.vars.rset is not None:
        q = db.comp_rulesets.ruleset_name == request.vars.rset
        rset = db(q).select(cacheable=True).first()
        if rset is None:
            log.append((1, "", "Unknown specified ruleset %(rset)s", dict(rset=request.vars.rset)))
            return log
        q &= db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
        q &= db.comp_ruleset_team_responsible.group_id == db.auth_group.id
        rows = db(q).select(cacheable=True)
        groups = map(lambda x: x.auth_group.id, rows)
        common_groups = set(user_group_ids()) & set(groups)
        if len(common_groups) == 0:
            log.append((1, "", "You are not allowed to create or modify the ruleset %(rset)s", dict(rset=rset_name)))
            return log

    # create ruleset
    q = db.comp_rulesets.ruleset_name == rset_name
    rset = db(q).select(cacheable=True).first()
    if rset is None:
        db.comp_rulesets.insert(ruleset_name=rset_name,
                                ruleset_type="explicit",
                                ruleset_public="T")
        table_modified("comp_rulesets")
        log.append((0, "compliance.ruleset.add", "Added explicit published ruleset '%(rset_name)s'", dict(rset_name=rset_name)))
        rset = db(q).select(cacheable=True).first()
        for gid in common_groups:
            db.comp_ruleset_team_responsible.insert(
              ruleset_id=rset.id,
              group_id=gid
            )
            table_modified("comp_ruleset_team_responsible")
            log.append((0, "compliance.ruleset.group.attach", "Added group %(gid)d ruleset '%(rset_name)s' owners", dict(gid=gid, rset_name=rset_name)))
    if rset is None:
        log.append((1, "", "error fetching %(rset_name)s ruleset", dict(rset_name=rset_name)))
        return log

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
            var_name_prefix = '_'.join((output.get('Class', 'noclass'), str(rset.id), ''))
            #log.append((1, "", "No variable name specified.", dict()))
            #return log

        q = db.comp_rulesets_variables.ruleset_id == rset.id
        q &= db.comp_rulesets_variables.var_name.like(var_name_prefix+'%')
        var_name_suffixes = map(lambda x: x.var_name.replace(var_name_prefix, ''), db(q).select(cacheable=True))
        i = 0
        while True:
            _i = str(i)
            if _i not in var_name_suffixes: break
            i += 1
        var_name = var_name_prefix + _i

    try:
        var_value = get_form_formatted_data(output, data)
    except Exception, e:
        log.append((1, "compliance.ruleset.variable.change", str(e), dict()))
        return log

    q = db.comp_rulesets_variables.ruleset_id == rset.id
    q &= db.comp_rulesets_variables.var_name == var_name
    n = db(q).count()

    if n == 0 and request.vars.var_id is not None:
        log.append((1, "compliance.ruleset.variable.change", "%(var_class)s' variable '%(var_name)s' does not exist in ruleset %(rset_name)s or invalid attempt to edit a variable in a parent ruleset", dict(var_class=var_class, var_name=var_name, rset_name=rset_name)))
        return log

    q &= db.comp_rulesets_variables.var_value == var_value
    n = db(q).count()
    __var_id = request.vars.var_id

    if n > 0:
        log.append((1, "compliance.ruleset.variable.add", "'%(var_class)s' variable '%(var_name)s' already exists with the same value in the ruleset '%(rset_name)s': cancel", dict(var_class=var_class, var_name=var_name, rset_name=rset_name)))
    else:
        q = db.comp_rulesets_variables.ruleset_id == rset.id
        q &= db.comp_rulesets_variables.var_name == var_name
        # ownership check
        var_rows = db(q).select(cacheable=True)
        n = len(var_rows)
        owned = True
        if "Manager" not in user_groups():
            q1 = db.comp_ruleset_team_responsible.ruleset_id == rset.id
            q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
            if db(q&q1).count() == 0:
                owned = False
        if n == 0:
            __var_id = db.comp_rulesets_variables.insert(
              ruleset_id=rset.id,
              var_name=var_name,
              var_value=var_value,
              var_class=var_class,
              var_author=user_name(),
              var_updated=datetime.datetime.now(),
            )
            table_modified("comp_rulesets_variables")
            log.append((0, "compliance.ruleset.variable.add", "Added '%(var_class)s' variable '%(var_name)s' to ruleset '%(rset_name)s' with value:\n%(var_value)s", dict(var_class=var_class, var_name=var_name, rset_name=rset_name, var_value=var_value)))
        elif not owned:
            if n == 1:
                log.append((1, "compliance.ruleset.variable.change", "Change '%(var_class)s' variable '%(var_name)s' in ruleset '%(rset_name)s' aborted: not owner", dict(var_class=var_class, var_name=var_name, rset_name=rset_name)))
            else:
                log.append((1, "compliance.ruleset.variable.add", "Add '%(var_class)s' variable '%(var_name)s' in ruleset '%(rset_name)s' aborted: not owner", dict(var_class=var_class, var_name=var_name, rset_name=rset_name)))
        elif n == 1:
            __var_id = var_rows.first().id
            db(q).update(
              var_value=var_value,
              var_class=var_class,
              var_author=user_name(),
              var_updated=datetime.datetime.now(),
            )
            table_modified("comp_rulesets_variables")
            log.append((0, "compliance.ruleset.variable.change", "Modified '%(var_class)s' variable '%(var_name)s' in ruleset '%(rset_name)s' with value:\n%(var_value)s", dict(var_class=var_class, var_name=var_name, rset_name=rset_name, var_value=var_value)))
        else:
            log.append((1, "compliance.ruleset.variable.change", "More than one variable found matching '%(var_name)s' in ruleset '%(rset_name)s'. Skip edition.", dict(var_name=var_name, rset_name=rset_name)))

    if request.vars.nodename is not None or request.vars.svcname is not None:
        modset_ids = []
        if 'Modulesets' in data:
            q = db.comp_moduleset.modset_name.belongs(data['Modulesets'])
            rows = db(q).select(db.comp_moduleset.id, cacheable=True)
            modset_ids = map(lambda x: x.id, rows)

        rset_ids = []
        if 'Rulesets' in data:
            q = db.comp_rulesets.ruleset_name.belongs(data['Rulesets'])
            q &= db.comp_rulesets.ruleset_type == "explicit"
            q &= db.comp_rulesets.ruleset_public == True
            rows = db(q).select(db.comp_rulesets.id, cacheable=True)
            rset_ids = map(lambda x: x.id, rows) + [rset.id]

        if request.vars.nodename is not None:
            # check node_team_responsible_id ?
            try:
                log += internal_comp_attach_modulesets(node_names=[request.vars.nodename],
                                       modset_ids=modset_ids)
            except ToolError:
                pass
            try:
                log += internal_comp_attach_rulesets(node_names=[request.vars.nodename],
                                              ruleset_ids=rset_ids)
            except ToolError:
                pass

        if request.vars.svcname is not None:
            # check svc_team_responsible_id ?
            try:
                log += internal_comp_attach_svc_modulesets(svc_names=[request.vars.svcname],
                                                  modset_ids=modset_ids,
                                                  slave=True)
            except ToolError:
                pass
            try:
                log += internal_comp_attach_svc_rulesets(svc_names=[request.vars.svcname],
                                                ruleset_ids=rset_ids,
                                                slave=True)

            except ToolError:
                pass

    return dict(log=log, var_id=__var_id)

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
             if val != "":
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

@service.json
def json_form_submit(form_name, form_data):
    auth.basic()
    if not auth.user:
        return "Not authorized"

    try:
        form_data = json.loads(form_data)
    except Exception, e:
        return str(e)

    q = db.forms.form_name == form_name
    q &= db.forms.id == db.forms_team_responsible.form_id
    q &= db.forms_team_responsible.group_id.belongs(user_group_ids())
    form = db(q).select(db.forms.ALL, cacheable=True).first()

    if form is None:
        return "form not found"

    import yaml
    data = yaml.load(form.form_yaml)

    log = ajax_generic_form_submit(form, data, form_data)

    return str(log)

def get_modset_names(modset_ids=None):
    # init modset name cache
    if modset_ids is not None:
        q = db.comp_moduleset.id.belongs(modset_ids)
    else:
        q = db.comp_moduleset.id > 0
    rows = db(q).select(cacheable=True)
    modset_names = {}
    for row in rows:
        modset_names[row.id] = row.modset_name
    return modset_names

def get_modset_relations_s():
    # modset relation cache (strings)
    modset_names = get_modset_names()
    modset_relations = get_modset_relations()
    modset_relations_s = {}
    for modset_id, l in modset_relations.items():
        modset_relations_s[modset_names[modset_id]] = map(lambda x: modset_names[x], l)
    return modset_relations_s

def get_modset_relations():
    # modset relation cache (modset ids)
    q = db.comp_moduleset_moduleset.id > 0
    rows = db(q).select(cacheable=True)
    modset_relations = {}
    for row in rows:
        if row.parent_modset_id in modset_relations:
            modset_relations[row.parent_modset_id] += [row.child_modset_id]
        else:
            modset_relations[row.parent_modset_id] = [row.child_modset_id]
    return modset_relations

def get_modset_tree_nodes(modset_ids=None):
    modset_tree_nodes = {}
    modset_relations = get_modset_relations()

    if modset_ids is None:
        modset_ids = modset_relations.keys()

    def recurse_relations(head):
        l = []
        if head not in modset_relations:
            return l
        for child_id in modset_relations[head]:
            l.append(child_id)
            l += recurse_relations(child_id)
        return l

    for parent_id in modset_ids:
        modset_tree_nodes[parent_id] = recurse_relations(parent_id)

    return modset_tree_nodes

def get_modset_rset_relations():
    modset_rset_relations = {}
    q = db.comp_moduleset_ruleset.id > 0
    rows = db(q).select()
    for row in rows:
        if row.modset_id not in modset_rset_relations:
            modset_rset_relations[row.modset_id] = [row.ruleset_id]
        else:
            modset_rset_relations[row.modset_id] += [row.ruleset_id]
    return modset_rset_relations

def get_modset_rset_relations_s():
    modset_rset_relations = {}
    q = db.comp_moduleset_ruleset.id > 0
    q &= db.comp_moduleset_ruleset.ruleset_id == db.comp_rulesets.id
    q &= db.comp_moduleset_ruleset.modset_id == db.comp_moduleset.id
    rows = db(q).select()
    for row in rows:
        if row.comp_moduleset.modset_name not in modset_rset_relations:
            modset_rset_relations[row.comp_moduleset.modset_name] = [row.comp_rulesets.ruleset_name]
        else:
            modset_rset_relations[row.comp_moduleset.modset_name] += [row.comp_rulesets.ruleset_name]
    return modset_rset_relations

def json_tree_modulesets():
    modsets = {
     'data': 'modulesets',
     'attr': {"id": "moduleset_head", "rel": "moduleset_head"},
     'children': [],
    }
    modset_by_objid = {}

    modset_rset_relations = get_modset_rset_relations()
    modset_relations = get_modset_relations()

    q = db.comp_moduleset.id > 0
    q &= db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    if 'Manager' not in user_groups():
        q &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    if request.vars.obj_filter is not None:
        q = _where(q, 'comp_moduleset', request.vars.obj_filter, 'modset_name')
    rows = db(q).select(db.comp_moduleset.id,
                        groupby=db.comp_moduleset.id,
                        cacheable=True)
    visible_head_modset_ids = [r.id for r in rows]
    modset_tree_nodes = get_modset_tree_nodes(visible_head_modset_ids)

    visible_modset_ids = set(visible_head_modset_ids)
    for modset_id in visible_head_modset_ids:
        if modset_id in modset_tree_nodes:
            visible_modset_ids |= set(modset_tree_nodes[modset_id])

    q = db.comp_moduleset.id.belongs(visible_modset_ids)
    q &= db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    q &= db.comp_moduleset_team_responsible.group_id == db.auth_group.id
    j = db.comp_moduleset.id == db.comp_moduleset_modules.modset_id
    l = db.comp_moduleset_modules.on(j)
    rows = db(q).select(db.comp_moduleset.id,
                        db.comp_moduleset.modset_name,
                        db.comp_moduleset_modules.id,
                        db.comp_moduleset_modules.modset_mod_name,
                        db.comp_moduleset_modules.autofix,
                        db.auth_group.id,
                        db.auth_group.role,
                        left=l,
                        orderby=(db.comp_moduleset.modset_name|db.comp_moduleset_modules.modset_mod_name),
                        groupby=(db.comp_moduleset.id|db.comp_moduleset_modules.id|db.auth_group.id)
           )

    modset_done = set([])
    _data = None
    for row in rows:
        if row.comp_moduleset.id not in modset_done:
            if _data is not None:
                _data['children'] += groups
                _data['children'] += mods
                _data['children'] += rulesets
                obj_id = _data["attr"]["obj_id"]
                modset_by_objid[obj_id] = _data
                if obj_id in visible_head_modset_ids:
                    modsets['children'].append(_data)

            _data = {
              "attr": {"id": "modset%d"%row.comp_moduleset.id, "rel": "modset", "obj_id": row.comp_moduleset.id},
              "data": row.comp_moduleset.modset_name,
              "children": []
            }
            groups_done = []
            groups = []
            mods_done = []
            mods = []
            rulesets = []
            if row.comp_moduleset.id in modset_rset_relations:
                rulesets += _tree_rulesets_children(modset_rset_relations[row.comp_moduleset.id],
                                                    id_prefix="modset%d_"%row.comp_moduleset.id,
                                                    hide_unpublished_and_encap_at_root_level=False)
            modset_done.add(row.comp_moduleset.id)

        if row.comp_moduleset_modules.id is not None and row.comp_moduleset_modules.id not in mods_done:
            if row.comp_moduleset_modules.autofix:
                rel = "module_autofix"
            else:
                rel = "module"
            __data = {
              "attr": {"id": "mod%d"%row.comp_moduleset_modules.id, "rel": rel, "obj_id": row.comp_moduleset_modules.id},
              "data": row.comp_moduleset_modules.modset_mod_name,
            }
            mods.append(__data)
            mods_done.append(row.comp_moduleset_modules.id)

        if row.auth_group.id is not None and row.auth_group.id not in groups_done:
            __data = {
              "attr": {"id": "grp%d"%row.auth_group.id, "rel": "group", "obj_id": row.auth_group.id},
              "data": row.auth_group.role,
            }
            groups.append(__data)
            groups_done.append(row.auth_group.id)

    if _data is not None:
        _data['children'] += groups
        _data['children'] += mods
        _data['children'] += rulesets
        obj_id = _data["attr"]["obj_id"]
        modset_by_objid[obj_id] = _data
        if obj_id in visible_head_modset_ids:
            modsets['children'].append(_data)

    def recurse_modsets(head, id_prefix=""):
        if "obj_id" in head["attr"]:
            obj_id = head["attr"]["obj_id"]
            if obj_id in modset_relations:
                for child_modset_id in modset_relations[obj_id]:
                    if child_modset_id in modset_by_objid:
                        _data = copy.deepcopy(modset_by_objid[child_modset_id])
                        _data["attr"]["id"] = id_prefix + "modset" + str(_data["attr"]["obj_id"])
                        head['children'].append(_data)
        for i, child in enumerate(head['children']):
            if child["attr"]["rel"] != "modset":
                srel = child["attr"]["rel"]
                if srel.startswith("ruleset"):
                    srel = "rset"
                elif srel == "module":
                    srel = "mod"
                elif srel == "group":
                    srel = "grp"
                child["attr"]["id"] = id_prefix+srel+str(child["attr"]["obj_id"])
                continue
            recurse_modsets(child, id_prefix=id_prefix+"modset"+str(child["attr"]["obj_id"])+'_')

    recurse_modsets(modsets)

    return modsets

def json_tree_groups():
    groups = {
     'data': 'groups',
     'children': [],
    }

    if request.vars.obj_filter is not None:
        q = _where(None, 'auth_group', request.vars.obj_filter, 'role')
        q = 'AND ' + str(q)
    else:
        q = ""

    sql = """ select id,role from auth_group where role not like "user_%" and privilege = "F" """ + q + """ order by role """
    rows = db.executesql(sql, as_dict=True)
    h = {}
    for row in rows:
        _data = {
          "attr": {"id": "grp%d"%row['id'], "rel": "group", "obj_id": row['id']},
          "data": row['role'],
        }
        groups['children'].append(_data)
    return groups

def json_tree_filters():
    filters = {
     'data': 'filters',
     'children': [],
    }
    q = db.gen_filters.id > 0
    o = db.gen_filters.f_table | db.gen_filters.f_field
    rows = db(q).select(orderby=o, cacheable=True)
    h = {}
    for row in rows:
        _data = {
          "attr": {"id": "f%d"%row.id, "rel": "filter", "obj_id": row.id},
          "data": "%s %s %s" % (row.f_field, row.f_op, row.f_value),
        }
        if row.f_table not in h:
            h[row.f_table] = []
        h[row.f_table].append(_data)
    for table in ('nodes', 'services', 'svcmon', 'node_hba', 'b_disk_app'):
        if table in h:
            l = h[table]
        else:
            l = []
        _data = {
         'data': table,
         'attr': {"rel": "table"},
         'children': l,
        }
        filters['children'].append(_data)
    return filters

def json_tree_filtersets():
    def recurse_json_tree_filtersets(data, parent_ids=[]):
        l = []
        if data is None:
            return l
        for o in data:
            if o['type'] == 'filter':
                row = o['data'].gen_filters
                tmp_parent_ids = parent_ids + ["f%d"%row.id]
                _data = {
                  "attr": {"id": "_".join(tmp_parent_ids), "rel": "filter", "obj_id": row.id},
                  "data": "%s %s.%s %s %s" % (o['op'], row.f_table, row.f_field, row.f_op, row.f_value),
                }
            elif o['type'] == 'filterset':
                parent_ids.append("fset%d"%o['fset_id'])
                _data = {
                  "attr": {"id": "_".join(parent_ids), "rel": "filterset", "obj_id": o['fset_id']},
                  "data": "%s %s" % (o['op'], fset_names[o['fset_id']]),
                  "children": recurse_json_tree_filtersets(o['data'], parent_ids),
                }
            l.append(_data)
        return l

    fset_names = {}
    q = db.gen_filtersets.id > 0
    rows = db(q).select(cacheable=True)
    for row in rows:
        fset_names[row.id] = row.fset_name

    filtersets = {
     'data': 'filtersets',
     'attr': {"id": "fset_head", "rel": "filterset_head"},
     'children': [],
    }
    fset_data = comp_get_fset_data()

    if request.vars.obj_filter is not None:
        q &= _where(None, 'gen_filtersets', request.vars.obj_filter, 'fset_name')
        o = db.gen_filtersets.fset_name
        rows = db(q).select(db.gen_filtersets.id, orderby=o, cacheable=True)

    for fset_id in [r.id for r in rows]:
        try:
            l = recurse_json_tree_filtersets(fset_data[fset_id], parent_ids=["fset%d"%fset_id])
        except KeyError:
            l = []
        _data = {
          "attr": {"id": "fset%d"%fset_id, "rel": "filterset", "obj_id": fset_id},
          "data": fset_names[fset_id],
          "children": l,
        }
        filtersets['children'].append(_data)

    return filtersets

def json_tree_rulesets():
    rulesets = {
      'data': 'rulesets',
      'attr': {"id": "rset_head", "rel": "ruleset_head"},
      'children': [],
    }
    rulesets['children'] = _tree_rulesets_children(obj_filter=request.vars.obj_filter)
    return rulesets

def _tree_rulesets_children(ruleset_ids=None, id_prefix="", obj_filter=None, hide_unpublished_and_encap_at_root_level=True):
    children = []
    q = db.comp_rulesets_rulesets.id > 0
    rows = db(q).select(orderby=db.comp_rulesets_rulesets.parent_rset_id, cacheable=True)
    rsets_relations = {}
    encap_rset_ids = set([])
    for row in rows:
        if row.parent_rset_id not in rsets_relations:
            rsets_relations[row.parent_rset_id] = []
        rsets_relations[row.parent_rset_id].append(row.child_rset_id)
        encap_rset_ids.add(row.child_rset_id)

    q = db.comp_rulesets_filtersets.id > 0
    q &= db.comp_rulesets_filtersets.fset_id == db.gen_filtersets.id
    rows = db(q).select(cacheable=True)
    rsets_fsets = {}
    for row in rows:
        if row.comp_rulesets_filtersets.ruleset_id not in rsets_fsets:
            rsets_fsets[row.comp_rulesets_filtersets.ruleset_id] = []
        rsets_fsets[row.comp_rulesets_filtersets.ruleset_id].append(row)

    q = db.comp_rulesets_variables.id > 0
    o = db.comp_rulesets_variables.ruleset_id | db.comp_rulesets_variables.var_name
    rows = db(q).select(orderby=o, cacheable=True)
    rsets_variables = {}
    for row in rows:
        if row.ruleset_id not in rsets_variables:
            rsets_variables[row.ruleset_id] = []
        rsets_variables[row.ruleset_id].append(row)

    q = db.comp_ruleset_team_responsible.id > 0
    q &= db.comp_ruleset_team_responsible.group_id == db.auth_group.id
    rows = db(q).select(cacheable=True)
    rsets_groups = {}
    for row in rows:
        if row.comp_ruleset_team_responsible.ruleset_id not in rsets_groups:
            rsets_groups[row.comp_ruleset_team_responsible.ruleset_id] = []
        rsets_groups[row.comp_ruleset_team_responsible.ruleset_id].append(row)

    q = db.comp_rulesets.id > 0
    q &= db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    rows = db(q).select(groupby=db.comp_rulesets.id,
                        cacheable=True)
    rsets = {}
    for row in rows:
        rsets[row.comp_rulesets.id] = row.comp_rulesets

    # main ruleset selection
    o = db.comp_rulesets.ruleset_name
    q = db.comp_rulesets.id > 0
    q &= db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if ruleset_ids is not None:
        q &= db.comp_rulesets.id.belongs(ruleset_ids)
    if 'Manager' not in user_groups():
        q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    if obj_filter is not None:
        q &= _where(None, 'comp_rulesets', obj_filter, 'ruleset_name')

    rows = db(q).select(groupby=db.comp_rulesets.id,
                        orderby=o, cacheable=True)

    def recurse_rset(rset, _data={}, parent_ids=[]):
        child_rsets = []
        parent_ids.append("rset%d"%rset.id)
        for rset_id in rsets_relations.get(rset.id, []):
             if rset_id not in rsets:
                 continue
             child_rsets.append(recurse_rset(rsets[rset_id], parent_ids=copy.copy(parent_ids)))
        child_rsets = sorted(child_rsets, lambda x, y: cmp(x['data'], y['data']))
        fsets = []
        for v in rsets_fsets.get(rset.id, []):
            _parent_ids = parent_ids + ["fset%d"%v.comp_rulesets_filtersets.fset_id]
            vdata = {
             "attr": {"id": id_prefix+"_".join(_parent_ids), "rel": "filterset", "obj_id": v.comp_rulesets_filtersets.fset_id, "class": "jstree-draggable"},
             "data": v.gen_filtersets.fset_name,
            }
            fsets.append(vdata)
        variables = []
        for v in rsets_variables.get(rset.id, []):
            _parent_ids = parent_ids + ["var%d"%v.id]
            vdata = {
             "attr": {"id": id_prefix+"_".join(_parent_ids), "rel": "variable", "obj_id": v.id, "class": "jstree-draggable"},
             "data": v.var_name,
            }
            variables.append(vdata)
        groups = []
        for v in rsets_groups.get(rset.id, []):
            _parent_ids = parent_ids + ["grp%d"%v.comp_ruleset_team_responsible.group_id]
            vdata = {
             "attr": {"id": id_prefix+"_".join(_parent_ids), "rel": "group", "obj_id": v.comp_ruleset_team_responsible.group_id, "class": "jstree-draggable"},
             "data": v.auth_group.role,
            }
            groups.append(vdata)
        if rset.ruleset_type == "contextual":
            if rset.ruleset_public == True:
                rel = "ruleset_cxt"
            else:
                rel = "ruleset_cxt_hidden"
        else:
            if rset.ruleset_public == True:
                rel = "ruleset"
            else:
                rel = "ruleset_hidden"
        _data = {
          "attr": {"id": id_prefix+"_".join(parent_ids), "rel": rel, "obj_id": rset.id, "rset_type": rset.ruleset_type, "class": "jstree-draggable,jstree-drop"},
          "data": rset.ruleset_name,
          "children": groups+fsets+variables+child_rsets,
        }
        return _data

    for row in rows:
        rset = row.comp_rulesets
        if hide_unpublished_and_encap_at_root_level and rset.id in encap_rset_ids and not rset.ruleset_public:
            continue
        _data = recurse_rset(rset, parent_ids=[])
        children.append(_data)

    return children

@service.json
def json_tree():
    data = [
      json_tree_groups(),
      json_tree_filters(),
      json_tree_filtersets(),
      json_tree_modulesets(),
      json_tree_rulesets(),
    ]
    return data

def comp_admin():
    q = db.forms.form_type == "obj"
    rows = db(q).select(db.forms.form_name,
                        cacheable=True,
                        orderby=db.forms.form_name)
    var_class_names = [row.form_name for row in rows]
    var_class_names = map(lambda x: '"'+x+'"', var_class_names)

    js = """
     designer.init({"var_class_names": [%(var_class_names)s]})
     """ % dict(
      var_class_names = ', '.join(var_class_names),
    )
    d = DIV(
      DIV(
        INPUT(
          _id="casearch",
          _value=request.vars.obj_filter,
          _style="float:left",
        _class="wfsearch",
        ),
        DIV(
          _id="calink",
          _class="link16 clickable",
          _style="float:left",
          _onclick="designer_link()",
        ),
        DIV(
          TEXTAREA(),
          _id="calink_val",
          _class="white_float hidden",
          _style="margin-top:1.1em",
        ),
        _style="margin-bottom:0.5em;margin-top:0.5em;",
      ),
      DIV(
        _class="spacer",
      ),
      DIV(
        DIV(
          _id="catree",
          _name="catree",
          _style="height:100%;overflow-y:scroll;width:20%;float:left",
        ),
        DIV(
          _id="catree2",
          _name="catree",
          _style="height:100%;overflow-y:scroll;width:20%;float:left;display:none",
        ),
        DIV(
          XML("&nbsp;"),
          _id="sep",
          _style="height:100%;float:left;cursor:pointer;width:5px;text-align:left;background-color:lightgrey",
        ),
        DIV(
          _id="cainfo",
          _style="height:100%;float:left;overflow-y:auto;float:left;text-align:left;padding-left:1em",
        ),
        _id="treerow",
      ),
      SCRIPT(js),
      _style="text-align:left",
    )
    return dict(table=d)

@service.json
def json_tree_action():
    action = request.vars.operation
    if action == "rename":
        return json_tree_action_rename()
    elif action == "show":
        return json_tree_action_show()
    elif action == "create":
        return json_tree_action_create()
    elif action == "delete":
        return json_tree_action_delete()
    elif action == "clone":
        return json_tree_action_clone()
    elif action == "move":
        if request.vars.obj_type == "variable" and \
           request.vars.dst_type.startswith("ruleset"):
            return json_tree_action_move_var_to_rset(request.vars.obj_id,
                                                     request.vars.dst_id)
        if request.vars.obj_type.startswith("ruleset") and \
           request.vars.dst_type.startswith("ruleset"):
            return json_tree_action_move_rset_to_rset(request.vars.obj_id,
                                                      request.vars.parent_obj_id,
                                                      request.vars.dst_id)
        if request.vars.obj_type == "filterset" and \
           request.vars.dst_type.startswith("ruleset"):
            return json_tree_action_move_fset_to_rset(request.vars.obj_id,
                                                      request.vars.dst_id)
        if request.vars.obj_type == "group" and \
           request.vars.dst_type.startswith("ruleset"):
            return json_tree_action_move_group_to_rset(request.vars.obj_id,
                                                       request.vars.dst_id)
        if request.vars.obj_type == "group" and \
           request.vars.dst_type == "modset":
            return json_tree_action_move_group_to_modset(request.vars.obj_id,
                                                         request.vars.dst_id)
    elif action == "copy":
        if request.vars.obj_type == "variable" and \
           request.vars.dst_type.startswith("ruleset"):
            return json_tree_action_copy_var_to_rset(request.vars.obj_id,
                                                     request.vars.dst_id)
        elif request.vars.obj_type.startswith("ruleset") and \
           request.vars.dst_type.startswith("ruleset"):
            return json_tree_action_copy_rset_to_rset(request.vars.obj_id,
                                                      request.vars.parent_obj_id,
                                                      request.vars.dst_id)
        elif request.vars.obj_type == "filterset" and \
           request.vars.dst_type.startswith("ruleset"):
            return json_tree_action_move_fset_to_rset(request.vars.obj_id,
                                                      request.vars.dst_id)
        elif request.vars.obj_type == "group" and \
           request.vars.dst_type.startswith("ruleset"):
            return json_tree_action_move_group_to_rset(request.vars.obj_id,
                                                       request.vars.dst_id)
        elif request.vars.obj_type == "group" and \
           request.vars.dst_type == "modset":
            return json_tree_action_move_group_to_modset(request.vars.obj_id,
                                                         request.vars.dst_id)
        elif request.vars.obj_type == "filter" and \
           request.vars.dst_type == "filterset":
            return json_tree_action_copy_filter_to_fset(request.vars.obj_id,
                                                        request.vars.dst_id)
        elif request.vars.obj_type == "filterset" and \
           request.vars.dst_type.startswith("filterset"):
            return json_tree_action_copy_fset_to_fset(request.vars.obj_id,
                                                      request.vars.dst_id)
        elif request.vars.obj_type == "filter" and \
           request.vars.dst_type.startswith("filterset"):
            return json_tree_action_copy_filter_to_fset(request.vars.obj_id,
                                                        request.vars.dst_id)
        if request.vars.obj_type.startswith("ruleset") and \
           request.vars.dst_type == "modset":
            return json_tree_action_copy_rset_to_modset(request.vars.obj_id,
                                                        request.vars.dst_id)
        if request.vars.obj_type == "modset" and \
           request.vars.dst_type == "modset":
            return json_tree_action_copy_modset_to_modset(request.vars.obj_id,
                                                          request.vars.dst_id)
    elif action == "set_autofix":
        return json_tree_action_set_autofix(request.vars.obj_id,
                                            request.vars.autofix)
    elif action == "set_var_class":
        return json_tree_action_set_var_class(request.vars.obj_id,
                                              request.vars.var_class)
    elif action == "set_public":
        return json_tree_action_set_public(request.vars.obj_id,
                                           request.vars.publication)
    elif action == "set_stats":
        return json_tree_action_set_stats(request.vars.obj_id,
                                          request.vars.value)
    elif action == "set_log_op":
        return json_tree_action_set_log_op(request.vars.obj_id,
                                           request.vars.obj_type,
                                           request.vars.parent_obj_id,
                                           request.vars.type)
    elif action == "set_type":
        return json_tree_action_set_type(request.vars.obj_id,
                                         request.vars.type)
    elif action == "detach_moduleset_from_moduleset":
        return json_tree_action_detach_moduleset_from_moduleset(request.vars.obj_id,
                                                                request.vars.parent_obj_id)
    elif action == "detach_ruleset_from_moduleset":
        return json_tree_action_detach_ruleset_from_moduleset(request.vars.obj_id,
                                                              request.vars.parent_obj_id)
    elif action == "detach_ruleset":
        return json_tree_action_detach_ruleset(request.vars.obj_id,
                                               request.vars.parent_obj_id)
    elif action == "detach_filter":
        return json_tree_action_detach_filter(request.vars.obj_id,
                                              request.vars.parent_obj_id)
    elif action == "detach_group":
        return json_tree_action_detach_group(request.vars.obj_id,
                                             request.vars.parent_obj_id,
                                             request.vars.parent_obj_type)
    elif action == "detach_filterset":
        return json_tree_action_detach_filterset(request.vars.obj_id,
                                                 request.vars.parent_obj_id,
                                                 request.vars.parent_obj_type)
    else:
        return "-1"

def json_tree_action_clone():
    if request.vars.obj_type.startswith("ruleset"):
        return json_tree_action_clone_ruleset(request.vars.obj_id)
    elif request.vars.obj_type == "modset":
        return json_tree_action_clone_moduleset(request.vars.obj_id)
    return ""

def json_tree_action_delete():
    if request.vars.obj_type == "variable":
        return json_tree_action_delete_variable(request.vars.obj_id)
    elif request.vars.obj_type.startswith("ruleset"):
        return json_tree_action_delete_ruleset(request.vars.obj_id)
    elif request.vars.obj_type.startswith("filterset"):
        return json_tree_action_delete_filterset(request.vars.obj_id)
    elif request.vars.obj_type == "module":
        return json_tree_action_delete_module(request.vars.obj_id)
    elif request.vars.obj_type == "modset":
        return json_tree_action_delete_moduleset(request.vars.obj_id)
    return ""

def json_tree_action_create():
    if request.vars.obj_type == "variable":
        return json_tree_action_create_variable(request.vars.parent_obj_id, request.vars.obj_name)
    elif request.vars.obj_type.startswith("ruleset"):
        return json_tree_action_create_ruleset(request.vars.obj_name)
    elif request.vars.obj_type == "module":
        return json_tree_action_create_module(request.vars.parent_obj_id, request.vars.obj_name)
    elif request.vars.obj_type == "modset":
        return json_tree_action_create_moduleset(request.vars.obj_name)
    elif request.vars.obj_type == "filterset":
        return json_tree_action_create_filterset(request.vars.obj_name)
    return ""

def json_tree_action_show():
    if request.vars.obj_type.startswith("ruleset"):
        return json_tree_action_show_ruleset(request.vars.obj_id)
    elif request.vars.obj_type == "variable":
        return json_tree_action_show_variable(request.vars.obj_id)
    elif request.vars.obj_type == "filterset":
        return json_tree_action_show_filterset(request.vars.obj_id)
    elif request.vars.obj_type == "modset":
        return json_tree_action_show_moduleset(request.vars.obj_id)
    return ""

def json_tree_action_rename():
    if request.vars.obj_type.startswith("ruleset"):
        return json_tree_action_rename_ruleset(request.vars.obj_id, request.vars.new_name)
    elif request.vars.obj_type == "filterset":
        return json_tree_action_rename_filterset(request.vars.obj_id, request.vars.new_name)
    elif request.vars.obj_type == "variable":
        return json_tree_action_rename_variable(request.vars.obj_id, request.vars.new_name)
    elif request.vars.obj_type == "module":
        return json_tree_action_rename_module(request.vars.obj_id, request.vars.new_name)
    elif request.vars.obj_type == "modset":
        return json_tree_action_rename_modset(request.vars.obj_id, request.vars.new_name)
    return "-1"

@auth.requires_membership('CompManager')
def json_tree_action_rename_modset(modset_id, new):
    if len(db(db.comp_moduleset.modset_name==new).select(cacheable=True)) > 0:
        return {"err": "rename moduleset failed: new moduleset name already exists"}
    q = db.comp_moduleset.id == modset_id
    q &= db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    if 'Manager' not in user_groups():
        q &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q).select(db.comp_moduleset.modset_name,
                        groupby=db.comp_moduleset.id, cacheable=True)
    if len(rows) == 0:
        return json.dumps({"err": "rename moduleset failed: can't find source moduleset"})
    old = rows[0].modset_name
    n = db(db.comp_moduleset.id == modset_id).update(modset_name=new)
    _log('compliance.moduleset.rename',
         'renamed moduleset %(old)s as %(new)s',
         dict(old=old, new=new))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_rename_filterset(fset_id, new):
    if len(db(db.gen_filtersets.fset_name==new).select(cacheable=True)) > 0:
        return {"err": "rename filterset failed: new filterset name already exists"}
    q = db.gen_filtersets.id == fset_id
    rows = db(q).select(db.gen_filtersets.fset_name, cacheable=True)
    if len(rows) == 0:
        return json.dumps({"err": "rename filterset failed: can't find source filterset"})
    old = rows[0].fset_name
    n = db(db.gen_filtersets.id == fset_id).update(fset_name=new)
    _log('compliance.filterset.rename',
         'renamed filterset %(old)s as %(new)s',
         dict(old=old, new=new))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_rename_ruleset(rset_id, new):
    if len(db(db.comp_rulesets.ruleset_name==new).select(cacheable=True)) > 0:
        return {"err": "rename ruleset failed: new ruleset name already exists"}
    q = db.comp_rulesets.id == rset_id
    q &= db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q).select(db.comp_rulesets.ruleset_name, groupby=db.comp_rulesets.id, cacheable=True)
    if len(rows) == 0:
        return json.dumps({"err": "rename ruleset failed: can't find source ruleset"})
    old = rows[0].ruleset_name
    n = db(db.comp_rulesets.id == rset_id).update(ruleset_name=new)
    _log('compliance.ruleset.rename',
         'renamed ruleset %(old)s as %(new)s',
         dict(old=old, new=new))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_rename_module(mod_id, new):
    q = db.comp_moduleset_modules.id == mod_id
    q &= db.comp_moduleset_modules.modset_id == db.comp_moduleset.id
    q &= db.comp_moduleset_modules.modset_id == db.comp_moduleset_team_responsible.modset_id
    if 'Manager' not in user_groups():
        q &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q).select(db.comp_moduleset.modset_name,
                        db.comp_moduleset_modules.modset_mod_name,
                        groupby=db.comp_moduleset_modules.id,
                        cacheable=True)
    if len(rows) == 0:
        return {"err": "rename module failed: can't find variable"}
    modset_name = rows[0].comp_moduleset.modset_name
    old = rows[0].comp_moduleset_modules.modset_mod_name
    n = db(db.comp_moduleset_modules.id == mod_id).update(modset_mod_name=new)
    _log('compliance.moduleset.module.rename',
         'renamed module %(old)s as %(new)s in moduleset %(modset_name)s',
         dict(old=old, new=new, modset_name=modset_name))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_rename_variable(var_id, new):
    q = db.comp_rulesets_variables.id == var_id
    q &= db.comp_rulesets_variables.ruleset_id == db.comp_rulesets.id
    q &= db.comp_rulesets_variables.ruleset_id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q).select(db.comp_rulesets.ruleset_name,
                        db.comp_rulesets_variables.var_name,
                        groupby=db.comp_rulesets_variables.id,
                        cacheable=True)
    if len(rows) == 0:
        return {"err": "rename variable failed: can't find variable"}
    rset_name = rows[0].comp_rulesets.ruleset_name
    old = rows[0].comp_rulesets_variables.var_name
    n = db(db.comp_rulesets_variables.id == var_id).update(var_name=new)
    _log('compliance.variable.rename',
         'renamed variable %(old)s as %(new)s in ruleset %(rset_name)s',
         dict(old=old, new=new, rset_name=rset_name))
    return "0"

def json_tree_action_show_filterset(fset_id):
    fset_id = int(fset_id)

    #
    q = db.gen_filtersets.id == fset_id
    rows = db(q).select(cacheable=False)
    v = rows.first()
    if v is None:
        return {"err": "filterset does not exist"}
    fset_name = v.fset_name

    #
    q = db.nodes.id > 0
    q = apply_filters(q, node_field=db.nodes.nodename, fset_id=fset_id)
    rows = db(q).select(db.nodes.nodename, orderby=db.nodes.nodename)
    nodes = [r.nodename.lower() for r in rows]

    matching_nodes = DIV(
      H3(T("Matching nodes"), " (%d) "%len(nodes)),
      P(', '.join(nodes)),
    )

    #
    q = db.services.id > 0
    q = apply_filters(q, service_field=db.services.svc_name, fset_id=fset_id)
    rows = db(q).select(db.services.svc_name, orderby=db.services.svc_name)
    services = [r.svc_name.lower() for r in rows]

    matching_services = DIV(
      H3(T("Matching services"), " (%d) "%len(services)),
      P(', '.join(services)),
    )

    #
    a = fset_get_ancestors()
    if fset_id not in a:
        ancestors = SPAN()
    else:
        q = db.gen_filtersets.id.belongs(a[fset_id])
        rows = db(q).select(cacheable=False)
        l = [ r.fset_name for r in rows ]
        ancestors = DIV(
          H3(T("Encapsulated in other filtersets"), " (%d) "%len(a[fset_id])),
          SPAN(', '.join(l)),
        )

    #
    q = db.comp_rulesets_filtersets.fset_id == fset_id
    q &= db.comp_rulesets_filtersets.ruleset_id == db.comp_rulesets.id
    rows = db(q).select(db.comp_rulesets.ruleset_name, cacheable=False)
    if len(rows) == 0:
        rulesets = SPAN()
    else:
        l = [ r.ruleset_name for r in rows ]
        rulesets = DIV(
          H3(T("Used by rulesets"), " (%d) "%len(rows)),
          SPAN(', '.join(l)),
        )

    #
    q = db.gen_filterset_check_threshold.fset_id == fset_id
    rows = db(q).select(cacheable=False)
    if len(rows) == 0:
        check_thres = SPAN()
    else:
        l = [ '.'.join((r.chk_type, r.chk_inst)) for r in rows ]
        check_thres = DIV(
          H3(T("Used by checker thresholds"), " (%d) "%len(rows)),
          SPAN(', '.join(l)),
        )

    #
    compare = SPAN()

    #
    metrics = SPAN()


    d = DIV(
      H2(fset_name),
      P(T('Compute statistics')+': ' + T(str(v.fset_stats))),
      matching_nodes,
      matching_services,
      ancestors,
      rulesets,
      check_thres,
      compare,
      metrics,
    )
    return d

def json_tree_action_show_moduleset(modset_id):
    modset_id = int(modset_id)

    q = db.comp_moduleset.id == modset_id
    modset = db(q).select(cacheable=True).first()
    if modset is None:
        return ""
    l = []
    l.append(H2(modset.modset_name))
    l.append(HR())

    q = db.comp_node_moduleset.modset_id == modset_id
    rows = db(q).select(cacheable=False)
    if len(rows) > 0:
        l.append(H3(T("Attached to servers")))
        l.append(P(' '.join(map(lambda x: x.modset_node, rows))))
        l.append(HR())

    q = db.comp_modulesets_services.modset_id == modset_id
    rows = db(q).select(cacheable=False)
    if len(rows) > 0:
        l.append(H3(T("Attached to services")))
        l.append(P(' '.join(map(lambda x: x.modset_svcname, rows))))
        l.append(HR())

    def mod_html(x):
        l = []
        l.append(B(x.modset_mod_name))
        l.append(P(T("Author"), ": ", I(x.modset_mod_author),
                      ", ",
                      T("Updated"), ": ", I(x.modset_mod_updated)))
        return P(l)

    q = db.comp_moduleset_modules.modset_id == modset_id
    rows = db(q).select(cacheable=False)
    if len(rows) > 0:
        l.append(H3(T("Modules")))
        l.append(SPAN(map(lambda x: mod_html(x), rows)))
        l.append(HR())

    return DIV(l)

def json_tree_action_show_ruleset(rset_id):
    q = db.comp_rulesets.id == rset_id
    j = db.comp_rulesets.id == db.comp_rulesets_filtersets.ruleset_id
    l1 = db.comp_rulesets_filtersets.on(j)
    j = db.comp_rulesets_filtersets.fset_id == db.gen_filtersets.id
    l2 = db.gen_filtersets.on(j)
    row = db(q).select(db.comp_rulesets.ALL,
                       db.comp_rulesets_filtersets.ALL,
                       db.gen_filtersets.ALL,
                       left=(l1,l2), cacheable=True).first()
    if row is None:
        return "-1"
    if 'comp_rulesets' in row:
        rset = row.comp_rulesets
    else:
        rset = row
    if 'comp_rulesets_filtersets' in row:
        fset_name = row.gen_filtersets.fset_name
    else:
        fset_name = T("not set")
    l = []
    l.append(H2(rset.ruleset_name))
    l.append(P(T('Type')+': ' + str(rset.ruleset_type)))
    if rset.ruleset_type == "contextual":
        l.append(P(T('Filterset')+': ' + str(fset_name)))
    l.append(P(T('Public')+': ' + str(rset.ruleset_public)))
    l.append(HR())

    rset_id = int(rset_id)

    q = db.comp_rulesets_nodes.ruleset_id == rset_id
    rows = db(q).select(cacheable=False)
    if len(rows) > 0:
        l.append(H3(T("Attached to servers")))
        l.append(P(' '.join(map(lambda x: x.nodename, rows))))
        l.append(HR())

    q = db.comp_rulesets_services.ruleset_id == rset_id
    rows = db(q).select(cacheable=False)
    if len(rows) > 0:
        l.append(H3(T("Attached to services")))
        l.append(P(' '.join(map(lambda x: x.svcname, rows))))
        l.append(HR())

    q = db.comp_rulesets_rulesets.id > 0
    rows = db(q).select(cacheable=True)
    rel = {}
    for row in rows:
        if row.parent_rset_id not in rel:
            rel[row.parent_rset_id] = []
        rel[row.parent_rset_id].append(row.child_rset_id)

    def recurse_rel(rset_id, l=[]):
        l.append(rset_id)
        for child_rset_id in rel.get(rset_id, []):
            l = recurse_rel(child_rset_id, l)
        return l

    rset_ids = recurse_rel(rset_id)

    q = db.comp_rulesets_variables.ruleset_id.belongs(rset_ids)
    rows = db(q).select()
    renderer = col_var_value(title='Value',
                             field='var_value',
                             table='comp_rulesets')
    t = table_comp_rulesets("treetable")
    renderer.t = t
    for row in rows:
        l.append(H3(row.var_name))
        l.append(P(T("Variable class: %(var_class)s", dict(var_class=str(row.var_class)))))
        l.append(P(T("Last modified by %(user)s on %(date)s", dict(user=row.var_author, date=str(row.var_updated)))))
        l.append(renderer.html(row))
    return DIV(l)

def json_tree_action_show_variable(var_id):
    q = db.comp_rulesets_variables.id == var_id
    rows = db(q).select()
    renderer = col_var_value(title='Value',
                             field='var_value',
                             table='comp_rulesets')
    t = table_comp_rulesets("treetable")
    renderer.t = t
    l = []
    for row in rows:
        l.append(H3(row.var_name))
        l.append(P(T("Variable class: %(var_class)s", dict(var_class=str(row.var_class)))))
        l.append(P(T("Last modified by %(user)s on %(date)s", dict(user=row.var_author, date=str(row.var_updated)))))
        l.append(renderer.html(row))
    return DIV(l)

@auth.requires_membership('CompManager')
def json_tree_action_create_filterset(name):
    name = name.strip()
    try:
        name = name[4:]
    except:
        pass

    q = db.gen_filtersets.fset_name == name
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is not None:
        return {"err": "a filterset named '%(name)s' already exists"%dict(name=name)}

    obj_id = db.gen_filtersets.insert(
      fset_name=name,
      fset_stats='F',
      fset_author=user_name(),
      fset_updated=datetime.datetime.now(),
    )
    table_modified("gen_filtersets")
    #add_default_team_responsible_to_filterset(name)
    _log('compliance.filterset.add',
         'added filterset %(name)s',
         dict(name=name))
    return {"obj_id": obj_id}

@auth.requires_membership('CompManager')
def json_tree_action_create_moduleset(modset_name):
    modset_name = modset_name.strip()
    try:
        modset_name = modset_name[4:]
    except:
        pass

    q = db.comp_moduleset.modset_name == modset_name
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is not None:
        return {"err": "a moduleset named '%(modset_name)s' already exists"%dict(modset_name=modset_name)}

    obj_id = db.comp_moduleset.insert(
      modset_name=modset_name,
      modset_author=user_name(),
      modset_updated=datetime.datetime.now(),
    )
    table_modified("comp_moduleset")
    add_default_team_responsible_to_modset(modset_name)
    _log('compliance.moduleset.add',
         'added moduleset %(modset_name)s',
         dict(modset_name=modset_name))
    return {"obj_id": obj_id}

@auth.requires_membership('CompManager')
def json_tree_action_create_ruleset(rset_name):
    rset_name = rset_name.strip()
    try:
        rset_name = rset_name[4:]
    except:
        pass

    q = db.comp_rulesets.ruleset_name == rset_name
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is not None:
        return {"err": "a ruleset named '%(rset_name)s' already exists"%dict(rset_name=rset_name)}

    obj_id = db.comp_rulesets.insert(
      ruleset_name=rset_name,
      ruleset_type="explicit",
    )
    table_modified("comp_rulesets")
    add_default_team_responsible(rset_name)
    _log('compliance.ruleset.add',
         'added ruleset %(rset_name)s',
         dict(rset_name=rset_name))
    comp_rulesets_chains()
    return {"obj_id": obj_id}

@auth.requires_membership('CompManager')
def json_tree_action_create_module(modset_id, modset_mod_name):
    q = db.comp_moduleset.id == modset_id
    q1 = db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "moduleset does not exist or not owned by you"}

    modset_mod_name = modset_mod_name.strip()
    try:
        modset_mod_name = modset_mod_name[4:]
    except:
        pass
    obj_id = db.comp_moduleset_modules.insert(
      modset_id=modset_id,
      modset_mod_name=modset_mod_name,
      modset_mod_author=user_name(),
      modset_mod_updated=datetime.datetime.now(),
    )
    table_modified("comp_moduleset_modules")
    _log('compliance.moduleset.module.add',
         'added module %(modset_mod_name)s in moduleset %(modset_name)s',
         dict(modset_mod_name=modset_mod_name,
              modset_name=v.comp_moduleset.modset_name))
    return {"obj_id": obj_id}

@auth.requires_membership('CompManager')
@service.json
def json_tree_action_create_variable(rset_id, var_name):
    q = db.comp_rulesets.id == rset_id
    q1 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "ruleset does not exist or not owned by you"}

    var_name = var_name.strip()
    try:
        var_name = var_name[4:]
    except:
        pass
    obj_id = db.comp_rulesets_variables.insert(
      ruleset_id=rset_id,
      var_name=var_name,
      var_author=user_name(),
      var_updated=datetime.datetime.now(),
      var_class="raw",
      var_value="",
    )
    table_modified("comp_rulesets_variables")
    _log('compliance.variable.add',
         'added variable %(var_name)s in ruleset %(rset_name)s',
         dict(var_name=var_name,
              rset_name=v.comp_rulesets.ruleset_name))
    return {"obj_id": obj_id}

@auth.requires_membership('CompManager')
def json_tree_action_delete_module(mod_id):
    q = db.comp_moduleset_modules.id == mod_id
    q1 = db.comp_moduleset.id == db.comp_moduleset_modules.modset_id
    v = db(q & q1).select(cacheable=True).first()
    if v is None:
        return "0"
    db(q).delete()
    table_modified("comp_moduleset_modules")
    _log('compliance.moduleset.module.delete',
         'deleted module %(modset_mod_name)s from moduleset %(modset_name)s',
         dict(modset_mod_name=v.comp_moduleset_modules.modset_mod_name,
              modset_name=v.comp_moduleset.modset_name))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_delete_variable(var_id):
    q = db.comp_rulesets_variables.id == var_id
    q1 = db.comp_rulesets.id == db.comp_rulesets_variables.ruleset_id
    v = db(q & q1).select(cacheable=True).first()
    if v is None:
        return "0"
    db(q).delete()
    table_modified("comp_rulesets_variables")
    _log('compliance.variable.delete',
         'deleted variable %(var_name)s from ruleset %(rset_name)s',
         dict(var_name=v.comp_rulesets_variables.var_name,
              rset_name=v.comp_rulesets.ruleset_name))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_set_var_class(var_id, var_class):
    q = db.comp_rulesets_variables.id == var_id
    q1 = db.comp_rulesets.id == db.comp_rulesets_variables.ruleset_id
    q1 &= db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return "-1"
    db(q).update(var_class=var_class)
    _log('compliance.variable.change',
         'set variable %(var_name)s class from %(old)s to %(new)s in ruleset %(rset_name)s',
         dict(var_name=v.comp_rulesets_variables.var_name,
              old=v.comp_rulesets_variables.var_class,
              new=var_class,
              rset_name=v.comp_rulesets.ruleset_name))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_set_log_op(obj_id, obj_type, parent_obj_id, log_op):
    if obj_type == "filter":
        return json_tree_action_set_filter_log_op(obj_id, parent_obj_id, log_op)
    elif obj_type == "filterset":
        return json_tree_action_set_filterset_log_op(obj_id, parent_obj_id, log_op)
    else:
        return {'err': 'unsupported action on this object type'}

@auth.requires_membership('CompManager')
def json_tree_action_set_filterset_log_op(obj_id, parent_obj_id, log_op):
    q = db.gen_filtersets.id == obj_id
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "filterset does not exist"}

    q = db.gen_filtersets.id == parent_obj_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"err": "filterset does not exist"}

    q = db.gen_filtersets_filters.fset_id == parent_obj_id
    q &= db.gen_filtersets_filters.encap_fset_id == obj_id
    rows = db(q).select(cacheable=True)
    x = rows.first()
    if x.f_log_op == log_op:
        return {"err": "filterset logical operator is already '%(log_op)s'"%dict(log_op=log_op)}
    db(q).update(f_log_op=log_op)

    db.commit()

    _log('compliance.filterset.change',
         'set filterset %(encap_fset_name)s logical operator from %(old)s to %(new)s in filterset %(fset_name)s',
         dict(old=x.f_log_op,
              encap_fset_name=v.fset_name,
              new=log_op,
              fset_name=w.fset_name))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_set_filter_log_op(obj_id, parent_obj_id, log_op):
    q = db.gen_filters.id == obj_id
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "filter does not exist"}

    q = db.gen_filtersets.id == parent_obj_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"err": "filterset does not exist"}

    q = db.gen_filtersets_filters.fset_id == parent_obj_id
    q &= db.gen_filtersets_filters.f_id == obj_id
    rows = db(q).select(cacheable=True)
    x = rows.first()
    if x.f_log_op == log_op:
        return {"err": "filter logical operator is already '%(log_op)s'"%dict(log_op=log_op)}
    db(q).update(f_log_op=log_op)

    db.commit()

    _log('compliance.filter.change',
         'set filter %(f_name)s logical operator from %(old)s to %(new)s in filterset %(fset_name)s',
         dict(old=x.f_log_op,
              f_name=v.f_table+'.'+v.f_field+' '+v.f_op+' '+v.f_value,
              new=log_op,
              fset_name=w.fset_name))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_set_type(rset_id, rset_type):
    q = db.comp_rulesets.id == rset_id
    q1 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "ruleset does not exist or not owned by you"}
    if v.comp_rulesets.ruleset_type == rset_type:
        return {"err": "ruleset type is already '%(rset_type)s'"%dict(rset_type=rset_type)}
    db(q).update(ruleset_type=rset_type)

    if rset_type == "explicit":
        q = db.comp_rulesets_filtersets.ruleset_id == rset_id
        db(q).delete()
        table_modified("comp_rulesets_filtersets")

    db.commit()

    _log('compliance.ruleset.change',
         'set ruleset %(rset_name)s type from %(old)s to %(new)s',
         dict(rset_name=v.comp_rulesets.ruleset_name,
              old=v.comp_rulesets.ruleset_type,
              new=rset_type))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_set_stats(fset_id, value):
    q = db.gen_filtersets.id == fset_id
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "filterset does not exist"}
    db(q).update(fset_stats=value)
    _log('compliance.filterset.change',
         'set filterset %(fset_name)s stats from %(old)s to %(new)s',
         dict(fset_name=v.fset_name,
              old=v.fset_stats,
              new=value))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_set_autofix(modset_mod_id, autofix):
    q = db.comp_moduleset_modules.id == modset_mod_id
    q1 = db.comp_moduleset_modules.modset_id == db.comp_moduleset_team_responsible.modset_id
    q1 &= db.comp_moduleset_modules.modset_id == db.comp_moduleset.id
    if 'Manager' not in user_groups():
        q1 &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return "-1"
    db(q).update(autofix=autofix)
    _log('compliance.module.change',
         'set module %(modset_mod_name)s autofix from %(old)s to %(new)s in moduleset %(modset_name)s',
         dict(modset_mod_name=v.comp_moduleset_modules.modset_mod_name,
              old=str(v.comp_moduleset_modules.autofix),
              new=str(autofix),
              modset_name=v.comp_moduleset.modset_name))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_set_public(rset_id, public):
    q = db.comp_rulesets.id == rset_id
    q1 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return "-1"
    db(q).update(ruleset_public=public)
    _log('compliance.ruleset.change',
         'set ruleset %(rset_name)s publication from %(old)s to %(new)s',
         dict(rset_name=v.comp_rulesets.ruleset_name,
              old=v.comp_rulesets.ruleset_public,
              new=public))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_move_var_to_rset(var_id, rset_id):
    q = db.comp_rulesets_variables.id == var_id
    q1 = db.comp_rulesets_variables.ruleset_id == db.comp_ruleset_team_responsible.ruleset_id
    q1 &= db.comp_rulesets_variables.ruleset_id == db.comp_rulesets.id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "variable not found or originating ruleset not owned by you"}

    q2 = db.comp_rulesets.id == rset_id
    q3 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q3 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q2&q3).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"err": "destination ruleset not found or not owned by you"}

    db(q).update(ruleset_id=rset_id)
    _log('compliance.variable.change',
         'move variable %(var_name)s from ruleset %(rset_name)s to %(dst_rset_name)s',
         dict(rset_name=v.comp_rulesets.ruleset_name,
              dst_rset_name=w.comp_rulesets.ruleset_name,
              var_name=v.comp_rulesets_variables.var_name))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_copy_var_to_rset(var_id, rset_id):
    q = db.comp_rulesets_variables.id == var_id
    q1 = db.comp_rulesets_variables.ruleset_id == db.comp_ruleset_team_responsible.ruleset_id
    q1 &= db.comp_rulesets_variables.ruleset_id == db.comp_rulesets.id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "variable not found or originating ruleset not owned by you"}

    q2 = db.comp_rulesets.id == rset_id
    q3 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q3 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q2&q3).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"err": "destination ruleset not found or not owned by you"}

    _v = v.comp_rulesets_variables
    obj_id = db.comp_rulesets_variables.insert(
      ruleset_id=rset_id,
      var_name=_v.var_name,
      var_class=_v.var_class,
      var_value=_v.var_value,
      var_author=user_name(),
      var_updated=datetime.datetime.now(),
    )
    table_modified("comp_rulesets_variables")
    _log('compliance.variable.copy',
         'copy variable %(var_name)s from ruleset %(rset_name)s to %(dst_rset_name)s',
         dict(rset_name=v.comp_rulesets.ruleset_name,
              dst_rset_name=w.comp_rulesets.ruleset_name,
              var_name=v.comp_rulesets_variables.var_name))
    return {"obj_id": obj_id}

@auth.requires_membership('CompManager')
def json_tree_action_copy_rset_to_rset(rset_id, parent_rset_id, dst_rset_id):
    return json_tree_action_copy_or_move_rset_to_rset(rset_id, parent_rset_id, dst_rset_id, move=False)

@auth.requires_membership('CompManager')
def json_tree_action_move_rset_to_rset(rset_id, parent_rset_id, dst_rset_id):
    return json_tree_action_copy_or_move_rset_to_rset(rset_id, parent_rset_id, dst_rset_id, move=True)

def fset_get_ancestors():
    q = db.gen_filtersets_filters.f_id == 0
    rows = db(q).select()
    ancestors = {}
    for row in rows:
        if row.encap_fset_id not in ancestors:
            ancestors[row.encap_fset_id] = []
        ancestors[row.encap_fset_id].append(row.fset_id)
    return ancestors

def fset_loop(fset_id, parent_fset_id):
    if fset_id == parent_fset_id:
        return True
    fset_id = int(fset_id)
    parent_fset_id = int(parent_fset_id)
    ancestors = fset_get_ancestors()
    tested = []
    def recurse_rel(fset_id, parent_fset_id):
        if parent_fset_id not in ancestors:
            return False
        for _parent_fset_id in ancestors[parent_fset_id]:
            tested.append("%d-%d"%(fset_id,_parent_fset_id))
            if fset_id == _parent_fset_id:
                return True
            if recurse_rel(fset_id, _parent_fset_id):
                return True
        return False

    return recurse_rel(fset_id, parent_fset_id)

def rset_loop(rset_id, parent_rset_id):
    rset_id = int(rset_id)
    parent_rset_id = int(parent_rset_id)
    q = db.comp_rulesets_rulesets.id > 0
    rows = db(q).select()
    ancestors = {}
    for row in rows:
        if row.child_rset_id not in ancestors:
            ancestors[row.child_rset_id] = []
        ancestors[row.child_rset_id].append(row.parent_rset_id)

    tested = []
    def recurse_rel(rset_id, parent_rset_id):
        if parent_rset_id not in ancestors:
            return False
        for _parent_rset_id in ancestors[parent_rset_id]:
            tested.append("%d-%d"%(rset_id,_parent_rset_id))
            if rset_id == _parent_rset_id:
                return True
            if recurse_rel(rset_id, _parent_rset_id):
                return True
        return False

    return recurse_rel(rset_id, parent_rset_id)

@auth.requires_membership('CompManager')
def json_tree_action_copy_or_move_rset_to_rset(rset_id, parent_rset_id, dst_rset_id, move=False):
    if dst_rset_id == rset_id:
        return {"err": "abort action to avoid introducing a recursion loop"}

    q = db.comp_rulesets_rulesets.parent_rset_id == dst_rset_id
    q &= db.comp_rulesets_rulesets.child_rset_id == rset_id
    if db(q).count() > 0:
        return {"err": "ruleset already attached"}

    q = db.comp_rulesets.id == rset_id
    q1 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "attached ruleset not found or not owned by you"}

    q2 = db.comp_rulesets.id == dst_rset_id
    q3 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q3 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q2&q3).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"err": "destination ruleset not found or not owned by you"}

    if rset_loop(rset_id, dst_rset_id):
        return {"err": "the parent ruleset is already a child of the encapsulated ruleset. abort encapsulation not to cause infinite recursion"}

    db.comp_rulesets_rulesets.insert(
      parent_rset_id=dst_rset_id,
      child_rset_id=rset_id,
    )
    table_modified("comp_rulesets_rulesets")
    _log('compliance.ruleset.attach',
         'attach ruleset %(rset_name)s to %(dst_rset_name)s',
         dict(rset_name=v.comp_rulesets.ruleset_name,
              dst_rset_name=w.comp_rulesets.ruleset_name))
    comp_rulesets_chains()
    if not move or parent_rset_id is None or parent_rset_id == dst_rset_id:
        return "0"

    q = db.comp_rulesets_rulesets.parent_rset_id == parent_rset_id
    q &= db.comp_rulesets_rulesets.child_rset_id == rset_id
    q1 = db.comp_rulesets_rulesets.parent_rset_id == db.comp_rulesets.id
    q1 &= db.comp_rulesets_rulesets.parent_rset_id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    x = rows.first()
    if x is None:
        return {"err": "parent ruleset not found or not owned by you"}

    db(q).delete()
    table_modified("comp_rulesets_rulesets")
    _log('compliance.ruleset.detach',
         'detach ruleset %(rset_name)s from %(parent_rset_name)s',
         dict(rset_name=v.comp_rulesets.ruleset_name,
              parent_rset_name=x.comp_rulesets.ruleset_name))
    comp_rulesets_chains()
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_detach_filterset(obj_id, parent_obj_id, parent_obj_type):
    if parent_obj_type.startswith("ruleset"):
        return json_tree_action_detach_filterset_from_rset(parent_obj_id)
    elif parent_obj_type == "filterset":
        return json_tree_action_detach_filterset_from_filterset(obj_id, parent_obj_id)
    else:
        return {"err": "detach filterset not supported for this parent object type"}

@auth.requires_membership('CompManager')
def json_tree_action_detach_group(group_id, obj_id, parent_obj_type):
    if parent_obj_type.startswith("ruleset"):
        return json_tree_action_detach_group_from_rset(group_id, obj_id)
    elif parent_obj_type == "modset":
        return json_tree_action_detach_group_from_modset(group_id, obj_id)
    else:
        return {"err": "detach group not supported for this parent object type"}

@auth.requires_membership('CompManager')
def json_tree_action_detach_group_from_modset(group_id, modset_id):
    q = db.comp_moduleset.id == modset_id
    q1 = db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "moduleset not found or not owned by you"}

    q = db.auth_group.id == group_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"err": "group not found"}

    q = db.comp_moduleset_team_responsible.modset_id == modset_id
    q &= db.comp_moduleset_team_responsible.group_id == group_id
    db(q).delete()
    table_modified("comp_moduleset_team_responsible")
    _log('compliance.moduleset.detach',
         'detach group %(role)s from moduleset %(modset_name)s',
         dict(modset_name=v.comp_moduleset.modset_name,
              role=w.role))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_detach_group_from_rset(group_id, rset_id):
    q = db.comp_rulesets.id == rset_id
    q1 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "ruleset not found or not owned by you"}

    q = db.auth_group.id == group_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"err": "group not found"}

    q = db.comp_ruleset_team_responsible.ruleset_id == rset_id
    q &= db.comp_ruleset_team_responsible.group_id == group_id
    db(q).delete()
    table_modified("comp_ruleset_team_responsible")
    _log('compliance.ruleset.detach',
         'detach group %(role)s from ruleset %(rset_name)s',
         dict(rset_name=v.comp_rulesets.ruleset_name,
              role=w.role))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_detach_moduleset_from_moduleset(child_modset_id, parent_modset_id):
    q = db.comp_moduleset.id == parent_modset_id
    q1 = db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "parent moduleset not found or not owned by you"}

    q = db.comp_moduleset.id == child_modset_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"err": "child ruleset not found"}

    q = db.comp_moduleset_moduleset.parent_modset_id == parent_modset_id
    q &= db.comp_moduleset_moduleset.child_modset_id == child_modset_id
    db(q).delete()
    table_modified("comp_moduleset_moduleset")
    _log('compliance.moduleset.detach',
         'detach moduleset %(child_modset_name)s from moduleset %(parent_modset_name)s',
         dict(parent_modset_name=v.comp_moduleset.modset_name,
              child_modset_name=w.modset_name))
    #comp_rulesets_chains()
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_detach_ruleset_from_moduleset(rset_id, modset_id):
    q = db.comp_moduleset.id == modset_id
    q1 = db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "parent moduleset not found or not owned by you"}

    q = db.comp_rulesets.id == rset_id
    q1 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"err": "child ruleset not found or not owned by you"}

    q = db.comp_moduleset_ruleset.modset_id == modset_id
    q &= db.comp_moduleset_ruleset.ruleset_id == rset_id
    db(q).delete()
    table_modified("comp_moduleset_ruleset")
    _log('compliance.ruleset.detach',
         'detach ruleset %(rset_name)s from moduleset %(modset_name)s',
         dict(rset_name=w.comp_rulesets.ruleset_name,
              modset_name=v.comp_moduleset.modset_name))
    #comp_rulesets_chains()
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_detach_ruleset(rset_id, parent_rset_id):
    q = db.comp_rulesets.id == parent_rset_id
    q1 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "parent ruleset not found or not owned by you"}

    q = db.comp_rulesets.id == rset_id
    q1 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"err": "child ruleset not found or not owned by you"}

    q = db.comp_rulesets_rulesets.parent_rset_id == parent_rset_id
    q &= db.comp_rulesets_rulesets.child_rset_id == rset_id
    db(q).delete()
    table_modified("comp_rulesets_rulesets")
    _log('compliance.ruleset.detach',
         'detach ruleset %(rset_name)s from %(parent_rset_name)s',
         dict(rset_name=w.comp_rulesets.ruleset_name,
              parent_rset_name=v.comp_rulesets.ruleset_name))
    comp_rulesets_chains()
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_copy_filter_to_fset(f_id, fset_id):
    q = db.gen_filters.id == f_id
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "filter not found"}

    q = db.gen_filtersets.id == fset_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"err": "filterset not found"}

    q = db.gen_filtersets_filters.f_id == f_id
    q &= db.gen_filtersets_filters.fset_id == fset_id
    if db(q).count() > 0:
        return "0"

    db.gen_filtersets_filters.insert(f_id=f_id,
                                     fset_id=fset_id,
                                     f_order=0,
                                     f_log_op="AND")
    table_modified("gen_filtersets_filters")

    _log('compliance.filter.attach',
         'attach filter %(f_name)s to filterset %(fset_name)s',
         dict(fset_name=w.fset_name,
              f_name=v.f_table+'.'+v.f_field+' '+v.f_op+' '+v.f_value))
    return 0

@auth.requires_membership('CompManager')
def json_tree_action_copy_fset_to_fset(fset_id, dst_fset_id):
    q = db.gen_filtersets.id == dst_fset_id
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "filterset not found"}

    q = db.gen_filtersets.id == fset_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"err": "filterset not found"}

    q = db.gen_filtersets_filters.encap_fset_id == fset_id
    q &= db.gen_filtersets_filters.fset_id == dst_fset_id
    if db(q).count() > 0:
        return "0"

    if fset_loop(fset_id, dst_fset_id):
        return {"err": "the parent filterset is already a child of the encapsulated filterset. abort encapsulation not to cause infinite recursion"}

    db.gen_filtersets_filters.insert(encap_fset_id=fset_id,
                                     fset_id=dst_fset_id,
                                     f_order=0,
                                     f_log_op="AND")
    table_modified("gen_filtersets_filters")

    _log('compliance.filterset.attach',
         'attach filterset %(fset_name)s to filterset %(dst_fset_name)s',
         dict(dst_fset_name=v.fset_name,
              fset_name=w.fset_name))
    return 0

@auth.requires_membership('CompManager')
def json_tree_action_move_fset_to_rset(fset_id, rset_id):
    q = db.comp_rulesets.id == rset_id
    q1 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "ruleset not found or not owned by you"}

    q = db.gen_filtersets.id == fset_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"err": "filterset not found"}

    q = db.comp_rulesets_filtersets.ruleset_id == rset_id
    q &= db.comp_rulesets_filtersets.fset_id == fset_id
    if db(q).count() > 0:
        return "0"

    db.comp_rulesets_filtersets.update_or_insert(db.comp_rulesets_filtersets.ruleset_id==rset_id,
                                                 ruleset_id=rset_id,
                                                 fset_id=fset_id)
    table_modified("comp_rulesets_filtersets")
    _log('compliance.ruleset.change',
         'attach filterset %(fset_name)s to ruleset %(rset_name)s',
         dict(rset_name=v.comp_rulesets.ruleset_name,
              fset_name=w.fset_name))
    return 0

@auth.requires_membership('CompManager')
def json_tree_action_detach_filter(f_id, fset_id):
    q = db.gen_filtersets.id == fset_id
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "filterset not found"}

    q = db.gen_filters.id == f_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"err": "filter not found"}

    q = db.gen_filtersets_filters.f_id == f_id
    q &= db.gen_filtersets_filters.fset_id == fset_id
    if len(db(q).select()) == 0:
        return 0

    db(q).delete()
    table_modified("gen_filtersets_filters")
    _log('compliance.filter.detach',
         'detach filter %(f_name)s from filterset %(fset_name)s',
         dict(fset_name=v.fset_name,
              f_name=w.f_table+'.'+w.f_field+' '+w.f_op+' '+w.f_value))
    return 0

@auth.requires_membership('CompManager')
def json_tree_action_detach_filterset_from_filterset(fset_id, parent_fset_id):
    q = db.gen_filtersets.id == parent_fset_id
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "filterset not found"}

    q = db.gen_filtersets.id == fset_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"err": "filterset not found"}

    q = db.gen_filtersets_filters.encap_fset_id == fset_id
    q &= db.gen_filtersets_filters.fset_id == parent_fset_id
    if len(db(q).select()) == 0:
        return 0

    db(q).delete()
    table_modified("gen_filtersets_filters")
    _log('compliance.filterset.detach',
         'detach filterset %(fset_name)s from filterset %(parent_fset_name)s',
         dict(fset_name=w.fset_name,
              parent_fset_name=v.fset_name))
    return 0

@auth.requires_membership('CompManager')
def json_tree_action_detach_filterset_from_rset(rset_id):
    q = db.comp_rulesets.id == rset_id
    q1 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "ruleset not found or not owned by you"}

    q = db.comp_rulesets_filtersets.ruleset_id == rset_id
    q &= db.gen_filtersets.id == db.comp_rulesets_filtersets.fset_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"err": "filterset not found"}

    q = db.comp_rulesets_filtersets.ruleset_id == rset_id
    db(q).delete()
    table_modified("comp_rulesets_filtersets")
    _log('compliance.filterset.detach',
         'detach filterset %(fset_name)s from ruleset %(rset_name)s',
         dict(rset_name=v.comp_rulesets.ruleset_name,
              fset_name=w.gen_filtersets.fset_name))
    return 0

@auth.requires_membership('CompManager')
def json_tree_action_move_group_to_modset(group_id, modset_id):
    ug = user_groups()
    q = db.comp_moduleset.id == modset_id
    q1 = db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    if 'Manager' not in ug:
        q1 &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "moduleset not found or not owned by you"}

    q = db.auth_group.id == group_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"err": "group not found"}

    if 'Manager' not in ug and int(group_id) not in user_group_ids():
        return {"err": "you can't attach a group you are not a member of"}

    q = db.comp_moduleset_team_responsible.modset_id == modset_id
    q &= db.comp_moduleset_team_responsible.group_id == group_id
    if db(q).count() > 0:
        return "0"

    db.comp_moduleset_team_responsible.update_or_insert(modset_id=modset_id,
                                                        group_id=group_id)
    table_modified("comp_moduleset_team_responsible")
    _log('compliance.moduleset.change',
         'attach group %(role)s to moduleset %(modset_name)s',
         dict(modset_name=v.comp_moduleset.modset_name,
              role=w.role))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_copy_modset_to_modset(child_modset_id, parent_modset_id):
    ug = user_groups()
    q = db.comp_moduleset.id == parent_modset_id
    q1 = db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    if 'Manager' not in ug:
        q1 &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "parent moduleset not found or not owned by you"}

    q = db.comp_moduleset.id == child_modset_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"err": "child moduleset not found"}

    q = db.comp_moduleset_moduleset.parent_modset_id == parent_modset_id
    q &= db.comp_moduleset_moduleset.child_modset_id == child_modset_id
    if db(q).count() > 0:
        return "0"

    db.comp_moduleset_moduleset.update_or_insert(parent_modset_id=parent_modset_id,
                                                 child_modset_id=child_modset_id)
    table_modified("comp_moduleset_moduleset")
    _log('compliance.moduleset.moduleset.attach',
         'attach moduleset %(child_modset_name)s to moduleset %(parent_modset_name)s',
         dict(child_modset_name=w.modset_name,
              parent_modset_name=v.comp_moduleset.modset_name))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_copy_rset_to_modset(rset_id, modset_id):
    ug = user_groups()
    q = db.comp_moduleset.id == modset_id
    q1 = db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    if 'Manager' not in ug:
        q1 &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "moduleset not found or not owned by you"}

    q = db.comp_rulesets.id == rset_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"err": "ruleset not found"}

    q = db.comp_moduleset_ruleset.ruleset_id == rset_id
    q &= db.comp_moduleset_ruleset.modset_id == modset_id
    if db(q).count() > 0:
        return "0"

    db.comp_moduleset_ruleset.update_or_insert(ruleset_id=rset_id,
                                               modset_id=modset_id)
    table_modified("comp_moduleset_ruleset")
    _log('compliance.moduleset.ruleset.attach',
         'attach ruleset %(rset_name)s to moduleset %(modset_name)s',
         dict(modset_name=v.comp_moduleset.modset_name,
              rset_name=w.ruleset_name))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_move_group_to_rset(group_id, rset_id):
    ug = user_groups()
    q = db.comp_rulesets.id == rset_id
    q1 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in ug:
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "ruleset not found or not owned by you"}

    q = db.auth_group.id == group_id
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is None:
        return {"err": "group not found"}

    if 'Manager' not in ug and int(group_id) not in user_group_ids():
        return {"err": "you can't attach a group you are not a member of"}

    q = db.comp_ruleset_team_responsible.ruleset_id == rset_id
    q &= db.comp_ruleset_team_responsible.group_id == group_id
    if db(q).count() > 0:
        return "0"

    db.comp_ruleset_team_responsible.update_or_insert(ruleset_id=rset_id,
                                                      group_id=group_id)
    table_modified("comp_ruleset_team_responsible")
    _log('compliance.ruleset.change',
         'attach group %(role)s to ruleset %(rset_name)s',
         dict(rset_name=v.comp_rulesets.ruleset_name,
              role=w.role))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_clone_moduleset(modset_id):
    q = db.comp_moduleset.id == modset_id
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "source moduleset not found"}

    modset_name = v.modset_name
    clone_modset_name = modset_name+"_clone"
    q = db.comp_moduleset.modset_name == clone_modset_name
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is not None:
        return {"err": "a moduleset named %s already exists" % clone_modset_name}

    newid = db.comp_moduleset.insert(modset_name=clone_modset_name,
                                     modset_author=user_name(),
                                     modset_updated=datetime.datetime.now())
    table_modified("comp_moduleset")

    # clone moduleset modules
    q = db.comp_moduleset_modules.modset_id == modset_id
    rows = db(q).select(cacheable=True)
    for row in rows:
        db.comp_moduleset_modules.insert(modset_id=newid,
                                         modset_mod_name=row.modset_mod_name,
                                         modset_mod_author=row.modset_mod_author,
                                         modset_mod_updated=datetime.datetime.now())
    table_modified("comp_moduleset_modules")
    add_default_team_responsible_to_modset(clone_modset_name)

    _log('compliance.moduleset.clone',
         'cloned moduleset %(o)s from %(n)s',
         dict(n=modset_name, o=clone_modset_name))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_clone_ruleset(rset_id):
    q = db.comp_rulesets.id == rset_id
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "source ruleset not found"}

    rset_name = v.ruleset_name
    clone_rset_name = rset_name+"_clone"
    q = db.comp_rulesets.ruleset_name == clone_rset_name
    rows = db(q).select(cacheable=True)
    w = rows.first()
    if w is not None:
        return {"err": "a ruleset named %s already exists" % clone_rset_name}

    newid = db.comp_rulesets.insert(ruleset_name=clone_rset_name,
                                    ruleset_type=v.ruleset_type,
                                    ruleset_public=v.ruleset_public)
    table_modified("comp_rulesets")

    # clone filterset for contextual rulesets
    if v.ruleset_type == 'contextual':
        q = db.comp_rulesets.id == rset_id
        q &= db.comp_rulesets.id == db.comp_rulesets_filtersets.ruleset_id
        rows = db(q).select(cacheable=True)
        if len(rows) > 0 and  rows[0].comp_rulesets_filtersets.fset_id is not None:
            db.comp_rulesets_filtersets.insert(ruleset_id=newid,
                                               fset_id=rows[0].comp_rulesets_filtersets.fset_id)
            table_modified("comp_rulesets_filtersets")

    # clone ruleset variables
    q = db.comp_rulesets_variables.ruleset_id == rset_id
    rows = db(q).select(cacheable=True)
    for row in rows:
        db.comp_rulesets_variables.insert(ruleset_id=newid,
                                          var_name=row.var_name,
                                          var_class=row.var_class,
                                          var_value=row.var_value,
                                          var_author=user_name())
    table_modified("comp_rulesets_variables")
    add_default_team_responsible(clone_rset_name)

    # clone parent to children relations
    q = db.comp_rulesets_rulesets.parent_rset_id==rset_id
    rows = db(q).select(cacheable=True)
    for child_rset_id in [r.child_rset_id for r in rows]:
        db.comp_rulesets_rulesets.insert(parent_rset_id=newid,
                                         child_rset_id=child_rset_id)
    table_modified("comp_rulesets_rulesets")

    comp_rulesets_chains()

    _log('compliance.ruleset.clone',
         'cloned ruleset %(o)s from %(n)s',
         dict(n=rset_name, o=clone_rset_name))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_delete_filterset(fset_id):
    q = db.gen_filtersets.id == fset_id
    rows = db(q).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "filterset not found"}

    q = db.gen_filtersets_filters.fset_id == fset_id
    db(q).delete()
    table_modified("gen_filtersets_filters")

    q = db.gen_filtersets_filters.encap_fset_id == fset_id
    db(q).delete()
    table_modified("gen_filtersets_filters")

    q = db.comp_rulesets_filtersets.fset_id == fset_id
    db(q).delete()
    table_modified("comp_rulesets_filtersets")

    q = db.gen_filterset_team_responsible.fset_id == fset_id
    db(q).delete()
    table_modified("gen_filterset_team_responsible")

    q = db.gen_filterset_check_threshold.fset_id == fset_id
    db(q).delete()
    table_modified("gen_filterset_check_threshold")

    q = db.gen_filterset_user.fset_id == fset_id
    db(q).delete()
    table_modified("gen_filterset_user")

    q = db.stats_compare_fset.fset_id == fset_id
    db(q).delete()
    table_modified("stats_compare_fset")

    q = db.stat_day_billing.fset_id == fset_id
    db(q).delete()
    table_modified("stat_day_billing")

    q = db.stat_day.fset_id == fset_id
    db(q).delete()
    table_modified("stat_day")

    q = db.metrics_log.fset_id == fset_id
    db(q).delete()
    table_modified("metrics_log")

    q = db.lifecycle_os.fset_id == fset_id
    db(q).delete()
    table_modified("lifecycle_os")

    q = db.gen_filtersets.id == fset_id
    db(q).delete()
    table_modified("gen_filtersets")

    _log('compliance.filterset.delete',
         'deleted filterset %(fset_name)s',
         dict(fset_name=v.fset_name))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_delete_ruleset(rset_id):
    q = db.comp_rulesets.id == rset_id
    q1 = db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "ruleset not found or not owned by you"}

    q = db.comp_rulesets_filtersets.ruleset_id == rset_id
    db(q).delete()
    table_modified("comp_rulesets_filtersets")

    q = db.comp_rulesets_nodes.ruleset_id == rset_id
    db(q).delete()
    table_modified("comp_rulesets_nodes")

    q = db.comp_rulesets_services.ruleset_id == rset_id
    db(q).delete()
    table_modified("comp_rulesets_services")

    q = db.comp_ruleset_team_responsible.ruleset_id == rset_id
    db(q).delete()
    table_modified("comp_ruleset_team_responsible")

    q = db.comp_rulesets_rulesets.parent_rset_id == rset_id
    db(q).delete()
    table_modified("comp_rulesets_rulesets")

    q = db.comp_rulesets_rulesets.child_rset_id == rset_id
    db(q).delete()
    table_modified("comp_rulesets_rulesets")

    q = db.comp_rulesets_variables.ruleset_id == rset_id
    db(q).delete()
    table_modified("comp_rulesets_variables")

    q = db.comp_rulesets.id == rset_id
    db(q).delete()
    table_modified("comp_rulesets")

    comp_rulesets_chains()

    _log('compliance.ruleset.delete',
         'deleted ruleset %(rset_name)s',
         dict(rset_name=v.comp_rulesets.ruleset_name))
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_delete_moduleset(modset_id):
    q = db.comp_moduleset.id == modset_id
    q1 = db.comp_moduleset.id == db.comp_moduleset_team_responsible.modset_id
    if 'Manager' not in user_groups():
        q1 &= db.comp_moduleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q&q1).select(cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "moduleset not found or not owned by you"}

    q = db.comp_node_moduleset.modset_id == modset_id
    db(q).delete()
    table_modified("comp_node_moduleset")

    q = db.comp_modulesets_services.modset_id == modset_id
    db(q).delete()
    table_modified("comp_modulesets_services")

    q = db.comp_moduleset_team_responsible.modset_id == modset_id
    db(q).delete()
    table_modified("comp_moduleset_team_responsible")

    q = db.comp_moduleset_modules.modset_id == modset_id
    db(q).delete()
    table_modified("comp_moduleset_modules")

    q = db.comp_moduleset.id == modset_id
    db(q).delete()
    table_modified("comp_moduleset")

    _log('compliance.moduleset.delete',
         'deleted moduleset %(modset_name)s',
         dict(modset_name=v.comp_moduleset.modset_name))
    return "0"


