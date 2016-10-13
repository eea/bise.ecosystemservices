#


from Products.Five.browser import BrowserView


class PDBView(BrowserView):

    def __call__(self):
        import pdb; pdb.set_trace()
        return "ok"
