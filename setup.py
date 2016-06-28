#!/usr/bin/env python
"""
wsgiwatch
---------

Synchronously rebuild assets for a WSGI application in response to source file changes.
"""

from distutils.core import setup

setup(
  name = 'wsgiwatch',
  version = '0.1.1',
  description = 'Synchronously rebuild assets for a WSGI application in response to source file changes',
  author = 'David P. Kendal',
  author_email = 'pypi@dpk.io',
  url = 'https://github.com/dpk/wsgiwatch',
  py_modules = ['wsgiwatch'],
  keywords = ['build', 'wsgi', 'assets'],
  classifiers = [
    'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
    'Topic :: Software Development :: Build Tools',
    'Programming Language :: Python :: 3.4'
  ]
)
