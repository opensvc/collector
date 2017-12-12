def task_docker_discover_registries():
    ws_send('scheduler_change')
    LOAD('registry', 'discover_registries')
    ws_send('scheduler_change')
    return 1

def task_dash_comp():
    ws_send('scheduler_change')
    LOAD('compliance', 'cron_dash_comp')
    ws_send('scheduler_change')
    return 1

def task_refresh_obsolescence():
    ws_send('scheduler_change')
    refresh_obsolescence()
    ws_send('scheduler_change')

def task_purge_expiry():
    ws_send('scheduler_change')
    LOAD('cron', 'cron_purge_expiry')
    ws_send('scheduler_change')
    return 1

def task_stats():
    ws_send('scheduler_change')
    LOAD('cron', 'cron_stats')
    ws_send('scheduler_change')
    return 1

def task_scrub():
    ws_send('scheduler_change')
    LOAD('cron', 'cron_scrub')
    ws_send('scheduler_change')
    return 1

def task_alerts_daily():
    ws_send('scheduler_change')
    LOAD('cron', 'cron_alerts_daily')
    ws_send('scheduler_change')
    return 1

def task_alerts_hourly():
    ws_send('scheduler_change')
    LOAD('cron', 'cron_alerts_hourly')
    ws_send('scheduler_change')
    return 1

def task_purge_static():
    """ unlink static/tempviz*.png
    """
    import os
    import glob
    ws_send('scheduler_change')
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
    for name in glob.glob(os.path.join(staticdir, '*-*-*-*.pdf')):
        files.append(name)
        os.unlink(name)
    ws_send('scheduler_change')
    return files

def task_purge_feed():
    sql = """
      delete from scheduler_task
      where
        repeats=1 and
        status in ("COMPLETED", "FAILED", "TIMEOUT") and
        last_run_time < date_sub(now(), interval 10 minute)
    """
    ws_send('scheduler_change')
    db.executesql(sql)
    db.commit()
    sql = """
      delete from scheduler_run
      where
        status in ("COMPLETED", "STOPPED") and
        stop_time < date_sub(now(), interval 10 minute)
    """
    db.executesql(sql)
    db.commit()
    sql = """
      delete from scheduler_run
      where
        status in ("FAILED", "TIMEOUT") and
        stop_time < date_sub(now(), interval 1 day)
    """
    db.executesql(sql)
    db.commit()
    sql = """
      select
        scheduler_run.id
      from scheduler_run, scheduler_task
      where
        scheduler_task.id=scheduler_run.task_id and
        scheduler_run.status="RUNNING" and
        scheduler_task.status!="RUNNING"
    """
    rows = db.executesql(sql)
    if len(rows) > 0:
        ids = [ r[0] for r in rows ]
        ids = ",".join(map(lambda x: str(x), ids))
        sql = """delete from scheduler_run where id in (%s)""" % ids
        db.executesql(sql)
        db.commit()
    ws_send('scheduler_change')


def task_feed_monitor():
    ws_send('scheduler_change')
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
    ws_send('scheduler_change')

def task_unfinished_actions():
    ws_send('scheduler_change')
    now = datetime.datetime.now()
    tmo = now - datetime.timedelta(minutes=120)
    q = (db.svcactions.begin < tmo)
    q &= (db.svcactions.end==None)
    rows = db(q).select(orderby=db.svcactions.id)
    db(q).update(status="err", end='1000-01-01 00:00:00')
    db.commit()
    for r in rows:
        _log('action.timeout', "action ids %(ids)s closed on timeout",
              dict(ids=r.id),
              user='collector',
              svc_id=r.svc_id,
              node_id=r.node_id,
              level="warning")
    ws_send('scheduler_change')
    return "%d actions marked timed out"%len(rows)

def task_purge_checks():
    ws_send('scheduler_change')
    thres = now - datetime.timedelta(days=2)
    q = db.checks_live.chk_updated < thres
    db(q).delete()
    db.commit()
    ws_send('scheduler_change')

from gluon.contrib.redis_scheduler import RScheduler
scheduler = RScheduler(db, migrate=False, redis_conn=rconn)
