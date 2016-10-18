from Products.CMFCore.utils import getToolByName
from zope.site.hooks import getSite
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import alsoProvides


# TODO: make a generic factory, show site path in title


def sparql_vocabulary(context):

    try:
        catalog = getToolByName(context, 'portal_catalog')
    except AttributeError:
        catalog = getToolByName(getSite(), 'portal_catalog')

    brains = catalog(portal_type="Sparql")
    terms = [SimpleTerm(b.UID, b.UID, b.Title) for b in brains]

    return SimpleVocabulary(terms)

alsoProvides(sparql_vocabulary, IVocabularyFactory)


def elasticsearch_vocabulary(context):

    try:
        catalog = getToolByName(context, 'portal_catalog')
    except AttributeError:
        catalog = getToolByName(getSite(), 'portal_catalog')

    brains = catalog(portal_type="ElasticSearch")
    terms = [SimpleTerm(b.UID, b.UID, b.Title) for b in brains]

    return SimpleVocabulary(terms)

alsoProvides(elasticsearch_vocabulary, IVocabularyFactory)
