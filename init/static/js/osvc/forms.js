function convert_boolean(val) {
	try {
		if (String(val)[0].toLowerCase().match(/[1ty]/)) {
			return true
		} else {
			return false
		}
	} catch(e) {
		return false
	}
}

function forms() {
	var o = {}

	o.load = function() {
		o.data = {}
		o.folders = {}
		var data = {
			"limit": "0",
			"meta": "0",
			"props": "form_definition,form_name,id,form_type,form_folder"
		}
		services_osvcgetrest("R_FORMS", "", data, function(jd) {
			jd.data = jd.data.concat(osvc.internal_forms)
			for (var i=0; i<jd.data.length; i++) {
				var d = jd.data[i]
				o.data[d.form_name] = d
				if (!(d.form_folder in o.folders)) {
					o.folders[d.form_folder] = []
				}
				o.folders[d.form_folder].push(d.form_name)
			}
			osvc.forms_loaded.resolve(true)
		})
	}

	o.change_form = function(id) {
		services_osvcgetrest("R_FORM", [id], "", function(jd) {
			var d = jd.data[0]
			o.delete_form(id)
			console.log("add form", d.form_name, "to the form cache")
			o.data[d.form_name] = d
			if (!(d.form_folder in o.folders)) {
				o.folders[d.form_folder] = []
			}
			o.folders[d.form_folder].push(d.form_name)
			console.log("add form", d.form_name, "to the form folder", d.form_folder, "cache")
		})
	}

	o.delete_form = function(id) {
		for (var form_name in o.data) {
			if (o.data[form_name].id == id) {
				var form_folder = o.data[form_name].form_folder
				console.log("delete form", form_name, "from cache")
				delete(o.data[form_name])

				// remove from the folder cache
				var idx = o.folders[form_folder].indexOf(form_name)
				if (idx >= 0) {
					console.log("delete form", form_name, "from folder", form_folder, "cache, found at index", idx)
					o.folders[form_folder].splice(idx)
				}
			}
		}
	}

	o.event_handler = function(data) {
		if (!data.event) {
			return
		}
		if (data.event == "forms_delete") {
			console.log("form delete event:", data.data.id)
			o.delete_form(data.data.id)
			return
		}
		if (data.event == "forms_change") {
			console.log("form change event", data.data.id)
			o.change_form(data.data.id)
			return
		}
	}

	o.load()

	wsh["forms_cache"] = function(data) {
		o.event_handler(data)
	}

	return o
}


