""" A content type to define an cache an ElasticSearch query
"""

from plone.directives import dexterity
from plone.directives import form
from plone import namedfile
from zope import schema
from zope.interface import implements
import json
import requests
import logging

logger = logging.getLogger('bise.ecosystemservices.elasticsearch')


class IElasticSearch(form.Schema):
    """ ElasticSearch precookedsearch content type
    """

    endpoint = schema.TextLine(title=u"ES Endpoint URL",
                               required=True)

    query = schema.Text(
        title=u'ElasticSearch Query in JSON format',
        required=True,
    )

    form.omitted('cached_results')
    cached_results = namedfile.field.NamedBlobFile(title=u"Cached results",
                                                   required=False)


class ElasticSearch(dexterity.Item):
    implements(IElasticSearch)

    def get_cached_results(self):
        import pdb; pdb.set_trace()

        return self.cached_results

    def precache_data(self):
        if not (self.endpoint and self.query):
            return

        logger.info("Updating results cache for %s", self.absolute_url())
        resp = requests.post(self.endpoint, json=json.loads(self.query))

        self.cached_results = namedfile.NamedBlobFile(resp.text,
                                                      filename=u"data.json")


def handle_es_change(obj, event):
    obj.precache_data()


# import DateTime
# from plone.app.async.interfaces import IAsyncService
# from zope.component import getUtility
#
# def async_update_cached_data(obj):
#     obj.precache_data()
# def es_added_or_modified(obj, evt):
#     async = getUtility(IAsyncService)
#
#     obj.scheduled_at = DateTime.DateTime()
#
#     async.queueJob(async_update_cached_data, obj)
