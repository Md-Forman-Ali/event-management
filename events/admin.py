from django.contrib import admin

from events.models import  Event,Category,Rsvp

admin.site.register(Category)
admin.site.register(Event)
admin.site.register(Rsvp)

# Register your models here.
