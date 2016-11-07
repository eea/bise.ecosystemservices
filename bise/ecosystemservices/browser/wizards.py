# from z3c.formwidget.optgroup.widget import OptgroupFieldWidget
# from plone.portlets.interfaces import IPortletAssignmentMapping
# from zope.schema import List
from Products.CMFCore.interfaces import IFolderish
from bise.ecosystemservices.browser.utils import make_group
from bise.ecosystemservices.browser.utils import make_layout
from bise.ecosystemservices.browser.utils import make_row
from bise.ecosystemservices.browser.utils import make_tile
from bise.ecosystemservices.tiles.vocabulary import get_tags
from eea.sparql.content.sparql import generateUniqueId
from plone.api.content import create
from plone.app.content.browser.folderfactories import FolderFactoriesView
from plone.app.textfield import RichText
from plone.app.textfield.value import RichTextValue
from plone.directives import form
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletManager
from plone.uuid.interfaces import IUUID
from z3c.form import button
from zope.component import getMultiAdapter, getUtility
from zope.schema import Choice
from zope.schema import Text
from zope.schema import TextLine
import json


# MAIN_TOPICS = [
#     "Ecosystems and habitats",
#     "Species",
#     "Genetic resources",
#     "Ecosystem services",
#     "Threats",
#     "Climate change",
#     "Invasive species",
#     "Fragmentation",
#     "Land use change",
#     "Pollution",
#     "Overexploitation",
#     "Responses",
#     "Protected areas",
#     "The wider country side",
#     "LIFE+ Nature and Biodiversity Projects",
#     "Tipping points",
# ]


DEFAULT_DAVIZ_QUERY = u"""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdfs2: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX pt: <http://www.eea.europa.eu/portal_types/Data#>
PREFIX dc: <http://purl.org/dc/terms/>

SELECT distinct (?s as ?item_url) ?item_title ?item_description ?item_published
WHERE {
 ?s ?p1 ?o1.

 OPTIONAL {?s dc:title ?item_title} .
 OPTIONAL {?s dc:abstract ?item_description} .
 OPTIONAL {?s dc:issued ?item_published} .

 filter(?p1 = <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>).
 filter(?o1 =
 <http://www.eea.europa.eu/portal_types/DavizVisualization#DavizVisualization>)
} limit 15 offset 0
"""


DEFAULT_INDICATORS_QUERY = u"""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdfs2: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX pt: <http://www.eea.europa.eu/portal_types/Data#>
PREFIX dc: <http://purl.org/dc/terms/>

SELECT (?s as ?item_url) ?item_title ?item_description ?item_published
WHERE {
 ?s ?p1 ?o1.

 OPTIONAL {?s dc:title ?item_title} .
 OPTIONAL {?s dc:abstract ?item_description} .
 OPTIONAL {?s dc:issued ?item_published} .

 filter(?p1 = <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>).
 filter(?o1 = <http://www.eea.europa.eu/portal_types/Assessment#Assessment>).

 ?s ?p2 ?o2.
 filter(?p2 = <http://www.eea.europa.eu/portal_types/Assessment#themes>).
 filter bif:contains(?o2, '"biodiversity"').

 ?s ?p3 ?o3.
 filter(?p3 = <http://purl.org/dc/terms/subject>).
 filter bif:contains(?o3, '"csi"')

} limit 15 offset 0
"""

DEFAULT_EMBED = u"""
<div class='tableauPlaceholder' id='viz1478163186645' style='position: relative'><noscript><a href='#'><img alt='Test page MAES ecosystems ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Te&#47;TestpageMAESecosystems&#47;Selectedecosystemsboard&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='site_root' value='' /><param name='name' value='TestpageMAESecosystems&#47;Selectedecosystemsboard' /><param name='tabs' value='no' /><param name='toolbar' value='no' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Te&#47;TestpageMAESecosystems&#47;Selectedecosystemsboard&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1478163186645');                    var vizElement = divElement.getElementsByTagName('object')[0];                    vizElement.style.width='1004px';vizElement.style.height='869px';                    var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>
"""


