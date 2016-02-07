import json
import nose
import os
import os.path
import tempfile
import unittest

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
	def test_get_socket_settings_missing_type(self):
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

