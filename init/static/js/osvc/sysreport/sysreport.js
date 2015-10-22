// SysReport JS Script
// MD 08062015

function sysrep_onchangebeginenddate(nodes)
{
  sysrep_timeline(nodes, sysrep_getparam());
  sysrep_createlink(nodes);
}

function sysrep_init()
{
  $("#sysrep_filter_begindate").datetimepicker({dateFormat:'yy-mm-dd'});
  $("#sysrep_filter_enddate").datetimepicker({dateFormat:'yy-mm-dd'});

  $("#sysrep_ql_link").on("click", function() { 
    toggle('sysrep_link_div');$('#sysrep_link').select(); });

  $("#sysrep_ql_filter").on("click", function() { toggle('sysrep_filter'); });

  $("#sysrep_form_filter").on("submit",function (event) {
    event.preventDefault();
    sysrep_onchangebeginenddate(nodes); });

  if (services_ismemberof("Manager")) // Authorization process
  {
    $("#sysrep_ql_admin").on("click", function() { toggle('sysrep_administration'); });
    $("#sysrep_ql_admin").show();

    $("#sysrep_secure_pattern_button").on("click",function () {
      mul_toggle('sysrep_secure_pattern_button','sysrep_secure_pattern_add'); });

    $("#sysrep_allow_button").on("click",function () {
      mul_toggle('sysrep_allow_button','sysrep_allow_input'); });

    $("#sysrep_form_allow").on("submit", function (event) {
      event.preventDefault();
      sysrep_admin_allow_handle('','add') });

    $("#sysrep_form_secure").on("submit", function (event) {
      event.preventDefault();
      sysrep_admin_secure_handle('','add') });

    // Feed FilterSet
    services_osvcgetrest("G_GETFILTERSET", "", "", function(jd)
      {
        var data = jd.data;
        for (var i=0;i<data.length;i++)
        {
          var option = $('<option />');
          option.attr('value', data[i].fset_name).text(data[i].fset_name);
          $('#sysreport_allow_filterset').append(option);
        }
      });
    // Feed Groups
    services_osvcgetrest("G_GETUSERSGROUPS", [], {"meta": "false", "limit": "0", "query": "not role starts with user_ and privilege=F"}, function(jd)
      {
        var data = jd.data;
        for (var i=0;i<data.length;i++)
        {
          if (!data[i].role.startsWith("user"))
          {
            var option = $('<option />');
            option.attr('value', data[i].role).text(data[i].role);
            $('#sysreport_allow_groups').append(option);
          }
        }
      });

    // Show section
    sysrep_admin_allow();
    sysrep_admin_secure();
  }
}

function sysrep_getparam()
{
  var data = {};
  fval = $("#sysrep_filter_value").val();
  if (fval != "") {
    data["path"] = fval;
  }
  fval = $("#sysrep_filter_begindate").val();
  if (fval!="") {
    data["begin"] = fval;
  }
  fval = $("#sysrep_filter_enddate").val();
  if (fval!="") {
    data["end"] = fval;
  }
  return data;
}

function send_link(url)
{
  window.open(url,'newtab')
}

