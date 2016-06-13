function osvc_date_from_collector(s) {
	try {
		var m = moment.tz(s, osvc.server_timezone).tz(osvc.client_timezone)
	} catch(e) {
		console.log(e)
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
	$("#"+divid).load("/init/" + link_id, options, function() {})
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

		url += "/init/link/link?link_id="+link_id
		if (fn.beginsWith("https://")) {
			// if is not an ajax link, but a function js call
			url +="&js=false"
		} else {
			url += "&js=true"
		}
		osvc_show_link(url, title, title_args)
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
	o.barel_id = {}
	o.e_barel = $("<div class='tag_container'></div>")
	o.e_show = $("<div id='flashtab' style='margin-top:20px'></div>")

	$(".menu_flash").bind("click", function(e) {
		o.div.slideToggle()
	})

	o.init = function() {
		o.div.show()
		o.div.html([o.e_barel, o.e_show])
	}

	o.find_id = function(id) {
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
		if (data.id) {
			var i = o.find_id(data.id)
			if (i>=0) {
				o.barel.splice(i, 1)
			}
		}
		data.date = new Date()
		o.barel.push(data)
		if (o.barel.length > o.barel_len) {
			o.barel = o.barel.splice(0)
		}
	}

	o.render_barel_entry = function(data) {
		var d = $("<span class='tag'></span>")
		o.e_barel.append(d)
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

	o.show_entry = function(data) {
		if (data.fn) {
			o.e_show.addClass("searchtab")
			data.fn("flashtab")
		} else if (data.content) {
			o.e_show.removeClass("searchtab").html(data.content)
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
		o.push(data)
		o.init()
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

function osvc_show_link(url, title, title_args) {
	// header
	var e = $("<div></div>")

	var header = $("<div class='icon attach16 fa-2x' data-i18n='api.link'></div>")
	e.append(header)

	var subheader = $("<div style='color:lightgray' data-i18n='api.link_text'></div>")
	e.append(subheader)

	if (title && (title != "")) {
		var e_title = $("<h2></h2>")
		if (title in window) {
			var s = window[title](title_args)
		} else {
			var s = i18n.t(title, title_args)
		}
		e_title.html(s)
		e_title.css({"padding": "1em 0 0 0"})
		e.append(e_title)
	}

	// link display area
	var p = $("<textarea style='width:100%' class='clickable'></textarea>")
	p.val(url)
	p.css({
		"width": "100%",
		"background": "rgba(0,0,0,0)",
		"border": "rgba(0,0,0,0)",
		"padding": "1em 0 0 0",
	})
	p.bind("click", function() {
		window.open($(this).val(), '_blank')
	})

	e.i18n()
	e.append(p)

	osvc.flash.show({
		"id": url,
		"bgcolor": osvc.colors.link,
		"cl": "icon link16",
		"text": i18n.t("api.link"),
		"content": e
	})

	require(["jquery.ns-autogrow.coffee"], function() {
		p.autogrow()
	})
	p.select()
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
				"id": options.flash_id_prefix+name,
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
		"icon": "spark16",
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
		"icon": "spark16",
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
		"icon": "spark16",
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
		"flash_id_prefix": "role-",
		"fn": function(id, opts) {
			group_tabs(id, opts)
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
			return
		}
		services_osvcgetrest("/nodes/%1", [node_id] , {"meta": "0", "props": "nodename,app"}, function(jd) {
			var e_nodename = $("<span class='node16 icon_fixed_width'>"+jd.data[0].nodename+"</span>")
			var e_app = $("<span class='app16 icon_fixed_width'>"+jd.data[0].app+"</span>")
			o.html([e_nodename, " ", e_app])
			o.prop("title", node_id)
			o.attr("rendered", "")
			o.tooltipster()
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
			return
		}
		services_osvcgetrest("/services/%1", [svc_id] , {"meta": "0", "props": "svcname,svc_app"}, function(jd) {
			var e_svcname = $("<span class='svc icon_fixed_width'>"+jd.data[0].svcname+"</span>")
			var e_app = $("<span class='app16 icon_fixed_width'>"+jd.data[0].svc_app+"</span>")
			o.html([e_svcname, " ", e_app])
			o.prop("title", svc_id)
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
		var link = result[0].link_function

		if (link.beginsWith("https://")) {
			// ajax link
			app_load_href(link+"?"+param)
		} else {
			// js function link
			var fn = window[link]
			fn(divid, param)
		}
	})
}

/*
 * pin a DOM element to top on scroll past
 */
function sticky_relocate(e, anchor, onstick) {
	if (!e || !anchor) {
		return
	}
	var window_top = $(window).scrollTop();
	var div_top = anchor.offset().top;
	if (window_top > div_top) {
		// add the top-fixed clone element if not already present
		if (!e.next().is(".stick")) {
			var clone = e.clone(true, true)
			if (onstick) {
				onstick(clone, e)
			}
			clone.addClass('stick')

			// adjust top-fixed clone element width
			clone.css({"width": e[0].getBoundingClientRect().width})

			// adjust top-fixed clone element children width
			var e_children = e.children()
			var i = 0
			clone.children().each(function(){
				//$(this).width(e_children[i].offsetWidth)
				$(this).css({"box-sizing": "border-box", "width": e_children[i].getBoundingClientRect().width})
				i++
			})
			clone.insertAfter(e)
		} else {
			var clone = e.next()
		}

		// adjust left position
		var left = e.scrollParent().scrollLeft()

		e.next(".stick").css({"left": -left})
	} else {
		try {e.next('.stick').remove()} catch(err) {}
	}
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
	e.addClass("otooled")
	e.append(o.tools)
	o.linker = linker(e, o.tools, options)
	o.fullscreener = fullscreener(e, o.tools, options.resize)
	o.closer = closer(e, o.tools, options)
	return o
}

