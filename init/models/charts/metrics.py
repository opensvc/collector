from applications.init.modules import config

if hasattr(config, 'dbopensvc'):
    dbopensvc = config.dbopensvc
else:
    dbopensvc = 'dbopensvc'

dbro = DAL('mysql://readonly:readonly@%s/opensvc' % dbopensvc)

def replace_fset_sql(sql, fset_id=None):
    if fset_id is None:
        fset_id = user_fset_id()

    nodenames, svcnames = filterset_encap_query_cached(fset_id)

    if len(svcnames) == 0:
        svcnames = "'magic1234567890'"
    else:
        svcnames = ",".join(map(lambda x: repr(str(x)), svcnames))

    if len(nodenames) == 0:
        nodenames = "'magic1234567890'"
    else:
        nodenames = ",".join(map(lambda x: repr(str(x)), nodenames))

    sql = sql.replace('%%fset_services%%', svcnames)
    sql = sql.replace('%%fset_nodenames%%', nodenames)

    return sql

def _metrics_cron_fset(m, fset_id):
    sql = replace_fset_sql(m.metric_sql, fset_id)
    try:
         rows = dbro.executesql(sql)
    except Exception as e:
         print e, sql
         return
    now = datetime.datetime.now()

    for row in rows:
        if m.metric_col_instance_index is not None:
            instance = row[m.metric_col_instance_index]
            print "  insert", instance, row[m.metric_col_value_index], "fset_id:", fset_id
        else:
            instance = None
            print "  insert", row[m.metric_col_value_index], "fset_id:", fset_id

        mid = db.metrics_log.insert(
               date=now,
               metric_id=m.id,
               fset_id=fset_id,
               instance=instance,
               value=row[m.metric_col_value_index],
              )

def _metrics_cron_fsets(m):
    q = db.gen_filtersets.id > 0
    rows = db(q).select(db.gen_filtersets.id)
    fset_ids = [r.id for r in rows]

    for fset_id in [0] + fset_ids:
        _metrics_cron_fset(m, fset_id)

def _metrics_cron(m):
    if "%%fset_services%%" in m.metric_sql or "%%fset_nodenames%%" in m.metric_sql:
        _metrics_cron_fsets(m)
        return

    rows = dbro.executesql(m.metric_sql)

    now = datetime.datetime.now()
    for row in rows:
        if m.metric_col_instance_index is not None:
            instance = row[m.metric_col_instance_index]
            print "  insert", instance, row[m.metric_col_value_index]
        else:
            instance = None
            print "  insert", row[m.metric_col_value_index]

        mid = db.metrics_log.insert(
               date=now,
               metric_id=m.id,
               instance=instance,
               value=row[m.metric_col_value_index],
              )

def task_metrics():
    q = db.metrics.id > 0
    rows = db(q).select()
    refresh_fset_cache()
    for row in rows:
        print "* metric:", row.metric_name
        try:
            _metrics_cron(row)
        except Exception as e:
            print e
            continue
    db.commit()


