var search_data = {
	"arrays": {
		"tab" : function(id, res){array_tabs(id, {"array_id": res.id, "array_name": res.array_name})},
		"type": "array",
		"color": "disk",
		"id": "id",
		"title": "__array_name__",
		"short_title": "__array_name__",
		"menu_entry_id": "array",
		"class": "array fa-2x search-section-icon",
		"subclass": "meta_array clickable"
	},
	"modulesets": {
		"tab" : function(id, res){moduleset_tabs(id, {"modset_id": res.id, "modset_name": res.modset_name})},
		"type": "modset",
		"color": "modset",
		"id": "id",
		"title": "__modset_name__",
		"short_title": "__modset_name__",
		"menu_entry_id": "comp-modulesets",
		"class": "modset16 fa-2x search-section-icon",
		"subclass": "meta_moduleset clickable"
	},
	"rulesets": {
		"tab" : function(id, res){ruleset_tabs(id, {"ruleset_id": res.id, "ruleset_name": res.ruleset_name})},
		"type": "rset",
		"color": "ruleset",
		"id": "id",
		"title": "__ruleset_name__",
		"short_title": "__ruleset_name__",
		"menu_entry_id": "comp-rulesets",
		"class": "rset16 fa-2x search-section-icon",
		"subclass": "meta_ruleset clickable"
	},
	"reports": {
		"tab" : function(id, res){report_tabs(id, {"report_id": res.id, "report_name": res.report_name})},
		"type": "report",
		"color": "report",
		"id": "id",
		"title": "__report_name__",
		"short_title": "__report_name__",
		"menu_entry_id": "adm-reports",
		"class": "report16 fa-2x search-section-icon",
		"subclass": "meta_report clickable"
	},
	"charts": {
		"tab" : function(id, res){chart_tabs(id, {"chart_id": res.id, "chart_name": res.chart_name})},
		"type": "chart",
		"color": "chart",
		"id": "id",
		"title": "__chart_name__",
		"short_title": "__chart_name__",
		"menu_entry_id": "adm-charts",
		"class": "chart16 fa-2x search-section-icon",
		"subclass": "meta_chart clickable"
	},
	"metrics": {
		"tab" : function(id, res){metric_tabs(id, {"metric_id": res.id, "metric_name": res.metric_name})},
		"type": "metric",
		"color": "metric",
		"id": "id",
		"title": "__metric_name__",
		"short_title": "__metric_name__",
		"menu_entry_id": "adm-metrics",
		"class": "metric16 fa-2x search-section-icon",
		"subclass": "meta_metric clickable"
	},
	"forms": {
		"tab" : function(id, res){form_tabs(id, {"form_id": res.id, "form_name": res.form_name})},
		"type": "form",
		"color": "form",
		"id": "id",
		"title": "__form_name__",
		"short_title": "__form_name__",
		"menu_entry_id": "adm-forms",
		"class": "wf16 fa-2x search-section-icon",
		"subclass": "meta_form clickable"
	},
	"users": {
		"tab" : function(id, res){user_tabs(id, {"user_id": res.id, "fullname": res.fullname})},
		"type": "user",
		"color": "org",
		"id": "id",
		"title": "__fullname__ <__email__>",
		"short_title": "__fullname__",
		"menu_entry_id": "adm-usr",
		"class": "guy16 fa-2x search-section-icon",
		"subclass": "meta_username clickable"
	},
	"safe_files": {
		"tab" : function(id, res){safe_file_tabs(id, {"id": res.id, "uuid": res.uuid, "name": res.name})},
		"type": "safe",
		"color": "comp",
		"id": "uuid",
		"title": "__id__ __name__ (__uuid__)",
		"short_title": "__id__ __name__ (__uuid__)",
		"menu_entry_id": "view-safe",
		"class": "safe16 fa-2x search-section-icon",
		"subclass": "meta_safe_file"
	},
	"disks": {
		"tab" : function(id, res){disk_tabs(id, {"disk_id": res.disk_id})},
		"title": "__disk_id__",
		"short_title": "__disk_id__",
		"type": "disk",
		"color": "disk",
		"menu_entry_id": "view-disks",
		"class": "hd16 fa-2x search-section-icon",
		"subclass": "meta_disk clickable"
	},
	"apps": {
		"id": "app",
		"title": "__app__",
		"short_title": "__app__",
		"type": "app",
		"color": "app",
		"tab" : function(id, res){app_tabs(id, {"app_name": res.app})},
		"menu_entry_id": "view-dummy",
		"class": "app16 fa-2x search-section-icon",
		"subclass": "meta_app clickable"
	},
	"ips": {
		"title": "__node_ip.addr__@__nodes.nodename__  *__nodes.app__",
		"short_title": "__node_ip.addr__@__nodes.nodename__",
		"type": "ip",
		"color": "net",
		"menu_entry_id": "view-node-net",
		"class": "net16 fa-2x search-section-icon",
		"subclass": "meta_username"
	},
	"privileges": {
		"tab" : function(id, res){group_tabs(id, {"group_id": res.id, "group_name": res.role, "privilege": true})},
		"type": "priv",
		"color": "priv",
		"id": "id",
		"title": "__role__",
		"short_title": "__role__",
		"menu_entry_id": "adm-priv",
		"class": "privilege16 fa-2x search-section-icon",
		"subclass": "meta_username clickable"
	},
	"groups": {
		"tab" : function(id, res){group_tabs(id, {"group_id": res.id, "group_name": res.role})},
		"type": "group",
		"color": "org",
		"id": "id",
		"title": "__role__",
		"short_title": "__role__",
		"menu_entry_id": "adm-usr",
		"class": "guys16 fa-2x search-section-icon",
		"subclass": "meta_username clickable"
	},
	"services": {
		"tab" : function(id, res){service_tabs(id, {"svc_id": res.svc_id})},
		"type": "svc",
		"color": "svc",
		"id": "svc_id",
		"title": "__svcname__  *__svc_app__",
		"short_title": "__svcname__",
		"menu_entry_id": "view-services",
		"class": "svc fa-2x search-section-icon",
		"subclass": "meta_svcname clickable"
	},
	"nodes": {
		"tab" : function(id, res){node_tabs(id, {"node_id": res.node_id})},
		"type": "node",
		"color": "node",
		"id": "node_id",
		"title": "__nodename__  *__app__",
		"short_title": "__nodename__",
		"menu_entry_id": "view-nodes",
		"class": "node16 fa-2x search-section-icon",
		"subclass": "meta_nodename clickable"
	},
	"docker_registries": {
		"tab" : function(id, res){docker_registry_tabs(id, {"registry_name": res.service, "registry_id": res.id})},
		"type": "docker_registry",
		"color": "docker",
		"id": "id",
		"title": "__service__ @ __url__",
		"short_title": "__service__ @ __url__",
		"menu_entry_id": "view-registries",
		"class": "docker_registry16 fa-2x search-section-icon",
		"subclass": "meta_docker_repository clickable"
	},
	"docker_repositories": {
		"tab" : function(id, res){docker_repository_tabs(id, {"repository_name": res.repository, "repository_id": res.id})},
		"type": "docker_repository",
		"color": "docker",
		"id": "id",
		"title": "__repository__",
		"short_title": "__repository__",
		"menu_entry_id": "view-registries",
		"class": "docker_repository16 fa-2x search-section-icon",
		"subclass": "meta_docker_repository clickable"
	},
	"prov_templates": {
		"tab" : function(id, res){prov_template_tabs(id, {"tpl_id": res.id, "tpl_name": res.tpl_name})},
		"type": "prov_template",
		"prefix": "prov",
		"color": "svc",
		"id": "id",
		"title": "__tpl_name__",
		"short_title": "__tpl_name__",
		"menu_entry_id": "view-prov",
		"class": "prov fa-2x search-section-icon",
		"subclass": "meta_prov_template clickable"
	},
	"filtersets": {
		"tab" : function(id, res){filterset_tabs(id, {"fset_name": res.fset_name})},
		"type": "fset",
		"color": "fset",
		"id": "fset_name",
		"title": "__fset_name__",
		"short_title": "__fset_name__",
		"menu_entry_id": "adm-filters",
		"class": "filter16 fa-2x search-section-icon",
		"subclass": "meta_username clickable"
	},
	"tags": {
		"tab" : function(id, res){tag_tabs(id, {"tag_name": res.tag_name})},
		"type": "tag",
		"color": "tag",
		"id": "tag_name",
		"title": "__tag_name__",
		"short_title": "__tag_name__",
		"menu_entry_id": "view-tags",
		"class": "tag16 fa-2x search-section-icon",
		"subclass": "meta_tag clickable"
	},
	"vms": {
		"tab" : function(id, res){node_tabs(id, {"nodename": res.mon_vmname})},
		"type": "node",
		"prefix": "vm",
		"color": "node",
		"title": "__mon_vmname__",
		"short_title": "__mon_vmname__",
		"menu_entry_id": "view-nodes",
		"class": "hv16 fa-2x search-section-icon",
		"subclass": "meta_nodename"
	},
	"variables": {
		"tab" : function(id, res){
			variable_tabs(id, {
				"variable_id": res.id,
				"ruleset_id": res.ruleset_id,
				"variable_name": res.var_name,
				"tab": "variable_tabs.content"
			})
		},
		"type": "var",
		"color": "rule",
		"id": "id",
		"title": "__var_name__ in __ruleset_name__",
		"short_title": "__var_name__ in __ruleset_name__",
		"menu_entry_id": "comp-variables",
		"class": "comp16 fa-2x search-section-icon",
		"subclass": "meta_variables clickable"
	}
}



