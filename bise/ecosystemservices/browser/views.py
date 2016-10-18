from Products.Five.browser import BrowserView


class ServiceView(BrowserView):
    """ View class The view will automatically use a similarly named template
    in templates called serviceview.pt .
    Template filenames should be all lower case.  The view will render when you
    request a content object with this interface with "/@@view" appended unless
    specified otherwise using grok.name below.  This will make this view the
    default view for your content-type

    """


class StudyView(BrowserView):
    """
    """


class EcosystemView(BrowserView):
    """
    """
