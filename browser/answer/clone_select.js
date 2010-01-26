function cloneSelect(){
    var selects = getElementsByTagAndClassName('select', 'answer_lead');
	if (selects.length == 0){return};
	var options = selects[0].options;
	for (var i = 1; i < selects.length; i++) {
        options_to_insert = '';
        if (selects[i].options.length === 1) {
            var selected_value = getNodeAttribute(selects[i].options[0], 'value');
        }
        else {
            var selected_value = null;
        };
        for (var g = 0; g < options.length; g++) {
            var current_value = getNodeAttribute(options[g], 'value');
			var current_id = getNodeAttribute(options[g], 'id');
            var current_option = createDOM('option');
            setNodeAttribute(current_option, 'value', current_value);
            setNodeAttribute(current_option, 'id', current_id);
			if (current_value === selected_value) {
                setNodeAttribute(current_option, 'selected', 'selected');
            };
            /*@cc_on
		  	@if (@_jscript)
				current_option.innerHTML = options[g].text
				selects[i].appendChild(current_option);
		  	@else */
				current_option.text = options[g].text
				options_to_insert += toHTML(current_option);
			/*@end
		  	@*/
        };

	    /*@cc_on
	  	@if (@_jscript)
			//do nothing for ie
	  	@else */
			selects[i].innerHTML = options_to_insert;
		/*@end
	  	@*/
		


    };
};

MochiKit.DOM.addLoadEvent(cloneSelect);









