from django.utils import timezone
from .models import UserProfile, LoginStreak

class LoginStreakMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Check if user is authenticated
        if request.user.is_authenticated:
            today = timezone.now().date()
            
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                streak, created = LoginStreak.objects.get_or_create(user=user_profile)
                
                # If this is a new day since last login
                if streak.last_login != today:
                    # If user logged in yesterday, increment streak
                    if streak.last_login == today - timezone.timedelta(days=1):
                        streak.current_streak += 1
                    # If user missed a day, reset streak
                    elif streak.last_login and streak.last_login < today - timezone.timedelta(days=1):
                        streak.current_streak = 1
                    # If this is first login, set streak to 1
                    else:
                        streak.current_streak = 1
                    
                    # Update longest streak if needed
                    if streak.current_streak > streak.longest_streak:
                        streak.longest_streak = streak.current_streak
                    
                    # Update last login
                    streak.last_login = today
                    streak.save()
                    
                    # Award XP for login streaks at milestones
                    if streak.current_streak in [3, 5, 7, 14, 30, 60, 90]:
                        bonus_xp = streak.current_streak * 2  # 2 XP per day in streak
                        user_profile.xp_points += bonus_xp
                        user_profile.save()
                        
                        # Add to session to notify user
                        if 'streak_bonus' not in request.session:
                            request.session['streak_bonus'] = {
                                'days': streak.current_streak,
                                'xp': bonus_xp
                            }
                            
            except UserProfile.DoesNotExist:
                pass
                
        return response