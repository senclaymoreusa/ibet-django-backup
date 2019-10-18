from django.test import TestCase
from django import forms

from users.models import (
    CustomUser
)
from users.forms import (
    UserCreationForm
)

# Create your tests here.

# Test User Creation Form
class UserCreationFormTest(TestCase):

    def setUp(self):
        self.user_creation = CustomUser.objects.create(username = 'wluuuutest', email = 'wluuuu@test.com')

    def test_userCreationForm_valid(self):
        form = UserCreationForm(data={
            'username': 'wluuuu01',
            'email': 'wluuuu01@test.com',
            'password1': 'hellotest1',
            'password2': 'hellotest1',
            'phone':'123'
        },instance = CustomUser.objects.create(username = 'wludksuuu', email = 'wluudsuu@test.com', phone='123345'))
        self.assertTrue(form.is_valid())

    def test_password1_field_label(self):
        form = UserCreationForm()
        self.assertTrue(form.fields['password1'].label == 'Password')

    def test_password2_matches_passwords1(self):
        form = UserCreationForm(data={
            'username': 'wluuuu02',
            'email': 'wluuuu02@test.com',
            'password1': 'hellotest1',
            'password2': 'hellotestdiff',
            'phone':'1234'
        },instance = CustomUser.objects.create(username = 'wluddkfksuuu', email = 'wluufsdndsuu@test.com', phone='23456'))
        self.assertFalse(form.is_valid())

    def test_if_phone_number_unique(self):
        form = UserCreationForm(data={
            'username': 'samet1',
            'email': 'samet1@test.com',
            'password1': 'Password1',
            'password2': 'Password1',
            'phone':'12345'
        },instance = CustomUser.objects.create(username = 'samet2', email = 'samet2@test.com', phone='12345'))
        self.assertTrue(form.is_valid())

    
    def test_if_email_unique(self):
        form = UserCreationForm(data={
            'username': 'samet2',
            'email': 'samet2@test.com',
            'password1': 'Password1',
            'password2': 'Password1',
            'phone':'12345'
        },instance = CustomUser.objects.create(username = 'samet3', email = 'samet2@test.com', phone='123455'))
        self.assertTrue(form.is_valid())
 

    