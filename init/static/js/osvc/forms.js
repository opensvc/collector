function form_inputs_trigger (o) {
  form_inputs_mandatory(o)
  form_inputs_constraints(o)
  form_inputs_conditions(o)
  form_inputs_resize(o)
  form_inputs_functions(o)
  form_submit_toggle(o)
}

function refresh_select(e) {
  return function(data) {
    if (typeof(data) == "string") {
      e.find('option:selected').removeAttr('selected')
      e.val(data).attr('selected', true)
      e.find("option:contains('" + data + "')").each(function(){
        if ($(this).text() == data) {
          $(this).attr('selected', true);
        }
      });
    } else {
      e.find('option').remove()
      data = parse_data(data, e)
      for (i=0;i<data.length;i++) {
        if (!data[i]) {
          continue
        } else if (typeof(data[i]) == "string") {
          var _label = data[i]
          var _value = data[i]
        } else {
          var _value = data[i][0]
          var _label = data[i][1]
        }
        e.find('option').end().append("<option value='"+_value+"'>"+_label+"</option>")
      }
    }
    e.combobox()
    e.trigger('change')
  };
}

function refresh_div(e) {
  return function(data) {
    data = parse_data(data, e)
    if (data instanceof Array) {
      s = data.join("\\n")
    } else if (("data" in data) && (data["data"].length == 0)) {
      s = i18n.t("forms.not_found")
    } else {
      s = data
    }
    e.html("<pre>"+s+"</pre>")
    e.trigger('change')
  };
}

