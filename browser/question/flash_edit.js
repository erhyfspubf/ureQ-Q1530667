function confirmJSONFlashApplyQuestion(buttons_body,result){
	var question_body = buttons_body[2].childNodes[0].value;
	buttons_body[2].innerHTML = question_body;
	grow(buttons_body[2]);
}
;

function notifyFlashApplyQuestionFailure(buttons_body,result){
	buttons_body[2].innerHTML = buttons_body[2].childNodes[0].innerHTML;
	
};

function doFlashApplyQuestion(buttons_body){
	pulsate(buttons_body[2]);
	var question_body = buttons_body[2].childNodes[0].value;
	var id = buttons_body[2].parentNode.id;
	var r = proxy.flashEditQuestion([id,question_body]);
	r.addCallback(confirmJSONFlashApplyQuestion,buttons_body);
	r.addErrback(notifyFlashApplyQuestionFailure,buttons_body);
	hideElement(buttons_body[1]);
	showElement(buttons_body[0]);
};

function doFlashEditQuestion(buttons_body){
	showElement(buttons_body[1]);
	hideElement(buttons_body[0]);
	var question_body = buttons_body[2].innerHTML;
	var body_input = createDOM('textarea');
	body_input.innerHTML = question_body;
	buttons_body[2].innerHTML = toHTML(body_input);
	buttons_body[1].onclick = partial(doFlashApplyQuestion,buttons_body);	
};

function addFlashEditQuestionAction(buttons_body){
	buttons_body[0].onclick = partial(doFlashEditQuestion,buttons_body)
};


function initJsonServerForFlashEditQuestion(){
		
	if (currentWindow().full_url == null){
		var full_url = currentDocument().location.href;
		var url = full_url.split('/constructor.html')[0];
		currentWindow().full_url = full_url;
		currentWindow().url = url;
			
	}
	if (currentWindow().proxy == null){
		var proxy = new JsonRpcProxy(url,['flashEditQuestion']);
		currentWindow().proxy = proxy;
	}
	else{
		currentWindow().proxy.addMethods(['flashEditQuestion']);
	};
};


function flashEditQuestion(){
	initJsonServerForFlashEditQuestion();
	var flash_edit_buttons = getElementsByTagAndClassName('img',"FlashEditQuestion");
	var flash_apply_buttons = getElementsByTagAndClassName('img',"FlashApplyQuestion");
	map(function(el){hideElement(el);},flash_apply_buttons)
	var question_bodyes = getElementsByTagAndClassName('div',"QuestionBody");
	var buttons_body_map = zip(flash_edit_buttons,flash_apply_buttons,question_bodyes);
	map(addFlashEditQuestionAction,buttons_body_map);	
};

MochiKit.DOM.addLoadEvent(flashEditQuestion);