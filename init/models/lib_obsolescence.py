def update_nodes_fields():
    print "update nodes obs dates"
    q = db.obsolescence.id > 0
    for row in db(q).select():
        _update_nodes_fields(row.obs_type, row.obs_name,
                             row.obs_warn_date, row.obs_alert_date)

def _update_nodes_fields(obs_type, obs_name, obs_warn_date, obs_alert_date):
        if obs_type == 'hw':
            q = db.nodes.model == obs_name
            db(q).update(hw_obs_warn_date=obs_warn_date,
                         hw_obs_alert_date=obs_alert_date)
        elif obs_type == 'os':
            q = db.nodes.os_concat == obs_name
            db(q).update(os_obs_warn_date=obs_warn_date,
                         os_obs_alert_date=obs_alert_date)

def cron_obsolescence_hw():
    print "refresh hw models"
    sql = """insert ignore into obsolescence (obs_type, obs_name, obs_warn_date_updated_by, obs_warn_date_updated, obs_alert_date_updated_by, obs_alert_date_updated)
             select "hw", model, "collector", now(), "collector", now()
             from nodes
             where model!=''
             group by model
          """
    db.executesql(sql)
    db.commit()
    print "refresh hw alerts"
    update_dash_obs_hw_alert()
    print "refresh hw warnings"
    update_dash_obs_hw_warn()
    return dict(message=T("done"))

def cron_obsolescence_os():
    print "refresh os names"
    sql = """insert ignore into obsolescence (obs_type, obs_name, obs_warn_date_updated_by, obs_warn_date_updated, obs_alert_date_updated_by, obs_alert_date_updated)
             select "os", os_concat, "collector", now(), "collector", now()
             from nodes
             where os_concat!=''
             group by os_concat
          """
    db.executesql(sql)
    db.commit()
    print "refresh os alerts"
    update_dash_obs_os_alert()
    print "refresh os warnings"
    update_dash_obs_os_warn()
    return dict(message=T("done"))

def refresh_obsolescence():
    cron_obsolescence_os()
    cron_obsolescence_hw()
    purge_dash_obs_without()
    update_nodes_fields()

#
# Dashboard updates
#
def _update_dash_obs_hw_warn():
    update_dash_obs_hw_warn()

def update_dash_obs_hw_warn(obs_name=None):
    if obs_name is None:
        where_obs_name = ""
        where_dash_dict = ""
    else:
        where_obs_name = """o.obs_name = "%(obs_name)s" and"""%dict(obs_name=obs_name)
        where_dash_dict = """dash_dict like '%%"o": "%(obs_name)s"%%' and"""%dict(obs_name=obs_name)

    sql = """select n.node_id from obsolescence o
                 join nodes n on
                   o.obs_name = n.model
               where
                 %(where_obs_name)s
                 o.obs_type = "hw" and (
                  o.obs_alert_date is NULL or
                  o.obs_name like "%%virtual%%" or
                  o.obs_name like "%%virtuel%%" or
                  o.obs_name like "%%cluster%%" or
                  o.obs_alert_date = "0000-00-00 00:00:00" or
                  o.obs_warn_date >= now() or
                  o.obs_alert_date <= now()
                 )
          """%dict(where_obs_name=where_obs_name)
    rows = db.executesql(sql)
    node_ids = [ r[0] for r in rows if r[0] != 0 and r[0] is not None]
    if len(node_ids) > 0:
        sql = """delete from dashboard
                 where
                        node_id in (%(node_ids)s) and
                        dash_type="hardware obsolescence warning"
                  """%dict(node_ids=",".join(map(lambda x: repr(str(x)), node_ids)))
        db.executesql(sql)
        db.commit()

    sql = """insert into dashboard
               select
                 NULL,
                 "hardware obsolescence warning",
                 "",
                 0,
                 "%%(o)s warning since %%(a)s",
                 concat('{"a": "', o.obs_warn_date,
                        '", "o": "', o.obs_name,
                        '"}'),
                 now(),
                 "",
                 n.node_env,
                 now(),
                 n.node_id,
                 NULL,
                 NULL
               from obsolescence o
                 join nodes n on
                   o.obs_name = n.model
               where
                 %(where_obs_name)s
                 o.obs_alert_date is not NULL and
                 o.obs_alert_date != "0000-00-00 00:00:00" and
                 o.obs_name not like "%%virtual%%" and
                 o.obs_name not like "%%virtuel%%" and
                 o.obs_name not like "%%cluster%%" and
                 o.obs_warn_date < now() and
                 o.obs_alert_date > now() and
                 o.obs_type = "hw"
               on duplicate key update
                 dash_updated=now()
          """%dict(where_obs_name=where_obs_name)
    db.executesql(sql)
    db.commit()

