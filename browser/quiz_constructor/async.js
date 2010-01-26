var extract_form_inputs = function(button){
	
	var form = button.form;
	var form_inputs = filter(function (el){return (el.nodeName == "SPAN") && (el.className == "row")},form.childNodes);
	/*@cc_on
  	@if (@_jscript)
		form_inputs = map(function(el){return el.childNodes[0]}, form_inputs);
  	@else */
		form_inputs = map(function(el){return el.childNodes[1]}, form_inputs);
	/*@end
  	@*/
	form_inputs = map(function (el){return el.childNodes},form_inputs);
	form_inputs = map(function(el){ return  filter(function(el){return (el.nodeType=="1") && (el.type != "hidden")},el)      },form_inputs);
	form_inputs = filter(function(el){return (el.length > 0)},form_inputs);
	form_inputs = flattenArray(form_inputs);
	return form_inputs;
};

var storeResultCollect = function (form_inputs){

	if (form_inputs.length != 2){return}
	var id = map(function (el) {return el.name.split('.')[0]},form_inputs)
	var form_id = id[0];
	var result_id = form_inputs[0].value;
	var result_value = form_inputs[1].value;
	currentWindow().resultsCollect[form_id] = {}
	currentWindow().resultsCollect[form_id]['value'] = result_value;
	currentWindow().resultsCollect[form_id]['result'] = result_id;
};

var updateResultCollectWidget = function (id,diff){
	var results_collect = getElementsByTagAndClassName('span','DependValue');
	map(function(el){
	if (el.id == id){
		el.innerHTML = Number(el.innerHTML) + Number(diff);
		shake(el)	
	};
	},
	results_collect)
};

var changeResultCollect = function (form_inputs) {

	if (form_inputs.length != 2){return}
	var id = map(function (el) {return el.name.split('.')[0]},form_inputs)
	var form_id = id[0];
	var result_id = form_inputs[0].value;
	var result_value = form_inputs[1].value;
	var old_record =  currentWindow().resultsCollect[form_id]

	if (old_record['result'] == result_id){
		updateResultCollectWidget(result_id,result_value - old_record['value']);	
	}
	else {
		var diff = result_value -old_record['value'];
		updateResultCollectWidget(old_record['result'], 0-old_record['value']);
		currentWindow().resultsCollect[form_id] = {};
		updateResultCollectWidget(result_id, result_value);	
	};
	
	storeResultCollect(form_inputs);
};



var addApplyAction = function (apply_button) {
	var form_inputs = extract_form_inputs(apply_button);
	storeResultCollect(form_inputs);
	addToCallStack(apply_button,'onclick',partial(doApply,form_inputs));
};

var doApply = function(form_inputs, evt){
	form_inputs[0].form.onsubmit = function(){return false};
	var values = map(function(el){return el.value},form_inputs)
	var ids = map(function (el) {return el.name.split('.')[0]},form_inputs)
	var to_send = zip(ids,values)
	var r = proxy.applyChanges(to_send);
	r.addCallback(confirmJSONApplySubmit,form_inputs);
	r.addErrback(doHTMLApplySubmit,form_inputs);
};

var confirmJSONApplySubmit = function (form_inputs,result) {
    if (result == "-1"){
		doHTMLApplySubmit(form_inputs,result);
		return;
		};
	changeResultCollect(form_inputs);
	var inline_form = form_inputs[0].form.parentNode;
	shake(inline_form);

};

var doHTMLApplySubmit = function (form_inputs,exp) {
	form_inputs[0].form.onsubmit = function(){return true};
	form_inputs[0].form.submit();
};




var addDeleteAction = function(delete_button){
	delete_button.onclick = partial(doDelete,delete_button)
	//addToCallStack(delete_button,'onclick',partial(doDelete,delete_button));
};

var doDelete = function (delete_button,exp) {
	delete_button.form.onsubmit = function(){return false};
	if (confirm('Удаляем?') == false){return};
	delete_button.form.onsubmit = function(){return false};
	var id = delete_button.name.split('.')[0];
	var r = proxy.deleteObject(id);
	r.addCallback(confirmJSONDeleteSubmit,delete_button);
	r.addErrback(doHTMLDeleteSubmit,delete_button);
};

