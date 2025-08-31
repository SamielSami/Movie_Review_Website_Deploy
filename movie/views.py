from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.utils.text import slugify
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Avg

from movie.models import Movie, Genre, Rating, Review
from actor.models import Actor
from authy.models import Profile
from django.contrib.auth.models import User
from gamification.services import award_points


from movie.forms import RateForm

import requests
import re


def validate_imdb_id(imdb_id):
	"""Validate IMDB ID format (tt followed by 7-8 digits)"""
	pattern = r'^tt\d{7,8}$'
	return bool(re.match(pattern, imdb_id))


# Create your views here.
def index(request):
	query = request.GET.get('q')

	if query:
		url = 'http://www.omdbapi.com/?apikey=4eb57329&s=' + query
		response = requests.get(url)
		movie_data = response.json()
		if "Search" in movie_data:
			movie_data["Search"] = movie_data["Search"][:9]  # only first 9 movies

		context = {
			'query': query,
			'movie_data': movie_data,
			'page_number': 1,
		}

		template = loader.get_template('search_results.html')

		return HttpResponse(template.render(context, request))

	return render(request, 'index.html')


def pagination(request, query, page_number):
    page_number = int(page_number)
    url = f'http://www.omdbapi.com/?apikey=4eb57329&s={query}&page={page_number}'
    response = requests.get(url)
    movie_data = response.json()
    if "Search" in movie_data:
        movie_data["Search"] = movie_data["Search"][:9]  # only first 9 movies

    context = {
        'query': query,
        'movie_data': movie_data,
        'page_number': page_number,  # keep current page number
    }

    template = loader.get_template('search_results.html')
    return HttpResponse(template.render(context, request))

def movieDetails(request, imdb_id):
	# Validate IMDB ID format
	if not validate_imdb_id(imdb_id):
		return HttpResponseRedirect(reverse('index'))

	if Movie.objects.filter(imdbID=imdb_id).exists():
		movie_data = Movie.objects.get(imdbID=imdb_id)
		reviews = Review.objects.filter(movie=movie_data).select_related('user', 'user__profile').prefetch_related('comments__user', 'comments__user__profile')
		reviews_avg = reviews.aggregate(Avg('rate'))
		reviews_count = reviews.count()
		our_db = True

		# Check if current user has already reviewed this movie
		user_has_reviewed = False
		current_user = None
		
		if request.user.is_authenticated:
			current_user = request.user
			profile = Profile.objects.get(user=current_user)
			user_has_reviewed = Review.objects.filter(user=request.user, movie=movie_data).exists()
			in_watchlist = profile.to_watch.filter(imdbID=imdb_id).exists()
			is_watched = profile.watched.filter(imdbID=imdb_id).exists()
		else:
			user_has_reviewed = False
			in_watchlist = False
			is_watched = False

		context = {
			'movie_data': movie_data,
			'reviews': reviews,
			'reviews_avg': reviews_avg,
			'reviews_count': reviews_count,
			'our_db': our_db,
			'user_has_reviewed': user_has_reviewed,
			'current_user': current_user,

			'in_watchlist': in_watchlist,
			'is_watched': is_watched
		}

	else:
		url = 'http://www.omdbapi.com/?apikey=4eb57329&i=' + imdb_id
		response = requests.get(url)
		movie_data = response.json()

		#Inject to our database bellow:

		rating_objs = []
		genre_objs = []
		actor_objs = []

		#For the actors
		actor_list = [x.strip() for x in movie_data['Actors'].split(',')]

		for actor in actor_list:
			a, created = Actor.objects.get_or_create(name=actor)
			actor_objs.append(a)

		#For the Genre or categories
		genre_list = list(movie_data['Genre'].replace(" ", "").split(','))

		for genre in genre_list:
			genre_slug = slugify(genre)
			g, created = Genre.objects.get_or_create(title=genre, slug=genre_slug)
			genre_objs.append(g)

		#For the Rate
		for rate in movie_data['Ratings']:
			r, created = Rating.objects.get_or_create(source=rate['Source'], rating=rate['Value'])
			rating_objs.append(r)

		if movie_data['Type'] == 'movie':  #update for movies
			m, created = Movie.objects.get_or_create(
				Title=movie_data['Title'],
				Year=movie_data['Year'],
				Rated=movie_data['Rated'],
				Released=movie_data['Released'],
				Runtime=movie_data['Runtime'],
				Director=movie_data['Director'],
				Writer=movie_data['Writer'],
				Plot=movie_data['Plot'],
				Language=movie_data['Language'],
				Country=movie_data['Country'],
				Awards=movie_data['Awards'],
				Poster_url=movie_data['Poster'],
				Metascore=movie_data['Metascore'],
				imdbRating=movie_data['imdbRating'],
				imdbVotes=movie_data['imdbVotes'],
				imdbID=movie_data['imdbID'],
				Type=movie_data['Type'],
				DVD=movie_data['DVD'],
				BoxOffice=movie_data['BoxOffice'],
				Production=movie_data['Production'],
				Website=movie_data['Website'],
				)
			m.Genre.set(genre_objs)
			m.Actors.set(actor_objs)
			m.Ratings.set(rating_objs)

		else:             #create
			m, created = Movie.objects.get_or_create(
				Title=movie_data['Title'],
				Year=movie_data['Year'],
				Rated=movie_data['Rated'],
				Released=movie_data['Released'],
				Runtime=movie_data['Runtime'],
				Director=movie_data['Director'],
				Writer=movie_data['Writer'],
				Plot=movie_data['Plot'],
				Language=movie_data['Language'],
				Country=movie_data['Country'],
				Awards=movie_data['Awards'],
				Poster_url=movie_data['Poster'],
				Metascore=movie_data['Metascore'],
				imdbRating=movie_data['imdbRating'],
				imdbVotes=movie_data['imdbVotes'],
				imdbID=movie_data['imdbID'],
				Type=movie_data['Type'],
				totalSeasons=movie_data['totalSeasons'],
				)

			m.Genre.set(genre_objs)
			m.Actors.set(actor_objs)
			m.Ratings.set(rating_objs)


		for actor in actor_objs:
			actor.movies.add(m)
			actor.save()

		m.save()
		our_db = False

		context = {
			'movie_data': movie_data,
			'our_db': our_db,
		}

	template = loader.get_template('movie_details.html')

	return HttpResponse(template.render(context, request))


