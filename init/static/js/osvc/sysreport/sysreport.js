// SysReport JS Script
// MD 08062015

function sysreport_trad()
{  
  $('#sysreport').i18n();
}

function sysreport_onchangebeginenddate(nodes)
{
  sysrep_timeline(nodes,sysreport_getparam());
  sysreport_createlink(nodes);
}

function sysrep_binding()
{
  $("#sysrep_filter_begindate").datetimepicker({dateFormat:'yy-mm-dd'});
  $("#sysrep_filter_enddate").datetimepicker({dateFormat:'yy-mm-dd'});
}

function sysreport_getparam()
{
  var url ="";
  fval = $("#sysrep_filter_value").val();
  if (fval!="") {
    url += "&path="+fval;
  }
  fval = $("#sysrep_filter_begindate").val();
  if (fval!="") {
    url += "&begin="+fval;
  }
  fval = $("#sysrep_filter_enddate").val();
  if (fval!="") {
    url += "&end="+fval;
  }
  return url.substring(1,url.length);  
}

function send_link(url)
{
  window.open(url,'newtab')
}

function sysreport_createlink(nodes)
{
    url = $(location).attr("origin");
    url += services_getaccessurl("S_SYSREPVIEW");
    url += "?nodes=";
    url += nodes;
    var sparam = sysreport_getparam();
    if (sparam != "") url += "&" + sparam;
    /*
    cid = $(item).parent().parent().find("[name=cid]").text();
    nodename = $(item).parent().parent().find("[name=nodename]").text();
    if (cid != "") {
      url += "&cid="+cid;
      url += "&nodename="+nodename;
    }
    */
    //var vurl = "<a href='"+url+"' target='_blank'>"+url+"</a>";
    $("#sysrep_link").empty().html(url);

    $("#sysrep_link").autogrow({vertical: true, horizontal: true});
}

function sysrep_timeline(nodes,param)
{
    $("#sysreport_timeline_title").html("Node "+nodes+" changes timeline");
    sysreport_createlink(nodes);

    $("#spinner").show();
    
    services_osvcgetrest("R_GETNODESSYS",[nodes],param, function(jd) 
    {
    $("#sysreport_timeline").empty();
    // DOM element where the Timeline will be attached
    var container = document.getElementById('sysreport_timeline');
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
      }/*
    _data = {
     'cid': item.cid,
     'nodename': item.group,
     'path': $("#"+id).parents("[name=sysrep_top]").find("input[name=filter]").val()
    }*/
      // List tree Diff
      services_osvcgetrest("R_GETNODESSYSCID",[item.group,item.cid],"",function(jd){
          // Link to tree file
          var result = jd.data;
          $("#sysreport_tree_diff_detail").empty();
          $("#sysreport_tree_diff_title").html("Changement du noeud " + nodes);
          $("#sysreport_tree_diff_date").html(result.date);
          i=0;
            for (var d in result.stat)
            {
              var z = d;

            var value="<h2 class='highlight clickable'"+
            " onclick=\"toggle('idc"+i+"');\">"+d+
            "</h2>"+
            "<pre id='idc" + i + "' class='diff hljs' style='display:none'>"+result.blocks[d].diff+"</pre>";
            $("#sysreport_tree_diff_detail").append(value);
            $("#idc" + i).each(function(i, block){
               hljs.highlightBlock(block);
             });
            i=i+1;
          }
           $("#sysreport_tree_diff").show();
          });
      
  
      // List Tree File/Cmd
      services_osvcgetrest("R_GETNODESSYSCIDTREE",[item.group,item.cid],"",function(jd){
          // Link to tree file
          var result = jd.data;
          $("#sysreport_tree_file").empty();
          $("#sysreport_tree_title").html("Fichiers");
          $("#sysreport_tree_date").html(result.date);
          for (i=0;i<result.length;i++)
          {
            var cl="";
            if (result[i].content_type == "file")
              cl = "highlight";
            else if (result[i].content_type == "command")
              cl = "action16";
            else 
              cl = "log16";
            var value="<h2 class='"+cl+" clickable'"+
            " _oid='"+ result[i].oid +"' " +
            " _cid='"+ result[i].cid +"' " +
            " onclick=\"sysreport_tree_file_detail(this,'" + nodes + "')\">"+
            "<pre>"+result[i].fpath+"</pre>"+
            "</h2>"+
            "<pre id='" + result[i].oid + "' class='diff hljs' style='display:none'></pre>";
            $("#sysreport_tree_file").append(value);
          }
           $("#sysreport_tree").show();
          });
      }
    )
  });
}

