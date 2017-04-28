#
# Dashboard updates
#
def node_dashboard_updates(node_id):
    delete_dash_node_without_asset(node_id)
    delete_dash_node_not_updated(node_id)
    update_dash_node_beyond_maintenance_end(node_id)
    update_dash_node_near_maintenance_end(node_id)
    dashboard_events()

def delete_dash_node_without_asset(node_id):
    sql = """delete from dashboard
               where
                 node_id="%(node_id)s" and
                 dash_type = "node without asset information"
          """%dict(node_id=node_id)
    rows = db.executesql(sql)
    db.commit()

def update_dash_node_beyond_maintenance_end(node_id):
    sql = """delete from dashboard
               where
                 node_id in (
                   select node_id
                   from nodes
                   where
                     node_id="%(node_id)s" and
                     maintenance_end is not NULL and
                     maintenance_end != "0000-00-00 00:00:00" and
                     maintenance_end > now()
                 ) and
                 dash_type = "node maintenance expired"
          """%dict(node_id=node_id)
    rows = db.executesql(sql)

    sql = """insert into dashboard
               select
                 NULL,
                 "node maintenance expired",
                 "",
                 1,
                 "",
                 "",
                 now(),
                 "",
                 node_env,
                 now(),
                 node_id,
                 NULL
               from nodes
               where
                 node_id="%(node_id)s" and
                 maintenance_end is not NULL and
                 maintenance_end != "0000-00-00 00:00:00" and
                 maintenance_end < now()
               on duplicate key update
                 dash_updated=now()
          """ % dict(node_id=node_id)
    db.executesql(sql)
    db.commit()

def update_dash_node_near_maintenance_end(node_id):
    sql = """delete from dashboard
               where
                 node_id in (
                   select node_id
                   from nodes
                   where
                     node_id="%(node_id)s" and
                     maintenance_end is not NULL and
                     maintenance_end != "0000-00-00 00:00:00" and
                     (maintenance_end < now() or
                      maintenance_end > date_sub(now(), interval - 30 day))
                 ) and
                 dash_type = "node close to maintenance end"
          """%dict(node_id=node_id)
    rows = db.executesql(sql)

    sql = """insert into dashboard
               select
                 NULL,
                 "node close to maintenance end",
                 "",
                 0,
                 "",
                 "",
                 now(),
                 "",
                 node_env,
                 now(),
                 node_id,
                 NULL
               from nodes
               where
                 node_id="%(node_id)s" and
                 maintenance_end is not NULL and
                 maintenance_end != "0000-00-00 00:00:00" and
                 maintenance_end > now() and
                 maintenance_end < date_sub(now(), interval - 30 day)
               on duplicate key update
                 dash_updated=now()
          """ % dict(node_id=node_id)
    db.executesql(sql)

    db.commit()

def update_dash_node_without_maintenance_end(node_id):
    sql = """delete from dashboard
               where
                 node_id in (
                   select node_id
                   from nodes
                   where
                     node_id="%(node_id)s" and
                     ((maintenance_end != "0000-00-00 00:00:00" and
                       maintenance_end is not NULL) or
                       model like "%%virt%%" or
                       model like "%%Not Specified%%" or
                       model like "%%KVM%%")
                 ) and
                 dash_type = "node without maintenance end date"
          """%dict(node_id=node_id)
    rows = db.executesql(sql)
    db.commit()

def delete_dash_node_not_updated(node_id):
    sql = """delete from dashboard
               where
                 node_id = "%(node_id)s" and
                 dash_type = "node information not updated"
          """%dict(node_id=node_id)
    rows = db.executesql(sql)
    db.commit()


