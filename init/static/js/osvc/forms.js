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
		var data = {
			"limit": "0",
			"meta": "0",
			"props": "form_definition,form_name,id,form_type"
		}
		services_osvcgetrest("R_FORMS", "", data, function(jd) {
			for (var i=0; i<jd.data.length; i++) {
				var d = jd.data[i]
				o.data[d.form_name] = d
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
	o.div = $("#"+divid)

	o.load = function() {
		if (!o.options.form_name) {
			o.div.html(i18n.t("forms.form_name_not_in_options"))
			return
		}
		if ((o.options.form_name == "") || (o.options.form_name == "empty")) {
			return
		}
		o.form_data = osvc.forms.data[o.options.form_name]
		if (!o.form_data) {
			o.div.html(i18n.t("forms.form_def_not_found"))
			return
		}
		if (o.options.display_mode) {
			o.render_display_mode()
		} else {
			o.render_form_mode()
		}
	}

	o.render_form_mode = function() {
		var area = $("<div name='form_area'></div>")
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
		o.div.empty().append(div)
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
		o.area_table = $("<table></table>")
		o.area.empty().append(o.area_table)
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			var d = o.form_data.form_definition.Inputs[i]
			if (d.Hidden == true) {
				continue
			}
			var line = $("<tr></tr>")
			var label = $("<td style='white-space:nowrap' class='b'></td>")
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
			if (d.Id in o.options.data) {
				var content = o.options.data[d.Id]
			}
			if (content == "") {
				content = "-"
			}
			if (!o.options.detailled && d.DisplayModeTrim && (content.length > d.DisplayModeTrim)) {
				content = content.slice(0, d.DisplayModeTrim/3) + "..." + content.slice(content.length-d.DisplayModeTrim/3*2, content.length)
			}
			value.text(content)
			o.area_table.append(line)
		}
	}

	o.render_form_group = function(data) {
		var table = $("<table></table>")
		for (var i=0; i<o.form_data.form_definition.Inputs.length; i++) {
			var d = o.form_data.form_definition.Inputs[i]
			var line = $("<tr></tr>")
			var label = $("<td style='white-space:nowrap' class='b'></td>")
			var value = $("<td name='val'></td>")
			var help = $("<td class='help'></td>")
			help.attr("title", d.Help)
			line.attr("iid", d.Id)
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
			if (typeof(data) === "undefined") {
				var content = ""
			} else if (typeof(data) === "string") {
				var content = data
			} else if (d.Id in data) {
				var content = data[d.Id]
			} else {
				var content = ""
			}
			if (d.Type == "date") {
				value.append(o.render_date(d, content))
			} else if (d.Type == "datetime") {
				value.append(o.render_date(d, content))
			} else if (d.Type == "text") {
				value.append(o.render_text(d, content))
			} else if (d.Candidates && (d.Candidates instanceof Array)) {
				value.append(o.render_select(d, content))
			} else {
				value.append(o.render_input(d, content))
			}
			table.append(line)
		}
		return table
	}

	o.render_del_group = function() {
		var div = $("<div class='del16 clickable' style='text-align:center'></div>")
		div.text(i18n.t("forms.del_group"))
		div.bind("click", function() {
			$(this).next("table").remove()
			$(this).remove()
		})
		return div
	}

	o.render_add_group = function() {
		var div = $("<div class='add16 clickable' style='text-align:center'></div>")
		div.text(i18n.t("forms.add_group"))
		o.area.append(div)
		div.bind("click", function() {
			var ref = o.area.children("table").last()
			var remove = o.render_del_group()
			remove.insertAfter(ref)
			ref.clone(true, true).insertAfter(remove)
		})
	}

	o.render_form_list = function() {
		o.area.empty()
		if (o.options.data.length == 0) {
			o.area.append(o.render_form_group({}))
		} else {
			for (var i=0; i<o.options.data.length; i++) {
				o.area.append(o.render_del_group())
				o.area.append(o.render_form_group(o.options.data[i]))
			}
		}
		o.render_add_group()
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
		o.render_submit()
		o.render_result()
	}

	o.render_form_dict = function() {
		o.area.empty().append(o.render_form_group(o.options.data))
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
		var result = $("<div></div>")
		o.area.append(result)
		o.result = result
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
			console.log("Output " + output.Dest + " not supported")
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
		})
	}

	o.render_datetime = function(d, content) {
		var input = $("<input class='oi'>")
		input.val(content)
		input.uniqueId()
		input.datetimepicker({dateFormat:'yy-mm-dd'})
		return input
	}
	o.render_date = function(d, content) {
		var input = $("<input class='oi'>")
		input.val(content)
		input.uniqueId()
		input.datepicker({dateFormat:'yy-mm-dd'})
		return input
	}
	o.render_text = function(d, content) {
		var textarea = $("<textarea class='oi pre' style='padding:0.4em;width:17em;height:8em'>")
		textarea.val(content)
		return textarea
	}
	o.render_input = function(d, content) {
		var input = $("<input class='oi'>")
		input.val(content)
		return input
	}
	o.render_select = function(d, content) {
		var input = $("<input class='oi aci'>")
		var opts = []
		for (var i=0; i<d.Candidates.length; i++) {
			opts.push(d.Candidates[i])
		}
		input.autocomplete({
			source: opts,
			minLength: 0
		})
		input.val(content)
		return input
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
		}
	}

	o.get_val = function(td, d) {
		if ((d.Type == "string") ||
		    (d.Type == "string or integer") ||
		    (d.Type == "list of string") ||
		    (d.Type == "date") ||
                    (d.Type == "datetime")) {
			return td.find("input").val()
		} else if (d.Type == "text") {
			return td.find("textarea").val()
		} else {
			console.log("form::get_val, " + d.Type + " not supported")
		}
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
			data = data.replace(re, o.get_val(td, d))
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
			data[d.Id] = o.get_val(td, d)
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

	$.when(osvc.forms_loaded).then(function() {
		o.load()
	})
	return o
}

