import asyncio
import collections

from .. import errors

class Dispatcher(collections.MutableMapping):
    def __init__(self, methods = None):
        self.method_handlers = {}

        if methods is not None:
            self.construct_method_map(methods)

    def add_class(self, cls):
        prefix = cls.__name__.lower() + '.'

        self.construct_method_map(cls(), prefix)

    def add_object(self, obj):
        prefix = obj.__class__.__name__.lower() + '.'

        self.construct_method_map(obj, prefix)

    def add_dict(self, prototype, prefix = ''):
        if prefix:
            prefix += '.'

        self.construct_method_map(prototype, prefix)

    def add_method(self, func, name = None):
        if not asyncio.iscoroutinefunction(func):
            raise errors.MyMCAdminError(
                'RPC handler functions must be coroutines'
            )

        self.method_handlers[name or func.__name__] = func

    def __getitem__(self, key):
        return self.method_handlers[key]

    def __setitem__(self, key, value):
        self.method_handlers[key] = value

    def __delitem__(self, key):
        del self.method_handlers[key]

    def __len__(self):
        return len(self.method_handlers)

    def __iter__(self):
        return iter(self.method_handlers)

    def construct_method_map(self, method_map, prefix = ''):
        if not isinstance(method_map, dict):
            method_map = {
                m: getattr(method_map, m)
                for m in dir(method_map)
                if not m.startswith('_')
            }

        for name, method in method_map.items():
            if callable(method):
                self.add_method(method, name = prefix + name)

