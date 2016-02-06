import unittest

from mymcadmin import server

class TestServer(unittest.TestCase):
	def setUp(self):
		self.server = server.Server('/path/to/testServers/test')

	def test_path(self):
		self.assertEqual(
			'/path/to/testServers/test',
			self.server.path,
			'Server path did not match',
		)

	def test_name(self):
		self.assertEqual(
			'test',
			self.server.name,
			'Server name did not match',
		)

if __name__ == '__main__':
	unittest.main()

