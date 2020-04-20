#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md') as f:
    readme = f.read()

setup(name='WormDemo',
      version='1.0',
      description='learn python',
      long_description=readme,
      author='wyh',
      author_email='609223770@qq.com',
      url='https://github.com/XiaoWuTongZhi/PythonWormDemo',
      packages=find_packages(),
      install_requires=requirements
     )