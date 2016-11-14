# coding: utf-8

from setuptools import setup, find_packages

setup(
        name='attune-python',
        version="1.0.3",
        description="Attune.co API Client",
        author_email="python@attune.co",
        author='Attune.co',
        url="https://github.com/attune-api/attune-python",
        keywords=["Attune API"],
        install_requires=[
            "requests == 1.2.0",
            "six == 1.4.1",
            "certifi",
            "python-dateutil <= 2.3",
            "futures",
            "pybreaker"
        ],
        packages=find_packages(),
        test_suite='tests',
        tests_require=['coverage', 'click', 'inflection', 'autopep8', 'bottle', 'coloredlogs', 'profilestats']
)
