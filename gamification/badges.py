"""
Badge requirements and point system configuration
"""

# Point values for different actions
POINT_VALUES = {
    'rate_movie': 10,           # Points for rating a movie
    'watch_movie': 5,           # Points for marking a movie as watched
    'create_list': 15,          # Points for creating a personal list
    'add_to_list': 2,           # Points for adding a movie to a list
    'make_comment': 5,          # Points for making a comment
    'receive_like': 1,          # Points for receiving a like on review/comment
    'receive_unlike': -1,       # Points lost for receiving an unlike
}

# Level system configuration
LEVEL_THRESHOLDS = {
    1: {'min_points': 0, 'max_points': 99, 'name': 'Novice'},
    2: {'min_points': 100, 'max_points': 249, 'name': 'Apprentice'},
    3: {'min_points': 250, 'max_points': 499, 'name': 'Enthusiast'},
    4: {'min_points': 500, 'max_points': 999, 'name': 'Expert'},
    5: {'min_points': 1000, 'max_points': 1999, 'name': 'Master'},
    6: {'min_points': 2000, 'max_points': 3999, 'name': 'Legend'},
    7: {'min_points': 4000, 'max_points': 9999, 'name': 'Mythic'},
    8: {'min_points': 10000, 'max_points': float('inf'), 'name': 'Divine'},
}

