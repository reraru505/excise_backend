from django.db import models
from django.contrib.postgres.fields import ArrayField

class Role(models.Model): 

    role_id = models.CharField(max_length=50, null=False, primary_key=True)

    can_add = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )

    can_update = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )

    
    can_delete = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )


    can_view = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )

    role_precedence = models.IntegerField(default=0)

    def __str__(self):
        return self.role_id



  
