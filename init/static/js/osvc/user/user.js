
function user_groups(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid);
	o.options = options

	o.set_group = function(group_id) {
		services_osvcpostrest("R_USER_GROUP", [o.options.user_id, group_id], "", "", function(jd) {
			if (jd.error) {
				return
			}
		},function() {})
	}

	o.unset_group = function(group_id) {
		services_osvcdeleterest("R_USER_GROUP", [o.options.user_id, group_id], "", "", function(jd) {
			if (jd.error) {
				return
			}
		},function() {})
	}

	o.init = function() {
		services_osvcgetrest("R_USER_GROUPS", [o.options.user_id], {"limit": "0", "meta": "0"}, function(jd) {
			o.user_groups = {}
			for (var i=0; i<jd.data.length; i++) {
				o.user_groups[jd.data[i].role] = jd.data[i]
			}
			services_osvcgetrest("R_GROUPS", "", {"limit": "0", "meta": "0", "orderby": "role", "filters": ["role !user_%"]}, function(jd) {
				o.all_groups = jd.data
				o.div.load("/init/static/views/user_groups.html", function(){
					o.build()
				})
			}, function() {})
		}, function() {})
	}

	o.build = function() {
		o.div.i18n()
		o.org = o.div.find("#org")
		o.priv = o.div.find("#priv")
		for (var i=0; i<o.all_groups.length; i++) {
			d = o.all_groups[i]
			o.add_group(d)
		}
	}

	o.add_group = function(data) {
		var div = $("<div class='clickable'></div>")
		var input = $("<input type='checkbox' class='ocb'>")
		var label = $("<label for='checkbox'>")
		var title = $("<div></div>")
		input.attr("id", data.id)
		label.attr("for", data.id)
		title.text(d.role)
		div.append(input)
		div.append(label)
		div.append(title)

		if (data.privilege) {
			o.priv.append(div)
		} else {
			o.org.append(div)
		}

		if (data.role in o.user_groups) {
			div.children("input").prop("checked", true)
		}

		// Bind action on group tab
		input.bind("click", function () {
			if ($(this).is(":checked")) {
				o.set_group($(this).attr("id"))
			} else {
				o.unset_group($(this).attr("id"))
			}
		})
	}

	o.init()
	return o
}

