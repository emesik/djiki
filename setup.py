# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

version = __import__('djiki').__version__

setup(
	name = 'djiki',
	version = version,
	description = 'Django Wiki Application',
	url = 'https://github.com/emesik/djiki/',
	long_description = open('README.rst').read(),
	author = 'Michał Sałaban',
	author_email = 'michal@salaban.info',
	install_requires = [
		'django',
		'diff_match_patch',
	],
	packages = find_packages(),
	include_package_data = True,
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Internet :: WWW/HTTP',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
	],
	zip_safe = False,
)
