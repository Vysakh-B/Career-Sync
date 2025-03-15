from django.urls import path
from . import views

urlpatterns = [
    path('chat',views.chat,name='chat'),
    path("get_messages/<int:session_id>/", views.get_messages, name="get_messages"),
    path("send_message/", views.send_message, name="send_message"),
]