def genres(request, genre_slug):
	genre = get_object_or_404(Genre, slug=genre_slug)
	movies = Movie.objects.filter(Genre=genre)

	#Pagination
	paginator = Paginator(movies, 9)
	page_number = request.GET.get('page')
	movie_data = paginator.get_page(page_number)

	context = {
		'movie_data': movie_data,
		'genre': genre,
	}


	template = loader.get_template('genre.html')

	return HttpResponse(template.render(context, request))


def addMoviesToWatch(request, imdb_id):
	movie = Movie.objects.get(imdbID=imdb_id)
	user = request.user
	profile = Profile.objects.get(user=user)

	profile.to_watch.add(movie)

	return HttpResponseRedirect(reverse('movie-details', args=[imdb_id]))

def addMoviesWatched(request, imdb_id):
	movie = Movie.objects.get(imdbID=imdb_id)
	user = request.user
	profile = Profile.objects.get(user=user)

	was_already_watched = profile.watched.filter(imdbID=imdb_id).exists()


	if profile.to_watch.filter(imdbID=imdb_id).exists():
		profile.to_watch.remove(movie)
		profile.watched.add(movie)
		
	else:
		profile.watched.add(movie)

	# Award points for watching a movie (only if not already watched)
	if not was_already_watched:
		award_points(user, 'watch_movie', f"Watched {movie.Title}", movie.imdbID)
	
	return HttpResponseRedirect(reverse('movie-details', args=[imdb_id]))

def removeFromWatchlist(request, imdb_id):
	movie = Movie.objects.get(imdbID=imdb_id)
	user = request.user
	profile = Profile.objects.get(user=user)

	profile.to_watch.remove(movie)

	# Redirect back to the watchlist page
	return HttpResponseRedirect(reverse('profile-watch-list', args=[user.username]))