# Badge requirements and definitions
BADGE_REQUIREMENTS = {
    # Rating badges
    'first_rating': {
        'name': 'First Critic',
        'description': 'Rated your first movie',
        'requirements': {'movies_rated': 1},
        'points': 25,
        'icon': 'star',
        'color': '#FFD700'
    },
    'rating_milestone_5': {
        'name': 'Movie Critic',
        'description': 'Rated 5 movies',
        'requirements': {'movies_rated': 5},
        'points': 50,
        'icon': 'star_rate',
        'color': '#FFA500'
    },
    'rating_milestone_10': {
        'name': 'Film Enthusiast',
        'description': 'Rated 10 movies',
        'requirements': {'movies_rated': 10},
        'points': 100,
        'icon': 'stars',
        'color': '#FF6347'
    },
    'rating_milestone_25': {
        'name': 'Cinema Expert',
        'description': 'Rated 25 movies',
        'requirements': {'movies_rated': 25},
        'points': 200,
        'icon': 'star_half',
        'color': '#9370DB'
    },
    'rating_milestone_50': {
        'name': 'Movie Master',
        'description': 'Rated 50 movies',
        'requirements': {'movies_rated': 50},
        'points': 400,
        'icon': 'star_border',
        'color': '#32CD32'
    },
    'rating_milestone_100': {
        'name': 'Legendary Critic',
        'description': 'Rated 100 movies',
        'requirements': {'movies_rated': 100},
        'points': 1000,
        'icon': 'star_purple500',
        'color': '#FF1493'
    },
    
    # Watching badges
    'first_watch': {
        'name': 'First Viewer',
        'description': 'Watched your first movie',
        'requirements': {'movies_watched': 1},
        'points': 20,
        'icon': 'visibility',
        'color': '#87CEEB'
    },
    'watch_milestone_5': {
        'name': 'Movie Watcher',
        'description': 'Watched 5 movies',
        'requirements': {'movies_watched': 5},
        'points': 40,
        'icon': 'visibility',
        'color': '#4682B4'
    },
    'watch_milestone_10': {
        'name': 'Film Viewer',
        'description': 'Watched 10 movies',
        'requirements': {'movies_watched': 10},
        'points': 80,
        'icon': 'visibility',
        'color': '#191970'
    },
    'watch_milestone_25': {
        'name': 'Cinema Goer',
        'description': 'Watched 25 movies',
        'requirements': {'movies_watched': 25},
        'points': 150,
        'icon': 'visibility',
        'color': '#4B0082'
    },
    'watch_milestone_50': {
        'name': 'Movie Marathoner',
        'description': 'Watched 50 movies',
        'requirements': {'movies_watched': 50},
        'points': 300,
        'icon': 'visibility',
        'color': '#8A2BE2'
    },
    'watch_milestone_100': {
        'name': 'Ultimate Viewer',
        'description': 'Watched 100 movies',
        'requirements': {'movies_watched': 100},
        'points': 800,
        'icon': 'visibility',
        'color': '#FF00FF'
    },
    
    # List creation badges
    'first_list': {
        'name': 'List Creator',
        'description': 'Created your first personal list',
        'requirements': {'lists_created': 1},
        'points': 30,
        'icon': 'playlist_add',
        'color': '#90EE90'
    },
    'list_milestone_3': {
        'name': 'List Organizer',
        'description': 'Created 3 personal lists',
        'requirements': {'lists_created': 3},
        'points': 60,
        'icon': 'playlist_add_check',
        'color': '#228B22'
    },
    'list_milestone_5': {
        'name': 'List Master',
        'description': 'Created 5 personal lists',
        'requirements': {'lists_created': 5},
        'points': 120,
        'icon': 'playlist_play',
        'color': '#006400'
    },
    
    # Comment badges
    'first_comment': {
        'name': 'First Commenter',
        'description': 'Made your first comment',
        'requirements': {'comments_made': 1},
        'points': 15,
        'icon': 'comment',
        'color': '#98FB98'
    },
    'comment_milestone_5': {
        'name': 'Active Commenter',
        'description': 'Made 5 comments',
        'requirements': {'comments_made': 5},
        'points': 30,
        'icon': 'comment',
        'color': '#00FF7F'
    },
    'comment_milestone_10': {
        'name': 'Discussion Starter',
        'description': 'Made 10 comments',
        'requirements': {'comments_made': 10},
        'points': 60,
        'icon': 'forum',
        'color': '#00CED1'
    },
    'comment_milestone_25': {
        'name': 'Community Voice',
        'description': 'Made 25 comments',
        'requirements': {'comments_made': 25},
        'points': 120,
        'icon': 'forum',
        'color': '#20B2AA'
    },
    'comment_milestone_50': {
        'name': 'Discussion Leader',
        'description': 'Made 50 comments',
        'requirements': {'comments_made': 50},
        'points': 250,
        'icon': 'forum',
        'color': '#008B8B'
    },
    
    # Points milestone badges
    'points_milestone_100': {
        'name': 'Point Collector',
        'description': 'Earned 100 points',
        'requirements': {'total_points': 100},
        'points': 50,
        'icon': 'emoji_events',
        'color': '#FFD700'
    },
    'points_milestone_250': {
        'name': 'Point Hunter',
        'description': 'Earned 250 points',
        'requirements': {'total_points': 250},
        'points': 100,
        'icon': 'emoji_events',
        'color': '#C0C0C0'
    },
    'points_milestone_500': {
        'name': 'Point Champion',
        'description': 'Earned 500 points',
        'requirements': {'total_points': 500},
        'points': 200,
        'icon': 'emoji_events',
        'color': '#CD7F32'
    },
    'points_milestone_1000': {
        'name': 'Point Legend',
        'description': 'Earned 1000 points',
        'requirements': {'total_points': 1000},
        'points': 500,
        'icon': 'emoji_events',
        'color': '#FF1493'
    },
    
    # Level badges
    'level_1': {
        'name': 'Novice',
        'description': 'Reached Level 1',
        'requirements': {'total_points': 0},
        'points': 0,
        'icon': 'grade',
        'color': '#B0B0B0'
    },
    'level_2': {
        'name': 'Apprentice',
        'description': 'Reached Level 2',
        'requirements': {'total_points': 100},
        'points': 50,
        'icon': 'grade',
        'color': '#CD7F32'
    },
    'level_3': {
        'name': 'Enthusiast',
        'description': 'Reached Level 3',
        'requirements': {'total_points': 250},
        'points': 100,
        'icon': 'grade',
        'color': '#C0C0C0'
    },
    'level_4': {
        'name': 'Expert',
        'description': 'Reached Level 4',
        'requirements': {'total_points': 500},
        'points': 200,
        'icon': 'grade',
        'color': '#FFD700'
    },
    'level_5': {
        'name': 'Master',
        'description': 'Reached Level 5',
        'requirements': {'total_points': 1000},
        'points': 500,
        'icon': 'grade',
        'color': '#FF1493'
    },
    'level_6': {
        'name': 'Legend',
        'description': 'Reached Level 6',
        'requirements': {'total_points': 2000},
        'points': 1000,
        'icon': 'grade',
        'color': '#FF00FF'
    },
    'level_7': {
        'name': 'Mythic',
        'description': 'Reached Level 7',
        'requirements': {'total_points': 4000},
        'points': 2000,
        'icon': 'grade',
        'color': '#8A2BE2'
    },
    'level_8': {
        'name': 'Divine',
        'description': 'Reached Level 8',
        'requirements': {'total_points': 10000},
        'points': 5000,
        'icon': 'grade',
        'color': '#FFD700'
    },
}
