from Products.CMFCore.utils import getToolByName
from plone.memoize import ram
from time import time
from zope.interface import alsoProvides, implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.site.hooks import getSite
import json
import requests


def datasource_vocabulary_factory(ptype):
    def factory(context):
        try:
            catalog = getToolByName(context, 'portal_catalog')
        except AttributeError:
            catalog = getToolByName(getSite(), 'portal_catalog')

        brains = catalog(portal_type=ptype)
        terms = [SimpleTerm(b.UID, b.UID, b.Title) for b in brains]

        return SimpleVocabulary(terms)

    return factory


sparql_vocabulary = datasource_vocabulary_factory("Sparql")
alsoProvides(sparql_vocabulary, IVocabularyFactory)

elasticsearch_vocabulary = datasource_vocabulary_factory('ElasticSearch')
alsoProvides(elasticsearch_vocabulary, IVocabularyFactory)

datasource_vocabulary = datasource_vocabulary_factory(['Sparql',
                                                       'ElasticSearch'])
alsoProvides(datasource_vocabulary, IVocabularyFactory)


def _cache_key(fun, *args):
    return (fun.__name__, time() // (20 * 60),)


@ram.cache(_cache_key)
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
        tm = {}
        for t in tags:
            if ':' in t:
                mt, st = t.split(':', 1)
                tm[mt] = tm.get(mt, []) + [st]
            else:
                tm[t] = []

        terms = []
        for t in sorted(tm):
            if tm[t]:
                title = u"{0} ({1} subtopics)".format(t, len(tm[t]))
                term = SimpleTerm(value=t, token=t, title=title)
                terms.append(term)
            else:
                term = SimpleTerm(value=t, token=t, title=t)
                terms.append(term)

        return SimpleVocabulary(terms)
