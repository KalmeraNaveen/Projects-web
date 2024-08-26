from django.contrib import admin
from .models import weathermodel,registermodel
# Register your models here.
class weatheradmin(admin.ModelAdmin):
    list_display=['url','City','Rain','Temperature']
class registeradmin(admin.ModelAdmin):
    list_display=['Username','Email','Password','City']
admin.site.register(weathermodel,weatheradmin)
admin.site.register(registermodel,registeradmin)