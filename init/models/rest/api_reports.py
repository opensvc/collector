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
        report_responsible(id)

        q = db.reports.id == id
        report = db(q).select().first()
        if report is None:
            raise Exception("Report %s not found"%str(id))

        report_id = db(q).delete()

        fmt = "Report %(report_name)s deleted"
        d = dict(report_name=report.report_name)

        _log('report.del', fmt, d)
        ws_send('reports_change', {'id': report.id})

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
        lib_reports_add_default_team_responsible(report_id)
        lib_reports_add_default_team_publication(report_id)

        fmt = "Report %(report_name)s added"
        d = dict(report_name=report_name)

        _log('report.add', fmt, d)
        ws_send('reports_change', {'id': report_id})

        ret = rest_get_report().handler(report_id)
        lib_reports_add_to_git(str(report_id), ret["data"][0]["report_yaml"])

        return ret


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
        report_responsible(id)

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
        ws_send('reports_change', {'id': report.id})

        ret = rest_get_report().handler(report.id)
        lib_reports_add_to_git(str(report.id), ret["data"][0]["report_yaml"])
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
          left=db.report_team_publication.on(db.reports.id==db.report_team_publication.report_id),
          groupby=db.reports.id,
        )

    def handler(self, **vars):
        q = db.reports.id > 0
        if "Manager" not in user_groups():
            q &= db.report_team_publication.group_id.belongs(user_group_ids())
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
          left=db.report_team_publication.on(db.reports.id==db.report_team_publication.report_id),
          groupby=db.reports.id,
        )

    def handler(self, id, **vars):
        q = db.reports.id == id
        if "Manager" not in user_groups():
            q &= db.report_team_publication.group_id.belongs(user_group_ids())
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
        ws_send('charts_change', {'id': chart.id})

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
        lib_charts_add_default_team_responsible(chart_id)
        lib_charts_add_default_team_publication(chart_id)

        fmt = "Chart %(chart_name)s added"
        d = dict(chart_name=chart_name)

        _log('chart.add', fmt, d)
        ws_send('charts_change', {'id': chart_id})

        ret = rest_get_reports_chart().handler(chart_id)
        chart_yaml = ret["data"][0]["chart_yaml"]
        if chart_yaml is None:
            chart_yaml = ""
        lib_reports_add_to_git(str(chart_id), chart_yaml, otype="charts")

        return ret


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
          groupby=db.charts.id,
        )

    def handler(self, id, **vars):
        check_privilege("ReportsManager")
        chart_responsible(id)

        if "id" in vars:
            del(vars["id"])

        q = db.charts.id == id
        if "Manager" not in user_groups():
            q &= db.chart_team_publication.chart_id == db.charts.id
            q &= db.chart_team_publication.group_id.belongs(user_group_ids())
        chart = db(q).select().first()
        if chart is None:
            raise Exception("Chart %s not found"%str(id))

        db(q).update(**vars)

        fmt = "Chart %(chart_name)s change: %(data)s"
        d = dict(chart_name=chart.chart_name, data=beautify_change(chart, vars))

        _log('chart.change', fmt, d)
        ws_send('charts_change', {'id': chart.id})

        ret = rest_get_reports_chart().handler(chart.id)
        lib_reports_add_to_git(str(chart.id), ret["data"][0]["chart_yaml"], otype="charts")

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
          groupby=db.charts.id,
        )

    def handler(self, **vars):
        q = db.charts.id > 0
        if "Manager" not in user_groups():
            q &= db.chart_team_publication.chart_id == db.charts.id
            q &= db.chart_team_publication.group_id.belongs(user_group_ids())
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
        ws_send('metrics_change', {'id': metric.id})

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
        check_privilege("Manager")

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
        lib_metrics_add_default_team_publication(metric_id)

        fmt = "Metric %(metric_name)s added"
        d = dict(metric_name=metric_name)

        _log('metric.add', fmt, d)
        ws_send('metrics_change', {'id': metric_id})

        ret = rest_get_reports_metric().handler(metric_id)
        metric_sql = ret["data"][0]["metric_sql"]
        if metric_sql is None:
            metric_sql = ""
        lib_reports_add_to_git(str(metric_id), metric_sql, otype="metrics")

        return ret


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
        check_privilege("Manager")

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
        ws_send('metrics_change', {'id': metric.id})

        ret = rest_get_reports_metric().handler(metric.id)
        lib_reports_add_to_git(str(metric.id), ret["data"][0]["metric_sql"], otype="metrics")

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
          groupby=db.metrics.id,
        )

    def handler(self, **vars):
        q = db.metrics.id > 0
        if "Manager" not in user_groups():
            q &= db.metric_team_publication.metric_id == db.metrics.id
            q &= db.metric_team_publication.group_id.belongs(user_group_ids())
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
          groupby=db.metrics.id,
        )

    def handler(self, id, **vars):
        q = db.metrics.id == id
        if "Manager" not in user_groups():
            q &= db.metric_team_publication.metric_id == db.metrics.id
            q &= db.metric_team_publication.group_id.belongs(user_group_ids())
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
        if "%%fset_svc_ids%%" in sql_req or "%%fset_node_ids%%" in sql_req:
            fset_id = user_fset_id()
            node_ids, svc_ids = filterset_encap_query_id(fset_id)
            sql_req = sql_req.replace("%%fset_node_ids%%", ','.join(map(lambda x: repr(str(x)), node_ids)))
            sql_req = sql_req.replace("%%fset_svc_ids%%", ','.join(map(lambda x: repr(str(x)), svc_ids)))
        try:
            rows = db.executesql(sql_req, as_ordered_dict=True)
        except:
            rows  = []

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
#          orderby=~db.metrics_log.date,
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
            for m in s.get("children", []):
                if "metric_id" in m:
                    metric_ids.add(m.get("metric_id"))
                if "chart_id" in m:
                    chart_ids.add(m.get("chart_id"))

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
              "metric_historize": row.metric_historize,
            })
            metric_name[row.id] = row.metric_name

        # replace chart and metric ids by their sym name reference
        for i, chart in enumerate(charts_data):
            for j, metric in enumerate(chart.get("chart_definition", {}).get("Metrics", [])):
                if "metric_id" in metric:
                    if not metric["metric_id"] in metric_name:
                        del charts_data[i]["chart_definition"]["Metrics"][j]
                        continue
                    charts_data[i]["chart_definition"]["Metrics"][j]["metric_name"] = metric_name[metric["metric_id"]]

        for i, section in enumerate(report_data.get("report_definition", {}).get("Sections", [])):
            if "children" not in report_data["report_definition"]["Sections"][i]:
                report_data["report_definition"]["Sections"][i]["children"] = []

            if "Charts" in section:
                for j, chart in enumerate(section.get("Charts", [])):
                    if "chart_id" in chart:
                        if not chart["chart_id"] in chart_name:
                            del report_data["report_definition"]["Sections"][i]["Charts"][j]
                            continue
                        report_data["report_definition"]["Sections"][i]["Charts"][j]["chart_name"] = chart_name[chart["chart_id"]]
                    report_data["report_definition"]["Sections"][i]["children"].append(report_data["report_definition"]["Sections"][i]["Charts"][j])
                del section["Charts"]

            if "Metrics" in section:
                for j, metric in enumerate(section.get("Metrics", [])):
                    if "metric_id" in metric:
                        if not metric["metric_id"] in metric_name:
                            del report_data["report_definition"]["Sections"][i]["Metrics"][j]
                            continue
                        report_data["report_definition"]["Sections"][i]["Metrics"][j]["metric_name"] = metric_name[metric["metric_id"]]
                    report_data["report_definition"]["Sections"][i]["children"].append(report_data["report_definition"]["Sections"][i]["Metrics"][j])
                del section["Metrics"]

            for j, child in enumerate(section.get("children", [])):
                if "metric_id" in child:
                    if not child["metric_id"] in metric_name:
                        del report_data["report_definition"]["Sections"][i]["children"][j]
                        continue
                    report_data["report_definition"]["Sections"][i]["children"][j]["metric_name"] = metric_name[child["metric_id"]]
                if "chart_id" in child:
                    if not child["chart_id"] in chart_name:
                        del report_data["report_definition"]["Sections"][i]["children"][j]
                        continue
                    report_data["report_definition"]["Sections"][i]["children"][j]["chart_name"] = chart_name[child["chart_id"]]

        return {
          "reports": [report_data],
          "charts": charts_data,
          "metrics": metrics_data,
        }


