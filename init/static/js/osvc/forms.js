const userLocale =
  navigator.languages && navigator.languages.length
    ? navigator.languages[0]
    : navigator.language;

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

function randomId() {
	return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
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
				console.log("mangle form definition: switch __node_selector__ to rest GET /users/self/nodes")
				o.form_data.form_definition.Inputs[i].Function = "/users/self/nodes"
				o.form_data.form_definition.Inputs[i].Args = ["props = nodename", "meta = 0", "limit = 0"]
				o.form_data.form_definition.Inputs[i].Candidates = null
			}
			if (d.Candidates == "__service_selector__") {
				console.log("mangle form definition: switch __node_selector__ to rest GET /users/self/services")
				o.form_data.form_definition.Inputs[i].Function = "/users/self/services"
				o.form_data.form_definition.Inputs[i].Args = ["props = svcname", "meta = 0", "limit = 0"]
				o.form_data.form_definition.Inputs[i].Candidates = null
			}
			if (d.Default == "__user_primary_group__") {
				console.log("mangle form definition: switch __user_primary_group__ to rest GET /users/self/primary_group")
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

	let getUrlFunc = function(input, func) {
		return function(params) {
			let fn = subst_refs(input, func)
			if (fn.match(/^\//) && fn.match(/\/\//)) {
				console.log("missing data in rest path")
				return
			}
			if (fn.match(/\/undefined\//) || fn.match(/\/$/) || fn.match(/#/)) {
				console.log("cancel rest get on", fn, ": missing parameters")
				return
			}
			return services_getaccessurl(fn)
		}
	}

	let getProcessResultFunc = function(input, d) {
		return function (data) {
			input.html(null)
			let id_prop = get_id_prop(input, d)
			let l = data.data.map(function(data){
				ndata = {
					option_data: data,
					id: subst_refs_from_data(data, "#"+id_prop)
				}
				if ("Format" in d) {
					ndata.text = subst_refs_from_data(data, d.Format)
				} else {
					ndata.text = ndata.id
				}
				return ndata
			})
			let more
			if ("meta" in data) {
				more = (data.meta.total > (data.meta.offset + data.meta.count))
			} else {
				more = false
			}
			return {
				results: l,
				pagination: {
					more: more
				}
			}
		}
	}

	function input_has_default(d) {
		return is_valid_default(d.Default)
	}
	function is_valid_default(v) {
		if (is_numeric(v) && (v == 0)) {
			return true
		}
		if (v) {
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
				var ret = o.eval_conditions(d, data)
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
			if (o.options.data instanceof Array) {
				for (var i=0; i<o.options.data.length; i++) {
					o.render_display_digest_line(o.options.data[i])
				}
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
				var ret = o.eval_conditions(d, data)
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
			let d = o.form_data.form_definition.Inputs[i]
			var input_key_id = get_dict_id(d)
			var line = $("<tr></tr>")
			var label = $("<th style='white-space:nowrap'></th>")
			var value = $("<td name='val'></td>")
			line.attr("iid", d.Id)
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
			let content = ""
			if ((typeof(data) === "undefined") || (is_dict(data) && !(input_key_id in data))) {
				if (d.Default == "__user_email__") {
					content = _self.email
				} else if (d.Default == "__user_primary_group__") {
					content = _self.primary_group
				} else if (d.Default == "__user_phone_work__") {
					content = _self.phone_work
				} else if (d.Default == "__user_name__") {
					content = _self.first_name + " " + _self.last_name
				} else if (typeof d.Default !== "undefined") {
					content = d.Default
				} else if (d.Type == "form") {
					content = undefined
				} else {
					content = ""
				}
			} else if (d.var_class=="raw" || (typeof(data) === "string") || (typeof(data) === "number")) {
				content = data
			} else if (is_dict(data) && input_key_id in data) {
				content = data[input_key_id]
			} else {
				content = ""
			}

			let input
			if (d.Type == "date") {
				input = o.render_date(d, content)
			} else if (d.Type == "datetime") {
				input = o.render_datetime(d, content)
			} else if (d.Type == "time") {
				input = o.render_time(d, content)
			} else if (d.Type == "info") {
				input = o.render_info(d, content)
			} else if (d.Type == "text") {
				input = o.render_text(d, content)
			} else if (d.Type == "boolean") {
				input = o.render_boolean(d, content)
			} else if (d.Type == "checklist") {
				input = o.render_checklist(d, content)
			} else if (d.Type == "form") {
				input = o.render_sub_form(d, content)
			} else {
				input = o.render_input(d, content)
			}

			o.set_input_width(d, input)

			o.add_cond_triggers(d)

			value.append(input)
			table.append(line)
		}
		o.install_mandatory_triggers(table)
		o.install_constraint_triggers(table)
		o.install_cond_triggers(table)
		o.install_fn_triggers(table)
		return table
	}

	o.set_input_width = function(d, input) {
		let width = o.input_width(d)
		if (width) {
			input.width(width)
		}
		if (o.form_data.form_definition.MinWidth) {
			input.css({"min-width": o.form_data.form_definition.MinWidth})
		}
	}

	o.input_width = function(d) {
		return d.Width || o.form_data.form_definition.Width
	}

	o.render_move_group = function() {
		var div = $("<div class='icon_fixed_width fa-bars form_tool movable hidden'></div>")
		return div
	}

	o.render_del_group = function() {
		var div = $("<div class='icon_fixed_width del16 form_tool nowrap hidden'></div>")
		div.text(i18n.t("forms.del_group"))
		div.bind("click", function() {
			$(this).parent().remove()
			o.set_form_group_tools_visibility()
		})
		return div
	}

	o.init_events = function() {
		// to call when inputs are displayed
		console.log("send initial change events")
		o.area.find("[iid]").find("select,input:not([type=checkbox]),textarea,.form_input_info").change()
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
		var div = $("<button name='add_group' class='button_div icon_fixed_width add16'>")
		div.text(i18n.t("forms.add_group"))
		div.css({"margin-top": "1em"})
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
			if (ref.length == 1) {
				form_group.insertAfter(ref)
			} else {
				o.area.prepend(form_group)
			}
			o.init_sortable()
			o.init_events()
			o.reinit_select2()
			o.set_form_group_tools_visibility()
		})
	}

	o.set_form_group_tools_visibility = function() {
		// show remove/move group tools if the area has more than min_groups group
		let groups = o.area.children(".form_group")
		let min = o.form_data.form_definition.Outputs[0].MinEntries
		let max = o.form_data.form_definition.Outputs[0].MaxEntries
		if (typeof(min) === "undefined") {
			min = 0
		}
		let floor = (groups.length <= min)
		let ceil = ((typeof(max) !== "undefined") && (groups.length >= max))
		if (floor) {
			groups.children(".form_tool").addClass("hidden")
		} else {
			groups.children(".form_tool").removeClass("hidden")
		}
		if (ceil) {
			o.area.children("button[name=add_group]").addClass("hidden")
		} else {
			o.area.children("button[name=add_group]").removeClass("hidden")
		}
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
		o.render_submit()
		o.render_test()
		o.render_result()
		o.set_form_group_tools_visibility()
		o.init_sortable()
		o.init_events()
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
		o.render_submit()
		o.render_test()
		o.render_result()
		o.init_sortable()
		o.init_events()
	}

	o.render_form_dict = function() {
		o.area.empty().append(o.render_form_group(o.options.data))
		o.render_submit()
		o.render_test()
		o.render_result()
		o.init_events()
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
		o.reinit_select2()
		o.update_submit()
	}

	o.reinit_select2 = function() {
		// select2 added when the element is not attached to the DOM are not rendered
		o.area.find("select[data-select2-id]:visible,input[data-select2-id]:visible").each(function(){
			let w = $(this)
			let options = $.data(this, "s2options");
			let initialized = w.prop("initialized")
			od = o.get_option_data(w.parents("td"))
			if (!initialized) {
				w.select2(options)
				w.prop("initialized", true)
			}
		})
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
		let _data = {}
		if (typeof(data) === "string") {
			_data.var_value = data
		} else {
			for (let key in data) {
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
		let _data = {}
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
		let path = "/tags/%1"
		let params = [o.options.tag_id]
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
		let button = $("<button class='icon_fixed_width fa-code button_div'>")
		o.test_tool = button
		button.text(i18n.t("forms.test"))
		button.css({"margin-top": "1em"})
		o.area.append(button)

		button.bind("click", function() {
			let data = o.form_to_data()
			let data_title = $("<h2>"+i18n.t("forms.test_title")+"</h2>")
			let data_pre = $("<pre style='text-align:left'>"+JSON.stringify(data, null, 4)+"</pre>")
			let render_title = $("<h2>"+i18n.t("forms.test_render_title")+"</h2>")
			let render_div = $("<div></div>")
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
		let button = $("<button class='icon_fixed_width fa-save button_div'>")
		o.submit_tool = button
		button.text(i18n.t("forms.submit"))
		button.css({"margin-top": "1em"})
		o.area.append(button)

		button.bind("click", function() {
			width = button.width()
			if (o.submit_disabled()) {
				o.area.find(".constraint_violation,.mandatory_violation").effect("highlight", 600)
				return
			}
			button.prop("disabled", true)
			timeout = o.form_data.form_definition.ResubmitDelay || 2000
			delay = 1000
			tick = function() {
				setTimeout(function() {
					if (timeout > 0) {
						timeout -= delay
						button.width(width)
						button.text(Math.floor(timeout/1000) + "s")
						tick()
					} else {
						button.width("auto")
						button.text(i18n.t("forms.submit"))
						button.prop("disabled", false)
					}
				}, delay)
			}
			tick()
			o.result.empty()
			let data = o.form_to_data()
			o.submit_action(data)
		})
	}

	o.submit_action = function(data) {
		o.need_submit_form_data = false
		o.results = {}
		for (let i=0; i<o.form_data.form_definition.Outputs.length; i++) {
			let output = o.form_data.form_definition.Outputs[i]
			o.submit_output(output, data)
		}
		if (o.need_submit_form_data == true) {
			o.need_submit_form_data = false
			o.submit_form_data(data)
		}
	}

	o.render_time = function(d, content) {
		let input = $("<input class='oi'>")
		if (d.ReadOnly == true) {
			input.prop("disabled", true)
		}
		input.val(content)
		input.uniqueId()
		input.timepicker()
		return input
	}
	o.render_datetime = function(d, content) {
		let input = $("<input class='oi'>")
		if (d.ReadOnly == true) {
			input.prop("disabled", true)
		}
		input.val(content)
		input.uniqueId()
		input.datetimepicker({dateFormat:'yy-mm-dd'})
		return input
	}
	o.render_date = function(d, content) {
		let input = $("<input class='oi'>")
		if (d.ReadOnly == true) {
			input.prop("disabled", true)
		}
		input.val(content)
		input.uniqueId()
		input.datepicker({dateFormat:'yy-mm-dd'})
		return input
	}
	o.render_info = function(d, content) {
		let div = $("<div class='form_input_info' style='padding:0.4em'>")
		div.text(content)
		if (d.Function && fn_has_refs(d)) {
			o.add_fn_triggers(d)
		}
		return div
	}
	o.render_text = function(d, content) {
		let textarea = $("<textarea class='oi pre' style='padding:0.4em;min-width:17em;min-height:8em'>")
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
		let input = $("<input class='oi'>")
		if (d.ReadOnly == true) {
			input.prop("disabled", true)
		}
		if (d.Type == "password") {
			input.prop("type", "password")
		}
		input.val(content)
		input.prop("acid", content)
		input.prop("placeholder", d.Placeholder)
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
		let input = $("<select class='oi aci' />")

		// prepare candidates
		let data = []
		let hasDefault = input_has_default(d)
		if (!hasDefault && d.DisableAutoDefault && !d.Multiple) {
			// dummy entry selected as a placeholder
			data.push({
				"id": "",
			})
		}
		for (let i=0; i<d.Candidates.length; i++) {
			let _d = d.Candidates[i]
			if (typeof(_d) === "string") {
				data.push({
					"id": _d,
					"text": _d
				})
			} else if (("Label" in _d) && ("Value" in _d)) {
				data.push({
					"id": _d.Value,
					"text": _d.Label
				})
			}
		}

		let options = {
			tags: d.Multiple || !d.StrictCandidates,
			dropdownParent: o.div,
			minimumResultsForSearch: 3,
			selectionCssClass: "ois2selection",
			dropdownCssClass: "ois2dropdown",
			width: o.input_width(d) || "100%",
			data: data
		}
		if (d.Multiple) {
			options.multiple = true
		}
		if (d.ReadOnly == true) {
			options.disabled = true
		}
		if (!hasDefault && d.DisableAutoDefault) {
			options.placeholder = d.Placeholder || "Select a candidate"
			//options.allowClear = true
		}

		// save options
		$.data(input[0], "s2options", options)
		input.select2(options)

		o.select_static_set_content(input, d, content)
		return input
	}

	o.select_static_set_content = function(input, d, content) {
		if (is_valid_default(content)) {
			input.val(content)
			input.change()
		} else {
			o.select_static_set_autodef(input, d)
		}
	}

	o.select_static_set_autodef = function(input, d) {
		if (d.DisableAutoDefault) {
			input.val(null)
			input.change()
		}
	}

	let get_id_prop = function(input, d) {
		let s
		if ("Value" in d) {
			s = d.Value
		} else {
			let props = prepare_args(input, d.Args).props
			if ((typeof(props) === "string")) {
				s = props.split(",")[0]
			} else {
				return get_dict_id(d)
			}
		}
		return s.replace("#", "")
	}

	o.render_select_rest = function(d, content) {
		let input = $("<select class='oi aci' />")
		let fmt = function(data) {
			if (data.id == "") {
				return d.Placeholder || "Select a candidate"
			}
			return data.text || data.id
		}
		let transport = function (params, success, failure) {
			let args = prepare_args(input, d.Args, params.data)
			return $.ajax({
				type: "GET",
				url: params.url,
				data: args,
				dataType: "json",
				contentType: "application/json; charset=utf-8",
				error: failure,
				success: success
			})
		}

		let options = {
			ajax: {
				delay: d.SearchDelay || 100,
				dataType: "json",
				contentType: "application/json; charset=utf-8",
				url: getUrlFunc(input, d.Function),
				processResults: getProcessResultFunc(input, d),
				transport: transport
			},
			tags: d.Multiple || !d.StrictCandidates,
			language: userLocale,
			allowClear: d.AllowClear,
			placeholder: d.Placeholder || "Select a candidate",
			minimumInputLength: d.SearchMinimumInputLength || 0,
			dropdownParent: o.div,
			selectionCssClass: "ois2selection",
			dropdownCssClass: "ois2dropdown",
			width: o.input_width(d) || "100%",
			templateResult: fmt,
			templateSelection: fmt
		}
		if (d.Multiple) {
			options.multiple = true
		}
		if (d.ReadOnly == true) {
			options.disabled = true
		}

		// save options
		$.data(input[0], "s2options", options)
		input.select2(options)

		o.add_fn_triggers(d)
		o.select_rest_set_content(input, d, content)

		return input
	}

	o.select_rest_set_autodef = function(input, d) {
		if (d.DisableAutoDefault == true) {
			console.log("autodef", d.Id, "skip")
			data = $.data(input[0])
			let options = data.s2options
			input.select2(options)
			return
		}
		let url = getUrlFunc(input, d.Function)()
		if (!url) {
			return
		}
		let id_prop = get_id_prop(input, d)
		let initArgs = prepare_args(input, d.Args)
		if (!("filters" in initArgs)) {
			initArgs.filters = []
		}
		if (d.CheckOnLoad != "all") {
			initArgs.limit = 1
		}
		initOpts = {
			type: "GET",
			url: url,
			data: initArgs,
			dataType: "json",
			contentType: "application/json; charset=utf-8",
			error: function(e){console.log("ajax error:", d.Id, url, e)}
		}
		$.ajax(initOpts).then(function(data){
			let normData = getProcessResultFunc(input, d)(data)
			if (normData.results.length == 0) {
				data = $.data(input[0])
				let options = data.s2options
				input.select2(options)
				return
			}
			normData.results.forEach(function(e) {
				let option = new Option(e.text, e.id, true, true)
				$.data(option, "data", e)
				input.append(option)
				input.trigger({
					type: "select2:select",
					params: {
						data: e,
					}
				})
			})
			input.trigger("change")

			data = $.data(input[0])
			let options = data.s2options
			input.select2(options)
		})
	}

	o.select_rest_set_autodef_from_default_func = function(input, d) {
		let url = getUrlFunc(input, d.DefaultFunction)()
		if (!url) {
			return
		}
		let id_prop = get_id_prop(input, d)
		let initArgs = prepare_args(input, d.DefaultArgs || d.Args)
		if (!("filters" in initArgs)) {
			initArgs.filters = []
		}
		initOpts = {
			type: "GET",
			url: url,
			data: initArgs,
			dataType: "json",
			contentType: "application/json; charset=utf-8",
			error: function(e){console.log("ajax error:", d.Id, url, e)}
		}
		$.ajax(initOpts).then(function(data){
			let normData = getProcessResultFunc(input, d)(data)
			if (normData.results.length == 0) {
				data = $.data(input[0])
				let options = data.s2options
				input.select2(options)
				return
			}
			normData.results.forEach(function(e) {
				let option = new Option(e.text, e.id, true, true)
				$.data(option, "data", e)
				input.append(option)
				input.trigger({
					type: "select2:select",
					params: {
						data: e,
					}
				})
			})
			input.trigger("change")

			data = $.data(input[0])
			let options = data.s2options
			input.select2(options)
		})
	}

	o.select_rest_set_content = function(input, d, content) {
		if (d.DefaultFunction) {
			o.select_rest_set_autodef_from_default_func(input, d)
			return
		}
		if ((typeof(content) === "undefined") || (content == "")) {
			o.select_rest_set_autodef(input, d)
			return
		}
		let url = getUrlFunc(input, d.Function)()
		if (!url) {
			return
		}
		let id_prop = get_id_prop(input, d)
		let initArgs = prepare_args(input, d.Args)
		if (Array.isArray(content)) {
			// in case content has element beyond the 1st page
			initArgs.limit = 0
		} else {
			initArgs.search = content
			initArgs.search_props = ""
		}
		initOpts = {
			type: "GET",
			url: url,
			data: initArgs,
			dataType: "json",
			contentType: "application/json; charset=utf-8",
			error: function(e){console.log("ajax error:", d.Id, url, e)},
		}
		$.ajax(initOpts).then(function(data){
			console.log("def", d.Id, id_prop, data)
			data = getProcessResultFunc(input, d)(data)
			if (data.results.length == 0) {
				return
			}
			let strcontent = []
			content.forEach(function(e) {
				strcontent.push(""+e)
			})
			data.results.forEach(function(e){
				if (Array.isArray(content)) {
					if (strcontent.indexOf(""+e.id) < 0) {
						return
					}
				} else {
					if (e.id != strcontent) {
						return
					}
				}
				let option = new Option(e.text, e.id, true, true)
				$.data(option, "data", e)
				input.append(option)
				input.trigger({
					type: "select2:select",
					params: {
						data: e,
					}
				})
			})
			input.trigger("change")

			data = $.data(input[0])
			let options = data.s2options
			input.select2(options)
		})
	}


	o.render_boolean = function(d, content) {
		let id = randomId()
		let div = $("<div class='formbool'>")
		let input = $("<input type='checkbox' id='"+id+"' class='btn-check formbool-input' autocomplete='off'>")
		let label = $("<label class='btn btn-secondary formbool-label' for='"+id+"'>")
		div.append([input, label])
		if (d.ReadOnly == true) {
			input.prop("disabled", true)
		}
		if (content == true) {
			label.text(i18n.t("action_menu.yes"))
			label.addClass("btn-success").removeClass("btn-secondary")
			input.prop("checked", true)
			input.prop("acid", true)
		} else {
			label.text(i18n.t("action_menu.no"))
			label.addClass("btn-secondary").removeClass("btn-success")
			input.prop("acid", false)
		}
		input.bind("change", function(){
			if ($(this).prop("checked")) {
				label.text(i18n.t("action_menu.yes"))
				label.addClass("btn-success").removeClass("btn-secondary")
				$(this).prop("acid", true)
			} else {
				label.text(i18n.t("action_menu.no"))
				label.addClass("btn-secondary").removeClass("btn-success")
				$(this).prop("acid", false)
			}
		})
		return div
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
		let div = $("<div></div>")
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
			for (let i=0; i<d.Args.length; i++) {
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
		if ((d.Function.match(/^\//)) || (d.Function.match(/^http/))) {
			if (input.is("select.select2-hidden-accessible")) {
				o.select_rest_set_content(input, d, content)
			} else {
				return rest_init(input, d, content, fn_callback)
			}
		} else {
			if (input.is("select.select2-hidden-accessible")) {
				o.select_static_set_content(input, d, content)
			}else {
				return jsonrpc_init(input, d, content, fn_callback)
			}
		}
	}

	function checklist_callback(input, d, args, data, content) {
		if (data.length == 0) {
			input.empty()
			return
		}

		// add a 'toggle all' master checkbox
		let line = $("<div style='padding:0.2em'></div>")
		let master_cb = $("<input type='checkbox' class='ocb'>")
		let master_cb_label = $("<label></label>")
		let e_label = $("<span class='grayed' style='padding:0 0.3em'></span>")

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
			let state = $(this).prop("checked")
			$(this).parent().siblings().children("input[type=checkbox]").prop("checked", state)
			o.update_submit()
		})

		// ck value can be a string, ex: id from a rest get are strings
		str_content = content.map(function(el) {
			return ""+el
		})

		for (let i=0; i<data.length; i++) {
			let _d = data[i]
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
			let line = $("<div style='padding:0.2em'></div>")
			let cb = $("<input type='checkbox' class='ocb'>")
			let cb_label = $("<label></label>")
			let e_label = $("<span style='padding:0 0.3em'></span>")
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
		let opts = []
		let acid = content
		for (let i=0; i<data.length; i++) {
			let _d = data[i]
			if (typeof(_d) === "string") {
				opts.push({
					"id": _d,
					"text": _d
				})
			} else if (("Format" in d) && ("Value" in d)) {
				var label = d.Format
				var value = d.Value
				label = subst_refs_from_data(_d, label)
				value = subst_refs_from_data(_d, value)
				opts.push({
					"id": value,
					"text": label,
					"option_data": _d
				})
			} else {
				var prop = args.props.split(",")[0]
				var value = subst_refs_from_data(_d, "#"+prop)
				opts.push({
					"id": value,
					"text": value,
					"option_data": _d
				})
			}
		}

		function opts_to_text(opts) {
			if (!opts) {
				return ""
			}
			let l = []
			for (let i=0; i<opts.length; i++) {
				l.push(opts[i].text)
			}
			return l.join("\n")
		}

		if (input.hasClass("form_input_info")) {
			input.text(opts_to_text(opts))
		} else if (input.is("textarea")) {
			input.val(opts_to_text(opts))
		}
		if (content && (content.length > 0)) {
			input.prop("acid", acid)
			if (d.Format != d.Value) {
				for (let j=0; j<opts.length; j++) {
					if (opts[j].id != content) {
						continue
					}
					input.prop("option_data", content)
					input.val(opts[j].text)
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
		let args = prepare_args(input, d.Args)
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
		let args = prepare_args(input, d.Args)
		let fn = subst_refs(input, d.Function)
		if (fn.match(/^\//) && fn.match(/\/\//)) {
			console.log("missing data in rest path")
			return
		}
		if (fn.match(/\/undefined\//) || fn.match(/\/$/) || fn.match(/#/)) {
			console.log("cancel rest get on", fn, ": missing parameters")
			return
		}
		let key = input.attr("id")
		if (!key) {
			input.uniqueId()
			key = input.attr("id")
		}
		let sign = fn_sign(fn, args)
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
		let re = RegExp(/#[\w\.]+/g)
		let _s = s
		do {
			m = re.exec(s)
			if (m) {
				let key = m[0].replace("#", "")
				let keys = key.split(".")
				let val = data
				for (let i=0; i<keys.length; i++) {
					if (keys[i] in val) {
						val = val[keys[i]]
					}
				}
				let re1 = RegExp("#"+key)
				let t = typeof val
				if ((t === "number") || (t === "string") || (t === "boolean")) {
					_s = _s.replace(re1, val)
				}
			}
		} while (m)
		return _s
	}

	function subst_refs(input, s) {
		let table = input.parents("table").first()
		let data = o.table_to_dict(table)
		return subst_refs_from_data(data, s)
	}

	o.install_constraint_triggers = function(table) {
		for (let i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			let d = o.form_data.form_definition.Inputs[i]
			if (d.Type == "form") {
				continue
			}
			let input = table.find("[iid="+d.Id+"] > [name=val]").children("div,textarea,input")
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
		input.bind("keyup change", function() {
			trigger($(this))
		})
		function trigger(e) {
			let val = o.get_converted_val(d, input)
			let c = o.parse_constraint(d)
			if (val == "" && !d.Mandatory) {
				e.removeClass("constraint_violation")
			} else {
				let ret = o.eval_constraint(c, val)

				console.log("constraint:", d.Id, val , d.Constraint, "=>", ret)
				if (!ret) {
					e.addClass("constraint_violation")
				} else {
					e.removeClass("constraint_violation")
				}
			}
			o.update_submit()
		}
	}

	o.parse_constraint = function(d) {
		let ret = {}
		if (d.Constraint.match(/^>/)) {
			ret.op = ">"
		} else if (d.Constraint.match(/^</)) {
			ret.op = "<"
		} else if (d.Constraint.match(/^>=/)) {
			ret.op = ">="
		} else if (d.Constraint.match(/^<=/)) {
			ret.op = "<="
		} else if (d.Constraint.match(/^==/)) {
			ret.op = "=="
		} else if (d.Constraint.match(/^match\s+/)) {
			ret.op = "match"
		}

		if (ret.op) {
			ret.ref = d.Constraint.split(ret.op)[1]
		} else {
			ret.ref = d.Constraint
			ret.op = "match"
		}

		// strip
		ret.ref = ret.ref.replace(/^\s+/, "").replace(/\s+$/, "")
		return ret
	}

	o.eval_constraint = function(c, val) {
		if (typeof val === "undefined") {
			return false
		}
		else if (typeof val === "number") {
			if (c.op == "match") {
				val = "" + val
			} else {
				try { c.ref = parseInt(c.ref) } catch(e) {}
			}
		}
		else if (typeof val === "boolean") {
			c.ref = (c.ref.toLowerCase() == 'true')
		}
		else if (typeof val === "string") {
			if (c.op == "match") {
				c.ref = "" + c.ref
			} else {
				return false
			}
		}
				console.log(c, val, typeof(val))
		if (((val != "") && (val != null)) || (typeof val === "number")) {
			if (c.op == ">") {
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
			} else if (c.op == ">=") {
				if (c.ref == "empty") {
					// foo >= empty
					return false
				} else if (val >= c.ref) {
					// foo >= foo
					return true
				} else {
					// foo >= bar
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
			} else if (c.op == "<=") {
				if (c.ref == "empty") {
					// foo <= empty
					return false
				} else if (val <= c.ref) {
					// foo <= foo
					return true
				} else {
					// foo <= bar
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
			} else if (c.op == "match") {
				let re = RegExp(c.ref)
				return re.exec(""+val)
			}
		} else {
			if (c.op == "==") {
				if (c.ref == "empty") {
					// empty == empty
					return true
				} else {
					// empty == foo
					return false
				}
			} else {
				return false
			}
		}
	}

	o.install_mandatory_triggers = function(table) {
		for (let i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			let d = o.form_data.form_definition.Inputs[i]
			let input = table.find("[iid="+d.Id+"] > [name=val]").children("div,textarea,input,select")
			o.install_mandatory_trigger(input, d)
		}
	}

	o.update_candidates_violation = function(d, input, opts) {
		if (!d.StrictCandidates) {
			return
		}

		function is_candidate(v, opts) {
			for (let i=0; i<opts.length; i++) {
				if (opts[i].text==v) {
					return true
				}
			}
			return false
		}

		let v = o.get_val(input)
		console.log("update_candidates_violation:", v, opts)
		if (is_candidate(v, opts)) {
			input.removeClass("candidates_violation")
		} else {
			input.addClass("candidates_violation")
		}
		o.update_submit()
	}

	o.update_submit = function() {
		if (o.div.find(".constraint_violation,.mandatory_violation,.candidates_violation").parents("tr[iid]:visible").length == 0) {
			o.enable_submit()
		} else {
			o.disable_submit()
		}
		if (o.options.parent_form) {
			o.options.parent_form.update_submit()
		}
	}

	o.submit_disabled = function() {
		return o.submit_tool.hasClass("nok")
	}

	o.violations = function() {
		let m = {
			constraint: [],
			mandatory: [],
			candidates: [],
		}
		o.div.find(".constraint_violation").parents("tr[iid]:not(.hidden)").each(function() {
			m["constraint"].push($(this).attr("iid"))
		})
		o.div.find(".mandatory_violation").parents("tr[iid]:not(.hidden)").each(function() {
			m["mandatory"].push($(this).attr("iid"))
		})
		o.div.find(".candidates_violation").parents("tr[iid]:not(.hidden)").each(function() {
			m["candidates"].push($(this).attr("iid"))
		})
		return m
	}

	o.violations_report = function() {
		let m = o.violations()
		console.log("violations:", m)
		div = $("<div>")
		let t = $("<h4>")
		t.text("violations")
		div.append(t)
		fmt = (cat) => {
			let l = m[cat]
			if (!l || l.length == 0) {
				return
			}
			let t = $("<h5>")
			let d = o.get_input_definition(id)
			t.text(cat)
			div.append(t)
			let u = $("<ul>")
			div.append(u)
			for (let i=0; i<l.length; i++) {
				let e = $("<li>")
				e.text(o.get_input_definition(l[i]).Label)
				u.append(e)
			}
		}
		fmt("constraint")
		fmt("mandatory")
		fmt("candidates")
		return div
	}

	o.disable_submit = function() {
		if (!o.submit_tool) {
			return
		}
		o.submit_tool.addClass("nok").removeClass("fa-save")
		//o.result.empty().append(o.violations_report())
	}

	o.enable_submit = function() {
		if (!o.submit_tool) {
			return
		}
		o.submit_tool.addClass("fa-save").removeClass("nok")
		//o.result.empty()
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
		function trigger() {
			let val = o.get_val(input)
			if (typeof(val) === "undefined") {
				input.addClass("mandatory_violation")
			} else if (val == "") {
				input.addClass("mandatory_violation")
			} else if ((val instanceof Array) && (val.length == 0)) {
				input.addClass("mandatory_violation")
			} else {
				input.removeClass("mandatory_violation")
			}
			o.update_submit()
		}
		trigger()
		input.bind("keyup change", function(e) {
			trigger()
		})
	}

	o.hide_input = function(table, d, initial) {
		let tr = table.find("[iid="+d.Id+"]")
		if (!initial && tr.hasClass("hidden")) {
			console.log("hide", d.Id, "already not visible")
		} else if (!d.Hidden) {
			console.log("hide", d.Id)
			tr.addClass("hidden")
		}
		if (d.Id in o.cond_triggers) {
			let triggers = o.cond_triggers[d.Id]
			for (let i=0; i<triggers.length; i++) {
				if (o.div.find("tr[iid="+triggers[i].Id+"]").hasClass("hidden")) {
					continue
				}
				o.hide_input(table, triggers[i], initial)
			}
		}
		o.update_submit()
	}

	o.show_input = function(table, d) {
		let tr = table.find("[iid="+d.Id+"]")
		if (!tr.hasClass("hidden")) {
			console.log("show", d.Id, "already visible")
		} else if (!d.Hidden) {
			console.log("show", d.Id)
			tr.removeClass("hidden")
		}
		let inputs = tr.find("[name=val]").children("select,input,textarea,.form_input_info")
		inputs.each(function(){
			input = $(this)
			if (input.is("select.select2-hidden-accessible")) {
				let data = $.data(input[0])
				let options = data.s2options
				//input.select2("destroy")
				input.select2(options)
				input.change()
			} else if (d.Function && fn_has_refs(d)) {
				var data = $.data(input)
				if (data.autocomplete && data.autocomplete.options.source.length > 0) {
					input.val(data.autocomplete.options.source[0].text)
					input.prop("acid", data.autocomplete.options.source[0].id)
					input.change()
				}
			} else if ((!d.Type || d.Type == "string" || d.Type == "integer" || d.Type == "time" || d.Type == "date" || d.Type == "datetime") && input_has_default(d)) {
				input.val(d.Default)
				input.prop("acid", d.Default)
				input.change()
			}
		})
		o.update_submit()
	}

	o.install_cond_trigger = function(table, key, d) {
		console.log("install cond trigger", key, "->", d.Id)

		var line = table.find("[iid="+key+"]")
		if (line.length == 0) {
			var input_id = o.resolve_key(key)
			var line = table.find("[iid="+input_id+"]")
		}
		var head = line.children("[name=val]")
		var cell = head.find("select,input,textarea")
		trigger(true)
		cell.bind("change", function() {
			trigger(false)
		})
		function trigger(initial) {
			let data
			if (initial) {
				data = o.options.data || {}
			} else {
				data = o.form_to_data()
			}
			if (Array.isArray(data) && (data.length > 0)) {
				let i = table.parent().prevAll(".form_group").length
				data = data[i]
			}
			let ret = o.eval_conditions(d, data)
			console.log("conditions:", d.Id+":", d.Condition, "->", ret, "with data", data)
			if (ret) {
				o.show_input(table, d)
			} else {
				o.hide_input(table, d, initial)
			}
		}
	}

	o.parse_condition = function(cond) {
		if (cond.match(/!=/)) {
			var op = "!="
		} else if (cond.match(/==/)) {
			var op = "=="
		} else if (cond.match(/NOT IN/)) {
			var op = "NOT IN"
		} else if (cond.match(/IN/)) {
			var op = "IN"
		} else if (cond.match(/>/)) {
			var op = ">"
		} else if (cond.match(/</)) {
			var op = "<"
		} else {
			console.log("unsupported condition operator:", cond)
		}

		var ref = cond.split(op)[1]
		var id = cond.split(op)[0]

		// strip
		id = id.replace(/^\s+/, "").replace(/\s+$/, "").replace(/^#/, "")
		ref = ref.replace(/^\s+/, "").replace(/\s+$/, "")
		return {"id": id, "op": op, "ref": ref}
	}

	o.eval_conditions = function(d, data) {
		if (typeof(d.Condition) === "string") {
			let c = o.parse_condition(d.Condition)
			return o.eval_condition(c, data)
		}
		if (Array.isArray(d.Condition)) {
			for (var i=0; i<d.Condition.length; i++) {
				let cond = d.Condition[i]
				let c = o.parse_condition(cond)
				if (o.eval_condition(c, data) == false) {
					console.log(" - condition:", c, "data:", data, "=> false")
					return false
				}
				console.log(" - condition:", c, "data:", data, "=> true")
			}
			return true
		}
		return false
	}

	o.eval_condition = function(c, data) {
		let val = data[c.id]
		if (typeof val === "number") {
			try {
				c.ref = parseInt(c.ref)
			} catch(e) {}
		}
		else if (typeof val === "boolean") {
			c.ref = (c.ref.toLowerCase() == 'true')
		}
		if ((val != "") && (val != null) && (typeof(val) !== "undefined")) {
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
		let re = RegExp(/#\w+/g)
		let repl = cond => {
			do {
				var m = re.exec(cond)
				if (m) {
					var key = m[0].replace("#", "")
					ids = o.resolve_keys(key)
					for (var i=0; i<ids.length; i++) {
						let id = ids[i]
						if (id in o.cond_triggers) {
							o.cond_triggers[id].push(d)
						} else {
							o.cond_triggers[id] = [d]
						}
					}
				}
			} while (m)
		}
		if (!d.Condition) {
			return
		}
		if ((typeof(d.Condition) === "string") && d.Condition.match(/#/)) {
			repl(d.Condition)
		}
		if (Array.isArray(d.Condition)) {
			for (var i=0; i<d.Condition.length; i++) {
				repl(d.Condition[i])
			}
		}
	}

	o.install_fn_trigger = function(table, key, d) {
		if (key == d.Id) {
			return
		}
		console.log("install fn trigger", key, "->", d.Id)
		var cell = table.find("[iid="+key+"]").children("[name=val]").children("select,input,textarea")
		cell.bind("change", function() {
			var input = table.find("[iid="+d.Id+"]").find("select,input:not([type=checkbox]),textarea,.form_input_info")
			if (input.length == 0) {
				return
			}
			console.log("fn:", key, "->", d.Id)
			input.val(null)
			input.change()
			if (input.is("select.select2-hidden-accessible")) {
				// clear the Option elements cached in DOM,
				// so the option_data is not lost when returning to a cached option.
				input.html(null)
			}
			fn_init(input, d, d.Default)
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
					ids = o.resolve_keys(key)
					for (var i=0; i<ids.length; i++) {
						let id = ids[i]
						var sign = id + "-" + d.Id
						if (o.fn_triggers_signs.indexOf(sign) >= 0) {
							continue
						} else {
							o.fn_triggers_signs.push(sign)
						}
						if (id in o.fn_triggers) {
							o.fn_triggers[id].push(d)
						} else {
							o.fn_triggers[id] = [d]
						}
					}
				}
			} while (m)
		}
		parse(d.Function)
		parse(d.DefaultFunction)
		let args = []
		if (Array.isArray(d.Args)) {
			args = args.concat(d.Args)
		}
		if (Array.isArray(d.DefaultArgs)) {
			args = args.concat(d.DefaultArgs)
		}
		if (Array.isArray(d.Condition)) {
			args = args.concat(d.Condition)
		} else {
			parse(d.Condition)
		}
		for (var i=0; i<args.length; i++) {
			parse(args[i])
		}
	}

	o.resolve_key = function(key) {
		let ids = o.resolve_keys(key)
		try {
			return ids[0]
		} catch(e) {
			return
		}
	}

	o.resolve_keys = function(key) {
		let ids = []
		for (let i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			let d = o.form_data.form_definition.Inputs[i]
			if (d.Key == key) {
				ids.push(d.Id)
				continue
			}
			if (d.Id == key) {
				ids.push(d.Id)
				continue
			}
			if (d.Keys) {
				for (var j=0; j<d.Keys.length; j++) {
					var key_def = d.Keys[j]
					var l = key_def.split("=")
					var keyname = l[0].replace(/^\s+/, "").replace(/\s+$/, "")
					if (keyname == key) {
						ids.push(d.Id)
						break
					}
				}
			}
		}
		return ids
	}

	function prepare_args(input, l, s2params) {
		var d = {
			filters: []
		}
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
		if (typeof(s2params) !== "undefined") {
			let page = 1
			let limit = 10
			if (s2params.page != null) {
				page = s2params.page
			}
			d.meta = 1
			d.limit = limit
			d.offset = (page-1) * limit
			d.search = s2params.term
		}
		return d
	}

	o.form_to_data = function() {
		if (!o.form_data) {
			return
		}
		let t = o.form_data.form_definition.Outputs[0].Template
		let f = o.form_data.form_definition.Outputs[0].Format
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
		let input
		if (td.is("input,textarea,div,select")) {
			input = td
		} else {
			input = td.children("input,textarea,div,select")
		}
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
		if (input.is("select.select2-hidden-accessible")) {
			val = input.select2("data")
			if (input.prop("multiple") == true) {
				return val.map(x => x.id)
			} else if (val.length > 0) {
				return val[0].id
			} else {
				return undefined
			}
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
		var input = td.children("input,textarea,div,select")
		if (input.is("select.select2-hidden-accessible")) {
			input = input.filter("select.select2-hidden-accessible")
			let val = input.select2("data")
			if (input.prop("multiple") == true) {
				return val.map(x => x.option_data)
			} else if (val.length > 0) {
				return val[0].option_data
			} else {
				return undefined
			}
		}
		return input.prop("option_data")
	}

	o.form_to_data_template = function(t) {
		let data = t
		for (let i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			let d = o.form_data.form_definition.Inputs[i]
			let input_key_id = get_dict_id(d)
			let td = o.area.find("tr[iid="+d.Id+"] > [name=val]")
			if (td.length == 0) {
				continue
			}
			let re = RegExp("%%"+input_key_id+"%%", "g")
			data = data.replace(re, o.get_val(td))
		}
		return data
	}

	o.get_converted_val = function(formDef, td) {
			let val = o.get_val(td)
			if (formDef.Type == "list of string") {
				val = val.split(",")
			} else
			if (formDef.Type == "list of size") {
				val = val.split(",")
				val = convert_size(val)
			} else
			if ((formDef.Type == "boolean")) {
				val = convert_boolean(val)
			} else
			if ((formDef.Type == "string or integer") || (formDef.Type == "size") || (formDef.Type == "integer")) {
				val = convert_size(val, formDef.Unit)
			} else
			if (formDef.Type == "form") {
				val = o.sub_forms[formDef.Id].form_to_data()
			}
			return val
	}

	o.get_input_definition = function(id) {
		for (let i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			let inputDef = o.form_data.form_definition.Inputs[i]
			if (inputDef.Id == id) {
				return inputDef
			}
		}
	}

	o.table_to_dict = function(table) {
		let data = {}
		var kv = function(key_def, option_data) {
			let idx = key_def.indexOf("=")
			let keyname = key_def.slice(0, idx).replace(/^\s+/, "").replace(/\s+$/, "")
			let keyval = key_def.slice(idx+1, key_def.length).replace(/^\s+/, "").replace(/\s+$/, "")
			if (keyval.match(/#/)) {
				if (option_data) {
					keyval = subst_refs_from_data(option_data, keyval)
				}
			}
			return {k: keyname, v: keyval}
		}
		for (let i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			let inputDef = o.form_data.form_definition.Inputs[i]
			let input_key_id = get_dict_id(inputDef)
			if (!input_key_id) {
				continue
			}
			let td = table.find("tr[iid="+inputDef.Id+"] > [name=val]")
			if (!td.is(":visible")) {
				if (input_key_id in data) {
					continue
				}
				if (typeof(o.options[input_key_id]) !== "undefined") {
					data[input_key_id] = o.options[input_key_id]
				}
				if (!inputDef.Hidden) {
					continue
				} else if (inputDef.Condition && !o.eval_conditions(inputDef, data)) {
					// all depending inputs must be located before
					continue
				}
				// Explicitely hidden inputs have their value embedded
			}
			if (td.length == 0) {
				continue
			}
			let val = o.get_converted_val(inputDef, td)

			if (inputDef.Multiple) {
				if (inputDef.Keys) {
					//
					// {
					//   <id>: [
					//     { <k>: <v> },
					//     { <k>: <v> },
					//     ...
					//   ]
					// }
					//
					let option_data = o.get_option_data(td)
					data[input_key_id] = []
					for (let k=0; k<val.length; k++) {
						let od = option_data[k]
						let rd = {}
						for (let j=0; j<inputDef.Keys.length; j++) {
							let d = kv(inputDef.Keys[j], od)
							rd[d.k] = d.v
						}
						data[input_key_id].push(rd)
					}
				} else {
					//
					// {
					//   <id>: [
					//     <v>,
					//     <v>,
					//     ...
					//   ]
					// }
					//
					data[input_key_id] = val
				}
			} else {
				if (inputDef.Keys) {
					//
					// {
					//   <k>: <v>,
					//   <k>: <v>,
					//   ...
					// }
					//
					data[input_key_id] = val
					let option_data = o.get_option_data(td)
					for (let j=0; j<inputDef.Keys.length; j++) {
						let d = kv(inputDef.Keys[j], option_data)
						data[d.k] = d.v
					}
				} else {
					//
					// {
					//   <id>: <v>
					// }
					//
					data[input_key_id] = val
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
