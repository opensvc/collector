//
// docker repository
//
function docker_repository_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.docker
	o.options.icon = osvc.icons.docker
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "format_title",
		"title_args": {
			"type": "docker_repository",
			"name": o.options.repository_name,
			"id": o.options.repository_id
		}
	}

	o.load(function(){
		var i = 0

		if (("repository_id" in o.options) && ("repository_name" in o.options)) {
			o._load()
		} else if ("repository_id" in o.options) {
			services_osvcgetrest("/docker/repositories/%1", [o.options.repository_id], "", function(jd) {
				if (jd.error) {
					osvc.flash.error(jd.error)
					return
				}
				o.options.data = jd.data[0]
				o.options.repository_name = o.options.data.repository
				o.link.title_args.name = o.options.data.repository
				o.link.title_args.id = o.options.repository_id
				o._load()
			})
		}
	})

	o._load = function() {
		o.closetab.text(o.options.repository_name)

		// tab properties
		i = o.register_tab({
			"title": "node_tabs.properties",
			"title_class": "icon fa-list-ul"
		})
		o.tabs[i].callback = function(divid) {
			docker_repository_properties(divid, o.options)
		}
		i = o.register_tab({
			"title": "docker_repository_tabs.tags",
			"title_class": "icon dockertags16"
		})
		o.tabs[i].callback = function(divid) {
			table_registries_repo(divid, o.options.repository_id)
		}

		o.set_tab(o.options.tab)
	}
	return o
}


function docker_repository_properties(divid, options) {
	var o = {}
	// store parameters
	o.divid = divid
	o.div = $("#"+divid);
	o.options = options
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "format_title",
		"title_args": {
			"type": "docker_repository"
		}
	}

	o.init = function() {
		o.info_registry_id = o.div.find("[name=registry_id]")
		o.info_registry_service = o.div.find("#service")
		o.info_registry_url = o.div.find("#url")
		o.info_registry_insecure = o.div.find("#insecure")
		o.info_repository_id = o.div.find("[name=repository_id]")
		o.info_repository_name = o.div.find("#repository")
		o.info_repository_updated = o.div.find("#repository_updated")
		o.info_repository_created = o.div.find("#repository_created")
		o.info_repository_description = o.div.find("#description")
		o.info_repository_stars = o.div.find("#stars")
		o.info_repository_automated = o.div.find("#automated")
		o.info_repository_official = o.div.find("#official")
		o.info_pushers = o.div.find("#pushers")
		o.info_pullers = o.div.find("#pullers")

		o.load()
	}

	o.load = function() {
		if (o.options.data) {
			o._load(o.options.data)
			o.options.data = null
		} else {
			services_osvcgetrest("/docker/repositories/%1", [o.options.repository_id], "", function(jd) {
				if (jd.error) {
					osvc.flash.error(jd.error)
					return
				}
				if (!jd.data || (jd.data.length == 0)) {
					return
				}
				o._load(jd.data[0])
			})
		}
	}

	o._load = function(data) {
		o.link.title_args.id = data.id
		o.link.title_args.name = data.repository
		osvc_tools(o.div, {
			"link": o.link
		})
		o.info_repository_id.html(data.id)
		o.info_repository_name.html(data.repository)
		o.info_repository_description.html(data.description)
		o.info_repository_stars.html(data.stars)
		o.info_repository_updated.html(osvc_date_from_collector(data.updated))
		o.info_repository_created.html(osvc_date_from_collector(data.created))

		services_osvcgetrest("/docker/registries/%1", [data.registry_id], "", function(jd) {
			if (!jd.data || (jd.data.length == 0)) {
				return
			}
			o.info_registry_id.html(jd.data[0].id)
			o.info_registry_service.html(jd.data[0].service)
			o.info_registry_url.html(jd.data[0].url)
			o.info_registry_insecure.html(jd.data[0].insecure)
		})

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
								"fn": "data_action_delete_docker_repositories",
								"privileges": ["Manager", "DockerRegistriesManager"]
							}
						]
					}
				]
			}
		]
		tab_tools({
			"div": o.div.find("#tools"),
			"data": {"repository_id": data.id},
			"am_data": am_data
		})

