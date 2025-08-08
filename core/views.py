from django.shortcuts import render,redirect

# Create your views here.
def no_permission(request):
    return render(request, 'no_permission.html')
from django.shortcuts import render

def user_role(user):
    if user.is_authenticated:
        if user.groups.filter(name='Admin').exists():
            return 'Admin'
        elif user.groups.filter(name='Organizer').exists():
            return 'Organizer'
        elif user.groups.filter(name='Participant').exists():
            return 'Participant'
    return None

def home(request):
    role = user_role(request.user)
    return render(request, 'home.html', {'user_role': role})