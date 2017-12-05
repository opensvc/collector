from hashlib import md5
import datetime
import copy
now=datetime.datetime.today()
sevendays = str(now-datetime.timedelta(days=7,
                                       hours=now.hour,
                                       minutes=now.minute,
                                       seconds=now.second,
                                       microseconds=now.microsecond))

img_h = {0: 'images/check16.png',
         1: 'images/nok.png',
         2: 'images/na.png',
       -15: 'images/kill16.png'}

import re
# ex: \x1b[37;44m\x1b[1mContact List\x1b[0m\n
regex = re.compile("\x1b\[([0-9]{1,3}(;[0-9]{1,3})*)?[m|K|G]", re.UNICODE)

def strip_unprintable(s):
    return regex.sub('', s)

#
# custom column formatting
#
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

#
# Rules sub-view
#
class table_comp_rulesets_services(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['svc_id', 'svcname', 'encap', 'ruleset_id', 'ruleset_name'] + services_cols + ['svc_status_updated']
        self.colprops = services_colprops
        self.colprops['svc_id'] = HtmlTableColumn(
                     field='svc_id',
                    )
        self.colprops['ruleset_id'] = HtmlTableColumn(
                     field='ruleset_id',
                    )
        self.colprops['ruleset_name'] = HtmlTableColumn(
                     field='ruleset_name',
                    )
        self.colprops['svc_status_updated'] = HtmlTableColumn(
                     field='svc_status_updated',
                    )
        self.colprops['encap'] = HtmlTableColumn(
                     field='encap',
                    )
        for c in self.cols:
            self.colprops[c].table = 'v_comp_services'
        self.ajax_col_values = 'ajax_comp_rulesets_services_col_values'


class table_comp_rulesets_nodes(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['node_id', 'nodename', 'ruleset_id', 'ruleset_name'] + nodes_cols
        self.colprops = nodes_colprops
        self.colprops['ruleset_id'] = HtmlTableColumn(
                     field='ruleset_id',
                    )
        self.colprops['node_id'] = HtmlTableColumn(
                     field='node_id',
                    )
        self.colprops['ruleset_name'] = HtmlTableColumn(
                     field='ruleset_name',
                    )
        for c in self.cols:
            self.colprops[c].table = 'v_comp_nodes'
        self.ajax_col_values = 'ajax_comp_rulesets_nodes_col_values'


@auth.requires_login()
def ajax_comp_rulesets_services_col_values():
    table_id = request.vars.table_id
    t = table_comp_rulesets_services(table_id, 'ajax_comp_rulesets_services')
    col = request.args[0]
    o = db.v_comp_services[col]
    g = db.v_comp_services.svcname | db.v_comp_services.encap | db.v_comp_services.ruleset_name
    q = q_filter(app_field=db.v_comp_services.svc_app)
    for f in t.cols:
        q = _where(q, 'v_comp_services', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, groupby=g, cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_comp_rulesets_nodes_col_values():
    table_id = request.vars.table_id
    t = table_comp_rulesets_nodes(table_id, 'table_comp_rulesets_nodes')
    col = request.args[0]
    o = db.v_comp_nodes[col]
    g = db.v_comp_nodes.nodename | db.v_comp_nodes.ruleset_name
    q = q_filter(app_field=db.v_comp_nodes.app)
    for f in t.cols:
        q = _where(q, 'v_comp_nodes', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, groupby=g, cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_comp_rulesets_services():
    table_id = request.vars.table_id
    t = table_comp_rulesets_services(table_id, 'ajax_comp_rulesets_services')

    o = t.get_orderby(default=db.v_comp_services.svcname|db.v_comp_services.encap|db.v_comp_services.ruleset_name)
    g = db.v_comp_services.svcname | db.v_comp_services.encap | db.v_comp_services.ruleset_name
    q = q_filter(app_field=db.v_comp_services.svc_app)
    for f in t.cols:
        q = _where(q, 'v_comp_services', t.filter_parse(f), f)
    q = apply_gen_filters(q, 'v_comp_services')

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.v_comp_services.id.count(), cacheable=True).first()._extra[db.v_comp_services.id.count()]
        t.setup_pager(n)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, limitby=(t.pager_start,t.pager_end),
                                     groupby=g, orderby=o, cacheable=True)
        return t.table_lines_data(n, html=False)
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        return t.csv()

@auth.requires_login()
def ajax_comp_rulesets_nodes():
    table_id = request.vars.table_id
    t = table_comp_rulesets_nodes(table_id, 'table_comp_rulesets_nodes')

    o = t.get_orderby(default=db.v_comp_nodes.nodename)
    g = db.v_comp_nodes.nodename | db.v_comp_nodes.ruleset_name
    q = q_filter(app_field=db.v_comp_nodes.app)
    if 'Manager' not in user_groups():
        q &= db.v_comp_nodes.team_responsible.belongs(user_groups())
    for f in t.cols:
        q = _where(q, 'v_comp_nodes', t.filter_parse(f), f)
    q = apply_gen_filters(q, 'v_comp_nodes')

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.v_comp_nodes.id.count(), cacheable=True).first()._extra[db.v_comp_nodes.id.count()]
        t.setup_pager(n)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, limitby=(t.pager_start,t.pager_end),
                                     groupby=g, orderby=o, cacheable=True)
        return t.table_lines_data(n, html=False)
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        return t.csv()

class table_comp_rulesets(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'ruleset_id',
                     'ruleset_name',
                     'ruleset_type',
                     'ruleset_public',
                     'teams_responsible',
                     'teams_publication',
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
                     field='var_updated',
                     table='v_comp_rulesets',
                    ),
            'teams_responsible': HtmlTableColumn(
                     field='teams_responsible',
                     table='v_comp_rulesets',
                    ),
            'teams_publication': HtmlTableColumn(
                     field='teams_publication',
                     table='v_comp_rulesets',
                    ),
            'var_author': HtmlTableColumn(
                     field='var_author',
                     table='v_comp_rulesets',
                    ),
            'id': HtmlTableColumn(
                     field='id',
                     table='v_comp_rulesets',
                    ),
            'fset_id': HtmlTableColumn(
                     field='fset_id',
                     table='v_comp_rulesets',
                    ),
            'ruleset_id': HtmlTableColumn(
                     field='ruleset_id',
                     table='v_comp_rulesets',
                    ),
            'chain_len': HtmlTableColumn(
                     field='chain_len',
                     table='v_comp_rulesets',
                    ),
            'chain': HtmlTableColumn(
                     field='chain',
                     table='v_comp_rulesets',
                    ),
            'encap_rset': HtmlTableColumn(
                     field='encap_rset',
                     table='v_comp_rulesets',
                    ),
            'encap_rset_id': HtmlTableColumn(
                     field='encap_rset_id',
                     table='v_comp_rulesets',
                    ),
            'ruleset_name': HtmlTableColumn(
                     field='ruleset_name',
                     table='v_comp_rulesets',
                    ),
            'ruleset_type': HtmlTableColumn(
                     field='ruleset_type',
                     table='v_comp_rulesets',
                    ),
            'ruleset_public': HtmlTableColumn(
                     field='ruleset_public',
                     table='v_comp_rulesets',
                    ),
            'fset_name': HtmlTableColumn(
                     field='fset_name',
                     table='v_comp_rulesets',
                    ),
            'var_value': HtmlTableColumn(
                     field='var_value',
                     table='v_comp_rulesets',
                    ),
            'var_name': HtmlTableColumn(
                     field='var_name',
                     table='v_comp_rulesets',
                    ),
            'var_class': HtmlTableColumn(
                     field='var_class',
                     table='v_comp_rulesets',
                    ),
        }

