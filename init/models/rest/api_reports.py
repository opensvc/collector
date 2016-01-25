class rest_delete_reports_metric(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a metric",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/reports/metrics/1"
        ]

        rest_delete_handler.__init__(
          self,
          path="/reports/metrics/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("ReportsManager")

        q = db.metrics.id == id
        metric = db(q).select().first()
        if metric is None:
            raise Exception("Metric %s not found"%str(id))

        metric_id = db(q).delete()

        fmt = "Metric %(metric_name)s deleted"
        d = dict(metric_name=metric.metric_name)

        _log('metric.del', fmt, d)
        l = {
          'event': 'metrics_change',
          'data': {'id': metric.id},
        }
        _websocket_send(event_msg(l))

        return dict(info=fmt%d)

class rest_delete_reports_metrics(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete metrics",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/reports/metrics"
        ]

        rest_delete_handler.__init__(
          self,
          path="/reports/metrics",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not 'id' in vars:
            raise Exception("The 'id' key is mandatory")

        metric_id = vars["id"]
        del(vars["id"])
        return rest_delete_reports_metric().handler(metric_id, **vars)

class rest_post_reports_metrics(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify or create metrics",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d metric_name=test -o- https://%(collector)s/init/rest/api/reports/metrics"
        ]

        rest_post_handler.__init__(
          self,
          path="/reports/metrics",
          tables=["metrics"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        check_privilege("ReportsManager")

        if 'id' in vars:
            metric_id = vars["id"]
            del(vars["id"])
            return rest_post_reports_metric().handler(metric_id, **vars)

        if "metric_name" not in vars:
            raise Exception("Key 'metric_name' is mandatory")
        metric_name = vars.get("metric_name")

        vars["metric_created"] = datetime.datetime.now()
        vars["metric_author"] = user_name()

        metric_id = db.metrics.insert(**vars)
        #lib_reports_add_default_team_responsible(metric_id)
        #lib_reports_add_default_team_publication(metric_id)

        fmt = "Metric %(metric_name)s added"
        d = dict(metric_name=metric_name)

        _log('metric.add', fmt, d)
        l = {
          'event': 'metrics_change',
          'data': {'id': metric_id},
        }
        _websocket_send(event_msg(l))

        return rest_get_reports_metric().handler(metric_id)


class rest_post_reports_metric(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify a metric properties",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d metric_name=test -o- https://%(collector)s/init/rest/api/reports/metrics/1"
        ]

        rest_post_handler.__init__(
          self,
          path="/reports/metrics/<id>",
          tables=["metrics"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("ReportsManager")

        if "id" in vars:
            del(vars["id"])

        q = db.metrics.id == id
        metric = db(q).select().first()
        if metric is None:
            raise Exception("Metric %s not found"%str(id))

        db(q).update(**vars)

        fmt = "Metric %(metric_name)s change: %(data)s"
        d = dict(metric_name=metric.metric_name, data=beautify_change(metric, vars))

        _log('metric.change', fmt, d)
        l = {
          'event': 'metrics_change',
          'data': {'id': metric.id},
        }
        _websocket_send(event_msg(l))

        ret = rest_get_reports_metric().handler(metric.id)
        ret["info"] = fmt % d
        return ret

class rest_get_reports_metrics(rest_get_table_handler):
    def __init__(self):
        desc = [
          "Display reports metrics list.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/metrics",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/reports/metrics",
          tables=["metrics"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.metrics.id > 0
        self.set_q(q)
        return self.prepare_data(**vars)

class rest_get_reports_metric(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display report metric details.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/metrics/1",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/reports/metrics/<id>",
          tables=["metrics"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.metrics.id == id
        self.set_q(q)
        return self.prepare_data(**vars)


class rest_get_reports(rest_get_table_handler):
    def __init__(self):
        desc = [
          "Display reports list for connected user.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/reports",
          tables=["reports"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.reports.id > 0
        self.set_q(q)
        return self.prepare_data(**vars)

class rest_get_report(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display report details for a specific report id.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/1",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/reports/<id>",
          tables=["reports"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.reports.id == id
        data = db(q).select(db.reports.ALL).first()

        if (data == None):
            raise Exception("no report found")

        import yaml
        d = yaml.load(data.report_yaml)

        return dict(data=d)

class rest_get_reports_metric_samples(rest_get_handler):
    def __init__(self):
        desc = [
          "Display datapoints of the specified metric id.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/metrics/1",
        ]
        rest_get_handler.__init__(
          self,
          path="/reports/metrics/<id>/samples",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.metrics.id == id
        definition = db(q).select().first()

        if (definition == None):
          return dict(info="No metrics found.")

        # handle fset ?
        sql_req = definition.metric_sql
        rows = db.executesql(sql_req, as_dict = True)

        return dict(data=rows)

class rest_get_reports_chart_samples(rest_get_table_handler):
    def __init__(self):
        desc = [
          "Display charts time series data for a specific chart id.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/charts/id",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/reports/charts/<id>/samples",
          tables=["metrics_log"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        fset_id = user_fset_id()
        q = db.charts.id == id
        chart = db(q).select().first()

        if chart is None:
            raise Exception("chart %s not found" % str(id))

        try:
            definition = yaml.load(chart.chart_yaml)
        except:
            raise Exception("chart %s definition is corrupted" % str(id))

        metric_ids = []
        for m in definition['Metrics']:
            metric_ids.append(m['metric_id'])

        q = db.metrics_log.metric_id.belongs(metric_ids)
        q &= db.metrics_log.fset_id == fset_id
        self.set_q(q)
        data = self.prepare_data(**vars)
        data["chart_definition"] = definition
        return data

