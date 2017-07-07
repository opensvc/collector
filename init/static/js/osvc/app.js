var osvc = {
	'tables': {},
	'user_loaded': $.Deferred(),
	'forms_loaded': $.Deferred(),
	'i18n_started': $.Deferred(),
	'app_started': $.Deferred(),
	'icons': {
		'docker_repository': 'docker_repository16',
		'docker_registry': 'docker_registry16',
		'node': 'node16',
		'svc': 'svc',
		'service': 'svc',
		'alert': 'alert16',
		'tag': 'tag16',
		'pkg': 'pkg16',
		'net': 'net16',
		'segment': 'segment16',
		'chk': 'check16',
		'form': 'wf16',
		'report': 'report16',
		'chart': 'chart16',
		'metric': 'metric16',
		'org': 'group16',
		'dns': 'dns16',
		'priv': 'privilege16',
		'link': 'link16',
		'fset': 'fset16',
		'disk': 'hd16',
		'array': 'array',
		'diskgroup': 'diskgroup',
		'rset': 'rset16',
		'ruleset': 'rset16',
		'modset': 'modset16',
		'moduleset': 'modset16',
		'module': 'mod16',
		'app': 'app16',
		'variable': 'comp16'
	},
	'colors': {
		'action': '#aaa',
		'alert': 'orange',
		'app': '#cc1377',
		'chart': 'sandybrown',
		'chk': 'green',
		'comp': '#ee5464',
		'disk': '#949413',
		'dns': 'turquoise',
		'docker_repository': '#27b8e8',
		'docker_registry': '#27b8e8',
		'docker': '#27b8e8',
		'error': 'red',
		'form': 'palevioletred',
		'fset': 'slategray',
		'info': 'slategray',
		'link': 'slategray',
		'metric': 'sandybrown',
		'moduleset': '#ee5464',
		'net': 'cadetblue',
		'node': 'cornflowerblue',
		'org': 'salmon',
		'pkg': '#cc9966',
		'priv': 'goldenrod',
		'report': 'sandybrown',
		'ruleset': '#ee5464',
		'segment': 'cadetblue',
		'service': 'seagreen',
		'stats': 'sandybrown',
		'svc': 'seagreen',
		'tag': 'darkcyan',
		'user': '#FAA272'
	},
	"app": window.location.pathname.split("/")[1]
}

if (osvc.app == "") {
        osvc.app = "init"
}

var _badIE=0

function i18n_init(callback) {
	i18n.init({
		debug: true,
		getAsync : true,
		fallbackLng: 'en',
		load:'unspecific',
		resGetPath: "/"+osvc.app+"/static/locales/__lng__/__ns__.json",
		ns: {
			namespaces: ['translation'],
			defaultNs: 'translation'
		}
	}, function() {
		$(document).i18n()
		osvc.i18n_started.resolve(true)
		if (callback) {
			callback()
		}
	})
}