var confirmJSONDeleteSubmit = function (delete_button,result) {
	if (result == "-1"){
		doHTMLDeleteSubmit(delete_button,result);
		return;
		};
	
	var form_inputs = extract_form_inputs(delete_button);
	updateResultCollectWidget(form_inputs[0].value, 0-form_inputs[1].value);
	
	if (result == "1"){
		hideElement(delete_button.form.parentNode);
		return;
		};
	
	var arrived_parent = delete_button.form.parentNode;
	arrived_parent.className = "";
	arrived_parent.innerHTML = result;
	var arrived = filter(function(el){return el.className == "QreatureInlineForm"},arrived_parent.childNodes)[0]
	arrived = filter(function(el){return el.nodeName == "FORM"},arrived.childNodes)[0];
	arrived = filter(function(el){return el.className == "action"},arrived.childNodes)[0];
	arrived = filter(function(el){return el.nodeName == "INPUT"},arrived.childNodes)[0];
	addAddAction(arrived);
	
	grow(arrived_parent);
};

var doHTMLDeleteSubmit = function (delete_button,exp) {
	delete_button.form.onsubmit = function(){return true};
	delete_button.form.submit();
};



var addAddAction = function(add_button){
	var form_inputs = extract_form_inputs(add_button)
	addToCallStack(add_button,'onclick',partial(doAdd,form_inputs));
};

var doAdd = function (form_inputs,exp) {
	form_inputs[0].form.onsubmit = function(){return false};
	var values = map(function(el){return el.value},form_inputs)
	var ids = map(function (el) {return el.name.split('.')[0]},form_inputs)
	var obs = map(function (el) {return el.name.split('.')[1]},form_inputs)
	var to_send = zip(ids,obs,values)
	var r = proxy.addObject(to_send);
	r.addCallback(confirmJSONAddSubmit,form_inputs);
	r.addErrback(doHTMLAddSubmit,form_inputs);
};

var confirmJSONAddSubmit = function (form_inputs,result) {
	if (result == "-1"){
		doHTMLAddSubmit(form_inputs,result);
		return;
		};
	var arrived_parent = form_inputs[0].form.parentNode;
	arrived_parent.className = "";
	arrived_parent.innerHTML = result;
	var arrived = filter(function(el){return el.className == "QreatureInlineForm"},arrived_parent.childNodes)[0]
	arrived = filter(function(el){return el.nodeName == "FORM"},arrived.childNodes)[0];
	arrived = filter(function(el){return el.className == "action"},arrived.childNodes);
	arrived = map(function (el) {return filter(function (el){return el.nodeName == "INPUT"},el.childNodes)}, arrived)
	arrived = map(function(el){return el[0]},arrived);
	
	delete_button = filter(function(el){return el.value == "Delete"},arrived)[0];
	addDeleteAction(delete_button);
	
	apply_button = filter(function(el){return el.value == "Apply"},arrived)[0];
	addApplyAction(apply_button);
	
	var form_inputs = extract_form_inputs(apply_button);
	updateResultCollectWidget(form_inputs[0].value, form_inputs[1].value);
	grow(arrived_parent);

};

var doHTMLAddSubmit = function (form_inputs,exp) {
	form_inputs[0].form.onsubmit = function(){return true};
	form_inputs[0].form.submit();
};


function initJsonServerForAsyncDepends (){
	if (currentWindow().full_url == null){
		var full_url = currentDocument().location.href;
		var url = full_url.split('/constructor.html')[0];
		currentWindow().full_url = full_url;
		currentWindow().url = url;	
	}
	if (currentWindow().proxy == null){
		var proxy = new JsonRpcProxy(url,['applyChanges','deleteObject', 'addObject']);
		currentWindow().proxy = proxy;
	}
	else{
		currentWindow().proxy.addMethods(['applyChanges','deleteObject', 'addObject']);
	};	
};


var asyncDepends = function () {
	currentWindow().resultsCollect = {};
	initJsonServerForAsyncDepends();
	var actions = getElementsByTagAndClassName('span','action');
	var inputs = map(function (el){return el.childNodes},actions);
	inputs = flattenArguments(inputs); 
	var image_buttons = filter(function(el){return el  != null},inputs);
	image_buttons = filter(function (el) {return el.form.parentNode.className == "QreatureInlineForm"},image_buttons);
	var apply_buttons = filter(function (el) {return el.value == "Apply"},image_buttons);
	map(addApplyAction,apply_buttons);
	var delete_buttons = filter(function (el) {return el.value == "Delete"},image_buttons);
	map(addDeleteAction,delete_buttons);
	var add_buttons = filter(function (el) {return el.value == "Add"},image_buttons);
	map(addAddAction,add_buttons);

};
MochiKit.DOM.addLoadEvent(asyncDepends);