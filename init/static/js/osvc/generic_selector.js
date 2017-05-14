function generic_selector(divid, options) {
	//
	// options = {
	//   'url_path': <a rest handler symbolic name as defined in osvc-services.js>
	//   'url_wildcards': <array of values to be substiuted in source>
	//   'url_params': <parameters to set with the GET request>
	//   'data': <the list of data dictionnary to use instead of the result of a rest get>
	//   'object_id': <the data dictionnary key to use as selector obj id>
	//   'object_name': <the data dictionnary key to use as selector obj label>
	// }
	//
	o = options
	o.div = $("#"+divid)
	o.selected_class = "generic_selector_selected"
	o.object_base_class = "generic_selector_object"

	o._init = function() {
		for (var i=0; i<o.data.length; i++) {
			o.add_object(o.data[i])
		}
	}

	o.init = function() {
		if (typeof(o.multi) === "undefined") {
			o.multi = true
		}
		o.object_area = $("<div></div>")
		o.div.append(o.object_area)
		if (o.data) {
			o._init()
			return
		}
		spinner_add(o.object_area)
		services_osvcgetrest(o.url_path, o.url_wildcards, o.url_params, function(jd) {
			spinner_del(o.object_area)
			if (jd.error && (jd.error.length > 0)) {
				o.object_area.html(services_error_fmt(jd))
				return
			}
			o.data = jd.data
			o._init()
		},
		function(xhr, stat, error) {
			o.object_area.html(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.add_object = function(data) {
		var object = $("<div class='icon'></div>")
		object.addClass(o.object_class)
		object.addClass(o.object_base_class)
		object.attr("obj_id", data[o.object_id])
		object.text(data[o.object_name])
		o.object_area.append(object)
		object.bind("click", function(event) {
			if (o.multi == false) {
				o.object_area.find("."+o.selected_class).removeClass(o.selected_class)
			}
			$(this).toggleClass(o.selected_class)
		})
	}

	o.get_selected = function() {
		var data = []
		o.object_area.find("."+o.selected_class).each(function(){
			data.push($(this).attr("obj_id"))
		})
		return data
	}
	o.init()
	return o
}

function generic_selector_tags(id) {
	return generic_selector(id, {
		"url_path": "R_TAGS",
		"url_params": {
			"orderby": "tag_name",
			"limit": "0",
			"props": "tag_id,tag_name",
			"meta": "0"
		},
		"object_class": "tag16",
		"object_id": "tag_id",
		"object_name": "tag_name"
	})
}

function generic_selector_modsets(id) {
	return generic_selector(id, {
		"url_path": "R_COMPLIANCE_MODULESETS",
		"url_params": {
			"orderby": "modset_name",
			"limit": "0",
			"props": "id,modset_name",
			"meta": "0"
		},
		"object_class": "modset16",
		"object_id": "id",
		"object_name": "modset_name"
	})
}

function generic_selector_rulesets(id) {
	return generic_selector(id, {
		"url_path": "R_COMPLIANCE_RULESETS",
		"url_params": {
			"orderby": "ruleset_name",
			"limit": "0",
			"props": "id,ruleset_name",
			"meta": "0",
			"filters": ["ruleset_type=explicit", "ruleset_public=T"]
		},
		"object_class": "comp16",
		"object_id": "id",
		"object_name": "ruleset_name"
	})
}

function generic_selector_checks_contextual_settings(id) {
	return generic_selector(id, {
		"url_path": "R_CHECKS_CONTEXTUAL_SETTINGS",
		"url_params": {
			"orderby": "name",
			"limit": "0",
			"props": "id,name",
			"meta": "0"
		},
		"object_class": "filter16",
		"object_id": "id",
		"object_name": "name"
	})
}

function generic_selector_org_groups(id, options) {
	var filters = ["privilege F"]
	if (options.exclude) {
		filters.push("role !("+options.exclude.join(",")+")")
	}
	return generic_selector(id, {
		"url_path": "R_GROUPS",
		"url_params": {
			"orderby": "role",
			"limit": "0",
			"props": "id,role",
			"filters": filters,
			"meta": "0"
		},
		"object_class": "guys16",
		"object_id": "id",
		"object_name": "role"
	})
}

function generic_selector_privilege_groups(id) {
	return generic_selector(id, {
		"url_path": "R_GROUPS",
		"url_params": {
			"orderby": "role",
			"limit": "0",
			"props": "id,role",
			"filters": ["privilege T"],
			"meta": "0"
		},
		"object_class": "guys16",
		"object_id": "id",
		"object_name": "role"
	})
}

function generic_selector_groups(id) {
	return generic_selector(id, {
		"url_path": "R_GROUPS",
		"url_params": {
			"orderby": "role",
			"limit": "0",
			"props": "id,role",
			"meta": "0"
		},
		"object_class": "guys16",
		"object_id": "id",
		"object_name": "role"
	})
}

function generic_selector_filtersets(id) {
	return generic_selector(id, {
		"url_path": "/filtersets",
		"url_params": {
			"orderby": "fset_name",
			"limit": "0",
			"props": "id,fset_name",
			"meta": "0"
		},
		"object_class": "filter16",
		"object_id": "id",
		"object_name": "fset_name"
	})
}

function generic_selector_filters(id) {
	return generic_selector(id, {
		"url_path": "/filters",
		"url_params": {
			"orderby": "f_label",
			"limit": "0",
			"props": "id,f_label",
			"meta": "0"
		},
		"object_class": "filter16",
		"object_id": "id",
		"object_name": "f_label"
	})
}

function generic_selector_operator(id) {
	return generic_selector(id, {
		"data": [
			{"id": "AND"},
			{"id": "OR"},
			{"id": "AND NOT"},
			{"id": "OR NOT"}
		],
		"object_class": "filter16",
		"object_id": "id",
		"object_name": "id",
		"multi": false
	})
}

function generic_selector_order(id) {
	return generic_selector(id, {
		"data": [
			{"id": 0},
			{"id": 1},
			{"id": 2},
			{"id": 3},
			{"id": 4},
			{"id": 5},
			{"id": 6},
			{"id": 7},
			{"id": 8},
			{"id": 9}
		],
		"object_class": "filter16",
		"object_id": "id",
		"object_name": "id",
		"multi": false
	})
}