def removeFromWatchlistAjax(request, imdb_id):
	"""AJAX endpoint to remove movie from watchlist without page redirect"""
	if request.method == 'POST':
		try:
			movie = Movie.objects.get(imdbID=imdb_id)
			user = request.user
			profile = Profile.objects.get(user=user)
			
			# Remove from watchlist
			profile.to_watch.remove(movie)
			
			return JsonResponse({
				'success': True,
				'message': f'"{movie.Title}" has been removed from your watchlist.',
				'movie_title': movie.Title
			})
		except Movie.DoesNotExist:
			return JsonResponse({
				'success': False,
				'message': 'Movie not found.'
			}, status=404)
		except Exception as e:
			return JsonResponse({
				'success': False,
				'message': 'An error occurred while removing the movie.'
			}, status=500)
	
	return JsonResponse({
		'success': False,
		'message': 'Invalid request method.'
	}, status=405)


def markAsWatchedAjax(request, imdb_id):
	"""AJAX endpoint to mark movie/series as watched and move to appropriate list"""
	if request.method == 'POST':
		try:
			movie = Movie.objects.get(imdbID=imdb_id)
			user = request.user
			profile = Profile.objects.get(user=user)
			
			# Remove from watchlist
			profile.to_watch.remove(movie)
			
			# Add to watched list
			profile.watched.add(movie)
			
			# Determine which list it was moved to
			list_name = "Movies Watched" if movie.Type.lower() == "movie" else "Series Watched"
			
			return JsonResponse({
				'success': True,
				'message': f'"{movie.Title}" has been marked as watched and moved to {list_name}.',
				'movie_title': movie.Title,
				'list_name': list_name,
				'content_type': movie.Type
			})
		except Movie.DoesNotExist:
			return JsonResponse({
				'success': False,
				'message': 'Movie not found.'
			}, status=404)
		except Exception as e:
			return JsonResponse({
				'success': False,
				'message': 'An error occurred while marking as watched.'
			}, status=500)
	
	return JsonResponse({
		'success': False,
		'message': 'Invalid request method.'
	}, status=405)


def Rate(request, imdb_id):
	# Validate IMDB ID format
	if not validate_imdb_id(imdb_id):
		return HttpResponseRedirect(reverse('index'))
	
	# Check if user is authenticated
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('login'))
	
	try:
		movie = Movie.objects.get(imdbID=imdb_id)
		user = request.user

		# Check if user already reviewed this movie
		existing_review = Review.objects.filter(user=user, movie=movie).first()
		if existing_review:
			# Redirect to movie details if user already reviewed
			return HttpResponseRedirect(reverse('movie-details', args=[imdb_id]))

		if request.method == 'POST':
			form = RateForm(request.POST)
			if form.is_valid():
				rate = form.save(commit=False)
				rate.user = user
				rate.movie = movie
				rate.save()

				# Award points for rating a movie (Sadia's)
				award_points(user, 'rate_movie', f"Rated {movie.Title}", movie.imdbID)
				

				return HttpResponseRedirect(reverse('movie-details', args=[imdb_id]))
		else:
			form = RateForm()

		template = loader.get_template('rate.html')

		context = {
			'form': form, 
			'movie': movie,
		}

		return HttpResponse(template.render(context, request))
	except Movie.DoesNotExist:
		return HttpResponseRedirect(reverse('index'))


def DeleteReview(request, imdb_id):
	"""Delete a user's own review for a movie"""
	# Validate IMDB ID format
	if not validate_imdb_id(imdb_id):
		return HttpResponseRedirect(reverse('index'))
	
	# Check if user is authenticated
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('login'))
	
	try:
		movie = Movie.objects.get(imdbID=imdb_id)
		user = request.user
		
		# Find the user's review for this movie
		review = Review.objects.filter(user=user, movie=movie).first()
		
		if not review:
			# User doesn't have a review for this movie
			return HttpResponseRedirect(reverse('movie-details', args=[imdb_id]))
		
		if request.method == 'POST':
			# Delete the review
			review.delete()
			return HttpResponseRedirect(reverse('movie-details', args=[imdb_id]))
		else:
			# Show confirmation page
			template = loader.get_template('delete_review_confirm.html')
			context = {
				'movie': movie,
				'review': review,
			}
			return HttpResponse(template.render(context, request))
			
	except Movie.DoesNotExist:
		return HttpResponseRedirect(reverse('index'))

