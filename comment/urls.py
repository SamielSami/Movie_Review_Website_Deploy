from django.urls import path
from .views import delete_comment

urlpatterns = [
	path('delete/<int:comment_id>', delete_comment, name='delete-comment'),
]
