# -*- coding: cp1251 -*-

from z3c.form import form, button, field, interfaces
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.traversing.browser import absoluteURL
from z3c.form.i18n import MessageFactory as _
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from qreature.browser.interfaces import IQreatureEditableView, IQreatureAddForm,\
                                         IQreatureEditForm, IQreatureActions
from zope.app.component.hooks import getSite
from qreature.interfaces import IQuiz
from zope.contentprovider.interfaces import IContentProvider
from zope.component import getMultiAdapter, getUtility
from qreature.browser.interfaces import IQreatureView,IQreaturePicturedView,IQreatureContentTitle
#from zope.app.intid.interfaces import IIntIds
from qreature.interfaces import IQreatureIntIds
from qreature.browser.interfaces import IQreaturePictureLink,\
                                        IQreaturePrefixedButton,ISourceCode,\
                                        IPreviewForm
from qreature.browser.events import CachedObjectChangedEvent
from qreature.interfaces import IQuizContainer
#Bad! Its better to move this interface upper. To this level. Not user_quiz!
from z3c.form.interfaces import IFieldWidget
from zope.interface import Interface
from qreature.browser.user_quiz.interfaces import IPublished,IChecked
from zope.schema import Text
from goog.photo.browser import GoogImageUploadForm                
from qreature.interfaces import IQreatureFolder
from pagable.interfaces import IPagableRelative
from zope.component import queryUtility
from qreature.browser.interfaces import IAdditionalAdjustment
from zope.component import adapts
from z3c.form.browser.checkbox import SingleCheckBoxWidget
from z3c.form.widget import FieldWidget
from zope.interface import alsoProvides, noLongerProvides
from zope.security.proxy import removeSecurityProxy
from qreature.browser.interfaces import  IOpenResultsQuiz,IOpenValuesQuiz,ICommentSubscriberQuiz,IPaidQuiz
from zope.app.container.interfaces import IAdding
from commentable.interfaces import ICommentable

    
class QreatureView(object):
    implements(IQreatureView)
    viewlets = None
    nothing = False
    def render(self):
        raise NotImplementedError
    def gimmeViewlets(self):
        for viewlet in self.viewlets:
            yield viewlet
    def gimmeUpdate(self):
        raise NotImplementedError
    
    
class QreatureEditableView(object):
    """ This class is a marker for Action viewlet"""
    implements(IQreatureEditableView)
    button_titles = True


PICTURES = ['scale','slots','publish','lead','depends','value', 'preview',
             'edit', 'delete','apply', 'answer','question', 'qreature_icon',
             'check','preview','back','user', 'rss', 'flash_edit','flash_apply']

class QreaturePicturedView(object):
    implements(IQreaturePicturedView)
    def gimmePicturesUrls(self):
        site = getSite()
        site_url = absoluteURL(site, self.request)
        urls = {}
        for picture in PICTURES:
            urls.update({picture: str(site_url + '/@@/' + picture + '.jpg')})
        return urls

#icon = queryMultiAdapter((obj, self.request), name='zmi_icon')

class QreatureForm(object):
    implements(IPagableRelative)
    template = ViewPageTemplateFile('templates/qreature_form.pt')
    prefix = 'qreature_form.'
    @property
    def button_name(self):
        raise NotImplementedError
    @property
    def form_name(self):
        raise NotImplementedError
    

class QreatureAddForm(QreatureForm,form.Form):
    
    implements(IQreatureAddForm)
    buttons = button.Buttons(button.ImageButton (name='add',title=u'Add',image=u'add.jpg'))
    ignoreContext = True
    ignoreReadonly = True
    _finishedAdd = False
    formErrorsMessage = _('There were some errors.')
    
    @property
    def fields(self):
        raise NotImplementedError
    
    @button.handler(buttons['add'])
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True
    
    def createAndAdd(self, data):
        obj = self.create(data)
        notify(ObjectCreatedEvent(obj))
        #clean objects only in constructor View (exclude cleaning viewlets if adding to QreatureFolder)
        obj = self.add(obj)
        if IQuizContainer.providedBy(self.context.context):
            notify(CachedObjectChangedEvent([obj]))
        return obj
    
    def create(self, data):
        raise NotImplementedError
    
    def add(self, object):
        ob = self.context.add(object)
        self._finishedAdd = True
        return ob

    def nextURL(self):
