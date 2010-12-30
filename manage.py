#!/usr/bin/env python
import os
from django.core.management import setup_environ, ManagementUtility
try:
	import settings # Assumed to be in the same directory.
except ImportError:
	import sys
	sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
	sys.exit(1)

if __name__ == "__main__":
	setup_environ(settings, original_settings_path=os.environ.get('DJANGO_SETTINGS_MODULE', 'settings'))
	utility = ManagementUtility(None)
	utility.execute()
