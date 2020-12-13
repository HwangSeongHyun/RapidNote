from django.contrib import admin
from .models import Member, FileSystem, FileList, HashList

# Register your models here.
admin.site.register(Member)
admin.site.register(FileSystem)
admin.site.register(FileList)
admin.site.register(HashList)