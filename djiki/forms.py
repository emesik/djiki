from django import forms
from django.conf import settings
from django.utils.translation import gettext as _
from diff_match_patch import diff_match_patch
from . import models, utils


class PageEditForm(forms.ModelForm):
    prev_revision = forms.ModelChoiceField(
        queryset=models.PageRevision.objects.none(),
        widget=forms.HiddenInput(),
        required=False,
    )
    language = forms.ChoiceField(choices=settings.LANGUAGES, widget=forms.HiddenInput)

    class Meta:
        model = models.PageRevision
        fields = ("content", "description")

    def __init__(self, *args, **kwargs):
        self.page = kwargs.pop("page")
        super(PageEditForm, self).__init__(*args, **kwargs)
        if self.page.pk:
            self.fields["prev_revision"].queryset = self.page.revisions.all()
            self.fields["prev_revision"].initial = self.page.last_revision()
        self.fields["language"].initial = self.page.language

    def _rebase(self, base, latest, our):
        dmp = diff_match_patch()
        diff = dmp.patch_make(base, our)
        return dmp.patch_apply(diff, latest)

    def clean(self):
        base_revision = self.cleaned_data.get("prev_revision")
        last_revision = self.page.last_revision()
        content = self.cleaned_data["content"]
        if base_revision != last_revision:
            rebase_success = False
            if base_revision:
                content, results = self._rebase(
                    base_revision.content, last_revision.content, content
                )
                rebase_success = False not in results
            if not rebase_success:
                raise forms.ValidationError(
                    _(
                        "Somebody else has modified this page in the meantime. It is not "
                        "possible to merge all the changes automatically. Stash your version "
                        "somewhere else and reapply with the latest revision."
                    )
                )
            self.cleaned_data["content"] = content
        return self.cleaned_data

    def save(self, *args, **kwargs):
        if not self.page.pk:
            self.page.save()
            self.instance.page = self.page
        super(PageEditForm, self).save(*args, **kwargs)


class ImageUploadForm(forms.ModelForm):
    prev_revision = forms.ModelChoiceField(
        queryset=models.ImageRevision.objects.none(),
        widget=forms.HiddenInput(),
        required=False,
    )

    class Meta:
        model = models.ImageRevision
        fields = ("file", "description")

    def __init__(self, *args, **kwargs):
        self.image = kwargs.pop("image")
        super(ImageUploadForm, self).__init__(*args, **kwargs)
        if self.image.pk:
            self.fields["prev_revision"].queryset = self.image.revisions.all()
            self.fields["prev_revision"].initial = self.image.last_revision()

    def clean(self):
        base_revision = self.cleaned_data.get("prev_revision")
        last_revision = self.image.last_revision()
        if base_revision != last_revision:
            raise forms.ValidationError(
                _(
                    "Somebody else has modified this image in the meantime. Please "
                    "review these changes before uploading your version."
                )
            )
        return self.cleaned_data

    def save(self, *args, **kwargs):
        if not self.image.pk:
            self.image.save()
        self.instance.image = self.image
        super(ImageUploadForm, self).save(*args, **kwargs)


class NewImageUploadForm(forms.ModelForm):
    name = forms.CharField(
        label=_("Name"),
        max_length=128,
        required=False,
        help_text=_(
            "If you leave it empty, the original name of the uploaded file will be used."
        ),
    )

    class Meta:
        model = models.ImageRevision
        fields = ("name", "file", "description")

    def _get_name(self):
        name = self.cleaned_data["name"]
        if not name:
            name = unicode(self.cleaned_data["file"])
        return name

    def clean(self):
        if models.Image.objects.filter(
            name=utils.deurlize_title(self._get_name())
        ).exists():
            raise forms.ValidationError(
                _(
                    "An image of the same name already exists. Please enter "
                    "different name."
                )
            )
        return self.cleaned_data

    def save(self, *args, **kwargs):
        image = models.Image(name=utils.deurlize_title(self._get_name()))
        image.save()
        self.instance.image = image
        super(NewImageUploadForm, self).save(*args, **kwargs)
