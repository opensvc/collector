var designer = {
  "url_static": $(location).attr("origin") + "/init/static",
  "url_action": $(location).attr("origin") + "/init/compliance/call/json/json_tree_action",
  "url": $(location).attr("origin") + "/init/compliance/call/json/json_tree",
  "init": d_init
}

function resizer(){
  $("#treerow").height($(window).height()-$(".header").outerHeight()-$(".footer").outerHeight()-$("#casearch").parent().outerHeight(true))
  $("#cainfo").width($(window).width()-$("#catree").outerWidth(true)-$("#catree2:visible").outerWidth(true)-$("#sep").outerWidth(true)-14)
}

function set_stats(value, label, node) {
  return {
    "label": label,
    "action": function(obj){
      $.ajax({
        async: false,
        type: "POST",
        url: designer.url_action,
        data: {
         "operation": "set_stats",
         "value": value,
         "obj_id": obj.attr("obj_id")
        },
        success: function(msg){
          json_status(msg)
        }
      });
    }
  }
}

function set_log_op_entry(label, obj_type, node) {
  return {
    "label": label,
    "action": function(obj){
      $.ajax({
        async: false,
        type: "POST",
        url: designer.url_action,
        data: {
         "operation": "set_log_op",
         "type": label,
         "obj_type": obj_type,
         "obj_id": obj.attr("obj_id"),
         "parent_obj_id": node.parents("li").attr("obj_id")
        },
        success: function(msg){
          $("[name=catree]:visible").jstree("refresh");
          json_status(msg)
        }
      });
    }
  }
}

function json_status(msg){
  if (msg == 0 || msg == "0") {
    $(".flash").html("")
    return
  }
  try {
    s = msg["err"]
  } catch(e) {
    s = ""
  }
  $(".flash").html(s).slideDown()
}

