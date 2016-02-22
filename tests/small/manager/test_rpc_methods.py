"""
Tests for the JSON RPC interface handling
"""

import asyncio
import os.path
import unittest

import asynctest
import nose

from ... import utils

from mymcadmin.errors import ServerDoesNotExistError, ServerExistsError
from mymcadmin.manager import Manager
from mymcadmin.rpc.errors import JsonRpcInvalidRequestError

# pylint: disable=too-many-public-methods
class TestRpcCommands(utils.EventLoopMixin, unittest.TestCase):
    """
    Tests for the JSON RPC commands
    """

    def setUp(self):
        super(TestRpcCommands, self).setUp()

        self.host            = 'example.com'
        self.port            = 8000
        self.root            = 'root'
        self.mock_event_loop = asynctest.Mock(spec = asyncio.BaseEventLoop)

        self.manager = Manager(
            self.host,
            self.port,
            self.root,
            event_loop = self.mock_event_loop,
        )

    @unittest.mock.patch('os.path.isdir')
    @unittest.mock.patch('os.listdir')
    @utils.run_async
    async def test_list_servers(self, listdir, isdir):
        """
        Check that the listServers command lists servers
        """

        listdir.return_value = [
            'test0',
            'test1',
            'test2',
            'conf',
        ]

        isdir.side_effect = lambda p: p.startswith(os.path.join(self.root, 'test'))

        result = await self.manager.rpc_command_list_servers()

        self.assertListEqual(
            ['test0', 'test1', 'test2'],
            result,
            'The server list was not correct',
        )

    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.mkdir')
    @unittest.mock.patch('os.path.exists')
    @utils.run_async
    async def test_server_create(self, exists, mkdir, server):
        """
        Tests that the server_create method creates a new server
        """

        version = 'stable-release'
        jar     = 'minecraft-stable-release.jar'

        server_id   = 'testification'
        server_path = os.path.join(self.root, server_id)

        exists.return_value = False

        server.download_server_jar.return_value = jar

        mock_proc = asynctest.Mock(spec = asyncio.subprocess.Process)

        server.return_value = server
        server.start = asynctest.CoroutineMock()
        server.start.return_value = mock_proc

        result = await self.manager.rpc_command_server_create(
            server_id = server_id,
            version   = version,
        )

        self.assertEqual(
            server_id,
            result,
            'RPC response did not match',
        )

        mkdir.assert_called_with(server_path)

        server.download_server_jar.assert_called_with(
            version,
            path = server_path,
        )

        server.generate_default_settings.assert_called_with(
            path = server_path,
            jar  = jar,
        )

        server.assert_called_with(server_path)

        mock_proc.wait.assert_called_with()

        server.agree_to_eula.assert_called_with(
            path = server_path,
        )

    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.mkdir')
    @unittest.mock.patch('os.path.exists')
    @utils.run_async
    async def test_server_create_latest(self, exists, mkdir, server):
        """
        Tests that the server_create method gets the latest version by default
        """

        jar = 'minecraft-stable-release.jar'

        server_id   = 'testification'
        server_path = os.path.join(self.root, server_id)

        exists.return_value = False

        server.download_server_jar.return_value = jar

        mock_proc = asynctest.Mock(spec = asyncio.subprocess.Process)

        server.return_value = server
        server.start = asynctest.CoroutineMock()
        server.start.return_value = mock_proc

        result = await self.manager.rpc_command_server_create(
            server_id = server_id,
        )

        self.assertEqual(
            server_id,
            result,
            'RPC response did not match',
        )

        mkdir.assert_called_with(server_path)

        server.download_server_jar.assert_called_with(
            None,
            path = server_path,
        )

        server.generate_default_settings.assert_called_with(
            path = server_path,
            jar  = jar,
        )

        server.assert_called_with(server_path)

        mock_proc.wait.assert_called_with()

        server.agree_to_eula.assert_called_with(
            path = server_path,
        )

    @asynctest.patch('asyncio.create_subprocess_exec')
    @unittest.mock.patch('mymcadmin.forge.get_forge_for_mc_version')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.mkdir')
    @unittest.mock.patch('os.path.exists')
    @utils.run_async
    async def test_server_create_forge_any(self, exists, mkdir, server, get_forge, subproc):
        """
        Tests that we get the latest version of Forge for this server
        """

        version = 'stable-release'
        jar     = 'minecraft-stable-release.jar'

        server_id   = 'testification'
        server_path = os.path.join(self.root, server_id)

        exists.return_value = False

        server.download_server_jar.return_value = jar

        mock_proc = asynctest.Mock(spec = asyncio.subprocess.Process)

        server.return_value = server
        server.settings = {}
        server.start = asynctest.CoroutineMock()
        server.start.return_value = mock_proc

        installer = 'forge-{}-latest-installer.jar'.format(version)
        forge_jar = 'forge-{}-latest-universal.jar'.format(version)

        installer_path = os.path.join(server_path, installer)
        forge_path     = os.path.join(server_path, forge_jar)

        get_forge.return_value = (installer_path, forge_path)

        subproc.return_value = subproc

        result = await self.manager.rpc_command_server_create(
            server_id = server_id,
            version   = version,
            forge     = True,
        )

        self.assertEqual(
            server_id,
            result,
            'RPC response did not match',
        )

        mkdir.assert_called_with(server_path)

        server.download_server_jar.assert_called_with(
            version,
            path = server_path,
        )

        server.generate_default_settings.assert_called_with(
            path = server_path,
            jar  = jar,
        )

        server.assert_called_with(server_path)

        mock_proc.wait.assert_called_with()

        server.agree_to_eula.assert_called_with(
            path = server_path,
        )

        get_forge.assert_called_with(version, path = server_path)

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
            {'jar': forge_jar},
            server.settings,
            'Settings were not updated',
        )

        server.save_settings.assert_called_with()

    @asynctest.patch('asyncio.create_subprocess_exec')
    @unittest.mock.patch('mymcadmin.forge.get_forge_version')
    @unittest.mock.patch('mymcadmin.server.Server')
    @unittest.mock.patch('os.mkdir')
    @unittest.mock.patch('os.path.exists')
    @utils.run_async
    async def test_server_create_forge(self, exists, mkdir, server, get_forge, subproc):
        """
        Tests that we can get Forge for this server
        """

        version = 'stable-release'
        jar     = 'minecraft-stable-release.jar'

        server_id   = 'testification'
        server_path = os.path.join(self.root, server_id)

        exists.return_value = False

        server.download_server_jar.return_value = jar

        mock_proc = asynctest.Mock(spec = asyncio.subprocess.Process)

        server.return_value = server
        server.settings = {}
        server.start = asynctest.CoroutineMock()
        server.start.return_value = mock_proc

        installer = 'forge-{}-release-installer.jar'.format(version)
        forge_jar = 'forge-{}-release-universal.jar'.format(version)

        installer_path = os.path.join(server_path, installer)
        forge_path     = os.path.join(server_path, forge_jar)

        get_forge.return_value = (
            installer_path,
            forge_path,
        )

        subproc.return_value = subproc

        result = await self.manager.rpc_command_server_create(
            server_id = server_id,
            version   = version,
            forge     = 'release',
        )

        self.assertEqual(
            server_id,
            result,
            'RPC response did not match',
        )

        mkdir.assert_called_with(server_path)

        server.download_server_jar.assert_called_with(
            version,
            path = server_path,
        )

        server.generate_default_settings.assert_called_with(
            path = server_path,
            jar  = jar,
        )

        server.assert_called_with(server_path)

        mock_proc.wait.assert_called_with()

        server.agree_to_eula.assert_called_with(
            path = server_path,
        )

        get_forge.assert_called_with(
            version,
            'release',
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
            {'jar': forge_jar},
            server.settings,
            'Settings were not updated',
        )

        server.save_settings.assert_called_with()

    @nose.tools.raises(ServerExistsError)
    @unittest.mock.patch('os.path.exists')
    @utils.run_async
    async def test_server_create_exists(self, exists):
        """
        Tests that the server_create method checks if the server_id is in use
        """

        server_id = 'testification'

        exists.side_effect = lambda p: p.endswith(server_id)

        await self.manager.rpc_command_server_create(server_id = server_id)

    @utils.run_async
    async def test_server_restart(self):
        """
        Check that the restart command restarts a server
        """

        server_id = 'testification'

        mock_rpc_server_stop  = asynctest.CoroutineMock()
        mock_rpc_server_start = asynctest.CoroutineMock()

        self.manager.rpc_command_server_stop  = mock_rpc_server_stop
        self.manager.rpc_command_server_start = mock_rpc_server_start

        result = await self.manager.rpc_command_server_restart(
            server_id = server_id,
        )

        self.assertEqual(
            server_id,
            result,
            'RPC method did not return the right value',
        )

        mock_rpc_server_stop.assert_called_with(server_id = server_id)
        mock_rpc_server_start.assert_called_with(server_id = server_id)

    @nose.tools.raises(ServerDoesNotExistError)
    @utils.run_async
    async def test_server_restart_bad_id(self):
        """
        Check that we return an error when we give an invalid ID
        """

        await self.manager.rpc_command_server_restart(
            server_id = 'bad',
        )

    @nose.tools.raises(JsonRpcInvalidRequestError)
    @utils.run_async
    async def test_server_restart_missing(self):
        """
        Check that we require the server_id parameter
        """

        await self.manager.rpc_command_server_restart()

    @nose.tools.raises(RuntimeError)
    @utils.run_async
    async def test_server_restart_fail(self):
        """
        Check that if one of the restart steps fails we still handle it
        """

        mock_rpc_server_stop  = asynctest.CoroutineMock()
        mock_rpc_server_start = asynctest.CoroutineMock()

        mock_rpc_server_stop.side_effect = RuntimeError('Server not running')

        self.manager.rpc_command_server_stop  = mock_rpc_server_stop
        self.manager.rpc_command_server_start = mock_rpc_server_start

        await self.manager.rpc_command_server_restart(
            server_id = 'testification',
        )

    @utils.run_async
    async def test_server_restart_all(self):
        """
        Check that the restartAll command restarts all servers
        """

        server_ids = ['test0', 'test1', 'test2']

        mock_rpc_command_server_restart = asynctest.CoroutineMock()
        mock_rpc_command_server_restart.side_effect = server_ids

        self.manager.instances = {
            server_id: asynctest.Mock()
            for server_id in server_ids
        }

        self.manager.rpc_command_server_restart = mock_rpc_command_server_restart

        result = await self.manager.rpc_command_server_restart_all()

        mock_rpc_command_server_restart.assert_has_calls(
            [
                unittest.mock.call(server_id)
                for server_id in self.manager.instances.keys()
            ]
        )

        self.assertListEqual(
            server_ids,
            result.get('success'),
            'Did not return the correct list of server IDs',
        )

        self.assertListEqual(
            [],
            result.get('failure'),
            'Did not return the correct list of server IDs',
        )

    @utils.run_async
    async def test_server_restart_all_errors(self):
        """
        Check that we keep going if one of the servers errors out
        """

        server_ids = [
            'success0',
            'error0',
            'success1',
            'error1',
            'success2',
            'error2',
        ]

        self.manager.instances = {
            server_id: asynctest.Mock()
            for server_id in server_ids
        }

        def _restart_func(server_id):
            if server_id.startswith('success'):
                return server_id
            else:
                raise RuntimeError('Boom!')

        mock_server_restart = asynctest.CoroutineMock()
        mock_server_restart.side_effect = _restart_func

        self.manager.rpc_command_server_restart = mock_server_restart

        result = await self.manager.rpc_command_server_restart_all()

        self.assertListEqual(
            [
                server_id
                for server_id in self.manager.instances.keys()
                if server_id.startswith('success')
            ],
            result.get('success'),
            'The list of restarted server\'s did not match',
        )

        self.assertListEqual(
            [
                server_id
                for server_id in self.manager.instances.keys()
                if not server_id.startswith('success')
            ],
            result.get('failure'),
            'The list of failures did not match',
        )

    @asynctest.patch('mymcadmin.server.Server')
    @asynctest.patch('os.path.exists')
    @utils.run_async
    async def test_server_start(self, exists, server):
        """
        Check that the start command starts a server
        """

        exists.return_value = True
        server.return_value = server

        server_id = 'testification'

        mock_start_server_proc = asynctest.CoroutineMock()

        self.manager.start_server_proc = mock_start_server_proc

        result = await self.manager.rpc_command_server_start(
            server_id = server_id,
        )

        self.assertEqual(
            server_id,
            result,
            'Did not return server ID',
        )

        mock_start_server_proc.assert_called_with(server)

    @nose.tools.raises(ServerDoesNotExistError)
    @utils.run_async
    async def test_server_start_bad_id(self):
        """
        Check that we return an error when we give an invalid ID
        """

        await self.manager.rpc_command_server_start(
            server_id = 'bad',
        )

    @nose.tools.raises(JsonRpcInvalidRequestError)
    @utils.run_async
    async def test_server_start_missing(self):
        """
        Chewck that we require the server_id parameter
        """

        await self.manager.rpc_command_server_start()

    @utils.run_async
    async def test_server_start_all(self):
        """
        Check that the startAll command starts all servers
        """

        server_ids = ['test0', 'test1', 'test2']

        mock_list_servers = asynctest.CoroutineMock()
        mock_list_servers.return_value = server_ids

        mock_server_start = asynctest.CoroutineMock()
        mock_server_start.side_effect = lambda s: s

        self.manager.rpc_command_list_servers = mock_list_servers
        self.manager.rpc_command_server_start = mock_server_start

        result = await self.manager.rpc_command_server_start_all()

        mock_server_start.assert_has_calls(
            [
                unittest.mock.call(server_id)
                for server_id in server_ids
            ]
        )

        self.assertListEqual(
            server_ids,
            result.get('success'),
            'The list of successful servers did not match',
        )

        self.assertListEqual(
            [],
            result.get('failure'),
            'The list of failed servers did not match',
        )

    @utils.run_async
    async def test_server_start_all_started(self):
        """
        Check that we don't try and start servers that are already running
        """

        server_ids  = ['test0', 'test1', 'test2']
        running_ids = ['running0', 'running1']

        mock_list_servers = asynctest.CoroutineMock()
        mock_list_servers.return_value = server_ids + running_ids

        mock_server_start = asynctest.CoroutineMock()
        mock_server_start.side_effect = lambda s: s

        self.manager.rpc_command_list_servers = mock_list_servers
        self.manager.rpc_command_server_start = mock_server_start

        self.manager.instances = {
            server_id: asynctest.Mock()
            for server_id in running_ids
        }

        result = await self.manager.rpc_command_server_start_all()

        mock_server_start.assert_has_calls(
            [
                unittest.mock.call(server_id)
                for server_id in server_ids
            ]
        )

        self.assertListEqual(
            server_ids,
            result.get('success'),
            'The list of successful servers did not match',
        )

        self.assertListEqual(
            [],
            result.get('failure'),
            'The list of failed servers did not match',
        )

    @utils.run_async
    async def test_server_start_all_errors(self):
        """
        Check that we keep trying to start servers even if one errors out
        """

        error_ids  = ['error0', 'error1']
        server_ids = ['success0', 'success1', 'success2']

        def _start_func(server_id):
            if server_id.startswith('success'):
                return server_id
            else:
                raise RuntimeError('Boom!')

        mock_list_servers = asynctest.CoroutineMock()
        mock_list_servers.return_value = error_ids + server_ids

        mock_server_start = asynctest.CoroutineMock()
        mock_server_start.side_effect = _start_func

        self.manager.rpc_command_list_servers = mock_list_servers
        self.manager.rpc_command_server_start = mock_server_start

        result = await self.manager.rpc_command_server_start_all()

        mock_server_start.assert_has_calls(
            [
                unittest.mock.call(server_id)
                for server_id in server_ids
            ]
        )

        self.assertListEqual(
            server_ids,
            result.get('success'),
            'The list of successful servers did not match',
        )

        self.assertListEqual(
            error_ids,
            result.get('failure'),
            'The list of failed servers did not match',
        )

    @asynctest.patch('mymcadmin.server.Server')
    @asynctest.patch('os.path.exists')
    @utils.run_async
    async def test_server_stop(self, exists, server):
        """
        Check that the stop command stops a server
        """

        exists.return_value = True

        server.return_value = server

        server_id = 'testification'
        mock_proc = asynctest.Mock(spec = asyncio.subprocess.Process)

        self.manager.instances = {
            server_id: mock_proc,
        }

        result = await self.manager.rpc_command_server_stop(
            server_id = server_id,
        )

        self.assertEqual(
            server_id,
            result,
            'Did not return the server ID',
        )

        mock_proc.communicate.assert_called_with('stop'.encode())

    @nose.tools.raises(ServerDoesNotExistError)
    @utils.run_async
    async def test_server_stop_bad_id(self):
        """
        Check that we return an error when we given an invalid ID
        """

        await self.manager.rpc_command_server_stop(
            server_id = 'bad',
        )

    @nose.tools.raises(JsonRpcInvalidRequestError)
    @asynctest.patch('os.path.exists')
    @utils.run_async
    async def test_server_stop_not_running(self, exists):
        """
        Check that we throw an error when the server isn't running
        """

        exists.return_value = True

        server_id = 'testification'

        await self.manager.rpc_command_server_stop(server_id)

    @utils.run_async
    async def test_server_stop_all(self):
        """
        Check that the stopAll command stops all servers
        """

        server_ids   = ['test0', 'test1', 'test2']
        server_procs = {
            server_id: asynctest.Mock(spec = asyncio.subprocess.Process)
            for server_id in server_ids
        }

        mock_list_servers = asynctest.CoroutineMock()
        mock_list_servers.return_value = server_ids

        mock_server_stop = asynctest.CoroutineMock()
        mock_server_stop.side_effect = lambda s: s

        self.manager.instances = server_procs

        self.manager.rpc_command_list_servers = mock_list_servers
        self.manager.rpc_command_server_stop  = mock_server_stop

        result = await self.manager.rpc_command_server_stop_all()

        mock_server_stop.assert_has_calls(
            [
                unittest.mock.call(server_id)
                for server_id in self.manager.instances.keys()
            ]
        )

        self.assertListEqual(
            list(server_procs.keys()),
            result.get('success'),
            'The list of successful servers did not match',
        )

        self.assertListEqual(
            [],
            result.get('failure'),
            'The list of failed servers did not match',
        )

    @utils.run_async
    async def test_server_stop_all_errors(self):
        """
        Check that we keep going if one of the servers errors out
        """

        server_ids = ['success0', 'success1', 'success2']
        error_ids  = ['error0', 'error1']

        mock_procs = {
            server_id: asynctest.Mock(spec = asyncio.subprocess.Process)
            for server_id in (server_ids + error_ids)
        }

        def _stop_func(server_id):
            if server_id.startswith('success'):
                return server_id
            else:
                raise RuntimeError('Boom!')

        mock_server_stop = asynctest.CoroutineMock()
        mock_server_stop.side_effect = _stop_func

        self.manager.instances = mock_procs
        self.manager.rpc_command_server_stop = mock_server_stop

        result = await self.manager.rpc_command_server_stop_all()

        mock_server_stop.assert_has_calls(
            [
                unittest.mock.call(server_id)
                for server_id in mock_procs.keys()
            ]
        )

        self.assertListEqual(
            [
                server_id
                for server_id in mock_procs.keys()
                if server_id.startswith('success')
            ],
            result.get('success'),
            'The list of successful servers did not match',
        )

        self.assertListEqual(
            [
                server_id
                for server_id in mock_procs.keys()
                if not server_id.startswith('success')
            ],
            result.get('failure'),
            'The list of failed servers did not match',
        )

    @utils.run_async
    async def test_shutdown_running_proc(self):
        """
        Check that the shutdown command stops any running server instances
        """

        instance_ids = ['test0', 'test1', 'test2', 'test3']
        instances    = {}
        for server_id in instance_ids:
            mock = asynctest.Mock(spec = asyncio.subprocess.Process)

            instances[server_id] = mock

        mock_server_stop = asynctest.CoroutineMock()
        self.manager.instances = instances
        self.manager.rpc_command_server_stop = mock_server_stop
        self.manager.rpc_command_server_stop.side_effect = instance_ids

        result = await self.manager.rpc_command_shutdown()

        self.assertEqual(
            instance_ids,
            result,
            'Return message did not match',
        )

        mock_server_stop.assert_has_calls(
            [
                unittest.mock.call(server_id = server_id)
                for server_id in instances.keys()
            ]
        )
# pylint: enable=too-many-public-methods

if __name__ == '__main__':
    unittest.main()

