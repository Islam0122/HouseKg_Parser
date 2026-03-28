from rest_framework import serializers
from .models import Chat, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("id", "chat", "role", "text", "meta", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_role(self, value):
        if value not in Message.Role.values:
            raise serializers.ValidationError(f"Invalid role. Must be one of: {Message.Role.values}")
        return value


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("id", "chat", "role", "text", "meta", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_role(self, value):
        if value not in Message.Role.values:
            raise serializers.ValidationError(f"Invalid role. Must be one of: {Message.Role.values}")
        return value


class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = (
            "id", "chat_type", "user", "external_id",
            "language", "messages_cache", "message_count",
            "messages", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_message_count(self, obj):
        return obj.messages.count()


class ChatListSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = (
            "id", "chat_type", "user", "external_id",
            "language", "message_count", "last_message",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_message_count(self, obj):
        return obj.messages.count()

    def get_last_message(self, obj):
        msg = obj.messages.order_by("-created_at").first()
        if not msg:
            return None
        return {"role": msg.role, "text": msg.text[:100], "created_at": msg.created_at}