function tags(options) {
	var o = {}
	o.options = options

	try {
		// element id
		o.div = $("#"+options.tid)
	} catch(e) {
		// jquery object
		o.div = options.tid
		o.div.uniqueId()
		o.options.tid = o.div.attr("id")
	}
	o.div.css({"min-height": "1em"})

	o.load = function() {
		// try to guess a title element
		if (!o.options.e_title) {
			o.options.e_title = o.div.prev(".line").children().first()
		}

		// init tags zone
		o.e_tags = $("<div class='tag_container' name='tag_container'></div>")
		o.div.append(o.e_tags)

		// init placeholders
		o.e_candidates = $("")
		o.e_tag_add_input = $("")

		// init edit/add/del tools
		if (o.options.responsible && o.options.candidates != true) {
			o.e_tools = $("<div class='tag_container mb-2 mt-2'></div>")
			o.e_del_tag = o.add_del_tag().hide()
			o.e_add_tag = o.add_add_tag().hide()
			o.e_tools.append(o.e_del_tag)
			o.e_tools.append(o.e_add_tag)
			o.div.append(o.e_tools)
			o.add_edit()
		} else {
			o.e_tools = $("")
			o.e_edit = $("")
			o.e_del_tag = $("")
			o.e_add_tag = $("")
		}

		// init error display zone
		if (!o.div.info) {
			info = $("<div></div>")
			o.div.append(info)
			o.div.info = info
		}
		o.reload_tags()
		o.div.info.empty()
	}

	o.reload_tags = function() {
		spinner_add(o.div.info)
		o.get(o.options.fval, function(_data) {
			spinner_del(o.div.info)
			if (_data.error) {
				o.div.info.html(services_error_fmt(_data))
				return
			}
			if (o.options.title && o.options.e_title && _data.meta) {
				o.options.e_title.text(i18n.t(o.options.title) + " (" + _data.meta.total + ")")
				o.add_edit()
			}
			_data = _data.data
			o.e_tags.empty()
			if ((_data.length == 0) && o.options.candidates) {
				if (o.options.create) {
					var msg = "tags.no_candidates_create"
				} else {
					var msg = "tags.no_candidates"
				}
				o.div.info.text(i18n.t(msg))
			}
			for (i=0; i<_data.length; i++) {
				o.e_tags.append(o.add_tag(_data[i]), " ")
			}
			if (_data.length > 4) {
				o.e_tags.addClass("grow")
			}
			o.bind_admin_tools()
			o.e_tags.children("[tag_id]").draggable({
				"opacity": 0.6,
				"addClasses": false,
				"revert": true,
				"refreshPositions": true,
				"zIndex": 3001
			})
		},
		function(xhr, stat, error) {
			o.div.info.html(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.add_tag = function(tag_data) {
		if (o.options.candidates == true) {
			if (o.options.parent_object.e_tags.find("[tag_id="+tag_data[o.options.id]+"]").length > 0) {
				// candidate already attached
				return
			}
			cl = "icon tag tag_candidate"
		} else {
			cl = "icon tag tag_attached"
		}
		s = "<span tag_id='"+tag_data[o.options.id]+"' class='"+cl+"'>"+tag_data[o.options.tag_name]+" </span>"
		var e = $(s)
		if (o.options.bgcolor) {
			e.css({"background-color": o.options.bgcolor})
		}
		e.bind("mouseover", function(){
			if (o.options.responsible && o.options.candidates != true) {
				$(this).addClass("tag_drag")
			}
		})
		e.bind("mouseout", function(){
			if (o.options.responsible && o.options.candidates != true) {
				$(this).removeClass("tag_drag")
			}
		})
		e.bind("click", function(event){
			event.stopPropagation()
			if (!o.options.responsible) {
				return
			}
			if ($(this).hasClass("tag_candidate")) {
				o.attach_tag(tag_data)
				return
			}
		})
		e.bind("dblclick", function(event){
			if (!o.options.ondblclick) {
				return
			}
			var options = {
				"name": $(this).text(),
				"id": $(this).attr("tag_id"),
			}
			if (o.options.flash_id_prefix) {
				var flash_id_prefix = o.options.flash_id_prefix
			} else {
				var flash_id_prefix = o.options.tag_name
			}
			var flash_id = flash_id_prefix+"-"+$(this).attr("tag_id")
			osvc.flash.show({
				id: flash_id,
				text: $(this).text(),
				bgcolor: o.options.bgcolor,
				cl: "icon "+o.options.icon,
				fn: function(id){
					o.options.ondblclick(id, options)
				}
			})
		})
		return e
	}

	o.del_tag = function(tag_data) {
		o.div.find("[tag_id="+tag_data[o.options.id]+"].tag").hide("fade", function(){
			$(this).remove()
		})
	}

	o.add_edit = function() {
		if (o.options.candidates) {
			return
		}
		var e = $("<span class='clickable editable editable-placeholder' style='cursor:pointer'></span>")
		e.bind("click", function(){
			if (o.e_add_tag.is(":visible")) {
				o.e_add_tag.hide()
				o.e_del_tag.hide()
				o.e_candidates.hide()
			} else {
				o.e_add_tag.show()
				o.e_del_tag.show()
				o.e_candidates.show()
			}
		})
		o.e_edit = e
		if (o.options.e_title) {
			o.options.e_title.append(o.e_edit)
		}
		return e
	}

	o.add_add_tag = function() {
		if (o.options.candidates) {
			return
		}
		var e = $("<span class='icon tag tag_add'></span>")
		e.text(i18n.t("tags.add"))
		e.bind("click", function(){
			var e = $(this).find(".tag_input")
			if (e.length>0) {
				return
			}
			o.e_tag_add_input = $("<input class='tag_input'></input>")
			$(this).html(o.e_tag_add_input)
			o.e_tag_add_input.bind("keyup", function(event){
				o.input_keyup(event)
			})
			o.e_tag_add_input.focus()
		})
		return e
	}

	o.add_del_tag = function() {
		if (o.options.candidates) {
			return
		}
		var e = $("<span class='icon tag tag_del'></span>")
		e.text(i18n.t("tags.del"))
		e.droppable({
			accept: ".tag",
			activeClass: "tag_del_active",
			hoverClass: "tag_del_hover",
			drop: function(event, ui) {
				o.detach_tag(ui.draggable)
			}
		})
		return e
	}

	o.add_candidates = function() {
		fval = o.e_tag_add_input.val()
		if (fval.length == 0) {
			fval = '%'
		} else {
			fval = fval.replace(/\//, "_")
			fval = encodeURIComponent(fval)
			if (fval[0] != '%') {
				fval = '%' + fval
			}
			if (fval[fval.length-1] != '%') {
				fval = fval + '%'
			}
		}

		// 1st candidates exec: init a new tag object
		ctid = o.options.tid+"c"
		options = $.extend({}, o.options, {
			"tid": ctid,
			"parent_object": o,
			"fval": fval,
			"candidates": true
		})
		o.div.find("#"+ctid).parent().remove()
		o.e_candidates = $("<span><h3>"+i18n.t("tags.candidates")+"</h3><div id='"+ctid+"' class='tags'></div></span>")
		if (o.options.bgcolor) {
			o.e_candidates.css({"background-color": o.options.bgcolor})
		}
		o.div.append(o.e_candidates)
		o.candidates = tags(options)
	}

	o._attach_tag = function(tag_data) {
		var tag = o.div.find("[tag_id="+tag_data["id"]+"]")
		tag.remove()
		spinner_add(o.div.info, i18n.t("tags.attaching"))
		o.options.attach(tag_data, function(jd) {
			spinner_del(o.div.info)
			if (jd.error) {
				o.div.info.html(services_error_fmt(jd))
				return
			}
			// refresh tags
			if (o.options.parent_object) {
				o.options.parent_object.reload_tags()
			} else {
				o.reload_tags()
			}
		},
		function(xhr, stat, error) {
			o.div.info.html(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.create_and_attach_tag = function(tag_data) {
		o.div.info.empty()
		o.candidates.div.parent().remove()
		o.options.get_candidates(tag_data[o.options.tag_name], function(jd) {
			if (o.options.create && (!jd.data || (jd.data.length == 0))) {
				// tag does not exist yet ... create
				spinner_add(o.div.info, i18n.t("tags.creating"))
				o.options.create(tag_data, function(jd) {
					spinner_del(o.div.info)
					if (jd.error) {
						o.div.info.html(services_error_fmt(jd))
						return
					}
					o._attach_tag(jd.data)
				},
				function(xhr, stat, error) {
					o.div.info.html(services_ajax_error_fmt(xhr, stat, error))
				})
			} else if (jd.data && (jd.data.length == 1)) {
				// tag already exists
				o._attach_tag(jd.data[0])
			} else {
				console.log("no candidate found")
			}
		},
		function(xhr, stat, error) {
			o.div.info.html(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.attach_tag = function(tag_data) {
		if (!tag_data[o.options.id]) {
			// from <enter> in add tag
			o.create_and_attach_tag(tag_data)

		} else {
			// from click on a candidate
			o._attach_tag(tag_data)
		}
	}

	o.detach_tag = function(tag) {
		o.div.info.empty()
		tag.hide()
		spinner_add(o.div.info, i18n.t("tags.detaching"))
		o.options.detach(tag, function(jd) {
			spinner_del(o.div.info)
			if (jd.error) {
				o.div.info.html(services_error_fmt(jd))
				tag.show()
				return
			}
			tag.remove()
			fval = o.e_tag_add_input.val()
			if (fval && (fval != "")) {
				// refresh candidates, in case the removed tag
				// should appear in the candidates list
				o.add_candidates()
			}
		},
		function(xhr, stat, error) {
			tag.show()
			o.div.info.html(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.bind_admin_tools = function() {
		// show tag admin tools to responsibles and managers
		if (o.options.responsible || services_ismemberof("Manager")) {
			o.e_edit.show()
		} else {
			o.e_edit.hide()
		}
	}

	o.event_handler = function(data) {
		if (o.options.candidates == true) {
			return
		}
		if (!o.e_add_tag || o.e_add_tag.is(":visible")) {
			return
		}
		if (o.options.event_handler) {
			// custom event handler
			o.options.event_handler(o, data)
		}
		if (o.options.events) {
			// simple reload tags action
			for (var i=0; i<o.options.events.length; i++) {
				if (o.options.events[i] == data.event) {
					o.reload_tags()
					return
				}
			}
		}
	}

	o.input_keyup = function(event) {
		tag = $(event.target).parent()
		if (!is_enter(event)) {
			tag.removeClass("tag_create")
			tag.find("input").removeClass("tag_create")
			o.add_candidates()
			return
		}
		o.attach_tag({"tag_name": o.e_tag_add_input.val()})
	}

	o.get = function(fval, callback, callback_err) {
		if ("candidates" in o.options) {
			return o.options.get_candidates(fval, callback, callback_err)
		} else {
			return o.options.get_tags(fval, callback, callback_err)
		}
	}

	wsh["tags_"+o.options.tid] = function(data) {
		o.event_handler(data)
	}

	o.options.am_i_responsible(function(jd){
		o.options.responsible = jd.data
		o.load()
	})
	return o
}


function node_tags(options) {
	options.tag_name = "tag_name"
	options.id = "tag_id"
	options.flash_id_prefix = "node"
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("R_NODE_TAGS", [options.node_id], {
			"orderby": options.tag_name,
			"props": "tag_id," + options.tag_name,
			"limit": "0"
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("R_NODE_CANDIDATE_TAGS", [options.node_id], {
			"orderby": options.tag_name,
			"props": "tag_id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": [options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.create = function(tag_data, callback, callback_err) {
		services_osvcpostrest("R_TAGS", "", "", tag_data, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("R_TAG_NODE", [tag_data.tag_id, options.node_id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("R_TAG_NODE", [tag.attr("tag_id"), options.node_id], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		services_osvcgetrest("R_NODE_AM_I_RESPONSIBLE", [options.node_id], "", callback)
	}
	options.event_handler = function(o, data) {
		if (!("data" in data)) {
			return
		} 
		data = data.data
		if (!data.node_id || (o.options.node_id != data.node_id)) {
			return
		}
		if (!("action" in data)) {
			return
		}
		if (data["action"] == "attach") {
			if (o.div.find("[tag_id="+data.tag_id+"]").length > 0) {
				return
			}
			o.div.children("div").first().prepend(o.add_tag({
				"id": data.tag_id,
				"tag_name": data[o.options.tag_name]
			}))
		} else if (data.action == "detach") {
			o.del_tag({
				"tag_id": data.tag_id,
			})
		}
	}


	return tags(options)
}

function service_tags(options) {
	options.tag_name = "tag_name"
	options.flash_id_prefix = "svc"
	options.id = "tag_id"
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("R_SERVICE_TAGS", [options.svc_id], {
			"orderby": options.tag_name,
			"props": "tag_id," + options.tag_name,
			"limit": "0"
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("R_SERVICE_CANDIDATE_TAGS", [options.svc_id], {
			"orderby": options.tag_name,
			"props": "tag_id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": [options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.create = function(tag_data, callback, callback_err) {
		services_osvcpostrest("R_TAGS", "", "", tag_data, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("R_TAG_SERVICE", [tag_data.tag_id, options.svc_id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("R_TAG_SERVICE", [tag.attr("tag_id"), options.svc_id], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		services_osvcgetrest("R_SERVICE_AM_I_RESPONSIBLE", [options.svc_id], "", callback)
	}
	options.event_handler = function(data, o) {
		if (!("data" in data)) {
			return
		} 
		data = data.data
		if (!data.svc_id || (o.options.svc_id != data.svc_id)) {
			return
		}
		if (!("action" in data)) {
			return
		}
		if (data["action"] == "attach") {
			if (o.div.find("[tag_id="+data.tag_id+"]").length > 0) {
				return
			}
			o.div.children("div").first().prepend(o.add_tag({
				"id": data.tag_id,
				"tag_name": data[o.options.tag_name]
			}))
		} else if (data.action == "detach") {
			o.del_tag({
				"tag_id": data.tag_id,
			})
		}
	}

	return tags(options)
}

function app_responsibles(options) {
	options.tag_name = "role"
	options.flash_id_prefix = "group"
	options.id = "id"
	options.bgcolor = osvc.colors.org
	options.icon = "guys16"
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/apps/%1/responsibles", [options.app_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0"
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/groups", "", {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": ["privilege F", options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("R_APP_RESPONSIBLE", [options.app_id, tag_data.id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("R_APP_RESPONSIBLE", [options.app_id, tag.attr("tag_id")], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		services_osvcgetrest("R_APP_AM_I_RESPONSIBLE", [options.app_id], "", callback)
	}
	options.ondblclick = function(divid, data) {
		group_tabs(divid, {"group_id": data.id, "group_name": data.name})
	}
	options.events = ["auth_group_change", "apps_responsibles_change"]
	return tags(options)
}

function app_publications(options) {
	options.tag_name = "role"
	options.flash_id_prefix = "group"
	options.id = "id"
	options.bgcolor = osvc.colors.org
	options.icon = "guys16"
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/apps/%1/publications", [options.app_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0"
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/groups", "", {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": ["privilege F", options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("R_APP_PUBLICATION", [options.app_id, tag_data.id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("R_APP_PUBLICATION", [options.app_id, tag.attr("tag_id")], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		services_osvcgetrest("R_APP_AM_I_RESPONSIBLE", [options.app_id], "", callback)
	}
	options.ondblclick = function(divid, data) {
		group_tabs(divid, {"group_id": data.id, "group_name": data.name})
	}
	options.events = ["auth_group_change", "apps_publications_change"]
	return tags(options)
}

function form_responsibles(options) {
	options.tag_name = "role"
	options.flash_id_prefix = "group"
	options.id = "id"
	options.bgcolor = osvc.colors.org
	options.icon = "guys16"
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/forms/%1/responsibles", [options.form_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0"
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/groups", "", {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": ["privilege F", options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("R_FORM_RESPONSIBLE", [options.form_id, tag_data.id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("R_FORM_RESPONSIBLE", [options.form_id, tag.attr("tag_id")], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		services_osvcgetrest("R_FORM_AM_I_RESPONSIBLE", [options.form_id], "", callback)
	}
	options.ondblclick = function(divid, data) {
		group_tabs(divid, {"group_id": data.id, "group_name": data.name})
	}
	options.events = ["auth_group_change", "forms_team_responsible_change"]
	return tags(options)
}

function form_publications(options) {
	options.tag_name = "role"
	options.flash_id_prefix = "group"
	options.id = "id"
	options.bgcolor = osvc.colors.org
	options.icon = "guys16"
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/forms/%1/publications", [options.form_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0"
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/groups", "", {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": ["privilege F", options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("R_FORM_PUBLICATION", [options.form_id, tag_data.id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("R_FORM_PUBLICATION", [options.form_id, tag.attr("tag_id")], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		services_osvcgetrest("R_FORM_AM_I_RESPONSIBLE", [options.form_id], "", callback)
	}
	options.ondblclick = function(divid, data) {
		group_tabs(divid, {"group_id": data.id, "group_name": data.name})
	}
	options.events = ["auth_group_change", "forms_team_publication_change"]
	return tags(options)
}

function ruleset_responsibles(options) {
	options.tag_name = "role"
	options.flash_id_prefix = "group"
	options.id = "id"
	options.bgcolor = osvc.colors.org
	options.icon = "guys16"
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/compliance/rulesets/%1/responsibles", [options.ruleset_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0"
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/groups", "", {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": ["privilege F", options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("/compliance/rulesets/%1/responsibles/%2", [options.ruleset_id, tag_data.id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("/compliance/rulesets/%1/responsibles/%2", [options.ruleset_id, tag.attr("tag_id")], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		services_osvcgetrest("/compliance/rulesets/%1/am_i_responsible", [options.ruleset_id], "", callback)
	}
	options.ondblclick = function(divid, data) {
		group_tabs(divid, {"group_id": data.id, "group_name": data.name})
	}
	options.events = ["auth_group_change", "comp_rulesets_change"]
	return tags(options)
}

function ruleset_publications(options) {
	options.tag_name = "role"
	options.flash_id_prefix = "group"
	options.id = "id"
	options.bgcolor = osvc.colors.org
	options.icon = "guys16"
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/compliance/rulesets/%1/publications", [options.ruleset_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0"
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/groups", "", {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": ["privilege F", options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("/compliance/rulesets/%1/publications/%2", [options.ruleset_id, tag_data.id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("/compliance/rulesets/%1/publications/%2", [options.ruleset_id, tag.attr("tag_id")], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		services_osvcgetrest("/compliance/rulesets/%1/am_i_responsible", [options.ruleset_id], "", callback)
	}
	options.ondblclick = function(divid, data) {
		group_tabs(divid, {"group_id": data.id, "group_name": data.name})
	}
	options.events = ["auth_group_change", "comp_ruleset_change"]
	return tags(options)
}

function prov_template_responsibles(options) {
	options.tag_name = "role"
	options.flash_id_prefix = "group"
	options.id = "id"
	options.bgcolor = osvc.colors.org
	options.icon = "guys16"
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/provisioning_templates/%1/responsibles", [options.tpl_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0"
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/groups", "", {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": ["privilege F", options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("/provisioning_templates/%1/responsibles/%2", [options.tpl_id, tag_data.id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("/provisioning_templates/%1/responsibles/%2", [options.tpl_id, tag.attr("tag_id")], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		services_osvcgetrest("/provisioning_templates/%1/am_i_responsible", [options.tpl_id], "", callback)
	}
	options.ondblclick = function(divid, data) {
		group_tabs(divid, {"group_id": data.id, "group_name": data.name})
	}
	options.events = ["auth_group_change", "prov_template_responsible_change"]
	return tags(options)
}

function prov_template_publications(options) {
	options.tag_name = "role"
	options.flash_id_prefix = "group"
	options.id = "id"
	options.bgcolor = osvc.colors.org
	options.icon = "guys16"
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/provisioning_templates/%1/publications", [options.tpl_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0"
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/groups", "", {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": ["privilege F", options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("/provisioning_templates/%1/publications/%2", [options.tpl_id, tag_data.id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("/provisioning_templates/%1/publications/%2", [options.tpl_id, tag.attr("tag_id")], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		services_osvcgetrest("/provisioning_templates/%1/am_i_responsible", [options.tpl_id], "", callback)
	}
	options.ondblclick = function(divid, data) {
		group_tabs(divid, {"group_id": data.id, "group_name": data.name})
	}
	options.events = ["auth_group_change", "prov_template_publication_change"]
	return tags(options)
}

function modset_responsibles(options) {
	options.tag_name = "role"
	options.flash_id_prefix = "group"
	options.id = "id"
	options.bgcolor = osvc.colors.org
	options.icon = "guys16"
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/compliance/modulesets/%1/responsibles", [options.modset_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0"
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/groups", "", {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": ["privilege F", options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("/compliance/modulesets/%1/responsibles/%2", [options.modset_id, tag_data.id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("/compliance/modulesets/%1/responsibles/%2", [options.modset_id, tag.attr("tag_id")], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		services_osvcgetrest("/compliance/modulesets/%1/am_i_responsible", [options.modset_id], "", callback)
	}
	options.ondblclick = function(divid, data) {
		group_tabs(divid, {"group_id": data.id, "group_name": data.name})
	}
	options.events = ["auth_group_change", "comp_moduleset_change"]
	return tags(options)
}

function modset_publications(options) {
	options.tag_name = "role"
	options.flash_id_prefix = "group"
	options.id = "id"
	options.bgcolor = osvc.colors.org
	options.icon = "guys16"
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/compliance/modulesets/%1/publications", [options.modset_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0"
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/groups", "", {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": ["privilege F", options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("/compliance/modulesets/%1/publications/%2", [options.modset_id, tag_data.id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("/compliance/modulesets/%1/publications/%2", [options.modset_id, tag.attr("tag_id")], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		services_osvcgetrest("/compliance/modulesets/%1/am_i_responsible", [options.modset_id], "", callback)
	}
	options.ondblclick = function(divid, data) {
		group_tabs(divid, {"group_id": data.id, "group_name": data.name})
	}
	options.events = ["auth_group_change", "comp_moduleset_change"]
	return tags(options)
}


function safe_file_responsibles(options) {
	options.tag_name = "role"
	options.flash_id_prefix = "group"
	options.id = "id"
	options.bgcolor = osvc.colors.org
	options.icon = "guys16"
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/safe/%1/responsibles", [options.uuid], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0"
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/groups", "", {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": ["privilege F", options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("/safe/%1/responsibles/%2", [options.uuid, tag_data.id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("/safe/%1/responsibles/%2", [options.uuid, tag.attr("tag_id")], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		services_osvcgetrest("/safe/%1/am_i_responsible", [options.uuid], "", callback)
	}
	options.ondblclick = function(divid, data) {
		group_tabs(divid, {"group_id": data.id, "group_name": data.name})
	}
	options.events = ["auth_group_change", "safe_team_responsible_change"]
	return tags(options)
}

function safe_file_publications(options) {
	options.tag_name = "role"
	options.flash_id_prefix = "group"
	options.id = "id"
	options.bgcolor = osvc.colors.org
	options.icon = "guys16"
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/safe/%1/publications", [options.uuid], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0"
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/groups", "", {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": ["privilege F", options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("/safe/%1/publications/%2", [options.uuid, tag_data.id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("/safe/%1/publications/%2", [options.uuid, tag.attr("tag_id")], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		services_osvcgetrest("/safe/%1/am_i_responsible", [options.uuid], "", callback)
	}
	options.ondblclick = function(divid, data) {
		group_tabs(divid, {"group_id": data.id, "group_name": data.name})
	}
	options.events = ["auth_group_change", "safe_team_publication_change"]
	return tags(options)
}

function user_org_membership(options) {
	options.tag_name = "role"
	options.flash_id_prefix = "group"
	options.id = "id"
	options.bgcolor = osvc.colors.org
	options.icon = "guys16"
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/users/%1/groups", [options.user_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"filters": ["privilege F"],
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/groups", "", {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": ["privilege F", options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("/users/%1/groups/%2", [options.user_id, tag_data.id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("/users/%1/groups/%2", [options.user_id, tag.attr("tag_id")], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		if (!services_ismemberof("Manager", "UserManager") && ! (services_ismemberof("SelfManager") && (options.user_id==_self.id))) {
			callback({"data": false})
			return
		}
		callback({"data": true})
	}
	options.ondblclick = function(divid, data) {
		group_tabs(divid, {"group_id": data.id, "group_name": data.name})
	}
	options.events = ["auth_group_change", "auth_membership_change"]
	return tags(options)
}

function user_priv_membership(options) {
	options.tag_name = "role"
	options.flash_id_prefix = "group"
	options.id = "id"
	options.bgcolor = osvc.colors.priv
	options.icon = "privilege16"
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/users/%1/groups", [options.user_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"filters": ["privilege T"],
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/groups", "", {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": ["privilege T", options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("/users/%1/groups/%2", [options.user_id, tag_data.id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("/users/%1/groups/%2", [options.user_id, tag.attr("tag_id")], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		if (!services_ismemberof("Manager", "UserManager") && ! (services_ismemberof("SelfManager") && (options.user_id==_self.id))) {
			callback({"data": false})
			return
		}
		callback({"data": true})
	}
	options.ondblclick = function(divid, data) {
		console.log(divid,data)
		group_tabs(divid, {"group_id": data.id, "group_name": data.name})
	}
	options.events = ["auth_group_change", "auth_membership_change"]
	return tags(options)
}

function node_modulesets(options) {
	options.tag_name = "modset_name"
	options.flash_id_prefix = "modset"
	options.id = "id"
	options.bgcolor = osvc.colors.comp
	options.icon = osvc.icons.modset
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/nodes/%1/compliance/modulesets", [options.node_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/nodes/%1/compliance/candidate_modulesets", [options.node_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": [options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("/nodes/%1/compliance/modulesets/%2", [options.node_id, tag_data.id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("/nodes/%1/compliance/modulesets/%2", [options.node_id, tag.attr("tag_id")], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		if (!services_ismemberof("Manager", "CompExec")) {
			callback({"data": false})
			return
		}
		services_osvcgetrest("/nodes/%1/am_i_responsible", [options.node_id], "", callback)
	}
	options.ondblclick = function(divid, data) {
		moduleset_tabs(divid, {"modset_id": data.id, "modset_name": data.name})
	}
	options.events = ["comp_node_moduleset_change", "comp_moduleset_change"]
	return tags(options)
}

function node_rulesets(options) {
	options.tag_name = "ruleset_name"
	options.flash_id_prefix = "rset"
	options.id = "id"
	options.bgcolor = osvc.colors.comp
	options.icon = osvc.icons.rset
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/nodes/%1/compliance/rulesets", [options.node_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/nodes/%1/compliance/candidate_rulesets", [options.node_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": [options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("/nodes/%1/compliance/rulesets/%2", [options.node_id, tag_data.id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("/nodes/%1/compliance/rulesets/%2", [options.node_id, tag.attr("tag_id")], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		if (!services_ismemberof("Manager", "CompExec")) {
			callback({"data": false})
			return
		}
		services_osvcgetrest("/nodes/%1/am_i_responsible", [options.node_id], "", callback)
	}
	options.ondblclick = function(divid, data) {
		ruleset_tabs(divid, {"ruleset_id": data.id, "ruleset_name": data.name})
	}
	options.events = ["comp_rulesets_nodes_change", "comp_rulesets_change"]
	return tags(options)
}

function service_modulesets(options) {
	options.tag_name = "modset_name"
	options.flash_id_prefix = "modset"
	options.id = "id"
	options.bgcolor = osvc.colors.comp
	options.icon = osvc.icons.modset
        if (typeof(options.slave) === "undefined") {
		options.slave = false
	}
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/services/%1/compliance/modulesets", [options.svc_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"slave": options.slave
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/services/%1/compliance/candidate_modulesets", [options.svc_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"slave": options.slave,
			"filters": [options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("/services/%1/compliance/modulesets/%2", [options.svc_id, tag_data.id], "", {"slave": options.slave}, callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("/services/%1/compliance/modulesets/%2", [options.svc_id, tag.attr("tag_id")], "", {"slave": options.slave}, callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		if (!services_ismemberof("Manager", "CompExec")) {
			callback({"data": false})
			return
		}
		services_osvcgetrest("/services/%1/am_i_responsible", [options.svc_id], "", callback)
	}
	options.ondblclick = function(divid, data) {
		moduleset_tabs(divid, {"modset_id": data.id, "modset_name": data.name})
	}
	options.events = ["comp_modulesets_services_change", "comp_moduleset_change"]
	return tags(options)
}

function service_rulesets(options) {
	options.tag_name = "ruleset_name"
	options.flash_id_prefix = "rset"
	options.id = "id"
	options.bgcolor = osvc.colors.comp
	options.icon = osvc.icons.rset
        if (typeof(options.slave) === "undefined") {
		options.slave = false
	}
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/services/%1/compliance/rulesets", [options.svc_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"slave": options.slave
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/services/%1/compliance/candidate_rulesets", [options.svc_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"slave": options.slave,
			"filters": [options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("/services/%1/compliance/rulesets/%2", [options.svc_id, tag_data.id], "", {"slave": options.slave}, callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("/services/%1/compliance/rulesets/%2", [options.svc_id, tag.attr("tag_id")], "", {"slave": options.slave}, callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		if (!services_ismemberof("Manager", "CompExec")) {
			callback({"data": false})
			return
		}
		services_osvcgetrest("/services/%1/am_i_responsible", [options.svc_id], "", callback)
	}
	options.ondblclick = function(divid, data) {
		ruleset_tabs(divid, {"ruleset_id": data.id, "ruleset_name": data.name})
	}
	options.events = ["comp_rulesets_services_change", "comp_rulesets_change"]
	return tags(options)
}

function ruleset_nodes(options) {
	options.tag_name = "nodename"
	options.flash_id_prefix = "node"
	options.id = "node_id"
	options.bgcolor = osvc.colors.node
	options.icon = osvc.icons.node
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/compliance/rulesets/%1/nodes", [options.ruleset_id], {
			"orderby": options.tag_name,
			"props": "node_id," + options.tag_name,
			"limit": "0",
			"meta": "false"
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/compliance/rulesets/%1/candidate_nodes", [options.ruleset_id], {
			"orderby": options.tag_name,
			"props": "node_id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": [options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("/nodes/%1/compliance/rulesets/%2", [tag_data.node_id, options.ruleset_id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("/nodes/%1/compliance/rulesets/%2", [tag.attr("tag_id"), options.ruleset_id], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		if (!services_ismemberof("Manager", "CompExec")) {
			callback({"data": false})
			return
		}
		callback({"data": true})
	}
	options.ondblclick = function(divid, data) {
		node_tabs(divid, {"node_id": data.id, "nodename": data.name})
	}
	options.events = ["comp_rulesets_nodes_change", "comp_rulesets_change"]
	return tags(options)
}

function ruleset_services(options) {
	options.tag_name = "svcname"
	options.flash_id_prefix = "svc"
	options.id = "svc_id"
	options.bgcolor = osvc.colors.svc
	options.icon = osvc.icons.svc
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/compliance/rulesets/%1/services", [options.ruleset_id], {
			"orderby": options.tag_name,
			"props": "svc_id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"slave": options.slave
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/compliance/rulesets/%1/candidate_services", [options.ruleset_id], {
			"orderby": options.tag_name,
			"props": "svc_id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"slave": options.slave,
			"filters": [options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("/services/%1/compliance/rulesets/%2", [tag_data.svc_id, options.ruleset_id], "", {"slave": options.slave}, callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("/services/%1/compliance/rulesets/%2", [tag.attr("tag_id"), options.ruleset_id], "", {"slave": options.slave}, callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		if (!services_ismemberof("Manager", "CompExec")) {
			callback({"data": false})
			return
		}
		callback({"data": true})
	}
	options.ondblclick = function(divid, data) {
		service_tabs(divid, {"svc_id": data.id, "svcname": data.name})
	}
	options.events = ["comp_rulesets_services_change", "comp_rulesets_change"]
	return tags(options)
}

function moduleset_nodes(options) {
	options.tag_name = "nodename"
	options.flash_id_prefix = "node"
	options.id = "node_id"
	options.bgcolor = osvc.colors.node
	options.icon = osvc.icons.node
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/compliance/modulesets/%1/nodes", [options.modset_id], {
			"orderby": options.tag_name,
			"props": "node_id," + options.tag_name,
			"limit": "0",
			"meta": "false"
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/compliance/modulesets/%1/candidate_nodes", [options.modset_id], {
			"orderby": options.tag_name,
			"props": "node_id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": [options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("/nodes/%1/compliance/modulesets/%2", [tag_data.node_id, options.modset_id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("/nodes/%1/compliance/modulesets/%2", [tag.attr("tag_id"), options.modset_id], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		if (!services_ismemberof("Manager", "CompExec")) {
			callback({"data": false})
			return
		}
		callback({"data": true})
	}
	options.ondblclick = function(divid, data) {
		node_tabs(divid, {"node_id": data.id, "nodename": data.name})
	}
	options.events = ["comp_node_moduleset_change", "comp_moduleset_change"]
	return tags(options)
}

function moduleset_services(options) {
	options.tag_name = "svcname"
	options.flash_id_prefix = "svc"
	options.id = "svc_id"
	options.bgcolor = osvc.colors.svc
	options.icon = osvc.icons.svc
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/compliance/modulesets/%1/services", [options.modset_id], {
			"orderby": options.tag_name,
			"props": "svc_id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"slave": options.slave
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/compliance/modulesets/%1/candidate_services", [options.modset_id], {
			"orderby": options.tag_name,
			"props": "svc_id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"slave": options.slave,
			"filters": [options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("/services/%1/compliance/modulesets/%2", [tag_data.svc_id, options.modset_id], "", {"slave": options.slave}, callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("/services/%1/compliance/modulesets/%2", [tag.attr("tag_id"), options.modset_id], "", {"slave": options.slave}, callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		if (!services_ismemberof("Manager", "CompExec")) {
			callback({"data": false})
			return
		}
		callback({"data": true})
	}
	options.ondblclick = function(divid, data) {
		service_tabs(divid, {"svc_id": data.id, "svcname": data.name})
	}
	options.events = ["comp_modulesets_services_change", "comp_modulesets_change"]
	return tags(options)
}

function docker_registry_responsibles(options) {
	options.tag_name = "role"
	options.flash_id_prefix = "group"
	options.id = "id"
	options.bgcolor = osvc.colors.org
	options.icon = "guys16"
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/docker/registries/%1/responsibles", [options.registry_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0"
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/groups", "", {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": ["privilege F", options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("/docker/registries/%1/responsibles/%2", [options.registry_id, tag_data.id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("/docker/registries/%1/responsibles/%2", [options.registry_id, tag.attr("tag_id")], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		services_osvcgetrest("/docker/registries/%1/am_i_responsible", [options.registry_id], "", callback)
	}
	options.ondblclick = function(divid, data) {
		group_tabs(divid, {"group_id": data.id, "group_name": data.name})
	}
	options.events = ["auth_group_change", "docker_registries_responsibles_change"]
	return tags(options)
}

function docker_registry_publications(options) {
	options.tag_name = "role"
	options.flash_id_prefix = "group"
	options.id = "id"
	options.bgcolor = osvc.colors.org
	options.icon = "guys16"
	options.get_tags = function(fval, callback, callback_err) {
		services_osvcgetrest("/docker/registries/%1/publications", [options.registry_id], {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0"
		}, callback, callback_err)
	}
	options.get_candidates = function(fval, callback, callback_err) {
		services_osvcgetrest("/groups", "", {
			"orderby": options.tag_name,
			"props": "id," + options.tag_name,
			"limit": "0",
			"meta": "false",
			"filters": ["privilege F", options.tag_name+" "+fval]
		}, callback, callback_err)
	}
	options.attach = function(tag_data, callback, callback_err) {
		services_osvcpostrest("/docker/registries/%1/publications/%2", [options.registry_id, tag_data.id], "", "", callback, callback_err)
	}
	options.detach = function(tag, callback, callback_err) {
		services_osvcdeleterest("/docker/registries/%1/publications/%2", [options.registry_id, tag.attr("tag_id")], "", "", callback, callback_err)
	}
	options.am_i_responsible = function(callback) {
		services_osvcgetrest("/docker/registries/%1/am_i_responsible", [options.registry_id], "", callback)
	}
	options.ondblclick = function(divid, data) {
		group_tabs(divid, {"group_id": data.id, "group_name": data.name})
	}
	options.events = ["auth_group_change", "docker_registries_publications_change"]
	return tags(options)
}


