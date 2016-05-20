# -*- coding: utf-8 -*-

# imports ####################################################################

from django.forms import ModelForm, BaseFormSet, Form, widgets
from polls.models import VotingPoll, Candidate, DateCandidate, PreferenceModel, INDEFINED_VALUE, Options
from django import forms


class VotingPollForm(ModelForm):
    class Meta:
        model = VotingPoll
        exclude = ['admin']
        widgets = {
            'closing_date': widgets.DateInput(attrs={'class': 'datepicker'}),
        }

    """def save(self, user=None):
        voting_poll = super(VotingPollForm, self).save(commit=False)
        if user:
            voting_poll.admin = user
        voting_poll.save()
        return voting_poll"""


class OptionsForm(ModelForm):
    class Meta:
        model = Options
        exclude = ['poll']


class CandidateForm(ModelForm):
    class Meta:
        model = Candidate
        exclude = ['poll']


class DateCandidateForm(Form):
    dates = forms.CharField(max_length=300, required=True)

    def clean_dates(self):
        dates = self.cleaned_data["dates"].split(',')
        return dates


class BaseCandidateFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        candidates = []
        for form in self.forms:
            candidate = form.cleaned_data.get("candidate")
            if candidate in candidates:
                raise forms.ValidationError("candidates must be distinct.")
            candidates.append(candidate)


class VotingForm(forms.Form):
    def __init__(self, candidates, preference_model, *args, **kwargs):
        super(VotingForm, self).__init__(*args, **kwargs)

        self.fields['nickname'] = forms.CharField(max_length=250, required=True, label='Nickname')
        for c in candidates:
            self.fields['value' + str(c.id)] = forms.ChoiceField(widget=forms.RadioSelect,
                                                                 choices=preference_model.zipPreference(),
                                                                 required=True, label=c.candidate
                                                                 )
            self.candidates = candidates

    def clean(self):
        cleaned_data = super(VotingForm, self).clean()
        for c in self.candidates:
            if self.cleaned_data.get('value' + str(c.id)) != str(INDEFINED_VALUE):
                return
        raise forms.ValidationError("You must give a score to at least one candidate!")
