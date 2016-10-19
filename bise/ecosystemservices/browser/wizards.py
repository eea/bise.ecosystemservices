from bise.ecosystemservices.browser.utils import make_group
from bise.ecosystemservices.browser.utils import make_layout
from bise.ecosystemservices.browser.utils import make_row
from bise.ecosystemservices.browser.utils import make_tile
from plone.api.content import create
from plone.app.content.browser.folderfactories import FolderFactoriesView
from plone.app.textfield import RichText
from plone.directives import form
from plone.uuid.interfaces import IUUID
from z3c.form import button
from zope.schema import Text
from zope.schema import TextLine
import json


class ITopicWizardSchema(form.Schema):
    """
    """

    title = TextLine(title=u"Title", required=True)
    description = RichText(title=u"Topic description", required=True)

    sparql_endpoint = TextLine(
        title=u"Sparql query endpoint",
        required=False,
        default=u"http://semantic.eea.europa.eu/sparql")
    sparql_query = Text(
        title=u"Sparql query",
        required=False)

    elasticsearch_query_endpoint = Text(
        title=u"ElasticSearch query endpoint",
        default=(u"http://localhost:9200/"
                 u"catalogue_development_articles/_search"),
        required=False)
    elasticsearch_query = Text(
        title=u"ElasticSearch query",
        default=(u'{"from" : 0, "size" : 100, '
                 u'"query":{"match": {"_all":"test"}}}'),
        required=False)


class BaseCreateTopic(form.SchemaForm):
    """
    """

    schema = ITopicWizardSchema
    ignoreContext = True

    label = u"Advanced Topic wizard"

    def create(self, data):
        raise NotImplementedError

    @button.buttonAndHandler(u'Ok')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        obj = self.create(data)

        return self.request.response.redirect(obj.absolute_url())

    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        """ handle cancel
        """


class CreateMainTopic(BaseCreateTopic):
    """ Easily create an advanced topic

    - create a folder based on title
    - set the description
    - set the sparql query
    - set the elasticsearch query

    - TODO: change suptopics tile to allow creating subtopics
    """

    def create(self, data):
        folder = create(
            container=self.context, type="Folder", title=data['title'])
        cover = create(container=folder,
                       type="collective.cover.content",
                       title=data['title'])

        folder.setDefaultPage(cover.getId())

        text = u"<h1>{0}</h1>".format(data['title']) + data['description'].raw
        info = {'title': u'Main Text', 'text': text}
        desc_tile = make_tile("collective.cover.richtext", cover, info)

        info = {'title': u'Subtopics', 'uuid': IUUID(folder)}
        fc_tile = make_tile("bise.folder_contents_listing", cover, info)

        row_1 = make_row(make_group(12, desc_tile))
        row_2 = make_row(make_group(12, fc_tile))

        rows = [row_1, row_2]

        if data.get('sparql_query'):
            endpoint = data['sparql_endpoint']
            sparql = create(container=folder,
                            type="Sparql",
                            title=data['title'] + u' Sparql Query',
                            endpoint_url=endpoint,
                            sparql_query=data['sparql_query']
                            )

            info = {'title': 'Daviz full width', 'uuid': IUUID(sparql)}
            dfw_tile = make_tile("bise.daviz_grid_listing", cover, info)
            row_3 = make_row(make_group(12, dfw_tile))
            rows.append(row_3)

        if data.get('elasticsearch_query'):
            endpoint = "http://10.0.30.44:9200/_search"
            query = data['elasticsearch_query']
            es = create(container=folder,
                        type='ElasticSearch',
                        title=data['title'] + u" ElasticSearch Query",
                        endpoint=endpoint,
                        query=query
                        )
            info = {'title': 'Further Links', 'uuid': IUUID(es)}
            es_list_tile = make_tile("bise.es_listing", cover, info)
            g1 = make_group(9, es_list_tile)

            info = {'title': 'Teaser Tile', 'uuid': IUUID(es)}
            es_teaser_tile = make_tile("bise.es_teaser", cover, info)
            g2 = make_group(3, es_teaser_tile)

            row_4 = make_row(g1, g2)
            rows.append(row_4)

        layout = make_layout(*rows)
        layout = json.dumps(layout)

        cover.cover_layout = layout

        return cover


class CreateSubTopic(BaseCreateTopic):
    """
    """

    def create(self, data):
        folder = create(
            container=self.context, type="Folder", title=data['title'])
        cover = create(container=folder,
                       type="collective.cover.content",
                       title=data['title'])

        folder.setDefaultPage(cover.getId())

        return cover


class OverrideFolderFactoriesView(FolderFactoriesView):
    """ Override the default folder factories, to add a fake add entry
    """

    def addable_types(self, include=None):
        res = super(OverrideFolderFactoriesView, self).addable_types(include)

        additional = [
            {
                'id': 'MainTopic',
                'title': u'Main Topic (advanced wizard)',
                'description': u'A wizard for main topics',
                'action': '@@create-maintopic',
                'selected': False,
                'icon': 'folder_icon.png',
                'extra': {
                    'id': 'maintopic',
                    'separator': None,
                    'class': 'contenttype-maintopic'
                },
                'submenu': None,
            },
            {
                'id': 'SubTopic',
                'title': u'Subtopic (advanced wizard)',
                'description': u'A wizard for subtopics',
                'action': '@@create-subtopic',
                'selected': False,
                'icon': 'folder_icon.png',
                'extra': {
                    'id': 'maintopic',
                    'separator': None,
                    'class': 'contenttype-subtopic'
                },
                'submenu': None,
            },
        ]

        res.extend(additional)
        return res
