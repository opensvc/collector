//
// tag
//
function tag_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options
	o.options.bgcolor = osvc.colors.tag
	o.options.icon = osvc.icons.tag
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "format_title",
		"title_args": {
			"type": "tag"
		}
	}

	o.load(function(){
		var i = 0

		if ("tag_name" in o.options) {
			services_osvcgetrest("/tags", "", {"filters": ["tag_name "+o.options.tag_name]}, function(jd) {
				o.options.tag_data = jd.data[0]
				o.options.tag_id = o.options.tag_data.tag_id
				o.link.title_args.name = o.options.tag_name
				o.link.title_args.id = o.options.tag_data.tag_id
				o._load()
			})
		} else if ("tag_id" in o.options) {
			services_osvcgetrest("/tags/%1", [o.options.tag_id], "", function(jd) {
				o.options.tag_data = jd.data[0]
				o.options.tag_name = o.options.tag_data.tag_name
				o.link.title_args.name = o.options.tag_data.tag_name
				o.link.title_args.id = o.options.tag_id
				o._load()
			})
		}
	})

	o._load = function() {
		o.closetab.text(o.options.tag_name)

		// tab properties
		i = o.register_tab({
			"title": "node_tabs.properties",
			"title_class": "icon tag16"
		})
		o.tabs[i].callback = function(divid) {
			tag_properties(divid, o.options)
		}

		o.set_tab(o.options.tab)
	}

	return o
}


function tag_properties(divid, options) {
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
			"type": "tag",
		}
	}

	o.init = function() {
		o.info_tag_id = o.div.find("#tag_id");
		o.info_tag_name = o.div.find("#tag_name");
		o.info_tag_exclude = o.div.find("#tag_exclude");
		o.info_tag_created = o.div.find("#tag_created");
		o.info_tag_data = o.div.find("#tag_data");
		o.info_nodes = o.div.find("#nodes");
		o.info_services = o.div.find("#services");
		o.load()
	}

	o.load = function() {
		if (o.options.reload) {
			o.options.tag_data = null
		}
		if (o.options.tag_data) {
			o._load(o.options.tag_data)
		} else {
			services_osvcgetrest("/tags/%1", [o.options.tag_id], "", function(jd) {
				if (!jd.data || (jd.data.length == 0)) {
					return
				}
				o._load(jd.data[0])
			})
		}
	}

	o._load = function(data) {
		o.link.title_args.id = data.tag_id
		o.link.title_args.name = data.tag_name
		osvc_tools(o.div, {
			"link": o.link
		})
		o.info_tag_name.html(data.tag_name);
		o.info_tag_exclude.html(data.tag_exclude);
		o.info_tag_created.html(osvc_date_from_collector(data.tag_created));
		o.info_tag_id.html(data.tag_id);

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
								"fn": "data_action_del_tag",
								"privileges": ["Manager", "TagManager"]
							}
						]
					}
				]
			}
		]
		tab_tools({
			"div": o.div.find("#tools"),
			"data": {"tag_id": data.tag_id},
			"am_data": am_data
		})

		tag_nodes({
			"bgcolor": osvc.colors.node,
			"tid": o.info_nodes,
			"tag_id": data.tag_id
		})
		tag_services({
			"bgcolor": osvc.colors.services,
			"tid": o.info_services,
			"tag_id": data.tag_id
		})
		tab_properties_generic_updater({
			"div": o.div,
			"privileges": ["TagManager", "Manager"],
			"post": function(_data, callback, error_callback) {
				services_osvcpostrest("/tags/%1", [data.tag_id], "", _data, callback, error_callback)
			}
		})

		if (data.tag_name.match(/::/)) {
			var tag_class = data.tag_name.split(/::/)[0]
		} else {
			var tag_class = "raw"
		}
		var form_div = $("<div style='padding:1px'></div>")
		form_div.uniqueId()
		o.info_tag_data.append(form_div)
		if (!data.tag_data) {
			tag_data = ""
		} else {
			tag_data = data.tag_data
		}
		form(form_div.attr("id"), {
			"data": tag_data,
			"display_mode": true,
			"digest": true,
			"form_name": tag_class,
			"tag_id": data.tag_id,
			"disable_edit": false
		})

	}

	o.div.load("/init/static/views/tag_properties.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.init()
	})

	return o

}
