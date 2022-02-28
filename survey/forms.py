from django import forms

from .models import Submission, Survey, Option,Question,Note


class SurveyForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput
    (attrs={'placeholder': 'فضلا ادخل العنوان'}))
    
    q1option1 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'فضلا ادخل الخيار الاول'}))
    q1option2 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'فضلا ادخل الخيار الثاني'}))

    q2option1 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'فضلا ادخل الخيار الاول'}))
    q2option2 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'فضلا ادخل الخيار الثاني'}))

    q3option1 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'فضلا ادخل الخيار الاول'}))
    q3option2 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'فضلا ادخل الخيار الثاني'}))

    q4option1 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'فضلا ادخل الخيار الاول'}))
    q4option2 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'فضلا ادخل الخيار الثاني'}))

    class Meta:
        model = Survey
        fields = ["title"]


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["prompt"]
    
class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ["text"]

class AnswerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        options = kwargs.pop("options")
        # Options must be a list of Option objects
        choices = {(o.pk, o.text) for o in options}
        super().__init__(*args, **kwargs)
        option_field = forms.ChoiceField(choices=choices, widget=forms.RadioSelect, required=True)
        self.fields["option"] = option_field



class BaseAnswerFormSet(forms.BaseFormSet):
    # note = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'فضلا ادخل الخيار الثاني'}))

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs["options"] = kwargs["options"][index]
        return kwargs

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["note"]