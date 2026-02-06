from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Task, CustomUser
from .forms import RegistrationForm, LoginForm, TaskForm

def landing_page(request):
    return render(request, 'todo_app/landing.html')

def is_admin(user):
    return user.is_superuser

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # User can be active but needs approval
            user.is_approved = False
            user.save()
            messages.success(request, 'Registration successful. Please wait for admin approval.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'todo_app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_approved or user.is_superuser:
                    login(request, user)
                    return redirect('task_list')
                else:
                    messages.error(request, 'Your account is pending approval.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'todo_app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def task_list(request):
    tasks = Task.objects.all()
    return render(request, 'todo_app/task_list.html', {'tasks': tasks})

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            messages.success(request, 'Task created successfully.')
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'todo_app/task_form.html', {'form': form, 'title': 'Create Task'})

@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully.')
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'todo_app/task_form.html', {'form': form, 'title': 'Edit Task'})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully.')
        return redirect('task_list')
    return render(request, 'todo_app/task_confirm_delete.html', {'task': task})

@user_passes_test(is_admin)
def admin_dashboard(request):
    unapproved_users = CustomUser.objects.filter(is_approved=False, is_superuser=False)
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = get_object_or_404(CustomUser, id=user_id)
        if action == 'approve':
            user.is_approved = True
            user.save()
            messages.success(request, f'User {user.username} approved.')
        elif action == 'reject':
            user.delete()
            messages.success(request, f'User {user.username} rejected.')
        return redirect('admin_dashboard')
    return render(request, 'todo_app/admin_dashboard.html', {'users': unapproved_users})
