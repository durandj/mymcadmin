import asyncio
import copy
import json
import nose
import os
import os.path
import tempfile
import unittest
import unittest.mock

from mymcadmin import errors, server

SAMPLE_PROPERTIES = """#Minecraft server properties
#Sat Feb 06 16:13:59 CST 2016
max-tick-time=60000
generator-settings=
force-gamemode=false
allow-nether=true
gamemode=0
enable-query=false
player-idle-timeout=0
difficulty=1
spawn-monsters=true
op-permission-level=4
resource-pack-hash=
announce-player-achievements=true
pvp=true
snooper-enabled=true
level-type=DEFAULT
hardcore=false
enable-command-block=false
max-players=20
network-compression-threshold=256
max-world-size=29999984
server-port=25565
server-ip=
spawn-npcs=true
allow-flight=false
level-name=world
view-distance=10
resource-pack=
spawn-animals=true
white-list=false
generate-structures=true
online-mode=true
max-build-height=256
level-seed=
use-native-transport=true
motd=A Test Minecraft Server
enable-rcon=false
"""

SAMPLE_VERSIONS = {
	'latest': {
		'snapshot': 'my_snapshot',
		'release':  'my_release',
	},
	'versions': [
		{
			'id':          'my_snapshot',
			'releaseTime': '2016-01-04T00:00:00+00:00',
			'time':        '2016-01-04T00:10:00+00:00',
			'type':        'snapshot',
			'url':         'http://example.com/mc/my_snapshot.json',
		},
		{
			'id':          'my_release',
			'releaseTime': '2016-01-03T00:00:00+00:00',
			'time':        '2016-01-03T00:20:00+00:00',
			'type':        'release',
			'url':         'http://example.com/mc/my_release.json',
		},
		{
			'id':          'my_beta',
			'releaseTime': '2016-01-02T00:00:00+00:00',
			'time':        '2016-01-02T00:30:00+00:00',
			'type':        'old_beta',
			'url':         'http://example.com/mc/my_beta.json',
		},
		{
			'id':          'my_alpha',
			'releaseTime': '2016-01-01T00:00:00+00:00',
			'time':        '2016-01-01T00:40:00+00:00',
			'type':        'old_alpha',
			'url':         'http://example.com/mc/my_alpha.json',
		}
	],
}

