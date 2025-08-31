from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gamification.services import get_or_create_user_points, check_and_award_badges
from movie.models import Review, Movie
from authy.models import PersonalList
from comment.models import Comment
from django.db.models import Count


class Command(BaseCommand):
    help = 'Initialize badges for existing users based on their current activity'

    def handle(self, *args, **options):
        self.stdout.write('Starting badge initialization...')
        
        users_processed = 0
        badges_awarded = 0
        
        for user in User.objects.all():
            try:
                # Get or create user points
                user_points = get_or_create_user_points(user)
                
                # Calculate current stats based on existing data
                movies_rated = Review.objects.filter(user=user).count()
                movies_watched = user.profile.watched.count()
                lists_created = PersonalList.objects.filter(user=user).count()
                comments_made = Comment.objects.filter(user=user).count()
                
                # Update user points with actual data
                user_points.movies_rated = movies_rated
                user_points.movies_watched = movies_watched
                user_points.lists_created = lists_created
                user_points.comments_made = comments_made
                
                # Calculate total points based on actual activity
                from gamification.badges import POINT_VALUES
                total_points = (
                    movies_rated * POINT_VALUES['rate_movie'] +
                    movies_watched * POINT_VALUES['watch_movie'] +
                    lists_created * POINT_VALUES['create_list'] +
                    comments_made * POINT_VALUES['make_comment']
                )
                
                user_points.total_points = total_points
                user_points.save()
                
                # Check and award badges
                new_badges = check_and_award_badges(user)
                badges_awarded += len(new_badges)
                
                users_processed += 1
                
                if new_badges:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'User {user.username}: {len(new_badges)} new badges awarded'
                        )
                    )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing user {user.username}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Badge initialization complete! Processed {users_processed} users, awarded {badges_awarded} badges.'
            )
        )
