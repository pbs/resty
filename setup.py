#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='resty',
    version='0.1.1',
    description='PBS API consumer library',
    author='TPG CORE Services Team',
    author_email='tpg-pbs-coreservices@threepillarglobal.com',
    url='https://github.com/pbs/resty',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['requests'],
    setup_requires=['unittest2'],
    test_suite='unittest2.collector',
)
