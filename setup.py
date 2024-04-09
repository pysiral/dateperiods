# -*- coding: utf-8 -*-

import pathlib
from setuptools import setup, find_packages

readme = pathlib.Path('README.md').read_text()
license_txt = pathlib.Path('LICENSE').read_text()

setup(
    name='dateperiods',
    version='1.2.0',
    description='Periods between dates in python',
    long_description=readme,
    author='Stefan Hendricks',
    author_email='stefan.hendricks@awi.de',
    url='https://github.com/shendric/dateperiods',
    license=license_txt,
    packages=find_packages(exclude=('tests',)),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ]
    )
