 # -*- coding: cp1251 -*-
from qreature.interfaces import IQuiz
from z3c.form import field
from qreature.quiz import Quiz
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.traversing.browser import absoluteURL
from zope.component import getUtility, getMultiAdapter
from qreature.browser.links import QreaturePictureLink
from qreature.browser.qreature_views import QreatureAddForm, QreatureEditForm

class QuizAddForm(QreatureAddForm):
    
    fields = field.Fields(IQuiz).omit('__parent__')
    form_name = u'Новый тест'
    button_name = u'Создать тест'
    def create(self, data):
        return Quiz(**data)

    
class QuizEditForm(QreatureEditForm):
    form_name = u'Редактирование теста'
    fields = field.Fields(IQuiz).omit('__parent__')
        

#-----Classes for representing Quiz in Quiz Folder -----#

class QuizShortcut(QreaturePictureLink):
    render = ViewPageTemplateFile('templates/quiz_shortcut.pt')
    @property
    def title(self):
        return self.context.title
    url='/constructor.html'
    image='qreature_icon'


class QuizDescription(object):
    pass


class QuizChecked(object):
    pass

class QuizPublished(object):
    pass


#-----Classes for representing Quiz in Quiz Folder -----#



class LeftSidebar(object):
    pass

class RightSideBar(object):
    pass