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

    # has a parent table been modified since last b_disk_app refresh ?
    # if not, skip the refresh
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

    # purge diskinfo agent-provided lines superceded by
    # lines from array parsers. This is ncessary to purge
    # agent-provided lines fetched from collector proxies
    sql = """delete from diskinfo
             where
              disk_id in (
               select disk_id from (
                select disk_id, count(*) as c from diskinfo group by disk_id
               ) t where t.c > 1
              ) and
              disk_arrayid not in (
               select distinct array_name from stor_array
              )"""
    db.executesql(sql)
    db.commit()

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
    sql = """alter table b_disk_app add index idx_disk_arrayid (disk_arrayid)"""
    db.executesql(sql)
    sql = """alter table b_disk_app add index idx_disk_group (disk_group)"""
    db.executesql(sql)
    sql = """alter table b_disk_app add index idx_app (app)"""
    db.executesql(sql)
    db.commit()
    _websocket_send(event_msg({
                 'event': 'disks_change',
                 'data': {'f': 'b'}
                }), schedule=False)


