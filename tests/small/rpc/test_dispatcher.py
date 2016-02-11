import nose
import unittest

from mymcadmin import errors
from mymcadmin.rpc import Dispatcher

async def func1():
	return

async def func2():
	return

METHOD_MAP = {
	'test1': func1,
	'test2': func2,
}

class MethodMapObject(object):
	async def test1(self):
		return

	async def test2(self):
		return

class MethodMapClass(object):
	@staticmethod
	async def test1():
		return

	@staticmethod
	async def test2():
		return

class TestDispatcher(unittest.TestCase):
	def test_constructor_dict(self):
		dispatcher = Dispatcher(methods = METHOD_MAP)

		self.assertDictEqual(
			METHOD_MAP,
			dispatcher.method_handlers,
			'Method map was not created properly',
		)

	def test_constructor_object(self):
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
		dispatcher = Dispatcher()
		dispatcher.add_dict(METHOD_MAP)

		self.assertDictEqual(
			METHOD_MAP,
			dispatcher.method_handlers,
			'Method map was not updated properly',
		)

	def test_add_dict_prefix(self):
		method_map = {('prefix.' + k): v for k, v in METHOD_MAP.items()}
		dispatcher = Dispatcher()
		dispatcher.add_dict(METHOD_MAP, prefix = 'prefix')

		self.assertDictEqual(
			method_map,
			dispatcher.method_handlers,
			'Method map was not updated properly',
		)

	def test_add_method_default(self):
		dispatcher = Dispatcher()
		dispatcher.add_method(func1)

		self.assertDictEqual(
			{'func1': func1},
			dispatcher.method_handlers,
			'Method map was not updated properly',
		)

	def test_add_method(self):
		dispatcher = Dispatcher()
		dispatcher.add_method(func1, name = 'test')

		self.assertDictEqual(
			{'test': func1},
			dispatcher.method_handlers,
			'Method map was not updated properly',
		)

	@nose.tools.raises(errors.MyMCAdminError)
	def test_add_method_non_coroutine(self):
		def i_fail():
			pass

		dispatcher = Dispatcher()
		dispatcher.add_method(i_fail)

	def test_get(self):
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
		dispatcher = Dispatcher()

		dispatcher['func1'] = func1

		self.assertEqual(
			func1,
			dispatcher['func1'],
			'Unable to set a handler',
		)

	@nose.tools.raises(KeyError)
	def test_delete(self):
		dispatcher = Dispatcher()
		dispatcher['func1'] = func1

		del dispatcher['func1']

		dispatcher['func1']

	def test_len(self):
		dispatcher = Dispatcher(methods = METHOD_MAP)

		self.assertEqual(
			2,
			len(dispatcher),
			'Method handler count was incorrect',
		)

	def test_iter(self):
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
		dispatcher = Dispatcher()
		dispatcher.construct_method_map(METHOD_MAP)

		self.assertDictEqual(
			METHOD_MAP,
			dispatcher.method_handlers,
			'Method map was not constructed properly',
		)

	def test_construct_method_map_class(self):
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

	def test_construct_method_map_object(self):
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

	def test_construct_method_map_prefix(self):
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

