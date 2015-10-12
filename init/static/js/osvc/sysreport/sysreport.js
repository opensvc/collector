// SysReport JS Script
// MD 08062015

function sysreport_onchangebeginenddate(event,nodes)
{
    if (is_enter(event))
    {
        dest = $("[name=sysrep_top]")
        postdata=
            {
                nodes: nodes,
                end: dest.find("[name=end]").val(),
                begin: dest.find("[name=begin]").val(),
                path: dest.find("[name=filter]").val()
            }
        services_osvcpost("S_SYSREP",postdata,
            function (msg)
            {
                dest.html(msg)
            })
    }
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

function show_dateTimePicker(item)
{
    $(item).toggle();
    $(item).siblings().toggle().children("input").focus();
    $(item).datetimepicker({dateFormat: "yy-mm-dd"});
}

function sysreport_createlink(item)
{
    url = $(location).attr("origin")
    url += services_getaccessurl("S_SYSREPVIEW")
    url += "?nodes="
    url += $(item).parent().parent().find("[name=nodes]").text()
    fval = $(item).parent().parent().find("input[name=filter]").val()
    if (fval!="") {
      url += "&path="+fval
    }
    fval = $(item).parent().parent().find("input[name=begin]").val()
    if (fval!="") {
      url += "&begin="+fval
    }
    fval = $(item).parent().parent().find("input[name=end]").val()
    if (fval!="") {
      url += "&end="+fval
    }

    cid = $(item).parent().parent().find("[name=cid]").text()
    nodename = $(item).parent().parent().find("[name=nodename]").text()
    if (cid != "") {
      url += "&cid="+cid
      url += "&nodename="+nodename
    }

    $(item).children().html(url)
    $(item).children().show()
}

function sysreport_timeline(id, data){
  var options = {
    template: function (item) {
      return '<pre style="text-align:left">' + item.stat + '</pre>';
    },
    clickToUse: false
  };
  var container = document.getElementById(id);
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
  timeline.on('select', function (properties) {
    var item_id = properties.items[0]
    var item = null;
    for (i=0; i<data.length; i++) {
      if (data[i]['id'] == item_id) {
        item = data[i]
        break
      }
    }
    _data = {
     'cid': item.cid,
     'nodename': item.group,
     'path': $("#"+id).parents("[name=sysrep_top]").find("input[name=filter]").val()
    }
    services_osvcpost("S_SYSREPCOMMIT",_data,function(msg){
           $("#"+id+"_show").html(msg)
           $("#"+id+"_show").find(".diff").each(function(i, block){
             hljs.highlightBlock(block);
           })
           $("#"+id+"_show").find("[name=tree]").children("h2").bind('click', function(){
             next = $(this).next()
             if (next.is("pre")) {
               next.remove()
             } else {
               sysreport_show_file($(this))
             }
           })
         }
    )
  });
  // bind admin tool
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

function sysreport_admin_secure(tid) {
  $("#"+tid).find("[sec_id]").bind("mouseover", function(){
    $(this).find(".nologo16").addClass("del16").addClass("clickable")
  }).bind("mouseout", function(){
    $(this).find(".nologo16").removeClass("del16").removeClass("clickable")
  })
  $("#"+tid).find(".meta_del").bind("click", function(){
    var sec_id = $(this).parent().attr("sec_id")
    var url = $(location).attr("origin") + "/init/ajax_sysreport/ajax_sysreport_admin_del_secure"
    url += "?sec_id="+sec_id
    sync_ajax(url, [], "", function(){$("[sec_id="+sec_id+"]").remove()})
  })
  $("#"+tid).find(".meta_add").find("input").bind("keyup", function(){
    if (!is_enter(event)) {
      return
    }
    var pattern = $(this).val()
    var url = $(location).attr("origin") + "/init/ajax_sysreport/ajax_sysreport_admin_add_secure"
    url += "?pattern="+encodeURIComponent(pattern)
    sync_ajax(url, [], "", function(){$(".lock").click().click()})
  })
}

function sysreport_admin_allow(tid) {
  $("#"+tid).find("[allow_id]").bind("mouseover", function(){
    $(this).find(".nologo16").addClass("del16").addClass("clickable")
  }).bind("mouseout", function(){
    $(this).find(".nologo16").removeClass("del16").removeClass("clickable")
  })
  $("#"+tid).find(".meta_del").bind("click", function(){
    var allow_id = $(this).parent().attr("allow_id")
    var url = $(location).attr("origin") + "/init/ajax_sysreport/ajax_sysreport_admin_del_allow"
    url += "?allow_id="+allow_id
    sync_ajax(url, [], "", function(){$("[allow_id="+allow_id+"]").remove()})
  })
  $("#"+tid).find(".meta_add").find("input").bind("keyup", function(){
    if (!is_enter(event)) {
      return
    }
    var pattern = $(this).parents(".meta_add").find("input.meta_pattern").val()
    var role = $(this).parents(".meta_add").find("input.meta_role").val()
    var fset_name = $(this).parents(".meta_add").find("input.meta_fset_name").val()
    var url = $(location).attr("origin") + "/init/ajax_sysreport/ajax_sysreport_admin_add_allow"
    url += "?pattern="+encodeURIComponent(pattern)
    url += "&role="+encodeURIComponent(role)
    url += "&fset_name="+encodeURIComponent(fset_name)
    sync_ajax(url, [], "", function(){$(".lock").click().click()})
  })
}

