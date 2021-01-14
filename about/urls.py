from django.urls import path
from about import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.about, name='about'),
]