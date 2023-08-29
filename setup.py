import os
import io

from setuptools import setup

DESCRIPTION = 'Python functions to facilitate the pre-processing of data for ML tasks in a clinical context.'

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

setup(
    name='cleandat',
    version='0.0.2',
    packages=['tests', 'cleandat'],
    url='https://github.com/tiadams/cleandat',
    license='MIT License',
    author='Tim Adams',
    author_email='tim-adams@gmx.net',
    description=DESCRIPTION,
    long_description=long_description,
)
