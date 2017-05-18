//
// group
//
function group_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.org
	o.options.icon = "guys16"
	o.link = {
		"fn": arguments.callee.name,
		"title": "link."+arguments.callee.name,
		"title_args": {
			"type": "group",
			"name": o.options.group_name
		}
	}

	o.load(function(){
		var i = 0
		if (!("group_id" in o.options) && ("group_name" in o.options)) {
			services_osvcgetrest("R_GROUPS", "", {"filters": ["role "+o.options.group_name]}, function(jd) {
				var group = jd.data[0]
				o.options.group_id = group.id
				o._load()
			})
		} else {
			o._load()
		}
	})

	o._load = function() {
		o.closetab.text(o.options.group_name ? o.options.group_name : o.options.group_id)

		// tab properties
		i = o.register_tab({
			"title": "node_tabs.properties",
			"title_class": "icon guys16"
		})
		o.tabs[i].callback = function(divid) {
			group_properties(divid, o.options)
		}

		// tab hidden menu entries
		i = o.register_tab({
			"title": "group_tabs.hidden_menu_entries",
			"title_class": "icon menu16"
		})
		o.tabs[i].callback = function(divid) {
			group_hidden_menu_entries(divid, o.options)
		}

		o.set_tab(o.options.tab)
	}
	return o
}

function group_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "link."+arguments.callee.name,
		"title_args": {
			"type": "group",
			"name": o.options.group_name
		}
	}

	o.init = function() {
		osvc_tools(o.div, {
			"link": o.link
		})
		o.info_id = o.div.find("#id")
		o.info_role = o.div.find("#role")
		o.info_description = o.div.find("#description")
		o.info_privilege = o.div.find("#privilege")
		o.info_users_title = o.div.find("#users_title")
		o.info_users = o.div.find("#users")
		o.info_nodes_title = o.div.find("#nodes_title")
		o.info_nodes = o.div.find("#nodes")
		o.info_apps_title = o.div.find("#apps_title")
		o.info_apps = o.div.find("#apps")
		o.info_services_title = o.div.find("#services_title")
		o.info_services = o.div.find("#services")

		o.load_group()
	}

	o.load_group = function() {
		services_osvcgetrest("R_GROUP", [o.options.group_id], "", function(jd) {
			if (!jd.data || (jd.data.length == 0)) {
				return
			}
			var data = jd.data[0]
			o.info_privilege.html(data.privilege)
			o.info_role.html(data.role)
			o.info_description.html(data.description)
			o.info_id.html(data.id)

			var am_data = [
				{
					"title": "action_menu.data_actions",
					"children": [
						{
							"selector": ["tab"],
							"foldable": false,
							"cols": [],
							"children": [
								{
									"title": "action_menu.del",
									"class": "del16",
									"fn": "data_action_del_group",
									"privileges": ["Manager", "GroupManager"]
								}
							]
						}
					]
				}
			]
			tab_tools({
				"div": o.div.find("#tools"),
				"data": {"id": data.id},
				"am_data": am_data
			})

			tab_properties_generic_boolean({
				"div": o.info_privilege,
				"privileges": ["Manager"],
				"post": function(_data, callback, error_callback) {
					services_osvcpostrest("R_GROUP", [data.id], "", _data, callback, error_callback)
				}
			})
			tab_properties_generic_updater({
				"div": o.div,
				"post": function(_data, callback, error_callback) {
					services_osvcpostrest("R_GROUP", [data.id], "", _data, callback, error_callback)
				}
			})
			tab_properties_generic_list({
				"request_service": "R_NODES",
				"request_data": {
					"filters": ["team_responsible "+data.role]
				},
				"limit": 50,
				"key": "nodename",
				"item_class": "icon node16",
				"id": "node_id",
				"flash_id_prefix": "node",
				"bgcolor": osvc.colors.node,
				"e_title": o.info_nodes_title,
				"e_list": o.info_nodes,
				"ondblclick": function(divid, data) {
					node_tabs(divid, {"node_id": data.id})
				}
			})
			tab_properties_generic_list({
				"request_service": "R_GROUP_SERVICES",
				"request_parameters": [data.id],
				"limit": 50,
				"key": "svcname",
				"item_class": "icon svc",
				"id": "svc_id",
				"flash_id_prefix": "svc",
				"bgcolor": osvc.colors.svc,
				"e_title": o.info_services_title,
				"e_list": o.info_services,
				"ondblclick": function(divid, data) {
					service_tabs(divid, {"svc_id": data.id})
				}
			})
			tab_properties_generic_list({
				"request_service": "R_GROUP_USERS",
				"request_parameters": [data.id],
				"request_data": {
					"props": "id,first_name,last_name"
				},
				"limit": 50,
				"flash_id": function(e){
					return "user-" + e.text()
				},
				"item_class": "icon guy16",
				"key": function(data) {
					var s = data.first_name + " " + data.last_name
					if (s == " ") {
						s = data.email
					}
					return s
				},
				"id": "id",
				"bgcolor": osvc.colors.user,
				"e_title": o.info_users_title,
				"e_list": o.info_users,
				"ondblclick": function(divid, data) {
					user_tabs(divid, {"user_id": data.id, "fullname": data.name})
				}

			})
			tab_properties_generic_list({
				"request_service": "R_GROUP_APPS",
				"request_parameters": [data.id],
				"limit": 50,
				"key": "app",
				"item_class": "icon app16",
				"id": "id",
				"bgcolor": osvc.colors.app,
				"e_title": o.info_apps_title,
				"e_list": o.info_apps,
				"ondblclick": function(divid, data) {
					app_tabs(divid, {"app_id": data.id, "app_name": data.name})
				}
			})
		})

	}

	o.div.load("/"+osvc.app+"/static/views/group_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o

}