#        for v in self.request:
#            if 'uri' in v.split('.'):
#                uri = self.request.get(v)
        print "Whats up man??? Where is my nextURL????"
        for v in self.request:
            if 'uri' in v.split('.'):
                uri = self.request.get(v)
        if uri is not None and uri != u'':
            print 'I am returning uri!!!!!!!!'
            print uri
            print "that was an uri. and this is uri type:"
            print type(uri)
            return uri
        else:
            print "---------------------------------"
            if IAdding.providedBy(self.context):
                context = self.context.context
                print "context is changed cause IAdding"
            else:
                context = self.context
            if IQuizContainer.providedBy(context):
                quiz = getSite()
                print 'I am returning constructor !!!!!!!!'
                return absoluteURL(quiz, self.request) + u'/constructor.html'
            elif IQreatureFolder.providedBy(context):
                print 'I am returning main !!!!!!!!'
                return absoluteURL(context, self.request) + u'/main.html'
            elif ICommentable.providedBy(context):
                print 'I am returning thread !!!!!!!!'
                return absoluteURL(context, self.request) + u'/thread.html'
            else:
                print "Fucking shit!!!!!!!!!"
        
        
        return uri
    
    def render(self):
        if self._finishedAdd:
            self.request.response.redirect(self.nextURL())
            return ""
        return super(QreatureAddForm, self).render()
    
    
class QreatureEditForm(QreatureForm,form.EditForm):
    
    implements(IQreatureEditForm)
    buttons = button.Buttons(button.ImageButton
                             (name='apply',title=u'Apply',image=u'apply.jpg'))
    @button.handler(buttons['apply'])
    def handleApply(self, action):
        super(QreatureEditForm,self).handleApply(self,action)
        if IQuizContainer.providedBy(self.context):
            notify(CachedObjectChangedEvent([self.context]))
    
    
    button_name = u'Изменить'



    
class QreatureActions(object):
    """ This class is only here to register buttons for it. This is a viewlet!"""
    implements(IQreatureActions)
    viewlets = None
    render = ViewPageTemplateFile('templates/actions.pt')
    def update(self):
        self.viewlets = []
        bvm = getMultiAdapter((self.context, self.request, self),IContentProvider, name="qreature.QreatureButtonsMenuVM")
        bvm.update()
        self.viewlets = bvm
        
class QreatureContentTitle(QreaturePicturedView):
    
    implements(IQreatureContentTitle)
    render = ViewPageTemplateFile('templates/qreature_content_title.pt')
    
    @property
    def css_class(self):
        raise NotImplementedError
        
    
    def __call__(self):
        self.update()
        return self.render
    
    @property
    def picture(self):
        raise NotImplementedError
        
    def gimmeIcon(self):
        urls = self.gimmePicturesUrls()
        return urls[self.picture]

    



IMG_BEG = u'<img border="0" alt="онлайн тест" src="'
IMG_MID = u'/@@/'
IMG_END = u'.jpg"/>'
URL_MID = u'/'
URL_END = u'.html'


def generateImageTag(image_name, request):
    site = getSite()
    site_url = absoluteURL(site, request)
    return (IMG_BEG + site_url +IMG_MID + image_name + IMG_END)
    

def quiz_or_folder(context):
    if IQuiz.providedBy(context):
        return context.__parent__
    return context
    


class QreaturePrefixedButton(object):
    implements(IQreaturePrefixedButton)
    @property
    def prefix(self):
        context = quiz_or_folder(self.context)
        int_ids = queryUtility(IQreatureIntIds, context=context)
        if int_ids is None:
            quiz = removeSecurityProxy(getSite())
            sm = quiz.getSiteManager()
            int_ids = sm['intids']
        return str(int_ids.getId(self.context))
    

class QreaturePictureLink(object):
    render = ViewPageTemplateFile('templates/picture_link.pt')
    implements(IQreaturePictureLink)
    
    def __call__(self):
        self.update()
        return self.render()
    
    def gimmeLink(self):
        
        overriden_url = self.url
        
        try:
            url = absoluteURL(self.context,self.request)
        except:
            url = 'deleted'
        
        image_tag = generateImageTag(self.image,self.request)
        return {'url':(url + overriden_url),\
                'image':image_tag,\
                'title':self.title}
    title=u''
    image = ''
    url=''
    css_class = "picture_menu"
    @property
    def show_title(self):
        editable_view = self.__parent__.__parent__
        if IQreatureEditableView.providedBy(editable_view): return editable_view.button_titles
        return True

