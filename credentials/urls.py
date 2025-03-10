from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('applied',views.applied,name='applied'),
    path('signin',views.signin,name='signin'),
    path('signup',views.signup,name='signup'),
    path('chat',views.chat,name='chat'),
    path('logout',views.logout,name='logout'),
    
]