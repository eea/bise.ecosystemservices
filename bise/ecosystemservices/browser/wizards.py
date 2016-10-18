from plone.app.content.browser.folderfactories import FolderFactoriesView
from plone.directives import form
from z3c.form import button
from zope.schema import TextLine


class IAdvancedTopicWizardSchema(form.Schema):
    """
    """

    title = TextLine(title=u"Title")


class CreateAdvancedTopic(form.SchemaForm):
    """
    """

    schema = IAdvancedTopicWizardSchema
    ignoreContext = True

    label = u"Advanced Topic wizard"

    @button.buttonAndHandler(u'Ok')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.status = "Thank you very much!"

    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """


class OverrideFolderFactoriesView(FolderFactoriesView):
    """ Override the default folder factories, to add a fake add entry
    """

    def addable_types(self, include=None):
        res = super(OverrideFolderFactoriesView, self).addable_types(include)

        res.append({
            'id': 'AdvancedTopic',
            'title': u'Advanced Topic',
            'description': u'A wizard for topics',
            'action': '@@create-advancedtopic',
            'selected': False,
            'icon': 'folder_icon.png',
            'extra': {
                'id': 'advancedtopic',
                'separator': None,
                'class': 'contenttype-advancedtopic'
            },
            'submenu': None,
        })
        return res
