from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils import timezone 


from auth.user.validators import validate_name , validate_phone_number
from auth.roles.models import Role

import random


class CustomUserManager():
    def create_user(
        self,
        email,
        first_name,
        last_name,
        phone_number ,

        district,
        subdivision,
        address,
        created_by,

        password=None
    ):
        if not email:
            raise ValueError('The Email field must be set')

        username = self.generate_unique_username(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            district=district,
            subdivision=subdivision
        )

        user_handle = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            district=district,
            subdivision=subdivision,
            address=address,                      
        )
        user_handle.set_password(password)

        user_handle.save()
        return user_handle

    
    def generate_unique_username(self,
                                 first_name,
                                 last_name,
                                 phone_number,
                                 district,
                                 subdivision):

        initials = first_name[0].upper() + last_name[0].upper()
        base_username = f"{initials}{phone_number[-4:]}{district}{subdivision}"
        username = base_username[:10]
        while self.model.objects.filter(username=username).exists():
            username = f"{base_username[:7]}{random.randint(100, 999)}"
        return username

    


class CustomUser(AbstractBaseUser):

    class Meta :
        db_table = 'custom_user'

    email = models.EmailField(unique=True)

    first_name = models.CharField( max_length=50,
                                   null = False,
                                   validators=[validate_name])
    last_name  = models.CharField( max_length=50,
                                   null=False,
                                   validators=[validate_name])

    phone_number = models.CharField( max_length=10,
                                     unique=True,
                                     validators=[validate_phone_number])

    district = models.BigIntegerField(default=117)

    subdivision = models.IntegerField(default=1001)
    address = models.CharField(max_length=70, null=True)

    objects = CustomUserManager()

    role = models.ForeignKey(to=Role.role_id , on_delete=models.SET_NULL , null=True)

    def __str__(self):
        return self.username
    
