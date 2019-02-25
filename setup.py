#!/usr/bin/env python
# pylint: disable=C0111,C0103,import-error,no-name-in-module
from setuptools import setup
from setuptools import find_packages

import versioneer
from sphinx.setup_command import BuildDoc

version = versioneer.get_version()
cmdclass = versioneer.get_cmdclass()
cmdclass['build_sphinx'] = BuildDoc
name = 'biblishelf'


setup(
    name=name,
    version=version,
    install_requires=[
        "cement",
    ],
    packages=find_packages('src'),
    package_dir={
        "": "src",
    },
    package_data={
        "": [],
    },
    description="a file ",
    author="xingci xu",
    author_email="x007007007@hotmail.com",
    license='MIT license',
    url='',
    classifiers=[
        'Programming Language :: Python',
    ],
    entry_points={
        'console_scripts': [
            'bib = bib.enterpoint:bib',
        ],
    },
    cmdclass=cmdclass,
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', '.'.join(version.split('.')[:2])),
            'release': ('setup.py', version),
        },
    },
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest',
        'coverage',
        'pytest-cov'
    ],
)
