"""
URL configuration for ecommerce project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def admin_login_redirect(request):
    next_url = request.GET.get('next', '/admin/')
    return redirect(f'/login/?next={next_url}')

urlpatterns = [
    path('admin/login/', admin_login_redirect),
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
