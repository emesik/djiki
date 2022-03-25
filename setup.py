# -*- coding: utf-8 -*-
import re
from distutils.core import setup
from setuptools import find_packages

version = __import__("djiki").__version__


def flatten_repo_links(line):
    if mo := re.match(r"^\s*-e.+egg=(.+)$", line):
        return mo.groups()[0]
    return line


setup(
    name="djiki",
    version=version,
    description="Django Wiki Engine",
    url="https://github.com/emesik/djiki/",
    long_description=open("README.rst").read(),
    author="Michał Sałaban",
    author_email="michal@salaban.info",
    license="BSD-3-Clause",
    install_requires=map(
        flatten_repo_links, open("requirements.txt", "r").read().splitlines()
    ),
    tests_require=open("test_requirements.txt", "r").read().splitlines(),
    packages=find_packages(".", exclude=["tests"]),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords="django wiki engine",
    test_suite="tests",
    zip_safe=False,
)
