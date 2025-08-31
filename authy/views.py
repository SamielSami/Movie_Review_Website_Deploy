from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.models import User
from authy.models import Profile, PersonalList
from movie.models import Movie, Review, Likes
from gamification.services import award_points
from comment.models import Comment
from comment.forms import CommentForm


from authy.forms import SignupForm, ChangePasswordForm, EditProfileForm



from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib import messages
import re
# Create your views here.


def validate_imdb_id(imdb_id):
	"""Validate IMDB ID format (tt followed by 7-8 digits)"""
	pattern = r'^tt\d{7,8}$'
	return bool(re.match(pattern, imdb_id))


def Signup(request):
	if request.method == 'POST':
		form = SignupForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			email = form.cleaned_data.get('email')
			first_name = form.cleaned_data.get('first_name')
			last_name = form.cleaned_data.get('last_name')
			password = form.cleaned_data.get('password')
			User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name, password=password)
			return redirect('login')
	else:
		form = SignupForm()

	context = {
		'form': form,
	}

	return render(request, 'registration/signup.html', context)


@login_required
def PasswordChange(request):
	user = request.user
	if request.method == 'POST':
		form = ChangePasswordForm(request.POST)
		if form.is_valid():
			new_password = form.cleaned_data.get('new_password')
			user.set_password(new_password)
			user.save()
			update_session_auth_hash(request, user)
			return redirect('change-password-done')
	else:
		form = ChangePasswordForm(instance=user)

	context = {
		'form': form,
	}

	return render(request, 'registration/change_password.html', context)


def PasswordChangeDone(request):
	return render(request, 'registration/change_password_done.html')


@login_required
def EditProfile(request):
    user = request.user
    profile = Profile.objects.get(user=user) # Use the request.user object directly

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Update the User model fields first
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')


            user.save()

            # The form handles the Profile model fields
            form.save()

            return redirect('index')
    else:
        # Pass the instance to the form for initial data
        form = EditProfileForm(instance=profile)

    context = {
        'form': form,
    }

    return render(request, 'edit_profile.html', context)


def UserProfile(request, username):
	user = get_object_or_404(User, username=username)
	profile = Profile.objects.get(user=user)

	#MovieBoxData
	mWatched_count = profile.watched.filter(Type='movie').count()
	sWatched_count = profile.watched.filter(Type='series').count()
	watch_list_count = profile.to_watch.all().count()
	m_reviewd_count = Review.objects.filter(user=user).count()
	personal_list_count = PersonalList.objects.filter(user=user).count()

	# Gamification data
	from gamification.services import get_user_stats, get_user_badges
	user_stats = get_user_stats(user)
	user_badges = get_user_badges(user)

	context = {
		'profile': profile,
		'mWatched_count': mWatched_count,
		'sWatched_count': sWatched_count,
		'watch_list_count': watch_list_count,
		'm_reviewd_count': m_reviewd_count,
		'personal_list_count': personal_list_count,
		'user_stats': user_stats,
		'user_badges': user_badges,
	}

	template = loader.get_template('profile.html')

	return HttpResponse(template.render(context, request))


def UserProfileMoviesWatched(request, username):
	user = get_object_or_404(User, username=username)
	profile = Profile.objects.get(user=user)

	#Movies List
	movies = profile.watched.filter(Type='movie')
	paginator = Paginator(movies, 9)
	page_number = request.GET.get('page')
	movie_data = paginator.get_page(page_number)

	context = {
		'profile': profile,
		'movies': movie_data,
	}

	return render(request, 'movies_watched.html', context)


def UserProfileSeriesWatched(request, username):
	user = get_object_or_404(User, username=username)
	profile = Profile.objects.get(user=user)

	#Series List
	series = profile.watched.filter(Type='series')
	paginator = Paginator(series, 9)
	page_number = request.GET.get('page')
	series_data = paginator.get_page(page_number)

	context = {
		'profile': profile,
		'series': series_data,
	}

	return render(request, 'series_watched.html', context)


def UserProfileWatchList(request, username):
	user = get_object_or_404(User, username=username)
	profile = Profile.objects.get(user=user)

	#Movies List
	movies = profile.to_watch.all()
	paginator = Paginator(movies, 9)
	page_number = request.GET.get('page')
	movie_data = paginator.get_page(page_number)

	context = {
		'profile': profile,
		'movies': movie_data,
	}

	return render(request, 'watchlist.html', context)


def UserProfileMoviesReviewed(request, username):
	user = get_object_or_404(User, username=username)
	profile = Profile.objects.get(user=user)

	#MovieBoxData
	mWatched_count = profile.watched.filter(Type='movie').count()
	sWatched_count = profile.watched.filter(Type='series').count()
	watch_list_count = profile.to_watch.all().count()
	m_reviewd_count = Review.objects.filter(user=user).count()

	#Movies List
	movies = Review.objects.filter(user=user)
	paginator = Paginator(movies, 9)
	page_number = request.GET.get('page')
	movie_data = paginator.get_page(page_number)


	context = {
		'profile': profile,
		'mWatched_count': mWatched_count,
		'sWatched_count': sWatched_count,
		'watch_list_count': watch_list_count,
		'm_reviewd_count': m_reviewd_count,
		'movie_data': movie_data,
		'list_title': 'Reviewed',
	}

	template = loader.get_template('profile.html')

	return HttpResponse(template.render(context, request))


