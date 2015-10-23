// SysReport JS Script
// MD 08062015

function sysrep_onchangebeginenddate(o)
{
    o.sysrep_timeline();
    o.sysrep_createlink();
}

function sysrep(divid, nodes, path, begin, end, cid)
{
    o = {}

    // store parameters
    o.divid = divid
    o.nodes = nodes
    o.begin = begin
    o.end = end
    o.path = path
    o.cid = cid

    o.div = $("#"+divid)

    o.sysrep_init = function(){
      return sysrep_init(this)
    }
    o.sysrep_timeline = function(){
      return sysrep_timeline(this)
    }
    o.sysrep_timeline_data = function(jd){
      return sysrep_timeline_data(this, jd)
    }
    o.sysrep_getparams = function(){
      return sysrep_getparams(this)
    }
    o.sysrep_createlink = function(){
      return sysrep_createlink(this)
    }
    o.sysrep_onchangebeginenddate = function(){
      return sysrep_onchangebeginenddate(this)
    }
    o.sysrep_admin_secure = function(){
      return sysrep_admin_secure(this)
    }
    o.sysrep_admin_allow = function(){
      return sysrep_admin_allow(this)
    }
    o.sysrep_admin_secure_handle = function(tid, func){
      return sysrep_admin_secure_handle(this, tid, func)
    }
    o.sysrep_admin_allow_handle = function(tid, func){
      return sysrep_admin_allow_handle(this, tid, func)
    }
    o.sysrep_tree_file_detail = function(item){
      return sysrep_tree_file_detail(this, item)
    }
    o.sysreport_timeline_on_select = function(item){
      return sysreport_timeline_on_select(this, item)
    }
    o.div.load('/init/static/views/sysreport.html', "", function() {o.sysrep_init()})
    return o
}

function sysrep_init(o)
{
    // initialize useful object refs to avoid DOM lookups
    o.spinner = $("#spinner")
    o.link = o.div.find("#sysrep_link")
    o.link_div = o.div.find("#sysrep_link_div")
    o.ql_link = o.div.find("#sysrep_ql_link")
    o.ql_filter = o.div.find("#sysrep_ql_filter")
    o.ql_admin = o.div.find("#sysrep_ql_admin")

    o.filter = o.div.find("#sysrep_filter")
    o.filter_begin = o.filter.find("#sysrep_filter_begindate")
    o.filter_end = o.filter.find("#sysrep_filter_enddate")
    o.filter_path = o.filter.find("#sysrep_filter_value")
    o.form_filter = o.filter.find("#sysrep_form_filter")

    o.administration = o.div.find("#sysrep_administration")
    o.form_allow = o.administration.find("#sysrep_form_allow")
    o.form_secure = o.administration.find("#sysrep_form_secure")
    o.secure_list_item = o.administration.find("#sysrep_secure_list_item")
    o.authorizations_list_item = o.administration.find("#sysrep_authorizations_list_item")
    o.secure_pattern_button = o.administration.find("#sysrep_secure_pattern_button")
    o.secure_pattern_new = o.administration.find("#sysrep_secure_pattern_new")
    o.secure_pattern_error = o.administration.find("#sysrep_secure_pattern_error")
    o.admin_allow_error = o.administration.find("#sysrep_admin_allow_error")
    o.allow_button = o.administration.find("#sysrep_allow_button")
    o.allow_filterset = o.administration.find('#sysreport_allow_filterset')
    o.allow_groups = o.administration.find('#sysreport_allow_groups')
    o.allow_pattern = o.administration.find("#sysreport_allow_pattern")

    o.timeline_title = o.div.find("#sysrep_timeline_title")
    o.timeline_graph = o.div.find("#sysrep_timeline_graph")
    o.tree_diff_detail = o.div.find("#sysrep_tree_diff_detail")
    o.tree_diff_title = o.div.find("#sysrep_tree_diff_title")
    o.tree_diff_date = o.div.find("#sysrep_tree_diff_date")
    o.tree_diff = o.div.find("#sysrep_tree_diff")
    o.tree_date = o.div.find("#sysrep_tree_date")
    o.tree_file = o.div.find("#sysrep_tree_file")
    o.tree_title = o.div.find("#sysrep_tree_title")
    o.tree = o.div.find("#sysrep_tree")

  o.div.i18n();
  o.filter_begin.datetimepicker({dateFormat:'yy-mm-dd'});
  o.filter_end.datetimepicker({dateFormat:'yy-mm-dd'});

  o.ql_link.bind("click", function() { 
    o.link_div.toggle(0, function(){o.link.select()})
  });

  o.ql_filter.on("click", function() {
    o.filter.slideToggle();
  });

  o.form_filter.on("submit", function (event) {
    event.preventDefault();
    o.sysrep_onchangebeginenddate();
  });

  o.link.bind("click", function() {
    send_link($(this).val())
  })

  // apply initial filters as default values
  if (o.begin) {
    o.filter_begin.val(o.begin)
  }
  if (o.end) {
    o.filter_end.val(o.end)
  }
  if (o.path) {
    o.filter_path.val(o.path)
  }
  if ((o.begin) || (o.end) || (o.path)) {
    o.filter.slideToggle();
  }

  o.sysrep_timeline();

  services_ismemberof("Manager", function() {
    // Authorization process
    o.ql_admin.on("click", function() {
      o.administration.slideToggle();
    });
    o.ql_admin.show();

    o.secure_pattern_button.on("click", function () {
      mul_toggle('sysrep_secure_pattern_button','sysrep_secure_pattern_add', o.divid);
    });

    o.allow_button.on("click", function () {
      mul_toggle('sysrep_allow_button','sysrep_allow_input', o.divid);
    });

    o.form_allow.on("submit", function (event) {
      event.preventDefault();
      o.sysrep_admin_allow_handle('','add')
    });

    o.form_secure.on("submit", function (event) {
      event.preventDefault();
      o.sysrep_admin_secure_handle('','add')
    });

    // Feed FilterSet
    services_osvcgetrest("G_GETFILTERSET", "", {"meta": "false", "limit": "0"}, function(jd) {
        var data = jd.data;
        for (var i=0;i<data.length;i++)
        {
          var option = $('<option />');
          option.attr('value', data[i].fset_name).text(data[i].fset_name);
          o.allow_filterset.append(option);
        }
    });

    // Feed Groups
    services_osvcgetrest("G_GETUSERSGROUPS", [], {"meta": "false", "limit": "0", "query": "not role starts with user_ and privilege=F"}, function(jd) {
        var data = jd.data;
        for (var i=0;i<data.length;i++)
        {
          if (!data[i].role.startsWith("user"))
          {
            var option = $('<option />');
            option.attr('value', data[i].role).text(data[i].role);
            o.allow_groups.append(option);
          }
        }
    });

    // Show section
    o.sysrep_admin_allow();
    o.sysrep_admin_secure();
  })
}

