function confirmJSONFlashApplyAnswer(buttons_body,result){
	var question_body = buttons_body[2].childNodes[0].value;
	buttons_body[2].innerHTML = question_body;
	grow(buttons_body[2]);
}
;

function notifyFlashApplyAnswerFailure(buttons_body,result){
	buttons_body[2].innerHTML = buttons_body[2].childNodes[0].innerHTML;
	
};

function doFlashApplyAnswer(buttons_body){
	pulsate(buttons_body[2]);
	var question_body = buttons_body[2].childNodes[0].value;
	var id = buttons_body[2].parentNode.id;
	var r = proxy.flashEditAnswer([id,question_body]);
	r.addCallback(confirmJSONFlashApplyAnswer,buttons_body);
	r.addErrback(notifyFlashApplyAnswerFailure,buttons_body);
	hideElement(buttons_body[1]);
	showElement(buttons_body[0]);
};

function doFlashEditAnswer(buttons_body){
	showElement(buttons_body[1]);
	hideElement(buttons_body[0]);
	var question_body = buttons_body[2].innerHTML;
	var body_input = createDOM('textarea');
	body_input.innerHTML = question_body;
	buttons_body[2].innerHTML = toHTML(body_input);
	buttons_body[1].onclick = partial(doFlashApplyAnswer,buttons_body);	
};

function addFlashEditAnswerAction(buttons_body){
	buttons_body[0].onclick = partial(doFlashEditAnswer,buttons_body)
};


function initJsonServerForFlashEditAnswer (){
	if (currentWindow().full_url == null){
		var full_url = currentDocument().location.href;
		var url = full_url.split('/constructor.html')[0];
		currentWindow().full_url = full_url;
		currentWindow().url = url;	
	}
	if (currentWindow().proxy == null){
		var proxy = new JsonRpcProxy(url,['flashEditAnswer']);
		currentWindow().proxy = proxy;
	}
	else{
		currentWindow().proxy.addMethods(['flashEditAnswer']);
	};
};


function flashEditAnswer(){
	initJsonServerForFlashEditAnswer();
	var flash_edit_buttons = getElementsByTagAndClassName('img',"FlashEditAnswer");
	var flash_apply_buttons = getElementsByTagAndClassName('img',"FlashApplyAnswer");
	map(function(el){hideElement(el);},flash_apply_buttons)
	var answer_bodyes = getElementsByTagAndClassName('div',"AnswerBody");
	var buttons_body_map = zip(flash_edit_buttons,flash_apply_buttons,answer_bodyes);
	map(addFlashEditAnswerAction,buttons_body_map);	
};

MochiKit.DOM.addLoadEvent(flashEditAnswer);