from zope.interface import Interface,Attribute
from zope.schema import Bool


class IRelationsForAnswer(Interface):
    pass
class ILeadForAnswer(Interface):
    something_happened_with_da_first = Bool(title = u'')
    first_widget = Bool(title=u'We have deal with the first widget')


class IInlineForm(Interface):
    pass

class IInlineAddForm(Interface):
    pass

class IInlineEditForm(Interface):
    pass

class IAnswerLeadWidget(Interface):
    terms_storage = Attribute(u'Terms Storage')
    your_holder = Attribute(u'Holder of this widgets viewlet')
    i_am_first_widget = Bool(title=u'Is it first widget or not')