def task_docker_discover_registries():
    LOAD('registry', 'discover_registries')

def task_dash_comp():
    LOAD('compliance', 'cron_dash_comp')

def task_refresh_obsolescence():
    refresh_obsolescence()

def task_perf():
    LOAD('cron', 'cron_perf')

def task_stats():
    LOAD('cron', 'cron_stats')

def task_scrub():
    LOAD('cron', 'cron_scrub')

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
    for name in glob.glob(os.path.join(staticdir, '*-*-*-*.pdf')):
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

def task_unfinished_actions():
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
    return "%d actions marked timed out"%len(rows)

def task_purge_checks():
    thres = now - datetime.timedelta(days=2)
    q = db.checks_live.chk_updated < thres
    db(q).delete()
    db.commit()

from gluon.contrib.redis_scheduler import RScheduler
scheduler = RScheduler(db, migrate=False, redis_conn=rconn)
