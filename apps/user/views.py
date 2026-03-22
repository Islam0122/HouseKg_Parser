from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TelegramUser
from .serializers import TelegramUserSerializer, TelegramUserCreateSerializer


@extend_schema_view(
    get=extend_schema(
        summary="Список пользователей",
        description="Возвращает всех Telegram-пользователей. Можно фильтровать по `is_active`.",
        parameters=[
            OpenApiParameter("is_active", bool, description="Фильтр: только активные / неактивные"),
        ],
        tags=["Пользователи"],
    )
)
class TelegramUserListView(generics.ListAPIView):
    serializer_class = TelegramUserSerializer

    def get_queryset(self):
        qs = TelegramUser.objects.all().order_by("-created_at")
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() in ("true", "1"))
        return qs


@extend_schema(
    summary="Регистрация / обновление пользователя",
    description=(
        "Создаёт нового пользователя или обновляет существующего по `telegram_id`. "
        "Вызывается ботом при команде /start."
    ),
    tags=["Пользователи"],
)
class TelegramUserCreateView(generics.CreateAPIView):
    serializer_class = TelegramUserCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            TelegramUserSerializer(user).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    summary="Детали пользователя",
    description="Получить пользователя по его `telegram_id`.",
    tags=["Пользователи"],
)
class TelegramUserDetailView(generics.RetrieveAPIView):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    lookup_field = "telegram_id"


@extend_schema(
    summary="Активировать / деактивировать пользователя",
    description="Переключает поле `is_active` для пользователя с указанным `telegram_id`.",
    tags=["Пользователи"],
)
class TelegramUserToggleActiveView(APIView):
    def patch(self, request, telegram_id):
        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
        except TelegramUser.DoesNotExist:
            return Response({"detail": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = not user.is_active
        user.save(update_fields=["is_active", "updated_at"])
        return Response(TelegramUserSerializer(user).data)