function sysrep_getparams(o)
{
  var data = {};
  fval = o.filter_path.val();
  if (fval != "") {
    data["path"] = fval;
  }
  fval = o.filter_begin.val();
  if (fval!="") {
    data["begin"] = fval;
  }
  fval = o.filter_end.val();
  if (fval!="") {
    data["end"] = fval;
  }
  if (o.cid) {
    data["cid"] = o.cid;
  }
  return data;
}

function send_link(url)
{
  window.open(url,'_blank')
}

function sysrep_createlink(o)
{
    url = $(location).attr("origin");
    url += services_getaccessurl("S_SYSREPVIEW");
    url += "?nodes=";
    url += o.nodes;
    var sparam = o.sysrep_getparams();
    if (Object.keys(sparam).length > 0) {
        for (key in sparam) {
            url += "&" + encodeURIComponent(key) + "=" + encodeURIComponent(sparam[key]);
        }
    }

    o.link.empty().html(url);
    o.link.autogrow({vertical: true, horizontal: true});
}

function sysrep_define_maxchanges(res)
{
  var max = 0;
  for (var d in res.stat)
  {
    var z=res.stat[d];
    var tot = z[0] + z[1];
    if (tot > max) max=tot;
  }
  return max;
}

function sysrep_timeline(o)
{
  o.timeline_title.html(i18n.t("sysrep.timeline_title", {"node": o.nodes}));
  o.sysrep_createlink();

  o.spinner.show();

  var params = o.sysrep_getparams()
  if ("cid" in params) {
    delete params.cid
  }
  params["nodes"] = o.nodes
  services_osvcgetrest("R_GETSYSREP", "", params, function(jd) {
    o.sysrep_timeline_data(jd);
  });
}

