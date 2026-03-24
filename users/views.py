import threading
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch, Count, Q
from django.contrib import messages
from users.forms import CustomRegistrationForm, CreateGroup,EditProfileForm, LoginForm, AssignRoleForm,CustomChangePasswordForm,CustomPasswordResetForm,CustomPasswordResetConfirmForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login, logout
from events.models import Event,Rsvp,Category
from django.views.generic import TemplateView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView,PasswordChangeView,PasswordResetView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth import get_user_model
from django.urls import reverse, reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from core.utils import is_admin, is_organizer, is_participant, get_user_role, email_sender

User = get_user_model()

def sign_up(request):
    form = CustomRegistrationForm()
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password'))
            user.is_active = False 
            user.save()  

            # Send activation email
            token = default_token_generator.make_token(user)
            activation_link = request.build_absolute_uri(
                reverse('activate_user', kwargs={'user_id': user.id, 'token': token})
            )
            
            subject = "Activate your EventMaster account"
            context = {
                'user': user,
                'activation_url': activation_link,
            }
            html_message = render_to_string('registration/activation_email.html', context)
            plain_message = strip_tags(html_message)
            
            thread = threading.Thread(
                target=email_sender,
                args=(subject, plain_message, settings.EMAIL_HOST_USER, [user.email], html_message)
            )
            thread.start()

            messages.success(request, 'A Confirmation mail sent. Please check your inbox')
            return redirect('sign-in')
        else:
            print("Form is not valid")
    return render(request, 'registration/register.html', {"form": form})

def get_role(user):
    # Fetch roles into a set once to avoid multiple database queries
    user_roles = set(user.groups.values_list('name', flat=True))
    if user.is_superuser or 'Admin' in user_roles:
        return 'admin_dashboard'  
    elif 'Organizer' in user_roles:
        return 'organizer_dashboard'
    elif 'Participant' in user_roles:
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
class CustomLogin(LoginView):
    form_class = LoginForm

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy(get_role(self.request.user))



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
    
    event_counts = Event.objects.aggregate(
        total=Count('id'),
        upcoming=Count('id', filter=Q(date__gt=today)),
        past=Count('id', filter=Q(date__lt=today))
    )
    
    total_events = event_counts['total']
    upcoming_events = event_counts['upcoming']
    past_events = event_counts['past']
    
    todays_events = Event.objects.filter(date=today)
    show_event = Event.objects.all()

    role = get_user_role(request.user)

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
    role = get_user_role(request.user)
    return render(request, 'dashboard/organizer_dashboard.html', {"user_role": role})

@user_passes_test(is_participant, login_url='no_permission')
def participant_dashboard(request):
    rsvp_events = Event.objects.filter(rsvp__user=request.user).annotate(participant_count=Count('rsvp'))
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
            return redirect('create-group')
    return render(request, 'admin/create_group.html', {"form": form})

@user_passes_test(is_admin, login_url='no_permission')
def group_list(request):
    groups = Group.objects.prefetch_related('permissions').all()
    return render(request,'admin/group_list.html', {'groups': groups})

@user_passes_test(is_admin, login_url='no_permission')
def user_list(request):
    users = User.objects.all()
    return render(request, 'admin/user_list.html', {'users': users})



class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['username'] = user.username
        context['email'] = user.email
        
        context['name'] = user.get_full_name()

        context['member_since'] = user.date_joined
        context['last_login'] = user.last_login
        context['phone_number'] = user.phone_number
        context['profile_image'] = user.profile_image
        context['bio'] = user.bio
        return context 

class ChangePassword(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    form_class = CustomChangePasswordForm

class PasswordReset(PasswordResetView):
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('sign-in')
    template_name = 'registration/reset_password.html'
    html_email_template_name = 'registration/reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        return context

    def form_valid(self, form):
        messages.success(self.request,'Reset Email Sent Check Your Inbox')
  
        return super().form_valid(form)
    

       
class PasswordResetConfirm(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'registration/reset_password.html'
    success_url = reverse_lazy('sign-in')

    def form_valid(self, form):
        messages.success(self.request,'Reset Succesfull')
        return super().form_valid(form)
    


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'accounts/update_profile.html'
    context_object_name = 'form'
    
    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('profile')

@user_passes_test(is_admin, login_url='no_permission')
def test_email(request):
    subject = "Test Email from EventMaster"
    message = "This is a test email to verify SMTP settings on production."
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [from_email]
    
    try:
        if not from_email:
            return HttpResponse("CRITICAL: EMAIL_HOST_USER is NOT SET.")
            
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return HttpResponse(f"SUCCESS: Test email sent to {from_email}. Check your inbox.")
    except Exception as e:
        return HttpResponse(f"FAILED: {str(e)}<br><br>Settings: HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}, TLS={settings.EMAIL_USE_TLS}")

