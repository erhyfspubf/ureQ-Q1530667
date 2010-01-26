# -*- coding: cp1251 -*-

from z3c.form import form, button, field
from qreature.browser.quiz_constructor.interfaces import IQuizAsXMLView
from zope.interface import implements
from zope.app.pagetemplate import ViewPageTemplateFile
from qreature.browser.qreature_views import QreatureForm, QreaturePicturedView
from z3c.form.interfaces import IFieldWidget, DISPLAY_MODE
from zope.component import getMultiAdapter
from zope.traversing.browser import absoluteURL
from multi_traverser.interfaces import IMultiTraverserClient
from qreature.interfaces import IQuizAsXML, IQuiz
from zope.component import adapts
from qreature.browser.events import CleanCacheEvent
from zope.event import notify
from zope.security.proxy import removeSecurityProxy

def downloadWidgetFactory(field,request):
    widget = getMultiAdapter((field,request), IFieldWidget)
    widget.render = lambda: u''.join((u'<div class="XMLDownload"><a href="',absoluteURL(widget.context, request),
                                        u'/',widget.context.title,u'.qml">',widget.context.title,u'.qml</a></div>'))
    widget.structure = True
    return widget

class QuizAsXMLView(QreatureForm, form.Form):
    
    implements(IQuizAsXMLView)
    
    def __init__(self, context,request,view,manager):
        self.context = context
        self.request = request
        self.__parent__ = view
        self.manager = manager
    
    template = ViewPageTemplateFile('./templates/quiz_as_xml.pt')
    buttons = button.Buttons(button.ImageButton (name='add',title=u'Add',image=u'add.jpg'))
    
    _fields = field.Fields(IQuizAsXML)
    
    def get_fields(self):
        self._fields['download'].mode = DISPLAY_MODE
        self._fields['download'].widgetFactory = downloadWidgetFactory
        return self._fields
    
    def set_fields(self,value):
        self._fields = value

    fields = property(get_fields,set_fields)
    
    @button.handler(buttons['add'])
    def handleAdd(self, action):
        file_upload = self.request.get('qreature_form.widgets.upload')
        if file_upload is None or file_upload == "":
            self.status = u'Нужен xml файл!'
            return
        qax = IQuizAsXML(self.context)
        err_message = qax.generateQuiz(file_upload)
        if err_message is not None:
            self.status = err_message
            return
        notify(CleanCacheEvent(self.context))
        self.request.response.redirect(self.request.URL)
    

class QuizXMLTraverser(object):
    implements(IMultiTraverserClient)
    adapts(IQuiz)
    priority = 10
    def __init__(self, context):
        self.context = context
    def publishTraverse(self, request, name, view):
        """See zope.publisher.interfaces.IPublishTraverse"""
        if name == self.context.title + u'.qml':
            qax = IQuizAsXML(removeSecurityProxy(self.context))
            return qax.generateXML()
        else:
            return view
    
class XMLHelp(QreaturePicturedView):
    pass  
    
