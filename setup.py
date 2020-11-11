# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='dateperiods',
    version='1.0.1',
    description='Managing date-based periods in python',
    long_description=readme,
    author='Stefan Hendricks',
    author_email='stefan.hendricks@awi.de',
    url='https://github.com/shendric/dateperiods',
    license=license,
    packages=find_packages(exclude=('tests')),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8']
    )
