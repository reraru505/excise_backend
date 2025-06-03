from auth.roles.models import Role
from rest_framework import serializers


class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = [
            'role_id','can_read','can_write','role_precedence'
        ]

