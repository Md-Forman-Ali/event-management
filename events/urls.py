from django.urls import path, include
from events import views 
from users import views as user_view

urlpatterns = [
    path('users/', include('users.urls')),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    path('event_list/', views.EventList.as_view(), name='event_list'),
    path('events/<int:id>/', views.EventDetail.as_view(), name='event_detail'), 

    path('events/create/', views.CreateEvent.as_view(), name='create_event'),
    path('events/<int:id>/update/', views.UpdateEvent.as_view(), name='update_event'),
    path('events/<int:id>/delete/', views.DeleteEvent.as_view(), name='delete_event'),

    path('events/<int:id>/rsvp/', views.rsvp_event, name='rsvp_event'),

    path('category/', views.CategoryListView.as_view(), name='category_list'),
    path('category/create/', views.CategoryCreateView.as_view(), name='create_category'),
    path('category/<int:id>/update/', views.CategoryUpdateView.as_view(), name='update_category'),
    path('category/<int:id>/delete/', views.CategoryDeleteView.as_view(), name='delete_category'),
    path('first-home/', views.first_home, name='first_home'),

    path('admin/dashboard/', user_view.admin_dashboard, name='admin_dashboard'),
    path('organizer/dashboard/', user_view.organizer_dashboard, name='organizer_dashboard'),
    path('participant/dashboard/', user_view.participant_dashboard, name='participant_dashboard'),
]
