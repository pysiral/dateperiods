# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='setiper',
    version='0.1.0',
    description='Segments from Time (Date) Periods',
    long_description=readme,
    author='Stefan Hendricks',
    author_email='stefan.hendricks@awi.de',
    url='https://github.com/shendric/setiper',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)