function group_hidden_menu_entries(divid, options) {
	var o = {}
	o.options = options
	o.div = $("#"+divid)
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "link."+arguments.callee.name
	}

	o.set = function(id) {
		var data = {
			"menu_entry": id
		}
		services_osvcpostrest("R_GROUP_HIDDEN_MENU_ENTRIES", [o.options.group_id], "", data, function(jd) {
			if (rest_error(jd)) {
				osvc.flash.error(services_error_fmt(jd))
			}
			
		})
	}

	o.del = function(id) {
		var data = {
			"menu_entry": id
		}
		services_osvcdeleterest("R_GROUP_HIDDEN_MENU_ENTRIES", [o.options.group_id], "", data, function(jd) {
			if (rest_error(jd)) {
				osvc.flash.error(services_error_fmt(jd))
			}
		})
	}

	o.get = function(callback) {
		var params = {
			"meta": "0",
			"limit": "0"
		}
		services_osvcgetrest("R_GROUP_HIDDEN_MENU_ENTRIES", [o.options.group_id], params, function(jd) {
			if (rest_error(jd)) {
				osvc.flash.error(services_error_fmt(jd))
			}
			o.hidden = []
			for (i=0; i<jd.data.length; i++) {
				o.hidden.push(jd.data[i].menu_entry)
			}
			callback()
		})
	}

	o.format_entry = function(section, entry) {
		var div = $("<div></div>")
		o.area.append(div)

		// entry
		var e = $(menu_create_entry_s(section, entry))

		// checkbox
		var input = $("<input class='ocb' type='checkbox' />")
		input.attr("id", entry.id)
		if (o.hidden.indexOf(entry.id) >= 0) {
			input.prop("checked", true)
			e.find(".menu_icon,.menu_title").css({"color": "darkred"})
		}
		var label = $("<label class='ocb'></label>")
		label.attr("for", entry.id)

		e.find(".menu_box").prepend([input, label])
		div.append(e)

		// click
		input.bind("click", function() {
			var id = $(this).attr("id")
			var val = $(this).is(":checked")
			if (val == true) {
				o.set(id)
				$(this).parent().find(".menu_icon,.menu_title").css({"color": "darkred"})
			} else {
				o.del(id)
				$(this).parent().find(".menu_icon,.menu_title").css({"color": "black"})
			}
		})
	}

	o.format_section = function(section) {
		var title = $("<h2></h2>")
		title.text(i18n.t("menu."+section+".title"))
		o.area.append(title)
		for (entry in menu_data[section]) {
			o.format_entry(section, menu_data[section][entry])
		}
	}

	o.init = function() {
		var area = $("<div class='group_hidden_menu'></div>")
		o.area = area
		for (section in menu_data) {
			o.format_section(section)
		}
		o.div.empty()
		o.div.append(area)
		osvc_tools(o.div, {
			"link": o.link
		})
	}

	o.get(function() {
		o.init()
	})
	return o
}