from commentable.interfaces import IHeadView
from elementtree import ElementTree as et
class PreviewForm(QreaturePrefixedButton,form.Form):
    
    implements(IPreviewForm, IHeadView)
    buttons = button.Buttons(button.Button
                             (name='proceed_first',title=u'Test'))
    template = ViewPageTemplateFile('templates/preview_form.pt')
    quiz = None
    source = True
    need_button = True
    values = 0
    rolled = True
    root = False
    
    def update(self):
        if self.quiz is None:
            self.quiz = getSite()
        super(PreviewForm, self).update()
    
    @property
    def fields(self):
        fields = field.Fields(IQuizContainer['body'],mode=interfaces.DISPLAY_MODE)
        fields['body'].widgetFactory = bodyForPreviewWidgetFactory
        if self.do_i_need_source_widget():
            source_fields = field.Fields(ISourceCode['source'], mode=interfaces.INPUT_MODE)
            source_fields['source'].widgetFactory = sourceCodeWidgetFactory(self.prefix)
            fields += source_fields
        return fields
    
    def gimmeTitle(self):
        return {'icon':generateImageTag('qreature_icon',self.request),'title':self.quiz.title}
    
    def gimmeLink(self):
        url = absoluteURL(self.quiz, self.request) + '/go.html'
        return url[:7] + 'www.' + url[7:]
    
    def do_i_need_source_widget(self):
        return self.source and IPublished.providedBy(self.quiz)
    
    
    
    def gimme_records_in_order(self):
        """ this method moves action one widget up in the form"""
        records = [item for item in self.widgets.items()] + \
                  [item for item in self.actions.items()]
        records = [value for name,value in records]
        #move source widget down, after the button
        
        if self.do_i_need_source_widget():
            if self.need_button:
                records = records[0:-2] + [records[-1]] + [records[-2]]
            else:
                records = records[0:-1]
        else:
            if not self.need_button:
                records = records[0:-1]
            #This is source code form. The last record is a button
            #install onclick script here!
            #THIS CODE MUST BE ONLY FOR PAID QUIZES
            else:
                if self.context is self.quiz and IPaidQuiz.providedBy(self.context):
                    records[-1].onclick = u'return makeRequest(this);'
                    records[-1].type = "button"
                
                
        return records
    
    @button.handler(buttons['proceed_first'])
    def handleProceedFirst(self, action):
        pass
    
    def gimmeAction(self):
        return absoluteURL(self.quiz, self.request) + '/go.html'
    
    
    def gimmeForm(self):
        return ViewPageTemplateFile('templates/preview_form_code.pt').__call__(self)
        
    
    def render(self):
        '''See interfaces.IForm'''
        if not self.source:
            return self.gimmeForm()
        return self.template()
    
    def gimmePHbb(self):
        """ I could prepare title manually, but the body could contain html tags.
        it need to remove em, except <img>. Instead of <img> insert [img]"""
        quiz = getSite()
        quiz_url = absoluteURL(quiz, self.request)
        phbtitle = u'[img]' + quiz_url + '/@@/qreature_icon.jpg [/img][b]' + self.context.title + u'[/b]'
        
        try:
            nbsp = '&nbsp;'
            def cleanNBSP(text):
                if nbsp in text:
                    i = text.index(nbsp)
                    text = text[:i] + text[i+len(nbsp):]
                    text = cleanNBSP(text)
                return text
            body = cleanNBSP(self.context.body)
            body = u'<div>' +  body + u'</div>'
            body = et.XML(body.encode('UTF-8'))
            
            def parseTag(tag):
                
                text = tag.text
                 
                if text is not None:
                    if tag.tag == 'b' or tag.tag == 'strong':
                        text = '[b]' + text + '[/b]'
                    elif tag.tag == 'i':
                        text = '[i]' + text + '[/i]'
                    elif tag.tag == 'em':
                        text = '[i]' + text + '[/i]'
                    elif tag.tag == 'a':
                        text = '[url=' + tag.attrib['href'] + ']' + text + '[/url]'
                    elif tag.tag == 'u':
                        text = '[u]' + text + '[/u]'
                    elif tag.tag == 'p':
                        text = "\n" + text + "\n"
                    elif tag.tag == 'div':
                        text = "\n" + text + "\n"
                        
                else:
                    if tag.tag == 'img':
                        text = '[img]' + tag.attrib['src'] + '[/img]'
                    elif tag.tag == 'url':
                        text = '[url]' + tag.attrib['href'] +'[/url]'
                    elif tag.tag == 'br':
                        text = "\n"
                    elif tag.tag == 'p':
                        text = "\n"
                    elif tag.tag == 'div':
                        text = "\n"
                
                if text is None: text = ''
                
                if tag.tail is not None:
                    text += tag.tail
                
                for t in tag.getchildren():
                    text += parseTag(t)
                if tag.tag == 'p' or tag.tag == 'div': text += "\n"
                return text
            
            phbbody = parseTag(body)
        except:
            phbbody = '' 
        phbbody += "\n" + '[url=' + quiz_url + '/go.html]' + u'Пройти тест' + '[/url]'      
        
        return phbtitle + "\n" + phbbody
            
            
            
            
                
        
        


