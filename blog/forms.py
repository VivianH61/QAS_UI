from functools import partial
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, get_user_model, login, logout, password_validation
from django.core.exceptions import ValidationError
from django.core import validators
from django.core.validators import RegexValidator


class SssSettingForm(forms.Form):
    Set_the_number_of_participants = forms.IntegerField()
    Least_number_of_participants_for_key_reconstruction = forms.IntegerField()
    class Meta:
        model = User
        fields = ['n', 'k']


# this form allows the user to input the partial shares
class EnterShareForm(forms.Form):
    party_id = forms.IntegerField()
    partial_key = forms.CharField()
    class Meta:
        model = User
        fields = ['id','share']


class TransactionsForm(forms.Form):
    amount = forms.IntegerField()
    #private_key = forms.CharField()
    address = forms.CharField()
    class Meta:
        model = User
        fields = ['amount', 'address']  