function sysrep_timeline_data(o, jd)
{
    o.timeline_graph.empty()

    // DOM element where the Timeline will be attached
    var container = o.timeline_graph[0];

    var data = jd.data;
    // Handle max lines
    var max_fpath = 5;
    for (i=0; i<jd.data.length; i++)
    {
      if (jd.data[i].stat.length > max_fpath)
      {
        var lastline = data[i].stat.length - max_fpath;
        data[i].stat = data[i].stat.slice(0, max_fpath);
        data[i].stat.push("... " + lastline + " more.");
      }
      data[i].stat[0] += '\n';
      for(j=1; j<data[i].stat.length; j++)
      {
        data[i].stat[0] += data[i].stat[j] + "\n";
      }
      data[i].stat = data[i].stat.slice(0, 1);
    }

    // Configuration for the Timeline
    var options = {
        template: function (item) {
          return '<pre style="text-align:left">' + item.stat + '</pre>';
        },
        //zoomKey: "metaKey",
        zoomable: false,
        clickToUse: false
    };

    // Create a Timeline
    var groups = []
    var groupids = []
    for (i=0; i<data.length; i++) {
        if (groupids.indexOf(data[i]['group']) >= 0) {
           continue
        }
    groupids.push(data[i]['group'])
    groups.push({
        'id': data[i]['group']
        })
    }
    if (groupids.length == 1) {
        groups = null
        }
    o.timeline = new vis.Timeline(container, data, groups, options);

    o.spinner.hide();

    if (!o.timeline_graph.is(':visible')) {
       o.timeline_graph.slideToggle();
    }

    o.timeline.on('select', function (properties) {
      var item_id = properties.items[0]
      var item = null;
      for (i=0; i<data.length; i++) 
      {
        if (data[i]['id'] == item_id) {
          item = data[i]
          break
        }
      }

      // remember the click for link generation
      o.cid = item.cid
      o.sysrep_createlink();

      o.sysreport_timeline_on_select(item)
    });

    if (o.cid) {
      for (i=0; i<data.length; i++) {
        if (data[i]['cid'] == o.cid) {
          o.timeline.setSelection(data[i]['id'])
          o.sysreport_timeline_on_select(data[i])
          break
        }
      }
    }
}

function sysreport_timeline_on_select(o, item)
{
      o.tree_diff_detail.empty();
      o.tree_file.empty();

      params = {};
      var filter_value = o.filter_path.val();
      if (filter_value != "" && filter_value != undefined) {
        params["path"] = filter_value;
      }
      // List tree Diff
      services_osvcgetrest("R_GETNODESSYSCID", [item.group, item.cid], params, function(jd) {
        // Link to tree file
        var result = jd.data;
        o.tree_diff_title.html(i18n.t("sysrep.timeline_tree_diff_title", {"node": o.nodes}));
        o.tree_diff_date.html(result.date);
        o.tree_date.html(result.date);
        i=0;
        var maximum = sysrep_define_maxchanges(result);
        var stat_width = 30;
        for (var d in result.stat)
        {
          var diff ="";
          if (result.blocks[d].secure) {
            var highlight_cl = "highlight";
          } else {
            var highlight_cl = "";
          }
          var total = result.stat[d][0] + result.stat[d][1];
          var quota = Math.round((stat_width*total)/maximum);
          if (quota == 0)
            quota = 1;
          else if (quota > total)
            quota = total;
            _inse = Math.round((result.stat[d][0]*quota)/total);
            _dele = quota-_inse;
            var stat = "<pre>"+total + " ";
            for (j=0;j<_inse;j++) stat += "+";
            for (j=0;j<_dele;j++) stat += "-";
          var value="<h2 class='clickable "+highlight_cl+"'" +
          " onclick=\"toggle('idc"+i+"');\">"+d+stat+
          "</h2>"+
          "<pre id='idc" + i + "' class='diff hljs' style='display:none'>"+result.blocks[d].diff+"</pre>";
          o.tree_diff_detail.append(value);
          o.tree_diff_detail.find("#idc" + i).each(function(i, block){
             hljs.highlightBlock(block);
           });
          i = i+1;
        }
        if (!o.tree_diff.is(':visible')) {
          o.tree_diff.slideToggle();
        }
      });
      
      // List Tree File/Cmd
      services_osvcgetrest("R_GETNODESSYSCIDTREE", [item.group,item.cid], params, function(jd) {
        // Link to tree file
        var result = jd.data;
        o.tree_title.html(i18n.t("sysrep.timeline_tree_file_title"));
        for (i=0;i<result.length;i++)
        {
          if (result[i].content_type == "command")
            cl = "action16";
          else 
            cl = "log16";

          var e = $("<h2>" + result[i].fpath + "</h2>");
          e.addClass("clickable");
          if (result[i].secure) {
            e.addClass("highlight");
          }
          e.addClass(cl);
          e.attr("_oid", result[i].oid);
          e.attr("_cid", result[i].cid);
          e.bind("click", function () {
            o.sysrep_tree_file_detail($(this));
          });
          o.tree_file.append(e);

          var e = $("<pre></pre>");
          e.addClass('diff hljs')
          e.css({"display": "none"})
          e.attr("id", result[i].oid);
          o.tree_file.append(e);
        }
        if (!o.tree.is(':visible')) {
          o.tree.slideToggle();
        }
      });
}

