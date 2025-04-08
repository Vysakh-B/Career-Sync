from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('applied',views.applied,name='applied'),
    path('contact',views.contact,name='contact'),
    path('signin',views.signin,name='signin'),
    path('signup',views.signup,name='signup'),
    path('logout',views.logout,name='logout'),
    path('forgot_password',views.forgot_password,name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password_view, name='reset_password'),
    
]