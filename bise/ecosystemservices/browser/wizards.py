from bise.ecosystemservices.browser.utils import make_group
from bise.ecosystemservices.browser.utils import make_layout
from bise.ecosystemservices.browser.utils import make_row
from bise.ecosystemservices.browser.utils import make_tile
from eea.sparql.content.sparql import generateUniqueId
from plone.api.content import create
from plone.app.content.browser.folderfactories import FolderFactoriesView
from plone.app.textfield import RichText
from plone.directives import form
from plone.uuid.interfaces import IUUID
from z3c.form import button
from zope.schema import List
from zope.schema import Text
from zope.schema import TextLine
import json


class IAdvancedTopicWizardSchema(form.Schema):
    """
    """

    title = TextLine(title=u"Title", required=True)
    description = RichText(title=u"Topic description", required=True)

    subtopics = List(
        title=u"Subtopics",
        description=u"One per line",
        value_type=TextLine(title=u"Subtopic title"),
        required=False,
    )

    sparql_endpoint = TextLine(
        title=u"Sparql query endpoint",
        required=False,
        default=u"http://semantic.eea.europa.eu/sparql"
    )
    graphs_sparql_query = Text(
        title=u"Graph and Trends sparql query",
        required=False
    )
    indicators_sparql_query = Text(
        title=u"Relevant Indicators sparql query",
        required=False
    )

    elasticsearch_query_endpoint = TextLine(
        title=u"ElasticSearch query endpoint",
        default=(u"http://localhost:9200/"
                 u"catalogue_development_articles/_search"),
        required=False
    )
    elasticsearch_query = Text(
        title=u"Further Links - ElasticSearch query",
        default=(u'{"from" : 0, "size" : 100, '
                 u'"query":{"match": {"_all":"test"}}}'),
        required=False
    )
    catalogue_teaser = TextLine(
        title=u"Catalogue Teaser Subject",
        required=False
    )
    catalogue_teaser_link = TextLine(
        title=u"Catalogue Teaser link",
        required=False
    )


class BaseCreateTopic(form.SchemaForm):
    """
    """

    ignoreContext = True

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


def create_sparql(container, title, query, endpoint):
    """ Create a sparql query object
    """
    _id = generateUniqueId("Sparql")
    _id = container.invokeFactory(type_name="Sparql", id=_id)
    ob = container[_id]
    ob.edit(
        title=title,
        endpoint_url=endpoint,
        sparql_query=query,
    )
    ob._renameAfterCreation(check_auto_id=True)
    ob.invalidateWorkingResult()

    return ob


class CreateMainTopic(BaseCreateTopic):
    """ Easily create an advanced topic

    - create a folder based on title
    - set the description
    - set the sparql query
    - set the elasticsearch query

    - TODO: change suptopics tile to allow creating subtopics
    """

    schema = IAdvancedTopicWizardSchema
    label = u"Advanced Topic wizard"

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

        # TODO: create a folder for each subtopic

        row_1 = make_row(make_group(12, desc_tile))
        row_2 = make_row(make_group(12, fc_tile))

        rows = [row_1, row_2]

        endpoint = data.get('sparql_endpoint', '').strip()
        gsq = data.get('graphs_sparql_query', '').strip()
        isq = data.get('indicators_sparql_query', '').strip()

        if endpoint and gsq:
            sparql = create_sparql(
                container=folder,
                title=data['title'] + u'Graphs and Trends Sparql Query',
                query=gsq,
                endpoint=endpoint,
            )
            info = {'title': u'Graphs and Trends', 'uuid': IUUID(sparql)}
            dfw_tile = make_tile("bise.daviz_grid_listing", cover, info)
            row_3 = make_row(make_group(12, dfw_tile))
            rows.append(row_3)

        if endpoint and isq:
            sparql = create_sparql(
                container=folder,
                title=data['title'] + u'Related Indicators Sparql Query',
                query=isq,
                endpoint=endpoint,
            )
            info = {'title': u'Related Indicators', 'uuid': IUUID(sparql)}
            dsr_tile = make_tile("bise.daviz_singlerow_listing", cover, info)
            row_4 = make_row(make_group(12, dsr_tile))
            rows.append(row_4)

        es_query = data.get('elasticsearch_query', '').strip()
        es_endpoint = data.get('elasticsearch_query_endpoint', '').strip()
        teaser_subj = data.get('catalogue_teaser', '').strip()
        teaser_link = data.get('catalogue_teaser_link', '').strip()

        if es_query and es_endpoint:
            groups = []
            es = create(container=folder,
                        type='ElasticSearch',
                        title=data['title'] + u"Further Links ES Query",
                        endpoint=es_endpoint,
                        query=es_query
                        )
            info = {'title': 'Further Links', 'uuid': IUUID(es)}
            es_list_tile = make_tile("bise.es_listing", cover, info)
            groups.append(make_group(9, es_list_tile))

            if teaser_subj and teaser_link:
                info = {'title': 'Teaser Tile', 'uuid': IUUID(es)}
                es_teaser_tile = make_tile("bise.es_teaser", cover, info)
                groups.append(make_group(3, es_teaser_tile))

            row_5 = make_row(*groups)
            rows.append(row_5)

        layout = make_layout(*rows)
        layout = json.dumps(layout)

        cover.cover_layout = layout

        return cover


