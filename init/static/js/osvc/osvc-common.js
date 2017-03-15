function osvc_date_from_collector(s) {
	try {
		var m = moment.tz(s, osvc.server_timezone).tz(osvc.client_timezone)
	} catch(e) {
		console.log(e)
		return s
	}
	if (!m) {
		return s
	}
	return m.format(m._f)
}

function osvc_date_to_collector(s) {
	try {
		var m = moment.tz(s, osvc.client_timezone).tz(osvc.server_timezone)
	} catch(e) {
		console.log(e)
		return s
	}
	return m.format(m._f)
}

function is_dict(obj) {
	if(!obj) return false;
	if(Array.isArray(obj)) return false;
	if(obj.constructor != Object) return false;
	return true;
}

function is_special_key(e) {
	var no_refresh_keys = [
		9,  // tab
		16, // shift
		17, // ctrl
		18, // alt
		20, // caps lock
		27, // esc
		33, // page up
		34, // page down
		35, // end
		36, // home
		37, // left
		38, // up
		39, // right
		40, // down
		45 // insert
	]
	if (e && e.which) {
		e = e
		characterCode = e.which
	} else if (e && e.keyCode) {
		characterCode = e.keyCode
	} else {
		return false
	}
	if (no_refresh_keys.indexOf(characterCode) >= 0) {
		return true
	}
	return false
}

function is_enter(e) {
	var characterCode = -1;
	if (e && e.which) {
		e = e
		characterCode = e.which
	} else if (e && e.keyCode) {
		characterCode = e.keyCode
	}
	if (characterCode == 13) {
		return true
	}
	return false
}

function is_blank(str) {
	return (!str || /^\s*$/.test(str));
}

function is_empty_or_null(str) {
	if (str=='' || str=="null" || str==null) {
		return false
	} else {
		return true
	}
}

function toggle(divid, head) {
	if (head) {
		e = $("#"+head).find("#"+divid)
	} else {
		e = $('#'+divid)
	}
	e.slideToggle()
}

function mul_toggle(divid,divid2, head) {
	if (head) {
		e1 = $("#"+head).find("#"+divid)
		e2 = $("#"+head).find("#"+divid2)
	} else {
		e1 = $('#'+divid)
		e2 = $('#'+divid2)
	}
	e1.slideToggle(200, function() {
		e2.slideToggle(200)
	})
}

function float2int (value) {
	return value | 0
}

function spinner_del(e, text)
{
	if (!e) {
		return
	}
	e.children(".spinner").remove()
	e.children(".spinner_text").remove()
}

function spinner_add(e, text)
{
	if (!e) {
		return
	}
	if (e.children(".spinner").length > 0) {
		return
	}
	if (!text) {
		text = ""
	}
	var s = $("<span class='icon spinner fa-spin'><span>")
	e.append(s)
	var t = $("<span style='margin-left:1em' class='spinner_text'><span>")
	t.text(text)
	e.append(t)
	if (!e.is(":visible")) {
		e.slideToggle()
	}
}

function print_date(d) {
	var day = d.getDate()
	var month = d.getMonth()+1
	var year = d.getFullYear()
	var hours = d.getHours()
	var minutes = d.getMinutes()
	if (month<10) { month = "0"+month }
	if (day<10) { day = "0"+day }
	if (hours<10) { hours = "0"+hours }
	if (minutes<10) { minutes = "0"+minutes }
	var ds = year+"-"+month+"-"+day+" "+hours+":"+minutes
	return ds
}

String.prototype.beginsWith = function (string) {
	return(this.indexOf(string) === 0);
}

function link(divid, options) {
	var link_id = options.link_id
	$("#"+divid).load("/"+osvc.app+"/" + link_id, options, function() {})
}

function osvc_create_link(fn, parameters, title, title_args) {
	if (!parameters) {
		parameters = {}
	}

	if (!title_args) {
		title_args = {}
	}

	// Security for old link
	fn = fn.replace("?","")

	if (is_dict(parameters) && ("divid" in parameters)) {
		// case for links to tables embedded in views
		parameters["divid"] = "layout"
	}

	var link_id =  services_osvcpostrest("R_LINKS", "", "", {
		"fn": fn,
		"title": title,
		"title_args": title_args,
		"param": parameters
	}, function(jd) {
		if (jd.error) {
			osvc.flash.error(services_error_fmt(jd))
			return
		}
		var link_id = jd.link_id
		var url = services_get_url()

		url += "/"+osvc.app+"/link/link?link_id="+link_id
		if (fn.beginsWith("https://")) {
			// if is not an ajax link, but a function js call
			url +="&js=false"
		} else {
			url += "&js=true"
		}
		osvc_show_link(url, title, title_args, fn, parameters)
	},
	function(xhr, stat, error) {
		osvc.flash.error(services_ajax_error_fmt(xhr, stat, error))
	})
}

