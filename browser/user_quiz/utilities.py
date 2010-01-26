from zope.app.component.hooks import getSite
from zope.component import getUtility
from qreature.interfaces import IQuizQuestion#,IQuizAnswer
#from zope.app.intid.interfaces import IIntIds
from qreature.interfaces import IQreatureIntIds

def extract_previous_answers(request):
    previous_answers = []
    for key,value in request.items():
        l = key.split('.')
        if ('form' in l) and ('widgets' in l) and ('previous_answers' in l):
            previous_answers = value
    previous_answers = [answer for answer in previous_answers]
    return previous_answers

def extract_answers(request):
    quiz = getSite()
    questions = [q for q in quiz.values() if IQuizQuestion.providedBy(q)]
    int_ids = getUtility(IQreatureIntIds, context=quiz)
    questions = [int_ids.getId(q) for q in questions]
    answers = []
    for q in questions:
        answer = 'form.widgets.' + str(q) + '.answer'
        answer = request.get(answer, None)
        answer and answers.append((answer.pop()))
    return answers