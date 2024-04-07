import elementtree.ElementTree as ET
from qreature.interfaces import IQuiz, IQuizAsXML, IQreatureIntIds, IQuizResult, IQuizQuestion,\
                                 IQuizAnswer, IAnswerDepends, ISlotQuiz, IScaleQuiz, IQuizContainer, ILeadedQuiz
from zope.interface import implements, alsoProvides, noLongerProvides
from zope.component import adapts, getUtility
from elementtree.SimpleXMLTreeBuilder import TreeBuilder
from qreature import quiz
from zope.annotation.interfaces import IAnnotations
from zope.security.proxy import removeSecurityProxy
from zope.app.container.interfaces import INameChooser
from qreature.browser.result.result_interval import INTERVAL_KEY
from xmllib import Error
from zope.app.container.contained import UserError
from qreature.browser.quiz_constructor.actions import PAGES_KEY
from zope.app.file import File
from zope.schema._field import ConstraintNotSatisfied
import re
import codecs

class XMLAttributeError(Exception):
    
    def __init__(self, tag, attr):
        self.tag = tag
        self.attr = attr
        
    def __str__(self):
        return u''.join((u'missing ',unicode(self.attr, 'utf-8'),u' attribute in <', unicode(self.tag, 'utf-8'), u'> tag'))


class XMLValueError(Exception):
    def __init__(self, el, attr, value):
        self.tag = el.tag.decode('UTF-8')
        self.attr = attr
        self.value = value

    def __str__(self):
        return u''.join((u'bad value:',self.value,u' for ',self.attr,u' in <',self.tag,u'> tag'))
        

class XMLContentError(Exception):
    def __init__(self, el):
        self.tag = el.tag.decode('UTF-8')
    def __str__(self):
        return u''.join((u'missing content for <', self.tag, u'> tag'))
        


class QuizAsXML(object):
    
    implements(IQuizAsXML)
    adapts(IQuiz)
    
    upload = u''
    download = u'http://qreature.ru/yourquiz.xml'
    
    
    def __init__(self, quiz):
        self.quiz = quiz

    
    def makeQuizContainer(self,el,parent,factory):
        
        title, err = self.getContent(el, 'title')
        if err: return None, err
        body, err = self.getContent(el, 'content')
        if err: return None, err
        chooser = INameChooser(parent)
        quiz_container = factory(title, body)
        try:
            name = chooser.chooseName(None, quiz_container)
            parent[name] = quiz_container
            #this one is for testing only! its better specify ObjectAddedEvent in test setUP !!!
            #notify(ObjectAddedEvent(quiz_container))
        except UserError, err:
            return None, err
        return quiz_container, None
        
        
    def getContent(self, el, tag):
        searched_tag = el.find(tag)
        if searched_tag is None:
            return None, XMLContentError(el)
        return searched_tag.text.decode('utf-8'), None

            
    
    def generateQuiz(self, file_upload):
        
        try:
