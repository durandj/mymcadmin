"""
Minecraft server instance representation
"""

import asyncio
import glob
import hashlib
import json
import logging
import os
import os.path
import re
import shlex

import requests

from . import errors

class Server(object):
    """
    A Minecraft server instance
    """

    PROPERTIES_FILE       = 'server.properties'
    PROPERTIES_REGEX      = re.compile(r'^([a-zA-Z0-9\-]+)=([^#]*)( *#.*)?$')
    PROPERTIES_BOOL_REGEX = re.compile(r'^(true|false)$', re.IGNORECASE)
    PROPERTIES_INT_REGEX  = re.compile(r'^([0-9]+)$')
    SETTINGS_FILE         = 'mymcadmin.settings'
    VERSION_URL           = 'https://launchermeta.mojang.com/mc/game/version_manifest.json'

    def __init__(self, path):
        """
        Create an instance of the Minecraft server at the given file path.
        This does not create a new Minecraft server, instead its used to model
        a server.
        """

        self._path            = path
        self._cache           = {}
        self._properties_file = os.path.join(path, Server.PROPERTIES_FILE)
        self._properties      = None
        self._settings_file   = os.path.join(path, Server.SETTINGS_FILE)
        self._settings        = None

    @property
    def path(self):
        """
        Get the file path of the server
        """

        return self._path

    @property
    def server_id(self):
        """
        Get the server server ID
        """

        return os.path.basename(self._path)

    @property
    def java(self):
        """
        Get the Java binary to use
        """

        if 'java' not in self._cache:
            self._cache['java'] = self.settings.get('java', 'java')

        return self._cache['java']

    @property
    def jar(self):
        """
        Get the server Jar to run
        """

        if 'jar' not in self._cache and 'jar' in self.settings:
            self._cache['jar'] = self.settings['jar']

        if 'jar' not in self._cache:
            jars = glob.glob(os.path.join(self._path, '*.jar'))

            if len(jars) == 0:
                raise errors.ServerError('No server jar could be found')
            elif len(jars) > 1:
                raise errors.ServerError('Unable to determine server jar')

            self._cache['jar'] = jars[0]

        return self._cache['jar']

    @property
    def command_args(self):
        """
        Get the command line arguments for starting the server
        """

        command_args = [self.java]
        command_args += [
            shlex.quote(arg)
            for arg in self.settings.get('jvm_args', [])
        ]
        command_args += ['-jar', shlex.quote(self.jar)]
        command_args += [
            shlex.quote(arg)
            for arg in self.settings.get('args', [])
        ]

        return command_args

    @property
    def properties(self):
        """
        Get the Minecraft server properties defined in the server.properties
        file
        """

        if not self._properties:
            try:
                with open(self._properties_file, 'r') as props_file:
                    props = props_file.readlines()
            except FileNotFoundError:
                raise errors.ServerError(
                    'Server properties file could not be found. ' +
                    'Try starting the server first to generate one.'
                )

            self._properties = {}
            for line in props:
                match = Server.PROPERTIES_REGEX.match(line.strip())
                if not match:
                    continue

                name, value, _ = match.groups()
                self._properties[name] = Server._convert_property_value(value)

        return self._properties

    @property
    def settings(self):
        """
        Get the MyMCAdmin settings for this server that are defined in the
        mymcadmin.settings file
        """

        if not self._settings:
            try:
                with open(self._settings_file, 'r') as settings_file:
                    self._settings = json.load(settings_file)
            except FileNotFoundError:
                raise errors.ServerSettingsError(
                    'Server settings file (mymcadmin.settings) could not be ' +
                    'found.'
                )

        return self._settings

    def create(self, name, version = None):
        """
        Create the Minecraft server
        """

        versions = Server.list_versions()
        if version is None:
            version = versions['latest']['release']

        versions = [
            v for v in versions
            if v['id'] == version
        ]

        if len(versions) == 0:
            raise errors.ServerCreationError('Invalid Minecraft version')

        version = versions[0]

        version_info = requests.get(version['url'])
        if not version_info.ok:
            raise errors.ServerCreationError('Unable to retrieve version info')

        version_info = version_info.json()

    def start(self):
        """
        Start the Minecraft server
        """

        command_args = self.command_args
        logging.info('Starting server with: %s', command_args)

        return asyncio.create_subprocess_exec(
            *command_args,
            cwd    = self.path,
            stdin  = asyncio.subprocess.PIPE,
            stdout = asyncio.subprocess.PIPE,
            stderr = asyncio.subprocess.PIPE,
        )

    @classmethod
    def list_versions(
            cls,
            snapshots = True,
            releases  = True,
            betas     = True,
            alphas    = True):
        """
        List all available server versions
        """

        def type_filter(version_filter, versions):
            """
            Filter out versions of a specific type
            """

            return [
                v for v in versions
                if v.get('type') != version_filter
            ]

        resp = requests.get(cls.VERSION_URL)

        if not resp.ok:
            raise errors.MyMCAdminError('Unable to retrieve version list')

        versions     = resp.json()
        latest       = versions['latest']
        all_versions = versions['versions']

        if not snapshots:
            del latest['snapshot']
            all_versions = type_filter('snapshot', all_versions)

        if not releases:
            del latest['release']
            all_versions = type_filter('release', all_versions)

        if not betas:
            all_versions = type_filter('old_beta', all_versions)

        if not alphas:
            all_versions = type_filter('old_alpha', all_versions)

        return {
            'latest':   latest,
            'versions': all_versions,
        }

    @classmethod
    def download_server_jar(cls, version_id, path = None):
        """
        Download a server Jar based on its version ID
        """

        if path is None:
            path = os.getcwd()

        jar_path = os.path.join(
            path,
            'minecraft_server_{}.jar'.format(version_id),
        )

        versions = cls.list_versions()['versions']
        versions = [v for v in versions if v['id'] == version_id]

        if len(versions) == 0:
            raise errors.MyMCAdminError('Could not find version {}', version_id)

        version   = versions[0]
        downloads = version['downloads']

        if 'server' not in downloads:
            raise errors.MyMCAdminError('Version does not support multiplayer')

        dl_info = downloads['server']
        dl_url  = dl_info['url']
        dl_sha1 = dl_info['sha1']

        jar_resp = requests.get(dl_url, stream = True)
        if not jar_resp.ok:
            raise errors.MyMCAdminError('Unable to download server jar')

        sha1 = hashlib.sha1()
        with open(jar_path, 'wb') as jar_file:
            for chunk in jar_resp.iter_content(chunk_size = 1024):
                # Ignore keep-alive chunks
                if not chunk:
                    continue

                jar_file.write(chunk)
                sha1.update(chunk)

        jar_sha1 = sha1.hexdigest()
        if jar_sha1 != dl_sha1:
            raise errors.MyMCAdminError(
                'Downloaded server jar\'s sha1 did not match the expected value. ' +
                'Was {}, should be {}.',
                jar_sha1,
                dl_sha1,
            )

        return jar_path

    @classmethod
    def _convert_property_value(cls, value):
        """
        Convert a value from the properties value to its correct type. IE
        integers are converted to ints, true/false to boolean, etc.
        """

        if value == '':
            return None
        elif cls.PROPERTIES_BOOL_REGEX.match(value):
            return value.lower() == 'true'
        elif cls.PROPERTIES_INT_REGEX.match(value):
            return int(value)
        else:
            return value
>>>>>>> master

