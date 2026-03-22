from rest_framework import serializers
from .models import TelegramUser


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ("id", "telegram_id", "username", "fullname", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class TelegramUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ("telegram_id", "username", "fullname")

    def create(self, validated_data):
        user, _ = TelegramUser.objects.update_or_create(
            telegram_id=validated_data["telegram_id"],
            defaults={
                "username": validated_data.get("username"),
                "fullname": validated_data.get("fullname"),
            },
        )
        return user