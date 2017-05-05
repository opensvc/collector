function requests(divid, options) {
	var o = {}
	o.options = options
	o.div = $("#"+divid)

	if (!o.options) {
		o.options = {}
	}

	if (o.options.form_folder) {
		o.current_folder = o.options.form_folder.replace(/^\//, "").split("/")
	} else {
		o.current_folder = []
	}

	o.div.load("/init/static/views/requests.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.e_search = o.div.find("#form_search")
		o.e_list = o.div.find("#forms_list")
		o.e_target = o.div.find("#forms_target")
		o.e_inputs = o.div.find("#forms_inputs")

		if (o.options.locked == true) {
			o.e_search.parent().hide()
			o.div.find("h1").first().hide()
		}

		require(["osvc/forms"], function(){
			$.when(osvc.forms_loaded).then(function(){
				o.init_search()
				o.init_list()
			})
		})
	})

	o.search = function() {
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
		o.e_list.empty()
		o.e_inputs.empty()
		var s = o.e_search.val()
		if (s == "") {
			delete(o.options.form_name)
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
	}

	o.init_search = function() {
		o.e_search.bind("keyup", function() {
			o.search()
		})
	}

	o.init_list = function() {
		o.e_list.empty()
		o.e_inputs.empty()
		o.e_target.empty()
		if (o.options && o.options.form_name) {
			var d = osvc.forms.data[o.options.form_name]
			o.e_list.append(o.render_form(d))
		} else {
			o.render_folders()
			o.render_forms()
		}
	}

	o.render_folder = function(d) {
		if (!d || !d.form_definition) {
			console.log("skip render_folder:", d)
			return
		}

		var div = $("<div class='formentry'></div>")
		var div_icon = $("<div></div>")
		var div_title = $("<div></div>")
		var link = $("<span class='icon link16'></span>")
		var p1 = $("<h6 class='b'></h6>")
		var p2 = $("<div style='font-style:italic;padding-left:1em'></div>")

		div.attr("folder_name", d.form_definition.FolderName)
		div.addClass("form_folder")
		if (d.form_definition.FolderCss) {
			div_icon.addClass(d.form_definition.FolderCss)
		} else {
			div_icon.addClass("fa-folder-open")
		}
		p1.text(d.form_definition.FolderLabel)
		p2.text(d.form_definition.FolderDesc)

		link.bind("click", function(event){
			event.stopPropagation()
			osvc_create_link("requests", {"form_folder": d.form_name}, "link.request_folder")
		})

		p1.prepend(link)
		div_title.append(p1)
		div_title.append(p2)
		div.append([div_icon, div_title])

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
		var div_icon = $("<div></div>")
		var div_title = $("<div></div>")
		var link = $("<span class='icon link16'></span>")
		var p1 = $("<h6 class='b'></h6>")
		var p2 = $("<div style='font-style:italic;padding-left:1em'></div>")

		div.attr("form_name", d.form_name)
		if (!d.form_definition) {
			return div
		}
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

		link.bind("click", function(event){
			event.stopPropagation()
			osvc_create_link("form", {"form_name": d.form_name}, "link.request")
		})

		p1.prepend(link)
		div_title.append(p1)
		div_title.append(p2)
		div.append([div_icon, div_title])

		div.bind("click", function() {
			$(this).siblings().hide()
			var d = {
				"FolderName": "current",
				"FolderLabel": i18n.t("requests.current_folder"),
				"FolderDesc": get_current_folder(),
			}
			if (o.options.locked != true) {
				o.render_folder({"form_definition": d}).insertBefore($(this))
			}
			o.e_inputs.empty().show()
			form(o.e_inputs, {
				"form_name": div.attr("form_name")
			})
		})

		if (o.options.locked == true) {
			div.click()
		}

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
	var o = {}
	o.divid = divid
	o.options = options
	o.div = $("#"+divid)
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "format_title",
		"title_args": {
			"type": "form",
			"id": o.options.workflow_id
		}
	}

	o.div.load("/init/static/views/workflow.html?v="+osvc.code_rev, function() {
		o.div.i18n()
		o.e_form = o.div.find("[name=form]")
		o.e_form_next = o.div.find("[name=form_next]")
		o.e_form_prev = o.div.find("[name=form_prev]")
		o.e_next = o.div.find("[name=next_steps]")
		o.e_next_form = o.div.find("[name=next_form]")

		require(["osvc/forms"], function(){
			$.when(osvc.forms_loaded).then(function() {
				o.init()
			})
		})
	})

	o.init = function() {
		services_osvcgetrest("R_STORE_FORM", [o.options.form_id], {"meta": 0}, function(jd) {
			o.stored_form = jd.data[0]
			services_osvcgetrest("R_STORE_FORMS", "", {"meta": 0, "filters": ["form_head_id "+o.stored_form.form_head_id]}, function(_jd) {
				o.workflow_stored_forms = _jd.data
				o.link.title_args.name = o.options.workflow_id+"/"+o.workflow_stored_forms[0].form_name
				o.render()
			})
		})

	}

	o.render_next = function(stored_form) {
		o.e_next.empty()
		if (stored_form.form_next_id) {
			o.e_next.html(i18n.t("requests.already_completed"))
			return
		}
		var d = o.get_workflow_output(stored_form)
		if (!d) {
			return
		}
		if (!d.NextForms || (d.NextForms.length == 0)) {
			o.e_next.html(i18n.t("requests.no_successor"))
			return
		}
		if ((_self.first_name + " " + _self.last_name != stored_form.form_assignee) &&
		    !services_ismemberof(stored_form.form_assignee)) {
			o.e_next.html(i18n.t("requests.not_assigned"))
			return
		}
		for (var i=0; i<d.NextForms.length; i++) {
			var e = d.NextForms[i]
			o.e_next.append(o.render_form_list_entry(e))
		}
	}

	o.render = function() {
		osvc_tools(o.div, {
			"link": o.link
		})
		var n = o.workflow_stored_forms.length
		for (var i=0; i<n; i++) {
			if (i>0) {
				var arrow = $("<div class='icon fa-angle-double-down' style='text-align:center'></div>")
				o.e_form.append(arrow)
			}
			o.render_form(o.workflow_stored_forms[i])
		}
		o.render_next(o.stored_form)
	}

	o.render_form_list_entry = function(form_name) {
		if (!(form_name in osvc.forms.data)) {
			console.log(form_name, "not found in osvc.forms")
			return
		}
		var d = osvc.forms.data[form_name]
		console.log(form_name, d)

		var div = $("<div class='clickable pb-2'></div>")
		if (d.form_definition.Css) {
			div.addClass(d.form_definition.Css)
		} else {
			div.addClass("wf48")
		}
		var h = $("<h2></h2>")
		if (d.form_definition.Label) {
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

	o.render_form_title = function(stored_form) {
		var div = $("<div class='clickable pt-3 pb-3'></div>")
		div.addClass(stored_form.form_definition.Css)
		var h = $("<h3></h3>")
		if (stored_form.form_definition.Label) {
			var title = stored_form.form_definition.Label
		} else {
			var title = stored_form.form_name
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

	o.render_form_results = function(stored_form) {
		if (!stored_form.results_id) {
			return
		}
		var div = $("<div class='postit p-3' style='margin-top:0.5em'></div>")
		form_results(div, {
			"results_id": stored_form.results_id,
			"async": false
		})
		o.e_form.append(div)
	}

	o.render_form = function(stored_form) {
		var div = $("<div name='step'></div>")
		var div_form = $("<div></div>")
		div.append(o.render_form_title(stored_form))
		div_form.uniqueId()
		div.append(div_form)
		o.e_form.append(div)
		var options = {
			"form_data": stored_form,
			"data": $.parseJSON(stored_form.form_data),
			"display_mode": true,
			"editable": false,
			"detailled": true
		}

		if (stored_form.id != o.stored_form.id) {
			div.addClass("grayed")
			div_form.hide()
		}

		div.bind("click", function(event) {
			if (!$(this).hasClass("grayed")) {
				return
			}
			o.e_form.children("[name=step]").addClass("grayed")
			o.e_form.find(".postit").parent().hide(500)
			$(this).removeClass("grayed")
			div_form.show()
			o.render_next(stored_form)
		})

		form(div_form.attr("id"), options)

		//div_form.append(o.render_form_results(stored_form))
		o.render_form_results(stored_form)
	}

	o.get_workflow_output = function(stored_form) {
		for (var i=0; i<stored_form.form_definition.Outputs.length; i++) {
			var d = stored_form.form_definition.Outputs[i]
			if (d.Dest && (d.Dest == "workflow")) {
				return d
			}
		}
	}


	return o
}
