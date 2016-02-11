"""
Command Line Interface
"""

from .base import mymcadmin
from .commands.list import list_servers, list_versions
from .commands.start import start, start_all
from .commands.stop import stop, stop_all
from .commands.restart import restart, restart_all
from .commands.terminate import terminate, terminate_all

__all__ = [
    'mymcadmin',
]

