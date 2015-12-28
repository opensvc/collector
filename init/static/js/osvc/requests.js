function requests(divid, options) {
	o = {}
	o.options = options
	o.div = $("#"+divid)
	o.current_folder = []

	o.div.load("/init/static/views/requests.html", function() {
		o.div.i18n()
		o.e_search = o.div.find("#form_search")
		o.e_list = o.div.find("#forms_list")
		o.e_target = o.div.find("#forms_target")
		o.e_inputs = o.div.find("#forms_inputs")

		$.when(osvc.forms_loaded).then(function(){
			o.init_search()
			o.init_list()
		})
	})

	o.init_search = function() {
		function match(re, d) {
			if (!d.form_folder) {
				return false
			}
			if (form_name.match(re)) {
				return true
			}
			if (!d.form_definition) {
				return false
			}
			if (d.form_definition.Label && d.form_definition.Label.match(re)) {
				return true
			}
			if (d.form_definition.Desc && d.form_definition.Desc.match(re)) {
				return true
			}
			return false

		}
		o.e_search.bind("keyup", function() {
			o.e_list.empty()
			var s = $(this).val()
			if (s == "") {
				o.init_list()
				return
			}
			var re = RegExp(s, "i")
			for (form_name in osvc.forms.data) {
				var d = osvc.forms.data[form_name]
				if (match(re, d)) {
					o.e_list.append(o.render_form(d))
				}
			}
		})
	}

	o.init_list = function() {
		o.e_list.empty()
		o.render_folders()
		o.render_forms()
	}

	o.render_folder = function(d) {
		var div = $("<div class='formentry'></div>")
		var div_icon = $("<div style='padding-top:1em;padding-bottom:1em'></div>")
		var p1 = $("<p></p>")
		var p2 = $("<p style='font-style:italic;padding-left:1em'></p>")

		div.attr("folder_name", d.form_definition.FolderName)
		if (d.form_definition.FolderCss) {
			div_icon.addClass(d.form_definition.FolderCss)
		} else {
			div_icon.addClass("folder48")
		}
		p1.text(d.form_definition.FolderLabel)
		p2.text(d.form_definition.FolderDesc)

		div_icon.append(p1)
		div_icon.append(p2)
		div.append(div_icon)

		div.bind("click", function() {
			var folder_name = div.attr("folder_name")
			if (folder_name == "prev") {
				o.current_folder.pop()
			} else if (folder_name == "current") {
				o.e_inputs.hide()
			} else {
				o.current_folder.push(folder_name)
			}
			o.init_list()
		})
		return div
	}

	o.render_form = function(d) {
		var div = $("<div class='formentry'></div>")
		var div_icon = $("<div style='padding-top:1em;padding-bottom:1em'></div>")
		var p1 = $("<p></p>")
		var p2 = $("<p style='font-style:italic;padding-left:1em'></p>")

		div.attr("form_name", d.form_name)
		if (d.form_definition.Css) {
			div_icon.addClass(d.form_definition.Css)
		} else {
			div_icon.addClass("wf48")
		}
		if (d.form_definition.Label) {
			p1.text(d.form_definition.Label)
		} else {
			p1.text(d.form_name)
		}
		p2.text(d.form_definition.Desc)

		div_icon.append(p1)
		div_icon.append(p2)
		div.append(div_icon)

		div.bind("click", function() {
			$(this).siblings().hide()
			var d = {
				"FolderName": "current",
				"FolderLabel": i18n.t("requests.current_folder"),
				"FolderDesc": get_current_folder(),
			}
			o.render_folder({"form_definition": d}).insertBefore($(this))
			o.e_inputs.empty().show()
			form("forms_inputs", {
				"form_name": div.attr("form_name")
			})
		})

		return div
	}

	function get_parent_folder() {
		var folder = "/" + o.current_folder.slice(0, o.current_folder.length-1).join("/")
		return folder
	}

	function get_current_folder() {
		var folder = "/" + o.current_folder.join("/")
		return folder
	}

	o.render_folders = function() {
		var folder = get_current_folder()
		console.log("render_folders", folder)

		if (folder != "/") {
			var d = {
				"FolderName": "prev",
				"FolderLabel": i18n.t("requests.parent_folder"),
				"FolderDesc": get_parent_folder(),
			}
			o.e_list.append(o.render_folder({"form_definition": d}))
		}

		var l = osvc.forms.folders[folder]
		if (!l) {
			return
		}
		l.sort()
		for (var i=0; i<l.length; i++) {
			var form_name = l[i]
			var d = osvc.forms.data[form_name]
			if (d.form_type == "folder") {
				o.e_list.append(o.render_folder(d))
			}
		}
	}

	o.render_forms = function() {
		var folder = get_current_folder()
		console.log("render_forms", folder)
		var l = osvc.forms.folders[folder]
		if (!l) {
			return
		}
		l.sort()
		for (var i=0; i<l.length; i++) {
			var form_name = l[i]
			var d = osvc.forms.data[form_name]
			if (d.form_type != "folder") {
				o.e_list.append(o.render_form(d))
			}
		}
	}

	return o
}

