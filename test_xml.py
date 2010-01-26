# -*- coding: cp1251 -*-
import unittest
from qreature.xml import QuizAsXML
import os.path
from qreature.quiz import Quiz
from qreature import interfaces
from qreature.browser.result.interfaces import IResultInterval
from zope.component import adapts, provideAdapter, provideUtility, provideHandler, getUtility
from zope.annotation.interfaces import IAnnotations
from zope.annotation.attribute import AttributeAnnotations
from qreature.adapters import QuizContainerNameChooser
from zope.app.container.interfaces import INameChooser
from qreature.eventhandlers import setQuizUtilities,setQreatureSiteManager,addQreatureIntIdSubscriber
from zope.app.component.site import SiteManagerAdapter
from qreature.browser.result.result_interval import ResultInterval
from zope.app.testing import setup  
from zope.app.keyreference.persistent import KeyReferenceToPersistent
from zope.app.keyreference.interfaces import IKeyReference
from persistent.interfaces import IPersistent
from ZODB.interfaces import IConnection
from zope.app.keyreference.persistent import connectionOfPersistent
from zope.app.intid.tests import ConnectionStub
from zope.schema import vocabulary
from qreature.utilities import depends_voc, percentage, flatten, leads_voc
import zope.app.component.hooks as hooks
from qreature.skin.interfaces import IScaleLayer
from qreature.browser.result.result_interval import INTERVAL_KEY
from qreature.browser.quiz_constructor.actions import PAGES_KEY
from zope.interface import alsoProvides
from cgi import FieldStorage
from zope.publisher.browser import FileUpload
import codecs

class QuizAsXMLTestCase(unittest.TestCase):
    
    def setUp(self):
        self.root = setup.placefulSetUp(site=True)
        conn_stub = ConnectionStub()
        def register(arg):
            """i just do not know what is this method doing :("""
        conn_stub.register = register
        self.root._p_jar = conn_stub
        provideAdapter(connectionOfPersistent, adapts=[IPersistent], provides=IConnection, )
        provideAdapter(KeyReferenceToPersistent, adapts=[IPersistent], provides=IKeyReference) 
        provideHandler(setQreatureSiteManager)
        provideHandler(setQuizUtilities)
        provideHandler(addQreatureIntIdSubscriber)
        provideAdapter(SiteManagerAdapter)
        provideAdapter(ResultInterval)
        quiz = Quiz(u'init title',u'init body')
        self.root.__setitem__('quiz', quiz)
        #the site is quiz! not the root
        hooks.siteinfo.site = quiz
        provideAdapter(ResultInterval,adapts=[interfaces.IQuizResult], provides=IResultInterval)
        provideAdapter(QuizAsXML,adapts=[interfaces.IQuiz], provides=interfaces.IQuizAsXML)
        provideAdapter(AttributeAnnotations, adapts=[interfaces.IQuizContainer], provides=IAnnotations)
        provideAdapter(QuizContainerNameChooser, adapts=[interfaces.IQuizContainer], provides=INameChooser)
        vocabulary.setVocabularyRegistry(vocabulary.VocabularyRegistry())
        vr = vocabulary.getVocabularyRegistry()
        vr.register('Quiz Results',depends_voc)
        vr.register('Percentage', percentage)
        vr.register('Quiz Leads', leads_voc)
        provideUtility(flatten, interfaces.IQreatureUtility, "Flatten")
          
    def tearDown(self):
        setup.placefulTearDown()
        
    
    def testQuizAsXML(self):
        #test parsing
        quiz = self.root['quiz']
        path = os.path.join(os.getcwd(),'xml_example_word.qml')
        xml_example = open(path)
        field_storage = FieldStorage()
        field_storage.file = xml_example
        field_storage.filename = 'xml_example_word.qml'
        file_upload = FileUpload(field_storage)
        qax = interfaces.IQuizAsXML(self.root['quiz'])
        status = qax.generateQuiz(file_upload)
        #status = qax.generateQuiz(xml_example)
        if status is not None:
            print status
            return
        self.assertEqual(quiz.title,u'Название теста. Вот как.')
        self.assertEqual(quiz.body,u'Contents of quiz')
        
        self.assertEqual(IAnnotations(quiz).get(PAGES_KEY), 1)
        self.assertEqual(interfaces.IScaleQuiz.providedBy(quiz), True)
        self.assertEqual(interfaces.ISlotQuiz.providedBy(quiz), False)
        
        results = [r for r in quiz.values() if interfaces.IQuizResult.providedBy(r)]
        
        self.assertEqual(results[0].title,u'Title of first result')
        self.assertEqual(results[1].title,u'Title of second result')
        self.assertEqual(results[0].body, results[1].body,u'Contents of result')
        self.assertEqual(IAnnotations(results[0]).get(INTERVAL_KEY), 10)
        self.assertEqual(IAnnotations(results[1]).get(INTERVAL_KEY), 20)
        
        questions = [q for q in quiz.values() if interfaces.IQuizQuestion.providedBy(q)]
        self.assertEqual(questions[0].title,u'Title of first question')
        self.assertEqual(questions[1].title,u'Title of second question')
        
        for q in questions:
            answers = [a for a in q.values() if interfaces.IQuizAnswer.providedBy(a)]
            self.assertEqual(answers[0].title,u'Title of first answer')
            self.assertEqual(answers[1].title,u'Title of second answer')
            self.assertEqual(answers[0].body,answers[1].body,u'Contents of answer')
            depends = [[d for d in answer.values() if interfaces.IAnswerDepends.providedBy(d)]
                       for answer in answers]
            flatten = getUtility(interfaces.IQreatureUtility, name="Flatten")
            int_ids = getUtility(interfaces.IQreatureIntIds, context=quiz)
            depends = [d for d in flatten(depends)]
            leads = [[l for l in answer.values() if interfaces.IAnswerLeads.providedBy(l)]
                     for answer in answers]
            
            if q.title == u'Title of first question':
                leads = [l for l in flatten(leads)]
                self.assertEqual(len(leads),1)
            i=0
            for depend in depends:
                i+=1
                if divmod(i,2)[1] == 1:
                    self.assertEqual(int_ids.getObject(depend.result_id).title, u'Title of first result')
                elif divmod(i,2)[1] == 0:
                    self.assertEqual(int_ids.getObject(depend.result_id).title, u'Title of second result')
                self.assertEqual(depend.depend_value, 100)
            self.assertTrue(interfaces.IScaleQuiz.providedBy(quiz))
            self.assertTrue(interfaces.ILeadedQuiz.providedBy(quiz))
        xml_example.close()
        
        #test generation. to generate depends, provide the quiz with ISlotLayer also
        xml_example = open(path)
        example_lines = xml_example.readlines()
        #check for BOM also
        example_lines = [example_lines[0].lstrip(codecs.BOM_UTF8)] + example_lines[1:]
        alsoProvides(quiz, interfaces.ISlotQuiz)
        xml_generated = qax.generateXML()
        generated_lines = xml_generated.data.split('\n')
        lines_to_compare = zip(example_lines,generated_lines)
        for example_line,generated_line in lines_to_compare:
            self.assertEqual(example_line, generated_line+'\n')
        xml_example.close()        
#to do! last line must conform without \n        
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(QuizAsXMLTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')