def ReviewDetail(request, username, imdb_id):
	user_comment = request.user
	user = get_object_or_404(User, username=username)
	movie = Movie.objects.get(imdbID=imdb_id)
	review = Review.objects.get(user=user, movie=movie)

	#Comment stuff:
	comments = Comment.objects.filter(review=review).order_by('date')

	#Comment Form stuff:
	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			comment = form.save(commit=False)
			comment.review = review
			comment.user = user_comment
			comment.save()


			# Award points for making a comment (Sadia's)
			award_points(user_comment, 'make_comment', f"Commented on {movie.Title} review", f"{movie.imdbID}_comment_{comment.id}")
				
			
			# Update comment count
			review.comment_count = Comment.objects.filter(review=review).count()
			review.save()
			
			# Redirect back to movie details page if user came from there
			referer = request.META.get('HTTP_REFERER', '')
			if 'movie-details' in referer or 'index' in referer:
				return HttpResponseRedirect(reverse('movie-details', args=[imdb_id]))
			else:
				return HttpResponseRedirect(reverse('user-review', args=[username, imdb_id]))
	else:
		form = CommentForm()


	# Check if current user can delete this review (only the review owner can delete)
	can_delete = user_comment == user

	context = {
		'review': review,
		'movie': movie,
		'comments': comments,
		'form': form,
		'can_delete': can_delete,
		'current_user': user_comment,
	}

	template = loader.get_template('movie_review.html')

	return HttpResponse(template.render(context, request))


def like(request, username, imdb_id):
	# Validate IMDB ID format
	if not validate_imdb_id(imdb_id):
		return HttpResponseRedirect(reverse('index'))
	
	# Check if user is authenticated
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('login'))
	
	try:
		user_liking = request.user
		user_review = get_object_or_404(User, username=username)
		movie = Movie.objects.get(imdbID=imdb_id)
		review = Review.objects.get(user=user_review, movie=movie)
		
		# Prevent users from liking their own reviews
		if user_liking == user_review:
			return HttpResponseRedirect(reverse('user-review', args=[username, imdb_id]))
		
		current_likes = review.likes

		liked = Likes.objects.filter(user=user_liking, review=review, type_like=2).count()

		if not liked:
			like = Likes.objects.create(user=user_liking, review=review, type_like=2)
			current_likes = current_likes + 1

		else:
			Likes.objects.filter(user=user_liking, review=review, type_like=2).delete()
			current_likes = current_likes - 1

		review.likes = current_likes
		review.save()

		# Award points for receiving a like/unlike
		if not liked:
			# User just liked the review
			award_points(user_review, 'receive_like', f"Received like on review for {movie.Title}", f"like_{review.id}_{user_liking.id}")
		else:
			# User just unliked the review
			award_points(user_review, 'receive_unlike', f"Received unlike on review for {movie.Title}", f"unlike_{review.id}_{user_liking.id}")

		# Redirect back to movie details page if user came from there
		referer = request.META.get('HTTP_REFERER', '')
		if 'movie-details' in referer or 'index' in referer:
			return HttpResponseRedirect(reverse('movie-details', args=[imdb_id]))
		else:
			return HttpResponseRedirect(reverse('user-review', args=[username, imdb_id]))
	except (User.DoesNotExist, Movie.DoesNotExist, Review.DoesNotExist):
		return HttpResponseRedirect(reverse('index'))


def unlike(request, username, imdb_id):
	# Validate IMDB ID format
	if not validate_imdb_id(imdb_id):
		return HttpResponseRedirect(reverse('index'))
	
	# Check if user is authenticated
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('login'))
	
	try:
		user_unliking = request.user
		user_review = get_object_or_404(User, username=username)
		movie = Movie.objects.get(imdbID=imdb_id)
		review = Review.objects.get(user=user_review, movie=movie)
		
		# Prevent users from disliking their own reviews
		if user_unliking == user_review:
			return HttpResponseRedirect(reverse('user-review', args=[username, imdb_id]))
		
		current_likes = review.unlikes

		liked = Likes.objects.filter(user=user_unliking, review=review, type_like=1).count()

		if not liked:
			like = Likes.objects.create(user=user_unliking, review=review, type_like=1)
			current_likes = current_likes + 1

		else:
			Likes.objects.filter(user=user_unliking, review=review, type_like=1).delete()
			current_likes = current_likes - 1

		review.unlikes = current_likes
		review.save()

		# Award points for receiving a like/unlike
		if not liked:
			# User just liked the review
			award_points(user_review, 'receive_like', f"Received like on review for {movie.Title}", f"like_{review.id}_{user_unliking.id}")
		else:
			# User just unliked the review
			award_points(user_review, 'receive_unlike', f"Received unlike on review for {movie.Title}", f"unlike_{review.id}_{user_unliking.id}")

		# Redirect back to movie details page if user came from there
		referer = request.META.get('HTTP_REFERER', '')
		if 'movie-details' in referer or 'index' in referer:
			return HttpResponseRedirect(reverse('movie-details', args=[imdb_id]))
		else:
			return HttpResponseRedirect(reverse('user-review', args=[username, imdb_id]))
	except (User.DoesNotExist, Movie.DoesNotExist, Review.DoesNotExist):
		return HttpResponseRedirect(reverse('index'))


