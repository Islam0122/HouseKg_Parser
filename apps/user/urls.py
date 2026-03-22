from django.urls import path
from .views import (
    TelegramUserListView,
    TelegramUserCreateView,
    TelegramUserDetailView,
    TelegramUserToggleActiveView,
)

urlpatterns = [
    path("",                              TelegramUserListView.as_view(),        name="user-list"),
    path("register/",                     TelegramUserCreateView.as_view(),      name="user-register"),
    path("<int:telegram_id>/",            TelegramUserDetailView.as_view(),      name="user-detail"),
    path("<int:telegram_id>/toggle/",     TelegramUserToggleActiveView.as_view(), name="user-toggle"),
]