//
// form renderer
//
function form(divid, options) {
	var o = {}
	o.options = options
	o.results = {}
	o.fn_triggers = {}
	o.fn_triggers_signs = []
	o.fn_trigger_last = {}
	o.cond_triggers = {}
	o.sub_forms = {}
	if (typeof divid === "string") {
		o.div = $("#"+divid)
	} else {
		o.div = divid
	}
	if (o.div.is("#link")) {
		o.div.addClass("p-3")
	}

	o.load = function() {
		if ("form_data" in o.options) {
			o.form_data = o.options.form_data
		} else {
			if (!o.options.form_name) {
				o.div.html(i18n.t("forms.form_name_not_in_options"))
				return
			}
			if ((o.options.form_name == "") || (o.options.form_name == "empty")) {
				return
			}
			o.form_data = osvc.forms.data[o.options.form_name]
		}
		if (!o.form_data) {
			o.div.html(i18n.t("forms.form_def_not_found"))
			return
		}
		o.mangle_form_data()

		if (o.options.display_mode) {
			o.render_display_mode()
		} else {
			o.render_form_mode()
		}
	}

	o.template_data_to_dict = function(t, data) {
		if (!data) {
			data = ""
		}
                var _data = {}
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			var d = o.form_data.form_definition.Inputs[i]
			var key = "%%"+d.Id.toUpperCase()+"%%"
			var l = t.split(key)
			if (l[0] == "") {
				var buff = data+""
			} else {
				var regex = new RegExp("^"+l[0].replace(/%%\w+%%/g, ".*?"))
				var buff = data.replace(regex, "")
			}
			if (l.length == 1) {
				_data[d.Id] = buff
			} else {
				var next = l[1].split(/%%\w+%%/)[0]
				var j = buff.indexOf(next)
				if (j <= 0) {
					_data[d.Id] = buff
				} else {
					_data[d.Id] = buff.slice(0,j)
				}
			}
		}
		return _data
	}

	o.mangle_form_data = function() {
		o.form_inputs = {}
		if (!o.form_data.form_definition || !o.form_data.form_definition.Inputs) {
			return
		}
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			var d = o.form_data.form_definition.Inputs[i]
			o.form_inputs[d.Id] = d
			if (d.Candidates == "__node_selector__") {
				console.log("mangle form definition: swich __node_selector__ to rest GET /users/self/nodes")
				o.form_data.form_definition.Inputs[i].Function = "/users/self/nodes"
				o.form_data.form_definition.Inputs[i].Args = ["props = nodename", "meta = 0", "limit = 0"]
				o.form_data.form_definition.Inputs[i].Candidates = null
			}
			if (d.Candidates == "__service_selector__") {
				console.log("mangle form definition: swich __node_selector__ to rest GET /users/self/services")
				o.form_data.form_definition.Inputs[i].Function = "/users/self/services"
				o.form_data.form_definition.Inputs[i].Args = ["props = svcname", "meta = 0", "limit = 0"]
				o.form_data.form_definition.Inputs[i].Candidates = null
			}
			if (d.Default == "__user_primary_group__") {
				console.log("mangle form definition: swich __user_primary_group__ to rest GET /users/self/primary_group")
				o.form_data.form_definition.Inputs[i].Function = "/users/self/primary_group"
				o.form_data.form_definition.Inputs[i].Args = ["props = role"]
				o.form_data.form_definition.Inputs[i].Default = null
			}
			if (d.Default == "__user_name__") {
				o.form_data.form_definition.Inputs[i].Default = _self.first_name + " " + _self.last_name
			}
			if (d.Default == "__user_phone_work__") {
				o.form_data.form_definition.Inputs[i].Default = _self.phone_work
			}
			if (d.Default == "__user_email__") {
				o.form_data.form_definition.Inputs[i].Default = _self.email
			}
		}
	}

	function input_has_default(d) {
		if (is_numeric(d.Default) && (d.Default == 0)) {
			return true
		}
		if (d.Default) {
			return true
		}
		return false
	}

	o.render_form_mode = function() {
		var area = $("<div name='form_area' class='container_head'></div>")
		if (o.form_data.form_definition.Vertical) {
			area.addClass("form_vertical")
		}

		o.area = area
		o.div.empty().append(area)
		o.render_form()
	}

	o.render_display_mode = function() {
		var div = $("<div class='postit' style='position:relative'></div>")
		var area = $("<div name='form_area'></div>")
		o.area = area
		div.append(o.render_edit())
		div.append(o.render_cancel())
		div.append(o.render_code())
		div.append(area)
		o.render_display()
		o.div.empty()
		o.div.append(div)
	}

	o.render_edit = function() {
		if (o.options.editable == false) {
			return ""
		}
		var a = $("<a class='icon edit16' style='position:absolute;top:2px;right:2px'></a>")
		a.attr("title", i18n.t("forms.edit")).tooltipster()
		a.bind("click", function(){
			$(this).siblings("a.nok").show()
			$(this).siblings("a.fa-th-list,a.fa-code").hide()
			$(this).hide()
			o.render_form()
		})
		return a
	}

	o.render_code = function() {
		if ("parent_form" in o.options) {
			return ""
		}
		var a = $("<a class='icon fa-code' style='position:absolute;top:2px;right:1.5em'></a>")
		if (o.options.editable == false) {
			a.css({"right": "2px"})
		}
		a.attr("title", i18n.t("forms.toggle_json")).tooltipster()
		a.bind("click", function() {
			if ($(this).hasClass("fa-code")) {
				$(this).removeClass("fa-code").addClass("fa-th-list")
				o.render_json()
			} else {
				$(this).removeClass("fa-th-list").addClass("fa-code")
				o.render_display()
			}
		})
		return a
	}

	o.render_cancel = function() {
		if (o.options.editable == false) {
			return ""
		}
		var a = $("<a class='icon nok' style='display:none;position:absolute;top:2px;right:2px'></a>")
		a.attr("title", i18n.t("forms.cancel")).tooltipster()
		a.bind("click", function(){
			$(this).siblings("a.edit16").show()
			$(this).siblings("a.fa-th-list").removeClass("fa-th-list").addClass("fa-code")
			$(this).siblings("a.fa-code").show()
			$(this).hide()
			o.render_display()
		})
		return a
	}

	o.render_json = function() {
		if ((typeof(o.options.data) == "string") || (typeof(o.options.data) == "number")) {
			o.area.text(o.options.data)
			o.area.addClass("pre")
			return
		}
		o.area.empty()
		o.area.text(JSON.stringify(o.options.data, null, 4))
		require(["hljs"], function(hljs) {
			hljs.highlightBlock(o.area[0])
		})
		o.area.addClass("pre")
	}

	o.render_display = function() {
		o.area.removeClass("hljs")
		if ((typeof(o.options.data) == "string") || (typeof(o.options.data) == "number") || (o.options.form_name == "raw")) {
			o.area.text(o.options.data)
			o.area.addClass("pre")
			return
		}
		o.area.removeClass("pre")
		if (o.options.digest) {
			o.render_display_digest()
		} else {
			o.render_display_normal()
		}
	}

	o.render_display_digest_header = function() {
		var line = $("<tr></tr>")
		var keys_done = []
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			var d = o.form_data.form_definition.Inputs[i]
			if (d.Hidden == true) {
				continue
			}
			if (d.DisplayInDigest == false) {
				continue
			}
			if (d.Key) {
				// avoid rendering multiple columns for the same input key
				if (keys_done.indexOf(d.Key) >=0) {
					continue
				}
				keys_done.push(d.Key)
			}
			var cell = $("<th></th>")
			if (d.DisplayModeLabel) {
				cell.text(d.DisplayModeLabel)
			} else {
				cell.text(d.Label)
			}
			if (i == 0) {
				cell.addClass("icon comp16")
			}
			line.append(cell)
		}
		o.area_table.append(line)
	}

	function get_dict_id(input) {
		if ("Key" in input) {
			return input.Key
		}
		return input.Id
	}

	o.render_display_digest_line = function(data, key) {
		var line = $("<tr></tr>")
		if (key) {
			var key_id = o.form_data.form_definition.Outputs[0].Key
		}
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			var d = o.form_data.form_definition.Inputs[i]
			var input_key_id = get_dict_id(d)
			if (d.Hidden == true) {
				continue
			}
			if (d.DisplayInDigest == false) {
				continue
			}
			if (d.Condition) {
				var c = o.parse_condition(d)
				var val = data[c.id]
				var ret = o.eval_condition(c, val)
				console.log("render condition:", input_key_id, "->", d.Id, ":", val, d.Condition, "=>", ret)
				if (!ret) {
					continue
				}
			}
			var cell = $("<td></td>")
			var content = ""

			if (key && (input_key_id == key_id)) {
				content = key
				cell.addClass("b")
			} else if (typeof(data) === "string") {
				content = data
				if(d.Css) {
					cell.addClass("icon_fixed_width")
					cell.addClass(d.Css)
				}
				if(d.LabelCss) {
					cell.addClass("icon_fixed_width")
					cell.addClass(d.LabelCss)
				}
			} else if (input_key_id in data) {
				content = String(data[input_key_id])
			}

			if (content == "") {
				content = "-"
			}
			if (!o.options.detailled && d.DisplayModeTrim && (content.length > d.DisplayModeTrim)) {
				content = content.slice(0, d.DisplayModeTrim/3) + "..." + content.slice(content.length-d.DisplayModeTrim/3*2, content.length)
			}
			cell.text(content)
			line.append(cell)
		}
		o.area_table.append(line)
	}

	o.render_display_digest = function() {
		if (o.form_data.form_definition.Outputs[0].Format == "dict") {
			// no digest view for dict. switch to normal.
			o.render_display_normal()
			return
		}

		o.area_table = $("<table></table>")
		o.area.empty().append(o.area_table)
		o.render_display_digest_header()
		if ((o.form_data.form_definition.Outputs[0].Format == "list") ||
                    (o.form_data.form_definition.Outputs[0].Format == "list of dict")) {
			for (var i=0; i<o.options.data.length; i++) {
				o.render_display_digest_line(o.options.data[i])
			} 
		} else if (o.form_data.form_definition.Outputs[0].Format == "dict of dict") {
			for (key in o.options.data) {
				o.render_display_digest_line(o.options.data[key], key)
			} 
		}
	}

	o.render_display_normal = function() {
		if (!(o.options.data instanceof Array)) {
			var l = [o.options.data]
		} else {
			var l = o.options.data
		}
		o.area.empty()
		for (var i=0; i<l.length; i++) {
			if (i>0 && o.form_data.form_definition.Inputs.length > 1) {
				o.area.append("<hr>")
			}
			o.area.append(o.render_display_normal_dict(l[i]))
		}
	}

	o.render_display_normal_dict = function(data) {
		var table = $("<table></table>")
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			var d = o.form_data.form_definition.Inputs[i]
			var input_key_id = get_dict_id(d)
			if (d.Hidden == true) {
				continue
			}
			if (d.Condition) {
				var c = o.parse_condition(d)
				try {
					var val = data[c.id]
				} catch(e) {
					var val = null
				}
				var ret = o.eval_condition(c, val)
				console.log("render condition:", input_key_id, "->", d.Id, ":", val, d.Condition, "=>", ret)
				if (!ret) {
					continue
				}
			}
			var line = $("<tr></tr>")
			var label = $("<th class='nowrap pr-3'></th>")
			var value = $("<td></td>")
			if (d.DisplayModeLabel) {
				label.text(d.DisplayModeLabel)
			} else {
				label.text(d.Label)
			}
			if(d.LabelCss) {
				label.addClass("icon_fixed_width")
				label.addClass(d.LabelCss)
			}
			if(d.Css) {
				value.addClass("icon_fixed_width")
				value.addClass(d.Css)
			}
			line.append(label)
			if (d.Format) {
				var label = subst_refs_from_data(data, d.Format)
				line.append(label)
			} else {
				line.append(value)
			}

                        if (d.Type == "form") {
				if (data && (input_key_id in data) && data[input_key_id]) {
					if ((is_dict(data[input_key_id]) || Array.isArray(data[input_key_id])) && Object.keys(data[input_key_id]).length==0) {
						// save space not displaying empty data
						continue
					}
					var opt_data = data[input_key_id]
				} else {
					continue
				}
				form(value, {
					"parent_form": o,
					"form_name": d.Form,
					"display_mode": true,
					"editable": false,
					"data": opt_data
				})
				table.append(line)
				continue
			}

 			if (is_dict(data) && input_key_id in data) {
				var content = String(data[input_key_id])
			} else if (typeof data === "string") {
				var content = data
			} else {
				var content = ""
			}
			if (content == "") {
				content = "-"
			}
			if (content instanceof Array) {
				for (var j=0; j<content.length; j++) {
					value.append("<span class='tag tag_attached'>"+content[j]+"</span>")
				}
			} else {
				if (!o.options.detailled && d.DisplayModeTrim && (content.length > d.DisplayModeTrim)) {
					content = content.slice(0, d.DisplayModeTrim/3) + "..." + content.slice(content.length-d.DisplayModeTrim/3*2, content.length)
				}
				value.text(content)
			}
			table.append(line)
		}
		return table
	}

	o.render_form_group = function(data) {
		var t = o.form_data.form_definition.Outputs[0].Template
                if (t) {
			data = o.template_data_to_dict(t, data)
		}

		var table = $("<table></table>")
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			var d = o.form_data.form_definition.Inputs[i]
			var input_key_id = get_dict_id(d)
			var line = $("<tr></tr>")
			var label = $("<th style='white-space:nowrap'></th>")
			var value = $("<td name='val'></td>")
			line.attr("iid", d.Id)
			if (d.ExpertMode == true) {
				line.addClass("hidden")
			}
			if (d.Hidden == true) {
				line.addClass("hidden")
			}
			label.text(d.Label)
			if(d.LabelCss) {
				label.addClass("icon_fixed_width")
				label.addClass(d.LabelCss)
			}
			line.append(label)
			line.append(value)
			if (d.Help) {
				label.addClass("cursor-help").tooltipster({
					content: $("<div>"+d.Help+"</div>"),
					interactive: true,
					trigger: 'custom',
					triggerOpen: {
						click: true,
						tap: true
					},
					triggerClose: {
						click: true,
						tap: true,
						scroll: true
					}
				})
			}
			if ((typeof(data) === "undefined") || (is_dict(data) && !(input_key_id in data))) {
				if (d.Default == "__user_email__") {
					var content = _self.email
				} else if (d.Default == "__user_primary_group__") {
					var content = _self.primary_group
				} else if (d.Default == "__user_phone_work__") {
					var content = _self.phone_work
				} else if (d.Default == "__user_name__") {
					var content = _self.first_name + " " + _self.last_name
				} else if (typeof d.Default !== "undefined") {
					var content = d.Default
				} else if (d.Type == "form") {
					var content = undefined
				} else {
					var content = ""
				}
			} else if (d.var_class=="raw" || (typeof(data) === "string") || (typeof(data) === "number")) {
				var content = data
			} else if (is_dict(data) && input_key_id in data) {
				var content = data[input_key_id]
			} else {
				var content = ""
			}

			if (d.Type == "date") {
				var input = o.render_date(d, content)
			} else if (d.Type == "datetime") {
				var input = o.render_datetime(d, content)
			} else if (d.Type == "time") {
				var input = o.render_time(d, content)
			} else if (d.Type == "info") {
				var input = o.render_info(d, content)
			} else if (d.Type == "text") {
				var input = o.render_text(d, content)
			} else if (d.Type == "boolean") {
				var input = o.render_boolean(d, content)
			} else if (d.Type == "checklist") {
				var input = o.render_checklist(d, content)
			} else if (d.Type == "form") {
				var input = o.render_sub_form(d, content)
			} else {
				var input = o.render_input(d, content)
			}

			if (o.form_data.form_definition.Width) {
				input.width(o.form_data.form_definition.Width)
			}

			if (d.Condition && d.Condition.match(/#/)) {
				o.add_cond_triggers(d)
			}

			value.append(input)
			table.append(line)
			if (d.Type == "boolean") {
				input.bootstrapToggle()
			}
		}
		o.install_mandatory_triggers(table)
		o.install_constraint_triggers(table)
		o.install_cond_triggers(table)
		o.install_fn_triggers(table)
		return table
	}

	o.render_move_group = function() {
		var div = $("<div class='icon_fixed_width fa-bars form_tool movable'></div>")
		return div
	}

	o.render_del_group = function() {
		var div = $("<div class='icon_fixed_width del16 form_tool nowrap'></div>")
		div.text(i18n.t("forms.del_group"))
		div.bind("click", function() {
			$(this).parent().remove()
		})
		return div
	}

	o.render_expert_toggle = function() {
		var n = 0
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			var d = o.form_data.form_definition.Inputs[i]
			if (d.ExpertMode) {
				n++
			}
		}
		if (n == 0) {
			return
		}
		var div = $("<button class='icon_fixed_width fa-unlock form_tool col-12'></button>")
		div.text(i18n.t("forms.expert"))
		o.area.append(div)
		div.bind("click", function() {
			if (div.hasClass("fa-unlock")) {
				div.removeClass("fa-unlock").addClass("fa-lock")
			} else {
				div.removeClass("fa-lock").addClass("fa-unlock")
			}
			for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
				var d = o.form_data.form_definition.Inputs[i]
				if (!d.ExpertMode) {
					continue
				}
				o.div.find("[iid="+d.Id+"]").toggle(500)
			}
		})
	}

	o.init_sortable = function() {
			o.area.sortable({
				helper: "clone",
				connectWith: ".form_group",
				handle: ".fa-bars",
				cancel: ".form_group *:not('.fa-bars')",
				placeholder: "fset_designer_placeholder",
				containment: "parent",
				start: function(event, ui) {
					ui.helper.addClass("sort_helper")
				}
			})
	}

	o.render_add_group = function() {
		var div = $("<div class='icon_fixed_width add16 form_tool col-12'>")
		div.text(i18n.t("forms.add_group"))
		o.area.append(div)
		div.bind("click", function() {
			var ref = o.area.children(".form_group").last()
			var move = o.render_move_group()
			var remove = o.render_del_group()
			var data = o.table_to_dict(ref)
			var new_group = o.render_form_group(data)
			var form_group = $("<div class='form_group'></div>")
			form_group.append(move)
			form_group.append(remove)
			form_group.append(new_group)
			form_group.insertAfter(ref)
			o.init_sortable()
		})
	}

	o.render_form_list = function() {
		o.area.empty()
		if (!o.options.data || o.options.data.length == 0) {
			var form_group = $("<div class='form_group'></div>")
			form_group.append(o.render_move_group())
			form_group.append(o.render_del_group())
			form_group.append(o.render_form_group({}))
			o.area.append(form_group)
		} else {
			for (var i=0; i<o.options.data.length; i++) {
				var form_group = $("<div class='form_group'></div>")
				form_group.append(o.render_move_group())
				form_group.append(o.render_del_group())
				form_group.append(o.render_form_group(o.options.data[i]))
				o.area.append(form_group)
			}
		}
		o.render_add_group()
		o.render_expert_toggle()
		o.render_submit()
		o.render_test()
		o.render_result()
		o.init_sortable()
	}

	o.render_form_dict_of_dict = function() {
		o.area.empty()
		var key_id = o.form_data.form_definition.Outputs[0].Key
		var i = 0
		if (!is_dict(o.options.data)) {
			// empty data
			o.options.data = {}
		}
		for (key in o.options.data) {
			i++
			o.options.data[key][key_id] = key
			var form_group = $("<div class='form_group'></div>")
			form_group.append(o.render_move_group())
			form_group.append(o.render_del_group())
			form_group.append(o.render_form_group(o.options.data[key]))
			o.area.append(form_group)
		}
		if (i == 0) {
			var form_group = $("<div class='form_group'></div>")
			form_group.append(o.render_del_group())
			form_group.append(o.render_move_group())
			form_group.append(o.render_form_group({}))
			o.area.append(form_group)
		}
		o.render_add_group()
		o.render_expert_toggle()
		o.render_submit()
		o.render_test()
		o.render_result()
		o.init_sortable()
	}

	o.render_form_dict = function() {
		o.area.empty().append(o.render_form_group(o.options.data))
		o.render_expert_toggle()
		o.render_submit()
		o.render_test()
		o.render_result()
	}

	o.render_form = function() {
		o.area.removeClass("pre")
		if (!o.form_data.form_definition) {
			o.area.html("<div data-i18n='forms.no_definition' class='icon fa-exclamation-triangle grayed'></div>").i18n()
			return
		}
		if (!o.form_data.form_definition.Outputs) {
			o.area.html("<div data-i18n='forms.no_output' class='icon fa-exclamation-triangle grayed'></div>").i18n()
			return
		}
		var f = o.form_data.form_definition.Outputs[0].Format
		if (!f || (f == "dict")) {
			o.render_form_dict()
		} else if (f == "dict of dict") {
			o.render_form_dict_of_dict()
		} else if (f == "list of dict") {
			o.render_form_list()
		} else if (f == "list") {
			o.render_form_list()
		} else {
			console.log("render_form: unsupported format", f) 
		}
		o.update_submit()
	}

	o.render_result = function() {
		if (o.options.submit == false) {
			return
		}
		var result = $("<div style='text-align:left;padding:1em 0'></div>")
		o.area.append(result)
		o.result = result
	}

	o.submit_form_data = function(data) {
		var _data = {}
		if (typeof(data) === "string") {
			_data.data = data
		} else {
			_data.data = JSON.stringify(data)
		}
		if (o.options.prev_wfid) {
			_data.prev_wfid = o.options.prev_wfid
		}
		if (o.form_data.form_definition.Async) {
			spinner_add(o.result, i18n.t("forms.creating_task"))
		} else {
			spinner_add(o.result, i18n.t("forms.RUNNING"))
		}
		services_osvcputrest("R_FORM", [o.form_data.id], "", _data, function(jd) {
			if (jd.error) {
				o.result.html("<div class='icon_fixed_width nok'>"+jd.error+"</div>")
				return
			}
			form_results(o.result, {
				"results_id": jd.results_id,
				"async": o.form_data.form_definition.Async
			})
		},
		function(xhr, stat, error) {
			o.result.html(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.submit_output_compliance = function(data) {
		var _data = {}
		if (typeof(data) === "string") {
			_data.var_value = data
		} else {
			for (var key in data) {
				if (!Array.isArray(data[key]) && (typeof(data[key]) === "string") && (data[key] == "")) {
					delete(data[key])
				}
			}
			_data.var_value = JSON.stringify(data)
		}
		services_osvcpostrest("R_COMPLIANCE_RULESET_VARIABLE", [o.options.rset_id, o.options.var_id], "", _data, function(jd) {
			if (rest_error(jd)) {
				o.result.html(services_error_fmt(jd))
				return
			}
			try {
				o.options.data = $.parseJSON(jd.data[0].var_value)
			} catch(e) {
				o.options.data = jd.data[0].var_value
			}
			o.result.html("<div class='icon ok'>"+i18n.t("forms.success")+"</div>")
		},
		function(xhr, stat, error) {
			o.result.html(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.submit_output_tag_data = function(data) {
		var _data = {}
		if (typeof(data) === "string") {
			var tag_data = data
		} else {
			for (var key in data) {
				if (!Array.isArray(data[key]) && (typeof(data[key]) === "string") && (data[key] == "")) {
					delete(data[key])
				}
			}
			var tag_data = JSON.stringify(data)
		}
		var path = "/tags/%1"
		var params = [o.options.tag_id]
		if (o.options.node_id) {
			path += "/nodes/%2"
			params.push(o.options.node_id)
			_data.tag_attach_data = tag_data
		} else if (o.options.svc_id) {
			path += "/services/%2"
			params.push(o.options.svc_id)
			_data.tag_attach_data = tag_data
		} else {
			_data.tag_data = tag_data
		}
		services_osvcpostrest(path, params, "", _data, function(jd) {
			if (rest_error(jd)) {
				o.result.html(services_error_fmt(jd))
				return
			}
			o.options.data = tag_data
			o.result.html("<div class='icon ok'>"+i18n.t("forms.success")+"</div>")
		},
		function(xhr, stat, error) {
			o.result.html(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.submit_output = function(output, data) {
		if (o.options.tag_id) {
			o.submit_output_tag_data(data)
		} else if (output.Dest == "compliance variable") {
			o.submit_output_compliance(data)
		} else {
			console.log("Output " + output.Dest + " not supported client-side")
			o.need_submit_form_data = true
		}
	}

	o.render_test = function() {
		if (o.options.test == false) {
			return
		}
		var button = $("<button class='icon_fixed_width fa-code button_div'>")
                o.test_tool = button
		button.text(i18n.t("forms.test"))
		button.css({"margin-top": "1em"})
		o.area.append(button)

		button.bind("click", function() {
			var data = o.form_to_data()
			var data_title = $("<h2>"+i18n.t("forms.test_title")+"</h2>")
			var data_pre = $("<pre style='text-align:left'>"+JSON.stringify(data, null, 4)+"</pre>")
			var render_title = $("<h2>"+i18n.t("forms.test_render_title")+"</h2>")
			var render_div = $("<div></div>")
			o.result.empty().append(data_title)
					.append(data_pre)
					.append(render_title)
					.append(render_div)
			require(["hljs"], function(hljs) {
				hljs.highlightBlock(data_pre[0])
			})
			form(render_div, {
				"form_name": o.options.form_name,
				"display_mode": true,
				"editable": false,
				"data": data
			})
		})
	}

	o.render_submit = function() {
		if (o.options.submit == false) {
			return
		}
		var button = $("<button class='icon_fixed_width fa-save button_div'>")
                o.submit_tool = button
		button.text(i18n.t("forms.submit"))
		button.css({"margin-top": "1em"})
		o.area.append(button)

		button.bind("click", function() {
			if (o.submit_disabled()) {
				o.area.find(".constraint_violation,.mandatory_violation").effect("highlight", 600)
				return
			}
			o.result.empty()
			var data = o.form_to_data()
			o.submit_action(data)
		})
	}

	o.submit_action = function(data) {
		o.need_submit_form_data = false
		o.results = {}
		for (var i=0; i<o.form_data.form_definition.Outputs.length; i++) {
			var output = o.form_data.form_definition.Outputs[i]
			o.submit_output(output, data)
		}
		if (o.need_submit_form_data == true) {
			o.need_submit_form_data = false
			o.submit_form_data(data)
		}
	}

	o.render_time = function(d, content) {
		var input = $("<input class='oi'>")
		if (d.ReadOnly == true) {
			input.prop("disabled", true)
		}
		input.val(content)
		input.uniqueId()
		input.timepicker()
		return input
	}
	o.render_datetime = function(d, content) {
		var input = $("<input class='oi'>")
		if (d.ReadOnly == true) {
			input.prop("disabled", true)
		}
		input.val(content)
		input.uniqueId()
		input.datetimepicker({dateFormat:'yy-mm-dd'})
		return input
	}
	o.render_date = function(d, content) {
		var input = $("<input class='oi'>")
		if (d.ReadOnly == true) {
			input.prop("disabled", true)
		}
		input.val(content)
		input.uniqueId()
		input.datepicker({dateFormat:'yy-mm-dd'})
		return input
	}
	o.render_info = function(d, content) {
		var div = $("<div class='form_input_info' style='padding:0.4em'>")
		div.text(content)
		if (d.Function && fn_has_refs(d)) {
			o.add_fn_triggers(d)
		}
		return div
	}
	o.render_text = function(d, content) {
		var textarea = $("<textarea class='oi pre' style='padding:0.4em;min-width:17em;min-height:8em'>")
		if (d.ReadOnly == true) {
			textarea.prop("disabled", true)
		}
		textarea.val(content)
		if (d.Function && fn_has_refs(d)) {
			o.add_fn_triggers(d)
		}
		return textarea
	}
	o.render_input_simple = function(d, content) {
		var input = $("<input class='oi'>")
		if (d.ReadOnly == true) {
			input.prop("disabled", true)
		}
		if (d.Type == "password") {
			input.prop("type", "password")
		}
		input.val(content)
		input.prop("acid", content)
		return input
	}
	o.render_input = function(d, content) {
		if (d.Candidates && (d.Candidates instanceof Array)) {
			return o.render_select_static(d, content)
		} else if (d.Function) {
			return o.render_select_rest(d, content)
		} else {
			return o.render_input_simple(d, content)
		}
	}
	o.render_select_static = function(d, content) {
		var input = $("<input class='oi aci'>")
		if (d.ReadOnly == true) {
			input.prop("disabled", true)
		}
		var opts = []
		var acid = content
		for (var i=0; i<d.Candidates.length; i++) {
			var _d = d.Candidates[i]
			if (typeof(_d) === "string") {
				opts.push({
					"id": _d,
					"label": _d
				})
			} else if (("Label" in _d) && ("Value" in _d)) {
				opts.push({
					"id": _d.Value,
					"label": _d.Label
				})
				if (_d.Value == content) {
					acid = _d.Value
					content = _d.Label
				}
			}
		}
		input.autocomplete({
			mustMatch: true,
			source: opts,
			minLength: 0,
			response: function(event, ui) {
				o.update_candidates_violation(d, input, opts)
			},
			change: function(event, ui) {
				if (ui.item) {
					input.prop("acid", ui.item.id)
					input.removeClass("candidates_violation")
				} else {
					input.removeProp("acid")
				}
				o.update_candidates_violation(d, input, opts)
				input.change()
			},
			focus: function(event, ui) {
				return false
			},
			select: function(event, ui) {
				input.prop("acid", ui.item.id)
				input.removeClass("candidates_violation")
				input.change()
			}
		})
		input.bind("blur", function(event) {
			o.update_candidates_violation(d, input, opts)
			input.change()
		})
		input.bind("keyup", function(event) {
			if (input.val() == "") {
				input.removeProp("acid")
			}
			o.update_candidates_violation(d, input, opts)
			input.change()
		})
		if (content && (content.length > 0)) {
			input.prop("acid", acid)
			input.val(content)
		}
		input.change()
		return input
	}

	o.render_select_rest = function(d, content) {
		var input = $("<input class='oi aci'>")
		if (d.ReadOnly == true) {
			input.prop("disabled", true)
		}
		input.val(content)
		if (fn_has_refs(d)) {
			o.add_fn_triggers(d)
			return input
		}
		fn_init(input, d, content)
		return input
	}

	o.render_boolean = function(d, content) {
		var input = $("<input type='checkbox' data-toggle='toggle' data-onstyle='success' data-offstyle='danger'>")
		if (d.ReadOnly == true) {
			input.prop("disabled", true)
		}
		if (content == true) {
			input.prop("checked", true)
			input.prop("acid", true)
		} else {
			input.prop("acid", false)
		}
		input.bind("change", function(){
			if ($(this).prop("checked")) {
				$(this).prop("acid", true)
			} else {
				$(this).prop("acid", false)
			}
		})
		return input
	}
	o.render_checklist = function(d, content) {
		if (d.Candidates && (d.Candidates instanceof Array)) {
			return o.render_checklist_static(d, content)
		} else if (d.Function) {
			return o.render_checklist_rest(d, content)
		}
	}
	o.render_checklist_rest = function(d, content) {
		input = $("<div class='form_input_info'><div>")
		if (fn_has_refs(d)) {
			o.add_fn_triggers(d)
			return input
		}
		fn_init(input, d, content)
		return input
	}
	o.render_checklist_static = function(d, content) {
		input = $("<div class='form_input_info' style='padding:0.5em 0'><div>")
		checklist_callback(input, d, [], d.Candidates, content)
		return input
	}
	o.render_sub_form = function(d, content) {
		if (!d.Form) {
			return
		}
		var div = $("<div></div>")
		o.sub_forms[d.Id] = form(div, {
			"parent_form": o,
			"form_name": d.Form,
			"data": content,
			"display_mode": false,
			"submit": false,
			"test": false
		})
		return div
	}


	function fn_has_refs(d) {
		// hardcoded refs
		d.Function = d.Function.replace(/#user_id/g, _self.id)

		if (d.Function.match(/#/)) {
			return true
		}
		if (d.Args) {
			for (var i=0; i<d.Args.length; i++) {
				d.Args[i] = d.Args[i].replace(/#user_id/g, _self.id)
				if (d.Args[i].match(/#/)) {
					return true
				}
			}
		}
		return false
	}

	function fn_init(input, d, content) {
		if (d.Type == "checklist") {
			var fn_callback = checklist_callback
		} else {
			var fn_callback = autocomplete_callback
		}
		if (d.Function.match(/^\//) || d.Function.match(/^http/)) {
			return rest_init(input, d, content, fn_callback)
		} else {
			return jsonrpc_init(input, d, content, fn_callback)
		}
	}

	function checklist_callback(input, d, args, data, content) {
		if (data.length == 0) {
			input.empty()
			return
		}

		// add a 'toggle all' master checkbox
		var line = $("<div style='padding:0.2em'></div>")
		var master_cb = $("<input type='checkbox' class='ocb'>")
		var master_cb_label = $("<label></label>")
		var e_label = $("<span class='grayed' style='padding:0 0.3em'></span>")

		if (!content) {
			// set a sane default to content
			var has_default = false
			content = []
		} else {
			var has_default = true
		}

		master_cb.uniqueId()
		master_cb_label.attr("for", master_cb.attr("id"))
		e_label.text(i18n.t("forms.toggle_all"))
		line.append(master_cb)
		line.append(master_cb_label)
		line.append(e_label)
		input.html(line)
		if (!has_default && (d.CheckOnLoad == "all")) {
			master_cb.prop("checked", true)
		}
		if (d.ReadOnly) {
			master_cb.prop("disabled", true)
		}
		master_cb.bind("change", function() {
			var state = $(this).prop("checked")
			$(this).parent().siblings().children("input[type=checkbox]").prop("checked", state)
			o.update_submit()
		})

		// ck value can be a string, ex: id from a rest get are strings
		str_content = content.map(function(el) {
			return ""+el
		})

		for (var i=0; i<data.length; i++) {
			var _d = data[i]
			if (typeof(_d) === "string") {
				var value = _d
				var label = _d
			} else if (("Value" in _d) && ("Label" in _d)) {
				var value = _d.Value
				var label = _d.Label
			} else if (("Format" in d) && ("Value" in d)) {
				var label = d.Format
				var value = d.Value
				label = subst_refs_from_data(_d, label)
				value = subst_refs_from_data(_d, value)
			}
			var line = $("<div style='padding:0.2em'></div>")
			var cb = $("<input type='checkbox' class='ocb'>")
			var cb_label = $("<label></label>")
			var e_label = $("<span style='padding:0 0.3em'></span>")
			cb.uniqueId()
			cb.prop("acid", value)
			cb_label.attr("for", cb.attr("id"))
			e_label.text(label)
			line.append(cb)
			line.append(cb_label)
			line.append(e_label)
			input.append(line)
			if (str_content.indexOf(""+value) >= 0) {
				cb.prop("checked", true)
			}
			if (!has_default && (d.CheckOnLoad == "all")) {
				cb.prop("checked", true)
			}
			if (d.ReadOnly) {
				cb.prop("disabled", true)
			}
			cb.bind("change", function() {
				o.update_submit()
			})
		}
	}

	function autocomplete_callback(input, d, args, data, content) {
		if (typeof(data) === "undefined") {
			return
		} else if (typeof(data) === "string") {
			if (input.hasClass("form_input_info")) {
				input.text(data)
			} else {
				input.val(data)
			}
			input.change()
			return
		}
		var opts = []
		var acid = content
		for (var i=0; i<data.length; i++) {
			var _d = data[i]
			if (typeof(_d) === "string") {
				opts.push({
					"id": _d,
					"label": _d
				})
			} else if (("Format" in d) && ("Value" in d)) {
				var label = d.Format
				var value = d.Value
				label = subst_refs_from_data(_d, label)
				value = subst_refs_from_data(_d, value)
				opts.push({
					"id": value,
					"label": label,
					"option_data": _d
				})
			} else {
				var prop = args.props.split(",")[0]
				var value = subst_refs_from_data(_d, "#"+prop)
				opts.push({
					"id": value,
					"label": value,
					"option_data": _d
				})
			}
			if (!d.DisableAutoDefault && !content && (opts.length > 0)) {
				var acid = opts[0].id
				content = opts[0].label
				var option_data = opts[0].option_data
			}
		}

		function opts_to_text(opts) {
			if (!opts) {
				return ""
			}
			var l = []
			for (var i=0; i<opts.length; i++) {
				l.push(opts[i].label)
			}
			return l.join("\n")
		}

		if (input.hasClass("form_input_info")) {
			input.text(opts_to_text(opts))
		} else if (input.is("textarea")) {
			input.val(opts_to_text(opts))
		} else {
			if ($.data(input[0], "ui-autocomplete") != undefined) {
				input.autocomplete("destroy")
			}
			input.val("")
			input.removeProp("acid")
			input.removeProp("option_data")
			input.autocomplete({
				mustMatch: true,
				source: opts,
				minLength: 0,
				response: function(event, ui) {
					o.update_candidates_violation(d, input, opts)
				},
				change: function(event, ui) {
					if (ui.item) {
						$(this).prop("acid", ui.item.id)
						$(this).prop("option_data", ui.item.option_data)
						input.removeClass("candidates_violation")
					} else {
						input.removeProp("acid")
						input.removeProp("option_data")
					}
					o.update_candidates_violation(d, input, opts)
					$(this).change()
				},
				focus: function(event, ui) {
					return false
				},
				select: function(event, ui) {
					$(this).prop("acid", ui.item.id)
					$(this).prop("option_data", ui.item.option_data)
					input.removeClass("candidates_violation")
					$(this).change()
				}
			})
			input.bind("blur", function(event) {
				o.update_candidates_violation(d, input, opts)
				$(this).change()
			})
			input.bind("keyup", function(event) {
				if ($(this).val() == "") {
					$(this).removeProp("acid")
					$(this).removeProp("option_data")
				}
				o.update_candidates_violation(d, input, opts)
				$(this).change()
			})
			if (opts.length == 1) {
				input.removeClass("aci")
			} else {
				input.addClass("aci")
			}
		}
		if (content && (content.length > 0)) {
			input.prop("acid", acid)
			if (d.Format != d.Value) {
				for (var j=0; j<opts.length; j++) {
					if (opts[j].id != content) {
						continue
					}
					input.prop("option_data", content)
					input.val(opts[j].label)
					break
				}
			}
			if (!input.val()) {
				input.prop("option_data", option_data)
				input.val(content)
			}
		}
		input.change()
	}

	function jsonrpc_init(input, d, content, fn_callback) {
		var args = prepare_args(input, d.Args)
		for (key in args) {
			if (!args[key]) {
				console.log("cancel jsonrpc on", d.Function, ": missing parameters", args)
				return
			}
		}
		$.ajax({
			url: "/init/forms/call/json/"+d.Function,
			data: args,
			success: function(data) {
				fn_callback(input, d, args, data, content)
			}

		})
	}

	function rest_init(input, d, content, fn_callback) {
		var args = prepare_args(input, d.Args)
		var fn = subst_refs(input, d.Function)
		if (fn.match(/^\//) && fn.match(/\/\//)) {
			console.log("missing data in rest path")
			return
		}
		if (fn.match(/\/undefined\//) || fn.match(/\/$/) || fn.match(/#/)) {
			console.log("cancel rest get on", fn, ": missing parameters")
			return
		}
		var key = input.attr("id")
		if (!key) {
			input.uniqueId()
			var key = input.attr("id")
		}
		var sign = fn_sign(fn, args)
		if ((key in o.fn_trigger_last) && (o.fn_trigger_last[key] == sign)) {
			console.log("cancel rest get on", fn, ": same as last call")
			return
		}
		o.fn_trigger_last[key] = sign
		services_osvcgetrest(fn, "", args, function(jd) {
			if (typeof(jd.data) === "undefined") {
				var data = []
			} else {
				var data = jd.data
			}
			fn_callback(input, d, args, data, content)
		}, function(){
			// ignore errors (due to incomplete form data)
		})
	}

	function fn_sign(fn, args) {
		s = fn
		for (key in args) {
			s += "-"+args[key]
		}
		return s
	}

	function subst_refs_from_data(data, s) {
		if (!is_dict(data)) {
			console.log("skip subst_refs_from_data: data is not a dict.", data)
			return s
		}
		var re = RegExp(/#[\w\.]+/g)
		var _s = s

		do {
			var m = re.exec(s)
			if (m) {
				var key = m[0].replace("#", "")
				var keys = key.split(".")
				var val = data
				for (var i=0; i<keys.length; i++) {
					if (keys[i] in val) {
						var val = val[keys[i]]
					}
				}
				var re1 = RegExp("#"+key, "g")
				var t = typeof val
				if ((t === "number") || (t === "string")) {
					_s = _s.replace(re1, val)
				}
			}
		} while (m)
		return _s
	}

	function subst_refs(input, s) {
		var table = input.parents("table").first()
		var data = o.table_to_dict(table)
		return subst_refs_from_data(data, s)
	}

	o.install_constraint_triggers = function(table) {
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			var d = o.form_data.form_definition.Inputs[i]
			if (d.Type == "form") {
				return
			}
			var input = table.find("[iid="+d.Id+"] > [name=val]").children("div,textarea,input")
			o.install_constraint_trigger(input, d)
		}
	}

	o.install_constraint_trigger = function(input, d) {
		if (!d.Constraint) {
			return
		}
		if (d.Type == "checklist") {
			return
		}
		trigger(input)
		input.bind("keyup change", function() {
			trigger($(this))
		})
		function trigger(e) {
			var s = e.val()
			var re = RegExp(d.Constraint.replace(/^match\s+/, ""))
			if (!re.exec(s)) {
				e.addClass("constraint_violation")
			} else {
				e.removeClass("constraint_violation")
			}
			o.update_submit()
		}
	}

	o.install_mandatory_triggers = function(table) {
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			var d = o.form_data.form_definition.Inputs[i]
			var input = table.find("[iid="+d.Id+"] > [name=val]").children("div,textarea,input")
			o.install_mandatory_trigger(input, d)
		}
	}

	o.update_candidates_violation = function(d, input, opts) {
		if (!d.StrictCandidates) {
			return
		}

		function is_candidate(v, opts) {
			for (var i=0; i<opts.length; i++) {
				if (opts[i].label==v) {
					return true
				}
			}
			return false
		}

		var v = input.val()
		console.log(v, opts)
		if (is_candidate(v, opts)) {
			input.removeClass("candidates_violation")
		} else {
			input.addClass("candidates_violation")
		}
		o.update_submit()
	}

	o.update_submit = function() {
		if (o.div.find(".constraint_violation,.mandatory_violation,.candidates_violation").parents("tr[iid]:not(.hidden)").length == 0) {
			o.enable_submit()
		} else {
			o.disable_submit()
		}
		if (o.options.parent_form) {
			o.options.parent_form.update_submit()
		}
	}

	o.submit_disabled = function() {
		return o.submit_tool.hasClass("nok")
	}

	o.disable_submit = function() {
		if (!o.submit_tool) {
			return
		}
		o.submit_tool.addClass("nok").removeClass("fa-save")
	}

	o.enable_submit = function() {
		if (!o.submit_tool) {
			return
		}
		o.submit_tool.addClass("fa-save").removeClass("nok")
	}

	o.install_mandatory_trigger = function(input, d) {
		if (d.Mandatory != true) {
			return
		}
		if (d.Type == "checklist") {
			return
		}
		if (d.Type == "form") {
			return
		}
		if (d.Type == "boolean") {
			return
		}
		trigger(input)
		input.bind("keyup change", function() {
			trigger($(this))
		})
		function trigger(e) {
			if (e.val() == "") {
				e.addClass("mandatory_violation")
			} else {
				e.removeClass("mandatory_violation")
			}
			o.update_submit()
		}
	}

	o.hide_input = function(table, d, initial) {
		var tr = table.find("[iid="+d.Id+"]")
		if (!initial && tr.hasClass("hidden")) {
			console.log("hide", d.Id, "already not visible")
			return
		}
		console.log("hide", d.Id)
		tr.addClass("hidden")
		tr.find("[name=val]").children("input,textarea").val("").prop("acid", "").trigger("change")
		if (d.Id in o.cond_triggers) {
			var triggers = o.cond_triggers[d.Id]
			for (var i=0; i<triggers.length; i++) {
				if (o.div.find("tr[iid="+triggers[i].Id+"]").hasClass("hidden")) {
					continue
				}
				o.hide_input(table, triggers[i], initial)
			}
		}
	}

	o.show_input = function(table, d) {
		var tr = table.find("[iid="+d.Id+"]")
		if (!tr.hasClass("hidden")) {
			return
		}
		console.log("show", d.Id)
		tr.removeClass("hidden")
		var input = tr.find("[name=val]").children("input,textarea,.form_input_info")
		if (d.Function && fn_has_refs(d)) {
			fn_init(input, d, null, autocomplete_callback)
			var data = $.data(input[0])
			if (data.autocomplete && data.autocomplete.options.source.length > 0) {
				input.val(data.autocomplete.options.source[0].label)
				input.prop("acid", data.autocomplete.options.source[0].id)
				input.change()
			}
		} else if ((d.Type == "string" || d.Type == "integer" || d.Type == "time" || d.Type == "date" || d.Type == "datetime") && input_has_default(d)) {
			input.val(d.Default)
			input.prop("acid", d.Default)
			input.change()
		}
	}

	o.install_cond_trigger = function(table, key, d) {
		console.log("install cond trigger", key, "->", d.Id)

		var line = table.find("[iid="+key+"]")
		if (line.length == 0) {
			var input_id = o.resolve_key(key)
			var line = table.find("[iid="+input_id+"]")
		}
		var cell = line.children("[name=val]").children("input,textarea")
		trigger(cell, true)
		cell.bind("change", function() {
			trigger($(this))
		})
		function trigger(input, initial) {
			if (key in o.form_inputs) {
				var val = o.get_val(input.parent())
			} else {
				var data = o.form_to_data()
				var val = data[key]
			}
			var c = o.parse_condition(d)
			var ret = o.eval_condition(c, val)
			console.log("condition:", key, "->", d.Id, val , d.Condition, "=>", ret)
			if (ret) {
				o.show_input(table, d)
			} else {
				o.hide_input(table, d, initial)
			}
		}
	}

	o.parse_condition = function(d) {
		if (d.Condition.match(/!=/)) {
			var op = "!="
		} else if (d.Condition.match(/==/)) {
			var op = "=="
		} else if (d.Condition.match(/NOT IN/)) {
			var op = "NOT IN"
		} else if (d.Condition.match(/IN/)) {
			var op = "IN"
		} else if (d.Condition.match(/>/)) {
			var op = ">"
		} else if (d.Condition.match(/</)) {
			var op = "<"
		} else {
			console.log(d.Id, "unsupported condition operator:", d.Condition)
		}

		var ref = d.Condition.split(op)[1]
		var id = d.Condition.split(op)[0]

		// strip
		id = id.replace(/^\s+/, "").replace(/\s+$/, "").replace(/^#/, "")
		ref = ref.replace(/^\s+/, "").replace(/\s+$/, "")
		return {"id": id, "op": op, "ref": ref}
	}

	o.eval_condition = function(c, val) {
		if (typeof val === "undefined") {
			return false
		}
		else if (typeof val === "number") {
			try {
				c.ref = parseInt(c.ref)
			} catch(e) {}
		}
		else if (typeof val === "boolean") {
			c.ref = (c.ref.toLowerCase() == 'true')
		}
		if ((val != "") || (typeof val === "number")) {
			if (c.op == "!=") {
				if (c.ref == "empty") {
					// foo != empty
					return true
				} else if (val != c.ref) {
					// foo != bar
					return true
				} else {
					// foo != foo
					return false
				}
			} else if (c.op == "==") {
				if (c.ref == "empty") {
					// foo == empty
					return false
				} else if (val == c.ref) {
					// foo == foo
					return true
				} else {
					// foo == bar
					return false
				}
			} else if (c.op == "NOT IN") {
				var l = c.ref.split(",")
				if (l.indexOf(val) >= 0) {
					return false
				} else {
					return true
				}
			} else if (c.op == "IN") {
				var l = c.ref.split(",")
				if (l.indexOf(val) >= 0) {
					return true
				} else {
					return false
				}
			} else if (c.op == ">") {
				if (c.ref == "empty") {
					// foo > empty
					return false
				} else if (val > c.ref) {
					// foo > foo
					return true
				} else {
					// foo > bar
					return false
				}
			} else if (c.op == "<") {
				if (c.ref == "empty") {
					// foo < empty
					return false
				} else if (val < c.ref) {
					// foo < foo
					return true
				} else {
					// foo < bar
					return false
				}
			}
		} else {
			if (c.op == "!=") {
				if (c.ref == "empty") {
					// empty != empty
					return false
				} else {
					// empty != foo
					return true
				}
			} else if (c.op == "==") {
				if (c.ref == "empty") {
					// empty == empty
					return true
				} else {
					// empty == foo
					return false
				}
			} else if (c.op == "NOT IN") {
				return false
			} else if (c.op == "IN") {
				return false
			} else if (c.op == ">") {
				return false
			} else if (c.op == "<") {
				return false
			}
		}
	}

	o.install_cond_triggers = function(table) {
		for (key in o.cond_triggers) {
			var triggers = o.cond_triggers[key]
			for (var i=0; i<triggers.length; i++) {
				var d = triggers[i]
				o.install_cond_trigger(table, key, d)
			}
		}
	}

	o.add_cond_triggers = function(d) {
		var re = RegExp(/#\w+/g)
		do {
			var m = re.exec(d.Condition)
			if (m) {
				var key = m[0].replace("#", "")
				if (key in o.cond_triggers) {
					o.cond_triggers[key].push(d)
				} else {
					o.cond_triggers[key] = [d]
				}
			}
		} while (m)
	}

	o.install_fn_trigger = function(table, key, d) {
		console.log("install fn trigger", key, "->", d.Id)
		var cell = table.find("[iid="+key+"]").children("[name=val]").children("input,textarea")
		cell.bind("change", function() {
			var input = table.find("[iid="+d.Id+"]").find("input:not([type=checkbox]),textarea,.form_input_info")
			if (input.length == 0) {
				return
			}
			console.log("fn:", key, "->", d.Id)
			fn_init(input, d)
			o.update_submit()
		})
	}

	o.install_fn_triggers = function(table) {
		for (key in o.fn_triggers) {
			var triggers = o.fn_triggers[key]
			for (var i=0; i<triggers.length; i++) {
				var d = triggers[i]
				o.install_fn_trigger(table, key, d)
			}
		}
	}

	o.add_fn_triggers = function(d) {
		function parse(s) {
			var re = RegExp(/#\w+/g)
			do {
				var m = re.exec(s)
				if (m) {
					var key = m[0].replace("#", "")
					key = o.resolve_key(key)
					var sign = key + "-" + d.Id
					if (o.fn_triggers_signs.indexOf(sign) >= 0) {
						continue
					} else {
						o.fn_triggers_signs.push(sign)
					}
					if (key in o.fn_triggers) {
						o.fn_triggers[key].push(d)
					} else {
						o.fn_triggers[key] = [d]
					}
				}
			} while (m)
		}
		parse(d.Function)
		for (var i=0; i<d.Args.length; i++) {
			parse(d.Args[i])
		}
	}

	o.resolve_key = function(key) {
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			d = o.form_data.form_definition.Inputs[i]
			if (d.Id == key) {
				return key
			}
			if (!d.Keys) {
				continue
			}
			for (var j=0; j<d.Keys.length; j++) {
				var key_def = d.Keys[j]
				var l = key_def.split("=")
				var keyname = l[0].replace(/^\s+/, "").replace(/\s+$/, "")
				if (keyname == key) {
					return d.Id
				}
			}
		}
		return key
	}

	function prepare_args(input, l) {
		var d = {}
		if (!l) {
			return d
		}
		for (var i=0; i<l.length; i++) {
			var s = l[i]
			var idx = s.indexOf("=")
			var key = s.slice(0, idx).replace(/\s+/g, "")
			var val = s.slice(idx+1, s.length).replace(/^\s+/, "")
			val = subst_refs(input, val)
			if (key in d) {
				// support multiple occurence of the same key
				if (!Array.isArray(d[key])) {
					d[key] = [d[key]]
				}
				d[key].push(val)
			} else {
				d[key] = val
			}
		}
		return d
	}

	o.form_to_data = function() {
		var t = o.form_data.form_definition.Outputs[0].Template
		var f = o.form_data.form_definition.Outputs[0].Format
		if (t) {
			return o.form_to_data_template(t)
		} else if (f == "dict") {
			return o.form_to_data_dict()
		} else if (f == "list") {
			return o.form_to_data_list()
		} else if (f == "list of dict") {
			return o.form_to_data_list_of_dict()
		} else if (f == "dict of dict") {
			return o.form_to_data_dict_of_dict()
		} else {
			return o.form_to_data_dict()
		}
	}

	o.get_val = function(td) {
		var input = td.find("input,textarea,div")
		if (input.is("div")) {
			var cbs = input.find("input[type=checkbox]")
			if (cbs.length > 0) {
				// list type
				var val = []
				cbs.each(function(){
					var _val = $(this).prop("acid")
					if (typeof(_val) === "undefined") {
						// skip the 'toggle all' checkbox
						return
					}
					if ($(this).prop("checked")) {
						val.push(_val)
					}
				})
				return val
			}
			return input.text()
		}
		var val = input.prop("acid")
		if ((typeof(val) === "undefined") || (typeof(input.attr("autocomplete")) === "undefined")) {
			val = input.val()
		}
		if (typeof(val) === "undefined") {
			console.log("get_val: unable to determine value of", td)
		}
		return val
	}

	o.get_option_data = function(td) {
		var input = td.find("input,textarea,div")
		return input.prop("option_data")
	}

	o.form_to_data_template = function(t) {
		var data = t
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			var d = o.form_data.form_definition.Inputs[i]
			var input_key_id = get_dict_id(d)
			var td = o.area.find("tr[iid="+d.Id+"] > [name=val]")
			if (td.length == 0) {
				continue
			}
			var re = RegExp("%%"+input_key_id+"%%", "g")
			data = data.replace(re, o.get_val(td))
		}
		return data
	}

	o.table_to_dict = function(table) {
		var data = {}
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			var d = o.form_data.form_definition.Inputs[i]
			var input_key_id = get_dict_id(d)
			if (!input_key_id) {
				continue
			}
			var td = table.find("tr[iid="+d.Id+"] > [name=val]")
			if (!td.is(":visible")) {
				if (typeof(o.options[input_key_id]) !== "undefined") {
					data[input_key_id] = o.options[input_key_id]
				}
			}
			if (td.length == 0) {
				continue
			}
			var val = o.get_val(td)
			if (d.Type == "list of string") {
				val = val.split(",")
			} else
			if (d.Type == "list of size") {
				val = val.split(",")
				val = convert_size(val)
			} else
			if ((d.Type == "boolean")) {
				val = convert_boolean(val)
			} else
			if ((d.Type == "string or integer") || (d.Type == "size") || (d.Type == "integer")) {
				val = convert_size(val, d.Unit)
			} else
			if (d.Type == "form") {
				val = o.sub_forms[d.Id].form_to_data()
			}
			data[input_key_id] = val

			if (d.Keys) {
				var option_data = o.get_option_data(td)
				for (var j=0; j<d.Keys.length; j++) {
					var key_def = d.Keys[j]
					var idx = key_def.indexOf("=")
					var keyname = key_def.slice(0, idx).replace(/^\s+/, "").replace(/\s+$/, "")
					var keyval = key_def.slice(idx+1, key_def.length).replace(/^\s+/, "").replace(/\s+$/, "")
					if (keyval.match(/#/)) {
						if (option_data) {
							data[keyname] = subst_refs_from_data(option_data, keyval)
						}
					} else {
						data[keyname] = keyval
					}
				}
			}
		}
		return data
	}

	o.form_to_data_dict = function() {
		return o.table_to_dict(o.area.children("table"))
	}

	o.form_to_data_dict_of_dict = function() {
		var data = {}
		var key_id = o.form_data.form_definition.Outputs[0].Key
		var embed_key = o.form_data.form_definition.Outputs[0].EmbedKey
		o.area.find(".form_group > table").each(function(){
			var _data = o.table_to_dict($(this))
			key = _data[key_id]
			if (embed_key != true) {
				delete(_data[key_id])
			}
			data[key] = _data
		})
		return data
	}

	o.form_to_data_list = function() {
		var data = []
		o.area.find(".form_group > table").each(function(){
			var _data = o.table_to_dict($(this))
			for (key in _data) {
				data.push(_data[key])
			}
		})
		if ((data.length == 1) && (data[0] == "")) {
			return []
		}
		return data
	}

	o.form_to_data_list_of_dict = function() {
		var data = []
		o.area.find(".form_group > table").each(function(){
			data.push(o.table_to_dict($(this)))
		})
		return data
	}

	// Allow callers to set their own submit_data()
	if (options.on_submit) {
		o.submit_data = options.submit_data
	}

	$.when(
		osvc.forms_loaded,
		osvc.user_loaded
	).then(function() {
		o.load()
	})
	return o
}

function form_results(divid, options) {
	o = {}
	o.options = options
	o.results_id = options.results_id
	o.wsh_id = "form_results_" + $("<span>").uniqueId().attr("id")
	o.timer = null

	if (typeof divid === "string") {
		o.div = $("#"+divid)
	} else {
		o.div = divid
	}

	o.render_results = function(results) {
		var document_scroll_pos = $(document).scrollTop()
		var flash_scroll_pos = osvc.flash.div.scrollTop()
		var output_area = $("<pre style='margin-top:1em'></pre>")
		o.div.empty()

		var status_title = $("<h2 data-i18n='forms.status'></h2>")
		o.div.append(status_title)
		if (results.status == "QUEUED") {
			spinner_add(o.div, i18n.t("forms."+results.status))
		} else if (results.status == "RUNNING") {
			spinner_add(o.div, i18n.t("forms."+results.status))
		} else if (results.status == "COMPLETED") {
			var e_status = $("<div class='icon_fixed_width' data-i18n='forms.COMPLETED'></div>")
			o.div.append(e_status)
			if (results.returncode == 0) {
				e_status.addClass("ok")
			} else {
				e_status.addClass("nok")
			}
			delete wsh[o.wsh_id]
		}

		if (results.log && "" in results.log) {
			o.render_output_results(results, output_area, "")
		}

		if (!results.outputs_order) {
			return
		}
		for (var i=0; i<results.outputs_order.length; i++) {
			var output_name = results.outputs_order[i]
			o.render_output_results(results, output_area, output_name)
		}

		o.div.append(output_area)
		o.div.i18n()
		$(document).scrollTop(document_scroll_pos)
		osvc.flash.div.scrollTop(flash_scroll_pos)
	}

	o.render_output_results = function(results, output_area, output_name) {
		var output_title = $("<h2>"+output_name+"</h2>")
		var log = results.log[output_name]
		o.div.append(output_title)

		if (log.length > 0) {
			var e_log = $("<div style='margin-bottom:0.5em'></div>")
			o.div.append(e_log)
		}

		for (var j=0; j<log.length; j++) {
			var level = log[j][0]
			var fmt = log[j][1]
			var d = log[j][2]
			if (level == 0) {
				var cl = "prewrap log_out"
			} else {
				var cl = "prewrap log_err"
			}
			for (key in d) {
				if (is_numeric(d[key]) || !d[key]) {
					var s = d[key]
				} else { 
					try {
						var _d = $.parseJSON(d[key])
						var s = "<br><pre>"+JSON.stringify(_d, null, 4)+"</pre>"
					} catch(e) {
						var s = d[key]
					}
				}
				var re = RegExp("%\\("+key+"\\)[sd]", "g")
				fmt = fmt.replace(re, "<b>"+s+"</b>")
			}
			var entry = $("<div class='icon_fixed_width'></div>")
			entry.addClass(cl)
			entry.html(fmt)
			e_log.append(entry)
		}

		if (output_name in results.request_data) {
			var result = results.request_data[output_name]
			try {
				result = JSON.stringify(result, null, 4)
			} catch(e) {}
			var log_result = $("<span data-i18n='forms.request_data' class='tag bgblack'></span>")
			$.data(log_result[0], "v", result)
			o.div.append(log_result)
			log_result.bind("click", function(e) {
				output_area.text($.data(this, "v"))
			})
		}
		if (output_name in results.outputs) {
			var result = results.outputs[output_name]
			try {
				result = JSON.stringify(result, null, 4)
			} catch(e) {}
			var log_result = $("<span data-i18n='forms.results' class='tag bgblack'></span>")
			$.data(log_result[0], "v", result)
			o.div.append(log_result)
			log_result.bind("click", function(e) {
				output_area.text($.data(this, "v"))
			})
		}
	}

	o.get_results = function() {
		// clear the timeout in case we're called from the event handler
		clearTimeout(o.timer)
		services_osvcgetrest("/form_output_results/%1", [o.results_id], "", function(jd) {
			o.render_results(jd)
			if (jd.status != "COMPLETED") {
				// schedule the next run
				o.timer = setTimeout(function(){
					o.get_results()
				}, 5000)
			}
		})
	}

	o.handle_results = function() {
		o.get_results()
		if (!o.options.async) {
			return
		}
		wsh[o.wsh_id] = function(data) {
			if (data.event != "form_output_results_change") {
				return
			}
			if (data.data.results_id != o.results_id) {
				return
			}
			o.get_results()
		}
	}

	o.load = function() {
		o.handle_results()
	}

	o.load()
	return o
}

// this file is loaded through require()
// init forms object upon load
osvc.forms = forms()
