from django.db import models
from django.contrib.auth.models import User
from solar_training.models import Course, Module, Lesson, Quiz

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    xp_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='badge_images/')
    
    def __str__(self):
        return self.name

class UserBadge(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    date_earned = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.user.username} - {self.badge.name}"

class UserProgress(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'course')

class LessonCompletion(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'lesson')

class QuizAttempt(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    max_score = models.IntegerField()
    date_attempted = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.user.username} - {self.quiz.title} - {self.score}/{self.max_score}"

class LoginStreak(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_login = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.user.username}'s streak: {self.current_streak} days"
