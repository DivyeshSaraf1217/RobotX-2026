from setuptools import find_packages
from setuptools import setup

setup(
    name='robotx_cv',
    version='0.1.0',
    packages=find_packages(
        include=('robotx_cv', 'robotx_cv.*')),
)