function init_requirejs() {
	require.config({
		baseUrl: '/'+osvc.app+'/static/js',
		urlArgs: 'v='+osvc.code_rev,
		paths: {
			"jsyaml": "js-yaml.min",
			"vis": "vis/dist/vis.min",
			"jquery": "jquery",
			"jqplot-base": "jqplot/jquery.jqplot.min",
			"jqplot-plugins": "jqplot/plugins",
			"jqplot-plugins-highlighter": "jqplot/plugins/jqplot.highlighter.min",
			"jqplot-plugins-canvasTextRenderer": "jqplot/plugins/jqplot.canvasTextRenderer.min",
			"jqplot-plugins-canvasAxisTickRenderer": "jqplot/plugins/jqplot.canvasAxisTickRenderer.min",
			"jqplot-plugins-categoryAxisRenderer": "jqplot/plugins/jqplot.categoryAxisRenderer.min",
			"jqplot-plugins-dateAxisRenderer": "jqplot/plugins/jqplot.dateAxisRenderer.min",
			"jqplot-plugins-barRenderer": "jqplot/plugins/jqplot.barRenderer.min",
			"jqplot-plugins-ohlcRenderer": "jqplot/plugins/jqplot.ohlcRenderer.min",
			"jqplot-plugins-cursor": "jqplot/plugins/jqplot.cursor.min",
			"jqplot-plugins-enhancedLegendRenderer": "jqplot/plugins/jqplot.enhancedLegendRenderer.min",
			"jqplot-plugins-pieRenderer": "jqplot/plugins/jqplot.pieRenderer.min",
			"jqplot-plugins-donutRenderer": "jqplot/plugins/jqplot.donutRenderer.min",
			"jstree": "jstree/jstree.min",
			"ace-base": "ace/ace",
			"ace-plugins": "ace",
			"ace-plugins-keybinding-vim": "ace/keybinding-vim",
			"ace-plugins-mode-yaml": "ace/mode-yaml",
			"ace-plugins-mode-ini": "ace/mode-ini",
			"hljs": "highlight/highlight.pack"
		},
		shim: {
			"ace-plugins-keybinding-vim": {
				deps: ["ace-base"]
			},
			"ace-plugins-mode-yaml": {
				deps: ["ace-base"]
			},
			"ace-plugins-mode-ini": {
				deps: ["ace-base"]
			},
			"ace": {
				deps: [
					"ace-base",
					"ace-plugins-keybinding-vim",
					"ace-plugins-mode-yaml",
					"ace-plugins-mode-ini"
				]
			},
			"jqplot-plugins-highlighter": {
				deps: ["jqplot-base"]
			},
			"jqplot-plugins-canvasTextRenderer": {
				deps: ["jqplot-base"]
			},
			"jqplot-plugins-canvasAxisTickRenderer": {
				deps: ["jqplot-base"]
			},
			"jqplot-plugins-categoryAxisRenderer": {
				deps: ["jqplot-base"]
			},
			"jqplot-plugins-dateAxisRenderer": {
				deps: ["jqplot-base"]
			},
			"jqplot-plugins-barRenderer": {
				deps: ["jqplot-base"]
			},
			"jqplot-plugins-ohlcRenderer": {
				deps: ["jqplot-base"]
			},
			"jqplot-plugins-cursor": {
				deps: ["jqplot-base"]
			},
			"jqplot-plugins-enhancedLegendRenderer": {
				deps: ["jqplot-base"]
			},
			"jqplot-plugins-pieRenderer": {
				deps: ["jqplot-base"]
			},
			"jqplot-plugins-donutRenderer": {
				deps: ["jqplot-base"]
			},
			"jqplot": {
				deps: [
					"jqplot-base",
					"jqplot-plugins-highlighter",
					"jqplot-plugins-canvasTextRenderer",
					"jqplot-plugins-canvasAxisTickRenderer",
					"jqplot-plugins-categoryAxisRenderer",
					"jqplot-plugins-dateAxisRenderer",
					"jqplot-plugins-barRenderer",
					"jqplot-plugins-ohlcRenderer",
					"jqplot-plugins-cursor",
					"jqplot-plugins-enhancedLegendRenderer",
					"jqplot-plugins-pieRenderer",
					"jqplot-plugins-donutRenderer"
				]
			}
		}
	})
}

function app_start() {
	load_user()
	i18n_init()
	osvc.flash = flash()

	// Check if IE and version < 10
	for (i=6; i< 10; i++) {
		if (IE(i)) _badIE=1
		else _badIE=0
	}

	osvc_popup_stack_listener()

	// Wait mandatory language info and User/groups info to be loaded before creating the IHM
	$.when(
		osvc.i18n_started,
		osvc.user_loaded
	).then(function() {
		init_requirejs()
		osvc.menu = menu("menu_location")
		osvc.login = login("login_location")
		osvc.search = search("layout_search_tool")
		osvc.fset_selector = fset_selector("fset_selector")
		osvc.body_scroll = body_scroll()
		ws_init()
		app_bindings()
		app_datetime_decorators()
		osvc.app_started.resolve(true)
	})
}

