from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('lesson/<int:lesson_id>/', views.lesson_view, name='lesson_view'),
    path('lesson/<int:lesson_id>/complete/', views.complete_lesson, name='complete_lesson'),
    path('quiz/<int:quiz_id>/', views.quiz_view, name='quiz_view'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
]