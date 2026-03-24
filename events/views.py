from django.shortcuts import render, redirect
from datetime import date
from events.models import Event, Category, Rsvp
from events.forms import EventModelForm, CategoryModelForm
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic.list import ListView
from django.views.generic import DetailView,CreateView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin,UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
User = get_user_model()



def is_participant(user):
    return user.groups.filter(name='Participant').exists()

def is_organizer(user):
    return user.groups.filter(name='Organizer').exists()

def is_admin(user):
    return user.is_superuser or user.groups.filter(name='Admin').exists()


class EventList(ListView):
    model = Event
    template_name = 'event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        user = self.request.user
        search = self.request.GET.get('search', '')
        category_id = self.request.GET.get('category', '')
        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '')
        
        events = Event.objects.select_related('category').prefetch_related('rsvp').all()

        if search:
            events = events.filter(Q(name__icontains=search) | Q(location__icontains=search))
        
        if category_id:
            events = events.filter(category_id=category_id)
        
        if start_date:
            events = events.filter(date__gte=start_date)
        
        if end_date:
            events = events.filter(date__lte=end_date)

        if user.is_authenticated:
            for event in events:
                event.user_has_rsvped = event.rsvp.filter(user=user).exists()
        else:
            for event in events:
                event.user_has_rsvped = False
        return events

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', '')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        return context
    

class EventDetail(DetailView):
    model = Event
    template_name = 'event/event_detail.html'
    context_object_name = 'event'
    pk_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        try:
            self.object = Event.objects.get(id=self.kwargs['id'])
        except Event.DoesNotExist:
            messages.error(request, "Event not found.")
            return redirect('event_list')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user_has_rsvped = False
        if self.request.user.is_authenticated:
            user_has_rsvped = Rsvp.objects.filter(user=self.request.user, event=self.object).exists()
        context['user_has_rsvped'] = user_has_rsvped
        
        return context



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

    from django.db.models import Count
    # Aggregate query to calculate total unique participants across all events
    total_participants_agg = Rsvp.objects.aggregate(total=Count('user', distinct=True))
    total_participants = total_participants_agg['total']

    total_events = Event.objects.count()
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



class CreateEvent(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'event_form.html'
    model = Event
    form_class = EventModelForm
    
    def test_func(self):
        return is_organizer(self.request.user) or is_admin(self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, "Event Created Successfully")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('event_list')
    


class UpdateEvent(LoginRequiredMixin,UserPassesTestMixin,UpdateView):

    pk_url_kwarg = 'id'
    template_name = 'event_form.html'
    model =Event
    form_class = EventModelForm

    def test_func(self):
        return is_organizer(self.request.user) or is_admin(self.request.user)
        
    def form_valid(self, form):
        messages.success(self.request, "Event Updated Successfully")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)
    def get_success_url(self):
        return reverse_lazy('event_list')




class DeleteEvent(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Event
    pk_url_kwarg = 'id'

    def test_func(self):
        return is_organizer(self.request.user) or is_admin(self.request.user)
    
    def get_success_url(self):
        messages.success(self.request, "Event Deleted Successfully")
        return reverse_lazy('event_list')



@login_required
@user_passes_test(lambda u: is_admin(u) or is_organizer(u), login_url='no_permission')
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
@user_passes_test(lambda u: is_admin(u) or is_organizer(u), login_url='no_permission')
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})


@login_required
@user_passes_test(lambda u: is_admin(u) or is_organizer(u), login_url='no_permission')
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
@user_passes_test(lambda u: is_admin(u) or is_organizer(u), login_url='no_permission')
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



"""
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
"""