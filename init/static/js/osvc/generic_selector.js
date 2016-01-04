function generic_selector(divid, options) {
  //
  // options = {
  //   'url_path': <a rest handler symbolic name as defined in osvc-services.js>
  //   'url_wildcards': <array of values to be substiuted in source>
  //   'url_params': <parameters to set with the GET request>
  //   'object_id': <the data dictionnary key to use as selector obj id>
  //   'object_name': <the data dictionnary key to use as selector obj label>
  // }
  //
  o = options
  o.div = $("#"+divid)
  o.selected_class = "generic_selector_selected"
  o.object_base_class = "generic_selector_object"

  o.init = function() {
    o.object_area = $("<div></div>")
    o.div.append(o.object_area)
    spinner_add(o.object_area)
    services_osvcgetrest(o.url_path, o.url_wildcards, o.url_params, function(jd) {
      spinner_del(o.object_area)
      if (jd.error && (jd.error.length > 0)) {
        o.object_area.html(services_error_fmt(jd))
        return
      }
      for (var i=0; i<jd.data.length; i++) {
        o.add_object(jd.data[i])
      }
    },
    function(xhr, stat, error) {
      o.object_area.html(services_ajax_error_fmt(xhr, stat, error))
    })
  }

  o.add_object = function(data) {
    var object = $("<div></div>")
    object.addClass(o.object_class)
    object.addClass(o.object_base_class)
    object.attr("obj_id", data[o.object_id])
    object.text(data[o.object_name])
    o.object_area.append(object)
    object.bind("click", function() {
      $(this).toggleClass(o.selected_class)
    })
  }

  o.get_selected = function() {
    var data = []
    o.object_area.find("."+o.selected_class).each(function(){
      data.push($(this).attr("obj_id"))
    })
    return data
  }
  o.init()
  return o
}

function generic_selector_tags(id) {
  return generic_selector(id, {
    "url_path": "R_TAGS",
    "url_params": {
      "orderby": "tag_name",
      "limit": "0",
      "props": "id,tag_name",
      "meta": "0"
    },
    "object_class": "tag16",
    "object_id": "id",
    "object_name": "tag_name"
  })
}

function generic_selector_modsets(id) {
  return generic_selector(id, {
    "url_path": "R_COMPLIANCE_MODULESETS",
    "url_params": {
      "orderby": "modset_name",
      "limit": "0",
      "props": "id,modset_name",
      "meta": "0"
    },
    "object_class": "actions",
    "object_id": "id",
    "object_name": "modset_name"
  })
}

function generic_selector_rulesets(id) {
  return generic_selector(id, {
    "url_path": "R_COMPLIANCE_RULESETS",
    "url_params": {
      "orderby": "ruleset_name",
      "limit": "0",
      "props": "id,ruleset_name",
      "meta": "0",
      "filters": ["ruleset_type=explicit", "ruleset_public=T"]
    },
    "object_class": "comp16",
    "object_id": "id",
    "object_name": "ruleset_name"
  })
}

function generic_selector_checks_contextual_settings(id) {
  return generic_selector(id, {
    "url_path": "R_CHECKS_CONTEXTUAL_SETTINGS",
    "url_params": {
      "orderby": "name",
      "limit": "0",
      "props": "id,name",
      "meta": "0"
    },
    "object_class": "filter16",
    "object_id": "id",
    "object_name": "name"
  })
}

function generic_selector_org_groups(id) {
  return generic_selector(id, {
    "url_path": "R_GROUPS",
    "url_params": {
      "orderby": "role",
      "limit": "0",
      "props": "id,role",
      "filters": ["role !user_%", "privilege F"],
      "meta": "0"
    },
    "object_class": "guys16",
    "object_id": "id",
    "object_name": "role"
  })
}

function generic_selector_org_and_private_groups(id) {
  return generic_selector(id, {
    "url_path": "R_GROUPS",
    "url_params": {
      "orderby": "role",
      "limit": "0",
      "props": "id,role",
      "filters": ["privilege F"],
      "meta": "0"
    },
    "object_class": "guys16",
    "object_id": "id",
    "object_name": "role"
  })
}

function generic_selector_privilege_groups(id) {
  return generic_selector(id, {
    "url_path": "R_GROUPS",
    "url_params": {
      "orderby": "role",
      "limit": "0",
      "props": "id,role",
      "filters": ["privilege T"],
      "meta": "0"
    },
    "object_class": "guys16",
    "object_id": "id",
    "object_name": "role"
  })
}

function generic_selector_groups(id) {
  return generic_selector(id, {
    "url_path": "R_GROUPS",
    "url_params": {
      "orderby": "role",
      "limit": "0",
      "props": "id,role",
      "meta": "0"
    },
    "object_class": "guys16",
    "object_id": "id",
    "object_name": "role"
  })
}

