 # -*- coding: cp1251 -*-
from qreature.interfaces import IQuizQuestion, IQuizAnswer
from qreature.quiz import QuizQuestion
from z3c.form import field, button
from qreature.browser.qreature_views import QreatureAddForm,QreatureEditForm,QreaturePicturedView
from zope.app.component.hooks import getSite
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.component import getMultiAdapter, getUtility
from zope.contentprovider.interfaces import IContentProvider
from qreature.browser.qreature_views import QreatureEditableView,QreatureContentTitle,QreatureView
from qreature.browser.quiz_constructor.interfaces import ITexturedQuestionsQuiz
from qreature.interfaces import IQreatureIntIds
from zope.interface import implements
from qreature.browser.question.interfaces import IAnswersForQuestion
from zc import resourcelibrary

class QuizQuestionAddForm(QreatureAddForm):
    fields = field.Fields(IQuizQuestion).omit('__parent__')
    form_name=u'Добавление вопроса'
    button_name = u'Создать вопрос'
    
    def create(self, data):
        return QuizQuestion(**data)



class QuizQuestionEditForm(QreatureEditForm):
    fields = field.Fields(IQuizQuestion).omit('__parent__')
    form_name=u'Редактирование вопроса'
    buttons = button.Buttons(button.ImageButton
                         (name='apply',title=u'Apply',image=u'apply.jpg'))
    @button.handler(buttons['apply'])
    def handleApply(self, action):
        super(QuizQuestionEditForm,self).handleApply(self,action)


class QuestionForConstructor(QreatureContentTitle):
    picture="question"
    css_class="question"
    
class QuestionIdForConstructor(object):
    def render(self):
        int_ids = getUtility(IQreatureIntIds)
        id = int_ids.getId(self.context)
        return u'<a name="' + unicode(id) + u'"></a>'
    
class QuestionBodyForConstructor(QreaturePicturedView):
    render = ViewPageTemplateFile('templates/question_body.pt')
    def __call__(self):
        self.update()
        return self.render()
    
    def gimmeId(self):
        return getUtility(IQreatureIntIds, context=self.context).getId(self.context)
    
    def update(self):
        quiz = getSite()
        if not ITexturedQuestionsQuiz.providedBy(quiz):
            def nothing():
                return ''
            self.render = nothing
        else:
            resourcelibrary.need('mochikit.Base')
            resourcelibrary.need('mochikit.DOM')
            resourcelibrary.need('mochikit.Async')
            resourcelibrary.need('mochikit.JsonRpc')
            resourcelibrary.need('mochikit.Style')
            resourcelibrary.need('mochikit.Color')
            resourcelibrary.need('mochikit.Position')
            resourcelibrary.need('mochikit.Visual')
            resourcelibrary.need('question')
    
class AnswersForQuestion(QreatureView,QreatureEditableView):
    render = ViewPageTemplateFile('templates/answers_for_question.pt')
    button_titles=False
    nothing = False
    implements(IAnswersForQuestion)
    def update(self):
        answers = [answer for answer in self.context.values() if  IQuizAnswer.providedBy(answer)]
        answers.sort(key=lambda x: x.title)
        viewlets = [getMultiAdapter((answer, self.request, self),IContentProvider, name=u'qreature.QreatureGeneralVM')\
                    for answer in answers]
        if len(viewlets) == 0:
            self.nothing = True
            return
        [viewlet.update() for viewlet in viewlets]
        self.viewlets = (viewlet for viewlet in viewlets)

        
class PreviewQuestion(object):
    def gimmeContent(self):
        return self.context.question