function flash() {
	var o = {}
	o.div = $(".flash")
	o.barel_len = 10
	o.barel = []
	o.e_barel = $("<div class='tag_container'></div>")
	o.e_show = $("<div style='margin-top:20px'></div>")
	o.div.html([o.e_barel, o.e_show])
	o.div.css({"display": "none"})

	$(".menu_flash").bind("click", function(e) {
		var opened = $(".menu:visible:not(.flash)").length
                osvc.search.close()
                osvc.fset_selector.close()
                osvc.menu.close()
                osvc.login.close()
		console.log(opened)
		if (opened == 0 || o.div.is(":visible")) {
			o.div.slideToggle()
		}
	})

	o.sanitize_id = function(id) {
		id = "" + id
		return id.replace(/[\.\s]/g, "-")
	}

	o.find_id = function(id) {
		id = o.sanitize_id(id)
		for (var i=0; i<o.barel.length; i++) {
			if (!o.barel[i].id) {
				continue
			}
			if (o.barel[i].id == id) {
				return i
			}
		}
		return -1
	}

	o.push = function(data) {
		data.id = o.sanitize_id(data.id)

		// drop redundant barel entry
		if (data.id) {
			var i = o.find_id(data.id)
			if (i>=0) {
				o.e_show.find("#"+data.id).remove()
				o.barel.splice(i, 1)
			}
		}

		// rpush the new entry
		data.date = new Date()
		o.barel.push(data)

		// ltrim the barel to its max length
		if (o.barel.length > o.barel_len) {
			o.e_show.find("#"+o.barel[0].id).remove()
			o.barel = o.barel.splice(0)
		}
	}

	o.delete_barel_entry = function(id) {
		var i = o.find_id(id)
		o.barel.splice(i, 1)
		o.e_barel.find("[barel_id="+id+"]").remove()
		o.e_show.find("#"+id).remove()
		if (o.barel.length == 0) {
			o.close()
		}
	}

	o.render_barel_entry = function(data) {
		var d = $("<span class='tag'></span>")
		o.e_barel.append(d)
		d.attr("barel_id", data.id)
		d.text(data.text)
		d.attr("title", data.date).tooltipster()
		if (data.bgcolor) {
			d.css({"background-color": data.bgcolor})
		}
		if (data.cl) {
			d.addClass(data.cl)
		}
		d.bind("click", function() {
			o.show_entry(data)
		})
	}

	o.render_barel = function() {
		o.e_barel.empty()
		for (var i=0; i<o.barel.length; i++) {
			o.render_barel_entry(o.barel[i])
		}
	}

	o.create_entry = function(data) {
		var e = $("<span></span>")
		e.attr("id", data.id)
		o.e_show.append(e)
		if (data.fn) {
			e.addClass("searchtab")
			data.fn(data.id)
		} else if (data.content) {
			e.html(data.content)
		}
	}

	o.show_entry = function(data) {
		o.e_show.children().hide()
		var e = o.e_show.children("span#"+data.id)
		if (e.length == 1) {
			e.show()
		} else {
			o.create_entry(data)
		}
	}

	o.info = function(content) {
		o.show({
			"content": content,
			"bgcolor": osvc.colors.info,
			"cl": "icon fa-info-circle",
			"text": "Info"
		})
	}

	o.error = function(content) {
		o.show({
			"content": content,
			"bgcolor": osvc.colors.error,
			"cl": "icon alert16",
			"text": "Error"
		})
	}

	o.show = function(data) {
		o.open()
		o.push(data)
		o.render_barel()
		o.show_entry(data)
	}

	o.open = function() {
		o.div.slideDown()
	}
	o.close = function() {
		o.div.slideUp()
	}

	return o
}

function osvc_render_title(e_title, title, title_args) {
	if (title && (title != "")) {
		if (title == "format_title") {
			console.log("format title generic:", e_title, title_args)
			title_args.element = e_title
			format_title(title_args)
		} else if (title in window) {
			console.log("format title with fn:", title, title_args)
			var s = window[title](title_args)
			e_title.html(s)
		} else {
			console.log("format title i18n key:", title, title_args)
			var s = i18n.t(title, title_args)
			e_title.html(s)
		}
	}
}

function osvc_show_link(url, title, title_args, fn, parameters) {
	// header
	var e = $("<div></div>")

	var header = $("<div class='icon attach16 fa-2x'></div>")
	e.append(header)

	var subheader = $("<div data-i18n='api.link_text'></div>")
	e.append(subheader)

	osvc_render_title(header, title, title_args)

	// link display area
	var p = $("<textarea class='clickable flash'></textarea>")
	p.val(url)
	p.bind("click", function() {
		window.open($(this).val(), '_blank')
	})

	e.append(p)

	osvc.flash.show({
		"id": md5(url),
		"bgcolor": osvc.colors.link,
		"cl": "icon link16",
		"text": i18n.t("api.link"),
		"content": e
	})

	p.select()

	// report snippet
	var report_header = $("<div class='icon report16 fa-2x' data-i18n='api.report_snippet'></div>")
	var report_subheader = $("<div style='color:lightgray' data-i18n='api.report_snippet_desc'></div>")
	var snippet = $("<textarea class='flash' style='height:15em'></textarea>")
	e.append([report_header, report_subheader, snippet])

	var data = [{
		"Desc": "",
		"Title": header.text(),
		"width": "100%",
		"Function": fn,
		"Args": parameters
	}]
	require(["jsyaml"], function(jsyaml){
		snippet.text(jsyaml.dump(data))
	})
	e.children("textarea").css({"width": "100%"})

	// translate
	e.i18n()
}

