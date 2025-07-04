
from django.urls import path
from events import views

urlpatterns = [

    path('dashboard/', views.dashboard, name='dashboard'),

    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/<int:id>/update/', views.update_event, name='update_event'),
    path('events/<int:id>/delete/', views.delete_event, name='delete_event'),

    path('participants/', views.participant_list, name='participant_list'),
    path('participants/create/', views.create_participate, name='create_participant'),
    path('participants/<int:id>/update/', views.update_participant, name='update_participant'),
    path('participants/<int:id>/delete/', views.delete_participate, name='delete_participant'),

    path('category/', views.category_list, name='category_list'),
    path('category/create/', views.create_category, name='create_category'),
    path('category/<int:id>/update/', views.update_category, name='update_category'),
    path('category/<int:id>/delete/', views.delete_category, name='delete_category'),
    

]
