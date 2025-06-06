from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('applied',views.applied,name='applied'),
    path('contact',views.contact,name='contact'),
    path('signin',views.signin,name='signin'),
    path('faq',views.faq,name='faq'),
    path('about',views.about,name='about'),
    path('privacy',views.privacy,name='privacy'),
    path('terms',views.terms,name='terms'),
    path('signup',views.signup,name='signup'),
    path('logout',views.logout,name='logout'),
    path('not_found',views.not_found,name='not_found'),
    path('forgot_password',views.forgot_password,name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password_view, name='reset_password'),
    
]