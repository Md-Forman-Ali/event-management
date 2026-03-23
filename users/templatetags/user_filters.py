from django import template
from datetime import timedelta
from django.utils import timezone

register = template.Library()

@register.filter
def humanized_date(value):
    if value:
        # Check if value is a date or datetime
        if hasattr(value, 'hour'):
            value = timezone.localtime(value)
            today = timezone.localtime(timezone.now()).date()
        else:
            today = timezone.localtime(timezone.now()).date()
            if value == today:
                return "Today"
            return value.strftime('%B %d, %Y')

        yesterday = today - timedelta(days=1)
        if value.date() == today:
            return f"Today at {value.strftime('%I:%M %p')}"
        elif value.date() == yesterday:
            return f"Yesterday at {value.strftime('%I:%M %p')}"
        else:
            return f"{value.strftime('%B %d, %Y at %I:%M %p')}"
    return "No record available"

@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
