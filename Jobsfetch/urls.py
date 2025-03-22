from django.urls import path
from . import views

urlpatterns = [
    # path('',views.index,name='index'),
    path('jobs',views.jobs,name='jobs'),
    path('jobsdetails/<int:id>/',views.jobdetails,name='jobdetails'),
    path('profile',views.profile,name='profile'),
    path("mark-applied/", views.mark_applied, name="mark-applied"),
    path("delete_apply/<int:id>/", views.delete_apply, name="delete_apply"),
    
]