""" Listing tiles
"""

from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from plone.app.uuid.utils import uuidToObject
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from zope.interface import implements
from zope.schema import TextLine
import logging
import json
from DateTime import DateTime


logger = logging.getLogger('eea.climateadapt')


class IListingTile(IPersistentCoverTile):

    title = TextLine(
        title=u'Title',
        required=False,
    )

    uuid = TextLine(
        title=u'UUID',
        required=False,
        readonly=True,
    )

    view_more_url = TextLine(
        title=u'View More URL',
        required=False,
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

    def children(self):
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
        try:
            rows, cols = data['result']['rows'], data['result']['var_names']
        except Exception:
            logger.exception("No results in sparql %s", source)

        return self._to_dict(rows, cols)

    def accepted_ct(self):
        """Return an empty list as no content types are accepted."""
        return ['Sparql']

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

    short_name = u'Daviz Grid Listing Tile'


class DavizSingleRowListingTile(DavizListingTile):
    """ Daviz in a singele row listing tile
    """

    index = ViewPageTemplateFile('pt/daviz_singlerow_listing.pt')
    cell_tpl = ViewPageTemplateFile('pt/daviz_cell.pt')

    short_name = u'Daviz Grid Listing Tile'


class IElasticSearchTile(IListingTile):
    """
    """


class ElasticSearchBaseTile(PersistentCoverTile):
    """ ElasticSearch / Bise Catalogue Teaser tile
    """
    implements(IElasticSearchTile)

    def title(self):
        return self.data.get('title', 'Missing tile title')

    def children(self):
        source = uuidToObject(self.data['uuid'])
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
