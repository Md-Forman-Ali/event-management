from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField()

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField()
    date = models.DateField(db_index=True)
    time = models.TimeField()
    location = models.CharField(max_length=250, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events') 
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Rsvp',
        related_name='rspv_events'
    )
    image = models.ImageField(
        upload_to='image_field',
        blank=True,
        null=True,
        default='image_field/def.jpg'
    )

    def __str__(self):
        return self.name

class Rsvp(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvp')
    rsvp_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f'{self.user.username} RSVP for {self.event.name}'