class TestServer(unittest.TestCase):
	def setUp(self):
		self.temp_dir    = tempfile.TemporaryDirectory()
		self.root_path   = self.temp_dir.name
		self.server_path = os.path.join(self.root_path, 'test')
		self.server      = server.Server(self.server_path)

		os.mkdir(self.server_path)

		self._set_server_settings({})

		properties_file = os.path.join(self.server_path, 'server.properties')
		with open(properties_file, 'w') as fh:
			fh.write(SAMPLE_PROPERTIES)

	def tearDown(self):
		self.temp_dir.cleanup()

	def test_get_path(self):
		self.assertEqual(
			self.server_path,
			self.server.path,
			'Server path did not match',
		)

	@nose.tools.raises(AttributeError)
	def test_set_path(self):
		self.server.path = 'Bad!'

	def test_get_name(self):
		self.assertEqual(
			'test',
			self.server.name,
			'Server name did not match',
		)

	@nose.tools.raises(AttributeError)
	def test_set_name(self):
		self.server.name = 'Bad!'

	def test_get_pid_file(self):
		self.assertEqual(
			os.path.join(self.server_path, 'server.pid'),
			self.server.pid_file,
			'Server PID file did not match',
		)

	@nose.tools.raises(AttributeError)
	def test_set_pid_file(self):
		self.server.pid_file = 'Bad!'

	def test_get_java_default(self):
		self.assertEqual(
			'java',
			self.server.java,
			'Server Java binary did not match',
		)

	def test_get_java_config(self):
		self._set_server_settings(
			{
				'java': '/usr/local/bin/java',
			}
		)

		self.assertEqual(
			'/usr/local/bin/java',
			self.server.java,
			'Server Java binary did not match',
		)

	@nose.tools.raises(AttributeError)
	def test_set_java(self):
		self.server.java = 'Bad!'

	def test_get_jar_default(self):
		fake_jar = self._touch_file('minecraft_test.jar')

		self.assertEqual(
			fake_jar,
			self.server.jar,
			'Server Jar did not match',
		)

	@nose.tools.raises(errors.ServerError)
	def test_get_jar_default_missing(self):
		self.server.jar

	@nose.tools.raises(errors.ServerError)
	def test_get_jar_default_multiple(self):
		for i in range(2):
			self._touch_file('minecraft_test_{}.jar'.format(i))

		self.server.jar

	def test_get_jar(self):
		self._set_server_settings(
			{
				'jar': 'minecraft_server.jar',
			}
		)

		self.assertEqual(
			'minecraft_server.jar',
			self.server.jar,
			'Server Jar did not match',
		)

	@nose.tools.raises(AttributeError)
	def test_set_jar(self):
		self.server.jar = 'Bad!'

	def test_get_command_args_default(self):
		fake_jar = self._touch_file('minecraft_test.jar')

		self.assertEqual(
			['java', '-jar', fake_jar],
			self.server.command_args,
			'Default command args did not match',
		)

	def test_get_command_args_java(self):
		self._set_server_settings({'java': '/usr/local/bin/java'})
		fake_jar = self._touch_file('minecraft_test.jar')

		self.assertEqual(
			['/usr/local/bin/java', '-jar', fake_jar],
			self.server.command_args,
			'Java binary was not set in command args',
		)

	def test_get_command_args_jvm_args(self):
		self._set_server_settings({'jvm_args': ['-test']})
		fake_jar = self._touch_file('minecraft_test.jar')

		self.assertEqual(
			['java', '-test', '-jar', fake_jar],
			self.server.command_args,
			'JVM args were not set in command args',
		)

	def test_get_command_args_args(self):
		self._set_server_settings({'args': ['-test']})
		fake_jar = self._touch_file('minecraft_test.jar')

		self.assertEqual(
			['java', '-jar', fake_jar, '-test'],
			self.server.command_args,
			'Program args were not set in command args',
		)

	def test_get_command_args_unsafe(self):
		self._set_server_settings({'args': ['; rm -rf /;']})
		fake_jar = self._touch_file('minecraft_test.jar')

		self.assertEqual(
			['java', '-jar', fake_jar, '\'; rm -rf /;\''],
			self.server.command_args,
			'Allowed unsafe bash commands to run',
		)

	@nose.tools.raises(AttributeError)
	def test_set_command_args(self):
		self.server.command_args = []

	def test_get_admin_log(self):
		self.assertEqual(
			os.path.join(self.server_path, 'mymcadmin.log'),
			self.server.admin_log,
			'Admin log did not match',
		)

	@nose.tools.raises(AttributeError)
	def test_set_admin_log(self):
		self.server.admin_log = 'Bad!'

	def test_get_properties(self):
		self.assertDictEqual(
			{
				'max-tick-time':                 60000,
				'generator-settings':            None,
				'force-gamemode':                False,
				'allow-nether':                  True,
				'gamemode':                      0,
				'enable-query':                  False,
				'player-idle-timeout':           0,
				'difficulty':                    1,
				'spawn-monsters':                True,
				'op-permission-level':           4,
				'resource-pack-hash':            None,
				'announce-player-achievements':  True,
				'pvp':                           True,
				'snooper-enabled':               True,
				'level-type':                    'DEFAULT',
				'hardcore':                      False,
				'enable-command-block':          False,
				'max-players':                   20,
				'network-compression-threshold': 256,
				'max-world-size':                29999984,
				'server-port':                   25565,
				'server-ip':                     None,
				'spawn-npcs':                    True,
				'allow-flight':                  False,
				'level-name':                    'world',
				'view-distance':                 10,
				'resource-pack':                 None,
				'spawn-animals':                 True,
				'white-list':                    False,
				'generate-structures':           True,
				'online-mode':                   True,
				'max-build-height':              256,
				'level-seed':                    None,
				'use-native-transport':          True,
				'motd':                          'A Test Minecraft Server',
				'enable-rcon':                   False,
			},
			self.server.properties,
			'Server properties did not match',
		)

	@nose.tools.raises(errors.ServerError)
	def test_get_properties_missing(self):
		os.remove(os.path.join(self.server_path, 'server.properties'))

		self.server.properties

	@nose.tools.raises(AttributeError)
	def test_set_properties(self):
		self.server.properties = 'Bad!'

	def test_get_settings(self):
		settings = {
			'java': '/usr/local/bin/java',
			'args': ['-test'],
		}

		self._set_server_settings(settings)

		self.assertEqual(
			settings,
			self.server.settings,
			'Server settings did not match',
		)

	@nose.tools.raises(errors.ServerSettingsError)
	def test_get_settings_missing(self):
		settings_file = os.path.join(self.server_path, 'mymcadmin.settings')
		os.remove(settings_file)

		self.server.settings

	@nose.tools.raises(AttributeError)
	def test_set_settings(self):
		self.server.settings = 'Bad!'

	def test_get_socket_settings(self):
		self._set_server_settings(
			{
				'socket': {
					'type': 'tcp',
					'host': 'example.com',
					'port': 9001,
				},
			}
		)

		socket_type, host, port = self.server.socket_settings

		self.assertEqual(
			'tcp',
			socket_type,
			'Socket type did not match',
		)

		self.assertEqual(
			'example.com',
			host,
			'The host did not match',
		)

		self.assertEqual(
			9001,
			port,
			'The port did not match',
		)

	@nose.tools.raises(errors.ServerSettingsError)
	def test_get_socket_settings_missing_type(self):
		self._set_server_settings(
			{
				'socket': {
					'host': 'example.com',
					'port': 9001,
				},
			}
		)

		socket_type, host, port = self.server.socket_settings

	def test_get_socket_settings_missing_host(self):
		self._set_server_settings(
			{
				'socket': {
					'type': 'tcp',
					'port': 9001,
				},
			}
		)

		socket_type, host, port = self.server.socket_settings

		self.assertEqual(
			'localhost',
			host,
			'The default host did not match',
		)

	@nose.tools.raises(errors.ServerSettingsError)
	def test_get_socket_settings_missing_port(self):
		self._set_server_settings(
			{
				'socket': {
					'type': 'tcp',
					'host': 'example.com',
				},
			}
		)

		socket_type, host, port = self.server.socket_settings

	@nose.tools.raises(errors.ServerSettingsError)
	def test_get_socket_settings_invalid_type(self):
		self._set_server_settings(
			{
				'socket': {
					'type': 'bad',
					'port': 9001,
				},
			}
		)

		socket_type, host, port = self.server.socket_settings

	@nose.tools.raises(errors.ServerSettingsError)
	def test_get_socket_settings_invalid_port(self):
		self._set_server_settings(
			{
				'socket': {
					'type': 'tcp',
					'port': 'test',
				}
			}
		)

		self.server.socket_settings

	@unittest.mock.patch('asyncio.create_subprocess_exec')
	def test_start(self, create_subprocess_exec):
		fake_jar = self._touch_file('minecraft_test.jar')

		self.server.start()

		create_subprocess_exec.assert_called_with(
			'java',
			'-jar',
			fake_jar,
			stdin  = asyncio.subprocess.PIPE,
			stdout = asyncio.subprocess.PIPE,
			stderr = asyncio.subprocess.PIPE,
		)

	@unittest.mock.patch('mymcadmin.server.rpc.RpcClient')
	def test_stop(self, rpc_client):
		rpc_client.return_value = rpc_client
		rpc_client.__enter__.return_value = rpc_client

		self._set_server_settings(
			{
				'socket': {
					'type': 'tcp',
					'port': 9001,
				}
			}
		)

		self.server.stop()

		rpc_client.assert_called_with('localhost', 9001)
		self.assertTrue(rpc_client.server_stop.called)

	def test_list_all(self):
		mock_config = unittest.mock.Mock(instance_path = self.root_path)

		servers = server.Server.list_all(mock_config)
		self.assertEqual(
			[self.server_path],
			servers,
			'Server list did not match',
		)

	@unittest.mock.patch('requests.get')
	def test_list_versions_default(self, requests_get):
		response_mock = unittest.mock.Mock()
		response_mock.configure_mock(
			ok = True,
			**{
				'json.return_value': copy.deepcopy(SAMPLE_VERSIONS),
			}
		)

		requests_get.return_value = response_mock

		versions = server.Server.list_versions()

		self.assertTrue(
			requests_get.called,
			'No HTTP request initiated',
		)

		self.assertDictEqual(
			SAMPLE_VERSIONS,
			versions,
			'Not all data was returned',
		)

	@unittest.mock.patch('requests.get')
	def test_list_versions_filter(self, requests_get):
		response_mock = unittest.mock.Mock()
		requests_get.return_value = response_mock

		# Iterate over every possible filter combination
		for i in range(16):
			requests_get.reset_mock()
			response_mock.configure_mock(
				ok = True,
				**{
					'json.return_value': copy.deepcopy(SAMPLE_VERSIONS),
				}
			)

			snapshots = i & 0b1000 > 0
			releases  = i & 0b0100 > 0
			betas     = i & 0b0010 > 0
			alphas    = i & 0b0001 > 0

			versions = self.server.list_versions(
				snapshots = snapshots,
				releases  = releases,
				betas     = betas,
				alphas    = alphas,
			)

			remaining_types = [
				v['type']
				for v in versions['versions']
			]

			if not snapshots:
				self.assertTrue(
					'latest' not in versions['latest'],
					'Snapshot not filtered from latest',
				)

				self.assertNotIn(
					'snapshot',
					remaining_types,
					'Snapshots were found in data',
				)

			if not releases:
				self.assertTrue(
					'release' not in versions['latest'],
					'Release not filtered from latest',
				)

				self.assertNotIn(
					'release',
					remaining_types,
					'Releases were found in data',
				)

			if not betas:
				self.assertNotIn(
					'old_beta',
					remaining_types,
					'Betas were found in data',
				)

			if not alphas:
				self.assertNotIn(
					'old_alpha',
					remaining_types,
					'Alphas were found in data',
				)

	@nose.tools.raises(errors.MyMCAdminError)
	@unittest.mock.patch('requests.get')
	def test_list_versions_network_error(self, requests_get):
		response_mock = unittest.mock.Mock()
		response_mock.configure_mock(ok = False)

		requests_get.return_value = response_mock

		versions = server.Server.list_versions()

	def _set_server_settings(self, settings):
		settings_file = os.path.join(self.server_path, 'mymcadmin.settings')
		with open(settings_file, 'w') as fh:
			json.dump(settings, fh)

	def _touch_file(self, file_name):
		file_name = os.path.join(self.server_path, file_name)
		with open(file_name, 'w'):
			pass

		return file_name

if __name__ == '__main__':
	unittest.main()