jstree_data = {
 "types": {
  "types": {
   "module": {
    "icon": {
     "image": designer.url_static+"/action16.png",
    },
   },
   "modset": {
    "icon": {
     "image": designer.url_static+"/action16.png",
    },
   },
   "group": {
    "icon": {
     "image": designer.url_static+"/guys16.png",
    },
   },
   "filter": {
    "icon": {
     "image": designer.url_static+"/filter16.png",
    },
   },
   "filterset": {
    "icon": {
     "image": designer.url_static+"/filter16.png",
    },
   },
   "ruleset": {
    "icon": {
     "image": designer.url_static+"/pkg16.png",
    },
   },
   "ruleset_hidden": {
    "icon": {
     "image": designer.url_static+"/pkglight16.png",
    },
   },
   "ruleset_cxt": {
    "icon": {
     "image": designer.url_static+"/rsetcxt16.png",
    },
   },
   "ruleset_cxt_hidden": {
    "icon": {
     "image": designer.url_static+"/rsetcxtlight16.png",
    },
   },
   "variable": {
    "icon": {
     "image": designer.url_static+"/comp16.png",
    },
   },
   "table": {
    "icon": {
     "image": designer.url_static+"/db16.png",
    },
   },
  },
 },
 "json_data" : {
  "ajax" : {
   "url" : function(){ return designer.url+"?obj_filter="+encodeURIComponent($("#casearch").val()) },
  },
 },
 "contextmenu": {
   "items": function(node){
     var_classes = {}
     function var_class_entry(var_class) {
       return {
         "label": var_class,
         "action": function(obj){
           $.ajax({
             async: false,
             type: "POST",
             url: designer.url_action,
             data: {
              "operation": "set_var_class",
              "var_class": var_class,
              "obj_id": obj.attr("obj_id"),
             },
             success: function(msg){
               //$("[rel="+obj.attr('rel')+"][obj_id="+obj.attr('obj_id')+"]").children("a").click()
               json_status(msg)
             }
           });
         }
       }
     }
     for (i=0;i<designer.var_class_names.length;i++) {
       var var_class = designer.var_class_names[i]
       var_classes['set_var_class_'+var_class] = var_class_entry(var_class)
     }
     h = {
       "remove" : {
         "label": "Delete",
         "_disabled": false,
         "separator_before": false,
         "separator_after": false,
         "icon": false,
         "action": function(obj){this.remove(obj)}
       },
       "rename" : {
         "label": "Rename",
         "_disabled": false,
         //"_class": "class",
         "separator_before": false,
         "separator_after": false,
         "icon": false,
         //"submenu": {},
         "action": function(obj){this.rename(obj)}
       }
     }

     //
     // moduleset_head
     //
     if (node.attr("rel")=="moduleset_head") {
       h["remove"]["_disabled"] = true
       h["rename"]["_disabled"] = true
       h["create"] = {
         "label": "Add moduleset",
         "separator_before": false,
         "separator_after": false,
         "icon": false,
         "action": function(obj){this.create(obj, "first", {"attr": {"rel": "modset"}})}
       }
     }

     //
     // filterset_head
     //
     else if (node.attr("rel")=="filterset_head") {
       h["remove"]["_disabled"] = true
       h["rename"]["_disabled"] = true
       h["create"] = {
         "label": "Add filterset",
         "separator_before": false,
         "separator_after": false,
         "icon": false,
         "action": function(obj){this.create(obj, "first", {"attr": {"rel": "filterset"}})}
       }
     }

     //
     // ruleset_head
     //
     else if (node.attr("rel")=="ruleset_head") {
       h["remove"]["_disabled"] = true
       h["rename"]["_disabled"] = true
       h["create"] = {
         "label": "Add ruleset",
         "separator_before": false,
         "separator_after": false,
         "icon": false,
         "action": function(obj){this.create(obj, "first", {"attr": {"rel": "ruleset"}})}
       }
     }

     //
     // moduleset
     //
     else if (node.attr("rel")=="modset") {
       h["create"] = {
         "label": "Add module",
         "separator_before": false,
         "separator_after": false,
         "icon": false,
         "action": function(obj){this.create(obj, "first", {"attr": {"rel": "module"}})}
       }
       h["clone"] = {
         "label": "Clone",
         "action": function(obj){
           $.ajax({
             async: false,
             type: "POST",
             url: designer.url_action,
             data: {
              "operation": "clone",
              "obj_id": obj.attr("obj_id"),
              "obj_type": obj.attr("rel"),
             },
             success: function(msg){
               $("[name=catree]:visible").jstree("refresh");
               json_status(msg)
             }
           });
         }
       }
     }

     //
     // ruleset
     //
     else if (node.attr("rel").indexOf("ruleset") == 0) {
       h["create"] = {
         "label": "Add variable",
         "separator_before": false,
         "separator_after": false,
         "icon": false,
         "action": function(obj){
            this.create(obj, "first", {"attr": {"rel": "variable"}})
         }
       }
       h["clone"] = {
         "label": "Clone",
         "action": function(obj){
           $.ajax({
             async: false,
             type: "POST",
             url: designer.url_action,
             data: {
              "operation": "clone",
              "obj_id": obj.attr("obj_id"),
              "obj_type": obj.attr("rel"),
             },
             success: function(msg){
               $("[name=catree]:visible").jstree("refresh");
               json_status(msg)
             }
           });
         }
       }
       h["set_type"] = {
         "label": "Set type",
         "separator_before": false,
         "separator_after": false,
         "icon": false,
         "submenu": {
           "contextual": {
             "label": "Contextual",
             "action": function(obj){
               $.ajax({
                 async: false,
                 type: "POST",
                 url: designer.url_action,
                 data: {
                  "operation": "set_type",
                  "type": "contextual",
                  "obj_type": "ruleset",
                  "obj_id": obj.attr("obj_id"),
                 },
                 success: function(msg){
                   var e = $("[name=catree]:visible").find("[obj_id="+obj.attr("obj_id")+"]")
                   var r = obj.attr('rel')
                   if (r == 'ruleset') {
                     e.attr('rel', 'ruleset_cxt')
                   } else if (r == 'ruleset_hidden') {
                     e.attr('rel', 'ruleset_cxt_hidden')
                   }
                   $("[rel="+obj.attr('rel')+"][obj_id="+obj.attr('obj_id')+"]").children("a").click()
                   json_status(msg)
                 }
               });
             }
           },
           "explicit": {
             "label": "Explicit",
             "action": function(obj){
               $.ajax({
                 async: false,
                 type: "POST",
                 url: designer.url_action,
                 data: {
                  "operation": "set_type",
                  "type": "explicit",
                  "obj_type": "ruleset",
                  "obj_id": obj.attr("obj_id"),
                 },
                 success: function(msg){
                   var e = $("[name=catree]:visible").find("[obj_id="+obj.attr("obj_id")+"]")
                   var r = obj.attr('rel')
                   if (r == 'ruleset_cxt') {
                     e.attr('rel', 'ruleset')
                   } else if (r == 'ruleset_cxt_hidden') {
                     e.attr('rel', 'ruleset_hidden')
                   }
                   $("[rel="+obj.attr('rel')+"][obj_id="+obj.attr('obj_id')+"]").children("a").click()
                   json_status(msg)
                 }
               });
             }
           },
         }
       }
       h["set_publication"] = {
         "label": "Set publication",
         "separator_before": false,
         "separator_after": false,
         "icon": false,
         "submenu": {
           "published": {
             "label": "Published",
             "action": function(obj){
               var t = this
               $.ajax({
                 async: false,
                 type: "POST",
                 url: designer.url_action,
                 data: {
                  "operation": "set_public",
                  "publication": true,
                  "obj_id": obj.attr("obj_id"),
                 },
                 success: function(msg){
                   var e = $("[name=catree]:visible").find("[obj_id="+obj.attr("obj_id")+"]")
                   var r = obj.attr("rel")
                   if (r == "ruleset_cxt_hidden") {
                     e.attr("rel", "ruleset_cxt")
                   } else if (r == "ruleset_hidden") {
                     e.attr("rel", "ruleset")
                   }
                   json_status(msg)
                 }
               });
             }
           },
           "not_published": {
             "label": "Not published",
             "action": function(obj){
               $.ajax({
                 async: false,
                 type: "POST",
                 url: designer.url_action,
                 data: {
                  "operation": "set_public",
                  "publication": false,
                  "obj_id": obj.attr("obj_id"),
                 },
                 success: function(msg){
                   var e = $("[name=catree]:visible").find("[obj_id="+obj.attr("obj_id")+"]")
                   var r = obj.attr("rel")
                   if (r == "ruleset_cxt") {
                     e.attr("rel", "ruleset_cxt_hidden")
                   } else if (r == "ruleset") {
                     e.attr("rel", "ruleset_hidden")
                   }
                   // remove unpublished contextual ruleset from head
                   $("[rel=ruleset_head]>ul>li[rel=ruleset_cxt_hidden").each(function(){
                     $(this).parents("[name=catree]").jstree("delete_node", "#"+$(this).attr("id"))
                   })
                   json_status(msg)
                 }
               });
             }
           },
         }
       }
       if (node.attr("rset_type") == "contextual") {
         h["detach_filterset"] = {
           "label": "Detach filterset",
           "action": function(obj){
             $.ajax({
               async: false,
               type: "POST",
               url: designer.url_action,
               data: {
                "operation": "detach_filterset",
                "obj_id": obj.attr("obj_id"),
               },
               success: function(msg){
                 var id = obj.attr("id")
                 var l = id.split("_")
                 var fset_id = l.pop()
                 var rset_id = l.pop()
                 l = [rset_id, fset_id]
                 id = l.join("_")
                 $("[name=catree]:visible").each(function(){
                   $(this).jstree("delete_node", "[id$="+id+"]")
                 })
                 json_status(msg)
               }
             });
           }
         }
       }
       if (node.parents("li").attr("rel").indexOf("ruleset") == 0 &&
           node.parents("li").attr("rel") != "ruleset_head") {
         h["remove"]["_disabled"] = true
         h["detach_ruleset"] = {
           "label": "Detach ruleset",
           "action": function(obj){
             var t = this
             $.ajax({
               async: false,
               type: "POST",
               url: designer.url_action,
               data: {
                "operation": "detach_ruleset",
                "publication": false,
                "obj_id": obj.attr("obj_id"),
                "parent_obj_id": obj.parents("li").attr("obj_id"),
               },
               success: function(msg){
                 var rel = obj.attr("rel")
                 if ((rel == "ruleset_hidden") || (rel == "ruleset_cxt_hidden")) {
                   var obj_id = obj.attr("obj_id")
                   var id = obj.attr("id")
                   var v = $("#catree").find("[obj_id="+obj_id+"][rel="+rel+"]")
                   if (v.length == 1) {
                     // re-attach the rule at head level
                     $("[name=catree]").jstree("move_node", "#"+id, "#rset_head")
                   }
                   var l = id.split("_")
                   var child_rset_id = l.pop()
                   var parent_rset_id = l.pop()
                   l = [parent_rset_id, child_rset_id]
                   id = l.join("_")
                   $("[name=catree]").each(function(){
                     t = $(this)
                     t.find("[id$="+id+"]").each(function(){
                       if ($(this).parents("li").first().attr("id") == "rset_head") {
                         return
                       }
                       t.jstree("delete_node", "#"+$(this).attr("id"))
                     })
                   })
                   // set id of restored non-published contextual ruleset at rset_head level
                   $("[id^=copy_]").each(function(){
                     var n_id = "rset"+$(this).attr("obj_id")
                     $(this).attr("id", n_id)
                   })
                 } else {
                   t.move_node(obj, "#rset_head")
                 }
                 json_status(msg)
               }
             });
           }
         }
       }
     }

     //
     // group
     //
     else if (node.attr("rel")=="group") {
       h["remove"]["_disabled"] = true
       h["rename"]["_disabled"] = true
       if (node.parents("li").attr("rel").indexOf("ruleset") == 0 || node.parents("li").attr("rel") == "modset") {
         h["detach_group"] = {
           "label": "Detach group",
           "action": function(obj){
             var t = this
             $.ajax({
               async: false,
               type: "POST",
               url: designer.url_action,
               data: {
                "operation": "detach_group",
                "parent_obj_type": obj.parents("li").attr("rel"),
                "obj_id": obj.attr("obj_id"),
                "parent_obj_id": obj.parents("li").attr("obj_id")
               },
               success: function(msg){
                   var id = obj.attr("id")
                   var l = id.split("_")
                   var child_id = l.pop()
                   var parent_id = l.pop()
                   l = [parent_id, child_id]
                   id = l.join("_")
                   $("[name=catree]:visible").each(function(){
                     $(this).jstree("delete_node", "[id$="+id+"]")
                   })

                 t.delete_node(obj)
                 json_status(msg)
               }
             });
           }
         }
       }
     }

     //
     // null
     //
     else if (node.attr("rel") == null) {
       h["remove"]["_disabled"] = true
       h["rename"]["_disabled"] = true
     }

     //
     // table
     //
     else if (node.attr("rel")=="table") {
       h["remove"]["_disabled"] = true
       h["rename"]["_disabled"] = true
     }

     //
     // filter
     //
     else if (node.attr("rel")=="filter") {
       h["remove"]["_disabled"] = true
       h["rename"]["_disabled"] = true
       if (node.parents("li").attr("rel") == "filterset") {
         h["set_log_op"] = {
           "label": "Set logical operator",
           "separator_before": false,
           "separator_after": false,
           "icon": false,
           "submenu": {
             "and": set_log_op_entry("AND", "filter", node),
             "and_not": set_log_op_entry("AND NOT", "filter", node),
             "or": set_log_op_entry("OR", "filter", node),
             "or not": set_log_op_entry("AND NOT", "filter", node)
           }
         }
         h["detach_filter"] = {
           "label": "Detach filter",
           "action": function(obj){
             var t = this
             $.ajax({
               async: false,
               type: "POST",
               url: designer.url_action,
               data: {
                "operation": "detach_filter",
                "obj_id": obj.attr("obj_id"),
                "parent_obj_id": node.parents("li").attr("obj_id"),
               },
               success: function(msg){
                 t.delete_node(obj)
                 json_status(msg)
               }
             });
           }
         }
       }
     }

     //
     // variable
     //
     else if (node.attr("rel")=="variable") {
       h["set_var_class"] = {
         "label": "Set variable class",
         "separator_before": false,
         "separator_after": false,
         "icon": false,
         "submenu": var_classes,
       }
     }

     //
     // filterset
     //
     else if (node.attr("rel")=="filterset") {
       h["set_stats"] = {
         "label": "Set statistics",
         "separator_before": false,
         "separator_after": false,
         "icon": false,
         "submenu": {
           "yes": set_stats(true, "Compute daily statitiscs", node),
           "no": set_stats(false, "Do not compute daily statistics", node)
         }
       }
       if (node.parents("li").attr("rel") == "filterset") {
         h["remove"]["_disabled"] = true
         h["rename"]["_disabled"] = true
         h["set_log_op"] = {
           "label": "Set logical operator",
           "separator_before": false,
           "separator_after": false,
           "icon": false,
           "submenu": {
             "and": set_log_op_entry("AND", "filterset", node),
             "and_not": set_log_op_entry("AND NOT", "filterset", node),
             "or": set_log_op_entry("OR", "filterset", node),
             "or not": set_log_op_entry("AND NOT", "filterset", node)
           }
         }
         h["detach_filterset"] = {
           "label": "Detach filterset",
           "action": function(obj){
             var t = this
             $.ajax({
               async: false,
               type: "POST",
               url: designer.url_action,
               data: {
                "operation": "detach_filterset",
                "parent_obj_type": "filterset",
                "obj_id": obj.attr("obj_id"),
                "parent_obj_id": node.parents("li").attr("obj_id"),
               },
               success: function(msg){
                 var id = obj.attr("id")
                 var l = id.split("_")
                 var fset_id = l.pop()
                 var rset_id = l.pop()
                 l = [rset_id, fset_id]
                 id = l.join("_")
                 $("[name=catree]:visible").each(function(){
                   $(this).jstree("delete_node", "[id$="+id+"]")
                 })
                 json_status(msg)
               }
             });
           }
         }
       } else if (node.parents("li").attr("rel").indexOf("ruleset") == 0) {
         h["remove"]["_disabled"] = true
         h["rename"]["_disabled"] = true
         h["detach_filterset"] = {
           "label": "Detach filterset",
           "action": function(obj){
             var t = this
             $.ajax({
               async: false,
               type: "POST",
               url: designer.url_action,
               data: {
                "operation": "detach_filterset",
                "parent_obj_type": "ruleset",
                "parent_obj_id": node.parents("li").attr("obj_id"),
               },
               success: function(msg){
                 var id = obj.attr("id")
                 var l = id.split("_")
                 var fset_id = l.pop()
                 var rset_id = l.pop()
                 l = [rset_id, fset_id]
                 id = l.join("_")
                 $("[name=catree]:visible").each(function(){
                   $(this).jstree("delete_node", "[id$="+id+"]")
                 })
                 json_status(msg)
               }
             });
           }
         }
       }
     }
     resizer()
     return h
   }
 },
 "search": {
   "show_only_matches": false
 },
 "crrm": {
   "move": {
     "always_copy": true,
     "check_move": function (m) {
        if (m.o.attr('rel')=="filterset" && m.np.attr('rel').indexOf("ruleset")==0) { return true }
        if (m.o.attr('rel').indexOf("ruleset")==0 && m.np.attr('rel').indexOf("ruleset")==0) { return true }
        if (m.o.attr('rel')=="variable" && m.np.attr('rel').indexOf("ruleset")==0) { return true }
        if (m.o.attr('rel')=="filter" && m.np.attr('rel')=="filterset") { return true }
        if (m.o.attr('rel')=="filterset" && m.np.attr('rel')=="filterset") { return true }
        if (m.o.attr('rel')=="group" && m.np.attr('rel').indexOf("ruleset")==0) { return true }
        if (m.o.attr('rel')=="group" && m.np.attr('rel')=="modset") { return true }
        return false
     }
   }
 },
 "plugins" : [
   "themes",
   "json_data",
   "ui",
   "types",
   "crrm",
   "contextmenu",
   "dnd",
   //"hotkeys",
   "cookies",
   "search",
   "adv_search"
 ]
}

