from django.urls import path
from .views import (
    CreatePrivateChatView,
    ChatListView,
    ChatDetailView,
    SendMessageView,
    MessageListView,
    BlockUserView,
)

urlpatterns = [
    path('private/create/', CreatePrivateChatView.as_view(), name='create_private_chat'),
    path('', ChatListView.as_view(), name='chat_list'),
    path('<int:chat_id>/', ChatDetailView.as_view(), name='chat_detail'),
    path('<int:chat_id>/send/', SendMessageView.as_view(), name='send_message'),
    path('<int:chat_id>/messages/', MessageListView.as_view(), name='message_list'),
    path('block/', BlockUserView.as_view(), name='block_user'),
]