#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='Extract Knack',
    version='0.0.2',
    packages=find_packages(),
    install_requires=[
        'click==6.7',
        'requests==2.18.4',
        'stringcase==1.2.0',
        'boto3==1.9.145'
    ],
    entry_points={
        'console_scripts': [
            'extract-knack=extract_knack:main',
        ],
    }
)
