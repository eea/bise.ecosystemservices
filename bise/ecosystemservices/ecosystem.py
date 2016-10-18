from bise.ecosystemservices import MessageFactory as _
from plone.app.textfield import RichText
from plone.directives import dexterity
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable
from zope import schema
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import implements


class IEcosystem(form.Schema, IImageScaleTraversable):
    """
    Ecosystems
    """

    category = schema.Choice(
        title=_(u'Category'),
        description=_(u'Major ecosystem category (level 1)'),
        required=True,
        vocabulary=SimpleVocabulary([
            SimpleTerm(1, title=u"Terrestrial"),
            SimpleTerm(2, title=u"Fresh water"),
            SimpleTerm(3, title=u"Marine"),
        ])
    )
    scale = schema.Choice(
        title=_(u'Scale level'),
        description=_(u'Scale level'),
        required=True,
        vocabulary=SimpleVocabulary([
            SimpleTerm(1, title=u"Global"),
            SimpleTerm(2, title=u"European"),
            SimpleTerm(3, title=u"National"),
            SimpleTerm(4, title=u"Subnational"),
        ]),
        default=2
    )
    webmapid = schema.Text(
        title=_(u'Webmap ID'),
        description=_(u'Webmap id'),
        required=True,
    )
    text = RichText(
        title=_(u'Description'),
        description=_(u'Description of the ecoystem type'),
        required=False,
    )


class Ecosystem(dexterity.Container):
    implements(IEcosystem)
