
function user(divid, options)
{
  var o = {}

  // store parameters
  o.divid = $("#"+divid);
  o.user_id = options.user_id;

  o.init = function init() {
  	return user_init(o);
  }

  o.divid.load("/init/static/views/user.html", function() {
  	o.init();
  })
}

function user_init(o)
{
	
	o.closetab = o.divid.find('.closetab');
	o.info_email = o.divid.find("#user_info_email");
	o.info_phone = o.divid.find("#user_info_phone_work");
	o.info_domains = o.divid.find("#user_info_domains");
	o.info_manager = o.divid.find("#user_info_manager");
	o.info_primaryg = o.divid.find("#user_info_primary_group");
	o.info_groups = o.divid.find("#user_info_groups");
	o.info_lfilter = o.divid.find("#user_info_lock_filter");
	o.info_filterset = o.divid.find("#user_info_filterset");
	o.close_tab_label = o.divid.find("#close_tab_label");

	o.tab_info = o.divid.find("#tab_user_info");
	o.tab_info_details = o.divid.find("#tab_user_info_detail");

	o.tab_group = o.divid.find("#tab_user_groups");
	o.tab_group_details = o.divid.find("#tab_user_groups_detail");

	o.div_user_org_group = o.divid.find("#div_user_org_groups");
	o.div_user_priv_group = o.divid.find("#div_user_priv_groups");

	o.tab_info.bind("click", function() {
		user_switch_tab(o, o.tab_info,o.tab_info_details);
	});

	o.tab_group.bind("click", function() {
		user_switch_tab(o, o.tab_group,o.tab_group_details);
	});

	o.current_tab = o.tab_info;
	o.current_tab_details = o.tab_info_details;

	o.closetab.bind("click", function () {
		o.divid.remove();
	});

	user_load_details(o);
}

function user_load_details(o)
{
	services_osvcgetrest("R_USER_DETAILS", [o.user_id], "", function(jd) {
	    var data = jd.data[0];
	    
	    o.info_email.html(data.email);
	    o.close_tab_label.html(data.fullname);
	    o.info_phone.html(data.phone_work);
	   	o.info_groups.html(data.groups);
		o.info_filterset.val(data.fset_name);

	   	if (data.domains != null) o.info_domains.val(data.domains);	
	   	if (data.primary_group !=null) o.info_primaryg.val(data.primary_group);

		//AutoComplete and bind filter set
		var fset = []
		services_osvcgetrest("R_FILTERSETS", [], {"meta": "false", "limit": "0"}, function(jd) {
		  var data = jd.data;
		  for (var i=0;i<data.length;i++) {
		    fset.push({ "label" : data[i].fset_name,"id" : data[i].id});
		  }
		  o.info_filterset.autocomplete({
		  	source: fset,
		  	minLength: 0,
		  	select: function(event, ui) {
		  	          event.preventDefault();
		  	          user_update_filter_set(o,ui.item.label,ui.item.id);
		  	      }
			});
		});

		// Bind lock filter action
		if (data.lock_filter != "F") 
	    {
	    	o.info_lfilter.attr('class','bcheck');
	    	o.info_filterset.attr("readonly","readonly");
	    }
	    else
	    {
	    	o.info_lfilter.attr('class','buncheck');
	    	o.info_filterset.bind("keypress", function (event) {
	    		if (event.keyCode == 13)
	    		{
	    			var d="here";
	    		}
	    	});
	    }

	    if (services_ismemberof(["Manager","UserManager"]))
	    {
		    // Bind domains actions
		     o.info_domains.bind("keypress", function (event) {
		    	if (event.keyCode == 13)
		    	{
		    		user_update_domains(o, o.info_domains.val());
		    	}
		    });
	     }
	     else
	     	o.info_domains.attr("readonly","readonly");

	    if (data.manager==1)
	    	o.info_manager.attr('class','bcheck');
	   	else
	   		o.info_manager.attr('class','buncheck');

	   	user_load_groups(o, data);
	});
}

