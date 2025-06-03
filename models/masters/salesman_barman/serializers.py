from rest_framework import serializers
from .models import SalesmanBarmanModel
from .helpers import (
    validate_pan_number,
    validate_aadhaar_number,
    validate_phone_number,
    validate_address,
    validate_email,
)

class SalesmanBarmanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesmanBarmanModel
        fields = '__all__'
        read_only_fields = ['id']

    def validate_emailId(self, value):
        if value:
            validate_email(value)
        return value

    def validate_pan_number(self, value):
        validate_pan_number(value)
        return value

    def validate_aadhaar(self, value):
        validate_aadhaar_number(value)
        return value

    def validate_mobileNumber(self, value):
        validate_phone_number(value)
        return value

    def validate_address(self, value):
        validate_address(value)
        return value
