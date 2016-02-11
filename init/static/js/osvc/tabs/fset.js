//
// filterset
//
function filterset_tabs(divid, options) {
	var o = tabs(divid)
	o.options = options

	o.load(function() {
		var title = o.options.fset_name
		o.closetab.children("p").text(title)

		// tab properties
		i = o.register_tab({
			"title": "node_tabs.properties",
			"title_class": "icon filter16"
		})
		o.tabs[i].callback = function(divid) {
			fset_properties(divid, o.options)
		}

		// tab quotas
		i = o.register_tab({
			"title": "fset_tabs.export",
			"title_class": "icon log16"
		})
		o.tabs[i].callback = function(divid) {
			fset_export(divid, o.options)
		}

		// tab designer
		i = o.register_tab({
			"title": "fset_tabs.designer",
			"title_class": "icon designer16"
		})
		o.tabs[i].callback = function(divid) {
			fset_designer(divid, o.options)
		}

		o.set_tab(o.options.tab)
	})

	return o
}

function fset_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options

	o.init = function() {
		o.info_id = o.div.find("#id")
		o.info_fset_name = o.div.find("#fset_name")
		o.info_fset_stats = o.div.find("#fset_stats")
		o.info_fset_author = o.div.find("#fset_author")
		o.info_fset_updated = o.div.find("#fset_updated")
		o.info_nodes = o.div.find("#nodes")
		o.info_nodes_title = o.div.find("#nodes_title")
		o.info_services = o.div.find("#services")
		o.info_services_title = o.div.find("#services_title")
		o.info_filtersets = o.div.find("#filtersets")
		o.info_filtersets_title = o.div.find("#filtersets_title")
		o.info_rulesets = o.div.find("#rulesets")
		o.info_rulesets_title = o.div.find("#rulesets_title")
		o.info_thresholds = o.div.find("#thresholds")
		o.info_thresholds_title = o.div.find("#thresholds_title")
		o.load_form()
	}

	o.load_form = function() {
		services_osvcgetrest("R_FILTERSETS", "", {"meta": "0", "filters": ["fset_name "+o.options.fset_name]}, function(jd) {
			o.data = jd.data[0]
			o._load_form(jd.data[0])
		})
	}

	o._load_form = function(data) {
		o.info_id.html(data.id)
		o.info_fset_name.html(data.fset_name)
		o.info_fset_stats.html(data.fset_stats)
		o.info_fset_author.html(data.fset_author)
		o.info_fset_updated.html(data.fset_updated)

		o.load_usage()

		tab_properties_generic_updater({
			"div": o.div,
			"privileges": ["Manager", "CompManager"],
			"post": function(_data, callback, error_callback) {
				services_osvcpostrest("/filtersets/%1", [data.id], "", _data, callback, error_callback)
			}
		})
		tab_properties_generic_list({
			"request_service": "/filtersets/%1/nodes",
			"request_parameters": [data.id],
			"limit": "0",
			"key": "nodename",
			"item_class": "node16",
			"e_title": o.info_nodes_title,
			"e_list": o.info_nodes
		})
		tab_properties_generic_list({
			"request_service": "/filtersets/%1/services",
			"request_parameters": [data.id],
			"limit": "0",
			"key": "svc_name",
			"item_class": "svc",
			"e_title": o.info_services_title,
			"e_list": o.info_services
		})

	}

	o.load_usage = function() {
		services_osvcgetrest("/filtersets/%1/usage", [o.data.id], "", function(jd) {
			tab_properties_generic_list({
				"data": jd.data.filtersets,
				"item_class": "svc",
				"e_title": o.info_filtersets_title,
				"e_list": o.info_filtersets
			})
			tab_properties_generic_list({
				"data": jd.data.rulesets,
				"item_class": "comp16",
				"e_title": o.info_rulesets_title,
				"e_list": o.info_rulesets
			})
			tab_properties_generic_list({
				"data": jd.data.thresholds,
				"item_class": "check16",
				"e_title": o.info_thresholds_title,
				"e_list": o.info_thresholds
			})
		})
	}

	o.div.load("/init/static/views/fset_properties.html", function() {
		o.div.i18n()
		o.init()
	})

	return o
}


