#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

dist = setup(
    name='im_util',
    version='0.1.2',
    description='Utilities for the im package library; used by most of them',
    author='Emlyn O\'Regan',
    author_email='emlynoregan@gmail.com',
    url='https://github.com/emlynoregan/im_util',
    license='../LICENSE.txt',
    packages=['im_util'],
    install_requires=['cloudpickle'],
    long_description=open('../README.md').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Distributed Computing',
    ]
)
