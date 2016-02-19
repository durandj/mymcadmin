"""
Tests for the Server class
"""

import asyncio
import copy
import io
import json
import os
import os.path
import tempfile
import unittest
import unittest.mock

import nose
import requests

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

# pylint: disable=too-many-public-methods
class TestServer(unittest.TestCase):
    """
    Tests for the Server class
    """

    def setUp(self):
        self.temp_dir    = tempfile.TemporaryDirectory()
        self.root_path   = self.temp_dir.name
        self.server_path = os.path.join(self.root_path, 'test')
        self.server      = server.Server(self.server_path)

        os.mkdir(self.server_path)

        self._set_server_settings({})

        properties_file = os.path.join(self.server_path, 'server.properties')
        with open(properties_file, 'w') as settings_file:
            settings_file.write(SAMPLE_PROPERTIES)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_get_path(self):
        """
        Test the path property works correctly
        """

        self.assertEqual(
            self.server_path,
            self.server.path,
            'Server path did not match',
        )

    @nose.tools.raises(AttributeError)
    def test_set_path(self):
        """
        Check that we can't assign the path property
        """

        self.server.path = 'Bad!'

    def test_get_server_id(self):
        """
        Test the server_id property works correctly
        """

        self.assertEqual(
            'test',
            self.server.server_id,
            'Server ID did not match',
        )

    @nose.tools.raises(AttributeError)
    def test_set_server_id(self):
        """
        Check that we can't assign the server_id property
        """

        self.server.server_id = 'Bad!'

    def test_get_java_config(self):
        """
        Test that we can get the Java binary from the config file
        """

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
        """
        Check that we can't assign the java property
        """

        self.server.java = 'Bad!'

    def test_get_jar_default(self):
        """
        Test that we can get the Java binary default value
        """

        fake_jar = self._touch_file('minecraft_test.jar')

        self.assertEqual(
            fake_jar,
            self.server.jar,
            'Server Jar did not match',
        )

    @nose.tools.raises(errors.ServerError)
    def test_get_jar_default_missing(self):
        """
        Test that we raise the correct error if no jar is given or could be found
        """

        _ = self.server.jar

    @nose.tools.raises(errors.ServerError)
    def test_get_jar_default_multiple(self):
        """
        Test that we raise the correct error if no jar was specified and there
        was more than one jar in the instance
        """

        for i in range(2):
            self._touch_file('minecraft_test_{}.jar'.format(i))

        _ = self.server.jar

    def test_get_jar(self):
        """
        Test that we can get the jar from the config setting
        """

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
        """
        Test that we can't set the jar property
        """

        self.server.jar = 'Bad!'

    def test_get_command_args_default(self):
        """
        Test that we can get the default value for the command line arguments
        """

        fake_jar = self._touch_file('minecraft_test.jar')

        self.assertEqual(
            ['java', '-jar', fake_jar],
            self.server.command_args,
            'Default command args did not match',
        )

    def test_get_command_args_java(self):
        """
        Test that we can get the command line arguments from the settings file
        """

        self._set_server_settings({'java': '/usr/local/bin/java'})
        fake_jar = self._touch_file('minecraft_test.jar')

        self.assertEqual(
            ['/usr/local/bin/java', '-jar', fake_jar],
            self.server.command_args,
            'Java binary was not set in command args',
        )

    def test_get_command_args_jvm_args(self):
        """
        Test that we get can get the JVM arguments from the settings
        """

        self._set_server_settings({'jvm_args': ['-test']})
        fake_jar = self._touch_file('minecraft_test.jar')

        self.assertEqual(
            ['java', '-test', '-jar', fake_jar],
            self.server.command_args,
            'JVM args were not set in command args',
        )

    def test_get_command_args_args(self):
        """
        Test that we get the program arguments from the settings
        """

        self._set_server_settings({'args': ['-test']})
        fake_jar = self._touch_file('minecraft_test.jar')

        self.assertEqual(
            ['java', '-jar', fake_jar, '-test'],
            self.server.command_args,
            'Program args were not set in command args',
        )

    def test_get_command_args_unsafe(self):
        """
        Test that we handle unsafe command line arguments
        """

        self._set_server_settings({'args': ['; rm -rf /;']})
        fake_jar = self._touch_file('minecraft_test.jar')

        self.assertEqual(
            ['java', '-jar', fake_jar, '\'; rm -rf /;\''],
            self.server.command_args,
            'Allowed unsafe bash commands to run',
        )

    @nose.tools.raises(AttributeError)
    def test_set_command_args(self):
        """
        Check that we can't assign the comand_args property
        """

        self.server.command_args = []

    def test_get_properties(self):
        """
        Check that we can get the server properties
        """

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
        """
        Check that we raise the correct error if there is no properties file
        """

        os.remove(os.path.join(self.server_path, 'server.properties'))

        _ = self.server.properties

    @nose.tools.raises(AttributeError)
    def test_set_properties(self):
        """
        Check that we don't allow assigning of the properties property
        """

        self.server.properties = 'Bad!'

    def test_get_settings(self):
        """
        Check that we ca get the settings property
        """

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
        """
        Check that we raise the correct error if there is no settings file
        """

        settings_file = os.path.join(self.server_path, 'mymcadmin.settings')
        os.remove(settings_file)

        _ = self.server.settings

    @nose.tools.raises(AttributeError)
    def test_set_settings(self):
        """
        Check that we can't assign the settings property
        """

        self.server.settings = 'Bad!'

    @unittest.mock.patch('asyncio.create_subprocess_exec')
    def test_start(self, create_subprocess_exec):
        """
        Test the server start command works as expected
        """

        fake_jar = self._touch_file('minecraft_test.jar')

        self.server.start()

        create_subprocess_exec.assert_called_with(
            'java',
            '-jar',
            fake_jar,
            cwd    = self.server_path,
            stdin  = asyncio.subprocess.PIPE,
            stdout = asyncio.subprocess.PIPE,
            stderr = asyncio.subprocess.PIPE,
        )

    @unittest.mock.patch('requests.get')
    def test_list_versions_default(self, requests_get):
        """
        Test that the list_versions method returns correctly
        """

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
        """
        Check that we can filter out versions by their release type
        """

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

    # pylint: disable=no-self-use
    @nose.tools.raises(errors.MyMCAdminError)
    @unittest.mock.patch('requests.get')
    def test_list_versions_network(self, requests_get):
        """
        Check that we handle networking errors when getting the version list
        """

        response_mock = unittest.mock.Mock()
        response_mock.configure_mock(ok = False)

        requests_get.return_value = response_mock

        server.Server.list_versions()
    # pylint: enable=no-self-use

    @unittest.mock.patch('requests.get')
    @unittest.mock.patch('mymcadmin.server.Server.list_versions')
    def test_get_version_info(self, list_versions, requests_get):
        """
        Tests that we can get the information about a specific version
        """

        list_versions.return_value = {
            'latest': {
                'snapshot': 'mysnapshot',
                'release':  'myrelease',
            },
            'versions': [
                {
                    'id':          'mysnapshot',
                    'type':        'snapshot',
                    'time':        '2016-01-04T00:00:00+00:00',
                    'releaseTime': '2016-01-04T00:00:00+00:00',
                    'url':         'http://example.com/mc/mysnapshot',
                },
                {
                    'id':          'myrelease',
                    'type':        'release',
                    'time':        '2016-01-03T00:00:00+00:00',
                    'releaseTime': '2016-01-03T00:00:00+00:00',
                    'url':         'http://example.com/mc/myrelease',
                },
                {
                    'id':          'mybeta',
                    'type':        'old_beta',
                    'time':        '2016-01-02T00:00:00+00:00',
                    'releaseTime': '2016-01-02T00:00:00+00:00',
                    'url':         'http://example.com/mc/mybeta',
                },
                {
                    'id':          'myalpha',
                    'type':        'old_alpha',
                    'time':        '2016-01-01T00:00:00+00:00',
                    'releaseTime': '2016-01-01T00:00:00+00:00',
                    'url':         'http://example.com/mc/myalpha',
                },
            ],
        }

        version_info = {
            'id':        'myrelease',
            'type':      'release',
            'downloads': {
                'client': {
                    'sha1': 'deadbeef',
                    'size': 0xDEADBEEF,
                    'url':  'http://example.com/download/myrelease/client',
                },
                'server': {
                    'sha1': 'deadbeef',
                    'size': 0xDEADBEEF,
                    'url':  'http://example.com/download/myrelease/server',
                },
            },
        }

        mock_response = unittest.mock.Mock(spec = requests.Response)
        mock_response.ok = True
        mock_response.json.return_value = version_info

        requests_get.return_value = mock_response

        version = server.Server.get_version_info('myrelease')

        requests_get.assert_called_with('http://example.com/mc/myrelease')

        self.assertDictEqual(
            version_info,
            version,
            'The version metadata did not match',
        )

    @unittest.mock.patch('requests.get')
    @unittest.mock.patch('mymcadmin.server.Server.list_versions')
    def test_get_version_info_latest(self, list_versions, requests_get):
        """
        Tests that we get the info for the latest version by default
        """

        list_versions.return_value = {
            'latest': {
                'snapshot': 'mysnapshot',
                'release':  'myrelease',
            },
            'versions': [
                {
                    'id':          'myrelease',
                    'type':        'release',
                    'time':        '2016-01-03T00:00:00+00:00',
                    'releaseTime': '2016-01-03T00:00:00+00:00',
                    'url':         'http://example.com/mc/myrelease',
                },
            ],
        }

        version_info = {
            'id':        'myrelease',
            'type':      'release',
            'downloads': {
                'client': {
                    'sha1': 'deadbeef',
                    'size': 0xDEADBEEF,
                    'url':  'http://example.com/download/myrelease/client',
                },
                'server': {
                    'sha1': 'deadbeef',
                    'size': 0xDEADBEEF,
                    'url':  'http://example.com/download/myrelease/server',
                },
            },
        }

        mock_response = unittest.mock.Mock(spec = requests.Response)
        mock_response.ok = True
        mock_response.json.return_value = version_info

        requests_get.return_value = mock_response

        version = server.Server.get_version_info()

        requests_get.assert_called_with('http://example.com/mc/myrelease')

        self.assertDictEqual(
            version_info,
            version,
            'Version metadata did not match',
        )

    # pylint: disable=no-self-use
    @nose.tools.raises(errors.VersionDoesNotExist)
    @unittest.mock.patch('mymcadmin.server.Server.list_versions')
    def test_get_version_info_missing(self, list_versions):
        """
        Tests that we return the right error when the version can't be found
        """

        list_versions.return_value = {
            'latest':   {},
            'versions': [],
        }

        server.Server.get_version_info('nope')
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(errors.MyMCAdminError)
    @unittest.mock.patch('requests.get')
    @unittest.mock.patch('mymcadmin.server.Server.list_versions')
    def test_get_version_info_network(self, list_versions, requests_get):
        """
        Tests that we handle when there's a networking problem
        """

        list_versions.return_value = {
            'latest': {
                'release':  'myrelease',
                'snapshot': 'mysnapshot',
            },
            'versions': [
                {
                    'id':          'myrelease',
                    'type':        'release',
                    'time':        '2016-01-03T00:00:00+00:00',
                    'releaseTime': '2016-01-03T00:00:00+00:00',
                    'url':         'http://example.com/mc/myrelease',
                },
            ],
        }

        mock_response = unittest.mock.Mock(spec = requests.Response)
        mock_response.ok = False

        requests_get.return_value = mock_response

        server.Server.get_version_info('myrelease')
    # pylint: enable=no-self-use

    @unittest.mock.patch('requests.get')
    @unittest.mock.patch('mymcadmin.server.Server.get_version_info')
    def test_download_server_default(self, get_version_info, requests_get):
        """
        Check that we get the latest version by default
        """

        get_version_info.return_value = {
            'id': 'test',
            'downloads': {
                'server': {
                    'url': 'http://example.com/mc/test/server.jar',
                    'sha1': '943a702d06f34599aee1f8da8ef9f7296031d699',
                },
            },
        }

        mock_response = unittest.mock.Mock(spec = requests.Response)
        mock_response.ok = True
        mock_response.iter_content.return_value = io.BytesIO(
            'Hello, world!'.encode(),
        )
        requests_get.return_value = mock_response

        cwd = os.getcwd()
        os.chdir(self.root_path)
        jar_path = server.Server.download_server_jar()
        os.chdir(cwd)

        self.assertEqual(
            os.path.join(self.root_path, 'minecraft_server_test.jar'),
            jar_path,
            'Jar file path did not match expected',
        )

        get_version_info.assert_called_with(None)

        requests_get.assert_called_with(
            'http://example.com/mc/test/server.jar',
            stream = True,
        )

        self.assertEqual(
            os.path.join(self.root_path, 'minecraft_server_test.jar'),
            jar_path,
            'Jar path did not match',
        )

        self.assertTrue(
            os.path.exists(jar_path),
            'Jar was not written to disk',
        )

    @unittest.mock.patch('requests.get')
    @unittest.mock.patch('mymcadmin.server.Server.get_version_info')
    def test_download_server_jar(self, get_version_info, requests_get):
        """
        Test that we get that we can download a specific version
        """

        get_version_info.return_value = {
            'id': 'test',
            'downloads': {
                'server': {
                    'url': 'http://example.com/mc/test/server.jar',
                    'sha1': '943a702d06f34599aee1f8da8ef9f7296031d699',
                },
            },
        }

        mock_response = unittest.mock.Mock(spec = requests.Response)
        mock_response.ok = True
        mock_response.iter_content.return_value = io.BytesIO(
            'Hello, world!'.encode(),
        )

        requests_get.return_value = mock_response

        jar_path = server.Server.download_server_jar(
            'test',
            path = self.root_path,
        )

        get_version_info.assert_called_with('test')

        requests_get.assert_called_with(
            'http://example.com/mc/test/server.jar',
            stream = True,
        )

        self.assertEqual(
            os.path.join(self.root_path, 'minecraft_server_test.jar'),
            jar_path,
            'Jar path did not match',
        )

        self.assertTrue(
            os.path.exists(jar_path),
            'Jar was not written to disk',
        )

    # pylint: disable=no-self-use
    @nose.tools.raises(errors.MyMCAdminError)
    @unittest.mock.patch('requests.get')
    @unittest.mock.patch('mymcadmin.server.Server.list_versions')
    def test_download_server_version(self, list_versions, requests_get):
        """
        Test that we handle bad versions
        """

        list_versions.return_value = {'versions': []}

        mock_response = unittest.mock.Mock()
        mock_response.configure_mock(ok = False)
        requests_get.return_value = mock_response

        _ = server.Server.download_server_jar('test')
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(errors.MyMCAdminError)
    @unittest.mock.patch('requests.get')
    @unittest.mock.patch('mymcadmin.server.Server.get_version_info')
    def test_download_server_response(self, get_version_info, requests_get):
        """
        Test that we handle bad responses while downloading
        """

        get_version_info.return_value = {
            'id': 'test',
            'downloads': {
                'server': {
                    'url': 'http://example.com/mc/test/server.jar',
                    'sha1': '943a702d06f34599aee1f8da8ef9f7296031d699',
                },
            },
        }

        mock_response = unittest.mock.Mock(spec = requests.Response)
        mock_response.ok = False

        requests_get.return_value = mock_response

        server.Server.download_server_jar('test')
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(errors.MyMCAdminError)
    @unittest.mock.patch('mymcadmin.server.Server.get_version_info')
    def test_download_server_no_server(self, get_version_info):
        """
        Test that we handle when there was no server jar available for a version
        """

        get_version_info.return_value = {
            'id': 'test',
            'downloads': {},
        }

        server.Server.download_server_jar('test')
    # pylint: enable=no-self-use

    @nose.tools.raises(errors.MyMCAdminError)
    @unittest.mock.patch('requests.get')
    @unittest.mock.patch('mymcadmin.server.Server.get_version_info')
    def test_download_server_bad_sha(self, get_version_info, requests_get):
        """
        Test that we handle when the downloads file has an incorrect SHA
        """

        get_version_info.return_value = {
            'id': 'test',
            'downloads': {
                'server': {
                    'url': 'http://example.com/mc/test/server.jar',
                    'sha1': 'deadbeef',
                },
            },
        }

        mock_response = unittest.mock.Mock(spec = requests.Response)
        mock_response.ok = True
        mock_response.iter_content.return_value = io.BytesIO(
            'Hello, world!'.encode(),
        )

        requests_get.return_value = mock_response

        server.Server.download_server_jar(
            'test',
            path = self.root_path,
        )

    # pylint: disable=no-self-use
    @unittest.mock.patch('builtins.print')
    @unittest.mock.patch('fileinput.FileInput')
    def test_agree_to_eula_default(self, file_input, mock_print):
        """
        Tests that we can agree to a EULA for a server in the CWD
        """

        stream = io.StringIO(
            """#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://account.mojang.com/documents/minecraft_eula).
#Mon Jan 01 00:00:00 CST 2016
eula=FALSE""",
        )

        file_input.return_value = file_input
        file_input.__enter__.return_value = stream

        server.Server.agree_to_eula()

        file_input.assert_called_with(
            'eula.txt',
            inplace = True,
            backup  = '.bak',
        )

        mock_print.assert_has_calls(
            [
                unittest.mock.call(
                    '#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://account.mojang.com/documents/minecraft_eula).\n',
                    end = '',
                ),
                unittest.mock.call(
                    '#Mon Jan 01 00:00:00 CST 2016\n',
                    end = '',
                ),
                unittest.mock.call(
                    'eula=TRUE',
                    end = '',
                ),
            ]
        )
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @unittest.mock.patch('builtins.print')
    @unittest.mock.patch('fileinput.FileInput')
    def test_agree_to_eula(self, file_input, mock_print):
        """
        Tests that we can agree to a EULA for a server
        """

        path = 'home'

        stream = io.StringIO(
            """#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://account.mojang.com/documents/minecraft_eula).
#Mon Jan 01 00:00:00 CST 2016
eula=FALSE""",
        )

        file_input.return_value = file_input
        file_input.__enter__.return_value = stream

        server.Server.agree_to_eula(path = path)

        file_input.assert_called_with(
            os.path.join(path, 'eula.txt'),
            inplace = True,
            backup  = '.bak',
        )

        mock_print.assert_has_calls(
            [
                unittest.mock.call(
                    '#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://account.mojang.com/documents/minecraft_eula).\n',
                    end = '',
                ),
                unittest.mock.call(
                    '#Mon Jan 01 00:00:00 CST 2016\n',
                    end = '',
                ),
                unittest.mock.call(
                    'eula=TRUE',
                    end = '',
                ),
            ]
        )
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @unittest.mock.patch('json.dump')
    @unittest.mock.patch('builtins.open')
    def test_gen_default_settings_cwd(self, mock_open, json_dump):
        """
        Tests that we can generate a default settings file in the CWD
        """

        file_stream = unittest.mock.Mock(spec = io.IOBase)

        mock_open.return_value = mock_open
        mock_open.__enter__.return_value = file_stream

        server.Server.generate_default_settings()

        mock_open.assert_called_with('mymcadmin.settings', 'w')

        json_dump.assert_called_with(
            {
                'java':      'java',
                'jvm_args':  [],
                'args':      ['nogui'],
                'autostart': True,
            },
            file_stream,
            indent = '\t',
        )
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @unittest.mock.patch('json.dump')
    @unittest.mock.patch('builtins.open')
    def test_gen_default_settings(self, mock_open, json_dump):
        """
        Tests that we can generate a default settings file
        """

        path = 'home'

        file_stream = unittest.mock.Mock(spec = io.IOBase)

        mock_open.return_value = mock_open
        mock_open.__enter__.return_value = file_stream

        server.Server.generate_default_settings(path = path)

        mock_open.assert_called_with(
            os.path.join(path, 'mymcadmin.settings'),
            'w',
        )

        json_dump.assert_called_with(
            {
                'java':      'java',
                'jvm_args':  [],
                'args':      ['nogui'],
                'autostart': True,
            },
            file_stream,
            indent = '\t',
        )
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @unittest.mock.patch('json.dump')
    @unittest.mock.patch('builtins.open')
    def test_gen_default_settings_opts(self, mock_open, json_dump):
        """
        Tests that we can generate a default settings file with configured options
        """

        path = 'home'

        file_stream = unittest.mock.Mock(spec = io.IOBase)

        mock_open.return_value = mock_open
        mock_open.__enter__.return_value = file_stream

        server.Server.generate_default_settings(path = path, jar = 'mc.jar')

        mock_open.assert_called_with(
            os.path.join(path, 'mymcadmin.settings'),
            'w',
        )

        json_dump.assert_called_with(
            {
                'java':      'java',
                'jvm_args':  [],
                'jar':       'mc.jar',
                'args':      ['nogui'],
                'autostart': True,
            },
            file_stream,
            indent = '\t',
        )
    # pylint: enable=no-self-use

    def _set_server_settings(self, settings):
        settings_file = os.path.join(self.server_path, 'mymcadmin.settings')
        with open(settings_file, 'w') as settings_file:
            json.dump(settings, settings_file)

    def _touch_file(self, file_name):
        file_name = os.path.join(self.server_path, file_name)
        with open(file_name, 'w'):
            pass

        return file_name
# pylint: enable=too-many-public-methods

if __name__ == '__main__':
    unittest.main()