def _update_dash_obs_hw_alert():
    update_dash_obs_hw_alert()

def update_dash_obs_hw_alert(obs_name=None):
    if obs_name is None:
        where_obs_name = ""
    else:
        where_obs_name = """o.obs_name = "%(obs_name)s" and"""%dict(obs_name=obs_name)


    sql = """select n.node_id from obsolescence o
                 join nodes n on
                   o.obs_name = n.model
               where
                 %(where_obs_name)s
                 o.obs_type = "hw" and (
                  o.obs_alert_date is NULL or
                  o.obs_name like "%%virtual%%" or
                  o.obs_name like "%%virtuel%%" or
                  o.obs_name like "%%cluster%%" or
                  o.obs_alert_date = "0000-00-00 00:00:00" or
                  o.obs_alert_date >= now()
                 )
          """%dict(where_obs_name=where_obs_name)
    rows = db.executesql(sql)
    node_ids = [ r[0] for r in rows if r[0] != 0 and r[0] is not None]
    if len(node_ids) > 0:
        sql = """delete from dashboard
                 where
                        node_id in (%(node_ids)s) and
                        dash_type="hardware obsolescence alert"
                  """%dict(node_ids=",".join(map(lambda x: repr(str(x)), node_ids)))
        db.executesql(sql)
        db.commit()


    sql = """insert into dashboard
               select
                 NULL,
                 "hardware obsolescence alert",
                 "",
                 1,
                 "%%(o)s obsolete since %%(a)s",
                 concat('{"a": "', o.obs_alert_date,
                        '", "o": "', o.obs_name,
                        '"}'),
                 now(),
                 "",
                 n.node_env,
                 now(),
                 n.node_id,
                 NULL,
                 NULL
               from obsolescence o
                 join nodes n on
                   o.obs_name = n.model
               where
                 %(where_obs_name)s
                 o.obs_alert_date is not NULL and
                 o.obs_name not like "%%virtual%%" and
                 o.obs_name not like "%%virtuel%%" and
                 o.obs_name not like "%%cluster%%" and
                 o.obs_alert_date != "0000-00-00 00:00:00" and
                 o.obs_alert_date < now() and
                 o.obs_type = "hw"
               on duplicate key update
                 dash_updated=now()
          """%dict(where_obs_name=where_obs_name)
    db.executesql(sql)
    db.commit()


def _update_dash_obs_os_warn():
    update_dash_obs_os_warn()

def update_dash_obs_os_warn(obs_name=None):
    if obs_name is None:
        where_obs_name = ""
    else:
        where_obs_name = """o.obs_name = "%(obs_name)s" and"""%dict(obs_name=obs_name)

    if obs_name is not None:
        sql = """select n.node_id from obsolescence o
                     join nodes n on
                       o.obs_name = n.os_concat
                   where
                     %(where_obs_name)s
                     o.obs_type = "os" and (
                      o.obs_alert_date is NULL or
                      o.obs_alert_date = "0000-00-00 00:00:00" or
                      o.obs_warn_date >= now() or
                      o.obs_alert_date <= now()
                     )
              """%dict(where_obs_name=where_obs_name)
        rows = db.executesql(sql)
        if len(rows) > 0:
            node_ids = [ r[0] for r in rows if r[0] != 0 and r[0] is not None]
            sql = """delete from dashboard
                     where
                        node_id in (%(node_ids)s) and
                        dash_type="os obsolescence warning"
                  """%dict(node_ids=",".join(map(lambda x: repr(str(x)), node_ids)))
            db.executesql(sql)
            db.commit()
    else:
        sql = """delete from dashboard
                      where
                        dash_updated < date_sub(now(), interval 2 day) and
                        dash_type="os obsolescence warning"
                  """
        db.executesql(sql)
        db.commit()

    sql = """insert into dashboard
               select
                 NULL,
                 "os obsolescence warning",
                 "",
                 0,
                 "%%(o)s warning since %%(a)s",
                 concat('{"a": "', o.obs_warn_date,
                        '", "o": "', o.obs_name,
                        '"}'),
                 now(),
                 "",
                 n.node_env,
                 now(),
                 n.node_id,
                 NULL,
                 NULL
               from obsolescence o
                 join nodes n on
                   o.obs_name = concat_ws(' ',n.os_name,n.os_vendor,n.os_release,n.os_update)
               where
                 %(where_obs_name)s
                 o.obs_alert_date is not NULL and
                 o.obs_alert_date != "0000-00-00 00:00:00" and
                 o.obs_warn_date < now() and
                 o.obs_alert_date > now() and
                 o.obs_type = "os"
               on duplicate key update
                 dash_updated=now()
          """%dict(where_obs_name=where_obs_name)
    db.executesql(sql)
    db.commit()

