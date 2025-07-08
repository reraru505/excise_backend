from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from auth.roles.decorators import has_app_permission
from auth.user.models import CustomUser
from auth.user.serializer import UserSerializer, UserCreateSerializer
from typing import cast

# Import your UserActivity model and get_client_ip function
from models.transactional.logs.models import UserActivity

from models.transactional.logs.signals import get_client_ip

# Open registration endpoint (no permission required)
@api_view(['POST'])
def register_user(request):
    """
    Handles user registration.
    User registration activity is tracked via a post_save signal on the User model.
    """
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = cast(CustomUser, serializer.save())
        # The post_save signal for the User model (defined in transactional.logs.signals)
        # will automatically handle logging the registration activity.
        return Response({
            'message': 'User registered successfully',
            'user_id': user.username,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Protected views
class UserListView(generics.ListAPIView):
    """
    Lists all users. Requires 'user.view' permission.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [has_app_permission('user', 'view')]

class UserDetailView(generics.RetrieveAPIView):
    """
    Retrieves details of a single user. Requires 'user.view' permission.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [has_app_permission('user', 'view')]

class UserUpdateView(generics.UpdateAPIView):
    """
    Updates an existing user's profile. Requires 'user.update' permission.
    Logs 'User Profile Update' activity.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [has_app_permission('user', 'update')]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object() 
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        
        
        # LOGGING USER ACTIVITY: User Profile Update
        # A new UserActivity record is created to log that a user's profile
        # has been updated.
        # - 'user': The authenticated user who initiated this update request.
        # - 'activity_type': Set to USER_UPDATE.
        # - 'target_user': The specific user whose profile was modified.
        # - 'ip_address' and 'user_agent': Contextual information about the request.
        # - 'metadata': Contains details like the fields that were updated and
        #               the username of the target user.
        

        UserActivity.objects.create(
            user=request.user,  # The authenticated user who performed the update

            activity_type=UserActivity.ActivityType.USER_UPDATE,

            target_user=instance, # The user whose profile was actually updated
            
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={
                'updated_fields': list(serializer.validated_data.keys()),
                'target_username': instance.username,
                
                # Optionally log more details
                # 'request_data_summary': {k: v for k, v in request.data.items() if k not in ['password', 'confirm_password']},
            }
        )
        return Response({'message': 'User updated successfully'})

class UserDeleteView(generics.DestroyAPIView):
    """
    Deletes a user account. Requires 'user.delete' permission.
    Logs 'User Account Deletion' activity.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [has_app_permission('user', 'delete')]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object() # The user being deleted
        self.perform_destroy(instance)

        '''
        LOGGING USER ACTIVITY: User Account Deletion
        A new UserActivity record is created to log that a user account
        has been deleted.
        - 'user': The authenticated user who initiated this delete request.
        - 'activity_type': Set to USER_DELETE.
        - 'target_user': The specific user account that was deleted.
        - 'ip_address' and 'user_agent': Contextual information about the request.
        - 'metadata': Contains details like the username and ID of the deleted user.
        '''

        UserActivity.objects.create(
            user=request.user,  # The authenticated user who performed the deletion
            activity_type=UserActivity.ActivityType.USER_DELETE,
            target_user=instance, # The user whose account was deleted
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            metadata={
                'deleted_username': instance.username,
                'deleted_user_id': str(instance.id) # Convert UUID/PK to string for metadata
            }
        )
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