@login_required
def personal_lists(request, username):
	user = get_object_or_404(User, username=username)
	if request.user != user:
		return HttpResponseRedirect(reverse('user-profile', args=[request.user.username]))

	if request.method == 'POST':
		name = request.POST.get('name', '').strip()
		is_private = bool(request.POST.get('is_private'))
		if name:
			if PersonalList.objects.filter(user=user).count() >= 5:
				messages.error(request, 'You have reached the maximum of 5 personal lists.')
				return HttpResponseRedirect(reverse('personal-lists', args=[username]))
			personal_list, created = PersonalList.objects.get_or_create(user=user, name=name, defaults={'is_private': is_private})
			if created:
				# Award points for creating a personal list
				award_points(user, 'create_list', f"Created list: {name}", f"list_{personal_list.id}")
				messages.success(request, 'Personal list created.')
			else:
				messages.info(request, 'List already exists.')
		return HttpResponseRedirect(reverse('personal-lists', args=[username]))

	lists = PersonalList.objects.filter(user=user)
	context = {
		'profile': user.profile,
		'lists': lists,
	}
	return render(request, 'personal_lists.html', context)


@login_required
def delete_personal_list(request, list_id):
	plist = get_object_or_404(PersonalList, id=list_id)
	if plist.user != request.user:
		return HttpResponseRedirect(reverse('personal-lists', args=[request.user.username]))
	plist.delete()
	messages.success(request, 'Personal list deleted.')
	return HttpResponseRedirect(reverse('personal-lists', args=[request.user.username]))


@login_required
def personal_list_detail(request, username, list_id):
	user = get_object_or_404(User, username=username)
	plist = get_object_or_404(PersonalList, id=list_id, user=user)
	if plist.is_private and request.user != user:
		messages.error(request, 'This list is private.')
		return HttpResponseRedirect(reverse('profile', args=[username]))
	movies = plist.movies.all()
	context = {
		'profile': user.profile,
		'plist': plist,
		'movies': movies,
	}
	return render(request, 'personal_list_detail.html', context)


@login_required
def add_to_personal_list(request, imdb_id):
	if not validate_imdb_id(imdb_id):
		return HttpResponseRedirect(reverse('index'))
	movie = get_object_or_404(Movie, imdbID=imdb_id)
	profile = request.user.profile
	if not profile.watched.filter(id=movie.id).exists():
		messages.error(request, 'You can only add movies you have marked as watched to personal lists.')
		return HttpResponseRedirect(reverse('movie-details', args=[imdb_id]))

	if request.method == 'POST':
		list_ids = request.POST.getlist('list_ids')
		added = 0
		for lid in list_ids:
			plist = PersonalList.objects.filter(id=lid, user=request.user).first()
			if plist:
				plist.movies.add(movie)
				# Award points for adding movie to list
				award_points(request.user, 'add_to_list', f"Added {movie.Title} to {plist.name}", f"add_to_list_{movie.imdbID}_{plist.id}")
				added += 1
		if added:
			messages.success(request, 'Movie added to selected list(s).')
		return HttpResponseRedirect(reverse('movie-details', args=[imdb_id]))

	lists = PersonalList.objects.filter(user=request.user)
	context = {
		'movie': movie,
		'lists': lists,
	}
	return render(request, 'choose_personal_list.html', context)


@login_required
def remove_from_personal_list(request, list_id, imdb_id):
	plist = get_object_or_404(PersonalList, id=list_id, user=request.user)
	movie = get_object_or_404(Movie, imdbID=imdb_id)
	plist.movies.remove(movie)
	messages.success(request, 'Movie removed from the list.')
	return HttpResponseRedirect(reverse('personal-list-detail', args=[request.user.username, plist.id]))

@login_required
def remove_from_personal_list_ajax(request, list_id, imdb_id):
	"""AJAX endpoint to remove movie from personal list without page redirect"""
	if request.method == 'POST':
		try:
			plist = get_object_or_404(PersonalList, id=list_id, user=request.user)
			movie = get_object_or_404(Movie, imdbID=imdb_id)
			
			# Remove from personal list
			plist.movies.remove(movie)
			
			return JsonResponse({
				'success': True,
				'message': f'"{movie.Title}" has been removed from "{plist.name}".',
				'movie_title': movie.Title,
				'list_name': plist.name
			})
		except PersonalList.DoesNotExist:
			return JsonResponse({
				'success': False,
				'message': 'Personal list not found.'
			}, status=404)
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