class IAdvancedTopicWizardSchema(form.Schema):
    """
    """

    # title = TextLine(title=u"Title", required=True)
    # form.widget(title=OptgroupFieldWidget)
    title = Choice(title=u"Main topic", required=True,
                   vocabulary=u'bise.catalogue.tagvocabulary_mainbranch')

    description = RichText(title=u"Topic description", required=True)

    # subtopics = List(
    #     title=u"Subtopics",
    #     description=(u"One subtopic title per line. This will prepare a "
    #                  u"separate folder for each one of them."),
    #     value_type=TextLine(title=u"Subtopic title"),
    #     required=True,
    # )

    # sparql_endpoint = TextLine(
    #     title=u"Sparql query endpoint",
    #     required=False,
    #     default=u"http://semantic.eea.europa.eu/sparql"
    # )
    baseline_sparql_query = Text(
        title=u"Baseline and Trends sparql query",
        description=(u"Sparql Query to select a colection of Daviz "
                     u"Vizualizations. This should be a sparql query "
                     u"that exposes columns: ?item_url ?item_title "
                     u"?item_description ?item_published"),
        default=DEFAULT_DAVIZ_QUERY,
        required=False
    )
    indicators_sparql_query = Text(
        title=u"Relevant Indicators sparql query",
        description=(u"Sparql Query to select a colection of Indicator "
                     u"Assessments. This should be a sparql query "
                     u"that exposes columns: ?item_url ?item_title "
                     u"?item_description ?item_published"),
        default=DEFAULT_INDICATORS_QUERY,
        required=False
    )

    tableau_embed = Text(
        title=u"Tableau embed code",
        description=u"Optional tableau embeded vizualization. Some HTML code.",
        default=DEFAULT_EMBED,
        required=False
    )

    # elasticsearch_query_endpoint = TextLine(
    #     title=u"ElasticSearch query endpoint",
    #     default=(u"http://10.128.0.50:9200/"
    #              u"catalogue_production_articles,"
    #              u"catalogue_production_documents/_search"),
    #     required=False
    # )
    elasticsearch_query = Text(
        title=u"ElasticSearch query parameters",
        default=(u'{"from" : 0, "size" : 10, '
                 u'"query":{"match": {"_all":"ecosystem"}}}'),
        required=False
    )
    # catalogue_teaser = TextLine(
    #     title=u"Catalogue Teaser Subject",
    #     description=u"If empty, will use selected topic word",
    #     required=False
    # )
    # catalogue_teaser_link = TextLine(
    #     title=u"Catalogue Teaser link",
    #     default=u"http://biodiversity.europa.eu/bise-catalogue",
    #     required=False
    # )


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
    label = u"Add Topic Page"

    def tweak_portlets(self, obj):
        manager = "plone.leftcolumn"
        portletManager = getUtility(IPortletManager, name=manager)
        assignable = getMultiAdapter((obj, portletManager),
                                     ILocalPortletAssignmentManager)
        assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)

    def create(self, data):
        folder = create(
            container=self.context, type="Folder", title=data['title'])
        cover = create(container=folder,
                       type="collective.cover.content",
                       title=data['title'])
        cover.setLayout('standard')
        folder.setDefaultPage(cover.getId())
        self.tweak_portlets(folder)

        info = {'title': u'Main Text', 'text': data['description']}
        desc_tile = make_tile("collective.cover.richtext", cover, info)

        info = {'title': u'Subtopics', 'uuid': IUUID(folder)}
        fc_tile = make_tile("bise.folder_contents_listing", cover, info)

        all_tags = get_tags()
        for tag in all_tags:
            if tag.startswith(data['title'] + ': '):
                subtopic = tag.split(':', 1)[1].strip()
                create(container=folder, type="Folder", title=subtopic)

        # for line in filter(None,
        #              [l.strip() for l in (data.get('subtopics') or [])]):
        #     create(container=folder, type="Folder", title=line)

        row_1 = make_row(make_group(12, desc_tile))
        row_2 = make_row(make_group(12, fc_tile))

        rows = [row_1, row_2]

        # endpoint = data.get('sparql_endpoint', '').strip()
        endpoint = "http://semantic.eea.europa.eu/sparql"
        gsq = data.get('baseline_sparql_query', '').strip()
        isq = data.get('indicators_sparql_query', '').strip()

        if endpoint and gsq:
            sparql = create_sparql(
                container=folder,
                title=data['title'] + u' - Baseline and Trends Sparql Query',
                query=gsq,
                endpoint=endpoint,
            )
            info = {'title': u'Baseline and Trends', 'uuid': IUUID(sparql)}
            dfw_tile = make_tile("bise.daviz_grid_listing", cover, info)
            row_3 = make_row(make_group(12, dfw_tile))
            row_3['css-class'] = "border-at-top"
            rows.append(row_3)

        tableau_embed = data.get('tableau_embed', '')
        if tableau_embed:
            info = {'title': u'Tableau embed', 'embed': tableau_embed}
            t_tile = make_tile("bise.embed", cover, info)
            row_3_1 = make_row(make_group(12, t_tile))
            rows.append(row_3_1)

        if endpoint and isq:
            sparql = create_sparql(
                container=folder,
                title=data['title'] + u' - Relevant Indicators Sparql Query',
                query=isq,
                endpoint=endpoint,
            )
            info = {'title': u'Relevant Indicators', 'uuid': IUUID(sparql)}
            dsr_tile = make_tile("bise.daviz_singlerow_listing", cover, info)
            row_4 = make_row(make_group(12, dsr_tile))
            row_4['css-class'] = "border-at-top"
            rows.append(row_4)

        es_query = data.get('elasticsearch_query', '').strip()
        es_endpoint = (u"http://10.128.0.50:9200/"
                       u"catalogue_production_articles,"
                       u"catalogue_production_documents/_search")
        teaser_subj = data['title']
        teaser_link = "http://biodiversity.europa.eu/search?q=" + teaser_subj

        # es_endpoint = data.get('elasticsearch_query_endpoint', '').strip()
        # teaser_subj = (data.get('catalogue_teaser') or '').strip()
        # if not teaser_subj:
        #     teaser_subj = data['title']
        # teaser_link = data.get('catalogue_teaser_link', '').strip()

        if es_query and es_endpoint:
            groups = []
            es = create(container=folder,
                        type='ElasticSearch',
                        title=data['title'] + u" Further Links ES Query",
                        endpoint=es_endpoint,
                        query=es_query
                        )
            info = {'title': 'Further Links', 'uuid': IUUID(es)}
            es_list_tile = make_tile("bise.es_listing", cover, info)
            groups.append(make_group(9, es_list_tile))

            if teaser_link:
                text = u"Search more about <br/>"\
                       u"<a href='{}'><i>{}</i></a> <br/> on <br/>"
                text = text.format(teaser_link, teaser_subj)
                text = RichTextValue(text or '', 'text/html', 'text/html')
                info = {'title': teaser_subj,
                        'text': text,
                        'view_more_url': teaser_link,
                        'uuid': IUUID(es)}
                es_teaser_tile = make_tile("bise.es_teaser", cover, info)
                groups.append(make_group(3, es_teaser_tile))

            row_5 = make_row(*groups)
            row_5['css-class'] = "border-at-top"
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
        description=u"A DavizVizualization URL, from the EEA website",
        default=(u"http://www.eea.europa.eu/data-and-maps/daviz/"
                 u"primary-energy-consumption-of-nzeb#tab-chart_1"),
        required=True
    )

    sparql_endpoint = TextLine(
        title=u"Sparql query endpoint",
        required=False,
        default=u"http://semantic.eea.europa.eu/sparql"
    )
    indicators_sparql_query = Text(
        title=u"Relevant Indicators sparql query",
        description=(u"Sparql Query to select a colection of Indicator "
                     u"Assessments. This should be a sparql query "
                     u"that exposes columns: ?item_url ?item_title "
                     u"?item_description ?item_published"),
        default=DEFAULT_INDICATORS_QUERY,
        required=False
    )

    elasticsearch_query_endpoint = TextLine(
        title=u"ElasticSearch query endpoint",
        default=(u"http://10.128.0.50:9200/"
                 u"catalogue_production_articles,"
                 u"catalogue_production_documents/_search"),
        required=False
    )
    elasticsearch_query = Text(
        title=u"Further Links - ElasticSearch query",
        default=(u'{"from" : 0, "size" : 100, '
                 u'"query":{"match": {"_all":"ecosystem"}}}'),
        required=False
    )
    catalogue_teaser = TextLine(
        title=u"Catalogue Teaser Subject",
        description=u"If empty, will use selected topic word",
        required=False
    )
    catalogue_teaser_link = TextLine(
        title=u"Catalogue Teaser link",
        default=u"http://biodiversity.europa.eu/bise-catalogue",
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
                'text': RichTextValue(data['introduction'].raw)}
        desc_tile = make_tile("collective.cover.richtext", cover, info)
        row_1 = make_row(make_group(12, desc_tile))

        htext = RichTextValue(u"<h1>{0}</h1>".format(data['title'] +
                                                     data['highlight'].raw))

        info = {'title': u'Introduction Text', 'text': htext}
        intro_tile = make_tile("collective.cover.richtext", cover, info)
        row_2 = make_row(make_group(12, intro_tile))

        rows = [row_1, row_2]

        daviz_url = data.get('daviz_url', '').strip()
        if daviz_url:
            info = {'title': 'Graphs and trends', 'daviz_url': daviz_url}
            daviz_tile = make_tile('bise.daviz_preview', cover, info)
            row_3 = make_row(make_group(12, daviz_tile))
            row_3['css-class'] = 'border-at-top'
            rows.append(row_3)

        endpoint = data.get('sparql_endpoint', '').strip()
        isq = data.get('indicators_sparql_query', '').strip()

        if endpoint and isq:
            sparql = create_sparql(
                container=folder,
                title=data['title'] + u'Relevant Indicators Sparql Query',
                query=isq,
                endpoint=endpoint,
            )
            info = {'title': u'Relevant Indicators', 'uuid': IUUID(sparql)}
            dsr_tile = make_tile("bise.daviz_grid_listing", cover, info)
            row_4 = make_row(make_group(12, dsr_tile))
            row_3['css-class'] = 'border-at-top'
            rows.append(row_4)

        es_query = data.get('elasticsearch_query', '').strip()
        es_endpoint = data.get('elasticsearch_query_endpoint', '').strip()
        teaser_subj = (data.get('catalogue_teaser') or '').strip()
        if not teaser_subj:
            teaser_subj = data['title']
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

            if teaser_link:
                text = u"Learn more about "\
                       u"<br/> <i>{}</i> <br/> using Bise Catalogue"
                text = RichTextValue(text.format(teaser_subj))
                info = {'title': teaser_subj,
                        'text': text,
                        'view_more_url': teaser_link,
                        'uuid': IUUID(es)}
                es_teaser_tile = make_tile("bise.es_teaser", cover, info)
                groups.append(make_group(3, es_teaser_tile))

            row_5 = make_row(*groups)
            row_3['css-class'] = 'border-at-top'
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

        if not IFolderish.providedBy(self.context):
            return res

        additional = [
            {
                'id': 'MainTopic',
                'title': u'Topic Page (advanced wizard)',
                'description': u'A wizard for topic pages',
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
