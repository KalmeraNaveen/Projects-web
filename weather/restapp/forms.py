from django import forms
from .models import registermodel
import re
def getotp(data):
    print(data)
    global generated_otp
    generated_otp=data
class RegisterForm(forms.ModelForm):
    ConfirmPassword = forms.CharField(
        max_length=35,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'form-control'}),
        label='Confirm Password'
    )
    OTP = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'form-control'}),
        label='OTP'
    )

    class Meta:
        model = registermodel
        fields = ['Username', 'Email', 'Password', 'ConfirmPassword', 'OTP']
        widgets = {
            'Username': forms.TextInput(attrs={'class': 'form-control', 'id': 'form-control'}),
            'Email': forms.EmailInput(attrs={'class': 'form-control', 'id': 'form-control'}),
            'Password': forms.PasswordInput(attrs={'class': 'form-control', 'id': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("Password")
        confirm_password = cleaned_data.get("ConfirmPassword")
        username = cleaned_data.get('Username')
        email = cleaned_data.get('Email')
        otp = cleaned_data.get('OTP')
        # Validate Username
        if len(username) <= 3:
            self.add_error('Username', 'Name must be >3 characters')
        elif re.search(r'[^a-zA-Z]', username) or ' ' in username:
            self.add_error('Username', 'Username must contain only alphabets')
        elif registermodel.objects.filter(Username=username).exists():
            self.add_error('Username', 'Username already exists')

        # Validate Password
        elif not all(re.search(pattern, password) for pattern in [r'[a-z]', r'[A-Z]', r'[0-9]', r'[^a-zA-Z0-9\s]']):
            self.add_error('Password', 'Password must be minimum 8 characters in format (ex: Abcd@#12)')
        elif ' ' in password or len(password) < 8:
            self.add_error('Password', 'Password must be minimum 8 characters in format (ex: Abcd@#12)')
        elif password != confirm_password:
            self.add_error('ConfirmPassword', "Passwords do not match")

        # Validate Email
        elif registermodel.objects.filter(Email=email).exists():
            self.add_error('Email', 'Email already exists')

        elif otp!=str(generated_otp):
            self.add_error('OTP','Otp mismatch')
