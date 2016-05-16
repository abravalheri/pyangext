# -*- coding: utf-8 -*-
"""TODO: doc
"""
import optparse  # pylint: disable=deprecated-module
import re

from pyang import plugin
from pyang.translators.yang import emit_yang
from pyang.translators.yin import emit_yin

from pyangext.transformations import Embedder

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"


def pyang_plugin_init():
    plugin.register_plugin(ExapanderPlugin())


class ExapanderPlugin(plugin.PyangPlugin):
    """Given a YANG module, expand ``uses`` statement"""

    FILENAME_REGEX = re.compile(r"^(.*?)(\@(\d{4}-\d{2}-\d{2}))?\.(\w+)$")

    def __init__(self, *args, **kwargs):
        super(ExapanderPlugin, self).__init__(*args, **kwargs)
        self.format = None
        self.prefix = None
        self.namespace = None
        self.name = None

    def add_opts(self, optparser):
        optgrp = optparser.add_option_group(
            '`uses` statement exapander specific options')
        optgrp.add_options([
            optparse.make_option(
                '--output-module-suffix',
                default=None,
                help=(
                    'The generated module will have this suffix appended to '
                    'the original module name (if no name provided)'
                )
            ),
            optparse.make_option(
                '--output-module-name',
                default=None,
                help='The generated module will have this name'
            ),
            optparse.make_option(
                '--output-module-namespace',
                default=None,
                help='The generated module will have this namespace'
            ),
            optparse.make_option(
                '--output-module-prefix',
                default=None,
                help='The generated module will have this prefix'
            ),
        ])

    def add_output_format(self, fmts):
        """Register output formats handled by plugin"""

        self.multiple_modules = False
        fmts['expanded'] = self

    def post_validate_ctx(self, ctx, modules):
        """Store context"""
        module = modules[0]

        options = ctx.opts
        output_name = ctx.opts.outfile
        self.format = 'yin' if 'yin' in ctx.opts.format else 'yang'

        self.prefix = (
            options.output_module_prefix or
            module.search_one('prefix').arg
        )
        prefix_joiner = '_' if '_' in self.prefix else '-'

        self.namespace = (
            options.output_module_namespace or
            module.search_one('namespace').arg
        )
        namespace_joiner = '/' if '://' in self.namespace else ':'

        self.name = options.output_module_name or module.arg
        name_joiner = '_' if '_' in self.name else '-'

        if options.output_module_suffix:
            suffix = options.output_module_suffix
            self.name = name_joiner.join([
                self.name, suffix])
            self.namespace = namespace_joiner.join([
                self.namespace, suffix])
            self.prefix = prefix_joiner.join([
                self.prefix, suffix])

        if output_name:
            match = self.FILENAME_REGEX.search(output_name)
            if match is not None:
                (self.name, _, _, self.format) = match.groups()

    def emit(self, ctx, modules, fd):
        """Generate YANG/YIN file with RPC definitions"""

        serialize = emit_yin if self.format == 'yin' else emit_yang
        transformation = Embedder(ctx)
        module = modules[0]
        node = transformation.transform(module, module)
        node.arg = self.name

        namespace = [
            child
            for child in node.substmts
            if child.raw_keyword == 'namespace'
        ]

        if namespace:
            namespace[0].arg = self.namespace

        prefix = [
            child
            for child in node.substmts
            if child.raw_keyword == 'prefix'
        ]

        if prefix:
            prefix[0].arg = self.prefix

        return serialize(ctx, node, fd)
