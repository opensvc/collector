function node_properties(divid, options)
{
    var o = {}

    // store parameters
    o.options = options

    o.div = $("#"+divid)

    o.init = function(){
      return node_props_init(this)
    }
    o.responsible_init = function(){
      return node_props_responsible_init(this)
    }

    o.div.load('/init/static/views/node_properties.html', "", function() {
      o.div = o.div.children()
      o.div.uniqueId()
      o.init()
    })
    return o
}

function node_props_init(o)
{
  o.div.i18n();
  o.e_tags = o.div.find(".tags")
  o.e_tags.uniqueId()


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

    // init sys responsible tools
    if (o.options.responsible) {
      o.responsible_init()
    } else {
      services_ismemberof("Manager", function() {
        alert("responsible")
        o.responsible_init()
      })
    }
  },
  function() {
    o.div.html(services_ajax_error_fmt(xhr, stat, error))
  });

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

  // init updaters
  if (o.div.find("#version").text() != "") {
    o.has_agent = true
  } else {
    o.has_agent = false
  }
  o.div.find("[upd]").each(function(){
    var agent = $(this).attr("agent")
    if ((agent == "1") && o.has_agent) {
      return
    }
    $(this).addClass("clickable")
    $(this).hover(
        function() {
          $(this).addClass("editable")
        },
        function() {
          $(this).removeClass("editable")
        }
    )
    $(this).bind("click", function() {
      //$(this).unbind("mouseenter mouseleave click")
      if ($(this).siblings().find("form").length > 0) {
        $(this).siblings().show()
        $(this).siblings().find("input").focus()
        $(this).hide()
        return
      }
      var updater = $(this).attr("upd")
      if ((updater == "string") || (updater == "integer") || (updater == "date") || (updater == "datetime")) {
        e = $("<td><form class='editable'><input type='text'></input></form></td>")
        e.css({"padding-left": "0px"})
        var input = e.find("input")
        input.uniqueId() // for date picker
        input.attr("pid", $(this).attr("id"))
        input.attr("value", $(this).text())
        input.bind("blur", function(){
          $(this).parents("td").first().siblings("td").show()
          $(this).parents("td").first().hide()
        })
        $(this).parent().append(e)
        $(this).hide()
        e.find("input").focus()
      } else {
        return
      }
      if (updater == "date") {
        input.datepicker({
          dateFormat:'yy-mm-dd',
          onSelect: function() {
            $(this).parents("td").first().siblings("td").click()
          }
        }).datepicker("show");
      } else if (updater == "datetime") {
        input.datetimepicker({
          dateFormat:'yy-mm-dd',
          onSelect: function() {
            $(this).parents("td").first().siblings("td").click()
          }
        }).datepicker("show");
      }

      e.find("form").submit(function() {
        event.preventDefault()
        var input = $(this).find("input")
        input.blur()
        data = {}
        data["nodename"] = o.options.nodename
        data[input.attr("pid")] = input.val()
        services_osvcpostrest("R_NODE", [o.options.nodename], "", data, function(jd) {
          o.init()
        })
      })
    })
  })
}
