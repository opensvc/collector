class table_templates(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'tpl_name',
                     'tpl_command',
                     'tpl_comment',
                     'tpl_created',
                     'tpl_author',
                     'tpl_team_responsible']
        self.keys = ['id']
        self.force_cols = ['id', 'tpl_name']
        self.colprops = {
            'id': HtmlTableColumn(
                title = 'Id',
                field = 'id',
                display = False,
                table = 'v_prov_templates',
                img = 'key'
            ),
            'tpl_name': HtmlTableColumn(
                title = 'Name',
                field = 'tpl_name',
                display = True,
                table = 'v_prov_templates',
                img = 'prov',
                _class = 'prov_template',
            ),
            'tpl_command': HtmlTableColumn(
                title = 'Command',
                field = 'tpl_command',
                display = True,
                table = 'v_prov_templates',
                img = 'action16',
                _class='tpl_command',
            ),
            'tpl_comment': HtmlTableColumn(
                title = 'Comment',
                field = 'tpl_comment',
                display = True,
                table = 'v_prov_templates',
                img = 'edit16'
            ),
            'tpl_created': HtmlTableColumn(
                title = 'Created on',
                field = 'tpl_created',
                display = False,
                table = 'v_prov_templates',
                img = 'time16'
            ),
            'tpl_author': HtmlTableColumn(
                title = 'Author',
                field = 'tpl_author',
                display = False,
                table = 'v_prov_templates',
                img = 'guy16'
            ),
            'tpl_team_responsible': HtmlTableColumn(
                title = 'Team responsible',
                field = 'tpl_team_responsible',
                display = True,
                table = 'v_prov_templates',
                img = 'guys16',
                _class='groups',
            ),
        }
        self.ajax_col_values = 'ajax_prov_admin_col_values'
        self.events = ["prov_templates_change"]
        self.dataable = True
        self.wsable = True
        self.dbfilterable = False
        self.checkboxes = True

@auth.requires_login()
def ajax_prov_admin_col_values():
    table_id = request.vars.table_id
    t = table_templates(table_id, 'ajax_prov_admin')
    col = request.args[0]
    o = db.v_prov_templates[col]
    q = db.v_prov_templates.id > 0
    for f in t.cols:
        q = _where(q, 'v_prov_templates', t.filter_parse(f), f)
    t.object_list = db(q).select(o, orderby=o)
    return t.col_values_cloud_ungrouped(col)

@auth.requires_login()
def ajax_prov_admin():
    table_id = request.vars.table_id
    t = table_templates(table_id, 'ajax_prov_admin')

    o = db.v_prov_templates.tpl_name > 0
    q = db.v_prov_templates.id > 0
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_orderby = o
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).count()
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby)
        return t.table_lines_data(n)

@auth.requires_login()
def prov_admin():
    t = SCRIPT(
          """$.when(osvc.app_started).then(function(){ table_prov_templates("layout", %s) })""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def prov_admin_load():
    return prov_admin()["table"]

