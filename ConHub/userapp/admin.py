from django.contrib import admin
from .models import Userprofile

# Register your models here.

@admin.register(Userprofile)
class userprofile(admin.ModelAdmin):
    list_display = ('fullname', 'dob', 'country')



# admin.site.register(Userprofile)    
