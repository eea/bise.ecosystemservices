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

# from bise.ecosystemservices.tiles.base import AssignItemsMixin

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


class DavizListingTile(PersistentCoverTile):
    """ Folder listing tile
    """

    implements(IListingTile)

    index = ViewPageTemplateFile('pt/daviz_listing.pt')
    cell_tpl = ViewPageTemplateFile('pt/daviz_cell.pt')

    is_configurable = False
    is_editable = True
    is_droppable = True
    short_name = u'Daviz Listing'

    def render_cell(self, info):
        return self.cell_tpl(daviz=info)

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

    def is_empty(self):
        return not (self.data.get('uuid', None))

    def accepted_ct(self):
        """Return an empty list as no content types are accepted."""
        return ['Sparql']

    def populate_with_object(self, obj):
        super(DavizListingTile, self).populate_with_object(obj)

        if obj.portal_type not in self.accepted_ct():
            return

        data = {
            'title': safe_unicode(obj.Title()),
            'uuid': IUUID(obj),
        }
        data_mgr = ITileDataManager(self)
        data_mgr.set(data)
