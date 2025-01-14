import setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pridepy',
    version='0.0.2',
    author="PRIDE Team",
    author_email="pride-report@ebi.ac.uk",
    description="Python Client library for PRIDE Rest API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anilkmg/pridepy",
    keywords="PRIDE python client REST API",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
        'ratelimit',
        'click',
        'pytest',
        'setuptools',
        'plotly'
    ],
    entry_points='''
        [console_scripts]
        pridepy=pridepy.commandline:main
    ''',
    test_suite="tests",
)
