# -*- coding: utf-8 -*-
"""TODO: doc
"""
from pyangext.definitions import PREFIX_SEPARATOR
from pyangext.utils import namespacefy

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"


class Registry(object):
    def __init__(self):
        # Indexes
        self.by_prefix = {}  # prefix -> module name
        self.by_name = {}    # module name -> prefix
        # Collisions counters
        self.prefix_request = {}

        self.prefixes_reserved = []

    def add(self, prefix, name):
        # See if module was already registed
        some_prefix = self.by_name.get(name)
        if some_prefix:
            return some_prefix

        if prefix is None:
            prefix = namespacefy(name)

        occurencies = self.prefix_request.get(prefix, 0) + 1

        if occurencies > 1:
            # Increment the number of colisions because 2 different modules
            # are trying to use the same prefix.
            self.prefix_request[prefix] = occurencies
            # Generate a brand new prefix, by adding the counter
            prefix += str(occurencies)

        # In this point of method, the prefix is guaranteed to be fresh
        self.prefix_request[prefix] = 1
        self.by_prefix[prefix] = name
        self.by_name[name] = prefix

        return prefix

    def find_name(self, prefix):
        return self.by_prefix.get(prefix)

    def find_prefix(self, name):
        return self.by_name.get(name)

    def reserve_prefix(self, *prefixes):
        for prefix in prefixes:
            self.prefixes_reserved.append(prefix)
            self.prefix_request[prefix] = 1

    def copy(self):
        other = type(self)()
        other.prefix_request = self.prefix_request.copy()
        other.by_prefix = self.by_prefix.copy()
        other.by_name = self.by_name.copy()
        other.prefixes_reserved = self.prefixes_reserved[:]

        return other

    @property
    def prefixes_taken(self):
        return self.by_prefix.keys()

    @classmethod
    def from_imports(cls, import_list):
        registry = cls()

        for node in import_list:
            name = node.arg
            prefix = getattr(node.search_one('prefix'), 'arg', None)
            registry.add(prefix, name)

        return registry


class Detector(object):
    def __init__(self, registry_cache=None):
        self.registry_cache = registry_cache or {}

    def create_registry(self, imports):  # pylint: disable=no-self-use
        return Registry.from_imports(imports)

    def find_imports(self, module):
        module_name = module.arg
        return (
            self.registry_cache.get(module_name) or
            self.registry_cache.setdefault(
                module_name, self.create_registry(module.search('import')))
        )

    def find_origin_by_prefix(self, prefix, module):
        registry = self.find_imports(module)
        return registry.find_name(prefix)

    def qualify(self, identifier, module):
        origin = None

        if isinstance(identifier, tuple):
            prefix, identifier = identifier
        if PREFIX_SEPARATOR in identifier:
            prefix, identifier = identifier.split(PREFIX_SEPARATOR)
        else:
            prefix = module.search_one('prefix').arg
            origin = module.arg

        if not origin:
            # when typedef is not local find the origin
            origin = self.find_origin_by_prefix(prefix, module)

        return (prefix, identifier, origin)