function workflow(divid, options) {
	o = {}
	o.divid = divid
	o.options = options
	o.div = $("#"+divid)

	o.div.load("/init/static/views/workflow.html", function() {
		o.div.i18n()
		o.e_form = $("[name=form]")
		o.e_form_next = $("[name=form_next]")
		o.e_form_prev = $("[name=form_prev]")
		o.e_next = $("[name=next_steps]")
		o.e_next_form = $("[name=next_form]")
		$.when(osvc.forms_loaded).then(function() {
			o.init()
		})
	})

	o.init = function() {
		services_osvcgetrest("R_STORE_FORM", [o.options.form_id], {"meta": 0}, function(jd) {
			o.stored_form = jd.data[0]
			services_osvcgetrest("R_FORMS_REVISIONS", "", {"meta": 0, "filters": ["form_md5 "+o.stored_form.form_md5]}, function(jd) {
				o.form_data = jd.data[0]
				o.render()
			})
		})

	}

	o.render = function() {
		o.render_form()
		o.render_form_prev()
		o.render_form_next()
		o.render_next()
	}

	o.render_form_list_entry = function(form_name) {
		if (!(form_name in osvc.forms.data)) {
			console.log(form_name, "not found in osvc.forms")
			return
		}
		var d = osvc.forms.data[form_name]
		console.log(form_name, d)

		var div = $("<div class='clickable' style='padding-bottom:0.5em'></div>")
		if (d.form_definition.Css) {
			div.addClass(d.form_definition.Css)
		} else {
			div.addClass("wf48")
		}
		var h = $("<h2 style='text-align:left'></h2>")
		if (o.form_data.form_definition.Label) {
			var title = d.form_definition.Label
		} else {
			var title = form_name
		}
		h.text(title)
		div.append(h)
		if (d.form_definition.Desc) {
			var i = $("<div style='text-align:left;font-style:italic'></div>")
			i.text(d.form_definition.Desc)
			div.append(i)
		}

		div.bind("click", function() {
			$(this).siblings().hide()
			var div_form = $("<div></div>")
			div_form.uniqueId()
			o.e_next_form.html(div_form)
			form(div_form.attr("id"), {
				"prev_wfid": o.options.form_id,
				"form_name": form_name,
				"display_mode": false
			})
		})
		return div
	}

	o.render_form_title = function(stored_form, form_data) {
		var div = $("<div class='clickable' style='padding-bottom:0.5em'></div>")
		div.addClass(form_data.form_definition.Css)
		var h = $("<h2 style='text-align:left'></h2>")
		if (form_data.form_definition.Label) {
			var title = form_data.form_definition.Label
		} else {
			var title = form_data.form_name
		}
		h.text(stored_form.id+": "+title)
		div.append(h)
		var i = $("<div style='text-align:left;font-style:italic'></div>")
		var s = i18n.t("requests.stored_form_subtitle1", {
			"requestor": stored_form.form_submitter,
			 "request_date": stored_form.form_submit_date
		})
		s += "<br>"
		s += i18n.t("requests.stored_form_subtitle2", {
			"team": stored_form.form_assignee
		})
		i.html(s)
		div.append(i)
		return div
	}

	o.render_form_prev = function() {
		if (!o.stored_form.form_prev_id) {
			return
		}
		services_osvcgetrest("R_STORE_FORM", [o.stored_form.form_prev_id], {"meta": 0}, function(jd) {
			var stored_form = jd.data[0]
			services_osvcgetrest("R_FORMS_REVISIONS", "", {"meta": 0, "filters": ["form_md5 "+stored_form.form_md5]}, function(jd) {
				var form_data = jd.data[0]
				var div = $("<div class='forms grayed'></div>")
				var arrow = $("<div class='icon fa-angle-double-down'></div>")
				o.e_form_prev.show()
				o.e_form_prev.append(div)
				o.e_form_prev.append(arrow)
				div.append(o.render_form_title(stored_form, form_data))
				div.bind("click", function() {
					workflow(o.divid, {
						"form_id": o.stored_form.form_prev_id
					})
				})
			})
		})
	}

	o.render_form_next = function() {
		if (!o.stored_form.form_next_id) {
			return
		}
		services_osvcgetrest("R_STORE_FORM", [o.stored_form.form_next_id], {"meta": 0}, function(jd) {
			var stored_form = jd.data[0]
			services_osvcgetrest("R_FORMS_REVISIONS", "", {"meta": 0, "filters": ["form_md5 "+stored_form.form_md5]}, function(jd) {
				var form_data = jd.data[0]
				var div = $("<div class='forms grayed'></div>")
				var arrow = $("<div class='icon fa-angle-double-down'></div>")
				o.e_form_next.show()
				o.e_form_next.append(arrow)
				o.e_form_next.append(div)
				div.append(o.render_form_title(stored_form, form_data))
				div.bind("click", function() {
					workflow(o.divid, {
						"form_id": o.stored_form.form_next_id
					})
				})
			})
		})
	}

	o.render_form = function() {
		var div = $("<div class='forms'></div>")
		div.append(o.render_form_title(o.stored_form, o.form_data))
		var div_form = $("<div></div>")
		div_form.uniqueId()
		div.append(div_form)
		o.e_form.append(div)
		var options = {
			"form_data": o.form_data,
			"data": $.parseJSON(o.stored_form.form_data),
			"display_mode": true,
			"editable": false,
			"detailled": true
		}
		form(div_form.attr("id"), options)
	}

	o.get_workflow_output = function() {
		for (var i=0; i<o.form_data.form_definition.Outputs.length; i++) {
			var d = o.form_data.form_definition.Outputs[i]
			if (d.Dest && (d.Dest == "workflow")) {
				return d
			}
		}
	}

	o.render_next = function() {
		if (o.stored_form.form_next_id) {
			o.e_next.html(i18n.t("requests.already_completed"))
			return
		}
		var d = o.get_workflow_output()
		if (!d) {
			return
		}
		if (!d.NextForms || (d.NextForms.length == 0)) {
			o.e_next.html(i18n.t("requests.no_successor"))
			return
		}
		if ((_self.first_name + " " + _self.last_name != o.stored_form.form_assignee) &&
		    !services_ismemberof(o.stored_form.form_assignee)) {
			o.e_next.html(i18n.t("requests.not_assigned"))
			return
		}
		for (var i=0; i<d.NextForms.length; i++) {
			var e = d.NextForms[i]
			o.e_next.append(o.render_form_list_entry(e))
		}
	}
}
