from django.shortcuts import render, redirect
from datetime import date
from events.models import Event, Category, Rsvp
from events.forms import EventModelForm, CategoryModelForm
from django.db.models import Q, Exists, OuterRef, Value, BooleanField, Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic.list import ListView
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.utils import is_participant, is_organizer, is_admin

User = get_user_model()

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
        
        events = Event.objects.select_related('category').prefetch_related('rsvp')
        
        if search:
            events = events.filter(Q(name__icontains=search) | Q(location__icontains=search))
        
        if category_id:
            events = events.filter(category_id=category_id)
            
        if start_date:
            events = events.filter(date__gte=start_date)
            
        if end_date:
            events = events.filter(date__lte=end_date)

        if user.is_authenticated:
            rsvp_subquery = Rsvp.objects.filter(event=OuterRef('pk'), user=user)
            events = events.annotate(user_has_rsvped=Exists(rsvp_subquery))
            
        return events.annotate(participant_count=Count('rsvp'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        return context

class EventDetail(DetailView):
    model = Event
    template_name = 'event/event_detail.html'
    context_object_name = 'event'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_has_rsvped = False
        if self.request.user.is_authenticated:
            user_has_rsvped = Rsvp.objects.filter(user=self.request.user, event=self.object).exists()
        context['user_has_rsvped'] = user_has_rsvped
        context['participants'] = self.object.rsvp.select_related('user').all()
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
        messages.warning(request, "You have already RSVP'd for this event.")
    else:
        Rsvp.objects.create(user=user, event=event)
        messages.success(request, "RSVP successful! A confirmation email has been sent.")
    return redirect('participant_dashboard')

class DashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "dashboard.html"

    def test_func(self):
        return is_admin(self.request.user) or is_organizer(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_type = self.request.GET.get('type', 'all')
        today = timezone.localdate()

        context['total_events'] = Event.objects.count()
        # Aggregate: Total unique participants across all events
        context['total_participants'] = Rsvp.objects.values('user').distinct().count()
        context['todays_events'] = Event.objects.filter(date=today).select_related('category')
        context['upcoming_events_count'] = Event.objects.filter(date__gt=today).count()
        context['past_events_count'] = Event.objects.filter(date__lt=today).count()
        
        events = Event.objects.select_related('category').annotate(participant_count=Count('rsvp'))

        if filter_type == 'today':
            events = events.filter(date=today)
        elif filter_type == 'upcoming_events':
            events = events.filter(date__gt=today)
        elif filter_type == 'past_events':
            events = events.filter(date__lt=today)

        context['show_event'] = events
        context['filter_type'] = filter_type
        return context

class CategoryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'

    def test_func(self):
        return is_organizer(self.request.user) or is_admin(self.request.user)

class CategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Category
    form_class = CategoryModelForm
    template_name = 'category_form.html'
    success_url = reverse_lazy('category_list')

    def test_func(self):
        return is_organizer(self.request.user) or is_admin(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Category Created Successfully")
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Category
    form_class = CategoryModelForm
    template_name = 'category_form.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('category_list')

    def test_func(self):
        return is_organizer(self.request.user) or is_admin(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Category Updated Successfully")
        return super().form_valid(form)

class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Category
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('category_list')

    def test_func(self):
        return is_admin(self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Category Deleted Successfully')
        return super().delete(request, *args, **kwargs)

class CreateEvent(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Event
    form_class = EventModelForm
    template_name = 'event_form.html'
    success_url = reverse_lazy('event_list')

    def test_func(self):
        return is_organizer(self.request.user) or is_admin(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Event Created Successfully")
        return super().form_valid(form)

class UpdateEvent(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    form_class = EventModelForm
    template_name = 'event_form.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('event_list')

    def test_func(self):
        return is_organizer(self.request.user) or is_admin(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Event Updated Successfully")
        return super().form_valid(form)

class DeleteEvent(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('event_list')
    template_name = 'event_confirm_delete.html'

    def test_func(self):
        return is_admin(self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Event Deleted Successfully')
        return super().delete(request, *args, **kwargs)

def first_home(request):
    return render(request, 'first_home.html')