function osvc_jq_decorator(e, options) {
        if (!options.options) {
		options.options = {}
	}
        if (!("show_icon" in options.options)) {
		options.options.show_icon = true
	}
        if (!("event" in options.options)) {
		options.options.event = "dblclick"
	}
        if (!("tag" in options.options)) {
		options.options.tag = true
	}
	$(e).each(function(){
		var o = $(this)
		if (o.is("[rendered]")) {
			return
		}
		var opts = {}
		if (options.options[options.attr]) {
			var id = options.options[options.attr]
		} else {
			var id = o.attr(options.attr)
		}
		if (options.options[options.name]) {
			var name = options.options[options.name]
		} else {
			var name = o.text()
		}
		if (!id && (!name || name == "")) {
			return
		}
		if (id) {
			opts[options.attr] = id
		}
		if (name) {
			opts[options.name] = name
		}
		var e = $("<span>"+name+"</span>")
		if (options.options.tag) {
			e.addClass("tag")
			e.css({"background-color": options.bgcolor})
		} else {
			e.addClass("link")
		}
		if (options.options.show_icon) {
			e.addClass("icon "+options.icon)
		}
		o.html(e)
		e.bind(options.options.event, function() {
			osvc.flash.show({
				"id": options.flash_id_prefix+id,
				"text": name,
				"cl": "icon "+options.icon,
				"bgcolor": options.bgcolor,
				"fn": function(id) {
					options.fn(id, opts)
				}
			})
		})
	})
}

jQuery.fn.osvc_docker_repository = function(options) {
	osvc_jq_decorator(this, {
		"options": options,
		"name": "repository_name",
		"attr": "repository_id",
		"icon": "docker_repository16",
		"bgcolor": osvc.colors.docker,
		"flash_id_prefix": "docker-repository-",
		"fn": function(id, opts) {
			docker_repository_tabs(id, opts)
		}
	})
}

jQuery.fn.osvc_docker_registry = function(options) {
	osvc_jq_decorator(this, {
		"options": options,
		"name": "registry_service",
		"attr": "registry_id",
		"icon": "docker_registry16",
		"bgcolor": osvc.colors.docker,
		"flash_id_prefix": "docker-registry-",
		"fn": function(id, opts) {
			docker_registry_tabs(id, opts)
		}
	})
}

jQuery.fn.osvc_form = function(options) {
	osvc_jq_decorator(this, {
		"options": options,
		"name": "form_name",
		"attr": "form_id",
		"icon": "wf16",
		"bgcolor": osvc.colors.form,
		"flash_id_prefix": "form-",
		"fn": function(id, opts) {
			form_tabs(id, opts)
		}
	})
}

jQuery.fn.osvc_report = function(options) {
	osvc_jq_decorator(this, {
		"options": options,
		"name": "report_name",
		"attr": "report_id",
		"icon": osvc.icons.report,
		"bgcolor": osvc.colors.stats,
		"flash_id_prefix": "report-",
		"fn": function(id, opts) {
			report_tabs(id, opts)
		}
	})
}

jQuery.fn.osvc_chart = function(options) {
	osvc_jq_decorator(this, {
		"options": options,
		"name": "chart_name",
		"attr": "chart_id",
		"icon": osvc.icons.chart,
		"bgcolor": osvc.colors.stats,
		"flash_id_prefix": "chart-",
		"fn": function(id, opts) {
			chart_tabs(id, opts)
		}
	})
}

jQuery.fn.osvc_metric = function(options) {
	osvc_jq_decorator(this, {
		"options": options,
		"name": "metric_name",
		"attr": "metric_id",
		"icon": osvc.icons.metric,
		"bgcolor": osvc.colors.stats,
		"flash_id_prefix": "metric-",
		"fn": function(id, opts) {
			metric_tabs(id, opts)
		}
	})
}

jQuery.fn.osvc_filterset = function(options) {
	osvc_jq_decorator(this, {
		"options": options,
		"name": "fset_name",
		"attr": "fset_id",
		"icon": "filter16",
		"bgcolor": osvc.colors.fset,
		"flash_id_prefix": "fset-",
		"fn": function(id, opts) {
			filterset_tabs(id, opts)
		}
	})
}

jQuery.fn.osvc_ruleset = function(options) {
	osvc_jq_decorator(this, {
		"options": options,
		"name": "ruleset_name",
		"attr": "ruleset_id",
		"icon": osvc.icons.rset,
		"bgcolor": osvc.colors.comp,
		"flash_id_prefix": "rset-",
		"fn": function(id, opts) {
			ruleset_tabs(id, opts)
		}
	})
}

jQuery.fn.osvc_module = function(options) {
	osvc_jq_decorator(this, {
		"options": options,
		"name": "modset_mod_name",
		"attr": "id",
		"icon": osvc.icons.module,
		"bgcolor": osvc.colors.comp,
		"flash_id_prefix": "module-",
		"fn": function(id, opts) {
		}
	})
}

jQuery.fn.osvc_moduleset = function(options) {
	osvc_jq_decorator(this, {
		"options": options,
		"name": "modset_name",
		"attr": "modset_id",
		"icon": osvc.icons.modset,
		"bgcolor": osvc.colors.comp,
		"flash_id_prefix": "modset-",
		"fn": function(id, opts) {
			moduleset_tabs(id, opts)
		}
	})
}

jQuery.fn.osvc_variable_class = function(options) {
	osvc_jq_decorator(this, {
		"options": options,
		"name": "var_class",
		"attr": "var_id",
		"icon": osvc.icons.variable,
		"bgcolor": osvc.colors.comp,
		"flash_id_prefix": "var-",
		"fn": function(id, opts) {
			variable_tabs(id, opts)
		}
	})
}

jQuery.fn.osvc_app = function(options) {
	osvc_jq_decorator(this, {
		"options": options,
		"name": "app_name",
		"attr": "app_id",
		"icon": "app16",
		"bgcolor": osvc.colors.app,
		"flash_id_prefix": "app-",
		"fn": function(id, opts) {
			app_tabs(id, opts)
		}
	})
}

