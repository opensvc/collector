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

