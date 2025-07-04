from django.shortcuts import render, redirect
from datetime import date
from events.models import Event,Participant,Category
from events.forms import EventModelForm,ParticipantModelForm,CategoryModelForm
from django.db.models import Count, Q
from django.http import HttpResponse 
from django.contrib import messages

def dashboard(request):
    type = request.GET.get('type', 'all')
    today = date.today()

    total_events = Event.objects.count()
    total_participants = Participant.objects.count()
    upcoming_events_count = Event.objects.filter(date__gt=today).count()
    past_events_count = Event.objects.filter(date__lt=today).count()
    base_query = Event.objects.select_related('category').prefetch_related('participants')

    if type == 'today':
        events = base_query.filter(date=today)
        event_list_title = "Today's Events"
    elif type == 'upcoming_events':
        events = base_query.filter(date__gt=today)
        event_list_title = "Upcoming Events"
    elif type == 'past_events':
        events = base_query.filter(date__lt=today)
        event_list_title = "Past Events"
    else:
        events = base_query.all()
        event_list_title = "All Events"

    context = {
        'total_events': total_events,
        'total_participants': total_participants,
        'upcoming_events': upcoming_events_count,
        'past_events': past_events_count,
        'event_list_title': event_list_title,
        'show_event': events,
    }

    return render(request, "dashboard.html", context)

def create_event(request):
    event_form = EventModelForm() 

    if request.method == "POST":
        event_form = EventModelForm(request.POST)
        if event_form.is_valid():
            event_form.save()
            messages.success(request, "Event Created Successfully")
            return redirect("event_list")
        return render(request, 'event_form.html', {'form': event_form})


def event_list(request):
    events = Event.objects.select_related('category').prefetch_related('participants').all()
    return render(request, 'event_list.html', {'events': events})


def update_event(request,id):
    event = Event.objects.get(id=id)
    event_form = EventModelForm(instance=event)

    if request.method =="POST":
        event_form = EventModelForm(request.POST,instance=event)

        if event_form.is_valid():
            event_form.save()
            messages.success(request, "Event Updated Successfully")
            return redirect('event_list')
           
        return render(request, 'event_form.html', {'form': event_form})

def delete_event(request,id):
    if request.method == "POST":
        event = Event.objects.get(id=id)
        event.delete()
        messages.success(request, 'Event Deleted Successfully')
        return redirect('event_list')
    
    
def create_participate(request):
    participant_form = ParticipantModelForm()

    if request.method =="POST":
        participant_form = ParticipantModelForm(request.POST)

        if participant_form.is_valid():
            participant_form.save()
            messages.success(request,"Participant Create Successfully")
            return redirect("participant_list")
        return render(request, 'participate_form.html', {'form': participant_form})

def participant_list(request):
    participants = Participant.objects.prefetch_related('events').all()
    return render(request, 'participant_list.html', {'participants': participants})

def update_participant(request,id):
    participant = Participant.objects.get(id=id)
    participant_form = ParticipantModelForm(instance=participant)

    if request.method == "POST":
        participant_form = ParticipantModelForm(request.POST,instance=participant)
        if participant_form.is_valid():
            participant_form.save()
            messages.success(request,"Participant Update Succesfully")
            return redirect('participant_list')
        return render(request, 'participate_form.html', {'form': participant_form})
     
            

def delete_participate(request,id):
    if request.method =="POST":
        participant= Participant.objects.get(id=id)
        participant.delete()
        messages.success(request, 'Participant Deleted Successfully')
        return redirect('participant_list')

def create_category(request):
    category_form = CategoryModelForm()
    if request.method =='POST':
        category_form = CategoryModelForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            return redirect('category_list')
        return render(request, 'category_form.html', {'form': category_form})
    
def category_list(request):
    category= Category.objects.all()
    return render(request, 'category_list.html', {'category': category})

def update_category(request,id):
    category = Category.objects.get(id=id)
    category_form = CategoryModelForm(instance=category)
    if request.method =="POST":
        category_form = CategoryModelForm(request.POST,instance=category)
        if category_form.is_valid():
            category_form.save()
            messages.success(request,"Category Update Successfully")
            return redirect('category_list')
        return render(request, 'category_form.html', {'form': category_form})

def delete_category(request,id):
    if request.method=="POST":
        category = Category.objects.get(id=id)
        category.delete()
        messages.success(request, 'Category Deleted Successfully')
        return redirect('category_list')
    