function sysrep_tree_file_detail(o, item)
{
  var oid = item.attr("_oid");
  var cid = item.attr("_cid");

  if (o.tree.find("#"+oid).is(':visible')) {
    toggle(oid, o.divid);
  } else { 
    services_osvcgetrest("R_GETNODESSYSCIDOID", [o.nodes, cid, oid], "", function(jd) {
      // Link to tree file
      var result = jd.data;
      o.tree.find("#"+oid).html(result.content);
      o.tree.find("#"+oid).each(function(i, block){
               hljs.highlightBlock(block);
             });
      o.tree.find("#"+oid).hide();
      toggle(oid, o.divid);
    });
  }
}

function sysrep_admin_secure(o)
{
  services_osvcgetrest("R_GETSYSREPSECPAT", "", "", function(jd) {
      o.secure_list_item.empty();
      var data = jd.data;
      for (i=0; i<data.length; i++)
      {
        var e = $("<tr><td class='button_div'><span class='del16'>" +
                  data[i].pattern +
                  "</span></td></tr>");
        var tid = data[i].id
        e.attr("id", tid)
        e.bind("click", function() {
          o.sysrep_admin_secure_handle($(this).attr("id"), 'del')
        })
        o.secure_list_item.append(e);
      }
  })  
}

function sysrep_admin_allow(o)
{
  services_osvcgetrest("R_GETSYSREPADMINALLOW", "", "", function(jd)
    {
      o.authorizations_list_item.empty();
      var data = jd.data;
      for (var i=0; i<data.length; i++)
      {
        var filter = {
          "pattern" : data[i].pattern,
          "group" : data[i].group_name,
          "filterset" : data[i].fset_name
        };
        var e = $("<tr><td class='button_div'><span class='del16'>" +
                  i18n.t("sysrep.allow_read_sentence", filter) +
                  "</span></td></tr>");
        var tid = data[i].id
        e.attr("id", tid)
        e.bind("click", function() {
          o.sysrep_admin_allow_handle($(this).attr("id"), 'del')
        })
        o.authorizations_list_item.append(e);
      }
    });
}

function sysrep_admin_secure_handle(o, tid, func)
{
  if (func=="add") {
    var value = o.secure_pattern_new.val();
    services_osvcpostrest("R_POSTSYSREPSECPAT", {"pattern": value}, function(jd) {
      if (jd.data === undefined) {
        o.secure_pattern_error.html(jd.info);
        return
      }
      o.secure_pattern_error.empty();
      o.sysrep_admin_secure();
      mul_toggle('sysrep_secure_pattern_add','sysrep_secure_pattern_button', o.divid);
    })
  } else if (func=="del") {
    var param = [];
    param.push(tid);
    services_osvcdeleterest("R_DELSYSREPSECPAT", param, function(jd) {
          var result = jd;
          o.sysrep_admin_secure();
    })  
  }
}

function sysrep_admin_allow_handle(o, tid, func)
{
  if (func=="add")
  {
    var meta_pattern = o.allow_pattern.val();
    var meta_role = o.allow_groups.val();
    var meta_fset_name = o.allow_filterset.val();
    var param = "pattern="+meta_pattern+"&group_name="+meta_role+"&fset_name="+meta_fset_name;
    services_osvcpostrest("R_POSTSYSREPADMINALLOW", param, function(jd) {
      if (jd.data === undefined)
      {
        // if info
        if (jd.info !== undefined)
          o.admin_allow_error.html(jd.info);
        else // if error
        {
          jd = JSON.parse(jd);
          o.admin_allow_error.html(jd.error);
        }
        return;
      }
      o.admin_allow_error.empty();
      o.sysrep_admin_allow();
      mul_toggle('sysrep_allow_input','sysrep_allow_button', o.divid);
    }
    )
  }
  else if (func=="del")
  {
    var param = [];
    param.push(tid);
    services_osvcdeleterest("R_DELSYSREPADMINALLOW", param, function(jd)
        {
          var result = jd;
         o.sysrep_admin_allow();
        }
  )  
  }
}
