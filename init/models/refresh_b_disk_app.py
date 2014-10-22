def queue_refresh_b_disk_app():
    q = db.scheduler_task.status.belongs(("QUEUED", "ASSIGNED"))
    q &= db.scheduler_task.function_name == "task_refresh_b_disk_app"
    n = db(q).count()
    if n > 2:
        print "skip: %d task(s) already queued" % n
        return
    scheduler.queue_task("task_refresh_b_disk_app", [], group_name="janitor")
    db.commit()
    print "queued at position %d" % (n+1)

def task_refresh_b_disk_app():
    from warnings import filterwarnings
    import MySQLdb
    filterwarnings('ignore', category = MySQLdb.Warning)
    sql = """
      select
        max(table_modified)>(select create_time from information_schema.tables where table_schema="opensvc" and table_name='b_disk_app') as need_update,
        max(table_modified) as last_parents_update,
        (select create_time from information_schema.tables where table_schema="opensvc" and table_name='b_disk_app') as last_update
      from
       table_modified
      where
       table_name in ('nodes', 'services', 'apps', 'svcdisks', 'diskinfo')
    """
    rows = db.executesql(sql)
    if rows[0][0] is not None and rows[0][0] != 1:
        return "skip " + str(rows)
    sql = """drop table if exists b_disk_app_old"""
    db.executesql(sql)
    sql = """drop table if exists b_disk_app_tmp"""
    db.executesql(sql)
    sql = """create table b_disk_app_tmp as select * from v_disk_app"""
    db.executesql(sql)
    sql = """rename table b_disk_app to b_disk_app_old, b_disk_app_tmp to b_disk_app"""
    db.executesql(sql)
    sql = """drop table if exists b_disk_app_old"""
    db.executesql(sql)
    sql = """alter table b_disk_app add index idx_disk_vendor (disk_vendor)"""
    db.executesql(sql)
    db.commit()
    _websocket_send(event_msg({
                 'event': 'disks_change',
                 'data': {'f': 'b'}
                }), schedule=False)


