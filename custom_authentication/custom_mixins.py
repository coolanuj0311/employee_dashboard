from rest_framework import permissions
from backend.exam.models.coremodels import UserRolePrivileges

'''this is how base permission works :

from rest_framework.permissions import BasePermission

class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

'''

class BaseAccessMixin:
    permission_classes = [permissions.IsAuthenticated]
    allowed_resources = set()
    
    def has_access(self, request):
        user = request.user
        user_privileges = UserRolePrivileges.objects.filter(role=user.role)
        privileged_resources = {privilege.resource.id for privilege in user_privileges}
        
        return self.allowed_resources == privileged_resources

class SuperAdminMixin(BaseAccessMixin):
    allowed_resources = {1, 2, 4, 5, 6}

class ClientAdminMixin(BaseAccessMixin):
    allowed_resources = {1, 3, 4, 6}

class ClientMixin(BaseAccessMixin):
    allowed_resources = {1, 4, 6}


# from rest_framework import permissions
# from backend.exam.models.coremodels import UserRolePrivileges

# class SuperAdminMixin:
#     permission_classes = [permissions.IsAuthenticated]
    
#     def has_super_admin_privileges(self, request):
#         super_admin_resources = {1, 2, 4, 5, 6}  # Using sets for O(1) lookup
        
#         user = request.user
#         user_privileges = UserRolePrivileges.objects.filter(role=user.role)
#         privileged_resources = {privilege.resource.id for privilege in user_privileges}
        
#         return super_admin_resources == privileged_resources
    
# class ClientAdminMixin:
#     permission_classes = [permissions.IsAuthenticated]
    
#     def has_super_admin_privileges(self, request):
#         client_admin_resources = {1, 3, 4, 6}  # Using sets for O(1) lookup
        
#         user = request.user
#         user_privileges = UserRolePrivileges.objects.filter(role=user.role)
#         privileged_resources = {privilege.resource.id for privilege in user_privileges}
        
#         return client_admin_resources == privileged_resources
    
# class ClientMixin:
#     permission_classes = [permissions.IsAuthenticated]
    
#     def has_super_admin_privileges(self, request):
#         client_resources = {1, 4, 6}  # Using sets for O(1) lookup
        
#         user = request.user
#         user_privileges = UserRolePrivileges.objects.filter(role=user.role)
#         privileged_resources = {privilege.resource.id for privilege in user_privileges}
        
#         return client_resources == privileged_resources
