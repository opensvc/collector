function format_filters(d) {
        fset_id = d[0]
        s = ""
        for (id in d[1]) {
                data = d[1][id]
                if (data['id'] == fset_id) {
                        selected = "selected"
                } else {
                        selected = ""
                }
                s += "<option value="+data['id']+" "+selected+">"+data['fset_name']+"</option>"
        }
        return s
}

function init_filters(event, data) {
        $.getJSON("{{=URL(r=request, f='call/json/json_filters')}}", function(data) {
                e = format_filters(data)
                $("#filters").append(e).selectmenu('refresh')
        });
        $('#filters').change('select', select_filter)
}

function select_filter(event, data) {
        $.getJSON("{{=URL(r=request, f='call/json/json_set_filter')}}/"+$(this).attr('value'), function(data) {
		location.reload()
        });
}

