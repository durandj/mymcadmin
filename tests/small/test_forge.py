"""
Tests for the Forge related functions
"""

import io
import os
import os.path
import unittest
import unittest.mock

import nose
import requests

from mymcadmin.errors import ForgeError
from mymcadmin.forge import (
    get_forge_for_mc_version,
    get_forge_mc_versions,
    get_forge_version,
)

class TestForge(unittest.TestCase):
    """
    Tests for the Forge related functions
    """

    @unittest.mock.patch('requests.get')
    def test_get_forge_mc_versions(self, requests_get):
        """
        Tests that we can retrieve a list of all the MC versions Forge supports
        """

        mock_response = unittest.mock.Mock(spec = requests.Response)
        mock_response.ok      = True
        mock_response.content = """
<html>
  <body>
    <div class="versions">
      <ul class="links">
        <li class="li-version-list">
          <span>1.8</span>
          <div class="versions-info">
            <ul class="text">
              <li class="li-version-list-current">
                1.8.9
              </li>
              <li>
                <a href="http://example.com/1.8.8">
                  1.8.8
                </a>
              </li>
            </ul>
          </div>
        </li>
        <li class="li-version-list">
          <span>1.7</span>
          <div class="versions-info">
            <ul class="text">
              <li>
                <a href="http://example.com/1.7.10">
                  1.7.10
                </a>
              </li>
              <li>
                <a href="http://example.com/1.7.2">
                  1.7.2
                </a>
              </li>
            </ul>
          </div>
        </li>
      </ul>
    </div>
  </body>
</html>
        """

        requests_get.return_value = mock_response

        versions = get_forge_mc_versions()

        requests_get.assert_called_with(
            'http://files.minecraftforge.net/',
        )

        self.assertListEqual(
            [
                '1.8.9',
                '1.8.8',
                '1.7.10',
                '1.7.2',
            ],
            versions,
            'Version list did not match expected',
        )

    # pylint: disable=no-self-use
    @nose.tools.raises(ForgeError)
    @unittest.mock.patch('requests.get')
    def test_forge_mc_versions_network(self, requests_get):
        """
        Tests that we handle when we can't get to the Forge site
        """

        mock_response = unittest.mock.Mock(spec = requests.Response)
        mock_response.ok = False

        requests_get.return_value = mock_response

        get_forge_mc_versions()
    # pylint: enable=no-self-use

    def test_get_forge_version(self):
        """
        Tests that we can get the correct Forge jar by version
        """

        self._do_forge_version()

    def test_get_forge_version_path(self):
        """
        Tests that we can get the right Forge version and put it at the path
        """

        self._do_forge_version('home')

    # pylint: disable=no-self-use
    @nose.tools.raises(ForgeError)
    @unittest.mock.patch('mymcadmin.forge.get_forge_mc_versions')
    def test_get_forge_ver_bad_mc(self, versions):
        """
        Tests that we handle when the given Minecraft version is bad
        """

        versions.return_value = []

        get_forge_version('1.8.9', '10.10.10.10')
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(ForgeError)
    @unittest.mock.patch('requests.get')
    @unittest.mock.patch('mymcadmin.forge.get_forge_mc_versions')
    def test_get_forge_ver_bad_forge(self, versions, requests_get):
        """
        Tests that we handle when the given Forge version is bad
        """

        versions.return_value = ['1.8.9']

        mock_response = unittest.mock.Mock(spec = requests.Response)
        mock_response.ok      = True
        mock_response.content = SAMPLE_DOWNLOADS_PAGE.format('LATEST')

        requests_get.return_value = mock_response

        get_forge_version('1.8.9', '20.20.20.20')
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(ForgeError)
    @unittest.mock.patch('requests.get')
    @unittest.mock.patch('mymcadmin.forge.get_forge_mc_versions')
    def test_get_forge_ver_network1(self, versions, requests_get):
        """
        Tests that we handle when theres a network problem getting the list page
        """

        versions.return_value = ['1.8.9']

        mock_response = unittest.mock.Mock(spec = requests.Response)
        mock_response.ok = False

        requests_get.return_value = mock_response

        get_forge_version('1.8.9', '20.20.20.20')
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(ForgeError)
    @unittest.mock.patch('requests.get')
    @unittest.mock.patch('mymcadmin.forge.get_forge_mc_versions')
    def test_get_forge_ver_network2(self, versions, requests_get):
        """
        Tests that we handle when theres a network problem getting the jar
        """

        versions.return_value = ['1.8.9']

        mock_list_response = unittest.mock.Mock(spec = requests.Response)
        mock_list_response.ok      = True
        mock_list_response.content = SAMPLE_DOWNLOADS_PAGE.format('LATEST')

        mock_jar_response = unittest.mock.Mock(spec = requests.Response)
        mock_jar_response.ok = False

        requests_get.side_effect = [
            mock_list_response,
            mock_jar_response,
        ]

        get_forge_version('1.8.9', '10.10.10.10')
    # pylint: enable=no-self-use

    def test_get_forge_for_mc_latest(self):
        """
        Tests that we can get the latest Forge jar by Minecraft version
        """

        self._do_forge_for_mc('LATEST')

    def test_get_forge_for_mc_recommend(self):
        """
        Tests that we can get the recommended Forge jar by Minecraft version
        """

        self._do_forge_for_mc('RECOMMENDED')

    def test_get_forge_for_mc_path(self):
        """
        Tests that we can get the correct Forge version and put it at the path
        """

        self._do_forge_for_mc('LATEST', 'home')

    # pylint: disable=no-self-use
    @nose.tools.raises(ForgeError)
    @unittest.mock.patch('requests.get')
    def test_get_forge_for_mc_network1(self, requests_get):
        """
        Tests that we handle when there's a networking problem getting the list
        """

        mock_response = unittest.mock.Mock(spec = requests.Response)
        mock_response.ok = False

        requests_get.return_value = mock_response

        get_forge_for_mc_version('1.8.9')
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(ForgeError)
    @unittest.mock.patch('requests.get')
    @unittest.mock.patch('mymcadmin.forge.get_forge_mc_versions')
    def test_get_forge_for_mc_network2(self, versions, requests_get):
        """
        Tests that we handle when there's a networking problem getting the jar
        """

        versions.return_value = ['1.8.9']

        mock_list_response = unittest.mock.Mock(spec = requests.Response)
        mock_list_response.ok      = True
        mock_list_response.content = SAMPLE_DOWNLOADS_PAGE.format('LATEST')

        mock_jar_response = unittest.mock.Mock(spec = requests.Response)
        mock_jar_response.ok = False

        requests_get.side_effect = [
            mock_list_response,
            mock_jar_response,
        ]

        get_forge_for_mc_version('1.8.9')
    # pylint: enable=no-self-use

    # pylint: disable=no-self-use
    @nose.tools.raises(ForgeError)
    @unittest.mock.patch('mymcadmin.forge.get_forge_mc_versions')
    def test_get_forge_for_mc_bad_ver(self, forge_versions):
        """
        Tests that we handle when an unsupported MC version is given
        """

        forge_versions.return_value = []

        get_forge_for_mc_version('1.8.9')
    # pylint: disable=no-self-use

    def _do_forge_for_mc(self, release, path = None):
        root       = path if path is not None else os.getcwd()
        version_id = '1.8.9'

        with unittest.mock.patch('mymcadmin.forge.get_forge_mc_versions') as forge_versions, \
             unittest.mock.patch('requests.get') as requests_get, \
             unittest.mock.patch('mymcadmin.utils.download_file') as download_file:
            forge_versions.return_value = ['1.8.9']

            mock_version_response = unittest.mock.Mock(spec = requests.Response)
            mock_version_response.ok      = True
            mock_version_response.content = SAMPLE_DOWNLOADS_PAGE.format(release)

            mock_inst_jar_response = unittest.mock.Mock(spec = requests.Response)
            mock_inst_jar_response.ok = True

            mock_uni_jar_response = unittest.mock.Mock(spec = requests.Response)
            mock_uni_jar_response.ok = True

            requests_get.side_effect = [
                mock_version_response,
                mock_inst_jar_response,
                mock_uni_jar_response,
            ]

            inst_jar_path, uni_jar_path = get_forge_for_mc_version(
                version_id,
                path = path,
            )

            self.assertEqual(
                os.path.join(root, 'forge-1.8.9-10.10.10.10-installer.jar'),
                inst_jar_path,
                'Installer path did not match expected',
            )

            self.assertEqual(
                os.path.join(root, 'forge-1.8.9-10.10.10.10-universal.jar'),
                uni_jar_path,
                'Jar path did not match expected',
            )

            # pylint: disable=line-too-long
            requests_get.assert_has_calls(
                [
                    unittest.mock.call(
                        'http://files.minecraftforge.net/maven/net/minecraftforge/forge/index_1.8.9.html',
                    ),
                    unittest.mock.call(
                        'http://example.com/10.10.10.10/forge-1.8.9-10.10.10.10-installer.jar',
                        stream = True,
                    ),
                    unittest.mock.call(
                        'http://example.com/10.10.10.10/forge-1.8.9-10.10.10.10-universal.jar',
                        stream = True,
                    ),
                ]
            )
            # pylint: enable=line-too-long

        download_file.assert_has_calls(
            [
                unittest.mock.call(
                    mock_inst_jar_response,
                    inst_jar_path,
                    '943a702d06f34599aee1f8da8ef9f7296031d699',
                ),
                unittest.mock.call(
                    mock_uni_jar_response,
                    uni_jar_path,
                    '943a702d06f34599aee1f8da8ef9f7296031d699',
                )
            ]
        )

    def _do_forge_version(self, path = None):
        root       = path if path is not None else os.getcwd()
        version_id = '1.8.9'

        with unittest.mock.patch('mymcadmin.forge.get_forge_mc_versions') as forge_versions, \
             unittest.mock.patch('requests.get') as requests_get, \
             unittest.mock.patch('mymcadmin.utils.download_file') as download_file:
            forge_versions.return_value = ['1.8.9']

            mock_version_response = unittest.mock.Mock(spec = requests.Response)
            mock_version_response.ok      = True
            mock_version_response.content = SAMPLE_DOWNLOADS_PAGE.format('LATEST')

            mock_inst_jar_response = unittest.mock.Mock(spec = requests.Response)
            mock_inst_jar_response.ok = True

            mock_uni_jar_response = unittest.mock.Mock(spec = requests.Response)
            mock_uni_jar_response.ok = True

            requests_get.side_effect = [
                mock_version_response,
                mock_inst_jar_response,
                mock_uni_jar_response,
            ]

            inst_jar, uni_jar = get_forge_version(
                version_id,
                '10.10.10.10',
                path = path,
            )

            self.assertEqual(
                os.path.join(root, 'forge-1.8.9-10.10.10.10-installer.jar'),
                inst_jar,
                'Installer path did not match expected',
            )

            self.assertEqual(
                os.path.join(root, 'forge-1.8.9-10.10.10.10-universal.jar'),
                uni_jar,
                'Jar path did not match expected',
            )

            # pylint: disable=line-too-long
            requests_get.assert_has_calls(
                [
                    unittest.mock.call(
                        'http://files.minecraftforge.net/maven/net/minecraftforge/forge/index_1.8.9.html',
                    ),
                    unittest.mock.call(
                        'http://example.com/10.10.10.10/forge-1.8.9-10.10.10.10-installer.jar',
                        stream = True,
                    ),
                    unittest.mock.call(
                        'http://example.com/10.10.10.10/forge-1.8.9-10.10.10.10-universal.jar',
                        stream = True,
                    ),
                ]
            )
            # pylint: enable=line-too-long

            download_file.assert_has_calls(
                [
                    unittest.mock.call(
                        mock_inst_jar_response,
                        inst_jar,
                        '943a702d06f34599aee1f8da8ef9f7296031d699',
                    ),
                    unittest.mock.call(
                        mock_uni_jar_response,
                        uni_jar,
                        '943a702d06f34599aee1f8da8ef9f7296031d699',
                    ),
                ]
            )

