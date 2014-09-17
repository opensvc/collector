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
         "action": function(obj){this.create(obj, "first", {"attr": {"rel": "variable"}})}
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
                   $("[name=catree]:visible").jstree("refresh");
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
                   $("[rel="+obj.attr('rel')+"][obj_id="+obj.attr('obj_id')+"]").children("a").click()
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
                   $("[rel="+obj.attr('rel')+"][obj_id="+obj.attr('obj_id')+"]").children("a").click()
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
                 $("[name=catree]:visible").jstree("refresh");
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
                 $("[name=catree]:visible").jstree("refresh");
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
                 $("[name=catree]:visible").jstree("refresh");
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
                 $("[name=catree]:visible").jstree("refresh");
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
                 $("[name=catree]:visible").jstree("refresh");
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
                 $("[name=catree]:visible").jstree("refresh");
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
    $.ajax({
    async: false,
    type: "POST",
    url: designer.url_action,
    data: {
      "operation": "rename",
      "obj_type": $(this).attr('rel'),
      "obj_id": $(this).attr('obj_id'),
      "new_name": data.rslt.new_name,
    },
    success: function(msg){
      if (msg != "0") {
        $.jstree.rollback(data.rlbk)
      } else {
        //$("[name=catree]:visible").jstree("refresh");
      }
      json_status(msg)
    }
  });
 })
}

function __move(e, data) {
    if (data.rslt.cy) {
        operation = "copy"
    } else {
        operation = "move"
    }
    $.ajax({
      async: false,
      type: "POST",
      url: designer.url_action,
      data: {
        "operation": operation,
        "obj_type": data.rslt.o.attr("rel"),
        "obj_id": data.rslt.o.attr("obj_id"),
        "dst_type": data.rslt.np.attr("rel"),
        "dst_id": data.rslt.np.attr("obj_id"),
        "parent_obj_id": data.rslt.op.attr("obj_id"),
      },
      success: function(msg){
        $("[name=catree]:visible").jstree("refresh");
        json_status(msg)
      }
    });
}

function __remove(e, data) {
  data.rslt.obj.each(function() {
    $.ajax({
      async: false,
      type: "POST",
      url: designer.url_action,
      data: {
        "operation": "delete",
        "obj_type": $(this).attr("rel"),
        "obj_id": $(this).attr("obj_id"),
      },
      success: function(msg){
        if (msg != "0") {
          $.jstree.rollback(data.rlbk)
        } else {
          $("[name=catree]:visible").jstree("refresh");
        }
        json_status(msg)
      }
    });
  });
}

function __create(e, data) {
  data.rslt.obj.each(function() {
    new_rel = ""
    if (data.rslt.parent.attr("rel") == "modset") {
      new_rel = "module"
    } else if (data.rslt.parent.attr("rel") == "moduleset_head") {
      new_rel = "modset"
    } else if (data.rslt.parent.attr("rel") == "ruleset_head") {
      new_rel = "ruleset"
    } else if (data.rslt.parent.attr("rel") == "filterset_head") {
      new_rel = "filterset"
    } else if (data.rslt.parent.attr("rel").indexOf("ruleset") == 0) {
      new_rel = "variable"
    }
    $.ajax({
      async: false,
      type: "POST",
      url: designer.url_action,
      data: {
        "operation": "create",
        "obj_name": $(this).text(),
        "obj_type": new_rel,
        "parent_obj_id": data.rslt.parent.attr("obj_id"),
      },
      success: function(msg){
        if (msg != "0") {
          $.jstree.rollback(data.rlbk)
        } else {
          $("[name=catree]:visible").jstree("refresh");
        }
        json_status(msg)
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
