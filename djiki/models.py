from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from . import utils


class Versioned(object):
    def last_revision(self):
        try:
            return self.revisions.order_by("-created")[0]
        except IndexError:
            return None

    def last_change(self):
        last = self.last_revision()
        if last:
            return last.created

    def last_author(self):
        last = self.last_revision()
        if last:
            return last.author


class Revision(models.Model):
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Author"),
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    description = models.CharField(_("Description"), max_length=400, blank=True)

    class Meta:
        abstract = True
        ordering = ("-created",)


class Page(models.Model, Versioned):
    title = models.CharField(_("Title"), max_length=256)
    language = models.CharField(_("Language"), max_length=5, blank=True, default="")

    class Meta:
        ordering = ("title",)
        unique_together = ("title", "language")

    def __unicode__(self):
        if self.language:
            return "%s:%s" % (self.language, self.title)
        return self.title


class PageRevision(Revision):
    page = models.ForeignKey(Page, related_name="revisions", on_delete=models.CASCADE)
    content = models.TextField(_("Content"), blank=True)

    def __unicode__(self):
        return "%s: %s" % (self.page, self.description)


class Image(models.Model, Versioned):
    name = models.CharField(_("Name"), max_length=128, unique=True)

    class Meta:
        ordering = ("name",)

    def __unicode__(self):
        return self.name


class ImageRevision(Revision):
    image = models.ForeignKey(Image, related_name="revisions", on_delete=models.CASCADE)
    file = models.FileField(
        _("File"),
        storage=utils.get_images_storage(),
        upload_to=getattr(settings, "DJIKI_IMAGES_PATH", ""),
    )
