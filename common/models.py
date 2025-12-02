from __future__ import unicode_literals
from __future__ import unicode_literals
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class AdminConfiguration(models.Model):
    production = models.BooleanField(default=False)
    demo = models.BooleanField(default=False)
    local = models.BooleanField(default=False)
class UserProfile(models.Model):
    USER_TYPE_ADMIN = 'admin'
    USER_TYPE_STAFF = 'staff'
    USER_TYPE_ACCOUNTANT = 'accountant'

    USER_TYPES = (
        (USER_TYPE_ADMIN, 'admin'),
        ( USER_TYPE_STAFF, 'staff'),
        (USER_TYPE_ACCOUNTANT, 'accountant'),
    )

    user = models.OneToOneField(User, related_name='user_profile',
                                on_delete=models.CASCADE, null=True, blank=True)
    user_type = models.CharField(
        max_length=100, choices=USER_TYPES, default= USER_TYPE_ADMIN
    )
    address = models.TextField(max_length=512, blank=True, null=True)
    phone_no = models.CharField(max_length=13, blank=True, null=True)
    mobile_no = models.CharField(max_length=13, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return self.user.username
