from AccessControl import getSecurityManager
from Acquisition import aq_inner
from plone.app.iterate.browser.control import Control
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.iterate.interfaces import IIterateAware
from plone.app.iterate.interfaces import IObjectArchiver
from plone.app.iterate.interfaces import IWorkingCopy
from plone.app.iterate.permissions import CheckinPermission
from plone.app.iterate.permissions import CheckoutPermission
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
