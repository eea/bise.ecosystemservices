from Acquisition import aq_inner
from Products.Five.browser import BrowserView


class AtlasView(BrowserView):

    def get_ecosystems(self):
        context = aq_inner(self.context)
        ecosystems = context.getFolderContents({'portal_type': 'Ecosystem'},
                                               full_objects=True)
        ret = []
        for ecosystem in ecosystems:
            data = {}
            data['item'] = ecosystem
            ret.append(data)

        return ret

    def get_services(self):
        context = aq_inner(self.context)
        services = context.getFolderContents({'portal_type': 'Service'},
                                             full_objects=True)
        ret = []
        for Service in services:
            data = {}
            data['item'] = Service
            ret.append(data)

        return ret