function __rename(e, data) {
  data.rslt.obj.each(function() {
    var rel = $(this).attr('rel')
    var obj_id = $(this).attr('obj_id')
    var new_name = data.rslt.new_name
    $.ajax({
      async: false,
      type: "POST",
      url: designer.url_action,
      data: {
       "operation": "rename",
       "obj_type": rel,
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
        $.jstree.rollback(data.rlbk)
        $(".flash").html(msg).slideDown()
      },
      success: function(msg){
        if (msg != "0") {
          $.jstree.rollback(data.rlbk)
          json_status(msg)
        }
        $("[rel="+rel+"][obj_id="+obj_id+"]").each(function(){
          $(this).parents("[name=catree]").jstree("rename_node", this, new_name)
        })
      }
    })
  })
}

function __move(e, data) {
    if (data.rslt.cy) {
        var operation = "copy"
    } else {
        var operation = "move"
    }
    var dst_id = data.rslt.np.attr("id")
    var dst_rel = data.rslt.np.attr("rel")
    var dst_obj_id = data.rslt.np.attr("obj_id")
    var dst_tree_id = data.rslt.np.parents("[name=catree]").attr("id")
    var text = data.rslt.o.text().replace(/^\s*/, "")
    var rel = data.rslt.o.attr("rel")
    var id = data.rslt.o.attr("id")
    var tree_id = data.rslt.o.parents("[name=catree]").attr("id")
    var obj_id = data.rslt.o.attr("obj_id")
    var parent_obj_id = data.rslt.op.attr("obj_id")

    if (dst_id == "rset_head") {
      // actually a detach
      return
    }
    if (id.indexOf("copy_") == 0) {
      // avoid recursing when copying the same node elsewhere
      return
    }

    $.ajax({
      async: false,
      type: "POST",
      url: designer.url_action,
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
        $.jstree.rollback(data.rlbk)
        $(".flash").html(msg).slideDown()
      },
      success: function(msg){
        try {
          new_obj_id = msg["obj_id"]
        } catch(e) {
          new_obj_id = -1
        }
        if ((msg != "0") && (new_obj_id < 0)) {
          $.jstree.rollback(data.rlbk)
          json_status(msg)
          return
        }

        $("[rel="+dst_rel+"][obj_id="+dst_obj_id+"]").each(function(){
          var this_dst_id = $(this).attr("id")
          var this_dst_tree_id = $(this).parents("[name=catree]").attr("id")
          if ((this_dst_tree_id == dst_tree_id) && (this_dst_id == dst_id)) {
            return
          }
          $(this).parents("[name=catree]").jstree("move_node", "#copy_"+id, "#"+this_dst_id, "last")
        })
        if (rel.indexOf("hidden") > 0) {
          $("[rel=ruleset_head]").children("ul").children("li[rel="+rel+"][obj_id="+obj_id+"]").remove()
        }
        $("[id^=copy_]").each(function(){
          var parent_id = $(this).parents("li").first().attr("id")
          var id = $(this).attr("id").replace(/^(\w*_)*/, "")
          if (new_obj_id > 0) {
            // the server provided a new obj_id. replace the original's.
            $(this).attr("obj_id", new_obj_id)
            var regex = new RegExp(obj_id + "$")
            id = id.replace(regex, new_obj_id)
          }
          $(this).attr("id", parent_id+"_"+id)
        })
        if ((rel == "filterset")&&(dst_rel.indexOf("ruleset")==0)) {
          // purge old ruleset's filterset
          $("[obj_id="+dst_obj_id+"][rel^=ruleset]").children("ul").children("li[rel=filterset]").each(function(){
            if ($(this).attr("obj_id") == obj_id) {
              $(this).prependTo($(this).parent())
              return
            }
            $(this).remove()
          })
        }
      }
    });
}

