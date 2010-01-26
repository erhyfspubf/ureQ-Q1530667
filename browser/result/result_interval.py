 # -*- coding: cp1251 -*-
from z3c.form import form, field, button, interfaces
from qreature.browser.result.interfaces import IResultInterval,IInterval
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.formlib.namedtemplate import NamedTemplateImplementation
from zope.formlib.namedtemplate import NamedTemplate
from zope.component import adapts
from qreature.interfaces import IQuizResult
from zope.interface import implements
from z3c.form.datamanager import AttributeField
from z3c.form.converter import NumberDataConverter, _
from zope.annotation.interfaces import IAnnotations
from zope.security.proxy import removeSecurityProxy
from qreature.browser.qreature_views import QreaturePrefixedButton
from zope.event import notify
from qreature.browser.events import CachedObjectChangedEvent
from pagable.interfaces import IPagableAction
from zope.app.component.hooks import getSite

class ResultInterval(object):
    """ This object represent the interval, extracted from result annotation,
    via adapter. It is adapter itself"""
    implements(IResultInterval)
    adapts(IQuizResult)

    def __init__(self, context):
        self.context = context    

INTERVAL_KEY = 'interval'

class ResultIntervalForm(QreaturePrefixedButton,form.EditForm):
    
    implements(IPagableAction)
    def __init__(self, context,request,view,manager):
        self.context = context
        self.request = request
        self.__parent__ = view
        self.manager = manager
    
    template = NamedTemplate('qreature.interval_form')
    fields = field.Fields(IResultInterval)
    buttons = button.Buttons(button.ImageButton
                             (name='interval',title=u'Interval',image=u'apply.jpg'))
    
    @button.handler(buttons['interval'])
    def handleInterval(self, action):
        super(ResultIntervalForm,self).handleApply(self,action)
        quiz = getSite()
        results = [r for r in quiz.values() if IQuizResult.providedBy(r)]
        notify(CachedObjectChangedEvent(results))
        
    def gimmeMin(self):
        quiz = getSite()
        results = [r for r in quiz.values() if IQuizResult.providedBy(r)]
        results.sort(key=lambda x: IAnnotations(removeSecurityProxy(x)).get(INTERVAL_KEY))
        index = results.index(self.context)
        if index <= 0: return 0
        previous_result = results[index-1]
        previous_interval = IAnnotations(removeSecurityProxy(previous_result)).get(INTERVAL_KEY)
        return previous_interval
        
        
    def gimmeMax(self):
        return self.widgets['interval'].value


class ResultIntervalDataManager(AttributeField):
    adapts(IQuizResult, IInterval)
    def get(self):
        interval = IAnnotations(removeSecurityProxy(self.context)).get(INTERVAL_KEY)
        return interval

    def set(self, value):
        ann = IAnnotations(removeSecurityProxy(self.context))
        ann[INTERVAL_KEY] = value

class IntervalDataConverter(NumberDataConverter):
    """A data converter for integers."""
    adapts(IInterval, interfaces.IWidget)
    type = int
    errorMessage = _('The entered value is not a valid integer literal')
    def toFieldValue(self, value):
        try:
            return int(value)
        except:
            super(IntervalDataConverter,self).toFieldValue(value) 

interval_template = NamedTemplateImplementation(
    ViewPageTemplateFile('templates/interval_form.pt'))