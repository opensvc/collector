function designer(divid, options) {
	var o = {}
	o.divid = divid
	o.div = $('#'+divid)
	if (!options) {
		options = {}
	}
	o.options = options

	o.url_images = services_get_url() + "/init/static/images",
	o.url_action = services_get_url() + "/init/compliance/call/json/json_tree_action",
	o.url = services_get_url() + "/init/compliance/call/json/json_tree",

	o.short_rel = function(rel) {
		if (rel == "module") {
			return "mod"
		} else if (rel == "modset") {
			return "modset"
		} else if (rel == "filterset") {
			return "fset"
		} else if (rel == "variable") {
			return "var"
		} else if (rel == "group") {
			return "grp"
		} else if (rel == "group_pub") {
			return "grppub"
		} else if (rel == "group_resp") {
			return "grpresp"
		} else if (rel.match(/^ruleset/)) {
			return "rset"
		}
	}

	o.for_each_node = function(obj_id, obj_type, parent_obj_id, parent_obj_type, fn) {
		$(":jstree").each(function(){
			var t = $(this)
			var tree = t.jstree()
			for (node_id in tree._model.data) {
				var node = tree._model.data[node_id]
                                if (!node.li_attr) {
					continue
				}
                                if (obj_id != node.li_attr.obj_id) {
					continue
				}
				if (node.type != obj_type) {
					continue
				}
				var parent_node = tree.get_node(node.parent)
				if (!parent_node) {
					continue
				}
				if (parent_obj_id && parent_node.li_attr && (parent_node.li_attr.obj_id != parent_obj_id)) {
					continue
				}
				if (parent_obj_type && (parent_node.type != parent_obj_type)) {
					continue
				}
				fn(t, node, parent_node)
			}
		})
	}

	o.show_variable = function(node) {
		var var_id = node.li_attr.obj_id
		var rset_id = $("#"+node.parent).attr("obj_id")
		var var_name = node.text
		var div = $("<div class='white_float' style='overflow:auto;position:relative;padding:0px'></div>")
		div.uniqueId()
		o.e_info.empty().append(div)
		variable_tabs(div.attr("id"), {"variable_id": var_id, "ruleset_id":rset_id, "variable_name": var_name, "tab": "variable_tabs.content"})
	}

	o.show_moduleset = function(node) {
		var modset_name = node.text
		var div = $("<div class='white_float' style='overflow:auto;position:relative;padding:0px'></div>")
		div.uniqueId()
		o.e_info.empty().append(div)
		moduleset_tabs(div.attr("id"), {"modset_name": modset_name})
	}

	o.show_ruleset = function(node) {
		var rset_id = node.li_attr.obj_id
		var rset_name = node.text
		var div = $("<div class='white_float' style='overflow:auto;position:relative;padding:0px'></div>")
		div.uniqueId()
		o.e_info.empty().append(div)
		ruleset_tabs(div.attr("id"), {"ruleset_id": rset_id, "ruleset_name": rset_name, "tab": "ruleset_tabs.content"})
	}

	o.show_fset = function(node) {
		var fset_name = node.text
		var div = $("<div class='white_float' style='overflow:auto;position:relative;padding:0px'></div>")
		div.uniqueId()
		o.e_info.empty().append(div)
		filterset_tabs(div.attr("id"), {"fset_name": fset_name})
	}

	o.show_group = function(node) {
		var group_id = node.li_attr.obj_id
		var group_name = node.text
		var div = $("<div class='white_float' style='overflow:auto;position:relative;padding:0px'></div>")
		div.uniqueId()
		o.e_info.empty().append(div)
		group_tabs(div.attr("id"), {"group_id": group_id, "group_name": group_name})
	}

	o.show_importer = function() {
		if (!services_ismemberof("Manager", "CompManager")) {
			return
		}
		var div = $("<div id='impoprt'></div>")
		var title = $("<h3 data-i18n='designer.import'></h3>")
		var textarea = $("<textarea id='import_text' class='pre' style='width:100%;height:20em;margin-bottom:1em'></textarea>")
		var input = $("<input type='button'></input>")
		input.attr("value", i18n.t("designer.import"))
		input.bind("click", function() {
			o.comp_import()
		})
		div.append(title)
		div.append(textarea)
		div.append("<br>")
		div.append(input)
		div.i18n()
		o.e_info.html(div)
	}

	o.json_data_url = function(tree) {
		return function() {
			if (tree==2) {
				var search = o.e_search_input2
				var osearch = osvc.user_prefs.data.designer.search2
			} else {
				var search = o.e_search_input
				var osearch = osvc.user_prefs.data.designer.search
			}
			var val = search.val()
			if ((!val || (val == "")) && osearch) {
				val = osearch
				search.val(val)
			}
			var url = o.url+"?obj_filter="+encodeURIComponent(val)
			return url
		}
	}

	o.resizer = function(t) {
		if (!o.e_search_input || !o.e_close) {
			// we were triggered by an event but not fully initialized
			return
		}
		var height = $(window).height()-$(".header").outerHeight()-$(".footer").outerHeight()
		o.div.height(height)
	}

	o.monitor_doc_height = function(t) {
		// monitor doc height changes to trigger the resizer
		var lastHeight, newHeight, timer;
		try {
			lastHeight = $(document).height()
		} catch(e) {
			lastHeight = 0
		}
		(function run() {
			try {
				newHeight = $(document).height()
			} catch(e) {
				newHeight = 0
			}

			if( lastHeight != newHeight ) {
				o.resizer()
			}
			lastHeight = newHeight
			timer = setTimeout(run, 200)
		})()
	}

	o.comp_import = function(t) {
		$.ajax({
			async: false,
			type: "POST",
			url: o.url_action,
			data: {
				"operation": "import",
				"value": $("#import_text").val(),
			},
			success: function(msg){
				o.e_info.html(msg)
			}
		})
	}

	o.link = function(t) {
		var url = get_view_url()
		var re = /#$/;
		url = url.replace(re, "");
		args = "obj_filter="+encodeURIComponent($("#casearch").val())
		args += "&obj_filter2="+encodeURIComponent($("#casearch2").val())
		osvc_create_link(url, args, "link.designer");
	}
	o.set_log_op_entry = function(label, obj_type, node) {
		return designer_set_log_op_entry(o, label, obj_type, node)
	}

	o.__rename = function(data) {
		var tree = $.jstree.reference(data.reference)
		var sel = tree.get_selected()
		if (!sel.length) {
			return false
		}
		sel = sel[0]
		tree.edit(sel, null, function(node){
			var tree = $.jstree.reference(node)
			var obj_id = node.li_attr.obj_id
			var obj_rel = node.type
			var new_name = node.text
			$.ajax({
				async: false,
				type: "POST",
				url: o.url_action,
				data: {
				"operation": "rename",
				"obj_type": obj_rel,
				"obj_id": obj_id,
				"new_name": new_name
			},
			error: function(jqXHR, exception) {
				if (jqXHR.status === 0) {
					msg = 'Connection error.'
				} else if (jqXHR.status == 404) {
					msg = 'Requested page not found. [404]'
				} else if (jqXHR.status == 500) {
					msg = 'Internal Server Error [500].'
				} else if (exception === 'parsererror') {
					msg = 'Requested JSON parse failed.'
				} else if (exception === 'timeout') {
					msg = 'Time out error.'
				} else if (exception === 'abort') {
					msg = 'Ajax request aborted.'
				} else {
					msg = 'Error: ' + jqXHR.responseText
				}
				osvc.flash.error(msg)
			},
			success: function(msg){
				if (msg != "0") {
					o.json_status(msg)
				}
				o.for_each_node(obj_id, obj_rel, null, null, function(t, node) {
					t.jstree("rename_node", node, new_name)
				})
			}
			})
		})
	}

	o.__move = function(e, data) {
		if (o.suppress_event == true) {
			console.log("suppressed event", e.type, data.node.id)
			return
		}

		if (!data.original) {
			// symptom of a move_node() call not triggered by dnd
			return
		}
		o.suppress_event = true

		var tree = $.jstree.reference(data.original)
		var dst_tree = $(e.target).jstree()
		var dst_tree_id = dst_tree.element.attr("id")
		var node = data.node
		var parent_node = dst_tree.get_node(data.parent)
		var old_parent_node = tree.get_node(data.old_parent)
		var dst_id = parent_node.id
		var dst_rel = parent_node.type
		var dst_obj_id = parent_node.li_attr.obj_id
		var text = node.text
		var rel = node.type
		var id = node.id
		var obj_id = node.li_attr.obj_id
		var parent_obj_id = old_parent_node.li_attr.obj_id

		if (e.type == "move_node") {
			var operation = "move"
		} else {
			var operation = "copy"
		}

		if (dst_id == "rset_head") {
			// actually a detach
			return
		}

		$.ajax({
			async: false,
			type: "POST",
			url: o.url_action,
			data: {
				"operation": operation,
				"obj_type": rel,
				"obj_id": obj_id,
				"dst_type": dst_rel,
				"dst_id": dst_obj_id,
				"parent_obj_id": parent_obj_id,
			},
			error: function(jqXHR, exception) {
				if (jqXHR.status === 0) {
					msg = 'Connection error.'
				} else if (jqXHR.status == 404) {
					msg = 'Requested page not found. [404]'
				} else if (jqXHR.status == 500) {
					msg = 'Internal Server Error [500].'
				} else if (exception === 'parsererror') {
					msg = 'Requested JSON parse failed.'
				} else if (exception === 'timeout') {
					msg = 'Time out error.'
				} else if (exception === 'abort') {
					msg = 'Ajax request aborted.'
				} else {
					msg = 'Error: ' + jqXHR.responseText
				}
				//$.jstree.rollback(data.rlbk)
				osvc.flash.error(msg)
			},
			success: function(msg){
				try {
					new_obj_id = msg["obj_id"]
				} catch(e) {
					new_obj_id = -1
				}
				if ((msg != "0") && (new_obj_id < 0)) {
					//$.jstree.rollback(data.rlbk)
					o.json_status(msg)
					return
				}

				// if the server provided a new obj_id, replace the original's.
				if (new_obj_id > 0) {
					node.li_attr.obj_id = new_obj_id
					obj_id = new_obj_id
					var regex = new RegExp(obj_id + "$")
					id = node.id.replace(regex, new_obj_id)
				} else if (operation == "copy") {
					// ignore the jstree generated a unique id
					id = o.short_rel(node.type) + obj_id
				}
				id = parent_node.id + "_" + id.replace(/^(\w*_)*/, "")
				dst_tree.set_id(node, id)
				console.log("set copied node id to", id)

				// pop node at in every dst occurences in the trees
				o.for_each_node(dst_obj_id, dst_rel, null, null, function(t, node) {
					var this_dst_tree = t.jstree()
					var this_dst_id = node.id
					var this_dst_tree_id = t.attr("id")
					if ((this_dst_tree_id == dst_tree_id) && (this_dst_id == dst_id)) {
						return
					}
					console.log("recopy id", dst_tree_id+":"+id, "in", this_dst_tree_id+":"+this_dst_id)
					var dst_node = dst_tree.get_node(id)
					var this_dst_node = this_dst_tree.get_node(this_dst_id)
					try {
						this_dst_tree.copy_node(dst_node, this_dst_node, data.position, function(node, parent_node){
							if (!node || !parent_node) {
								return
							}
							this_dst_tree.set_id(node, parent_node.id + '_' + id.replace(/^(\w*_)*/, ""))
						})
					} catch(err) {
						console.log(err)
					}
				})

				// purge hidden rulesets from the rset_head
				if (rel.match(/hidden$/)) {
					o.for_each_node(dst_obj_id, dst_rel, "rset_head", "rset_head", function(t, node) {
						var tree = t.jstree()
						tree.delete_node(node)
					})
				}

				// purge old ruleset's filterset
				if ((rel == "filterset") && dst_rel.match(/^ruleset/)) {
					o.for_each_node(dst_obj_id, dst_rel, null, null, function(t, node) {
						var tree = t.jstree()
						for (var i=0; i<node.children.length; i++) {
							var n = tree.get_node(node.children[i])
							if (n.type == "filterset" && n.li_attr.obj_id != obj_id) {
								console.log("remove old filterset", n.id)
								tree.delete_node(n.id)
							}
						}
					})
				}

				o.suppress_event = false
			}
		})
	}

	o.__remove = function(data) {
		data.reference.each(function() {
			var tree = $.jstree.reference(this)
			node = tree.get_node(this)
			var obj_id = node.li_attr.obj_id
			var obj_rel = node.type
			if (!confirm(i18n.t("designer.warn_remove"))) {
				return
			}
			$.ajax({
				async: false,
				type: "POST",
				url: o.url_action,
				data: {
					"operation": "delete",
					"obj_type": obj_rel,
					"obj_id": obj_id,
				},
				error: function(jqXHR, exception) {
					if (jqXHR.status === 0) {
						msg = 'Connection error.'
					} else if (jqXHR.status == 404) {
						msg = 'Requested page not found. [404]'
					} else if (jqXHR.status == 500) {
						msg = 'Internal Server Error [500].'
					} else if (exception === 'parsererror') {
						msg = 'Requested JSON parse failed.'
					} else if (exception === 'timeout') {
						msg = 'Time out error.'
					} else if (exception === 'abort') {
						msg = 'Ajax request aborted.'
					} else {
						msg = 'Error: ' + jqXHR.responseText
					}
					osvc.flash.error(msg)
				},
				success: function(msg){
					if (msg != "0") {
						o.json_status(msg)
					}
					o.for_each_node(obj_id, obj_rel, null, null, function(t, node) {
						t.jstree("delete_node", node)
					})
				}
			})
		})
	}

	o.__create = function(data, new_type) {
		var ref = $.jstree.reference(data.reference)
		var sel = ref.get_selected()
		if (!sel.length) {
			console.log("no selection", ref, sel)
			return false
		}

		// create a tmp node to allow users to define the object name
		ref.create_node(sel[0], {"type": new_type}, "first", function(node){
			if (!node) {
				return
			}
			var tree = $.jstree.reference(node.id)
			$(".jstree-contextmenu").hide()

			// edit the tmp node
			tree.edit(node, null, function(node){
				var parent_node = tree.get_node(node.parent)
				var parent_id = parent_node.id
				var parent_obj_id = parent_node.li_attr.obj_id
				var parent_type = parent_node.type
				var tree_id = tree.id
				var new_data = node.text
				var new_rel = ""
				var new_rel_short = ""

				if (new_type == "module") {
					if (parent_type != "modset") {
						return
					}
					new_rel = "module"
					new_rel_short = "mod"
				} else if (new_type == "modset") {
					if ((parent_type != "modset") && (parent_id != "moduleset_head")) {
						return
					}
					new_rel = "modset"
					new_rel_short = "modset"
				} else if (new_type == "ruleset") {
					new_rel_short = "rset"
					if (parent_type != "rset_head") {
						new_rel = "ruleset_hidden"
					} else if (parent_id == "rset_head") {
						new_rel = "ruleset"
					} else {
						return
					}
				} else if (new_type == "filterset") {
					if (parent_type != "filterset_head") {
						return
					}
					new_rel = "filterset"
					new_rel_short = "fset"
				} else if (new_type == "variable") {
					if (parent_type.indexOf("ruleset") != 0) {
						return
					}
					new_rel = "variable"
					new_rel_short = "var"
				} else {
					return
				}
				$.ajax({
					async: false,
					type: "POST",
					url: o.url_action,
					data: {
						"operation": "create",
						"obj_name": new_data,
						"obj_type": new_rel,
						"parent_obj_id": parent_obj_id,
						"parent_type": parent_type
					},
					error: function(jqXHR, exception) {
						if (jqXHR.status === 0) {
							msg = 'Connection error.'
						} else if (jqXHR.status == 404) {
							msg = 'Requested page not found. [404]'
						} else if (jqXHR.status == 500) {
							msg = 'Internal Server Error [500].'
						} else if (exception === 'parsererror') {
							msg = 'Requested JSON parse failed.'
						} else if (exception === 'timeout') {
							msg = 'Time out error.'
						} else if (exception === 'abort') {
							msg = 'Ajax request aborted.'
						} else {
							msg = 'Error: ' + jqXHR.responseText
						}
						//$.jstree.rollback(data.rlbk)
						osvc.flash.error(msg)
					},
					success: function(msg){
						if (msg == "0") {
							$("[name=catree]:visible").jstree("refresh");
							return
						}
						if ((msg != "0") && !("obj_id" in msg)) {
							//$.jstree.rollback(data.rlbk)
							o.json_status(msg)
							return
						}
						var new_obj_id = msg['obj_id']
						node.li_attr.obj_id = new_obj_id
						tree.delete_node(node)

						if ((parent_id == "rset_head") || (parent_id == "fset_head") || (parent_id == "moduleset_head")) {
							var new_id = new_rel_short+new_obj_id
							$("[name=catree]").each(function(){
								var t = $(this)
								var new_id = new_rel_short+new_obj_id
								t.jstree("create_node", "#"+parent_id, {"id": new_id, "text": new_data.replace(/^\s*/, ""), "type": new_rel, "li_attr": {"obj_id": new_obj_id}}, "first")
							})
						} else {
							var new_id = parent_id+'_'+new_rel_short+new_obj_id
							$("[name=catree]").each(function(){
								var t = $(this)
								t.find("[obj_id="+parent_obj_id+"]:visible").each(function(){
									var par_id = $(this).attr("id")
									var par_node = t.jstree("get_node", par_id)
									if (par_node.type != parent_node.type) {
										return
									}
									var new_id = par_id+'_'+new_rel_short+new_obj_id
									t.jstree("create_node", "#"+par_id, {
										"id": new_id,
										"text": new_data.replace(/^\s*/, ""),
										"type": new_rel,
										"li_attr": {"obj_id": new_obj_id}
									}, "first")
								})
							})
						}
					}
				}) // end ajax call
			}) // end edit tmp node callback
		}) // end create tmp node callback
	}

	o.__select = function(e, data) {
		var rel = data.node.type
		if (data.node.id.match(/_head$/)) {
			o.show_importer()
		} else if (rel == "variable") {
			o.show_variable(data.node)
		} else if (rel.match(/^ruleset/)) {
			o.show_ruleset(data.node)
		} else if (rel.match(/^group/)) {
			o.show_group(data.node)
		} else if (rel.match(/^modset/)) {
			o.show_moduleset(data.node)
		} else if (rel.match(/^filterset/)) {
			o.show_fset(data.node)
		}
	}

	o.json_status = function(msg) {
		if ((msg == 0) || (msg == "0")) {
			return
		}
		if (!msg) {
			s = i18n.t("designer.empty_response")
		} else if ("err" in msg) {
			s = msg["err"]
		} else if ("error" in msg) {
			s = msg["error"]
		} else {
			s = ""
		}
		osvc.flash.error(s)
	}

	o.jstree_check_callback = function(operation, node, parent_node, position, more) {
		var tree = $.jstree.reference(node)
		if ((operation == "move_node") || (operation == "copy_node")) {
			if (!node || !parent_node || !parent_node.li_attr || !node.li_attr) {
				return false
			}
			if ((node.li_attr.obj_id == parent_node.li_attr.obj_id) && (node.type == parent_node.type)) {
				console.log("check_callback: disallow copy and move in self")
				return false
			}
			for (var i=0; i<parent_node.children.length; i++) {
				var child = tree.get_node(parent_node.children[i])
				if (!child || !child.li_attr) {
					continue
				}
				if ((child.li_attr.obj_id == node.li_attr.obj_id) && (child.type == node.type)) {
					console.log("check_callback: disallow copy and move, already in this parent leaf")
					return false
				}
			}
		}
		return true
	}

	o.action_set_autofix = function(data, autofix, new_type) {
		var tree = $.jstree.reference(data.reference)
		var node = tree.get_node(data.reference)
		$.ajax({
			async: false,
			type: "POST",
			url: o.url_action,
			data: {
				"operation": "set_autofix",
				"autofix": autofix,
				"obj_id": node.li_attr.obj_id,
			},
			success: function(msg){
				if ((msg != "0") && ("err" in msg)) {
					return
				}
				o.for_each_node(node.li_attr.obj_id, node.type, null, null, function(t, node) {
					var tree = t.jstree()
					tree.set_type(node.id, new_type)
				})
				o.json_status(msg)
			}
		})
	}

	o.action_detach_moduleset = function(data) {
		var tree = $.jstree.reference(data.reference)
		var node = tree.get_node(data.reference)
		var parent_node = tree.get_node(node.parent)
		var t = this
		$.ajax({
			async: false,
			type: "POST",
			url: o.url_action,
			data: {
				"operation": "detach_moduleset_from_moduleset",
				"obj_id": node.li_attr.obj_id,
				"parent_obj_id": parent_node.li_attr.obj_id,
			},
			success: function(msg){
				o.for_each_node(node.li_attr.obj_id, node.type, parent_node.li_attr.obj_id, parent_node.type, function(t, node) {
					t.jstree("delete_node", node.id)
				})
				o.json_status(msg)
			}
		})
	}

	o.action_detach_filterset = function(data) {
		var tree = $.jstree.reference(data.reference)
		var node = tree.get_node(data.reference)
		var parent_node = tree.get_node(node.parent)
		$.ajax({
			async: false,
			type: "POST",
			url: o.url_action,
			data: {
				"operation": "detach_filterset",
				"parent_obj_type": "ruleset",
				"parent_obj_id": parent_node.li_attr.obj_id
			},
			success: function(msg) {
				if ((msg != "0") && ("err" in msg)) {
					return
				}
				o.for_each_node(node.li_attr.obj_id, node.type, parent_node.li_attr.obj_id, parent_node.type, function(t, node) {
					var tree = t.jstree()
					tree.delete_node(node.id)
				})
				o.json_status(msg)
			}
		})
	}

	o.action_detach_moduleset = function(data){
		var tree = $.jstree.reference(data.reference)
		var node = tree.get_node(data.reference)
		var parent_node = tree.get_node(node.parent)
		$.ajax({
			async: false,
			type: "POST",
			url: o.url_action,
			data: {
				"operation": "detach_moduleset_from_moduleset",
				"parent_obj_type": parent_node.type,
				"parent_obj_id": parent_node.li_attr.obj_id,
				"obj_id": node.li_attr.obj_id
			},
			success: function(msg) {
				if ((msg != "0") && ("err" in msg)) {
					return
				}
				o.for_each_node(node.li_attr.obj_id, node.type, parent_node.li_attr.obj_id, parent_node.type, function(t, node) {
					var tree = t.jstree()
					tree.delete_node(node.id)
				})
				o.json_status(msg)
			}
		})
	}

	o.action_clone = function(data){
		var tree = $.jstree.reference(data.reference)
		var node = tree.get_node(data.reference)
		$.ajax({
			async: false,
			type: "POST",
			url: o.url_action,
			data: {
				"operation": "clone",
				"obj_id": node.li_attr.obj_id,
				"obj_type": node.type
			},
			success: function(msg){
				$("[name=catree]:visible").jstree("refresh");
				o.json_status(msg)
			}
		})
	}

	o.action_set_contextual = function(data) {
		var tree = $.jstree.reference(data.reference)
		var node = tree.get_node(data.reference)
		$.ajax({
			async: false,
			type: "POST",
			url: o.url_action,
			data: {
				"operation": "set_type",
				"type": "contextual",
				"obj_type": "ruleset",
				"obj_id": node.li_attr.obj_id,
			},
			success: function(msg){
				if ((msg != "0") && ("err" in msg)) {
					return
				}
				if (node.type == 'ruleset') {
					var new_type = 'ruleset_cxt'
				} else if (node.type == 'ruleset_hidden') {
					var new_type = 'ruleset_cxt_hidden'
				}
				o.for_each_node(node.li_attr.obj_id, node.type, null, null, function(t, node) {
					var tree = t.jstree()
					tree.set_type(node.id, new_type)
				})
				o.json_status(msg)
			}
		})
	}

	o.action_set_explicit = function(data){
		var tree = $.jstree.reference(data.reference)
		var node = tree.get_node(data.reference)
		$.ajax({
			async: false,
			type: "POST",
			url: o.url_action,
			data: {
				"operation": "set_type",
				"type": "explicit",
				"obj_type": "ruleset",
				"obj_id": node.li_attr.obj_id,
			},
			success: function(msg){
				if ((msg != "0") && ("err" in msg)) {
					return
				}
				if (node.type == 'ruleset_cxt') {
					var new_type = 'ruleset'
				} else if (node.type == 'ruleset_cxt_hidden') {
					var new_type = 'ruleset_hidden'
				}
				o.for_each_node(node.li_attr.obj_id, node.type, null, null, function(t, node) {
					var tree = t.jstree()
					tree.set_type(node.id, new_type)
				})
				o.json_status(msg)
			}
		})
	}

	o.action_set_public = function(data) {
		var tree = $.jstree.reference(data.reference)
		var node = tree.get_node(data.reference)
		$.ajax({
			async: false,
			type: "POST",
			url: o.url_action,
			data: {
				"operation": "set_public",
				"publication": true,
				"obj_id": node.li_attr.obj_id,
			},
			success: function(msg) {
				if ((msg != "0") && ("err" in msg)) {
					return
				}
				if (node.type == 'ruleset_cxt_hidden') {
					var new_type = 'ruleset_cxt'
				} else if (node.type == 'ruleset_hidden') {
					var new_type = 'ruleset'
				}
				o.for_each_node(node.li_attr.obj_id, node.type, null, null, function(t, node) {
					var tree = t.jstree()
					tree.set_type(node.id, new_type)
				})
				o.json_status(msg)
			}
		})
	}

	o.action_set_not_public = function(data) {
		var tree = $.jstree.reference(data.reference)
		var node = tree.get_node(data.reference)
		$.ajax({
			async: false,
			type: "POST",
			url: o.url_action,
			data: {
				"operation": "set_public",
				"publication": false,
				"obj_id": node.li_attr.obj_id,
			},
			success: function(msg){
				if ((msg != "0") && ("err" in msg)) {
					return
				}
				if (node.type == 'ruleset_cxt') {
					var new_type = 'ruleset_cxt_hidden'
				} else if (node.type == 'ruleset') {
					var new_type = 'ruleset_hidden'
				}
				o.for_each_node(node.li_attr.obj_id, node.type, null, null, function(t, node) {
					var tree = t.jstree()
					tree.set_type(node.id, new_type)
				})
				o.json_status(msg)
			}
		})
	}

	o.action_detach_ruleset_filterset = function(data) {
		var tree = $.jstree.reference(data.reference)
		var node = tree.get_node(data.reference)
		var filter_node = tree.get_node(node.children.filter(function(e){if (e.match(/fset/)){return true} else {return false}})[0])
		$.ajax({
			async: false,
			type: "POST",
			url: o.url_action,
			data: {
				"operation": "detach_filterset",
				"parent_obj_type": "ruleset",
				"parent_obj_id": node.li_attr.obj_id
			},
			success: function(msg) {
				if ((msg != "0") && ("err" in msg)) {
					return
				}
				o.for_each_node(filter_node.li_attr.obj_id, filter_node.type, node.li_attr.obj_id, node.type, function(t, node) {
					var tree = t.jstree()
					tree.delete_node(node.id)
				})
				o.json_status(msg)
			}
		})
	}

	o.action_detach_ruleset_from_moduleset = function(data) {
		var tree = $.jstree.reference(data.reference)
		var node = tree.get_node(data.reference)
		var parent_node = tree.get_node(node.parent)
		$.ajax({
			async: false,
			type: "POST",
			url: o.url_action,
			data: {
				"operation": "detach_ruleset_from_moduleset",
				"obj_id": node.li_attr.obj_id,
				"parent_obj_id": parent_node.li_attr.obj_id
			},
			success: function(msg) {
				if ((msg != "0") && ("err" in msg)) {
					return
				}
				o.suppress_event = true
				o.for_each_node(node.li_attr.obj_id, node.type, parent_node.li_attr.obj_id, parent_node.type, function(t, node, parent_node) {
					var tree = t.jstree()
					if (node.type.match(/hidden$/) && !("rset"+parent_node.li_attr.obj_id in tree._model.data)) {
						// re-attach the ruleset at head level
						tree.move_node("#"+node.id, "#rset_head")
						tree.set_id("#"+node.id, "rset"+parent_node.li_attr.obj_id)
					}
					tree.delete_node("#"+node.id)
				})
				o.suppress_event = false
				o.json_status(msg)
			}
		})
	}

	o.action_detach_ruleset_from_ruleset = function(data) {
		var tree = $.jstree.reference(data.reference)
		var node = tree.get_node(data.reference)
		var parent_node = tree.get_node(node.parent)
		$.ajax({
			async: false,
			type: "POST",
			url: o.url_action,
			data: {
				"operation": "detach_ruleset",
				"publication": false,
				"obj_id": node.li_attr.obj_id,
				"parent_obj_id": parent_node.li_attr.obj_id
			},
			success: function(msg){
				if ((msg != "0") && ("err" in msg)) {
					return
				}
				node.suppress_event = true
				o.for_each_node(node.li_attr.obj_id, node.type, parent_node.li_attr.obj_id, parent_node.type, function(t, node, parent_node) {
					var tree = t.jstree()
					if (node.type.match(/hidden$/) && !("rset"+parent_node.li_attr.obj_id in tree._model.data)) {
						// re-attach the ruleset at head level
						tree.move_node("#"+node.id, "#rset_head")
						tree.set_id("#"+node.id, "rset"+parent_node.li_attr.obj_id)
					}
					tree.delete_node("#"+node.id)
				})
				node.suppress_event = false
				o.json_status(msg)
			}
		})
	}

	o.action_set_group_responsible = function(data, set_group_responsible){
		var tree = $.jstree.reference(data.reference)
		var node = tree.get_node(data.reference)
		var parent_node = tree.get_node(node.parent)
		$.ajax({
			async: false,
			type: "POST",
			url: o.url_action,
			data: {
				"operation": set_group_responsible,
				"parent_obj_id": parent_node.li_attr.obj_id,
				"obj_id": node.li_attr.obj_id
			},
			success: function(msg) {
				if ((msg != "0") && ("err" in msg)) {
					return
				}
				var new_type = 'group_resp'
				o.for_each_node(node.li_attr.obj_id, node.type, parent_node.li_attr.obj_id, parent_node.type, function(t, node) {
					var tree = t.jstree()
					tree.set_type(node.id, new_type)
				})
				o.json_status(msg)
			}
		})
	}

	o.action_set_group_publication = function(data, set_group_publication){
		var tree = $.jstree.reference(data.reference)
		var node = tree.get_node(data.reference)
		var parent_node = tree.get_node(node.parent)
		$.ajax({
			async: false,
			type: "POST",
			url: o.url_action,
			data: {
				"operation": set_group_publication,
				"parent_obj_id": parent_node.li_attr.obj_id,
				"obj_id": node.li_attr.obj_id
			},
			success: function(msg){
				if ((msg != "0") && ("err" in msg)) {
					return
				}
				var new_type = 'group_pub'
				o.for_each_node(node.li_attr.obj_id, node.type, parent_node.li_attr.obj_id, parent_node.type, function(t, node) {
					var tree = t.jstree()
					tree.set_type(node.id, new_type)
				})
				o.json_status(msg)
			}
		})
	}

	o.action_detach_group_publication = function(data){
		var tree = $.jstree.reference(data.reference)
		var node = tree.get_node(data.reference)
		var parent_node = tree.get_node(node.parent)
		$.ajax({
			async: false,
			type: "POST",
			url: o.url_action,
			data: {
				"operation": "detach_publication_group",
				"parent_obj_type": parent_node.type,
				"parent_obj_id": parent_node.li_attr.obj_id,
				"obj_id": node.li_attr.obj_id
			},
			success: function(msg){
				if ((msg != "0") && ("err" in msg)) {
					return
				}
				o.for_each_node(node.li_attr.obj_id, node.type, parent_node.li_attr.obj_id, parent_node.type, function(t, node) {
					var tree = t.jstree()
					tree.delete_node(node.id)
				})
				o.json_status(msg)
			}
		})
	}

	o.action_detach_group_responsible = function(data){
		var tree = $.jstree.reference(data.reference)
		var node = tree.get_node(data.reference)
		var parent_node = tree.get_node(node.parent)
		$.ajax({
			async: false,
			type: "POST",
			url: o.url_action,
			data: {
				"operation": "detach_responsible_group",
				"parent_obj_type": parent_node.type,
				"parent_obj_id": parent_node.li_attr.obj_id,
				"obj_id": node.li_attr.obj_id
			},
			success: function(msg){
				if ((msg != "0") && ("err" in msg)) {
					return
				}
				o.for_each_node(node.li_attr.obj_id, node.type, parent_node.li_attr.obj_id, parent_node.type, function(t, node) {
					var tree = t.jstree()
					tree.delete_node(node.id)
				})
				o.json_status(msg)
			}
		})
	}

	o.get_var_classes = function() {
		var var_classes = {}

		function var_class_entry(var_class) {
			return {
				"label": var_class,
				"icon": "fa fa-puzzle-piece",
				"action": function(data){
					var tree = $.jstree.reference(data.reference)
					var node = tree.get_node(data.reference)
					$.ajax({
						async: false,
						type: "POST",
						url: o.url_action,
						data: {
							"operation": "set_var_class",
							"var_class": var_class,
							"obj_id": node.li_attr.obj_id,
						},
						success: function(msg){
							o.show_variable(node)
							o.json_status(msg)
						}
					})
				}
			}
		}

		for (i=0;i<o.options.var_class_names.length;i++) {
			var var_class = o.options.var_class_names[i]
			var_classes['set_var_class_'+var_class] = var_class_entry(var_class)
		}
		return var_classes
	}

	o.jstree_contextmenu_items = function(node){
		var tree = $.jstree.reference(node.parent)
		var parent_node = tree.get_node(node.parent)
		var parent_type = parent_node.type
		var var_classes = o.get_var_classes()
		h = {
			"remove" : {
				"label": i18n.t("designer.delete"),
				"icon": "fa fa-minus-square",
				"_disabled": false,
				"separator_before": false,
				"separator_after": false,
				"action": o.__remove
			},
			"rename" : {
				"label": i18n.t("designer.rename"),
				"icon": "fa fa-pencil",
				"_disabled": false,
				"separator_before": false,
				"separator_after": false,
				"action": o.__rename
			}
		}

		//
		// moduleset_head
		//
		if (node.id == "moduleset_head") {
			h["remove"]["_disabled"] = true
			h["rename"]["_disabled"] = true
			h["create"] = {
				"label": i18n.t("designer.add_moduleset"),
				"icon": "fa fa-plus-square",
				"separator_before": false,
				"separator_after": false,
				"action": function(data){
					o.__create(data, "modset")
				}
			}
		}

		//
		// filterset_head
		//
		else if (node.id == "filterset_head") {
			h["remove"]["_disabled"] = true
			h["rename"]["_disabled"] = true
			h["create"] = {
				"label": i18n.t("designer.add_filterset"),
				"icon": "fa fa-plus-square",
				"separator_before": false,
				"separator_after": false,
				"action": function(data){
					o.__create(data, "filterset")
				}
			}
		}

		//
		// ruleset_head
		//
		else if (node.id == "rset_head") {
			h["remove"]["_disabled"] = true
			h["rename"]["_disabled"] = true
			h["create"] = {
				"label": i18n.t("designer.add_ruleset"),
				"icon": "fa fa-plus-square",
				"separator_before": false,
				"separator_after": false,
				"action": function(data){
					o.__create(data, "ruleset")
				}
			}
		}


		//
		// module
		//
		else if (node.type.match(/^module/)) {
			h["autofix"] = {
				"label": i18n.t("designer.autofix"),
				"icon": "fa fa-pencil",
				"separator_before": false,
				"separator_after": false,
				"submenu": {
					"on": {
						"label": i18n.t("designer.on"),
						"icon": "fa fa-toggle-on",
						"action": function(data) {
							o.action_set_autofix(data, true, "module_autofix")
						}
					},
					"off": {
						"label": i18n.t("designer.off"),
						"icon": "fa fa-toggle-off",
						"action": function(data) {
							o.action_set_autofix(data, false, "module")
						}
					}
				}
			}
		}

		//
		// moduleset
		//
		else if (node.type=="modset") {
			h["create"] = {
				"label": i18n.t("designer.add_module"),
				"icon": "fa fa-plus-square",
				"separator_before": false,
				"separator_after": false,
				"action": function(data){
					o.__create(data, "module")
				}
			}
			h["create_modset"] = {
				"label": i18n.t("designer.add_moduleset"),
				"icon": "fa fa-plus-square",
				"separator_before": false,
				"separator_after": false,
				"action": function(data){
					o.__create(data, "modset")
				}
			}
			h["create_ruleset"] = {
				"label": i18n.t("designer.add_ruleset"),
				"icon": "fa fa-plus-square",
				"separator_before": false,
				"separator_after": false,
				"action": function(data){
					o.__create(data, "ruleset")
				}
			}
			h["clone"] = {
				"label": i18n.t("designer.clone"),
				"icon": "fa fa-copy",
				"action": o.action_clone
			}

			if (parent_type == "modset") {
				h["remove"]["_disabled"] = true
				h["detach_moduleset"] = {
					"label": i18n.t("designer.detach_moduleset"),
					"icon": "fa fa-chain-broken",
					"action": o.action_detach_moduleset
				}
			}
		}

		//
		// ruleset
		//
		else if (node.type.match(/^ruleset/)) {
			h["create"] = {
				"label": i18n.t("designer.add_variable"),
				"icon": "fa fa-plus-square",
				"separator_before": false,
				"separator_after": false,
				"action": function(data){
					o.__create(data, "variable")
				}
			}
			h["create_ruleset"] = {
				"label": i18n.t("designer.add_ruleset"),
				"icon": "fa fa-plus-square",
				"separator_before": false,
				"separator_after": false,
				"action": function(data){
					o.__create(data, "ruleset")
				}
			}
			h["clone"] = {
				"label": i18n.t("designer.clone"),
				"icon": "fa fa-copy",
				"action": o.action_clone
			}
			h["set_type"] = {
				"label": i18n.t("designer.set_type"),
				"icon": "fa fa-pencil",
				"separator_before": false,
				"separator_after": false,
				"submenu": {
					"contextual": {
						"label": i18n.t("designer.contextual"),
						"icon": "fa fa-filter",
						"action": o.action_set_contextual
					},
					"explicit": {
						"label": i18n.t("designer.explicit"),
						"icon": "fa fa-link",
						"action": o.action_set_explicit
					}
				}
			}
			h["set_publication"] = {
				"label": i18n.t("designer.set_publication"),
				"icon": "fa fa-pencil",
				"separator_before": false,
				"separator_after": false,
				"submenu": {
					"published": {
						"label": i18n.t("designer.published"),
						"icon": "fa fa-eye",
						"action": o.action_set_public
					},
					"not_published": {
						"label": i18n.t("designer.not_published"),
						"icon": "fa fa-eye-slash",
						"action": o.action_set_not_public
					}
				}
			}

			if (node.li_attr.rset_type == "contextual") {
				h["detach_filterset"] = {
					"label": i18n.t("designer.detach_filterset"),
					"icon": "fa fa-chain-broken",
					"action": o.action_detach_ruleset_filterset
				}
			}

			if (parent_type == "modset") {
				h["remove"]["_disabled"] = true
				h["detach_ruleset"] = {
					"label": i18n.t("designer.detach_ruleset"),
					"icon": "fa fa-chain-broken",
					"action": o.action_detach_ruleset_from_moduleset
				}
			}

			if (parent_type.match(/^ruleset/) && parent_node.id != "rset_head") {
				h["remove"]["_disabled"] = true
				h["detach_ruleset"] = {
					"label": i18n.t("designer.detach_ruleset"),
					"icon": "fa fa-chain-broken",
					"action": o.action_detach_ruleset_from_ruleset
				}
			}
		}

		//
		// group responsible or publication
		//
		if (node.type.match(/^group_/)) {
			h["remove"]["_disabled"] = true
			h["rename"]["_disabled"] = true
			if (parent_type.match(/^ruleset/)) {
				var set_group_publication = "set_rset_group_publication"
				var set_group_responsible = "set_rset_group_responsible"
			} else if (parent_type == "modset") {
				var set_group_publication = "set_modset_group_publication"
				var set_group_responsible = "set_modset_group_responsible"
			}
			if ((parent_type.match(/^ruleset/)) || (parent_type == "modset")) {
				h["set_gtype"] = {
					"label": i18n.t("designer.set_group_role"),
					"icon": "fa fa-pencil",
					"separator_before": false,
					"separator_after": false,
					"submenu": {
						"publication": {
							"label": i18n.t("designer.publication"),
							"icon": "fa fa-eye",
							"action": function (data) {
								o.action_set_group_publication(data, set_group_publication)
							}
						},
						"responsible": {
							"label": i18n.t("designer.responsible"),
							"icon": "fa fa-pencil",
							"action": function (data) {
								o.action_set_group_responsible(data, set_group_responsible)
							}
						}
					}
				}
			}
		}

		//
		// group responsible
		//
		if (node.type == "group_resp") {
			if (parent_type.match(/^ruleset/) || parent_type == "modset") {
				h["detach_group_responsible"] = {
					"label": i18n.t("designer.detach_responsible"),
					"icon": "fa fa-chain-broken",
					"action": o.action_detach_group_responsible
				}
			}
		}

		//
		// group publication
		//
		if (node.type == "group_pub") {
			h["remove"]["_disabled"] = true
			h["rename"]["_disabled"] = true
			if (parent_type.match(/^ruleset/) || parent_type == "modset") {
				h["detach_group_publication"] = {
					"label": i18n.t("designer.detach_publication"),
					"icon": "fa fa-chain-broken",
					"action": o.action_detach_group_publication
				}
			}
		}

		//
		// null
		//
		else if (node.type == null) {
			h["remove"]["_disabled"] = true
			h["rename"]["_disabled"] = true
		}

		//
		// table
		//
		else if (node.type=="table") {
			h["remove"]["_disabled"] = true
			h["rename"]["_disabled"] = true
		}

		//
		// variable
		//
		else if (node.type=="variable") {
			h["set_var_class"] = {
				"label": i18n.t("designer.set_variable_class"),
				"icon": "fa fa-pencil",
				"separator_before": false,
				"separator_after": false,
				"submenu": var_classes,
			}
		}

		//
		// filterset
		//
		else if ((node.type == "filterset") && parent_type.match(/^ruleset/)) {
			h["remove"]["_disabled"] = true
			h["rename"]["_disabled"] = true
			h["detach_filterset"] = {
				"label": i18n.t("designer.detach_filterset"),
				"icon": "fa fa-chain-broken",
				"action": o.action_detach_filterset
			}
		}
		//o.resizer()
		return h
	}

	o.init = function() {
		o.e_calink = o.div.find("#calink")
		o.e_close = o.div.find("#caclose")
		o.e_tree = o.div.find("#catree")
		o.e_tree_container = o.e_tree.parent()
		o.e_tree2 = o.div.find("#catree2")
		o.e_tree_container2 = o.e_tree2.parent()
		o.e_info = o.div.find("#cainfo")
		o.e_sep = o.div.find(".casep")
		o.e_search_input = o.div.find("#casearch")
		o.e_search_input2 = o.div.find("#casearch2")


		o.div.i18n()
		o.div.find("[title]").tooltipster()

		if (!osvc.user_prefs.data.designer) {
			osvc.user_prefs.data.designer = {
				"search": "",
				"search2": ""
			}
		}
		if (o.options.search) {
			osvc.user_prefs.data.designer.search = o.options.search
		}
		if (o.options.search2) {
			osvc.user_prefs.data.designer.search2 = o.options.search2
		}
		if (o.options.search2) {
			o.e_tree_container2.show(500)
		}
		o.resizer()

		o.e_calink.bind("click", function() {
			o.link()
		})

		o.e_close.bind("click", function() {
			o.div.find("[name=catree]").jstree("close_all")
			o.resizer()
		})

		o.jstree_data = {
			"search": {
				"show_only_matches": false
			},
			"dnd": {
				"always_copy": true
			},
			"plugins" : [
				"themes",
				"json_data",
				"ui",
				"contextmenu",
				"dnd",
				"types",
				//"hotkeys",
				"cookies",
				"search",
				"adv_search"
			],
			"types": {
				"#": {
					"valid_children": [],
				},
				"default": {
					"valid_children": [],
				},
					"moduleset_head": {
					"valid_children": ["modset"]
				},
					"ruleset_head": {
					"valid_children": ["ruleset", "ruleset_cxt", "ruleset_hidden", "ruleset_cxt_hidden"]
				},
				"module": {
					"valid_children": [],
					"icon": o.url_images+"/action16.png"
				},
				"module_autofix": {
					"valid_children": [],
					"icon": o.url_images+"/actionred16.png"
				},
				"modset": {
					"valid_children": ["module", "module_autofix", "modset", "ruleset", "ruleset_cxt", "ruleset_hidden", "ruleset_cxt_hidden", "group", "group_pub", "group_resp"],
					"icon": o.url_images+"/modset16.png"
				},
				"group": {
					"valid_children": [],
					"icon": o.url_images+"/guys16.png"
				},
				"group_pub": {
					"valid_children": [],
					"icon": o.url_images+"/guys16.png"
				},
				"group_resp": {
					"valid_children": [],
					"icon": o.url_images+"/admins16.png"
				},
				"filterset": {
					"valid_children": [],
					"icon": o.url_images+"/filter16.png"
				},
				"ruleset": {
					"valid_children": ["ruleset", "ruleset_cxt", "ruleset_hidden", "ruleset_cxt_hidden", "group", "group_pub", "group_resp", "variable"],
					"icon": o.url_images+"/pkg16.png"
				},
				"ruleset_hidden": {
					"valid_children": ["ruleset", "ruleset_cxt", "ruleset_hidden", "ruleset_cxt_hidden", "group", "group_pub", "group_resp", "variable"],
					"icon": o.url_images+"/pkglight16.png"
				},
				"ruleset_cxt": {
					"valid_children": ["ruleset", "ruleset_cxt", "ruleset_hidden", "ruleset_cxt_hidden", "group", "group_pub", "group_resp", "variable", "filterset"],
					"icon": o.url_images+"/rsetcxt16.png"
				},
				"ruleset_cxt_hidden": {
					"valid_children": ["ruleset", "ruleset_cxt", "ruleset_hidden", "ruleset_cxt_hidden", "group", "group_pub", "group_resp", "variable", "filterset"],
					"icon": o.url_images+"/rsetcxtlight16.png"
				},
				"variable": {
					"valid_children": [],
					"icon": o.url_images+"/comp16.png"
				}
			},
			"core" : {
				"check_callback" : o.jstree_check_callback,
				"data" : {
					"url" : o.json_data_url(),
					"data" : function(node) {
						if (node.id == "#") {
							return {}
						} else {
							return {"obj_id": node.li_attr.obj_id, "obj_type": node.type}
						}
					}
				}
			},
			"contextmenu": {
				"items": o.jstree_contextmenu_items
			}
		}

		o.monitor_doc_height();

		o.e_tree.jstree(o.jstree_data)
			//.bind("move_node.jstree", o.__move)
			.bind("copy_node.jstree", o.__move)
			.bind("select_node.jstree", o.__select)

		o.jstree_data["cookies"] = {
			"save_opened": "jstree_open2",
			"save_selected": "jstree_select2",
		}
		o.jstree_data["core"]["data"]["url"] = o.json_data_url(2)

		o.e_tree2.jstree(o.jstree_data)
			//.bind("move_node.jstree", o.__move)
			.bind("copy_node.jstree", o.__move)
			.bind("select_node.jstree", o.__select)


		o.e_search_input.keyup(function(event){
			if (is_enter(event)) {
				osvc.user_prefs.data.designer.search = $(this).val()
				osvc.user_prefs.save()
				$("#catree:visible").jstree("refresh");
			}
		})
		o.e_search_input2.keyup(function(event){
			if (is_enter(event)) {
				osvc.user_prefs.data.designer.search2 = $(this).val()
				osvc.user_prefs.save()
				$("#catree2:visible").jstree("refresh");
			}
		})

		// tree width change when dragging the separator
		o.e_sep.mousedown(function(){
			$("body").addClass("noselect")
			var tree = $(this).prev()
			var ini_x = event.pageX
			var ini_w = tree.width()
			$(document).bind("mousemove", function(){
				tree.css({"width": ini_w+event.pageX-ini_x})
			})
		})
		$(document).mouseup(function(){
			$("body").removeClass("noselect")
			$(document).unbind("mousemove")
		})

		// double click on the separator opens the 2nd tree
		o.e_sep.dblclick(function(){
			o.e_tree_container2.toggle()
			o.e_tree_container2.next().toggle()
			o.e_tree_container2.find("#catree2:visible").jstree("refresh");
		})

		$(window).bind("resize", o.resizer)
		$(window).bind("load", o.resizer)
		o.resizer()
	}



	o.div.load('/init/static/views/designer.html?v='+osvc.code_rev, function() {
		o.init()
	})
	return o
}


