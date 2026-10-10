from django.forms import CheckboxInput, Textarea


class Toggle(CheckboxInput):
    template_name = 'django_modals/widgets/toggle.html'
    crispy_kwargs = {'template': 'django_modals/fields/label_checkbox.html', 'field_class': 'col-6 input-group-sm'}
    # In a table cell too. crispy-bootstrap4's field.html gives a checkbox in a "td" a
    # custom-control label of its own, which drew an empty checkbox under the toggle.
    formset_field_template = 'django_modals/fields/label_checkbox.html'


class TinyMCE(Textarea):
    template_name = 'django_modals/widgets/tinymce.html'
    crispy_kwargs = {'label_class': 'col-3 col-form-label-sm', 'field_class': 'col-12 input-group-sm'}