function parse_data(data, e) {
  if (typeof(data[i]) == "string") {
    return [data]
  }
  if (!data instanceof Array) {
    return [data]
  }
  if (data.length == 0) {
    return data
  }
  if (data[0] instanceof Array) {
    return data
  }
  if (!(data["data"] instanceof Array)) {
    data["data"] = [data["data"]]
  }
  var fmt = e.attr("trigger_fmt")
  var key = e.attr("trigger_id")
  if (key) {
    key = key.replace(/^#/, "")
  }
  if (key && !fmt) {
    fmt = "#"+key
  }
  if (fmt.length == 0) {
    try {
      keys = Object.keys(data["data"][0])
      fmt = "#"+keys[0]
    } catch(e) {
      fmt = false
    }
  }
  if (key && key.length == 0) {
    try {
      keys = Object.keys(data["data"][0])
      key = "#"+keys[0]
    } catch(e) {
      key = false
    }
  }
  if (e.get(0).tagName == 'SELECT' && key && fmt) {
    var _data = []
    for (i=0; i<data["data"].length; i++) {
      var _fmt = fmt
      for (k in data["data"][i]) {
        var reg = new RegExp("#"+k, "i")
        var val = data["data"][i][k]
        _fmt = _fmt.replace(reg, val)
      }
      _data.push([data["data"][i][key], _fmt])
    }
    return _data
  }
  if (fmt) {
    var _data = []
    for (i=0; i<data["data"].length; i++) {
      var _fmt = fmt
      for (k in data["data"][i]) {
        var reg = new RegExp("#"+k, "i")
        var val = data["data"][i][k]
        _fmt = _fmt.replace(reg, val)
      }
      _data.push(_fmt)
    }
    return _data
  }
  return data
}

function refresh_input(e) {
  return function(data) {
    data = parse_data(data, e)
    if (data.length == 0) {
      return
    }
    if (data instanceof Array) {
      s = data.join("\\n")
    } else {
      s = data
    }
    e.val(s)
    e.trigger('change')
  }
}

function refresh_textarea(e) {
  return function(data) {
    data = parse_data(data, e)
    h = 1.3
    if (data instanceof Array) {
      s = data.join("\\n")
      if (data.length > 1) {
        h = 1.3 * data.length
      }
    } else if (("data" in data) && (data["data"].length == 0)) {
      s = i18n.t("forms.not_found")
    } else {
      s = data
    }
    e.val(s)
    e.height(h+'em')
    e.trigger('change')
  };
}

function form_submit_toggle (o) {
  n = 0
  $(o).parents('table').first().find("tr").each(function(){
    if ($(this).hasClass("highlight_input") || $(this).hasClass("highlight_input1")) {
      $(o).parents('[name=container_head]').first().find("input[type=submit]").attr("disabled", "disabled")
      n++
      return
    }
  })
  if (n==0) {
    $(o).parents('[name=container_head]').first().find("input[type=submit]").removeAttr("disabled")
  }
}

function replace_references(s, index) {
  regex = /#\w+/g
  while (match = regex.exec(s)) {
    _match = match[0].replace(/^#/, "")
    if (_match == "user_id") {
      val = _self.id
    } else {
      id = 'forms_'+_match+"_"+index
      if ($('#'+id).length == 0) {
        continue
      }
      if ($('#'+id).get(0).tagName == 'SELECT') {
        val = $("#"+id+" option:selected").val()
      } else {
        val = $("#"+id).val()
      }
      if ((val == undefined) || (val == "")) {
        val = "ERR_REFERENCE_NOT_FOUND"
      }
    }
    re = new RegExp(match[0])
    s = s.replace(re, val)
  }
  return s
}

function form_input_functions (o, init) {
    l = $(o).attr("id").split("_")
    var index = l[l.length-1]
    var trigger_args = o.attr("trigger_args")
    if (!trigger_args) {
      return
    }
    l = o.attr("trigger_args").split("@@")
    var data = {}
    for (i=0; i<l.length; i++) {
      arg = replace_references(l[i], index)
      if (!arg) {
        break
      }
      parm = arg.substring(0, arg.indexOf("="))
      val = arg.substring(arg.indexOf("=")+1, arg.length)
      data[parm] = val
    }
    trigger_fn = replace_references(o.attr("trigger_fn"), index)
    if (!trigger_fn) { return; }
    if (trigger_fn[0] == "/") {
      url = "/init/rest/api"+trigger_fn
    } else {
      url = "/init/forms/call/json/"+trigger_fn
    }
    if (o.get(0).tagName == 'SELECT') {
      $.getJSON(url, data, refresh_select(o))
    } else if (o.get(0).tagName == 'INPUT') {
      $.getJSON(url, data, refresh_input(o))
    } else if (o.get(0).tagName == 'TEXTAREA') {
      $.getJSON(url, data, refresh_textarea(o))
    } else {
      $.getJSON(url, data, refresh_div(o))
    }
}

function form_inputs_functions (o) {
  l = $(o).attr("id").split("_")
  var index = l[l.length-1]
  l.pop()
  id = l.join("_").replace("forms_", "")
  $(o).parents('table').first().find("[trigger_args*=#"+id+"],[trigger_fn*=#"+id+"]").each(function(){
    form_input_functions($(this), false)
  })
  reg = new RegExp("#"+id)
  $(o).parents('table').first().find("[name=cond]").each(function(){
    if (!$(this).text().match(reg)) {
      return
    }
    var input = $(this).parent().find("[name^=forms_]").first()
    form_input_functions(input, false)
  })
}

function form_inputs_mandatory (o) {
  $(o).parents('table').first().find("[mandatory=mandatory]").each(function(){
    if ($(this).get(0).tagName == 'SELECT') {
      val = $(this).find("option:selected").val()
    } else {
      val = $(this).val()
    }
    if (val == undefined || val.length == 0) {
      $(this).parents('tr').first().addClass("highlight_input1")
    } else {
      $(this).parents('tr').first().removeClass("highlight_input1")
    }
  })
}

function form_inputs_resize (o) {
  var max = 0
  $(o).parents('table').first().find('input,textarea,select').each(function(){
    $(this).width('auto')
    w = $(this).width()
    if (w > max) { max = w }
  })
  $(o).parents('table').first().find('input,textarea,select').width(max+'px')
}

function form_inputs_constraints (o) {
  $(o).parents('tr').first().children("[name=constraint]").each(function(){
    var l = $(this).attr('id').split("_")
    var index = l[l.length-1]
    constraint = $(this).text()
    l = constraint.split(" ")
    if (l.length!=2) {
      return
    }
    op = l[0]
    val = $(this).siblings().children('input[name^=forms_],select[name^=forms_],textarea[name^=forms_]').val()
    if (op == ">") {
      tgt = l[1]
      if (1.0*val <= 1.0*tgt) {
        $(this).parents('tr').first().addClass("highlight_input")
        $(this).show()
        form_input_functions($(this), false)
        return
      }
    } else if (op == "match") {
      pattern = constraint.replace(/match */, "")
      re = new RegExp(pattern)
      if (!re.test(val)) {
        $(this).parents('tr').first().addClass("highlight_input")
        $(this).show()
        form_input_functions($(this), false)
        return
      }
    }
    $(this).parents('tr').first().removeClass("highlight_input")
    $(this).hide()
  })
};

function form_inputs_conditions (o) {
  $(o).parents('table').first().find("[name=cond]").each(function(){
    condition = $(this).text()
    var l = $(this).attr('id').split("_")
    var index = l[l.length-1]
    l.pop()
    prefix = l.join("_")
    if (condition.length==0) {
      return
    }
    ops = ["==", "!="]
    op = "not found"
    for (i=0;i<ops.length;i++) {
      l = condition.split(ops[i])
      if (l.length==2) {
        op = ops[i]
        left = $.trim(l[0])
        right = $.trim(l[1])
      }
    }
    if (op == "not found") {
      return
    }
    if (left.charAt(0) == "#"){
      left = left.substr(1);
      v_left = $('#'+prefix+"_"+left+"_"+index).val()
      if (!v_left) { v_left = "" }
    } else {
      v_left = left
    }
    if (right.charAt(0) == "#"){
      right = right.substr(1);
      v_right = $('#'+prefix+"_"+right+"_"+index).val()
      if (!v_right) { v_right = "" }
    } else {
      v_right = right
    }
    if (v_right == "empty") {
      v_right = ""
    }
    match = false
    if (op == "==" && v_left == v_right) { match=true }
    else if (op == "!=" && v_left != v_right) { match=true }

    if (!match) {
      $(this).siblings().children('input[name^=forms_],select[name^=forms_],textarea[name^=forms_]').val("")
      $(this).parent('tr').hide()
      return
    }
    $(this).parent('tr').show()
  })
};


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

	o.event_handler = function(data) {
		if (!data.event) {
			return
		}
		if (data.event == "forms_change") {
			o.load()
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
	o.fn_triggers = {}
	o.fn_triggers_signs = []
	o.fn_trigger_last = {}
	o.cond_triggers = {}
	o.div = $("#"+divid)

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

	o.mangle_form_data = function() {
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			var d = o.form_data.form_definition.Inputs[i]
			if (d.Candidates == "__node_selector__") {
				console.log("mangle form definition: swich __node_selector__ to rest GET /users/self/nodes")
				o.form_data.form_definition.Inputs[i].Function = "/users/self/nodes"
				o.form_data.form_definition.Inputs[i].Args = ["props = nodename", "meta = 0", "limit = 0"]
				o.form_data.form_definition.Inputs[i].Candidates = null
			}
			if (d.Candidates == "__service_selector__") {
				console.log("mangle form definition: swich __node_selector__ to rest GET /users/self/services")
				o.form_data.form_definition.Inputs[i].Function = "/users/self/services"
				o.form_data.form_definition.Inputs[i].Args = ["props = svc_name", "meta = 0", "limit = 0"]
				o.form_data.form_definition.Inputs[i].Candidates = null
			}
			if (d.Default == "__user_primary_group__") {
				console.log("mangle form definition: swich __user_primary_group__ to rest GET /users/self/primary_group")
				o.form_data.form_definition.Inputs[i].Function = "/users/self/primary_group"
				o.form_data.form_definition.Inputs[i].Args = ["props = role"]
				o.form_data.form_definition.Inputs[i].Default = null
			}
		}
	}

	o.render_form_mode = function() {
		var area = $("<div name='form_area' class='container_head'></div>")
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
		div.append(area)
		o.render_display()
		o.div.empty()
		o.div.append(div)
	}

	o.render_edit = function() {
		if (o.options.editable == false) {
			return ""
		}
		var a = $("<a class='edit16' style='position:absolute;top:2px;right:2px;z-index:400'></a>")
		a.attr("title", i18n.t("forms.edit"))
		a.bind("click", function(){
			$(this).siblings("a.nok").show()
			$(this).hide()
			o.render_form()
		})
		return a
	}

	o.render_cancel = function() {
		if (o.options.editable == false) {
			return ""
		}
		var a = $("<a class='nok' style='display:none;position:absolute;top:2px;right:2px;z-index:400'></a>")
		a.attr("title", i18n.t("forms.cancel"))
		a.bind("click", function(){
			$(this).siblings("a.edit16").show()
			$(this).hide()
			o.render_display()
		})
		return a
	}

	o.render_display = function() {
		console.log("here", o.options.data)
		if (typeof(o.options.data) == "string") {
			o.area.text(o.options.data)
			o.area.addClass("pre")
			return
		}
		if (o.options.digest) {
			o.render_display_digest()
		} else {
			o.render_display_normal()
		}
	}

	o.render_display_digest_header = function() {
		var line = $("<tr></tr>")
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			var d = o.form_data.form_definition.Inputs[i]
			if (d.Hidden == true) {
				continue
			}
			if (d.DisplayInDigest == false) {
				continue
			}
			var cell = $("<th></th>")
			cell.text(d.DisplayModeLabel)
			if (i == 0) {
				cell.addClass("comp16")
			}
			line.append(cell)
		}
		o.area_table.append(line)
	}

	o.render_display_digest_line = function(data, key) {
		var line = $("<tr></tr>")
		if (key) {
			var key_id = o.form_data.form_definition.Outputs[0].Key
		}
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			var d = o.form_data.form_definition.Inputs[i]
			if (d.Hidden == true) {
				continue
			}
			if (d.DisplayInDigest == false) {
				continue
			}
			var cell = $("<td></td>")
			var content = ""

			if (key && (d.Id == key_id)) {
				content = key
				cell.addClass("b")
			} else if (typeof(data) === "string") {
				content = data
				if(d.Css) {
					cell.addClass(d.Css)
				}
				if(d.LabelCss) {
					cell.addClass(d.LabelCss)
				}
			} else if (d.Id in data) {
				content = data[d.Id]
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
			if (i>0) {
				o.area.append("<hr>")
			}
			o.area.append(o.render_display_normal_dict(l[i]))
		}
	}

	o.render_display_normal_dict = function(data) {
		var table = $("<table></table>")
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			var d = o.form_data.form_definition.Inputs[i]
			if (d.Hidden == true) {
				continue
			}
			var line = $("<tr></tr>")
			var label = $("<td style='white-space:nowrap'></td>")
			var value = $("<td></td>")
			label.text(d.DisplayModeLabel)
			if(d.LabelCss) {
				label.addClass(d.LabelCss)
			}
			if(d.Css) {
				value.addClass(d.Css)
			}
			line.append(label)
			line.append(value)
			if (d.Id in data) {
				var content = data[d.Id]
			}
			if (content == "") {
				content = "-"
			}
			if (!o.options.detailled && d.DisplayModeTrim && (content.length > d.DisplayModeTrim)) {
				content = content.slice(0, d.DisplayModeTrim/3) + "..." + content.slice(content.length-d.DisplayModeTrim/3*2, content.length)
			}
			value.text(content)
			table.append(line)
		}
		return table
	}

	o.render_form_group = function(data) {
		var table = $("<table></table>")
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			var d = o.form_data.form_definition.Inputs[i]
			var line = $("<tr></tr>")
			var label = $("<td style='white-space:nowrap'></td>")
			var value = $("<td name='val'></td>")
			var help = $("<td class='help'></td>")
			help.attr("title", d.Help)
			line.attr("iid", d.Id)
			if (d.ExpertMode == true) {
				line.hide()
			}
			if (d.Hidden == true) {
				line.hide()
			}
			label.text(d.Label)
			if(d.LabelCss) {
				label.addClass(d.LabelCss)
			}
			line.append(label)
			line.append(value)
			line.append(help)
			if ((typeof(data) === "undefined") || !(d.Id in data)) {
				if (d.Default == "__user_email__") {
					var content = _self.email
				} else if (d.Default == "__user_primary_group__") {
					var content = _self.primary_group
				} else if (d.Default == "__user_phone_work__") {
					var content = _self.phone_work
				} else if (d.Default == "__user_name__") {
					var content = _self.first_name + " " + _self.last_name
				} else if (d.Default) {
					var content = d.Default
				} else {
					var content = ""
				}
			} else if (typeof(data) === "string") {
				var content = data
			} else if (d.Id in data) {
				var content = data[d.Id]
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
			} else if (d.Candidates && (d.Candidates instanceof Array)) {
				var input = o.render_select(d, content)
			} else if (d.Function) {
				var input = o.render_select_rest(d, content)
			} else {
				var input = o.render_input(d, content)
			}

			if (d.Condition && d.Condition.match(/#/)) {
				o.add_cond_triggers(d)
			}
			o.install_mandatory_trigger(input, d)
			o.install_constraint_trigger(input, d)

			value.append(input)
			table.append(line)
		}
		o.install_fn_triggers(table)
		o.install_cond_triggers(table)
		return table
	}

	o.render_del_group = function() {
		var div = $("<div class='del16 clickable' style='text-align:center'></div>")
		div.text(i18n.t("forms.del_group"))
		div.bind("click", function() {
			$(this).prev("hr").remove()
			$(this).next("table").remove()
			$(this).remove()
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
		var div = $("<div class='icon fa-unlock clickable' style='text-align:center'></div>")
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

	o.render_add_group = function() {
		var div = $("<div class='add16 clickable' style='text-align:center'></div>")
		div.text(i18n.t("forms.add_group"))
		o.area.append(div)
		div.bind("click", function() {
			var ref = o.area.children("table").last()
			var remove = o.render_del_group()
			var hr = $("<hr>")
			var data = o.table_to_dict(ref)
			var new_group = o.render_form_group(data)
			hr.insertAfter(ref)
			remove.insertAfter(hr)
			new_group.insertAfter(remove)
		})
	}

	o.render_form_list = function() {
		o.area.empty()
		if (!o.options.data || o.options.data.length == 0) {
			o.area.append(o.render_form_group({}))
		} else {
			for (var i=0; i<o.options.data.length; i++) {
				o.area.append(o.render_del_group())
				o.area.append(o.render_form_group(o.options.data[i]))
			}
		}
		o.render_add_group()
		o.render_expert_toggle()
		o.render_submit()
		o.render_result()
	}

	o.render_form_dict_of_dict = function() {
		o.area.empty()
		var key_id = o.form_data.form_definition.Outputs[0].Key
		var i = 0
		for (key in o.options.data) {
			i++
			o.options.data[key][key_id] = key
			o.area.append(o.render_del_group())
			o.area.append(o.render_form_group(o.options.data[key]))
		}
		if (i == 0) {
			o.area.append(o.render_del_group())
			o.area.append(o.render_form_group({}))
		}
		o.render_add_group()
		o.render_expert_toggle()
		o.render_submit()
		o.render_result()
	}

	o.render_form_dict = function() {
		o.area.empty().append(o.render_form_group(o.options.data))
		o.render_expert_toggle()
		o.render_submit()
		o.render_result()
	}

	o.render_form = function() {
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
	}

	o.render_result = function() {
		var result = $("<div style='padding:1em'></div>")
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
		services_osvcputrest("R_FORM", [o.form_data.id], "", _data, function(jd) {
			if (jd.error.length == 0) {
				o.result.html("<div class='ok'>"+i18n.t("forms.success")+"</div>")
			} else {
				o.result.html("<div class='nok'>"+i18n.t("forms.error")+"</div>")
			}
			if (jd.info) {
				if (typeof(jd.info) === "string") {
					o.result.append("<p class='icon fa-info-circle'>"+jd.info+"</p>")
				} else {
					for (var i=0; i<jd.info.length; i++) {
						o.result.append("<p class='icon fa-info-circle'>"+jd.info[i]+"</p>")
					}
				}
			}
			if (jd.error) {
				if (typeof(jd.error) === "string") {
					o.result.append("<p class='icon fa-exclamation-triangle'>"+jd.error+"</p>")
				} else {
					for (var i=0; i<jd.error.length; i++) {
						o.result.append("<p class='icon fa-exclamation-triangle'>"+jd.error[i]+"</p>")
					}
				}
			}
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
			_data.var_value = JSON.stringify(data)
		}
		services_osvcpostrest("R_COMPLIANCE_RULESET_VARIABLE", [o.options.rset_id, o.options.var_id], "", _data, function(jd) {
			if (jd.error && (jd.error.length > 0)) {
				o.result.html(services_error_fmt(jd))
				return
			}
			try {
				o.options.data = $.parseJSON(jd.data[0].var_value)
			} catch(e) {
				o.options.data = jd.data[0].var_value
			}
			o.result.html("<div class='ok'>"+i18n.t("forms.success")+"</div>")
		},
		function(xhr, stat, error) {
			o.result.html(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.submit_output = function(output, data) {
		if (output.Dest == "compliance variable") {
			o.submit_output_compliance(data)
		} else {
			console.log("Output " + output.Dest + " not supported client-side")
			o.need_submit_form_data = true
		}
	}

	o.render_submit = function() {
		var button = $("<input type='button' style='margin:1em'>")
		button.attr("value", i18n.t("forms.submit"))
		o.area.append(button)

		button.bind("click", function() {
			var data = o.form_to_data()
			for (var i=0; i<o.form_data.form_definition.Outputs.length; i++) {
				var output = o.form_data.form_definition.Outputs[i]
				o.submit_output(output, data)
			}
			if (o.need_submit_form_data == true) {
				o.need_submit_form_data = false
				o.submit_form_data(data)
			}
		})
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
		var textarea = $("<textarea class='oi pre' style='padding:0.4em;width:17em;height:8em'>")
		if (d.ReadOnly == true) {
			textarea.prop("disabled", true)
		}
		textarea.val(content)
		if (d.Function && fn_has_refs(d)) {
			o.add_fn_triggers(d)
		}
		return textarea
	}
	o.render_input = function(d, content) {
		var input = $("<input class='oi'>")
		if (d.ReadOnly == true) {
			input.prop("disabled", true)
		}
		input.val(content)
		return input
	}
	o.render_select = function(d, content) {
		var input = $("<input class='oi aci'>")
		if (d.ReadOnly == true) {
			input.prop("disabled", true)
		}
		var opts = []
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
					var acid = _d.Value
					content = _d.Label
				}
			}
		}
		input.autocomplete({
			mustMatch: true,
			autoFocus: true,
			source: opts,
			minLength: 0,
			select: function(event, ui) {
				$(this).prop("acid", ui.item.id)
				$(this).change()
			}
		})
		if (content && content.length > 0) {
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
		if (fn_has_refs(d)) {
			o.add_fn_triggers(d)
			return input
		}
		fn_init_autocomplete(input, d, content)
		return input
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

	function fn_init_autocomplete(input, d, content) {
		if (d.Function.match(/^\//)) {
			return rest_init_autocomplete(input, d, content)
		} else {
			return jsonrpc_init_autocomplete(input, d, content)
		}
	}

	function fn_callback(input, d, args, data, content) {
		if (typeof(data) === "string") {
			if (input.hasClass("form_input_info")) {
				input.text(data)
			} else {
				input.val(data)
			}
			input.change()
			return
		}
		var opts = []
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
				var props = args.props.split(",")
				for (var j=0; j<props.length; j++) {
					var prop = props[j]
					var re = RegExp("#"+prop, "g")
					label = label.replace(re, _d[prop])
					value = value.replace(re, _d[prop])
				}
				opts.push({
					"id": value,
					"label": label
				})
				if (content && (value == content)) {
					var acid = value
					content = label
				}
			} else {
				opts.push({
					"id": _d[args.props],
					"label": _d[args.props]
				})
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
			try { input.autocomplete("destroy") } catch(e) {}
			input.val("")
			input.removeProp("acid")
			input.autocomplete({
				mustMatch: true,
				autoFocus: true,
				source: opts,
				minLength: 0,
				select: function(event, ui) {
					$(this).prop("acid", ui.item.id)
					$(this).change()
				}
			})
			if (opts.length == 1) {
				input.removeClass("aci")
			} else {
				input.addClass("aci")
			}
			if (input.is(":visible") && (opts.length > 0)) {
				input.val(opts[0].label)
				input.prop("acid", opts[0].id)
			}
		}
		if (content && content.length > 0) {
			input.prop("acid", acid)
			input.val(content)
		}
		input.change()
	}

	function jsonrpc_init_autocomplete(input, d, content) {
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

	function rest_init_autocomplete(input, d, content) {
		var args = prepare_args(input, d.Args)
		var fn = subst_refs(input, d.Function)
		if (fn.match(/\/\//) || fn.match(/\/undefined\//) || fn.match(/\/$/)) {
			console.log("cancel rest get on", fn, ": missing parameters")
			return
		}
		var key = input.attr("id")
		if (!key) {
			input.uniqueId()
			var key = input.attr("id")
		}
		var sign = fn_sign(fn, args)
		console.log(key, sign)
		if ((key in o.fn_trigger_last) && (o.fn_trigger_last[key] == sign)) {
			console.log("cancel rest get on", fn, ": same as last call")
			return
		}
		o.fn_trigger_last[key] = sign
		services_osvcgetrest("/init/rest/api"+fn, "", args, function(jd) {
			fn_callback(input, d, args, jd.data, content)
		})
	}

	function fn_sign(fn, args) {
		s = fn
		for (key in args) {
			s += "-"+args[key]
		}
		return s
	}

	function subst_refs(input, s) {
		var table = input.parents("table").first()
		var re = RegExp(/#\w+/g)
		var _s = s

		do {
			var m = re.exec(s)
			if (m) {
				var key = m[0].replace("#", "")
				var td = table.find("tr[iid="+key+"] td[name=val]")
				var val = o.get_val(td)
				var re1 = RegExp("#"+key, "g")
				_s = _s.replace(re1, val)
			}
		} while (m)
		return _s
	}

	o.install_constraint_trigger = function(input, d) {
		if (!d.Constraint) {
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
			if (o.div.find(".constraint_violation").filter(":visible").length == 0) {
				o.div.find("input[type=button]").prop("disabled", false)
			} else {
				o.div.find("input[type=button]").prop("disabled", true)
			}
		}
	}

	o.install_mandatory_trigger = function(input, d) {
		if (d.Mandatory != true) {
			return
		}
		trigger(input)
		input.bind("keyup change", function() {
			trigger($(this))
		})
		function trigger(e) {
			if (e.val() == "") {
				e.addClass("constraint_violation")
			} else {
				e.removeClass("constraint_violation")
			}
			if (o.div.find(".constraint_violation").filter(":visible").length == 0) {
				o.div.find("input[type=button]").prop("disabled", false)
			} else {
				o.div.find("input[type=button]").prop("disabled", true)
			}
		}
	}

	o.hide_input = function(table, d, initial) {
		var tr = table.find("[iid="+d.Id+"]")
		if (!initial && !tr.is(":visible")) {
			console.log("hide", d.Id, "already not visible", tr.parents("table"))
			return
		}
		console.log("hide", d.Id)
		tr.hide()
		tr.find("[name=val]").children("input,textarea").val("").prop("acid", "").trigger("change")
	}

	o.show_input = function(table, d) {
		var tr = table.find("[iid="+d.Id+"]")
		if (tr.is(":visible")) {
			return
		}
		console.log("show", d.Id)
		tr.show(500)
		var input = tr.find("[name=val]").children("input,textarea,.form_input_info")
		if (d.Function && fn_has_refs(d)) {
			fn_init_autocomplete(input, d)
			var data = $.data(input[0])
			if (data.autocomplete && data.autocomplete.options.source.length > 0) {
				input.val(data.autocomplete.options.source[0].label)
				input.prop("acid", data.autocomplete.options.source[0].id)
				input.change()
			}
		}
	}

	o.install_cond_trigger = function(table, key, d) {
		console.log("install cond trigger", key, "->", d.Id)

		var cell = table.find("[iid="+key+"]").children("[name=val]").children("input,textarea")
		trigger(cell, true)
		cell.bind("blur change", function() {
			trigger($(this))
		})
		function trigger(input, initial) {
			var val = o.get_val(input.parent())
			var tr = input.parents("table").first().find("[iid="+d.Id+"]")

			if (d.Condition.match(/!=/)) {
				var eq = false
				var ref = d.Condition.split("!=")[1]
			} else if (d.Condition.match(/==/)) {
				var eq = true
				var ref = d.Condition.split("==")[1]
			} else {
				console.log(d.Id, "unsupported condition operator:", d.Condition)
			}

			// strip
			ref = ref.replace(/^\s+/, "").replace(/\s+$/, "")

			console.log("condition:", key, "->", d.Id, val, eq, ref)
			if (val != "") {
				if (!eq) {
					if (ref == "empty") {
						// foo != empty
						o.show_input(table, d)
					} else if (val != ref) {
						// foo != bar
						o.show_input(table, d)
					} else {
						// foo != foo
						o.hide_input(table, d, initial)
					}
				} else {
					if (ref == "empty") {
						// foo == empty
						o.hide_input(table, d, initial)
					} else if (val == ref) {
						// foo == foo
						o.show_input(table, d)
					} else {
						// foo == bar
						o.hide_input(table, d, initial)
					}
				}
			} else {
				if (!eq) {
					if (ref == "empty") {
						// empty != empty
						o.hide_input(table, d, initial)
					} else {
						// empty != foo
						o.show_input(table, d)
					}
				} else {
					if (ref == "empty") {
						// empty == empty
						o.show_input(table, d)
					} else {
						// empty == foo
						o.hide_input(table, d, initial)
					}
				}
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
		cell.bind("blur change", function() {
			var input = table.find("[iid="+d.Id+"]").find("input,textarea,.form_input_info")
			if (input.length == 0) {
				return
			}
			console.log("fn:", key, "->", d.Id)
			fn_init_autocomplete(input, d)
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

	function prepare_args(input, l) {
		var d = {}
		for (var i=0; i<l.length; i++) {
			var s = l[i]
			var idx = s.indexOf("=")
			var key = s.slice(0, idx).replace(/\s+/g, "")
			var val = s.slice(idx+1, s.length).replace(/^\s+/, "")
			val = subst_refs(input, val)
			d[key] = val
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
		var input = td.find("input,textarea")
		var val = input.prop("acid")
		if (typeof(val) === "undefined") {
			val = input.val()
		}
		if (typeof(val) === "undefined") {
			console.log("get_val: unable to determine value of", td)
		}
		return val
	}

	o.form_to_data_template = function(t) {
		var data = t
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			var d = o.form_data.form_definition.Inputs[i]
			var td = o.area.find("tr[iid="+d.Id+"] > [name=val]")
			if (td.length == 0) {
				continue
			}
			var re = RegExp("%%"+d.Id+"%%", "g")
			data = data.replace(re, o.get_val(td))
		}
		return data
	}

	o.table_to_dict = function(table) {
		var data = {}
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			var d = o.form_data.form_definition.Inputs[i]
			var td = table.find("tr[iid="+d.Id+"] > [name=val]")
			if (td.length == 0) {
				continue
			}
			data[d.Id] = o.get_val(td)
		}
		return data
	}

	o.form_to_data_dict = function() {
		return o.table_to_dict(o.area.children("table"))
	}

	o.form_to_data_dict_of_dict = function() {
		var data = {}
		var key_id = o.form_data.form_definition.Outputs[0].Key
		o.area.children("table").each(function(){
			var _data = o.table_to_dict($(this))
			key = _data[key_id]
			data[key] = _data
		})
		return data
	}

	o.form_to_data_list = function() {
		var data = []
		o.area.children("table").each(function(){
			var _data = o.table_to_dict($(this))
			for (key in _data) {
				data.push(_data[key])
			}
		})
		return data
	}

	o.form_to_data_list_of_dict = function() {
		var data = []
		o.area.children("table").each(function(){
			data.push(o.table_to_dict($(this)))
		})
		return data
	}

	$.when(osvc.forms_loaded,osvc.user_groups_loaded).then(function() {
		o.load()
	})
	return o
}

