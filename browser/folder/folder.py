# -*- coding: cp1251 -*-
from zope.traversing.browser import absoluteURL
from zope.component import getUtility,getMultiAdapter, adapts, getAdapters
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.contentprovider.interfaces import IContentProvider
from qreature.interfaces import IQreatureFolder
from z3c.form import field, interfaces,form,button
from qreature.folder import QreatureFolder as Folder
from zope.security.proxy import removeSecurityProxy
from qreature.interfaces import IQuiz
from qreature.browser.folder.interfaces import IQreatureFolderView
from zope.interface import implements
from qreature.browser.qreature_views import QreatureAddForm, QreatureEditableView,QreatureView,QreaturePicturedView
from pagable.interfaces import IPagableView
from zope.dublincore.interfaces import IZopeDublinCore

class QreatureFolderAddForm(QreatureAddForm):
    
    fields = field.Fields(IQreatureFolder).omit('__name__', '__parent__','url','about')
    form_name = u'Регистрация'
    button_name = u'Создать пользователя'
    
    def create(self, data):
        self.domen = data['login']
        return Folder(**data)


    def nextURL(self):
        site_url = absoluteURL(self.context.context, self.request)+ u'/' + unicode(self.domen) + u'/main.html'
        return site_url




class QreatureFolder(QreatureView,QreaturePicturedView):
    
    implements(IQreatureFolderView,IPagableView)
    items_on_page = 10
    request_range = 1
    reverse = True
    
    def sequence(self):
        quizes = [quiz for quiz in self.context.values() if  IQuiz.providedBy(quiz)]
        quizes.sort(key=lambda x: IZopeDublinCore(x).created)
        return quizes
    
    def filter(self,item):
        return True
    
    def __call__(self):
        self.update()
        return self.render()
    
    def update(self):
        """ """     
        fvm = getMultiAdapter((self.context, self.request, self),IContentProvider, name=u'qreature.QreatureFolderVM')
        fvm.update()
        self.viewlets = [fvm]
    
    
    def render(self):
        if self.context.__len__() == 0:
            return ViewPageTemplateFile("templates/help.pt").__call__(self)
        return ViewPageTemplateFile("templates/main.pt").__call__(self)



class QuizesForQreatureFolder(QreatureView,QreatureEditableView):
    
    render = ViewPageTemplateFile('templates/quizes_for_qreature_folder.pt')
    button_titles=False
    def update(self):
        quizes = self.__parent__.sequence()
#        quizes = (quiz for quiz in self.context.values() if IQuiz.providedBy(quiz))
        self.viewlets = []
        for quiz in quizes:
            vmq = getMultiAdapter((quiz, self.request, self),IContentProvider, name=u'qreature.QreatureFolderVM')
            vmq.update()
            self.viewlets.append(vmq)
                


        
class WidgetFactoryForQreatureFolderPassword(object):
    def __init__(self, folder):
        self.folder = removeSecurityProxy(folder)
    def gimmeWidget(self, field, request):
        widget = getMultiAdapter((field, request), interfaces.IFieldWidget)
        attr = str(widget.name.split(u'.').pop())
        def gimmeValue():
            new_value = widget.request.get(widget.name)
            if not new_value or new_value == interfaces.NOVALUE:
                new_value = self.folder.__getattribute__(attr)
            return new_value 
        widget.extract = gimmeValue
        widget.label = widget.label + u' (новый)'
        return widget

class QreatureFolderEditForm(form.EditForm):
    #template is overrided cause it is not View. It is VIEWLET!
    template = ViewPageTemplateFile('templates/qreature_folder_edit_form.pt')
    form_name = u'Личное'
    prefix = 'qreature_form.'
    button_name = u'Изменить'
    def __init__(self, context,request,view,manager):
        """ The form is implemented as Viewlet, so extra attribute in __init__ required"""
        self.context = context
        self.request = request
        self.__parent__= view
        self.manager = manager
    @property
    def fields(self):
        self.context.confirm_password = self.context.password
        fields = field.Fields(IQreatureFolder).omit('__parent__', 'login')
        fields['password'].widgetFactory = \
            fields['confirm_password'].widgetFactory = \
                WidgetFactoryForQreatureFolderPassword(self.context).gimmeWidget
        return fields
    buttons = button.Buttons(button.ImageButton
                             (name='apply',title=u'Apply',image=u'apply.jpg'))
    
    @button.handler(buttons['apply'])
    def handleApply(self, action):
        super(QreatureFolderEditForm,self).handleApply(self,action)

        
from qreature.browser.user_quiz.author import AuthorInfo as ResultAuthorInfo
from qreature.browser.user_quiz.interfaces import IPublished

class AuthorInfo(ResultAuthorInfo):
    rendered_template = None
    def __call__(self):
        self.update()
        return self.render()
    def update(self):
        self.folder = self.context
        self.quizes = [q for q in self.context.values() if IPublished.providedBy(q)]
        if len(self.quizes) != 0: self.other_quizes = True
        template = ViewPageTemplateFile('../user_quiz/templates/author_info.pt')
        self.rendered_template = template(self)
    render = ViewPageTemplateFile('./templates/author_info.pt')
    
    
class PictureHelp(QreaturePicturedView):
    pass
        