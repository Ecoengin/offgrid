from django.contrib import admin
from .models import UserProfile, Badge, UserBadge, UserProgress, LessonCompletion, QuizAttempt

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'xp_points', 'level')
    search_fields = ('user__username',)

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'date_earned')
    list_filter = ('badge', 'date_earned')
    search_fields = ('user__user__username', 'badge__name')

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'completed', 'last_accessed')
    list_filter = ('completed', 'course')

@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed', 'completion_date')
    list_filter = ('completed', 'lesson__module__course')

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'max_score', 'date_attempted')
    list_filter = ('quiz__lesson__module__course',)
