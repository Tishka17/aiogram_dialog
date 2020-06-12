#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))


setup(
    name='aiogram_dialog',
    description='Mini-framework for dialogs on top of aiogram',
    version='0.1',
    url='https://github.com/tishka17/aiogram_dialog',
    author='A. Tikhonov',
    author_email='17@itishka.org',
    license='Apache2',
    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3'
    ],
    packages=['aiogram_dialog'],
    install_requires=[
        'aiogram<3',
    ],
    python_requires=">=3.6",
)
