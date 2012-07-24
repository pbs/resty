#!/usr/bin/env python
from setuptools import setup, find_packages

dependencies = [
    'requests',
]

setup(
    name='resty',
    version='0.1',
    description='PBS API consumer library',
    author='TPG CORE Services Team',
    author_email='tpg-pbs-coreservices@threepillarglobal.com',
    url='https://github.com/pbs/resty',
    packages=find_packages(),
    include_package_data=True,
    install_requires=dependencies,
)
