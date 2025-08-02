from django.contrib import admin

from events.models import  Event,Category

admin.site.register(Category)
admin.site.register(Event)

# Register your models here.
