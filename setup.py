# coding: utf-8

from setuptools import setup

setup(
        name='attune',
        version="1.0.0",
        description="Attune API Client",
        author_email="",
        url="",
        keywords=["Attune API"],
        install_requires=["urllib3 >= 1.10", "six >= 1.9", "certifi", "python-dateutil"],
        packages=['attune'],
        test_suite='tests',
        # include_package_data=True
)
