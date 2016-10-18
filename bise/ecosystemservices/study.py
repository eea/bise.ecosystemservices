from bise.ecosystemservices import MessageFactory as _
from plone.app.textfield import RichText
from plone.directives import dexterity
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable
from zope import schema
from zope.interface import implements


class IStudy(form.Schema, IImageScaleTraversable):
    """
    Studies
    """
    text = RichText(
        title=_(u'Description'),
        description=_(u'Description of the ecosystem service'),
        required=False,
        )
    thumbnail = schema.Text(
        title=_(u'Study thumbnail'),
        description=_(u'Study thumbnail'),
        required=True,
        )
    document = schema.Text(
        title=_(u'Study document'),
        description=_(u'Study document'),
        required=True,
        )


class Study(dexterity.Container):
    implements(IStudy)
