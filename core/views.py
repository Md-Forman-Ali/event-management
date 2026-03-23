from django.shortcuts import render, redirect
from events.models import Event, Rsvp
from django.db.models import Count

def user_role(user):
    if user.is_authenticated:
        if user.groups.filter(name='Admin').exists():
            return 'Admin'
        elif user.groups.filter(name='Organizer').exists():
            return 'Organizer'
        elif user.groups.filter(name='Participant').exists():
            return 'Participant'
    return None

def no_permission(request):
    return render(request, 'no_permission.html')

def home(request):
    role = user_role(request.user)
    
    # Dynamic content for the stunning home page
    featured_events = Event.objects.select_related('category').annotate(
        participant_count=Count('rsvp')
    ).order_by('-date')[:3]
    
    total_events = Event.objects.count()
    total_participants = Rsvp.objects.values('user').distinct().count()
    
    context = {
        'user_role': role,
        'featured_events': featured_events,
        'total_events_count': total_events,
        'total_participants_count': total_participants,
    }
    
    return render(request, 'home.html', context)