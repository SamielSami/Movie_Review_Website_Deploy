"""
Gamification services for handling points and badges
"""
from django.contrib.auth.models import User
from .models import UserPoints, Badge, UserBadge, ActionLog
from .badges import POINT_VALUES, BADGE_REQUIREMENTS


def get_or_create_user_points(user):
    """Get or create UserPoints for a user"""
    user_points, created = UserPoints.objects.get_or_create(user=user)
    return user_points


def has_performed_action(user, action_type, action_id):
    """Check if user has already performed this specific action"""
    return ActionLog.objects.filter(
        user=user, 
        action_type=action_type, 
        action_id=action_id
    ).exists()


def log_action(user, action_type, action_id):
    """Log that user has performed an action"""
    ActionLog.objects.create(
        user=user,
        action_type=action_type,
        action_id=action_id
    )


def award_points(user, action, reason="", action_id=None):
    """
    Award points to a user for a specific action with duplicate prevention
    
    Args:
        user: User instance
        action: Action type (e.g., 'rate_movie', 'watch_movie', etc.)
        reason: Optional reason for the points
        action_id: Unique identifier for the action (e.g., movie imdbID)
    """
    if action not in POINT_VALUES:
        return False
    
    # Check for duplicate action if action_id is provided
    if action_id and has_performed_action(user, action, action_id):
        return False  # Already awarded points for this action
    
    points = POINT_VALUES[action]
    user_points = get_or_create_user_points(user)
    
    # Update the relevant counter
    if action == 'rate_movie':
        user_points.movies_rated += 1
    elif action == 'watch_movie':
        user_points.movies_watched += 1
    elif action == 'create_list':
        user_points.lists_created += 1
    elif action == 'make_comment':
        user_points.comments_made += 1
    
    # Add points and check for badges
    user_points.add_points(points, reason)
    user_points.save()
    
    # Log the action to prevent duplicates
    if action_id:
        log_action(user, action, action_id)
    
    # Check for new badges
    check_and_award_badges(user)
    
    return True


def check_and_award_badges(user):
    """Check if user qualifies for new badges and award them"""
    user_points = get_or_create_user_points(user)
    new_badges = []
    
    for badge_type, requirements in BADGE_REQUIREMENTS.items():
        if user_points.qualifies_for_badge(badge_type):
            badge, created = Badge.objects.get_or_create(
                badge_type=badge_type,
                defaults={
                    'name': requirements['name'],
                    'description': requirements['description'],
                    'icon': requirements['icon'],
                    'color': requirements['color']
                }
            )
            
            user_badge, created = UserBadge.objects.get_or_create(
                user=user, 
                badge=badge
            )
            
            if created:
                # Award bonus points for earning the badge
                bonus_points = requirements.get('points', 0)
                if bonus_points > 0:
                    user_points.add_points(bonus_points, f"Badge bonus: {badge.name}")
                
                new_badges.append(badge)
    
    return new_badges


def get_user_stats(user):
    """Get comprehensive user statistics including level information"""
    user_points = get_or_create_user_points(user)
    level_info = user_points.get_level_info()
    
    return {
        'total_points': user_points.total_points,
        'movies_rated': user_points.movies_rated,
        'movies_watched': user_points.movies_watched,
        'lists_created': user_points.lists_created,
        'comments_made': user_points.comments_made,
        'badges_earned': user.badges.count(),
        'total_badges': Badge.objects.count(),
        'level_info': level_info,
    }


def get_user_badges(user):
    """Get all badges earned by a user"""
    return UserBadge.objects.filter(user=user).select_related('badge').order_by('-earned_at')


def get_available_badges():
    """Get all available badges"""
    return Badge.objects.all().order_by('badge_type')


def get_user_progress(user):
    """Get user's progress towards next badges"""
    user_points = get_or_create_user_points(user)
    progress = {}
    
    for badge_type, requirements in BADGE_REQUIREMENTS.items():
        # Skip if user already has this badge
        if UserBadge.objects.filter(user=user, badge__badge_type=badge_type).exists():
            continue
        
        badge_progress = {}
        for field, required_value in requirements['requirements'].items():
            if hasattr(user_points, field):
                current_value = getattr(user_points, field)
                progress_percentage = min(100, (current_value / required_value) * 100)
                badge_progress[field] = {
                    'current': current_value,
                    'required': required_value,
                    'percentage': progress_percentage
                }
        
        if badge_progress:
            progress[badge_type] = {
                'name': requirements['name'],
                'description': requirements['description'],
                'progress': badge_progress
            }
    
    return progress


def get_leaderboard(limit=10):
    """Get top users by points"""
    return UserPoints.objects.select_related('user').order_by('-total_points')[:limit]


def get_recent_activity(user, limit=10):
    """Get recent point activity for a user"""
    from .models import PointLog
    return PointLog.objects.filter(user=user).order_by('-timestamp')[:limit]


def get_user_level_info(user):
    """Get detailed level information for a user"""
    user_points = get_or_create_user_points(user)
    return user_points.get_level_info()
