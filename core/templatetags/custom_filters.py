from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    if user.is_authenticated:
        return user.groups.filter(name=group_name).exists()
    return False
@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
