from django_filters.rest_framework import DjangoFilterBackend, FilterSet, filters
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import generics, filters as drf_filters, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Flat, MarketStat, ParserSettings, ParserLog
from .serializers import (
    FlatListSerializer,
    FlatDetailSerializer,
    MarketStatSerializer,
    ParserSettingsSerializer,
    ParserLogSerializer,
    ProfitableFlatSerializer,
)
from .services import get_profitable_flats


# ──────────────────────────────────────────────
#  Filters
# ──────────────────────────────────────────────

class FlatFilter(FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")
    min_area  = filters.NumberFilter(field_name="area",  lookup_expr="gte")
    max_area  = filters.NumberFilter(field_name="area",  lookup_expr="lte")
    min_rooms = filters.NumberFilter(field_name="rooms", lookup_expr="gte")
    max_rooms = filters.NumberFilter(field_name="rooms", lookup_expr="lte")
    district  = filters.CharFilter(field_name="district", lookup_expr="icontains")
    source    = filters.CharFilter(field_name="source",   lookup_expr="exact")
    is_urgent = filters.BooleanFilter(field_name="is_urgent")
    is_owner  = filters.BooleanFilter(field_name="is_owner")

    class Meta:
        model = Flat
        fields = [
            "min_price", "max_price",
            "min_area",  "max_area",
            "min_rooms", "max_rooms",
            "district", "source",
            "is_urgent", "is_owner",
        ]


# ──────────────────────────────────────────────
#  Flat endpoints
# ──────────────────────────────────────────────

@extend_schema_view(
    get=extend_schema(
        summary="Список квартир",
        description=(
            "Возвращает постраничный список всех квартир с фильтрацией "
            "по цене, площади, комнатам, району и источнику."
        ),
        parameters=[
            OpenApiParameter("min_price", int,   description="Минимальная цена ($)"),
            OpenApiParameter("max_price", int,   description="Максимальная цена ($)"),
            OpenApiParameter("min_area",  float, description="Минимальная площадь (м²)"),
            OpenApiParameter("max_area",  float, description="Максимальная площадь (м²)"),
            OpenApiParameter("min_rooms", int,   description="Минимум комнат"),
            OpenApiParameter("max_rooms", int,   description="Максимум комнат"),
            OpenApiParameter("district",  str,   description="Район (частичное совпадение)"),
            OpenApiParameter("source",    str,   description="Источник: house | lalafo"),
            OpenApiParameter("is_urgent", bool,  description="Только срочные"),
            OpenApiParameter("is_owner",  bool,  description="Только от собственника"),
            OpenApiParameter("search",    str,   description="Поиск по заголовку / адресу"),
            OpenApiParameter("ordering",  str,   description="Сортировка: price, -price, created_at, -created_at"),
        ],
        tags=["Квартиры"],
    )
)
class FlatListView(generics.ListAPIView):
    queryset = Flat.objects.prefetch_related("images").all()
    serializer_class = FlatListSerializer
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = FlatFilter
    search_fields = ["title", "address", "district"]
    ordering_fields = ["price", "price_per_m2", "area", "rooms", "created_at"]
    ordering = ["-created_at"]


@extend_schema(
    summary="Детали квартиры",
    description="Полная информация о квартире, включая все фотографии.",
    tags=["Квартиры"],
)
class FlatDetailView(generics.RetrieveAPIView):
    queryset = Flat.objects.prefetch_related("images").all()
    serializer_class = FlatDetailSerializer


# ──────────────────────────────────────────────
#  Profitable flats
# ──────────────────────────────────────────────

@extend_schema(
    summary="Выгодные квартиры",
    description=(
        "Возвращает квартиры, цена за м² которых ниже рыночной медианы "
        "на заданный в настройках процент. Дополнительно возвращает "
        "`discount_from_market` — процент скидки от рынка."
    ),
    tags=["Аналитика"],
)
class ProfitableFlatsView(APIView):
    def get(self, request):
        flats = get_profitable_flats(already_sent_ids=set())
        serializer = ProfitableFlatSerializer(
            flats, many=True, context={"request": request}
        )
        return Response({
            "count": len(flats),
            "results": serializer.data,
        })


# ──────────────────────────────────────────────
#  Market stats
# ──────────────────────────────────────────────

@extend_schema_view(
    get=extend_schema(
        summary="Статистика рынка",
        description="Средняя и медианная цена за м² по комнатам и районам.",
        parameters=[
            OpenApiParameter("rooms",    int, description="Фильтр по кол-ву комнат"),
            OpenApiParameter("district", str, description="Фильтр по району"),
        ],
        tags=["Аналитика"],
    )
)
class MarketStatListView(generics.ListAPIView):
    queryset = MarketStat.objects.all()
    serializer_class = MarketStatSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["rooms", "district"]


# ──────────────────────────────────────────────
#  Parser settings (read-only public)
# ──────────────────────────────────────────────

@extend_schema_view(
    get=extend_schema(
        summary="Настройки парсера",
        description="Список активных настроек парсера.",
        tags=["Настройки"],
    )
)
class ParserSettingsListView(generics.ListAPIView):
    queryset = ParserSettings.objects.filter(is_active=True)
    serializer_class = ParserSettingsSerializer


# ──────────────────────────────────────────────
#  Parser logs
# ──────────────────────────────────────────────

@extend_schema_view(
    get=extend_schema(
        summary="Логи парсера",
        description="История событий и ошибок парсера. Новые — первые.",
        parameters=[
            OpenApiParameter("source",   str,  description="Источник: house | lalafo"),
            OpenApiParameter("is_error", bool, description="Только ошибки"),
        ],
        tags=["Логи"],
    )
)
class ParserLogListView(generics.ListAPIView):
    queryset = ParserLog.objects.all()
    serializer_class = ParserLogSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["source", "is_error"]


# ──────────────────────────────────────────────
#  Stats summary
# ──────────────────────────────────────────────

@extend_schema(
    summary="Сводная статистика",
    description="Общие цифры: кол-во квартир, средняя цена и т.д.",
    tags=["Аналитика"],
)
class StatsSummaryView(APIView):
    def get(self, request):
        from django.db.models import Avg, Min, Max, Count

        qs = Flat.objects.filter(price_per_m2__isnull=False)
        agg = qs.aggregate(
            total=Count("id"),
            avg_price=Avg("price"),
            avg_price_per_m2=Avg("price_per_m2"),
            min_price=Min("price"),
            max_price=Max("price"),
        )

        by_source = (
            Flat.objects.values("source")
            .annotate(count=Count("id"))
            .order_by("source")
        )

        return Response({
            "total_flats": Flat.objects.count(),
            "flats_with_price_per_m2": agg["total"],
            "avg_price": round(agg["avg_price"] or 0, 2),
            "avg_price_per_m2": round(agg["avg_price_per_m2"] or 0, 2),
            "min_price": agg["min_price"],
            "max_price": agg["max_price"],
            "by_source": list(by_source),
        })