def _update_dash_obs_os_alert():
    update_dash_obs_os_alert()

def update_dash_obs_os_alert(obs_name=None):
    if obs_name is None:
        where_obs_name = ""
    else:
        where_obs_name = """o.obs_name = "%(obs_name)s" and"""%dict(obs_name=obs_name)

    if obs_name is not None:
        sql = """select n.node_id from obsolescence o
                     join nodes n on
                       o.obs_name = n.os_concat
                   where
                     %(where_obs_name)s
                     o.obs_type = "os" and (
                      o.obs_alert_date is NULL or
                      o.obs_alert_date = "0000-00-00 00:00:00" or
                      o.obs_alert_date >= now()
                     )
              """%dict(where_obs_name=where_obs_name)
        rows = db.executesql(sql)
        if len(rows) > 0:
            node_ids = [ r[0] for r in rows if r[0] != 0 and r[0] is not None]
            sql = """delete from dashboard
                     where
                        node_id in (%(node_ids)s) and
                        dash_type="os obsolescence alert"
                  """%dict(node_ids=",".join(map(lambda x: repr(str(x)), node_ids)))
            db.executesql(sql)
            db.commit()
    else:
        sql = """delete from dashboard
                      where
                        dash_updated < date_sub(now(), interval 2 day) and
                        dash_type="os obsolescence alert"
                  """
        db.executesql(sql)
        db.commit()

    sql = """insert into dashboard
               select
                 NULL,
                 "os obsolescence alert",
                 "",
                 1,
                 "%%(o)s obsolete since %%(a)s",
                 concat('{"a": "', o.obs_alert_date,
                        '", "o": "', o.obs_name,
                        '"}'),
                 now(),
                 "",
                 n.node_env,
                 now(),
                 n.nodename,
                 NULL,
                 NULL
               from obsolescence o
                 join nodes n on
                   o.obs_name = concat_ws(' ',n.os_name,n.os_vendor,n.os_release,n.os_update)
               where
                 %(where_obs_name)s
                 o.obs_alert_date is not NULL and
                 o.obs_alert_date != "0000-00-00 00:00:00" and
                 o.obs_alert_date < now() and
                 o.obs_type = "os"
               on duplicate key update
                 dash_updated=now()
          """%dict(where_obs_name=where_obs_name)
    db.executesql(sql)
    db.commit()

def delete_dash_obs_without(obs_name, t, a):
    if t == "hw":
        tl = "hardware"
    else:
        tl = t
    if a == "warn":
        al = "warning"
    else:
        al = a
    sql = """delete from dashboard
             where
               dash_dict = '{"o": "%(obs_name)s"}' and
               dash_type="%(tl)s obsolescence %(al)s date not set"
          """%dict(obs_name=obs_name, tl=tl, al=al)
    db.executesql(sql)
    db.commit()

def purge_dash_obs_without():
    data_hw = (
             ("hardware obsolescence warning date not set", "hw"),
             ("hardware obsolescence alert date not set", "hw"),
           )
    data_os = (
             ("os obsolescence alert date not set", "os"),
             ("os obsolescence warning date not set", "os")
           )

    for dash_type, obs_type in data_hw:
        print "purge %s" % dash_type
        sql = """select d.id from dashboard d
                 join nodes n on d.node_id=n.node_id
                 where
                   d.dash_type="%(dash_type)s" and
                   d.dash_dict != concat('{"o": "', n.model, '"}')
        """%dict(dash_type=dash_type)
        rows = db.executesql(sql, as_dict=True)

        q = db.dashboard.id.belongs([r["id"] for r in rows])
        db(q).delete()
        db.commit()

    for dash_type, obs_type in data_os:
        print "purge %s" % dash_type
        sql = """select d.id from dashboard d
                 join nodes n on d.node_id=n.node_id
                 where
                   d.dash_type="%(dash_type)s" and
                   d.dash_dict != concat('{"o": "', n.os_name, " ", n.os_vendor, " ", n.os_release, ' "}')
        """%dict(dash_type=dash_type)
        rows = db.executesql(sql, as_dict=True)

        q = db.dashboard.id.belongs([r["id"] for r in rows])
        db(q).delete()
        db.commit()

    for dash_type, obs_type in data_os + data_hw:
        sql = """delete from dashboard
                 where
                   dash_type = "%(dash_type)s" and
                   dash_dict in (
                     select
                       concat('{"o": "', obs_name, '"}')
                     from obsolescence
                     where
                       obs_warn_date is not null and
                       obs_type = "%(obs_type)s"
                   )
        """%dict(dash_type=dash_type, obs_type=obs_type)
        db.executesql(sql)
        db.commit()


