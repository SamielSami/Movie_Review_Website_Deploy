from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Comment
from movie.models import Review
from django.contrib.auth.models import User


@login_required
def delete_comment(request, comment_id):
	"""Delete a user's own comment"""
	try:
		comment = get_object_or_404(Comment, id=comment_id)
		
		# Check if user owns this comment
		if comment.user != request.user:
			return HttpResponseRedirect(reverse('index'))
		
		# Get the review and movie for redirect
		review = comment.review
		movie = review.movie
		
		if request.method == 'POST':
			# Delete the comment
			comment.delete()
			
			# Update comment count in review
			review.comment_count = Comment.objects.filter(review=review).count()
			review.save()
			
			# Redirect back to movie details page
			return HttpResponseRedirect(reverse('movie-details', args=[movie.imdbID]))
		else:
			# Show confirmation page
			from django.template import loader
			from django.http import HttpResponse
			
			template = loader.get_template('delete_comment_confirm.html')
			context = {
				'comment': comment,
				'movie': movie,
			}
			return HttpResponse(template.render(context, request))
		
	except (Comment.DoesNotExist, Review.DoesNotExist):
		return HttpResponseRedirect(reverse('index'))
