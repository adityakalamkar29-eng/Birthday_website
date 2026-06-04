from django import forms
from .models import BirthdayPerson, BirthdayPhoto

class BirthdayPersonForm(forms.ModelForm):
    class Meta:
        model = BirthdayPerson
        fields = ['name', 'nickname', 'dob', 'message', 'song_url', 'song_file', 'song_name', 'theme_color', 'admin_password']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'message': forms.Textarea(attrs={'rows': 4}),
            'admin_password': forms.PasswordInput(render_value=True),
            'theme_color': forms.TextInput(attrs={'type': 'color'}),
        }
        labels = {
            'dob': 'Date of Birth (This becomes your page URL)',
            'admin_password': 'Manage Password (to upload/edit photos)',
        }

class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = BirthdayPhoto
        fields = ['image', 'caption']
        widgets = {
            'caption': forms.TextInput(attrs={'placeholder': 'Add a cute caption... (optional)'}),
        }

class AuthForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter manage password'}))
