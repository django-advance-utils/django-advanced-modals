from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe

from ..fields import FieldEx


class MonthPicker(TextInput):
    template_name = 'django_modals/widgets/month_picker.html'
    crispy_field_class = FieldEx
    crispy_kwargs = {'appended_text': mark_safe('<i class="fas fa-calendar-alt fa-fw"></i>'), 'input_size': 'input-group-sm'}
