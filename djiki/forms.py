from django import forms
from django.utils.translation import ugettext as _
from diff_match_patch import diff_match_patch
from . import models

class PageEditForm(forms.ModelForm):
	prev_revision = forms.ModelChoiceField(
		queryset=models.PageRevision.objects.none(),
		widget=forms.HiddenInput(),
		required=False
		)

	class Meta:
		model = models.PageRevision
		fields = ('content', 'description')

	def __init__(self, *args, **kwargs):
		self.page = kwargs.pop('page')
		super(PageEditForm, self).__init__(*args, **kwargs)
		if self.page.pk:
			self.fields['prev_revision'].queryset = self.page.revisions.all()
			self.fields['prev_revision'].initial = self.page.last_revision()

	def _rebase(self, base, latest, our):
		dmp = diff_match_patch()
		diff = dmp.patch_make(base, our)
		return dmp.patch_apply(diff, latest)

	def clean(self):
		base_revision = self.cleaned_data.get('prev_revision')
		last_revision = self.page.last_revision()
		content = self.cleaned_data['content']
		if base_revision != last_revision:
			rebase_success = False
			if base_revision:
				content, results = self._rebase(base_revision.content, last_revision.content, content)
				rebase_success = False not in results
			if not rebase_success:
				raise forms.ValidationError(
						_("Somebody else has modified this page in the meantime. It is not "\
						"possible to merge all the changes automatically. Stash your version "\
						"somewhere else and reapply with the latest revision."))
			self.cleaned_data['content'] = content
		return self.cleaned_data

	def save(self, *args, **kwargs):
		if not self.page.pk:
			self.page.save()
			self.instance.page = self.page
		super(PageEditForm, self).save(*args, **kwargs)
