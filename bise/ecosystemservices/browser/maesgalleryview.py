from Acquisition import aq_inner
from Products.Five.browser import BrowserView


class MAESGalleryView(BrowserView):

    def get_studies(self):
        context = aq_inner(self.context)
        studies = context.getFolderContents({'portal_type': 'Study'},
                                            full_objects=True)
        ret = []
        for study in studies:
            data = {}
            data['item'] = study
            ret.append(data)

        return ret
