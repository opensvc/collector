function login(divid) {
  var o = {}
  o.divid = divid
  o.div = $("#"+divid)
  
  o.init = function init() {
    return login_init(o)
  }

  o.login_clicked = function login_clicked() {
  	return login_clicked(o);
  }
  
  o.div.load("/init/static/views/login.html", function() {
    o.init()
    o.login_menu_top.show();
  })

  return o
}


function login_init(o)
{
  var timer;

  o.login_div = $("#login_login");
  o.login_clickable = $("#login_user_name");
  o.login_menu_top = $("#login_menu_top");

  o.login_div.i18n();

  o.login_clickable.append(_self.first_name);

  //Binding
  o.login_clickable.on("click",function (event) {
    login_clicked(o);
  });
}

function nlogin(divid)
{
  var o = {}
  o.divid = divid
  o.div = $("#" + divid);
 
  i18n_init(function ()
  {

  o.div.load("/init/static/views/login.html", function() {
    
    o.div.nlogin_div = $("#login_menu_top_not");
    o.div.login_clickable = $("#login_help");
    o.login_div = $("#login_not_login");
    
    o.div.i18n();
    o.div.nlogin_div.show();
    //Binding
    o.div.login_clickable.on("click",function (event) {
    login_clicked(o);
  });
  });
  });  
}

function login_clicked(o)
{
  o.login_div.toggle("fold", function()
  {
    ;
  });
}