function __remove(e, data) {
  data.rslt.obj.each(function() {
    var obj_id = $(this).attr("obj_id")
    var obj_rel = $(this).attr("rel")
    $.ajax({
      async: false,
      type: "POST",
      url: designer.url_action,
      data: {
        "operation": "delete",
        "obj_type": $(this).attr("rel"),
        "obj_id": $(this).attr("obj_id"),
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
        $.jstree.rollback(data.rlbk)
        $(".flash").html(msg).slideDown()
      },
      success: function(msg){
        if (msg != "0") {
          $.jstree.rollback(data.rlbk)
          json_status(msg)
        }
        $("[name=catree]:visible").each(function(){
          $(this).jstree("delete_node", "[rel="+obj_rel+"][obj_id="+obj_id+"]")
        })
      }
    });
  });
}

function __create(e, data) {
  data.rslt.obj.each(function() {
    var tmp_obj = $(this)
    var parent_id = data.rslt.parent.attr("id")
    var parent_obj_id = data.rslt.parent.attr("obj_id")
    var parent_rel = data.rslt.parent.attr("rel")
    var tree_id = data.rslt.parent.parents("[name=catree]").attr("id")
    var new_data = tmp_obj.text()
    var new_rel = ""
    var new_rel_short = ""
    if (parent_rel == "modset") {
      new_rel = "module"
      new_rel_short = "mod"
    } else if (parent_rel == "moduleset_head") {
      new_rel = "modset"
      new_rel_short = "mset"
    } else if (parent_rel == "ruleset_head") {
      new_rel = "ruleset"
      new_rel_short = "rset"
    } else if (parent_rel == "filterset_head") {
      new_rel = "filterset"
      new_rel_short = "fset"
    } else if (parent_rel.indexOf("ruleset") == 0) {
      new_rel = "variable"
      new_rel_short = "var"
    } else {
      return
    }
    $.ajax({
      async: false,
      type: "POST",
      url: designer.url_action,
      data: {
        "operation": "create",
        "obj_name": new_data,
        "obj_type": new_rel,
        "parent_obj_id": parent_obj_id
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
        $.jstree.rollback(data.rlbk)
        $(".flash").html(msg).slideDown()
      },
      success: function(msg){
        if (msg == "0") {
          $("[name=catree]:visible").jstree("refresh");
          return
        }
        if ((msg != "0") && !("obj_id" in msg)) {
          $.jstree.rollback(data.rlbk)
          json_status(msg)
          return
        }
        var new_obj_id = msg['obj_id']
        tmp_obj.attr("obj_id", new_obj_id)

        if ((parent_id == "rset_head") || (parent_id == "fset_head") || (parent_id == "moduleset_head")) {
          var new_id = new_rel_short+new_obj_id
          tmp_obj.attr("id", new_id)
          $("[rel="+parent_rel+"]:visible").each(function(){
              var this_tree_id = $(this).parents("[name=catree]").attr("id")
              if (this_tree_id == tree_id) {
                return
              }
              var new_id = new_rel_short+new_obj_id
              $(this).parents("[name=catree]").jstree("create_node", "#"+parent_id, "first", {"data": new_data.replace(/^\s*/, ""), "attr": {"rel": new_rel, "id": new_id, "obj_id": new_obj_id}})
          })
        } else {
          var new_id = parent_id+'_'+new_rel_short+new_obj_id
          tmp_obj.attr("id", new_id)
          $("[rel="+parent_rel+"][obj_id="+parent_obj_id+"]:visible").each(function(){
              var this_tree_id = $(this).parents("[name=catree]").attr("id")
              if (($(this).attr("id") == parent_id) && (this_tree_id == tree_id)) {
                return
              }
              var par_id = $(this).attr("id")
              var new_id = par_id+'_'+new_rel_short+new_obj_id
              $(this).parents("[name=catree]").jstree("create_node", "#"+par_id, "first", {"data": new_data.replace(/^\s*/, ""), "attr": {"rel": new_rel, "id": new_id, "obj_id": new_obj_id}})
          })
        }
        
        //$("{name=jstree]:visible").find()
      }
    });
  });
}