function user_properties(divid, options) {
	var o = {}

	// store parameters
	o.divid = divid
	o.div = $("#"+divid);
	o.options = options

	o.init = function() {
		o.info_first_name = o.div.find("#first_name");
		o.info_last_name = o.div.find("#last_name");
		o.info_perpage = o.div.find("#perpage");
		o.info_email = o.div.find("#email");
		o.info_phone_work = o.div.find("#phone_work");
		o.info_email_log_level = o.div.find("#email_log_level");
		o.info_email_notifications = o.div.find("#email_notifications");
		o.info_im_type = o.div.find("#im_type");
		o.info_im_notifications = o.div.find("#im_notifications");
		o.info_im_log_level = o.div.find("#im_log_level");
		o.info_im_username = o.div.find("#im_username");
		o.info_domains = o.div.find("#domains");
		o.info_manager = o.div.find("#manager");
		o.info_primaryg = o.div.find("#primary_group");
		o.info_lfilter = o.div.find("#lock_filter");
		o.info_filterset = o.div.find("#filterset");

		o.load_user()
		o.load_fset()
	}

	o.load_fset = function() {
		// AutoComplete and bind filter set
		var fset = []
		services_osvcgetrest("R_FILTERSETS", "", {"limit": "0", "meta": "0", "orderby": "fset_name"}, function(jd) {
			var fsets = {"": {"id": 0, "label": ""}}
			var pg = [{"id": 0, "label": ""}]
			for (var i=0; i<jd.data.length; i++) {
				fsets[jd.data[i].fset_name] = jd.data[i]
				pg.push({
					"id": jd.data[i].id,
					"label": jd.data[i].fset_name
				})
			}
			o.info_filterset.addClass("clickable")
			o.info_filterset.hover(
				function() {
					$(this).addClass("editable")
				},
				function() {
					$(this).removeClass("editable")
				}
			)
			o.info_filterset.bind("click", function() {
				//$(this).unbind("mouseenter mouseleave click")
				if ($(this).siblings().find("form").length > 0) {
					$(this).siblings().show()
					$(this).siblings().find("input[type=text]:visible,select").focus()
					$(this).hide()
					return
				}
				var e = $("<td><form><input class='oi' type='text'></input></form></td>")
				e.css({"padding-left": "0px"})
				var input = e.find("input")
				input.uniqueId() // for date picker
				input.attr("pid", $(this).attr("id"))
				input.attr("value", $(this).text())
				input.autocomplete({
					source: pg,
					minLength: 0,
					select: function(event, ui) {
						event.preventDefault()
						o.set_filterset(ui.item.label, ui.item.id)
					}
				})
				e.find("form").submit(function(event) {
					event.preventDefault()
					var val = input.val()
					if (!(val in fsets)) {
						return
					}
					var fset_id = fsets[val].id
					o.set_filterset(val, fset_id)
				})
				input.bind("blur", function(){
					$(this).parents("td").first().siblings("td").show()
					$(this).parents("td").first().hide()
				})
				$(this).parent().append(e)
				$(this).hide()
				input.focus()
			})
		})

	}

	o.load_user = function() {
		services_osvcgetrest("R_USER", [o.options.user_id], "", function(jd) {
			o._load_user(jd.data[0])
		})
	}

	o._load_user = function(data) {
		o.info_first_name.html(data.first_name);
		o.info_last_name.html(data.last_name);
		o.info_perpage.html(data.perpage);
		o.info_email.html(data.email);
		o.info_phone_work.html(data.phone_work);
		o.info_email_log_level.html(data.email_log_level);
		o.info_im_type.html(data.im_type);
		o.info_im_username.html(data.im_username);
		o.info_im_log_level.html(data.im_log_level);

		// lock filter
		if (data.lock_filter == true) {
			o.info_lfilter.attr('class', 'toggle-on');
		} else {
			o.info_lfilter.attr('class','toggle-off');
		}
		if (data.email_notifications == true) {
			o.info_email_notifications.attr('class', 'toggle-on');
		} else {
			o.info_email_notifications.attr('class','toggle-off');
		}
		if (data.im_notifications == true) {
			o.info_im_notifications.attr('class', 'toggle-on');
		} else {
			o.info_im_notifications.attr('class','toggle-off');
		}

		services_osvcgetrest("R_USER_DOMAINS", [o.options.user_id], "", function(jd) {
			if (!jd.data || (jd.data.length == 0)) {
				return
			}
			o.info_domains.text(jd.data[0].domains)
		})

		services_osvcgetrest("R_USER_FILTERSET", [o.options.user_id], "", function(jd) {
			if (!jd.data || (jd.data.length == 0)) {
				return
			}
			o.info_filterset.text(jd.data[0].fset_name)
		})

		// modifications for privileged user
		if (services_ismemberof(["Manager","UserManager"])) {
			// lock filter
			//o.info_lfilter.addClass("clickable")
			o.info_lfilter.bind("click", function (event) {
				o.toggle_lock_filterset(this)
			});
			o.info_email_notifications.bind("click", function (event) {
				o.toggle_email_notifications(this)
			});
			o.info_im_notifications.bind("click", function (event) {
				o.toggle_im_notifications(this)
			});

			// domains
			o.info_domains.bind("keypress", function (event) {
				if (event.keyCode == 13) {
					user_update_domains(o, o.info_domains.val());
				}
			})
		}

		o.load_groups()

	}

	o.load_groups = function() {
	   	services_osvcgetrest("R_USER_PRIMARY_GROUP", [o.options.user_id], {"meta": "false", "limit": "0"}, function(jd) {
			if (jd.data.length != 1) {
				return
			}
			var current_primary = jd.data[0].role
			o.info_primaryg.text(current_primary)
		})
	   	services_osvcgetrest("R_GROUPS", [o.options.user_id], {"meta": "false", "limit": "0","query": "not role starts with user_"}, function(jd) {
			var data = jd.data;
			var pg = []
			var org_groups = {}
			var priv_groups = {}

			for (var i=0; i<data.length; i++) {
				var d = data[i]
				if (d.privilege == true) {
					priv_groups[d.role] = d
				} else {
					org_groups[d.role] = data[i]

					// for automplete
					pg.push({
						"label" : d.role,
						"id" : d.id
					})
				}
			}

			// manager
			if ("Manager" in priv_groups) {
				o.info_manager.attr('class', 'toggle-on');
			} else {
				o.info_manager.attr('class', 'toggle-off');
			}

			o.div.find("[upd]").each(function(){
				$(this).addClass("clickable")
				$(this).hover(
					function() {
						$(this).addClass("editable")
					},
					function() {
						$(this).removeClass("editable")
					}
				)
				$(this).bind("click", function() {
					//$(this).unbind("mouseenter mouseleave click")
					if ($(this).siblings().find("form").length > 0) {
						$(this).siblings().show()
						$(this).siblings().find("input[type=text]:visible,select").focus()
						$(this).hide()
						return
					}
					var updater = $(this).attr("upd")
					if ((updater == "string") || (updater == "integer") || (updater == "date") || (updater == "datetime")) {
						var e = $("<td><form><input class='oi' type='text'></input></form></td>")
						e.css({"padding-left": "0px"})
						var input = e.find("input")
						input.uniqueId() // for date picker
						input.attr("pid", $(this).attr("id"))
						input.attr("value", $(this).text())
						input.bind("blur", function(){
							$(this).parents("td").first().siblings("td").show()
							$(this).parents("td").first().hide()
						})
						$(this).parent().append(e)
						$(this).hide()
						input.focus()
						e.find("form").submit(function(event) {
							event.preventDefault()
							var input = $(this).find("input[type=text],select")
							input.blur()
							var data = {}
							data[input.attr("pid")] = input.val()
							services_osvcpostrest("R_USER", [o.options.user_id], "", data, function(jd) {
								e.hide()
								e.prev().text(input.val()).show()
							})
						})
					} else if (updater == "domains") {
						var e = $("<td><form><input class='oi' type='text'></input></form></td>")
						e.css({"padding-left": "0px"})
						var input = e.find("input")
						input.uniqueId() // for date picker
						input.attr("pid", $(this).attr("id"))
						input.attr("value", $(this).text())
						input.bind("blur", function(){
							$(this).parents("td").first().siblings("td").show()
							$(this).parents("td").first().hide()
						})
						$(this).parent().append(e)
						$(this).hide()
						input.focus()
						e.find("form").submit(function(event) {
							event.preventDefault()
							var input = $(this).find("input[type=text],select")
							input.blur()
							var data = {}
							data[input.attr("pid")] = input.val()
							services_osvcpostrest("R_USER_DOMAINS", [o.options.user_id], "", data, function(jd) {
								e.hide()
								e.prev().text(input.val()).show()
							})
						})
					} else if (updater == "im_type") {
						var e = $("<td></td>")
						var form = $("<form></form>")
						var input = $("<input class='oi' type='text'></input>")
						e.append(form)
						form.append(input)
						e.css({"padding-left": "0px"})
						input.val($(this).text())
						input.attr("pid", $(this).attr("id"))
						var opts = [
							{"label": "gtalk", "id": 1}
						]
						input.autocomplete({
							source: opts,
							minLength: 0,
							select: function(event, ui) {
								event.preventDefault()
								o.set_im_type(ui.item.label, ui.item.id);
							}
						})
						e.find("form").submit(function(event) {
							event.preventDefault()
						})
						input.bind("blur", function(){
							$(this).parents("td").first().siblings("td").show()
							$(this).parents("td").first().hide()
						})
						$(this).parent().append(e)
						$(this).hide()
						input.focus()
					} else if (updater == "primary_group") {
						var e = $("<td></td>")
						var form = $("<form></form>")
						var input = $("<input class='oi' type='text'></input>")
						e.append(form)
						form.append(input)
						e.css({"padding-left": "0px"})
						input.val($(this).text())
						input.attr("pid", $(this).attr("id"))
						input.autocomplete({
							source: pg,
							minLength: 0,
							select: function(event, ui) {
								event.preventDefault()
								o.set_primary_group(ui.item.label, ui.item.id)
							}
						})
						e.find("form").submit(function(event) {
							event.preventDefault()
							var val = input.val()
							if (!(val in org_groups)) {
								return
							}
							var group_id = org_groups[val].id
							o.set_primary_group(val, group_id)
						})
						input.bind("blur", function(){
							$(this).parents("td").first().siblings("td").show()
							$(this).parents("td").first().hide()
						})
						$(this).parent().append(e)
						$(this).hide()
						input.focus()
					}
				})
			})
		});
	}

	o.toggle_im_notifications = function() {
		if (o.info_im_notifications.hasClass("toggle-on")) {
			var data = {im_notifications: false}
		} else {
			var data = {im_notifications: true}
		}
		services_osvcpostrest("R_USER", [o.options.user_id], "", data, function(jd) {
			if (jd.error) {
				return
			}
			if (jd.data[0].im_notifications == false) {
				o.info_im_notifications.removeClass("toggle-on").addClass("toggle-off")
			} else {
				o.info_im_notifications.removeClass("toggle-off").addClass("toggle-on")
			}
		},
		function() {}
	)}

	o.toggle_email_notifications = function() {
		if (o.info_email_notifications.hasClass("toggle-on")) {
			var data = {email_notifications: false}
		} else {
			var data = {email_notifications: true}
		}
		services_osvcpostrest("R_USER", [o.options.user_id], "", data, function(jd) {
			if (jd.error) {
				return
			}
			if (jd.data[0].email_notifications == false) {
				o.info_email_notifications.removeClass("toggle-on").addClass("toggle-off")
			} else {
				o.info_email_notifications.removeClass("toggle-off").addClass("toggle-on")
			}
		},
		function() {}
	)}

	o.toggle_lock_filterset = function() {
		if (o.info_lfilter.hasClass("toggle-on")) {
			var data = {lock_filter: false}
		} else {
			var data = {lock_filter: true}
		}
		services_osvcpostrest("R_USER", [o.options.user_id], "", data, function(jd) {
			if (jd.error) {
				return
			}
			if (jd.data[0].lock_filter == false) {
				o.info_lfilter.removeClass("toggle-on").addClass("toggle-off")
			} else {
				o.info_lfilter.removeClass("toggle-off").addClass("toggle-on")
			}
		},
		function() {}
	)}

	o.set_im_type = function(label, id) {
		var domain = o.info
		services_osvcpostrest("R_USER", [o.options.user_id], "", {"im_type" : id}, function(jd) {
			if (jd.error && jd.error.length > 0) {
				return
			}
			o.info_im_type.next().hide()
			o.info_im_type.text(label).show()
		},
		function() {})
	}

	o.set_primary_group = function(label, group_id) {
		services_osvcpostrest("R_USER_PRIMARY_GROUP_SET", [o.options.user_id, group_id], "","", function(jd) {
			if (jd.error && jd.error.length > 0) {
				return
			}
			o.info_primaryg.next().hide()
			o.info_primaryg.text(label).show()
		},
		function() {})
	}

	o.set_filterset = function(label, fset_id) {
		if (fset_id == 0) {
			services_osvcdeleterest("R_USER_FILTERSET", [o.options.user_id], "","", function(jd) {
				if (jd.error && jd.error.length > 0) {
					o.info_filterset.next().hide()
					o.info_filterset.text(jd.error).show()
					return
				}
				o.info_filterset.next().hide()
				o.info_filterset.text(label).show()
			},
			function() {})
		} else {
			services_osvcpostrest("R_USER_FILTERSET_SET", [o.options.user_id, fset_id], "","", function(jd) {
				if (jd.error && jd.error.length > 0) {
					o.info_filterset.next().hide()
					o.info_filterset.text(jd.error).show()
					return
				}
				o.info_filterset.next().hide()
				o.info_filterset.text(label).show()
			},
			function() {})
		}
	}

	o.div.load("/init/static/views/user_properties.html", function() {
		o.div.i18n()
		o.init()
	})

	return o
}


