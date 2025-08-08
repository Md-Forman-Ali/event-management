from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch
from django.contrib import messages
from users.forms import CustomRegistrationForm, CreateGroup, LoginForm, AssignRoleForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login, logout
from events.models import Event,Rsvp,Category

# rolecheck
def is_admin(user):
    return user.groups.filter(name="Admin").exists()

def is_participant(user):
    return user.groups.filter(name='Participant').exists()

def is_organizer(user):
    return user.groups.filter(name='Organizer').exists()

def user_role(user):
    if user.is_authenticated:
        if user.groups.filter(name='Admin').exists():
            return 'Admin'
        elif user.groups.filter(name='Organizer').exists():
            return 'Organizer'
        elif user.groups.filter(name='Participant').exists():
            return 'Participant'
    return None

def sign_up(request):
    form = CustomRegistrationForm()
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password'))
            user.is_active = False 
            user.save()  
            messages.success(request, 'A Confirmation mail sent. Please check your inbox')
            return redirect('sign-in')
        else:
            print("Form is not valid")
    return render(request, 'registration/register.html', {"form": form})

def get_role(user):
    if user.groups.filter(name='Admin').exists():
        return 'admin_dashboard'  
    elif user.groups.filter(name='Organizer').exists():
        return 'organizer_dashboard'
    elif user.groups.filter(name='Participant').exists():
        return 'participant_dashboard'
    else:
        return 'home'

def sign_in(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(get_role(user))
    return render(request, 'registration/login.html', {'form': form})

@login_required
def sign_out(request):
    if request.method == 'POST':
        logout(request)
        return redirect('sign-in')
    return render(request, 'registration/logout.html')

def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('sign-in')
        else:
            return HttpResponse('Invalid Id or token')
    except User.DoesNotExist:
        return HttpResponse('User not found')
from django.utils import timezone
from datetime import date


@user_passes_test(is_admin, login_url='no_permission')
def admin_dashboard(request):
    today = timezone.localdate() 
    users = User.objects.prefetch_related(
        Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
    ).all()

    for user in users:
        if user.all_groups:
            user.group_name = user.all_groups[0].name 
        else:
            user.group_name = "No Group Assigned"

    total_participants = User.objects.filter(groups__name="Participant").count()
    total_events = Event.objects.count()
    upcoming_events = Event.objects.filter(date__gt=today).count()
    past_events = Event.objects.filter(date__lt=today).count()
    todays_events = Event.objects.filter(date=today)
    show_event = Event.objects.all()

    role = user_role(request.user)

    context = {
        "users": users,
        "user_role": role,
        "total_participants": total_participants,
        "total_events": total_events,
        "upcoming_events": upcoming_events,
        "past_events": past_events,
        "todays_events": todays_events,
        "show_event": show_event,
    }

    return render(request, "dashboard/admin_dashboard.html", context)


@user_passes_test(is_organizer, login_url='no_permission')
def organizer_dashboard(request):
    role = user_role(request.user)
    return render(request, 'dashboard/organizer_dashboard.html', {"user_role": role})

@user_passes_test(is_participant, login_url='no_permission')
def participant_dashboard(request):
    rsvp_events = Event.objects.filter(rsvp__user=request.user)
    return render(request, 'dashboard/participant_dashboard.html', {'rsvp_events': rsvp_events})


@user_passes_test(is_admin, login_url='no_permission')
def assign_role(request, user_id):
    user = User.objects.get(id=user_id)
    form = AssignRoleForm()
    if request.method == "POST":
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            user.groups.clear()
            user.groups.add(role)
            messages.success(request, f"User {user.username} has been assigned to the {role.name}")
            return redirect('admin_dashboard')
    return render(request,'admin/assign_role.html', {"form": form})

@user_passes_test(is_admin, login_url='no_permission')
def create_group(request):
    form = CreateGroup()
    if request.method == "POST":
        form = CreateGroup(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group {group.name} has been created Successfully")
            return redirect('create_group')
    return render(request, 'admin/create_group.html', {"form": form})

@user_passes_test(is_admin, login_url='no_permission')
def group_list(request):
    groups = Group.objects.prefetch_related('permissions').all()
    return render(request,'admin/group_list.html', {'groups': groups})
def user_list(request):
    users = User.objects.all()
    return render(request, 'admin/user_list.html', {'users': users})

