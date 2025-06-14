from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.db.models import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from auth.user.models import CustomUserManager
from auth.user.serializer import UserSerializer

def get_user_role_instance(user):

    if not hasattr(user, 'user') or user.role is None:
        return None 
    try:
        return user.role
    except ObjectDoesNotExist: 
        return None
    except Exception as e:
        return None

@login_required
def check_view(request):
    user_role_instance = get_user_role_instance(request.user)
    if user_role_instance is None:
        return False
    return 'user' in user_role_instance.can_view

@login_required
def check_add(request):
    user_role_instance = get_user_role_instance(request.user)
    if user_role_instance is None:
        return False
    return 'user' in user_role_instance.can_add

@login_required
def check_update(request):
    user_role_instance = get_user_role_instance(request.user)
    if user_role_instance is None:
        return False
    return 'user' in user_role_instance.can_update

@login_required
def check_delete(request):
    user_role_instance = get_user_role_instance(request.user)
    if user_role_instance is None:
        return False
    return 'user' in user_role_instance.can_delete


#################################
# CRUD functions for user model #
#################################


class UserApi(APIView):

    @login_required
    def get(self , request , pk=None ,*args , **kwargs ):

        if not check_view(request):
            return Response({"detail": "You do not have permission to view roles"} ,
                            status=status.HTTP_403_FORBIDDEN)
        # @todo 
        return CustomUserManager.objects()
