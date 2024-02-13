from django.contrib import admin
from .models import *
from embed_video.admin import AdminVideoMixin

# Register your models here.

class ContentAdmin(AdminVideoMixin, admin.ModelAdmin):
    pass

admin.site.register(Content, ContentAdmin)



admin.site.register(Video)
admin.site.register(Contentpd)
# admin.site.register(Content)