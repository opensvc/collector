//
// docker registry
//
function docker_registry_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.docker
	o.options.icon = osvc.icons.docker
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "format_title",
		"title_args": {
			"type": "docker_registry"
		}
	}

	o.load(function(){
		var i = 0

		if (("registry_id" in o.options) && ("registry_service" in o.options)) {
			o._load()
		} else if ("registry_id" in o.options) {
			services_osvcgetrest("/docker/registries/%1", [o.options.registry_id], "", function(jd) {
				o.options.data = jd.data[0]
				o.options.registry_service = o.options.data.service
				o.link.title_args.name = o.options.data.service
				o.link.title_args.id = o.options.registry_id
				o._load()
			})
		} else if ("registry_service" in o.options) {
			services_osvcgetrest("/docker/registries", "", {"filters": ["service "+o.options.registry_service]}, function(jd) {
				o.options.data = jd.data[0]
				o.options.registry_id = o.options.data.id
				o.link.title_args.name = o.options.data.service
				o.link.title_args.id = o.options.registry_id
				o._load()
			})
		}
	})

	o._load = function() {
		o.closetab.text(o.options.registry_service)

		// tab properties
		i = o.register_tab({
			"title": "node_tabs.properties",
			"title_class": "icon fa-list-ul"
		})
		o.tabs[i].callback = function(divid) {
			docker_registry_properties(divid, o.options)
		}
		i = o.register_tab({
			"title": "docker_repository_tabs.tags",
			"title_class": "icon dockertags16"
		})
		o.tabs[i].callback = function(divid) {
			table_registries_registry(divid, o.options.registry_id)
		}

		o.set_tab(o.options.tab)
	}
	return o
}


function docker_registry_properties(divid, options) {
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
			"type": "docker_registry",
		}
	}

	o.init = function() {
		o.info_registry_id = o.div.find("[name=registry_id]")
		o.info_registry_service = o.div.find("#service")
		o.info_registry_url = o.div.find("#url")
		o.info_registry_insecure = o.div.find("#insecure")
		o.info_registry_restricted = o.div.find("#restricted")
		o.info_registry_updated = o.div.find("#registry_updated")
		o.info_registry_created = o.div.find("#registry_created")
		o.info_publications = o.div.find("#publications")
		o.info_responsibles = o.div.find("#responsibles")

		o.load()
	}

	o.load = function() {
		if (o.options.data) {
			o._load(o.options.data)
			o.options.data = null
		} else {
			services_osvcgetrest("/docker/registries/%1", [o.options.registry_id], "", function(jd) {
				if (!jd.data || (jd.data.length == 0)) {
					return
				}
				o._load(jd.data[0])
			})
		}
	}

	o._load = function(data) {
		o.link.title_args.id = data.id
		o.link.title_args.name = data.registry
		osvc_tools(o.div, {
			"link": o.link
		})
		o.info_registry_id.html(data.id)
		o.info_registry_service.html(data.service)
		o.info_registry_url.html(data.url)
		o.info_registry_insecure.html(data.insecure)
		o.info_registry_restricted.html(data.restricted)
		o.info_registry_updated.html(osvc_date_from_collector(data.updated))
		o.info_registry_created.html(osvc_date_from_collector(data.created))

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
								"fn": "data_action_delete_docker_registry",
								"privileges": ["Manager", "DockerRegistriesManager"]
							}
						]
					}
				]
			}
		]

		docker_registry_publications({
			"bgcolor": osvc.colors.org,
			"tid": o.info_publications,
			"registry_id": data.id
		})
		docker_registry_responsibles({
			"bgcolor": osvc.colors.org,
			"tid": o.info_responsibles,
			"registry_id": data.id
		})

		tab_tools({
			"div": o.div.find("#tools"),
			"data": {"id": data.id},
			"am_data": am_data
		})

		tab_properties_generic_updater({
			"div": o.div,
			"privileges": ["DockerRegistriesManager", "Manager"],
			"post": function(_data, callback, error_callback) {
				services_osvcpostrest("/docker/registries/%1", [data.id], "", _data, callback, error_callback)
			}
		})
	}

	o.div.load("/init/static/views/docker_registry_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o

}
