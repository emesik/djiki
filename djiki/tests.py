# -*- coding: utf-8 -*-
from django.conf import settings
try:
	from django.contrib.auth import get_user_model
	User = get_user_model()
except ImportError:
	# django < 1.5
	from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from . import models
from .auth.base import UnrestrictedAccess

content1 = u"""
= Hello world! =

This is a simple test page.
"""
description1 = u"Initial page version"
content2 = content1 + """
== Subsection ==

This page has a subsection.
"""
description2 = u"Subsection added"
content3 = """
= Hello world! =

Some text added here.
This is a simple test page.

== Subsection ==

This page has a subsection.
"""
description3 = u"Added some text"


class SimpleTest(TestCase):
	def setUp(self):
		settings.DJIKI_SPACES_AS_UNDERSCORES = False
		settings.DJIKI_AUTHORIZATION_BACKEND = 'djiki.auth.base.UnrestrictedAccess'
		self.user = User.objects.create(username='foouser')
		user_password = 'foopassword'
		self.user.set_password(user_password)
		self.user.save()
		self.admin = User.objects.create(username='admin', is_superuser=True)
		admin_password = 'adminpassword'
		self.admin.set_password(admin_password)
		self.admin.save()
		self.anon_client = Client()
		self.user_client = Client()
		self.admin_client = Client()
		self.user_client.login(username='foouser', password=user_password)
		self.admin_client.login(username='admin', password=admin_password)

	def _page_edit(self, title, content, description='', username=None, password=None):
		client = Client()
		if username:
			client.login(username=username, password=password)
		rev_count = models.PageRevision.objects.filter(page__title=title).count()
		try:
			prev_rev = models.PageRevision.objects.filter(page__title=title).order_by('-created')[0].pk
		except IndexError:
			prev_rev = ''
		r = client.get(reverse('djiki-page-edit', kwargs={'title': title}))
		self.assertEqual(r.status_code, 200)
		r = client.post(reverse('djiki-page-edit', kwargs={'title': title}),
				{'content': content, 'description': description, 'prev_revision': prev_rev})
		self.assertEqual(r.status_code, 302)
		p = models.Page.objects.get(title=title)
		self.assertEqual(p.revisions.count(), rev_count + 1)
		self.assertEqual(p.last_revision().content, content)
		if username:
			self.assertEqual(p.last_revision().author.username, username)
		else:
			self.assertEqual(p.last_revision().author, None)
		self.assertEqual(p.last_revision().description, description)

	def test_subsequent_edits(self):
		title = u"Test page"
		self._page_edit(title, content1, description1)
		self._page_edit(title, content2, description2)
		self._page_edit(title, content3, description3)

	def test_underscores(self):
		title_raw  = u"Another test page, let's see..."
		title_xlat = u"Another_test_page,_let's_see..."
		self._page_edit(title_raw, "test content", "")
		client = Client()
		r = client.get(reverse('djiki-page-view', kwargs={'title': title_raw}))
		self.assertEqual(200, r.status_code)
		r = client.get(reverse('djiki-page-view', kwargs={'title': title_xlat}))
		self.assertEqual(404, r.status_code)
		settings.DJIKI_SPACES_AS_UNDERSCORES = True
		r = client.get(reverse('djiki-page-view', kwargs={'title': title_raw}))
		self.assertEqual(302, r.status_code)
		r = client.get(reverse('djiki-page-view', kwargs={'title': title_xlat}))
		self.assertEqual(200, r.status_code)

	def test_edit_crash(self):
		title = u"Crash page"
		self._page_edit(title, content1, description1)
		p = models.Page.objects.get(title=title)
		first_revision = p.last_revision()
		self._page_edit(title, content2, description2)
		client = Client()
		# attempt to save a new version with an outdated base revision
		r = client.post(reverse('djiki-page-edit', kwargs={'title': title}),
				{'content': content3, 'description': description3, 'prev_revision': first_revision.pk})
		if r.status_code == 200:
			print r.content
		self.assertEqual(r.status_code, 302)

	def test_edits(self):
		title = u"Auth test page"
		settings.DJIKI_AUTHORIZATION_BACKEND = 'djiki.auth.base.UnrestrictedAccess'
		# anonymous create
		r = self.anon_client.post(reverse('djiki-page-edit', kwargs={'title': title}),
				{'content': "blah", "description": ""})
		self.assertEqual(r.status_code, 302)
		# anonymous edit
		last_pk = models.Page.objects.get(title=title).last_revision().pk
		r = self.anon_client.post(reverse('djiki-page-edit', kwargs={'title': title}),
				{'content': "blah", "description": "", 'prev_revision': last_pk})
		self.assertEqual(r.status_code, 302)
		# authenticated edit
		last_pk = models.Page.objects.get(title=title).last_revision().pk
		r = self.user_client.post(reverse('djiki-page-edit', kwargs={'title': title}),
				{'content': "blah", "description": "", 'prev_revision': last_pk})
		self.assertEqual(r.status_code, 302)
		# admin edit
		last_pk = models.Page.objects.get(title=title).last_revision().pk
		r = self.admin_client.post(reverse('djiki-page-edit', kwargs={'title': title}),
				{'content': "blah", "description": "", 'prev_revision': last_pk})
		self.assertEqual(r.status_code, 302)

		settings.DJIKI_AUTHORIZATION_BACKEND = 'djiki.auth.base.OnlyAuthenticatedEdits'
		# anonymous create
		r = self.anon_client.post(reverse('djiki-page-edit', kwargs={'title': u'Other title 1'}),
				{'content': "blah", "description": ""})
		self.assertEqual(r.status_code, 403)
		# anonymous edit
		last_pk = models.Page.objects.get(title=title).last_revision().pk
		r = self.anon_client.post(reverse('djiki-page-edit', kwargs={'title': title}),
				{'content': "blah", "description": "", 'prev_revision': last_pk})
		self.assertEqual(r.status_code, 403)
		# authenticated create
		r = self.user_client.post(reverse('djiki-page-edit', kwargs={'title': u'Other title 2'}),
				{'content': "blah", "description": ""})
		self.assertEqual(r.status_code, 302)
		# authenticated edit
		r = self.user_client.post(reverse('djiki-page-edit', kwargs={'title': title}),
				{'content': "blah", "description": "", 'prev_revision': last_pk})
		self.assertEqual(r.status_code, 302)
		# admin edit
		last_pk = models.Page.objects.get(title=title).last_revision().pk
		r = self.admin_client.post(reverse('djiki-page-edit', kwargs={'title': title}),
				{'content': "blah", "description": "", 'prev_revision': last_pk})
		self.assertEqual(r.status_code, 302)

		settings.DJIKI_AUTHORIZATION_BACKEND = 'djiki.auth.base.OnlyAdminEdits'
		# anonymous create
		r = self.anon_client.post(reverse('djiki-page-edit', kwargs={'title': u'Other title 3'}),
				{'content': "blah", "description": ""})
		self.assertEqual(r.status_code, 403)
		# anonymous edit
		last_pk = models.Page.objects.get(title=title).last_revision().pk
		r = self.anon_client.post(reverse('djiki-page-edit', kwargs={'title': title}),
				{'content': "blah", "description": "", 'prev_revision': last_pk})
		self.assertEqual(r.status_code, 403)
		# authenticated create
		r = self.user_client.post(reverse('djiki-page-edit', kwargs={'title': u'Other title 4'}),
				{'content': "blah", "description": ""})
		self.assertEqual(r.status_code, 403)
		# authenticated edit
		r = self.user_client.post(reverse('djiki-page-edit', kwargs={'title': title}),
				{'content': "blah", "description": "", 'prev_revision': last_pk})
		self.assertEqual(r.status_code, 403)
		# admin create
		r = self.admin_client.post(reverse('djiki-page-edit', kwargs={'title': u'Other title 5'}),
				{'content': "blah", "description": ""})
		self.assertEqual(r.status_code, 302)
		# admin edit
		r = self.admin_client.post(reverse('djiki-page-edit', kwargs={'title': title}),
				{'content': "blah", "description": "", 'prev_revision': last_pk})
		self.assertEqual(r.status_code, 302)

	def test_history_view(self):
		title = u"History page"
		self._page_edit(title, "foo bar", "baz")

		settings.DJIKI_AUTHORIZATION_BACKEND = 'djiki.auth.base.UnrestrictedAccess'
		r = self.anon_client.get(reverse('djiki-page-history', kwargs={'title': title}))
		self.assertEqual(r.status_code, 200)

		class NoHistoryView(UnrestrictedAccess):
			def can_view_history(self, request, target):
				return False

		settings.DJIKI_AUTHORIZATION_BACKEND = NoHistoryView
		r = self.anon_client.get(reverse('djiki-page-history', kwargs={'title': title}))
		self.assertEqual(r.status_code, 403)
