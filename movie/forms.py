from django import forms
from movie.models import Review, RATE_CHOICES

class RateForm(forms.ModelForm):
	text = forms.CharField(widget=forms.Textarea(attrs={'class': 'materialize-textarea'}), required=False)
	rate = forms.ChoiceField(choices=RATE_CHOICES, widget=forms.Select(), required=True)

	class Meta:
		model = Review
		fields = ('text', 'rate')

	def clean_rate(self):
		rate = self.cleaned_data.get('rate')
		if not rate:
			raise forms.ValidationError("Rating is required.")
		return rate