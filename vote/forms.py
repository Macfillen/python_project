from django import forms
from vote.models import CLAIM_CHOICES


class VoteAddForm(forms.Form):
    multi = forms.BooleanField(label="Мультиголосование", required=False)

    def __init__(self, *args, **kwargs):
        extra = kwargs.pop('extra')
        title = kwargs.pop('title')
        description = kwargs.pop('description')
        super(VoteAddForm, self).__init__(*args, **kwargs)
        for i, question in list(extra):
            self.fields['custom_%s' % i] = forms.CharField(label = str(i + 1),  required = i<2, widget=forms.TextInput(attrs={'class': 'vote-input vote-line', 'value': question}), max_length=50)
        self.fields['title'] = forms.CharField(label="Заголовок", required=True, widget=forms.TextInput(attrs={'class': 'vote-input', 'value': title}), max_length=100)
        self.fields['description'] = forms.CharField(label="Описание", required=True, widget=forms.TextInput(attrs={'class': 'vote-input', 'value': description}), max_length=200)


class VoteProcessForm(forms.Form):
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices')
        multi = kwargs.pop('multi')
        super(VoteProcessForm, self).__init__(*args, **kwargs)
        if multi == 0:
            self.fields['chosen'] = forms.ChoiceField(widget=forms.RadioSelect, choices=choices)
        else:
            self.fields['chosen'] = forms.MultipleChoiceField(widget = forms.CheckboxSelectMultiple, choices=choices)


class ClaimForm(forms.Form):
    reason = forms.ChoiceField(label='Причина', choices=CLAIM_CHOICES, widget=forms.Select(attrs={'class': 'claim-input-alt'}))
    comment = forms.CharField(label='Комментарий', max_length=500, widget=forms.TextInput(attrs={'class': 'claim-input'}))
    def __init__(self, *args, **kwargs):
        extra = kwargs.pop('id')
        super(ClaimForm, self).__init__(*args, **kwargs)
        self.fields['voteid'] = forms.IntegerField(label='ID голосования', widget=forms.TextInput(attrs={'class': 'claim-input-alt', 'value' : extra, 'readonly': True}))
