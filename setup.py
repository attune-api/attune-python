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
            "requests",
            "six >= 1.9",
            "certifi",
            "python-dateutil",
            "futures",
            "pybreaker"
        ],
        packages=find_packages(),
        test_suite='tests',
        tests_require=['coverage', 'click', 'inflection', 'autopep8', 'bottle', 'coloredlogs']
)
