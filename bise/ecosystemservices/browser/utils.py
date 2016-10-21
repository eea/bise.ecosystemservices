from collective.cover.tiles.configuration import TilesConfigurationScreen
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUIDGenerator
from zope.component import getUtility


def set_css_class(cover, tile, css_class):
    if css_class:
        tile_conf_adapter = TilesConfigurationScreen(cover, None, tile)

        conf = tile_conf_adapter.get_configuration()
        conf['css_class'] = css_class
        tile_conf_adapter.set_configuration(conf)


def make_tile(tilename, cover, info):
    id = getUtility(IUUIDGenerator)()
    # tilename = "bise.folder_contents_listing"
    tile = cover.restrictedTraverse('@@%s/%s' % (tilename, id))

    css_class = info.pop('css_class', None)

    ITileDataManager(tile).set(info)

    set_css_class(cover, tile, css_class)

    return {
        'tile-type': tilename,
        'type': 'tile',
        'id': id
    }


def make_row(*cols):
    # creates a cover row. Needs a list of columns (groups)
    return {
        'type': 'row',
        'children': cols
    }


def make_group(size=12, *tiles):
    # {"type": "group", "children":
    #     [
    #         {"tile-type": "collective.cover.richtext",
    #          "type": "tile",
    #          "id": "a42d3c2a88c8430da52136e2a204cf25"}
    #      ],
    #     "roles": ["Manager"],
    #     "column-size": 16}]

    return {
        'type': 'group',
        'roles': ['Manager'],
        'column-size': size,
        'children': tiles
    }


def make_layout(*rows):
    # creates a cover layout. Needs a list of rows

    # a layout contains rows
    # a row can contain columns (in its children).
    # a column will contain a group
    # a group will have the tile

    # sample cover layout. This is a JSON string!
    # cover_layout = [
    #     {"type": "row", "children":
    #      [{"type": "group",
    #        "children":
    #        [
    #            {"tile-type": "collective.cover.richtext",
    #            "type": "tile",
    #            "id": "be70f93bd1a4479f8a21ee595b001c06"}
    #         ],
    #        "roles": ["Manager"],
    #        "column-size": 8},
    #       {"type": "group",
    #        "children":
    #        [
    #            {"tile-type": "collective.cover.embed",
    #            "type": "tile",
    #            "id": "face16b81f2d46bc959df9da24407d94"}
    #        ],
    #        "roles": ["Manager"],
    #        "column-size": 8}]},
    #     {"type": "row",
    #      "children":
    #         [
    #             {"type": "group", "children":
    #              [
    #                  {"tile-type": "collective.cover.richtext",
    #                  "type": "tile",
    #                  "id": "a42d3c2a88c8430da52136e2a204cf25"}
    #               ],
    #              "roles": ["Manager"],
    #              "column-size": 16}]}
    # ]
    # [{u'children': [{u'children': [None],
    #                  'class': 'cell width-2 position-0',
    #                  u'column-size': 2,
    #                  u'roles': [u'Manager'],
    #                  u'type': u'group'},
    #                 {u'children': [
    #                     {u'id': u'36759ad0c8114bb48467b858593b271f',
    #                      u'tile-type': u'collective.cover.richtext',
    #                      u'type': u'tile'}],
    #                  'class': 'cell width-14 position-2',
    #                  u'column-size': 14,
    #                  u'roles': [u'Manager'],
    #                  u'type': u'group'}],
    #   'class': 'row',
    #   u'type': u'row'}]
    #
    return rows
