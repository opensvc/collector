function node_properties(divid, options)
{
    var o = {}

    // store parameters
    o.divid = divid
    o.options = options

    o.div = $("#"+divid)

    o.init = function(){
      return node_props_init(this)
    }
    o.responsible_init = function(){
      return node_props_responsible_init(this)
    }

    o.div.load('/init/static/views/node_properties.html', "", function() {
      o.init()
    })
    return o
}

function node_props_init(o)
{
  o.div.i18n();
  o.e_tags = o.div.find(".tags")
  o.e_tags.uniqueId()

  //o.filter_begin.datetimepicker({dateFormat:'yy-mm-dd'});
  //o.filter_end.datetimepicker({dateFormat:'yy-mm-dd'});

  services_osvcgetrest("R_NODE", [o.options.nodename], {"meta": "false"}, function(jd) {
    if (!jd.data) {
      o.div.html(services_error_fmt(jd))
    }
    var data = jd.data[0];
    var key;
    for (key in data) {
      if (!data[key]) {
          continue
      }
      o.div.find("#"+key).text(data[key])
    }
  },
  function() {
    o.div.html(services_ajax_error_fmt(xhr, stat, error))
  });

  if (o.options.responsible) {
    o.responsible_init()
  } else {
    services_ismemberof("Manager", function() {
      alert("responsible")
      o.responsible_init()
    })
  }

  // init tags
  tags({
    "tid": o.e_tags.attr("id"),
    "nodename": o.options.nodename,
    "responsible": o.options.responsible
  })


}

function node_props_responsible_init(o)
{
  // init uuid
  o.div.find("#uuid").parent().show()
  services_osvcgetrest("R_NODE_UUID", [o.options.nodename], {"meta": "false"}, function(jd) {
    if (!jd.data) {
      o.div.find("#uuid").html(services_error_fmt(jd))
    }
    var data = jd.data[0];
    o.div.find("#uuid").text(data.uuid)
  },
  function() {
    o.div.find("#uuid").html(services_ajax_error_fmt(xhr, stat, error))
  })

  // init passwd
  o.div.find("#root_pwd").parent().show()
  e = $("<span></span>")
  e.text(i18n.t("node_properties.retrieve_root_password"))
  e.addClass("lock clickable")
  e.bind("click", function(){
    o.div.find("#root_pwd").empty()
    spinner_add(o.div.find("#root_pwd"))
    services_osvcgetrest("R_NODE_ROOT_PASSWORD", [o.options.nodename], "", function(jd) {
      spinner_del(o.div.find("#root_pwd"))
      if (!jd.data) {
        o.div.find("#root_pwd").html(services_error_fmt(jd))
      }
      o.div.find("#root_pwd").text(jd.data)
    })
  })
  o.div.find("#root_pwd").html(e)
}
