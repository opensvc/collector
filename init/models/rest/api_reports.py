
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
        #q = db.reports_user.user_id == auth.user_id
        q = db.reports.id > 0
        result = db(q).select(db.reports.id,
                            db.reports.report_name)

        return dict(data=result)

class rest_get_report(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display report details for a specific report id.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/id",
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
          return dict(info="No report found.")

        import yaml
        d = yaml.load(data.report_yaml)

        return dict(data=d)

class rest_get_metrics(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display metric for a specific metric id.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/metrics/id",
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
        data = db(q).select().first()
        
        if (data == None):
          return dict(info="No metrics found.")
        
        sql_req = data.metric_sql
        result = db.executesql(sql_req,as_dict = True)

        return dict(data=result,metric_id=id)

class rest_get_charts(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display charts data for a specific chart id.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/reports/charts/id",
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
        data = db(q).select(db.charts.ALL).first()
        
        if (data == None):
          return dict(info="No charts found.")
        
        import yaml
        d = yaml.load(data.chart_yaml)

        return dict(data=d)