from django.db import models
# from django.contrib.auth.models import User
from membership.models import User

# Create your models here.

class Userprofile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=300, blank=True, null=True)
    country = models.CharField(max_length= 300, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    fullname = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(max_length=50, null=True, default=1)
    profile_image = models.ImageField(upload_to='profile')
    activation_key = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return str(self.user.username)
