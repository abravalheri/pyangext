# -*- coding: utf-8 -*-
"""Meta information about YANG modeling language."""

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"

PREFIX_SEPARATOR = ':'

URL_SEPARATOR = '/'

BUILT_IN_TYPES = [
    'binary',
    'bits',
    'boolean',
    'decimal64',
    'empty',
    'enumeration',
    'identityref',
    'instance-identifier',
    'int16',
    'int32',
    'int64',
    'int8',
    'leafref',
    'string',
    'uint16',
    'uint32',
    'uint64',
    'uint8',
    'union',
]

YANG_KEYWORDS = [
    'action',
    'anydata',
    'anyxml',
    'argument',
    'augment',
    'base',
    'belongs-to',
    'bit',
    'case',
    'choice',
    'config',
    'contact',
    'container',
    'default',
    'description',
    'deviate',
    'deviation',
    'enum',
    'error-app-tag',
    'error-message',
    'extension',
    'feature',
    'fraction-digits',
    'grouping',
    'identity',
    'if-feature',
    'import',
    'include',
    'input',
    'key',
    'leaf',
    'leaf-list',
    'length',
    'list',
    'mandatory',
    'max-elements',
    'min-elements',
    'modifier',
    'module',
    'must',
    'namespace',
    'notification',
    'ordered-by',
    'organization',
    'output',
    'path',
    'pattern',
    'position',
    'prefix',
    'presence',
    'range',
    'reference',
    'refine',
    'require-instance',
    'revision',
    'revision-date',
    'rpc',
    'status',
    'submodule',
    'type',
    'typedef',
    'unique',
    'units',
    'uses',
    'value',
    'when',
    'yang-version',
    'yin-element',
]

HEADER_STATEMENTS = [
    'organization',
    'contact',
    'revision',
    'yang-version',
]

ID_STATEMENTS = [
    'namespace',
    'prefix',
]

DATA_STATEMENTS = [
    'container',
    'leaf',
    'leaf-list',
    'list',
    'anyxml',
]