function search(divid) {
	var o = {}
	o.divid = divid
	o.div = $("#"+divid)
	o.highlight_class = "search_selector_selected"
	o.object_types = [
		{
			"color": "fset",
			"prefix": "fset",
			"title": "search.menu_header.title_filtersets",
		},
		{
			"color": "org",
			"prefix": "user",
			"title": "search.menu_header.title_users",
		},
		{
			"color": "org",
			"prefix": "group",
			"title": "search.menu_header.title_groups",
		},
		{
			"color": "priv",
			"prefix": "priv",
			"title": "search.menu_header.title_privs",
		},
		{
			"color": "app",
			"prefix": "app",
			"title": "search.menu_header.title_apps",
		},
		{
			"color": "svc",
			"prefix": "svc",
			"title": "search.menu_header.title_services",
		},
		{
			"color": "node",
			"prefix": "node",
			"title": "search.menu_header.title_nodes",
		},
		{
			"color": "node",
			"prefix": "vm",
			"title": "search.menu_header.title_vms",
		},
		{
			"color": "net",
			"prefix": "ip",
			"title": "search.menu_header.title_ips",
		},
		{
			"color": "disk",
			"prefix": "disk",
			"title": "search.menu_header.title_disks",
		},
		{
			"color": "comp",
			"prefix": "safe",
			"title": "search.menu_header.title_safe_files",
		},
		{
			"color": "form",
			"prefix": "form",
			"title": "search.menu_header.title_forms",
		},
		{
			"color": "report",
			"prefix": "report",
			"title": "search.menu_header.title_reports",
		},
		{
			"color": "chart",
			"prefix": "chart",
			"title": "search.menu_header.title_charts",
		},
		{
			"color": "metric",
			"prefix": "metric",
			"title": "search.menu_header.title_metrics",
		},
		{
			"color": "modset",
			"prefix": "modset",
			"title": "search.menu_header.title_modulesets",
		},
		{
			"color": "ruleset",
			"prefix": "rset",
			"title": "search.menu_header.title_rulesets",
		},
		{
			"color": "rule",
			"prefix": "var",
			"title": "search.menu_header.title_variables",
		},
		{
			"color": "tag",
			"prefix": "tag",
			"title": "search.menu_header.title_tags",
		}
	]

	o.router = function router(delay) {
		if (osvc.menu && osvc.menu.menu_div.is(":visible")) {
			o.filter_menu(null)
		} else if (osvc.fset_selector && osvc.fset_selector.area.is(":visible")) {
			o.filter_fset_selector(null)
		} else if (!delay) {
			// close the search result panel if no search keyword
			if (o.e_search_input.val() == "") {
				//o.close()
			} else {
				o.search()
			}
		}
	}

	o.div.load("/init/static/views/search.html?v="+osvc.code_rev, function() {
		o.init()
	})

	o.init = function() {
		o.timer = null
		o.div.i18n()
		o.e_search_div = $("#search_div")
		o.e_search_input = $("#search_input")
		o.e_search_result = $("#search_result")

		o.e_search_input.on("blur", function (event) {
			o.del_selector(event)
		})
		o.e_search_input.on("focus click", function (event) {
			if (osvc.menu && osvc.menu.menu_div.is(":visible")) {
				return
			}
			if (osvc.fset_selector && osvc.fset_selector.area.is(":visible")) {
				return
			}
			if (!o.e_search_result.is(":visible")) {
				o.open()
			}
			o.add_selector()
		})
		o.e_search_input.on("keyup",function (event) {
			if (is_special_key(event)) {
				// do search on special key (esc, arrows, etc...)
				o.add_selector()
				o.set_selector()
			} else if (event.keyCode == 13) {
				// do a search immediately on <enter>
				o.router(0)
			} else {
				// type-ahead search
				o.add_selector()
				o.set_selector()
				o.router(1000)
			}
		})
	}

	o.set_selector = function(event) {
		if (o.e_search_result.children("[name=selector]").length == 0) {
			return
		}
		var val = o.e_search_input.val()
		var current_prefix = o.search_parse_input(val).in
		if (current_prefix == o.last_prefix) {
			return
		}
		o.last_prefix = current_prefix
		if (!current_prefix) {
			o.e_selector.children("[search_prefix]").removeClass(o.highlight_class)
			o.e_selector.children("[search_prefix=all]").addClass(o.highlight_class)
			return
		}
		o.e_selector.children("[search_prefix]").removeClass(o.highlight_class)
		o.e_selector.children("[search_prefix="+current_prefix+"]").addClass(o.highlight_class)
	}
	o.del_selector = function(event) {
		if ($(event.relatedTarget).is(".search_selector>button,.search_selector")) {
			return
		}
		o.e_search_result.children("[name=selector]").remove()
	}
	o.add_selector = function() {
		if (o.e_search_result.children("[name=selector]").length > 0) {
			return
		}
		var sel = $("<div name='selector' class='search_selector'><h4 data-i18n='search.selector_title' style='width:100%'></h4></div>")
		sel.i18n()
		var b = $("<button search_prefix='all' class='btn'>")
		b.text(i18n.t("search.menu_header.title_all"))
		b.on("click", function() {
			var val = o.e_search_input.val()
			val = val.replace(/^\w+:/, "")
			$(this).siblings("."+o.highlight_class).removeClass(o.highlight_class)
			$(this).addClass(o.highlight_class)
			o.e_search_input.val(val).focus().trigger("keyup")
		})
		sel.append(b)
		for (var i=0; i<o.object_types.length; i++) {
			var data = o.object_types[i]
			var b = $("<button class='btn'>")
			b.attr("search_prefix", data.prefix)
			b.css({"border-color": osvc.colors[data.color]})
			b.text(i18n.t(data.title))
			sel.append(b)
			o.e_search_result.prepend(sel)
			b.on("click", function() {
				var val = o.e_search_input.val()
				val = $(this).attr("search_prefix")+":"+val.replace(/^\w+:/, "")
				$(this).siblings("."+o.highlight_class).removeClass(o.highlight_class)
				$(this).addClass(o.highlight_class)
				o.e_search_input.val(val).focus().trigger("keyup")
			})
		}
		o.set_selector()
		o.e_selector = sel
		o.e_search_result.prepend(sel)
	}
	o.search = function(section, limit) {
		var count = 0
		var search_query = o.e_search_input.val()

		if (search_query == "") {
			return
		}

		var data = o.search_parse_input(search_query)
		if (typeof section !== "undefined") {
			data["in"] = section
		}
		if (typeof limit !== "undefined") {
			data["limit"] = limit
		}

		o.e_search_div.removeClass("searchidle")
		o.e_search_div.addClass("searching")
		o.e_search_result.empty()

		services_osvcgetrest("R_SEARCH", "", data, function(jd) {
			var result = jd.data
			for (d in result) {
				if (result[d].data.length>0 && search_data[d] !== undefined) {
					response = o.search_build_result_view(d, result[d])
					o.e_search_result.append(response)
					count += result[d].data.length
				}
			}
			osvc.flash.close()

			if (count == 0) {
				var div = "<div class='menu_entry meta_not_found'><a><div class='question48'>"+i18n.t("search.nothing_found")+"</div></a></div>"
				o.e_search_result.append(div)
			} else if (count == 1) {
				o.e_search_result.find(".search_entry .clickable").first().trigger("click")
			}

			o.open()
			o.e_search_div.removeClass("searching")
			o.e_search_div.addClass("searchidle")
			o.search_highlight(o.e_search_result, data.substring)
		})
	}

	o.set_placeholder = function() {
		if (osvc.menu && osvc.menu.menu_div.is(":visible")) {
			o.e_search_input.attr("placeholder", i18n.t("search.placeholder.filter"))
		} else if (osvc.fset_selector && osvc.fset_selector.area.is(":visible")) {
			o.e_search_input.attr("placeholder", i18n.t("search.placeholder.filter"))
		} else {
			o.e_search_input.attr("placeholder", i18n.t("search.placeholder.search"))
		}
	}

	o.open = function() {
		if (!o.e_search_result.is(':visible')) {
			toggle('search_result')
			osvc.body_scroll.disable()
			o.set_placeholder()
		}
	}

	o.close = function() {
		if (o.e_search_result.is(':visible')) {
			toggle('search_result')
			osvc.body_scroll.enable()
			o.set_placeholder()
		}
	}

	o.search_subst_keys = function(s, data, key) {
		if (is_dict(data[key])) {
			for (subkey in data[key]) {
				var _key = key+"."+subkey
				s = s.replace("__"+_key+"__", o.search_get_val(data, _key))
			}
		} else {
			s = s.replace("__"+key+"__", o.search_get_val(data, key))
		}
		return s
	}

	o.search_get_val = function(data, key) {
		var l = key.split(".")
		var val = data
		for (var i=0; i<l.length; i++) {
			val = val[l[i]]
		}
		return val
	}

	o.search_parse_input = function(search_query) {
		var data = {}
		if (search_query.match(/^\w+:\s*/)) {
			data["substring"] = search_query.replace(/^\w+:\s*/, "")
			data["in"] = search_query.match(/^\w+:\s*/)[0].replace(/:\s*$/, "")
			data["limit"] = o.search_limit
			o.search_limit = 10
		} else {
			data["substring"] = search_query
		}
		return data
	}

	o.search_build_result_row = function(label, first, res, count) {
		var section_data = search_data[label]

		// init result row, set icon cell
		var row_group = $("<div></div>")
		var row = $("<tr></tr>")
		row_group.append(row)
		var cell_icon = $("<td class='icon'></td>")
		cell_icon.addClass(section_data.class)
		row.append(cell_icon)

		// title cell
		cell_result = $("<td></td>")
		p_title = $("<p></p>")
		cell_result.append(p_title)
		row.append(cell_result)

		if (first==1) {
			// first header with %___%
			var val = $('#search_input').val()
			var title = "%" + o.search_parse_input(val).substring + "%"
			p_title.text(title)
		} else {
			// substitute key in the title format
			row.addClass("search_entry")
			var title = section_data.title
			for (key in res) {
				title = o.search_subst_keys(title, res, key)
				p_title.text(title)
			}
			p_title.addClass(section_data.subclass)

			var short_title = section_data.short_title
			for (key in res) {
				short_title = o.search_subst_keys(short_title, res, key)
			}

			var tab = section_data.tab
			if (tab) {
				if (tab[0] == "/") {
					// tab action: load ajax content
					var url = services_get_url() + tab
					var fn = "sync_ajax('"+url+"', [], '"+rowid+"', function() {})"
				} else {
					// tab action: execute a function
					var fn = tab
				}
				p_title.parent().bind("click", function(){
					osvc.flash.show({
						id: section_data.type+"-"+res[section_data.id],
						cl: "icon "+section_data.class.replace(/fa-2x/, "").replace(/search-section-icon/, ""),
						text: short_title,
						bgcolor: osvc.colors[section_data.color],
						fn: function(id){fn(id, res)}
					})
				})
			}
		}

		return row_group.children()
	}

	o.search_build_result_view = function(label, resultset) {
		var section_data = search_data[label]
		if (osvc.hidden_menu_entries.indexOf(section_data.menu_entry_id) >= 0) {
			return
		}
		var section_div = $("<div class='menu_section clickable'></div>")
		section_div.attr("id", label)
		var title = $("<h4></h4>")
		title.text(i18n.t("search.menu_header.title_"+label) + " (" + resultset.total +")")
		section_div.append(title)
		var table = $("<table id='search_result_table' style='width:100%'></table>")
		section_div.append(table)
		title.on("click", function() {
			var prefix = section_data.prefix
			if (!prefix) {
				prefix = section_data.type
			}
			o.search(prefix, 0)
		})

		for (i=0; i<resultset.data.length; i++) {
			table.append(o.search_build_result_row(label, 0, resultset.data[i], i))
		}
		return section_div
	}

	o.filter_menu = function(event) {
		var menu = $("#menu_menu")
		var text = $(".search").find("input").val()

		var reg = new RegExp(text, "i")
		menu.find(".menu_entry").each(function(){
			if ($(this).text().match(reg)) {
				$(this).show()
				$(this).parents(".menu_section").first().show()
			} else {
				$(this).hide()
			}
		})
		menu.find(".menu_section").each(function(){
			if ($(this).children("a").text().match(reg)) {
				$(this).find(".menu_entry").show()
				$(this).show()
			}
			n = $(this).find(".menu_entry:visible").length
			if (n == 0) {
				$(this).hide()
			}
		})
		var entries = menu.find(".menu_entry:visible")
		if (is_enter(event)) {
			if (menu.is(":visible") && (entries.length == 1)) {
				entries.effect("highlight")
				window.location = entries.attr("link")
			}
		}
		if (entries.length==0) {
			menu.append("<div class='menu_entry meta_not_found'><a><div class='question48'>"+i18n.t("search.nothing_found")+"</div></a></div>")
		} else {
			menu.find(".meta_not_found").remove()
		}
		o.search_highlight(menu, text)
	}

	o.filter_fset_selector = function(event) {
		var div = $(".header [name=fset_selector_entries]")
		if (!div.is("[ready]")) {
			var timer = setTimeout(function(){
				o.filter_fset_selector(event)
			}, 500)
			return
		}
		var text = $(".search").find("input").val()
		var reg = new RegExp(text, "i")
		div.find(".menu_entry").each(function(){
			if ($(this).find("[name=title]").text().match(reg)) {
				$(this).show()
			} else {
				$(this).hide()
			}
		})
		var entries = div.find(".menu_entry:visible")
		if (entries.length==0) {
			div.append("<div class='menu_entry meta_not_found'><a><div class='question48'>"+i18n.t("search.nothing_found")+"</div></a></div>")
		} else {
			div.find(".meta_not_found").remove()
		}
		o.search_highlight(div, text)
	}

	o.search_highlight = function(e, s) {
		// keep track of original texts
		if (e.children("[name=orig]").length == 0) {
			var cache = $("<div name='orig'></div>")
			cache.css({"display": "none"})
			e.find("*").each(function() {
				var clone = $(this).clone()
				clone.children().remove()
				if (clone.text().match(/^$/)) {
					return
				}
				var cache_entry = $("<div></div>")
				cache_entry.uniqueId()
				var id = cache_entry.attr("id")
				$(this).attr("highlight_id", id)
				cache_entry.html(clone.html())
				cache.append(cache_entry)
			})
			e.append(cache)
		}

		var regexp = new RegExp(s, 'ig')

		e.children("[name=orig]").children().each(function(){
			// restore orig
			var id = $(this).attr("id")
			var tgt = e.find("[highlight_id="+id+"]")
			tgt.find("[name=highlighted]").remove()
			var children = tgt.children().detach()

			tgt.empty()
			tgt.text($(this).text())

			if ((s != "") && $(this).text().match(regexp)) {
				var highlighted = $("<span name='highlighted'></span>")
				highlighted.html($(this).text().replace("<", "&lt;").replace(">", "&gt;").replace(regexp, function(x) {
					return '<span class="highlight_light">' + x + '</span>'
				}))
				tgt.text("")
				tgt.prepend(highlighted)
			}
			tgt.append(children)
		})
	}

	return o
}

