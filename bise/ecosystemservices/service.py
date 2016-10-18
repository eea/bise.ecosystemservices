from bise.ecosystemservices import MessageFactory as _
from plone.app.textfield import RichText
from plone.directives import dexterity
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable
from zope import schema
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class IService(form.Schema, IImageScaleTraversable):
    """
    Services
    """
    section = schema.Choice(
        title=_(u'Section'),
        description=_(u'Section'),
        required=True,
        vocabulary=SimpleVocabulary([
            SimpleTerm(1, title=u"Provisioning"),
            SimpleTerm(2, title=u"Regulation and maintenance"),
            SimpleTerm(3, title=u"Cultural"),
        ])
    )
    division = schema.Choice(
        title=_(u'Division'),
        description=_(u'Division'),
        required=True,
        vocabulary=SimpleVocabulary([
            SimpleTerm(1, title=u"Nutrition"),
            SimpleTerm(2, title=u"Materials"),
            SimpleTerm(3, title=u"Energy"),
            SimpleTerm(
                4, title=u"Mediation of waste, toxics and other nuisances"),
            SimpleTerm(5, title=u"Mediation of flows"),
            SimpleTerm(6, title=u"Maintenance of physical, "
                       u"chemical, biological conditions"),
            SimpleTerm(7, title=u"Physical and experiential interactions"),
            SimpleTerm(8, title=u"Spiritual, symbolic and other interactions"),
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
        description=_(u'Description of the ecosystem service'),
        required=False,
    )


class Service(dexterity.Container):
    """ Custom content-type class; objects created for this content type will
    be instances of this class. Use this class to add content-type specific
    methods and properties. Put methods that are mainly useful for rendering in
    separate view classes.
    """
    implements(IService)
