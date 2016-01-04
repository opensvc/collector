function group_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid);
	o.options = options

	o.init = function() {
		o.info_id = o.div.find("#id");
		o.info_description = o.div.find("#description");
		o.info_privilege = o.div.find("#privilege");
		o.info_users_title = o.div.find("#users_title");
		o.info_users = o.div.find("#users");
		o.info_nodes_title = o.div.find("#nodes_title");
		o.info_nodes = o.div.find("#nodes");
		o.info_apps_title = o.div.find("#apps_title");
		o.info_apps = o.div.find("#apps");
		o.info_services_title = o.div.find("#services_title");
		o.info_services = o.div.find("#services");

		o.load_group()
	}

	o.load_group = function() {
		services_osvcgetrest("R_GROUP", [o.options.group_id], "", function(jd) {
			if (!jd.data || (jd.data.length == 0)) {
				return
			}
			var data = jd.data[0]
			o.info_description.html(data.description);
			o.info_id.html(data.id);

			// nodes
			if (data.privilege == true) {
				o.info_privilege.attr('class', 'toggle-on');
			} else {
				o.info_privilege.attr('class','toggle-off');
			}

			services_osvcgetrest("R_NODES", "", {"limit": 50, "props": "nodename", "filters": ["team_responsible "+data.role]}, function(jd) {
				if (!jd.data) {
					return
				}
				o.info_nodes_title.text(i18n.t("group_properties.nodes", {"n": jd.meta.total}))
				for (var i=0; i<jd.data.length; i++) {
					var e = $("<span style='display:inline-block;padding:0 0.2em'></span>")
					e.text(jd.data[i].nodename)
					o.info_nodes.append(e)
				}
				if (jd.meta.total > jd.meta.count) {
					var e = $("<span></span>")
					e.text("...")
					o.info_nodes.append(e)
				}
			})
			services_osvcgetrest("R_GROUP_USERS", [data.id], {"limit": 50, "props": "first_name,last_name"}, function(jd) {
				if (!jd.data) {
					return
				}
				o.info_users_title.text(i18n.t("group_properties.users", {"n": jd.meta.total}))
				for (var i=0; i<jd.data.length; i++) {
					var e = $("<span style='display:inline-block;padding:0 0.2em'></span>")
					e.text(jd.data[i].first_name + " " + jd.data[i].last_name)
					o.info_users.append(e)
				}
				if (jd.meta.total > jd.meta.count) {
					var e = $("<span></span>")
					e.text("...")
					o.info_users.append(e)
				}
			})
			services_osvcgetrest("R_GROUP_APPS", [data.id], {"limit": 50, "props": "app"}, function(jd) {
				if (!jd.data) {
					return
				}
				o.info_apps_title.text(i18n.t("group_properties.apps", {"n": jd.meta.total}))
				for (var i=0; i<jd.data.length; i++) {
					var e = $("<span style='display:inline-block;padding:0 0.2em'></span>")
					e.text(jd.data[i].app)
					o.info_apps.append(e)
				}
				if (jd.meta.total > jd.meta.count) {
					var e = $("<span></span>")
					e.text("...")
					o.info_apps.append(e)
				}
			})
			services_osvcgetrest("R_GROUP_SERVICES", [data.id], {"limit": 50, "props": "svc_name"}, function(jd) {
				if (!jd.data) {
					return
				}
				o.info_services_title.text(i18n.t("group_properties.services", {"n": jd.meta.total}))
				for (var i=0; i<jd.data.length; i++) {
					var e = $("<span style='display:inline-block;padding:0 0.2em'></span>")
					e.text(jd.data[i].svc_name)
					o.info_services.append(e)
				}
				if (jd.meta.total > jd.meta.count) {
					var e = $("<span></span>")
					e.text("...")
					o.info_services.append(e)
				}
			})

			// modifications for privileged user
			if (services_ismemberof(["Manager", "UserManager"])) {
				o.info_privilege.addClass("clickable")
				o.info_privilege.bind("click", function (event) {
					o.toggle_privilege(this)
				})
			}

		})

	}

	o.toggle_privilege = function() {
		if (o.info_privilege.hasClass("toggle-on")) {
			var data = {privilege: false}
		} else {
			var data = {privilege: true}
		}
		services_osvcpostrest("R_GROUP", [o.options.group_id], "", data, function(jd) {
			if (jd.error) {
				return
			}
			if (jd.data[0].privilege == false) {
				o.info_privilege.removeClass("toggle-on").addClass("toggle-off")
			} else {
				o.info_privilege.removeClass("toggle-off").addClass("toggle-on")
			}
		},
		function() {}
	)}

	o.div.load("/init/static/views/group_properties.html", function() {
		o.div.i18n()
		o.init()
	})

	return o

}