@auth.requires_login()
def ajax_comp_rulesets_col_values():
    t = table_comp_rulesets('cr0', 'ajax_comp_rulesets')
    col = request.args[0]
    o = db.v_comp_rulesets[col]
    q = db.v_comp_rulesets.id > 0
    q = teams_publication_filter()
    for f in t.cols:
        q = _where(q, 'v_comp_rulesets', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o, cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_comp_rulesets():
    t = table_comp_rulesets('cr0', 'ajax_comp_rulesets')

    o = t.get_orderby(default=db.v_comp_rulesets.ruleset_name|db.v_comp_rulesets.chain_len|db.v_comp_rulesets.encap_rset|db.v_comp_rulesets.var_name)
    g = db.v_comp_rulesets.ruleset_id|db.v_comp_rulesets.id
    q = teams_publication_filter()
    for f in t.cols:
        q = _where(q, 'v_comp_rulesets', t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        t.csv_groupby = o
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        t.csv_orderby = o
        t.csv_groupby = o
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby, cacheable=False)
        return t.table_lines_data(n, html=False)

def teams_publication_filter():
    if 'Manager' in user_groups():
        q = db.v_comp_rulesets.ruleset_id > 0
    else:
        q = db.v_comp_rulesets.ruleset_id == db.comp_ruleset_team_publication.ruleset_id
        q &= db.comp_ruleset_team_publication.group_id.belongs(user_group_ids())
    return q

@auth.requires_login()
def comp_rules():
    t = SCRIPT(
          """table_comp_rules("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def comp_rules_load():
    return comp_rules()["table"]

@auth.requires_login()
def comp_rulesets_services():
    t = SCRIPT(
          """table_comp_rulesets_services("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def comp_rulesets_services_load():
    return comp_rulesets_services()["table"]

@auth.requires_login()
def comp_rulesets_nodes():
    t = SCRIPT(
          """table_comp_rulesets_nodes("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def comp_rulesets_nodes_load():
    return comp_rulesets_nodes()["table"]

#
# Modules sub-view
#
class table_comp_moduleset(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'modset_id',
                     'modset_name',
                     'teams_responsible',
                     'teams_publication',
                     'modset_mod_name',
                     'autofix',
                     'modset_mod_updated',
                     'modset_mod_author']
        self.colprops = {
            'id': HtmlTableColumn(
                     table='v_comp_modulesets',
                     field='id',
                    ),
            'modset_id': HtmlTableColumn(
                     table='v_comp_modulesets',
                     field='modset_id',
                    ),
            'modset_name': HtmlTableColumn(
                     table='v_comp_modulesets',
                     field='modset_name',
                    ),
            'autofix': HtmlTableColumn(
                     table='v_comp_modulesets',
                     field='autofix',
                    ),
            'modset_mod_name': HtmlTableColumn(
                     table='v_comp_modulesets',
                     field='modset_mod_name',
                    ),
            'modset_mod_updated': HtmlTableColumn(
                     table='v_comp_modulesets',
                     field='modset_mod_updated',
                    ),
            'modset_mod_author': HtmlTableColumn(
                     table='v_comp_modulesets',
                     field='modset_mod_author',
                    ),
            'teams_responsible': HtmlTableColumn(
                     table='v_comp_modulesets',
                     field='teams_responsible',
                    ),
            'teams_publication': HtmlTableColumn(
                     table='v_comp_modulesets',
                     field='teams_publication',
                    ),
        }
        self.ajax_col_values = ajax_comp_moduleset_col_values

@auth.requires_login()
def ajax_comp_moduleset_col_values():
    table_id = request.vars.table_id
    t = table_comp_moduleset(table_id, 'ajax_comp_moduleset')
    col = request.args[0]
    o = db[t.colprops[col].table][col]

    q = db.v_comp_modulesets.modset_id > 0
    if 'Manager' not in user_groups():
        q &= db.comp_moduleset_team_publication.group_id.belongs(user_group_ids())
        q &= db.comp_moduleset_team_publication.modset_id == v_comp_modulesets.modset_id
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_comp_moduleset():
    table_id = request.vars.table_id
    t = table_comp_moduleset(table_id, 'ajax_comp_moduleset')

    o = t.get_orderby(default=db.v_comp_modulesets.modset_name|db.v_comp_modulesets.modset_mod_name)
    q = db.v_comp_modulesets.modset_id > 0
    if 'Manager' not in user_groups():
        q &= db.comp_moduleset_team_publication.group_id.belongs(user_group_ids())
        q &= db.comp_moduleset_team_publication.modset_id == db.v_comp_modulesets.modset_id
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'data':
        n = len(db(q).select(db.v_comp_modulesets.id))
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(
          *cols,
          orderby=o,
          limitby=limitby,
          cacheable=True
        )
        return t.table_lines_data(n, html=False)
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_o = o
        return t.csv()


class table_comp_modulesets_services(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['svc_id', 'svcname', 'encap', 'modset_id', 'modset_name'] + services_cols + ['svc_status_updated']
        self.colprops = services_colprops
        self.colprops['svc_id'] = HtmlTableColumn(
                     field='svc_id',
                    )
        self.colprops['modset_id'] = HtmlTableColumn(
                     field='modset_id',
                    )
        self.colprops['modset_name'] = HtmlTableColumn(
                     field='modset_name',
                    )
        self.colprops['svc_status_updated'] = HtmlTableColumn(
                     field='svc_status_updated',
                    )
        self.colprops['encap'] = HtmlTableColumn(
                     field='encap',
                    )
        for c in self.cols:
            self.colprops[c].table = 'v_comp_services'
        self.ajax_col_values = 'ajax_comp_modulesets_services_col_values'

class table_comp_modulesets_nodes(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['node_id', 'nodename', 'modset_id', 'modset_name'] + nodes_cols
        self.colprops = nodes_colprops
        self.colprops['modset_id'] = HtmlTableColumn(
                     field='modset_id',
                    )
        self.colprops['node_id'] = HtmlTableColumn(
                     field='node_id',
                    )
        self.colprops['modset_name'] = HtmlTableColumn(
                     table='v_comp_moduleset',
                     field='modset_name',
                    )
        for c in self.cols:
            self.colprops[c].table = 'v_comp_nodes'
        self.ajax_col_values = 'ajax_comp_modulesets_nodes_col_values'

@auth.requires_login()
def ajax_comp_modulesets_services_col_values():
    table_id = request.vars.table_id
    t = table_comp_modulesets_services(table_id, 'ajax_comp_modulesets_services')
    col = request.args[0]
    o = db.v_comp_services[col]
    g = db.v_comp_services.svcname | db.v_comp_services.encap | db.v_comp_services.modset_name
    q = q_filter(app_field=db.v_comp_services.svc_app)
    if 'Manager' not in user_groups():
        q &= db.v_comp_services.team_responsible.belongs(user_groups())
    for f in t.cols:
        q = _where(q, 'v_comp_services', t.filter_parse(f), f)
    q = apply_gen_filters(q, 'v_comp_services')
    t.object_list = db(q).select(o, groupby=g, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_comp_modulesets_nodes_col_values():
    table_id = request.vars.table_id
    t = table_comp_modulesets_nodes(table_id, 'ajax_comp_modulesets_services')
    col = request.args[0]
    o = db.v_comp_nodes[col]
    g = db.v_comp_nodes.nodename | db.v_comp_nodes.modset_name
    q = q_filter(app_field=db.v_comp_nodes.app)
    if 'Manager' not in user_groups():
        q &= db.v_comp_nodes.team_responsible.belongs(user_groups())
    for f in t.cols:
        q = _where(q, 'v_comp_nodes', t.filter_parse(f), f)
    q = apply_gen_filters(q, 'v_comp_nodes')
    t.object_list = db(q).select(o, groupby=g, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_comp_modulesets_services():
    table_id = request.vars.table_id
    t = table_comp_modulesets_services(table_id, 'ajax_comp_modulesets_services')

    o = t.get_orderby(default=db.v_comp_services.svcname|db.v_comp_services.encap|db.v_comp_services.modset_name)
    g = db.v_comp_services.svcname | db.v_comp_services.encap | db.v_comp_services.modset_name
    q = q_filter(app_field=db.v_comp_services.svc_app)
    for f in t.cols:
        q = _where(q, 'v_comp_services', t.filter_parse(f), f)
    q = apply_gen_filters(q, 'v_comp_services')

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.v_comp_services.id.count(), cacheable=True).first()._extra[db.v_comp_services.id.count()]
        t.setup_pager(n)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, groupby=g, limitby=(t.pager_start,t.pager_end), orderby=o)
        return t.table_lines_data(n, html=False)
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_o = o
        return t.csv()

@auth.requires_login()
def ajax_comp_modulesets_nodes():
    table_id = request.vars.table_id
    t = table_comp_modulesets_nodes(table_id, 'ajax_comp_modulesets_services')

    o = t.get_orderby(default=db.v_comp_nodes.nodename)
    g = db.v_comp_nodes.nodename | db.v_comp_nodes.modset_name
    q = q_filter(app_field=db.v_comp_nodes.app)
    if 'Manager' not in user_groups():
        q &= db.v_comp_nodes.team_responsible.belongs(user_groups())
    for f in t.cols:
        q = _where(q, 'v_comp_nodes', t.filter_parse(f), f)
    q = apply_gen_filters(q, 'v_comp_nodes')

    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.v_comp_nodes.id.count(), cacheable=True).first()._extra[db.v_comp_nodes.id.count()]
        t.setup_pager(n)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, groupby=g, limitby=(t.pager_start,t.pager_end), orderby=o)
        return t.table_lines_data(n, html=False)
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_o = o
        return t.csv()

@auth.requires_login()
def comp_modules():
    t = SCRIPT(
          """table_comp_modules("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

@auth.requires_login()
def comp_modulesets_services():
    t = SCRIPT(
          """table_comp_modulesets_services("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def comp_modulesets_services_load():
    return comp_modulesets_services()["table"]

@auth.requires_login()
def comp_modulesets_nodes():
    t = SCRIPT(
          """table_comp_modulesets_nodes("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def comp_modulesets_nodes_load():
    return comp_modulesets_nodes()["table"]

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
                     field='mod_name',
                     table='comp_mod_status',
                    ),
            'total': HtmlTableColumn(
                     field='total',
                     table='comp_mod_status',
                    ),
            'ok': HtmlTableColumn(
                     field='ok',
                     table='comp_mod_status',
                    ),
            'nok': HtmlTableColumn(
                     field='nok',
                     table='comp_mod_status',
                    ),
            'na': HtmlTableColumn(
                     field='na',
                     table='comp_mod_status',
                    ),
            'obs': HtmlTableColumn(
                     field='obs',
                     table='comp_mod_status',
                    ),
            'pct': HtmlTableColumn(
                     field='pct',
                     table='comp_mod_status',
                    ),
            'mod_log': HtmlTableColumn(
                     field='mod_log',
                    ),
        }


class table_comp_svc_status(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['svc_id', 'svcname', 'total', 'ok', 'nok', 'na', 'obs', 'pct', "svc_log"]
        self.colprops = {
            'svc_id': HtmlTableColumn(
                     field='svc_id',
                     table='comp_svc_status',
                    ),
            'svcname': HtmlTableColumn(
                     field='svcname',
                     table='comp_svc_status',
                    ),
            'total': HtmlTableColumn(
                     field='total',
                     table='comp_svc_status',
                    ),
            'ok': HtmlTableColumn(
                     field='ok',
                     table='comp_svc_status',
                    ),
            'nok': HtmlTableColumn(
                     field='nok',
                     table='comp_svc_status',
                    ),
            'na': HtmlTableColumn(
                     field='na',
                     table='comp_svc_status',
                    ),
            'obs': HtmlTableColumn(
                     field='obs',
                     table='comp_svc_status',
                    ),
            'pct': HtmlTableColumn(
                     field='pct',
                     table='comp_svc_status',
                    ),
            'svc_log': HtmlTableColumn(
                     field='svc_log',
                    ),
        }

class table_comp_node_status(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['node_id', 'nodename', 'total', 'ok', 'nok', 'na', 'obs', 'pct', "node_log"]
        self.colprops = {
            'node_id': HtmlTableColumn(
                     field='node_id',
                     table='comp_node_status',
                    ),
            'nodename': HtmlTableColumn(
                     field='nodename',
                     table='comp_node_status',
                    ),
            'total': HtmlTableColumn(
                     field='total',
                     table='comp_node_status',
                    ),
            'ok': HtmlTableColumn(
                     field='ok',
                     table='comp_node_status',
                    ),
            'nok': HtmlTableColumn(
                     field='nok',
                     table='comp_node_status',
                    ),
            'na': HtmlTableColumn(
                     field='na',
                     table='comp_node_status',
                    ),
            'obs': HtmlTableColumn(
                     field='obs',
                     table='comp_node_status',
                    ),
            'pct': HtmlTableColumn(
                     field='pct',
                     table='comp_node_status',
                    ),
            'node_log': HtmlTableColumn(
                     field='node_log',
                    ),
        }

@service.json
def json_run_status_log(node_id, module):
    c = db.comp_log.run_status
    o = db.comp_log.run_date
    q = db.comp_log.node_id == node_id
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

def spark_id(node_id, module):
    module = module.replace('.', '_')
    module = module.replace('-', '_')
    return 'rh_%s_%s'%(node_id, module)

def spark_url(node_id, module):
    return URL(r=request,
               f='call/json/json_run_status_log/%(node)s/%(module)s'%dict(
                 node=node_id,
                 module=module)
           )

class table_comp_status(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'run_date',
                     'node_id',
                     'nodename',
                     'svc_id',
                     'svcname',
                     'run_module',
                     'run_status',
                     'run_status_log',
                     'rset_md5',
                     'run_log']
        self.cols += nodes_cols
        self.colprops = nodes_colprops
        self.colprops.update({
            'id': HtmlTableColumn(
                     field='id',
                     table='comp_status',
                    ),
            'run_date': HtmlTableColumn(
                     field='run_date',
                     table='comp_status',
                    ),
            'nodename': HtmlTableColumn(
                     field='nodename',
                     table='nodes',
                    ),
            'node_id': HtmlTableColumn(
                     field='node_id',
                     table='comp_status',
                    ),
            'svc_id': HtmlTableColumn(
                     field='svc_id',
                     table='comp_status',
                    ),
            'svcname': HtmlTableColumn(
                     field='svcname',
                     table='services',
                    ),
            'run_action': HtmlTableColumn(
                     field='run_action',
                     table='comp_status',
                    ),
            'run_module': HtmlTableColumn(
                     field='run_module',
                     table='comp_status',
                    ),
            'rset_md5': HtmlTableColumn(
                     field='rset_md5',
                     table='comp_status',
                    ),
            'run_status': HtmlTableColumn(
                     field='run_status',
                     table='comp_status',
                    ),
            'run_status_log': HtmlTableColumn(
                     field='un_status_log',
                     table='comp_status',
                    ),
            'run_log': HtmlTableColumn(
                     field='run_log',
                     table='comp_status',
                    ),
        })
        self.ajax_col_values = 'ajax_comp_status_col_values'

@auth.requires_login()
def fix_module_on_node():
    node_id = request.args[0]
    module = request.args[1]
    ug = user_groups()
    q = db.comp_status.node_id == node_id
    q &= db.comp_status.run_module == module
    q &= db.comp_status.node_id == db.nodes.node_id
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

    q = db.comp_status.id.belongs(ids)
    q &= db.comp_status.node_id == db.nodes.node_id
    q &= (db.nodes.team_responsible.belongs(user_groups())) | \
         (db.nodes.team_integ.belongs(user_groups()))
    rows = db(q).select(db.nodes.os_name,
                        db.nodes.action_type,
                        db.nodes.fqdn,
                        db.comp_status.node_id,
                        db.comp_status.svc_id,
                        db.comp_status.run_module)

    for row in rows:
        d = {
          "node_id": row.comp_status.node_id,
          "module": row.comp_status.run_module,
        }
        if row.comp_status.svc_id != "":
            d["svc_id"] = row.comp_status.svc_id
        json_action_one(d)

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

@auth.requires_login()
def ajax_comp_log_col_values():
    table_id = request.vars.table_id
    t = table_comp_log(table_id, 'ajax_comp_log')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    q = db.comp_log.node_id == db.nodes.node_id
    q = q_filter(q, node_field=db.comp_log.node_id)
    l = db.services.on(db.comp_log.svc_id==db.services.svc_id)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters_id(q, db.comp_log.node_id)
    t.object_list = db(q).select(o, orderby=o, left=l)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_comp_status_col_values():
    table_id = request.vars.table_id
    t = table_comp_status(table_id, 'ajax_comp_status')
    col = request.args[0]
    try:
        o = db[t.colprops[col].table][col]
    except:
        return T("this column is not filterable")
    q = db.comp_status.node_id == db.nodes.node_id
    l = db.services.on(db.comp_status.svc_id==db.services.svc_id)
    q = q_filter(q, node_field=db.comp_log.node_id)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters_id(q, db.comp_status.node_id)
    t.object_list = db(q).select(o, orderby=o, left=l, cacheable=True)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_comp_status():
    table_id = request.vars.table_id
    t = table_comp_status(table_id, 'ajax_comp_status')
    o = t.get_orderby(default=db.nodes.nodename)
    q = q_filter(node_field=db.comp_status.node_id)
    q &= db.comp_status.node_id == db.nodes.node_id
    l = db.services.on(db.comp_status.svc_id==db.services.svc_id)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters_id(q, db.comp_status.node_id)


    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        t.csv_left = l
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        t.csv_left = l
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.comp_status.id.count(), left=l, cacheable=True).first()._extra[db.comp_status.id.count()]
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, limitby=limitby, orderby=o, left=l, cacheable=False)
        return t.table_lines_data(n, html=False)

@service.json
@auth.requires_login()
def json_comp_status_agg():
    table_id = request.vars.table_id
    t = table_comp_status(table_id, 'ajax_comp_status')
    o = t.get_orderby(default=db.nodes.nodename)
    q = q_filter(node_field=db.comp_status.node_id)
    q &= db.comp_status.node_id == db.nodes.node_id
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters_id(q, db.comp_status.node_id)

    q_obs = q & (db.comp_status.run_date < now - datetime.timedelta(days=7))
    q_nok = q & (db.comp_status.run_date > now - datetime.timedelta(days=7)) & (db.comp_status.run_status == 1)
    q_na = q & (db.comp_status.run_date > now - datetime.timedelta(days=7)) & (db.comp_status.run_status == 2)
    q_ok = q & (db.comp_status.run_date > now - datetime.timedelta(days=7)) & (db.comp_status.run_status == 0)

    obs = db(q_obs).count()
    nok = db(q_nok).count()
    na = db(q_na).count()
    ok = db(q_ok).count()

    return {'obs': obs, 'ok': ok, 'na':na, 'nok': nok}

@auth.requires_login()
def comp_status():
    t = SCRIPT(
          """view_comp_status("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def comp_status_load():
    return comp_status()["table"]


@auth.requires_login()
def ajax_comp_svc_status():
    t = table_comp_status('cs0', 'ajax_comp_status')
    mt = table_comp_svc_status('css', 'ajax_comp_svc_status')

    o = t.get_orderby(default=db.services.svcname)
    q = q_filter(node_field=db.comp_status.node_id)
    q &= db.comp_status.node_id == db.nodes.node_id
    q &= db.comp_status.svc_id == db.services.svc_id
    q &= db.comp_status.svc_id != ""
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters_id(q, db.comp_status.node_id)
    sql1 = db(q)._select().rstrip(';').replace('v_svcmon.id, ','').replace('comp_status.id>0 AND', '')
    regex = re.compile("SELECT .* FROM")
    sql1 = regex.sub('', sql1)

    q = db.comp_svc_status.id > 0
    for f in mt.cols:
        q = _where(q, mt.colprops[f].table, mt.filter_parse(f), f)
    where = str(q).replace("comp_svc_status.", "u.")

    mt.setup_pager(-1)
    mt.additional_inputs = t.ajax_inputs()

    sql2 = """select * from (
                select t.id,
                     t.svc_id as svc_id,
                     t.svcname as svcname,
                     t.ok+t.nok+t.na+t.obs as total,
                     t.ok,
                     t.nok,
                     t.na,
                     t.obs,
                     floor((t.ok+t.na)*100/(t.ok+t.nok+t.na+t.obs)) as pct
                from (select comp_status.id,
                           comp_status.svc_id,
                           services.svcname,
                           sum(if(run_date>="%(d)s" and run_status=0, 1, 0)) as ok,
                           sum(if(run_date>="%(d)s" and run_status=1, 1, 0)) as nok,
                           sum(if(run_date>="%(d)s" and run_status=2, 1, 0)) as na,
                           sum(if(run_date<"%(d)s", 1, 0)) as obs
                    from %(sql)s and comp_status.svc_id=services.svc_id group by svc_id) t) u
              where %(where)s
              order by pct, total desc, svcname
              limit %(limit)d
              offset %(offset)d"""%dict(
                sql=sql1,
                where=where,
                d=(now-datetime.timedelta(days=7)),
                limit=mt.limit,
                offset=mt.pager_start,
           )

    rows = db.executesql(sql2)

    mt.object_list = map(lambda x: {'svc_id': x[1],
                                    'svcname': x[2],
                                    'total':x[3],
                                    'ok':x[4],
                                    'nok': x[5],
                                    'na': x[6],
                                    'obs': x[7],
                                    'pct':x[8]},
                          rows)

    if len(request.args) == 1 and request.args[0] == 'csv':
        return mt.csv()
    if len(request.args) == 1 and request.args[0] == 'data':
        return mt.table_lines_data(-1)

@auth.requires_login()
def ajax_comp_node_status():
    t = table_comp_status('cs0', 'ajax_comp_status')
    mt = table_comp_node_status('cns', 'ajax_comp_node_status')

    q = q_filter(node_field=db.comp_status.node_id)
    q &= db.comp_status.node_id == db.nodes.node_id
    q &= db.comp_status.svc_id == ""
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters_id(q, db.comp_status.node_id)
    sql1 = db(q)._select().rstrip(';').replace('nodes.id, ','').replace('comp_status.id>0 AND', '')
    regex = re.compile("SELECT .* FROM")
    sql1 = regex.sub('', sql1)

    q = db.comp_node_status.id > 0
    for f in mt.cols:
        q = _where(q, mt.colprops[f].table, mt.filter_parse(f), f)
    where = str(q).replace("comp_node_status.", "u.")

    mt.setup_pager(-1)
    mt.additional_inputs = t.ajax_inputs()

    sql2 = """select * from (
                select t.id,
                     t.node_id,
                     t.nodename,
                     t.ok+t.nok+t.na+t.obs as total,
                     t.ok,
                     t.nok,
                     t.na,
                     t.obs,
                     floor((t.ok+t.na)*100/(t.ok+t.nok+t.na+t.obs)) as pct
                from (select comp_status.id,
                           comp_status.node_id,
                           nodes.nodename,
                           sum(if(comp_status.run_date>="%(d)s" and comp_status.run_status=0, 1, 0)) as ok,
                           sum(if(comp_status.run_date>="%(d)s" and comp_status.run_status=1, 1, 0)) as nok,
                           sum(if(comp_status.run_date>="%(d)s" and comp_status.run_status=2, 1, 0)) as na,
                           sum(if(comp_status.run_date<"%(d)s", 1, 0)) as obs
                    from %(sql)s group by comp_status.node_id) t) u
              where %(where)s
              order by pct, total desc, nodename
              limit %(limit)d
              offset %(offset)d"""%dict(
                sql=sql1,
                where=where,
                d=(now-datetime.timedelta(days=7)),
                limit=mt.limit,
                offset=mt.pager_start,
           )

    rows = db.executesql(sql2)

    mt.object_list = map(lambda x: {'node_id': x[1],
                                    'nodename': x[2],
                                    'total':x[3],
                                    'ok':x[4],
                                    'nok': x[5],
                                    'na': x[6],
                                    'obs': x[7],
                                    'pct':x[8]},
                          rows)

    if len(request.args) == 1 and request.args[0] == 'csv':
        return mt.csv()
    if len(request.args) == 1 and request.args[0] == 'data':
        return mt.table_lines_data(-1)

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
               url=URL(r=request, f='call/json/json_svc_history', vars={'svc_id': request.vars.svc_id}),
               id=id_chart,
            ),
            _name=id+'_to_eval'
          ),
        _class="p-3",
        )
    return d

@service.json
def json_svc_history():
    t = table_comp_status('cs0', 'ajax_comp_status')
    q = q_filter(node_field=db.comp_status.node_id)
    q &= db.comp_status.node_id == db.nodes.node_id
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters_id(q, db.comp_status.node_id)
    _sql = db(q)._select(db.comp_status.run_module)
    _sql = _sql.rstrip(';')

    sql = """select
               t.run_date,
               sum(t.ok) as ok,
               sum(t.nok) as nok,
               sum(t.na) as na
              from
              (
                select run_date,
                    if(run_status=0, 1, 0) as ok,
                    if(run_status=1, 1, 0) as nok,
                    if(run_status=2, 1, 0) as na
                from comp_log_daily
                where svc_id="%(svc_id)s" and
                    run_date>date_sub(now(), interval 1 year) and
                    run_module in (%(_sql)s)
              ) t
              group by t.run_date
             """%dict(svc_id=request.vars.svc_id, _sql=_sql)
    ok = []
    nok = []
    na = []
    for r in db.executesql(sql):
        ok.append((r[0], int(r[1])))
        nok.append((r[0], int(r[2])))
        na.append((r[0], int(r[3])))
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
        _class="p-3",
      )
    return d

@service.json
def json_mod_history():
    t = table_comp_status('cs0', 'ajax_comp_status')
    q = q_filter(node_field=db.comp_status.node_id)
    q &= db.comp_status.run_module == request.vars.modname
    q &= db.comp_status.node_id == db.nodes.node_id
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters_id(q, db.comp_status.node_id)
    _sql = db(q)._select(db.comp_status.node_id)
    _sql = _sql.rstrip(';')
    #nodes = ','.join(map(lambda x: repr(str(x)), [r[0] for r in db.executesql(_sql)]))

    sql = """select
               t.run_date,
               sum(t.ok) as ok,
               sum(t.nok) as nok,
               sum(t.na) as na
              from
              (
                select run_date,
                    if(run_status=0, 1, 0) as ok,
                    if(run_status=1, 1, 0) as nok,
                    if(run_status=2, 1, 0) as na
                from comp_log_daily
                where run_module="%(mod)s" and
                    run_date>date_sub(now(), interval 1 year) and
                    node_id in (%(_sql)s)
              ) t
              group by t.run_date
             """%dict(mod=request.vars.modname, _sql=_sql)
    #raise Exception(sql)
    ok = []
    nok = []
    na = []
    for r in db.executesql(sql):
        ok.append((r[0], int(r[1])))
        nok.append((r[0], int(r[2])))
        na.append((r[0], int(r[3])))
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
               url=URL(r=request, f='call/json/json_node_history', vars={'node_id': request.vars.node_id}),
               id=id_chart,
            ),
            _name=id+'_to_eval'
          ),
        _class="p-3",
        )
    return d

@service.json
def json_node_history():
    t = table_comp_status('cs0', 'ajax_comp_status')
    q = q_filter(node_field=db.comp_status.node_id)
    q &= db.comp_status.node_id == db.nodes.node_id
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters_id(q, db.comp_status.node_id)
    _sql = db(q)._select(db.comp_status.run_module)
    _sql = _sql.rstrip(';')

    sql = """select
               t.run_date,
               sum(t.ok) as ok,
               sum(t.nok) as nok,
               sum(t.na) as na
              from
              (
                select run_date,
                    if(run_status=0, 1, 0) as ok,
                    if(run_status=1, 1, 0) as nok,
                    if(run_status=2, 1, 0) as na
                from comp_log_daily
                where node_id="%(node)s" and
                    run_date>date_sub(now(), interval 1 year) and
                    run_module in (%(_sql)s)
              ) t
              group by t.run_date
             """%dict(node=request.vars.node_id, _sql=_sql)
    ok = []
    nok = []
    na = []
    for r in db.executesql(sql):
        ok.append((r[0], int(r[1])))
        nok.append((r[0], int(r[2])))
        na.append((r[0], int(r[3])))
    return [ok, nok, na]

@auth.requires_login()
def ajax_comp_mod_status():
    t = table_comp_status('cs0', 'ajax_comp_status')
    mt = table_comp_mod_status('cms', 'ajax_comp_mod_status')

    o = mt.get_orderby(default=~db.nodes.nodename)
    q = q_filter(node_field=db.comp_status.node_id)
    q &= db.comp_status.node_id == db.nodes.node_id
    q &= ((db.comp_status.svc_id != None) & (db.comp_status.svc_id == db.services.svc_id))
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters_id(q, db.comp_status.node_id)
    sql1 = db(q)._select().rstrip(';').replace('nodes.id, ','').replace('comp_status.id>0 AND', '')
    regex = re.compile("SELECT .* FROM")
    sql1 = regex.sub('', sql1)

    q = db.comp_mod_status.id > 0
    for f in mt.cols:
        q = _where(q, mt.colprops[f].table, mt.filter_parse(f), f)
    where = str(q).replace("comp_mod_status.", "u.")

    mt.setup_pager(-1)
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
                limit=mt.limit,
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
    if len(request.args) == 1 and request.args[0] == 'data':
        return mt.table_lines_data(-1)

class table_comp_log(table_comp_status):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        table_comp_status.__init__(self, id, 'ajax_comp_log', innerhtml)
        self.cols = ['run_date',
                     'node_id',
                     'nodename',
                     'svc_id',
                     'svcname',
                     'id',
                     'run_module',
                     'run_action',
                     'run_status',
                     'run_log',
                     'rset_md5']
        for c in self.colprops:
            if 'run_' in c or c in ('rset_md5', 'node_id', 'svc_id', 'id'):
                self.colprops[c].table = 'comp_log'
        self.ajax_col_values = 'ajax_comp_log_col_values'

@auth.requires_login()
def ajax_comp_log():
    table_id = request.vars.table_id
    t = table_comp_log(table_id, 'ajax_comp_log')

    db.commit()
    o = ~db.comp_log.id
    q = q_filter(node_field=db.comp_log.node_id)
    q &= db.comp_log.node_id == db.nodes.node_id
    l = db.services.on(db.comp_log.svc_id==db.services.svc_id)
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    q = apply_filters_id(q, db.comp_log.node_id)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        t.csv_left = l
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        t.csv_left = l
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        if request.vars.volatile_filters is None:
            limitby = (t.pager_start,t.pager_end)
        else:
            limitby = (0, 500)
        n = db(q).select(db.comp_log.id.count(), left=l, cacheable=True).first()._extra[db.comp_log.id.count()]
        t.setup_pager(n)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, limitby=limitby, orderby=o, left=l, cacheable=False)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def comp_log():
    t = SCRIPT(
          """table_comp_log("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def comp_log_load():
    return comp_log()["table"]

def call():
    session.forget(response)
    return service()

def user():
    return auth()

@service.xmlrpc
def comp_get_moduleset_modules(moduleset, auth):
    return rpc_comp_get_moduleset_modules(moduleset, auth)

@auth_uuid
def rpc_comp_get_moduleset_modules(moduleset, auth):
    node_id = auth_to_node_id(auth)
    return _comp_get_moduleset_modules(moduleset, node_id)

def _comp_get_moduleset_modules(moduleset, node_id):
    if isinstance(moduleset, list):
        if len(moduleset) == 0:
            return []
        q = db.comp_moduleset.modset_name.belongs(moduleset)
    elif isinstance(moduleset, str):
        q = db.comp_moduleset.modset_name == moduleset
    else:
        return []
    q &= db.comp_moduleset_modules.modset_id == db.comp_moduleset.id
    q &= db.comp_moduleset.id == db.comp_moduleset_team_publication.modset_id
    q &= db.auth_group.id == db.comp_moduleset_team_publication.group_id
    q &= (db.nodes.team_responsible == db.auth_group.role)|(db.auth_group.role=="Everybody")
    q &= db.nodes.node_id == node_id
    rows = db(q).select(db.comp_moduleset_modules.modset_mod_name,
                        groupby=db.comp_moduleset_modules.modset_mod_name,
                        cacheable=True)
    return [r.modset_mod_name for r in rows]

def _comp_get_moduleset_svc_modules(moduleset, svc_id):
    if isinstance(moduleset, list):
        if len(moduleset) == 0:
            return []
        q = db.comp_moduleset.modset_name.belongs(moduleset)
    elif isinstance(moduleset, str):
        q = db.comp_moduleset.modset_name == moduleset
    else:
        return []
    q &= db.comp_moduleset_modules.modset_id == db.comp_moduleset.id
    q &= db.comp_moduleset.id == db.comp_moduleset_team_publication.modset_id
    q &= db.auth_group.id == db.comp_moduleset_team_publication.group_id
    q &= db.apps_responsibles.group_id == db.auth_group.id
    q &= db.apps_responsibles.app_id == db.apps.id
    q &= db.apps.app == db.services.svc_app
    q &= db.services.svc_id == svc_id
    rows = db(q).select(db.comp_moduleset_modules.modset_mod_name,
                        groupby=db.comp_moduleset_modules.modset_mod_name,
                        cacheable=True)
    return [r.modset_mod_name for r in rows]

def mangle_lib_result(d):
    msg = []
    if "error" in d:
        d["status"] = False
        msg.append(d["error"])
    else:
        d["status"] = True
    if "info" in d:
        d["msg"] = d["info"]
        msg.append(d["info"])
    d["msg"] = '. '.join(msg)
    return d

@service.xmlrpc
def comp_attach_svc_ruleset(svcname, ruleset, auth):
    return rpc_comp_attach_svc_ruleset(svcname, ruleset, auth)

@auth_uuid
def rpc_comp_attach_svc_ruleset(svcname, ruleset, auth):
    if len(ruleset) == 0:
        return dict(status=False, msg="no ruleset specified"%ruleset)
    rset_id = comp_ruleset_id(ruleset)
    if rset_id is None:
        return dict(status=False, msg="ruleset %s does not exist"%ruleset)
    node_id = auth_to_node_id(auth)
    svc_id = node_svc_id(node_id, svcname)
    slave = comp_slave(svc_id, node_id)
    d = lib_comp_ruleset_attach_service(svc_id, rset_id, slave)
    return mangle_lib_result(d)

@service.xmlrpc
def comp_attach_svc_moduleset(svcname, moduleset, auth):
    return rpc_comp_attach_svc_moduleset(svcname, moduleset, auth)

@auth_uuid
def rpc_comp_attach_svc_moduleset(svcname, moduleset, auth):
    if len(moduleset) == 0:
        return dict(status=False, msg="no moduleset specified"%moduleset)
    modset_id = comp_moduleset_id(moduleset)
    if modset_id is None:
        return dict(status=False, msg="moduleset %s does not exist"%moduleset)
    node_id = auth_to_node_id(auth)
    svc_id = node_svc_id(node_id, svcname)
    slave = comp_slave(svc_id, node_id)
    d = lib_comp_moduleset_attach_service(svc_id, modset_id, slave)
    return mangle_lib_result(d)

@service.xmlrpc
def comp_attach_moduleset(nodename, moduleset, auth):
    return rpc_comp_attach_moduleset(nodename, moduleset, auth)

@auth_uuid
def rpc_comp_attach_moduleset(nodename, moduleset, auth):
    if len(moduleset) == 0:
        return dict(status=False, msg="no moduleset specified"%moduleset)
    modset_id = comp_moduleset_id(moduleset)
    if modset_id is None:
        return dict(status=False, msg="moduleset %s does not exist"%moduleset)
    node_id = auth_to_node_id(auth)
    d = lib_comp_moduleset_attach_node(node_id, modset_id)
    return mangle_lib_result(d)

@service.xmlrpc
def comp_detach_svc_ruleset(svcname, ruleset, auth):
    return rpc_comp_detach_svc_ruleset(svcname, ruleset, auth)

@auth_uuid
def rpc_comp_detach_svc_ruleset(svcname, ruleset, auth):
    if len(ruleset) == 0:
        return dict(status=False, msg="no ruleset specified"%ruleset)
    node_id = auth_to_node_id(auth)
    svc_id = node_svc_id(node_id, svcname)
    slave = comp_slave(svc_id, node_id)
    if ruleset == 'all':
        ruleset_id = comp_attached_svc_ruleset_id(svc_id, slave)
    else:
        ruleset_id = comp_ruleset_id(ruleset)
    if ruleset_id is None:
        return dict(status=True, msg="ruleset %s does not exist"%ruleset)
    elif ruleset == 'all' and len(ruleset_id) == 0:
        return dict(status=True, msg="this service has no ruleset attached")
    d = lib_comp_ruleset_detach_service(svc_id, ruleset_id, slave)
    return mangle_lib_result(d)

@service.xmlrpc
def comp_detach_svc_moduleset(svcname, moduleset, auth):
    return rpc_comp_detach_svc_moduleset(svcname, moduleset, auth)

@auth_uuid
def rpc_comp_detach_svc_moduleset(svcname, moduleset, auth):
    if len(moduleset) == 0:
        return dict(status=False, msg="no moduleset specified"%moduleset)
    node_id = auth_to_node_id(auth)
    svc_id = node_svc_id(node_id, svcname)
    slave = comp_slave(svc_id, node_id)
    if moduleset == 'all':
        modset_id = comp_attached_svc_moduleset_id(svc_id)
    else:
        modset_id = comp_moduleset_id(moduleset)
    if modset_id is None:
        return dict(status=True, msg="moduleset %s does not exist"%moduleset)
    elif moduleset == 'all' and len(modset_id) == 0:
        return dict(status=True, msg="this service has no moduleset attached")
    d = lib_comp_moduleset_detach_service(svc_id, modset_id, slave)
    return mangle_lib_result(d)

@service.xmlrpc
def comp_detach_moduleset(nodename, moduleset, auth):
    return rpc_comp_detach_moduleset(nodename, moduleset, auth)

@auth_uuid
def rpc_comp_detach_moduleset(nodename, moduleset, auth):
    if len(moduleset) == 0:
        return dict(status=False, msg="no moduleset specified"%moduleset)
    node_id = auth_to_node_id(auth)
    if moduleset == 'all':
        modset_id = comp_attached_moduleset_id(node_id)
    else:
        modset_id = comp_moduleset_id(moduleset)
    if modset_id is None:
        return dict(status=True, msg="moduleset %s does not exist"%moduleset)
    elif moduleset == 'all' and len(modset_id) == 0:
        return dict(status=True, msg="this node has no moduleset attached")
    d = lib_comp_moduleset_detach_node(node_id, modset_id)
    return mangle_lib_result(d)

@service.xmlrpc
def comp_attach_ruleset(nodename, ruleset, auth):
    return rpc_comp_attach_ruleset(nodename, ruleset, auth)

@auth_uuid
def rpc_comp_attach_ruleset(nodename, ruleset, auth):
    if len(ruleset) == 0:
        return dict(status=False, msg="no ruleset specified"%ruleset)
    ruleset_id = comp_ruleset_id(ruleset)
    if ruleset_id is None:
        return dict(status=False, msg="ruleset %s does not exist"%ruleset)
    node_id = auth_to_node_id(auth)
    d = lib_comp_ruleset_attach_node(node_id, ruleset_id)
    return mangle_lib_result(d)

@service.xmlrpc
def comp_detach_ruleset(nodename, ruleset, auth):
    return rpc_comp_detach_ruleset(nodename, ruleset, auth)

@auth_uuid
def rpc_comp_detach_ruleset(nodename, ruleset, auth):
    if len(ruleset) == 0:
        return dict(status=False, msg="no ruleset specified"%ruleset)
    node_id = auth_to_node_id(auth)
    if ruleset == 'all':
        ruleset_id = comp_attached_ruleset_id(node_id)
    else:
        ruleset_id = comp_ruleset_id(ruleset)
    if ruleset_id is None:
        return dict(status=False, msg="ruleset %s does not exist"%ruleset)
    elif ruleset == 'all' and len(ruleset_id) == 0:
        return dict(status=True, msg="this node has no ruleset attached")
    d = lib_comp_ruleset_detach_node(node_id, ruleset_id)
    return mangle_lib_result(d)

@service.xmlrpc
def comp_list_rulesets(pattern='%', nodename=None, auth=("", "")):
    return rpc_comp_list_rulesets(pattern=pattern, nodename=nodename, auth=auth)

@auth_uuid
def rpc_comp_list_rulesets(pattern='%', nodename=None, auth=("", "")):
    node_id = auth_to_node_id(auth)
    q = db.comp_rulesets.ruleset_name.like(pattern)
    q &= db.comp_rulesets.ruleset_type == 'explicit'
    q &= db.comp_rulesets.ruleset_public == True
    q &= db.comp_rulesets.id == db.comp_ruleset_team_publication.ruleset_id
    if node_id != None:
        q &= db.nodes.node_id == node_id
        q &= (db.nodes.team_responsible == db.auth_group.role)|(db.auth_group.role=="Everybody")
        q &= db.auth_group.id == db.comp_ruleset_team_publication.group_id
    rows = db(q).select(groupby=db.comp_rulesets.id, cacheable=True)
    return sorted([r.comp_rulesets.ruleset_name for r in rows])

@service.xmlrpc
def comp_list_modulesets(pattern='%', auth=("", "")):
    return rpc_comp_list_modulesets(pattern=pattern, auth=auth)

@auth_uuid
def rpc_comp_list_modulesets(pattern='%', auth=("", "")):
    node_id = auth_to_node_id(auth)
    q = db.comp_moduleset.modset_name.like(pattern)
    q &= db.comp_moduleset.id == db.comp_moduleset_team_publication.modset_id
    q &= db.auth_group.id == db.comp_moduleset_team_publication.group_id
    q &= (db.nodes.team_responsible == db.auth_group.role)|(db.auth_group.role=="Everybody")
    q &= db.nodes.node_id == node_id
    rows = db(q).select(db.comp_moduleset.modset_name,
                        groupby=db.comp_moduleset.modset_name, cacheable=True)
    return sorted([r.modset_name for r in rows])

@service.xmlrpc
def comp_show_status(svcname="", pattern='%', auth=("", "")):
    return rpc_comp_show_status(svcname=svcname, pattern=pattern, auth=auth)

@auth_uuid
def rpc_comp_show_status(svcname="", pattern='%', auth=("", "")):
    node_id = auth_to_node_id(auth)
    svc_id = node_svc_id(node_id, svcname)
    q = db.comp_status.run_module.like(pattern)
    q &= db.comp_status.node_id == node_id
    q &= db.comp_status.svc_id == svc_id
    rows = db(q).select(orderby=db.comp_status.run_module, cacheable=True)
    l = [('module', 'status', 'date', 'log')]
    for row in rows:
        l.append((row.run_module,
                  str(row.run_status),
                  row.run_date.strftime("%Y-%m-%d %H:%M:%S"),
                  row.run_log))
    return l

@service.xmlrpc
def comp_get_svc_moduleset(svcname, auth):
    return rpc_comp_get_svc_moduleset(svcname, auth)

@auth_uuid
def rpc_comp_get_svc_moduleset(svcname, auth):
    node_id = auth_to_node_id(auth)
    svc_id = node_svc_id(node_id, svcname)
    slave = comp_slave(svc_id, node_id)
    return _comp_get_svc_moduleset(svc_id, slave=slave)

@service.xmlrpc
def comp_get_svc_data_v2(nodename, svcname, modulesets, auth):
    return rpc_comp_get_svc_data(nodename, svcname, modulesets, True, auth)

@service.xmlrpc
def comp_get_svc_data(nodename, svcname, modulesets, auth):
    return rpc_comp_get_svc_data(nodename, svcname, modulesets, False, auth)

@auth_uuid
def rpc_comp_get_svc_data(nodename, svcname, modulesets, var_class, auth):
    node_id = auth_to_node_id(auth)
    svc_id = node_svc_id(node_id, svcname)
    return _comp_get_svc_data(node_id, svc_id, modulesets=modulesets, var_class=var_class)

@service.xmlrpc
def comp_get_data_v2(nodename, modulesets, auth):
    return rpc_comp_get_data(nodename, modulesets, True, auth)

@service.xmlrpc
def comp_get_data(nodename, modulesets, auth):
    return rpc_comp_get_data(nodename, modulesets, False, auth)

@auth_uuid
def rpc_comp_get_data(nodename, modulesets, var_class, auth):
    node_id = auth_to_node_id(auth)
    return _comp_get_data(node_id, modulesets=modulesets, var_class=var_class)

def sanitize_modulesets(modulesets):
    return list(set(modulesets) - set([""]))

def _comp_get_data(node_id, modulesets=[], var_class=False):
    modulesets = sanitize_modulesets(modulesets)
    return {
      'modulesets': _comp_get_moduleset_data(node_id, modulesets=modulesets),
      'rulesets': _comp_get_ruleset(node_id, modulesets=modulesets, var_class=var_class),
      'modset_rset_relations': get_modset_rset_relations_s(),
      'modset_relations': get_modset_relations_s(),
    }

def _comp_get_svc_data(node_id, svc_id, modulesets=[], var_class=False):
    slave = comp_slave(svc_id, node_id)
    modulesets = sanitize_modulesets(modulesets)
    return {
      'modulesets': _comp_get_svc_moduleset_data(svc_id, modulesets=modulesets, slave=slave),
      'rulesets': _comp_get_svc_ruleset(svc_id, node_id, slave=slave, modulesets=modulesets, var_class=var_class),
      'modset_rset_relations': get_modset_rset_relations_s(),
      'modset_relations': get_modset_relations_s(),
    }

def test_comp_get_data():
    d = _comp_get_data(1137921)
    print d

def test_comp_get_svc_ruleset():
    return _comp_get_svc_ruleset("unxdevweb01", 1137921)

@service.xmlrpc
def comp_get_moduleset_data(nodename, auth):
    node_id = auth_to_node_id(auth)
    return rpc_comp_get_moduleset_data(node_id, auth)

@auth_uuid
def rpc_comp_get_moduleset_data(node_id, auth):
    return _comp_get_moduleset_data(node_id)

@service.xmlrpc
def comp_get_data_moduleset(nodename, auth):
    node_id = auth_to_node_id(auth)
    return rpc_comp_get_data_moduleset(node_id, auth)

@auth_uuid
def rpc_comp_get_data_moduleset(node_id, auth):
    return {
      'root_modulesets': _comp_get_moduleset_names(node_id),
      'modulesets': _comp_get_moduleset_data(node_id),
      'modset_relations': get_modset_relations_s(),
    }

@service.xmlrpc
def comp_get_svc_data_moduleset(svcname, auth):
    return rpc_comp_get_svc_data_moduleset(svcname, auth)

@auth_uuid
def rpc_comp_get_svc_data_moduleset(svcname, auth):
    node_id = auth_to_node_id(auth)
    svc_id = node_svc_id(node_id, svcname)
    slave = comp_slave(svc_id, node_id)
    return {
      'root_modulesets': _comp_get_svc_moduleset_names(svc_id, slave=slave),
      'modulesets': _comp_get_svc_moduleset_data(svc_id, slave=slave),
      'modset_relations': get_modset_relations_s(),
    }

@service.xmlrpc
def comp_get_svc_moduleset_data(svcname, auth):
    return rpc_comp_get_svc_moduleset_data(svcname, auth)

@auth_uuid
def rpc_comp_get_svc_moduleset_data(svcname, auth):
    node_id = auth_to_node_id(auth)
    svc_id = node_svc_id(node_id, svcname)
    slave = comp_slave(svc_id, node_id)
    return _comp_get_svc_moduleset_data(svc_id, slave=slave)

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

@service.xmlrpc
def comp_get_moduleset(nodename, auth):
    return rpc_comp_get_moduleset(auth)

@auth_uuid
def rpc_comp_get_moduleset(auth):
    node_id = auth_to_node_id(auth)
    return _comp_get_moduleset(node_id)

def _comp_get_svc_moduleset_ids_with_children(svc_id, modulesets=[], slave=False):
    modset_ids = _comp_get_svc_moduleset_ids(svc_id, modulesets=modulesets, slave=slave)
    modset_tree_nodes = get_modset_tree_nodes(modset_ids)
    modset_ids = set(modset_tree_nodes.keys())
    for l in modset_tree_nodes.values():
        modset_ids |= set(l)
    return modset_ids

def _comp_get_svc_moduleset(svc_id, modulesets=[], slave=False):
    modset_ids = _comp_get_svc_moduleset_ids(svc_id, modulesets=modulesets, slave=slave)
    q = db.comp_moduleset.id.belongs(modset_ids)
    rows = db(q).select(db.comp_moduleset.modset_name, cacheable=True)
    return [r.modset_name for r in rows]

def _comp_get_svc_moduleset_ids(svc_id, modulesets=[], slave=False):
    if len(modulesets) == 0:
        return _comp_get_svc_moduleset_ids_attached(svc_id, slave)
    else:
        return _comp_get_svc_moduleset_ids_specified(svc_id, modulesets, slave)

def _comp_get_svc_moduleset_ids_attached(svc_id, modulesets=[], slave=False):
    q = db.comp_modulesets_services.svc_id == svc_id
    q &= db.comp_modulesets_services.slave == slave
    q &= db.comp_modulesets_services.modset_id == db.comp_moduleset.id
    q &= db.comp_moduleset.id == db.comp_moduleset_team_publication.modset_id
    q &= db.auth_group.id == db.comp_moduleset_team_publication.group_id
    q1 = db.auth_group.role == "Everybody"
    q2 = db.services.svc_id == svc_id
    q2 &= db.services.svc_app == db.apps.app
    q2 &= db.apps.id == db.apps_responsibles.app_id
    q2 &= db.apps_responsibles.group_id == db.auth_group.id
    q &= (q1 | q2)
    rows = db(q).select(db.comp_moduleset.id, groupby=db.comp_moduleset.id, cacheable=True)
    modset_ids = [r.id for r in rows]
    return modset_ids

def _comp_get_svc_moduleset_ids_specified(svc_id, modulesets=[], slave=False):
    q = db.comp_moduleset.modset_name.belongs(modulesets)
    q &= db.comp_moduleset.id == db.comp_moduleset_team_publication.modset_id
    q &= db.auth_group.id == db.comp_moduleset_team_publication.group_id
    q1 = db.auth_group.role == "Everybody"
    q2 = db.services.svc_id == svc_id
    q2 &= db.services.svc_app == db.apps.app
    q2 &= db.apps.id == db.apps_responsibles.app_id
    q2 &= db.apps_responsibles.group_id == db.auth_group.id
    q &= (q1 | q2)
    rows = db(q).select(db.comp_moduleset.id, groupby=db.comp_moduleset.id, cacheable=True)
    modset_ids = [r.id for r in rows]
    return modset_ids

def _comp_get_svc_moduleset_names(svc_id, modulesets=[], slave=False):
    modset_ids = _comp_get_svc_moduleset_ids(svc_id, modulesets=modulesets, slave=slave)
    modset_names = get_modset_names(modset_ids)
    return modset_names.values()

def _comp_get_svc_moduleset_data(svc_id, modulesets=[], slave=False):
    modset_ids = _comp_get_svc_moduleset_ids_with_children(svc_id, modulesets=modulesets, slave=slave)
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

def _comp_get_moduleset_ids(node_id, modulesets=[]):
    if len(modulesets) == 0:
        return _comp_get_moduleset_ids_attached(node_id)
    else:
        return _comp_get_moduleset_ids_specified(node_id, modulesets)

def _comp_get_moduleset_ids_attached(node_id):
    q = db.comp_node_moduleset.node_id == node_id
    q &= db.comp_node_moduleset.modset_id == db.comp_moduleset.id
    q &= db.comp_moduleset.id == db.comp_moduleset_team_publication.modset_id
    q &= db.auth_group.id == db.comp_moduleset_team_publication.group_id
    q &= (db.nodes.team_responsible == db.auth_group.role)|(db.auth_group.role=="Everybody")
    q &= db.nodes.node_id == node_id
    rows = db(q).select(db.comp_moduleset.id, groupby=db.comp_moduleset.id, cacheable=True)
    modset_ids = [r.id for r in rows]
    return modset_ids

def _comp_get_moduleset_ids_specified(node_id, modulesets=[]):
    q = db.comp_moduleset.modset_name.belongs(modulesets)
    q &= db.comp_moduleset.id == db.comp_moduleset_team_publication.modset_id
    q &= db.auth_group.id == db.comp_moduleset_team_publication.group_id
    q &= (db.nodes.team_responsible == db.auth_group.role)|(db.auth_group.role=="Everybody")
    q &= db.nodes.node_id == node_id
    rows = db(q).select(db.comp_moduleset.id, groupby=db.comp_moduleset.id, cacheable=True)
    modset_ids = [r.id for r in rows]
    return modset_ids

def _comp_get_moduleset_names(node_id, modulesets=[]):
    modset_ids = _comp_get_moduleset_ids(node_id, modulesets=modulesets)
    modset_names = get_modset_names(modset_ids)
    return modset_names.values()

def _comp_get_moduleset_ids_with_children(node_id, modulesets=[]):
    modset_ids = _comp_get_moduleset_ids(node_id, modulesets=modulesets)
    modset_tree_nodes = get_modset_tree_nodes(modset_ids)
    modset_ids = set(modset_tree_nodes.keys())
    for l in modset_tree_nodes.values():
        modset_ids |= set(l)
    return modset_ids

def _comp_get_moduleset_data(node_id, modulesets=[]):
    modset_ids = _comp_get_moduleset_ids_with_children(node_id, modulesets=modulesets)
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

def _comp_get_moduleset(node_id, modulesets=[]):
    modset_ids = _comp_get_moduleset_ids_with_children(node_id, modulesets)
    q = db.comp_moduleset.id.belongs(modset_ids)
    rows = db(q).select(db.comp_moduleset.modset_name, cacheable=True)
    return [r.modset_name for r in rows]

@service.xmlrpc
def comp_log_action(vars, vals, auth):
    return rpc_comp_log_action(vars, vals, auth)

@auth_uuid
def rpc_comp_log_action(vars, vals, auth):
    node_id = auth_to_node_id(auth)
    vars, vals = replace_nodename_in_data(vars, vals, auth, fieldname="run_nodename")
    vars, vals = replace_svcname_in_data(vars, vals, auth, fieldname="run_svcname")
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

    update_dash_compdiff(node_id)
    ws_send('comp_status_change', {'node_id': node_id})
    ws_send('comp_log_change', {'node_id': node_id})


@service.xmlrpc
def comp_log_actions(vars, vals, auth):
    return rpc_comp_log_actions(vars, vals, auth)

@auth_uuid
def rpc_comp_log_actions(vars, vals, auth):
    if len(vals) == 0:
        return
    node_id = auth_to_node_id(auth)
    vars, vals = replace_nodename_in_data(vars, vals, auth, fieldname="run_nodename")
    vars, vals = replace_svcname_in_data(vars, vals, auth, fieldname="run_svcname")
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
    ws_send('comp_status_change', {'node_id': node_id})
    ws_send('comp_log_change', {'node_id': node_id})
    update_dash_compdiff(node_id)

    # update comp_log_daily for faster charting
    l = []
    for key in ("run_log", "run_action", "rset_md5"):
        l.append(vars.index(key))
    l = sorted(l, reverse=True)
    for j in l:
        del(vars[j])
    for i, _vals in enumerate(check_vals):
        for j in l:
            del(check_vals[i][j])
    generic_insert('comp_log_daily', vars, check_vals)


def comp_format_filter(q):
    s = str(q)
    if 'comp_node_ruleset' in s:
        return ''
    #s = s.replace('(','')
    #s = s.replace(')','')
    s = s.replace('nodes.id>0 AND ','')
    return s

def comp_get_svcmon_ruleset(svc_id, node_id):
    q = db.svcmon.svc_id == svc_id
    q &= db.svcmon.node_id == node_id
    q &= db.svcmon.mon_updated > now - datetime.timedelta(minutes=15)
    row = db(q).select(cacheable=True).first()
    if row is None:
        q = db.svcmon.svc_id == svc_id
        q &= db.svcmon.mon_vmname == db.nodes.nodename
        q &= db.nodes.node_id == node_id
        q &= db.svcmon.mon_containerstatus == "up"
        row = db(q).select(db.svcmon.ALL, cacheable=True).first()
    if row is None:
        return {}
    ruleset = {'name': 'osvc_svcmon',
               'filter': str(q),
               'vars': []}
    for f in db.svcmon.fields:
        val = row[f]
        ruleset['vars'].append(('svcmon.'+f, val))
    return {'osvc_svcmon':ruleset}

def comp_get_service_ruleset(svc_id):
    q = db.services.svc_id == svc_id
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

def comp_get_node_ruleset(node_id):
    q = db.nodes.node_id == node_id
    rows = db(q).select(cacheable=True)
    if len(rows) != 1:
        return {}
    ruleset = {'name': 'osvc_node',
               'filter': str(q),
               'vars': []}
    for f in db.nodes.fields:
        val = rows[0][f]
        if type(val) == datetime.date:
            val = val.strftime("%Y-%m-%d")
        ruleset['vars'].append(('nodes.'+f, val))
    return {'osvc_node':ruleset}

def comp_get_rulesets_fset_ids(rset_ids=None, node_id=None, svc_id=None):
    if rset_ids is None:
        q = db.comp_rulesets_filtersets.ruleset_id>0
    else:
        q = db.comp_rulesets_filtersets.ruleset_id.belongs(rset_ids)

    q &= db.comp_rulesets.id == db.comp_rulesets_filtersets.ruleset_id
    q &= db.comp_rulesets_filtersets.fset_id == db.gen_filtersets.id

    if node_id is None:
        raise

    q &= db.comp_rulesets.id == db.comp_rulesets_chains.tail_rset_id

    l = {}
    g = db.comp_rulesets_filtersets.fset_id|db.comp_rulesets.id
    rows = db(q).select(db.comp_rulesets_filtersets.fset_id,
                        db.gen_filtersets.fset_name,
                        db.comp_rulesets.id,
                        groupby=g, cacheable=True)

    fset_ids = [r.comp_rulesets_filtersets.fset_id for r in rows]

    if svc_id == "":
        q = db.v_gen_filtersets.fset_id.belongs(fset_ids)
        q &= db.v_gen_filtersets.f_table.belongs(['services', 'svcmon'])
        f_rows = db(q).select(db.v_gen_filtersets.fset_id,
                              groupby=db.v_gen_filtersets.fset_id, cacheable=True)
        fsets_with_svc_tables = [r.fset_id for r in f_rows]

    for row in rows:
        if svc_id == "" and row.comp_rulesets_filtersets.fset_id in fsets_with_svc_tables:
            # for node compliance, discard fsets services related
            continue

        t = (row.comp_rulesets_filtersets.fset_id,
             row.gen_filtersets.fset_name)
        if t not in l:
            l[t] = [row.comp_rulesets.id]
        else:
            l[t] += [row.comp_rulesets.id]
    return l

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

def comp_ruleset_vars(ruleset_id, qr=None, matching_fsets=[],
                      rset_relations=None, rset_names=None,
                      via_moduleset=False, var_class=False):
    if qr is None:
        f = 'explicit attachment'
    else:
        f = comp_format_filter(qr)

    if via_moduleset:
        f += ' via moduleset'

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
      db.comp_rulesets_variables.var_class,
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
        if var_class:
            d['vars'].append((row.var_name,
                              row.var_value,
                              row.var_class))
        else:
            d['vars'].append((row.var_name,
                              row.var_value))
    return {ruleset_name: d}

def ruleset_add_var(d, rset_name, var, val):
    d[rset_name]['vars'].append((var, val))
    return d

@service.xmlrpc
def comp_get_ruleset_md5(rset_md5, auth):
    return rpc_comp_get_ruleset_md5(rset_md5, auth)

@auth_uuid
def rpc_comp_get_ruleset_md5(rset_md5, auth):
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

def svc_team_responsible_id(svc_id):
    q = db.services.svc_id == svc_id
    q &= db.services.svc_app == db.apps.app
    q &= db.apps.id == db.apps_responsibles.app_id
    q &= db.apps_responsibles.group_id == db.auth_group.id
    rows = db(q).select(db.auth_group.id, groupby=db.auth_group.id,
                        cacheable=True)
    return map(lambda x: x['id'], rows)

def node_team_responsible_id(node_id):
    q = db.nodes.node_id == node_id
    q &= db.nodes.team_responsible == db.auth_group.role
    rows = db(q).select(db.auth_group.id, cacheable=True)
    if len(rows) != 1:
        return None
    return rows[0].id

@service.xmlrpc
def comp_get_ruleset(nodename, auth):
    return rpc_comp_get_ruleset(auth)

@auth_uuid
def rpc_comp_get_ruleset(auth):
    node_id = auth_to_node_id(auth)
    return _comp_get_ruleset(node_id)

@service.xmlrpc
def comp_get_svc_ruleset(svcname, auth):
    return rpc_comp_get_svc_ruleset(svcname, auth)

@auth_uuid
def rpc_comp_get_svc_ruleset(svcname, auth):
    node_id = auth_to_node_id(auth)
    svc_id = node_svc_id(node_id, svcname)
    ruleset = _comp_get_svc_ruleset(svc_id, node_id)
    return ruleset

def comp_contextual_rulesets(node_id, svc_id=None, slave=False,
                             matching_fsets=None, fset_ids=None,
                             rset_relations=None, rset_names=None,
                             modulesets=[], var_class=False):
    ruleset = {}

    q = db.comp_rulesets.ruleset_public == True
    rows = db(q).select(db.comp_rulesets.id, cacheable=True)
    public_rsets = [r.id for r in rows]

    # attached to the node through modulesets
    if svc_id is not None:
        modset_ids = _comp_get_svc_moduleset_ids_with_children(svc_id, slave=slave,
                                                               modulesets=modulesets)
    elif node_id is not None:
        modset_ids = _comp_get_moduleset_ids_with_children(node_id,
                                                           modulesets=modulesets)
    q = db.comp_moduleset_ruleset.modset_id.belongs(modset_ids)
    q &= db.comp_moduleset_ruleset.ruleset_id == db.comp_rulesets.id
    q &= db.comp_rulesets.ruleset_type == "contextual"
    rows = db(q).select(db.comp_moduleset_ruleset.ruleset_id)
    rset_ids_via_modset = set([r.ruleset_id for r in rows])

    for (fset_id, fset_name), rset_ids in fset_ids.items():
        if fset_id not in matching_fsets:
            continue
        for rset_id in rset_ids:
            if rset_id not in public_rsets and rset_id not in rset_ids_via_modset:
                continue
            if rset_id not in public_rsets and rset_id in rset_ids_via_modset:
                comment = " (matching non-public contextual ruleset shown via moduleset)"
            else:
                comment = ""
            ruleset.update(comp_ruleset_vars(rset_id, qr=fset_name+comment,
                                             matching_fsets=matching_fsets,
                                             rset_relations=rset_relations,
                                             rset_names=rset_names,
                                             var_class=var_class))
    return ruleset

def _comp_get_svc_ruleset(svc_id, node_id, slave=None, modulesets=[], var_class=False):
    if slave is None:
        slave = comp_slave(svc_id, node_id)

    rset_relations = get_rset_relations()
    rset_names = get_rset_names()

    # initialize ruleset with service variables
    ruleset = comp_get_service_ruleset(svc_id)

    # initialize ruleset with asset variables
    ruleset.update(comp_get_node_ruleset(node_id))

    # initialize ruleset with svcmon variables
    ruleset.update(comp_get_svcmon_ruleset(svc_id, node_id))

    # add contextual rulesets variables
    l = comp_get_rulesets_fset_ids(svc_id=svc_id, node_id=node_id)
    matching_fsets = comp_get_matching_fset_ids(fset_ids=l, node_id=node_id, svc_id=svc_id, slave=slave)
    ruleset.update(comp_contextual_rulesets(node_id=node_id,
                                            svc_id=svc_id,
                                            slave=slave,
                                            matching_fsets=matching_fsets,
                                            fset_ids=l,
                                            rset_relations=rset_relations,
                                            rset_names=rset_names,
                                            modulesets=modulesets,
                                            var_class=var_class))

    # add explicit rulesets variables
    rset_ids, rset_ids_via_modset = _comp_get_explicit_svc_ruleset_ids(svc_id, slave=slave, modulesets=modulesets)
    for rset_id in rset_ids:
        ruleset.update(comp_ruleset_vars(rset_id,
                                         matching_fsets=matching_fsets,
                                         rset_relations=rset_relations,
                                         rset_names=rset_names,
                                         var_class=var_class))
    for rset_id in rset_ids_via_modset:
        ruleset.update(comp_ruleset_vars(rset_id,
                                         matching_fsets=matching_fsets,
                                         rset_relations=rset_relations,
                                         rset_names=rset_names,
                                         via_moduleset=True,
                                         var_class=var_class))

    insert_run_rset(ruleset)
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
        db.comp_run_ruleset.insert(rset_md5=rset_md5, rset=s, date=request.now)
        table_modified("comp_run_ruleset")
    except:
        q = db.comp_run_ruleset.rest_md5 == rset_md5
        db(q).update(date=request.now)
        table_modified("comp_run_ruleset")
    rset = {'name': 'osvc_collector',
            'filter': '',
            'vars': [('ruleset_md5', rset_md5)]}
    return ruleset.update({'osvc_collector': rset})

def _comp_get_explicit_svc_ruleset_ids(svc_id, slave=False, modulesets=[]):
    # attached to the node directly
    q = db.comp_rulesets_services.svc_id == svc_id
    q &= db.comp_rulesets_services.slave == slave
    rows = db(q).select(db.comp_rulesets_services.ruleset_id, cacheable=True)
    rset_ids = [r.ruleset_id for r in rows]

    # attached to the node through modulesets
    modset_ids = _comp_get_svc_moduleset_ids_with_children(svc_id, slave=slave,
                                                           modulesets=modulesets)
    q = db.comp_moduleset_ruleset.modset_id.belongs(modset_ids)
    q &= db.comp_moduleset_ruleset.ruleset_id == db.comp_rulesets.id
    q &= db.comp_rulesets.ruleset_type == "explicit"
    rows = db(q).select(db.comp_moduleset_ruleset.ruleset_id)
    rset_ids_via_modset = list(set([r.ruleset_id for r in rows]) - set(rset_ids))

    return rset_ids, rset_ids_via_modset

def _comp_get_explicit_ruleset_ids(node_id, modulesets=[]):
    # attached to the node directly
    q = db.comp_rulesets_nodes.node_id == node_id
    rows = db(q).select(db.comp_rulesets_nodes.ruleset_id,
                        orderby=db.comp_rulesets_nodes.ruleset_id,
                        cacheable=True)
    rset_ids = [r.ruleset_id for r in rows]

    # attached to the node through modulesets
    modset_ids = _comp_get_moduleset_ids_with_children(node_id, modulesets)
    q = db.comp_moduleset_ruleset.modset_id.belongs(modset_ids)
    q &= db.comp_moduleset_ruleset.ruleset_id == db.comp_rulesets.id
    q &= db.comp_rulesets.ruleset_type == "explicit"
    rows = db(q).select(db.comp_moduleset_ruleset.ruleset_id)
    rset_ids_via_modset = list(set([r.ruleset_id for r in rows]) - set(rset_ids))

    return rset_ids, rset_ids_via_modset

def _comp_get_ruleset(node_id, modulesets=[], var_class=False):
    # initialize ruleset with asset variables
    ruleset = comp_get_node_ruleset(node_id)

    rset_relations = get_rset_relations()
    rset_names = get_rset_names()

    # add contextual rulesets variables
    l = comp_get_rulesets_fset_ids(node_id=node_id)
    matching_fsets = comp_get_matching_fset_ids(fset_ids=l, node_id=node_id)
    ruleset.update(comp_contextual_rulesets(node_id=node_id,
                                            matching_fsets=matching_fsets,
                                            fset_ids=l,
                                            rset_relations=rset_relations,
                                            rset_names=rset_names,
                                            modulesets=modulesets,
                                            var_class=var_class))

    # add explicit rulesets variables
    rset_ids, rset_ids_via_modset = _comp_get_explicit_ruleset_ids(node_id, modulesets=modulesets)
    for rset_id in rset_ids:
        ruleset.update(comp_ruleset_vars(rset_id,
                                         matching_fsets=matching_fsets,
                                         rset_relations=rset_relations,
                                         rset_names=rset_names,
                                         var_class=var_class))
    for rset_id in rset_ids_via_modset:
        ruleset.update(comp_ruleset_vars(rset_id,
                                         matching_fsets=matching_fsets,
                                         rset_relations=rset_relations,
                                         rset_names=rset_names,
                                         via_moduleset=True,
                                         var_class=var_class))

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
              _class="icon right16",
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
    svc_ids = request.vars.node.split(',')
    l = []
    compdiff_svc = show_services_compdiff_svc(svc_ids)
    compdiff_svc_encap = show_services_compdiff_svc(svc_ids,encap=True)
    compdiff = show_services_compdiff(svc_ids)
    compdiff_encap = show_services_compdiff(svc_ids, encap=True)

    moddiff_svc = show_services_moddiff_svc(svc_ids)
    moddiff_svc_encap = show_services_moddiff_svc(svc_ids, encap=True)
    moddiff = show_services_moddiff(svc_ids)
    moddiff_encap = show_services_moddiff(svc_ids, encap=True)

    rsetdiff_svc = show_services_rsetdiff_svc(svc_ids)
    rsetdiff_svc_encap = show_services_rsetdiff_svc(svc_ids, encap=True)
    rsetdiff = show_services_rsetdiff(svc_ids)
    rsetdiff_encap = show_services_rsetdiff(svc_ids, encap=True)

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

def show_diff(svc_id):
    l = []
    compdiff = show_compdiff(svc_id)
    compdiff_encap = show_compdiff(svc_id, encap=True)
    moddiff = show_moddiff(svc_id)
    moddiff_encap = show_moddiff(svc_id, encap=True)
    rsetdiff = show_rsetdiff(svc_id)
    rsetdiff_encap = show_rsetdiff(svc_id, encap=True)

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

@service.xmlrpc
def register_node(node):
    """ placeholder to signal the registration support
    """
    pass


#
# Dashboard alerts
#
def cron_dash_comp():
    cron_dash_moddiff()
    cron_dash_rsetdiff()

def show_nodes_compdiff(node_ids):
    node_ids = list(set(node_ids))
    q = db.nodes.node_id.belongs(node_ids)
    rows = db(q).select(db.nodes.nodename, orderby=db.nodes.nodename)
    nodes = [r.nodename for r in rows]
    n = len(nodes)

    if n < 2:
        return

    sql = """select t.* from (
               select
                 count(distinct cs.node_id) as c,
                 cs.run_module,
                 n.nodename,
                 cs.run_status
               from
                 comp_status cs,
                 nodes n
               where
                 cs.node_id = n.node_id and
                 cs.node_id in (%(node_ids)s)
               group by
                 cs.run_module,
                 cs.run_status
              ) as t
              where
                t.c!=%(n)s
              order by
                t.run_module,
                t.nodename,
                t.run_status
              """%dict(node_ids=','.join(map(lambda x: repr(x), node_ids)), n=n)

    _rows = db.executesql(sql)
    if len(_rows) == 0:
        return

    mods = [r[1] for r in _rows]

    sql = """select
               n.nodename,
               cs.run_module,
               cs.run_status,
               cs.run_log,
               cs.run_date,
               cs.node_id
             from
               comp_status cs,
               nodes n
             where
               cs.node_id = n.node_id and
               cs.run_module in (%(mods)s) and
               cs.node_id in (%(node_ids)s)
             order by
               cs.run_module,
               n.nodename
         """%dict(node_ids=','.join(map(lambda x: repr(x), node_ids)), mods=','.join(map(lambda x: repr(str(x)), mods)))
    _rows = db.executesql(sql)

    if len(_rows) == 0:
        return

    return _show_compdiff(nodes, n, _rows)

def show_services_compdiff_svc(svc_ids, encap=False):
    svc_ids = list(set(svc_ids))
    svc_ids.sort()
    n = len(svc_ids)

    if n < 2:
        return

    if encap:
        sql = """select
                   concat(s.svcname, '@', m.mon_vmname)
                 from svcmon m, services s
                 where
                   m.svc_id = s.svc_id and
                   m.mon_vmname is not null and
                   m.mon_vmname != "" and
                   m.svc_id in (%(svc_ids)s)
                 group by
                   m.svc_id, m.mon_vmname
              """ % dict(svc_ids=','.join(map(lambda x: repr(x), svc_ids)))
    else:
        sql = """select
                   concat(s.svcname, '@', n.nodename)
                 from svcmon m, nodes n, services s
                 where
                   m.node_id = n.node_id and
                   m.svc_id = s.svc_id and
                   m.svc_id in (%(svc_ids)s)
                 group by
                   m.svc_id, m.node_id
              """ % dict(svc_ids=','.join(map(lambda x: repr(x), svc_ids)))

    _rows = db.executesql(sql)
    objs = list(set([r[0] for r in _rows]))
    n = len(objs)

    if n < 2:
        return

    sql = """select t.* from (
               select
                 count(distinct u.obj) as c,
                 u.run_module,
                 u.svc_id,
                 u.run_status
               from (
                 select
                   concat(cs.svc_id, '@', n.nodename) as obj,
                   cs.run_module,
                   cs.svc_id,
                   cs.run_status
                 from comp_status cs, nodes n
                 where
                   cs.node_id = n.node_id and
                   concat(cs.svc_id, '@', cs.node_id) in (%(objs)s)
               ) u
               group by
                 u.run_module,
                 u.run_status
              ) as t
              where
                t.c!=%(n)s
              order by
                t.run_module,
                t.svc_id,
                t.run_status
              """%dict(objs=','.join(map(lambda x: repr(str(x)), objs)), n=n)

    _rows = db.executesql(sql)
    if len(_rows) == 0:
        return

    mods = [r[1] for r in _rows]

    sql = """select
               concat(s.svcname, '@', n.nodename),
               cs.run_module,
               cs.run_status,
               cs.run_log,
               cs.run_date,
               cs.node_id
             from
               comp_status cs, nodes n, services s
             where
               cs.node_id = n.node_id and
               cs.svc_id = s.svc_id and
               cs.run_module in (%(mods)s) and
               concat(cs.svc_id, '@', cs.node_id) in (%(objs)s)
             order by
               cs.run_module,
               cs.svc_id,
               n.nodename
         """%dict(objs=','.join(map(lambda x: repr(str(x)), objs)), mods=','.join(map(lambda x: repr(str(x)), mods)))
    _rows = db.executesql(sql)

    if len(_rows) == 0:
        return

    return _show_compdiff(objs, n, _rows, "Service@Node")

def show_services_compdiff(svc_ids, encap=False):
    q = db.svcmon.svc_id.belongs(svc_ids)
    q = q_filter(q, svc_field=db.svcmon.svc_id)
    l = db.nodes.on(db.svcmon.mon_vmname==db.nodes.node_id)
    rows = db(q).select(left=l, cacheable=True)
    if encap:
        node_ids = [r.nodes.node_id for r in rows if r.nodes.node_id is not None]
    else:
        node_ids = [r.svcmon.node_id for r in rows]
    node_ids = list(set(node_ids))
    node_ids.sort()
    n = len(node_ids)

    if n < 2:
        return

    sql = """select t.* from (
               select
                 count(distinct cs.node_id) as c,
                 cs.run_module,
                 cs.node_id,
                 cs.run_status
               from
                 comp_status cs
               where
                 cs.node_id in (%(node_ids)s) and
                 (cs.svc_id = "" or cs.svc_id is NULL)
               group by
                 cs.run_module,
                 cs.run_status
              ) as t
              where
                t.c!=%(n)s
              order by
                t.run_module,
                t.node_id,
                t.run_status
              """%dict(node_ids=','.join(map(repr, node_ids)), n=n)

    _rows = db.executesql(sql)
    if len(_rows) == 0:
        return

    mods = [r[1] for r in _rows]

    sql = """select
               n.nodename,
               cs.run_module,
               cs.run_status,
               cs.run_log,
               cs.run_date,
               cs.node_id
             from
               comp_status cs,
               svcmon m,
               nodes n
             where
               cs.run_module in (%(mods)s) and
               m.node_id=cs.node_id and
               m.node_id=n.node_id and
               m.node_id in (%(node_ids)s) and
               (cs.svc_id = "" or cs.svc_id is NULL)
             order by
               cs.run_module,
               n.nodename
         """%dict(node_ids=','.join(map(lambda x: repr(x), node_ids)), mods=','.join(map(lambda x: repr(str(x)), mods)))
    _rows = db.executesql(sql)

    if len(_rows) == 0:
        return

    return _show_compdiff(node_ids, n, _rows)

def show_compdiff(svc_id, encap=False):
    q = db.svcmon.svc_id==svc_id
    q = q_filter(q, svc_field=db.svcmon.svc_id)
    l = db.nodes.on(db.svcmon.mon_vmname==db.nodes.node_id)
    rows = db(q).select(left=l, cacheable=True)
    if encap:
        node_ids = [r.nodes.node_id for r in rows if r.nodes.node_id is not None]
    else:
        node_ids = [r.svcmon.node_id for r in rows]
    node_ids = list(set(node_ids))
    node_ids.sort()
    n = len(node_ids)

    if n < 2:
        return

    sql = """select t.* from (
               select
                 count(distinct cs.node_id) as c,
                 cs.run_module,
                 cs.node_id,
                 cs.run_status
               from
                 comp_status cs
               where
                 (cs.node_id="" or cs.svc_id="") and
                 cs.svc_id="%(svc_id)s" and
                 cs.node_id in (%(node_ids)s)
               group by
                 cs.run_module,
                 cs.run_status
              ) as t
              where
                t.c!=%(n)s
              order by
                t.run_module,
                t.node_id,
                t.run_status
              """%dict(svc_id=svc_id, n=n, node_ids=','.join(map(repr, node_ids)))

    _rows = db.executesql(sql)
    if len(_rows) == 0:
        return

    mods = [r[1] for r in _rows]

    sql = """select
               n.nodename,
               cs.run_module,
               cs.run_status,
               cs.run_log,
               cs.run_date,
               cs.node_id
             from
               comp_status cs, nodes n
             where
               cs.node_id = n.node_id and
               (cs.svc_id="" or cs.svc_id="") and
               cs.run_module in (%(mods)s) and
               cs.svc_id="%(svc_id)s" and
               cs.node_id in (%(node_ids)s)
             order by
               cs.run_module,
               cs.node_id
         """%dict(svc_id=svc_id,
                  mods=','.join(map(lambda x: repr(str(x)), mods)),
                  node_ids=','.join(map(repr, node_ids)))
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
        data[module][row[5]] = row

    def fmt_header1():
        return TR(
                 TH("", _colspan=1),
                 TH(T(objtype), _colspan=n, _style="text-align:center"),
               )

    def fmt_header2():
        h = [TH(T("Module"))]
        for node in nodes:
            _node = get_node(node)
            if _node:
                nodename = _node.nodename
            else:
                nodename = node
            h.append(TH(
              nodename,
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
        return TABLE(lines, _class="table")

    return DIV(fmt_table(_rows))


def cron_dash_moddiff():
    q = db.services.updated > now - datetime.timedelta(days=2)
    svc_ids = [r.svc_id for r in db(q).select(db.services.svc_id, cacheable=True)]

    r = []
    for svc_id in svc_ids:
        r.append(update_dash_moddiff(svc_id))

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
               count(distinct nm.node_id) as n,
               group_concat(distinct nm.node_id) as nodes,
               ms.modset_name as modset
             from
               comp_node_moduleset nm,
               comp_moduleset ms
             where
               nm.node_id in (%(nodes)s) and
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

def show_services_moddiff_svc(svc_ids, encap=False):
    if encap:
        slave = 'T'
    else:
        slave = 'F'
    svc_ids = list(set(svc_ids))
    svc_ids.sort()
    n = len(svc_ids)

    if n < 2:
        return

    sql = """
            select t.* from
            (
             select
               count(distinct ms.svc_id) as n,
               group_concat(distinct ms.svc_id) as services,
               m.modset_name as modset
             from
               comp_modulesets_services ms,
               comp_moduleset m
             where
               ms.svc_id in (%(svc_ids)s) and
               ms.slave="%(slave)s" and
               ms.modset_id=m.id
             group by
               modset_name
             order by
               modset_name
            ) t
            where t.n != %(n)d
    """%dict(svc_ids=','.join(map(lambda x: repr(x), svc_ids)), n=n, slave=slave)
    _rows = db.executesql(sql)
    return _show_moddiff(svc_ids, n, _rows, "Services")

def show_services_moddiff(svc_ids, encap=False):
    q = db.svcmon.svc_id.belongs(svc_ids)
    q = q_filter(q, svc_field=db.svcmon.svc_id)
    l = db.nodes.on(db.svcmon.mon_vmname==db.nodes.node_id)
    rows = db(q).select(left=l, cacheable=True)
    if encap:
        node_ids = [r.nodes.node_id for r in rows if r.nodes.node_id is not None]
    else:
        node_ids = [r.svcmon.node_id for r in rows]
    node_ids = list(set(node_ids))
    node_ids.sort()
    n = len(node_ids)

    if n < 2:
        return

    sql = """
            select t.* from
            (
             select
               count(distinct nm.node_id) as n,
               group_concat(distinct nm.node_id) as nodes,
               ms.modset_name as modset
             from
               comp_node_moduleset nm,
               comp_moduleset ms
             where
               nm.node_id in (%(node_ids)s) and
               nm.modset_id=ms.id
             group by
               modset_name
             order by
               modset_name
            ) t
            where t.n != %(n)d
    """%dict(node_ids=','.join(map(repr, node_ids)), n=n)
    _rows = db.executesql(sql)
    return _show_moddiff(node_ids, n, _rows)

def show_moddiff(svc_id, encap=False):
    q = db.svcmon.svc_id==svc_id
    q = q_filter(q, svc_field=db.svcmon.svc_id)
    l = db.nodes.on(db.svcmon.mon_vmname==db.nodes.node_id)
    rows = db(q).select(left=l, cacheable=True)
    if encap:
        node_ids = [r.nodes.node_id for r in rows if r.nodes.node_id is not None]
    else:
        node_ids = [r.svcmon.node_id for r in rows]
    node_ids = list(set(node_ids))
    node_ids.sort()
    n = len(node_ids)

    if n < 2:
        return

    sql = """
            select t.* from
            (
             select
               count(distinct nm.node_id) as n,
               group_concat(distinct nm.node_id) as nodes,
               ms.modset_name as modset
             from
               comp_node_moduleset nm,
               comp_moduleset ms
             where
               nm.node_id in (%(node_ids)s) and
               nm.modset_id=ms.id
             group by
               modset_name
             order by
               modset_name
            ) t
            where t.n != %(n)d
    """%dict(node_ids=','.join(map(repr, node_ids)), n=n)
    _rows = db.executesql(sql)
    return _show_moddiff(node_ids, n, _rows)

def _show_moddiff(node_ids, n, _rows, objtype="Nodes"):

    if len(_rows) == 0:
        return

    def fmt_header1():
        return TR(
                 TH("", _colspan=1),
                 TH(T(objtype), _colspan=n, _style="text-align:center"),
               )

    def fmt_header2():
        h = [TH(T("Moduleset"))]
        for node_id in node_ids:
            if objtype == "Nodes":
                name = get_node(node_id).nodename
            else:
                name = get_svc(node_id).svcname
            h.append(TH(
              name,
              _style="text-align:center",
            ))
        return TR(h)

    def fmt_line(row, bg):
        h = [TD(row[2])]
        l = row[1].split(',')
        for node_id in node_ids:
            if node_id in l:
                h.append(TD(
                  IMG(_src=URL(r=request,c='static',f='images/attach16.png')),
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
        return TABLE(lines, _class="table")

    return DIV(fmt_table(_rows))

#
def cron_dash_rsetdiff():
    q = db.services.updated > now - datetime.timedelta(days=2)
    svc_ids = [r.svc_id for r in db(q).select(db.services.svc_id, cacheable=True)]

    r = []
    for svc_id in svc_ids:
        r.append(update_dash_rsetdiff(svc_id))

    return str(r)

def show_nodes_rsetdiff(nodes):
    nodes = list(set(nodes))
    q = db.nodes.nodename.belongs(nodes)
    q = q_filter(q, app_field=db.nodes.app)
    rows = db(q).select(db.nodes.nodename, orderby=db.nodes.nodename)
    nodes = [r.nodename for r in rows]
    n = len(nodes)

    if n < 2:
        return

    sql = """
            select t.* from
            (
             select
               count(distinct n.nodename) as n,
               group_concat(distinct n.nodename) as nodes,
               rs.ruleset_name as ruleset
             from
               nodes n,
               comp_rulesets_nodes rn,
               comp_rulesets rs
             where
               rn.nodename in (%(nodes)s) and
               rn.ruleset_id=rs.id and
               rn.node_id=nodes.node_id
             group by
               ruleset_name
             order by
               ruleset_name
            ) t
            where t.n != %(n)d
    """%dict(nodes=','.join(map(lambda x: repr(str(x)), nodes)), n=n)
    _rows = db.executesql(sql)

    return _show_rsetdiff(nodes, n, _rows)

def show_services_rsetdiff_svc(svc_ids, encap=False):
    svc_ids = list(set(svc_ids))
    svc_ids.sort()
    n = len(svc_ids)
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
               count(distinct rss.svc_id) as n,
               group_concat(distinct rss.svc_id) as services,
               rs.ruleset_name as ruleset
             from
               comp_rulesets_services rss,
               comp_rulesets rs
             where
               rss.svc_id in (%(svc_ids)s) and
               rss.slave="%(slave)s" and
               rss.ruleset_id=rs.id
             group by
               ruleset_name
             order by
               ruleset_name
            ) t
            where t.n != %(n)d
    """%dict(svc_ids=','.join(map(lambda x: repr(x), svc_ids)), n=n, slave=slave)
    _rows = db.executesql(sql)

    return _show_rsetdiff(svc_ids, n, _rows, "Services")

def show_services_rsetdiff(svc_ids, encap=False):
    q = db.svcmon.svc_id.belongs(svc_ids)
    q = q_filter(q, svc_field=db.svcmon.svc_id)
    l = db.nodes.on(db.svcmon.mon_vmname==db.nodes.node_id)
    rows = db(q).select(left=l, cacheable=True)
    if encap:
        node_ids = [r.nodes.node_id for r in rows if r.nodes.node_id is not None]
    else:
        node_ids = [r.svcmon.node_id for r in rows]
    node_ids = list(set(node_ids))
    node_ids.sort()
    n = len(node_ids)

    if n < 2:
        return

    sql = """
            select t.* from
            (
             select
               count(distinct rn.node_id) as n,
               group_concat(distinct rn.node_id) as nodes,
               rs.ruleset_name as ruleset
             from
               comp_rulesets_nodes rn,
               comp_rulesets rs
             where
               rn.node_id in (%(node_ids)s) and
               rn.ruleset_id=rs.id
             group by
               ruleset_name
             order by
               ruleset_name
            ) t
            where t.n != %(n)d
    """%dict(node_ids=','.join(map(repr, node_ids)), n=n)
    _rows = db.executesql(sql)

    return _show_rsetdiff(node_ids, n, _rows)


def show_rsetdiff(svc_id, encap=False):
    q = db.svcmon.svc_id==svc_id
    q = q_filter(q, svc_field=db.svcmon.svc_id)
    l = db.nodes.on(db.svcmon.mon_vmname==db.nodes.node_id)
    rows = db(q).select(left=l, cacheable=True)
    if encap:
        node_ids = [r.nodes.node_id for r in rows if r.nodes.node_id is not None]
    else:
        node_ids = [r.svcmon.node_id for r in rows]
    node_ids = list(set(node_ids))
    node_ids.sort()
    n = len(node_ids)

    if n < 2:
        return

    sql = """
            select t.* from
            (
             select
               count(distinct rn.node_id) as n,
               group_concat(distinct rn.node_id) as nodes,
               rs.ruleset_name as ruleset
             from
               comp_rulesets_nodes rn,
               comp_rulesets rs
             where
               rn.ruleset_id=rs.id and
               rn.node_id in (%(node_ids)s)
             group by
               ruleset_name
             order by
               ruleset_name
            ) t
            where t.n != %(n)d
    """%dict(node_ids=','.join(map(repr, node_ids)), n=n)
    _rows = db.executesql(sql)

    return _show_rsetdiff(node_ids, n, _rows)

def _show_rsetdiff(node_ids, n, _rows, objtype="Nodes"):
    if len(_rows) == 0:
        return

    def fmt_header1():
        return TR(
                 TH("", _colspan=1),
                 TH(T(objtype), _colspan=n, _style="text-align:center"),
               )

    def fmt_header2():
        h = [TH(T("Ruleset"))]
        for node_id in node_ids:
            if objtype=="Nodes":
                name = get_node(node_id).nodename
            else:
                name = get_svc(node_id).svcname
            h.append(TH(
              name,
              _style="text-align:center",
            ))
        return TR(h)

    def fmt_line(row, bg):
        h = [TD(row[2])]
        l = row[1].split(',')
        for node_id in node_ids:
            if node_id in l:
                h.append(TD(
                  IMG(_src=URL(r=request,c='static',f='images/attach16.png')),
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
        return TABLE(lines, _class="table")

    return DIV(fmt_table(_rows))

def json_tree_modulesets():
    modsets = {
     "id": "moduleset_head",
     'text': T('modulesets'),
     'type': "moduleset_head",
     'children': [],
    }
    modset_by_objid = {}

    modset_rset_relations = get_modset_rset_relations()
    modset_relations = get_modset_relations()

    group_names = {}
    q = db.auth_group.privilege == False
    rows = db(q).select(db.auth_group.id, db.auth_group.role, cacheable=True)
    for row in rows:
        group_names[row.id] = row.role

    q = db.comp_moduleset.id > 0
    if 'Manager' not in user_groups():
        q &= db.comp_moduleset.id == db.comp_moduleset_team_publication.modset_id
        q &= db.comp_moduleset_team_publication.group_id.belongs(user_group_ids())
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

    # caches
    groups_responsible = {}
    q = db.comp_moduleset_team_responsible.modset_id.belongs(visible_modset_ids)
    rows = db(q).select()
    for row in rows:
        if row.modset_id not in groups_responsible:
            groups_responsible[row.modset_id] = [row.group_id]
        else:
            groups_responsible[row.modset_id].append(row.group_id)

    groups_publication = {}
    q = db.comp_moduleset_team_publication.modset_id.belongs(visible_modset_ids)
    rows = db(q).select()
    for row in rows:
        if row.modset_id not in groups_publication:
            groups_publication[row.modset_id] = [row.group_id]
        else:
            groups_publication[row.modset_id].append(row.group_id)

    # modules
    q = db.comp_moduleset.id.belongs(visible_modset_ids)
    j = db.comp_moduleset.id == db.comp_moduleset_modules.modset_id
    l = db.comp_moduleset_modules.on(j)
    g = db.comp_moduleset.id|db.comp_moduleset_modules.id
    rows = db(q).select(db.comp_moduleset.id,
                        db.comp_moduleset.modset_name,
                        db.comp_moduleset_modules.id,
                        db.comp_moduleset_modules.modset_mod_name,
                        db.comp_moduleset_modules.autofix,
                        left=l,
                        orderby=(db.comp_moduleset.modset_name|db.comp_moduleset_modules.modset_mod_name),
                        groupby=g
           )

    modset_done = set([])
    _data = None

    # caches for _tree_rulesets_children()
    trc_rsets = _tree_get_rsets()
    trc_rsets_relations, trc_encap_rset_ids = _tree_get_rset_relations()
    trc_rsets_fsets = _tree_get_rsets_fsets_relations()
    trc_rsets_variables = _tree_get_rsets_variables_relations()
    trc_rsets_publications = _tree_get_rsets_publications_relations()
    trc_rsets_responsibles = _tree_get_rsets_responsibles_relations()

    for row in rows:
        if row.comp_moduleset.id not in modset_done:
            if _data is not None:
                _data['children'] += mods
                _data['children'] += rulesets
                obj_id = _data["li_attr"]["obj_id"]
                modset_by_objid[obj_id] = _data
                if obj_id in visible_head_modset_ids:
                    modsets['children'].append(_data)

            _data = {
              "id": "modset%d"%row.comp_moduleset.id,
              "type": "modset",
              "li_attr": {"obj_id": row.comp_moduleset.id},
              "text": row.comp_moduleset.modset_name,
              "children": []
            }
            mods_done = []
            mods = []
            rulesets = []
            if row.comp_moduleset.id in modset_rset_relations:
                rulesets += _tree_rulesets_children(modset_rset_relations[row.comp_moduleset.id],
                                                    id_prefix="modset%d_"%row.comp_moduleset.id,
                                                    hide_unpublished_and_encap_at_root_level=False,
                                                    rsets=trc_rsets,
                                                    rsets_relations=trc_rsets_relations,
                                                    encap_rset_ids=trc_encap_rset_ids,
                                                    rsets_fsets=trc_rsets_fsets,
                                                    rsets_variables=trc_rsets_variables,
                                                    rsets_publications=trc_rsets_publications,
                                                    rsets_responsibles=trc_rsets_responsibles)
            modset_done.add(row.comp_moduleset.id)

        if row.comp_moduleset_modules.id is not None and row.comp_moduleset_modules.id not in mods_done:
            if row.comp_moduleset_modules.autofix:
                rel = "module_autofix"
            else:
                rel = "module"
            __data = {
              "id": "mod%d"%row.comp_moduleset_modules.id,
              "type": rel,
              "li_attr": {"obj_id": row.comp_moduleset_modules.id},
              "text": row.comp_moduleset_modules.modset_mod_name,
            }
            mods.append(__data)
            mods_done.append(row.comp_moduleset_modules.id)

    if _data is not None:
        _data['children'] += mods
        _data['children'] += rulesets
        obj_id = _data["li_attr"]["obj_id"]
        modset_by_objid[obj_id] = _data
        if obj_id in visible_head_modset_ids:
            modsets['children'].append(_data)

    for i, modset in enumerate(modsets["children"]):
        modset_id = modset["li_attr"]["obj_id"]
        for group_id in groups_responsible.get(modset_id, []):
            __data = {
              "id": "grpresp%d"%group_id,
              "type": "group_resp",
              "li_attr": {"obj_id": group_id},
              "text": group_names.get(group_id, ""),
            }
            modsets["children"][i]["children"].append(__data)

        for group_id in groups_publication.get(modset_id, []):
            __data = {
              "id": "grppub%d"%group_id,
              "type": "group_pub",
              "li_attr": {"obj_id": group_id},
              "text": group_names.get(group_id, ""),
            }
            modsets["children"][i]["children"].append(__data)

    def recurse_modsets(head, id_prefix=""):
        if "li_attr" in head and "obj_id" in head["li_attr"]:
            obj_id = head["li_attr"]["obj_id"]
            if obj_id in modset_relations:
                for child_modset_id in modset_relations[obj_id]:
                    if child_modset_id in modset_by_objid:
                        _data = copy.deepcopy(modset_by_objid[child_modset_id])
                        _data["id"] = id_prefix + "modset" + str(_data["li_attr"]["obj_id"])
                        head['children'].append(_data)
        for i, child in enumerate(head['children']):
            if child["type"] != "modset":
                srel = child["type"]
                if srel.startswith("ruleset"):
                    srel = "rset"
                elif srel == "module":
                    srel = "mod"
                child["id"] = id_prefix+srel+str(child["li_attr"]["obj_id"])
                continue
            recurse_modsets(child, id_prefix=id_prefix+"modset"+str(child["li_attr"]["obj_id"])+'_')

    recurse_modsets(modsets)

    return modsets

def json_tree_groups():
    groups = {
     'id': 'grp_head',
     'text': T('groups'),
     'children': [],
     "type": "groups",
    }

    if request.vars.obj_filter is not None:
        q = _where(None, 'auth_group', request.vars.obj_filter, 'role')
        q = 'AND ' + str(q)
    else:
        q = ""

    q = q_filter(group_field=db.auth_group.role)
    q &= db.auth_group.privilege == False
    rows = db(q).select().as_list()
    h = {}
    for row in rows:
        _data = {
          "id": "grp%d"%row['id'],
          "text": row['role'],
          "type": "group",
          "li_attr": {"obj_id": row['id']},
        }
        groups['children'].append(_data)
    return groups

def json_tree_filtersets():
    fset_names = {}
    q = db.gen_filtersets.id > 0
    rows = db(q).select(cacheable=True)
    for row in rows:
        fset_names[row.id] = row.fset_name

    filtersets = {
     "id": "fset_head",
     'text': T('filtersets'),
     'type': "filterset_head",
     'children': [],
    }
    fset_data = comp_get_fset_data()

    if request.vars.obj_filter is not None:
        q &= _where(None, 'gen_filtersets', request.vars.obj_filter, 'fset_name')
        o = db.gen_filtersets.fset_name
        rows = db(q).select(db.gen_filtersets.id, orderby=o, cacheable=True)

    for fset_id in [r.id for r in rows]:
        _data = {
          "id": "fset%d"%fset_id,
          "type": "filterset",
          "li_attr": {"obj_id": fset_id},
          "text": fset_names[fset_id],
          "children": [],
        }
        filtersets['children'].append(_data)

    return filtersets

def json_tree_rulesets():
    rulesets = {
      "id": "rset_head",
      'text': T('rulesets'),
      'type': "ruleset_head",
      'children': [],
    }
    rulesets['children'] = _tree_rulesets_children(obj_filter=request.vars.obj_filter)
    return rulesets

def _tree_get_rset_relations():
    q = db.comp_rulesets_rulesets.id > 0
    rows = db(q).select(orderby=db.comp_rulesets_rulesets.parent_rset_id, cacheable=True)
    rsets_relations = {}
    encap_rset_ids = set([])
    for row in rows:
        if row.parent_rset_id not in rsets_relations:
            rsets_relations[row.parent_rset_id] = []
        rsets_relations[row.parent_rset_id].append(row.child_rset_id)
        encap_rset_ids.add(row.child_rset_id)
    return rsets_relations, encap_rset_ids

def _tree_get_rsets_fsets_relations():
    q = db.comp_rulesets_filtersets.id > 0
    q &= db.comp_rulesets_filtersets.fset_id == db.gen_filtersets.id
    rows = db(q).select(cacheable=True)
    rsets_fsets = {}
    for row in rows:
        if row.comp_rulesets_filtersets.ruleset_id not in rsets_fsets:
            rsets_fsets[row.comp_rulesets_filtersets.ruleset_id] = []
        rsets_fsets[row.comp_rulesets_filtersets.ruleset_id].append(row)
    return rsets_fsets

def _tree_get_rsets_variables_relations():
    q = db.comp_rulesets_variables.id > 0
    o = db.comp_rulesets_variables.ruleset_id | db.comp_rulesets_variables.var_name
    rows = db(q).select(orderby=o, cacheable=True)
    rsets_variables = {}
    for row in rows:
        if row.ruleset_id not in rsets_variables:
            rsets_variables[row.ruleset_id] = []
        rsets_variables[row.ruleset_id].append(row)
    return rsets_variables

def _tree_get_rsets_publications_relations():
    q = db.comp_ruleset_team_publication.id > 0
    q &= db.comp_ruleset_team_publication.group_id == db.auth_group.id
    rows = db(q).select(cacheable=True)
    rsets_publications = {}
    for row in rows:
        if row.comp_ruleset_team_publication.ruleset_id not in rsets_publications:
            rsets_publications[row.comp_ruleset_team_publication.ruleset_id] = []
        rsets_publications[row.comp_ruleset_team_publication.ruleset_id].append(row)
    return rsets_publications

def _tree_get_rsets_responsibles_relations():
    q = db.comp_ruleset_team_responsible.id > 0
    q &= db.comp_ruleset_team_responsible.group_id == db.auth_group.id
    rows = db(q).select(cacheable=True)
    rsets_responsibles = {}
    for row in rows:
        if row.comp_ruleset_team_responsible.ruleset_id not in rsets_responsibles:
            rsets_responsibles[row.comp_ruleset_team_responsible.ruleset_id] = []
        rsets_responsibles[row.comp_ruleset_team_responsible.ruleset_id].append(row)
    return rsets_responsibles

def _tree_get_rsets():
    q = db.comp_rulesets.id > 0
    q &= db.comp_rulesets.id == db.comp_ruleset_team_publication.ruleset_id
    rows = db(q).select(groupby=db.comp_rulesets.id, cacheable=True)
    rsets = {}
    for row in rows:
        rsets[row.comp_rulesets.id] = row.comp_rulesets
    return rsets

def _tree_rulesets_children(ruleset_ids=None, id_prefix="", obj_filter=None,
                            hide_unpublished_and_encap_at_root_level=True,
                            rsets=None,
                            rsets_relations=None, encap_rset_ids=None,
                            rsets_fsets=None, rsets_variables=None,
                            rsets_publications=None, rsets_responsibles=None):
    children = []

    if rsets is None:
        rsets = _tree_get_rsets()

    if rsets_relations is None or encap_rset_ids is None:
        rsets_relations, encap_rset_ids = _tree_get_rset_relations()

    if rsets_fsets is None:
        rsets_fsets = _tree_get_rsets_fsets_relations()

    if rsets_variables is None:
        rsets_variables = _tree_get_rsets_variables_relations()

    if rsets_publications is None:
        rsets_publications = _tree_get_rsets_publications_relations()

    if rsets_responsibles is None:
        rsets_responsibles = _tree_get_rsets_responsibles_relations()

    # main ruleset selection
    o = db.comp_rulesets.ruleset_name
    q = db.comp_rulesets.id > 0
    q &= db.comp_rulesets.id == db.comp_ruleset_team_publication.ruleset_id
    if ruleset_ids is not None:
        q &= db.comp_rulesets.id.belongs(ruleset_ids)
    if 'Manager' not in user_groups():
        q &= db.comp_ruleset_team_publication.group_id.belongs(user_group_ids())
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
        child_rsets = sorted(child_rsets, lambda x, y: cmp(x['text'], y['text']))
        fsets = []
        for v in rsets_fsets.get(rset.id, []):
            _parent_ids = parent_ids + ["fset%d"%v.comp_rulesets_filtersets.fset_id]
            vdata = {
             "id": id_prefix+"_".join(_parent_ids),
             "type": "filterset",
             "li_attr": {"obj_id": v.comp_rulesets_filtersets.fset_id, "class": "jstree-draggable"},
             "text": v.gen_filtersets.fset_name,
            }
            fsets.append(vdata)
        variables = []
        for v in rsets_variables.get(rset.id, []):
            _parent_ids = parent_ids + ["var%d"%v.id]
            vdata = {
             "id": id_prefix+"_".join(_parent_ids),
             "type": "variable",
             "li_attr": {"obj_id": v.id, "class": "jstree-draggable"},
             "text": v.var_name,
            }
            variables.append(vdata)
        groups_publication = []
        for v in rsets_publications.get(rset.id, []):
            _parent_ids = parent_ids + ["grppub%d"%v.comp_ruleset_team_publication.group_id]
            vdata = {
             "id": id_prefix+"_".join(_parent_ids),
             "type": "group_pub",
             "li_attr": {"obj_id": v.comp_ruleset_team_publication.group_id, "class": "jstree-draggable"},
             "text": v.auth_group.role,
            }
            groups_publication.append(vdata)
        groups_responsible = []
        for v in rsets_responsibles.get(rset.id, []):
            _parent_ids = parent_ids + ["grpresp%d"%v.comp_ruleset_team_responsible.group_id]
            vdata = {
             "id": id_prefix+"_".join(_parent_ids),
             "type": "group_resp",
             "li_attr": {"obj_id": v.comp_ruleset_team_responsible.group_id, "class": "jstree-draggable"},
             "text": v.auth_group.role,
            }
            groups_responsible.append(vdata)
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
          "id": id_prefix+"_".join(parent_ids),
          "type": rel,
          "li_attr": {"obj_id": rset.id, "rset_type": rset.ruleset_type, "class": "jstree-draggable,jstree-drop"},
          "text": rset.ruleset_name,
          "children": groups_publication+groups_responsible+fsets+variables+child_rsets,
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

    js = """ $.when(osvc.app_started).then(function(){designer("designer", %(options)s)}) """ % dict(
      options = str({
        "search": request.vars.obj_filter if request.vars.obj_filter else "",
        "search2": request.vars.obj_filter2 if request.vars.obj_filter2 else "",
        "var_class_names": var_class_names,
      }),
    )

    d = DIV(
      SCRIPT(js),
      _id="designer",
    )
    return dict(table=d)

def comp_admin_load():
    return comp_admin()["table"]

@service.json
def json_tree_action():
    action = request.vars.operation
    if action == "rename":
        return json_tree_action_rename()
    elif action == "import":
        return json_tree_action_import()
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
        elif (request.vars.obj_type == "group" or request.vars.obj_type == "group_pub") and \
           request.vars.dst_type.startswith("ruleset"):
            return json_tree_action_move_group_to_rset(request.vars.obj_id,
                                                       request.vars.dst_id,
                                                       gtype="publication")
        elif request.vars.obj_type == "group_resp" and \
           request.vars.dst_type.startswith("ruleset"):
            return json_tree_action_move_group_to_rset(request.vars.obj_id,
                                                       request.vars.dst_id,
                                                       gtype="responsible")
        elif (request.vars.obj_type == "group" or request.vars.obj_type == "group_pub") and \
           request.vars.dst_type == "modset":
            return json_tree_action_move_group_to_modset(request.vars.obj_id,
                                                         request.vars.dst_id,
                                                         gtype="publication")
        elif request.vars.obj_type == "group_resp" and \
           request.vars.dst_type == "modset":
            return json_tree_action_move_group_to_modset(request.vars.obj_id,
                                                         request.vars.dst_id,
                                                         gtype="responsible")
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
    elif action == "set_modset_group_responsible":
        return json_tree_action_set_modset_group_responsible(request.vars.obj_id,
                                                             request.vars.parent_obj_id)
    elif action == "set_modset_group_publication":
        return json_tree_action_set_modset_group_publication(request.vars.obj_id,
                                                             request.vars.parent_obj_id)
    elif action == "set_rset_group_responsible":
        return json_tree_action_set_rset_group_responsible(request.vars.obj_id,
                                                           request.vars.parent_obj_id)
    elif action == "set_rset_group_publication":
        return json_tree_action_set_rset_group_publication(request.vars.obj_id,
                                                           request.vars.parent_obj_id)
    elif action == "set_public":
        return json_tree_action_set_public(request.vars.obj_id,
                                           request.vars.publication)
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
    elif action == "detach_publication_group":
        return json_tree_action_detach_group(request.vars.obj_id,
                                             request.vars.parent_obj_id,
                                             request.vars.parent_obj_type,
                                             gtype="publication")
    elif action == "detach_responsible_group":
        return json_tree_action_detach_group(request.vars.obj_id,
                                             request.vars.parent_obj_id,
                                             request.vars.parent_obj_type,
                                             gtype="responsible")
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

@auth.requires_membership('CompManager')
def json_tree_action_import():
    val = request.vars.value
    try:
        data = json.loads(val)
    except:
        return T("Error: unable to parse JSON")

    l = lib_compliance_import(data)
    l =  map(lambda x: P(x), l)
    return DIV(l)

def json_tree_action_create_filterset(name):
    name = name.strip()
    try:
        obj_id = create_filterset(name)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return {"obj_id": obj_id}

def json_tree_action_create_moduleset(modset_name):
    modset_name = modset_name.strip()
    try:
        obj_id = create_moduleset(modset_name)
        if request.vars.parent_obj_id:
            if request.vars.parent_type == "modset":
                attach_moduleset_to_moduleset(obj_id, request.vars.parent_obj_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return {"obj_id": obj_id}

def json_tree_action_create_ruleset(rset_name):
    if request.vars.parent_obj_id:
        published = False
    else:
        published = True
    rset_name = rset_name.strip()
    try:
        obj_id = create_ruleset(rset_name, published=published)
        if request.vars.parent_obj_id:
            if request.vars.parent_type == "ruleset":
                attach_ruleset_to_ruleset(obj_id, request.vars.parent_obj_id)
            elif request.vars.parent_type == "modset":
                attach_ruleset_to_moduleset(obj_id, request.vars.parent_obj_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}

    return {"obj_id": obj_id}

def json_tree_action_create_module(modset_id, modset_mod_name):
    modset_mod_name = modset_mod_name.strip()
    try:
        obj_id = create_module(modset_id, modset_mod_name)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return {"obj_id": obj_id}

@service.json
def json_tree_action_create_variable(rset_id, var_name):
    var_name = var_name.strip()
    try:
        obj_id = create_variable(rset_id, var_name)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return {"obj_id": obj_id}

def json_tree_action_delete_module(mod_id):
    try:
        delete_module(mod_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_delete_variable(var_id):
    try:
        delete_variable(var_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
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
def json_tree_action_set_type(rset_id, rset_type):
    q = db.comp_rulesets.id == rset_id
    if 'Manager' not in user_groups():
        q &= db.comp_rulesets.id == db.comp_ruleset_team_responsible.ruleset_id
        q &= db.comp_ruleset_team_responsible.group_id.belongs(user_group_ids())
    rows = db(q).select(db.comp_rulesets.ALL, cacheable=True)
    v = rows.first()
    if v is None:
        return {"err": "ruleset does not exist or not owned by you"}
    if v.ruleset_type == rset_type:
        return {"err": "ruleset type is already '%(rset_type)s'"%dict(rset_type=rset_type)}
    q = db.comp_rulesets.id == rset_id
    db(q).update(ruleset_type=rset_type)

    if rset_type == "explicit":
        q = db.comp_rulesets_filtersets.ruleset_id == rset_id
        db(q).delete()
        table_modified("comp_rulesets_filtersets")

    db.commit()

    _log('compliance.ruleset.change',
         'set ruleset %(rset_name)s type from %(old)s to %(new)s',
         dict(rset_name=v.ruleset_name,
              old=v.ruleset_type,
              new=rset_type))
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
    table_modified("comp_moduleset_modules")
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
    try:
        obj_id = move_variable_to_ruleset(var_id, rset_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_copy_var_to_rset(var_id, rset_id):
    try:
        obj_id = copy_variable_to_ruleset(var_id, rset_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return {"obj_id": obj_id}

@auth.requires_membership('CompManager')
def json_tree_action_copy_rset_to_rset(rset_id, parent_rset_id, dst_rset_id):
    return json_tree_action_copy_or_move_rset_to_rset(rset_id, parent_rset_id, dst_rset_id, move=False)

@auth.requires_membership('CompManager')
def json_tree_action_move_rset_to_rset(rset_id, parent_rset_id, dst_rset_id):
    return json_tree_action_copy_or_move_rset_to_rset(rset_id, parent_rset_id, dst_rset_id, move=True)

@auth.requires_membership('CompManager')
def json_tree_action_copy_or_move_rset_to_rset(rset_id, parent_rset_id, dst_rset_id, move=False):
    try:
        attach_ruleset_to_ruleset(rset_id, dst_rset_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    if not move or parent_rset_id is None or parent_rset_id == dst_rset_id:
        return "0"
    try:
        detach_ruleset_from_ruleset(rset_id, parent_rset_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_detach_filterset(obj_id, parent_obj_id, parent_obj_type):
    if parent_obj_type.startswith("ruleset"):
        return json_tree_action_detach_filterset_from_rset(parent_obj_id)
    else:
        return {"err": "detach filterset not supported for this parent object type"}

@auth.requires_membership('CompManager')
def json_tree_action_detach_group(group_id, obj_id, parent_obj_type, gtype="responsible"):
    if parent_obj_type.startswith("ruleset"):
        return json_tree_action_detach_group_from_rset(group_id, obj_id, gtype=gtype)
    elif parent_obj_type == "modset":
        return json_tree_action_detach_group_from_modset(group_id, obj_id, gtype=gtype)
    else:
        return {"err": "detach group not supported for this parent object type"}

def json_tree_action_detach_group_from_modset(group_id, modset_id, gtype="responsible"):
    try:
        detach_group_from_moduleset(group_id, modset_id, gtype=gtype)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"

def json_tree_action_detach_group_from_rset(group_id, rset_id, gtype="responsible"):
    try:
        detach_group_from_ruleset(group_id, rset_id, gtype=gtype)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"

def json_tree_action_detach_moduleset_from_moduleset(child_modset_id, parent_modset_id):
    try:
        detach_moduleset_from_moduleset(child_modset_id, parent_modset_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"

def json_tree_action_detach_ruleset_from_moduleset(rset_id, modset_id):
    try:
        detach_ruleset_from_moduleset(rset_id, modset_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"

def json_tree_action_detach_ruleset(rset_id, parent_rset_id):
    try:
        detach_ruleset_from_ruleset(rset_id, parent_rset_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_copy_filter_to_fset(f_id, fset_id):
    try:
        attach_filter_to_filterset(f_id, fset_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_copy_fset_to_fset(fset_id, dst_fset_id):
    try:
        attach_filterset_to_filterset(fset_id, dst_fset_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"


def json_tree_action_move_fset_to_rset(fset_id, rset_id):
    try:
        attach_filterset_to_ruleset(fset_id, rset_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"

def json_tree_action_detach_filterset_from_rset(rset_id):
    try:
        detach_filterset_from_ruleset(rset_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"

def json_tree_action_move_group_to_modset(group_id, modset_id, gtype="publication"):
    try:
        attach_group_to_moduleset(group_id, modset_id, gtype=gtype)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"

def json_tree_action_copy_modset_to_modset(child_modset_id, parent_modset_id):
    try:
        attach_moduleset_to_moduleset(child_modset_id, parent_modset_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"

def json_tree_action_copy_rset_to_modset(rset_id, modset_id):
    try:
        attach_ruleset_to_moduleset(rset_id, modset_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_set_modset_group_responsible(group_id, modset_id):
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

    if w.role == "Everybody":
        return {"err": "Giving responsibility of a moduleset to Everybody is not allowed"}

    q = db.comp_moduleset_team_publication.modset_id == modset_id
    q &= db.comp_moduleset_team_publication.group_id == group_id
    db(q).delete()

    q = db.comp_moduleset_team_responsible.modset_id == modset_id
    q &= db.comp_moduleset_team_responsible.group_id == group_id
    n = db(q).count()
    if n > 0:
        return "0"
    db.comp_moduleset_team_responsible.insert(modset_id=modset_id,
                                              group_id=group_id)
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_set_modset_group_publication(group_id, modset_id):
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

    q = db.comp_moduleset_team_responsible.modset_id == modset_id
    q &= db.comp_moduleset_team_responsible.group_id == group_id
    db(q).delete()

    q = db.comp_moduleset_team_publication.modset_id == modset_id
    q &= db.comp_moduleset_team_publication.group_id == group_id
    n = db(q).count()
    if n > 0:
        return "0"
    db.comp_moduleset_team_publication.insert(modset_id=modset_id,
                                            group_id=group_id)
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_set_rset_group_responsible(group_id, rset_id):
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

    if w.role == "Everybody":
        return {"err": "Giving responsibility of a ruleset to Everybody is not allowed"}

    q = db.comp_ruleset_team_publication.ruleset_id == rset_id
    q &= db.comp_ruleset_team_publication.group_id == group_id
    db(q).delete()

    q = db.comp_ruleset_team_responsible.ruleset_id == rset_id
    q &= db.comp_ruleset_team_responsible.group_id == group_id
    n = db(q).count()
    if n > 0:
        return "0"
    db.comp_ruleset_team_responsible.insert(ruleset_id=rset_id,
                                            group_id=group_id)
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_set_rset_group_publication(group_id, rset_id):
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

    if w.role == "Everybody" and v.ruleset_type == "contextual":
        return {"err": "Publishing a contextual ruleset to Everybody is not allowed"}

    q = db.comp_ruleset_team_responsible.ruleset_id == rset_id
    q &= db.comp_ruleset_team_responsible.group_id == group_id
    db(q).delete()

    q = db.comp_ruleset_team_publication.ruleset_id == rset_id
    q &= db.comp_ruleset_team_publication.group_id == group_id
    n = db(q).count()
    if n > 0:
        return "0"
    db.comp_ruleset_team_publication.insert(ruleset_id=rset_id,
                                            group_id=group_id)
    return "0"

def json_tree_action_move_group_to_rset(group_id, rset_id, gtype="publication"):
    try:
        attach_group_to_ruleset(group_id, rset_id, gtype=gtype)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_clone_moduleset(modset_id):
    try:
        clone_moduleset(modset_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"

def json_tree_action_clone_ruleset(rset_id):
    try:
        clone_ruleset(rset_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"

def json_tree_action_delete_filterset(fset_id):
    try:
        delete_filterset(fset_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_delete_ruleset(rset_id):
    try:
        delete_ruleset(rset_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"

@auth.requires_membership('CompManager')
def json_tree_action_delete_moduleset(modset_id):
    try:
        delete_moduleset(modset_id)
    except CompError as e:
        return {"err": str(e)}
    except CompInfo as e:
        return {"info": str(e)}
    return "0"


