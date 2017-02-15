from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Products.CMFCore.interfaces import IDynamicType
from Products.CMFCore.permissions import AddPortalContent
from plone.app.iterate import PloneMessageFactory as _
from plone.app.iterate.browser.control import Control
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.iterate.interfaces import IIterateAware
from plone.app.iterate.interfaces import IObjectArchiver
from plone.app.iterate.interfaces import IWCContainerLocator
from plone.app.iterate.interfaces import IWorkingCopy
from plone.app.iterate.permissions import CheckinPermission
from plone.app.iterate.permissions import CheckoutPermission
from plone.memoize.view import memoize
from zope.component import adapter
from zope.component import hooks
from zope.interface import implementer
import logging

logger = logging.getLogger('bise.ecosystemservices')


class IterateControl(Control):
    """ Better behaviour for plone.app.iterate
    """

    def is_checkout(self):
        """ Is this object a checkout? Used by CCA for workflow guards
        """
        context = aq_inner(self.context)

        if not IIterateAware.providedBy(context):
            return False

        archiver = IObjectArchiver(context)
        if not archiver.isVersionable():
            return False

        if IWorkingCopy.providedBy(context):
            return True

        return False

    def checkin_allowed(self):
        """ Overrided to check for the checkin permission, as it should be normal
        """

        context = aq_inner(self.context)
        checkPermission = getSecurityManager().checkPermission

        if not IIterateAware.providedBy(context):
            return False

        archiver = IObjectArchiver(context)
        if not archiver.isVersionable():
            return False

        if not IWorkingCopy.providedBy(context):
            return False

        policy = ICheckinCheckoutPolicy(context, None)
        if policy is None:
            return False

        try:
            original = policy.getBaseline()
        except:
            return False
        if original is None:
            return False

        checkPermission = getSecurityManager().checkPermission
        if not checkPermission(CheckinPermission, original):
            return False

        return True

    def checkout_allowed(self):
        """ Overrided to check for the checkout permission, as it is normal
        """
        context = aq_inner(self.context)

        if not IIterateAware.providedBy(context):
            return False

        archiver = IObjectArchiver(context)
        if not archiver.isVersionable():
            return False

        policy = ICheckinCheckoutPolicy(context, None)
        if policy is None:
            return False

        if policy.getWorkingCopy() is not None:
            return False

        # check if its is a checkout
        if policy.getBaseline() is not None:
            return False

        checkPermission = getSecurityManager().checkPermission
        if not checkPermission(CheckoutPermission, context):
            return False

        return True

    @memoize
    def cancel_allowed(self):
        """Check to see if the user can cancel the checkout on the
        given working copy
        """
        policy = ICheckinCheckoutPolicy(self.context, None)
        if policy is None:
            return False
        wc = policy.getWorkingCopy()

        if wc is None:
            return False

        has_wc = (wc is not None)
        is_wc = (self.context.aq_inner.aq_self is wc.aq_inner.aq_self)
        return has_wc and is_wc


@implementer(IWCContainerLocator)
@adapter(IDynamicType)
class CheckoutFolderLocator(object):
    """Locate the parent of the context, if the user has the
    Add portal content permission.
    """

    def __init__(self, context):
        self.context = context

    title = _(u'Special Checkout location')

    def checkout_location(self):
        site = hooks.getSite()
        if 'checkout-folder' in site.contentIds():
            return site['checkout-folder']

    @property
    def available(self):
        folder = self.checkout_location()
        if folder is None:
            return False
        return bool(
            getSecurityManager().checkPermission(
                AddPortalContent,
                aq_inner(folder)
            ))

    def __call__(self):
        if not self.available:
            return None
        return aq_inner(self.checkout_location())
