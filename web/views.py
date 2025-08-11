from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import EditProfileForm
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from .forms import CustomLoginForm
from datetime import datetime
from .models import Schedule
from datetime import date
from django.shortcuts import redirect, get_object_or_404
from django.utils.timezone import localtime
from django.utils import timezone
from collections import defaultdict
from django.utils.timezone import now
from .models import Schedule, History
from itertools import chain






class CustomLoginView(LoginView):

    template_name = 'login.html'

class MyPasswordChangeView(PasswordChangeView):
    template_name = 'change_password.html'
    success_url = reverse_lazy('change_password') 

    def form_valid(self, form):
        messages.success(self.request, 'Your password was successfully updated!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the error below.')
        return super().form_invalid(form)
    
    
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")  # or wherever you want to redirect
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})

from django.contrib.auth import authenticate, login

def login_view(request):
    form = CustomLoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect('dashboard')  # or wherever you want
    return render(request, 'login.html', {'form': form})


from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    logout(request)
    return redirect('login')  
 

@login_required
def account_view(request):
    return render(request, 'account.html')

@login_required
def my_account(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('my_account') 
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EditProfileForm(instance=request.user)  # preload with current user data

    return render(request, 'myaccount.html', {'form': form})

def logout_confirm(request):
    return render(request, 'logout_confirm.html')

@login_required
def dashboard(request):
    now = timezone.localtime()
    today = now.date()
    current_time = now.time()

    # --- Step 1: Handle past schedules ---
    past_schedules = Schedule.objects.filter(user=request.user
    ).filter(
        date__lt=today
    ) | Schedule.objects.filter(
        user=request.user,
        date=today,
        end_time__lt=current_time
    )

    # Save to History before deleting
    for task in past_schedules:
        History.objects.create(
            user=request.user,
            date=task.date,
            subject=task.subject,
            start_time=task.start_time,
            end_time=task.end_time,
            deleted_at=timezone.now()
        )

    # Delete past schedules
    past_schedules.delete()

    # --- Step 2: Current month range ---
    start_month = today.replace(day=1)
    if today.month == 12:
        end_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        end_month = today.replace(month=today.month + 1, day=1)

    # --- Step 3: Only upcoming schedules ---
    schedules = Schedule.objects.filter(
        user=request.user,
        date__gte=today,
        date__lt=end_month
    ).order_by('date', 'start_time')

    return render(request, 'dashboard.html', {'schedules': schedules})




@login_required
def add_schedule(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        Schedule.objects.create(
            user=request.user,
            subject=subject,
            date=date,
            start_time=start_time,
            end_time=end_time
        )

        return redirect('dashboard')  
    return render(request, 'add_schedule.html')  

def delete_task(request, task_id):
    task = get_object_or_404(Schedule, id=task_id)

    # Save to history before deleting
    History.objects.create(
        user=request.user,  # ✅ store the user
        date=task.date,
        subject=task.subject,
        start_time=task.start_time,
        end_time=task.end_time,
        deleted_at=timezone.now()  # ✅ track when it was deleted
    )

    task.delete()
    return redirect('schedule_list')


@login_required
def schedule_view(request):
    print("Logged in user:", request.user)
    print("Is authenticated:", request.user.is_authenticated)

    schedules = Schedule.objects.filter(user=request.user).order_by('date', 'start_time')

    grouped_schedules = defaultdict(list)
    for schedule in schedules:
        month_label = schedule.date.strftime('%B %Y')
        grouped_schedules[month_label].append(schedule)

    return render(request, 'schedule_list.html', {
        'grouped_schedules': dict(grouped_schedules)
    })


def cleanup_schedules():
    now = timezone.localtime()
    today = now.date()

    Schedule.objects.filter(
        date__lt=today
    ).delete()

    Schedule.objects.filter(
        date=today, end_time__lt=now.time()
    ).delete()

def history_view(request):
   timezone.activate('Asia/Manila')
   history_items = History.objects.filter(user=request.user).order_by('-deleted_at')
   return render(request, 'history.html', {'history_items': history_items})

@login_required
def delete_all_history(request):
     if request.method == "POST":
        History.objects.filter(user=request.user).delete()  # ✅ only delete current user's history
        return redirect('history')
     return redirect('history')


def edit_task(request, task_id):
    task = get_object_or_404(Schedule, id=task_id)

    if request.method == "POST":
        task.subject = request.POST.get("subject")
        task.date = request.POST.get("date")
        task.start_time = request.POST.get("start_time")
        task.end_time = request.POST.get("end_time")
        task.save()

        messages.success(request, "Task successfully updated!")
        return redirect('edit_task', task_id=task.id)

    return render(request, "edit_task.html", {"task": task})

@login_required
def delete_selected_history(request):
    if request.method == "POST":
        ids = request.POST.getlist('selected_items')
        History.objects.filter(id__in=ids, user=request.user).delete()
    return redirect('history')