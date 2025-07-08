from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator , MaxValueValidator


class Role(models.Model): 

    role_id = models.CharField(max_length=50, null=False, primary_key=True)
    name = models.CharField(max_length=100),

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
                                                       # this below is a LSP specific command to stop it from bitching
    role_precedence = models.IntegerField(default= 0 , # pyright: ignore [reportArgumentType, reportGeneralTypeIssues]
                                          validators = [
                                              MinValueValidator(0),
                                              MaxValueValidator(9),
                                              ],
                                          help_text="Higher number = higher privileges"
                                          )

    class Meta:
        db_table = 'roles'
        ordering = ['-role_precedence']

    def __str__(self) -> str:
        return f"{self.name} (level {self.role_precedence})" 



  