#
class rest_post_reports_import(rest_post_handler):
    def __init__(self):
        desc = [
          "Import a report and its required metrics and charts definitions from the JSON formatted posted data.",
        ]
        examples = [
          "# curl -u %(email)s -d @/tmp/foo.json -X POST -o- https://%(collector)s/init/rest/api/reports/import"
        ]

        rest_post_handler.__init__(
          self,
          path="/reports/import",
          desc=desc,
          examples=examples,
        )

    def handler(self, reports=[], charts=[], metrics=[]):
        check_privilege("ReportsManager")
        data = {
          "info": [],
          "error": [],
        }

        metric_id = {}
        chart_id = {}

        for i, m in enumerate(metrics):
            if "metric_name" not in m:
                data["error"].append("Missing 'metric_name' key in metric %d" % i)
                continue
            q = db.metrics.metric_name == m["metric_name"]
            metric = db(q).select().first()
            if metric:
                metric_id[m["metric_name"]] = metric.id
                data["info"].append("Skip metric %s: already exists" % m["metric_name"])
            else:
                if "id" in m:
                    del(m["id"])
                metric_id[m["metric_name"]] = db.metrics.insert(**m)
                data["info"].append("Added metric %s" % m["metric_name"])
        db.commit()

        for i, m in enumerate(charts):
            if "chart_name" not in m:
                data["error"].append("Missing 'chart_name' key in chart %d" % i)
                continue
            q = db.charts.chart_name == m["chart_name"]
            chart = db(q).select().first()
            if chart:
                chart_id[m["chart_name"]] = chart.id
                data["info"].append("Skip chart %s: already exists" % m["chart_name"])
            else:
                if "id" in m:
                    del(m["id"])
                for j, metric in enumerate(m["chart_definition"].get("Metrics", [])):
                     if not "metric_name" in metric:
                         data["error"].append("Missing 'metric_name' key in metric %d of chart %d" % (j,i))
                         continue
                     m["chart_definition"]["Metrics"][j]["metric_id"] = int(metric_id[metric["metric_name"]])
                     del(m["chart_definition"]["Metrics"][j]["metric_name"])
                try:
                    m["chart_yaml"] = yaml.safe_dump(m["chart_definition"], default_flow_style=False, allow_unicode=True)
                except Exception as e:
                    data["error"].append("Error converting to yaml: %s, %s" % (str(m["chart_definition"]), str(e)))
                    continue
                del(m["chart_definition"])
                chart_id[m["chart_name"]] = db.charts.insert(**m)
                data["info"].append("Added chart %s" % m["chart_name"])
        db.commit()

        for i, m in enumerate(reports):
            if "report_name" not in m:
                data["error"].append("Missing 'report_name' key in report %d" % i)
                continue
            q = db.reports.report_name == m["report_name"]
            report = db(q).select().first()
            if report:
                data["info"].append("Skip report %s: already exists" % m["report_name"])
            else:
                if "id" in m:
                    del(m["id"])
                for j, section in enumerate(m["report_definition"].get("Sections", [])):
                    for k, child in enumerate(m["report_definition"]["Sections"][j].get("children", [])):
                         if "metric_name" in child:
                             m["report_definition"]["Sections"][j]["children"][k]["metric_id"] = int(metric_id[child["metric_name"]])
                             del(m["report_definition"]["Sections"][j]["children"][k]["metric_name"])
                         elif "chart_name" in child:
                             if child["chart_name"] not in chart_id:
                                 data["error"].append("Id of chart %s not found" % child["chart_name"])
                                 continue
                             m["report_definition"]["Sections"][j]["children"][k]["chart_id"] = int(chart_id[child["chart_name"]])
                             del(m["report_definition"]["Sections"][j]["children"][k]["chart_name"])
                         else:
                             data["error"].append("Missing 'metric_name' or 'chart_name' key in child %d of section %d of report %d" % (k, j, i))
                             del(m["report_definition"]["Sections"][j]["children"][k])
                    try:
                        m["report_yaml"] = yaml.safe_dump(m["report_definition"], default_flow_style=False, allow_unicode=True)
                    except Exception as e:
                        data["error"].append("Error converting to yaml: %s, %s" % (str(m["report_definition"]), str(e)))
                        continue
                del(m["report_definition"])
                db.reports.insert(**m)
                data["info"].append("Added report %s" % m["report_name"])
        db.commit()

        return data

