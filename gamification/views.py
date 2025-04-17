from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models  # Add this import
from datetime import timedelta
from .models import UserProfile, Badge, UserBadge, UserProgress, LessonCompletion, QuizAttempt, LoginStreak  # Add LoginStreak here
from solar_training.models import Course

def award_badge(user_profile, badge_name):
    """Award a badge to a user if they don't already have it"""
    try:
        badge = Badge.objects.get(name=badge_name)
        # Check if user already has this badge
        if not UserBadge.objects.filter(user=user_profile, badge=badge).exists():
            UserBadge.objects.create(user=user_profile, badge=badge)
            return True
    except Badge.DoesNotExist:
        pass
    return False

def check_badges(request, user_profile):
    """Check if user qualifies for any badges"""
    badges_awarded = []
    
    # First Lesson Badge
    lesson_completions = LessonCompletion.objects.filter(user=user_profile, completed=True)
    if lesson_completions.count() >= 1:
        if award_badge(user_profile, "First Step"):
            badges_awarded.append("First Step")
    
    # Course Complete Badge
    courses_completed = UserProgress.objects.filter(user=user_profile, completed=True)
    if courses_completed.count() >= 1:
        if award_badge(user_profile, "Solar Scholar"):
            badges_awarded.append("Solar Scholar")
    
    # Perfect Quiz Badge
    perfect_quizzes = QuizAttempt.objects.filter(user=user_profile, score=models.F('max_score'))
    if perfect_quizzes.count() >= 1:
        if award_badge(user_profile, "Master Mind"):
            badges_awarded.append("Master Mind")
    
    # Fast Learner Badge
    today = timezone.now().date()
    lessons_today = LessonCompletion.objects.filter(
        user=user_profile, 
        completed=True,
        completion_date__date=today
    )
    if lessons_today.count() >= 5:
        if award_badge(user_profile, "Speed Demon"):
            badges_awarded.append("Speed Demon")
    
    # Dedication Badge (requires login tracking, so just check total progress as a proxy)
    total_progress = LessonCompletion.objects.filter(user=user_profile, completed=True).count()
    if total_progress >= 10:
        if award_badge(user_profile, "Consistent Learner"):
            badges_awarded.append("Consistent Learner")
    
    # Display messages for badges earned
    for badge_name in badges_awarded:
        messages.success(request, f"🏆 Congratulations! You earned the '{badge_name}' badge!")
    
    return badges_awarded

@login_required
def dashboard(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Check for new badges
    check_badges(request, user_profile)
    
    # Get user progress
    course_progress = UserProgress.objects.filter(user=user_profile)
    courses_completed = course_progress.filter(completed=True).count()
    total_courses = Course.objects.count()
    
    # Get lessons completed
    lessons_completed = LessonCompletion.objects.filter(user=user_profile, completed=True).count()
    
    # Get badges
    badges = UserBadge.objects.filter(user=user_profile)
    
    # Get quiz performance
    quiz_attempts = QuizAttempt.objects.filter(user=user_profile)
    avg_score = 0
    if quiz_attempts.exists():
        total_score = sum(attempt.score for attempt in quiz_attempts)
        total_possible = sum(attempt.max_score for attempt in quiz_attempts)
        if total_possible > 0:
            avg_score = (total_score / total_possible) * 100
    
    # Calculate progress percentage
    completion_percentage = 0
    if total_courses > 0:
        completion_percentage = (courses_completed / total_courses) * 100
    
    context = {
        'user_profile': user_profile,
        'badges': badges,
        'courses_completed': courses_completed,
        'total_courses': total_courses,
        'lessons_completed': lessons_completed,
        'completion_percentage': completion_percentage,
        'avg_score': avg_score,
        'xp_to_next_level': (user_profile.level * 100) - user_profile.xp_points
    }
    
    return render(request, 'gamification/dashboard.html', context)

@login_required
def leaderboard(request):
    top_users = UserProfile.objects.all().order_by('-xp_points')[:20]
    
    context = {
        'top_users': top_users,
        'user_profile': UserProfile.objects.get(user=request.user)
    }
    
    return render(request, 'gamification/leaderboard.html', context)

@login_required
def claim_daily_reward(request):
    user_profile = UserProfile.objects.get(user=request.user)
    streak = LoginStreak.objects.get(user=user_profile)
    
    # Calculate reward based on streak
    base_reward = 5  # Base XP for daily login
    streak_bonus = min(streak.current_streak, 10) * 2  # Max bonus caps at 20 XP (10 days)
    total_reward = base_reward + streak_bonus
    
    # Award XP
    user_profile.xp_points += total_reward
    user_profile.save()
    
    messages.success(request, f"Daily Reward: You earned {total_reward} XP! 🎁 ({base_reward} base + {streak_bonus} streak bonus)")
    
    # Mark as claimed in session
    request.session['daily_reward_claimed'] = True
    
    return redirect('dashboard')
