function table_packages(divid, options) {
	var defaults = {
		"id": "packages",
		"caller": "table_packages",
		"divid": divid,
		"name": "packages",
		"ajax_url": "/init/packages/ajax_packages",
		"force_cols": ["id", "os_name"],
		"columns": [].concat(["nodename", "id", "pkg_name", "pkg_version", "pkg_arch", "pkg_type", "sig_provider", "pkg_sig", "pkg_install_date", "pkg_updated"], objcols.node),
		"default_columns": ["nodename", "pkg_name", "pkg_version", "pkg_arch", "pkg_type", "sig_provider", "pkg_install_date", "pkg_updated"],
		"wsable": true,
		"events": ["packages_change"]
	}
	var _options = $.extend({}, defaults, options)
	return table_init(_options)
}

