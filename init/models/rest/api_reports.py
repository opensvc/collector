#
# Reports
#
class rest_delete_report(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a report",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/reports/1"
        ]

        rest_delete_handler.__init__(
          self,
          path="/reports/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("ReportsManager")

        q = db.reports.id == id
        report = db(q).select().first()
        if report is None:
            raise Exception("Report %s not found"%str(id))

        report_id = db(q).delete()

        fmt = "Report %(report_name)s deleted"
        d = dict(report_name=report.report_name)

        _log('report.del', fmt, d)
        l = {
          'event': 'reports_change',
          'data': {'id': report.id},
        }
        _websocket_send(event_msg(l))

        return dict(info=fmt%d)

class rest_delete_reports(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete reports",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/reports"
        ]

        rest_delete_handler.__init__(
          self,
          path="/reports",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not 'id' in vars:
            raise Exception("The 'id' key is mandatory")

        report_id = vars["id"]
        del(vars["id"])
        return rest_delete_report().handler(report_id, **vars)

class rest_post_reports(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify or create reports",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d report_name=test -o- https://%(collector)s/init/rest/api/reports"
        ]

        rest_post_handler.__init__(
          self,
          path="/reports",
          tables=["reports"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        check_privilege("ReportsManager")

        if 'id' in vars:
            report_id = vars["id"]
            del(vars["id"])
            return rest_post_report().handler(report_id, **vars)

        if "report_name" not in vars:
            raise Exception("Key 'report_name' is mandatory")
        report_name = vars.get("report_name")

        #vars["report_created"] = datetime.datetime.now()
        #vars["report_author"] = user_name()

        report_id = db.reports.insert(**vars)
        #lib_reports_add_default_team_responsible(report_id)
        #lib_reports_add_default_team_publication(report_id)

        fmt = "Chart %(report_name)s added"
        d = dict(report_name=report_name)

        _log('report.add', fmt, d)
        l = {
          'event': 'reports_change',
          'data': {'id': report_id},
        }
        _websocket_send(event_msg(l))

        return rest_get_report().handler(report_id)


class rest_post_report(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify a report properties",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d report_name=test -o- https://%(collector)s/init/rest/api/reports/1"
        ]

        rest_post_handler.__init__(
          self,
          path="/reports/<id>",
          tables=["reports"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("ReportsManager")

        if "id" in vars:
            del(vars["id"])

        q = db.reports.id == id
        report = db(q).select().first()
        if report is None:
            raise Exception("Chart %s not found"%str(id))

        db(q).update(**vars)

        fmt = "Chart %(report_name)s change: %(data)s"
        d = dict(report_name=report.report_name, data=beautify_change(report, vars))

        _log('report.change', fmt, d)
        l = {
          'event': 'reports_change',
          'data': {'id': report.id},
        }
        _websocket_send(event_msg(l))

        ret = rest_get_report().handler(report.id)
        ret["info"] = fmt % d
        return ret

class rest_get_reports(rest_get_table_handler):
    def __init__(self):
        desc = [
          "Display reports list.",
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
          "Display report report details.",
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
        self.set_q(q)
        return self.prepare_data(**vars)


#
# Charts
#
class rest_delete_reports_chart(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a chart",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/reports/charts/1"
        ]

        rest_delete_handler.__init__(
          self,
          path="/reports/charts/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("ReportsManager")

        q = db.charts.id == id
        chart = db(q).select().first()
        if chart is None:
            raise Exception("Chart %s not found"%str(id))

        chart_id = db(q).delete()

        fmt = "Chart %(chart_name)s deleted"
        d = dict(chart_name=chart.chart_name)

        _log('chart.del', fmt, d)
        l = {
          'event': 'charts_change',
          'data': {'id': chart.id},
        }
        _websocket_send(event_msg(l))

        return dict(info=fmt%d)

class rest_delete_reports_charts(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete charts",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/reports/charts"
        ]

        rest_delete_handler.__init__(
          self,
          path="/reports/charts",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not 'id' in vars:
            raise Exception("The 'id' key is mandatory")

        chart_id = vars["id"]
        del(vars["id"])
        return rest_delete_reports_chart().handler(chart_id, **vars)

class rest_post_reports_charts(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify or create charts",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d chart_name=test -o- https://%(collector)s/init/rest/api/reports/charts"
        ]

        rest_post_handler.__init__(
          self,
          path="/reports/charts",
          tables=["charts"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        check_privilege("ReportsManager")

        if 'id' in vars:
            chart_id = vars["id"]
            del(vars["id"])
            return rest_post_reports_chart().handler(chart_id, **vars)

        if "chart_name" not in vars:
            raise Exception("Key 'chart_name' is mandatory")
        chart_name = vars.get("chart_name")

        #vars["chart_created"] = datetime.datetime.now()
        #vars["chart_author"] = user_name()

        chart_id = db.charts.insert(**vars)
        #lib_reports_add_default_team_responsible(chart_id)
        #lib_reports_add_default_team_publication(chart_id)

        fmt = "Chart %(chart_name)s added"
        d = dict(chart_name=chart_name)

        _log('chart.add', fmt, d)
        l = {
          'event': 'charts_change',
          'data': {'id': chart_id},
        }
        _websocket_send(event_msg(l))

        return rest_get_reports_chart().handler(chart_id)


class rest_post_reports_chart(rest_post_handler):
    def __init__(self):
        desc = [
          "Modify a chart properties",
        ]
        examples = [
          "# curl -u %(email)s -X POST -d chart_name=test -o- https://%(collector)s/init/rest/api/reports/charts/1"
        ]

        rest_post_handler.__init__(
          self,
          path="/reports/charts/<id>",
          tables=["charts"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("ReportsManager")

        if "id" in vars:
            del(vars["id"])

        q = db.charts.id == id
        chart = db(q).select().first()
        if chart is None:
            raise Exception("Chart %s not found"%str(id))

        db(q).update(**vars)

        fmt = "Chart %(chart_name)s change: %(data)s"
        d = dict(chart_name=chart.chart_name, data=beautify_change(chart, vars))

        _log('chart.change', fmt, d)
        l = {
          'event': 'charts_change',
          'data': {'id': chart.id},
        }
        _websocket_send(event_msg(l))

        ret = rest_get_reports_chart().handler(chart.id)
        ret["info"] = fmt % d
        return ret

class rest_get_reports_charts(rest_get_table_handler):
    def __init__(self):
        desc = [
          "Display reports charts list.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/charts",
        ]
        rest_get_table_handler.__init__(
          self,
          path="/reports/charts",
          tables=["charts"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.charts.id > 0
        self.set_q(q)
        return self.prepare_data(**vars)

class rest_get_reports_chart(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display report chart details.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/charts/1",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/reports/charts/<id>",
          tables=["charts"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.charts.id == id
        self.set_q(q)
        return self.prepare_data(**vars)


#
# Metrics
#
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


#
# for the report explorer and report object
#
class rest_get_report_definition(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display report details for a specific report id.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/1",
        ]
        rest_get_line_handler.__init__(
          self,
          path="/reports/<id>/definition",
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
        if "%%fset_services%%" in sql_req or "%%fset_nodenames%%" in sql_req:
            fset_id = user_fset_id()
            nodenames, svcnames = filterset_encap_query_cached(fset_id)
            sql_req = sql_req.replace("%%fset_nodenames%%", ','.join(map(lambda x: repr(x).lstrip('u'), nodenames)))
            sql_req = sql_req.replace("%%fset_services%%", ','.join(map(lambda x: repr(x).lstrip("u"), svcnames)))
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
          orderby=~db.metrics_log.date,
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

        n = db(q).count()
        if n > 500:
            skip = n // 500
            q &= (db.metrics_log.date.day() % skip) == 0

        self.set_q(q)
        data = self.prepare_data(**vars)
        data["chart_definition"] = definition
        return data

#
class rest_get_report_export(rest_get_handler):
    def __init__(self):
        desc = [
          "Export the report and its required metrics and charts dedinitions in a JSON format compatible with the import handler.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/2/export"
        ]

        rest_get_handler.__init__(
          self,
          path="/reports/<id>/export",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.reports.id == id
        report = db(q).select().first()
        if report is None:
            return {"error": "Report not found"}

        report_definition = yaml.load(report.report_yaml)
        report_data = {
          "report_name": report.report_name,
          "report_definition": report_definition
        }

        chart_ids = set([])
        metric_ids = set([])

        for s in report_definition.get("Sections", []):
            for c in s.get("Charts", []):
                if not "chart_id" in c:
                    continue
                chart_ids.add(c.get("chart_id"))
            for m in s.get("Metrics", []):
                if not "metric_id" in m:
                    continue
                metric_ids.add(m.get("metric_id"))

        q = db.charts.id.belongs(chart_ids)
        chart_rows = db(q).select()
        charts_data = []
        chart_name = {}

        for row in chart_rows:
            chart_definition = yaml.load(row.chart_yaml)
            chart_data = {
              "chart_name": row.chart_name,
              "chart_definition": chart_definition
            }
            charts_data.append(chart_data)
            chart_name[row.id] = row.chart_name

            for m in chart_definition.get("Metrics", []):
                if not "metric_id" in m:
                    continue
                metric_ids.add(m.get("metric_id"))

        q = db.metrics.id.belongs(metric_ids)
        metric_rows = db(q).select()
        metrics_data = []
        metric_name = {}
        for row in metric_rows:
            metrics_data.append({
              "metric_name": row.metric_name,
              "metric_sql": row.metric_sql,
              "metric_col_value_index": row.metric_col_value_index,
              "metric_col_instance_index": row.metric_col_instance_index,
              "metric_col_instance_label": row.metric_col_instance_label,
            })
            metric_name[row.id] = row.metric_name

        # replace chart and metric ids by their sym name reference
        for i, chart in enumerate(charts_data):
            for j, metric in enumerate(chart.get("chart_definition", {}).get("Metrics", [])):
                if "metric_id" in metric:
                    charts_data[i]["chart_definition"]["Metrics"][j]["metric_name"] = metric_name[metric["metric_id"]]

        for i, section in enumerate(report_data.get("report_definition", {}).get("Sections", [])):
            for j, metric in enumerate(section.get("Metrics", [])):
                if "metric_id" in metric:
                    report_data["report_definition"]["Sections"][i]["Metrics"][j]["metric_name"] = metric_name[metric["metric_id"]]
            for j, chart in enumerate(section.get("Charts", [])):
                if "chart_id" in chart:
                    report_data["report_definition"]["Sections"][i]["Charts"][j]["chart_name"] = chart_name[chart["chart_id"]]

        return {
          "reports": [report_data],
          "charts": charts_data,
          "metrics": metrics_data,
        }


