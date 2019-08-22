from django import forms
from django.contrib.auth.models import User
from EyeMap2.models import UserProfile, Fonts, Experiment, Participant, Report, ExpVariable, ConfigList
from django.core.exceptions import ValidationError



class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    required_css_class = 'required'

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = UserProfile
        fields = ('user_type', 'avatar', 'country', 'institute', 'current_exps')

