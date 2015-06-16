from gluon.dal import smart_query
import json

api_scheduler_doc = {}


#
api_scheduler_doc["/scheduler/tasks"] = """
### GET

Description:

- List tasks in the collector scheduler.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/scheduler/tasks?query=not repeats=1``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.scheduler_task.fields)),
      )

def get_scheduler_tasks(props=None, query=None):
    check_privilege("Manager")
    q = db.scheduler_task.id > 0
    if query:
        cols = props_to_cols(None, tables=["scheduler_task"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["scheduler_task"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)


api_scheduler_doc["/scheduler/tasks/<id>"] = """
### GET

Description:

- Display properties of a specific task in the collector scheduler

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/scheduler/tasks/10``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.scheduler_task.fields)),
      )

def get_scheduler_task(id, props=None):
    check_privilege("Manager")
    q = db.scheduler_task.id == int(id)
    cols = props_to_cols(props, tables=["scheduler_task"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)

api_scheduler_doc["/scheduler/tasks/<id>"] += """
### DELETE

Description:

- Delete a task in the collector scheduler

Example:

``# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/scheduler/tasks/10``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
      )

def delete_scheduler_task(id, props=None):
    check_privilege("Manager")
    q = db.scheduler_task.id == int(id)
    row = db(q).select().first()
    if row is None:
        return dict(info="Task %s does not exist in the scheduler" % id)
    db(q).delete()
    _log('rest.scheduler.delete',
         'deleted task %(u)s',
         dict(u=row.function_name))
    return dict(info="Task %s deleted" % id)


api_scheduler_doc["/scheduler/tasks/<id>"] += """
### POST

Description:

- Modify properties of a task in the collector scheduler
- The user must be responsible for the node
- The user must be in the NodeManager privilege group
- The modification is logged in the collector's log.
- A websocket event is sent to announce the change in the table.

Data:

- <property>=<value> pairs.
- Available properties are: ``%(props)s``:green.

Example:

``# curl -u %(email)s -o- -X POST -d status="C" https://%(collector)s/init/rest/api/scheduler/10``

""" % dict(
        email=user_email(),
        props=', '.join(sorted(set(db.scheduler_task.fields)-set(["id"]))),
        collector=request.env.http_host,
      )

def set_scheduler_task(_id, **vars):
    check_privilege("Manager")
    q = db.scheduler_task.id == int(_id)
    row = db(q).select().first()
    if row is None:
        return dict(error="Task %s does not exist in the scheduler" % _id)
    if "id" in vars.keys():
        del(vars["id"])
    db(q).update(**vars)
    l = []
    for key in vars:
        l.append("%s: %s => %s" % (str(key), str(row[key]), str(vars[key])))
    _log('rest.scheduler.update',
         'update properties %(data)s',
         dict(data=", ".join(l)))
    return get_scheduler_task(_id)


#
api_scheduler_doc["/scheduler/runs"] = """
### GET

Description:

- List runs in the collector scheduler.

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


- **query**
. A web2py smart query

Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/scheduler/runs?query=not repeats=1``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.scheduler_run.fields)),
      )

def get_scheduler_runs(props=None, query=None):
    check_privilege("Manager")
    q = db.scheduler_run.id > 0
    if query:
        cols = props_to_cols(None, tables=["scheduler_run"])
        q &= smart_query(cols, query)
    cols = props_to_cols(props, tables=["scheduler_run"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)


api_scheduler_doc["/scheduler/runs/<id>"] = """
### GET

Description:

- Display properties of a specific run in the collector scheduler

Optional parameters:

- **props**
. A list of properties to include in each dictionnary.
. If omitted, all properties are included.
. The separator is ','.
. Available properties are: ``%(props)s``:green.


Example:

``# curl -u %(email)s -o- https://%(collector)s/init/rest/api/scheduler/runs/10``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
        props=", ".join(sorted(db.scheduler_run.fields)),
      )

def get_scheduler_run(id, props=None):
    check_privilege("Manager")
    q = db.scheduler_run.id == int(id)
    cols = props_to_cols(props, tables=["scheduler_run"])
    data = db(q).select(*cols, cacheable=True).as_list()
    return dict(data=data)

api_scheduler_doc["/scheduler/runs/<id>"] += """
### DELETE

Description:

- Delete a run in the collector scheduler

Example:

``# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/scheduler/runs/10``

""" % dict(
        email=user_email(),
        collector=request.env.http_host,
      )

def delete_scheduler_run(id, props=None):
    check_privilege("Manager")
    q = db.scheduler_run.id == int(id)
    row = db(q).select().first()
    if row is None:
        return dict(info="Run %s does not exist in the scheduler" % id)
    q = db.scheduler_task.id == row.task_id
    task = db(q).select().first()
    if task is None:
        u = str(row.id)
    else:
        u = "%d (%s)" % (row.id, str(task.function_name))
    db(q).delete()
    _log('rest.scheduler.delete',
         'deleted run %(u)s',
         dict(u=u))
    return dict(info="Run %s deleted" % id)


api_scheduler_doc["/scheduler/runs/<id>"] += """
### POST

Description:

- Modify properties of a run in the collector scheduler
- The user must be responsible for the node
- The user must be in the NodeManager privilege group
- The modification is logged in the collector's log.
- A websocket event is sent to announce the change in the table.

Data:

- <property>=<value> pairs.
- Available properties are: ``%(props)s``:green.

Example:

``# curl -u %(email)s -o- -X POST -d status="COMPLETED" https://%(collector)s/init/rest/api/scheduler/runs/10``

""" % dict(
        email=user_email(),
        props=', '.join(sorted(set(db.scheduler_run.fields)-set(["id"]))),
        collector=request.env.http_host,
      )

def set_scheduler_run(_id, **vars):
    check_privilege("Manager")
    q = db.scheduler_run.id == int(_id)
    row = db(q).select().first()
    if row is None:
        return dict(error="Run %s does not exist in the scheduler" % _id)
    if "id" in vars.keys():
        del(vars["id"])
    db(q).update(**vars)
    l = []
    for key in vars:
        l.append("%s: %s => %s" % (str(key), str(row[key]), str(vars[key])))
    _log('rest.scheduler.update',
         'update properties %(data)s',
         dict(data=", ".join(l)))
    return get_scheduler_run(_id)


