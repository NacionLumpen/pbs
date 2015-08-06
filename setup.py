"""
Describes the setup of pbs
"""
from setuptools import setup

setup(name='pbs',
      author='Luis Osa',
      author_email='luis.osa.gdc@gmail.com',
      version='0.1.0',
      packages=['pbs'],
      tests_require=[
          'nose',
          'coverage',
          'mock',
          'funcsigs'],
      test_suite='nose.collector',
      install_requires=[
          'requests',
          'pyquery'],
      entry_points={
          'console_scripts': ['pbs=pbs.main:main']})
