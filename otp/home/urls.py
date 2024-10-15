from django.urls import path
from . import views

urlpatterns = [
    path('',views.homepage,name='homepage'),
    path('vid/',views.capture,name='capture'),
    path('verify/',views.verify,name='verify'),
    path('vote/',views.vote,name='vote'),
    path('logout',views.logout2,name='logout')
]
