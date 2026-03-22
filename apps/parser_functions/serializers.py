from rest_framework import serializers
from .models import Flat, FlatImage, MarketStat, ParserSettings, ParserLog


class FlatImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlatImage
        fields = ("id", "image_url", "created_at")


class FlatListSerializer(serializers.ModelSerializer):
    """Компактный сериализатор для списка квартир."""
    first_image = serializers.SerializerMethodField()
    floor_info = serializers.SerializerMethodField()

    class Meta:
        model = Flat
        fields = (
            "id", "title", "price", "price_per_m2",
            "rooms", "area", "floor_info",
            "city", "district", "address",
            "source", "link",
            "is_urgent", "is_owner",
            "first_image", "created_at",
        )

    def get_first_image(self, obj):
        img = obj.images.first()
        return img.image_url if img else None

    def get_floor_info(self, obj):
        if obj.floor is None:
            return None
        return f"{obj.floor}/{obj.total_floors}" if obj.total_floors else str(obj.floor)


class FlatDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор с полным списком фото."""
    images = FlatImageSerializer(many=True, read_only=True)
    floor_info = serializers.SerializerMethodField()

    class Meta:
        model = Flat
        fields = (
            "id", "title", "price", "price_per_m2",
            "rooms", "area", "floor", "total_floors", "floor_info",
            "city", "district", "address",
            "source", "link",
            "is_urgent", "is_owner",
            "images", "created_at",
        )

    def get_floor_info(self, obj):
        if obj.floor is None:
            return None
        return f"{obj.floor}/{obj.total_floors}" if obj.total_floors else str(obj.floor)


class MarketStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketStat
        fields = ("id", "rooms", "district", "avg_price_per_m2", "median_price_per_m2", "updated_at")


class ParserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParserSettings
        fields = (
            "id", "name", "discount_percent",
            "min_rooms", "max_rooms", "district",
            "is_active", "created_at",
        )


class ParserLogSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()

    class Meta:
        model = ParserLog
        fields = ("id", "source", "message", "is_error", "level", "created_at")

    def get_level(self, obj):
        return "error" if obj.is_error else "info"


class ProfitableFlatSerializer(FlatListSerializer):
    """Расширяет FlatListSerializer — добавляет процент скидки от рынка."""
    discount_from_market = serializers.SerializerMethodField()
    market_median = serializers.SerializerMethodField()

    class Meta(FlatListSerializer.Meta):
        fields = FlatListSerializer.Meta.fields + ("discount_from_market", "market_median")

    def get_discount_from_market(self, obj):
        stat = MarketStat.objects.filter(
            rooms=obj.rooms, district__iexact=obj.district
        ).first() or MarketStat.objects.filter(rooms=obj.rooms).first()
        if not stat or not obj.price_per_m2:
            return None
        pct = (stat.median_price_per_m2 - obj.price_per_m2) / stat.median_price_per_m2 * 100
        return round(pct, 1)

    def get_market_median(self, obj):
        stat = MarketStat.objects.filter(
            rooms=obj.rooms, district__iexact=obj.district
        ).first() or MarketStat.objects.filter(rooms=obj.rooms).first()
        return stat.median_price_per_m2 if stat else None