function sysrep_createlink(nodes)
{
    url = $(location).attr("origin");
    url += services_getaccessurl("S_SYSREPVIEW");
    url += "?nodes=";
    url += nodes;
    var sparam = sysrep_getparam();
    if (sparam != "") url += "&" + sparam;
    /*
    cid = $(item).parent().parent().find("[name=cid]").text();
    nodename = $(item).parent().parent().find("[name=nodename]").text();
    if (cid != "") {
      url += "&cid="+cid;
      url += "&nodename="+nodename;
    }
    */
    $("#sysrep_link").empty().html(url);
    $("#sysrep_link").autogrow({vertical: true, horizontal: true});
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

function sysrep_timeline(nodes, param)
{
    $("#sysrep_timeline_title").html(i18n.t("sysrep.timeline_title", {"node":nodes}));
    sysrep_createlink(nodes);

    $("#spinner").show();
    
    services_osvcgetrest("R_GETNODESSYS", [nodes], param, function(jd) 
    {
    $("#sysrep_timeline_graph").empty();
    // DOM element where the Timeline will be attached
    var container = document.getElementById('sysrep_timeline_graph');
    while (container.hasChildNodes()) {
      container.removeChild(container.firstChild);
    }
    var data = jd.data;
    // Handle max lines
    var max_fpath = 5;
    for (i=0;i<jd.data.length;i++)
    {
      if (jd.data[i].stat.length > max_fpath)
      {
        var lastline = (data[i].stat.length-max_fpath);
        data[i].stat = data[i].stat.slice(0,max_fpath);
        data[i].stat.push("... " + lastline + " more.");
      }
      data[i].stat[0] += '\n';
      for(j=1;j<data[i].stat.length;j++)
      {
        data[i].stat[0] += data[i].stat[j] + "\n";
      }
      data[i].stat = data[i].stat.slice(0,1);
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
    var timeline = new vis.Timeline(container, data, groups, options);

    $("#spinner").hide();

    if (!$("#sysrep_timeline_graph").is(':visible')) toggle("sysrep_timeline_graph");

    timeline.on('select', function (properties) 
    {
      var item_id = properties.items[0]
      var item = null;
      for (i=0; i<data.length; i++) 
      {
        if (data[i]['id'] == item_id) {
          item = data[i]
          break
        }
      }

      params = {};
      var filter_value = $("#sysrep_filter_value").val();
      if (filter_value != "" && filter_value != undefined)
        params["path"] = filter_value;
      // List tree Diff
      services_osvcgetrest("R_GETNODESSYSCID", [item.group,item.cid], params, function(jd) {
        // Link to tree file
        var result = jd.data;
        $("#sysrep_tree_diff_detail").empty();
        $("#sysrep_tree_diff_title").html(i18n.t("sysrep.timeline_tree_diff_title", {"node":nodes}));
        $("#sysrep_tree_diff_date").html(result.date);
        $("#sysrep_tree_date").html(result.date);
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
          var value="<h2 class='"+highlight_cl+"'" +
          " onclick=\"toggle('idc"+i+"');\">"+d+stat+
          "</h2>"+
          "<pre id='idc" + i + "' class='diff hljs' style='display:none'>"+result.blocks[d].diff+"</pre>";
          $("#sysrep_tree_diff_detail").append(value);
          $("#idc" + i).each(function(i, block){
             hljs.highlightBlock(block);
           });
          i = i+1;
        }
        if (!$("#sysrep_tree_diff").is(':visible')) toggle("sysrep_tree_diff");
      });
      
      // List Tree File/Cmd
      services_osvcgetrest("R_GETNODESSYSCIDTREE", [item.group,item.cid], params, function(jd) {
        // Link to tree file
        var result = jd.data;
        $("#sysrep_tree_file").empty();
        $("#sysrep_tree_title").html(i18n.t("sysrep.timeline_tree_file_title"));
        for (i=0;i<result.length;i++)
        {
          if (result[i].secure) {
            var cl = "highlight";
          } else {
            var cl = "";
          }
          if (result[i].content_type == "command")
            cl += " action16";
          else 
            cl += " log16";
          var value="<h2 class='"+cl+ "'" +
          " _oid='"+ result[i].oid +"' " +
          " _cid='"+ result[i].cid +"' " +
          " onclick=\"sysrep_tree_file_detail(this,'" + nodes + "')\">"+
          result[i].fpath+
          "</h2>"+
          "<pre id='" + result[i].oid + "' class='diff hljs' style='display:none'></pre>";
          $("#sysrep_tree_file").append(value);
        }
        if (!$("#sysrep_tree").is(':visible')) toggle("sysrep_tree");
      });
      }
    )
  });
}

function sysrep_tree_file_detail(item, node)
{
  var oid = item.getAttribute("_oid");
  var cid = item.getAttribute("_cid");

  if ($("#"+oid).is(':visible'))
  {
    toggle(oid);
  }
  else
  { 
      services_osvcgetrest("R_GETNODESSYSCIDOID", [node,cid,oid], "", function(jd) {
      // Link to tree file
      var result = jd.data;
      $("#"+oid).html(result.content);
      
      $("#"+oid).each(function(i, block){
               hljs.highlightBlock(block);
             });
      $("#"+oid).hide();
      toggle(oid);
      });
  }
}

function sysrep_admin_secure()
{
  services_osvcgetrest("R_GETSYSREPSECPAT", "", "", function(jd)
    {
      $("#sysrep_secure_list_item").empty();
      var data = jd.data;
      for (i=0;i<data.length;i++)
      {
        var value = "<tr id='%1' onclick=\"sysrep_admin_secure_handle('%1','del')\"><td class='button_div'>"+
        "<span class='del16'>%2</span>" +
        "</td></tr>";
        value = value.split("%1").join(data[i].id);
        value = value.split("%2").join(data[i].pattern);
        $("#sysrep_secure_list_item").append(value);
      }
    }
  )  
}

function sysrep_admin_secure_handle(tid, func)
{
  if (func=="add")
  {
    var value = $("#sysrep_secure_pattern_new").val();
    services_osvcpostrest("R_POSTSYSREPSECPAT", {"pattern": value}, function(jd) {
      if (jd.data === undefined)
      {
        $("#sysrep_secure_pattern_error").html(jd.info);
        return
      }
      $("#sysrep_secure_pattern_error").empty();
      sysrep_admin_secure();
      mul_toggle('sysrep_secure_pattern_add','sysrep_secure_pattern_button');
    }
    )
  }
  else if (func=="del")
  {
    var param = [];
    param.push(tid);
    services_osvcdeleterest("R_DELSYSREPSECPAT", param, function(jd)
        {
          var result = jd;
          sysrep_admin_secure();
        }
  )  
  }
}

function sysrep_admin_allow()
{
  services_osvcgetrest("R_GETSYSREPADMINALLOW", "", "", function(jd)
    {
      $("#sysrep_authorizations_list_item").empty();
      var data = jd.data;
      for (var i=0;i<data.length;i++)
      {
        var filter = {
          "pattern" : data[i].pattern,
          "group" : data[i].group_name,
          "filterset" : data[i].fset_name };

        var value = "<tr id='%1' onclick=\"sysrep_admin_allow_handle('%1','del')\"><td class='button_div'>"+
        "<span class='del16'> " + i18n.t("sysrep.allow_read_sentence", filter) + "</span>" +
        "</td></tr>";
        value = value.split("%1").join(data[i].id);
        $("#sysrep_authorizations_list_item").append(value);
      }
    });
}

function sysrep_admin_allow_handle(tid, func)
{
  if (func=="add")
  {
    var meta_pattern = $("#sysreport_allow_pattern").val();
    var meta_role = $("#sysreport_allow_groups").val();
    var meta_fset_name = $("#sysreport_allow_filterset").val();
    var param = "pattern="+meta_pattern+"&group_name="+meta_role+"&fset_name="+meta_fset_name;
    services_osvcpostrest("R_POSTSYSREPADMINALLOW", param, function(jd) {
      if (jd.data === undefined)
      {
        // if info
        if (jd.info !== undefined)
          $("#sysrep_admin_allow_error").html(jd.info);
        else // if error
        {
          jd = JSON.parse(jd);
          $("#sysrep_admin_allow_error").html(jd.error);
        }
        return;
      }
      $("#sysrep_admin_allow_error").empty();
      sysrep_admin_allow();
      mul_toggle('sysrep_allow_input','sysrep_allow_button');
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
          sysrep_admin_allow();
        }
  )  
  }
}