jQuery.fn.osvc_org_group = function(options) {
	osvc_jq_decorator(this, {
		"options": options,
		"name": "group_name",
		"attr": "group_id",
		"icon": "guys16",
		"bgcolor": osvc.colors.org,
		"flash_id_prefix": "group-",
		"fn": function(id, opts) {
			group_tabs(id, opts)
		}
	})
}

jQuery.fn.osvc_fullname = function(options) {
	osvc_jq_decorator(this, {
		"options": options,
		"name": "fullname",
		"attr": "fullname",
		"icon": "guys16",
		"bgcolor": osvc.colors.user,
		"flash_id_prefix": "user-",
		"fn": function(fullname, opts) {
			user_tabs(fullname, opts)
		}
	})
}

jQuery.fn.osvc_array = function(options) {
	osvc_jq_decorator(this, {
		"options": options,
		"name": "array_name",
		"attr": "array_id",
		"icon": "array",
		"bgcolor": osvc.colors.disk,
		"flash_id_prefix": "array-",
		"fn": function(id, opts) {
			array_tabs(id, opts)
		}
	})
}

jQuery.fn.osvc_prov_template = function(options) {
	osvc_jq_decorator(this, {
		"options": options,
		"name": "tpl_name",
		"attr": "tpl_id",
		"icon": "prov",
		"bgcolor": osvc.colors.svc,
		"flash_id_prefix": "tpl-",
		"fn": function(id, opts) {
			prov_template_tabs(id, opts)
		}
	})
}

jQuery.fn.osvc_nodename = function(options) {
        if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is("[rendered]")) {
			return
		}
		var node_id = o.attr("node_id")
		if (!node_id) {
			node_id = o.text()
		}
		if (node_id == "") {
			return
		}
		services_osvcgetrest("/nodes/%1", [node_id] , {"meta": "0", "props": "nodename,app"}, function(jd) {
			if (!options.tag) {
				var e_nodename = $("<span class='node16 icon_fixed_width'>"+jd.data[0].nodename+"</span>")
				var e_app = $("<span class='app16 icon_fixed_width'>"+jd.data[0].app+"</span>")
				o.html([e_nodename, " ", e_app])
				o.prop("title", node_id)
				o.attr("rendered", "")
				o.tooltipster()
			} else {
				var e_nodename = $("<span class='tag icon node16'>"+jd.data[0].nodename+"</span>")
				e_nodename.css({"background-color": osvc.colors.node})
				o.html(e_nodename)
				o.attr("rendered", "")
			}
			e_nodename.bind("dblclick", function() {
				osvc.flash.show({
					"id": "node-"+node_id,
					"text": jd.data[0].nodename,
					"cl": "icon node16",
					"bgcolor": osvc.colors.node,
					"fn": function(id) {
						node_tabs(id, {"node_id": node_id, "nodename": jd.data[0].nodename})
					}
				})
			})
			if (options.callback) {
				options.callback()
			}
		})
	})
}

jQuery.fn.osvc_svcname = function(options) {
        if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is("[rendered]")) {
			return
		}
		var svc_id = o.attr("svc_id")
		if (!svc_id) {
			svc_id = o.text()
		}
		if (svc_id == "" || svc_id == "undefined") {
			return
		}
		services_osvcgetrest("/services/%1", [svc_id] , {"meta": "0", "props": "svcname,svc_app"}, function(jd) {
			if (!options.tag) {
				var e_svcname = $("<span class='svc icon_fixed_width'>"+jd.data[0].svcname+"</span>")
				var e_app = $("<span class='app16 icon_fixed_width'>"+jd.data[0].svc_app+"</span>")
				o.html([e_svcname, " ", e_app])
				o.prop("title", svc_id)
				o.attr("rendered", "")
				o.tooltipster()
			} else {
				var e_svcname = $("<span class='tag icon svc'>"+jd.data[0].svcname+"</span>")
				e_svcname.css({"background-color": osvc.colors.svc})
				o.html(e_svcname)
				o.attr("rendered", "")
			}
			e_svcname.bind("dblclick", function() {
				osvc.flash.show({
					"id": "svc-"+svc_id,
					"text": jd.data[0].svcname,
					"cl": "icon svc",
					"bgcolor": osvc.colors.svc,
					"fn": function(id) {
						service_tabs(id, {"svc_id": svc_id, "svcname": jd.data[0].svcname})
					}
				})
			})
			if (options.callback) {
				options.callback()
			}
		})
	})
}

jQuery.fn.osvc_resourcename = function(options) {
	if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is("[rendered]")) {
			return
		}

		var rid = o.attr("rid")
		if (!rid ) {
			rid = o.attr("id")
			services_osvcgetrest("/resources/%1", [rid], {"meta": "0", "props": "rid"}, function(jd) {
				var e_resname = $("<span class='resource icon_fixed_width'>"+jd.data[0].rid+"</span>")
				o.html([e_resname])
				o.prop("title", rid)
				o.attr("rendered", "")
				o.tooltipster()
				if (options.callback) {
					options.callback()
				}
			})
		} else {
			var e_resname = $("<span class='resource icon_fixed_width'>"+rid+"</span>")
			o.html([e_resname])
			o.prop("title", rid)
			o.attr("rendered", "")
			o.tooltipster()
			if (options.callback) {
				options.callback()
			}
		}
	})
}

jQuery.fn.osvc_svcaction_name = function(options) {
	var o = $(this)
	if (!options) {
		options = {}
	}
	if (o.is('[rendered]')) {
		return
	}
	var e_action_name = $("<span class='actions icon_fixed_width'>"+o.attr("action")+"</span>")
	o.html([e_action_name])
	o.attr("rendered", "")
	if (options.callback) {
		options.callback()
	}
}

