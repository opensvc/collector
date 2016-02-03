#
# XMLRPC functions
#
@auth.requires_membership('ReplicationManager')
def call():
    session.forget()
    return service()

@service.xmlrpc
def replication_push(data, mirror):
    merge_data(data, mirror)

@service.xmlrpc
def serve_table_current_status(tables):
    return table_current_status(tables)

@service.xmlrpc
def serve_common(fullname, common):
    sql = "select distinct %s from %s" % (common, fullname)
    rows = db.executesql(sql)
    return [r[0] for r in rows]

@service.xmlrpc
def replication_pull(sql):
    rows = list(db.executesql(sql))
    for i, row in enumerate(rows):
        rows[i] = list(row)
        for j, t in enumerate(rows[i]):
            if type(t) == datetime.date:
                rows[i][j] = datetime.datetime(t.year, t.month, t.day)
    return rows

class table_replication_status(HtmlTable):
    def __init__(self, id=None, func=None, innerhtml=None):
        if id is None and 'tableid' in request.vars:
            id = request.vars.tableid
        HtmlTable.__init__(self, id, func, innerhtml)
        self.cols = ['mode',
                     'remote',
                     'table_schema',
                     'table_name',
                     'need_resync',
                     'current_cksum',
                     'last_cksum',
                     'table_updated']
        self.colprops = {
            'mode': HtmlTableColumn(
                     title='Mode',
                     field='mode',
                     img='net16',
                     display=True,
                    ),
            'remote': HtmlTableColumn(
                     title='Remote',
                     field='remote',
                     img='node16',
                     display=True,
                    ),
            'table_schema': HtmlTableColumn(
                     title='Database',
                     field='table_schema',
                     img='db16',
                     display=True,
                    ),
            'table_name': HtmlTableColumn(
                     title='Table',
                     field='table_name',
                     img='db16',
                     display=True,
                    ),
            'need_resync': HtmlTableColumn(
                     title='Need resync',
                     field='need_resync',
                     img='db16',
                     display=True,
                    ),
            'current_cksum': HtmlTableColumn(
                     title='Current csum',
                     field='current_cksum',
                     img='db16',
                     display=True,
                    ),
            'last_cksum': HtmlTableColumn(
                     title='Last csum',
                     field='last_cksum',
                     img='db16',
                     display=True,
                    ),
            'table_updated': HtmlTableColumn(
                     title='Updated',
                     field='table_updated',
                     img='time16',
                     display=True,
                    ),
        }

        self.dbfilterable = False
        self.filterable = False
        self.pageable = False
        self.checkboxes = True
        self.dataable = True

        self.ajax_col_values = 'ajax_replication_status_col_values'

    def line_id(self, o):
        if o is None:
            return ""
        return '+'.join((o.get('remote', ''),
                         o.get('table_schema', ''),
                         o.get('table_name', '')))

@auth.requires_login()
def ajax_replication_status():
    table_id = request.vars.table_id
    t = table_replication_status(table_id, 'ajax_replication_status')
    t.object_list = table_status()
    n = len(t.object_list)
    if len(request.args) == 1 and request.args[0] == 'csv':
        return t.csv()
    if len(request.args) == 1 and request.args[0] == 'commonality':
        return t.do_commonality()
    if len(request.args) == 1 and request.args[0] == 'data':
        t.setup_pager(n)
        limitby = (t.pager_start,t.pager_end)
        return t.table_lines_data(n, html=False)

@auth.requires_login()
def repl_admin():
    t = SCRIPT(
          """table_replication("layout", %s)""" % request_vars_to_table_options(),
        )
    return dict(table=t)

def test_resync_all():
    resync_all()
