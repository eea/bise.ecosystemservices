# from Products.CMFCore.utils import getToolByName
import logging

default_profile = 'profile-bise.ecosystemservices:default'
logger = logging.getLogger('bise.ecosystemservices.upgrades')


def upgrade_to_2(context):
    logger.info("Upgrading to 2")

    # need to reimport plone.app.iterate, it has updated registry settings
    context.runImportStepFromProfile('profile-plone.app.iterate:default',
                                     'plone.app.registry')

    for name in [
        'plone.app.registry',       # collective.cover tiles
        'typeinfo',                 # the MainTopic, SubTopic types
        'workflow',                 # bise_checkout_workflow
        'placeful_workflow',        # countries policy
    ]:
        context.runImportStepFromProfile(default_profile, name)
