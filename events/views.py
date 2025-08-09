from django.shortcuts import render, redirect
from datetime import date
from events.models import Event, Category, Rsvp
from events.forms import EventModelForm, CategoryModelForm
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test


def is_participant(user):
    return user.groups.filter(name='Participant').exists()

def is_organizer(user):
    return user.groups.filter(name='Organizer').exists()

def is_admin(user):
    return user.is_superuser or user.groups.filter(name='Admin').exists()


def event_list(request):
    user = request.user
    search = request.GET.get('search', '')

    if search:
        events = Event.objects.filter(
            Q(name__icontains=search) | Q(location__icontains=search)
        ).select_related('category').prefetch_related('rsvp')
    else:
        events = Event.objects.select_related('category').prefetch_related('rsvp').all()

    if user.is_authenticated:
        for event in events:
            event.user_has_rsvped = event.rsvp.filter(user=user).exists()
    else:
        for event in events:
            event.user_has_rsvped = False

    context = {
        'events': events,
        'search': search,
    }
    return render(request, 'event_list.html', context)


def event_detail(request, id):
    try:
        event = Event.objects.get(id=id)
    except Event.DoesNotExist:
        messages.error(request, "Event not found.")
        return redirect('event_list')

    user_has_rsvped = False
    if request.user.is_authenticated:
        user_has_rsvped = Rsvp.objects.filter(user=request.user, event=event).exists()

    context = {
        'event': event,
        'user_has_rsvped': user_has_rsvped,
    }
    return render(request, 'event/event_detail.html', context)


@login_required
@user_passes_test(is_participant, login_url='no_permission')
def rsvp_event(request, id):
    try:
        event = Event.objects.get(id=id)
    except Event.DoesNotExist:
        messages.error(request, "Event not found.")
        return redirect('event_list')

    user = request.user
    if Rsvp.objects.filter(user=user, event=event).exists():
        messages.warning(request, "You have already Rsvp.")
    else:
        Rsvp.objects.create(user=user, event=event)
        messages.success(request, "RSVP successful! Check your email.")
    return redirect('participant_dashboard')


@login_required
@user_passes_test(lambda u: is_admin(u) or is_organizer(u), login_url='no_permission')
def dashboard(request):
    type = request.GET.get('type', 'all')
    today = date.today()

    total_events = Event.objects.count()
    total_participants = User.objects.count()
    todays_events = Event.objects.filter(date=today).select_related('category')
    upcoming_events_count = Event.objects.filter(date__gt=today).count()
    past_events_count = Event.objects.filter(date__lt=today).count()
    base_query = Event.objects.select_related('category').prefetch_related('participants')

    if type == 'today':
        events = base_query.filter(date=today)
    elif type == 'upcoming_events':
        events = base_query.filter(date__gt=today)
    elif type == 'past_events':
        events = base_query.filter(date__lt=today)
    else:
        events = base_query.all()

    context = {
        'total_events': total_events,
        'total_participants': total_participants,
        'todays_events': todays_events,
        'upcoming_events': upcoming_events_count,
        'past_events': past_events_count,
        'show_event': events,
    }

    return render(request, "dashboard.html", context)


@login_required
@user_passes_test(is_organizer, login_url='no_permission')
def create_event(request):
    event_form = EventModelForm()

    if request.method == "POST":
        event_form = EventModelForm(request.POST, request.FILES)
        if event_form.is_valid():
            event_form.save()
            messages.success(request, "Event Created Successfully")
            return redirect("event_list")
        else:
            messages.error(request, "Please correct the errors below.")
    return render(request, 'event_form.html', {'form': event_form})


@login_required
@user_passes_test(is_organizer, login_url='no_permission')
def update_event(request, id):
    try:
        event = Event.objects.get(id=id)
    except Event.DoesNotExist:
        messages.error(request, "Event not found.")
        return redirect('event_list')

    event_form = EventModelForm(instance=event)

    if request.method == "POST":
        event_form = EventModelForm(request.POST, request.FILES, instance=event)
        if event_form.is_valid():
            event_form.save()
            messages.success(request, "Event Updated Successfully")
            return redirect('event_list')
        else:
            messages.error(request, "Please correct the errors below.")
    return render(request, 'event_form.html', {'form': event_form})


@login_required
@user_passes_test(is_admin, login_url='no_permission')
def delete_event(request, id):
    if request.method == "POST":
        try:
            event = Event.objects.get(id=id)
            event.delete()
            messages.success(request, 'Event Deleted Successfully')
        except Event.DoesNotExist:
            messages.error(request, "Event not found.")
        return redirect('event_list')


@login_required
@user_passes_test(is_organizer, login_url='no_permission')
def create_category(request):
    category_form = CategoryModelForm()
    if request.method == 'POST':
        category_form = CategoryModelForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            messages.success(request, "Category Created Successfully")
            return redirect('category_list')
        else:
            messages.error(request, "Please correct the errors below.")
    return render(request, 'category_form.html', {'form': category_form})


@login_required
@user_passes_test(is_organizer, login_url='no_permission')
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})


@login_required
@user_passes_test(is_organizer, login_url='no_permission')
def update_category(request, id):
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        messages.error(request, "Category not found.")
        return redirect('category_list')

    category_form = CategoryModelForm(instance=category)

    if request.method == "POST":
        category_form = CategoryModelForm(request.POST, instance=category)
        if category_form.is_valid():
            category_form.save()
            messages.success(request, "Category Updated Successfully")
            return redirect('category_list')
        else:
            messages.error(request, "Please correct the errors below.")
    return render(request, 'category_form.html', {'form': category_form})


@login_required
@user_passes_test(is_admin, login_url='no_permission')
def delete_category(request, id):
    if request.method == "POST":
        try:
            category = Category.objects.get(id=id)
            category.delete()
            messages.success(request, 'Category Deleted Successfully')
        except Category.DoesNotExist:
            messages.error(request, "Category not found.")
        return redirect('category_list')


def first_home(request):
    return render(request, 'first_home.html')
