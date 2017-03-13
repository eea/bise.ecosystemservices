""" Browser pages to adapt random queries to a format ready for Bise
"""

from Products.Five.browser import BrowserView
from Products.ZSPARQLMethod.Method import interpolate_query
from Products.ZSPARQLMethod.Method import query_and_get_result
from Products.ZSPARQLMethod.Method import run_with_timeout
from Products.statusmessages.interfaces import IStatusMessage
from eea.sparql.converter.sparql2json import sparql2json
import re


class SparqlQueryWizard(BrowserView):
    """ Wizard to change a sparql query to a format usable by Bise
    """

    choices = {
        'item_url': 'URL',
        'item_title': 'Title',
        'item_description': 'Description',
        'item_published': 'Published'
    }

    def __call__(self):
        self.results = []
        self.can_save = False
        is_post = self.request.method == 'POST'

        if is_post and ('get_data' in self.request.form):
            endpoint_url = self.context.getEndpoint_url()
            query = self.request.form.get('query')
            if not query:
                return self.index()

            cooked_query = interpolate_query(query, {})

            args = (endpoint_url, cooked_query)
            results = run_with_timeout(20, query_and_get_result, *args)
            print results
            self.results = sparql2json(results)

        elif is_post and 'relabel' in self.request.form:
            blacklist = ['query', 'relabel', 'save']
            remap = [(k, v)
                     for k, v in self.request.form.items()
                     if (v and (k not in blacklist))]

            query = self.request.form.get('query')
            sm = IStatusMessage(self.request)
            if not query:
                sm.add(u"Need a query.", type='warning')
                return self.index()

            if len(remap) != len(self.choices):
                sm.add(u"You don't have enough mapped columns", type='warning')

                return self.index()
            else:
                for rep, sub in remap:
                    rx = r'(\?' + rep + ')(?!\w)'
                    query = re.sub(rx, '?' + sub, query)
                self.query = query  # override the method
                self.can_save = True

        elif is_post and 'save' in self.request.form:
            self.context.setSparql_query(self.query())
            return self.request.response.redirect(self.context.absolute_url())

        return self.index()

    def query(self):
        if 'query' in self.request.form:
            return self.request.form.get('query')
        return self.context.getSparql_query()
