from rest_framework import serializers
from .models import weathermodel,registermodel
import re
class weatherserializer(serializers.ModelSerializer):
    class Meta:
        model=weathermodel
        fields="__all__" 

class RegisterSerializer(serializers.ModelSerializer):
#this validations are only to update
    class Meta:
        model = registermodel
        fields = ['Username', 'Email', 'Password','City']

    def validate(self, data):
        username = data.get('Username')
        email = data.get('Email')
        password = data.get('Password')

        if len(username) <= 3:
            raise serializers.ValidationError({'Username': 'Username must be greater than 3 characters'})
        elif re.search(r'[^a-zA-Z]', username) or ' ' in username:
            raise serializers.ValidationError({'Username': 'Username must contain only alphabets'})

        elif not all(re.search(pattern, password) for pattern in [r'[a-z]', r'[A-Z]', r'[0-9]', r'[^a-zA-Z0-9\s]']):
            raise serializers.ValidationError({'Password': 'Password must be minimum 8 characters in format (ex: Abcd@#12)'})
        elif ' ' in password or len(password) < 8:
            raise serializers.ValidationError({'Password': 'Password must be minimum 8 characters in format (ex: Abcd@#12)'})

        return data

    