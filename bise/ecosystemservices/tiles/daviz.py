""" Tiles to embed daviz
"""

# from dateutile import parser
from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from collective.cover.tiles.data import PersistentCoverTileDataManager
from plone.app.textfield import RichText
from zope.component import adapter
from zope.interface import implements
from zope.schema import TextLine        # , Int
import logging
import lxml.etree
import requests

logger = logging.getLogger('bise.ecosystemservices.tiles.daviz')


class IDavizTile(IPersistentCoverTile):

    title = TextLine(title=u'Title', required=False,)
    daviz_url = TextLine(title=u'Daviz URL', required=True,)
    description = RichText(title=u'Description', required=False)
    published = TextLine(title=u'Published', required=False)


class DavizFullWidthTile(PersistentCoverTile):
    """ Daviz viewed in a big (fullwidth) tile
    """

    is_configurable = True
    is_editable = True
    is_droppable = False

    implements(IDavizTile)

    index = ViewPageTemplateFile('pt/daviz_fullwidth.pt')
    short_name = u'Daviz FullWidth'

    def is_empty(self):
        url = self.data.get('daviz_url', None)
        # title = self.data.get('daviz_url', None)
        # description = self.data.get('description', None)

        return not url


@adapter(IDavizTile)
class DavizTileDataManager(PersistentCoverTileDataManager):
    """ Data manager for daviz tiles, enables populating the
    from @@rdf based on url
    """

    # _provider = """Data provided by <a href=${url}>${title}</a>"""

    def _get_daviz_details(self, url):
        resp = requests.get(url)
        text = resp.text
        e = lxml.etree.fromstring(str(text))
        title = e.xpath(
            'davizvisualization:DavizVisualization/dcterms:title',
            namespaces=e.nsmap)[0].text
        issued = e.xpath(
            'davizvisualization:DavizVisualization/dcterms:issued',
            namespaces=e.nsmap)[0].text
        issued = self.context.toLocalizedTime(DateTime(issued))
        res = dict(title=title, published=issued)

        return res

    def set(self, data):
        url = data.get('daviz_url')
        if url:
            url = url + '/@@rdf'

        try:
            extracted = self._get_daviz_details(url)
            data.update(extracted)
        except Exception:
            logger.exception("Errors while trying to extract daviz data")

        super(DavizTileDataManager, self).set(data)
