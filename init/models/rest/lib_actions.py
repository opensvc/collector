def update_action_errors():
    sql = """truncate b_action_errors
          """
    db.executesql(sql)
    sql = """insert into b_action_errors
               select null, svc_id, node_id, count(id)
               from svcactions
               where
                 status = 'err' and
                 (ack <> 1 or isnull(ack)) and
                 end is not null
               group by svc_id, node_id
          """
    db.executesql(sql)
    db.commit()

def update_instance_action_errors(svc_id, node_id):
    sql = """select count(id) from svcactions
             where
               node_id = "%(node_id)s" and
               svc_id = "%(svc_id)s" and
               status = 'err' and
               (ack <> 1 or isnull(ack)) and
               end is not null
             group by svc_id, node_id
          """ % dict(node_id=node_id, svc_id=svc_id)
    rows = db.executesql(sql)
    if len(rows) == 0:
        sql = """delete from b_action_errors where
                 node_id = "%(node_id)s" and
                 svc_id = "%(svc_id)s"
              """ % dict(node_id=node_id, svc_id=svc_id)
    else:
        sql = """insert into b_action_errors set
                   node_id = "%(node_id)s",
                   svc_id = "%(svc_id)s",
                   err = %(n)d
                 on duplicate key update
                   err = %(n)d
              """ % dict(node_id=node_id, svc_id=svc_id, n=rows[0][0])
    db.executesql(sql)
    db.commit()

def update_dash_action_errors(svc_id, node_id):
    sql = """select e.err, s.svc_env from b_action_errors e
             join services s on e.svc_id=s.svc_id
             where
               e.svc_id="%(svc_id)s" and
               e.node_id="%(node_id)s"
          """%dict(svc_id=svc_id, node_id=node_id)
    rows = db.executesql(sql)

    if len(rows) == 1:
        if rows[0][1] == 'PRD':
            sev = 4
        else:
            sev = 3
        sql = """insert into dashboard
                 set
                   dash_type="action errors",
                   svc_id="%(svc_id)s",
                   node_id="%(node_id)s",
                   dash_severity=%(sev)d,
                   dash_fmt="%%(err)s action errors",
                   dash_dict='{"err": "%(err)d"}',
                   dash_env='%(env)s',
                   dash_created="%(now)s",
                   dash_updated="%(now)s"
                 on duplicate key update
                   dash_severity=%(sev)d,
                   dash_fmt="%%(err)s action errors",
                   dash_dict='{"err": "%(err)d"}',
                   dash_updated="%(now)s"
              """%dict(svc_id=svc_id,
                       node_id=node_id,
                       sev=sev,
                       env=rows[0][1],
                       now=str(datetime.datetime.now()),
                       err=rows[0][0])
        db.executesql(sql)
        db.commit()
        sqlws = """select
                     dash_md5
                   from
                     dashboard
                   where
                     dash_type="action errors" and
                     svc_id="%(svc_id)s" and
                     node_id="%(node_id)s" and
                     dash_fmt="%%(err)s action errors"
              """%dict(svc_id=svc_id,
                       node_id=node_id,
                  )
        rows = db.executesql(sqlws)
        if len(rows) > 0:
            ws_send('dash_change', {'dash_md5': rows[0][0]})

    else:
        sqlws = """select dash_md5 from dashboard
                 where
                   dash_type="action errors" and
                   svc_id="%(svc_id)s" and
                   node_id="%(node_id)s"
              """%dict(svc_id=svc_id,
                       node_id=node_id)
        rows = db.executesql(sqlws)
        if len(rows) > 0:
            ws_send('dash_delete', {'dash_md5': rows[0][0]})
        sql = """delete from dashboard
                 where
                   dash_type="action errors" and
                   svc_id="%(svc_id)s" and
                   node_id="%(node_id)s"
              """%dict(svc_id=svc_id,
                       node_id=node_id)
        db.executesql(sql)
        db.commit()

