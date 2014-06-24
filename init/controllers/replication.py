cf = local_import('replication_config', reload=True)

@auth.requires_membership('ReplicationManager')
def call():
    session.forget()
    return service()

@service.xmlrpc
def replication_test():
    return 1

#@auth.requires_membership('ReplicationManager')
@service.xmlrpc
def replication_push(data):
    max = 500
    for table, (vars, vals) in data.items():
        while len(vals) > max:
            generic_insert(table, vars, vals[:max])
            vals = vals[max:]
        generic_insert(table, vars, vals)

def get_push_remote_tables():
    tables = set([])
    push_data = cf.repl_config.get("push", [])
    if push_data is None or type(push_data) != list:
        return []

    for host in push_data:
        remote = host.get("remote")
        if remote is None:
            continue
        push_tables = host.get("tables")
        if push_tables is None:
            continue
        for t in push_tables:
            schema = t.get("schema", "opensvc")
            name = t.get("name")
            if name is None:
                continue
            tables.add(remote+"."+schema+"."+name)

    tables = list(tables)
    return tables

def get_push_tables():
    tables = set([])
    push_data = cf.repl_config.get("push", [])
    if push_data is None or type(push_data) != list:
        return []

    for host in push_data:
        push_tables = host.get("tables")
        if push_tables is None:
            continue
        for t in push_tables:
            schema = t.get("schema", "opensvc")
            name = t.get("name")
            if name is None:
                continue
            tables.add(schema+"."+name)

    tables = list(tables)
    return tables

def push_table_current_status(tables):
    tables = ','.join(map(lambda x: repr(x), tables))
    sql = """
     select
       table_schema,
       table_name,
       md5(concat(rows, '_', modified)) as current_cksum
     from
       information_schema.innodb_table_stats
     where
       concat(table_schema, ".", table_name) in (%(tables)s)
    """ % dict(tables=tables)

    rows = db.executesql(sql, as_dict=True)
    return rows

def push_table_last_status(tables):
    tables = ','.join(map(lambda x: repr(x), tables))
    sql = """
     select
       remote,
       mode,
       table_schema,
       table_name,
       table_cksum as last_cksum,
       table_updated
     from
       replication_status
     where
       concat(table_schema, ".", table_name) in (%(tables)s)
    """ % dict(tables=tables)
    rows = db.executesql(sql, as_dict=True)
    return rows

def push_table_status():
    tables = get_push_tables()
    last = push_table_last_status(tables)
    current = push_table_current_status(tables)

    d_current = {}
    for e in current:
        fullname = '.'.join((e['table_schema'], e['table_name']))
        d_current[fullname] = e

    d_last = {}
    for e in last:
        fullname = '.'.join((e['remote'], e['table_schema'], e['table_name']))
        d_last[fullname] = e

    data = {}
    for e in get_push_remote_tables():
        _data = {}
        fullname = e[e.index('.')+1:]
        if fullname in d_current:
            _data.update(d_current[fullname])
        else:
            continue

        if e in d_last:
            _data.update(d_last[e])
        else:
            _data.update({
             'remote': e.split(".")[0],
             'mode': 'push',
             'last_cksum': None,
             'table_updated': None,
            })

        if _data.get("current_cksum", "1") == _data.get("last_cksum", "2"):
            _data['need_resync'] = "F"
        else:
            _data['need_resync'] = "T"

        data[e] = _data

    return data

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
                     img='sync16',
                     display=True,
                    ),
            'remote': HtmlTableColumn(
                     title='Remote',
                     field='remote',
                     img='hw16',
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
                     img='action16',
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

        self.ajax_col_values = 'ajax_replication_status_col_values'

    def line_id(self, o):
        return '.'.join((o['remote'], o['table_schema'], o['table_name']))

@auth.requires_login()
def ajax_replication_status():
    t = table_replication_status('rs', 'ajax_replication_status')
    t.object_list = push_table_status()
    n = len(t.object_list)
    t.setup_pager(n)

    return t.html()

def get_creds(remote):
    push_data = cf.repl_config.get("push", []) + cf.repl_config.get("pull", [])
    for d in push_data:
        _remote = d.get('remote')
        if _remote != remote:
            continue
        return d.get('user'), d.get('password')
    return None, None

def rpc_push(remote, data):
    user, password = get_creds(remote)
    import xmlrpclib
    xmlrpclib.Marshaller.dispatch[type(0L)] = lambda _, v, w: w("<value><i8>%d</i8></value>" % v)
    p = xmlrpclib.ServerProxy("https://%s:%s@%s/init/replication/call/xmlrpc" %
                               (user, password, remote), allow_none=True)
    return p.replication_push(data)

def get_table_columns(schema, name):
    sql = """
      SELECT
        `COLUMN_NAME`
      FROM
        `INFORMATION_SCHEMA`.`COLUMNS`
      WHERE
        `TABLE_SCHEMA`='%s' AND
        `TABLE_NAME`='%s'
    """ % (schema, name)
    rows = db.executesql(sql)
    columns = [ r[0] for r in rows ]
    return columns

def rpc_push_all_table_to_all_remote():
    ts = push_table_status()
    remotes = list(set([ e['remote'] for e in ts.values() ]))

    for remote in remotes:
        for d in ts.values():
            data = {}

            if d.get('remote') != remote:
               continue

            fullname = ".".join((d['table_schema'], d['table_name']))
            rfullname = ".".join((d['remote'], fullname))

            need_resync = d.get('need_resync')
            if need_resync is not None and need_resync != 'T':
               print "skip resync %s" % rfullname
               continue

            columns = d.get('columns')
            if columns is None:
                columns = get_table_columns(d['table_schema'], d['table_name'])
            sql = """select * from %s""" % fullname
            rows = list(db.executesql(sql))
            print "resync %s (%d lines)" % (rfullname, len(rows))
            for i, row in enumerate(rows):
                rows[i] = list(row)

            """
            try:
                idx = columns.index('id')
                del columns[idx]
                for i, row in enumerate(rows):
                    del rows[i][idx]
            except Exception as e:
                return str(e)
            """

            data[fullname] = (columns, rows)
            print "data prepared. send."
            try:
                rpc_push(remote, data)
                print "sent. update replication status"
                update_last_push(d)
            except:
                raise

def update_last_push(d):
    import datetime
    vars = ["remote",
            "table_schema",
            "table_name",
            "table_cksum",
            "table_updated"]
    vals = [d["remote"],
            d["table_schema"],
            d["table_name"],
            d["current_cksum"],
            datetime.datetime.now()]
    generic_insert("replication_status", vars, vals)

@auth.requires_login()
def repl_admin():
    t = DIV(
          ajax_replication_status(),
          _id='rs',
        )
    #rpc_push_all_table_to_all_remote()
    return dict(table=t)

