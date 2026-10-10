from django.forms import DateInput
from django.utils.safestring import mark_safe

from ..fields import FieldEx


class DatePicker(DateInput):
    template_name = 'django_modals/widgets/datepicker.html'
    crispy_field_class = FieldEx
    crispy_kwargs = {'appended_text': mark_safe('<i class="fas fa-calendar-alt fa-fw"></i>'), 'input_size': 'input-group-sm'}
