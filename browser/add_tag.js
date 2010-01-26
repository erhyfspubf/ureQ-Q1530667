function changeTagInputField(tag_field,text)
	{
		tag_field.value += " " + text;
	};

function addTag()
	{
    for (var i = 1; i < 7; i++) {
		var tag_span_fields = getElementsByTagAndClassName('span', 'tag' + i);
		var tag_input_field = getElement('qreature_form-widgets-tags');
		map(function(el){
			addToCallStack(el, 'onclick', partial(changeTagInputField, tag_input_field, el.innerHTML));
		}, tag_span_fields);
	};
};

MochiKit.DOM.addLoadEvent(addTag);