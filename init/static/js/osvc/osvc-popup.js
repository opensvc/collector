//MD

var _stack = [];

function osvc_popup_find_in_stack(value)
{
	for(i=0;i<_stack.length;i++)
	{
		if (value == _stack[i].span)
			return i+1;
	}
	return 0;
}

function osvc_popup_push_to_stack(obj)
{
	var test = osvc_popup_find_in_stack(obj.span);

	if ( test == 0) {
		_stack.push(obj);
	}
}

function osvc_popup_remove_from_stack_by_id(value)
{
	var line = osvc_popup_find_in_stack(value)-1;

	var span = _stack[line].span;

	var target = $(".layout").find("tr[spansum='"+ span + "']");
	target.next().toggle("Blind",function () {
		target.next().remove();
	});

	_stack.splice(line,1); // remove the element

	// Handle children remove
	for(i=0;i<_stack.length;i++)
	{
		if (_stack[i].parent == span) // Children found
		{
			_stack.splice(i,1); // destroy it
		}
	}
}

function osvc_popup_stack_listener()
{
	$(document).bind("DOMNodeInserted", function (e)
	{
		var span ="";
		if (e.target.className == "extraline") 
		{ 
	    	span = e.target.previousSibling.attributes["spansum"].value;
	    }
	    else if (e.target.className == "white_float action_menu")
	    {
	    	span = ".white_float";
	    }
	    else 
	    	return;

	    if (span === undefined || osvc_popup_find_in_stack(span) !=0 ) // if not a tr or already in stack, stop collect
	        return;

	    var parent = e.target.parentElement;
	    var p = null;
	    try {
	    	while(1)
	    	{
	    		parent = parent.parentElement;//.parentElement.parentElement.previousSibling.attributes["spansum"];
	    		if (parent === undefined) break;
	    		else if (parent.className == "extraline") 
	    		{
	    			p = parent.previousSibling.attributes["spansum"].value;
	    			break;
	    		}
	    	}
	    }
	    catch (e)
	    {
	    	// No parent
	    }

	    var id = {"span":span,"parent":p};

	    _stack.push(id); // push rows in stack process
	});

	$(document).bind("DOMNodeRemoved", function (e)
	{
		return;
		var obj = e;

		if (e.target.className == "extraline") return; // if remove by ESC

		try {
	    	var sarray = e.target.offsetParent.attributes["id"].value.split("_"); // collect identifier of the selected row
		}
		catch (e)
		{
			return; // Not a valid stackable element
		}
	    var span = sarray[sarray.length-1];

	    osvc_popup_remove_from_stack_by_id(span);
	    osvc_popup_delete_from_stack({"span":span,"parent":""});
	});
}

function osvc_popup_remove_from_stack() // Remove last item from stack and destroy DOM element
{
	if (_stack.length == 0) return;

	var span = _stack.pop();

	osvc_popup_delete_from_stack(span);
}

function osvc_popup_delete_from_stack(span)
{
	if (span.parent=="menuflash" || span.parent=="menusearch" || span.parent=="menu" || span.span==".white_float") // If menu element 
	{
		$(span.span).hide("fold");
		return;
	}

	var target = $(".layout").find("tr[spansum='"+span.span + "']");
	target.next().toggle("Blind",function () {
		target.next().remove();
	});
	// Handle children remove
	for(i=0;i<_stack.length;i++)
	{
		if (_stack[i].parent == span.span) // Children found
		{
			_stack.splice(i,1); // destroy it
		}
	}
}