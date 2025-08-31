from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class UserPoints(models.Model):
    """Model to track user points and achievements"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='points')
    total_points = models.PositiveIntegerField(default=0)
    movies_rated = models.PositiveIntegerField(default=0)
    movies_watched = models.PositiveIntegerField(default=0)
    lists_created = models.PositiveIntegerField(default=0)
    comments_made = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "User Points"
    
    def __str__(self):
        return f"{self.user.username} - {self.total_points} points"
    
    def get_level_info(self):
        """Get current level and progress information"""
        from .badges import LEVEL_THRESHOLDS
        
        current_level = 1
        for level, threshold in LEVEL_THRESHOLDS.items():
            if self.total_points >= threshold['min_points'] and self.total_points <= threshold['max_points']:
                current_level = level
                break
        
        level_info = LEVEL_THRESHOLDS[current_level]
        next_level = current_level + 1
        
        if next_level in LEVEL_THRESHOLDS:
            next_level_info = LEVEL_THRESHOLDS[next_level]
            points_needed = next_level_info['min_points'] - self.total_points
            progress_percentage = min(100, ((self.total_points - level_info['min_points']) / 
                                          (next_level_info['min_points'] - level_info['min_points'])) * 100)
        else:
            # Max level reached
            points_needed = 0
            progress_percentage = 100
        
        return {
            'current_level': current_level,
            'level_name': level_info['name'],
            'next_level': next_level if next_level in LEVEL_THRESHOLDS else None,
            'next_level_name': LEVEL_THRESHOLDS.get(next_level, {}).get('name', 'Max Level'),
            'points_needed': points_needed,
            'progress_percentage': progress_percentage,
            'current_points': self.total_points,
            'level_min_points': level_info['min_points'],
            'level_max_points': level_info['max_points'],
        }
    
    def add_points(self, points, reason=""):
        """Add points to user and log the action"""
        self.total_points += points
        self.save()
        
        # Create a point log entry
        PointLog.objects.create(
            user=self.user,
            points=points,
            reason=reason,
            total_after=self.total_points
        )
    
    def check_and_award_badges(self):
        """Check if user qualifies for new badges based on current stats"""
        from .badges import BADGE_REQUIREMENTS
        
        for badge_type, requirements in BADGE_REQUIREMENTS.items():
            if self.qualifies_for_badge(badge_type):
                badge, created = Badge.objects.get_or_create(
                    badge_type=badge_type,
                    defaults={'name': requirements['name'], 'description': requirements['description']}
                )
                UserBadge.objects.get_or_create(user=self.user, badge=badge)
    
    def qualifies_for_badge(self, badge_type):
        """Check if user qualifies for a specific badge"""
        from .badges import BADGE_REQUIREMENTS
        
        if badge_type not in BADGE_REQUIREMENTS:
            return False
            
        requirements = BADGE_REQUIREMENTS[badge_type]
        
        # Check if user already has this badge
        if UserBadge.objects.filter(user=self.user, badge__badge_type=badge_type).exists():
            return False
        
        # Check requirements
        for field, required_value in requirements['requirements'].items():
            if hasattr(self, field):
                if getattr(self, field) < required_value:
                    return False
            else:
                return False
        
        return True


class PointLog(models.Model):
    """Log of all point transactions for audit trail"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_logs')
    points = models.IntegerField()  # Can be negative for point deductions
    reason = models.CharField(max_length=200)
    total_after = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username}: {self.points:+d} points ({self.reason})"


class Badge(models.Model):
    """Badge definitions"""
    BADGE_TYPES = [
        ('first_rating', 'First Rating'),
        ('rating_milestone_5', '5 Movies Rated'),
        ('rating_milestone_10', '10 Movies Rated'),
        ('rating_milestone_25', '25 Movies Rated'),
        ('rating_milestone_50', '50 Movies Rated'),
        ('rating_milestone_100', '100 Movies Rated'),
        ('first_watch', 'First Movie Watched'),
        ('watch_milestone_5', '5 Movies Watched'),
        ('watch_milestone_10', '10 Movies Watched'),
        ('watch_milestone_25', '25 Movies Watched'),
        ('watch_milestone_50', '50 Movies Watched'),
        ('watch_milestone_100', '100 Movies Watched'),
        ('first_list', 'First List Created'),
        ('list_milestone_3', '3 Lists Created'),
        ('list_milestone_5', '5 Lists Created'),
        ('first_comment', 'First Comment'),
        ('comment_milestone_5', '5 Comments'),
        ('comment_milestone_10', '10 Comments'),
        ('comment_milestone_25', '25 Comments'),
        ('comment_milestone_50', '50 Comments'),
        ('points_milestone_100', '100 Points'),
        ('points_milestone_250', '250 Points'),
        ('points_milestone_500', '500 Points'),
        ('points_milestone_1000', '1000 Points'),
        ('level_1', 'Level 1'),
        ('level_2', 'Level 2'),
        ('level_3', 'Level 3'),
        ('level_4', 'Level 4'),
        ('level_5', 'Level 5'),
        ('level_6', 'Level 6'),
        ('level_7', 'Level 7'),
        ('level_8', 'Level 8'),
    ]
    
    badge_type = models.CharField(max_length=50, choices=BADGE_TYPES, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='star')  # Material Icons name
    color = models.CharField(max_length=7, default='#FFD700')  # Hex color
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['badge_type']
    
    def __str__(self):
        return self.name
    
    def get_icon_class(self):
        """Get CSS class for the badge icon"""
        return f"badge-icon badge-{self.badge_type.replace('_', '-')}"


class UserBadge(models.Model):
    """User's earned badges"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='users')
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'badge']
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


class ActionLog(models.Model):
    """Log of user actions to prevent duplicate point awards"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='action_logs')
    action_type = models.CharField(max_length=50)  # e.g., 'rate_movie', 'watch_movie'
    action_id = models.CharField(max_length=100)   # e.g., movie imdbID, list id, etc.
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'action_type', 'action_id']
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username}: {self.action_type} - {self.action_id}"