function app_load_href(href, fn, options, fn_options) {
	if (!options) {
		options = {
			"disable_pushstate": false
		}
	}

	// loadable co-functions ends with '_load'
	var _href
	if (options.loadable_href) {
		_href = href
	} else {
		if (href.match(/:\/\//)) {
			// full url
			var fn_idx = 5
		} else {
			// relative url
			var fn_idx = 3
		}

		// http:, , host:port, app, ctrl, fn, arg0, arg1, ... lastarg?key=val,key=val
		var l = href.split("?")
		var v = l[0].split("/")

		v[fn_idx] += "_load"

		l[0] = v.join("/")
		_href = l.join("?")
	}

	// update browser url and history
	if (!_badIE && !options.disable_pushstate) {
		console.log("pushstate", {"fn": fn, "fn_options": fn_options}, href)
		history.pushState({"fn": fn, "fn_options": fn_options}, "", href)
	}

	var menu = $(".header .menu16")
	menu.removeClass("menu16")
	menu.parent().prepend($("<span class='fa refresh16 fa-spin'></span>"))

	// the designer view sets a height, and triggers a resizer on resize and
	// load window events, which is annoying for other views. clean-up
	$(window).off("resize")
	$(window).off("load")
	$("#layout").removeAttr("style")

	if ((fn != "undefined") && (fn !== "undefined") && fn) {
		console.log("load", fn)
		window[fn]("layout", fn_options)
		post_load()
		return
	}
	console.log("load", _href)
	$(".layout").load(_href, {}, function (responseText, textStatus, req) {
		if (textStatus == "error") {
			// load error
			console.log("fallback to location", href)
			document.location.replace(href)
		} else {
			post_load()
		}
	})

	function post_load() {
		menu.addClass("menu16")
		menu.prev(".refresh16").remove()
		osvc.menu.set_title_from_href()
		// load success, purge tables not displayed anymore
		for (tid in osvc.tables) {
			if ($('#'+tid).length == 0) {
				delete osvc.tables[tid]
				if (tid in wsh) {
					delete wsh[tid]
				}
			}
		}
	}
}

function app_bindings() {
	// Handle navigation between load()ed pages through browser tools
	$(window).on("popstate", function(e) {
		if (e.originalEvent.state !== null) {
			if (e.state && e.state.fn) {
				fn = e.state.fn
				fn_options = e.state.fn_options
			} else if (e.originalEvent && e.originalEvent.state && e.originalEvent.state.fn) {
				fn = e.originalEvent.state.fn
				fn_options = e.originalEvent.state.fn_options
			} else {
				fn = null
				fn_options = null
			}
			console.log("popstate", location.href, fn, fn_options)
			app_load_href(location.href, fn, {disable_pushstate: true}, fn_options)
			//e.preventDefault()
		}
	})

	// disable browser context menu expect on canvases (topology, ...)
	$(document).on('click', function(event){
		if(event.which == 2){
			event.preventDefault()
		}
	})
	$(document).on('contextmenu', function(event){
		if ($(event.target).is("canvas")) {
			return
		}
		event.preventDefault()
	})

	// key bindings
	$(document).keydown(function(event) {
		if (event.altKey) {
			return
		}
		var tgt = $(event.target)

		// ESC closes pop-ups and blur inputs
		if ( event.which == 27 ) {
			$("input:focus").blur()
			$("textarea:focus").blur()
			osvc.search.e_search_input.val("")
			osvc_popup_remove_from_stack()
			return
		}

		// 'TAB' from search input focuses the first visible menu_entry
		if (event.which == 9) {
			if (tgt.is('#search_input')) {
				$(".header").find(".menu_selected").removeClass("menu_selected")
				$(".header").find(".menu_entry:visible").first().addClass("menu_selected")
				$(".header").find(".search_entry").first().addClass("menu_selected")
				osvc.search.e_search_input.blur()
				event.preventDefault()
			}
			if (tgt.is("#amsearch")) {
				tgt.parent().find(".menu_selected").addClass("menu_selected")
				tgt.parent().find(".search_entry").first().addClass("menu_selected")
				tgt.blur()
				event.preventDefault()
			}
		}

		// don't honor shortcuts if a input is focused
		if ($('input').is(":focus")) {
			return
		}
		if ($('textarea').is(":focus")) {
			return
		}


		//
		// shortcuts
		//

		// 'f' for fset selector
		if ((event.which == 70) && !event.ctrlKey && !event.metaKey) {
			if (!osvc.search.e_search_input.is(":focus")) {
				event.preventDefault()
				osvc.fset_selector.open()
			}
		}

		// 's' for search
		else if (event.which == 83) {
			if (!osvc.search.e_search_input.is(":focus")) {
				event.preventDefault()
				osvc.search.e_search_input.val('')
			}
			osvc.search.e_search_input.focus()
		}

		// 'n' to open nav menu
		else if (event.which == 78) {
			event.preventDefault()
			$(".header").find(".menu_selected").removeClass("menu_selected")
			osvc.search.e_search_input.val('')
			osvc.menu.open()
		}

		// 'r' for refresh
		else if (event.which == 82 && !event.ctrlKey) {
			event.preventDefault()
			for (var id in osvc.tables) {
				osvc.tables[id].refresh()
			}
		}

		// Left
		else if (event.which == 37) {
			event.preventDefault()
			var entries = $(".header").find(".menu_entry:visible,.search_entry")
			var selected = entries.filter(".menu_selected")
			if ((selected.length > 0) && (entries.length > 1)) {
				var selected_index = entries.index(selected)
				if (selected_index == 0) {
					var next_index = entries.length - 1
				} else {
					var next_index = selected_index - 1
				}
				entries.removeClass("menu_selected")
				var new_selected = $(entries[next_index])
				new_selected.addClass("menu_selected")
			}
		}

		// Up
		else if (event.which == 38) {
			event.preventDefault()
			var entries = $(".header,.action_menu").find(".menu_entry:visible,.search_entry")
			var selected = entries.filter(".menu_selected")
			if ((selected.length > 0) && (entries.length > 0)) {
				var selected_index = entries.index(selected)
				var selected_y = selected.position().top
				var first_y = entries.first().position().top
				if (selected_y == first_y) {
					var candidate_entries = entries
				} else {
					var candidate_entries = entries.slice(0, selected_index)
				}
				if (selected.length == 0) {
					selected = entries.first()
				}
				if (candidate_entries.length == 0) {
					candidate_entries = entries
				}
				candidate_entries.filter(function(i, e){
					if ($(this).position().left == selected.position().left) {
						return true
					}
					return false
				}).last().each(function(){
					entries.removeClass("menu_selected")
					$(this).addClass("menu_selected")
					return
				})
			}
		}

		// Right
		else if (event.which == 39) {
			event.preventDefault()
			var entries = $(".header").find(".menu_entry:visible,.search_entry")
			var selected = entries.filter(".menu_selected")
			if ((selected.length > 0) && (entries.length > 1)) {
				var selected_index = entries.index(selected)
				if (selected_index == entries.length - 1) {
					var next_index = 0
				} else {
					var next_index = selected_index + 1
				}
				entries.removeClass("menu_selected")
				var new_selected = $(entries[next_index])
				new_selected.addClass("menu_selected")
			}
		}

		// Down
		else if (event.which == 40) {
			event.preventDefault()
			var entries = $(".header,.action_menu").find(".menu_entry:visible,.search_entry")
			var selected = entries.filter(".menu_selected")
			if ((selected.length > 0) && (entries.length > 0)) {
				var selected_index = entries.index(selected)
				var selected_y = selected.position().top
				var last_y = entries.last().position.top
				if (selected_y == last_y) {
					var candidate_entries = entries
				} else {
					var candidate_entries = entries.slice(selected_index+1)
				}
				if (selected.length == 0) {
					selected = entries.first()
				}
				if (candidate_entries.length == 0) {
					candidate_entries = entries
				}
				found = candidate_entries.filter(function(i, e){
					if ($(this).position().left == selected.position().left) {
						return true
					}
					return false
				}).first()
				if (found.length == 0) {
					// wrap to top
					found = entries.filter(function(i, e){
						if ($(this).position().left == selected.position().left) {
							return true
						}
						return false
					}).first()
				}
				found.each(function(){
					entries.removeClass("menu_selected")
					$(this).addClass("menu_selected")
					return
				})
			}
		}

		// 'Enter' from a menu entry does a click
		else if (is_enter(event)) {
			$(".header,.action_menu").find(".menu_selected:visible").each(function(){
				event.preventDefault()
				$(this).effect("highlight")

				e = jQuery.Event("click")
				e.ctrlKey = event.ctrlKey
				if ($(this).is(".clickable")) {
					$(this).trigger(e)
				} else {
					$(this).find(".clickable").first().trigger(e)
				}
			})
		}


		// scroll up/down to keep selected entry displayed
		var directional_events = [37, 38, 39, 40]
		if (directional_events.indexOf(event.which) >= 0) {
			var selected = entries.filter(".menu_selected")
			var container = selected.parents(".menu,.flash").first()

			if (selected.length > 0) {
				// scroll down
				var selected_y = selected.position().top + selected.outerHeight()
				var container_y = container.position().top + container.height()
				if (container_y < selected_y) {
					container.stop().animate({
						scrollTop: container.scrollTop()+selected_y-selected.outerHeight()
					}, 500)
				}

				// scroll up
				var selected_y = selected.position().top
				var container_y = container.position().top
				if (container_y > selected_y) {
					container.stop().animate({
						scrollTop: container.scrollTop() + selected_y + container_y - container.height() + selected.outerHeight()
					}, 500)
				}
			}
		}
	})
}

function app_datetime_decorators() {
	var data = {
		"date_future": cell_decorator_date_future,
		"datetime_future": cell_decorator_datetime_future,
		"datetime_weekly": cell_decorator_datetime_weekly,
		"datetime_daily": cell_decorator_datetime_daily,
		"datetime_status": cell_decorator_datetime_status,
		"datetime_no_age": cell_decorator_datetime_no_age,
		"date_no_age": cell_decorator_date_no_age
	}
	osvc.interval_datetime_decorators = setInterval(function(){
		try {
			if (osvc.datetime_decorators_running) {
				console.log("skip datetime periodic decoration because already running")
				return
			}
			osvc.datetime_decorators_running = true
			for (var key in data) {
				$("."+key).each(function() {
					cell_decorators[key]($(this))
				})
			}
			osvc.datetime_decorators_running = false
		} catch(err) {
			console.log(err)
			osvc.datetime_decorators_running = false
		}
	}, 5000)
}

function designer(divid, options) {
	require(["osvc/designer"], function() {
		designer(divid, options)
	})
}

function topology(divid, options) {
	require(["osvc/topology/topology"], function() {
		topology(divid, options)
	})
}

function startup(divid, options) {
	require(["osvc/tabs/startup"], function() {
		startup(divid, options)
	})
}

function alert_info(divid, options) {
	require(["osvc/tabs/alert_event"], function() {
		alert_info(divid, options)
	})
}

function wiki(divid, options) {
	require(["osvc/tabs/wiki"], function() {
		wiki(divid, options)
	})
}

function filterset_tabs(divid, options) {
	require(["osvc/tabs/fset"], function() {
		filterset_tabs(divid, options)
	})
}

function fset_properties(divid, options) {
	require(["osvc/tabs/fset"], function() {
		fset_properties(divid, options)
	})
}

function fset_export(divid, options) {
	require(["osvc/tabs/fset"], function() {
		fset_export(divid, options)
	})
}

function fset_designer(divid, options) {
	require(["osvc/tabs/fset"], function() {
		fset_designer(divid, options)
	})
}

function requests(divid, options) {
	require(["osvc/requests"], function() {
		requests(divid, options)
	})
}

function workflow(divid, options) {
	require(["osvc/requests"], function() {
		workflow(divid, options)
	})
}

function comp_log(divid, options) {
	require(["osvc/comp_log"], function() {
		comp_log(divid, options)
	})
}

function services_status_log(divid, options) {
	require(["osvc/services_status_log"], function() {
		services_status_log(divid, options)
	})
}

function sysrep(divid, options) {
	require(["osvc/sysreport/sysreport"], function() {
		sysrep(divid, options)
	})
}

function sysrepdiff(divid, options) {
	require(["osvc/sysreport/sysreport"], function() {
		sysrepdiff(divid, options)
	})
}

function api_doc(divid, options) {
	require(["osvc/api_doc"], function() {
		api_doc(divid, options)
	})
}

function scheduler_stats(divid, options) {
	require(["osvc/scheduler_stats"], function() {
		scheduler_stats(divid, options)
	})
}

function docker_registry_tabs(divid, options) {
	require(["osvc/tabs/docker_registry"], function() {
		docker_registry_tabs(divid, options)
	})
}

function docker_registry_properties(divid, options) {
	require(["osvc/tabs/docker_registry"], function() {
		docker_registry_properties(divid, options)
	})
}

function docker_repository_tabs(divid, options) {
	require(["osvc/tabs/docker_repository"], function() {
		docker_repository_tabs(divid, options)
	})
}

function docker_repository_properties(divid, options) {
	require(["osvc/tabs/docker_repository"], function() {
		docker_repository_properties(divid, options)
	})
}

function form_tabs(divid, options) {
	require(["osvc/tabs/form", "osvc/forms"], function() {
		form_tabs(divid, options)
	})
}

function form_properties(divid, options) {
	require(["osvc/tabs/form", "osvc/forms"], function() {
		form_properties(divid, options)
	})
}

function form_definition(divid, options) {
	require(["osvc/tabs/form", "osvc/forms"], function() {
		form_definition(divid, options)
	})
}

function safe_file_tabs(divid, options) {
	require(["osvc/tabs/safe_file"], function() {
		safe_file_tabs(divid, options)
	})
}

function safe_file_content(divid, options) {
	require(["osvc/tabs/safe_file"], function() {
		safe_file_content(divid, options)
	})
}

function safe_file_properties(divid, options) {
	require(["osvc/tabs/safe_file"], function() {
		safe_file_properties(divid, options)
	})
}

function metric_properties(divid, options) {
	require(["osvc/tabs/metric"], function() {
		metric_properties(divid, options)
	})
}

function metric_request(divid, options) {
	require(["osvc/tabs/metric"], function() {
		metric_request(divid, options)
	})
}

function metric_tabs(divid, options) {
	require(["osvc/tabs/metric"], function() {
		metric_tabs(divid, options)
	})
}

function chart_properties(divid, options) {
	require(["osvc/tabs/chart"], function() {
		chart_properties(divid, options)
	})
}

function chart_definition(divid, options) {
	require(["osvc/tabs/chart"], function() {
		chart_definition(divid, options)
	})
}

function chart_tabs(divid, options) {
	require(["osvc/tabs/chart"], function() {
		chart_tabs(divid, options)
	})
}

function report_properties(divid, options) {
	require(["osvc/tabs/report"], function() {
		report_properties(divid, options)
	})
}

function report_definition(divid, options) {
	require(["osvc/tabs/report"], function() {
		report_definition(divid, options)
	})
}

function report_tabs(divid, options) {
	require(["osvc/tabs/report"], function() {
		report_tabs(divid, options)
	})
}

function report_export(divid, options) {
	require(["osvc/tabs/report"], function() {
		report_export(divid, options)
	})
}

function moduleset_tabs(divid, options) {
	require(["osvc/tabs/modset"], function() {
		moduleset_tabs(divid, options)
	})
}

function modset_export(divid, options) {
	require(["osvc/tabs/modset"], function() {
		modset_export(divid, options)
	})
}

function modset_properties(divid, options) {
	require(["osvc/tabs/modset"], function() {
		modset_properties(divid, options)
	})
}

function prov_template_properties(divid, options) {
	require(["osvc/tabs/prov_template"], function() {
		prov_template_properties(divid, options)
	})
}

function prov_template_definition(divid, options) {
	require(["osvc/tabs/prov_template"], function() {
		prov_template_definition(divid, options)
	})
}

function prov_template_tabs(divid, options) {
	require(["osvc/tabs/prov_template"], function() {
		prov_template_tabs(divid, options)
	})
}

function quota_properties(divid, options) {
	require(["osvc/tabs/quota"], function() {
		quota_properties(divid, options)
	})
}

function quota_tabs(divid, options) {
	require(["osvc/tabs/quota"], function() {
		quota_tabs(divid, options)
	})
}

function disk_tabs(divid, options) {
	require(["osvc/tabs/disk"], function() {
		disk_tabs(divid, options)
	})
}

function disk_properties(divid, options) {
	require(["osvc/tabs/disk"], function() {
		disk_properties(divid, options)
	})
}

function array_tabs(divid, options) {
	require(["osvc/tabs/array"], function() {
		array_tabs(divid, options)
	})
}

function array_properties(divid, options) {
	require(["osvc/tabs/array"], function() {
		array_properties(divid, options)
	})
}

function diskgroup_properties(divid, options) {
	require(["osvc/tabs/diskgroup"], function() {
		diskgroup_properties(divid, options)
	})
}

function diskgroup_tabs(divid, options) {
	require(["osvc/tabs/diskgroup"], function() {
		diskgroup_tabs(divid, options)
	})
}

function dns_record_properties(divid, options) {
	require(["osvc/tabs/dns_record"], function() {
		dns_record_properties(divid, options)
	})
}

function dns_record_tabs(divid, options) {
	require(["osvc/tabs/dns_record"], function() {
		dns_record_tabs(divid, options)
	})
}

function dns_domain_properties(divid, options) {
	require(["osvc/tabs/dns_domain"], function() {
		dns_domain_properties(divid, options)
	})
}

function dns_domain_tabs(divid, options) {
	require(["osvc/tabs/dns_domain"], function() {
		dns_domain_tabs(divid, options)
	})
}

function variable_tabs(divid, options) {
	require(["osvc/tabs/variable"], function() {
		variable_tabs(divid, options)
	})
}

function actionq_tabs(divid, options) {
	require(["osvc/tabs/actionq"], function() {
		actionq_tabs(divid, options)
	})
}

function actionq_outputs(divid, options) {
	require(["osvc/tabs/actionq"], function() {
		actionq_outputs(divid, options)
	})
}

function comp_status_tabs(divid, options) {
	require(["osvc/tabs/run_status"], function() {
		comp_status_tabs(divid, options)
	})
}

function comp_log_tabs(divid, options) {
	require(["osvc/tabs/run_status"], function() {
		comp_log_tabs(divid, options)
	})
}

function run_status_ruleset(divid, options) {
	require(["osvc/tabs/run_status"], function() {
		run_status_ruleset(divid, options)
	})
}

function run_status_outputs(divid, options) {
	require(["osvc/tabs/run_status"], function() {
		run_status_outputs(divid, options)
	})
}

function ruleset_tabs(divid, options) {
	require(["osvc/tabs/ruleset"], function() {
		ruleset_tabs(divid, options)
	})
}

function ruleset_content(divid, options) {
	require(["osvc/tabs/ruleset"], function() {
		ruleset_content(divid, options)
	})
}

function ruleset_properties(divid, options) {
	require(["osvc/tabs/ruleset"], function() {
		ruleset_properties(divid, options)
	})
}

function ruleset_export(divid, options) {
	require(["osvc/tabs/ruleset"], function() {
		ruleset_export(divid, options)
	})
}

function network_properties(divid, options) {
	require(["osvc/tabs/network"], function() {
		network_properties(divid, options)
	})
}

function workflow_tabs(divid, options) {
	require(["osvc/tabs/workflow"], function() {
		workflow_tabs(divid, options)
	})
}

function workflow_derive(divid, options) {
	require(["osvc/tabs/workflow"], function() {
		workflow_derive(divid, options)
	})
}

function network_tabs(divid, options) {
	require(["osvc/tabs/network"], function() {
		network_tabs(divid, options)
	})
}

function group_properties(divid, options) {
	require(["osvc/tabs/group"], function() {
		group_properties(divid, options)
	})
}

function group_tabs(divid, options) {
	require(["osvc/tabs/group"], function() {
		group_tabs(divid, options)
	})
}

function group_hidden_menu_entries(divid, options) {
	require(["osvc/tabs/group"], function() {
		group_hidden_menu_entries(divid, options)
	})
}

function user_properties(divid, options) {
	require(["osvc/tabs/user"], function() {
		user_properties(divid, options)
	})
}

function user_tabs(divid, options) {
	require(["osvc/tabs/user"], function() {
		user_tabs(divid, options)
	})
}

function app_properties(divid, options) {
	require(["osvc/tabs/app"], function() {
		app_properties(divid, options)
	})
}

function app_tabs(divid, options) {
	require(["osvc/tabs/app"], function() {
		app_tabs(divid, options)
	})
}

function metric(divid, options) {
	require(["osvc/reports/reports"], function() {
		metric(divid, options)
	})
}

function chart(divid, options) {
	require(["osvc/reports/reports"], function() {
		chart(divid, options)
	})
}

function report(divid, options) {
	require(["osvc/reports/reports"], function() {
		report(divid, options)
	})
}

function reports(divid, options) {
	require(["osvc/reports/reports"], function() {
		reports(divid, options)
	})
}

function form(divid, options) {
	require(["osvc/forms"], function() {
		form(divid, options)
	})
}

function forms() {
	require(["osvc/forms"], function() {
		forms()
	})
}


