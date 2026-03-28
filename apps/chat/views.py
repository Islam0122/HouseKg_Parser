from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, filters
from rest_framework.response import Response

from .models import Chat, Message
from .serializers import (
    ChatSerializer,
    ChatListSerializer,
    MessageSerializer,
    MessageCreateSerializer,
)


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.select_related("user").prefetch_related("messages").all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["chat_type", "language", "user"]
    search_fields = ["external_id", "user__username"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return ChatListSerializer
        return ChatSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ("retrieve",):
            return qs.prefetch_related("messages")
        return qs


class MessageViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Message.objects.select_related("chat").all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["chat", "role"]
    ordering_fields = ["created_at"]
    ordering = ["created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return MessageCreateSerializer
        return MessageSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        chat_id = self.request.query_params.get("chat_id")
        if chat_id:
            qs = qs.filter(chat_id=chat_id)
        return qs