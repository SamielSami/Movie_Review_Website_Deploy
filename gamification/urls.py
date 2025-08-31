from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('badges/', views.badges_page, name='badges'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('activity/', views.activity_log, name='activity_log'),
    path('api/stats/', views.api_user_stats, name='api_user_stats'),
    path('api/badges/', views.api_recent_badges, name='api_recent_badges'),
]