jQuery.fn.osvc_formname = function(options) {
	if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is(["rendered"])) {
			return
		}
		var id = o.attr('id')
		if (!id) {
			id = o.text()
		}
		if (id == "") {
			return
		}
		services_osvcgetrest("/forms/%1", [id] , {"meta": "0", "props": "form_name"}, function(jd) {
			var e_formname = $("<span class='wf16 icon_fixed_width'>"+jd.data[0].form_name+"</span>")
			o.html([e_formname])
			o.prop("title", id)
			o.attr("rendered", "")
			o.tooltipster()
			if (options.callback) {
				options.callback()
			}
		})
	})
}

jQuery.fn.osvc_appname = function(options) {
	if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is(["rendered"])) {
			return
		}
		var id = o.attr('id')
		if (!id) {
			id = o.text()
		}
		if (id == "") {
			return
		}
		services_osvcgetrest("/apps/%1", [id] , {"meta": "0", "props": "app"}, function(jd) {
			var e_appname = $("<span class='app16 icon_fixed_width'>"+jd.data[0].app+"</span>")
			o.html([e_appname])
			o.prop("title", id)
			o.attr("rendered", "")
				o.tooltipster()
			if (options.callback) {
				options.callback()
			}
		})
	})
}

jQuery.fn.osvc_dns_domainname = function(options) {
	if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is(["rendered"])) {
			return
		}
		var id = o.attr('id')
		if (!id) {
			id = o.text()
		}
		if (id == "") {
			return
		}
		services_osvcgetrest("/dns/domains/%1", [id] , {"meta": "0", "props": "name"}, function(jd) {
			var e_domainname = $("<span class='dns16 icon_fixed_width'>"+jd.data[0].name+"</span>")
			o.html([e_domainname])
			o.prop("title", id)
			o.attr("rendered", "")
				o.tooltipster()
			if (options.callback) {
				options.callback()
			}
		})
	})
}

jQuery.fn.osvc_dns_recordname = function(options) {
	if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is(["rendered"])) {
			return
		}
		var id = o.attr('id')
		if (!id) {
			id = o.text()
		}
		if (id == "") {
			return
		}
		services_osvcgetrest("/dns/records/%1", [id] , {"meta": "0", "props": "name"}, function(jd) {
			var e_recordname = $("<span class='dns16 icon_fixed_width'>"+jd.data[0].name+"</span>")
			o.html([e_recordname])
			o.prop("title", id)
			o.attr("rendered", "")
				o.tooltipster()
			if (options.callback) {
				options.callback()
			}
		})
	})
}

jQuery.fn.osvc_docker_registryname = function(options) {
	if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is(["rendered"])) {
			return
		}
		var id = o.attr('registry_id')
		if (!id) {
			id = o.text()
		}
		if (id == "") {
			return
		}
		services_osvcgetrest("/docker/registries/%1", [id] , {"meta": "0", "props": "service"}, function(jd) {
			var e_registryname = $("<span class='docker_registry16 icon_fixed_width'>"+jd.data[0].service+"</span>")
			o.html([e_registryname])
			o.prop("title", id)
			o.attr("rendered", "")
				o.tooltipster()
			if (options.callback) {
				options.callback()
			}
		})
	})
}

jQuery.fn.osvc_docker_repositoryname = function(options) {
	if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is(["rendered"])) {
			return
		}
		var id = o.attr('repository_id')
		if (!id) {
			id = o.text()
		}
		if (id == "") {
			return
		}
		services_osvcgetrest("/docker/repositories/%1", [id] , {"meta": "0", "props": "repository"}, function(jd) {
			var e_reponame = $("<span class='docker_repository16 icon_fixed_width'>"+jd.data[0].repository+"</span>")
			o.html([e_reponame])
			o.prop("title", id)
			o.attr("rendered", "")
				o.tooltipster()
			if (options.callback) {
				options.callback()
			}
		})
	})
}

jQuery.fn.osvc_docker_tagname = function(options) {
	if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is(["rendered"])) {
			return
		}
		var id = o.attr('tag_id')
		if (!id) {
			id = o.text()
		}
		if (id == "") {
			return
		}
		services_osvcgetrest("/docker/tags/%1", [id] , {"meta": "0", "props": "name"}, function(jd) {
			var e_tagname = $("<span class='dockertags16 icon_fixed_width'>"+jd.data[0].name+"</span>")
			o.html([e_tagname])
			o.prop("title", id)
			o.attr("rendered", "")
				o.tooltipster()
			if (options.callback) {
				options.callback()
			}
		})
	})
}

jQuery.fn.osvc_netname = function(options) {
	if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is(["rendered"])) {
			return
		}
		var net_id = o.attr("net_id")
		if (!net_id) {
			net_id = o.text()
		}
		if (net_id == "") {
			return
		}
		services_osvcgetrest("/networks/%1", [net_id] , {"meta": "0", "props": "name"}, function(jd) {
			var e_netname = $("<span class='net16 icon_fixed_width'>"+jd.data[0].name+"</span>")
			o.html([e_netname])
			o.prop("title", net_id)
			o.attr("rendered", "")
			o.tooltipster()
			if (options.callback) {
				options.callback()
			}
		})
	})
}

