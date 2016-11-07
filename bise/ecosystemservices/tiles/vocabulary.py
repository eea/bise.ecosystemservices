from Products.CMFCore.utils import getToolByName
from plone.memoize import ram
from time import time
from zope.interface import alsoProvides, implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.site.hooks import getSite
import json
import requests


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


def _cache_key(fun, *args):
    return (fun.__name__, time() // (20 * 60),)


# @ram.cache(_cache_key)
def get_tags():
    url = 'http://catalogue.biodiversity.europa.eu/api/v1/shared_tags'
    data = requests.get(url)
    if data.status_code != 200:
        return []
    items = json.loads(data.content)
    tags = set()
    for tagitem in items:
        kcontainer = tagitem.get('keyword_container')
        for item in kcontainer.get('keywords'):
            value = item.get('keyword').get('name')
            if value:       # and (':' not in value):
                tags.add(value)
    return sorted(tags)


class CatalogueTagVocabularyMainBranch(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        tags = get_tags()
        terms = [SimpleTerm(tag, tag, tag) for tag in tags if ':' not in tag]
        return SimpleVocabulary(terms)
