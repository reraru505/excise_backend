from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.db.models import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated  

from auth.roles.models import Role
from auth.roles.serializers import RoleSerializer

def get_user_role_instance(user):

    if not hasattr(user, 'role') or user.role is None:
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
    return 'roles' in user_role_instance.can_view

@login_required
def check_add(request):
    user_role_instance = get_user_role_instance(request.user)
    if user_role_instance is None:
        return False
    return 'roles' in user_role_instance.can_add

@login_required
def check_update(request):
    user_role_instance = get_user_role_instance(request.user)
    if user_role_instance is None:
        return False
    return 'roles' in user_role_instance.can_update

@login_required
def check_delete(request):
    user_role_instance = get_user_role_instance(request.user)
    if user_role_instance is None:
        return False
    return 'roles' in user_role_instance.can_delete


###############################################################
# roles table must be only be altered and viewed by the admin #
###############################################################

class RolesApi(APIView):

    # Ensures request.user is not AnonymousUser
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs): 
        if not check_view(request):
            return Response({"detail": "You do not have permission to view roles."},
                            status=status.HTTP_403_FORBIDDEN)
        
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs): 
        if not check_add(request):
            return Response({"detail": "You do not have permission to add roles."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, role_id, *args, **kwargs): 
        if not check_update(request):
            return Response({"detail": "You do not have permission to update roles."},
                            status=status.HTTP_403_FORBIDDEN)
        
        try:
            role_instance = Role.objects.get(role_id=role_id)
        except Role.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = RoleSerializer(role_instance, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, role_id, *args, **kwargs): 
        if not check_delete(request):
            return Response({"detail": "You do not have permission to delete roles."},
                            status=status.HTTP_403_FORBIDDEN)
        
        try:
            role_instance = Role.objects.get(role_id=role_id)
        except Role.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        role_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