jQuery.fn.osvc_metricname = function(options) {
	if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is(["rendered"])) {
			return
		}
		var id = o.attr("id")
		if (!id) {
			id = o.text()
		}
		if (id == "") {
			return
		}
		services_osvcgetrest("/reports/metrics/%1", [id] , {"meta": "0", "props": "metric_name"}, function(jd) {
			var e_metricname = $("<span class='metric16 icon_fixed_width'>"+jd.data[0].metric_name+"</span>")
			o.html([e_metricname])
			o.prop("title", id)
			o.attr("rendered", "")
			o.tooltipster()
			if (options.callback) {
				options.callback()
			}
		})
	})
}

jQuery.fn.osvc_chartname = function(options) {
	if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is(["rendered"])) {
			return
		}
		var id = o.attr("id")
		if (!id) {
			id = o.text()
		}
		if (id == "") {
			return
		}
		services_osvcgetrest("/reports/charts/%1", [id] , {"meta": "0", "props": "chart_name"}, function(jd) {
			var e_chartname = $("<span class='chart16 icon_fixed_width'>"+jd.data[0].chart_name+"</span>")
			o.html([e_chartname])
			o.prop("title", id)
			o.attr("rendered", "")
			o.tooltipster()
			if (options.callback) {
				options.callback()
			}
		})
	})
}

jQuery.fn.osvc_obsolescencename = function(options) {
	if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is(["rendered"])) {
			return
		}
		var id = o.attr("id")
		if (!id) {
			id = o.text()
		}
		if (id == "") {
			return
		}
		services_osvcgetrest("/obsolescence/settings/%1", [id] , {"meta": "0", "props": "obs_name,obs_type"}, function(jd) {
			var e_obsname = $("<span>"+jd.data[0].obs_name+"</span>")
			var e_obstype = $("<span class='"+jd.data[0].obs_type+"16 icon_fixed_width'>"+jd.data[0].obs_type+"</span>")
			o.html([e_obstype, " : ", e_obsname])
			o.prop("title", id)
			o.attr("rendered", "")
			o.tooltipster()
			if (options.callback) {
				options.callback()
			}
		})
	})
}

jQuery.fn.osvc_reportname = function(options) {
	if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is(["rendered"])) {
			return
		}
		var id = o.attr("id")
		if (!id) {
			id = o.text()
		}
		if (id == "") {
			return
		}
		services_osvcgetrest("/reports/%1", [id] , {"meta": "0", "props": "report_name"}, function(jd) {
			var e_reportname = $("<span class='report16 icon_fixed_width'>"+jd.data[0].report_name+"</span>")
			o.html([e_reportname])
			o.prop("title", id)
			o.attr("rendered", "")
			o.tooltipster()
			if (options.callback) {
				options.callback()
			}
		})
	})
}

jQuery.fn.osvc_prov_templatename = function(options) {
	if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is(["rendered"])) {
			return
		}
		var id = o.attr("id")
		if (!id) {
			id = o.text()
		}
		if (id == "") {
			return
		}
		services_osvcgetrest("/provisioning_templates/%1", [id] , {"meta": "0", "props": "tpl_name"}, function(jd) {
			var e_tplname = $("<span class='prov icon_fixed_width'>"+jd.data[0].tpl_name+"</span>")
			o.html([e_tplname])
			o.prop("title", id)
			o.attr("rendered", "")
			o.tooltipster()
			if (options.callback) {
				options.callback()
			}
		})
	})
}

jQuery.fn.osvc_ip = function(options) {
	if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is(["rendered"])) {
			return
		}
		var id = o.attr("id")
		if (!id) {
			id = o.text()
		}
		if (id == "") {
			return
		}
		services_osvcgetrest("/ips/%1", [id] , {"meta": "0", "props": "nodename,addr"}, function(jd) {
			var e_addr = $("<span class='net16 icon_fixed_width'>"+jd.data[0].addr+"</span>")
			o.html([e_addr])
			o.prop("title", id)
			o.attr("rendered", "")
			o.tooltipster()
			if (options.callback) {
				options.callback()
			}
		})
	})
}

jQuery.fn.osvc_modulesetname = function(options) {
	if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is(["rendered"])) {
			return
		}
		var id = o.attr("modset_id")
		if (!id) {
			id = o.text()
		}
		if (id == "") {
			return
		}
		services_osvcgetrest("/compliance/modulesets/%1", [id] , {"meta": "0", "props": "modset_name"}, function(jd) {
			var e_modsetname = $("<span class='modset16 icon_fixed_width'>"+jd.data[0].modset_name+"</span>")
			o.html([e_modsetname])
			o.prop("title", id)
			o.attr("rendered", "")
			o.tooltipster()
			if (options.callback) {
				options.callback()
			}
		})
	})
}

jQuery.fn.osvc_rulesetname = function(options) {
	if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is(["rendered"])) {
			return
		}
		var id = o.attr("id")
		if (!id) {
			id = o.text()
		}
		if (id == "") {
			return
		}
		services_osvcgetrest("/compliance/rulesets/%1", [id] , {"meta": "0", "props": "ruleset_name"}, function(jd) {
			var e_rsetname = $("<span class='rset16 icon_fixed_width'>"+jd.data[0].ruleset_name+"</span>")
			o.html([e_rsetname])
			o.prop("title", id)
			o.attr("rendered", "")
			o.tooltipster()
			if (options.callback) {
				options.callback()
			}
		})
	})
}

