from django.contrib import admin
from .models import UserPoints, PointLog, Badge, UserBadge, ActionLog


@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'movies_rated', 'movies_watched', 'lists_created', 'comments_made', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['last_updated']
    ordering = ['-total_points']


@admin.register(PointLog)
class PointLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'reason', 'total_after', 'timestamp']
    list_filter = ['timestamp', 'points']
    search_fields = ['user__username', 'reason']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'badge_type', 'icon', 'color', 'created_at']
    list_filter = ['badge_type', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    ordering = ['badge_type']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'earned_at']
    list_filter = ['earned_at', 'badge__badge_type']
    search_fields = ['user__username', 'badge__name']
    readonly_fields = ['earned_at']
    ordering = ['-earned_at']


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'action_id', 'timestamp']
    list_filter = ['action_type', 'timestamp']
    search_fields = ['user__username', 'action_id']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
