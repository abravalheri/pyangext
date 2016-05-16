# -*- coding: utf-8 -*-
"""TODO: doc

don't use extensions inside type (prefer typedef)
declare extensions, typedefs and groupings at top level

Embedder do not solve augment statements
"""
import logging

from pyangext import __version__  # noqa
from pyangext.definitions import (
    BUILT_IN_TYPES,
    PREFIX_SEPARATOR,
    YANG_KEYWORDS
)
from pyangext.import_manager import Detector, Registry
from pyangext.syntax_tree import builder
from pyangext.utils import merge_dicts

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"

logging.basicConfig()
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.INFO)


_EXTENSION = 'custom node type (extension usage)'


def find_node_type(node):
    node_type = node.raw_keyword
    if node_type not in YANG_KEYWORDS:
        return _EXTENSION

    return node_type


def find_grouping(argument, module, ctx):
    for grouping in module.search('grouping'):
        name = grouping.arg.split(PREFIX_SEPARATOR)[-1]
        if name == argument:
            return grouping

    # Not directly found, search in includes
    for include in module.search('include'):
        grouping = find_grouping(
            argument, ctx.search_module(include.arg), ctx)
        if grouping:
            return grouping

    return None


class NoModuleFound(RuntimeError):
    pass


class NoGroupingFound(RuntimeError):
    pass


class AbstractTransformation(object):
    def __init__(self, ctx):
        self.ctx = ctx

    def transform(self, node, origin_module):
        raise NotImplementedError


class SubtreeExtractor(AbstractTransformation):
    REFERENCED_STATEMENTS = ('extension', 'typedef', 'identity', 'feature')
    """Node types that should not be present in the output
    abstract syntax tree. Instead they should be referenced using imports.
    """

    SHALLOW_NODES = ('leaf', 'leaf-list', 'anyxml', 'type', 'uses')
    """Node types which substatements can usually be safed copied
    without recursion, since they do not make references to another
    modules using prefixes.
    """

    SHALLOW_EXCEPTIONS = ('type', _EXTENSION, 'if-feature', 'base')
    """In a shallow node, just these substatements must be traversed."""

    NOT_FULLY_SUPPORTED = ('must', 'when', 'augment', 'refine', 'deviation')

    TRANSFORMATION_MAPPING = merge_dicts(
        {_EXTENSION: 'transform_extension', 'type': 'transform_type'},
        {keyword: 'transform_prefixable'
         for keyword in ('uses', 'if-feature', 'base')}
    )

    def __init__(self, ctx, output_imports=None,
                 import_registry_cache=None):
        """
        """
        super(SubtreeExtractor, self).__init__(ctx)
        self.detector = Detector(import_registry_cache)
        self.output_imports = output_imports or Registry()

    def reserve_prefix(self, *prefix):
        self.output_imports.reserve_prefix(*prefix)

    def transform(self, node, origin_module):
        node_type = find_node_type(node)

        if node_type in self.REFERENCED_STATEMENTS:
            return None

        if node_type in self.NOT_FULLY_SUPPORTED:
            _LOGGER.warning(
                '`%s` statement is not fully supported yet.', node_type)

        is_shallow = node_type in self.SHALLOW_NODES

        children = []
        for child in node.substmts:
            child_type = find_node_type(child)

            if not is_shallow or child_type in self.SHALLOW_EXCEPTIONS:
                child = self.transform(child, origin_module)

            if isinstance(child, (list, tuple)):
                # Accepting lists instead of statements is required in order
                # to bypass virutal nodes, moving offspring to grandparent.
                # This is useful, e.g., to remove the `grouping` <-> `uses`
                # indirection.
                children.extend([item for item in child if item])
            elif child:
                children.append(child)

        node.substmts = children
        if node_type not in self.TRANSFORMATION_MAPPING:
            return node

        transformation = getattr(self, self.TRANSFORMATION_MAPPING[node_type])

        return transformation(node, origin_module)

    def transform_prefixable(self, node, usage_module):
        prefix, argument, origin = self.detector.qualify(
            node.arg, usage_module)
        prefix = self.output_imports.add(prefix, origin)

        return builder(
            node.keyword,
            PREFIX_SEPARATOR.join([prefix, argument]),
            node.substmts)

    def transform_extension(self, node, usage_module):
        prefix, extension, origin = self.detector.qualify(
            node.raw_keyword, usage_module)
        prefix = self.output_imports.add(prefix, origin)

        return builder((prefix, extension), node.arg, node.substmts)

    def transform_type(self, node, usage_module):
        if node.arg in BUILT_IN_TYPES:
            return node
        return self.transform_prefixable(node, usage_module)


class UsesStatementEmbedder(SubtreeExtractor):
    # Post Order Traversion
    # Destrutive operation: objects are manipulated inline

    TRANSFORMATION_MAPPING = merge_dicts(
        SubtreeExtractor.TRANSFORMATION_MAPPING,
        {'uses': 'transform_uses'}
    )

    def transform_uses(self, node, origin_module):
        if node.substmts:
            _LOGGER.warning(
                'Defining substatements for `uses` is not fully supported.')

        (_, identifier, origin) = self.detector.qualify(
            node.arg, origin_module)

        other_module = self.ctx.search_module(None, origin)
        if other_module is None:
            raise NoModuleFound('No module %s found', origin_module)

        other_node = find_grouping(identifier, other_module, self.ctx)
        if other_node is None:
            raise NoGroupingFound('No grouping %s found', node.arg)

        children = [builder.comment(
            '--- start grouping: `{}` from `{}`'.format(identifier, origin))]

        for child in other_node.substmts:
            child = self.transform(child, other_module)
            if isinstance(child, (list, tuple)):
                for item in child:
                    if item:
                        if item.raw_keyword == 'description':
                            item = builder.comment(item.arg)

                        children.append(item)
            elif child:
                children.append(child)

        return node.substmts + children + [
            builder.comment('--- end `{}`'.format(identifier)),
            builder.blankline()
        ]
