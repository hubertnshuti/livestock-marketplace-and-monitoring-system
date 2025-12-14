from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    """
    Adds a CSS class to a Django form field widget.
    Usage: {{ field|add_class:'form-control' }}
    """
    return value.as_widget(attrs={'class': arg})