from django.urls import path
from .views import (
    FlatListView,
    FlatDetailView,
    ProfitableFlatsView,
    MarketStatListView,
    ParserSettingsListView,
    ParserLogListView,
    StatsSummaryView,
)

urlpatterns = [
    # Квартиры
    path("flats/",            FlatListView.as_view(),       name="flat-list"),
    path("flats/<int:pk>/",   FlatDetailView.as_view(),     name="flat-detail"),

    # Аналитика
    path("flats/profitable/", ProfitableFlatsView.as_view(), name="flat-profitable"),
    path("market-stats/",     MarketStatListView.as_view(),  name="market-stat-list"),
    path("stats/",            StatsSummaryView.as_view(),    name="stats-summary"),

    # Система
    path("settings/",         ParserSettingsListView.as_view(), name="parser-settings"),
    path("logs/",             ParserLogListView.as_view(),      name="parser-logs"),
]