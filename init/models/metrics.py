from applications.init.modules import timeseries

dbro_host = config_get('dbro_host', dbopensvc_host)
dbro_user = config_get('dbro_user', 'readonly')
dbro_password = config_get('dbro_password', 'readonly')

try:
    dbro = DAL('mysql://%s:%s@%s/opensvc' % (dbro_user, dbro_password, dbro_host))
except Exception as exc:
    db_error_handler(exc)

def replace_fset_sql(sql, fset_id=None):
    if fset_id is None:
        fset_id = user_fset_id()

    node_ids, svc_ids = filterset_encap_query_cached(fset_id)

    if len(svc_ids) == 0:
        svc_ids = "'magic1234567890'"
    else:
        svc_ids = ",".join(map(lambda x: str(repr(x)), svc_ids))

    if len(node_ids) == 0:
        node_ids = "'magic1234567890'"
    else:
        node_ids = ",".join(map(lambda x: repr(str(x)), node_ids))

    sql = sql.replace('%%fset_svc_ids%%', svc_ids)
    sql = sql.replace('%%fset_node_ids%%', node_ids)

    return sql

def _metrics_cron_fset(m, fset_id, verbose=False, instances_as_colums=False, kwargs=None):
    if kwargs is None:
        kwargs = {}

    sql = replace_fset_sql(m.metric_sql, fset_id)
    try:
         rows = dbro.executesql(sql, **kwargs)
    except Exception as e:
         print e, sql
         return
    now = datetime.datetime.now()

    if instances_as_colums:
        if len(rows) != 1:
            print "  skip: instances_as_colums mode, but %d lines in resultset" % len(rows)
            return
        row = rows[0]
        for instance, value in row.items():
            if verbose:
                print "  insert", instance, value, "fset_id:", fset_id
            path = timeseries.wsp_path("metrics", m.id, "fsets", fset_id, instance)
            timeseries.whisper_update(path, value, now, retentions=timeseries.daily_retentions)
        return

    for row in rows:
        if m.metric_col_instance_index is not None:
            instance = row[m.metric_col_instance_index]
            if verbose:
                print "  insert", instance, row[m.metric_col_value_index], "fset_id:", fset_id
        else:
            instance = None
            if verbose:
                print "  insert", row[m.metric_col_value_index], "fset_id:", fset_id

        path = timeseries.wsp_path("metrics", m.id, "fsets", fset_id, instance)
        timeseries.whisper_update(path, row[m.metric_col_value_index], now, retentions=timeseries.daily_retentions)

def _metrics_cron_fsets(m, verbose=False, instances_as_colums=False, kwargs=None):
    q = db.gen_filtersets.fset_stats == True
    rows = db(q).select(db.gen_filtersets.id)
    fset_ids = [r.id for r in rows]

    for fset_id in [0] + fset_ids:
        _metrics_cron_fset(m, fset_id, verbose=verbose, instances_as_colums=instances_as_colums, kwargs=kwargs)

def _metrics_cron(m, verbose=False):
    if (m.metric_col_instance_index and m.metric_col_instance_index < 0) or \
       (m.metric_col_value_index and m.metric_col_value_index < 0):
        instances_as_colums = True
        kwargs = {"as_dict": True}
    else:
        instances_as_colums = False
        kwargs = {}

    if "%%fset_svc_ids%%" in m.metric_sql or "%%fset_node_ids%%" in m.metric_sql:
        _metrics_cron_fsets(m, verbose=verbose, instances_as_colums=instances_as_colums, kwargs=kwargs)
        return

    rows = dbro.executesql(m.metric_sql, **kwargs)
    now = datetime.datetime.now()

    if instances_as_colums:
        if len(rows) != 1:
            print "  skip: instances_as_colums mode, but %d lines in resultset" % len(rows)
            return
        row = rows[0]
        for instance, value in row.items():
            if verbose:
                print "  insert", instance, value
            path = timeseries.wsp_path("metrics", m.id, "fsets", 0, instance)
            timeseries.whisper_update(path, value, now, retentions=timeseries.daily_retentions)
        return

    for row in rows:
        if m.metric_col_instance_index is not None:
            instance = row[m.metric_col_instance_index]
            if verbose:
                print "  insert", instance, row[m.metric_col_value_index]
        else:
            instance = None
            if verbose:
                print "  insert", row[m.metric_col_value_index]

        path = timeseries.wsp_path("metrics", m.id, "fsets", 0, instance)
        timeseries.whisper_update(path, row[m.metric_col_value_index], now, retentions=timeseries.daily_retentions)

def task_metrics(verbose=False):
    q = db.metrics.metric_historize == True
    rows = db(q).select()
    refresh_fset_cache()
    if verbose:
        print len(rows), "metrics to compute"
    for row in rows:
        if verbose:
            print "* metric:", row.metric_name
        try:
            _metrics_cron(row, verbose=verbose)
        except Exception as e:
            print e
            continue


