from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .models import Course, Module, Lesson, Quiz, Question
from gamification.models import UserProfile, UserProgress, LessonCompletion, QuizAttempt

# Add this new view
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a user profile for gamification
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def course_list(request):
    courses = Course.objects.all().order_by('order')
    return render(request, 'solar_training/course_list.html', {'courses': courses})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    modules = course.modules.all().order_by('order')
    
    # Get or create user progress
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    progress, created = UserProgress.objects.get_or_create(user=user_profile, course=course)
    
    context = {
        'course': course,
        'modules': modules,
        'progress': progress
    }
    
    return render(request, 'solar_training/course_detail.html', context)

@login_required
def lesson_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Mark lesson as accessed
    completion, created = LessonCompletion.objects.get_or_create(user=user_profile, lesson=lesson)
    
    # Check if there's a quiz for this lesson
    has_quiz = hasattr(lesson, 'quiz')
    
    context = {
        'lesson': lesson,
        'module': lesson.module,
        'course': lesson.module.course,
        'has_quiz': has_quiz,
        'completed': completion.completed
    }
    
    return render(request, 'solar_training/lesson_view.html', context)

# Add this function to check for course completion
def check_course_completion(user_profile, lesson):
    """Check if all lessons in a course have been completed"""
    module = lesson.module
    course = module.course
    
    # Get all lessons in this course
    course_lessons = Lesson.objects.filter(module__course=course)
    completed_lessons = LessonCompletion.objects.filter(
        user=user_profile,
        lesson__in=course_lessons,
        completed=True
    )
    
    # If all lessons are completed, mark the course as completed
    if completed_lessons.count() == course_lessons.count():
        progress, created = UserProgress.objects.get_or_create(
            user=user_profile,
            course=course
        )
        
        # If this is the first time completing the course, award XP
        if not progress.completed:
            progress.completed = True
            progress.save()
            
            # Award XP for course completion (100 XP bonus)
            user_profile.xp_points += 100
            user_profile.save()
            
            return True
    
    return False

@login_required
def complete_lesson(request, lesson_id):
    if request.method == 'POST':
        lesson = get_object_or_404(Lesson, id=lesson_id)
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Mark lesson as completed
        completion, created = LessonCompletion.objects.get_or_create(user=user_profile, lesson=lesson)
        
        # Only award XP if this is the first time completing
        if not completion.completed:
            completion.completed = True
            completion.save()
            
            # Award XP points
            user_profile.xp_points += 10  # Award 10 XP for completing a lesson
            user_profile.save()
            
            # Check if this completes a course
            course_completed = check_course_completion(user_profile, lesson)
            if course_completed:
                messages.success(
                    request, 
                    f"🎉 Congratulations! You've completed the entire course '{lesson.module.course.title}'!"
                )
            
        return redirect('lesson_view', lesson_id=lesson_id)
    
    return redirect('lesson_view', lesson_id=lesson_id)

@login_required
def quiz_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'lesson': quiz.lesson,
        'module': quiz.lesson.module,
        'course': quiz.lesson.module.course
    }
    
    return render(request, 'solar_training/quiz_view.html', context)

@login_required
def submit_quiz(request, quiz_id):
    if request.method == 'POST':
        quiz = get_object_or_404(Quiz, id=quiz_id)
        questions = quiz.questions.all()
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        score = 0
        max_score = questions.count()
        
        for question in questions:
            selected_answer_id = request.POST.get(f'question_{question.id}')
            if selected_answer_id:
                answer = question.answers.get(id=selected_answer_id)
                if answer.is_correct:
                    score += 1
        
        # Create quiz attempt record
        QuizAttempt.objects.create(
            user=user_profile,
            quiz=quiz,
            score=score,
            max_score=max_score
        )
        
        # Award XP based on performance
        xp_earned = int((score / max_score) * 50)  # Up to 50 XP for perfect score
        user_profile.xp_points += xp_earned
        
        # Check if user leveled up
        old_level = user_profile.level
        new_level = 1 + (user_profile.xp_points // 100)  # Level up every 100 XP
        user_profile.level = new_level
        user_profile.save()
        
        # Mark lesson as completed if score is passing
        if score >= (max_score / 2):  # Passing is 50%
            completion, created = LessonCompletion.objects.get_or_create(
                user=user_profile, 
                lesson=quiz.lesson
            )
            completion.completed = True
            completion.save()
        
        context = {
            'quiz': quiz,
            'score': score,
            'max_score': max_score,
            'xp_earned': xp_earned,
            'leveled_up': new_level > old_level,
            'new_level': new_level,
            'lesson': quiz.lesson
        }
        
        return render(request, 'solar_training/quiz_results.html', context)
    
    return redirect('quiz_view', quiz_id=quiz_id)
