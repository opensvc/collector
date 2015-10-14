// SysReport JS Script
// MD 08062015

function sysreport_onchangebeginenddate(nodes)
{
  sysrep_timeline(nodes,sysreport_getparam());
  sysreport_createlink(nodes);
}

function sysreport_onsubmitsysrepdiff(event,nodes)
{
  if (is_enter(event))
  {
    sysreport_onsubmitsysrepdiff(nodes)
  }
}

function sysreport_onsubmitsysrepdiff(nodes)
{
    dest = $("[name=sysrepdiff_top]")
    postdata=
        {
           nodes: nodes,
           path: $(dest).find("[name=filter]").val(),
           ignore_blanks: $(dest).find("input[name=ignore_blanks]").is(":checked")
        }
    services_osvcpost("S_SYSREPDIFF",postdata,function (msg)
        {
            dest.html(msg)
        })
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

function sysreport_createlink(nodes)
{
    url = $(location).attr("origin");
    url += services_getaccessurl("S_SYSREPVIEW");
    url += "?nodes=";
    url += nodes;
    url += "&" + sysreport_getparam();
    /*
    cid = $(item).parent().parent().find("[name=cid]").text();
    nodename = $(item).parent().parent().find("[name=nodename]").text();
    if (cid != "") {
      url += "&cid="+cid;
      url += "&nodename="+nodename;
    }
    */
    var vurl = "<a href='"+url+"' target='_blank'>"+url+"</a>";
    $("#sysrep_link").empty().html(vurl)
}

function sysrep_timeline(nodes,param)
{
    $("#sysreport_timeline_title").html("Node "+nodes+" changes timeline");
    sysreport_createlink(nodes);
    services_osvcgetrest("R_GETNODESSYS",[nodes],param, function(jd) 
    {
    
    $("sysreport_timeline").empty();

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
      services_osvcgetrest("R_GETNODESSYSCID",[item.group,item.cid],"",function(jd){
           // Link to tree file
           var result = jd.data;
           $("#sysreport_tree_file").empty();
           $("#sysreport_tree_title").html("Changement du noeud " + nodes);
           for(i=0;i<result.length;i++)
           {
            var value="<h2 class='highlight clickable'>"+result[i].fpath+
                "</h2><div id='"+result[i].oid+"'' class='hidden'></div>";
            $("#sysreport_tree_file").append(value);
           }
           $("#sysreport_tree").show();
          })
      }
    )
  });
  /* bind admin tool
  $("#"+id).siblings(".lock").bind("click", function(){
    var e = $(this).siblings("#"+id+"_admin")
    if (e.is(":visible")) {
      e.hide()
    } else {
      e.show()
      var url = $(location).attr("origin") + "/init/ajax_sysreport/ajax_sysreport_admin"
      sync_ajax(url, [], id+"_admin", function(){})
    }
  })
})*/
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
      for (i=0;i<data.length;i++)
      {
        var value = "<tr id='%1' onclick=\"sysrep_admin_allow_handle('%1','del')\"><td>Le groupe '%2' peut lire les fichiers protégés '%3' des noeuds du jeu de filtres '%4'</td></tr>";
        value = value.split("%1").join(data[i].id);
        value = value.split("%2").join(data[i].group_name);
        value = value.split("%3").join(data[i].pattern);
        value = value.split("%4").join(data[i].fset_name);
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

function sysreport_show_file(e) {
  data = {
   'nodename': e.attr("nodename"),
   'fpath': e.attr("fpath"),
   'oid': e.attr("oid"),
   'cid': e.attr("cid")
  }
  services_osvcpost("S_SYSREPSHOWFILE",data,function(msg){
         s = "<pre style='padding:1em'>"+msg+"</pre>"
         $(s).insertAfter(e)
         hljs.highlightBlock(e.next("pre"));
       }
  )
}