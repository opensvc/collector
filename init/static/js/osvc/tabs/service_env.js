function service_env(divid, options)
{
    var o = {}

    // store parameters
    o.options = options

    o.div = $("#"+divid)

    o.init = function(){
      return service_env_init(this)
    }

    o.div.load('/init/static/views/service_env.html', "", function() {
      o.init()
    })
    return o
}

function service_env_init(o)
{
  o.header = o.div.find("p")
  o.body = o.div.find("code")

  spinner_add(o.div)
  services_osvcgetrest("R_SERVICE", [o.options.svcname], {"meta": "false", "props": "updated,svc_envfile"}, function(jd) {
    spinner_del(o.div)
    if (!jd.data) {
      o.div.html(services_error_fmt(jd))
    }
    var data = jd.data[0]
    o.header.text(i18n.t("service_env.header", {"updated": data.updated}))
    text = data.svc_envfile.replace(/\\n\[/g, "\n\n[").replace(/\\n/g, "\n").replace(/\\t/g, "\t")
    o.body.html(text)
    hljs.highlightBlock(o.body[0])
    o.body.find(".hljs-setting").css({"color": "green"}).children().css({"color": "initial"})
  },
  function() {
    o.div.html(services_ajax_error_fmt(xhr, stat, error))
  });
}