#
class rest_get_reports_metric_am_i_responsible(rest_get_handler):
    def __init__(self):
        desc = [
          "- return true if the requester is responsible for this metric.",
          "- only Manager members are responsible for metrics.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/metrics/1/am_i_responsible",
        ]
        rest_get_handler.__init__(
          self,
          path="/reports/metrics/<id>/am_i_responsible",
          desc=desc,
          examples=examples,
        )

    def handler(self, chart_id, **vars):
        try:
            check_privilege("Manager")
            return dict(data=True)
        except:
            return dict(data=False)

class rest_get_reports_chart_am_i_responsible(rest_get_handler):
    def __init__(self):
        desc = [
          "- return true if the requester is responsible for this chart.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/charts/1/am_i_responsible",
        ]
        rest_get_handler.__init__(
          self,
          path="/reports/charts/<id>/am_i_responsible",
          desc=desc,
          examples=examples,
        )

    def handler(self, chart_id, **vars):
        try:
            chart_id = get_chart_id(chart_id)
            chart_responsible(chart_id)
            return dict(data=True)
        except:
            return dict(data=False)

class rest_get_report_am_i_responsible(rest_get_handler):
    def __init__(self):
        desc = [
          "- return true if the requester is responsible for this report.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/1/am_i_responsible",
        ]
        rest_get_handler.__init__(
          self,
          path="/reports/<id>/am_i_responsible",
          desc=desc,
          examples=examples,
        )

    def handler(self, report_id, **vars):
        try:
            report_id = get_report_id(report_id)
            report_responsible(report_id)
            return dict(data=True)
        except:
            return dict(data=False)

#
# metrics revisions
#
class rest_post_reports_metric_rollback(rest_post_handler):
    def __init__(self):
        desc = [
          "Restore an old revision of a metric",
        ]
        examples = [
          "# curl -u %(email)s -X POST -o- https://%(collector)s/init/rest/api/reports/metrics/1/rollback/9a26e8e40d9d7a7e585ac8ccb6bc01f70f68b710"
        ]

        rest_post_handler.__init__(
          self,
          path="/reports/metrics/<id>/rollback/<cid>",
          desc=desc,
          examples=examples,
        )

    def handler(self, metric_id, cid, **vars):
        check_privilege("ReportsManager")
        metric_responsible(metric_id)
        lib_reports_rollback(metric_id, cid, otype="metrics")
        return

