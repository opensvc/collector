class table_templates(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'tpl_name',
                     'tpl_definition',
                     'tpl_comment',
                     'tpl_created',
                     'tpl_author',
                     'tpl_team_responsible',
                     'tpl_team_publication']
        self.colprops = {
            'id': HtmlTableColumn(
                field = 'id',
                table = 'v_prov_templates',
            ),
            'tpl_name': HtmlTableColumn(
                field = 'tpl_name',
                table = 'v_prov_templates',
            ),
            'tpl_definition': HtmlTableColumn(
                field = 'tpl_definition',
                table = 'v_prov_templates',
            ),
            'tpl_comment': HtmlTableColumn(
                field = 'tpl_comment',
                table = 'v_prov_templates',
            ),
            'tpl_created': HtmlTableColumn(
                field = 'tpl_created',
                table = 'v_prov_templates',
            ),
            'tpl_author': HtmlTableColumn(
                field = 'tpl_author',
                table = 'v_prov_templates',
            ),
            'tpl_team_responsible': HtmlTableColumn(
                field = 'tpl_team_responsible',
                table = 'v_prov_templates',
            ),
            'tpl_team_publication': HtmlTableColumn(
                field = 'tpl_team_publication',
                table = 'v_prov_templates',
            ),
        }
        self.ajax_col_values = 'ajax_prov_admin_col_values'

@auth.requires_login()
def ajax_prov_admin_col_values():
    table_id = request.vars.table_id
    t = table_templates(table_id, 'ajax_prov_admin')
    col = request.args[0]
    o = db.v_prov_templates[col]
    q = db.v_prov_templates.id > 0
    for f in t.cols:
        q = _where(q, 'v_prov_templates', t.filter_parse(f), f)
    t.object_list = db(q).select(
        o,
        db.v_prov_templates.id.count(),
        orderby=~db.v_prov_templates.id.count(),
        groupby=o,
    )
    return t.col_values_cloud_grouped(col)

@auth.requires_login()
def ajax_prov_admin():
    table_id = request.vars.table_id
    t = table_templates(table_id, 'ajax_prov_admin')

    o = t.get_orderby(default=db.v_prov_templates.tpl_name)
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
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def prov_admin():
    t = SCRIPT(
          """table_prov_templates("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def prov_admin_load():
    return prov_admin()["table"]

