"""
Forge related functions
"""

import hashlib
import os
import os.path
import urllib.parse

import bs4
import requests

from . import errors

FORGE_MC_VERSION_URL = \
    'http://files.minecraftforge.net/maven/net/minecraftforge/forge/index_{}.html'

def get_forge_mc_versions():
    """
    Get all the versions of Minecraft that are supported by Forge.
    """

    def _versions_filter(tag):
        if 'li-version-list-current' in tag.get('class', []):
            return True

        return tag.name == 'a'

    resp = requests.get('http://files.minecraftforge.net/')
    if not resp.ok:
        raise errors.ForgeError('Forge servers could not be reached')

    soup = bs4.BeautifulSoup(resp.content, 'html.parser')

    version_elem = soup.find(class_ = 'versions')
    versions     = version_elem.find_all(_versions_filter)

    return [
        v.text.strip()
        for v in versions
    ]

def get_forge_version(mc_version, forge_version, path = None):
    """
    Download Forge by a specific Forge version. Optionally
    you can specify a specific location to store the download
    otherwise defaults to the current directory.
    """

    minecraft_versions = get_forge_mc_versions()
    if mc_version not in minecraft_versions:
        raise errors.ForgeError(
            'Version {} of Minecraft is not supported by Forge',
            mc_version,
        )

    if path is None:
        path = os.getcwd()

    url = FORGE_MC_VERSION_URL.format(
        urllib.parse.quote(mc_version),
    )

    resp = requests.get(url)
    if not resp.ok:
        raise errors.ForgeError(
            'Could not retrieve the Forge download page for version {}',
            mc_version,
        )

    soup = bs4.BeautifulSoup(resp.content, 'html.parser')

    downloads = soup.find(class_ = 'downloadsTable')
    releases  = downloads.find_all('tr')[1:]
    print(releases)

    for release in releases:
        version, _, _, _ = _get_forge_build_info(release)
        print(version)

        if version == forge_version:
            return _get_forge_build(path, release)

    raise errors.ForgeError(
        'Could not find Forge version {}',
        forge_version,
    )

def get_forge_for_mc_version(version_id, path = None):
    """
    Download Forge for a specific Minecraft version. This will
    be the latest recommended release for the given Minecraft
    version. Optionally you can specify a specific location to
    store the download otherwise defaults to the current
    directory.
    """

    minecraft_versions = get_forge_mc_versions()
    if version_id not in minecraft_versions:
        raise errors.ForgeError(
            'Version {} of Minecraft is not supported by Forge',
            version_id,
        )

    if path is None:
        path = os.getcwd()

    url = FORGE_MC_VERSION_URL.format(
        urllib.parse.quote(version_id),
    )

    resp = requests.get(url)
    if not resp.ok:
        raise errors.ForgeError(
            'Could not retrieve the Forge download page for version {}',
            version_id,
        )

    soup = bs4.BeautifulSoup(resp.content, 'html.parser')

    downloads = soup.find(class_ = 'downloadsTable')

    # Try getting the recommended build
    build = downloads.find(class_ = 'promo-RECOMMENDED')
    if build is not None:
        return _get_forge_build(path, build)

    # Try getting the latest build
    build = downloads.find(class_ = 'promo-LATEST')
    if build is not None:
        return _get_forge_build(path, build)

    raise errors.ForgeError('No builds viable Forge version found')

def _get_forge_build_info(tag):
    if tag.name != 'tr':
        for parent in tag.parents:
            if parent is None:
                raise errors.ForgeError('Could not found build information')

            if parent.name != 'tr':
                continue

            build = parent
    else:
        build = tag

    cells = build.find_all('td', recursive = False)

    downloads = cells[-1]
    info      = downloads.find(class_ = 'info')

    version    = cells[0].text.strip()
    url        = info.find('a').get('href').strip()
    sha        = info.find_all('strong')[-1].nextSibling.strip()
    components = urllib.parse.urlparse(url)
    jar_file   = components.path.split('/')[-1]

    return (version, url, sha, jar_file)

def _get_forge_build(path, promo_tag):
    _, url, sha, jar_file = _get_forge_build_info(promo_tag)

    jar_path = os.path.join(path, jar_file)

    resp = requests.get(url, stream = True)
    if not resp.ok:
        raise errors.ForgeError('Could not download Forge jar')

    file_sha = hashlib.sha1()
    with open(jar_path, 'wb') as file_handle:
        for chunk in resp.iter_content(chunk_size = 1024):
            # Ignore keep-alive chunks
            if not chunk:
                continue

            file_handle.write(chunk)
            file_sha.update(chunk)

    file_sha = file_sha.hexdigest()
    if file_sha != sha:
        raise errors.ForgeError(
            'Downloaded Forge jar\'s SHA1 did not match expected' +
            ' Was {}, should be {}',
            file_sha,
            sha,
        )

    return jar_path

