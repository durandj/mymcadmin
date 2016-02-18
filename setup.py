"""
MyMCAdmin installer
"""

import setuptools

with open('requirements.txt', 'r') as req_file:
    REQUIREMENTS = req_file.readlines()

setuptools.setup(
    name             = 'mymcadmin',
    version          = '0.1.0',
    packages         = setuptools.find_packages(),
    install_requires = REQUIREMENTS,
    entry_points     = """
        [console_scripts]
        mymcadmin=mymcadmin.cli:mymcadmin
    """,
)

