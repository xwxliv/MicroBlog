from django import forms
from .models import User, UserProfile
from django.contrib.auth.forms import UserCreationForm


class LoginForm(forms.Form):
    username = forms.CharField(label="Username", widget=forms.TextInput)
    password = forms.CharField(label="Password:", widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, max_length=200, help_text='Required')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")


class ResetForm(forms.Form):
    email = forms.EmailField(required=True, label="Email address", error_messages={'required': "enter email address"},
                             widget=forms.EmailInput(attrs={'rows': 1, 'cols': 20, }), )

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError("Invalid email format, must ends with domain name")
        else:
            cleaned_data = super(ResetForm, self).clean()
        return cleaned_data


class ResetpwdForm(forms.Form):
    newpassword1 = forms.CharField(
        required=True,
        label="New password",
        error_messages={'required': "Enter your new password"},
        widget=forms.PasswordInput(
            attrs={'rows': 1, 'placeholder': "Length of password should be at least 5 chars"}), )

    newpassword2 = forms.CharField(
        required=True,
        label="Confirm password",
        error_messages={'required': 'Confirm your password'},
        widget=forms.PasswordInput(attrs={'rows': 1, 'placeholder': "Length of password should be at least 5 chars"}), )

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError("All fields are required")
        elif len(self.cleaned_data['newpassword1']) < 5:
            raise forms.ValidationError("Password length should be at least 5")
        elif self.cleaned_data['newpassword1'] != self.cleaned_data['newpassword2']:
            raise forms.ValidationError("Your password and confirmation password do not match")
        else:
            cleaned_data = super(ResetpwdForm, self).clean()
        return cleaned_data


class ChangepwdForm(forms.Form):
    oldpassword = forms.CharField(
        required=True,
        label="Current password",
        error_messages={'required': "Enter your current password"},
        widget=forms.PasswordInput(attrs={'rows': 1}), )

    newpassword1 = forms.CharField(
        required=True,
        label="New password",
        error_messages={'required': "Enter your new password"},
        widget=forms.PasswordInput(
            attrs={'rows': 1, 'placeholder': "Length of password should be at least 5 chars"}), )

    newpassword2 = forms.CharField(
        required=True,
        label="Confirm password",
        error_messages={'required': 'Confirm your password'},
        widget=forms.PasswordInput(attrs={'rows': 1, 'placeholder': "Length of password should be at least 5 chars"}), )

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError("All fields are required")
        elif len(self.cleaned_data['newpassword1']) < 5:
            raise forms.ValidationError("Password length should be at least 5")
        elif self.cleaned_data['newpassword1'] != self.cleaned_data['newpassword2']:
            raise forms.ValidationError("Your password and confirmation password do not match")
        else:
            cleaned_data = super(ChangepwdForm, self).clean()
        return cleaned_data


class ProfileForm(forms.Form):
    age = forms.CharField(label="Your age", required=True, max_length=2,
                          widget=forms.TextInput(attrs={'rows': 1, 'maxlength': 2, 'placeholder': 'Max of 2 digits'}))

    bio = forms.CharField(label="Biography", required=True,
                          widget=forms.Textarea(attrs={'cols': 40, 'rows': 10, 'maxlength': 420,
                                                       'placeholder': 'Max of 420 chars'}))

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError("All fields are required")
        else:
            cleaned_data = super(ProfileForm, self).clean()
        return cleaned_data


class PhotoForm(forms.Form):
    photo = forms.FileField(label="Upload your profile image")

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError("Image type is not supported. ONLY .jpg or .png")
        else:
            cleaned_data = super(PhotoForm, self).clean()
        return cleaned_data


