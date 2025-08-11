from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.contrib import admin
from django.shortcuts import redirect
from .views import custom_logout
from .views import MyPasswordChangeView
from django.contrib.auth import views as auth_views






urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login')),  # redirect / to login
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout-confirm/', views.logout_confirm, name='logout_confirm'),
    path('logout/', custom_logout, name='logout'),
    path('account/', views.account_view, name='account'),
    path('account/edit/', views.my_account, name='my_account'),
    path('change-password/', MyPasswordChangeView.as_view(), name='change_password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('schedule/', views.schedule_view, name='schedule_list'),
    path('add-schedule/', views.add_schedule, name='add_schedule'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('history/', views.history_view, name='history'),
    path('history/delete_all/', views.delete_all_history, name='delete_all_history'),
    path('edit-task/<int:task_id>/', views.edit_task, name='edit_task'),
    path('history/delete-selected/', views.delete_selected_history, name='delete_selected_history'),

    

    path('reset-password/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
] 



