//MD

var _stack = [];

function osvc_popup_is_in_stack(value)
{
	return (_stack.indexOf(value) > -1);
}

function osvc_popup_listen_for_row_change(table_id)
{
	$("#"+table_id).on("click", "tr", function (e) 
	{ // Listen for any Rows/Columns click
		if (e.currentTarget.attributes["spansum"] === undefined) return; // Not a DOM element

	    var span = e.currentTarget.attributes["spansum"].value; // collect identifier of the selected row

	    if (span === undefined || osvc_popup_is_in_stack(span)) // if not a tr or already in stack, stop collect
	    	return;

	    _stack.push(span); // push rows in stack process
	});
}

function osvc_popup_remove_from_stack() // Remove last item from stack and destroy DOM element
{
	var span = _stack.pop();

	$("#"+table_id).find("tr[spansum='"+span + "']").next().remove();
}