function fset_export(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid)
	o.options = options

	o.init = function() {
		o.load_export()
	}

	o.load_export = function() {
		o.div.empty()
		spinner_add(o.div)
		services_osvcgetrest("R_FILTERSETS", "", {"filters": ["fset_name "+o.options.fset_name]}, function(jd) {
			services_osvcgetrest("/filtersets/%1/export", [jd.data[0].id], "", function(jd) {
				o._load_export(jd)
			})
		})
	}

	o._load_export = function(data) {
		var div = $("<textarea class='export_data'>")
		div.prop("disabled", true)
		div.text(JSON.stringify(data, null, 4))
		o.div.html(div)
	}

	o.init()

	return o
}


function fset_designer(divid, options) {
	var o = {}
	o.div = $("#"+divid)
	o.options = options
	o.data = {}
	o.fset_data = {}

	o.init = function() {
		if (o.options.fset_id) {
			services_osvcgetrest("/filtersets/%1/export", [o.options.fset_id], "", function(jd) {
				o.data = jd
				o.get_fset_data(o.options.fset_id)
				o.render()
			})
		} else if (o.options.fset_name) {
			o.options.fset_id = o.get_fset_id(o.options.fset_name)
			services_osvcgetrest("/filtersets/%1/export", [o.options.fset_id], "", function(jd) {
				o.data = jd
				o.get_fset_data(o.options.fset_id)
				o.render()
			})
		} else {
			o.render()
		}
	}

	o.get_fset_data = function(id) {
		for (var i=0; i<o.data.filtersets.length; i++) {
			if (o.data.filtersets[i].id == id) {
				o.fset_data = o.data.filtersets[i]
			}
		}
		o.fset_data.filters.sort(function(a, b){
			if (a.f_order < b.f_order) return -1
			if (a.f_order > b.f_order) return 1
			return 0
		})
	}

	o.save_orders = function() {
		var i = 0
		o.div.find(".fset_designer_item").each(function(){
			var item = $(this)
			var data = {
				"f_order": i
			}
			if (item.attr("f_id")) {
				var service = "/filtersets/%1/filters/%2"
				var service_parameters = [o.options.fset_id, item.attr("f_id")]
			} else if (item.attr("fset_id")) {
				var service = "/filtersets/%1/filtersets/%2"
				var service_parameters = [o.options.fset_id, item.attr("fset_id")]
			}
			services_osvcpostrest(service, service_parameters, "", data)
			i++
		})
	}

	o.render = function() {
		o.div.empty()
		o.area = $("<div></div>")
		o.div.append(o.area)

		for (var i=0; i<o.fset_data.filters.length; i++) {
			o.add_item(o.fset_data.filters[i])
		}
		o.add_adder()

		o.area.sortable({
			connectWith: ".fset_designer_item",
			handle: ".fa-bars",
			cancel: ".fset_designer_item *:not('.fa-bars')",
			placeholder: "fset_designer_placeholder",
			update: o.save_orders
		})
	}

	o.render_f_table = function(data) {
		var span = $("<span id='f_table'></span>")
		if (data.filter.f_table in db_tables) {
			span.attr("value", data.filter.f_table)
			span.text(db_tables[data.filter.f_table].title)
			span.addClass("icon")
			span.addClass(db_tables[data.filter.f_table].cl)
		} else {
			span.text(data.filter.f_table)
		}
		return span

	}

	o.render_f_field = function(data) {
		var span = $("<span id='f_field'></span>")
		if (data.filter.f_field in db_columns) {
			span.attr("value", data.filter.f_field)
			span.text(db_columns[data.filter.f_field].title)
			span.addClass("icon")
			span.addClass(db_columns[data.filter.f_field].img)
		} else {
			span.text(data.filter.f_field)
		}
		return span

	}

	o.log_op_input = function(current) {
		if (!current) {
			current = "AND"
		}
		var opts = [
			{"label": "AND", "value": "AND"},
			{"label": "OR", "value": "OR"},
			{"label": "AND NOT", "value": "AND NOT"},
			{"label": "OR NOT", "value": "OR NOT"},
		]
		var input = $("<input id='f_log_op' class='aci oi' style='width:6em'>")
		input.val(current)
		input.attr("acid", current)
		input.autocomplete({
			source: opts,
			minLength: 0,
			focus: function(event, ui) {
				event.preventDefault()
				input.val(ui.item.label)
				input.attr("acid", ui.item.label)
			},
			select: function(event, ui) {
				event.preventDefault()
				input.val(ui.item.label)
				input.attr("acid", ui.item.label)
			}
		})
		input.click(function(){
			input.autocomplete("search")
		})
		input.keyup(function(){
			var opts = input.autocomplete("option").source
			var current = input.val()
			var found = false
			for (var i=0; i<opts.length; i++) {
				var opt = opts[i]
				if (opt.label == current) {
					found = true
					break
				}
			}
			if (!found) {
				input.addClass("constraint_violation")
			} else {
				input.removeClass("constraint_violation")
				input.attr("acid", opt.value)
			}
		})
		return input
	}

	o.fset_name_input = function(current) {
		var input = $("<input id='encap_fset_id' class='aci oi'>")
		var opts = []
		for (var i=0; i<osvc.fset_selector.get_data.length; i++) {
			opts.push({
				"label": osvc.fset_selector.get_data[i].fset_name,
				"value": osvc.fset_selector.get_data[i].id
			})
		}
		input.val(current)
		input.attr("acid", o.get_fset_id(current))
		input.autocomplete({
			source: opts,
			minLength: 0,
			focus: function(event, ui) {
				event.preventDefault()
				input.val(ui.item.label)
				input.attr("acid", ui.item.value)
			},
			select: function(event, ui) {
				event.preventDefault()
				input.val(ui.item.label)
				input.attr("acid", ui.item.value)
			}
		})
		input.click(function(){
			input.autocomplete("search")
		})
		input.keyup(function(){
			var opts = input.autocomplete("option").source
			var current = input.val()
			var found = false
			for (var i=0; i<opts.length; i++) {
				var opt = opts[i]
				if (opt.label == current) {
					found = true
					break
				}
			}
			if (!found) {
				input.addClass("constraint_violation")
			} else {
				input.removeClass("constraint_violation")
				input.attr("acid", opt.value)
			}
		})
		return input
	}

	o.f_value_input = function(current) {
		var input = $("<input id='f_value' class='oi'>")
		input.val(current)
		input.attr("acid", current)
		input.keyup(function(){
			if (!$(this).val()) {
				$(this).addClass("constraint_violation")
				$(this).attr("acid", "")
			} else {
				$(this).removeClass("constraint_violation")
				$(this).attr("acid", $(this).val())
			}
		})
		return input
	}

	o.f_op_input = function(current) {
		if (!current) {
			current = "="
		}
		var opts = [
			{"label": "=", "value": "="},
			{"label": ">", "value": ">"},
			{"label": "<", "value": "<"},
			{"label": ">=", "value": ">="},
			{"label": "<=", "value": "<="},
			{"label": "LIKE", "value": "LIKE"},
			{"label": "IN", "value": "IN"}
		]
		var input = $("<input id='f_op' class='aci oi' style='width:3em'>")
		input.val(current)
		input.attr("acid", current)
		input.autocomplete({
			source: opts,
			minLength: 0,
			focus: function(event, ui) {
				event.preventDefault()
				input.val(ui.item.label)
				input.attr("acid", ui.item.label)
			},
			select: function(event, ui) {
				event.preventDefault()
				input.val(ui.item.label)
				input.attr("acid", ui.item.label)
			}
		})
		input.click(function(){
			input.autocomplete("search")
		})
		input.keyup(function(){
			var opts = input.autocomplete("option").source
			var current = input.val()
			var found = false
			for (var i=0; i<opts.length; i++) {
				var opt = opts[i]
				if (opt.label == current) {
					found = true
					break
				}
			}
			if (!found) {
				input.addClass("constraint_violation")
			} else {
				input.removeClass("constraint_violation")
				input.attr("acid", opt.value)
			}
		})
		return input
	}

	o.f_field_input = function(table, current) {
		var fields = {
			'nodes': table_nodes_defaults.columns,
			'services': table_services_defaults.columns,
			'svcmon': table_service_instances_defaults.columns.filter(function(e){
				return e.match(/^mon_/)
			}),
			'resmon': table_resources_defaults.columns.filter(function(e){
				return e.match(/^res_/)
			}),
			'b_disk_app': ["disk_devid", "disk_vendor", "svcdisk_updated", "disk_updated", "disk_raid", "disk_used", "svcdisk_id", "disk_arrayid", "disk_id", "disk_level", "disk_name", "disk_created", "disk_dg", "disk_model", "disk_local", "disk_group", "disk_size", "disk_alloc", "disk_region"],
			'node_hba': ["hba_type", "hba_id"],
			'apps': table_apps_defaults.columns,
			'v_comp_moduleset_attachments': ['modset_name'],
			'v_tags': ['tag_name'],
			'packages': table_packages_defaults.columns.filter(function(e){
				return e.match(/^pkg_/)
			})
		}

		var input = $("<input id='f_field' class='aci oi'>")
		var opts = []
		var keys = fields[table]
console.log(table, keys)
		if (!keys) {
			keys = []
		}
		keys.sort()
		for (var i=0; i<keys.length; i++) {
			t = keys[i]
			if (t in db_columns) {
				opts.push({
					"label": db_columns[t].title,
					"cl": db_columns[t].img,
					"value": t
				})
			} else {
				opts.push({
					"label": t,
					"value": t
				})
			}
		}
		if (current && db_columns[current]) {
			input.val(db_columns[current].title)
			input.attr("acid", current)
		}
		input.autocomplete({
			source: opts,
			minLength: 0,
			focus: function(event, ui) {
				event.preventDefault()
				input.val(ui.item.label)
				input.attr("acid", ui.item.value)
			},
			select: function(event, ui) {
				event.preventDefault()
				input.val(ui.item.label)
				input.attr("acid", ui.item.value)
			}
		})
		input.click(function(){
			input.autocomplete("search")
		})
		input.keyup(function(){
			var opts = input.autocomplete("option").source
			var current = input.val()
			var found = false
			for (var i=0; i<opts.length; i++) {
				var opt = opts[i]
				if (opt.label == current) {
					found = true
					break
				}
			}
			if (!found) {
				input.addClass("constraint_violation")
			} else {
				input.removeClass("constraint_violation")
				input.attr("acid", opt.value)
			}
		})
		input.data("autocomplete")._renderItem = function(ul, item) {
			return $("<li></li>")
				.data("item.autocomplete", item)
				.append("<a class='icon_fixed_width "+item.cl+"'>"+item.label+"</a>")
				.appendTo(ul)
		}
		return input
	}

	o.f_table_input = function(current) {
		var input = $("<input id='f_table' class='aci oi'>")
		var opts = []
		var keys = []
		for (t in db_tables) {
			keys.push(t)
		}
		keys.sort()
		for (var i=0; i<keys.length; i++) {
			t = keys[i]
			opts.push({
				"label": db_tables[t].title,
				"cl": db_tables[t].cl,
				"value": db_tables[t].name
			})
		}
		if (current) {
			input.val(db_tables[current].title)
			input.attr("acid", current)
		}
		input.autocomplete({
			source: opts,
			minLength: 0,
			focus: function(event, ui) {
				event.preventDefault()
				input.val(ui.item.label)
				input.attr("acid", ui.item.value)
				var new_fields = o.f_field_input(ui.item.value)
				input.parents(".fset_designer_item,.fset_designer_adder").first().find("span#f_field").html(new_fields)
			},
			select: function(event, ui) {
				event.preventDefault()
				input.val(ui.item.label)
				input.attr("acid", ui.item.value)
				var new_fields = o.f_field_input(ui.item.value)
				input.parents(".fset_designer_item,.fset_designer_adder").first().find("span#f_field").html(new_fields)
			}
		})
		input.click(function(){
			input.autocomplete("search")
		})
		input.keyup(function(){
			var opts = input.autocomplete("option").source
			var current = input.val()
			var found = false
			for (var i=0; i<opts.length; i++) {
				var opt = opts[i]
				if (opt.label == current) {
					found = true
					break
				}
			}
			if (!found) {
				input.addClass("constraint_violation")
			} else {
				input.removeClass("constraint_violation")
				input.attr("acid", opt.value)
			}
		})
		input.data("autocomplete")._renderItem = function(ul, item) {
			return $("<li></li>")
				.data("item.autocomplete", item)
				.append("<a class='icon_fixed_width "+item.cl+"'>"+item.label+"</a>")
				.appendTo(ul)
		}
		return input
	}

	o.save_input = function() {
		var input = $("<input type='submit'>").val(i18n.t("fset_designer.save"))
		return input
	}

	o.render_new_filter = function(div, data) {
		if (!data) {
			data = {filter: {}}
		}
		div.empty()
		var handle = $("<span class='fa fa-bars clickable'></span>")
		div.append(handle)

		var log_op = $("<span></span>")
		log_op.append(o.log_op_input(data.f_log_op))
		div.append(log_op)

		var f_table = $("<span id='f_table'></span>")
		f_table.append(o.f_table_input(data.filter.f_table))
		div.append(f_table)

		var f_field = $("<span id='f_field'></span>")
		f_field.append(o.f_field_input(data.filter.f_table, data.filter.f_field))
		div.append(f_field)

		var f_op = $("<span id='f_op'></span>")
		f_op.append(o.f_op_input(data.filter.f_op))
		div.append(f_op)

		var f_value = $("<span id='f_value'></span>")
		f_value.append(o.f_value_input(data.filter.f_value))
		div.append(f_value)

		var save = $("<span></span>")
		var save_b = o.save_input()
		save.append(save_b)
		div.append(save)

		var original_f_id = data.filter.id

		var timer = null
		var xhr = null

		// highlight the item if the filter does not exist yet
		div.find("input.oi").keyup(function(event){
			clearTimeout(timer)
			timer = setTimeout(function(){
				if (xhr) {
					xhr.abort()
				}
				services_osvcgetrest("/filters", "", {
					"filters": [
						"f_table="+div.find("input#f_table").attr("acid"),
						"f_field="+div.find("input#f_field").attr("acid"),
						"f_op="+div.find("input#f_op").attr("acid"),
						"f_value="+div.find("input#f_value").attr("acid")
					]
				}, function(jd){
					if (jd.data && jd.data.length > 0) {
						div.removeClass("highlight")
					} else {
						div.addClass("highlight")
					}
				})
			}, 500)
		})

		save_b.click(function(event){
			event.stopPropagation()
			$(this).prop("disabled", true)
			var item = $(this).parents(".fset_designer_adder,.fset_designer_item").first()
			var e_f_log_op = item.find("input#f_log_op")
			var e_f_table = item.find("input#f_table")
			var e_f_field = item.find("input#f_field")
			var e_f_op = item.find("input#f_op")
			var e_f_value = item.find("input#f_value")

			// get existing filter id or create filter
			var f_id = null
			services_osvcgetrest("/filters", "", {
				"filters": [
					"f_table="+e_f_table.attr("acid"),
					"f_field="+e_f_field.attr("acid"),
					"f_op="+e_f_op.attr("acid"),
					"f_value="+e_f_value.attr("acid")
				]
			}, function(jd){
				if (jd.data && jd.data.length > 0) {
					var f_id = jd.data[0].id
					attach(f_id)
				} else {
					var _data = {
						"f_table": e_f_table.attr("acid"),
						"f_field": e_f_field.attr("acid"),
						"f_op": e_f_op.attr("acid"),
						"f_value": e_f_value.attr("acid")
					}
					services_osvcpostrest("/filters", "", "", _data, function(jd){
						div.removeClass("highlight")
						var f_id = jd.data[0].id
						attach(f_id)
					})
				}
			})

			function attach(f_id) {
				var data = {
					"f_log_op": e_f_log_op.attr("acid"),
					"f_order": o.div.find(".fset_designer_item,.fset_designer_adder").index(item)
				}
				services_osvcpostrest("/filtersets/%1/filters/%2", [o.options.fset_id, f_id], "", data, function(){
					if (original_f_id && (original_f_id != f_id)) {
						services_osvcdeleterest("/filtersets/%1/filters/%2", [o.options.fset_id, original_f_id], "", "", function(){})
					}
					var _data = {
						"id": f_id,
						"f_table": e_f_table.attr("acid"),
						"f_field": e_f_field.attr("acid"),
						"f_op": e_f_op.attr("acid"),
						"f_value": e_f_value.attr("acid")
					}
					data.filter = _data
					o.render_item(item, data)
				})
			}
		})

		var del = $("<span class='icon del16 highlight clickable' style='float:right'></span>")
		div.append(del)
		del.click(function(){
			var item = $(this).parents(".fset_designer_adder,.fset_designer_item").first()
			if (item.attr("f_id")) {
				var service = "/filtersets/%1/filters/%2"
				var f_id = item.attr("f_id")
				var service_parameters = [o.options.fset_id, f_id]
			} else {
				// not yet submitted
				div.remove()
				return
			}
			services_osvcdeleterest(service, service_parameters, "", "", function(){
				div.remove()
			})
		})

		div.find("input").first().focus()
	}

	o.render_new_filterset = function(div, data) {
		if (!data) {
			data = {}
		}
		div.empty()
		var handle = $("<span class='fa fa-bars clickable'></span>")
		div.append(handle)

		var log_op = $("<span></span>")
		log_op.append(o.log_op_input(data.f_log_op))
		div.append(log_op)

		var fset_name = $("<span class='icon filter16'></span>")
		fset_name.append(o.fset_name_input(data.filterset))
		div.append(fset_name)

		var save = $("<span></span>")
		var save_b = o.save_input()
		save.append(save_b)
		div.append(save)

		var original_fset_id = o.get_fset_id(data.filterset)

		save_b.click(function(event){
			event.stopPropagation()
			$(this).prop("disabled", true)
			var item = $(this).parents(".fset_designer_adder,.fset_designer_item").first()
			var e_encap_fset_id = item.find("input#encap_fset_id")
			var e_f_log_op = item.find("input#f_log_op")
			var encap_fset_id = e_encap_fset_id.attr("acid")
			var data = {
				"f_log_op": e_f_log_op.attr("acid"),
				"f_order": o.div.find(".fset_designer_item,.fset_designer_adder").index(item)
			}
			services_osvcpostrest("/filtersets/%1/filtersets/%2", [o.options.fset_id, encap_fset_id], "", data, function(){
				if (original_fset_id && (original_fset_id != encap_fset_id)) {
					services_osvcdeleterest("/filtersets/%1/filtersets/%2", [o.options.fset_id, original_fset_id], "", "", function(){})
				}
				data.filterset = e_encap_fset_id.val()
				o.render_item(item, data)
			})
		})

		var del = $("<span class='icon del16 highlight clickable' style='float:right'></span>")
		div.append(del)
		del.click(function(){
			var item = $(this).parents(".fset_designer_adder,.fset_designer_item").first()
			if (item.attr("fset_id")) {
				var service = "/filtersets/%1/filtersets/%2"
				var encap_fset_id = item.attr("fset_id")
				var service_parameters = [o.options.fset_id, encap_fset_id]
			} else {
				// not yet submitted
				div.remove()
				return
			}
			services_osvcdeleterest(service, service_parameters, "", "", function(){
				div.remove()
			})
		})

		div.find("input").first().focus()
	}

	o.add_adder = function(data) {
		var item = $("<div class='fset_designer_adder'></div>")

		var handle = $("<span class='fa fa-plus-square'></span>")
		item.append(handle)

		var s1 = $("<span class='icon filter16 clickable'></span>")
		s1.text(i18n.t("fset_designer.add_filter"))
		item.append(s1)
		s1.click(function(){
			o.render_new_filter(item)
			o.add_adder()
		})

		var s2 = $("<span class='icon filter16 clickable'></span>")
		s2.text(i18n.t("fset_designer.add_filterset"))
		item.append(s2)
		s2.click(function(){
			o.render_new_filterset(item)
			o.add_adder()
		})

		o.area.append(item)
	}

	o.get_fset_id = function(fset_name) {
		for (var i=0; i<osvc.fset_selector.get_data.length; i++) {
			if (osvc.fset_selector.get_data[i].fset_name == fset_name) {
				return osvc.fset_selector.get_data[i].id
			}
		}
	}

	o.add_item = function(data) {
		var item = $("<div></div>")
		o.render_item(item, data)
		o.area.append(item)
	}

	o.render_item = function(item, data) {
		item.addClass("fset_designer_item").removeClass("fset_designer_adder")
		item.empty()
		var handle = $("<span class='fa fa-bars clickable'></span>")
		item.append(handle)

		var log_op = $("<span id='f_log_op' style='width:5em;display:inline-block'></span>").text(data.f_log_op)
		item.append(log_op)

		if (data.filterset) {
			item.attr("fset_id", o.get_fset_id(data.filterset))
			var fset_name = $("<span id='fset_name' class='icon filter16'></span>").text(data.filterset)
			item.append(fset_name)
		} else {
			item.attr("f_id", data.filter.id)
			item.append(o.render_f_table(data))
			item.append(o.render_f_field(data))

			var op = $("<span id='f_op'></span>").text(data.filter.f_op)
			item.append(op)

			var val = $("<span id='f_value'></span>").text(data.filter.f_value)
			item.append(val)
		}

		var edit = $("<span class='edit16 clickable' style='float:right'></span>")
		item.append(edit)
		edit.click(function(){
			var item = $(this).parents(".fset_designer_item").first()
			if (item.find("span#fset_name").length == 1) {
				var data = {
					"filterset": item.find("span#fset_name").text(),
					"f_log_op": item.find("span#f_log_op").text(),
				}
				o.render_new_filterset(item, data)
			} else {
				var data = {
					"filter": {
						"id": item.attr("f_id"),
						"f_table": item.find("span#f_table").attr("value"),
						"f_field": item.find("span#f_field").attr("value"),
						"f_op": item.find("span#f_op").text(),
						"f_value": item.find("span#f_value").text(),
					},
					"f_log_op": item.find("span#f_log_op").text(),
				}
				o.render_new_filter(item, data)
			}
		})

	}

	o.init()
	return o
}

