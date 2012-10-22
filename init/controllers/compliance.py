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
# Sub-view menu
#
def comp_menu(current):
    m = [{
          'title': 'Status',
          'url': URL(
                   request.application,
                   'compliance',
                   'comp_status'
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
        ]

    def item(i):
        if i['title'] == current:
            bg = 'orange'
        else:
            bg = '#f0f1dd'
        d = DIV(
              i['title'],
              _class='menu_item clickable',
              _style='background-color:%s'%bg,
              _onclick="location.href='%s'"%i['url'],
              _onmouseover="this.style.backgroundColor='orange'",
              _onmouseout="this.style.backgroundColor='%s'"%bg,
            )
        return d

    d = DIV(
          SPAN(map(lambda x: item(x), m)),
          DIV(XML('&nbsp;'), _class='spacer'),
          _style='background-color:#e0e1cd;',
        )
    return d

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
    import json
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
    def html_raw(self, o):
        s = self.get(o)
        if s == '':
            ss = '(no value)'
        else:
            ss = s
        d = DIV(
              PRE(ss),
              _class="comp16",
              _style="min-height:16px",
            )
        return d

    def form_raw(self, o):
        s = self.get(o)
        if s == '':
            ss = '(no value)'
        else:
            ss = s
        iid = 'vd_i_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        d = DIV(
              TEXTAREA(
                value=s,
                _id=iid,
                _onkeypress="if (is_enter(event)) {%s};"%\
                   self.t.ajax_submit(additional_inputs=[iid],
                                      args="var_value_set"),
              ),
            )
        return d

    def html_process(self, o):
        v = self.get(o)
        l = [DIV(
               DIV('comm', _style='display:table-cell;font-weight:bold', _class="comp16"),
               DIV('state', _style='display:table-cell'),
               DIV('uid', _style='display:table-cell'),
               DIV('user', _style='display:table-cell'),
               DIV('start', _style='display:table-cell'),
               _style="display:table-row",
             )]
        try:
            lines = json.loads(v)
        except:
            return SPAN("malformed value", PRE(v))
        for line in lines:
            if 'comm' in line:
                comm = '%s'%str(line['comm'])
            else:
                comm = "-"
            if 'state' in line:
                state = '%s'%str(line['state'])
            else:
                state = "-"
            if 'uid' in line:
                uid = '%s'%str(line['uid'])
            else:
                uid = "-"
            if 'user' in line:
                user = '%s'%line['user']
            else:
                user = "-"
            if 'start' in line:
                start = '%s'%line['start']
            else:
                start = "-"
            l += [DIV(
                    DIV('%s '%comm, _style='display:table-cell', _class="action16"),
                    DIV(state, _style='display:table-cell'),
                    DIV(uid, _style='display:table-cell'),
                    DIV(user, _style='display:table-cell'),
                    DIV(start, _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        return DIV(l, _class="comp_var_table")

    def form_process(self, o):
        name = 'process_n_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        l = [DIV(
               DIV('comm', _style='display:table-cell;font-weight:bold', _class="comp16"),
               DIV('state', _style='display:table-cell'),
               DIV('uid', _style='display:table-cell'),
               DIV('user', _style='display:table-cell'),
               DIV('start', _style='display:table-cell'),
               _style="display:table-row",
             )]
        v = self.get(o)
        if v is None or v == "":
            f = {}
        else:
            try:
                f = json.loads(v)
            except:
                return self.form_raw(o)
        for i, line in enumerate(f):
            ll = [DIV(
                    INPUT(
                      _name=name,
                      _id="%s_%d_%s"%(name, i, 'comm'),
                      _value=line['comm'],
                      _style='width:5em',
                    ),
                    _style='display:table-cell',
                    _class="action16",
                  )]
            for key,w in (('state', '3em'),
                          ('uid', '3em'),
                          ('user', '3em'),
                          ('start', 'auto')):
                if key not in line:
                    value = ""
                else:
                    value = line[key]
                ll += [DIV(
                         INPUT(
                           _name=name,
                           _id="%s_%d_%s"%(name, i, key),
                           _value=value,
                           _style='width:%s'%w,
                         ),
                         _style='display:table-cell',
                       )]
            l += [DIV(
                    ll,
                    _style="display:table-row",
                  )]
        form = DIV(
                 SPAN(l, _id=name+'_container'),
                 BR(),
                 INPUT(
                   _value="Add",
                   _type="submit",
                   _onclick="""d=new Date();
i=d.getTime();$("#%(n)s_container").append("<div style='display:table-row'><div style='display:table-cell'><span class='action16'></span><input style='width:5em' name='%(n)s' id='%(n)s_"+i+"_comm'></div><div style='display:table-cell'><input style='width:3em' name='%(n)s' id='%(n)s_"+i+"_state'></div><div style='display:table-cell'><input style='width:3em' name='%(n)s' id='%(n)s_"+i+"_uid'></div><div style='display:table-cell'><input style='width:3em' name='%(n)s' id='%(n)s_"+i+"_user'></div><div style='display:table-cell'><input style='width:3em' name='%(n)s' id='%(n)s_"+i+"_start'></div></div>")"""%dict(n=name),
                 ),
                 " ",
                 INPUT(
                   _type="submit",
                   _onclick=self.t.ajax_submit(additional_input_name=name,
                                               args=["var_value_set_process", name]),
                 ),
                 _class="comp_var_table",
               )
        return form

    def html_nodeconf(self, o):
        return self.html_etcsystem(o)

    def form_nodeconf(self, o):
        name = 'nodeconf_n_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        l = [DIV(
               DIV('key', _style='display:table-cell;font-weight:bold', _class="comp16"),
               DIV('op', _style='display:table-cell'),
               DIV('value', _style='display:table-cell'),
               _style="display:table-row",
             )]
        v = self.get(o)
        if v is None or v == "":
            f = {}
        else:
            try:
                f = json.loads(v)
            except:
                return self.form_raw(o)
        for i, line in enumerate(f):
            ll = [DIV(
                    INPUT(
                      _name=name,
                      _id="%s_%d_%s"%(name, i, 'key'),
                      _value=line['key'],
                      _style='width:9em',
                    ),
                    _style='display:table-cell',
                    _class="action16",
                  )]
            for key,w in (('op', '3em'),
                          ('value', 'auto')):
                if key not in line:
                    value = ""
                else:
                    value = line[key]
                ll += [DIV(
                         INPUT(
                           _name=name,
                           _id="%s_%d_%s"%(name, i, key),
                           _value=value,
                           _style='width:%s'%w,
                         ),
                         _style='display:table-cell',
                       )]
            l += [DIV(
                    ll,
                    _style="display:table-row",
                  )]
        form = DIV(
                 SPAN(l, _id=name+'_container'),
                 BR(),
                 INPUT(
                   _value="Add",
                   _type="submit",
                   _onclick="""d=new Date();
i=d.getTime();$("#%(n)s_container").append("<div style='display:table-row'><div style='display:table-cell'><span class='action16'></span><input style='width:9em' name='%(n)s' id='%(n)s_"+i+"_key'></div><div style='display:table-cell'><input style='width:3em' name='%(n)s' id='%(n)s_"+i+"_op'></div><div style='display:table-cell'><input style='width:auto' name='%(n)s' id='%(n)s_"+i+"_value'></div></div>")"""%dict(n=name),
                 ),
                 " ",
                 INPUT(
                   _type="submit",
                   _onclick=self.t.ajax_submit(additional_input_name=name,
                                               args=["var_value_set_nodeconf", name]),
                 ),
                 _class="comp_var_table",
               )
        return form

    def html_etcsystem(self, o):
        v = self.get(o)
        l = [DIV(
               DIV('key', _style='display:table-cell;font-weight:bold', _class="comp16"),
               DIV('op', _style='display:table-cell'),
               DIV('value', _style='display:table-cell'),
               _style="display:table-row",
             )]
        try:
            lines = json.loads(v)
        except:
            return SPAN("malformed value", PRE(v))
        for line in lines:
            if 'key' in line:
                key = '%s'%str(line['key'])
            else:
                key = "-"
            if 'op' in line:
                op = '%s'%str(line['op'])
            else:
                op = "-"
            if 'value' in line:
                value = '%s'%line['value']
            else:
                value = "-"
            l += [DIV(
                    DIV('%s '%key, _style='display:table-cell', _class="action16"),
                    DIV(op, _style='display:table-cell'),
                    DIV(value, _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        return DIV(l, _class="comp_var_table")

    def form_etcsystem(self, o):
        name = 'etcsystem_n_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        l = [DIV(
               DIV('key', _style='display:table-cell;font-weight:bold', _class="comp16"),
               DIV('op', _style='display:table-cell'),
               DIV('value', _style='display:table-cell'),
               _style="display:table-row",
             )]
        v = self.get(o)
        if v is None or v == "":
            f = {}
        else:
            try:
                f = json.loads(v)
            except:
                return self.form_raw(o)
        for i, line in enumerate(f):
            ll = [DIV(
                    INPUT(
                      _name=name,
                      _id="%s_%d_%s"%(name, i, 'key'),
                      _value=line['key'],
                      _style='width:9em',
                    ),
                    _style='display:table-cell',
                    _class="action16",
                  )]
            for key,w in (('op', '3em'),
                          ('value', 'auto')):
                if key not in line:
                    value = ""
                else:
                    value = line[key]
                ll += [DIV(
                         INPUT(
                           _name=name,
                           _id="%s_%d_%s"%(name, i, key),
                           _value=value,
                           _style='width:%s'%w,
                         ),
                         _style='display:table-cell',
                       )]
            l += [DIV(
                    ll,
                    _style="display:table-row",
                  )]
        form = DIV(
                 SPAN(l, _id=name+'_container'),
                 BR(),
                 INPUT(
                   _value="Add",
                   _type="submit",
                   _onclick="""d=new Date();
i=d.getTime();$("#%(n)s_container").append("<div style='display:table-row'><div style='display:table-cell'><span class='action16'></span><input style='width:9em' name='%(n)s' id='%(n)s_"+i+"_key'></div><div style='display:table-cell'><input style='width:3em' name='%(n)s' id='%(n)s_"+i+"_op'></div><div style='display:table-cell'><input style='width:auto' name='%(n)s' id='%(n)s_"+i+"_value'></div></div>")"""%dict(n=name),
                 ),
                 " ",
                 INPUT(
                   _type="submit",
                   _onclick=self.t.ajax_submit(additional_input_name=name,
                                               args=["var_value_set_etcsystem", name]),
                 ),
                 _class="comp_var_table",
               )
        return form

    def html_symlink(self, o):
        v = self.get(o)
        try:
            e = json.loads(v)
        except:
            return SPAN("malformed value", PRE(v))
        l = [DIV(
               DIV('symlink', _style='display:table-cell;font-weight:bold', _class="comp16"),
               DIV(e['symlink'], _style='display:table-cell'),
               _style="display:table-row",
             )]
        if 'target' in e:
            l += [DIV(
                    DIV('target', _style='display:table-cell', _class="hd16"),
                    DIV(e['target'], _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        return DIV(l, _class="comp_var_table")

    def form_symlink(self, o):
        name = 'symlink_n_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        l = []
        v = self.get(o)
        if v is None or v == "":
            e = {}
        else:
            try:
                e = json.loads(v)
            except:
                return self.form_raw(o)
        for key, img in (('symlink', 'comp16'),
                         ('target', 'hd16')):
            if key not in e:
                value = ""
            else:
                value = e[key]
            _WIDGET = INPUT
            l += [DIV(
                   DIV(key, _style='display:table-cell;font-weight:bold', _class=img),
                   DIV(_WIDGET(_name=name, _id="%s_%s"%(name, key), value=value), _style='display:table-cell'),
                   _style="display:table-row",
                 )]
        form = DIV(
                 SPAN(l, _id=name+'_container'),
                 BR(),
                 INPUT(
                   _type="submit",
                   _onclick=self.t.ajax_submit(additional_input_name=name,
                                               args=["var_value_set_dict", name]),
                 ),
                 _class="comp_var_table",
               )
        return form

    def html_crontabentry(self, o):
        v = self.get(o)
        try:
            e = json.loads(v)
        except:
            return SPAN("malformed value", PRE(v))
        l = [DIV(
               DIV('check', _style='display:table-cell;font-weight:bold', _class="comp16"),
               DIV(e['check'], _style='display:table-cell'),
               _style="display:table-row",
             )]
        if 'user' in e:
            l += [DIV(
                    DIV('user', _style='display:table-cell', _class="guy16"),
                    DIV(e['user'], _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        if 'entry' in e:
            l += [DIV(
                    DIV('entry', _style='display:table-cell', _class="action16"),
                    DIV(e['entry'], _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        if 'ref' in e:
            l += [DIV(
                    DIV('ref', _style='display:table-cell', _class="loc"),
                    DIV(e['ref'], _style='display:table-cell'),
                    _style="display:table-row",
                  )]

        return DIV(l, _class="comp_var_table")

    def form_crontabentry(self, o):
        name = 'crontabentry_n_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        l = []
        v = self.get(o)
        if v is None or v == "":
            e = {}
        else:
            try:
                e = json.loads(v)
            except:
                return self.form_raw(o)
        for key, img in (('check', 'comp16'),
                         ('user', 'guy16'),
                         ('entry', 'action16'),
                         ('ref', 'loc')):
            if key not in e:
                value = ""
            else:
                value = e[key]
            if key == 'entry':
                _WIDGET = TEXTAREA
            else:
                _WIDGET = INPUT
            l += [DIV(
                   DIV(key, _style='display:table-cell;font-weight:bold', _class=img),
                   DIV(_WIDGET(_name=name, _id="%s_%s"%(name, key), value=value), _style='display:table-cell'),
                   _style="display:table-row",
                 )]
        form = DIV(
                 SPAN(l, _id=name+'_container'),
                 BR(),
                 INPUT(
                   _type="submit",
                   _onclick=self.t.ajax_submit(additional_input_name=name,
                                               args=["var_value_set_dict", name]),
                 ),
                 _class="comp_var_table",
               )
        return form

    def html_fileinc(self, o):
        v = self.get(o)
        try:
            e = json.loads(v)
        except:
            return SPAN("malformed value", PRE(v))
        l = [DIV(
               DIV('file', _style='display:table-cell;font-weight:bold', _class="comp16"),
               DIV(e['path'], _style='display:table-cell'),
               _style="display:table-row",
             )]
        if 'check' in e:
            l += [DIV(
                    DIV('check', _style='display:table-cell', _class="action16"),
                    DIV(e['check'], _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        if 'fmt' in e:
            l += [DIV(
                    DIV('fmt', _style='display:table-cell', _class="hd16"),
                    DIV(e['fmt'], _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        if 'ref' in e:
            l += [DIV(
                    DIV('ref', _style='display:table-cell', _class="loc"),
                    DIV(e['ref'], _style='display:table-cell'),
                    _style="display:table-row",
                  )]

        return DIV(l, _class="comp_var_table")

    def form_fileinc(self, o):
        name = 'fileinc_n_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        l = []
        v = self.get(o)
        if v is None or v == "":
            e = {}
        else:
            try:
                e = json.loads(v)
            except:
                return self.form_raw(o)
        for key, img in (('check', 'comp16'),
                         ('path', 'hd16'),
                         ('fmt', 'action16'),
                         ('ref', 'loc')):
            if key not in e:
                value = ""
            else:
                value = e[key]
            if key == 'fmt':
                _WIDGET = TEXTAREA
            else:
                _WIDGET = INPUT
            l += [DIV(
                   DIV(key, _style='display:table-cell;font-weight:bold', _class=img),
                   DIV(_WIDGET(_name=name, _id="%s_%s"%(name, key), value=value), _style='display:table-cell'),
                   _style="display:table-row",
                 )]
        form = DIV(
                 SPAN(l, _id=name+'_container'),
                 BR(),
                 INPUT(
                   _type="submit",
                   _onclick=self.t.ajax_submit(additional_input_name=name,
                                               args=["var_value_set_dict", name]),
                 ),
                 _class="comp_var_table",
               )
        return form

    def html_fileprop(self, o):
        v = self.get(o)
        try:
            e = json.loads(v)
        except:
            return SPAN("malformed value", PRE(v))
        l = [DIV(
               DIV('path', _style='display:table-cell;font-weight:bold', _class="comp16"),
               DIV(e['path'], _style='display:table-cell'),
               _style="display:table-row",
             )]
        if 'mode' in e:
            l += [DIV(
                    DIV('mode', _style='display:table-cell', _class="action16"),
                    DIV(e['mode'], _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        if 'uid' in e:
            l += [DIV(
                    DIV('gid', _style='display:table-cell', _class="guy16"),
                    DIV(e['gid'], _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        if 'gid' in e:
            l += [DIV(
                    DIV('gid', _style='display:table-cell', _class="guys16"),
                    DIV(e['gid'], _style='display:table-cell'),
                    _style="display:table-row",
                  )]

        return DIV(l, _class="comp_var_table")

    def form_fileprop(self, o):
        name = 'fileprop_n_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        l = []
        v = self.get(o)
        if v is None or v == "":
            e = {}
        else:
            try:
                e = json.loads(v)
            except:
                return self.form_raw(o)
        for key, img in (('path', 'hd16'),
                         ('mode', 'action16'),
                         ('uid', 'guy16'),
                         ('gid', 'guys16')):
            if key not in e:
                value = ""
            else:
                value = e[key]
            l += [DIV(
                   DIV(key, _style='display:table-cell;font-weight:bold', _class=img),
                   DIV(INPUT(_name=name, _id="%s_%s"%(name, key), value=value), _style='display:table-cell'),
                   _style="display:table-row",
                 )]
        form = DIV(
                 SPAN(l, _id=name+'_container'),
                 BR(),
                 INPUT(
                   _type="submit",
                   _onclick=self.t.ajax_submit(additional_input_name=name,
                                               args=["var_value_set_dict", name]),
                 ),
                 _class="comp_var_table",
               )
        return form

    def html_rc(self, o):
        v = self.get(o)
        l = [DIV(
               DIV('service', _style='display:table-cell;font-weight:bold', _class="comp16"),
               DIV('level', _style='display:table-cell'),
               DIV('seq', _style='display:table-cell'),
               DIV('state', _style='display:table-cell'),
               _style="display:table-row",
             )]
        try:
            lines = json.loads(v)
        except:
            return SPAN("malformed value", PRE(v))
        for line in lines:
            if 'service' in line:
                service = '%s'%str(line['service'])
            else:
                service = "-"
            if 'level' in line:
                level = '%s'%str(line['level'])
            else:
                level = "-"
            if 'seq' in line:
                seq = '%s'%str(line['seq'])
            else:
                seq = "-"
            if 'state' in line:
                state = '%s'%line['state']
            else:
                state = "-"
            l += [DIV(
                    DIV('%s '%service, _style='display:table-cell', _class="action16"),
                    DIV(level, _style='display:table-cell'),
                    DIV(seq, _style='display:table-cell'),
                    DIV(state, _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        return DIV(l, _class="comp_var_table")

    def form_rc(self, o):
        name = 'rc_n_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        l = [DIV(
               DIV('service', _style='display:table-cell;font-weight:bold', _class="comp16"),
               DIV('level', _style='display:table-cell'),
               DIV('seq', _style='display:table-cell'),
               DIV('state', _style='display:table-cell'),
               _style="display:table-row",
             )]
        v = self.get(o)
        if v is None or v == "":
            f = {}
        else:
            try:
                f = json.loads(v)
            except:
                return self.form_raw(o)
        for i, line in enumerate(f):
            ll = [DIV(
                    INPUT(
                      _name=name,
                      _id="%s_%d_%s"%(name, i, 'service'),
                      _value=line['service'],
                      _style='width:5em',
                    ),
                    _style='display:table-cell',
                    _class="action16",
                  )]
            for key,w in (('level', '3em'),
                          ('seq', '3em'),
                          ('state', 'auto')):
                if key not in line:
                    value = ""
                else:
                    value = line[key]
                ll += [DIV(
                         INPUT(
                           _name=name,
                           _id="%s_%d_%s"%(name, i, key),
                           _value=value,
                           _style='width:%s'%w,
                         ),
                         _style='display:table-cell',
                       )]
            l += [DIV(
                    ll,
                    _style="display:table-row",
                  )]
        form = DIV(
                 SPAN(l, _id=name+'_container'),
                 BR(),
                 INPUT(
                   _value="Add",
                   _type="submit",
                   _onclick="""d=new Date();
i=d.getTime();$("#%(n)s_container").append("<div style='display:table-row'><div style='display:table-cell'><span class='action16'></span><input style='width:5em' name='%(n)s' id='%(n)s_"+i+"_service'></div><div style='display:table-cell'><input style='width:3em' name='%(n)s' id='%(n)s_"+i+"_level'></div><div style='display:table-cell'><input style='width:3em' name='%(n)s' id='%(n)s_"+i+"_seq'></div><div style='display:table-cell'><input style='width:3em' name='%(n)s' id='%(n)s_"+i+"_state'></div></div>")"""%dict(n=name),
                 ),
                 " ",
                 INPUT(
                   _type="submit",
                   _onclick=self.t.ajax_submit(additional_input_name=name,
                                               args=["var_value_set_rc", name]),
                 ),
                 _class="comp_var_table",
               )
        return form

    def html_user(self, o):
        v = self.get(o)
        l = [DIV(
               DIV('user', _style='display:table-cell;font-weight:bold', _class="comp16"),
               DIV('uid', _style='display:table-cell'),
               DIV('gid', _style='display:table-cell'),
               DIV('shell', _style='display:table-cell'),
               DIV('home', _style='display:table-cell'),
               DIV('pwd', _style='display:table-cell'),
               DIV('gecos', _style='display:table-cell'),
               _style="display:table-row",
             )]
        try:
            users = json.loads(v)
        except:
            return SPAN("malformed value", PRE(v))
        for user, u in users.items():
            if 'uid' in u:
                uid = '%s'%str(u['uid'])
            else:
                uid = "-"
            if 'gid' in u:
                gid = '%s'%str(u['gid'])
            else:
                gid = "-"
            if 'shell' in u:
                shell = '%s'%u['shell']
            else:
                shell = "-"
            if 'home' in u:
                home = '%s'%u['home']
            else:
                home = "-"
            if 'password' in u:
                pwd = '%s'%u['password']
            else:
                pwd = "-"
            if 'gecos' in u:
                gecos = '%s'%u['gecos']
            else:
                gecos = "-"
            l += [DIV(
                    DIV('%s '%user, _style='display:table-cell', _class="guy16"),
                    DIV(uid, _style='display:table-cell'),
                    DIV(gid, _style='display:table-cell'),
                    DIV(shell, _style='display:table-cell'),
                    DIV(home, _style='display:table-cell'),
                    DIV(pwd, _style='display:table-cell'),
                    DIV(gecos, _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        return DIV(l, _class="comp_var_table")

    def form_user(self, o):
        name = 'group_n_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        l = [DIV(
               DIV('user', _style='display:table-cell;font-weight:bold', _class="comp16"),
               DIV('uid', _style='display:table-cell'),
               DIV('gid', _style='display:table-cell'),
               DIV('shell', _style='display:table-cell'),
               DIV('home', _style='display:table-cell'),
               DIV('pwd', _style='display:table-cell'),
               DIV('gecos', _style='display:table-cell'),
               _style="display:table-row",
             )]
        v = self.get(o)
        if v is None or v == "":
            f = {}
        else:
            try:
                f = json.loads(v)
            except:
                return self.form_raw(o)
        for i, user in enumerate(f):
            ll = [DIV(
                    INPUT(
                      _name=name,
                      _id="%s_%d_%s"%(name, i, 'user'),
                      _value=user,
                      _style='width:5em',
                    ),
                    _style='display:table-cell',
                    _class="guy16",
                  )]
            for key,w in (('uid', '3em'),
                          ('gid', '3em'),
                          ('shell', '5em'),
                          ('home', '5em'),
                          ('password', '3em'),
                          ('gecos', 'auto')):
                if key not in f[user]:
                    value = ""
                else:
                    value = f[user][key]
                ll += [DIV(
                         INPUT(
                           _name=name,
                           _id="%s_%d_%s"%(name, i, key),
                           _value=value,
                           _style='width:%s'%w,
                         ),
                         _style='display:table-cell',
                       )]
            l += [DIV(
                    ll,
                    _style="display:table-row",
                  )]
        form = DIV(
                 SPAN(l, _id=name+'_container'),
                 BR(),
                 INPUT(
                   _value="Add",
                   _type="submit",
                   _onclick="""d=new Date(); i=d.getTime();$("#%(n)s_container").append("<div style='display:table-row'><div style='display:table-cell'><span class='guy16'></span><input style='width:5em' name='%(n)s' id='%(n)s_"+i+"_user'></div><div style='display:table-cell'><input style='width:3em' name='%(n)s' id='%(n)s_"+i+"_uid'></div><div style='display:table-cell'><input style='width:3em' name='%(n)s' id='%(n)s_"+i+"_gid'></div><div style='display:table-cell'><input style='width:5em' name='%(n)s' id='%(n)s_"+i+"_shell'></div><div style='display:table-cell'><input style='width:5em' name='%(n)s' id='%(n)s_"+i+"_home'></div><div style='display:table-cell'><input name='%(n)s' id='%(n)s_"+i+"_password'></div><div style='display:table-cell'><input name='%(n)s' id='%(n)s_"+i+"_gecos'></div></div>")"""%dict(n=name),
                 ),
                 " ",
                 INPUT(
                   _type="submit",
                   _onclick=self.t.ajax_submit(additional_input_name=name,
                                               args=["var_value_set_user", name]),
                 ),
                 _class="comp_var_table",
               )
        return form

    def html_fs(self, o):
        v = self.get(o)
        l = []
        try:
            fss = json.loads(v)
        except:
            return SPAN("malformed value", PRE(v))
        if type(fss) != list:
            return v
        for fs in fss:
            if 'mnt' in fs:
                mnt = fs['mnt']
            else:
                mnt = "-"
            if 'dev' in fs:
                dev = fs['dev']
            else:
                dev = "-"
            if 'type' in fs:
                t = fs['type']
            else:
                t = "-"
            if 'size' in fs:
                size = fs['size']
            else:
                size = "-"
            if 'opts' in fs:
                opts = fs['opts']
            else:
                opts = "-"
            if 'vg' in fs:
                vg = map(lambda x: P(x), fs['vg'])
            else:
                vg = "-"
            l += [DIV(
                    DIV('fs', _style='display:table-cell;font-weight:bold', _class="comp16"),
                    _style="display:table-row",
                  ),
                  DIV(
                    DIV('dev', _style='display:table-cell', _class="hd16"),
                    DIV('%s '%dev, _style='display:table-cell'),
                    _style="display:table-row",
                  ),
                  DIV(
                    DIV('mnt', _style='display:table-cell;padding-left:20px'),
                    DIV(mnt, _style='display:table-cell'),
                    _style="display:table-row",
                  ),
                  DIV(
                    DIV('type', _style='display:table-cell;padding-left:20px'),
                    DIV(t, _style='display:table-cell'),
                    _style="display:table-row",
                  ),
                  DIV(
                    DIV('opts', _style='display:table-cell;padding-left:20px'),
                    DIV(opts, _style='display:table-cell'),
                    _style="display:table-row",
                  ),
                  DIV(
                    DIV('size', _style='display:table-cell;padding-left:20px'),
                    DIV(size, _style='display:table-cell'),
                    _style="display:table-row",
                  ),
                  DIV(
                    DIV('vg', _style='display:table-cell;padding-left:20px'),
                    DIV(vg, _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        return DIV(l, _class="comp_var_table")

    def form_fs(self, o):
        name = 'fs_n_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        l = []
        v = self.get(o)
        if v is None or v == "":
            f = []
        else:
            try:
                f = json.loads(v)
            except:
                return self.form_raw(o)
        if type(f) != list:
            return self.form_raw(o)
        for i, fs in enumerate(f):
            if 'mnt' in fs:
                mnt = fs['mnt']
            else:
                mnt = ""
            if 'dev' in fs:
                dev = fs['dev']
            else:
                dev = ""
            if 'type' in fs:
                t = fs['type']
            else:
                t = ""
            if 'size' in fs:
                size = fs['size']
            else:
                size = ""
            if 'opts' in fs:
                opts = fs['opts']
            else:
                opts = ""
            if 'vg' in fs:
                vg = ','.join(fs['vg'])
            else:
                vg = ""

            l += [DIV(
                    SPAN("fs", _class="comp16"),
                    _style="display:table-row",
                  ),
                  DIV(
                    DIV('dev', _style='display:table-cell;padding-left:20px'),
                    DIV(
                      INPUT(_name=name, _id="%s_%d_%s"%(name, i, 'dev'), _value=dev),
                      _style='display:table-cell',
                    ),
                    _style="display:table-row",
                  ),
                  DIV(
                    DIV('mnt', _style='display:table-cell;padding-left:20px'),
                    DIV(
                      INPUT(_name=name, _id="%s_%d_%s"%(name, i, 'mnt'), _value=mnt),
                      _style='display:table-cell',
                    ),
                    _style="display:table-row",
                  ),
                  DIV(
                    DIV('type', _style='display:table-cell;padding-left:20px'),
                    DIV(
                      INPUT(_name=name, _id="%s_%d_%s"%(name, i, 'type'), _value=t),
                      _style='display:table-cell',
                    ),
                    _style="display:table-row",
                  ),
                  DIV(
                    DIV('opts', _style='display:table-cell;padding-left:20px'),
                    DIV(
                      INPUT(_name=name, _id="%s_%d_%s"%(name, i, 'opts'), _value=opts),
                      _style='display:table-cell',
                    ),
                    _style="display:table-row",
                  ),
                  DIV(
                    DIV('size', _style='display:table-cell;padding-left:20px'),
                    DIV(
                      INPUT(_name=name, _id="%s_%d_%s"%(name, i, 'size'), _value=size),
                      _style='display:table-cell',
                    ),
                    _style="display:table-row",
                  ),
                  DIV(
                    DIV('vg', _style='display:table-cell;padding-left:20px'),
                    DIV(
                      INPUT(_name=name, _id="%s_%d_%s"%(name, i, 'vg'), _value=vg),
                      _style='display:table-cell',
                    ),
                    _style="display:table-row",
                  )]
        form = DIV(
                 SPAN(l, _id=name+'_container'),
                 BR(),
                 INPUT(
                   _value="Add",
                   _type="submit",
                   _onclick="""
d=new Date();
i=d.getTime();
$("#%(n)s_container").append("\
 <div style='display:table-row'>\
   <span class='comp16'>fs</span>\
 </div>\
 <div style='display:table-row'>\
  <div style='display:table-cell;padding-left:20px'>dev</div>\
  <div style='display:table-cell'>\
   <input name='%(n)s' id='%(n)s_"+i+"_dev'>\
  </div>\
 </div>\
 <div style='display:table-row'>\
  <div style='display:table-cell;padding-left:20px'>mnt</div>\
  <div style='display:table-cell'>\
   <input name='%(n)s' id='%(n)s_"+i+"_mnt'>\
  </div>\
 </div>\
 <div style='display:table-row'>\
  <div style='display:table-cell;padding-left:20px'>type</div>\
  <div style='display:table-cell'>\
   <input name='%(n)s' id='%(n)s_"+i+"_type'>\
  </div>\
 </div>\
 <div style='display:table-row'>\
  <div style='display:table-cell;padding-left:20px'>opts</div>\
  <div style='display:table-cell'>\
   <input name='%(n)s' id='%(n)s_"+i+"_opts'>\
  </div>\
 </div>\
 <div style='display:table-row'>\
  <div style='display:table-cell;padding-left:20px'>size</div>\
  <div style='display:table-cell'>\
   <input name='%(n)s' id='%(n)s_"+i+"_size'>\
  </div>\
 </div>\
 <div style='display:table-row'>\
  <div style='display:table-cell;padding-left:20px'>vg</div>\
  <div style='display:table-cell'>\
   <input name='%(n)s' id='%(n)s_"+i+"_vg'>\
  </div>\
 </div>\
")"""%dict(n=name),
                 ),
                 " ",
                 INPUT(
                   _type="submit",
                   _onclick=self.t.ajax_submit(additional_input_name=name,
                                               args=["var_value_set_fs", name]),
                 ),
                 _class="comp_var_table",
               )
        return form

    def html_group(self, o):
        v = self.get(o)
        l = [DIV(
               DIV('group', _style='display:table-cell;font-weight:bold', _class="comp16"),
               DIV('gid', _style='display:table-cell'),
               DIV('members', _style='display:table-cell'),
               _style="display:table-row",
             )]
        try:
            groups = json.loads(v)
        except:
            return SPAN("malformed value", PRE(v))
        if type(groups) != dict:
            return v
        for group, g in groups.items():
            if 'gid' in g:
                gid = '%d'%g['gid']
            else:
                gid = "-"
            if 'members' in g:
                members = '%s'%', '.join(g['members'])
            else:
                members = "-"
            l += [DIV(
                    DIV('%s '%group, _style='display:table-cell', _class="guys16"),
                    DIV(gid, _style='display:table-cell'),
                    DIV(members, _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        return DIV(l, _class="comp_var_table")

    def form_group(self, o):
        name = 'group_n_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        l = [DIV(
               DIV('group', _style='display:table-cell;font-weight:bold', _class="comp16"),
               DIV('gid', _style='display:table-cell'),
               DIV('members', _style='display:table-cell'),
               _style="display:table-row",
             )]
        v = self.get(o)
        if v is None or v == "":
            f = {}
        else:
            try:
                f = json.loads(v)
            except:
                return self.form_raw(o)
        if type(f) != dict:
            return self.form_raw(o)
        for i, group in enumerate(f):
            ll = [DIV(
                    SPAN("", _class="guys16"),
                    INPUT(_name=name, _id="%s_%d_%s"%(name, i, 'group'), _value=group),
                    _style='display:table-cell',
                  )]
            for key in ('gid', 'members'):
                if key not in f[group]:
                    value = ""
                else:
                    value = f[group][key]
                if key == 'members':
                    value = ','.join(value)
                ll += [DIV(
                         INPUT(_name=name, _id="%s_%d_%s"%(name, i, key), _value=value),
                         _style='display:table-cell',
                       )]
            l += [DIV(
                    ll,
                    _style="display:table-row",
                  )]
        form = DIV(
                 SPAN(l, _id=name+'_container'),
                 BR(),
                 INPUT(
                   _value="Add",
                   _type="submit",
                   _onclick="""d=new Date(); i=d.getTime(); $("#%(n)s_container").append("<div style='display:table-row'><div style='display:table-cell'><span class='guys16'></span><input name='%(n)s' id='%(n)s_"+i+"_group'></div><div style='display:table-cell'><input name='%(n)s' id='%(n)s_"+i+"_gid'></div><div style='display:table-cell'><input name='%(n)s' id='%(n)s_"+i+"_members'></div></div>")"""%dict(n=name),
                 ),
                 " ",
                 INPUT(
                   _type="submit",
                   _onclick=self.t.ajax_submit(additional_input_name=name,
                                               args=["var_value_set_group", name]),
                 ),
                 _class="comp_var_table",
               )
        return form

    def html_vuln(self, o):
        v = self.get(o)
        l = [DIV(
               DIV('package name', _style='display:table-cell;font-weight:bold', _class="comp16"),
               DIV('minimum version', _style='display:table-cell'),
               _style="display:table-row",
             )]
        try:
            vulns = json.loads(v)
        except:
            return SPAN("malformed value", PRE(v))
        for vuln in vulns:
            l += [DIV(
                    DIV('%s '%vuln['pkgname'], _style='display:table-cell', _class="pkg16"),
                    DIV(vuln['minver'], _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        return DIV(l, _class="comp_var_table")

    def form_vuln(self, o):
        name = 'vuln_n_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        l = [DIV(
               DIV('package name', _style='display:table-cell;font-weight:bold', _class="comp16"),
               DIV('minimum version', _style='display:table-cell'),
               _style="display:table-row",
             )]
        v = self.get(o)
        if v is None or v == "":
            f = {}
        else:
            try:
                f = json.loads(v)
            except:
                return self.form_raw(o)
        for i, vuln in enumerate(f):
            ll = [DIV(
                    SPAN("", _class="pkg16"),
                    INPUT(_name=name, _id="%s_%d_%s"%(name, i, 'pkgname'), _value=vuln['pkgname']),
                    _style='display:table-cell',
                  )]
            for key in ['minver']:
                if key not in vuln:
                    value = ""
                else:
                    value = vuln[key]
                if key == 'members':
                    value = ','.join(value)
                ll += [DIV(
                         INPUT(_name=name, _id="%s_%d_%s"%(name, i, key), _value=value),
                         _style='display:table-cell',
                       )]
            l += [DIV(
                    ll,
                    _style="display:table-row",
                  )]
        form = DIV(
                 SPAN(l, _id=name+'_container'),
                 BR(),
                 INPUT(
                   _value="Add",
                   _type="submit",
                   _onclick="""d=new Date(); i=d.getTime(); $("#%(n)s_container").append("<div style='display:table-row'><div style='display:table-cell'><span class='guys16'></span><input name='%(n)s' id='%(n)s_"+i+"_pkgname'></div><div style='display:table-cell'><input name='%(n)s' id='%(n)s_"+i+"_minver'></div><div style='display:table-cell'></div></div>")"""%dict(n=name),
                 ),
                 " ",
                 INPUT(
                   _type="submit",
                   _onclick=self.t.ajax_submit(additional_input_name=name,
                                               args=["var_value_set_vuln", name]),
                 ),
                 _class="comp_var_table",
               )
        return form

    def html_cron(self, o):
        v = self.get(o)
        f = v.split(':')
        if len(f) == 5:
            act, usr, sch, cmd, fil = f
        elif len(f) == 4:
            act, usr, sch, cmd = f
            fil = None
        else:
            return SPAN("malformed value", PRE(v))
        l = [DIV(
               DIV('cron', _style='display:table-cell;font-weight:bold', _class="comp16"),
               DIV(_style='display:table-cell'),
               _style="display:table-row",
             )]
        if act == "add":
            act_cl = "add16"
        elif act == "del":
            act_cl = "del16"
        else:
            act_cl = "alert16"
        l += [DIV(
                DIV('action', _style='display:table-cell', _class=act_cl),
                DIV(act, _style='display:table-cell'),
                _style="display:table-row",
              )]
        l += [DIV(
                DIV('user', _style='display:table-cell', _class="guy16"),
                DIV(usr, _style='display:table-cell'),
                _style="display:table-row",
              )]
        l += [DIV(
                DIV('sched', _style='display:table-cell', _class="time16"),
                DIV(sch, _style='display:table-cell'),
                _style="display:table-row",
              )]
        l += [DIV(
                DIV('command', _style='display:table-cell', _class="action16"),
                DIV(cmd, _style='display:table-cell'),
                _style="display:table-row",
              )]
        if fil is not None:
            l += [DIV(
                    DIV('file', _style='display:table-cell', _class="hd16"),
                    DIV(fil, _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        return DIV(l, _class="comp_var_table")

    def form_cron(self, o):
        name = 'cron_n_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        l = []
        v = self.get(o)
        if v is None or v == "":
            f = {}
        else:
            vl = v.split(':')
            f = {}
            if len(vl) == 5:
                f['action'], f['user'], f['sched'], f['command'], f['file'] = vl
            elif len(vl) == 4:
                f['action'], f['user'], f['sched'], f['command'] = vl
                f['file'] = ""
            else:
                return self.form_raw(o)
        for key, img in (('action', 'action16'),
                         ('user', 'guy16'),
                         ('sched', 'time16'),
                         ('command', 'action16'),
                         ('file', 'hd16')):
            if key not in f:
                value = ""
            else:
                value = f[key]
            l += [DIV(
                   DIV(key, _style='display:table-cell;font-weight:bold', _class=img),
                   DIV(INPUT(_name=name, _id="%s_%s"%(name, key), _value=value), _style='display:table-cell'),
                   _style="display:table-row",
                 )]
        form = DIV(
                 SPAN(l, _id=name+'_container'),
                 BR(),
                 INPUT(
                   _type="submit",
                   _onclick=self.t.ajax_submit(additional_input_name=name,
                                               args=["var_value_set_cron", name]),
                 ),
                 _class="comp_var_table",
               )
        return form

    def html_authkey(self, o):
        def truncate_key(key):
            if len(key) < 50:
                return key
            else:
                return key[0:17] + "..." + key[-30:]

        v = self.get(o)
        try:
            f = json.loads(v)
        except:
            return SPAN("malformed value", PRE(v))
        l = [DIV(
               DIV('authentication key', _style='display:table-cell;font-weight:bold', _class="comp16"),
               _style="display:table-row",
             )]
        l += [DIV(
               DIV('user', _style='display:table-cell', _class="guy16"),
               DIV(f['user'], _style='display:table-cell'),
               _style="display:table-row",
             )]
        l += [DIV(
               DIV('key', _style='display:table-cell', _class="key16"),
               DIV(truncate_key(f['key']), _style='display:table-cell'),
               _style="display:table-row",
             )]
        if 'action' in f:
            l += [DIV(
                    DIV('action', _style='display:table-cell', _class="action16"),
                    DIV(f['action'], _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        if 'authfile' in f:
            l += [DIV(
                    DIV('file', _style='display:table-cell', _class="edit16"),
                    DIV(f['authfile'], _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        return DIV(l, _class="comp_var_table")

    def form_authkey(self, o):
        name = 'authkey_n_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        l = []
        v = self.get(o)
        if v is None or v == "":
            f = {}
        else:
            try:
                f = json.loads(v)
            except:
                return self.form_raw(o)
        for key, img in (('user', 'guy16'),
                         ('key', 'key16'),
                         ('action', 'action16'),
                         ('authfile', 'edit16')):
            if key not in f:
                value = ""
            else:
                value = f[key]
            if key == 'key':
                _WIDGET = TEXTAREA(_name=name, _id="%s_%s"%(name, key), value=value)
            elif key == 'action':
                _WIDGET = SELECT(
                            (
                               OPTION("add", _value="add"),
                               OPTION("del", _value="del")
                            ),
                            _name=name,
                            _id="%s_%s"%(name, key),
                          )
            elif key == 'authfile':
                if 'authfile' in f:
                    authfile = f['authfile']
                else:
                    authfile = "authorized_keys"
                _WIDGET = SELECT(
                            (
                               OPTION("authorized_keys", _value="authorized_keys"),
                               OPTION("authorized_keys2", _value="authorized_keys2")
                            ),
                            _name=name,
                            _id="%s_%s"%(name, key),
                            value=authfile,
                          )
            else:
                _WIDGET = INPUT(_name=name, _id="%s_%s"%(name, key), value=value)
            l += [DIV(
                   DIV(key, _style='display:table-cell;font-weight:bold', _class=img),
                   DIV(_WIDGET, _style='display:table-cell'),
                   _style="display:table-row",
                 )]
        form = DIV(
                 SPAN(l, _id=name+'_container'),
                 BR(),
                 INPUT(
                   _type="submit",
                   _onclick=self.t.ajax_submit(additional_input_name=name,
                                               args=["var_value_set_dict", name]),
                 ),
                 _class="comp_var_table",
               )
        return form

    def html_file(self, o):
        v = self.get(o)
        try:
            f = json.loads(v)
        except:
            return SPAN("malformed value", PRE(v))
        l = [DIV(
               DIV('file', _style='display:table-cell;font-weight:bold', _class="comp16"),
               DIV(f['path'], _style='display:table-cell'),
               _style="display:table-row",
             )]
        if 'fmt' in f:
            l += [DIV(
                    DIV('fmt', _style='display:table-cell', _class="hd16"),
                    DIV(f['fmt'], _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        if 'ref' in f:
            l += [DIV(
                    DIV('ref', _style='display:table-cell', _class="loc"),
                    DIV(f['ref'], _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        if 'mode' in f:
            l += [DIV(
                    DIV('mode', _style='display:table-cell', _class="action16"),
                    DIV(str(f['mode']), _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        if 'uid' in f:
            l += [DIV(
                    DIV('uid', _style='display:table-cell', _class="guy16"),
                    DIV(str(f['uid']), _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        if 'gid' in f:
            l += [DIV(
                    DIV('gid', _style='display:table-cell', _class="guys16"),
                    DIV(str(f['gid']), _style='display:table-cell'),
                    _style="display:table-row",
                  )]
        return DIV(l, _class="comp_var_table")

    def form_file(self, o):
        name = 'file_n_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        l = []
        v = self.get(o)
        if v is None or v == "":
            f = {}
        else:
            try:
                f = json.loads(v)
            except:
                return self.form_raw(o)
        for key, img in (('path', 'hd16'),
                         ('fmt', 'hd16'),
                         ('ref', 'loc'),
                         ('mode', 'action16'),
                         ('uid', 'guy16'),
                         ('gid', 'guys16')):
            if key not in f:
                value = ""
            else:
                value = f[key]
            if key == 'fmt':
                _WIDGET = TEXTAREA
            else:
                _WIDGET = INPUT
            l += [DIV(
                   DIV(key, _style='display:table-cell;font-weight:bold', _class=img),
                   DIV(_WIDGET(_name=name, _id="%s_%s"%(name, key), value=value), _style='display:table-cell'),
                   _style="display:table-row",
                 )]
        form = DIV(
                 SPAN(l, _id=name+'_container'),
                 BR(),
                 INPUT(
                   _type="submit",
                   _onclick=self.t.ajax_submit(additional_input_name=name,
                                               args=["var_value_set_dict", name]),
                 ),
                 _class="comp_var_table",
               )
        return form

    def html_package(self, o):
        v = self.get(o)
        l = [DIV(
               DIV('package', _style='display:table-cell;font-weight:bold', _class="comp16"),
               _style="display:table-row",
             )]
        try:
            packages = json.loads(v)
        except:
            return SPAN("malformed value", PRE(v))
        for pkg in packages:
            l += [DIV(
                    DIV(pkg, _style='display:table-cell', _class="pkg16"),
                    _style="display:table-row",
                  )]
        return DIV(l, _class="comp_var_table")

    def form_package(self, o):
        name = 'pack_n_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        l = []
        v = self.get(o)
        if v is None or v == "":
            packages = []
        else:
            try:
                packages = json.loads(v)
            except:
                return self.form_raw(o)
        for i, package in enumerate(packages):
            l.append(DIV(
                       SPAN("", _class="pkg16"),
                       INPUT(_name=name, _id="%s_%d"%(name, i), _value=package),
                       _style="display:table-row",
                     ))
        form = DIV(
                 SPAN(l, _id=name+'_container'),
                 BR(),
                 INPUT(
                   _value="Add",
                   _type="submit",
                   _onclick="""d=new
Date();$("#%(n)s_container").append("<div style='display:table-row'><span class='pkg16'></span><input name='%(n)s' id='%(n)s_"+d.getTime()+"'></div>")"""%dict(n=name),
                 ),
                 " ",
                 INPUT(
                   _type="submit",
                   _onclick=self.t.ajax_submit(additional_input_name=name,
                                               args=["var_value_set_list", name]),
                 ),
                 _class="comp_var_table",
               )
        return form

    def html_cve(self, o):
        v = self.get(o)
        l = [DIV(
               DIV('cve', _style='display:table-cell;font-weight:bold', _class="comp16"),
               _style="display:table-row",
             )]
        try:
            cve = json.loads(v)
            if 'product' not in cve:
                raise
        except:
            return SPAN("malformed value", PRE(v))
        l += [DIV(
                DIV(T('Product'), _style='display:table-cell', _class="pkg16"),
                DIV(cve['product'], _style='display:table-cell'),
                _style="display:table-row",
              )]
        l += [DIV(
                DIV(T('Minimum version'), _style='display:table-cell', _class="pkg16"),
                DIV(cve['minver'], _style='display:table-cell'),
                _style="display:table-row",
              )]
        l += [DIV(
                DIV(T('Maximum version'), _style='display:table-cell', _class="pkg16"),
                DIV(cve['maxver'], _style='display:table-cell'),
                _style="display:table-row",
              )]
        return DIV(l, _class="comp_var_table")

    def form_cve(self, o):
        name = 'pack_n_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        l = []
        v = self.get(o)
        if v is None or v == "":
            cve = {'product':'', 'minver':'', 'maxver':''}
        else:
            try:
                cve = json.loads(v)
                if 'product' not in cve:
                    raise
            except:
                return self.form_raw(o)
        l.append(DIV(
                   DIV(T("Product"), _class="pkg16"),
                   INPUT(_name=name, _id="%s_product"%name, _value=cve['product']),
                   _style="display:table-row",
                 ))
        l.append(DIV(
                   DIV(T("Minimum version"), _class="pkg16"),
                   INPUT(_name=name, _id="%s_minver"%name, _value=cve['minver']),
                   _style="display:table-row",
                 ))
        l.append(DIV(
                   DIV(T("Maximum version"), _class="pkg16"),
                   INPUT(_name=name, _id="%s_maxver"%name, _value=cve['maxver']),
                   _style="display:table-row",
                 ))
        form = DIV(
                 SPAN(l, _id=name+'_container'),
                 BR(),
                 INPUT(
                   _type="submit",
                   _onclick=self.t.ajax_submit(additional_input_name=name,
                                               args=["var_value_set_dict", name]),
                 ),
                 _class="comp_var_table",
               )
        return form

    def _html(self, o):
        c = self.t.colprops['var_class'].get(o)
        if not hasattr(self, 'html_'+str(c)):
            return self.html_raw(o)
        return getattr(self, 'html_'+str(c))(o)

    def _form(self, o):
        c = self.t.colprops['var_class'].get(o)
        if not hasattr(self, 'form_'+str(c)):
            return self.form_raw(o)
        return getattr(self, 'form_'+str(c))(o)

    def html(self, o):
        hid = 'vd_h_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        fid = 'vd_f_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        cid = 'vd_c_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        eid = 'vd_e_%s_%s'%(self.t.colprops['id'].get(o), self.t.colprops['ruleset_id'].get(o))
        return DIV(
                 A(
                   IMG(_src=URL(r=request, c='static', f='edit.png')),
                   _id=eid,
                   _onclick="""hide_eid('%(hid)s');hide_eid('%(eid)s');show_eid('%(fid)s');show_eid('%(cid)s');"""%dict(hid=hid, fid=fid, eid=eid, cid=cid),
                   _label=T("edit"),
                   _style='position: absolute; top: 2px; right: 2px; z-index: 400',
                 ),
                 A(
                   IMG(_src=URL(r=request, c='static', f='cancel.png')),
                   _id=cid,
                   _onclick="""hide_eid('%(fid)s');hide_eid('%(cid)s');show_eid('%(hid)s');show_eid('%(eid)s');"""%dict(hid=hid, fid=fid, eid=eid, cid=cid),
                   _label=T("cancel"),
                   _style='display:none;position: absolute; top: 2px; right: 2px; z-index: 400',
                 ),
                 DIV(
                   self._html(o),
                   _id=hid,
                   _style="position: relative;",
                 ),
                 DIV(
                   self._form(o),
                   _id=fid,
                   _style="display:none",
                 ),
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
                                                        'ruleset_attach',
                                                        'ruleset_detach',
                                                        'ruleset_node_attach'])
        self.ajax_col_values = 'ajax_comp_rulesets_col_values'

    def ruleset_node_attach(self):
        return A(
                 T("Rulesets/Nodes attachment"),
                 _href=URL(r=request, f="comp_rulesets_nodes_attachment"),
                 _class="attach16",
               )

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
        o = db.nodes.team_responsible
        q = db.nodes.team_responsible == db.auth_group.role
        if 'Manager' not in user_groups():
            q &= db.nodes.team_responsible.belongs(user_groups())
        options = [OPTION(g.auth_group.role,_value=g.auth_group.id) for g in db(q).select(orderby=o, groupby=o)]

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
    if rows[0].ruleset_type == 'contextual':
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
    ids = map(lambda x: x.split('_')[2], ids)
    ids = [id for id in ids if id != 'None']
    ids = map(lambda x: int(x), ids)
    if len(ids) == 0:
        raise ToolError("delete variables failed: no variable selected")
    q = db.v_comp_rulesets.id.belongs(ids)
    n = db(q).count()
    q &= db.v_comp_rulesets.encap_rset_id == None
    rows = db(q).select()
    diff = n - len(rows)
    if diff > 0:
        raise ToolError("Deleting variables in a encapsulated ruleset is not allowed. Please detach the encapsulated ruleset, or delete the variables from the ruleset owning the variables directly.")
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

    for node in node_names:
        update_dash_rsetdiff_node(node)

    q = db.comp_rulesets.id.belongs(ruleset_ids)
    rows = db(q).select(db.comp_rulesets.ruleset_name)
    rulesets = ', '.join([r.ruleset_name for r in rows])
    _log('compliance.ruleset.node.detach',
         'detached rulesets %(rulesets)s from nodes %(nodes)s',
         dict(rulesets=rulesets, nodes=nodes))

@auth.requires_membership('CompManager')
def comp_attach_rulesets(node_ids=[], ruleset_ids=[]):
    if len(node_ids) == 0:
        raise ToolError("attach ruleset failed: no node selected")
    if len(ruleset_ids) == 0:
        raise ToolError("attach ruleset failed: no ruleset selected")

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

    for node in node_names:
        update_dash_rsetdiff_node(node)

    q = db.comp_rulesets.id.belongs(ruleset_ids)
    rows = db(q).select(db.comp_rulesets.ruleset_name)
    rulesets = ', '.join([r.ruleset_name for r in rows])
    _log('compliance.ruleset.node.attach',
         'attached rulesets %(rulesets)s to nodes %(nodes)s',
         dict(rulesets=rulesets, nodes=nodes))

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
    v.sub_span = ['ruleset_type', 'fset_name', 'teams_responsible']
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
          comp_menu('Rules'),
          DIV(
            ajax_comp_rulesets(),
            _id='cr0',
          ),
        )
    return dict(table=t)

@auth.requires_login()
def comp_rulesets_nodes_attachment():
    t = DIV(
          comp_menu('Rules'),
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

    def team_responsible_select_tool(self, label, action, divid, sid,
_class=''):
        o = db.nodes.team_responsible
        q = db.nodes.team_responsible == db.auth_group.role
        if 'Manager' not in user_groups():
            q &= db.nodes.team_responsible.belongs(user_groups())
        options = [OPTION(g.auth_group.role,_value=g.auth_group.id) for g in db(q).select(orderby=o, groupby=o)]

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
def comp_attach_modulesets(node_ids=[], modset_ids=[]):
    if len(node_ids) == 0:
        raise ToolError("attach modulesets failed: no node selected")
    if len(modset_ids) == 0:
        raise ToolError("attach modulesets failed: no moduleset selected")

    q = db.v_nodes.id.belongs(node_ids)
    rows = db(q).select(db.v_nodes.nodename)
    node_names = [r.nodename for r in rows]
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
          comp_menu('Modules'),
          DIV(
            ajax_comp_moduleset(),
            _id='ajax_comp_moduleset',
          ),
        )
    return dict(table=t)

@auth.requires_login()
def comp_modulesets_nodes():
    t = DIV(
          comp_menu('Modules'),
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
            self += HtmlTableMenu('Action', 'action16', ['tool_action_node', 'tool_action_module', 'tool_action_moduleset'], id='menu_comp_action')

    def tool_action_node(self):
        return self._tool_action("node")

    def tool_action_module(self):
        return self._tool_action("module")

    def tool_action_moduleset(self):
        return self._tool_action("moduleset")

    def _tool_action(self, mode):
        if mode in ["module", "moduleset"]:
            cmd = [
              'check',
              'fixable',
              'fix',
            ]
            cl = "comp16"
        else:
            cmd = [
              'checks',
              'pushasset',
              'pushservices',
              'pushstats',
              'pushpkg',
              'pushpatch',
              'reboot',
              'shutdown',
              'syncservices',
              'updatecomp',
              'updatepkg',
              'updateservices',
            ]
            cl = "node16"

        sid = 'action_s_'+mode
        s = []
        for c in cmd:
            if mode in ["module", "moduleset"]:
                confirm=T("""Are you sure you want to execute a %(a)s action on all selected nodes. Please confirm action""",dict(a=c))
            else:
                confirm=T("""Are you sure you want to execute a compliance %(a)s action on all selected nodes. Please confirm action""",dict(a=c))
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
                             s=self.ajax_submit(additional_inputs=[sid], args=['do_action', c, mode]),
                             text=confirm,
                           ),
                         ),
                       ),
                     ))

        if mode == "module":
            q = db.comp_moduleset_modules.id > 0
            o = db.comp_moduleset_modules.modset_mod_name
            rows = db(q).select(orderby=o, groupby=o)
            options = [OPTION(g.modset_mod_name,_value=g.modset_mod_name) for g in rows]
            id_col = 'comp_modules.id'
        elif mode == "moduleset":
            q = db.comp_moduleset.id > 0
            o = db.comp_moduleset.modset_name
            rows = db(q).select(orderby=o)
            options = [OPTION(g.modset_name,_value=g.modset_name) for g in rows]
            id_col = 'comp_moduleset.id'

        if mode in ["module", "moduleset"]:
            fancy_mode = mode[0].upper()+mode[1:].lower()
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
            selector = TABLE(
                          TR(
                            TH(
                              T(fancy_mode),
                            ),
                            TD(
                              SELECT(
                                *options,
                                **dict(_id=sid,
                                       _requires=IS_IN_DB(db, id_col))
                              ),
                            ),
                          ),
                        )
        else:
            actions = TABLE(*s)
            selector = SPAN()

        d = DIV(
              A(
                T("Run "+mode),
                _class=cl,
                _onclick="""
                  click_toggle_vis(event,'%(div)s', 'block');
                """%dict(div='tool_action_'+mode),
              ),
              DIV(
                actions,
                selector,
                _style='display:none',
                _class='white_float',
                _name='tool_action_'+mode,
                _id='tool_action_'+mode,
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

@auth.requires_membership('CompExec')
def do_action(ids, action=None, mode=None):
    if mode not in ("module", "moduleset", "node"):
        raise ToolError("unsupported mode")
    if action is None or len(action) == 0:
        raise ToolError("no action specified")
    if len(ids) == 0:
        raise ToolError("no target to execute %s on"%action)

    if mode in ("module", "moduleset"):
        if not hasattr(request.vars, 'action_s_'+mode):
            raise ToolError("no module or moduleset selected")
        mod = request.vars['action_s_'+mode]

        def fmt_action(node, action, mode):
            cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                          '-o', 'ForwardX11=no',
                          '-o', 'PasswordAuthentication=no',
                          '-tt',
                   'opensvc@'+node,
                   '--',
                   'sudo', '/opt/opensvc/bin/nodemgr', 'compliance', action,
                   '--'+mode, mod]
            return ' '.join(cmd)
    elif mode == "node":
        def fmt_action(node, action, mode):
            cmd = ['ssh', '-o', 'StrictHostKeyChecking=no',
                          '-o', 'ForwardX11=no',
                          '-o', 'PasswordAuthentication=no',
                          '-tt',
                   'opensvc@'+node,
                   '--',
                   'sudo', '/opt/opensvc/bin/nodemgr', action,
                   '--force']
            return ' '.join(cmd)

    q = db.comp_status.id.belongs(ids)
    q &= db.comp_status.run_nodename == db.nodes.nodename
    q &= db.nodes.team_responsible.belongs(user_groups())
    rows = db(q).select(db.nodes.nodename)

    vals = []
    vars = ['command']
    for row in rows:
        vals.append([fmt_action(row.nodename, action, mode)])

    purge_action_queue()
    generic_insert('action_queue', vars, vals)
    from subprocess import Popen
    actiond = 'applications'+str(URL(r=request,c='actiond',f='actiond.py'))
    process = Popen(actiond)
    process.communicate()
    if mode in ("module", "moduleset"):
        _log('node.action', 'run %(a)s of %(mode)s %(m)s on nodes %(s)s', dict(
              a=action,
              mode=mode,
              s=','.join(map(lambda x: x.nodename, rows)),
              m=mod))
    elif mode == "node":
        _log('node.action', 'run %(a)s on nodes %(s)s', dict(
              a=action,
              s=','.join(map(lambda x: x.nodename, rows)),
              ))

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
        if key == 'level':
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
            elif action == 'do_action' and len(request.args) == 3:
                saction = request.args[1]
                mode = request.args[2]
                do_action(t.get_checked(), saction, mode)
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
          comp_menu('Status'),
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

def comp_ruleset_svc_attached(svcname, rset_id):
    q = db.comp_rulesets_services.svcname == svcname
    q &= db.comp_rulesets_services.ruleset_id == rset_id
    if len(db(q).select(db.comp_rulesets_services.id)) == 0:
        return False
    return True

def comp_moduleset_svc_attached(svcname, modset_id):
    q = db.comp_modulesets_services.modset_svcname == svcname
    q &= db.comp_modulesets_services.modset_id == modset_id
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

@auth_uuid
@service.xmlrpc
def comp_attach_svc_ruleset(svcname, ruleset, auth):
    if len(ruleset) == 0:
        return dict(status=False, msg="no ruleset specified"%ruleset)
    rset_id = comp_ruleset_id(ruleset)
    if rset_id is None:
        return dict(status=False, msg="ruleset %s does not exist"%ruleset)
    if comp_ruleset_svc_attached(svcname, rset_id):
        return dict(status=True, msg="ruleset %s is already attached to this service"%ruleset)
    if not comp_ruleset_svc_attachable(svcname, rset_id):
        return dict(status=False, msg="ruleset %s is not attachable"%ruleset)

    n = db.comp_rulesets_services.insert(svcname=svcname,
                                           ruleset_id=rset_id)
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
    if modset_id is None:
        return dict(status=False, msg="moduleset %s does not exist"%moduleset)
    if comp_moduleset_svc_attached(svcname, modset_id):
        return dict(status=True, msg="moduleset %s is already attached to this service"%moduleset)
    if not comp_moduleset_svc_attachable(svcname, modset_id):
        return dict(status=False, msg="moduleset %s is not attachable"%moduleset)

    n = db.comp_modulesets_services.insert(modset_svcname=svcname,
                                           modset_id=modset_id)
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
    if rset_id is None:
        return dict(status=True, msg="ruleset %s does not exist"%ruleset)
    elif ruleset == 'all' and len(rset_id) == 0:
        return dict(status=True, msg="this service has no ruleset attached")
    if ruleset != 'all' and not comp_ruleset_svc_attached(svcname, rset_id):
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
    if modset_id is None:
        return dict(status=True, msg="moduleset %s does not exist"%moduleset)
    elif moduleset == 'all' and len(modset_id) == 0:
        return dict(status=True, msg="this service has no moduleset attached")
    if moduleset != 'all' and not comp_moduleset_svc_attached(svcname, modset_id):
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
    return _comp_get_svc_moduleset(svcname)

@auth_uuid
@service.xmlrpc
def comp_get_moduleset(nodename, auth):
    return _comp_get_moduleset(nodename)

def _comp_get_svc_moduleset(svcname):
    q = db.comp_modulesets_services.modset_svcname == svcname
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

def comp_get_svcmon_ruleset(svcname, nodename, virt=False):
    if virt:
        q = db.svcmon.mon_vmname == svcname
        q &= db.svcmon.mon_availstatus == "up"
        row = db(q).select(db.svcmon.mon_svcname, db.svcmon.mon_nodname).first()
        if row is None:
            return {}
        svcname = row.mon_svcname
        nodename = row.mon_nodname
    q = db.svcmon.mon_svcname == svcname
    q &= db.svcmon.mon_nodname == nodename
    rows = db(q).select()
    if len(rows) != 1:
        return {}
    ruleset = {'name': 'osvc_svcmon',
               'filter': str(q),
               'vars': []}
    for f in db.svcmon.fields:
        val = rows[0][f]
        ruleset['vars'].append(('svcmon.'+f, val))
    return {'osvc_svcmon':ruleset}

def comp_get_service_ruleset(svcname, virt=False):
    if virt:
        q = db.svcmon.mon_vmname == svcname
        row = db(q).select(db.svcmon.mon_svcname).first()
        if row is None:
            return {}
        svcname = row.mon_svcname
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

def comp_ruleset_vars(ruleset_id, qr=None):
    if qr is None:
        f = 'explicit attachment'
    else:
        f = comp_format_filter(qr)
    q1 = db.comp_rulesets_rulesets.parent_rset_id==ruleset_id
    q = db.comp_rulesets.id == ruleset_id
    head_rset = db(q).select(db.comp_rulesets.ruleset_name).first()
    if head_rset is None:
        return dict()
    children = db(q1).select(db.comp_rulesets_rulesets.child_rset_id)
    children = map(lambda x: x.child_rset_id, children)
    if len(children) > 0:
        q |= db.comp_rulesets.id.belongs(children)
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
    ruleset = _comp_get_svc_ruleset(svcname)
    ruleset.update(_comp_get_svc_per_node_ruleset(svcname, auth[1]))
    ruleset.update(comp_get_svcmon_ruleset(svcname, auth[1]))
    ruleset.update(comp_get_node_ruleset(auth[1]))
    ruleset = _comp_remove_dup_vars(ruleset)
    insert_run_rset(ruleset)
    return ruleset

def _comp_get_svc_per_node_ruleset(svcname, nodename):
    ruleset = {}

    # add contextual rulesets variables
    v = db.v_gen_filtersets
    rset = db.comp_rulesets
    rset_fset = db.comp_rulesets_filtersets
    o = rset.ruleset_name|v.f_order
    q = rset.id>0
    q &= rset.id == rset_fset.ruleset_id
    q &= rset_fset.fset_id == v.fset_id
    q &= rset.id == db.comp_ruleset_team_responsible.ruleset_id
    q &= db.comp_ruleset_team_responsible.group_id.belongs(svc_team_responsible_id(svcname))
    rows = db(q).select(orderby=o)

    q = db.services.svc_name == svcname
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
                    ruleset.update(comp_ruleset_vars(row.comp_rulesets.id, qr=qr))
                need = False
            qr = db.services.id > 0

    return ruleset

def _comp_get_svc_ruleset(svcname):
    # initialize ruleset with asset variables
    ruleset = comp_get_service_ruleset(svcname)

    # add contextual rulesets variables
    v = db.v_gen_filtersets
    rset = db.comp_rulesets
    rset_fset = db.comp_rulesets_filtersets
    o = rset.ruleset_name|v.f_order
    q = rset.id>0
    q &= rset.id == rset_fset.ruleset_id
    q &= rset_fset.fset_id == v.fset_id
    q &= rset.id == db.comp_ruleset_team_responsible.ruleset_id
    q &= db.comp_ruleset_team_responsible.group_id.belongs(svc_team_responsible_id(svcname))
    rows = db(q).select(orderby=o)

    q = db.services.svc_name == svcname
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
                    ruleset.update(comp_ruleset_vars(row.comp_rulesets.id, qr=qr))
                need = False
            qr = db.services.id > 0

    # add explicit rulesets variables
    q = db.comp_rulesets_services.svcname == svcname
    rows = db(q).select(db.comp_rulesets_services.ruleset_id,
                        orderby=db.comp_rulesets_services.ruleset_id)
    for row in rows:
        ruleset.update(comp_ruleset_vars(row.ruleset_id))

    return ruleset

def insert_run_rset(ruleset):
    import cPickle
    o = md5()
    s = cPickle.dumps(ruleset)
    o.update(s)
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

    # if the node is driven by a opensvc service, add the service ruleset
    ruleset.update(comp_get_service_ruleset(nodename, virt=True))
    ruleset.update(comp_get_svcmon_ruleset(nodename, None, virt=True))

    # add contextual rulesets variables
    v = db.v_gen_filtersets
    rset = db.comp_rulesets
    rset_fset = db.comp_rulesets_filtersets
    o = rset.ruleset_name|v.f_order
    q = rset.id>0
    q &= rset.id == rset_fset.ruleset_id
    q &= rset_fset.fset_id == v.fset_id
    q &= rset.id == db.comp_ruleset_team_responsible.ruleset_id
    q &= db.comp_ruleset_team_responsible.group_id == node_team_responsible_id(nodename)
    rows = db(q).select(orderby=o)

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
                ruleset.update(comp_ruleset_vars(row.comp_rulesets.id, qr=qr))
            qr = db.nodes.id > 0
    # add explicit rulesets variables
    q = db.comp_rulesets_nodes.nodename == nodename
    rows = db(q).select(db.comp_rulesets_nodes.ruleset_id,
                        orderby=db.comp_rulesets_nodes.ruleset_id)
    for row in rows:
        ruleset.update(comp_ruleset_vars(row.ruleset_id))

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
    rows = db(q).select(db.svcmon.mon_nodname)
    nodes = [r.mon_nodname for r in rows]

    for node in nodes:
        did = 'nrs_'+node.replace('.','').replace('-','')
        n_rsets = comp_get_svcmon_ruleset(svcname, node)
        n_rsets.update(comp_get_node_ruleset(node))
        n_rsets.update(_comp_get_svc_per_node_ruleset(svcname, node))
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
              _title=str(row[4]) + '\n' + row[3]
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

