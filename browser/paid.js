function JSONscriptRequest(fullUrl) {
	this.fullUrl = fullUrl; 
    this.noCacheIE = '&noCacheIE=' + (new Date()).getTime();
    this.headLoc = document.getElementsByTagName("head").item(0);
	};
JSONscriptRequest.prototype.buildScriptTag = function () {
	    this.scriptObj = document.createElement("script");
	    this.scriptObj.setAttribute("type", "text/javascript");
	    this.scriptObj.setAttribute("charset", "utf-8");
	    this.scriptObj.setAttribute("src", this.fullUrl + this.noCacheIE);
	    this.scriptObj.setAttribute("src", this.fullUrl);
		this.scriptObj.setAttribute("id", "QuizData");
	};
JSONscriptRequest.prototype.removeScriptTag = function () {
		/*@cc_on
	  	@if (@_jscript)
			//do nothing for ie
	  	@else */
			this.headLoc.removeChild(this.scriptObj);
		/*@end
	  	@*/
};
JSONscriptRequest.prototype.addScriptTag = function () {
	this.headLoc.appendChild(this.scriptObj);
};
function makeUpdate(content){
	window.UserQuiz.innerHTML = content['user_quiz'];
	var proceed = document.getElementById('form-buttons-proceed');
	if (proceed != null) {
		proceed.onclick = function(event){
			makeRequest(proceed);
		};
	};
};
function makeRequest(button){
	window.UserQuiz = button.form.parentNode;
	button.form.onsubmit = function(){return false};
	var inputs = document.getElementsByTagName('input')
	var quiz_answers = {}; var quiz_previous_answers = {}; var has_answers = false;
	for (var i=0; i<inputs.length;i++){
		if ((inputs[i].className == "QuizAnswer") && inputs[i].checked) {
			quiz_answers[inputs[i].name] = inputs[i].value;
			has_answers = true;
		};
		//here the differrent thing!!!!!!!!!!!!!!
		if (inputs[i].className == "QuizPreviousAnswers"){
			quiz_previous_answers[inputs[i].name] = inputs[i].value;	
		};
	};
	var url = 'http://localhost:8080/++skin++Qreature/qreature/1/Quiz-2/paidQuiz'; 
	if (has_answers){url += '?'};
	for (var name in quiz_answers) {
		if (url[url.length -1] != '?'){url +='&'};
		url += name + '=' + quiz_answers[name];
	};
	//local!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	url = url.replace(/http:\/\/localhost:/, 'mock');
	url_array = url.split(":");
	url = url_array.join('%3A');
	url = url.replace(/mock/, 'http://localhost:');
	if (button.id == 'form-buttons-proceed'){url += '&' + button.name + '=proceed'};
	var action = button.form.action;
	if (action.search(/result.html/) != -1){
		url += '&result=result';
	};
	bObj = new JSONscriptRequest(url);
	bObj.buildScriptTag();
	bObj.addScriptTag();
	bObj.removeScriptTag();
};