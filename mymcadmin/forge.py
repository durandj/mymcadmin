"""
Forge related functions
"""

import os
import os.path
import urllib.parse

import bs4
import requests

from . import errors, utils

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

    soup = bs4.BeautifulSoup(resp.content, 'html5lib')

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

    soup = bs4.BeautifulSoup(resp.content, 'html5lib')

    downloads = soup.find(class_ = 'downloadsTable')
    releases  = downloads.find_all('tr')[1:]

    for release in releases:
        version = release.find('td').text.strip()

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

    soup = bs4.BeautifulSoup(resp.content, 'html5lib')

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

            if parent.name == 'tr':
                build = parent
                break
    else:
        build = tag

    cells = build.find_all('td', recursive = False)

    downloads = cells[-1].find('ul').find_all('li', recursive = False)
    installer = downloads[1]
    universal = downloads[-1]

    inst_url   = installer.find_all('a')[-1].get('href').strip()
    inst_sha   = installer.find_all('strong')[-1].nextSibling.strip()
    components = urllib.parse.urlparse(inst_url)
    inst_jar   = components.path.split('/')[-1]
    uni_url    = universal.find_all('a')[-1].get('href').strip()
    uni_sha    = universal.find_all('strong')[-1].nextSibling.strip()
    components = urllib.parse.urlparse(uni_url)
    uni_jar    = components.path.split('/')[-1]

    return (inst_url, inst_sha, inst_jar, uni_url, uni_sha, uni_jar)

def _get_forge_build(path, promo_tag):
    inst_url, inst_sha, inst_jar, uni_url, uni_sha, uni_jar = \
            _get_forge_build_info(promo_tag)

    inst_jar = os.path.join(path, inst_jar)
    uni_jar  = os.path.join(path, uni_jar)

    resp = requests.get(inst_url, stream = True)
    if not resp.ok:
        raise errors.ForgeError('Could not download Forge installer')

    utils.download_file(resp, inst_jar, inst_sha)

    resp = requests.get(uni_url, stream = True)
    if not resp.ok:
        raise errors.ForgeError('Could not download Forge jar')

    utils.download_file(resp, uni_jar, uni_sha)

    return (inst_jar, uni_jar)

