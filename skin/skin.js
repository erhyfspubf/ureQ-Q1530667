function round(){
	roundElement(getElement('site_menu'),{corners:'top', bgColor: '#000000'});
	roundElement(getElement('site_menu'),{corners:'bottom', bgColor: 'white'});
	roundElement(getElement('hdr'));
	roundClass('h1','about');
	roundClass('p','about');
};

MochiKit.DOM.addLoadEvent(round);
