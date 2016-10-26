""" Listing tiles
"""

from DateTime import DateTime
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from plone.app.textfield import RichText
from plone.app.uuid.utils import uuidToObject
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from zope.interface import implements
from zope.schema import TextLine, Int, Choice
import json
import logging

# from z3c.relationfield.schema import RelationChoice
# from plone.formwidget.contenttree import UUIDSourceBinder
# from plone.app.vocabularies.catalog import CatalogSource
# from plone.app.vocabularies.catalog import CatalogVocabulary

logger = logging.getLogger('eea.climateadapt')


class IListingTile(IPersistentCoverTile):

    title = TextLine(
        title=u'Title',
        required=False,
    )

    # uuid = RelationChoice(
    #     title=u"Linked Source",
    #     source=UUIDSourceBinder(portal_type="Sparql"),
    #     required=False,
    # )
    uuid = Choice(
        title=u"Linked Source",
        vocabulary="bise.sparql_vocabulary",
        required=False,
    )

    text = RichText(title=u'Text', required=False)

    view_more_url = TextLine(
        title=u'View More URL',
        required=False,
    )

    count = Int(
        title=u'Number of items to display',
        required=False,
        default=6,
    )


class DavizListingTile(PersistentCoverTile):
    """ Base class for Daviz listing tiles
    """

    is_configurable = False
    is_editable = True
    is_droppable = True

    implements(IListingTile)

    def render_cell(self, info):
        return self.cell_tpl(daviz=info)

    def accepted_ct(self):
        """Return an empty list as no content types are accepted."""
        return ['Sparql']

    def children(self):
        uuid = self.data.get('uuid')
        if not uuid:
            return []
        source = uuidToObject(self.data['uuid'])
        if not source:
            return []
        data = None
        try:
            data = source.getSparqlCacheResults()
        except Exception:
            logger.exception("Error in getting cached data "
                             "for sparql %s", source)
            return []
        count = self.data.get('count', 6)
        try:
            rows, cols = (data['result']['rows'][:count],
                          data['result']['var_names'][:count])
        except Exception:
            logger.exception("No results in sparql %s", source)

        return self._to_dict(rows, cols)

    def populate_with_object(self, obj):
        PersistentCoverTile.populate_with_object(self, obj)

        if obj.portal_type not in self.accepted_ct():
            return

        data = {
            'title': safe_unicode(obj.Title()),
            'uuid': IUUID(obj),
        }
        data_mgr = ITileDataManager(self)
        data_mgr.set(data)

    def is_empty(self):
        return not (self.data.get('uuid', None))

    def _to_dict(self, rows, cols):
        """ Packs a sparql result into a listing of dicts
        """
        res = []
        for row in rows:
            l = {}
            for i, c in enumerate(cols):
                l[c] = row[i]
            res.append(l)

        return res

    def format_date(self, ds):
        """ Convert a (possible) sparql literal to DateTime
        """
        if str(ds) == "None":
            return None
        try:
            return DateTime(str(ds))
        except Exception:
            logger.exception("Error while parsing date from sparql")
            return None


class DavizGridListingTile(DavizListingTile):
    """ Daviz-in-a-grid listing tile
    """

    index = ViewPageTemplateFile('pt/daviz_grid_listing.pt')
    cell_tpl = ViewPageTemplateFile('pt/daviz_cell.pt')

    short_name = u'Daviz Grid'


class DavizSingleRowListingTile(DavizListingTile):
    """ Daviz in a singele row listing tile
    """

    index = ViewPageTemplateFile('pt/daviz_singlerow_listing.pt')
    cell_tpl = ViewPageTemplateFile('pt/daviz_cell.pt')

    short_name = u'Daviz Row'


class IElasticSearchTile(IListingTile):
    """
    """

    # uuid = RelationChoice(
    #     title=u"Linked Source",
    #     source=UUIDSourceBinder(
    #         portal_type="ElasticSearch",
    #     ),
    #     required=False,
    # )
    uuid = Choice(
        title=u"Linked Source",
        vocabulary="bise.elasticsearch_vocabulary",
        required=False,
    )


class ElasticSearchBaseTile(PersistentCoverTile):
    """ ElasticSearch / Bise Catalogue Teaser tile
    """
    implements(IElasticSearchTile)

    def title(self):
        return self.data.get('title', 'Missing tile title')

    def children(self):
        uuid = self.data.get('uuid')
        if not uuid:
            return []
        source = uuidToObject(uuid)
        if not source:
            return []

        data = json.loads(source.cached_results.data)

        rows = [x['_source'] for x in data['hits']['hits']]

        return rows

    def accepted_ct(self):
        """Return an empty list as no content types are accepted."""
        return ['ElasticSearch']

    def populate_with_object(self, obj):
        PersistentCoverTile.populate_with_object(self, obj)

        if obj.portal_type not in self.accepted_ct():
            return

        data = {
            'title': safe_unicode(obj.Title()),
            'uuid': IUUID(obj),
        }
        data_mgr = ITileDataManager(self)
        data_mgr.set(data)

    def is_empty(self):
        return not (self.data.get('uuid', None))


class ElasticSearchTeaserTile(ElasticSearchBaseTile):
    """ ElasticSearch / Bise Catalogue Teaser tile
    """

    index = ViewPageTemplateFile('pt/es_teaser.pt')


class ElasticSearchListingTile(ElasticSearchBaseTile):
    """ ElasticSearch / Bise Catalogue Teaser tile
    """

    index = ViewPageTemplateFile('pt/es_listing.pt')

    def get_url(self, obj):
        # try different strategies to get the source url from the catalogue
        # info
        base = 'http://catalogue.biodiversity.europa.eu'
        strategies = [
            lambda o: o['source_url'],
            lambda o: base + obj['file_name']
        ]
        for l in strategies:
            try:
                return l(obj)
            except KeyError:
                continue

        return ""

    def get_title(self, obj):
        if 'title' in obj:
            return obj['title']
        if 'name' in obj:
            return obj['name']