SAMPLE_DOWNLOADS_PAGE = """
<html>
  <body>
    <table class="downloadsTable">
      <tbody>
        <tr>
          <th>Version</th>
          <th>Time</th>
          <th>Downloads</th>
        </tr>
        <tr>
          <td>
            <ul>
              <li>
                10.10.10.10
                <a class="info-link tooltipstered" data-toggle="popup" style="cursor:default;">
                  <i class="fa fa-start promo-{}"></i>
                </a>
              </li>
            </ul>
          </td>
          <td>01/01/2016 00:00:00 AM</td>
          <td>
            <ul>
              <li>
                Changelog
              </li>
              <li>
                <a href="http://example.com/10.10.10.10/forge-1.8.9-10.10.10.10-installer.jar">
                  <i class="fa fa-save classifier-installer"></i>
                  Installer
                </a>
                <div class="info">
                  <strong>MD5:</strong>
                  deadbeef
                  <strong>SHA1:</strong>
                  943a702d06f34599aee1f8da8ef9f7296031d699
                  <br>
                  <a href="http://example.com/10.10.10.10/forge-1.8.9-10.10.10.10-installer.jar">
                    (Direct Download)
                  </a>
                </div>
              </li>
              <li>
                Installer-win
              </li>
              <li>
                MDK
              </li>
              <li>
                <a href="http://example.com/10.10.10.10/forge-1.8.9-10.10.10.10-universal.jar">
                  <i class="fa fa-save classifier-universal"></i>
                  Universal
                </a>
                <div class="info">
                  <strong>MD5:</strong>
                  1b0aed33d51dbcacbe6440fa8998f9e6<br>
                  <strong>SHA1:</strong>
                  943a702d06f34599aee1f8da8ef9f7296031d699
                  <br>
                  <a href="http://example.com/10.10.10.10/forge-1.8.9-10.10.10.10-universal.jar">
                    (Direct Download)
                  </a>
                </div>
              </li>
            </ul>
          </td>
        </tr>
      </tbody>
    </table>
  </body>
</html>
"""

if __name__ == '__main__':
    unittest.main()

