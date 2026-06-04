from django.contrib import admin
from .models import BirthdayPerson, BirthdayPhoto

class BirthdayPhotoInline(admin.TabularInline):
    model = BirthdayPhoto
    extra = 0
    readonly_fields = ['uploaded_at']

@admin.register(BirthdayPerson)
class BirthdayPersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'dob', 'theme_color', 'created_at']
    inlines = [BirthdayPhotoInline]

@admin.register(BirthdayPhoto)
class BirthdayPhotoAdmin(admin.ModelAdmin):
    list_display = ['person', 'caption', 'uploaded_at']
