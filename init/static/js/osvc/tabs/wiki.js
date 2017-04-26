function wiki(divid, options) {
	var o = {}
	o.options = options

	// store parameters
	o.divid = divid

	o.div = $("#"+divid)
	o.nodes = options.nodes
	o.link = {
		"fn": arguments.callee.name,
		"parameters": o.options,
		"title": "format_title",
		"title_args": {
			"fn": o.options.type+"_wiki",
			"type": o.options.type,
			"id": o.options.nodes
		}
	}

	o.wiki_insert_sign = function(){
		jQuery.fn.extend({
			insertAtCaret: function(myValue){
				return this.each(function(i) {
					if (document.selection) {
						//For browsers like Internet Explorer
						this.focus()
						sel = document.selection.createRange()
						sel.text = myValue
						this.focus()
					} else if (this.selectionStart || this.selectionStart == '0') {
						//For browsers like Firefox and Webkit based
						var startPos = this.selectionStart
						var endPos = this.selectionEnd
						var scrollTop = this.scrollTop
						this.value = this.value.substring(0,startPos)+myValue+this.value.substring(endPos,this.value.length)
						this.focus()
						this.selectionStart = startPos + myValue.length
						this.selectionEnd = startPos + myValue.length
						this.scrollTop = scrollTop
					} else {
						this.value += myValue
						this.focus()
					}
				})
			}
		})
		var currentTime = new Date()
		var ds = print_date(currentTime)
		o.wiki_tab_ins.insertAtCaret("*" + ds + " " +  _self.first_name + " " + _self.last_name + "*")
	}

	o.wiki_help = function() {
		toggle("wiki_syntax")
	}

	o.wiki_save = function() {
		var value = o.wiki_tab_ins.val()

		services_osvcpostrest("R_WIKIS", "", "", {"body": value, "name": o.nodes}, function(jd) {
			if (jd.error) {
				o.wiki_messages.html(jd.error)
				return
			}
			o.wiki_switch_edit()
		},function() {})
	}

	o.wiki_switch_edit = function() {
		if (o.wiki_tab_show.is(':visible')) {
			o.wiki_tab_show.hide()
			o.wiki_tab_insert.show()
		} else {
			o.wiki_load()
			o.wiki_tab_show.show()
			o.wiki_tab_insert.hide()
		}
	}

	o.wiki_load = function() {
		services_osvcgetrest("R_WIKIS", "", {"meta": "0", "limit": "5", "query": "name="+o.nodes}, function(jd) {
			if (jd.data === undefined) {
				return
			}
			o.wiki_messages.html('')
			var result = jd.data

			if (result == undefined || result.length ==0) {
				o.wiki_switch_edit()
				return
			}

			o.wiki_table_last_changes.empty()

			for (i=0; i<result.length; i++) {
				var line = "<tr><td class='datetime'>" + osvc_date_from_collector(result[i].saved_on) + "</td><td>"+ result[i].email +"</td></tr>"
				o.wiki_table_last_changes.append(line)
			}
			o.wiki_tab_titles.html(i18n.t("wiki.last_table_title", {"count" : i}))

			require(["markdown-converter"], function() {
				var converter = new Markdown.Converter()

				o.wiki_show_result.html(converter.makeHtml(result[0].body))
				o.wiki_tab_ins.html(result[0].body)
			})
		})
	}

	o.init = function() {
		osvc_tools(o.div, {
			"link": o.link
		})

		o.wiki_table_last_changes = o.div.find("#wiki_table_last_changes")
		o.wiki_save_button = o.div.find("#wiki_save_button")
		o.wiki_help_button = o.div.find("#wiki_help_button")
		o.wiki_insert_button = o.div.find("#wiki_insert_button")
		o.wiki_edit_button = o.div.find("#wiki_edit_button")

		o.wiki_tab_show = o.div.find("#wiki_tab_show")
		o.wiki_edit = o.div.find("#wiki_edit")
		o.wiki_editor = o.div.find("#wiki_editor")
		o.wiki_tab_insert = o.div.find("#wiki_tab_insert")

		o.wiki_tab_ins = o.div.find("#wiki_tab_ins")
		o.wiki_tab_res = o.div.find("#wiki_tab_res")

		o.wiki_table_last_changes = o.div.find("#wiki_table_last_changes")

		o.wiki_messages = o.div.find("#wiki_messages")
		o.wiki_tab_titles = o.div.find("#wiki_tab_title")

		o.wiki_show_result = o.div.find("#wiki_show_result")

		o.wiki_save_button.on("click", function () {
			o.wiki_save()
		})

		o.wiki_help_button.on("click", function () {
			o.wiki_help()
		})

		o.wiki_insert_button.on("click", function () {
			o.wiki_insert_sign()
		})

		o.wiki_edit_button.on("click", function () {
			o.wiki_switch_edit()
		})

		o.wiki_load()
	}

	o.div.load('/init/static/views/wiki.html?v='+osvc.code_rev, function() {
		o.init()
		o.div.i18n()
	})

	return o
}