jQuery.fn.osvc_filtersetname = function(options) {
	if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is(["rendered"])) {
			return
		}
		var id = o.attr("id")
		if (!id) {
			id = o.text()
		}
		if (id == "") {
			return
		}
		services_osvcgetrest("/filtersets/%1", [id] , {"meta": "0", "props": "fset_name"}, function(jd) {
			var e_fsetname = $("<span class='filter16 icon_fixed_width'>"+jd.data[0].fset_name+"</span>")
			o.html([e_fsetname])
			o.prop("title", id)
			o.attr("rendered", "")
			o.tooltipster()
			if (options.callback) {
				options.callback()
			}
		})
	})
}

jQuery.fn.osvc_safe = function(options) {
	if (!options) {
		options = {}
	}
	$(this).each(function(){
		var o = $(this)
		if (o.is(["rendered"])) {
			return
		}
		var id = o.attr('id')
		if (!id) {
			id = o.text()
		}
		if (id == "") {
			return
		}
		services_osvcgetrest("/safe/%1", [id] , {"meta": "0", "props": "uuid"}, function(jd) {
			var e_safe_uuid = $("<span class='safe16 icon_fixed_width'>"+jd.data[0].uuid+"</span>")
			o.html([e_safe_uuid])
			o.prop("title", id)
			o.attr("rendered", "")
			o.tooltipster()
			if (options.callback) {
				options.callback()
			}
		})
	})
}

function osvc_nodenames(l) {
	if (!l) {
		return
	}
	if (typeof(l) === "number") {
		return osvc_nodename(l)
	}
	if (typeof(l) === "string") {
		l = l.split(",")
	}
	var e = $("<span></span>")
	for (var i=0; i<l.length; i++) {
		if (i>0) {
			e.append(", ")
		}
                e.append(osvc_nodename(l[i]))
        }
	return e
}

function osvc_nodename(node_id) {
	var e = $("<span>"+node_id+"</span>")
	if (!node_id) {
		return e
	}
	services_osvcgetrest("/nodes", [node_id] , {"meta": "0", "props": "nodename,app"}, function(jd) {
		var e_nodename = $("<span>"+jd.data[0].nodename+"</span>")
		var e_app = $("<span class='app16'>"+jd.data[0].app+"</span>")
		e.html([e_nodename, " ", e_app])
		e.prop("title", node_id)
                e.tooltipster()
	})
	return e
}

function osvc_get_link(divid,link_id) {
	services_osvcgetrest("R_LINK",[link_id] , "", function(jd) {
		if (jd.data.length === 0) {
			// Link not found
			var val = "<div style='text-align:center'>" + i18n.t("link.notfound")+"</div>"
			$('#'+divid).html(val)
			return
		}
		var result = jd.data
		if (result[0].link_parameters == "") {
			var param = {}
		} else {
			var param = JSON.parse(result[0].link_parameters)
		}
		if (result[0].link_title_args == "") {
			var title_args = {}
		} else {
			var title_args = JSON.parse(result[0].link_title_args)
		}
		var link = result[0].link_function

		var e_title = $("<span></span>")
		osvc_render_title(e_title, result[0].link_title, title_args) 
		if (e_title.text().length > 0) {
			osvc.menu.menu_clickable.find(".menu16").text("").append(e_title)
		}

		if (link.beginsWith("https://") || link.beginsWith("/")) {
			// ajax link
			if (param.indexOf("=") > 0) {
				app_load_href(link+"?"+param, null, {"loadable_href": true})
			} else {
				app_load_href(link+"/"+param, null, {"loadable_href": true})
			}
		} else {
			// js function link
			var fn = window[link]
			fn(divid, param)
		}
	})
}

function check_visible(e, top_offset) {
	var vpH = $(window).height()
	var st = $(window).scrollTop()
	if (top_offset) {
		st += top_offset
	}
        var y = $(e).offset().top
        var elementHeight = $(e).height()
	return ((y < (vpH + st)) && (y > (st - elementHeight)))
}

function is_numeric(n) {
	return !isNaN(parseFloat(n)) && isFinite(n);
}

function IE(v) {
	return RegExp('msie' + (!isNaN(v)?('\\s'+v):''), 'i').test(navigator.userAgent);
}

function closer(e, tools, options) {
	var o = {}
	if (!options.close) {
		return o
	}
	o.tool = $("<div class='fa fa-times linker'></div>")
	tools.append(o.tool)
	//o.tool.attr("title", i18n.t("tabs.close")).tooltipster()

	o.tool.bind("click", function() {
		// Remove extraline
		e.parents(".extraline").first().remove()

		e.parent().parent().each(function() {
			if ($(this).hasClass("flash")) {
				// Tabs in flash zone
				e.empty()
				e.parent().removeClass("searchtab")
				return
			}
		})
		if (e.parent().hasClass("searchtab")) {
			// Tabs in search result
			osvc.flash.delete_barel_entry(e.parent()[0].id)
			e.parent().hide()
		}
		e.remove()
	})
	return o
}

function linker(e, tools, options) {
	var o = {}
	if (!options.link) {
		return o
	}
	if (!options.link.fn) {
		return o
	}
	if (options.link.title_args && !options.link.title_args.fn) {
		options.link.title_args.fn = options.link.fn
	}
	o.tool = $("<div class='fa fa-link linker'></div>")
	tools.append(o.tool)
	o.tool.bind("click", function() {
		osvc_create_link(options.link.fn, options.link.parameters, options.link.title, options.link.title_args)
	})
	return o
}

function get_layout_max_height() {
	return $(window).height()-$(".header").height()-$(".footer").height()-1
}

function max_child_height(div) {
	var max_height = get_layout_max_height()
	if (div.parent().hasClass("layout") || div.parent().parent().hasClass("layout")) {
		return max_height
	} else {
		return max_height*0.75
	}
}

