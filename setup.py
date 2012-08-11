#!/usr/bin/env python

from setuptools import setup

setup(
    name='MCP',
    version='0.1',
    author='Keegan Carruthers-Smith',
    author_email='keegan.csmith@gmail.com',
    url='https://github.com/keegancsmith/MCP',
    license='LICENSE',
    py_modules=['mcp'],
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
    entry_points={'console_scripts': ['mcp = mcp:main']},
)
