from django.urls import path

from authy.views import Signup, PasswordChange, PasswordChangeDone, EditProfile
from django.contrib.auth import views as authViews
from authy import views as authy_views


urlpatterns = [
	path('profile/edit', EditProfile, name='edit-profile'),
	path('signup/', Signup, name='signup'),
	path('login/', authViews.LoginView.as_view(template_name='registration/login.html'), name='login'),
	path('logout/', authViews.LogoutView.as_view(), name='logout'),
	path('changepassword/', PasswordChange, name='change-password'),
	path('changepassword/done', PasswordChangeDone, name='change-password-done'),
	path('passwordreset/', authViews.PasswordResetView.as_view(), name='password_reset'),
	path('passwordreset/done', authViews.PasswordResetDoneView.as_view(), name='password_reset_done'),
	path('passwordreset/<uidb64>/<token>/', authViews.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
	path('passwordreset/complete', authViews.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

	# Personal lists
	path('u/<username>/lists', authy_views.personal_lists, name='personal-lists'),
	path('u/<username>/lists/<int:list_id>', authy_views.personal_list_detail, name='personal-list-detail'),
	path('u/lists/<int:list_id>/delete', authy_views.delete_personal_list, name='delete-personal-list'),
	path('movie/<imdb_id>/add-to-list', authy_views.add_to_personal_list, name='add-to-personal-list'),
	path('u/lists/<int:list_id>/remove/<imdb_id>', authy_views.remove_from_personal_list, name='remove-from-personal-list'),
	path('u/lists/<int:list_id>/remove/<imdb_id>/ajax', authy_views.remove_from_personal_list_ajax, name='remove-from-personal-list-ajax'),
]