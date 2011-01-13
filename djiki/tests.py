# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from . import models

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
		settings.DJIKI_ALLOW_ANONYMOUS_EDITS = True
		self.user1 = User.objects.create(username='foouser')
		self.password1 = 'foopassword'
		self.user1.set_password(self.password1)
		self.user1.save()

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

	def test_new_page_creation(self):
		self._page_edit(u"User Page", content1, description1, self.user1.username, self.password1)
		self._page_edit(u"Anonymous Page", content2, description2)

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

	def test_anonymous_edits(self):
		title = u"Auth test page"
		anon_client = Client()
		user_client = Client()
		user_client.login(username='foouser', password='foopassword')
		settings.DJIKI_ALLOW_ANONYMOUS_EDITS = False
		r = anon_client.post(reverse('djiki-page-edit', kwargs={'title': title}),
				{'content': "blah", "description": ""})
		self.assertEqual(r.status_code, 403)
		r = user_client.post(reverse('djiki-page-edit', kwargs={'title': title}),
				{'content': "blah", "description": ""})
		self.assertEqual(r.status_code, 302)
		last_pk = models.Page.objects.get(title=title).last_revision().pk
		settings.DJIKI_ALLOW_ANONYMOUS_EDITS = True
		r = anon_client.post(reverse('djiki-page-edit', kwargs={'title': title}),
				{'content': "blah", "description": "", 'prev_revision': last_pk})
		self.assertEqual(r.status_code, 302)
		r = user_client.post(reverse('djiki-page-edit', kwargs={'title': title}),
				{'content': "blah", "description": "", 'prev_revision': last_pk})
		self.assertEqual(r.status_code, 302)
