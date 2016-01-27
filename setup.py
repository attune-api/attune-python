# coding: utf-8

from setuptools import setup

setup(
        name='attune-client',
        version="1.0.0",
        description="Attune API Client",
        author_email="",
        url="",
        keywords=["Attune API"],
        install_requires=[
            "requests",
            "six >= 1.9",
            "certifi",
            "python-dateutil",
            "pybreaker"
        ],
        packages=['attune'],
        test_suite='tests',

        tests_require=['coverage', 'click', 'inflection', 'autopep8', 'bottle']
        # include_package_data=True
)
