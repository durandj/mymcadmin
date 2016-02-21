"""
Utilities common to the entire system
"""

import hashlib
import logging
import pwd

from . import errors

def setup_logging():
    """
    Setup the logging system
    """

    logging.basicConfig(
        datefmt = '%Y-%m-%d %H:%M:%S',
        format  = '%(asctime)s %(levelname)s %(message)s',
        level   = logging.INFO,
    )

def get_user_home(user = None):
    """
    Get the home directory for a user. Defaults to current user
    """

    home_func = pwd.getpwuid if isinstance(user, int) else pwd.getpwnam

    return home_func(user).pw_dir

def download_file(resp, path, sha):
    """
    Download a file from an HTTP request and save it at the specified path
    """

    file_sha = hashlib.sha1()
    try:
        with open(path, 'wb') as file_handle:
            for chunk in resp.iter_content(chunk_size = 1024):
                # Ignore keep-alive chunks
                if not chunk:
                    continue

                file_handle.write(chunk)
                file_sha.update(chunk)
    except IOError as ex:
        raise errors.DownloadError(
            'There was a problem saving a file: {}',
            str(ex),
        )

    file_sha = file_sha.hexdigest()
    if file_sha != sha:
        raise errors.DownloadError(
            'Downloaded file\'s SHA1 did not match expected' +
            ' Was {}, should be {}',
            file_sha,
            sha,
        )

