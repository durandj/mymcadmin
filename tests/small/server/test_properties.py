"""
Tests for the properties of the Server class
"""

import io
import json
import os.path
import unittest
import unittest.mock

import nose

from ... import utils

from mymcadmin.errors import ServerError, ServerSettingsError
from mymcadmin.server import Server

class TestServerProperties(unittest.TestCase):
    """
    Tests for the properties of the Server class
    """

    def setUp(self):
        self.server_id   = 'test_server'
        self.server_path = os.path.join('root', self.server_id)

        self.server = Server(self.server_path)

    def test_get_path(self):
        """
        Tests that we can get the path property
        """

        self.assertEqual(
            self.server_path,
            self.server.path,
            'The server path did not match',
        )

    def test_get_server_id(self):
        """
        Tests that we can get the server_id property
        """

        self.assertEqual(
            self.server_id,
            self.server.server_id,
            'The server ID did not match',
        )

    def test_get_java_default(self):
        """
        Tests that we can get a default Java binary
        """

        with utils.mock_property(self.server, 'settings') as settings:
            settings.return_value = {}

            self.assertEqual(
                'java',
                self.server.java,
                'The default Java binary did not match expected',
            )

    def test_get_java_config(self):
        """
        Tests that we can get the Java binary from the config file
        """

        java = '/usr/local/bin/java'

        with utils.mock_property(self.server, 'settings') as settings:
            settings.return_value = {
                'java': java,
            }

            self.assertEqual(
                java,
                self.server.java,
                'Java binary did not match expected',
            )

    @unittest.mock.patch('glob.glob')
    def test_get_jar_default(self, glob):
        """
        Test that we can get the default jar
        """

        glob.return_value = [
            'minecraft_server.jar',
        ]

        with utils.mock_property(self.server, 'settings') as settings:
            settings.return_value = {}

            self.assertEqual(
                'minecraft_server.jar',
                self.server.jar,
                'Server jar did not match expected',
            )

    @nose.tools.raises(ServerError)
    @unittest.mock.patch('glob.glob')
    def test_get_jar_default_missing(self, glob):
        """
        Tests that we handle when there's no jar file found
        """

        glob.return_value = []

        with utils.mock_property(self.server, 'settings') as settings:
            settings.return_value = {}

            _ = self.server.jar

    @nose.tools.raises(ServerError)
    @unittest.mock.patch('glob.glob')
    def test_get_jar_default_ambiguous(self, glob):
        """
        Tests that we handle when multiple jar files are found
        """

        glob.return_value = [
            'minecraft_server.jar',
            'thing.jar',
        ]

        with utils.mock_property(self.server, 'settings') as settings:
            settings.return_value = {}

            _ = self.server.jar

    def test_get_jar(self):
        """
        Tests that we can get the jar property from the config
        """

        with utils.mock_property(self.server, 'settings') as settings:
            settings.return_value = {
                'jar': 'minecraft_server.jar',
            }

            self.assertEqual(
                'minecraft_server.jar',
                self.server.jar,
                'Server jar did not match expected',
            )

    def test_get_command_args_default(self):
        """
        Test that we can get the default value for command line arguments
        """

        with utils.mock_property(self.server, 'java') as java, \
             utils.mock_property(self.server, 'jar') as jar, \
             utils.mock_property(self.server, 'settings') as settings:
            java.return_value     = 'java'
            jar.return_value      = 'minecraft_server.jar'
            settings.return_value = {}

            self.assertListEqual(
                ['java', '-jar', 'minecraft_server.jar'],
                self.server.command_args,
                'Command args did not match expected',
            )

    def test_get_command_args(self):
        """
        Tests that we set extra arguments that they're used
        """

        with utils.mock_property(self.server, 'java') as java, \
             utils.mock_property(self.server, 'jar') as jar, \
             utils.mock_property(self.server, 'settings') as settings:
            java.return_value     = 'java'
            jar.return_value      = 'minecraft_server.jar'
            settings.return_value = {
                'jvm_args': ['-Xmx1024M'],
                'args':     ['nogui']
            }

            self.assertListEqual(
                ['java', '-Xmx1024M', '-jar', 'minecraft_server.jar', 'nogui'],
                self.server.command_args,
                'Command args did not match expected',
            )

    def test_get_command_args_unsafe(self):
        """
        Tests that we handle unsafe command line arguments
        """

        with utils.mock_property(self.server, 'java') as java, \
             utils.mock_property(self.server, 'jar') as jar, \
             utils.mock_property(self.server, 'settings') as settings:
            java.return_value     = 'java'
            jar.return_value      = 'minecraft_server.jar'
            settings.return_value = {
                'args': ['; rm -rf /;'],
            }

            self.assertEqual(
                ['java', '-jar', 'minecraft_server.jar', '\'; rm -rf /;\''],
                self.server.command_args,
                'Unsafe command was executed',
            )

    @unittest.mock.patch('builtins.open')
    def test_get_properties(self, mock_open):
        """
        Tests that we can get the properties property
        """

        stream = io.StringIO(SAMPLE_PROPERTIES)

        mock_open.return_value = mock_open
        mock_open.__enter__.return_value = stream

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
            'Properties did not match expected',
        )

    @nose.tools.raises(ServerError)
    @unittest.mock.patch('builtins.open')
    def test_get_properties_missing(self, mock_open):
        """
        Tests that we handle when the properties file is missing
        """

        mock_open.side_effect = FileNotFoundError('Nope.nope')

        _ = self.server.properties

    @unittest.mock.patch('builtins.open')
    def test_get_settings(self, mock_open):
        """
        Tests that we can get the settings property
        """

        settings = {
            'java': '/usr/local/bin/java',
            'args': ['-test'],
        }

        stream = io.StringIO(
            json.dumps(
                settings,
            )
        )

        mock_open.return_value = mock_open
        mock_open.__enter__.return_value = stream

        self.assertEqual(
            settings,
            self.server.settings,
            'Settings did not match expected',
        )

    @nose.tools.raises(ServerSettingsError)
    @unittest.mock.patch('builtins.open')
    def test_get_settings_missing(self, mock_open):
        """
        Tests that we handle when there's no settings file
        """

        mock_open.side_effect = FileNotFoundError('Nope.nope')

        _ = self.server.settings

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

if __name__ == '__main__':
    unittest.main()

