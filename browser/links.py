# -*- coding: cp1251 -*-

from zope.traversing.browser import absoluteURL
from zope.app.component.hooks import getSite
from qreature.interfaces import IQreatureSite,IQuizAnswer,IQuiz,IQreatureComment
from zope.app.container.interfaces import IAdding
from qreature.browser.qreature_views import QreaturePictureLink
from zope.app.pagetemplate import ViewPageTemplateFile

class AddingQuiz(QreaturePictureLink):
    title=u'Новый тест'
    url='/+/AddQuiz.html'
    image='add'


class Preview(QreaturePictureLink):
    title=u'Просмотр'
    url='/preview.html'
    image='preview'
    


    
class Edit(QreaturePictureLink):
    title=u'Редактировать'
    url='/edit.html'
    image='edit'
    
    
class Back(QreaturePictureLink):
    title=u'Назад'
    image='back'
    #The base class take absolute url of context and add url attribute of this class
    @property
    def url(self):
        if IQuiz.providedBy(self.context):
            folder = self.context.__parent__
            self.context = folder
            context_page = '/main.html?'
        else:
            quiz = getSite()
            self.context = quiz
            context_page = '/constructor.html?'
        #so, the base class will use context, to get absoluteURL of it
        #now it need return something for Pagable
        
        url = None
        for v in self.request:
            if 'uri' in v.split('.'):
                url = self.request.get(v)
        if url is None: 
            url = self.request.get('HTTP_REFERER')
        if url is not None:
            url = url.split('?').pop()
            return context_page + url
        #ie case. looks like there are no HTTP_REFFERER in ie 6.0 :(
        else:
            return context_page[:-1]
            
        

    

class AddingResult(QreaturePictureLink):
    title=u'Результат'
    url='/+/AddQuizResult.html'
    image='add'
    
class AddingQuestion(QreaturePictureLink):
    title=u'Вопрос'
    url='/+/AddQuizQuestion.html'
    image='add'


class RSS(QreaturePictureLink):
    title=u'Прямая трансляция'
    url='/rss'
    image='rss'

class Refresh(QreaturePictureLink):
    title=u'Обновить'
    url='/constructor.html'
    image='apply'

class AddingAnswer(QreaturePictureLink):
    show_title = True
    title=u'Ответ'
    url='/+/AddQuizAnswer.html'
    image='add'
    
    @property
    def css_class(self):
        answers = []
        for a in self.context.values():
            if IQuizAnswer.providedBy(a):
                answers.append(a)
        if len(answers) !=0:
            return "QuizAnswers"
        else:
            return ""

        
class Link(object):
    title = u''
    url = u''
    
    def getURL(self):
        try:
            url = absoluteURL(self.context, self.request)
        except:
            url = 'deleted'
        return url
    
    def gimmeLink(self):
        return {'url':(self.getURL() + self.url), 'title':self.title}

class Main(Link):
    def gimmeLink(self):
        if IAdding.providedBy(self.context):
            self.context = self.context.context
        try:
            while not IQreatureSite.providedBy(self.context):
                self.context = self.context.__parent__
            return {'url':(self.getURL() + u'/main.html'),\
                 'title':u'Главная'}
        except:
            return {'url':u'http://www.qreature.ru',\
                 'title':u'Главная'}
            


class Qreatures(Link):
    title=u'Моя папка'
    url = '/MyQreatures.html'


class Register(Link):
    title=u'Регистрация'
    url = '/+/AddQreatureFolder.html'


class Login(Link):
    title=u'Вход'
    url='/edit.html'

class Logout(Link):
    title=u'Выход'
    url='/logout.html'


class Admin(Link):
    title=u'Администрирование'
    url = '/admin.html'                
                
class Thread(Link):
    title=u'Ветка'
    url='/thread.html'
    render = ViewPageTemplateFile('./templates/link.pt')
    def update(self):
        if not ICommentable.providedBy(self.context):
            while not ICommentable.providedBy(self.context):
                self.context = self.context.__parent__
        def nothing():
                return u''
        if not self.__parent__.rolled:
            self.render = nothing
        comments = [comment for comment in self.context.values() if IQreatureComment.providedBy(comment)]
        if len(comments) == 0:
            self.render = nothing

from commentable.interfaces import ICommentable
    
class AddingComment(Link):
    title=u'Комментировать'
    url="/+/AddQreatureComment.html"
    def update(self):
        if not ICommentable.providedBy(self.context):
            while not ICommentable.providedBy(self.context):
                self.context = self.context.__parent__

    
class LevelUp(Link):
    def update(self):
        if not self.__parent__.root:
            def nothing():
                return u''
            self.render = nothing 
    def gimmeLink(self):
        url = absoluteURL(self.context.__parent__,self.request) + u'/thread.html'
        return {'url':url,
                 'title':u'на уровень выше'}
