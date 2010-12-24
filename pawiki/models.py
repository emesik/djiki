from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Page(models.Model):
	title = models.CharField(_("Title"), max_length=256, unique=True)
	rendered_content = models.TextField(_("Rendered content"), blank=True)

	class Meta:
		ordering = ('title',)

	def __unicode__(self):
		return self.title

	def last_revision(self):
		return self.revisions.order_by('-created')[0]

	def last_change(self):
		return self.last_revision().created

	def last_author(self):
		return self.last_revision().author


class PageRevision(models.Model):
	page = models.ForeignKey(Page, related_name='revisions')
	content = models.TextField(_("Content"), blank=True)
	created = models.DateTimeField(_("Created"), auto_now_add=True)
	author = models.ForeignKey(User, label=_("Author"))
	description = models.CharField(_("Description"), max_length=400, blank=True)

	class Meta:
		ordering = ('-created',)

	def __unicode__(self):
		return u"%s: %s" % (self.page, self.description)

def render_content(sender, instance=None, **kwargs):
	# XXX: add real parser here
	instance.page.rendered_content = instance.content
	instance.page.save()
models.signals.post_save.connect(render_content, sender=PageRevision)
