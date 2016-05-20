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

function osvc_create_link(fn, parameters) {
	if (!parameters) {
		parameters = {}
	}

	// Security for old link
	fn = fn.replace("?","")

	if ("divid" in parameters) {
		// case for links to tables embedded in views
		parameters["divid"] = "layout"
	}

	var link_id =  services_osvcpostrest("R_LINKS", "", "", {"fn": fn, "param": JSON.stringify(parameters)}, function(jd) {
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
		osvc_show_link(url)
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

	$(".header").addClass("clickable").bind("click", function(e) {
		if (!$(e.target).hasClass("header")) {
			// exit if the click is in a header descendant
			e.stopPropagation()
			return
		}
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
			"bgcolor": "slategray",
			"cl": "icon fa-info-circle",
			"text": "Info"
		})
	}

	o.error = function(content) {
		o.show({
			"content": content,
			"bgcolor": "red",
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

	return o
}

function osvc_show_link(url) {
	// header
	var e = $("<div></div>")

	var title = $("<div class='icon attach16 fa-2x' data-i18n='api.link'></div>")
	e.append(title)

	var subtitle = $("<div style='color:lightgray' data-i18n='api.link_text'></div>")
	e.append(subtitle)

	// link display area
	p = $("<textarea style='width:100%' class='clickable'></textarea>")
	p.val(url)
	p.css({
		"width": "100%",
		"background": "rgba(0,0,0,0)",
		"border": "rgba(0,0,0,0)",
		"padding": "2em 0 0 0",
	})
	p.bind("click", function() {
		send_link($(this).val())
	})

	e.i18n()
	e.append(p)

	osvc.flash.show({
		"id": url,
		"bgcolor": "slategray",
		"cl": "icon link16",
		"text": i18n.t("api.link"),
		"content": e
	})

	p.autogrow()
	p.select()
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
		var param = JSON.parse(result[0].link_parameters)
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
