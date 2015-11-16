import json

class rest_get_alert_event(rest_get_line_handler):
    def __init__(self):
        desc = [
          "Display alert event on last 30 days following nodename/servicename and MD5 Id .",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/alert_event"
        ]

        rest_get_line_handler.__init__(
          self,
          path="/alert_event",
          tables=["dashboard_events"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
    	if 'md5name' not in vars:
    	    raise Exception("the md5name property is mandatory")
    	md5name = vars['md5name']

    	if 'nodename' not in vars:
    	    raise Exception("the nodename property is mandatory")
    	nodename = vars['nodename']

    	if 'svcname' not in vars:
    	    raise Exception("the svcname property is mandatory")
    	svcname = vars['svcname']

    	limit = datetime.datetime.now() - datetime.timedelta(days=30)
    	q = db.dashboard_events.dash_md5 == md5name
    	q &= db.dashboard_events.dash_nodename == nodename
    	q &= db.dashboard_events.dash_svcname == svcname
    	q &= db.dashboard_events.dash_begin > limit
    	q &= _where(None, 'dashboard_events', domain_perms(), 'dash_svcname')|_where(None, 'dashboard_events', domain_perms(), 'dash_nodename')
    	self.set_q(q)
        return self.prepare_data()