class rest_get_reports_metric_revision(rest_get_handler):
    def __init__(self):
        desc = [
          "Return the metric content for the given revision.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/metrics/1/revision/1234",
        ]
        rest_get_handler.__init__(
          self,
          path="/reports/metrics/<id>/revisions/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, metric_id, cid, **vars):
        r = []
        q = db.metrics.id == int(metric_id)
        if "Manager" not in user_groups():
            q &= db.metrics.id == db.metric_team_publication.metric_id
            q &= db.metric_team_publication.group_id.belongs(user_group_ids())
        if db(q).count():
            r =  lib_reports_revision(metric_id, cid, otype="metrics")
        return r

class rest_get_reports_metric_revisions(rest_get_handler):
    def __init__(self):
        desc = [
          "Return the metric revisions.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/metrics/1/revisions",
        ]
        rest_get_handler.__init__(
          self,
          path="/reports/metrics/<id>/revisions",
          desc=desc,
          examples=examples,
        )

    def handler(self, metric_id, **vars):
        r = []
        q = db.metrics.id == int(metric_id)
        if "Manager" not in user_groups():
            q &= db.metrics.id == db.metric_team_publication.metric_id
            q &= db.metric_team_publication.group_id.belongs(user_group_ids())
        if db(q).count():
            r =  lib_reports_revisions(metric_id, otype="metrics")
        return r

class rest_get_reports_metric_diff(rest_get_handler):
    def __init__(self):
        desc = [
          "Show the commit diff, or differences between <cid> and <other> if"
          "other is set",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/metrics/1/diff/9a26e8e40d9d7a7e585ac8ccb6bc01f70f68b710",
        ]
        rest_get_handler.__init__(
          self,
          path="/reports/metrics/<id>/diff/<cid>",
          desc=desc,
          examples=examples,
        )

    def handler(self, metric_id, cid, other=None, **vars):
        r = []
        q = db.metrics.id == int(metric_id)
        if "Manager" not in user_groups():
            q &= db.metrics.id == db.metric_team_publication.metric_id
            q &= db.metric_team_publication.group_id.belongs(user_group_ids())
        if db(q).count():
            r =  lib_reports_diff(metric_id, cid, other=other, otype="metrics")
        return r

#
# charts revisions
#
class rest_post_reports_chart_rollback(rest_post_handler):
    def __init__(self):
        desc = [
          "Restore an old revision of a chart",
        ]
        examples = [
          "# curl -u %(email)s -X POST -o- https://%(collector)s/init/rest/api/reports/charts/1/rollback/9a26e8e40d9d7a7e585ac8ccb6bc01f70f68b710"
        ]

        rest_post_handler.__init__(
          self,
          path="/reports/charts/<id>/rollback/<cid>",
          desc=desc,
          examples=examples,
        )

    def handler(self, chart_id, cid, **vars):
        check_privilege("ReportsManager")
        chart_responsible(chart_id)
        lib_reports_rollback(chart_id, cid, otype="charts")
        return

class rest_get_reports_chart_revision(rest_get_handler):
    def __init__(self):
        desc = [
          "Return the chart content for the given revision.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/charts/1/revision/1234",
        ]
        rest_get_handler.__init__(
          self,
          path="/reports/charts/<id>/revisions/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, chart_id, cid, **vars):
        r = []
        q = db.charts.id == int(chart_id)
        if "Manager" not in user_groups():
            q &= db.charts.id == db.chart_team_publication.chart_id
            q &= db.chart_team_publication.group_id.belongs(user_group_ids())
        if db(q).count():
            r =  lib_reports_revision(chart_id, cid, otype="charts")
        return r

class rest_get_reports_chart_revisions(rest_get_handler):
    def __init__(self):
        desc = [
          "Return the chart revisions.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/charts/1/revisions",
        ]
        rest_get_handler.__init__(
          self,
          path="/reports/charts/<id>/revisions",
          desc=desc,
          examples=examples,
        )

    def handler(self, chart_id, **vars):
        r = []
        q = db.charts.id == int(chart_id)
        if "Manager" not in user_groups():
            q &= db.charts.id == db.chart_team_publication.chart_id
            q &= db.chart_team_publication.group_id.belongs(user_group_ids())
        if db(q).count():
            r =  lib_reports_revisions(chart_id, otype="charts")
        return r

class rest_get_reports_chart_diff(rest_get_handler):
    def __init__(self):
        desc = [
          "Show the commit diff, or differences between <cid> and <other> if"
          "other is set",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/charts/1/diff/9a26e8e40d9d7a7e585ac8ccb6bc01f70f68b710",
        ]
        rest_get_handler.__init__(
          self,
          path="/reports/charts/<id>/diff/<cid>",
          desc=desc,
          examples=examples,
        )

    def handler(self, chart_id, cid, other=None, **vars):
        r = []
        q = db.charts.id == int(chart_id)
        if "Manager" not in user_groups():
            q &= db.charts.id == db.chart_team_publication.chart_id
            q &= db.chart_team_publication.group_id.belongs(user_group_ids())
        if db(q).count():
            r =  lib_reports_diff(chart_id, cid, other=other, otype="charts")
        return r

#
# reports revisions
#
class rest_post_report_rollback(rest_post_handler):
    def __init__(self):
        desc = [
          "Restore an old revision of a report",
        ]
        examples = [
          "# curl -u %(email)s -X POST -o- https://%(collector)s/init/rest/api/reports/1/rollback/9a26e8e40d9d7a7e585ac8ccb6bc01f70f68b710"
        ]

        rest_post_handler.__init__(
          self,
          path="/reports/<id>/rollback/<cid>",
          desc=desc,
          examples=examples,
        )

    def handler(self, report_id, cid, **vars):
        check_privilege("ReportsManager")
        report_responsible(report_id)
        lib_reports_rollback(report_id, cid)
        return

class rest_get_report_revision(rest_get_handler):
    def __init__(self):
        desc = [
          "Return the report content for the given revision.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/1/revision/1234",
        ]
        rest_get_handler.__init__(
          self,
          path="/reports/<id>/revisions/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, report_id, cid, **vars):
        r = []
        q = db.reports.id == int(report_id)
        if "Manager" not in user_groups():
            q &= db.reports.id == db.report_team_publication.report_id
            q &= db.report_team_publication.group_id.belongs(user_group_ids())
        if db(q).count():
            r =  lib_reports_revision(report_id, cid)
        return r

class rest_get_report_revisions(rest_get_handler):
    def __init__(self):
        desc = [
          "Return the report revisions.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/1/revisions",
        ]
        rest_get_handler.__init__(
          self,
          path="/reports/<id>/revisions",
          desc=desc,
          examples=examples,
        )

    def handler(self, report_id, **vars):
        r = []
        q = db.reports.id == int(report_id)
        if "Manager" not in user_groups():
            q &= db.reports.id == db.report_team_publication.report_id
            q &= db.report_team_publication.group_id.belongs(user_group_ids())
        if db(q).count():
            r =  lib_reports_revisions(report_id)
        return r

class rest_get_report_diff(rest_get_handler):
    def __init__(self):
        desc = [
          "Show the commit diff, or differences between <cid> and <other> if"
          "other is set",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/1/diff/9a26e8e40d9d7a7e585ac8ccb6bc01f70f68b710",
        ]
        rest_get_handler.__init__(
          self,
          path="/reports/<id>/diff/<cid>",
          desc=desc,
          examples=examples,
        )

    def handler(self, report_id, cid, other=None, **vars):
        r = []
        q = db.reports.id == int(report_id)
        if "Manager" not in user_groups():
            q &= db.reports.id == db.report_team_publication.report_id
            q &= db.report_team_publication.group_id.belongs(user_group_ids())
        if db(q).count():
            r =  lib_reports_diff(report_id, cid, other=other)
        return r

#
# Reports responsibles and publications
#
class rest_get_report_responsibles(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List groups responsible for the provisioning template.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/report/1/responsibles"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/reports/<id>/responsibles",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, report_id, **vars):
        report_id = get_report_id(report_id)
        report_published(report_id)
        q = db.report_team_responsible.report_id == report_id
        q &= db.report_team_responsible.group_id == db.auth_group.id
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data

class rest_delete_report_responsible(rest_delete_handler):
    def __init__(self):
        desc = [
          "Remove a provisioning template responsible group",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/reports/1/responsibles/2"
        ]

        rest_delete_handler.__init__(
          self,
          path="/reports/<id>/responsibles/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, report_id, group_id, **vars):
        check_privilege("ReportsManager")
        report_id = get_report_id(report_id)
        report_responsible(report_id)
        q = db.report_team_responsible.report_id == report_id
        q &= db.report_team_responsible.group_id == group_id

        fmt = "Report %(report_id)s responsibility to group %(group_id)s removed"
        d = dict(report_id=str(report_id), group_id=str(group_id))

        row = db(q).select().first()
        if row is None:
            return dict(info="Report %(report_id)s responsibility to group %(group_id)s already removed" % d)

        db(q).delete()

        _log(
          'report.responsible.delete',
          fmt,
          d
        )
        ws_send('report_responsible_change', {'id': report_id})

        return dict(info=fmt%d)

class rest_delete_reports_responsibles(rest_delete_handler):
    def __init__(self):
        desc = [
          "Remove responsible groups from report",
        ]
        examples = [
          """# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/reports_responsibles?filters[]="report_id 1" """
        ]

        rest_delete_handler.__init__(
          self,
          path="/reports_responsibles",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "report_id" in vars:
            raise Exception("The 'report_id' key is mandatory")
        report_id = vars.get("report_id")
        del(vars["report_id"])

        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_delete_report_responsible().handler(report_id, group_id, **vars)

class rest_post_report_responsible(rest_post_handler):
    def __init__(self):
        desc = [
          "Add a provisioning template responsible group",
        ]
        examples = [
          "# curl -u %(email)s -X POST -o- https://%(collector)s/init/rest/api/reports/1/responsibles/2"
        ]

        rest_post_handler.__init__(
          self,
          path="/reports/<id>/responsibles/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, report_id, group_id, **vars):
        check_privilege("ReportsManager")
        report_id = get_report_id(report_id)
        report_responsible(report_id)

        try:
            id = int(group_id)
            q = db.auth_group.id == group_id
        except:
            q = db.auth_group.role == group_id
        group = db(q).select().first()
        if group is None:
            raise Exception("Group %s does not exist" % str(group_id))

        fmt = "Report %(report_id)s responsibility to group %(group_id)s added"
        d = dict(report_id=str(report_id), group_id=str(group_id))

        q = db.report_team_responsible.report_id == report_id
        q &= db.report_team_responsible.group_id == group.id
        row = db(q).select().first()
        if row is not None:
            return dict(info="Report %(report_id)s responsibility to group %(group_id)s already added" % d)

        db.report_team_responsible.insert(report_id=report_id, group_id=group.id)

        _log(
          'report.responsible.add',
          fmt,
          d
        )
        ws_send('report_responsible_change', {'id': report_id})

        return dict(info=fmt%d)

class rest_post_reports_responsibles(rest_post_handler):
    def __init__(self):
        desc = [
          "Add responsible groups to report",
        ]
        examples = [
          "# curl -u %(email)s --header 'Content-Type: application/json' -d @/tmp/data.json -X POST -o- https://%(collector)s/init/rest/api/reports_responsibles"
        ]

        rest_post_handler.__init__(
          self,
          path="/reports_responsibles",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "report_id" in vars:
            raise Exception("The 'report_id' key is mandatory")
        report_id = vars.get("report_id")
        del(vars["report_id"])

        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_post_report_responsible().handler(report_id, group_id, **vars)


class rest_get_report_publications(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List groups publication for the provisioning template.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/report/1/publications"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/reports/<id>/publications",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, report_id, **vars):
        report_published(report_id)
        report_id = get_report_id(report_id)
        q = db.report_team_publication.report_id == report_id
        q &= db.report_team_publication.group_id == db.auth_group.id
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data

class rest_delete_report_publication(rest_delete_handler):
    def __init__(self):
        desc = [
          "Remove a provisioning template publication group",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/reports/1/publications/2"
        ]

        rest_delete_handler.__init__(
          self,
          path="/reports/<id>/publications/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, report_id, group_id, **vars):
        check_privilege("ReportsManager")
        report_id = get_report_id(report_id)
        report_responsible(report_id)
        q = db.report_team_publication.report_id == report_id
        q &= db.report_team_publication.group_id == group_id

        fmt = "Report %(report_id)s publication to group %(group_id)s removed"
        d = dict(report_id=str(report_id), group_id=str(group_id))

        row = db(q).select().first()
        if row is None:
            return dict(info="Report %(report_id)s publication to group %(group_id)s already removed" % d)

        db(q).delete()

        _log(
          'report.publication.delete',
          fmt,
          d
        )
        ws_send('report_publication_change', {'id': report_id})

        return dict(info=fmt%d)

class rest_delete_reports_publications(rest_delete_handler):
    def __init__(self):
        desc = [
          "Remove publication groups from report",
        ]
        examples = [
          """# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/reports_publications?filters[]="report_id 1" """
        ]

        rest_delete_handler.__init__(
          self,
          path="/reports_publications",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "report_id" in vars:
            raise Exception("The 'report_id' key is mandatory")
        report_id = vars.get("report_id")
        del(vars["report_id"])

        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_delete_report_publication().handler(report_id, group_id, **vars)

class rest_post_report_publication(rest_post_handler):
    def __init__(self):
        desc = [
          "Add a provisioning template publication group",
        ]
        examples = [
          "# curl -u %(email)s -X POST -o- https://%(collector)s/init/rest/api/reports/1/publications/2"
        ]

        rest_post_handler.__init__(
          self,
          path="/reports/<id>/publications/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, report_id, group_id, **vars):
        check_privilege("ReportsManager")
        report_id = get_report_id(report_id)
        report_responsible(report_id)

        try:
            id = int(group_id)
            q = db.auth_group.id == group_id
        except:
            q = db.auth_group.role == group_id
        group = db(q).select().first()
        if group is None:
            raise Exception("Group %s does not exist" % str(group_id))

        fmt = "Report %(report_id)s publication to group %(group_id)s added"
        d = dict(report_id=str(report_id), group_id=str(group_id))

        q = db.report_team_publication.report_id == report_id
        q &= db.report_team_publication.group_id == group.id
        row = db(q).select().first()
        if row is not None:
            return dict(info="Report %(report_id)s publication to group %(group_id)s already added" % d)

        db.report_team_publication.insert(report_id=report_id, group_id=group.id)

        _log(
          'report.publication.add',
          fmt,
          d
        )
        ws_send('report_publication_change', {'id': report_id})

        return dict(info=fmt%d)

class rest_post_reports_publications(rest_post_handler):
    def __init__(self):
        desc = [
          "Add publication groups to report",
        ]
        examples = [
          "# curl -u %(email)s --header 'Content-Type: application/json' -d @/tmp/data.json -X POST -o- https://%(collector)s/init/rest/api/reports_publications"
        ]

        rest_post_handler.__init__(
          self,
          path="/reports_publications",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "report_id" in vars:
            raise Exception("The 'report_id' key is mandatory")
        report_id = vars.get("report_id")
        del(vars["report_id"])

        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_post_report_publication().handler(report_id, group_id, **vars)

#
# Charts responsibles and publications
#
class rest_get_reports_chart_responsibles(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List groups responsible for the provisioning template.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/chart/1/responsibles"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/reports/charts/<id>/responsibles",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, chart_id, **vars):
        chart_id = get_chart_id(chart_id)
        chart_published(chart_id)
        q = db.chart_team_responsible.chart_id == chart_id
        q &= db.chart_team_responsible.group_id == db.auth_group.id
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data

class rest_delete_reports_chart_responsible(rest_delete_handler):
    def __init__(self):
        desc = [
          "Remove a provisioning template responsible group",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/reports/charts/1/responsibles/2"
        ]

        rest_delete_handler.__init__(
          self,
          path="/reports/charts/<id>/responsibles/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, chart_id, group_id, **vars):
        check_privilege("ChartsManager")
        chart_id = get_chart_id(chart_id)
        chart_responsible(chart_id)
        q = db.chart_team_responsible.chart_id == chart_id
        q &= db.chart_team_responsible.group_id == group_id

        fmt = "Chart %(chart_id)s responsibility to group %(group_id)s removed"
        d = dict(chart_id=str(chart_id), group_id=str(group_id))

        row = db(q).select().first()
        if row is None:
            return dict(info="Chart %(chart_id)s responsibility to group %(group_id)s already removed" % d)

        db(q).delete()

        _log(
          'chart.responsible.delete',
          fmt,
          d
        )
        ws_send('chart_responsible_change', {'id': chart_id})

        return dict(info=fmt%d)

class rest_delete_reports_charts_responsibles(rest_delete_handler):
    def __init__(self):
        desc = [
          "Remove responsible groups from chart",
        ]
        examples = [
          """# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/reports/charts_responsibles?filters[]="chart_id 1" """
        ]

        rest_delete_handler.__init__(
          self,
          path="/reports/charts_responsibles",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "chart_id" in vars:
            raise Exception("The 'chart_id' key is mandatory")
        chart_id = vars.get("chart_id")
        del(vars["chart_id"])

        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_delete_reports_chart_responsible().handler(chart_id, group_id, **vars)

class rest_post_reports_chart_responsible(rest_post_handler):
    def __init__(self):
        desc = [
          "Add a provisioning template responsible group",
        ]
        examples = [
          "# curl -u %(email)s -X POST -o- https://%(collector)s/init/rest/api/reports/charts/1/responsibles/2"
        ]

        rest_post_handler.__init__(
          self,
          path="/reports/charts/<id>/responsibles/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, chart_id, group_id, **vars):
        check_privilege("ChartsManager")
        chart_id = get_chart_id(chart_id)
        chart_responsible(chart_id)

        try:
            id = int(group_id)
            q = db.auth_group.id == group_id
        except:
            q = db.auth_group.role == group_id
        group = db(q).select().first()
        if group is None:
            raise Exception("Group %s does not exist" % str(group_id))

        fmt = "Chart %(chart_id)s responsibility to group %(group_id)s added"
        d = dict(chart_id=str(chart_id), group_id=str(group_id))

        q = db.chart_team_responsible.chart_id == chart_id
        q &= db.chart_team_responsible.group_id == group.id
        row = db(q).select().first()
        if row is not None:
            return dict(info="Chart %(chart_id)s responsibility to group %(group_id)s already added" % d)

        chart_id = db.chart_team_responsible.insert(chart_id=chart_id, group_id=group.id)

        _log(
          'chart.responsible.add',
          fmt,
          d
        )
        ws_send('chart_responsible_change', {'id': chart_id})

        return dict(info=fmt%d)

class rest_post_reports_charts_responsibles(rest_post_handler):
    def __init__(self):
        desc = [
          "Add responsible groups to chart",
        ]
        examples = [
          "# curl -u %(email)s --header 'Content-Type: application/json' -d @/tmp/data.json -X POST -o- https://%(collector)s/init/rest/api/reports/charts_responsibles"
        ]

        rest_post_handler.__init__(
          self,
          path="/reports/charts_responsibles",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "chart_id" in vars:
            raise Exception("The 'chart_id' key is mandatory")
        chart_id = vars.get("chart_id")
        del(vars["chart_id"])

        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_post_reports_chart_responsible().handler(chart_id, group_id, **vars)


class rest_get_reports_chart_publications(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List groups publication for the provisioning template.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/chart/1/publications"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/reports/charts/<id>/publications",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, chart_id, **vars):
        chart_published(chart_id)
        chart_id = get_chart_id(chart_id)
        q = db.chart_team_publication.chart_id == chart_id
        q &= db.chart_team_publication.group_id == db.auth_group.id
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data

class rest_delete_reports_chart_publication(rest_delete_handler):
    def __init__(self):
        desc = [
          "Remove a provisioning template publication group",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/reports/charts/1/publications/2"
        ]

        rest_delete_handler.__init__(
          self,
          path="/reports/charts/<id>/publications/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, chart_id, group_id, **vars):
        check_privilege("ChartsManager")
        chart_id = get_chart_id(chart_id)
        chart_responsible(chart_id)
        q = db.chart_team_publication.chart_id == chart_id
        q &= db.chart_team_publication.group_id == group_id

        fmt = "Chart %(chart_id)s publication to group %(group_id)s removed"
        d = dict(chart_id=str(chart_id), group_id=str(group_id))

        row = db(q).select().first()
        if row is None:
            return dict(info="Chart %(chart_id)s publication to group %(group_id)s already removed" % d)

        db(q).delete()

        _log(
          'chart.publication.delete',
          fmt,
          d
        )
        ws_send('chart_publication_change', {'id': chart_id})

        return dict(info=fmt%d)

class rest_delete_reports_charts_publications(rest_delete_handler):
    def __init__(self):
        desc = [
          "Remove publication groups from chart",
        ]
        examples = [
          """# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/reports/charts_publications?filters[]="chart_id 1" """
        ]

        rest_delete_handler.__init__(
          self,
          path="/reports/charts_publications",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "chart_id" in vars:
            raise Exception("The 'chart_id' key is mandatory")
        chart_id = vars.get("chart_id")
        del(vars["chart_id"])

        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_delete_reports_chart_publication().handler(chart_id, group_id, **vars)

class rest_post_reports_chart_publication(rest_post_handler):
    def __init__(self):
        desc = [
          "Add a provisioning template publication group",
        ]
        examples = [
          "# curl -u %(email)s -X POST -o- https://%(collector)s/init/rest/api/reports/charts/1/publications/2"
        ]

        rest_post_handler.__init__(
          self,
          path="/reports/charts/<id>/publications/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, chart_id, group_id, **vars):
        check_privilege("ChartsManager")
        chart_id = get_chart_id(chart_id)
        chart_responsible(chart_id)

        try:
            id = int(group_id)
            q = db.auth_group.id == group_id
        except:
            q = db.auth_group.role == group_id
        group = db(q).select().first()
        if group is None:
            raise Exception("Group %s does not exist" % str(group_id))

        fmt = "Chart %(chart_id)s publication to group %(group_id)s added"
        d = dict(chart_id=str(chart_id), group_id=str(group_id))

        q = db.chart_team_publication.chart_id == chart_id
        q &= db.chart_team_publication.group_id == group.id
        row = db(q).select().first()
        if row is not None:
            return dict(info="Chart %(chart_id)s publication to group %(group_id)s already added" % d)

        db.chart_team_publication.insert(chart_id=chart_id, group_id=group.id)

        _log(
          'chart.publication.add',
          fmt,
          d
        )
        ws_send('chart_publication_change', {'id': chart_id})

        return dict(info=fmt%d)

class rest_post_reports_charts_publications(rest_post_handler):
    def __init__(self):
        desc = [
          "Add publication groups to chart",
        ]
        examples = [
          "# curl -u %(email)s --header 'Content-Type: application/json' -d @/tmp/data.json -X POST -o- https://%(collector)s/init/rest/api/reports/charts_publications"
        ]

        rest_post_handler.__init__(
          self,
          path="/reports/charts_publications",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "chart_id" in vars:
            raise Exception("The 'chart_id' key is mandatory")
        chart_id = vars.get("chart_id")
        del(vars["chart_id"])

        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_post_reports_chart_publication().handler(chart_id, group_id, **vars)

#
# Metrics publications
#
class rest_get_reports_metric_publications(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List groups publication for the provisioning template.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/metric/1/publications"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/reports/metrics/<id>/publications",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, metric_id, **vars):
        metric_published(metric_id)
        metric_id = get_metric_id(metric_id)
        q = db.metric_team_publication.metric_id == metric_id
        q &= db.metric_team_publication.group_id == db.auth_group.id
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data

class rest_delete_reports_metric_publication(rest_delete_handler):
    def __init__(self):
        desc = [
          "Remove a provisioning template publication group",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/reports/metrics/1/publications/2"
        ]

        rest_delete_handler.__init__(
          self,
          path="/reports/metrics/<id>/publications/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, metric_id, group_id, **vars):
        check_privilege("Manager")
        metric_id = get_metric_id(metric_id)
        q = db.metric_team_publication.metric_id == metric_id
        q &= db.metric_team_publication.group_id == group_id

        fmt = "Metric %(metric_id)s publication to group %(group_id)s removed"
        d = dict(metric_id=str(metric_id), group_id=str(group_id))

        row = db(q).select().first()
        if row is None:
            return dict(info="Metric %(metric_id)s publication to group %(group_id)s already removed" % d)

        db(q).delete()

        _log(
          'metric.publication.delete',
          fmt,
          d
        )
        ws_send('metric_publication_change', {'id': metric_id})

        return dict(info=fmt%d)

class rest_delete_reports_metrics_publications(rest_delete_handler):
    def __init__(self):
        desc = [
          "Remove publication groups from metric",
        ]
        examples = [
          """# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/reports/metrics_publications?filters[]="metric_id 1" """
        ]

        rest_delete_handler.__init__(
          self,
          path="/reports/metrics_publications",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "metric_id" in vars:
            raise Exception("The 'metric_id' key is mandatory")
        metric_id = vars.get("metric_id")
        del(vars["metric_id"])

        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_delete_reports_metric_publication().handler(metric_id, group_id, **vars)

class rest_post_reports_metric_publication(rest_post_handler):
    def __init__(self):
        desc = [
          "Add a provisioning template publication group",
        ]
        examples = [
          "# curl -u %(email)s -X POST -o- https://%(collector)s/init/rest/api/reports/metrics/1/publications/2"
        ]

        rest_post_handler.__init__(
          self,
          path="/reports/metrics/<id>/publications/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, metric_id, group_id, **vars):
        check_privilege("Manager")
        metric_id = get_metric_id(metric_id)

        try:
            id = int(group_id)
            q = db.auth_group.id == group_id
        except:
            q = db.auth_group.role == group_id
        group = db(q).select().first()
        if group is None:
            raise Exception("Group %s does not exist" % str(group_id))

        fmt = "Metric %(metric_id)s publication to group %(group_id)s added"
        d = dict(metric_id=str(metric_id), group_id=str(group_id))

        q = db.metric_team_publication.metric_id == metric_id
        q &= db.metric_team_publication.group_id == group.id
        row = db(q).select().first()
        if row is not None:
            return dict(info="Metric %(metric_id)s publication to group %(group_id)s already added" % d)

        db.metric_team_publication.insert(metric_id=metric_id, group_id=group.id)

        _log(
          'metric.publication.add',
          fmt,
          d
        )
        ws_send('metric_publication_change', {'id': metric_id})

        return dict(info=fmt%d)

class rest_post_reports_metrics_publications(rest_post_handler):
    def __init__(self):
        desc = [
          "Add publication groups to metric",
        ]
        examples = [
          "# curl -u %(email)s --header 'Content-Type: application/json' -d @/tmp/data.json -X POST -o- https://%(collector)s/init/rest/api/reports/metrics_publications"
        ]

        rest_post_handler.__init__(
          self,
          path="/reports/metrics_publications",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "metric_id" in vars:
            raise Exception("The 'metric_id' key is mandatory")
        metric_id = vars.get("metric_id")
        del(vars["metric_id"])

        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_post_reports_metric_publication().handler(metric_id, group_id, **vars)


