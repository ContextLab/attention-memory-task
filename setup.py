
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='attention-memory-task',
    version='1.0',
    description='Attention and Memory Experiment',
    long_description='This repository contains the Psychopy code for a psychology experiment exploring the relationship between covert attention and recognition memory.',
    author='Contextual Dynamics Laboratory',
    author_email='contextualdynamics@gmail.com',
    url='https://github.com/ContextLab/attention-memory-task',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
