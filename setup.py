#!/usr/bin/env python

from distutils.core import setup

setup(
    name='MCP',
    version='0.1',
    author='Keegan Carruthers-Smith',
    author_email='keegan.csmith@gmail.com',
    url='https://bitbucket.org/keegan_csmith/mcp',
    license='LICENSE',
    scripts=['mcp.py'],
    description='A program to orchestrate Entellect Challenge bot matches.',
    long_description=file('README.rst').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
)