function user_load_groups(o, data)
{
	group_list= data.groups;

	   	// Build group Tab
	   	services_osvcgetrest("R_GROUPS", [o.user_id], {"meta": "false", "limit": "0","query": "not role starts with user_"}, function(jd) {
	   	    var data = jd.data;
	   	    for(i=0;i<data.length;i++)
	   	    {
	   	    	user_build_group_div(o, data[i], group_list);
	   	    }

	   	   	if (services_ismemberof(["Manager","UserManager"]))
		    {
		   	    var pg =[];
		   	    // Bind Primary group automplete
				for (var i=0;i<data.length;i++) {
				  pg.push({ "label" : data[i].role,"id" : data[i].id});
				}
				o.info_primaryg.autocomplete({
				  	source: pg,
				  	minLength: 0,
				  	select: function(event, ui) {
				  	          event.preventDefault();
				  	          user_update_primary_group(o,ui.item.label,ui.item.id);
				  	      }
				});
			}
			else
				o.primary_group.attr("readonly","readonly");
	   	});
}

function user_build_group_div(o, data, list_user_group)
{
  var priv_groups = [
	  "CheckExec",
	  "CheckManager",
	  "CheckRefresh",
	  "CompExec",
	  "CompManager",
	  "DnsManager",
	  "FormsManager",
	  "Manager",
	  "NetworkManager",
	  "NodeManager",
	  "ObsManager",
	  "ProvisioningManager",
	  "StorageExec",
	  "StorageManager",
	  "TagManager",
	  "UserManager"
	];

	blist_groups = [
	  "UnaffectedProjects"
	];

	var userdiv = $("<div class='user_group'></div>");
	var div = $("<div id='role_" + data.id+ "' class='clickable'></div>");
	userdiv.append(div);

	if (list_user_group.indexOf(data.role) > 0)
		div.addClass("bcheck");
	else
		div.addClass("buncheck");

	div.append(data.role);
	
	var p = priv_groups.indexOf(data.role);
	if (p != -1)
		o.div_user_priv_group.append(userdiv);
	else
		o.div_user_org_group.append(userdiv);

	// Bind action on group tab
	var target = o.divid.find("#role_" + data.id);
	target.bind("click", function () {
		if (target.hasClass("bcheck"))
		{
			target.removeClass("bcheck");
			target.addClass("buncheck");
			user_delete_groups(o, data);
		}
		else
		{
			target.removeClass("buncheck");
			target.addClass("bcheck");
			user_update_groups(o, data);
		}
	});
}

function user_update_groups(o, data)
{
	services_osvcpostrest("R_POST_GROUPS", [o.user_id, data.id], "", "", function(jd) {
      if (jd.error) {
        return
      }
      o.info_groups.append(" " + data.role);
    },function() {});
}

function user_update_primary_group(o, label, group_id)
{
	services_osvcpostrest("R_USER_PRIMARY_GROUP", [o.user_id, group_id], "","", function(jd) {
      if (jd.error) {
        return
      }
      o.info_primaryg.val(label);
    },function() {});
}

function user_update_filter_set(o, label, filter_id)
{
	services_osvcpostrest("R_USER_PRIMARY_GROUP", [o.user_id,filter_id], "","", function(jd) {
      if (jd.error) {
        return
      }
      o.info_filterset.val(label);
    },function() {});
}

function user_update_domains(o, domain)
{
	services_osvcpostrest("R_USER_DOMAINS", [o.user_id], "", [{"domains" : domain}], function(jd) {
      if (jd.error) {
        return
      }
    },function() {});
}

function user_delete_groups(o, data)
{
	services_osvcdeleterest("R_POST_GROUPS", [o.user_id, data.id], "", "", function(jd) {
      if (jd.error) {
        return
      }
      var val = o.info_groups.html();
      val = val.replace(" " + data.role,"");
      o.info_groups.html(val);
    },function() {});
}

function user_switch_tab(o, tab, details)
{
	tab.addClass("tab_active");
	o.current_tab.removeClass("tab_active");
	o.current_tab_details.hide();
	details.show();
	o.current_tab = tab;
	o.current_tab_details = details;
}