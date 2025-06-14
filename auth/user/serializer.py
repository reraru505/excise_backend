from auth.user.models import CustomUser
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        exclude = ['password']

    
