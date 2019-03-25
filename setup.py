import os
import sys

from setuptools import setup, find_packages

py_version = sys.version_info[:2]
if py_version < (3, 3):
    raise Exception("aiopyramid requires Python >= 3.3.")


here = os.path.abspath(os.path.dirname(__file__))
NAME = 'GethWS'
with open(os.path.join(here, 'README.rst')) as readme:
    README = readme.read()
with open(os.path.join(here, 'CHANGES.rst')) as changes:
    CHANGES = changes.read()

requires = [
    'pyramid==1.9.2',
    'aiopyramid',
    'web3==4.5.0',
    'eth-utils==1.0.2',
    'eth-keyfile==0.5.0',
    'eth-abi==1.1.1',
    'eth-keys==0.2.0b3',
    'websockets==5.0.1',
    'aiohttp==2.3.10',
    'aiohttp-wsgi==0.7.1',
    'uwsgi'

]

dev_require = [
  'bumpversion',
  'pytest',
  'pytest-cov'
]

setup(
    name=NAME,
    version='0.1.0',
    description='GethWS',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='',
    author_email='',
    url='',
    keywords='aiopyramid asyncio web wsgi pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'dev': dev_require,
    },
    test_suite=NAME,
    install_requires=requires,
    entry_points="""\
    [paste.app_factory]
    main = gethws:main
    """,
)
