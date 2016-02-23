"""
Tests for the JSON RPC request dispatcher
"""

import unittest

import nose

from mymcadmin import errors
from mymcadmin.rpc import Dispatcher

async def func1():
    """
    Test RPC method
    """

    return

async def func2():
    """
    Test RPC method
    """

    return

METHOD_MAP = {
    'test1': func1,
    'test2': func2,
}

class MethodMapObject(object):
    """
    Class that creates a method map as an object
    """

    async def test1(self):
        """
        Test RPC method
        """

        return

    async def test2(self):
        """
        Test RPC method
        """

        return

class MethodMapClass(object):
    """
    Class that is a method map
    """

    @staticmethod
    async def test1():
        """
        Test RPC method
        """

        return

    @staticmethod
    async def test2():
        """
        Test RPC method
        """

        return

class TestDispatcher(unittest.TestCase):
    """
    Tests for the JSON RPC request dispatcher
    """

    def test_constructor_dict(self):
        """
        Tests the dispatcher constructor
        """

        dispatcher = Dispatcher(methods = METHOD_MAP)

        self.assertDictEqual(
            METHOD_MAP,
            dispatcher.method_handlers,
            'Method map was not created properly',
        )

    def test_constructor_object(self):
        """
        Tests the dispatcher constructor with an object as the method map
        """

        method_map = MethodMapObject()
        dispatcher = Dispatcher(methods = method_map)

        self.assertDictEqual(
            {
                'test1': method_map.test1,
                'test2': method_map.test2,
            },
            dispatcher.method_handlers,
            'Method map was not created properly',
        )

    def test_constructor_class(self):
        """
        Tests the dispatcher constructor with a class as the method map
        """

        dispatcher = Dispatcher(methods = MethodMapClass)

        self.assertDictEqual(
            {
                'test1': MethodMapClass.test1,
                'test2': MethodMapClass.test2,
            },
            dispatcher.method_handlers,
            'Method map was not created properly',
        )

    def test_add_class(self):
        """
        Tests the add_class method
        """

        dispatcher = Dispatcher()
        dispatcher.add_class(MethodMapClass)

        self.assertDictEqual(
            {
                'methodmapclass.test1': MethodMapClass.test1,
                'methodmapclass.test2': MethodMapClass.test2,
            },
            dispatcher.method_handlers,
            'Method map was not updated properly',
        )

    def test_add_object(self):
        """
        Tests the add_object method
        """

        method_map = MethodMapObject()
        dispatcher = Dispatcher()
        dispatcher.add_object(method_map)

        self.assertDictEqual(
            {
                'methodmapobject.test1': method_map.test1,
                'methodmapobject.test2': method_map.test2,
            },
            dispatcher.method_handlers,
            'Method map was not updated properly',
        )

    def test_add_dict(self):
        """
        Tests the add_dict method
        """

        dispatcher = Dispatcher()
        dispatcher.add_dict(METHOD_MAP)

        self.assertDictEqual(
            METHOD_MAP,
            dispatcher.method_handlers,
            'Method map was not updated properly',
        )

    def test_add_dict_prefix(self):
        """
        Tests the add_dict method with a prefix
        """

        method_map = {('prefix.' + k): v for k, v in METHOD_MAP.items()}
        dispatcher = Dispatcher()
        dispatcher.add_dict(METHOD_MAP, prefix = 'prefix')

        self.assertDictEqual(
            method_map,
            dispatcher.method_handlers,
            'Method map was not updated properly',
        )

    def test_add_method_default(self):
        """
        Tests the add_method method with a default name
        """

        dispatcher = Dispatcher()
        dispatcher.add_method(func1)

        self.assertDictEqual(
            {'func1': func1},
            dispatcher.method_handlers,
            'Method map was not updated properly',
        )

    def test_add_method(self):
        """
        Tests the add_method method with a name
        """

        dispatcher = Dispatcher()
        dispatcher.add_method(func1, name = 'test')

        self.assertDictEqual(
            {'test': func1},
            dispatcher.method_handlers,
            'Method map was not updated properly',
        )

    # pylint: disable=no-self-use
    @nose.tools.raises(errors.MyMCAdminError)
    def test_add_method_non_coroutine(self):
        """
        Tests that the add_method method doesn't accept regular functions
        """

        def _i_fail():
            pass

        dispatcher = Dispatcher()
        dispatcher.add_method(_i_fail)
    # pylint: enable=no-self-use

    def test_get(self):
        """
        Tests that we can get a handler for a method name
        """

        dispatcher = Dispatcher(methods = METHOD_MAP)

        self.assertEqual(
            func1,
            dispatcher['test1'],
            'Unable to retrieve the correct handler',
        )

        self.assertEqual(
            func2,
            dispatcher['test2'],
            'Unable to retrieve the correct handler',
        )

    def test_set(self):
        """
        Tests that we can set a handler by a method name
        """

        dispatcher = Dispatcher()

        dispatcher['func1'] = func1

        self.assertEqual(
            func1,
            dispatcher['func1'],
            'Unable to set a handler',
        )

    # pylint: disable=no-self-use
    @nose.tools.raises(KeyError)
    def test_delete(self):
        """
        Tests that we can remove a method by a method name
        """

        dispatcher = Dispatcher()
        dispatcher['func1'] = func1

        del dispatcher['func1']

        _ = dispatcher['func1']
    # pylint: enable=no-self-use

    def test_len(self):
        """
        Tests that we can get the number of methods in the dispatcher
        """

        dispatcher = Dispatcher(methods = METHOD_MAP)

        self.assertEqual(
            2,
            len(dispatcher),
            'Method handler count was incorrect',
        )

    def test_iter(self):
        """
        Tests that we can iterate over all of the method handlers
        """

        dispatcher = Dispatcher(methods = METHOD_MAP)

        keys = set(METHOD_MAP.keys())

        for k in dispatcher:
            keys.remove(k)

        self.assertEqual(
            0,
            len(keys),
            'Not all methods were iterated over',
        )

    def test_construct_method_map_dict(self):
        """
        Tests that the construct_method_map works with a dict
        """

        dispatcher = Dispatcher()
        dispatcher.construct_method_map(METHOD_MAP)

        self.assertDictEqual(
            METHOD_MAP,
            dispatcher.method_handlers,
            'Method map was not constructed properly',
        )

    def test_construct_method_map_class(self):
        """
        Tests that the construct_method_map works with a class
        """

        dispatcher = Dispatcher()
        dispatcher.construct_method_map(MethodMapClass)

        self.assertDictEqual(
            {
                'test1': MethodMapClass.test1,
                'test2': MethodMapClass.test2,
            },
            dispatcher.method_handlers,
            'Method map was not constructed properly',
        )

    def test_construct_method_map_obj(self):
        """
        Tests that the construct_method_map works with an object
        """

        method_map = MethodMapObject()
        dispatcher = Dispatcher()
        dispatcher.construct_method_map(method_map)

        self.assertDictEqual(
            {
                'test1': method_map.test1,
                'test2': method_map.test2,
            },
            dispatcher.method_handlers,
            'Method map was not constructed properly',
        )

    def test_constr_method_map_prefix(self):
        """
        Tests that the construct_method_map works with a prefix
        """

        dispatcher = Dispatcher()
        dispatcher.construct_method_map(METHOD_MAP, prefix = 'prefix.')

        method_map = {('prefix.' + k): v for k, v in METHOD_MAP.items()}

        self.assertDictEqual(
            method_map,
            dispatcher.method_handlers,
            'Method map was not constructed properly',
        )

if __name__ == '__main__':
    unittest.main()

