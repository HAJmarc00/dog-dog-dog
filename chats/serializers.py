from rest_framework import serializers
from .models import Chat, ChatParticipant, Message, Block
from accounts.serializers import UserSerializer  # فرض بر این است که سریالایزر User داری
from django.contrib.auth import get_user_model

User = get_user_model()

# سریالایزر شرکت‌کننده‌ها که فقط یوزر رو نشون میده (برای استفاده در ChatSerializer)
class ChatParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ChatParticipant
        fields = ['user', 'is_muted', 'is_blocked', 'joined_at']


class ChatSerializer(serializers.ModelSerializer):
    chat_participants = ChatParticipantSerializer(many=True, read_only=True)  # توجه به related_name

    class Meta:
        model = Chat
        fields = ['id', 'chat_type', 'group', 'created_at', 'chat_participants']


class CreatePrivateChatSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        request_user = self.context['request'].user
        if value == request_user.id:
            raise serializers.ValidationError("You can't start a chat with yourself.")
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User not found.")
        return value

    def create(self, validated_data):
        request_user = self.context['request'].user
        other_user = User.objects.get(id=validated_data['user_id'])

        # جستجو چت خصوصی موجود بین دو نفر
        chat = Chat.objects.filter(chat_type='private').filter(
            chat_participants__user=request_user
        ).filter(chat_participants__user=other_user).distinct().first()

        if chat:
            return chat

        # ایجاد چت خصوصی جدید
        chat = Chat.objects.create(chat_type='private')
        ChatParticipant.objects.create(chat=chat, user=request_user)
        ChatParticipant.objects.create(chat=chat, user=other_user)
        return chat


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'content', 'file', 'created_at', 'is_edited']


class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['content', 'file']

    def validate(self, data):
        if not data.get('content') and not data.get('file'):
            raise serializers.ValidationError("Message must have either content or a file.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        chat = self.context['chat']
        return Message.objects.create(sender=user, chat=chat, **validated_data)


class BlockSerializer(serializers.ModelSerializer):
    blocker = UserSerializer(read_only=True)
    blocked = UserSerializer(read_only=True)

    class Meta:
        model = Block
        fields = ['id', 'blocker', 'blocked', 'created_at']
