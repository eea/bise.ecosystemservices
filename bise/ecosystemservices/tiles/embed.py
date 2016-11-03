from collective.cover.tiles.embed import EmbedTile as BaseEmbedTile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class EmbedTile(BaseEmbedTile):
    """ Override the default embed tile because we never want to show title
    """

    short_name = default = u'HTML Embed'
    index = ViewPageTemplateFile('pt/embed.pt')