function __select(e, data) {
  data.rslt.obj.each(function() {
    $.ajax({
    async: false,
    type: "POST",
    url: designer.url_action,
    data: {
      "operation": "show",
      "obj_type": $(this).attr('rel'),
      "obj_id": $(this).attr('obj_id'),
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
      $.jstree.rollback(data.rlbk)
      $(".flash").html(msg).slideDown()
    },
    success: function(msg){
      $("#cainfo").html(msg)
      $("#cainfo").find("script").each(function(i){
        eval($(this).text());
        $(this).remove();
      });
    }
  });
 });
}

function d_init(data) {
  designer["var_class_names"] = data.var_class_names

  $("#catree").jstree(jstree_data).bind("rename.jstree", __rename)
                                  .bind("move_node.jstree", __move)
                                  .bind("remove.jstree", __remove)
                                  .bind("create.jstree", __create)
                                  .bind("select_node.jstree", __select)
  
  jstree_data["cookies"] = {
    "save_opened": "jstree_open2",
    "save_selected": "jstree_select2",
  }
  
  $("#catree2").jstree(jstree_data).bind("rename.jstree", __rename)
                                   .bind("move_node.jstree", __move)
                                   .bind("remove.jstree", __remove)
                                   .bind("create.jstree", __create)
                                   .bind("select_node.jstree", __select)
  
  
  $("#casearch").keyup(function(event){
    if (is_enter(event)) {
      $("#catree:visible").jstree("refresh");
      $("#catree2:visible").jstree("refresh");
    }
  })
  
  $("#sep").click(function(){
    $("#catree2").toggle()
    $("#catree2:visible").jstree("refresh");
    resizer()
  })
  
  $(window).bind('resize', resizer)
  $(window).load(resizer)
}