def bodyForPreviewWidgetFactory(field,request):
    new_field = Text(title=u'Содержание', default=u'', required=True)
    new_field.__name__ = field.__name__
    widget = getMultiAdapter((new_field, request), IFieldWidget)
    return widget

def sourceCodeWidgetFactory(field_prefix):
    quiz = getSite()
    qreature_folder = quiz.__parent__
    context_id = int(field_prefix)
    context = getUtility(IQreatureIntIds, context=quiz).queryObject(context_id)
    if context is None:
        context = getUtility(IQreatureIntIds, context=qreature_folder).getObject(context_id)
    def realSourceCodeWidgetFactory(field, request):
        widget = getMultiAdapter((field, request), IFieldWidget) 
        code = getMultiAdapter((context, request),Interface, name="preview.html")
        code.source = False
        code.update()
        render = code.render()
        #THIS CODE MUST BE ONLY FOR PAID QUIZES
        if context is quiz and IPaidQuiz.providedBy(context):
            render += u'<script type="text/javascript" src="' + absoluteURL(context, request) + \
                                 u'/@@/paid.js"></script>'
        def clean_render():
            return render
        widget.extract = clean_render
        return widget
    return realSourceCodeWidgetFactory

class NotFound(object):
    def notPublished(self):
        if IQuiz.providedBy(self.context) and not IPublished.providedBy(self.context):
            return True
        return False
    def notChecked(self):
        if IQuiz.providedBy(self.context) and not IChecked.providedBy(self.context):
            return True
        return False
    
    
class QreatureAbouted(object):
    """ This class has a viewlet 'about the project'
    any view wanted to render the viewlet must inherit from it"""
    def update(self):
        pass
    render = ViewPageTemplateFile('./templates/about.pt')
    



def singleCheckBoxWidgetFactory(field,request):
    checkbox = SingleCheckBoxWidget(request)
    return FieldWidget(field,checkbox)



additional_values_interfaces_map = {'need_results':IOpenResultsQuiz,'need_values':IOpenValuesQuiz, 'subscribe_on_to_comments':ICommentSubscriberQuiz}


    
class AdditionalQuizAdjustment(QreatureForm, form.Form):

    def __init__(self,context,request,view,manager):
        self.context = context
        self.request = request
        self.__parent__ = view
        self.manager = manager

    _fields = field.Fields(IAdditionalAdjustment).omit('quiz')
    
    def get_fields(self):
        for f in self._fields.values():
            if f.interface is IAdditionalAdjustment:
                f.widgetFactory = singleCheckBoxWidgetFactory
        return self._fields
    def set_fields(self,value):
        self._fields = value
    fields = property(get_fields,set_fields)
    
    template = ViewPageTemplateFile('./templates/additional_quiz_adjustment.pt')
    
    form_name = u'Дополнительные настройки'
    
    buttons = button.Buttons(button.ImageButton
                             (name='change',title=u'Apply',image=u'apply.jpg'))
    
    @button.handler(buttons['change'])
    def handleChange(self, action):
        data, errors = self.extractData()
        for name, field in self.fields.items():
        # If the field is not in the data, then go on to the next one
            quiz = removeSecurityProxy(self.context)
            if name not in data:
                continue
            if data[name] == True:
                alsoProvides(quiz,additional_values_interfaces_map[name])
            else:
                noLongerProvides(quiz,additional_values_interfaces_map[name])
        
    
    button_name = u'Применить'
    
class AdditionalAdjustment(object):
    implements(IAdditionalAdjustment)
    adapts(IQuiz)
    need_values = False
    need_results = False
    subscribe_on_to_comments = False
    def __init__(self,context):
        self.quiz = context
        for name,interface in additional_values_interfaces_map.items():
            if interface.providedBy(self.quiz):
                self.__setattr__(name, True) 



class GoogImageForQuizContainer(GoogImageUploadForm ):
    
    def userAlbumId(self):
        folder = self.context
        while not IQreatureFolder.providedBy(folder):
            folder = folder.__parent__
        int_ids = getUtility(IQreatureIntIds, context = folder)
        return int_ids.getId(folder)
        

