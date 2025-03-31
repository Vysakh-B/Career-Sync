from django.urls import path
from . import views

urlpatterns = [
    path('chats',views.chats,name='chats'),
    path('chat/<int:id>/',views.chat,name='chat'),
    path('freechat',views.freechat,name='freechat'),
    path("get_messages/<int:session_id>/", views.get_messages, name="get_messages"),
    path("send_message/", views.send_message, name="send_message"),
    path("redirecting_chat", views.redirecting_chat, name="redirecting_chat"),
    path("read_interview/<int:id>/", views.read_interview, name="read_interview"),
    # path("update_interview/<int:id>/", views.update_interview, name="update_interview"),
]