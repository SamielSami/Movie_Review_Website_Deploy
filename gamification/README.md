# Gamification System

A comprehensive points and achievement system for the movie review website that rewards users for their engagement and activity.

## Features

### Points System
Users earn points for various activities:
- **Rate a movie**: 10 points
- **Watch a movie**: 5 points  
- **Create a personal list**: 15 points
- **Add movie to list**: 2 points
- **Make a comment**: 5 points
- **Receive a like**: 1 point
- **Receive an unlike**: -1 point

### Badge System
Users can earn badges for reaching milestones:

#### Rating Badges
- **First Critic**: Rate your first movie
- **Movie Critic**: Rate 5 movies
- **Film Enthusiast**: Rate 10 movies
- **Cinema Expert**: Rate 25 movies
- **Movie Master**: Rate 50 movies
- **Legendary Critic**: Rate 100 movies

#### Watching Badges
- **First Viewer**: Watch your first movie
- **Movie Watcher**: Watch 5 movies
- **Film Viewer**: Watch 10 movies
- **Cinema Goer**: Watch 25 movies
- **Movie Marathoner**: Watch 50 movies
- **Ultimate Viewer**: Watch 100 movies

#### List Creation Badges
- **List Creator**: Create your first personal list
- **List Organizer**: Create 3 personal lists
- **List Master**: Create 5 personal lists

#### Comment Badges
- **First Commenter**: Make your first comment
- **Active Commenter**: Make 5 comments
- **Discussion Starter**: Make 10 comments
- **Community Voice**: Make 25 comments
- **Discussion Leader**: Make 50 comments

#### Points Milestone Badges
- **Point Collector**: Earn 100 points
- **Point Hunter**: Earn 250 points
- **Point Champion**: Earn 500 points
- **Point Legend**: Earn 1000 points

## Usage

### For Users
1. **View your profile**: Visit your profile page to see your points and badges
2. **Gamification profile**: Click "Gamification Profile" in the dropdown menu for detailed stats
3. **Badges page**: View all available badges and your progress
4. **Leaderboard**: See how you rank against other users

### For Developers

#### Adding Points
```python
from gamification.services import award_points

# Award points for an action
award_points(user, 'rate_movie', 'Rated The Matrix')
```

#### Checking User Stats
```python
from gamification.services import get_user_stats, get_user_badges

# Get user statistics
stats = get_user_stats(user)

# Get user badges
badges = get_user_badges(user)
```

#### Available Actions
- `rate_movie`: Rating a movie
- `watch_movie`: Marking a movie as watched
- `create_list`: Creating a personal list
- `add_to_list`: Adding a movie to a list
- `make_comment`: Making a comment
- `receive_like`: Receiving a like
- `receive_unlike`: Receiving an unlike

## Database Models

### UserPoints
Tracks user points and activity counts:
- `total_points`: Total points earned
- `movies_rated`: Number of movies rated
- `movies_watched`: Number of movies watched
- `lists_created`: Number of lists created
- `comments_made`: Number of comments made

### Badge
Defines available badges with requirements and rewards.

### UserBadge
Tracks which badges each user has earned.

### PointLog
Audit trail of all point transactions.

## Management Commands

### Initialize Badges for Existing Users
```bash
python manage.py init_badges
```
This command will:
- Create UserPoints records for all users
- Calculate points based on existing activity
- Award badges based on current stats

## Templates

### Badge Display Component
Include the badge display component in any template:
```html
{% include 'gamification/badge_display.html' with user_badges=user_badges %}
```

### Badge Notifications
Include badge notifications for new badges:
```html
{% include 'gamification/badge_notification.html' with new_badges=new_badges %}
```

## URLs

- `/gamification/profile/<username>/`: User's gamification profile
- `/gamification/badges/`: All available badges
- `/gamification/leaderboard/`: User leaderboard
- `/gamification/activity/`: User activity log

## Integration

The gamification system is automatically integrated with:
- Movie rating system
- Movie watching system
- Personal list creation
- Comment system

Points are awarded automatically when users perform these actions.
