//
// login menu when logged-in
//
function login(divid) {
	var o = {}
	o.divid = divid
	o.div = $("#"+divid)

	o.div.load("/init/static/views/login.html?v="+osvc.code_rev, function() {
		o.init()
		o.login_menu_top.show()
	})

	o.init = function() {
		o.div.addClass("clickable")
		o.login_div = $("#login_login")
		o.login_clickable = $("#login_user_name")
		o.login_menu_top = $("#login_menu_top")

		o.login_div.i18n()
		o.login_clickable.append(_self.first_name)

		//Binding
		o.div.on("click",function (event) {
			login_clicked(o)
		})
	}

	return o
}

function login_clicked(o) {
	if (o.login_div.is(":visible")) {
		o.login_div.slideUp()
	} else {
		$(".header").find(".menu").hide()
		o.login_div.slideDown()
	}
}


//
// menu when not logged-in
//
function nlogin(divid) {
	var o = {}
	o.divid = divid
	o.div = $("#" + divid)
 
	i18n_init(function () {
		o.div.load("/init/static/views/login.html?v="+osvc.code_rev, function() {
			o.div.nlogin_div = $("#login_menu_top_not")
			o.div.login_clickable = $("#login_help")
			o.login_div = $("#login_not_login")

			o.div.i18n()
			o.div.nlogin_div.show()

			//Binding
			o.div.login_clickable.on("click",function (event) {
				login_clicked(o)
			})
		})
	})

	return o
}

