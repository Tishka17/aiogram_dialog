  #!/usr/bin/env python3
# -*- coding: utf-8 -*-
from os import path

from setuptools import setup, find_packages

this_directory = path.abspath(path.dirname(__file__))


setup(
    name='aiogram_dialog',
    description='Mini-framework for dialogs on top of aiogram',
    version='1.0.0',
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
    packages=find_packages(include=['aiogram_dialog', 'aiogram_dialog.*']),
    install_requires=[
        'aiogram>=2.12,<3',
        'babel~=2.9.0',
        'cachetools==4.*',
        'jinja2',
        'magic_filter',
    ],
    extras_require={
        "tools": [
            "diagrams"
        ]
    },
    package_data={
        'aiogram_dialog.tools': ['calculator.png'],
        'aiogram_dialog.tools.templates': ['message.html'],
    },
    python_requires=">=3.8",
)
