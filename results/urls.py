from django.urls import path
from results import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.results, name='results'),
]