class ISubTopicWizardSchema(form.Schema):
    """
    """

    title = TextLine(title=u"Title", required=True)
    introduction = RichText(title=u"Topic introduction", required=True)
    highlight = RichText(
        title=u"Subtopic details",
        description=u"This text will be highlighted in green left border",
        required=True
    )

    daviz_url = TextLine(
        title=u"Graphs and trends Daviz link",
        required=False
    )

    sparql_endpoint = TextLine(
        title=u"Sparql query endpoint",
        required=False,
        default=u"http://semantic.eea.europa.eu/sparql"
    )
    indicators_sparql_query = Text(
        title=u"Relevant Indicators sparql query",
        required=False
    )

    elasticsearch_query_endpoint = TextLine(
        title=u"ElasticSearch query endpoint",
        default=(u"http://localhost:9200/"
                 u"catalogue_development_articles/_search"),
        required=False
    )
    elasticsearch_query = Text(
        title=u"Further Links - ElasticSearch query",
        default=(u'{"from" : 0, "size" : 100, '
                 u'"query":{"match": {"_all":"test"}}}'),
        required=False
    )
    catalogue_teaser = TextLine(
        title=u"Catalogue Teaser Subject",
        required=False
    )
    catalogue_teaser_link = TextLine(
        title=u"Catalogue Teaser link",
        required=False
    )


class CreateSubTopic(BaseCreateTopic):
    """
    """

    schema = ISubTopicWizardSchema
    label = u"SubTopic wizard"

    def create(self, data):
        folder = create(
            container=self.context, type="Folder", title=data['title'])
        cover = create(container=folder,
                       type="collective.cover.content",
                       title=data['title'])

        folder.setDefaultPage(cover.getId())

        info = {'title': u'Introduction Text',
                'text': data['introduction'].raw}
        desc_tile = make_tile("collective.cover.richtext", cover, info)
        row_1 = make_row(make_group(12, desc_tile))

        htext = u"<h1>{0}</h1>".format(data['title'] +
                                       data['highlight'].raw)

        info = {'title': u'Introduction Text', 'text': htext}
        intro_tile = make_tile("collective.cover.richtext", cover, info)
        row_2 = make_row(make_group(12, intro_tile))

        rows = [row_1, row_2]

        daviz_url = data.get('daviz_url', '').strip()
        if daviz_url:
            info = {'title': 'Graphs and trends', 'daviz_url': daviz_url}
            daviz_tile = make_tile('bise.daviz_preview', cover, info)
            row_3 = make_row(make_group(12, daviz_tile))
            rows.append(row_3)

        endpoint = data.get('sparql_endpoint', '').strip()
        isq = data.get('indicators_sparql_query', '').strip()

        if endpoint and isq:
            sparql = create_sparql(
                container=folder,
                title=data['title'] + u'Related Indicators Sparql Query',
                query=isq,
                endpoint=endpoint,
            )
            info = {'title': u'Related Indicators', 'uuid': IUUID(sparql)}
            dsr_tile = make_tile("bise.daviz_grid_listing", cover, info)
            row_4 = make_row(make_group(12, dsr_tile))
            rows.append(row_4)

        es_query = data.get('elasticsearch_query', '').strip()
        es_endpoint = data.get('elasticsearch_query_endpoint', '').strip()
        teaser_subj = data.get('catalogue_teaser', '').strip()
        teaser_link = data.get('catalogue_teaser_link', '').strip()

        if es_query and es_endpoint:
            groups = []
            es = create(container=folder,
                        type='ElasticSearch',
                        title=data['title'] + u"Further Links ES Query",
                        endpoint=es_endpoint,
                        query=es_query
                        )
            info = {'title': 'Further Links', 'uuid': IUUID(es)}
            es_list_tile = make_tile("bise.es_listing", cover, info)
            groups.append(make_group(9, es_list_tile))

            if teaser_subj and teaser_link:
                info = {'title': 'Teaser Tile', 'uuid': IUUID(es)}
                es_teaser_tile = make_tile("bise.es_teaser", cover, info)
                groups.append(make_group(3, es_teaser_tile))

            row_5 = make_row(*groups)
            rows.append(row_5)

        layout = make_layout(*rows)
        layout = json.dumps(layout)

        cover.cover_layout = layout

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
                    'id': 'wizard-maintopic',
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
                    'id': 'wizard-subtopic',
                    'separator': None,
                    'class': 'contenttype-subtopic'
                },
                'submenu': None,
            },
        ]

        res.extend(additional)
        return res
