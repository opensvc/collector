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
