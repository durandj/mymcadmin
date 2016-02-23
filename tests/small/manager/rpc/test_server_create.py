"""
Tests for the server_create JSON RPC method
"""

import asyncio
import os.path
import unittest
import unittest.mock

import asynctest
import nose

from .... import utils

from mymcadmin.errors import ServerExistsError

class TestServerCreate(utils.ManagerMixin, unittest.TestCase):
    """
    Tests for the server_create JSON RPC method
    """

    @utils.run_async
    async def test_method(self):
        """
        Tests that the server_create method creates a new server
        """

        await self._do_method('stable-release')

    @utils.run_async
    async def test_method_latest(self):
        """
        Tests the server_create method uses the latest MC version by default
        """

        await self._do_method()

    @unittest.mock.patch('mymcadmin.forge.get_forge_for_mc_version')
    @utils.run_async
    async def test_method_forge_latest(self, get_forge):
        """
        Tests that we get the latest version of Forge for this version
        """

        await self._do_method(forge = True, forge_installer = get_forge)

    @unittest.mock.patch('mymcadmin.forge.get_forge_version')
    @utils.run_async
    async def test_method_forge_version(self, get_forge):
        """
        Tests that we can get a specific version of Forge
        """

        await self._do_method(
            forge           = '10.10.10.10',
            forge_installer = get_forge,
            forge_args      = ['10.10.10.10'],
        )

    @nose.tools.raises(ServerExistsError)
    @unittest.mock.patch('os.path.exists')
    @utils.run_async
    async def test_server_create_exists(self, exists):
        """
        Tests that the method checks if the server_id is already in use
        """

        server_id = 'testification'

        exists.side_effect = lambda p: p.endswith(server_id)

        await self.manager.rpc_command_server_create(server_id = server_id)

    async def _do_method(self, version = None,
                         forge = None, forge_installer = None, forge_args = None):
        server_id   = 'testification'
        server_path = os.path.join(self.root, server_id)

        with unittest.mock.patch('os.path.exists') as exists, \
             unittest.mock.patch('mymcadmin.server.Server') as server, \
             unittest.mock.patch('os.mkdir') as mkdir, \
             asynctest.patch('asyncio.create_subprocess_exec') as subproc:
            exists.return_value = False

            server.download_server_jar.return_value = 'minecraft-{}.jar'.format(
                version or 'latest',
            )

            mock_proc = asynctest.Mock(spec = asyncio.subprocess.Process)

            server.return_value = server
            server.settings = {}
            server.start = asynctest.CoroutineMock()
            server.start.return_value = mock_proc

            if forge_installer:
                installer_path = os.path.join(
                    server_path,
                    'forge-{}-latest-installer.jar'.format(version),
                )
                forge_path = os.path.join(
                    server_path,
                    'forge-{}-latest-universal.jar'.format(version),
                )

                forge_installer.return_value = (installer_path, forge_path)

                subproc.return_value = subproc

                if forge_args is None:
                    forge_args = []

            result = await self.manager.rpc_command_server_create(
                server_id = server_id,
                version   = version,
                forge     = forge,
            )

            self.assertEqual(
                server_id,
                result,
                'JSON RPC resonse did not match expected',
            )

            mkdir.assert_called_with(server_path)

            server.download_server_jar.assert_called_with(
                version,
                path = server_path,
            )

            server.assert_called_with(server_path)

            mock_proc.wait.assert_called_with()

            server.agree_to_eula.assert_called_with(
                path = server_path,
            )

            if forge_installer:
                forge_installer.assert_called_with(
                    version,
                    *forge_args,
                    path = server_path,
                )

                subproc.assert_called_with(
                    server.java,
                    '-jar',
                    installer_path,
                    '--installServer',
                    cwd    = server_path,
                    stdin  = asyncio.subprocess.PIPE,
                    stdout = asyncio.subprocess.PIPE,
                    stderr = asyncio.subprocess.PIPE,
                )

                subproc.wait.assert_called_with()

                self.assertDictEqual(
                    {'jar': os.path.basename(forge_path)},
                    server.settings,
                    'Settings were not updated',
                )

                server.save_settings.assert_called_with()

if __name__ == '__main__':
    unittest.main()

