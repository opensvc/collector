class table_safe(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['id',
                     'uuid',
                     'safe_name',
                     'size',
                     'md5',
                     'safe_team_publication',
                     'safe_team_responsible',
                     'uploader',
                     'uploader_name',
                     'uploaded_from',
                     'uploaded_date',
                    ]
        self.colprops = {
          "id": HtmlTableColumn(
            table="v_safe",
            field="id"
          ),
          "safe_team_publication": HtmlTableColumn(
            table="v_safe",
            field="safe_team_publication"
          ),
          "safe_team_responsible": HtmlTableColumn(
            table="v_safe",
            field="safe_team_responsible"
          ),
          "uploader": HtmlTableColumn(
            table="v_safe",
            field="uploader"
          ),
          "uploader_name": HtmlTableColumn(
            table="v_safe",
            field="uploader_name"
          ),
          "uploaded_from": HtmlTableColumn(
            table="v_safe",
            field="uploaded_from"
          ),
          "uploaded_date": HtmlTableColumn(
            table="v_safe",
            field="uploaded_date"
          ),
          "safe_name": HtmlTableColumn(
            table="v_safe",
            field="safe_name"
          ),
          "size": HtmlTableColumn(
            table="v_safe",
            field="size"
          ),
          "uuid": HtmlTableColumn(
            table="v_safe",
            field="uuid"
          ),
          "md5": HtmlTableColumn(
            table="v_safe",
            field="md5"
          ),
        }
        self.ajax_col_values = 'ajax_safe_col_values'

@auth.requires_login()
def ajax_safe_col_values():
    table_id = request.vars.table_id
    t = table_safe(table_id, 'ajax_safe')
    col = request.args[0]
    o = db[t.colprops[col].table][col]
    g = db.v_safe.id
    q = db.v_safe.id > 0
    l = db.safe_team_publication.on(db.v_safe.id == db.safe_team_publication.file_id)
    if "Manager" not in user_groups():
        q &= db.safe_team_publication.group_id.belongs(user_group_ids())
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)
    t.object_list = db(q).select(o,
                                 db.v_safe.id.count(),
                                 orderby=~db.v_safe.id.count(),
                                 groupby=o,
                                 left=l)
    return t.col_values_cloud_grouped(col)

@auth.requires_login()
def ajax_safe():
    table_id = request.vars.table_id
    t = table_safe(table_id, 'ajax_safe')
    o = t.get_orderby(default=db.v_safe.safe_name)
    g = db.v_safe.id

    q = db.v_safe.id>0
    l = db.safe_team_publication.on(db.v_safe.id == db.safe_team_publication.file_id)
    if "Manager" not in user_groups():
        q &= db.safe_team_publication.group_id.belongs(user_group_ids())
    for f in t.cols:
        q = _where(q, t.colprops[f].table, t.filter_parse(f), f)

    if len(request.args) == 1 and request.args[0] == 'csv':
        t.csv_q = q
        t.csv_left = l
        t.csv_groupby = g
        t.csv_orderby = o
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        t.csv_q = q
        t.csv_left = l
        t.csv_groupby = g
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        n = db(q).select(db.v_safe.id.count()).first()._extra[db.v_safe.id.count()]
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        cols = t.get_visible_columns()
        t.object_list = db(q).select(*cols, orderby=o, limitby=limitby,
                                     groupby=g, left=l, cacheable=False)
        return t.table_lines_data(n, html=False)



@auth.requires_login()
def safe():
    t = SCRIPT(
          """table_safe("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def safe_load():
    return safe()["table"]