/*
		docker_repository_publications({
			"bgcolor": osvc.colors.org,
			"tid": o.info_publications,
			"docker_repository_id": data.id
		})
		docker_repository_responsibles({
			"bgcolor": osvc.colors.org,
			"tid": o.info_responsibles,
			"docker_repository_id": data.id
		})
*/

		services_osvcgetrest("/docker/repositories/%1/pullers", [o.options.repository_id], "", function(jd) {
			tab_properties_generic_list({
				"data": jd.data.apps,
				"key": "app",
				"item_class": "icon app16",
				"id": "id",
				"flash_id_prefix": "app",
				"bgcolor": osvc.colors.app,
				"e_title": $(""),
				"e_list": o.info_pullers,
				"lowercase": true,
				"ondblclick": function(divid, data) {
					app_tabs(divid, {"app_id": data.id, "app_name": data.name})
				}
			})
			tab_properties_generic_list({
				"data": jd.data.groups,
				"key": "role",
				"item_class": "icon guys16",
				"id": "id",
				"flash_id_prefix": "group",
				"bgcolor": osvc.colors.org,
				"e_title": $(""),
				"e_list": o.info_pullers,
				"lowercase": true,
				"ondblclick": function(divid, data) {
					group_tabs(divid, {"group_id": data.id, "group_name": data.name})
				}
			})
			tab_properties_generic_list({
				"data": jd.data.users,
				"key": function(data) {
					var s = data.first_name + " " + data.last_name
					if (s == " ") {
						s = data.email
					}
					return s
				},
				"item_class": "icon guy16",
				"id": "id",
				"flash_id_prefix": "user",
				"bgcolor": osvc.colors.user,
				"e_title": $(""),
				"e_list": o.info_pullers,
				"lowercase": true,
				"ondblclick": function(divid, data) {
					user_tabs(divid, {"user_id": data.id, "fullname": data.name})
				}
			})
			tab_properties_generic_list({
				"data": jd.data.services,
				"key": "svcname",
				"item_class": "icon svc",
				"id": "svc_id",
				"flash_id_prefix": "svc",
				"bgcolor": osvc.colors.svc,
				"e_title": $(""),
				"e_list": o.info_pullers,
				"lowercase": true,
				"ondblclick": function(divid, data) {
					service_tabs(divid, {"svc_id": data.id, "svcname": data.name})
				}
			})
		})

		services_osvcgetrest("/docker/repositories/%1/pushers", [o.options.repository_id], "", function(jd) {
			tab_properties_generic_list({
				"data": jd.data.apps,
				"key": "app",
				"item_class": "icon app16",
				"id": "id",
				"flash_id_prefix": "app",
				"bgcolor": osvc.colors.app,
				"e_title": $(""),
				"e_list": o.info_pushers,
				"lowercase": true,
				"ondblclick": function(divid, data) {
					app_tabs(divid, {"app_id": data.id, "app_name": data.name})
				}
			})
			tab_properties_generic_list({
				"data": jd.data.groups,
				"key": "role",
				"item_class": "icon guys16",
				"id": "id",
				"flash_id_prefix": "group",
				"bgcolor": osvc.colors.org,
				"e_title": $(""),
				"e_list": o.info_pushers,
				"lowercase": true,
				"ondblclick": function(divid, data) {
					group_tabs(divid, {"group_id": data.id, "group_name": data.name})
				}
			})
			tab_properties_generic_list({
				"data": jd.data.users,
				"key": function(data) {
					var s = data.first_name + " " + data.last_name
					if (s == " ") {
						s = data.email
					}
					return s
				},
				"item_class": "icon guy16",
				"id": "id",
				"flash_id_prefix": "user",
				"bgcolor": osvc.colors.user,
				"e_title": $(""),
				"e_list": o.info_pushers,
				"lowercase": true,
				"ondblclick": function(divid, data) {
					user_tabs(divid, {"user_id": data.id, "fullname": data.name})
				}
			})
		})

		tab_properties_generic_updater({
			"div": o.div,
			"privileges": ["DockerRegistriesManager", "Manager"],
			"post": function(_data, callback, error_callback) {
				services_osvcpostrest("/docker/repositories/%1", [data.id], "", _data, callback, error_callback)
			}
		})
	}

	o.div.load("/init/static/views/docker_repository_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o

}
