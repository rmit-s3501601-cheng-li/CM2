from django.contrib.auth import get_user_model
from django import forms


class SignupForm(forms.Form):
    permission = forms.IntegerField(default=3)

    def signup(self, request, user):
        user.permission = self.cleaned_data['permission']
        user.save()