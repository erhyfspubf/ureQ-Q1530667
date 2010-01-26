from zope.app.pagetemplate import ViewPageTemplateFile
from zope.component import getMultiAdapter, getUtility, queryMultiAdapter
from qreature.interfaces import IQuizQuestion,IQuizResult,IQuizAnswer
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import implements
from qreature.browser.quiz_constructor.interfaces import IResultsForConstructor,IQuestionsForConstructor,IFirstTimeHelped
from qreature.browser.qreature_views import QreatureEditableView
from qreature.skin.interfaces import ISlotLayer,IScaleLayer
from qreature.browser.qreature_views import QreatureView,QreaturePicturedView
from zope.annotation.interfaces import IAnnotations
from qreature.browser.result.result_interval import INTERVAL_KEY
from zope.security.proxy import removeSecurityProxy
from pagable.interfaces import IPagableView
from qreature.browser.quiz_constructor.interfaces import IQuizConstructor    
from qreature.browser.quiz_constructor.actions import PAGES_KEY
from zc import resourcelibrary    
class QuizConstructor(QreatureView,QreaturePicturedView):
    
    implements(IQuizConstructor ,IFirstTimeHelped,IPagableView)
    
    def __call__(self):
        self.update()
        return self.render()
    
    def update(self):
        """ """     
        resourcelibrary.need('mochikit.Base')
        resourcelibrary.need('mochikit.DOM')
        resourcelibrary.need('mochikit.Async')
        resourcelibrary.need('mochikit.JsonRpc')
        resourcelibrary.need('mochikit.Style')
        resourcelibrary.need('mochikit.Color')
        resourcelibrary.need('mochikit.Position')
        resourcelibrary.need('mochikit.Visual')
        resourcelibrary.need('quiz_constructor')
        resourcelibrary.need('answer')
        cvm = getMultiAdapter((self.context, self.request, self),IContentProvider, name=u'qreature.QreatureGeneralVM')
        cvm.update()
        self.viewlets = cvm
    
    
    def render(self):
        if self.context.__len__() == 0:
            return ViewPageTemplateFile("templates/help.pt").__call__(self)
        
        return ViewPageTemplateFile("templates/constructor.pt").__call__(self)
    
    def help(self):
        return False
    
    @property
    def items_on_page(self):
        pages = IAnnotations(removeSecurityProxy(self.context)).get(PAGES_KEY)
        if pages is not None: return pages
        return 10
        
    request_range = 1
    reverse = False
    
    def sequence(self):
        questions = [question for question in self.context.values() if  IQuizQuestion.providedBy(question)]
        questions.sort(key=lambda x: x.title)
        return questions
    
    def filter(self,item):
        return True
            
            
 
#Help Screen            

class Help(QreaturePicturedView):
    
    implements(IFirstTimeHelped)
    
    render = ViewPageTemplateFile("templates/help.pt")
    def __call__(self):
        self.update()
        return self.render()
    def update(self):
        pass
    def help(self):
        return True

#Viewlets for LeftSideBar    

class PictureHelp(QreaturePicturedView):
    pass

class SlotsHelp(QreaturePicturedView):
    pass

class ScaleHelp(QreaturePicturedView):
    pass
         




COLUMNS = 3

class ResultsForConstructor(QreatureView,QreatureEditableView):
    
    implements(IResultsForConstructor)
    
    render = ViewPageTemplateFile('templates/results_for_constructor.pt')
    button_titles=False
    nothing = False
    rows=0
    
    def update(self):
        results = [result for result in self.context.values() if IQuizResult.providedBy(result)]
        if len(results) == 0: self.nothing = True
        rows,rest = divmod(len(results),COLUMNS)
        if rest !=0: rows +=1
        self.rows = xrange(rows)
        if IScaleLayer.providedBy(self.request):
            results.sort(key=lambda x: IAnnotations(removeSecurityProxy(x)).get(INTERVAL_KEY))
        elif ISlotLayer.providedBy(self.request):
            results.sort(key=lambda x: x.title)
        
        viewlets = []    
        for result in results:
            vm = getMultiAdapter((result, self.request, self),\
                                IContentProvider, name=u'qreature.QreatureGeneralVM')
            vm.update()
            viewlets.append(vm)
            
        self.viewlets = (viewlet for viewlet in viewlets)
        
    def gimmeViewlets(self):
        for i in xrange(COLUMNS):
            viewlet = self.viewlets.next()
            yield viewlet

        
class QuestionsForConstructor(QreatureView,QreatureEditableView):
    
    implements(IQuestionsForConstructor)
    render = ViewPageTemplateFile('templates/questions_for_constructor.pt')
    button_titles=False
    nothing = False
    question_was_removed = False
    terms = None
    def update(self):
        questions = self.__parent__.sequence()
        viewlets = [getMultiAdapter((question, self.request, self),IContentProvider, name=u'qreature.QreatureGeneralVM')\
                    for question in questions]
        if len(viewlets) == 0:
            self.nothing = True
            return
        [viewlet.update() for viewlet in viewlets]
        
        #handle case where first lead viewlet need to be cleaned
        if self.question_was_removed:
            self.terms = None
            for v in viewlets:
                q = v.context
                answers = [q for a in q.values() if IQuizAnswer.providedBy(a)]
                if len(answers) >0:
                    v.update()
                    break
        self.viewlets = (viewlet for viewlet in viewlets)