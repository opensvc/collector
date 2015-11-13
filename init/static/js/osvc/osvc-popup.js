//MD

var _stack = [];

var _stack_className = "stackable";
var _stackcounter = 0;

function osvc_popup_delete_children(value) // Multiple childran can have 1 parent
{
	is = 0;
	// Handle children remove
	for(i=0;i<_stack.length;i++)
	{
		if (_stack[i].parent == value) // Children found
		{
			console.log("splice children : " + _stack[i].span + ' for parent : ' + value);
			_stack.splice(i,1); // destroy it
			is=1;
			break;
		}
	}
	if (is==1) osvc_popup_delete_children(_stack[i].span);
}

function osvc_popup_delete_by_id(value) // Only 1 stack can be found
{
	for(i=0;i<_stack.length;i++)
	{
		if (_stack[i].span == value)
		{
			console.log("splice element :" + _stack[i].span + ' for span : ' + value);
			_stack.splice(i,1);
			break;
		}
	}
	osvc_popup_delete_children(value);
}

function osvc_popup_stack_listener()
{
	var target = document;//.querySelector('');
	 
	// create an observer instance
	var observer = new MutationObserver(function(mutations) {
	  mutations.forEach(function(mutation) {
	  	var classe ="";
	  	if (mutation.addedNodes.length !=0 || mutation.removedNodes.length !=0) // Add or remove nodes
		  	{
		  	try {

		  		for(i=0;i<mutation.addedNodes.length;i++)
		  		{
		  			if (mutation.addedNodes[i].className.indexOf(_stack_className) != -1)
		  			{
		  				if (mutation.addedNodes[i].attributes !== undefined &&
		  					mutation.addedNodes[i].attributes["style"] != null) 
		  				{
		  					if (mutation.addedNodes[i].attributes["style"].value.indexOf("display: none") != -1)
		  						break;
		  				}
		  				// Gather parent
		  				var parent = mutation.addedNodes[i].parentElement;
					    var p = null;
					    try {
					    	while(1)
					    	{
					    		parent = parent.parentElement;//.parentElement.parentElement.previousSibling.attributes["spansum"];
					    		if (parent === undefined) break;
					    		else if (parent.className.indexOf("stackable") != -1) 
					    		{
					    			p = parent.attributes["stack_id"].value;
					    			break;
					    		}
					    	}
					    }
					    catch (e)
					    {
					    	// No parent
					    }
					    var sc = "A"+ (++_stackcounter).toString();
		  				$(mutation.addedNodes[i]).attr('stack_id', sc);
		  				_stack.push({"span":sc,"parent" : p});
		  				console.log("add stack for " + mutation.addedNodes[i].className + " : " + sc);
		  			}
		  		}
		  	 	for(i=0;i<mutation.removedNodes.length;i++)
		  		{
		  			if (mutation.removedNodes[i].className.indexOf(_stack_className) != -1)
		  			{
		  				if (mutation.removedNodes[i].attributes["stack_id"] != undefined)
		  				{
		  					var s = mutation.removedNodes[i].attributes["stack_id"].value;
		  					console.log("del stack for " + mutation.removedNodes[i].className + " : " + s);
		  					osvc_popup_delete_by_id(s);
		  				}
		  			}
		  		}
			}
			catch (e)
			{

			}
		}
		else // Show/hide
		  	{
		  	try {
		  		if (mutation.target.className.indexOf(_stack_className) != -1)
		  		{
		  			if (mutation.target.attributes["style"].value.indexOf("display: none") != -1)
		  			{
		  				if (mutation.target.attributes["stack_id"] != undefined)
		  				{
		  					var s = mutation.target.attributes["stack_id"].value;
		  					console.log("del v stack for " + mutation.target.className + " : " + s);
							osvc_popup_delete_by_id(s);
							mutation.target.removeAttribute('stack_id');
		  				}
		  			}
		  			else
		  			{
		  				if ($(mutation.target).attr('stack_id') == undefined)
		  				{
		  					var sc = "V"+(++_stackcounter).toString();
		  					$(mutation.target).attr('stack_id', sc);
		  					$(mutation.target).css({'z-index': 1000+_stack.length});
		  					_stack.push({"span":sc,"parent":""});
		  					console.log("add v stack for " + mutation.target.className + " : " + sc);
		  				}
		  			}
		  		}
		  	}
			catch (e)
			{

			}
		}	

	  });    
});

// configuration of the observer:
var config = { attributes: true, childList: true, characterData: true, subtree: true, attributeFilter:['style','class']};
 
// pass in the target node, as well as the observer options
observer.observe(target, config);

}

function osvc_popup_remove_from_stack() // Remove last item from stack and destroy DOM element
{
	if (_stack.length == 0) return;

	var span = _stack.pop();

	osvc_popup_delete_from_stack(span);
}

function osvc_popup_delete_from_stack(span)
{
	var target = $(document).find("[stack_id='"+span.span + "']");

        if (target.hasClass("menu") || (target.parents(".menu").length > 0)) {
          target.hide("blind")
        } else {
          target.hide()
        }
}