function sysreport_tree_file_detail(item,node)
{
  var oid = item.getAttribute("_oid");
  var cid = item.getAttribute("_cid");

  if ($("#"+oid).is(':visible'))
  {
    toggle(oid);
  }
  else
  { 
      services_osvcgetrest("R_GETNODESSYSCIDOID",[node,cid,oid],"",function(jd) {
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

function sysreport_admin_secure()
{
  services_osvcgetrest("R_GETSYSREPSECPAT","","",function(jd)
    {
      $("#sysreport_secure_list_item").empty();
      var data = jd.data;
      for (i=0;i<data.length;i++)
      {
        var value = "<tr id='%1' onclick=\"sysrep_admin_secure_handle('%1','del')\"><td>%2</td></tr>";
        value = value.split("%1").join(data[i].id);
        value = value.split("%2").join(data[i].pattern);
        $("#sysreport_secure_list_item").append(value);
      }
    }
  )  
}

function sysrep_admin_secure_handle(tid,func)
{
  if (func=="add")
  {
    var value = $("#sysreport_secure_patern_new").val();
    services_osvcpostrest("R_POSTSYSREPSECPAT","pattern="+value,function(jd) {
      if (jd.data === undefined)
      {
        $("#sysrep_secure_pattern_error").html(jd.info);
        return
      }
      $("#sysrep_secure_pattern_error").empty();
      sysreport_admin_secure();
      mul_toggle('sysrep_secure_pattern_add','sysrep_secure_pattern_button');
    }
    )
  }
  else if (func=="del")
  {
    var param = [];
    param.push(tid);
    services_osvcdeleterest("R_DELSYSREPSECPAT",param,function(jd)
        {
          var result = jd;
          sysreport_admin_secure();
        }
  )  
  }
}

function sysreport_admin_allow()
{
  services_osvcgetrest("R_GETSYSREPADMINALLOW","","",function(jd)
    {
      $("#sysreport_authorizations_list_item").empty();
      var data = jd.data;
      for (var i=0;i<data.length;i++)
      {
        var filter = {
          "pattern" : data[i].pattern,
          "group" : data[i].group_name,
          "filterset" : data[i].fset_name};

        var value = "<tr id='%1' onclick=\"sysrep_admin_allow_handle('%1','del')\"><td>"+
        i18n.t("sysrep.allow_read_sentence", filter) +
        "</td></tr>";
        value = value.split("%1").join(data[i].id);
        $("#sysreport_authorizations_list_item").append(value);
      }
    }
  )  
}

function sysrep_admin_allow_handle(tid,func)
{
  if (func=="add")
  {
    var meta_pattern = $("#sysreport_authorizations_list").find(".meta_add").find("input.meta_pattern").val();
    var meta_role = $("#sysreport_authorizations_list").find(".meta_add").find("input.meta_role").val();
    var meta_fset_name = $("#sysreport_authorizations_list").find(".meta_add").find("input.meta_fset_name").val();
    var param = "pattern="+meta_pattern+"&group_name="+meta_role+"&fset_name="+meta_fset_name;
    services_osvcpostrest("R_POSTSYSREPADMINALLOW",param,function(jd) {
      if (jd.data === undefined)
      {
        jd = JSON.parse(jd);
        $("#sysrep_admin_allow_error").html(jd.error);
        return
      }
      $("#sysrep_admin_allow_error").empty();
      sysreport_admin_allow();
      mul_toggle('sysrep_authorizations_input','sysrep_authorizations_button');
    }
    )
  }
  else if (func=="del")
  {
    var param = [];
    param.push(tid);
    services_osvcdeleterest("R_DELSYSREPADMINALLOW",param,function(jd)
        {
          var result = jd;
          sysreport_admin_allow();
        }
  )  
  }
}