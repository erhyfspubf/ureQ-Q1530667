# -*- coding: cp1251 -*-
from zope.interface import implements, Interface
from zope.component import adapts, getUtility, getMultiAdapter
from graph.interfaces import IGraphNode, IPossibleGraph
from qreature import interfaces
from qreature.browser.actions import FIRST_QUESTION_KEY,GRAF_KEY
from zope.annotation.interfaces import IAnnotations
from zope.security.proxy import removeSecurityProxy
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

class QuestionToNode(object):
    title = u''
    implements(IGraphNode)
    adapts(interfaces.IQuizQuestion)
    def __init__(self, context):
        self.context = context
        self.title = unicode(context.title)
        self.int_ids = getUtility(interfaces.IQreatureIntIds, context = self.context)
    def nextNodes(self):
        answers = [a for a in self.context.values()\
                   if interfaces.IQuizAnswer.providedBy(a)]
        leads = [a.get('lead') for a in answers if a.has_key('lead')]
        next_questions = [self.int_ids.getObject(l.question_id) for l in leads]
        if len(next_questions) == 0: return [None]
        next_questions.sort(key = lambda x: x.title)
        return [IGraphNode(q) for q in next_questions]
    @property
    def nodeId(self):
        return self.int_ids.getId(self.context)
    
class QuizToGraph(object):
    title = u''
    implements(IPossibleGraph)
    adapts(interfaces.IQuiz)
    def __init__(self, context):
        self.context = context
        self.title = context.title
    def gimmeFirstNode(self):
        quiz = removeSecurityProxy(self.context)
        ann = IAnnotations(quiz)
        graph = ann.get(GRAF_KEY)
        #handle not checked quiz. just take the first question with the lead
        if graph is None:
            questions = [q for q in quiz.values() if interfaces.IQuizQuestion.providedBy(q)]
            for q in questions:
                answers = [a for a in q.values() if interfaces.IQuizAnswer.providedBy(a)]
                leads = [a['lead'] for a in  answers if a.has_key('lead')]
                if len(leads)>0: return IGraphNode(q)
        for i in graph.items():
                if i[1] == FIRST_QUESTION_KEY:
                    first_question_id = i[0]
        int_ids = getUtility(interfaces.IQreatureIntIds, context = self.context)
        first_question = int_ids.getObject(first_question_id)
        return IGraphNode(first_question)
    
class Graph(object):

    render = ViewPageTemplateFile('./templates/quiz_graph.pt')
    
    def gimmeGraph(self):
        return self.graph()
        
    def __call__(self):
        self.update()
        return self.render()
    def update(self):
        to_graph = IPossibleGraph(self.context)
        self.graph = getMultiAdapter((to_graph, self.request), Interface, 'graph.html')
        
        
        
