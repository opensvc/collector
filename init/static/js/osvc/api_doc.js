function api_doc(divid, path) {
	var o = {
		divid: divid,
		path: path,
		div: $("#"+divid)
	}
	var actions = [
	  "GET",
	  "DELETE",
	  "POST",
	  "PUT"
	]

	o.init = function() {
		o.div.load("/init/static/views/api_doc.html", "", function(){
			o.div.i18n()
			o.substitute_wildcards()
			o.get()
		})
	}
	o.get = function() {
		services_osvcgetrest("R_API", "", "", function(jd) {
			if (jd.error) {
				$(".flash").show("blind").html(services_error_fmt(jd))
				return
			}
			o.format(jd.data)
		},
		function(xhr, stat, error) {
			$(".flash").show("blind").html(services_ajax_error_fmt(xhr, stat, error))
		})
	}

	o.format = function(data) {
		// restructure the data to factorize by handler path
		o.table = o.div.find("[section=paths]")
		o.all_docs = {}
		for (a in data) {
			var _data = data[a]
			for (var i=0; i<_data.length; i++) {
				var handler = _data[i]
				if (!(handler.path in o.all_docs)) {
					o.all_docs[handler.path] = {}
				}
				o.all_docs[handler.path][a] = handler
			}
		}
		var urls = Object.keys(o.all_docs).sort()
		for (var i=0; i<urls.length; i++) {
			var url = urls[i]
			var d = o.all_docs[url]
			var tr = $("<tr></tr>")
			var td1 = $("<td style='width:100%'></td")
                        td1.text(url)
			o.table.append(tr)
			tr.append(td1)
			for (var j=0; j<actions.length; j++) {
				var action = actions[j]
				var td = $("<td>"+action+"</td>")
				tr.append(td)
				if (action in d) {
					td.addClass("highlight clickable")
					td.bind("click", function() {
						o.format_handler($(this))
					})
				} else {
					td.addClass("grayed")
				}
			}
		}
	}

	o.format_handler = function(e) {
		// remove all other handler areas
		o.table.find(".api_handler").remove()

		// get context from event target
		var parent_tr = e.parents("tr")
		var action = e.text()
		var path = parent_tr.children("td").first().text()
		var d = o.all_docs[path][action]

		// create our area
		var tr = $("<tr class='stackable api_handler'></tr>")
		var td = $("<td colspan='5'></td>")
		var div = $("<div class='white_float'></div>")
		div.css({"position": "initial", "margin": "1em 0 1em 0"})
		tr.insertAfter(parent_tr)
		tr.append(td)
		td.append(div)

		// format title
		var title_span = $("<span class='wf16 highlight fa-2x'></span>")
		title_span.text(path+" :: "+action)
		div.append(title_span)

		// desc
		div.append("<h2 data-i18n='api.doc.desc'></h2>")
		var t = o.format_handler_desc(d.desc)
		div.append(t)

		// params
		div.append("<h2 data-i18n='api.doc.params'></h2>")
		var t = o.format_handler_params(d.params)
		div.append(t)

		// data
		div.append("<h2 data-i18n='api.doc.data'></h2>")
		var data = d.data
		var t = o.format_handler_data(d.data)
		div.append(t)

		// examples
		div.append("<h2 data-i18n='api.doc.example'></h2>")
		var t = o.format_handler_examples(d.examples)
		if (t) {
			div.append(t)
		}

		div.i18n()
	}

	o.format_handler_desc = function(desc) {
		var converter = new Markdown.Converter()
		if (!desc) {
			desc = []
		}
		var div_desc = $("<ul></ul>")
		for (var i=0; i<desc.length; i++) {
			var p = $("<li></li>")
			p.text(desc[i])
			div_desc.append(p)
		}
		return div_desc
	}

	o.format_handler_examples = function(examples) {
		if (!examples) {
			return
		}
		var pre = $("<pre class='api_doc'></pre>")
		var s = examples.join("<br>")
		s = s.replace(/%\(collector\)s/g, window.location.host)
		s = s.replace(/%\(email\)s/g, _self.email)
		pre.text(s)
		return pre
	}

	o.format_handler_data = function(data) {
		var converter = new Markdown.Converter()
		if (!data) {
			data = {}
		}

		if (Object.keys(data).length == 0) {
			return $("<span data-i18n='api.doc.none'></span>")
		}

		// init the param | desc table
		var t = $("<table></table>")
		var tr = $("<tr></tr>")
		var td0 = $("<th></th>")
		var td1 = $("<th></th>")
		var td2 = $("<th data-i18n='api.doc.data_type'></th>")
		var td3 = $("<th data-i18n='api.doc.data_writable'></th>")
		var td4 = $("<th data-i18n='api.doc.data_unique'></th>")
		var td5 = $("<th data-i18n='api.doc.data_desc'></th>")
		t.append(tr)
		tr.append(td0)
		tr.append(td1)
		tr.append(td2)
		tr.append(td3)
		tr.append(td4)
		tr.append(td5)

		for (p in data) {
			var tr = $("<tr></tr>")
			t.append(tr)

			// data name
			var td0 = $("<td></td>")
			var span_p = $("<span class='param'></span>")
			span_p.text(p)
			td0.append(span_p)
			tr.append(td0)

			// icon
			var td1 = $("<td></td>")
			tr.append(td1)
			if (data[p].img) {
				td1.addClass(data[p].img)
			}

			// data type
			var td2 = $("<td></td>")
			tr.append(td2)
			if (data[p].type) {
				td2.text(data[p].type)
			}

			// data writeable
			var td3 = $("<td></td>")
			tr.append(td3)
			if (data[p].writeable) {
				td3.text(data[p].writeable)
			}

			// data unique
			var td4 = $("<td></td>")
			tr.append(td4)
			if (data[p].unique) {
				td4.text(data[p].unique)
			}

			// data desc
			var td5 = $("<td></td>")
			tr.append(td5)
			if (data[p].desc) {
				td5.text(data[p].desc)
			}
		}
		return t
	}

	o.format_handler_params = function(params) {
		var converter = new Markdown.Converter()
		if (!params) {
			params = {}
		}

		if (Object.keys(params).length == 0) {
			return $("<span data-i18n='api.doc.none'></span>")
		}

		// init the param | desc table
		var t = $("<table></table>")

		for (p in params) {
			var tr = $("<tr></tr>")
			t.append(tr)

			// param name
			var td_p = $("<td></td>")
			var span_p = $("<span class='param'></span>")
			span_p.text(p)
			td_p.append(span_p)
			tr.append(td_p)

			// param desc
			var td_d = $("<td></td>")
			tr.append(td_d)
			if (params[p].desc) {
				var desc = params[p].desc
				desc = desc.replace(/``(.*)``:green/g, function(a, b) {
					return "<span class='greened'>"+b+"</span>"
				})
				td_d.html(converter.makeHtml(desc))
			}
		}
		return t
	}

	o.substitute_wildcards = function() {
		o.div.find("[wildcard=collector]").each(function() {
			$(this).text(window.location.host)
		})
		o.div.find("[wildcard=email]").each(function() {
			$(this).text(_self.email)
		})
	}

	o.init()

	return o
}


