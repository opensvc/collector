function tags(options) {
	var o = {}
	o.div = $("#"+options.tid)
	o.options = options

	o.load = function() {
		// init error display zone
		if (!o.div.info) {
			info = $("<div></div>")
			o.div.append(info)
			o.div.info = info
		}
		o.div.info.empty()
		spinner_add(o.div.info)
		options = {
			"meta": "false",
			"limit": "0",
			"props": "id,tag_name"
		}
		if ("prefix" in o.options) {
			options["query"] = "tag_name starts with " + o.options.prefix
		}
		services_osvcgetrest(o.url, o.url_params, options, function(_data) {
			spinner_del(o.div.info)
			if (_data.error) {
				o.div.info.html(services_error_fmt(_data))
				return
			}
			_data = _data.data
			if ((_data.length == 0) && o.options.candidates) {
				o.div.info.text(i18n.t("tags.no_candidates"))
			}
			d = $("<div name='tag_container'></div>")
			for (i=0; i<_data.length; i++) {
				d.append(o.add_tag(_data[i]), " ")
			}
			if (o.options.responsible && o.options.candidates != true) {
				d.append(o.add_add_tag())
				d.append(o.add_del_tag())
			}
			o.div.find("[name=tag_container]").remove()
			o.div.prepend(d)

			o.bind_admin_tools()
		},
		function(xhr, stat, error) {
			o.div.info.html(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.add_tag = function(tag_data) {
		if (o.options.candidates == true) {
			cl = "icon tag tag_candidate"
		} else {
			cl = "icon tag tag_attached"
		}
		s = "<span tag_id='"+tag_data.id+"' class='"+cl+"'>"+tag_data.tag_name+" </span>"
		e = $(s)
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
		e.draggable({
			"containment": o.div,
			"opacity": 0.9,
			"revert": true,
			"stack": ".tag",
		})
		return e
	}

	o.del_tag = function(tag_data) {
		o.div.find("[tag_id="+tag_data.tag_id+"].tag").hide("fade", function(){
			$(this).remove()
		})
	}

	o.add_add_tag = function() {
		if (o.options.candidates) {
			return
		}
		e = $("<span class='icon tag_add'></span>")
		e.css({"display": "none"})
		e.text(i18n.t("tags.add"))
		e.bind("click", function(){
			old_html = $(this).html()
			e = $(this).find(".tag_input")
			if (e.length>0) {
				return
			}
			s = "<input class='tag_input'></input>"
			$(this).html(s)
			e = $(this).find(".tag_input")
			e.bind("keyup", function(event){
				tag = $(this).parent()
				tag_name = $(this).val()
				o.input_keyup(event, tag, tag_name)
			})
			e.focus()
		})
		return e
	}

	o.add_del_tag = function() {
		if (o.options.candidates) {
			return
		}
		e = $("<span class='icon tag_del'></span>")
		e.css({"display": "none"})
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

	o.add_candidates = function(tag, tag_name) {
		prefix = o.div.find(".tag_input").val()
		if (prefix.length == 0) {
			prefix = "%"
		}
		prefix = prefix.replace(/\//, "_")
		prefix = encodeURIComponent(prefix)

		// 1st candidates exec: init a new tag object
		ctid = o.options.tid+"c"
		options = {
			"tid": ctid,
			"responsible": o.options.responsible,
			"parent_object": o,
			"prefix": prefix,
			"candidates": true
		}
		if ("node_id" in o.options) {
			options.node_id = o.options.node_id
		} else if ("svc_id" in o.options) {
			options.svc_id = o.options.svc_id
		}
		o.div.find("#"+ctid).parent().remove()
		e = $("<span><h3>"+i18n.t("tags.candidates")+"</h3><div id='"+ctid+"' class='tags'></div></span>")
		o.div.append(e)
		o.candidates = tags(options)
	}

	o._attach_tag = function(tag_data) {
		if ("node_id" in o.options) {
			url = "R_TAG_NODE"
			url_params = [tag_data.id, o.options.node_id]
		} else if ("svc_id" in o.options) {
			url = "R_TAG_SERVICE"
			url_params = [tag_data.id, o.options.svc_id]
		} else {
			return
		}
		o.div.info.empty()
		spinner_add(o.div.info, i18n.t("tags.attaching"))
		services_osvcpostrest(url, url_params, "", "", function(jd) {
			spinner_del(o.div.info)
			if (jd.error) {
				o.div.info.html(services_error_fmt(jd))
				return
			}
			// refresh tags
			if (o.options.parent_object) {
				o.div.parent().remove()
				o.options.parent_object.load()
			} else {
				o.load()
			}
		},
		function(xhr, stat, error) {
			o.div.info.html(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.attach_tag = function(tag_data) {
		if (!tag_data.id) {
			// from <enter> in add tag
			o.div.info.empty()
			o.candidates.div.parent().remove()
			services_osvcgetrest("R_TAGS", "", {"meta": "false", "query": "tag_name="+tag_data.tag_name}, function(jd) {
				if (!jd.data || (jd.data.length == 0)) {
					// tag does not exist yet ... create
					spinner_add(o.div.info, i18n.t("tags.creating"))
					services_osvcpostrest("R_TAGS", "", "", tag_data, function(jd) {
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
				} else {
					// tag elready exists
					o._attach_tag(jd.data[0])
				}
			},
			function(xhr, stat, error) {
				o.div.info.html(services_ajax_error_fmt(xhr, stat, error))
			})
		} else {
			// from click on a candidate
			o._attach_tag(tag_data)
		}
	}

	o.detach_tag = function(tag) {
		o.div.info.empty()
		tag.hide()
		spinner_add(o.div.info, i18n.t("tags.detaching"))
		if ("node_id" in o.options) {
			url = "R_TAG_NODE"
			url_params = [tag.attr("tag_id"), o.options.node_id]
		} else if ("svc_id" in o.options) {
			url = "R_TAG_SERVICE"
			url_params = [tag.attr("tag_id"), o.options.svc_id]
		} else {
			return
		}
		services_osvcdeleterest(url, url_params, "", "", function(jd) {
			spinner_del(o.div.info)
			if (jd.error) {
				o.div.info.html(services_error_fmt(jd))
				return
			}
			// refresh tags
			o.load()
		},
		function(xhr, stat, error) {
			tag.show()
			o.div.info.html(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.bind_admin_tools = function() {
		// show tag admin tools to responsibles and managers
		if (o.options.responsible) {
			o._bind_admin_tools()
			return
		}
		if (services_ismemberof("Manager")) {
			o._bind_admin_tools()
		}
	}
	o._bind_admin_tools = function() {
		o.div.hover(
			function(){
				o.div.find(".tag_add,.tag_del").fadeIn()
			},
			function(){
				o.div.find(".tag_add,.tag_del").fadeOut()
			}
		)
	}

	o.event_handler = function(data) {
		if (o.options.candidates == true) {
			return
		}
		if (!("data" in data)) {
			return
		} 
		data = data.data
		if (o.options.node_id) {
			if (!data.node_id || (o.options.node_id != data.node_id)) {
				return
			}
		} else if (o.options.svc_id) {
			if (!data.svc_id || (o.options.svc_id != data.svc_id)) {
				return
			}
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
				"tag_name": data.tag_name
			}))
		} else if (data.action == "detach") {
			o.del_tag({
				"tag_id": data.tag_id,
			})
		}
	}

	o.input_keyup = function(event, tag, tag_name) {
		if (!is_enter(event)) {
			tag.removeClass("tag_create")
			tag.find("input").removeClass("tag_create")
			o.add_candidates(tag, tag_name)
			return
		}
		o.attach_tag({"tag_name": tag_name})
	}


	if (("candidates" in options) && ("node_id" in options)) {
		o.url = "R_NODE_CANDIDATE_TAGS"
		o.url_params = [options.node_id]
	} else if (("candidates" in options) && ("svc_id" in options)) {
		o.url = "R_SERVICE_CANDIDATE_TAGS"
		o.url_params = [options.svc_id]
	} else if ("node_id" in options) {
		o.url = "R_NODE_TAGS"
		o.url_params = [options.node_id]
	} else if ("svc_id" in options) {
		o.url = "R_SERVICE_TAGS"
		o.url_params = [options.svc_id]
	} else {
		return
	}

	wsh["tags_"+o.options.tid] = function(data) {
		o.event_handler(data)
	}

	if (o.options.node_id) {
		services_osvcgetrest("R_NODE_AM_I_RESPONSIBLE", [o.options.node_id], "", function(jd) {
			o.options.responsible = jd.data
			o.load()
		})
	} else if (o.options.svc_id) {
		services_osvcgetrest("R_SERVICE_AM_I_RESPONSIBLE", [o.options.svc_id], "", function(jd) {
			o.options.responsible = jd.data
			o.load()
		})
	}
	return o
}


