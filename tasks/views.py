from django.shortcuts import render, get_object_or_404, redirect
from .models import Task
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'completed']

def is_admin(user):
    "Check if the user is an admin/superuser."
    return user.is_authenticated and user.is_staff

#registration view
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = UserCreationForm()
    return render(request, 'tasks/register.html', {'form': form})

#login view
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user=form.get_user()
            login(request, user)
            return redirect('task_list')
    else:
        form = AuthenticationForm()
    return render(request, 'tasks/login.html', {'form': form})


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False) #create task object but don't save to database yet
            task.user = request.user #assign current user to task
            task.save() #save task to database
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_list.html', {'form': form})

@login_required
def task_update(request, id):
    if is_admin(request.user):
        task = get_object_or_404(Task, id=id) #admin can update any task
    else:
        task = get_object_or_404(Task, id=id, user=request.user) #ensure user can only update their own tasks
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_list.html', {'form': form})

@login_required
def tasks_delete(request, id):
    if is_admin(request.user):
        task = get_object_or_404(Task, id=id) #admin can delete any task
    else:
        task = get_object_or_404(Task, id=id, user=request.user) #ensure user can only delete their own tasks
    task.delete()
    return redirect('task_list')

# Create your views here.
@login_required
def task_list(request):
    if is_admin(request.user):
        tasks = Task.objects.all() #admin can see all tasks
        is_admin_view = True
    else:
        tasks = Task.objects.filter(user=request.user)
        is_admin_view = False
    return render(request, 'tasks/task_list.html', {'tasks': tasks, 'is_admin_view': is_admin_view})

def user_logout(request):
    logout(request)
    return redirect('login')