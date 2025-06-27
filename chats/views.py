from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Chat, ChatParticipant, Message, Block
from .serializers import (
    ChatSerializer,
    CreatePrivateChatSerializer,
    MessageSerializer,
    CreateMessageSerializer,
    BlockSerializer,
)
from django.shortcuts import get_object_or_404
from django.utils import timezone


# ایجاد چت خصوصی (اگر وجود داشت، همون رو برمی‌گردونه)
class CreatePrivateChatView(generics.CreateAPIView):
    serializer_class = CreatePrivateChatSerializer
    permission_classes = [permissions.IsAuthenticated]


# لیست چت‌های کاربر (چت‌هایی که خودش توش هست)
class ChatListView(generics.ListAPIView):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(chat_participants__user=user).distinct()


# نمایش جزییات یک چت خاص (شامل شرکت‌کنندگان)
class ChatDetailView(generics.RetrieveAPIView):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'chat_id'

    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(chat_participants__user=user)


# ارسال پیام به یک چت
class SendMessageView(generics.CreateAPIView):
    serializer_class = CreateMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_chat(self):
        chat_id = self.kwargs['chat_id']
        user = self.request.user
        chat = get_object_or_404(Chat, id=chat_id, chat_participants__user=user)
        return chat

    def perform_create(self, serializer):
        chat = self.get_chat()
        serializer.save(sender=self.request.user, chat=chat)


# لیست پیام‌های یک چت
class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        user = self.request.user
        chat = get_object_or_404(Chat, id=chat_id, chat_participants__user=user)
        return chat.messages.all().order_by('created_at')


# بلاک کردن یک کاربر
class BlockUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        blocker = request.user
        blocked_id = request.data.get('blocked_id')

        if not blocked_id:
            return Response({"detail": "blocked_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        if blocked_id == blocker.id:
            return Response({"detail": "You cannot block yourself."}, status=status.HTTP_400_BAD_REQUEST)

        blocked = get_object_or_404(ChatParticipant._meta.get_field('user').related_model, id=blocked_id)

        block, created = Block.objects.get_or_create(blocker=blocker, blocked=blocked)
        if not created:
            return Response({"detail": "User already blocked."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": f"You have blocked {blocked.username}."}, status=status.HTTP_201_CREATED)
