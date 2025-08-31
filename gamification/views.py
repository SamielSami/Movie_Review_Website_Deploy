from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .services import (
    get_user_stats, get_user_badges, get_available_badges, 
    get_user_progress, get_leaderboard, get_recent_activity
)


@login_required
def user_profile(request, username):
    """Display user's gamification profile with stats and badges"""
    user = get_object_or_404(User, username=username)
    
    # Only allow users to view their own profile or public profiles
    if request.user != user:
        # In the future, you might want to add privacy settings
        pass
    
    stats = get_user_stats(user)
    badges = get_user_badges(user)
    progress = get_user_progress(user)
    recent_activity = get_recent_activity(user, limit=5)
    
    context = {
        'profile_user': user,
        'stats': stats,
        'badges': badges,
        'progress': progress,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'gamification/user_profile.html', context)


@login_required
def badges_page(request):
    """Display all available badges and user's progress"""
    user = request.user
    available_badges = get_available_badges()
    user_badges = get_user_badges(user)
    progress = get_user_progress(user)
    
    # Create a list of all badges with user's progress
    all_badges = []
    user_badge_ids = set(user_badges.values_list('badge_id', flat=True))
    
    for badge in available_badges:
        badge_data = {
            'badge': badge,
            'earned': badge.id in user_badge_ids,
            'progress': progress.get(badge.badge_type, None)
        }
        all_badges.append(badge_data)
    
    context = {
        'badges': all_badges,
        'user_badges_count': len(user_badges),
        'total_badges': len(available_badges),
    }
    
    return render(request, 'gamification/badges.html', context)


@login_required
def leaderboard(request):
    """Display leaderboard of top users"""
    page = request.GET.get('page', 1)
    leaderboard_data = get_leaderboard(limit=50)
    
    paginator = Paginator(leaderboard_data, 10)
    page_obj = paginator.get_page(page)
    
    context = {
        'leaderboard': page_obj,
        'user_rank': None,
    }
    
    # Get current user's rank
    if request.user.is_authenticated:
        from .models import UserPoints
        user_points = UserPoints.objects.filter(user=request.user).first()
        if user_points:
            user_rank = UserPoints.objects.filter(total_points__gt=user_points.total_points).count() + 1
            context['user_rank'] = user_rank
            context['user_points'] = user_points
    
    return render(request, 'gamification/leaderboard.html', context)


@login_required
def activity_log(request):
    """Display user's activity log"""
    page = request.GET.get('page', 1)
    activity_data = get_recent_activity(request.user, limit=100)
    
    paginator = Paginator(activity_data, 20)
    page_obj = paginator.get_page(page)
    
    context = {
        'activity': page_obj,
    }
    
    return render(request, 'gamification/activity_log.html', context)


@login_required
def api_user_stats(request):
    """API endpoint to get user stats for AJAX requests"""
    if request.method == 'GET':
        stats = get_user_stats(request.user)
        return JsonResponse(stats)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
def api_recent_badges(request):
    """API endpoint to get user's recent badges"""
    if request.method == 'GET':
        badges = get_user_badges(request.user)[:5]  # Get 5 most recent badges
        badge_data = []
        for user_badge in badges:
            badge_data.append({
                'name': user_badge.badge.name,
                'description': user_badge.badge.description,
                'icon': user_badge.badge.icon,
                'color': user_badge.badge.color,
                'earned_at': user_badge.earned_at.strftime('%Y-%m-%d %H:%M')
            })
        return JsonResponse({'badges': badge_data})
    return JsonResponse({'error': 'Invalid request method'}, status=400)
