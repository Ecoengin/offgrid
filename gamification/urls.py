from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('claim-daily-reward/', views.claim_daily_reward, name='claim_daily_reward'),
]