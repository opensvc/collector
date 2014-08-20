def task_dash_comp():
    LOAD('compliance', 'cron_dash_comp')

def task_refresh_obsolescence():
    LOAD('obsolescence', 'refresh_obsolescence')

def task_perf():
    LOAD('cron', 'cron_perf')

def task_stats():
    LOAD('cron', 'cron_stats')

def task_alerts_daily():
    LOAD('cron', 'cron_alerts_daily')

def task_alerts_hourly():
    LOAD('cron', 'cron_alerts_hourly')

def task_purge_static():
    """ unlink static/tempviz*.png
    """
    import os
    import glob
    staticdir = os.path.join(os.getcwd(), 'applications', 'init', 'static')
    vizprefix = 'tempviz'
    files = []
    for name in glob.glob(os.path.join(staticdir, vizprefix+'*.png')):
        files.append(name)
        os.unlink(name)
    for name in glob.glob(os.path.join(staticdir, vizprefix+'*.dot')):
        files.append(name)
        os.unlink(name)
    for name in glob.glob(os.path.join(staticdir, 'stats_*_[0-9]*.png')):
        files.append(name)
        os.unlink(name)
    for name in glob.glob(os.path.join(staticdir, 'stat_*_[0-9]*.png')):
        files.append(name)
        os.unlink(name)
    for name in glob.glob(os.path.join(staticdir, 'stats_*_[0-9]*.svg')):
        files.append(name)
        os.unlink(name)
    return files

def task_purge_feed():
    sql = """
      delete from scheduler_task
      where
        repeats=1 and
        status in ("COMPLETED", "FAILED", "TIMEOUT") and
        last_run_time < date_sub(now(), interval 10 minute)
    """
    db.executesql(sql)
    sql = """
      delete from scheduler_run
      where
        status = "COMPLETED" and
        stop_time < date_sub(now(), interval 10 minute)
    """
    db.executesql(sql)
    sql = """
      delete from scheduler_run
      where
        status in ("FAILED", "TIMEOUT") and
        stop_time < date_sub(now(), interval 1 day)
    """
    db.executesql(sql)
    db.commit()

def task_feed_monitor():
    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)
    limit = now - datetime.timedelta(minutes=5)

    q = db.scheduler_task.status == "QUEUED"
    q &= db.scheduler_task.repeats == 1
    q &= db.scheduler_task.start_time < limit
    n = db(q).count()

    if n == 0:
        # clean all
        sql = """delete from dashboard
                 where
                   dash_type = "feed queue"
              """
        db.executesql(sql)
        db.commit()
        return

    sql = """insert into dashboard
             set
               dash_type="feed queue",
               dash_severity=4,
               dash_fmt="%%(n)s entries stalled in feed queue",
               dash_dict='{"n": "%(n)d"}',
               dash_created="%(now)s",
               dash_env="PRD",
               dash_updated="%(now)s"
             on duplicate key update
               dash_fmt="%%(n)s entries stalled in feed queue",
               dash_dict='{"n": "%(n)d"}',
               dash_updated="%(now)s"
          """%dict(n=n, now=str(now))
    db.executesql(sql)
    db.commit()

    # clean old
    sql = """delete from dashboard
             where
               dash_type = "feed queue" and
               dash_updated < "%(now)s" """%dict(now=str(now))
    db.executesql(sql)
    db.commit()

def task_refresh_b_apps():
    from warnings import filterwarnings
    import MySQLdb
    filterwarnings('ignore', category = MySQLdb.Warning)
    try:
        sql = "drop table if exists b_apps_new"
        db.executesql(sql)
        sql = "create table b_apps_new as select * from v_apps"
        db.executesql(sql)
        sql = "alter table b_apps_new add key idx1 (app)"
        db.executesql(sql)
        sql = "drop table if exists b_apps_old"
        db.executesql(sql)
        sql = "rename table b_apps to b_apps_old, b_apps_new to b_apps"
        db.executesql(sql)
    except:
        sql = "drop table if exists b_apps"
        db.executesql(sql)
        sql = "create table b_apps as select * from v_apps"
        db.executesql(sql)
        sql = "alter table b_apps add key idx1 (app)"
        db.executesql(sql)
    db.commit()

def task_unfinished_actions():
    now = datetime.datetime.now()
    tmo = now - datetime.timedelta(minutes=120)
    q = (db.SVCactions.begin < tmo)
    q &= (db.SVCactions.end==None)
    rows = db(q).select(orderby=db.SVCactions.id)
    db(q).update(status="err", end='1000-01-01 00:00:00')
    db.commit()
    for r in rows:
        _log('action.timeout', "action ids %(ids)s closed on timeout",
              dict(ids=r.id),
              user='collector',
              svcname=r.svcname,
              nodename=r.hostname,
              level="warning")
    return "%d actions marked timed out"%len(rows)

def task_refresh_b_disk_app():
    from warnings import filterwarnings
    import MySQLdb
    filterwarnings('ignore', category = MySQLdb.Warning)
    sql = """
      select
        max(update_time)>(select update_time from information_schema.tables where table_schema="opensvc" and table_name='b_disk_app') as need_update ,
        max(update_time) as src_tables_last_update,
        (select update_time from information_schema.tables where table_schema="opensvc" and table_name='b_disk_app') as b_disk_app_last_update
      from information_schema.tables
      where
        table_schema="opensvc" and table_name in ('nodes', 'services', 'apps', 'svcdisks', 'diskinfo')
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
    db.commit()

def task_purge_checks():
    thres = now - datetime.timedelta(days=2)
    q = db.checks_live.chk_updated < thres
    db(q).delete()
    db.commit()

from gluon.scheduler import Scheduler
scheduler = Scheduler(db)
