from django import forms
from django.utils.translation import ugettext as _
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
			last = self.page.last_revision()
			self.fields['prev_revision'].queryset = models.PageRevision.objects.filter(pk=last.pk)
			self.fields['prev_revision'].initial = last

	def clean(self):
		last = self.cleaned_data['prev_revision']
		if last != self.page.last_revision():
			# TODO: try merging
			raise forms.ValidationError(_("Somebody else has modified this page in the meantime. "\
					"Stash your changes somewhere else and reapply wit the latest revision."))
		return self.cleaned_data

	def save(self, *args, **kwargs):
		if not self.page.pk:
			self.page.save()
			self.instance.page = self.page
		super(PageEditForm, self).save(*args, **kwargs)
