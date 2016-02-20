"""
Error and exception types
"""

class MyMCAdminError(Exception):
    """
    A general MyMCAdmin error
    """

    def __init__(self, message, *args, **kwargs):
        self.message = message.format(*args, **kwargs)

        super(MyMCAdminError, self).__init__(self.message)

class ConfigurationError(MyMCAdminError):
    """
    An error in a configuration of MyMCAdmin
    """

class ManagerError(MyMCAdminError):
    """
    An error with the management process
    """

class ServerDoesNotExistError(ManagerError):
    """
    Raised when a requested server does not exist
    """

    def __init__(self, server_id):
        super(ServerDoesNotExistError, self).__init__(
            'Server {} does not exist',
            server_id,
        )

class ServerExistsError(ManagerError):
    """
    Raised when creating a server and the server ID is already in use
    """

    def __init__(self, server_id):
        super(ServerExistsError, self).__init__(
            'Server {} already exists',
            server_id,
        )

class ServerError(MyMCAdminError):
    """
    An error with the Minecraft server
    """

class ServerCreationError(ServerError):
    """
    An error with creating a new Minecraft server
    """

class ServerSettingsError(ServerError):
    """
    An error in the MyMCAdmin settings for the server
    """

class VersionDoesNotExistError(ManagerError):
    """
    Version does not exist
    """

    def __init__(self, version):
        super(VersionDoesNotExistError, self).__init__(
            'Version {} does not exist',
            version,
        )

class ForgeError(MyMCAdminError):
    """
    A general error when working with Forge
    """

