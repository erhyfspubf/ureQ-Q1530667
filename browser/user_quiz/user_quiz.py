# -*- coding: cp1251 -*-

from z3c.form.form import Form
from z3c.form import button
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class UserQuiz(Form):
    template = ViewPageTemplateFile('templates/user_quiz.pt')
    buttons = button.Buttons(button.Button
                             (name='proceed',title=u'Дальше'))

    def update(self):
        super(UserQuiz,self).update()
    
    @button.handler(buttons['proceed'])
    def handleProceed(self, action):
        """So. This action only fires if there are no lead in answer which question which
        contains in SinglePageQuiz object """
        
class IdleViewlet(object):
    def update(self):
        pass
    def render(self):
        return '_'
    
    