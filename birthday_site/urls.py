from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('birthdays.urls')),
]

# Serve local media only when not using Cloudinary
if not getattr(settings, 'DEFAULT_FILE_STORAGE', '').startswith('cloudinary'):
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    if media_root:
        urlpatterns += static(settings.MEDIA_URL, document_root=media_root)
