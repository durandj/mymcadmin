"""
Tests for the class methods of the Server class
"""

import copy
import io
import os
import unittest
import unittest.mock

import nose
import requests

from mymcadmin.errors import MyMCAdminError, VersionDoesNotExistError
from mymcadmin.server import Server

class TestServerClassMethods(unittest.TestCase):
    """
    Tests for the class methods of the Server class
    """

    @unittest.mock.patch('requests.get')
    def test_list_versions_default(self, requests_get):
        """
        Tests that the list_versions method returns correctly
        """

        mock_response = unittest.mock.Mock(spec = requests.Response)
        mock_response.ok = True
        mock_response.json.return_value = copy.deepcopy(SAMPLE_VERSIONS)

        requests_get.return_value = mock_response

        versions = Server.list_versions()

        requests_get.assert_called_with(
            'https://launchermeta.mojang.com/mc/game/version_manifest.json',
        )

        self.assertDictEqual(
            SAMPLE_VERSIONS,
            versions,
            'Version data did not match expected',
        )

    @unittest.mock.patch('requests.get')
    def test_list_versions_filter(self, requests_get):
        """
        Tests that we can filter out versions by release type
        """

        mock_response = unittest.mock.Mock(spec = requests.Response)
        requests_get.return_value = mock_response

        for i in range(16):
            requests_get.reset_mock()
            mock_response.ok = True
            mock_response.json.return_value = copy.deepcopy(SAMPLE_VERSIONS)

            snapshots = i & 0b1000 > 0
            releases  = i & 0b0100 > 0
            betas     = i & 0b0010 > 0
            alphas    = i & 0b0001 > 0

            versions = Server.list_versions(
                snapshots = snapshots,
                releases  = releases,
                betas     = betas,
                alphas    = alphas,
            )

            remaining_types = set(
                [
                    v['type']
                    for v in versions['versions']
                ]
            )

            if not snapshots:
                self.assertNotIn(
                    'latest',
                    versions['latest'],
                    'Snapshots not filtered from latest',
                )

                self.assertNotIn(
                    'snapshot',
                    remaining_types,
                    'Snapshots were not filtered out',
                )

            if not releases:
                self.assertNotIn(
                    'release',
                    versions['latest'],
                    'Release not filtered from latest',
                )

                self.assertNotIn(
                    'release',
                    remaining_types,
                    'Releases were not filtered out',
                )

            if not betas:
                self.assertNotIn(
                    'old_beta',
                    remaining_types,
                    'Betas were not filtered out',
                )

            if not alphas:
                self.assertNotIn(
                    'old_alpha',
                    remaining_types,
                    'Alphas were not filtered out',
                )

    # pylint: disable=no-self-use
    @nose.tools.raises(MyMCAdminError)
    @unittest.mock.patch('requests.get')
    def test_list_versions_network(self, requests_get):
        """
        Tests that we can handle networking errors
        """

        mock_response = unittest.mock.Mock(spec = requests.Response)
        mock_response.ok = False

        requests_get.return_value = mock_response

        Server.list_versions()
    # pylint: enable=no-self-use

    @unittest.mock.patch('requests.get')
    @unittest.mock.patch('mymcadmin.server.Server.list_versions')
    def test_get_version_info(self, list_versions, requests_get):
        """
        Tests that we can get the information about a specific server version
        """

        list_versions.return_value = copy.deepcopy(SAMPLE_VERSIONS)

        version_info = SAMPLE_VERSION

        mock_response = unittest.mock.Mock(spec = requests.Response)
        mock_response.ok = True
        mock_response.json.return_value = version_info

        requests_get.return_value = mock_response

        version = Server.get_version_info('my_release')

        requests_get.assert_called_with('http://example.com/mc/my_release.json')

        self.assertDictEqual(
            version_info,
            version,
            'The version metadata did not match the expected',
        )

    @unittest.mock.patch('requests.get')
    @unittest.mock.patch('mymcadmin.server.Server.list_versions')
    def test_get_version_info_latest(self, list_versions, requests_get):
        """
        Tests that we can get the infor for the latest server version by default
        """

        list_versions.return_value = SAMPLE_VERSIONS

        version_info = SAMPLE_VERSION

        mock_response = unittest.mock.Mock(spec = requests.Response)
        mock_response.ok = True
        mock_response.json.return_value = version_info

        requests_get.return_value = mock_response

        version = Server.get_version_info()

        requests_get.assert_called_with('http://example.com/mc/my_release.json')

        self.assertDictEqual(
            version_info,
            version,
            'Version metadata did not match expected',
        )

    # pylint: disable=no-self-use
    @nose.tools.raises(VersionDoesNotExistError)
    @unittest.mock.patch('mymcadmin.server.Server.list_versions')
    def test_get_version_info_missing(self, list_versions):
        """
        Tests that we handle when the version can't be found
        """

        list_versions.return_value = {
            'latest':   {},
            'versions': [],
        }

        Server.get_version_info('nope')
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(MyMCAdminError)
    @unittest.mock.patch('requests.get')
    @unittest.mock.patch('mymcadmin.server.Server.list_versions')
    def test_get_version_info_network(self, list_versions, requests_get):
        """
        Tests that we handle when there's a networking problem
        """

        list_versions.return_value = copy.deepcopy(SAMPLE_VERSIONS)

        mock_response = unittest.mock.Mock(spec = requests.Response)
        mock_response.ok = False

        requests_get.return_value = mock_response

        Server.get_version_info('my_release')
    # pylint: enable=no-self-use

    def test_download_server_default(self):
        """
        Tests that we can get the latest version by default
        """

        self._do_server_download_test(None, None)

    def test_download_server_jar(self):
        """
        Tests that we can get a jar for a specific server version
        """

        self._do_server_download_test('my_release', 'home')

    # pylint: disable=no-self-use
    @nose.tools.raises(MyMCAdminError)
    @unittest.mock.patch('requests.get')
    @unittest.mock.patch('mymcadmin.server.Server.get_version_info')
    def test_download_server_response(self, get_version_info, requests_get):
        """
        Tests that we handle bad responses while downloading
        """

        get_version_info.return_value = SAMPLE_VERSION

        mock_response = unittest.mock.Mock(spec = requests.Response)
        mock_response.ok = False

        requests_get.return_value = mock_response

        Server.download_server_jar('my_release')
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(MyMCAdminError)
    @unittest.mock.patch('mymcadmin.server.Server.get_version_info')
    def test_download_server_no_server(self, get_version_info):
        """
        Tests that we handle then there's no server download for this version
        """

        get_version_info.return_value = {
            'id':        'test',
            'downloads': {},
        }

        Server.download_server_jar('test')
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(MyMCAdminError)
    @unittest.mock.patch('builtins.open')
    @unittest.mock.patch('requests.get')
    @unittest.mock.patch('mymcadmin.server.Server.get_version_info')
    def test_download_server_bad_sha(self, get_version_info, requests_get, mock_open):
        """
        Tests that we handle when the jar download has an incorrect SHA
        """

        get_version_info.return_value = {
            'id':        'test',
            'downloads': {
                'server': {
                    'url':  'http://example.com/mc/test/server',
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

        file_stream = io.BytesIO()

        mock_open.return_value = mock_open
        mock_open.__enter__.return_value = file_stream

        Server.download_server_jar(
            'test',
            path = 'home',
        )
    # pylint: enable=no-self-use

    def test_agree_to_eula_default(self):
        """
        Tests that we can agree to a EULA for a server in the CWD
        """

        self._do_agree_to_eula()

    def test_agree_to_eula(self):
        """
        Tests that we can agree to a EULA for a server
        """

        self._do_agree_to_eula('home')

    def test_gen_default_settings_cwd(self):
        """
        Tests that we can generate a default settings file in the CWD
        """

        self._do_generate_default_settings()

    def test_gen_default_settings(self):
        """
        Tests that we can generate a default settings file
        """

        self._do_generate_default_settings('home')

    def test_gen_default_settings_opts(self):
        """
        Tests that we can generate a default settings file with config options
        """

        self._do_generate_default_settings(
            path = 'home',
            jar  = 'mc.jar',
        )

    def _do_server_download_test(self, target, path):
        root = path if path is not None else os.getcwd()

        with unittest.mock.patch('mymcadmin.server.Server.get_version_info') as get_version_info, \
             unittest.mock.patch('requests.get') as requests_get, \
             unittest.mock.patch('builtins.open') as mock_open:
            get_version_info.return_value = SAMPLE_VERSION

            mock_response = unittest.mock.Mock(spec = requests.Response)
            mock_response.ok = True
            mock_response.iter_content.return_value = io.BytesIO(
                'Hello, world!'.encode(),
            )

            requests_get.return_value = mock_response

            file_stream = io.BytesIO()

            mock_open.return_value = mock_open
            mock_open.__enter__.return_value = file_stream

            jar_path = Server.download_server_jar(
                version_id = target,
                path       = path,
            )

            self.assertEqual(
                os.path.join(root, 'minecraft_server_my_release.jar'),
                jar_path,
                'Jar file path did not match expected',
            )

            mock_open.assert_called_with(
                jar_path,
                'wb',
            )

            get_version_info.assert_called_with(target)

            requests_get.assert_called_with(
                'http://example.com/download/myrelease/server',
                stream = True,
            )

    # pylint: disable=no-self-use
    def _do_agree_to_eula(self, path = None):
        expected_path = 'eula.txt' if path is None else os.path.join(path, 'eula.txt')

        # pylint: disable=line-too-long
        stream = io.StringIO(
            """#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://account.mojang.com/documents/minecraft_eula).
#Mon Jan 01 00:00:00 CST 2016
eula=FALSE""",
        )
        # pylint: enable=line-too-long

        with unittest.mock.patch('fileinput.FileInput') as file_input, \
             unittest.mock.patch('builtins.print') as mock_print:
            file_input.return_value = file_input
            file_input.__enter__.return_value = stream

            Server.agree_to_eula(path = path)

            file_input.assert_called_with(
                expected_path,
                inplace = True,
                backup  = '.bak',
            )

            # pylint: disable=line-too-long
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
            # pylint: enable=line-too-long

    # pylint: disable=no-self-use
    def _do_generate_default_settings(self, path = None, jar = None):
        if path is None:
            expected_path = 'mymcadmin.settings'
        else:
            expected_path = os.path.join(path, 'mymcadmin.settings')

        expected_settings = {
            'java':      'java',
            'jvm_args':  [],
            'args':      ['nogui'],
            'autostart': True,
        }

        if jar is not None:
            expected_settings['jar'] = jar

        with unittest.mock.patch('builtins.open') as mock_open, \
             unittest.mock.patch('json.dump') as json_dump:
            file_stream = unittest.mock.Mock(spec = io.IOBase)

            mock_open.return_value = mock_open
            mock_open.__enter__.return_value = file_stream

            Server.generate_default_settings(
                path = path,
                jar  = jar,
            )

            mock_open.assert_called_with(expected_path, 'w')

            json_dump.assert_called_with(
                expected_settings,
                file_stream,
                indent = '\t',
            )
    # pylint: enable=no-self-use

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

SAMPLE_VERSION = {
    'id':        'my_release',
    'type':      'release',
    'downloads': {
        'client': {
            'sha1': 'deadbeef',
            'size': 0xDEADBEEF,
            'url':  'http://example.com/download/myrelease/client',
        },
        'server': {
            'sha1': '943a702d06f34599aee1f8da8ef9f7296031d699',
            'size': 0xDEADBEEF,
            'url':  'http://example.com/download/myrelease/server',
        },
    },
}

if __name__ == '__main__':
    unittest.main()

