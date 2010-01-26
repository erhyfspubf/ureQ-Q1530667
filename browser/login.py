# -*- coding: cp1251 -*-
from z3c.form import field,button,form
from qreature.interfaces import IQreatureSite
from zope.interface import implements
from qreature.browser.interfaces import IQreatureLogin, ILoginEmail
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from qreature.browser.qreature_views import QreaturePrefixedButton
from qreature.interfaces import IQreatureCatalog, IQreatureIntIds
from zope.component import getMultiAdapter, getUtility, adapts
from zc.async import interfaces,job
from goog.gmail.gmailer import IGMailer
from zope.security.proxy import removeSecurityProxy
from zope.interface import Interface
class LoginEmail(object):
    implements(ILoginEmail)
    adapts(Interface)
    def __init__(self,site):
        self.login = u''
        self.choose = u''
        self.email = u''
    


    
class QreatureLogin(form.Form,QreaturePrefixedButton):
    implements(IQreatureLogin)
    template = ViewPageTemplateFile('templates/loginform.pt')
    fields = field.Fields(ILoginEmail)
    form_name=u'Напомнить пароль'
    button_name=u'отправить на email'
    buttons = button.Buttons(button.ImageButton
                             (name='apply',title=u'Apply',image=u'apply.jpg'))
    @button.handler(buttons['apply'])
    def handleApply(self, action):
        data, errors = self.extractData()
        
        if errors:
            self.status = u'Что-то не так набрали?'
            return
        
        if data['login'] is data['email'] is None:
            self.status = u'Нужно набрать что-нибудь. Логин или email'
            return
        
        success_status = u'Вам отправлено письмо с логином и паролем'
        site = removeSecurityProxy(self.context)
        if not IQreatureSite.providedBy(site):
            site = site.__parent__
        folder = data['login']
        email = data['email']
        if folder is not None:
            if site.has_key(folder):
                login = site[folder].login
                email = site[folder].email
                password = site[folder].password
                self.sendPassword(email, login, password)
                self.status = success_status
            else:
                self.status = u'Введенный вами логин не существует'
            return
        cat = getUtility(IQreatureCatalog, context = site)
        int_ids = getUtility(IQreatureIntIds, context = site)
        users = cat['users'].apply((None,None))
        users = [int_ids.getObject(user) for user in users]
        for user in users:
            if email == user.email:
                password = user.password
                login = user.login
                self.sendPassword(email, login, password)
                self.status = success_status
                return
        self.status = u'Пользователь с таким адресом не зарегистрирован'
                
            
        print '-------------sending email----------'
    
    def sendPassword(self,recepient, login, password):
        site = removeSecurityProxy(self.context)
        gmailer = getUtility(IGMailer, context = site)
        queue = interfaces.IQueue(site)
        msg = u'Ваш логин: ' + login + u' Пароль: ' + password
        queue.put(job.Job(gmailer.send_email,recepient,u'www.qreature.ru',msg))

    