#        so, nobody knows what the file i will get. I want clean unicode!
            
            file_content = file_upload.read()
            #the ET reads the file in "while 1" cycle. it is awaiting for EOF
            #this means without EOF, it will call thos method infinite amount of times
            #It need to prevent it to call it twice 
            self.allready_read = False
            def read_content(size=-1, ):
                if self.allready_read: return False
                encodings = ['utf-8','cp1251','cp866']    
                for e in encodings:
                    try:
                        u_content = file_content.decode(e)
                        if e == 'utf-8' and unicode(codecs.BOM_UTF8, "utf8") in u_content:
                            u_content = u_content.lstrip(unicode(codecs.BOM_UTF8, "utf8"))
                        break
                    except:
                        continue
                self.allready_read = True
                return u_content.encode('utf-8')
            
            file_upload.read = read_content
            
            tree = ET.parse(file_upload, parser=TreeBuilder())
            root = tree.getroot()
            
            quiz_title, err = self.getContent(root,'title')
            if err: raise err
            self.quiz.title = quiz_title
            
            quiz_body, err = self.getContent(root, 'content')
            if err: raise err
            self.quiz.body = quiz_body
            
            quiz_ann = IAnnotations(removeSecurityProxy(self.quiz))
            pages, err = self.getContent(root, 'questions_per_page')
            if pages is not None:
                try:
                    pages = int(pages)
                except ValueError:
                    raise XMLValueError(root,u'questions_per_page',pages)  
                quiz_ann[PAGES_KEY] = pages
            
            
            schema, err = self.getContent(root, 'schema')
            if schema == u'scale' or schema is None:
                alsoProvides(removeSecurityProxy(self.quiz), IScaleQuiz)
                noLongerProvides(removeSecurityProxy(self.quiz), ISlotQuiz)
                
            elif schema == u'slots':
                alsoProvides(removeSecurityProxy(self.quiz), ISlotQuiz)
                noLongerProvides(removeSecurityProxy(self.quiz), IScaleQuiz)
                
            #delete all from quiz :(
            def clean(container):
                names = []
                containers = []
                for k,v in container.items():
                    if IQuizContainer.providedBy(v):
                        names.append(k)
                        containers.append(v)
                for v in containers:
                    clean(v)
                for n in names:
                    container.__delitem__(n)
            
            clean(self.quiz)
            
            results_el = root.findall('result')
            int_ids = getUtility(IQreatureIntIds, context=self.quiz)
            
            for result_el in results_el:
                
                result, err = self.makeQuizContainer(result_el,self.quiz,quiz.QuizResult)
                if err: raise err
                
                res_ann = IAnnotations(removeSecurityProxy(result))
                border, err = self.getContent(result_el, 'border')
                if err: pass #possible slot quiz. no intervals
                if border is not None:
                    try:
                        border = int(border)
                    except ValueError:
                        raise XMLValueError(result_el,u'border',border)  
                    res_ann[INTERVAL_KEY] = border
            
            questions_el = root.findall('question')
            #leads are added after cycle, cause all questions must be created
            leads = {}
            for question_el in questions_el:
                question, err = self.makeQuizContainer(question_el,self.quiz,quiz.QuizQuestion)
                if err: raise err
                
                answers_el = question_el.findall('answer')
                for answer_el in answers_el:
                    answer, err = self.makeQuizContainer(answer_el,question,quiz.QuizAnswer)
                    if err: raise err
                    try:
                        value, err = self.getContent(answer_el, 'value')
                        if err: raise err
                        if (removeSecurityProxy(answer)).has_key('value'):
                            answer['value'].value = value
                        else:
                            answer['value'] = quiz.AnswerValue(value)
                        alsoProvides(removeSecurityProxy(self.quiz), ILeadedQuiz)
                    except XMLContentError:
                        #it will be zero valued quiz. see qreature.eventhandlers.addAnswerValue
                        noLongerProvides(removeSecurityProxy(self.quiz), ILeadedQuiz)
                        pass
                    
                    try:
                        lead, err = self.getContent(answer_el, 'lead')
                        if err: raise err
                        #leads are added after cycle, cause all questions must be created
                        leads.update({answer:lead})
                    except XMLContentError:
                        #so, no leads.
                        pass
                    
                    #find all depends. some depends may be omited (if it is Scale quiz).
                    depends_el = answer_el.findall('depend')
                    for depend_el in depends_el:
                        result_title, err= self.getContent(depend_el,'result_title')
                        if err: raise err
                        results = [r for r in self.quiz.values() if IQuizResult.providedBy(r) and r.title == result_title]
                        if len(results) == 0:
                            raise Error(u'Wrong result title in <depend>')
                        result_id = int_ids.queryId(results[0])
                        depend_value, err = self.getContent(depend_el,u'value')
                        if err: raise err
                        try:
                            depend_value=int(depend_value)
                        except ValueError:
                            raise XMLValueError(depend_el,u'value',depend_value) 
                        depend = quiz.AnswerDepends(result_id, depend_value)
                        depend_name = INameChooser(answer).chooseName(None, depend)
                        if (removeSecurityProxy(answer)).has_key(depend_name):
                            answer[depend_name].result_id = depend.result_id
                            answer[depend_name].depend_value = depend.depend_value
                        else:
                            answer[depend_name] = depend
           
            for answer, lead in leads.items():
                    questions = [q for q in self.quiz.values() if IQuizQuestion.providedBy(q) and q.title == lead]
                    if len(questions) == 0:
                        raise Error(u'Wrong question title in <lead>')
                    question_id = int_ids.queryId(questions[0])
                    if (removeSecurityProxy(answer)).has_key('lead'):
                        answer['lead'].question_id = question_id
                    else:
                        answer['lead'] = quiz.AnswerLeads(question_id)
                    

        except (Error, XMLAttributeError, XMLValueError, XMLContentError, UserError, ConstraintNotSatisfied), msg:
            return msg
        
    
    
    def generateXML(self):
        raw_xml = self.makeXML()
        indented_xml = self.indentXML(raw_xml)
        file = File(indented_xml,u'text/xml')
        return file
    
    def makeXML(self):
        def makeChildEl(parent_el,child_tag,content):
            parent_el.tail ="\n"
            if content is None: return
            parent_el.text = "\n"
            child_el = ET.Element(child_tag)
            child_el.text = content
            child_el.tail = "\n"
            parent_el.append(child_el)
        int_ids = getUtility(IQreatureIntIds, context=self.quiz)    
        root = ET.Element(u'quiz')
        makeChildEl(root,u'title',self.quiz.title)
        
        makeChildEl(root, u'content', self.quiz.body)
        
        if IScaleQuiz.providedBy(self.quiz):
            makeChildEl(root,u'schema',u'scale')
        elif ISlotQuiz.providedBy(self.quiz):
            makeChildEl(root,u'schema',u'slots')
            
        pages = IAnnotations(removeSecurityProxy(self.quiz)).get(PAGES_KEY)
        if pages is not None:
            makeChildEl(root,u'questions_per_page',str(pages))
        
        results = [r for r in self.quiz.values() if IQuizResult.providedBy(r)]
        for r in results:
            r_el = ET.Element(u'result')
            makeChildEl(r_el,u'title',r.title)
            makeChildEl(r_el,u'content',r.body)
            result_interval = IAnnotations(removeSecurityProxy(r)).get(INTERVAL_KEY)
            if result_interval is not None:
                makeChildEl(r_el,u'border',unicode(result_interval))
            root.append(r_el)
        
        questions = [q for q in self.quiz.values() if IQuizQuestion.providedBy(q)]
        for q in questions:
            q_el = ET.Element(u'question')
            makeChildEl(q_el,u'title',q.title)
            makeChildEl(q_el,u'content',q.body)
            answers = [a for a in q.values() if IQuizAnswer.providedBy(a)]
            for a in answers:
                a_el = ET.Element(u'answer')
                makeChildEl(a_el,u'title',a.title)
                makeChildEl(a_el,u'content',a.body)
                makeChildEl(a_el,u'value',unicode(a['value'].value))
                if (removeSecurityProxy(a)).has_key('lead'):
                    makeChildEl(a_el, u'lead', int_ids.getObject(int(a['lead'].question_id)).title)
                depends = [d for d in a.values() if IAnswerDepends.providedBy(d)]
                for d in depends:
                    d_el = ET.Element(u'depend')
                    makeChildEl(d_el,u'result_title',int_ids.getObject(int(d.result_id)).title)
                    makeChildEl(d_el,u'value',unicode(d.depend_value))
                    a_el.append(d_el)
                q_el.append(a_el)
            root.append(q_el)
        data = ET.tostring(root,'utf-8')
        return data
        
    def indentXML(self, raw_xml):
        data = raw_xml
        #indented_xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        indented_xml = ''
        CONTAINER_TAGS_INDENT = {'<quiz>':0,'</quiz>':0,
                          '<result>':1,'</result>':1,
                          '<question>':1,'</question>':1,
                          '<answer>':2,'</answer>':2,
                          '<depend>':3,'</depend>':3}
        lines = data.split('\n')
        indent = ''
        shifted_indent = False
        container = False
        for line in lines:
            for key, value in CONTAINER_TAGS_INDENT.items():
                if key in line:
                    indent = '\t'*value
                    shifted_indent = False
                    container = True
                    break
            if not container:
                if not shifted_indent:
                    indent += '\t'
                    shifted_indent = True
                else:
                    pass
            indented_xml += ''.join((indent,line,'\n'))
            container = False
            
        return indented_xml                 