function fullscreener(e, tools, resize) {
	var o = {}
	o.dom_prev = e.prev()
	o.dom_parent = e.parent()
	o.backup = null
	o.tool = $("<div class='fa fa-expand'></div>")
	tools.append(o.tool)
	o.tool.bind("click", function() {
		if (o.tool.hasClass("fa-expand")) {
			if (e.parents(".flash").length == 1) {
				o.from_flash = true
				osvc.flash.close()
			}
			if (e.parents("#search_result").length == 1) {
				o.from_search = true
				$("#search_result").slideUp()
			}
			e.detach()
			o.backup = $(".layout").children().detach()
			$(".layout").append(e)
			o.tool.removeClass("fa-expand").addClass("fa-compress")
			if (resize) {
				resize()
			}
		} else {
			if (o.from_flash) {
				o.from_flash = false
				osvc.flash.open()
			}
			if (o.from_search) {
				o.from_search = false
				$("#search_result").slideDown()
			}
			e.detach()
			$(".layout").append(o.backup)
			if (o.dom_prev.length == 1) {
				e.insertAfter(o.dom_prev)
			} else {
				o.dom_parent.prepend(e)
			}
			o.tool.removeClass("fa-compress").addClass("fa-expand")
			o.backup = null
			if (resize) {
				resize()
			}
		}
	})
	return o
}

function osvc_tools(e, options) {
	var o = {}
	o.tools = $("<div class='otools'></div>")
	e.css({"position": "relative"})
	if (e.hasClass("layout")) {
		// add the layout padding for the header
		o.tools.css({"top": o.tools.position().top+$(".header").height()+"px"})
	}
	e.addClass("otooled")
	e.append(o.tools)
	o.linker = linker(e, o.tools, options)
	o.fullscreener = fullscreener(e, o.tools, options.resize)
	o.closer = closer(e, o.tools, options)
	return o
}

//
// Format link and tab titles
//
// Options:
//   - type: the object type, known as a osvc.colors, osvc.icons key
//   - name: if passed the object name. requested if not passed
//   - id: the object id used to request 'name' if 'name' is not passed
//   - element: the jquery selector to place the title in
//
function format_title(options) {
	var o = {}
	o.options = options

	o.render = function() {
		var color = osvc.colors[o.options.type]
		var icon = osvc.icons[o.options.type]
		o.options.element.html(i18n.t("link."+o.options.fn, {"name": "<span style='color:"+color+"' class='"+icon+" icon'>"+o.options.name+"</span>"}))
	}

	if ("name" in options) {
		o.render()
	}

	if (options.type == "node") {
		services_osvcgetrest("R_NODE", [o.options.id], {"props": "nodename", "meta": "false", "limit": 1}, function(jd) {
			o.options.name = jd.data[0].nodename
			o.render()
		})
	}
	else if (options.type == "service") {
		services_osvcgetrest("R_SERVICE", [o.options.id], {"props": "svcname", "meta": "false", "limit": 1}, function(jd) {
			o.options.name = jd.data[0].svcname
			o.render()
		})
	}
	else if (options.type == "report") {
		services_osvcgetrest("/reports/%1", [o.options.id], {"props": "report_name", "meta": "false", "limit": 1}, function(jd) {
			o.options.name = jd.data[0].report_name
			o.render()
		})
	}
	else if (options.type == "chart") {
		services_osvcgetrest("/reports/charts/%1", [o.options.id], {"props": "chart_name", "meta": "false", "limit": 1}, function(jd) {
			o.options.name = jd.data[0].chart_name
			o.render()
		})
	}
	else if (options.type == "metric") {
		services_osvcgetrest("/reports/metrics/%1", [o.options.id], {"props": "metric_name", "meta": "false", "limit": 1}, function(jd) {
			o.options.name = jd.data[0].metric_name
			o.render()
		})
	}
	else if (options.type == "ruleset") {
		services_osvcgetrest("/compliance/rulesets/%1", [o.options.id], {"props": "ruleset_name", "meta": "false", "limit": 1}, function(jd) {
			o.options.name = jd.data[0].ruleset_name
			o.render()
		})
	}
	else if (options.type == "moduleset") {
		services_osvcgetrest("/compliance/modulesets/%1", [o.options.id], {"props": "modset_name", "meta": "false", "limit": 1}, function(jd) {
			o.options.name = jd.data[0].modset_name
			o.render()
		})
	}
	else if (options.type == "app") {
		services_osvcgetrest("/apps/%1", [o.options.id], {"props": "app", "meta": "false", "limit": 1}, function(jd) {
			o.options.name = jd.data[0].app
			o.render()
		})
	}
	else if (options.type == "fset") {
		services_osvcgetrest("/filtersets/%1", [o.options.id], {"props": "fset_name", "meta": "false", "limit": 1}, function(jd) {
			o.options.name = jd.data[0].fset_name
			o.render()
		})
	}
	else if (options.type == "docker_registry") {
		services_osvcgetrest("/docker/registries/%1", [o.options.id], {"props": "service", "meta": "false", "limit": 1}, function(jd) {
			o.options.name = jd.data[0].service
			o.render()
		})
	}
	else if (options.type == "docker_repository") {
		services_osvcgetrest("/docker/repositories/%1", [o.options.id], {"props": "repository", "meta": "false", "limit": 1}, function(jd) {
			o.options.name = jd.data[0].repository
			o.render()
		})
	}
}

function is_in_view(e) {
	return !($(e).offset().top - $(window).scrollTop() < $(e).height())
}
