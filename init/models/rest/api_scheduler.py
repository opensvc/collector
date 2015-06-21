from gluon.dal import smart_query
import json

#
class rest_get_scheduler_tasks(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List tasks in the collector scheduler.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/scheduler/tasks?query=not repeats=1"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/scheduler/tasks",
          tables=["scheduler_task"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        check_privilege("Manager")
        q = db.scheduler_task.id > 0
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_scheduler_task(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display properties of a specific task in the collector scheduler.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/scheduler/tasks/10",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/scheduler/tasks/<id>",
          tables=["scheduler_task"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("Manager")
        q = db.scheduler_task.id == int(id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_delete_scheduler_task(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a task in the collector scheduler.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/scheduler/tasks/10",
        ]
        rest_delete_handler.__init__(
          self,
          path="/scheduler/tasks/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
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


#
class rest_post_scheduler_task(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify properties of a task in the collector scheduler.",
          "The modification is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        data = """
- <property>=<value> pairs.
- Available properties are: ``%(props)s``:green.
""" % dict(
        props=', '.join(sorted(set(db.scheduler_task.fields)-set(["id"]))),
      )
        examples = [
          """# curl -u %(email)s -o- -X POST -d status="C" https://%(collector)s/init/rest/api/scheduler/tasks/10""",
        ]
        rest_post_handler.__init__(
          self,
          path="/scheduler/tasks/<id>",
          desc=desc,
          data=data,
          examples=examples
        )

    def handler(self, _id, **vars):
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
class rest_get_scheduler_runs(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List runs in the collector scheduler.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/scheduler/runs?query=not repeats=1"
        ]
        rest_get_table_handler.__init__(
          self,
          path="/scheduler/runs",
          tables=["scheduler_run"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        check_privilege("Manager")
        q = db.scheduler_run.id > 0
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_scheduler_run(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display properties of a specific run in the collector scheduler.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/scheduler/runs/10",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/scheduler/runs/<id>",
          tables=["scheduler_run"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("Manager")
        q = db.scheduler_run.id == int(id)
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_delete_scheduler_run(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a run in the collector scheduler.",
        ]
        examples = [
          "# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/scheduler/runs/10",
        ]
        rest_delete_handler.__init__(
          self,
          path="/scheduler/runs/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
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


#
class rest_post_scheduler_run(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify properties of a run in the collector scheduler.",
          "The modification is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        data = """
- <property>=<value> pairs.
- Available properties are: ``%(props)s``:green.
""" % dict(
        props=', '.join(sorted(set(db.scheduler_run.fields)-set(["id"]))),
      )
        examples = [
          """# curl -u %(email)s -o- -X POST -d status="C" https://%(collector)s/init/rest/api/scheduler/runs/10""",
        ]
        rest_post_handler.__init__(
          self,
          path="/scheduler/runs/<id>",
          desc=desc,
          data=data,
          examples=examples
        )

    def handler(self, _id, **vars):
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


class rest_get_scheduler_workers(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List workers of the collector scheduler.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/scheduler/workers?query=group_names contains slow",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/scheduler/workers",
          tables=["scheduler_worker"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        check_privilege("Manager")
        q = db.scheduler_worker.id > 0
        self.set_q(q)
        return self.prepare_data(**vars)


#
class rest_get_scheduler_worker(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display properties of a specific worker of the collector scheduler.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/scheduler/workers/10",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/scheduler/workers/<id>",
          tables=["scheduler_worker"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("Manager")
        q = db.scheduler_worker.id == int(id)
        self.set_q(q)
        return self.prepare_data(**vars)



