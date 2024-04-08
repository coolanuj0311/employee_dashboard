from django.db import models
from django.core.validators import FileExtensionValidator
from django.urls import reverse
from django.db.models import Q
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
import re
import json
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.validators import (
    MaxValueValidator,
    validate_comma_separated_integer_list,
)
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from backend import settings
from django.db.models.signals import pre_save
from model_utils.managers import InheritanceManager

class Customer(models.Model):
    name = models.CharField(max_length=255, null=True)
    # country_code = models.CharField(max_length=255, null=True, default=None)
    # status = models.CharField(max_length=255, default='active', null=True)
    is_active = models.BooleanField(default=True, null=True)
    # is_deleted = models.BooleanField(default=False, null=True)
    # email = models.EmailField(unique=True, null=True)
    # address = models.CharField(max_length=255, null=True)
    # address_secondary = models.CharField(max_length=255, null=True)
    # city = models.CharField(max_length=255, null=True)
    # state = models.CharField(max_length=255, null=True)
    # postal_code = models.CharField(max_length=255, null=True)
    # country = models.CharField(max_length=255, null=True)
    # business_size = models.IntegerField(null=True)
    # industry_vertical = models.CharField(max_length=255, null=True)
    # users = models.ManyToManyField('User', related_name='customer_users')
    # roles = models.ManyToManyField('Role', related_name='customer_roles')
    # customer_resources = models.ManyToManyField('CustomerResources', related_name='customer_resources')

    class Meta:
        db_table = 'customer'
        verbose_name_plural = 'Customers'
class Role(models.Model):
    name = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    class Meta:
        db_table = 'role'

class User(models.Model):
    # tsp_user_id = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    role = models.IntegerField(null=True)
    # email = models.EmailField(unique=True, null=True)
    # password = models.CharField(max_length=255, null=True)
    # profile_image = models.CharField(max_length=255, null=True, default=None)
    # mpin = models.CharField(max_length=255, null=True, default=None)
    # language = models.CharField(max_length=255, null=True, default=None)
    # country_code = models.CharField(max_length=255, null=True, default=None)
    # phone = models.CharField(max_length=255, null=True, default=None)
    # is_phone_number_verified = models.BooleanField(default=False)
    # tnc_accepted = models.BooleanField(default=False)
    # is_notifies = models.BooleanField(default=False)
    # otp = models.IntegerField(null=True, default=None)
    # marketing_email_accepted = models.BooleanField(default=False)
    # access_token = models.CharField(max_length=255, null=True)
    # status = models.CharField(max_length=255, choices=[
    #     ('active', 'Active'),
    #     ('inactive', 'Inactive'),
    #     ('archived', 'Archived')
    # ], default='active', null=True)
    # address = models.CharField(max_length=255, null=True, default=None)
    # color_code = models.JSONField(default=[
    #     {"key": "Speeding", "value": "FF9950"},
    #     {"key": "Idling", "value": "00CBA0"},
    #     {"key": "Harsh Acceleration", "value": "4DBFFF"},
    #     {"key": "Harsh Cornering", "value": "FF7070"},
    #     {"key": "Harsh Braking", "value": "FFEA6C"}
    # ])
    # socket_token = models.CharField(max_length=255, null=True, default=None)
    # org_point_of_contact = models.BooleanField(default=False)
    # failed_login_count = models.IntegerField(null=True, default=0)
    # failed_login_at = models.CharField(max_length=255, null=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='users')
    # user_role = models.ForeignKey('Role', on_delete=models.CASCADE, related_name='user_roles')
    # onboarding_flow = models.OneToOneField('OnboardingFlow', on_delete=models.CASCADE, related_name='user')
    # created_by = models.ForeignKey('Role', on_delete=models.CASCADE, related_name='created_users')

    class Meta:
        db_table = 'users'



class UserRolePrivileges(models.Model):
    # role = models.ForeignKey('Role', on_delete=models.CASCADE, related_name='role_privileges')
    resource = models.ForeignKey('Resources', on_delete=models.CASCADE, related_name='role_privileges')
#     has_read = models.BooleanField(default=True, null=False)
#     has_write = models.BooleanField(default=False, null=False)

    class Meta:
        db_table = 'user_role_privileges'
        verbose_name_plural = 'User Role Privileges'

class Resources(models.Model):
    resource_name = models.CharField(max_length=255, null=False)
#     status = models.IntegerField(default=0, null=False)
#     parent_id = models.IntegerField(null=True)
#     customer_resources = models.ManyToManyField('CustomerResources', related_name='resources')
#     user_role_privileges = models.ManyToManyField('UserRolePrivileges', related_name='resources')

    class Meta:
        db_table = 'resources'
        verbose_name_plural = 'Resources'

class CustomerResources(models.Model):
    resource = models.ForeignKey('Resources', on_delete=models.CASCADE, related_name='customer_resource')
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='customer_resource')
#     access_type = models.IntegerField(null=True)

    class Meta:
        db_table = 'customer_resources'
        verbose_name_plural = 'Customer Resources'

