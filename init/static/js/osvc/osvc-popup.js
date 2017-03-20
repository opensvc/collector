var _stack = [];
var _stack_counter = 0;
var _stack_className = "stackable";

function osvc_popup_remove_from_stack()
{
	// public function
	// pop from stack and hide DOM element

	if (_badIE) {
		$(document).find(".stackable").hide()
		return
	}
	if (_stack.length == 0) {
		return
	}
	var span = _stack.pop()
	osvc_popup_hide(span)
}

function osvc_popup_stack_log_stack() {
	// dump the stack to the console
	for (var i=0; i<_stack.length; i++) {
		console.log(_stack[i].span, _stack[i].parent)
	}
}

function osvc_popup_get_stack_index_of(value) {
	if (value == undefined) {
		return -1
	}
	for (var i=0; i<_stack.length; i++) {
		if (_stack[i].span == value) {
			return i
		}
	}
	return -1
}

function osvc_popup_delete_children(value)
{
	// handle children remove
	for(var i=0; i<_stack.length; i++) {
		if (_stack[i].parent != value) {
			continue
		}
		// remove children
		var e = _stack.splice(i, 1);

		// recurse
		osvc_popup_delete_children(e.span);
	}
}

function osvc_popup_delete_by_id(value)
{
	var idx = osvc_popup_get_stack_index_of(value)
	if (idx < 0) {
		return
	}
	_stack.splice(idx, 1);
	osvc_popup_delete_children(value);
}

function osvc_popup_get_parent_id(e) {
        p = e.parents("."+_stack_className).first()
        if (p.length == 0 || !p.is("[stack_id]")) {
		p = null;
	} else {
		p = p.attr("stack_id")
	}
	return p
}

function osvc_popup_stack_listener_mutation_handler_add_node(mutation, node) {
	var e = $(node)
	if (!e.hasClass(_stack_className)) {
		return
	}
	if (!e.is(":visible")) {
		return
	}
        if (e.is("[stack_id]")) {
		return
	}

	p = osvc_popup_get_parent_id(e)
	var stack_id = "p"+ (_stack_counter++).toString();
	e.attr('stack_id', stack_id);
	_stack.push({"span": stack_id, "parent": p});
	//console.log("stack push (add mutation)", stack_id, e);
}

function osvc_popup_stack_listener_mutation_handler_add(mutation) {
  	if (mutation.addedNodes.length == 0) {
		return
	}
  	for (var i=0; i<mutation.addedNodes.length; i++) {
		osvc_popup_stack_listener_mutation_handler_add_node(mutation, mutation.addedNodes[i])
  	}
}

function osvc_popup_stack_listener_mutation_handler_remove_node(node) {
	var e = $(node)
	if (!e.hasClass(_stack_className)) {
		return
	}
        if (!e.is("[stack_id]")) {
		return
	}
	var stack_id = e.attr("stack_id")
  	//console.log("stack del (delete mutation)", stack_id, e);
	osvc_popup_delete_by_id(stack_id);
	e.removeAttr('stack_id');
}

function osvc_popup_stack_listener_mutation_handler_remove(mutation) {
  	if (mutation.removedNodes.length == 0) {
		return
	}
	for (var i=0; i<mutation.removedNodes.length; i++) {
		osvc_popup_stack_listener_mutation_handler_remove_node(mutation.removedNodes[i])
	}
}

function osvc_popup_stack_listener_mutation_handler_show(mutation) {
	var e = $(mutation.target)
	if (!e.hasClass(_stack_className)) {
		return
	}
	if (!e.is(":visible")) {
		if (e.is("[stack_id]")) {
			var stack_id = e.attr("stack_id")
			//console.log("stack del (hide mutation)", stack_id, e)
			osvc_popup_delete_by_id(stack_id);
			e.removeAttr('stack_id');
		}
	} else {
		if (!e.is("[stack_id]")) {
			var stack_id = "p"+(_stack_counter++).toString();
			p = osvc_popup_get_parent_id(e)
			e.attr('stack_id', stack_id);
			_stack.push({"span": stack_id, "parent": p});
			//console.log("stack push (show mutation)", stack_id, e)
		}
	}
}

function osvc_popup_stack_listener_mutation_handler(mutation) {
	osvc_popup_stack_listener_mutation_handler_add(mutation)
	osvc_popup_stack_listener_mutation_handler_remove(mutation)
	osvc_popup_stack_listener_mutation_handler_show(mutation)
}


function osvc_popup_stack_listener_callback(mutations) {
	mutations.forEach(function(mutation) {
		osvc_popup_stack_listener_mutation_handler(mutation)
	})
}

function osvc_popup_stack_listener()
{
	if (_badIE) return; // No stack function if IE9>10
	console.log("init popup event observer")
	var target = document;
	 
	var observer = new MutationObserver(osvc_popup_stack_listener_callback)

	// configuration of the observer:
	var config = { attributes: true, childList: true, characterData: true, subtree: true, attributeFilter:['style','class']};
 
	// pass in the target node, as well as the observer options
	observer.observe(target, config);
}

function osvc_popup_hide(span)
{
	var target = $(document).find("[stack_id='"+span.span + "']")

        if (target.hasClass("menu") || (target.parents(".menu").length > 0)) {
		target.stop().slideUp(function(){
			osvc.body_scroll.enable()
		})
        } else {
		target.hide()
        }
	if (target.hasClass("empty_on_pop")) {
		target.empty()
	}
}
